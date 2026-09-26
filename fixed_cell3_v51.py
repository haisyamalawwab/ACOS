# Sel 3: Import semua modul & setup path dua-root (ROBUST V5.1 - Fixed)
import os, sys, time, json, pickle, random, math, importlib, urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# ============================================================
# SIMPLE PATH SETUP - NO DUPLICATED LOGIC
# ============================================================

ACOS_REPO_URL = "https://github.com/haisyamalawwab/ACOS.git"
ACOS_ID_MODULES = [
    "taxonomy", "checkpoint", "cross_val", "experiment_runner",
    "result_saver", "model_wrappers", "build_acos", "tokenize_data", "selftest"
]

def _prepend_path(p):
    """Paksa p ke posisi terdepan sys.path."""
    try:
        p_str = str(Path(p).resolve())
    except Exception:
        return None
    if not os.path.isdir(p_str):
        return None
    while p_str in sys.path:
        sys.path.remove(p_str)
    sys.path.insert(0, p_str)
    return p_str

# Helper validation functions
def _is_upstream(d):
    """Validasi Extract-Classify-ACOS lengkap (modeling.py + bert_utils/tokenization.py)."""
    return os.path.isfile(os.path.join(d, 'modeling.py')) and os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py'))

# Deteksi base project directory
kandidat_base = [
    "/content",
    "/shared-docker/ACOS",
    "d:/laragon/www/ACOS-ASLI", 
    "D:/laragon/www/ACOS-ASLI",
    "/content/drive/MyDrive/ACOS",
    "/content/drive/MyDrive/ACOS-ASLI",
    str(Path.cwd().parent.parent),
    str(Path.cwd().parent),
    str(Path.cwd()),
]

base_project_dir = None
upstream_root = None
indo_root = None

for base_cand in kandidat_base:
    if not os.path.isdir(base_cand):
        continue
        
    # Cek Extract-Classify-ACOS
    extract_path = os.path.join(base_cand, "Extract-Classify-ACOS")
    indo_path = os.path.join(base_cand, "ACOS-IndoBERT")
    
    if _is_upstream(extract_path):
        base_project_dir = base_cand
        upstream_root = extract_path
        print(f"✓ Found Extract-Classify-ACOS: {extract_path}")
        break

# Fallback: clone if needed
if upstream_root is None:
    print(f"📥 Extract-Classify-ACOS tidak ditemukan. Clone dari {ACOS_REPO_URL} ...")
    base_project_dir = "/content" if os.path.exists("/content") else str(Path.cwd())
    _tmpf = '/tmp/ACOS_clone'
    os.system(f"rm -rf {_tmpf}")
    os.system(f"git clone --depth 1 {ACOS_REPO_URL} {_tmpf}")
    _src = os.path.join(_tmpf, 'Extract-Classify-ACOS')
    upstream_root = os.path.join(base_project_dir, 'Extract-Classify-ACOS')
    if _is_upstream(_src):
        os.makedirs(upstream_root, exist_ok=True)
        os.system(f'cp -r "{_src}/." "{upstream_root}/"')
        print(f"  ✓ Cloned: {upstream_root}")
    os.system(f"rm -rf {_tmpf}")

# Cari indo_root
for indo_cand in [
    os.path.join(base_project_dir, "ACOS-IndoBERT"),
    "/content/ACOS-IndoBERT",
    str(Path.cwd())
]:
    if os.path.isdir(os.path.join(indo_cand, "acos_id")):
        indo_root = indo_cand
        break

if indo_root is None:
    indo_root = os.path.join(base_project_dir, "ACOS-IndoBERT")
    print(f"📥 Creating ACOS-IndoBERT at: {indo_root}")

# ============================================================
# SETUP SYS.PATH DENGAN URUTAN YANG BENAR 
# ============================================================
_prepend_path(upstream_root)  # Extract-Classify-ACOS HARUS PERTAMA
_prepend_path(indo_root)     # ACOS-IndoBERT kedua  
_prepend_path(base_project_dir)  # Base project ketiga

print("=" * 65)
print("✅ PATHS CONFIGURED SUCCESSFULLY")
print("=" * 65)
print(f"  base_project_dir : {base_project_dir}")
print(f"  upstream_root    : {upstream_root}")
print(f"  indo_root        : {indo_root}")
print(f"  modeling.py      : {os.path.isfile(os.path.join(upstream_root, 'modeling.py'))}")
print(f"  bert_utils/      : {os.path.isfile(os.path.join(upstream_root, 'bert_utils', 'tokenization.py'))}")
print(f"  sys.path[0]      : {sys.path[0]}")

print(f"\n{'='*60}")
print("Importing modules...")
print("=" * 60)

# ============================================================
# IMPORT MODULES - ONLY AFTER PATH IS PROPERLY SETUP
# ============================================================

# Import bert_utils ONLY after sys.path is setup
from bert_utils.tokenization import BertTokenizer
print("  ✓ BertTokenizer")

from modeling import BertForQuadABSA, CategorySentiClassification
print("  ✓ BertForQuadABSA, CategorySentiClassification")

# Import acos_id modules
acos_id = importlib.import_module("acos_id")
print(f"  ✓ acos_id (v{getattr(acos_id, '__version__', '0.2.1')})")

acos_taxonomy = importlib.import_module("acos_id.taxonomy")
print(f"  ✓ taxonomy ({len(getattr(acos_taxonomy, 'CATEGORIES', []))} categories)")

acos_ckpt = importlib.import_module("acos_id.checkpoint")
print("  ✓ checkpoint")

acos_cross_val = importlib.import_module("acos_id.cross_val")
build_with_ratio = acos_cross_val.build_with_ratio
build_kfold_splits = acos_cross_val.build_kfold_splits
ExperimentGrid = acos_cross_val.ExperimentGrid
tokenize_all_splits = acos_cross_val.tokenize_all_splits
print("  ✓ cross_val")

acos_experiment_runner = importlib.import_module("acos_id.experiment_runner")
prepare_all_data = acos_experiment_runner.prepare_all_data
run_all_experiments = acos_experiment_runner.run_all_experiments
aggregate_cv_results = acos_experiment_runner.aggregate_cv_results
print("  ✓ experiment_runner")

acos_result_saver = importlib.import_module("acos_id.result_saver")
ResultSaver = acos_result_saver.ResultSaver
merge_experiment_results = acos_result_saver.merge_experiment_results
print("  ✓ result_saver")

model_wrappers = importlib.import_module("acos_id.model_wrappers")
print("  ✓ model_wrappers")

print(f"\n✅ ALL IMPORTS SUCCESSFUL!")

# ============================================================
# SEED GLOBAL & DIREKTORI OUTPUT
# ============================================================
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if globals().get('ROCM_BENCHMARK', True):
        torch.backends.cudnn.benchmark = True

# Setup output directories
results_dir = os.path.join(indo_root, "results")
os.makedirs(results_dir, exist_ok=True)
print(f"📁 Results directory: {results_dir}")