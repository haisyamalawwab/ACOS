#!/usr/bin/env python3
"""
V5.1 Fixed Cells untuk Colab
Tambahkan cells ini di awal notebook untuk fix bert_utils import issue
"""

# =============================================================================
# CELL 0: Google Drive Mount & Setup 
# =============================================================================
CELL_0_GDRIVE_SETUP = '''
# Cell 0: Google Drive Mount & Initialization
from google.colab import drive
import os, shutil

# Mount Google Drive
print("🔗 Mounting Google Drive...")
drive.mount('/content/drive')

# Verify mount and show space
if os.path.exists('/content/drive/MyDrive'):
    stat = shutil.disk_usage('/content/drive')
    free_gb = stat.free / 1024**3
    total_gb = stat.total / 1024**3
    print(f"✅ Google Drive mounted successfully")
    print(f"💾 Available: {free_gb:.1f}GB / {total_gb:.1f}GB total")
else:
    print("❌ Google Drive mount failed")
    raise RuntimeError("Cannot proceed without Google Drive")

# Setup ACOS project directories in Google Drive
gdrive_dirs = {
    "acos": "/content/drive/MyDrive/ACOS",
    "acos_asli": "/content/drive/MyDrive/ACOS-ASLI", 
    "backup": "/content/drive/MyDrive/ACOS_V51_BACKUP",
    "results": "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results",
    "checkpoints": "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/checkpoints"
}

for name, dir_path in gdrive_dirs.items():
    os.makedirs(dir_path, exist_ok=True)
    print(f"📁 {name}: {dir_path}")

# Set environment variables for later cells
os.environ['GDRIVE_ACOS'] = gdrive_dirs["acos"]
os.environ['GDRIVE_BACKUP'] = gdrive_dirs["backup"] 
os.environ['GDRIVE_RESULTS'] = gdrive_dirs["results"]

print("🎯 Google Drive initialization complete!")
'''

