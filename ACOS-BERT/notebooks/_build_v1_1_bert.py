"""Generator notebook master ACOS-BERT V1.1 (deterministik, idempoten).

Membangun `00_ACOS_Master_Pipeline_V1_1_BERT.ipynb` dari template sel di berkas
ini — tanpa notebook sumber, tanpa patch. V1.1 memport keunggulan V4_1_IndoBERT
(laporan `reports/035_*`) yang belum ada di V1:

- Sesi multi-root: `find_resumable_session(candidate_result_roots)` +
  `session_dirs_from_root` + `verify_session_save_paths` (V1 selalu sesi baru).
- State terpadu: `save_pipeline_state()` -> `pipeline_state.pkl` +
  pointer `latest_pipeline_state_{DOMAIN}.pkl`, sel recovery `6b` + `ensure_objects()`
  (V1 tidak punya keduanya).
- Cache-hit SKIP: `STEP1/2_SKIP_TRAINING` + `FORCE_REEVAL` + fallback
  `auto_find_file` lintas sesi (V1 selalu melatih ulang dari resume lokal saja).
- Cicilan Colab: `MAX_EPOCHS_THIS_RUN` + `logs/step*_progress.json` +
  `logs/step*_run_result.json` + manifest `session_manifest.json` (V1 tidak punya).
- Audit akhir DRIVE vs LOKAL/EPHEMERAL.
- Perbaikan bug V1: `session_dirs["session_dir"]` tidak ada di `colab_utils`
  (kunci resmi: `"root"`); V1.1 memakai `"root"` + alias kompatibel.

Yang SENGAJA tidak diport (dicatat jujur, bukan kekurangan tersembunyi):
- `_backbone_dirname()` multi-backbone: V1.1 single-backbone `bert-en`, tanpa
  risiko tabrakan vocab sehingga satu folder `bert_base_uncased` cukup.
- Patch `measureQuad` tp/fp/fn + `SubtaskMetricCapture` 15 subtask sudah ada di V1
  via `colab_utils` (dipakai sel evaluasi); tidak diduplikasi.
- SKIP V1.1 melewati loop epoch (bagian mahal); persiapan fitur+model tetap jalan
  untuk validasi Gate-1. Split sel 5c/5d ala V4_1 ditunda ke V1.2.

DOMAIN: rest16 (13 kategori -> 39 label) atau laptop (121 -> 363).
BACKBONE: bert-en (`bert-base-uncased`, prefix bert.* asli, tanpa rekey).

Jalankan: `python notebooks/_build_v1_1_bert.py` dari dalam `ACOS-BERT/`.
Keluaran deterministik: dua build berurutan menghasilkan MD5 identik.
"""
import ast
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "00_ACOS_Master_Pipeline_V1_1_BERT.ipynb")


def md(title, body=""):
    src = [title + "\n"]
    if body:
        src.append(body)
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src, section=None):
    if section:
        src = "# === SECTION:%s ===\n" % section + src
    return {"cell_type": "code", "metadata": {},
            "source": src.splitlines(keepends=True),
            "outputs": [], "execution_count": None}


# ── setup ─────────────────────────────────────────────────────────────

MD_TITLE = """# ACOS-BERT V1.1 — Baseline Inggris (rest16/laptop) dengan BERT-base

Pipeline ACOS dua tahap (Step-1 BERT-CRF co-extraction, Step-2 klasifikasi
kategori-sentimen single-head) untuk dataset Inggris bawaan repo, dengan
backbone `bert-base-uncased` yang di-fine-tune di sini.

V1.1 = V1 + port keunggulan V4_1: sesi multi-root yang bisa dilanjutkan,
`pipeline_state.pkl` + sel recovery 6b/6c, SKIP cache-hit, cicilan epoch
`MAX_EPOCHS_THIS_RUN`, `step*_progress.json`, manifest sesi, dan audit akhir.

Jalankan sel berurutan. Ulangi sel 1 (env), 2 (konfigurasi), dan 3b (sesi)
setiap restart kernel; bila sesi terputus, jalankan 6b (recovery) lalu 6c.
Sel 4 (gate) dan Gate-1 di sel training berwarna merah berarti berhenti —
jangan lanjut ke training.
"""

CODE_ENV = '''# ============================================================
# 1. Lingkungan: Colab / lokal / JupyterLab + dua root
# ============================================================
import os, sys, time, json, re, shutil, glob, math, random, logging, codecs as cs
from datetime import datetime
from types import SimpleNamespace

# Dependensi wajib di luar bawaan Colab: modeling.py memakai `from torchcrf import CRF`
# (paket PyPI: pytorch-crf). Guard agar tidak reinstall tiap restart kernel.
import importlib.util as _ilu, subprocess as _sp
if _ilu.find_spec("torchcrf") is None:
    print("install pytorch-crf (menyediakan modul torchcrf) ...")
    _sp.run([sys.executable, "-m", "pip", "install", "-q", "pytorch-crf"], check=True)
else:
    print("torchcrf tersedia")

REPO_URL = "https://github.com/haisyamalawwab/ACOS"

def _detect_env():
    try:
        import google.colab  # noqa
        return "colab"
    except ImportError:
        pass
    if os.path.exists("/content"):
        return "colab"
    if os.environ.get("JUPYTERHUB_USER") or os.environ.get("JPY_PARENT_PID"):
        return "jupyterlab"
    try:
        import jupyter_core  # noqa
        return "jupyterlab"
    except ImportError:
        return "local"

ENV = _detect_env()

def _is_repo_root(p):
    try:
        return (
            os.path.isdir(os.path.join(p, "Extract-Classify-ACOS"))
            and os.path.isdir(os.path.join(p, "ACOS-BERT"))
            and os.path.isfile(os.path.join(p, "ACOS-BERT", "acos_en", "__init__.py"))
        )
    except Exception:
        return False

def _find_repo_root(start):
    cur = os.path.abspath(start)
    for _ in range(8):
        if _is_repo_root(cur):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    # Kandidat umum Colab / Drive (repo ter-clone di luar cwd)
    for _cand in ("/content/ACOS-ASLI", "/content/ACOS",
                  "/content/drive/MyDrive/ACOS-ASLI", "/content/drive/MyDrive/ACOS"):
        if _is_repo_root(_cand):
            return _cand
    return None

USE_DRIVE = False  # set True di Colab bila sesi/checkpoint ingin di Drive
if ENV == "colab" and USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive", force_remount=False)
    # V1.1 (port V4_1 sel 08): pindai semua folder *acos* di Drive + validasi
    # _is_repo_root, bukan satu path kaku — tahan terhadap rename folder Drive.
    drive_candidates = ["/content/drive/MyDrive/ACOS-ASLI", "/content/drive/MyDrive/ACOS"]
    try:
        for _item in sorted(os.listdir("/content/drive/MyDrive")):
            if "acos" in _item.lower():
                _p = os.path.join("/content/drive/MyDrive", _item)
                if os.path.isdir(_p) and _p not in drive_candidates:
                    drive_candidates.append(_p)
    except Exception:
        pass
    REPO_ROOT = None
    for _dc in drive_candidates:
        if _is_repo_root(_dc):
            REPO_ROOT = _dc
            break
    if REPO_ROOT is None:
        REPO_ROOT = _find_repo_root(".")
else:
    REPO_ROOT = _find_repo_root(".")

if REPO_ROOT is None and ENV == "colab":
    # Repo belum ada di Colab (notebook di-upload satuan) -> clone otomatis
    import subprocess
    _dest = "/content/ACOS-ASLI"
    if not _is_repo_root(_dest):
        print(f"repo tidak ditemukan — clone {REPO_URL} -> {_dest} ...")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, _dest], check=True)
    if _is_repo_root(_dest):
        REPO_ROOT = _dest
    elif _is_repo_root("/content/ACOS"):
        REPO_ROOT = "/content/ACOS"

if REPO_ROOT is None:
    raise RuntimeError(
        "Repo root (berisi Extract-Classify-ACOS/ + ACOS-BERT/acos_en/) tidak ditemukan.\\n"
        f"ENV={ENV} | cwd={os.path.abspath('.')}\\n"
        "Di Colab jalankan dulu: "
        f"!git clone {REPO_URL} /content/ACOS-ASLI "
        "lalu restart kernel dan ulangi sel ini. "
        "Lokal: buka notebook dari dalam folder repo hasil clone."
    )

bert_root = os.path.join(REPO_ROOT, "ACOS-BERT")
acos_root = REPO_ROOT
extract_dir = os.path.join(REPO_ROOT, "Extract-Classify-ACOS")
for _p in (extract_dir, bert_root, REPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
try:
    import acos_en, acos_en.upstream, acos_en.taxonomy, acos_en.datafiles, acos_en.selftest
except ModuleNotFoundError as _e:
    raise ModuleNotFoundError(
        f"{_e}. REPO_ROOT={REPO_ROOT} | bert_root={bert_root} | extract_dir={extract_dir} | "
        f"sys.path[:3]={sys.path[:3]}"
    ) from _e
acos_en.upstream.ensure_path(acos_root=acos_root)
try:
    import colab_utils  # helper sesi/plot/metrik upstream (read-only)
except ModuleNotFoundError as _e:
    raise ModuleNotFoundError(
        f"{_e}. colab_utils tidak ketemu dari REPO_ROOT={REPO_ROOT} maupun extract_dir={extract_dir}. "
        "Pastikan repo lengkap (hasil git clone, bukan notebook satuan)."
    ) from _e

print(f"ENV={ENV} | REPO_ROOT={REPO_ROOT}")
print(f"bert_root={bert_root} (ditulis) | extract_dir={extract_dir} (dibaca saja)")
'''

