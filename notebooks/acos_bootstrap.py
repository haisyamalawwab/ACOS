"""Bootstrap mandiri untuk notebook master pipeline ACOS.

Sesi Colab selalu mulai dari filesystem yang tidak bisa ditebak: folder Drive
mungkin belum ada, ada tapi kosong, atau ada tapi berisi salinan setengah jadi
dari sesi sebelumnya. Modul ini membuat sel pertama notebook menjadi
deterministik — ia menyatakan apa yang dibutuhkan pipeline, memeriksa satu per
satu, lalu menambal yang hilang dengan mengunduh dari repositori induk di GitHub.

Kenapa `except ModuleNotFoundError` di notebook tidak cukup: from-import terhadap
modul yang **ada** tetapi kekurangan nama akan melempar ``ImportError``, bukan
``ModuleNotFoundError``. Repo ini punya tiga salinan ``colab_utils.py``, dan
salinan di root repo kehilangan 10 dari 16 simbol yang diimpor notebook. Jadi
setiap kali salinan itu menang balapan ``sys.path``, notebook crash tepat di sel
yang fallback-nya justru terpasang di situ. Karena itu :func:`ensure_symbols`
memeriksa nama, bukan cuma keberhasilan impor.

Pemakaian di notebook::

    from acos_bootstrap import ensure_project
    report = ensure_project()
    base_project_dir = report.base

Seluruh isi modul memakai standard library saja, supaya bisa jalan sebelum
``pip install`` dan tidak ikut gagal kalau jaringan pip bermasalah.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_REPO = "haisyamalawwab/ACOS"
DEFAULT_BRANCH = "main"
RAW_TEMPLATE = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
CLONE_TEMPLATE = "https://github.com/{repo}.git"

DRIVE_ROOT = "/content/drive/MyDrive"
PROJECT_FOLDER = "ACOS"

# Simbol yang diimpor notebook dari colab_utils.  Daftar ini adalah kontraknya:
# kalau salah satu hilang, salinan colab_utils.py itu dianggap tidak layak dan
# diganti dari induk, bukan dibiarkan lalu crash beberapa sel kemudian.
COLAB_UTILS_SYMBOLS: Tuple[str, ...] = (
    "setup_timestamped_run_dir",
    "download_bert_pretrained",
    "analyze_and_plot_eda",
    "plot_training_history",
    "export_benchmark_tables_and_plots",
    "display_quadruple_dataframe",
    "df_to_markdown",
    "export_step_table",
    "MarkdownReport",
    "SubtaskMetricCapture",
    "plot_subtask_metrics",
    "features_step1",
    "features_step2",
    "pair_examples_from_file",
    "resolve_eval_pair_file",
    "unpack_model_output",
    "detect_acos_project_root",
    "inspect_acos_drive_structure",
    "verify_session_save_paths",
    "find_resumable_session",
    "auto_find_file",
)

# Modul repo yang diimpor pipeline dari Extract-Classify-ACOS/.
REQUIRED_MODULES: Tuple[Tuple[str, str], ...] = (
    ("modeling", "Extract-Classify-ACOS/modeling.py"),
    ("run_classifier_dataset_utils", "Extract-Classify-ACOS/run_classifier_dataset_utils.py"),
    ("eval_metrics", "Extract-Classify-ACOS/eval_metrics.py"),
    ("dataset_utils", "Extract-Classify-ACOS/dataset_utils.py"),
    ("manager", "Extract-Classify-ACOS/manager.py"),
    ("file_utils", "Extract-Classify-ACOS/file_utils.py"),
)

# File yang harus ada, relatif terhadap base project dir.
REQUIRED_FILES: Tuple[str, ...] = (
    "Extract-Classify-ACOS/modeling.py",
    "Extract-Classify-ACOS/run_classifier_dataset_utils.py",
    "Extract-Classify-ACOS/eval_metrics.py",
    "Extract-Classify-ACOS/dataset_utils.py",
    "Extract-Classify-ACOS/manager.py",
    "Extract-Classify-ACOS/file_utils.py",
    "Extract-Classify-ACOS/run_step1.py",
    "Extract-Classify-ACOS/run_step2.py",
    "Extract-Classify-ACOS/bert_utils/__init__.py",
    "Extract-Classify-ACOS/bert_utils/tokenization.py",
    "Extract-Classify-ACOS/bert_utils/optimization.py",
    "Extract-Classify-ACOS/bert_utils/file_utils.py",
    "Extract-Classify-ACOS/tokenized_data/get_1st_pairs.py",
    "notebooks/colab_utils.py",
)

# Data latih. Tanpa ini pipeline tidak punya apa pun untuk dilatih, jadi
# kegagalan di sini bersifat fatal, bukan peringatan.
REQUIRED_DATA: Tuple[str, ...] = (
    "data/Restaurant-ACOS/rest16_quad_train.tsv",
    "data/Restaurant-ACOS/rest16_quad_dev.tsv",
    "data/Restaurant-ACOS/rest16_quad_test.tsv",
    "data/Laptop-ACOS/laptop_quad_train.tsv",
    "data/Laptop-ACOS/laptop_quad_dev.tsv",
    "data/Laptop-ACOS/laptop_quad_test.tsv",
)

# Data hasil pra-tokenisasi. Generatornya tidak pernah dirilis upstream, jadi
# file ini tidak bisa dibuat ulang di Colab dan harus benar-benar diunduh.
REQUIRED_TOKENIZED: Tuple[str, ...] = tuple(
    f"Extract-Classify-ACOS/tokenized_data/{name}"
    for name in (
        "rest16_train_quad_bert.tsv", "rest16_dev_quad_bert.tsv", "rest16_test_quad_bert.tsv",
        "rest16_train_pair.tsv", "rest16_dev_pair.tsv", "rest16_test_pair.tsv",
        "rest16_test_pair_1st.tsv",
        "laptop_train_quad_bert.tsv", "laptop_dev_quad_bert.tsv", "laptop_test_quad_bert.tsv",
        "laptop_train_pair.tsv", "laptop_dev_pair.tsv", "laptop_test_pair.tsv",
        "laptop_test_pair_1st.tsv",
    )
)

class BootstrapError(RuntimeError):
    """Sesuatu yang wajib tidak bisa dipenuhi, bahkan setelah fallback."""


@dataclass
class BootstrapReport:
    """Catatan apa yang ditemukan, apa yang diunduh, dan apa yang masih kurang."""

    base: str = ""
    save_dir: str = ""
    extract_dir: str = ""
    notebooks_dir: str = ""
    source: str = ""
    repo: str = DEFAULT_REPO
    branch: str = DEFAULT_BRANCH
    on_drive: bool = False
    present: List[str] = field(default_factory=list)
    fetched: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    moved: List[str] = field(default_factory=list)
    symbols_missing: Dict[str, List[str]] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    elapsed: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.failed

    def note(self, message: str) -> None:
        self.actions.append(message)

    def as_dict(self) -> Dict[str, object]:
        return {
            "base": self.base,
            "save_dir": self.save_dir,
            "extract_dir": self.extract_dir,
            "notebooks_dir": self.notebooks_dir,
            "source": self.source,
            "repo": self.repo,
            "branch": self.branch,
            "on_drive": self.on_drive,
            "present": len(self.present),
            "fetched": self.fetched,
            "failed": self.failed,
            "skipped": self.skipped,
            "moved": self.moved,
            "symbols_missing": self.symbols_missing,
            "warnings": self.warnings,
            "elapsed_seconds": round(self.elapsed, 2),
        }

    def summary(self) -> str:
        lines = [
            f"base project dir : {self.base}",
            f"sumber           : {self.source}",
            f"output dir       : {self.save_dir}",
            f"file lengkap     : {len(self.present)} ada, {len(self.fetched)} diunduh dari induk",
        ]
        if self.moved:
            lines.append(f"dipindahkan      : {', '.join(self.moved)}")
        if self.symbols_missing:
            for module, names in self.symbols_missing.items():
                lines.append(
                    f"diganti          : {module} kehilangan {len(names)} simbol "
                    f"({', '.join(names[:3])}{'...' if len(names) > 3 else ''})"
                )
        if self.skipped:
            lines.append(f"dilewati         : {len(self.skipped)} file opsional")
        for w in self.warnings:
            lines.append(f"peringatan       : {w}")
        if self.failed:
            lines.append(f"GAGAL            : {len(self.failed)} file wajib tidak tersedia")
            for f in self.failed[:8]:
                lines.append(f"                   {f}")
        else:
            lines.append("status           : semua prasyarat terpenuhi")
        lines.append(f"durasi           : {self.elapsed:.1f}s")
        return "\n".join(lines)

    def _repr_markdown_(self) -> str:  # ditampilkan rapi di Jupyter
        body = "\n".join(f"    {line}" for line in self.summary().splitlines())
        mark = "OK" if self.ok else "GAGAL"
        return f"**Bootstrap ACOS — {mark}**\n\n<pre>\n{body}\n</pre>"


# -- lokasi proyek ---------------------------------------------------------
def drive_mounted(drive_root: str = DRIVE_ROOT) -> bool:
    return os.path.isdir(drive_root)


def resolve_base_dir(
    *,
    prefer_drive: bool = True,
    drive_root: str = DRIVE_ROOT,
    project_folder: str = PROJECT_FOLDER,
) -> Tuple[str, str, bool]:
    """Tentukan direktori proyek. Mengembalikan ``(base, sumber, di_drive)``.

    Urutan preferensi menaruh Drive di depan supaya hasil training bertahan
    setelah runtime Colab mati, tapi tetap menerima checkout lokal apa pun yang
    sudah berisi ``Extract-Classify-ACOS``.
    """
    if prefer_drive and drive_mounted(drive_root):
        base = os.path.join(drive_root, project_folder)
        os.makedirs(base, exist_ok=True)
        return base, f"Google Drive ({base})", True

    for candidate, label in (
        (os.path.join("/content", project_folder), "runtime Colab"),
        (os.path.abspath("."), "direktori kerja"),
        (os.path.abspath(".."), "direktori induk"),
    ):
        if os.path.isdir(os.path.join(candidate, "Extract-Classify-ACOS")):
            return candidate, f"{label} ({candidate})", False

    base = os.path.abspath(project_folder)
    os.makedirs(base, exist_ok=True)
    return base, f"folder baru ({base})", False


def relocate_stray_folders(
    base: str,
    *,
    drive_root: str = DRIVE_ROOT,
    names: Sequence[str] = ("Extract-Classify-ACOS", "data", "notebooks"),
    report: Optional[BootstrapReport] = None,
) -> List[str]:
    """Pindahkan folder yang telanjur tersimpan di root Drive ke dalam ``base``.

    Sesi lama kadang menulis ke ``MyDrive/`` langsung. Kalau dibiarkan, folder
    itu jadi kembar dengan yang di dalam ``MyDrive/ACOS/`` dan pipeline bisa
    membaca salinan yang salah. Kalau tujuannya sudah terisi, sumbernya
    dibiarkan supaya tidak ada data yang tertimpa.
    """
    moved: List[str] = []
    if not drive_mounted(drive_root):
        return moved
    for name in names:
        src = os.path.join(drive_root, name)
        dst = os.path.join(base, name)
        if not os.path.isdir(src) or os.path.abspath(src) == os.path.abspath(dst):
            continue
        if os.path.isdir(dst) and os.listdir(dst):
            if report is not None:
                report.warnings.append(
                    f"{src} dan {dst} dua-duanya ada; yang di root Drive dibiarkan "
                    f"agar tidak menimpa, hapus manual kalau memang duplikat"
                )
            continue
        try:
            if os.path.isdir(dst):
                os.rmdir(dst)
            shutil.move(src, dst)
            moved.append(name)
        except Exception as exc:  # noqa: BLE001
            if report is not None:
                report.warnings.append(f"gagal memindahkan {src}: {exc}")
    return moved


# -- pengambilan file ------------------------------------------------------
def raw_url(path: str, *, repo: str = DEFAULT_REPO, branch: str = DEFAULT_BRANCH) -> str:
    return RAW_TEMPLATE.format(repo=repo, branch=branch, path=path.replace(os.sep, "/"))


def fetch_file(
    path: str,
    base: str,
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    retries: int = 3,
    timeout: int = 30,
    overwrite: bool = True,
) -> Tuple[bool, str]:
    """Unduh satu file dari induk GitHub ke ``base/path``.

    Menulis ke file sementara lalu me-rename, supaya file separuh terunduh
    tidak pernah terlihat lengkap — penting di Drive yang sering terputus.
    """
    target = os.path.join(base, path.replace("/", os.sep))
    if os.path.exists(target) and not overwrite:
        return True, "sudah ada"
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    url = raw_url(path, repo=repo, branch=branch)
    tmp = target + ".part"

    last = ""
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if getattr(response, "status", 200) != 200:
                    last = f"HTTP {response.status}"
                    continue
                payload = response.read()
            with open(tmp, "wb") as fh:
                fh.write(payload)
            os.replace(tmp, target)
            return True, f"{len(payload)} byte"
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            if exc.code == 404:
                break  # tidak ada gunanya mengulang
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(1.5 * attempt)
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass
    return False, last or "gagal"


def clone_repo(
    base: str,
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    report: Optional[BootstrapReport] = None,
) -> bool:
    """Clone dangkal ke folder sementara lalu salin isinya ke ``base``.

    Dipakai kalau file yang hilang banyak: satu clone jauh lebih cepat daripada
    puluhan permintaan HTTP. File yang sudah ada di ``base`` tidak ditimpa,
    sehingga hasil training di Drive tetap aman.
    """
    import tempfile

    # tempfile, bukan "/tmp" yang dirakit sendiri: di Windows os.path.join
    # menghasilkan "/tmp\_acos_clone", dan sisa folder dari percobaan sebelumnya
    # membuat git clone menolak jalan.
    parent = tempfile.mkdtemp(prefix="acos_clone_")
    tmp = os.path.join(parent, "repo")
    url = CLONE_TEMPLATE.format(repo=repo)
    try:
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, url, tmp],
            capture_output=True, text=True, timeout=600,
        )
        if proc.returncode != 0:
            if report is not None:
                report.warnings.append(f"git clone gagal: {proc.stderr.strip()[-200:]}")
            return False
        copied = 0
        for root, dirs, files in os.walk(tmp):
            dirs[:] = [d for d in dirs if d != ".git"]
            for name in files:
                src = os.path.join(root, name)
                rel = os.path.relpath(src, tmp)
                dst = os.path.join(base, rel)
                # File kosong dianggap tidak ada: unduhan Drive yang terputus
                # meninggalkan file nol byte yang lolos os.path.exists.
                if os.path.exists(dst) and os.path.getsize(dst) > 0:
                    continue
                os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
        if report is not None:
            report.note(f"clone induk: {copied} file baru disalin ke {base}")
        return True
    except FileNotFoundError:
        if report is not None:
            report.warnings.append("git tidak tersedia; fallback per-file dipakai")
        return False
    except Exception as exc:  # noqa: BLE001
        if report is not None:
            report.warnings.append(f"clone gagal: {type(exc).__name__}: {exc}")
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# -- pemeriksaan file ------------------------------------------------------
def ensure_files(
    paths: Iterable[str],
    base: str,
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    required: bool = True,
    min_bytes: int = 1,
    report: Optional[BootstrapReport] = None,
) -> Tuple[List[str], List[str]]:
    """Pastikan tiap file ada dan tidak kosong; unduh dari induk kalau tidak.

    File berukuran nol diperlakukan sebagai tidak ada. Ini bukan kehati-hatian
    berlebih: unduhan Drive yang terputus meninggalkan file kosong, dan file
    kosong akan lolos ``os.path.exists`` lalu gagal jauh di dalam training.
    """
    fetched: List[str] = []
    missing: List[str] = []
    for path in paths:
        target = os.path.join(base, path.replace("/", os.sep))
        if os.path.isfile(target) and os.path.getsize(target) >= min_bytes:
            if report is not None:
                report.present.append(path)
            continue
        ok, detail = fetch_file(path, base, repo=repo, branch=branch)
        if ok:
            fetched.append(path)
            if report is not None:
                report.fetched.append(path)
        else:
            missing.append(f"{path} ({detail})")
            if report is not None:
                (report.failed if required else report.skipped).append(f"{path} ({detail})")
    return fetched, missing


def module_symbols(module_name: str, path: str) -> Tuple[bool, List[str]]:
    """Baca nama top-level dari sebuah file .py tanpa mengeksekusinya.

    Memakai ``ast`` supaya pemeriksaan tidak menjalankan kode yang bisa jadi
    justru rusak, dan tidak bergantung pada state ``sys.modules``.
    """
    import ast

    try:
        with open(path, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
    except (OSError, SyntaxError):
        return False, []
    names: List[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.Assign):
            names.extend(t.id for t in node.targets if isinstance(t, ast.Name))
    return True, names


def ensure_symbols(
    path: str,
    symbols: Sequence[str],
    remote_path: str,
    base: str,
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    report: Optional[BootstrapReport] = None,
) -> Tuple[bool, List[str]]:
    """Pastikan file ``path`` benar-benar mendefinisikan ``symbols``.

    Inilah pemeriksaan yang tidak dilakukan notebook. Fallback lamanya menangkap
    ``ModuleNotFoundError``, padahal kasus yang benar-benar terjadi adalah modul
    yang ada tapi kurang simbol — itu ``ImportError``, dan tidak tertangkap. Repo
    punya tiga ``colab_utils.py`` dan salinan di root kehilangan 10 dari 16 simbol,
    jadi masalah ini bukan hipotesis.
    """
    exists, names = module_symbols("colab_utils", path)
    missing = [s for s in symbols if s not in names]
    if exists and not missing:
        return True, []

    reason = "tidak terbaca" if not exists else f"kehilangan {len(missing)} simbol"
    if report is not None:
        report.note(f"{os.path.basename(path)} {reason}; mengambil ulang dari induk")
        report.symbols_missing[os.path.relpath(path, base) if base in path else path] = missing

    ok, detail = fetch_file(remote_path, base, repo=repo, branch=branch, overwrite=True)
    if not ok:
        if report is not None:
            report.failed.append(f"{remote_path} ({detail})")
        return False, missing

    fresh = os.path.join(base, remote_path.replace("/", os.sep))
    exists2, names2 = module_symbols("colab_utils", fresh)
    still = [s for s in symbols if s not in names2]
    if still:
        if report is not None:
            report.failed.append(
                f"{remote_path} tetap kehilangan {len(still)} simbol setelah diunduh: "
                f"{', '.join(still[:5])}"
            )
        return False, still
    if report is not None:
        report.fetched.append(remote_path)
    return True, []


def prune_shadowing_copies(
    base: str,
    keep: str,
    *,
    filename: str = "colab_utils.py",
    symbols: Sequence[str] = COLAB_UTILS_SYMBOLS,
    report: Optional[BootstrapReport] = None,
) -> List[str]:
    """Ganti nama salinan ``colab_utils.py`` lain yang tidak lengkap.

    Selama salinan yang cacat masih ada di ``sys.path``, urutan pencarian bisa
    menang atas salinan yang benar dan notebook gagal lagi di sel berikutnya.
    Salinan itu di-rename (``.incomplete``), bukan dihapus, supaya tidak ada
    pekerjaan orang lain yang hilang.
    """
    renamed: List[str] = []
    keep_abs = os.path.abspath(keep)
    for candidate in (
        os.path.join(base, filename),
        os.path.join(base, "Extract-Classify-ACOS", filename),
        os.path.join(base, "notebooks", filename),
    ):
        if not os.path.isfile(candidate) or os.path.abspath(candidate) == keep_abs:
            continue
        _, names = module_symbols("colab_utils", candidate)
        missing = [s for s in symbols if s not in names]
        if not missing:
            continue
        backup = candidate + ".incomplete"
        try:
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(candidate, backup)
            renamed.append(os.path.relpath(candidate, base))
            if report is not None:
                report.note(
                    f"{os.path.relpath(candidate, base)} kehilangan {len(missing)} simbol, "
                    f"di-rename menjadi .incomplete agar tidak membayangi salinan yang benar"
                )
        except OSError as exc:
            if report is not None:
                report.warnings.append(f"tidak bisa me-rename {candidate}: {exc}")
    return renamed


def verify_imports(
    modules: Sequence[Tuple[str, str]],
    base: str,
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    report: Optional[BootstrapReport] = None,
    execute: bool = False,
) -> List[str]:
    """Pastikan setiap modul pipeline ada sebagai file; unduh yang hilang.

    ``execute=False`` secara default karena ``import modeling`` menuntut torch dan
    torchcrf sudah terpasang. Bootstrap harus bisa jalan sebelum ``pip install``,
    jadi yang diperiksa adalah keberadaan dan keterbacaan file.
    """
    broken: List[str] = []
    for module_name, path in modules:
        target = os.path.join(base, path.replace("/", os.sep))
        ok, _ = module_symbols(module_name, target)
        if not ok:
            fetched, missing = ensure_files(
                [path], base, repo=repo, branch=branch, report=report
            )
            if missing:
                broken.extend(missing)
                continue
            ok, _ = module_symbols(module_name, target)
            if not ok:
                broken.append(f"{path} (tidak bisa di-parse)")
                continue
        if execute:
            try:
                importlib.import_module(module_name)
            except Exception as exc:  # noqa: BLE001
                if report is not None:
                    report.warnings.append(
                        f"import {module_name} gagal ({type(exc).__name__}); "
                        f"biasanya karena dependensi belum ter-install"
                    )
    return broken


# -- orkestrasi ------------------------------------------------------------
def ensure_project(
    *,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    prefer_drive: bool = True,
    drive_root: str = DRIVE_ROOT,
    project_folder: str = PROJECT_FOLDER,
    output_folder: str = "Output",
    include_tokenized: bool = True,
    clone_threshold: int = 6,
    add_to_syspath: bool = True,
    strict: bool = True,
    verbose: bool = True,
    report_path: Optional[str] = None,
) -> BootstrapReport:
    """Siapkan direktori proyek lengkap, ambil dari induk apa pun yang hilang.

    Alurnya sengaja berjenjang dari yang paling murah ke yang paling mahal:
    pindahkan folder yang salah tempat, lalu clone kalau yang hilang banyak,
    lalu tambal per-file, lalu verifikasi simbol. ``clone_threshold`` menentukan
    kapan satu clone lebih hemat daripada banyak HTTP request.

    ``strict=True`` melempar :class:`BootstrapError` kalau ada prasyarat wajib
    yang tetap tidak terpenuhi. Itu disengaja: lebih baik gagal di sel pertama
    dengan pesan jelas daripada gagal di tengah training dua jam kemudian.
    """
    started = time.time()
    base, source, on_drive = resolve_base_dir(
        prefer_drive=prefer_drive, drive_root=drive_root, project_folder=project_folder
    )
    report = BootstrapReport(
        base=base, source=source, repo=repo, branch=branch, on_drive=on_drive
    )

    report.moved = relocate_stray_folders(base, drive_root=drive_root, report=report)

    wanted: List[str] = list(REQUIRED_FILES) + list(REQUIRED_DATA)
    if include_tokenized:
        wanted += list(REQUIRED_TOKENIZED)

    absent = [
        p for p in wanted
        if not (
            os.path.isfile(os.path.join(base, p.replace("/", os.sep)))
            and os.path.getsize(os.path.join(base, p.replace("/", os.sep))) > 0
        )
    ]
    if len(absent) >= clone_threshold:
        report.note(f"{len(absent)} file wajib hilang; mencoba clone induk sekali jalan")
        clone_repo(base, repo=repo, branch=branch, report=report)

    ensure_files(REQUIRED_FILES, base, repo=repo, branch=branch, required=True, report=report)
    ensure_files(REQUIRED_DATA, base, repo=repo, branch=branch, required=True, report=report)
    if include_tokenized:
        ensure_files(
            REQUIRED_TOKENIZED, base, repo=repo, branch=branch, required=True, report=report
        )

    # Pemeriksaan simbol, bukan cuma keberadaan file (lihat ensure_symbols).
    canonical = os.path.join(base, "notebooks", "colab_utils.py")
    ensure_symbols(
        canonical, COLAB_UTILS_SYMBOLS, "notebooks/colab_utils.py", base,
        repo=repo, branch=branch, report=report,
    )
    prune_shadowing_copies(base, canonical, report=report)

    broken = verify_imports(REQUIRED_MODULES, base, repo=repo, branch=branch, report=report)
    if broken:
        report.failed.extend(broken)

    extract_dir = os.path.join(base, "Extract-Classify-ACOS")
    notebooks_dir = os.path.join(base, "notebooks")
    save_dir = os.path.join(base, output_folder) if on_drive else base
    os.makedirs(save_dir, exist_ok=True)
    for sub in ("tokenized_data", "bert_utils"):
        os.makedirs(os.path.join(extract_dir, sub), exist_ok=True)

    report.extract_dir = extract_dir
    report.notebooks_dir = notebooks_dir
    report.save_dir = save_dir

    if add_to_syspath:
        # notebooks_dir lebih dulu supaya salinan colab_utils yang lengkap menang.
        for path in (notebooks_dir, extract_dir, base):
            if path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)

    report.elapsed = time.time() - started

    if report_path is None:
        report_path = os.path.join(save_dir, "_bootstrap_report.json")
    try:
        os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report.as_dict(), fh, indent=2, ensure_ascii=False)
    except OSError as exc:
        report.warnings.append(f"tidak bisa menulis laporan bootstrap: {exc}")

    if verbose:
        print(report.summary())

    if strict and not report.ok:
        raise BootstrapError(
            f"{len(report.failed)} prasyarat tidak terpenuhi meski sudah fallback ke "
            f"{repo}@{branch}. Yang pertama: {report.failed[0]}"
        )
    return report


def import_colab_utils(symbols: Sequence[str] = COLAB_UTILS_SYMBOLS) -> Dict[str, object]:
    """Impor ``colab_utils`` dan kembalikan simbol yang diminta sebagai dict.

    Membedakan tiga kegagalan yang gejalanya mirip tapi penanganannya berbeda:
    dependensi pihak ketiga belum ter-install (jalankan sel ``pip install``),
    file colab_utils tidak ada (jalankan :func:`ensure_project`), atau file ada
    tapi kurang simbol karena salinan yang salah yang menang di ``sys.path``.
    """
    sys.modules.pop("colab_utils", None)
    try:
        module = importlib.import_module("colab_utils")
    except ModuleNotFoundError as exc:
        culprit = getattr(exc, "name", "") or ""
        if culprit and culprit != "colab_utils":
            raise BootstrapError(
                f"colab_utils butuh paket '{culprit}' yang belum ter-install. "
                f"Jalankan sel instalasi dependensi lebih dulu, lalu ulangi sel ini."
            ) from exc
        raise BootstrapError(
            "colab_utils tidak ditemukan di sys.path. Jalankan ensure_project() "
            "lebih dulu agar salinannya diambil dari induk."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise BootstrapError(f"colab_utils tidak bisa diimpor: {exc}") from exc

    missing = [s for s in symbols if not hasattr(module, s)]
    if missing:
        raise BootstrapError(
            f"colab_utils di {getattr(module, '__file__', '?')} kehilangan "
            f"{len(missing)} simbol: {', '.join(missing)}. Repo ini punya beberapa "
            f"salinan colab_utils.py dengan isi berbeda; jalankan ensure_project() "
            f"agar salinan yang tidak lengkap di-rename dan yang benar dipakai."
        )
    return {s: getattr(module, s) for s in symbols}


def preflight(base: Optional[str] = None, *, include_tokenized: bool = True) -> Dict[str, object]:
    """Laporkan apa yang ada tanpa mengunduh apa pun. Berguna untuk diagnosa."""
    if base is None:
        base, _, _ = resolve_base_dir()
    wanted = list(REQUIRED_FILES) + list(REQUIRED_DATA)
    if include_tokenized:
        wanted += list(REQUIRED_TOKENIZED)
    missing, empty = [], []
    for path in wanted:
        target = os.path.join(base, path.replace("/", os.sep))
        if not os.path.isfile(target):
            missing.append(path)
        elif os.path.getsize(target) == 0:
            empty.append(path)
    canonical = os.path.join(base, "notebooks", "colab_utils.py")
    _, names = module_symbols("colab_utils", canonical)
    return {
        "base": base,
        "checked": len(wanted),
        "missing": missing,
        "empty": empty,
        "colab_utils_missing_symbols": [s for s in COLAB_UTILS_SYMBOLS if s not in names],
        "ready": not missing and not empty,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap proyek ACOS")
    parser.add_argument("--base", help="paksa direktori proyek")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--no-drive", action="store_true")
    parser.add_argument("--no-tokenized", action="store_true")
    parser.add_argument("--preflight", action="store_true", help="hanya periksa, jangan unduh")
    parser.add_argument("--lenient", action="store_true", help="jangan melempar saat gagal")
    args = parser.parse_args()

    if args.preflight:
        print(json.dumps(preflight(args.base, include_tokenized=not args.no_tokenized),
                         indent=2, ensure_ascii=False))
        raise SystemExit(0)

    if args.base:
        os.makedirs(args.base, exist_ok=True)
        os.chdir(args.base)
    result = ensure_project(
        repo=args.repo,
        branch=args.branch,
        prefer_drive=not args.no_drive,
        include_tokenized=not args.no_tokenized,
        strict=not args.lenient,
    )
    raise SystemExit(0 if result.ok else 1)