# =============================================================================
# CELL 3 FIXED: Import & Path Setup (Simple & Working)
# =============================================================================  
CELL_3_FIXED_IMPORT = '''
# Cell 3: Import & Path Setup (FIXED V5.1 - Simplified)
import os, sys, time, json, pickle, random, math, importlib, urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# =============================================================
# SIMPLE & ROBUST PATH SETUP - NO CONFLICTS
# =============================================================

ACOS_REPO_URL = "https://github.com/haisyamalawwab/ACOS.git"

def _prepend_path(p):
    """Force path to front of sys.path"""
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

def _is_upstream(d):
    """Validate Extract-Classify-ACOS completeness"""
    return (os.path.isfile(os.path.join(d, 'modeling.py')) and 
            os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py')))

# Detect project structure
candidates = [
    "/content",
    "/content/drive/MyDrive/ACOS", 
    "/content/drive/MyDrive/ACOS-ASLI",
    "d:/laragon/www/ACOS-ASLI",
    "D:/laragon/www/ACOS-ASLI",
    str(Path.cwd())
]

base_project_dir = None
upstream_root = None
indo_root = None

# Find existing structure
for base_cand in candidates:
    if not os.path.isdir(base_cand):
        continue
        
    extract_path = os.path.join(base_cand, "Extract-Classify-ACOS")
    indo_path = os.path.join(base_cand, "ACOS-IndoBERT")
    
    if _is_upstream(extract_path):
        base_project_dir = base_cand
        upstream_root = extract_path
        indo_root = indo_path if os.path.isdir(indo_path) else base_cand
        print(f"✓ Found project at: {base_cand}")
        break

# Clone if needed (Colab environment)
if upstream_root is None:
    print(f"📥 Cloning ACOS project from {ACOS_REPO_URL}...")
    base_project_dir = "/content"
    
    # Clone full repo
    temp_dir = '/tmp/ACOS_full_clone'
    os.system(f"rm -rf {temp_dir}")
    clone_result = os.system(f"git clone --depth 1 {ACOS_REPO_URL} {temp_dir}")
    
    if clone_result == 0:
        # Copy Extract-Classify-ACOS
        src_extract = os.path.join(temp_dir, 'Extract-Classify-ACOS')
        upstream_root = "/content/Extract-Classify-ACOS"
        if _is_upstream(src_extract):
            os.system(f'cp -r "{src_extract}" "{upstream_root}"')
            print(f"  ✓ Extract-Classify-ACOS: {upstream_root}")
        
        # Copy ACOS-IndoBERT  
        src_indo = os.path.join(temp_dir, 'ACOS-IndoBERT')
        indo_root = "/content/ACOS-IndoBERT"
        if os.path.isdir(src_indo):
            os.system(f'cp -r "{src_indo}" "{indo_root}"')
            print(f"  ✓ ACOS-IndoBERT: {indo_root}")
        
        os.system(f"rm -rf {temp_dir}")
    else:
        raise RuntimeError("Failed to clone ACOS repository")

# =============================================================
# CRITICAL: Setup sys.path in CORRECT ORDER
# =============================================================
print("\\n" + "="*60)
print("Setting up Python paths...")
print("="*60)

# MUST be in this order for imports to work:
_prepend_path(upstream_root)      # 1. Extract-Classify-ACOS (for bert_utils, modeling)
_prepend_path(indo_root)          # 2. ACOS-IndoBERT (for acos_id modules) 
_prepend_path(base_project_dir)   # 3. Base directory

print(f"  base_project_dir : {base_project_dir}")
print(f"  upstream_root    : {upstream_root}")
print(f"  indo_root        : {indo_root}")
print(f"  sys.path[0]      : {sys.path[0]}")
print(f"  modeling.py      : {os.path.isfile(os.path.join(upstream_root, 'modeling.py'))}")
print(f"  bert_utils/      : {os.path.isfile(os.path.join(upstream_root, 'bert_utils', 'tokenization.py'))}")

print("\\n" + "="*60)
print("Importing modules...")
print("="*60)

# =============================================================
# IMPORTS - Only after sys.path is correctly configured
# =============================================================

# Core BERT utilities (MUST import first after path setup)
from bert_utils.tokenization import BertTokenizer
print("  ✓ BertTokenizer")

from modeling import BertForQuadABSA, CategorySentiClassification  
print("  ✓ BertForQuadABSA, CategorySentiClassification")

# ACOS-ID modules
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

print(f"\\n✅ ALL IMPORTS SUCCESSFUL!")

# =============================================================
# Global setup
# =============================================================
random.seed(SEED)
np.random.seed(SEED) 
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if globals().get('ROCM_BENCHMARK', True):
        torch.backends.cudnn.benchmark = True

# Output directories
results_dir = os.path.join(indo_root, "results")
os.makedirs(results_dir, exist_ok=True)
print(f"\\n📁 Local results: {results_dir}")

# Google Drive sync setup
if 'GDRIVE_RESULTS' in os.environ:
    gdrive_results = os.environ['GDRIVE_RESULTS']
    print(f"☁️  GDrive results: {gdrive_results}")

print("\\n🎯 V5.1 Setup Complete - bert_utils import issue FIXED!")
'''

if __name__ == "__main__":
    print("V5.1 Fixed Cells Ready!")
    print("\\nTo use:")
    print("1. Add Cell 0 (Google Drive) at the beginning of your Colab notebook")
    print("2. Replace Cell 3 (Import & Path) with the fixed version")
    print("3. Run cells in order")
    
    print("\\n" + "="*60)
    print("CELL 0 - GOOGLE DRIVE SETUP:")
    print("="*60)
    print(CELL_0_GDRIVE_SETUP)
    
    print("\\n" + "="*60) 
    print("CELL 3 - FIXED IMPORT & PATH:")
    print("="*60)
    print(CELL_3_FIXED_IMPORT)