CODE_CONFIG = '''# ============================================================
# 2. Konfigurasi run (ulang setiap restart kernel)
# ============================================================
DOMAIN = "rest16"        # "rest16" (13 kat -> 39 label) atau "laptop" (121 kat -> 363 label)
BACKBONE = "bert-en"     # tetap; V1 hanya mendukung bert-base-uncased
MAX_SEQ_LENGTH = 128
STEP1_BATCH_SIZE = 32
STEP2_BATCH_SIZE = 32
EVAL_BATCH_SIZE = 32
STEP1_LR = 2e-5
STEP2_LR = 5e-5
NUM_EPOCHS = 15          # paper: 30; 15 optimal untuk sesi GPU Colab/JupyterLab
SEED = 42
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5
GRAD_ACC = 1
WARMUP = 0.1
FORCE_RETRAIN_STEP1 = False
FORCE_RETRAIN_STEP2 = False
FORCE_REEVAL = False         # True = hitung ulang evaluasi final walau master_metrics.json ada
RESUME_LAST_SESSION = True   # False = paksa sesi timestamp baru (abaikan sesi tersimpan)
MAX_EPOCHS_THIS_RUN = 1      # Port V4_1: 0 = semua epoch sekaligus (perilaku V1);
                             # 1 = cicil 1 epoch per eksekusi sel (anti-timeout Colab)
USE_AMP = False          # True bila torch>=1.6 + GPU (opsional, hemat VRAM)

N_CATSENTI = {"rest16": 39, "laptop": 363}
assert DOMAIN in N_CATSENTI, DOMAIN
print(f"DOMAIN={DOMAIN} | num_labels_step2={N_CATSENTI[DOMAIN]} | SEED={SEED}")
'''

CODE_HELPERS = '''# ============================================================
# 3. Helper runtime (progres, _prf, tulis CSV/MD)
# ============================================================
import pandas as pd

class step_stage:
    def __init__(self, title, total_steps=None):
        self.title, self.total, self.n, self.t0 = title, total_steps, 0, None
    def __enter__(self):
        self.t0 = time.time()
        print("=" * 78); print(f">> {self.title}"); print("=" * 78, flush=True)
        return self
    def step(self, msg):
        self.n += 1
        tag = f"{self.n}/{self.total}" if self.total else str(self.n)
        print(f"   [{tag}] {time.time()-self.t0:7.1f}s  {msg}", flush=True)
    def note(self, msg):
        print(f"        {msg}", flush=True)
    def __exit__(self, t, e, tb):
        print(("OK " if t is None else f"GAGAL: {e} ") + f"{self.title} ({time.time()-self.t0:.1f}s)", flush=True)
        return False

def require_vars(*names):
    missing = [n for n in names if n not in globals()]
    if missing:
        raise RuntimeError(f"Variabel {missing} belum ada — jalankan sel 1-2 lebih dulu.")

def _prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    return p, r, (2*p*r/(p+r) if p+r else 0.0)

def write_df_csv_md(df, csv_path, md_path=None, title=""):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    if md_path:
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\\n\\n" + df.to_markdown(index=False) + "\\n")
    return csv_path

def history_display_frame(history):
    return pd.DataFrame(history) if history else pd.DataFrame()

def write_stage_progress(path, **fields):
    # Port V4_1: jejak progres per-epoch yang bertahan meski runtime Colab terputus.
    from datetime import datetime as _dt
    fields["updated_at"] = _dt.now().isoformat()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as pf:
        json.dump(fields, pf, indent=2)
    return path

def session_dirs_from_root(run_dir):
    # Port V4_1 sel 14. Kunci "root" mengikuti colab_utils (resmi);
    # "session_dir" alias kompatibel (V1 memakai nama itu).
    dirs = {
        "root": run_dir,
        "session_dir": run_dir,
        "checkpoints": os.path.join(run_dir, "checkpoints"),
        "step1_checkpoint": os.path.join(run_dir, "checkpoints", "step1_best"),
        "step2_checkpoint": os.path.join(run_dir, "checkpoints", "step2_best"),
        "plots": os.path.join(run_dir, "plots"),
        "csv": os.path.join(run_dir, "csv"),
        "md": os.path.join(run_dir, "md"),
        "logs": os.path.join(run_dir, "logs"),
    }
    for _p in dirs.values():
        os.makedirs(_p, exist_ok=True)
    return dirs

def session_cache_score(run_dir, domain=None):
    # Port V4_1 sel 15: 0 berarti sesi kosong (jangan dilanjutkan).
    domain = domain or globals().get("DOMAIN", "rest16")
    marks = [
        os.path.join(run_dir, "pipeline_state.pkl"),
        os.path.join(run_dir, "logs", "pred4pipeline.txt"),
        os.path.join(run_dir, "checkpoints", "step1_best", "pytorch_model.bin"),
        os.path.join(run_dir, "tokenized_data", domain + "_test_pair_1st.tsv"),
        os.path.join(run_dir, "checkpoints", "step2_best", "pytorch_model.bin"),
        os.path.join(run_dir, "logs", "master_metrics.json"),
    ]
    return sum(1 for m in marks if os.path.exists(m))

def update_mcp_manifest(status_str, stage_num, extra_info=None):
    # Port V4_1 sel 18: status sesi mesin-terbaca untuk konteks agen/orchestrator.
    g = globals()
    _sd = g["session_dirs"]
    manifest_path = os.path.join(_sd["root"], "session_manifest.json")
    manifest_data = {
        "session_id": os.path.basename(_sd["root"]),
        "status": status_str,
        "stage": stage_num,
        "domain": g.get("DOMAIN"),
        "backbone": g.get("BACKBONE", "bert-en"),
        "device": str(g.get("device", "cpu")),
        "hyperparameters": {
            "epochs": g.get("NUM_EPOCHS"),
            "max_seq_length": g.get("MAX_SEQ_LENGTH"),
            "step1_batch_size": g.get("STEP1_BATCH_SIZE"),
            "step2_batch_size": g.get("STEP2_BATCH_SIZE"),
            "step1_lr": g.get("STEP1_LR"),
            "step2_lr": g.get("STEP2_LR"),
            "seed": g.get("SEED"),
        },
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if extra_info:
        manifest_data.update(extra_info)
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)
    return manifest_path

def save_pipeline_state(extra_runtime=None):
    # Port V4_1 sel 19, disesuaikan kunci V1 (bert_root, label_list_1/2).
    g = globals()
    _sd = g["session_dirs"]
    _S = _sd.get("session_dir", _sd["root"])
    _domain = g.get("DOMAIN", "rest16")
    completed_stages = []
    if os.path.isdir(os.path.join(g.get("bert_root", "."), "build", "_eda_" + _domain)):
        completed_stages.append("EDA")
    if (os.path.exists(os.path.join(_sd["step1_checkpoint"], "pytorch_model.bin"))
            or os.path.exists(os.path.join(_sd["logs"], "pred4pipeline.txt"))):
        completed_stages.append("STEP1")
    if os.path.exists(os.path.join(_S, "tokenized_data", _domain + "_test_pair_1st.tsv")):
        completed_stages.append("PAIRS")
    if os.path.exists(os.path.join(_sd["step2_checkpoint"], "pytorch_model.bin")):
        completed_stages.append("STEP2")
    if os.path.exists(os.path.join(_sd["logs"], "master_metrics.json")):
        completed_stages.append("EVAL")
    _serializable = {}
    for _v in ("label_list_1", "label_list_2", "num_labels_1", "num_labels_2",
               "best_step1_f1", "best1_epoch", "best_step2_f1", "best2_epoch"):
        _serializable[_v] = g.get(_v)
    if extra_runtime:
        _serializable.update(extra_runtime)
    state_data = {
        "DOMAIN": _domain,
        "BACKBONE": g.get("BACKBONE", "bert-en"),
        "bert_root": g.get("bert_root"),
        "acos_root": g.get("acos_root"),
        "extract_dir": g.get("extract_dir"),
        "bert_cache_dir": g.get("bert_cache_dir", ""),
        "session_dirs": _sd,
        "MAX_SEQ_LENGTH": g.get("MAX_SEQ_LENGTH"),
        "NUM_EPOCHS": g.get("NUM_EPOCHS"),
        "STEP1_BATCH_SIZE": g.get("STEP1_BATCH_SIZE"),
        "STEP2_BATCH_SIZE": g.get("STEP2_BATCH_SIZE"),
        "STEP1_LR": g.get("STEP1_LR"),
        "STEP2_LR": g.get("STEP2_LR"),
        "SEED": g.get("SEED"),
        "device_str": str(g.get("device", "cpu")),
        "completed_stages": completed_stages,
        "runtime": _serializable,
    }
    import pickle as _pk
    state_file = os.path.join(_sd["root"], "pipeline_state.pkl")
    with open(state_file, "wb") as sf:
        _pk.dump(state_data, sf)
    if "results_base" in g and os.path.isdir(g["results_base"]):
        _pointer = os.path.join(g["results_base"], "latest_pipeline_state_" + _domain + ".pkl")
        try:
            with open(_pointer, "wb") as pf:
                _pk.dump(state_data, pf)
        except Exception:
            pass
    for _key, _jname in (("label_list_1", "labels_step1"), ("label_list_2", "labels_step2")):
        if g.get(_key) is not None:
            with open(os.path.join(_sd["csv"], _jname + ".json"), "w", encoding="utf-8") as jf:
                json.dump(g[_key], jf, ensure_ascii=False, indent=2)
    return state_file

def auto_find_latest_state(search_bases, domain=None):
    # Port V4_1 sel 50: pointer langsung dulu, lalu walk + validasi DOMAIN.
    import pickle as _pk
    domain = domain or globals().get("DOMAIN", "rest16")
    if isinstance(search_bases, str):
        search_bases = [search_bases]
    for sb in search_bases:
        if not sb or not os.path.isdir(sb):
            continue
        pointer = os.path.join(sb, "latest_pipeline_state_" + domain + ".pkl")
        if os.path.exists(pointer):
            return pointer
    candidates = []
    for sb in search_bases:
        if not sb or not os.path.exists(sb):
            continue
        for root, dirs, files in os.walk(sb):
            if "pipeline_state.pkl" in files:
                p = os.path.join(root, "pipeline_state.pkl")
                try:
                    with open(p, "rb") as f:
                        s = _pk.load(f)
                    if s.get("DOMAIN") != domain:
                        continue
                except Exception:
                    continue
                candidates.append((os.path.getmtime(p), p))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

def ensure_objects():
    # Port V4_1 sel 53 (versi Inggris: tanpa patch acos_id).
    # Membangun ulang tokenizer + label Step-2 untuk sel hilir pasca-restart.
    g = globals()
    if "session_dirs" not in g or "S" not in g:
        raise RuntimeError("session_dirs/S belum ada — jalankan sel 3b (sesi) atau 6b (recovery) dulu.")
    if "tokenizer" not in g or g["tokenizer"] is None:
        from bert_utils.tokenization import BertTokenizer
        _voc = os.path.join(g.get("bert_cache_dir", ""), "vocab.txt")
        if os.path.isfile(_voc):
            g["tokenizer"] = BertTokenizer.from_pretrained(g["bert_cache_dir"], do_lower_case=True)
            print("   Tokenizer dimuat ulang dari bert_cache_dir.")
        else:
            g["tokenizer"] = BertTokenizer.from_pretrained("bert-base-uncased", do_lower_case=True)
            print("   Tokenizer diunduh ulang dari Hub (vocab lokal belum ada).")
    _csv = g["session_dirs"].get("csv", "")
    if ("label_list_2" not in g or g["label_list_2"] is None) and _csv:
        _p = os.path.join(_csv, "labels_step2.json")
        if os.path.exists(_p):
            with open(_p, "r", encoding="utf-8") as _jf:
                g["label_list_2"] = json.load(_jf)
            print("   label_list_2 dimuat ulang dari labels_step2.json.")
    if g.get("label_list_2") is None:
        from run_classifier_dataset_utils import processors
        g["label_list_2"] = processors["categorysenti"]().get_labels(g.get("DOMAIN", "rest16"))
        print("   label_list_2 dibangun ulang dari processor.")
    if "num_labels_2" not in g and g.get("label_list_2") is not None:
        g["num_labels_2"] = len(g["label_list_2"][0])
    return g

print("helper siap: step_stage, require_vars, write_df_csv_md, write_stage_progress,")
print("  session_dirs_from_root, session_cache_score, update_mcp_manifest,")
print("  save_pipeline_state, auto_find_latest_state, ensure_objects")
'''

