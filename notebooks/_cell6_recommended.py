# Rekomendasi pengganti CODE CELL [6] (cell index 9) pada
# notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb
#
# Prasyarat di memori: base_project_dir, save_dir (dari cell [5]), os, sys.
# extract_dir / notebooks_dir / data_root ikut dipulihkan sendiri di bawah,
# jadi cell ini tetap jalan walau cell [5] mati di tengah proses git clone.
#
# Kenapa cell lama gagal:
#   1. `except ModuleNotFoundError` tidak pernah menangkap kasus yang benar-benar
#      terjadi. Modul yang ADA tapi kekurangan nama melempar ImportError, dan
#      ImportError bukan subclass ModuleNotFoundError, jadi fallback-nya mati.
#   2. Impor yang gagal tetap meninggalkan modul di sys.modules, sehingga
#      percobaan impor kedua memakai salinan usang yang sama.
#   3. base_project_dir masuk sys.path lebih dulu daripada notebooks_dir, jadi
#      salinan colab_utils.py di root Drive menang balapan. Salinan di root Drive
#      berasal dari sesi lama dan bisa jauh lebih tua dari yang di notebooks/.
#   4. Kalau torch/seaborn belum ter-install, ModuleNotFoundError('torch') dari
#      dalam colab_utils ikut tertangkap, lalu file diunduh ulang tanpa guna dan
#      pesan errornya menyesatkan.

import re
import importlib

# Kontrak: 21 nama yang dipakai notebook. Kalau satu hilang, salinan itu ditolak.
REQUIRED_UTILS = (
    "setup_timestamped_run_dir", "download_bert_pretrained", "analyze_and_plot_eda",
    "plot_training_history", "export_benchmark_tables_and_plots",
    "display_quadruple_dataframe", "df_to_markdown", "export_step_table",
    "MarkdownReport", "SubtaskMetricCapture", "plot_subtask_metrics",
    "features_step1", "features_step2", "pair_examples_from_file",
    "resolve_eval_pair_file", "unpack_model_output",
    "detect_acos_project_root", "inspect_acos_drive_structure",
    "verify_session_save_paths", "find_resumable_session", "auto_find_file",
)

# 1. Pulihkan variabel path bila cell [5] berhenti sebelum barisnya tercapai
if "base_project_dir" not in globals() or not base_project_dir:
    base_project_dir = os.path.abspath(".")
if "save_dir" not in globals() or not save_dir:
    save_dir = os.path.join(base_project_dir, "Output")
if "extract_dir" not in globals() or not extract_dir:
    extract_dir = os.path.join(base_project_dir, "Extract-Classify-ACOS")
if "notebooks_dir" not in globals() or not notebooks_dir:
    notebooks_dir = os.path.join(base_project_dir, "notebooks")
if "data_root" not in globals() or not data_root:
    data_root = os.path.join(base_project_dir, "data")


def _utils_missing_symbols(path):
    """Nama publik yang tidak didefinisikan di satu file colab_utils.py.

    Membaca teks file, bukan mengimpornya: pemeriksaan ini harus tetap benar
    sebelum pip install selesai, karena colab_utils sendiri butuh torch.
    """
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return list(REQUIRED_UTILS)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    return [n for n in REQUIRED_UTILS
            if not re.search(r"^(?:def|class)\s+%s\b" % re.escape(n), src, re.M)]


def _prepend_sys_path(p):
    """Paksa p ke posisi terdepan walau sudah ada di urutan yang lebih rendah."""
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)


# 2. Pilih salinan colab_utils.py yang lengkap; notebooks/ diperiksa lebih dulu
_utils_candidates = [notebooks_dir, extract_dir, base_project_dir, os.getcwd()]
_utils_dir = None
_utils_report = []
for _d in _utils_candidates:
    _f = os.path.join(_d, "colab_utils.py")
    _miss = _utils_missing_symbols(_f)
    if os.path.isfile(_f):
        _utils_report.append((_f, _miss))
    if not _miss:
        _utils_dir = _d
        break

# 3. Unduh dari induk hanya kalau semua salinan lokal memang tidak layak
if _utils_dir is None:
    print("⚠️ Tidak ada salinan colab_utils.py yang lengkap. Mengunduh dari GitHub...")
    for _f, _miss in _utils_report:
        print(f"   ✗ {_f} — kurang {len(_miss)} simbol: {', '.join(_miss[:4])}...")
    import urllib.request
    _fresh_dir = os.path.join(base_project_dir, "_acos_utils")
    os.makedirs(_fresh_dir, exist_ok=True)
    _target = os.path.join(_fresh_dir, "colab_utils.py")
    for _url in (
        "https://raw.githubusercontent.com/haisyamalawwab/ACOS/main/notebooks/colab_utils.py",
        "https://raw.githubusercontent.com/haisyamalawwab/ACOS/main/colab_utils.py",
        "https://raw.githubusercontent.com/haisyamalawwab/ACOS/main/Extract-Classify-ACOS/colab_utils.py",
    ):
        try:
            urllib.request.urlretrieve(_url, _target)
        except Exception as _e:
            print(f"   ✗ gagal unduh {_url}: {_e}")
            continue
        if not _utils_missing_symbols(_target):
            _utils_dir = _fresh_dir
            print(f"   ✅ Berhasil: {_url}")
            break
        print(f"   ✗ {_url} juga belum lengkap.")
    if _utils_dir is None:
        raise RuntimeError(
            "colab_utils.py lengkap tidak ditemukan secara lokal maupun dari GitHub. "
            "Salin manual notebooks/colab_utils.py dari repo ke " + base_project_dir)

# 4. Sumber terpilih ditaruh paling depan agar salinan usang tidak membayangi
for _p in [notebooks_dir, extract_dir, base_project_dir, _utils_dir]:
    if os.path.isdir(_p):
        _prepend_sys_path(_p)

# 5. Impor bersih: buang cache lama supaya salinan usang tidak dipakai ulang
sys.modules.pop("colab_utils", None)
try:
    colab_utils = importlib.import_module("colab_utils")
except ModuleNotFoundError as _e:
    _dep = getattr(_e, "name", "") or ""
    if _dep and _dep != "colab_utils":
        raise RuntimeError(
            f"colab_utils butuh paket '{_dep}' yang belum ter-install. Jalankan "
            f"sel instalasi dependensi lebih dulu, lalu ulangi sel ini.") from _e
    raise

_missing_attr = [n for n in REQUIRED_UTILS if not hasattr(colab_utils, n)]
if _missing_attr:
    raise ImportError(
        f"colab_utils di {colab_utils.__file__} tidak punya: {_missing_attr}")
globals().update({n: getattr(colab_utils, n) for n in REQUIRED_UTILS})

print(f"🧩 colab_utils aktif       : {colab_utils.__file__}")
print(f"📂 Base Project Directory : {base_project_dir}")
print(f"📁 Extract & Model Dir     : {extract_dir}")
print(f"📁 Dataset Data Dir        : {data_root}")
print(f"📁 Output & Save Directory : {save_dir}")
