"""Pecah 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb menjadi 4 notebook serial.

Tiap notebook 02-04 diawali dengan:
  1. Header markdown
  2. Cell bootstrap: step_stage, require_vars, sys.path, acos_id reimport
  3. Cell recovery: pipeline_state.pkl load (sel 49-53 dari V4.1)
  4. Sel-sel tahap yang sesuai

File output:
  V4_1_01_setup.ipynb          sel 0-31  (setup + gate data)
  V4_1_02_step1_train.ipynb    bootstrap + recovery + sel 32-48 (step1)
  V4_1_03_step2_train.ipynb    bootstrap + recovery + sel 54-68 (step2)
  V4_1_04_eval_inference.ipynb bootstrap + recovery + sel 69-79 (eval+demo)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb")

with open(SRC, "r", encoding="utf-8") as f:
    nb_src = json.load(f)

cells = nb_src["cells"]

RECOVERY_CELLS = [49, 50, 51, 52, 53]   # 6b recovery + 6c ensure_objects

BOOTSTRAP_SRC = r'''# ============================================================
#  Bootstrap: definisi runtime yang tidak tersimpan di pipeline_state.pkl
#  Dijalankan otomatis sebelum state recovery di setiap notebook serial.
# ============================================================
import os, sys, time, json, re, pickle, shutil, glob, importlib, warnings
from datetime import datetime

# --- step_stage & require_vars (dari sel 6 V4.1) ---
class step_stage:
    def __init__(self, title, total_steps=None):
        self.title = title
        self.total = total_steps
        self.n = 0
        self.t0 = None
    def __enter__(self):
        self.t0 = time.time()
        print("=" * 78)
        print(f"\u25b6\ufe0f  {self.title}")
        print("=" * 78, flush=True)
        return self
    def step(self, msg):
        self.n += 1
        tag = f"{self.n}/{self.total}" if self.total else str(self.n)
        print(f"   [{tag}] {time.time() - self.t0:6.1f}s  {msg}", flush=True)
    def note(self, msg):
        print(f"        {msg}", flush=True)
    def __exit__(self, exc_type, exc, tb):
        dur = time.time() - self.t0
        if exc_type is None:
            print(f"\u2705 {self.title} \u2014 selesai dalam {dur:.1f}s\n", flush=True)
        else:
            print(f"\u274c {self.title} \u2014 gagal setelah {dur:.1f}s: {exc}\n", flush=True)
        return False

def require_vars(*names):
    missing = [n for n in names if n not in globals()]
    if missing:
        raise RuntimeError(
            f"Variabel {missing} belum ada di memori. Jalankan sel pemulihan state "
            f"(6b/6c) atau notebook 01_setup lebih dulu.")

def write_stage_progress(path, **fields):
    d = {"saved_at": datetime.now().isoformat()}
    d.update(fields)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                old = json.load(f)
            if isinstance(old, dict):
                d["previous"] = old
        except Exception:
            pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def _prf(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1

# --- patch_eval_metrics_counts (ringkas; full patch dijalankan ulang di sel 5a/8a) ---
# Pastikan nama fungsi tersedia agar require_vars tidak gagal bila sel import
# upstream belum berjalan. Patch sebenarnya dilakukan di sel step1/step2 init.
def patch_eval_metrics_counts():
    try:
        import eval_metrics as _em
    except ImportError:
        return "eval_metrics belum di-import (akan dipatch di sel init)"
    return "eval_metrics siap"

def history_display_frame(history, epochs_col="epoch"):
    import pandas as pd
    if not history:
        return pd.DataFrame()
    return pd.DataFrame(history)

def metrics_display_frame(res):
    import pandas as pd
    if not res:
        return pd.DataFrame()
    rows = [{"Metric": k, "Value": v} for k, v in res.items()]
    return pd.DataFrame(rows)

def best_epoch_row(history, f1_key="micro-F1"):
    if not history:
        return None, 0.0, None
    best = max(history, key=lambda r: float(r.get(f1_key, 0.0)))
    return best, float(best.get(f1_key, 0.0)), int(best.get("epoch", 0))

def unpack_model_output(out):
    losses, logits = out
    loss = losses[0] if isinstance(losses, (list, tuple)) else losses
    return loss, logits

# --- Path setup (dari sel 8 V4.1, versi ringkas) ---
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
if "base_project_dir" not in globals() or not globals().get("base_project_dir"):
    if os.path.exists("/content/drive/MyDrive/ACOS"):
        base_project_dir = "/content/drive/MyDrive/ACOS"
    elif os.path.exists("/content/ACOS"):
        base_project_dir = "/content/ACOS"
    else:
        base_project_dir = os.path.abspath(".")
    extract_dir = os.path.join(base_project_dir, "Extract-Classify-ACOS")
    data_root = os.path.join(base_project_dir, "data")

# sys.path: upstream ACOS + acos_id
for _p in [extract_dir, os.path.join(extract_dir, "absa5")]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# --- acos_id reimport ---
def _cari_indo_root():
    for _d in ["/content/drive/MyDrive/ACOS-IndoBERT",
               "/content/drive/MyDrive/ACOS/ACOS-IndoBERT",
               "/content/drive/MyDrive/ACOS-ASLI/ACOS-IndoBERT",
               os.path.join(base_project_dir, "ACOS-IndoBERT"),
               os.path.abspath("ACOS-IndoBERT"),
               os.path.abspath(os.path.join("..", "ACOS-IndoBERT"))]:
        if os.path.isdir(os.path.join(_d, "acos_id")):
            return _d
    return None

indo_root = globals().get("indo_root") or _cari_indo_root()
if indo_root and indo_root not in sys.path:
    sys.path.insert(0, indo_root)
if indo_root:
    try:
        acos_id = importlib.import_module("acos_id")
        acos_taxonomy = importlib.import_module("acos_id.taxonomy")
        acos_selftest = importlib.import_module("acos_id.selftest")
        acos_ckpt = importlib.import_module("acos_id.checkpoint")
        acos_eda = importlib.import_module("acos_id.eda")
        acos_upstream = importlib.import_module("acos_id.upstream")
    except ModuleNotFoundError:
        pass  # akan dipatch di sel init masing-masing step

# _backbone_dirname untuk recovery state
BACKBONE_DIRNAME = {
    "indobert": "indobert_base_p1",
    "indobert-large": "indobert_large_p1",
    "bert-en": "bert_base_uncased",
}
def _backbone_dirname(backbone=None):
    key = backbone or globals().get("BACKBONE") or "bert-en"
    return BACKBONE_DIRNAME.get(key, str(key).replace("-", "_"))

print(f"\u26a1 Bootstrap siap | base_project_dir={base_project_dir} | indo_root={indo_root}")
'''


def md(title, body=""):
    src = [title + "\n"]
    if body:
        src.append(body)
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src):
    return {"cell_type": "code", "metadata": {}, "source": src.splitlines(keepends=True),
            "outputs": [], "execution_count": None}


SPLITS = [
    {
        "file": "V4_1_01_setup.ipynb",
        "title": "V4.1 \u2014 01: Setup, EDA, Gate Data",
        "ranges": [(0, 31)],
        "bootstrap": False,
    },
    {
        "file": "V4_1_02_step1_train.ipynb",
        "title": "V4.1 \u2014 02: Step 1 Training (Aspect & Opinion Co-Extraction)",
        "ranges": [tuple(RECOVERY_CELLS), (32, 48)],
        "bootstrap": True,
    },
    {
        "file": "V4_1_03_step2_train.ipynb",
        "title": "V4.1 \u2014 03: Step 2 Training (Category & Sentiment)",
        "ranges": [tuple(RECOVERY_CELLS), (54, 68)],
        "bootstrap": True,
    },
    {
        "file": "V4_1_04_eval_inference.ipynb",
        "title": "V4.1 \u2014 04: Final Evaluation, Benchmark & Inference",
        "ranges": [tuple(RECOVERY_CELLS), (69, 79)],
        "bootstrap": True,
    },
]

for split in SPLITS:
    nb_out = {
        "cells": [],
        "metadata": dict(nb_src.get("metadata", {})),
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_out["cells"].append(md(f"# {split['title']}", ""))

    if split["bootstrap"]:
        nb_out["cells"].append(md(
            "## Bootstrap",
            "Mendefinisikan ulang `step_stage`, `require_vars`, dan path modul "
            "yang tidak tersimpan di `pipeline_state.pkl`."))
        nb_out["cells"].append(code(BOOTSTRAP_SRC))
        nb_out["cells"].append(md(
            "## State Recovery",
            "Memuat `pipeline_state.pkl` dari sesi sebelumnya. "
            "Jika belum ada, jalankan notebook `01_setup` lebih dulu."))

    selected = []
    for r in split["ranges"]:
        lo, hi = r[0], r[1]
        for i in range(lo, hi + 1):
            selected.append(cells[i])
    nb_out["cells"].extend(selected)

    dst = os.path.join(HERE, split["file"])
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(nb_out, f, ensure_ascii=False, indent=1)
    n_code = sum(1 for c in nb_out["cells"] if c.get("cell_type") == "code")
    print(f"{split['file']}: {len(nb_out['cells'])} sel ({n_code} kode)")

print("Selesai.")