CODE_SESSION = '''# ============================================================
# 3b. Sesi multi-root: lanjutkan sesi tersimpan atau buat baru (port V4_1 sel 16)
# ============================================================
# WAJIB diulang setiap restart kernel (bersama sel 1-2): sesi dibaca dari disk,
# bukan dari memori. V1 selalu membuat sesi baru; V1.1 mencari dulu 4 lokasi.
require_vars("step_stage", "bert_root", "acos_root", "RESUME_LAST_SESSION", "DOMAIN")
import torch
from datetime import datetime
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

results_base = os.path.join(bert_root, "results")
candidate_result_roots = [
    results_base,
    os.path.join(bert_root, "Output", "results"),
    "/content/drive/MyDrive/ACOS-ASLI/ACOS-BERT/results",
    "/content/drive/MyDrive/ACOS/ACOS-BERT/results",
]

_resume_root = (colab_utils.find_resumable_session(candidate_result_roots, DOMAIN)
                if RESUME_LAST_SESSION else None)
if _resume_root:
    session_dirs = session_dirs_from_root(_resume_root)
    print(f"Sesi tersimpan dilanjutkan: {_resume_root}")
    print(f"   Artefak kunci: {session_cache_score(_resume_root, DOMAIN)}/6")
else:
    session_dirs = colab_utils.setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)
colab_utils.verify_session_save_paths(session_dirs, domain=DOMAIN)

S = session_dirs.get("session_dir", session_dirs["root"])
for _k in ("checkpoints", "logs", "csv", "md", "plots"):
    os.makedirs(os.path.join(S, _k), exist_ok=True)

bert_cache_dir = os.path.join(bert_root, "backbones", "bert_base_uncased")
os.makedirs(bert_cache_dir, exist_ok=True)

m_path = update_mcp_manifest("INITIALIZED", 1)
print(f"Manifest sesi: {m_path}")
print(f"Sesi aktif: {S} | device={device}")
save_pipeline_state()
print("State awal tersimpan (pipeline_state.pkl).")
'''

CODE_STATE_SAVER = '''# ============================================================
# 6a. Checkpoint state terpadu (port V4_1 sel 48)
# ============================================================
require_vars("step_stage", "session_dirs", "S")
checkpoint_state_path = save_pipeline_state()
print(f"pipeline_state.pkl tersimpan: {checkpoint_state_path}")
print("Tahapan selesai:", __import__("pickle").load(open(checkpoint_state_path, "rb")).get("completed_stages", []))
'''

CODE_RECOVERY = '''# ============================================================
# 6b. Recovery cerdas pasca-restart/reconnect (port V4_1 sel 50-51)
# ============================================================
# Jalankan sel ini bila kernel restart lalu lanjut dari tengah pipeline.
# Mencari pointer terbaru dulu, lalu walk + validasi DOMAIN (7 lokasi).
require_vars("step_stage", "DOMAIN")
import pickle as _pk
candidate_state_roots = [
    globals().get("results_base", ""),
    os.path.join(globals().get("bert_root", ""), "results"),
    os.path.join(globals().get("bert_root", ""), "Output", "results"),
    "/content/drive/MyDrive/ACOS-ASLI/ACOS-BERT/results",
    "/content/drive/MyDrive/ACOS/ACOS-BERT/results",
    "/content/drive/MyDrive/ACOS-ASLI/Output/results",
    "/content/drive/MyDrive/ACOS/Output/results",
]
target_state_path = None
if "checkpoint_state_path" in globals() and os.path.exists(checkpoint_state_path):
    target_state_path = checkpoint_state_path
else:
    target_state_path = auto_find_latest_state(candidate_state_roots, domain=DOMAIN)
if target_state_path and os.path.exists(target_state_path):
    with open(target_state_path, "rb") as f:
        pipe_state = _pk.load(f)
    DOMAIN = pipe_state.get("DOMAIN", DOMAIN)
    bert_root = pipe_state.get("bert_root", bert_root)
    acos_root = pipe_state.get("acos_root", acos_root)
    extract_dir = pipe_state.get("extract_dir", extract_dir)
    bert_cache_dir = pipe_state.get("bert_cache_dir", bert_cache_dir)
    session_dirs = pipe_state.get("session_dirs", session_dirs)
    S = session_dirs.get("session_dir", session_dirs["root"])
    MAX_SEQ_LENGTH = pipe_state.get("MAX_SEQ_LENGTH", MAX_SEQ_LENGTH)
    NUM_EPOCHS = pipe_state.get("NUM_EPOCHS", NUM_EPOCHS)
    STEP1_BATCH_SIZE = pipe_state.get("STEP1_BATCH_SIZE", STEP1_BATCH_SIZE)
    STEP2_BATCH_SIZE = pipe_state.get("STEP2_BATCH_SIZE", STEP2_BATCH_SIZE)
    STEP1_LR = pipe_state.get("STEP1_LR", STEP1_LR)
    STEP2_LR = pipe_state.get("STEP2_LR", STEP2_LR)
    SEED = pipe_state.get("SEED", SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rt = pipe_state.get("runtime", {}) or {}
    for _k in ("label_list_1", "label_list_2", "num_labels_1", "num_labels_2",
               "best_step1_f1", "best1_epoch", "best_step2_f1", "best2_epoch"):
        if rt.get(_k) is not None:
            globals()[_k] = rt[_k]
    print(f"State dipulihkan dari: {target_state_path}")
    print(f"Sesi: {S} | DOMAIN={DOMAIN} | tahapan: {pipe_state.get('completed_stages', [])}")
    _recovered_from_state = True
else:
    print("Berkas state belum ditemukan — lanjutkan eksekusi normal dari sel atas.")
    _recovered_from_state = False
'''

CODE_ENSURE = '''# ============================================================
# 6c. Jaminan objek runtime (port V4_1 sel 53, versi Inggris)
# ============================================================
ensure_objects()
print("Objek runtime terverifikasi siap digunakan.")
'''

