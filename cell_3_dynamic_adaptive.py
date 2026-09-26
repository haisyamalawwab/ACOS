# =============================================================================
# CELL 3: ADAPTIVE PATH SETUP BASED ON DETECTED ENVIRONMENT 
# Uses ENV_CONFIG from Cell 0 dynamic detection
# =============================================================================

import os, sys, time, json, pickle, random, math, importlib, urllib.request
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import torch

# =============================================================================
# GET ENVIRONMENT CONFIG FROM CELL 0
# =============================================================================

env_config = globals().get('ENV_CONFIG', {
    'platform': 'unknown',
    'setup_strategy': 'local_path',
    'project_paths': [str(Path.cwd())]
})

print("🔧 ADAPTIVE ACOS SETUP")
print("=" * 50)
print(f"Platform: {env_config.get('platform', 'unknown').upper()}")
print(f"Strategy: {env_config.get('setup_strategy', 'unknown')}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _prepend_path(p):
    """Force path to front of sys.path"""
    if not p or not os.path.isdir(p):
        return None
    p_str = str(Path(p).resolve())
    while p_str in sys.path:
        sys.path.remove(p_str)
    sys.path.insert(0, p_str)
    return p_str

def _is_upstream(d):
    """Check if directory contains valid Extract-Classify-ACOS"""
    if not d or not os.path.isdir(d):
        return False
    return (os.path.isfile(os.path.join(d, 'modeling.py')) and 
            os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py')))

def _is_indo_complete(d):
    """Check if ACOS-IndoBERT has acos_id modules"""
    if not d or not os.path.isdir(d):
        return False
    acos_id_dir = os.path.join(d, 'acos_id')
    return os.path.isdir(acos_id_dir) and len(os.listdir(acos_id_dir)) > 5

# =============================================================================
# PLATFORM-SPECIFIC PROJECT DETECTION/SETUP
# =============================================================================

ACOS_REPO_URL = "https://github.com/haisyamalawwab/ACOS.git"

base_project_dir = None
upstream_root = None
indo_root = None

# Get project path candidates based on detected environment
project_candidates = env_config.get('project_paths', [str(Path.cwd())])

print(f"🔍 Searching {len(project_candidates)} locations...")

# =================================================================
# STRATEGY 1: FIND EXISTING PROJECT
# =================================================================
for candidate in project_candidates:
    if not os.path.isdir(candidate):
        continue
        
    extract_path = os.path.join(candidate, "Extract-Classify-ACOS")
    indo_path = os.path.join(candidate, "ACOS-IndoBERT")
    
    print(f"  Checking: {candidate}")
    
    if _is_upstream(extract_path):
        base_project_dir = candidate
        upstream_root = extract_path
        indo_root = indo_path if _is_indo_complete(indo_path) else candidate
        
        print(f"  ✅ Found complete ACOS project")
        print(f"     Extract-Classify-ACOS: {extract_path}")
        print(f"     ACOS-IndoBERT: {indo_path}")
        break
    elif os.path.isdir(extract_path) or os.path.isdir(indo_path):
        print(f"  ⚠️  Partial ACOS project (incomplete)")

# =================================================================
# STRATEGY 2: CLONE IF NOT FOUND (Cloud/VPS)
# =================================================================
if upstream_root is None and env_config.get('setup_strategy') in ['clone', 'local_or_clone']:
    
    print(f"\\n📥 Project not found. Cloning from {ACOS_REPO_URL}")
    
    # Determine clone destination based on platform
    if env_config.get('platform') == 'colab':
        base_project_dir = '/content'
    elif env_config.get('platform') == 'kaggle':
        base_project_dir = '/kaggle/working'
    else:
        # VPS/Cloud - use first candidate or current directory
        base_project_dir = project_candidates[0] if project_candidates else str(Path.cwd())
    
    print(f"   Target: {base_project_dir}")
    
    # Clone repository
    temp_clone = '/tmp/acos_full_clone'
    os.system(f"rm -rf {temp_clone}")
    
    clone_cmd = f"git clone --depth 1 {ACOS_REPO_URL} {temp_clone}"
    print(f"   Running: {clone_cmd}")
    
    result = os.system(clone_cmd)
    
    if result == 0:
        # Copy to target locations
        upstream_root = os.path.join(base_project_dir, 'Extract-Classify-ACOS')
        indo_root = os.path.join(base_project_dir, 'ACOS-IndoBERT')
        
        # Copy Extract-Classify-ACOS
        src_extract = os.path.join(temp_clone, 'Extract-Classify-ACOS')
        if _is_upstream(src_extract):
            os.system(f'cp -r "{src_extract}" "{upstream_root}"')
            print(f"   ✅ Extract-Classify-ACOS → {upstream_root}")
        
        # Copy ACOS-IndoBERT
        src_indo = os.path.join(temp_clone, 'ACOS-IndoBERT')  
        if os.path.isdir(src_indo):
            os.system(f'cp -r "{src_indo}" "{indo_root}"')
            print(f"   ✅ ACOS-IndoBERT → {indo_root}")
        
        # Cleanup
        os.system(f"rm -rf {temp_clone}")
        
        print("   🎯 Clone completed successfully")
    else:
        raise RuntimeError(f"Failed to clone ACOS repository (exit code: {result})")

# =================================================================
# STRATEGY 3: LOCAL PATH ERROR (Local development)
# =================================================================
elif upstream_root is None:
    print("\\n❌ ACOS project not found in any candidate locations:")
    for i, candidate in enumerate(project_candidates, 1):
        exists = "✅" if os.path.exists(candidate) else "❌"
        print(f"   {i}. {exists} {candidate}")
    
    print(f"\\n💡 Solutions:")
    print(f"   1. Clone manually: git clone {ACOS_REPO_URL}")
    print(f"   2. Update project_paths in ENV_CONFIG")
    print(f"   3. Create symlink to existing ACOS project")
    
    raise FileNotFoundError("ACOS project not found. Please clone or update paths.")

# =============================================================================
# CRITICAL: SYS.PATH SETUP IN CORRECT ORDER
# =============================================================================

print(f"\\n🛠️  CONFIGURING PYTHON IMPORT PATHS")
print("=" * 50)

# MUST be in this exact order for bert_utils import to work:
path_order = [
    ("Extract-Classify-ACOS", upstream_root),
    ("ACOS-IndoBERT", indo_root), 
    ("Base Project", base_project_dir)
]

for name, path in path_order:
    if path and _prepend_path(path):
        print(f"  ✅ {name}: {path}")
    else:
        print(f"  ❌ {name}: {path} (invalid)")

print(f"\\n📋 Final sys.path[0]: {sys.path[0]}")

# Verify critical files
critical_files = [
    ("modeling.py", os.path.join(upstream_root, 'modeling.py')),
    ("bert_utils/tokenization.py", os.path.join(upstream_root, 'bert_utils', 'tokenization.py')),
    ("acos_id/__init__.py", os.path.join(indo_root, 'acos_id', '__init__.py'))
]

print("\\n🔍 Verifying critical files:")
all_critical_exist = True
for name, filepath in critical_files:
    exists = os.path.isfile(filepath)
    status = "✅" if exists else "❌"
    print(f"  {status} {name}")
    if not exists:
        all_critical_exist = False

if not all_critical_exist:
    raise FileNotFoundError("Critical ACOS files missing. Check project structure.")

# =============================================================================
# MODULE IMPORTS - THE MOMENT OF TRUTH
# =============================================================================

print(f"\\n🔥 IMPORTING MODULES (bert_utils fix test)")
print("=" * 50)

try:
    # The problematic import that was failing - should work now!
    from bert_utils.tokenization import BertTokenizer
    print("  🎉 BertTokenizer - SUCCESS!")
    
    from modeling import BertForQuadABSA, CategorySentiClassification  
    print("  ✅ BertForQuadABSA, CategorySentiClassification")
    
    # ACOS-ID modules
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

except ImportError as e:
    print(f"  ❌ IMPORT FAILED: {e}")
    print(f"\\n🔍 Debug info:")
    print(f"     sys.path[0]: {sys.path[0]}")
    print(f"     upstream_root: {upstream_root}")
    print(f"     Available in sys.path[0]: {os.listdir(sys.path[0]) if os.path.exists(sys.path[0]) else 'Not found'}")
    raise

print(f"\\n🏆 ALL IMPORTS SUCCESSFUL!")

# =============================================================================
# FINAL SETUP
# =============================================================================

print(f"\\n⚙️  FINAL CONFIGURATION")
print("=" * 50)

# Global random seeds
random.seed(SEED)
np.random.seed(SEED) 
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if globals().get('ROCM_BENCHMARK', True):
        torch.backends.cudnn.benchmark = True

# Setup results directory
results_dir = os.path.join(indo_root, "results")
os.makedirs(results_dir, exist_ok=True)

print(f"📁 Results directory: {results_dir}")

# Platform-specific backup setup
if env_config.get('platform') == 'colab' and os.path.exists('/content/drive'):
    backup_dir = '/content/drive/MyDrive/ACOS_V51_BACKUP'
    os.makedirs(backup_dir, exist_ok=True)
    print(f"☁️  Backup directory: {backup_dir}")

print("\\n" + "=" * 60)
print(f"🎯 V5.1 SETUP COMPLETE FOR {env_config.get('platform', 'UNKNOWN').upper()}")
print("🔧 bert_utils import issue = FIXED!")
print("🚀 Ready for experiments!")
print("=" * 60)