# =============================================================================
# CELL 3 FIXED: Import & Path Setup (Simplified - No Conflicts)
# =============================================================================
# Ganti Cell 3 yang bermasalah dengan versi ini

import os, sys, time, json, pickle, random, math, importlib, urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# =============================================================
# PATH SETUP - SIMPLE & ROBUST (NO DUPLICATED LOGIC)
# =============================================================

ACOS_REPO_URL = "https://github.com/haisyamalawwab/ACOS.git"

def _prepend_path(p):
    """Force path to front of sys.path"""
    if not os.path.isdir(p):
        return None
    p_str = str(Path(p).resolve())
    while p_str in sys.path:
        sys.path.remove(p_str)
    sys.path.insert(0, p_str)
    return p_str

def _is_upstream(d):
    """Validate Extract-Classify-ACOS completeness"""
    return (os.path.isfile(os.path.join(d, 'modeling.py')) and 
            os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py')))

# Detect or clone project structure
print("=" * 60)
print("ACOS Project Setup...")
print("=" * 60)

candidates = [
    "/content",
    "/content/drive/MyDrive/ACOS", 
    "/content/drive/MyDrive/ACOS-ASLI",
    "d:/laragon/www/ACOS-ASLI"
]

base_project_dir = None
upstream_root = None
indo_root = None

# Try to find existing structure
for base_cand in candidates:
    if not os.path.isdir(base_cand):
        continue
        
    extract_path = os.path.join(base_cand, "Extract-Classify-ACOS")
    indo_path = os.path.join(base_cand, "ACOS-IndoBERT")
    
    if _is_upstream(extract_path):
        base_project_dir = base_cand
        upstream_root = extract_path
        indo_root = indo_path if os.path.isdir(indo_path) else base_cand
        print(f"✓ Found ACOS project: {base_cand}")
        break

# Clone if not found (typical in fresh Colab)
if upstream_root is None:
    print(f"📥 Cloning ACOS from {ACOS_REPO_URL}...")
    base_project_dir = "/content"
    
    temp_dir = '/tmp/acos_clone'
    os.system(f"rm -rf {temp_dir}")
    result = os.system(f"git clone --depth 1 {ACOS_REPO_URL} {temp_dir}")
    
    if result == 0:
        # Copy to permanent locations
        upstream_root = "/content/Extract-Classify-ACOS"
        indo_root = "/content/ACOS-IndoBERT"
        
        os.system(f'cp -r "{temp_dir}/Extract-Classify-ACOS" "{upstream_root}"')
        os.system(f'cp -r "{temp_dir}/ACOS-IndoBERT" "{indo_root}"')
        os.system(f"rm -rf {temp_dir}")
        
        print(f"  ✓ Extract-Classify-ACOS: {upstream_root}")
        print(f"  ✓ ACOS-IndoBERT: {indo_root}")
    else:
        raise RuntimeError("Failed to clone ACOS repository")

# =============================================================
# CRITICAL: Setup sys.path in CORRECT ORDER  
# =============================================================
print(f"\n{'='*60}")
print("Configuring Python import paths...")
print("="*60)

# MUST be in this exact order:
_prepend_path(upstream_root)      # 1. Extract-Classify-ACOS (bert_utils, modeling)
_prepend_path(indo_root)          # 2. ACOS-IndoBERT (acos_id modules)
_prepend_path(base_project_dir)   # 3. Base directory

# Verify setup
print(f"  base_project_dir : {base_project_dir}")
print(f"  upstream_root    : {upstream_root}")
print(f"  indo_root        : {indo_root}")
print(f"  sys.path[0]      : {sys.path[0]}")

# Verify critical files
modeling_exists = os.path.isfile(os.path.join(upstream_root, 'modeling.py'))
bert_utils_exists = os.path.isfile(os.path.join(upstream_root, 'bert_utils', 'tokenization.py'))

print(f"  modeling.py      : {modeling_exists}")
print(f"  bert_utils/      : {bert_utils_exists}")

if not (modeling_exists and bert_utils_exists):
    raise RuntimeError("Critical files missing - check project structure")

print(f"\n{'='*60}")
print("Importing modules...")
print("="*60)

# =============================================================
# IMPORTS - Only AFTER sys.path is correctly configured
# =============================================================

# Import bert_utils FIRST (the problematic import)
try:
    from bert_utils.tokenization import BertTokenizer
    print("  ✅ BertTokenizer")
except ImportError as e:
    print(f"  ❌ BertTokenizer failed: {e}")
    print(f"     sys.path[0]: {sys.path[0]}")
    print(f"     Available files: {os.listdir(sys.path[0]) if os.path.exists(sys.path[0]) else 'Path not found'}")
    raise

# Import modeling classes
from modeling import BertForQuadABSA, CategorySentiClassification  
print("  ✅ BertForQuadABSA, CategorySentiClassification")

# Import acos_id modules
acos_id = importlib.import_module("acos_id")
print(f"  ✅ acos_id (v{getattr(acos_id, '__version__', '0.2.1')})")

acos_taxonomy = importlib.import_module("acos_id.taxonomy")
print(f"  ✅ taxonomy ({len(getattr(acos_taxonomy, 'CATEGORIES', []))} categories)")

acos_ckpt = importlib.import_module("acos_id.checkpoint")
print("  ✅ checkpoint")

acos_cross_val = importlib.import_module("acos_id.cross_val")
build_with_ratio = acos_cross_val.build_with_ratio
build_kfold_splits = acos_cross_val.build_kfold_splits
ExperimentGrid = acos_cross_val.ExperimentGrid
tokenize_all_splits = acos_cross_val.tokenize_all_splits
print("  ✅ cross_val")

acos_experiment_runner = importlib.import_module("acos_id.experiment_runner")
prepare_all_data = acos_experiment_runner.prepare_all_data
run_all_experiments = acos_experiment_runner.run_all_experiments
aggregate_cv_results = acos_experiment_runner.aggregate_cv_results
print("  ✅ experiment_runner")

acos_result_saver = importlib.import_module("acos_id.result_saver")
ResultSaver = acos_result_saver.ResultSaver
merge_experiment_results = acos_result_saver.merge_experiment_results
print("  ✅ result_saver")

model_wrappers = importlib.import_module("acos_id.model_wrappers")
print("  ✅ model_wrappers")

print(f"\n🎉 ALL IMPORTS SUCCESSFUL!")

# =============================================================
# GLOBAL SETUP
# =============================================================
random.seed(SEED)
np.random.seed(SEED) 
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if globals().get('ROCM_BENCHMARK', True):
        torch.backends.cudnn.benchmark = True

# Setup directories
results_dir = os.path.join(indo_root, "results")
os.makedirs(results_dir, exist_ok=True)

print(f"\n📁 Results directory: {results_dir}")
print("🎯 V5.1 Setup Complete - bert_utils import issue FIXED!")