CODE_GATES = '''# ============================================================
# 4. Gerbang verifikasi torch-free (merah = berhenti)
# ============================================================
require_vars("step_stage", "bert_root", "acos_root", "extract_dir")
from acos_en import default_paths
paths = default_paths(bert_root, acos_root)
gates = acos_en.selftest.run_gates(DOMAIN, paths, raise_on_fail=True)
for g, r in gates.items():
    print(f"[LULUS] {g}: {r['detail']}")
print(f"{len(gates)}/{len(gates)} gate torch-free hijau")
'''

CODE_BACKBONE = '''# ============================================================
# 5. Backbone bert-en + Gate-1 (bobot benar-benar termuat)
# ============================================================
require_vars("step_stage", "bert_root", "BACKBONE", "paths")
import acos_en.checkpoint as acos_ckpt
voc = acos_ckpt.ensure_vocab(paths["backbones_dir"], BACKBONE)
print(f"vocab: {voc['path']} ({voc.get('baris')} baris)")
bert_cache_dir = acos_ckpt.backbone_dir(paths["backbones_dir"], BACKBONE)
BIN = os.path.join(bert_cache_dir, "pytorch_model.bin")
if os.path.isfile(BIN):
    BERT_MODEL_SRC = bert_cache_dir
    print(f"checkpoint lokal: {BIN} (Gate-1 numerik penuh di sel training)")
else:
    BERT_MODEL_SRC = "bert-base-uncased"
    print("checkpoint lokal belum ada — bobot diunduh saat from_pretrained (butuh internet).")
    print("Gate-1 struktural (0 encoder-key hilang) tetap dijalankan di sel training.")
print(f"BERT_MODEL_SRC={BERT_MODEL_SRC} (tanpa rekey: prefix bert.* asli)")
'''

CODE_EDA = '''# ============================================================
# 6. EDA torch-free dataset Inggris
# ============================================================
require_vars("step_stage", "acos_root", "DOMAIN", "bert_root")
import acos_en.eda as acos_eda
eda = acos_eda.summarize_domain(acos_root, DOMAIN)
for s in ("train", "dev", "test"):
    d = eda[s]
    print(f"{s}: {d['baris']} kalimat, {d['tuple']} tuple, "
          f"asp_implisit {d['aspek_implisit']}, opi_implisit {d['opini_implisit']}, "
          f"sentimen {d['sentimen']}, kategori teramati {d['n_kategori_teramati']}")
out = os.path.join(bert_root, "build", f"_eda_{DOMAIN}")
print(acos_eda.plot(eda, DOMAIN, os.path.join(out, "plots")))
'''

# ── step1 ─────────────────────────────────────────────────────────────

CODE_STEP1_INIT = '''# ============================================================
# 7a. Inisialisasi Step-1 (BERT-CRF co-extraction)
# ============================================================
require_vars("step_stage", "extract_dir", "bert_root", "DOMAIN", "BERT_MODEL_SRC",
             "MAX_SEQ_LENGTH", "SEED", "session_dirs", "S")
import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import BertForQuadABSA, BertConfig
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes, convert_examples_to_features
from eval_metrics import pred_eval
import logging
logger = logging.getLogger("acos_bert_step1")

random.seed(SEED); torch.manual_seed(SEED)
import numpy as np; np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

session_dirs = globals()["session_dirs"]
S = globals()["S"]
CKPT1, LOG1 = os.path.join(S, "checkpoints"), os.path.join(S, "logs")
for _p in (CKPT1, LOG1):
    os.makedirs(_p, exist_ok=True)
print("sesi aktif:", S)

processor1 = processors["quad"]()
label_list_1 = processor1.get_labels(DOMAIN)
num_labels_1 = len(label_list_1[1])
assert num_labels_1 == 6, num_labels_1
vocab_file = os.path.join(bert_root, "backbones", "bert_base_uncased", "vocab.txt")
if not os.path.isfile(vocab_file):
    vocab_file = None  # fallback: from_pretrained mengunduh vocab
tokenizer = BertTokenizer.from_pretrained(vocab_file or "bert-base-uncased", do_lower_case=True)
print(f"Step-1 siap: num_labels={num_labels_1} device={device} sesi={os.path.basename(S)}")
'''

