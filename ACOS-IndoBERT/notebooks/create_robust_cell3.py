#!/usr/bin/env python
# coding=utf-8
"""Create a more robust version of Cell 3 with better error handling."""

import json

notebook_path = "01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb"

# The new, robust Cell 3 content
ROBUST_CELL3 = r"""# Sel 3: Import semua modul & setup path dua-root (ROBUST VERSION)
import os, sys, time, json, pickle, random, math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# ============================================================
# DETEKSI ROOT DAN SETUP PATH (EKSPLISIT)
# ============================================================

# Deteksi root (lokal / Docker / Colab)
_ROOT_CANDIDATES = [
    '/shared-docker/ACOS',
    'd:/laragon/www/ACOS-ASLI',
    'D:/laragon/www/ACOS-ASLI',
    str(Path.cwd().parent.parent),
    str(Path.cwd().parent),
]

base_project_dir = None
for _c in _ROOT_CANDIDATES:
    p = Path(_c)
    if (p / 'Extract-Classify-ACOS').exists() and (p / 'ACOS-IndoBERT').exists():
        base_project_dir = str(p.resolve())
        break

if base_project_dir is None:
    print("❌ Root proyek tidak ditemukan!")
    print("Dicoba:")
    for _c in _ROOT_CANDIDATES:
        print(f"  - {_c}: {Path(_c).exists()}")
    raise RuntimeError('Root proyek tidak ditemukan. Edit _ROOT_CANDIDATES di Sel 3.')

upstream_root = str((Path(base_project_dir) / 'Extract-Classify-ACOS').resolve())
indo_root     = str((Path(base_project_dir) / 'ACOS-IndoBERT').resolve())

# Clear module cache untuk acos_id
if 'acos_id' in sys.modules:
    del sys.modules['acos_id']
modules_to_clear = [k for k in sys.modules.keys() if k.startswith('acos_id.')]
for mod in modules_to_clear:
    del sys.modules[mod]

# Hapus path lama jika ada, insert yang baru
for p in [base_project_dir, upstream_root, indo_root]:
    while p in sys.path:
        sys.path.remove(p)

sys.path.insert(0, upstream_root)
sys.path.insert(0, indo_root)
sys.path.insert(0, base_project_dir)

print(f'✓ Paths configured:')
print(f'  base_project_dir : {base_project_dir}')
print(f'  upstream_root    : {upstream_root}')
print(f'  indo_root        : {indo_root}')

# Verifikasi file penting ada
key_files = [
    (upstream_root, 'modeling.py'),
    (upstream_root, 'bert_utils/tokenization.py'),
    (indo_root, 'acos_id/__init__.py'),
    (indo_root, 'acos_id/cross_val.py'),
    (indo_root, 'acos_id/model_wrappers.py'),
]
print(f'\n✓ Verifying key files:')
for folder, filename in key_files:
    filepath = Path(folder) / filename
    if not filepath.exists():
        raise FileNotFoundError(f'File penting tidak ditemukan: {filepath}')
print('  All key files found!')

# ============================================================
# IMPORT MODUL
# ============================================================
print(f'\n{"="*60}')
print('Importing modules...')
print("="*60)

from bert_utils.tokenization import BertTokenizer
print('  ✓ BertTokenizer')

from modeling import BertForQuadABSA, CategorySentiClassification
print('  ✓ BertForQuadABSA, CategorySentiClassification')

import acos_id
print(f'  ✓ acos_id (v{acos_id.__version__})')

from acos_id import taxonomy as acos_taxonomy
print(f'  ✓ taxonomy ({len(acos_taxonomy.ASPECT_LABELS)} aspects)')

from acos_id import checkpoint as acos_ckpt
print('  ✓ checkpoint')

from acos_id.cross_val import (
    build_with_ratio, build_kfold_splits,
    ExperimentGrid, tokenize_all_splits,
)
print('  ✓ cross_val')

from acos_id.experiment_runner import (
    prepare_all_data, run_all_experiments, aggregate_cv_results,
)
print('  ✓ experiment_runner')

from acos_id import model_wrappers
print('  ✓ model_wrappers')

print(f'\n✅ ALL IMPORTS SUCCESSFUL!')

# Seed global
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if ROCM_BENCHMARK:
        torch.backends.cudnn.benchmark = True

# Path directories
data_dir        = os.path.join(indo_root, 'data', 'Apps-ACOS')
processed_dir   = os.path.join(data_dir, 'processed')
tokenized_base  = os.path.join(indo_root, 'tokenized_data')
results_base    = os.path.join(indo_root, 'results')
experiments_dir = os.path.join(results_base, 'experiments')
bert_cache_dir  = os.path.join(indo_root, 'backbones', 'indobert_base_p1')

os.makedirs(experiments_dir, exist_ok=True)

print(f'\nDirectory paths configured:')
print(f'  data_dir        : {data_dir}')
print(f'  tokenized_base  : {tokenized_base}')
print(f'  experiments_dir : {experiments_dir}')
print(f'\n✅ Setup complete!')
"""

print(f"Reading {notebook_path}...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 3 and replace it
cell_found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'Sel 3: Import semua modul' in source or '# Import modul acos_id' in source:
            print("Found Cell 3! Replacing with robust version...")
            
            # Split into lines and add newlines
            lines = ROBUST_CELL3.split('\n')
            cell['source'] = [line + '\n' if i < len(lines) - 1 else line 
                            for i, line in enumerate(lines)]
            cell_found = True
            print("✓ Cell 3 replaced with robust version")
            break

if not cell_found:
    print("❌ Could not find Cell 3 to replace")
else:
    # Save the notebook
    print(f"\nSaving updated notebook...")
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    
    print("✓ Notebook updated successfully!")
    print("\nChanges made:")
    print("1. Added module cache clearing")
    print("2. More robust path detection with .resolve()")
    print("3. Added file verification")
    print("4. Better error messages")
    print("5. Explicit import sequence with status messages")
    print("\nNOTE: You MUST restart the Jupyter kernel before running this cell!")