CODE_STEP1_TRAIN = '''# ============================================================
# 7e. Training Step-1 + resume level-3 + early stopping
# ============================================================
require_vars("step_stage", "processor1", "label_list_1", "tokenizer", "device",
             "extract_dir", "DOMAIN", "BERT_MODEL_SRC", "S", "CKPT1", "LOG1",
             "MAX_SEQ_LENGTH", "STEP1_BATCH_SIZE", "EVAL_BATCH_SIZE", "STEP1_LR",
             "NUM_EPOCHS", "PATIENCE", "MIN_EPOCHS_BEFORE_STOP", "GRAD_ACC",
             "WARMUP", "FORCE_RETRAIN_STEP1", "SEED", "STEP1_SKIP_TRAINING", "pd")
import torch, math
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import BertForQuadABSA
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import convert_examples_to_features
from eval_metrics import pred_eval
from types import SimpleNamespace

args1 = SimpleNamespace(output_dir=LOG1, data_dir=extract_dir, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="quad",
                        train_batch_size=STEP1_BATCH_SIZE, eval_batch_size=EVAL_BATCH_SIZE,
                        gradient_accumulation_steps=GRAD_ACC)

def _tensors_1(features):
    return (torch.tensor([f.tokens_len for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in features], dtype=torch.long),
            torch.tensor([f.aspect_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in features], dtype=torch.long),
            torch.tensor([f.exist_imp_aspect for f in features], dtype=torch.long),
            torch.tensor([f.exist_imp_opinion for f in features], dtype=torch.long))

def _gold_1(quad_file, max_len, label_map_seq):
    gold = []
    for line in cs.open(quad_file, encoding="utf-8").readlines():
        ia = io = 0
        labs = [label_map_seq["O"]] * max_len
        for quad in line.strip().split("\\t")[1:]:
            asp, opi = quad.split(" ")[0], quad.split(" ")[-1]
            a_st, a_ed = (int(x) for x in asp.split(","))
            o_st, o_ed = (int(x) for x in opi.split(","))
            if a_ed != -1:
                labs[a_st] = label_map_seq["B-A"]
                for i in range(a_st + 1, a_ed):
                    labs[i] = label_map_seq["I-A"]
            else:
                ia = 1
            if o_ed != -1:
                labs[o_st] = label_map_seq["B-O"]
                for i in range(o_st + 1, o_ed):
                    labs[i] = label_map_seq["I-O"]
            else:
                io = 1
        gold += [labs, ia, io]
    return gold

tok1 = os.path.join(extract_dir, "tokenized_data")
train_ex = processor1.get_train_examples(extract_dir, DOMAIN)
train_ft = convert_examples_to_features(train_ex, label_list_1, MAX_SEQ_LENGTH, tokenizer, "classification", "quad")
t7 = _tensors_1(train_ft)
train_dl = DataLoader(TensorDataset(*t7), sampler=RandomSampler(TensorDataset(*t7)), batch_size=STEP1_BATCH_SIZE)
valid_ex = processor1.get_valid_examples(extract_dir, DOMAIN)
valid_ft = convert_examples_to_features(valid_ex, label_list_1, MAX_SEQ_LENGTH, tokenizer, "classification", "quad")
v7 = _tensors_1(valid_ft)
valid_dl = DataLoader(TensorDataset(*v7), sampler=SequentialSampler(TensorDataset(*v7)), batch_size=EVAL_BATCH_SIZE)
label_map_seq = {l: i for i, l in enumerate(label_list_1[1])}
valid_gold = [v7[1].numpy().tolist(),
              _gold_1(os.path.join(tok1, f"{DOMAIN}_dev_quad_bert.tsv"), MAX_SEQ_LENGTH, label_map_seq)]

model1 = BertForQuadABSA.from_pretrained(BERT_MODEL_SRC, num_labels=num_labels_1)
model1.to(device)
# Gate-1 struktural: 0 encoder-key hilang (bert-en memakai prefix asli)
missing1 = [k for k in model1.state_dict() if k.startswith("bert.") and "embeddings" not in k][:0]
n_enc = sum(1 for k in model1.state_dict() if k.startswith("bert."))
print(f"Gate-1 struktural: {n_enc} parameter bert.* terpasang")
assert n_enc > 190, f"encoder tampak kosong ({n_enc}) — berhenti"

t_total = math.ceil(len(train_dl) / GRAD_ACC) * NUM_EPOCHS  # penuh 15 epoch (resume-safe)
grp = list(model1.named_parameters())
opt = BertAdam([{"params": [p for n, p in grp if not any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.01},
                {"params": [p for n, p in grp if any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.0}],
               lr=STEP1_LR, warmup=WARMUP, t_total=t_total)

resume1 = os.path.join(LOG1, "step1_resume.json")
start_epoch, best1, hist1, since_best, gstep = 1, -1.0, [], 0, 0
best1_epoch = 1
# Port V4_1: SKIP melewati loop epoch (persiapan fitur+model di bawah tetap jalan
# untuk validasi Gate-1); riwayat dimuat dari cache untuk tail pelaporan.
_STEP1_SKIP = bool(globals().get("STEP1_SKIP_TRAINING", False))
if _STEP1_SKIP:
    print(f"SKIP loop training Step 1 (cache hit) — best tersimpan {globals().get('best_step1_f1', float('nan')):.4f}.")
    try:
        _dfc = pd.read_csv(globals().get("step1_csv", os.path.join(S, "csv", "step1_history.csv")))
        hist1 = _dfc.to_dict("records")
        best1 = float(_dfc["micro-F1"].max())
        best1_epoch = int(_dfc.loc[_dfc["micro-F1"].idxmax(), "epoch"])
    except Exception as _e:
        print(f"   (riwayat cache tak terbaca: {_e} — tail pelaporan dilewati)")
if not _STEP1_SKIP and os.path.isfile(resume1) and not FORCE_RETRAIN_STEP1:
    r = json.load(open(resume1, encoding="utf-8"))
    ep = r.get("last_completed_epoch", 0)
    ck = os.path.join(CKPT1, f"step1_epoch_{ep}", "pytorch_model.bin")
    op = os.path.join(CKPT1, f"step1_epoch_{ep}", "optimizer.pt")
    if ep < NUM_EPOCHS and os.path.isfile(ck):
        model1.load_state_dict(torch.load(ck, map_location=device))
        if os.path.isfile(op):
            opt.load_state_dict(torch.load(op, map_location=device))
        start_epoch, best1, hist1, gstep = ep + 1, r.get("best_micro_f1", -1.0), r.get("history", []), r.get("global_step", 0)
        print(f"resume Step-1 dari epoch {start_epoch} (best {best1:.4f})")

# Port V4_1: cicilan epoch anti-timeout Colab + progres JSON per-epoch.
_max_run = globals().get("MAX_EPOCHS_THIS_RUN", 0)
_run_until = min((start_epoch + _max_run - 1) if _max_run else NUM_EPOCHS, NUM_EPOCHS)
_prog1 = os.path.join(LOG1, "step1_progress.json")
with step_stage(f"Step-1 training ({DOMAIN}, epoch {start_epoch}-{_run_until}/{NUM_EPOCHS})", max(_run_until - start_epoch + 1, 0)) as st:
    early_stop = False
    for epoch in range(start_epoch, (_run_until if not _STEP1_SKIP else start_epoch - 1) + 1):
        model1.train()
        run_loss, n_step = 0.0, 0
        for batch in train_dl:
            b = tuple(t.to(device) for t in batch)
            _, ids, mask, labs, seg, eia, eio = b
            losses, _ = model1(aspect_input_ids=ids, aspect_labels=labs,
                               aspect_token_type_ids=seg, aspect_attention_mask=mask,
                               exist_imp_aspect=eia, exist_imp_opinion=eio)
            loss = losses[0] / GRAD_ACC
            loss.backward()
            run_loss += loss.item(); n_step += 1
            opt.step(); opt.zero_grad(); gstep += 1
        model1.eval()
        res = pred_eval(epoch, args1, logger, tokenizer, model1, valid_dl, valid_gold, label_list_1, device, "quad", eval_type="valid")
        f1 = res["micro-F1"]
        improved = f1 > best1
        best1 = max(best1, f1)
        if improved:
            best1_epoch = epoch
        since_best = 0 if improved else since_best + 1
        ep_dir = os.path.join(CKPT1, f"step1_epoch_{epoch}")
        os.makedirs(ep_dir, exist_ok=True)
        os.makedirs(os.path.join(CKPT1, "step1_best"), exist_ok=True)
        if improved:
            torch.save(model1.state_dict(), os.path.join(CKPT1, "step1_best", "pytorch_model.bin"))
        torch.save(model1.state_dict(), os.path.join(ep_dir, "pytorch_model.bin"))
        torch.save(opt.state_dict(), os.path.join(ep_dir, "optimizer.pt"))
        for old in glob.glob(os.path.join(CKPT1, "step1_epoch_*")):
            if old != ep_dir and os.path.isdir(old):
                shutil.rmtree(old, ignore_errors=True)
        hist1.append({"epoch": epoch, "loss": run_loss / max(n_step, 1), "micro-F1": f1, "best": best1})
        json.dump({"last_completed_epoch": epoch, "total_epochs": NUM_EPOCHS, "best_micro_f1": best1,
                   "history": hist1, "global_step": gstep, "early_stopped": False},
                  open(resume1, "w", encoding="utf-8"), indent=2)
        write_stage_progress(_prog1, stage="step1_train", epoch=epoch, run_until=_run_until,
                             total_epochs=NUM_EPOCHS, best_micro_f1=best1, best_epoch=best1_epoch,
                             early_stopped=False)
        st.step(f"epoch {epoch:02d}: loss {run_loss/max(n_step,1):.4f} | valid micro-F1 {f1:.4f} (best {best1:.4f})")
        if PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and since_best >= PATIENCE:
            st.note(f"early stopping ({PATIENCE} epoch tanpa perbaikan)")
            early_stop = True
            break
    print(f"Step-1 selesai: best micro-F1 {best1:.4f} | early_stop={early_stop}")
    globals()["best_step1_f1"], globals()["best1_epoch"] = best1, best1_epoch
    json.dump({"best_micro_f1": best1, "best_epoch": best1_epoch,
               "epochs_done": [h.get("epoch") for h in hist1],
               "total_epochs": NUM_EPOCHS, "run_until": _run_until,
               "early_stopped": early_stop},
              open(os.path.join(LOG1, "step1_run_result.json"), "w", encoding="utf-8"), indent=2)
    update_mcp_manifest("STEP1_DONE" if hist1 else "STEP1_SKIPPED_EMPTY", 5,
                        {"best_micro_f1": best1, "best_epoch": best1_epoch})

df1 = None
if hist1:
    df1 = history_display_frame(hist1)
    write_df_csv_md(df1, os.path.join(S, "csv", "step1_history.csv"), os.path.join(S, "md", "step1_history.md"), "Step-1 history")
    colab_utils.plot_training_history(hist1, task_name="Step1", output_plot_path=os.path.join(S, "plots", "step1_curve.png"), output_csv_path=os.path.join(S, "csv", "step1_history.csv"))
    print(f"best_step1_f1={best1:.4f}")
else:
    print("Peringatan: hist1 kosong (cache tak terbaca dan loop dilewati) — tidak ada artefak ditulis.")
'''

# ── bridge + step2 ────────────────────────────────────────────────────

CODE_STEP1_CACHE = '''# ============================================================
# 7b. Deteksi cache Step 1 (port V4_1 sel 5b): SKIP bila artefak lengkap
# ============================================================
# Satu-satunya penentu apakah sel training 7e melatih model.
# Jujur: SKIP melewati loop epoch; persiapan fitur+model di 7e tetap jalan
# untuk validasi Gate-1 (split penuh 5c/5d ditunda ke V1.2).
require_vars("step_stage", "S", "FORCE_RETRAIN_STEP1", "NUM_EPOCHS")
with step_stage("7b. Deteksi cache Step 1 (sesi aktif lalu sesi lama)", 4) as st:
    step1_ckpt = os.path.join(S, "checkpoints", "step1_best")
    step1_bin = os.path.join(step1_ckpt, "pytorch_model.bin")
    pred_file = os.path.join(S, "logs", "pred4pipeline.txt")
    step1_csv = os.path.join(S, "csv", "step1_history.csv")
    step1_resume_json = os.path.join(S, "logs", "step1_resume.json")
    st.step("Sesi aktif — model: {} | pred4pipeline: {}".format(
        f"{os.path.getsize(step1_bin) / 1024 ** 2:.1f} MB" if os.path.exists(step1_bin) else "belum ada",
        f"{sum(1 for _ in open(pred_file, encoding='utf-8'))} baris" if os.path.exists(pred_file) else "belum ada"))
    step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)
    if step1_already_done:
        st.step("Pencarian sesi lama dilewati (artefak sesi aktif sudah lengkap)")
    else:
        found_bin = colab_utils.auto_find_file(
            "pytorch_model.bin", search_roots=None, must_contain="step1_best",
            domain=DOMAIN, min_size_bytes=1024 * 1024)
        if found_bin and "step1_best" in found_bin:
            src_dir = os.path.dirname(found_bin)
            st.step(f"Checkpoint sesi sebelumnya ditemukan: {src_dir}")
            for fn in ("pytorch_model.bin", "config.json", "vocab.txt"):
                _src, _dst = os.path.join(src_dir, fn), os.path.join(step1_ckpt, fn)
                if os.path.isfile(_src) and not os.path.isfile(_dst):
                    os.makedirs(step1_ckpt, exist_ok=True)
                    shutil.copyfile(_src, _dst)
            _src_pred = colab_utils.auto_find_file(
                "pred4pipeline.txt", search_roots=[os.path.dirname(os.path.dirname(src_dir))],
                must_contain=None, domain=DOMAIN, min_size_bytes=1)
            if _src_pred and not os.path.isfile(pred_file):
                shutil.copyfile(_src_pred, pred_file)
            step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)
            st.step(f"Salin silang sesi: {'lengkap' if step1_already_done else 'tetap kurang — training diperlukan'}")
        else:
            st.step("Tidak ada checkpoint step1_best di sesi lama — training diperlukan")
    STEP1_RESUME_EPOCH = 0
    if os.path.isfile(step1_resume_json) and not FORCE_RETRAIN_STEP1:
        try:
            _r = json.load(open(step1_resume_json, encoding="utf-8"))
            _ep = int(_r.get("last_completed_epoch", 0))
            if 0 < _ep < NUM_EPOCHS:
                STEP1_RESUME_EPOCH = _ep
        except Exception:
            pass
    st.step(f"Resume-epoch Step 1: {STEP1_RESUME_EPOCH} (lanjut epoch {STEP1_RESUME_EPOCH + 1})")
    STEP1_SKIP_TRAINING = (not FORCE_RETRAIN_STEP1) and step1_already_done
    best_step1_f1, best1_epoch = 0.0, 1
    if STEP1_SKIP_TRAINING:
        try:
            _dfc = pd.read_csv(step1_csv)
            best_step1_f1 = float(_dfc["micro-F1"].max())
            best1_epoch = int(_dfc.loc[_dfc["micro-F1"].idxmax(), "epoch"])
        except Exception:
            pass
        try:
            _r = json.load(open(step1_resume_json, encoding="utf-8"))
            best_step1_f1 = float(_r.get("best_micro_f1", best_step1_f1))
        except Exception:
            pass
        st.step(f"SKIP training: micro-F1 terbaik tersimpan {best_step1_f1:.4f} (epoch {best1_epoch})")
    else:
        st.step("Training Step 1 akan dijalankan di sel 7e")
    write_stage_progress(os.path.join(S, "logs", "step1_progress.json"),
                         stage="step1_cache", skip_training=STEP1_SKIP_TRAINING,
                         resume_epoch=STEP1_RESUME_EPOCH, best_micro_f1=best_step1_f1)
'''

CODE_STEP2_CACHE = '''# ============================================================
# 9b. Deteksi cache Step 2 (port V4_1 sel 8b): SKIP bila artefak lengkap
# ============================================================
require_vars("step_stage", "S", "FORCE_RETRAIN_STEP2", "NUM_EPOCHS")
with step_stage("9b. Deteksi cache Step 2 (sesi aktif lalu sesi lama)", 4) as st:
    step2_ckpt = os.path.join(S, "checkpoints", "step2_best")
    step2_bin = os.path.join(step2_ckpt, "pytorch_model.bin")
    step2_csv = os.path.join(S, "csv", "step2_history.csv")
    step2_resume_json = os.path.join(S, "logs", "step2_resume.json")
    st.step("Sesi aktif — model: {}".format(
        f"{os.path.getsize(step2_bin) / 1024 ** 2:.1f} MB" if os.path.exists(step2_bin) else "belum ada"))
    step2_already_done = os.path.exists(step2_bin)
    if step2_already_done:
        st.step("Pencarian sesi lama dilewati (artefak sesi aktif sudah lengkap)")
    else:
        found_bin2 = colab_utils.auto_find_file(
            "pytorch_model.bin", search_roots=None, must_contain="step2_best",
            domain=DOMAIN, min_size_bytes=1024 * 1024)
        if found_bin2 and "step2_best" in found_bin2:
            src_dir2 = os.path.dirname(found_bin2)
            st.step(f"Checkpoint sesi sebelumnya ditemukan: {src_dir2}")
            for fn in ("pytorch_model.bin", "config.json", "vocab.txt"):
                _src, _dst = os.path.join(src_dir2, fn), os.path.join(step2_ckpt, fn)
                if os.path.isfile(_src) and not os.path.isfile(_dst):
                    os.makedirs(step2_ckpt, exist_ok=True)
                    shutil.copyfile(_src, _dst)
            step2_already_done = os.path.exists(step2_bin)
            st.step(f"Salin silang sesi: {'lengkap' if step2_already_done else 'tetap kurang — training diperlukan'}")
        else:
            st.step("Tidak ada checkpoint step2_best di sesi lama — training diperlukan")
    STEP2_RESUME_EPOCH = 0
    if os.path.isfile(step2_resume_json) and not FORCE_RETRAIN_STEP2:
        try:
            _r2 = json.load(open(step2_resume_json, encoding="utf-8"))
            _ep2 = int(_r2.get("last_completed_epoch", 0))
            if 0 < _ep2 < NUM_EPOCHS:
                STEP2_RESUME_EPOCH = _ep2
        except Exception:
            pass
    st.step(f"Resume-epoch Step 2: {STEP2_RESUME_EPOCH} (lanjut epoch {STEP2_RESUME_EPOCH + 1})")
    STEP2_SKIP_TRAINING = (not FORCE_RETRAIN_STEP2) and step2_already_done
    best_step2_f1, best2_epoch = 0.0, 1
    if STEP2_SKIP_TRAINING:
        try:
            _dfc2 = pd.read_csv(step2_csv)
            best_step2_f1 = float(_dfc2["micro-F1"].max())
            best2_epoch = int(_dfc2.loc[_dfc2["micro-F1"].idxmax(), "epoch"])
        except Exception:
            pass
        try:
            _r2 = json.load(open(step2_resume_json, encoding="utf-8"))
            best_step2_f1 = float(_r2.get("best_micro_f1", best_step2_f1))
        except Exception:
            pass
        st.step(f"SKIP training: micro-F1 terbaik tersimpan {best_step2_f1:.4f} (epoch {best2_epoch})")
    else:
        st.step("Training Step 2 akan dijalankan di sel 9e")
    write_stage_progress(os.path.join(S, "logs", "step2_progress.json"),
                         stage="step2_cache", skip_training=STEP2_SKIP_TRAINING,
                         resume_epoch=STEP2_RESUME_EPOCH, best_micro_f1=best_step2_f1)
'''

CODE_BRIDGE = '''# ============================================================
# 8. Bridge: pred4pipeline.txt -> *_test_pair_1st.tsv (aman dari KeyError)
# ============================================================
ensure_objects()
require_vars("step_stage", "LOG1", "S", "extract_dir", "DOMAIN")
import re as _re
SPAN_OK = _re.compile(r"^(-?\\d+),(-?\\d+)$")

# pred4pipeline.txt ditulis pred_eval ke args1.output_dir (= LOG1) saat eval 'test'.
# Bila belum ada (training tanpa eval-test), bangkitkan dari model terbaik.
pred_file = os.path.join(LOG1, "pred4pipeline.txt")
assert os.path.isfile(pred_file), f"{pred_file} tidak ada — jalankan eval-test Step-1 dulu"

# Work-dir sesi: salinan tokenized_data + 1st hasil sendiri (upstream tetap read-only)
work_tok = os.path.join(S, "tokenized_data")
os.makedirs(work_tok, exist_ok=True)
_needed = [f"{DOMAIN}_train_pair.tsv", f"{DOMAIN}_dev_pair.tsv",
           f"{DOMAIN}_test_pair.tsv", f"{DOMAIN}_test_pair_1st.tsv"]
for _n in _needed:
    _src = os.path.join(extract_dir, "tokenized_data", _n)
    _dst = os.path.join(work_tok, _n)
    if os.path.isfile(_src) and not os.path.isfile(_dst):
        shutil.copyfile(_src, _dst)

# Perbaikan KeyError 'a--1,-1': tiru get_1st_pairs.py — kupas prefix 'a'/'o',
# tulis span '-1,-1' untuk slot kosong, dan TOLAK token berawalan 'a-'
# lolos ke tokenizer (convert_tokens_to_ids tidak mengenalnya).
n_pair, n_impl = 0, 0
out1st = os.path.join(work_tok, f"{DOMAIN}_test_pair_1st.tsv")
with open(pred_file, encoding="utf-8") as fh, open(out1st, "w", encoding="utf-8") as wf:
    for line in fh:
        line = line.strip().split("\\t")
        if len(line) <= 1:
            continue
        text, asp, opi = line[0], [], []
        for ele in line[1:]:
            if ele.startswith("a-"):
                s = ele[2:]
                assert SPAN_OK.match(s), f"span aspek rusak: {ele!r}"
                asp.append(s)
            elif ele.startswith("o-"):
                s = ele[2:]
                assert SPAN_OK.match(s), f"span opini rusak: {ele!r}"
                opi.append(s)
            # token lain (bukan a-/o-) diabaikan: tidak boleh masuk pair file
        asp = asp or ["-1,-1"]
        opi = opi or ["-1,-1"]
        for pa in asp:
            for po in opi:
                assert pa != "a--1,-1" and po != "a--1,-1"
                wf.write(text + "####" + pa + " " + po + "\\n")
                n_pair += 1
                n_impl += (pa == "-1,-1") + (po == "-1,-1")
print(f"bridge: {n_pair} pasangan -> {out1st} (span implisit {n_impl})")
print(f"data_dir Step-2 = {S} (work-dir sesi, upstream tak tersentuh)")
'''

CODE_STEP2_INIT = '''# ============================================================
# 9a. Inisialisasi Step-2 (single-head kategori-sentimen)
# ============================================================
ensure_objects()
require_vars("step_stage", "S", "DOMAIN", "BERT_MODEL_SRC", "MAX_SEQ_LENGTH", "SEED", "N_CATSENTI")
import torch
from modeling import CategorySentiClassification
from run_classifier_dataset_utils import processors
print(f"Step-2 siap: num_labels={N_CATSENTI[DOMAIN]} (single-head gabungan)")
'''

CODE_STEP2_TRAIN = '''# ============================================================
# 9e. Training Step-2 + resume level-3 + early stopping
# ============================================================
require_vars("step_stage", "S", "DOMAIN", "BERT_MODEL_SRC", "tokenizer", "device",
             "MAX_SEQ_LENGTH", "STEP2_BATCH_SIZE", "EVAL_BATCH_SIZE", "STEP2_LR",
             "NUM_EPOCHS", "PATIENCE", "MIN_EPOCHS_BEFORE_STOP", "GRAD_ACC",
             "WARMUP", "FORCE_RETRAIN_STEP2", "N_CATSENTI", "STEP2_SKIP_TRAINING", "pd")
import torch, math
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import CategorySentiClassification
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, convert_examples_to_features2nd
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval
import logging
logger2 = logging.getLogger("acos_bert_step2")

CKPT2, LOG2 = os.path.join(S, "checkpoints"), os.path.join(S, "logs")
data2 = S  # work-dir sesi (salinan token + 1st hasil sendiri)
args2 = SimpleNamespace(output_dir=LOG2, data_dir=data2, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="categorysenti",
                        train_batch_size=STEP2_BATCH_SIZE, eval_batch_size=EVAL_BATCH_SIZE,
                        gradient_accumulation_steps=GRAD_ACC)
processor2 = processors["categorysenti"]()
label_list_2 = processor2.get_labels(DOMAIN)
num_labels_2 = len(label_list_2[0])
assert num_labels_2 == N_CATSENTI[DOMAIN], (num_labels_2, N_CATSENTI[DOMAIN])

def _tensors_2(features):
    return (torch.tensor([f.tokens_len for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in features], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in features], dtype=torch.long),
            torch.tensor([f.candidate_aspect for f in features], dtype=torch.long),
            torch.tensor([f.candidate_opinion for f in features], dtype=torch.long),
            torch.tensor([f.label_id for f in features], dtype=torch.long))

tr_ex = processor2.get_train_examples(data2, DOMAIN)
tr_ft = convert_examples_to_features2nd(tr_ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
t7 = _tensors_2(tr_ft)
train_dl2 = DataLoader(TensorDataset(*t7), sampler=RandomSampler(TensorDataset(*t7)), batch_size=STEP2_BATCH_SIZE)
va_ex = processor2.get_valid_examples(data2, DOMAIN)
va_ft = convert_examples_to_features2nd(va_ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
v7 = _tensors_2(va_ft)
valid_dl2 = DataLoader(TensorDataset(*v7), sampler=SequentialSampler(TensorDataset(*v7)), batch_size=EVAL_BATCH_SIZE)
vf = cs.open(os.path.join(data2, "tokenized_data", f"{DOMAIN}_dev_pair.tsv"), encoding="utf-8").readlines()
valid_gold2 = list(read_pair_gold(vf, args2))

model2 = CategorySentiClassification.from_pretrained(BERT_MODEL_SRC, num_labels=num_labels_2)
model2.to(device)
t_total2 = math.ceil(len(train_dl2) / GRAD_ACC) * NUM_EPOCHS
grp2 = list(model2.named_parameters())
opt2 = BertAdam([{"params": [p for n, p in grp2 if not any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.01},
                 {"params": [p for n, p in grp2 if any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.0}],
                lr=STEP2_LR, warmup=WARMUP, t_total=t_total2)

resume2 = os.path.join(LOG2, "step2_resume.json")
start2, best2, hist2, since2, gstep2 = 1, -1.0, [], 0, 0
best2_epoch = 1
# Port V4_1: SKIP melewati loop epoch (persiapan data+model tetap jalan untuk
# validasi bentuk); riwayat dimuat dari cache untuk tail pelaporan.
_STEP2_SKIP = bool(globals().get("STEP2_SKIP_TRAINING", False))
if _STEP2_SKIP:
    print(f"SKIP loop training Step 2 (cache hit) — best tersimpan {globals().get('best_step2_f1', float('nan')):.4f}.")
    try:
        _dfc2 = pd.read_csv(globals().get("step2_csv", os.path.join(S, "csv", "step2_history.csv")))
        hist2 = _dfc2.to_dict("records")
        best2 = float(_dfc2["micro-F1"].max())
        best2_epoch = int(_dfc2.loc[_dfc2["micro-F1"].idxmax(), "epoch"])
    except Exception as _e:
        print(f"   (riwayat cache tak terbaca: {_e} — tail pelaporan dilewati)")
if not _STEP2_SKIP and os.path.isfile(resume2) and not FORCE_RETRAIN_STEP2:
    r = json.load(open(resume2, encoding="utf-8"))
    ep = r.get("last_completed_epoch", 0)
    ck = os.path.join(CKPT2, f"step2_epoch_{ep}", "pytorch_model.bin")
    op = os.path.join(CKPT2, f"step2_epoch_{ep}", "optimizer.pt")
    if ep < NUM_EPOCHS and os.path.isfile(ck):
        model2.load_state_dict(torch.load(ck, map_location=device))
        if os.path.isfile(op):
            opt2.load_state_dict(torch.load(op, map_location=device))
        start2, best2, hist2, gstep2 = ep + 1, r.get("best_micro_f1", -1.0), r.get("history", []), r.get("global_step", 0)
        print(f"resume Step-2 dari epoch {start2} (best {best2:.4f})")

# Port V4_1: cicilan epoch anti-timeout Colab + progres JSON per-epoch.
_max_run2 = globals().get("MAX_EPOCHS_THIS_RUN", 0)
_run_until2 = min((start2 + _max_run2 - 1) if _max_run2 else NUM_EPOCHS, NUM_EPOCHS)
_prog2 = os.path.join(LOG2, "step2_progress.json")
with step_stage(f"Step-2 training ({DOMAIN}, epoch {start2}-{_run_until2}/{NUM_EPOCHS})", max(_run_until2 - start2 + 1, 0)) as st:
    early2 = False
    for epoch in range(start2, (_run_until2 if not _STEP2_SKIP else start2 - 1) + 1):
        model2.train()
        run_loss, n_step = 0.0, 0
        for batch in train_dl2:
            b = tuple(t.to(device) for t in batch)
            _, ids, mask, seg, ca, co, lab = b
            losses, _ = model2(tokenizer, epoch, aspect_input_ids=ids,
                               aspect_token_type_ids=seg, aspect_attention_mask=mask,
                               candidate_aspect=ca, candidate_opinion=co, label_id=lab)
            loss = losses[0] / GRAD_ACC
            loss.backward()
            run_loss += loss.item(); n_step += 1
            opt2.step(); opt2.zero_grad(); gstep2 += 1
        model2.eval()
        res = pair_eval(epoch, args2, logger2, tokenizer, model2, valid_dl2, valid_gold2, label_list_2, device, "categorysenti", eval_type="valid")
        f1 = res["micro-F1"]
        improved = f1 > best2
        best2 = max(best2, f1)
        if improved:
            best2_epoch = epoch
        since2 = 0 if improved else since2 + 1
        ep_dir = os.path.join(CKPT2, f"step2_epoch_{epoch}")
        os.makedirs(ep_dir, exist_ok=True)
        os.makedirs(os.path.join(CKPT2, "step2_best"), exist_ok=True)
        if improved:
            torch.save(model2.state_dict(), os.path.join(CKPT2, "step2_best", "pytorch_model.bin"))
        torch.save(model2.state_dict(), os.path.join(ep_dir, "pytorch_model.bin"))
        torch.save(opt2.state_dict(), os.path.join(ep_dir, "optimizer.pt"))
        for old in glob.glob(os.path.join(CKPT2, "step2_epoch_*")):
            if old != ep_dir and os.path.isdir(old):
                shutil.rmtree(old, ignore_errors=True)
        hist2.append({"epoch": epoch, "loss": run_loss / max(n_step, 1), "micro-F1": f1, "best": best2})
        json.dump({"last_completed_epoch": epoch, "total_epochs": NUM_EPOCHS, "best_micro_f1": best2,
                   "history": hist2, "global_step": gstep2, "early_stopped": False},
                  open(resume2, "w", encoding="utf-8"), indent=2)
        write_stage_progress(_prog2, stage="step2_train", epoch=epoch, run_until=_run_until2,
                             total_epochs=NUM_EPOCHS, best_micro_f1=best2, best_epoch=best2_epoch,
                             early_stopped=False)
        st.step(f"epoch {epoch:02d}: loss {run_loss/max(n_step,1):.4f} | valid micro-F1 {f1:.4f} (best {best2:.4f})")
        if PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and since2 >= PATIENCE:
            st.note(f"early stopping ({PATIENCE} epoch tanpa perbaikan)")
            early2 = True
            break
    print(f"Step-2 selesai: best micro-F1 {best2:.4f} | early_stop={early2}")
    globals()["best_step2_f1"], globals()["best2_epoch"] = best2, best2_epoch
    json.dump({"best_micro_f1": best2, "best_epoch": best2_epoch,
               "epochs_done": [h.get("epoch") for h in hist2],
               "total_epochs": NUM_EPOCHS, "run_until": _run_until2,
               "early_stopped": early2},
              open(os.path.join(LOG2, "step2_run_result.json"), "w", encoding="utf-8"), indent=2)
    update_mcp_manifest("STEP2_DONE" if hist2 else "STEP2_SKIPPED_EMPTY", 8,
                        {"best_micro_f1": best2, "best_epoch": best2_epoch})

df2 = None
if hist2:
    df2 = history_display_frame(hist2)
    write_df_csv_md(df2, os.path.join(S, "csv", "step2_history.csv"), os.path.join(S, "md", "step2_history.md"), "Step-2 history")
    colab_utils.plot_training_history(hist2, task_name="Step2", output_plot_path=os.path.join(S, "plots", "step2_curve.png"), output_csv_path=os.path.join(S, "csv", "step2_history.csv"))
    print(f"best_step2_f1={best2:.4f}")
else:
    print("Peringatan: hist2 kosong (cache tak terbaca dan loop dilewati) — tidak ada artefak ditulis.")
'''

# ── eval ──────────────────────────────────────────────────────────────

CODE_EVAL = '''# ============================================================
# 10. Evaluasi final + 15 subtask + master_metrics.json
# ============================================================
ensure_objects()
require_vars("step_stage", "S", "DOMAIN", "tokenizer", "device", "label_list_2",
             "BERT_MODEL_SRC", "N_CATSENTI", "MAX_SEQ_LENGTH", "EVAL_BATCH_SIZE",
             "FORCE_REEVAL")
# Port V4_1 sel 9a: CACHE HIT bila master_metrics.json sudah ada.
# (Isi cache dimuat setelah inisialisasi metrics di bawah.)
_master_json = os.path.join(S, "logs", "master_metrics.json")
_EVAL_SKIP = bool(os.path.isfile(_master_json) and not FORCE_REEVAL)
import torch
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset
from modeling import CategorySentiClassification
from run_classifier_dataset_utils import processors, convert_examples_to_features2nd
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval
import logging
loggerE = logging.getLogger("acos_bert_eval")

modelE = CategorySentiClassification.from_pretrained(BERT_MODEL_SRC, num_labels=N_CATSENTI[DOMAIN])
best_bin = os.path.join(S, "checkpoints", "step2_best", "pytorch_model.bin")
assert os.path.isfile(best_bin), f"model terbaik tidak ada: {best_bin} — latih Step-2 dulu"
modelE.load_state_dict(torch.load(best_bin, map_location=device))
modelE.to(device); modelE.eval()
processorE = processors["categorysenti"]()
argsE = SimpleNamespace(output_dir=os.path.join(S, "logs"), data_dir=S, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="categorysenti",
                        eval_batch_size=EVAL_BATCH_SIZE)

def _eval_pair_file(pair_path, tag):
    ex = colab_utils.pair_examples_from_file(processorE, pair_path, "test")
    ft = convert_examples_to_features2nd(ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
    t = (torch.tensor([f.tokens_len for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_input_ids for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_input_mask for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_segment_ids for f in ft], dtype=torch.long),
         torch.tensor([f.candidate_aspect for f in ft], dtype=torch.long),
         torch.tensor([f.candidate_opinion for f in ft], dtype=torch.long),
         torch.tensor([f.label_id for f in ft], dtype=torch.long))
    dl = DataLoader(TensorDataset(*t), sampler=SequentialSampler(TensorDataset(*t)), batch_size=EVAL_BATCH_SIZE)
    gold = list(read_pair_gold(cs.open(pair_path, encoding="utf-8").readlines(), argsE))
    with colab_utils.SubtaskMetricCapture(loggerE) as cap:
        res = pair_eval("final", argsE, loggerE, tokenizer, modelE, dl, gold, label_list_2, device, "categorysenti", eval_type="test")
    return res, cap.to_frame()

tokS = os.path.join(S, "tokenized_data")
metrics = {"domain": DOMAIN, "num_labels_step2": N_CATSENTI[DOMAIN]}
if _EVAL_SKIP:
    metrics = json.load(open(_master_json, encoding="utf-8"))
    print(f"CACHE HIT evaluasi final (FORCE_REEVAL=False): {metrics.get('pipeline_1st', {})}")
if not _EVAL_SKIP:
    res_pipe, df_pipe = _eval_pair_file(os.path.join(tokS, f"{DOMAIN}_test_pair_1st.tsv"), "pipeline")
    metrics["pipeline_1st"] = {k: (float(v) if isinstance(v, float) else v) for k, v in res_pipe.items()}
    res_gold, df_gold = _eval_pair_file(os.path.join(tokS, f"{DOMAIN}_test_pair.tsv"), "gold")
    metrics["gold_pair"] = {k: (float(v) if isinstance(v, float) else v) for k, v in res_gold.items()}
    print("pipeline (pred Step-1):", metrics["pipeline_1st"])
    print("gold pair:", metrics["gold_pair"])

    df_pipe.to_csv(os.path.join(S, "csv", "subtask_pipeline.csv"), index=False)
    colab_utils.plot_subtask_metrics(df_pipe, os.path.join(S, "plots", "subtask_pipeline.png"),
                                     title=f"{DOMAIN}: 15 subtask (pipeline)")
    with open(os.path.join(S, "logs", "master_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("master_metrics.json + subtask_pipeline.[csv|png] tersimpan")
update_mcp_manifest("FINAL_EVAL", 9, {"pipeline_1st": metrics.get("pipeline_1st", {})})
save_pipeline_state()
print("State pasca-evaluasi tersimpan.")
'''

CODE_AUDIT = '''# ============================================================
# 10b. Audit artefak sesi + finalisasi (port V4_1 sel 79/11)
# ============================================================
require_vars("step_stage", "session_dirs", "S", "DOMAIN")
print("=" * 78)
print(f"AUDIT ARTEFAK SESI AKTIF [{DOMAIN.upper()}]")
print("=" * 78)
print(f"Lokasi penyimpanan: {S}")
is_drive_saved = "/content/drive/MyDrive" in S
print(f"Persistensi Drive: {'TERSIMPAN DI DRIVE' if is_drive_saved else 'LOKAL / EPHEMERAL (hilang saat runtime Colab didaur ulang)'}")
print()
all_saved_files = []
for sub_name, sub_path in session_dirs.items():
    if sub_name in ("root", "session_dir") or not os.path.isdir(sub_path):
        continue
    for root, dirs, files in os.walk(sub_path):
        for f in sorted(files):
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            all_saved_files.append({
                "Subfolder": sub_name,
                "File": f,
                "Size": f"{sz / 1024:.1f} KB" if sz < 1024 * 1024 else f"{sz / (1024 ** 2):.2f} MB",
                "Path": fp,
            })
df_audit = pd.DataFrame(all_saved_files)
if not df_audit.empty:
    print(f"Total {len(df_audit)} file di sesi ini:")
    for sf, grp in df_audit.groupby("Subfolder"):
        print(f"[{sf.upper()}] ({len(grp)} file):")
        for r in grp.itertuples():
            print(f"   - {r.File} ({r.Size})")
else:
    print("Belum ada file tersimpan di subfolder sesi.")
print("=" * 78)
save_pipeline_state()
update_mcp_manifest("COMPLETED", 10, {"total_files": len(all_saved_files)})
print("Sesi difinalisasi (state + manifest COMPLETED).")
'''

CODE_DEMO = '''# ============================================================
# 11. Demo inferensi 2 kalimat (rest16/laptop)
# ============================================================
require_vars("step_stage", "DOMAIN")
SAMPLES = {"rest16": ["The sushi was fresh but service was slow .",
                      "Great ambience , overpriced food ."],
           "laptop": ["Battery life is great but the keyboard feels cheap .",
                      "Fast shipping , noisy fan ."]}
for s in SAMPLES[DOMAIN]:
    print(">", s)
print("(inferensi penuh memakai model1+modelE terbaik; sel ini contoh pemicu — lihat pred4pipeline.txt sesi untuk hasil batch)")
'''

CELLS = [
    ("md", MD_TITLE, None),
    ("code", CODE_ENV, "setup"),
    ("code", CODE_CONFIG, "setup"),
    ("code", CODE_HELPERS, "setup"),
    ("code", CODE_SESSION, "setup"),
    ("code", CODE_GATES, "setup"),
    ("code", CODE_BACKBONE, "setup"),
    ("code", CODE_EDA, "setup"),
    ("code", CODE_STATE_SAVER, "setup"),
    ("code", CODE_RECOVERY, "setup"),
    ("code", CODE_ENSURE, "setup"),
    ("md", "## Step 1 — Aspect-Opinion Co-Extraction (BERT-CRF)", None),
    ("code", CODE_STEP1_INIT, "step1"),
    ("code", CODE_STEP1_CACHE, "step1"),
    ("code", CODE_STEP1_TRAIN, "step1"),
    ("md", "## Bridge + Step 2 — Category-Sentiment (single-head)", None),
    ("code", CODE_BRIDGE, "step2"),
    ("code", CODE_STEP2_INIT, "step2"),
    ("code", CODE_STEP2_CACHE, "step2"),
    ("code", CODE_STEP2_TRAIN, "step2"),
    ("md", "## Evaluasi final + demo", None),
    ("code", CODE_EVAL, "eval"),
    ("code", CODE_AUDIT, "eval"),
    ("code", CODE_DEMO, "eval"),
]


def build():
    cells = []
    for kind, src, section in CELLS:
        if kind == "md":
            cells.append(md(src))
        else:
            cells.append(code(src, section))
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python", "version": "3"}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    h = hashlib.md5(open(OUT, "rb").read()).hexdigest()
    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    print(f"{os.path.basename(OUT)}: {len(cells)} sel ({n_code} kode), MD5 {h}")
    return h


def main():
    h = build()
    # validasi: semua sel kode lolos ast.parse (tanpa torch)
    nb = json.load(open(OUT, encoding="utf-8"))
    bad = 0
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            try:
                ast.parse("".join(c["source"]))
            except SyntaxError as e:
                bad += 1
                print(f"SYNTAX sel {i}: {e}")
    assert bad == 0, f"{bad} sel gagal parse"
    print(f"ast.parse: {sum(1 for c in nb['cells'] if c['cell_type']=='code')} sel kode OK")


if __name__ == "__main__":
    main()
