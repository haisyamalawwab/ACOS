# Fix untuk ModuleNotFoundError di Jupyter Notebook

## Masalah

```
ModuleNotFoundError: No module named 'acos_id.cross_val'
ModuleNotFoundError: No module named 'acos_id.model_wrappers'
```

Ini terjadi karena Jupyter kernel tidak mengenali path `ACOS-IndoBERT/` dengan benar.

## Solusi: Restart Kernel dan Jalankan Ulang

### Opsi 1: Restart Kernel (RECOMMENDED)

1. Di Jupyter, klik menu: **Kernel → Restart & Clear Output**
2. Jalankan ulang Cell 1, 2, dan 3 secara berurutan
3. Pastikan tidak ada error di Cell 3

### Opsi 2: Force Reload Modules

Tambahkan cell BARU sebelum Cell 3 dengan kode ini:

```python
# CELL BARU: Force reload sys.path
import sys
import os
from pathlib import Path

# Hapus cache Python
if 'acos_id' in sys.modules:
    del sys.modules['acos_id']

# Clear cached acos_id submodules
modules_to_clear = [k for k in sys.modules.keys() if k.startswith('acos_id.')]
for mod in modules_to_clear:
    del sys.modules[mod]

print("✓ Module cache cleared")
```

Lalu jalankan Cell 3 lagi.

### Opsi 3: Modifikasi Cell 3 dengan Explicit Path

Ganti Cell 3 dengan versi yang lebih eksplisit:

```python
# Sel 3: Import semua modul & setup path dua-root
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
    'D:/laragon/www/ACOS-ASLI',  # Try uppercase juga
    str(Path.cwd().parent.parent),
    str(Path.cwd().parent),  # Jika notebook di subfolder
]

base_project_dir = None
for _c in _ROOT_CANDIDATES:
    p = Path(_c)
    if (p / 'Extract-Classify-ACOS').exists() and (p / 'ACOS-IndoBERT').exists():
        base_project_dir = str(p.resolve())  # Use resolve() untuk absolute path
        break

if base_project_dir is None:
    print("❌ Root proyek tidak ditemukan!")
    print("Dicoba:")
    for _c in _ROOT_CANDIDATES:
        print(f"  - {_c}: {Path(_c).exists()}")
    raise RuntimeError('Root proyek tidak ditemukan. Edit _ROOT_CANDIDATES di Sel 3.')

upstream_root = str((Path(base_project_dir) / 'Extract-Classify-ACOS').resolve())
indo_root     = str((Path(base_project_dir) / 'ACOS-IndoBERT').resolve())

# Hapus path lama jika ada
for p in [base_project_dir, upstream_root, indo_root]:
    while p in sys.path:
        sys.path.remove(p)

# Insert di posisi 0 (prioritas tertinggi)
sys.path.insert(0, upstream_root)
sys.path.insert(0, indo_root)
sys.path.insert(0, base_project_dir)

print(f'✓ Paths configured:')
print(f'  base_project_dir : {base_project_dir}')
print(f'  upstream_root    : {upstream_root}')
print(f'  indo_root        : {indo_root}')
print(f'\nsys.path[0:3]:')
for i, p in enumerate(sys.path[:3]):
    print(f'  [{i}] {p}')

# Verifikasi file penting ada
print(f'\n✓ Verifying key files:')
key_files = [
    (upstream_root, 'modeling.py'),
    (upstream_root, 'bert_utils/tokenization.py'),
    (indo_root, 'acos_id/__init__.py'),
    (indo_root, 'acos_id/cross_val.py'),
    (indo_root, 'acos_id/model_wrappers.py'),
]
for folder, filename in key_files:
    filepath = Path(folder) / filename
    status = '✓' if filepath.exists() else '❌'
    print(f'  {status} {filepath.name}')
    if not filepath.exists():
        raise FileNotFoundError(f'File penting tidak ditemukan: {filepath}')

# ============================================================
# IMPORT MODUL UPSTREAM (Extract-Classify-ACOS)
# ============================================================
print(f'\n{"="*60}')
print('Importing upstream modules...')
print("=" * 60)

try:
    from bert_utils.tokenization import BertTokenizer
    print('  ✓ BertTokenizer')
except ImportError as e:
    print(f'  ❌ BertTokenizer: {e}')
    raise

try:
    from modeling import BertForQuadABSA, CategorySentiClassification
    print('  ✓ BertForQuadABSA')
    print('  ✓ CategorySentiClassification')
except ImportError as e:
    print(f'  ❌ modeling: {e}')
    raise

# ============================================================
# IMPORT MODUL ACOS_ID
# ============================================================
print(f'\n{"="*60}')
print('Importing acos_id modules...')
print("=" * 60)

try:
    import acos_id
    print(f'  ✓ acos_id (v{acos_id.__version__})')
except ImportError as e:
    print(f'  ❌ acos_id: {e}')
    raise

try:
    from acos_id import taxonomy as acos_taxonomy
    print(f'  ✓ taxonomy ({len(acos_taxonomy.ASPECT_LABELS)} aspects)')
except ImportError as e:
    print(f'  ❌ taxonomy: {e}')
    raise

try:
    from acos_id import checkpoint as acos_ckpt
    print('  ✓ checkpoint')
except ImportError as e:
    print(f'  ❌ checkpoint: {e}')
    raise

try:
    from acos_id.cross_val import (
        build_with_ratio, build_kfold_splits,
        ExperimentGrid, tokenize_all_splits,
    )
    print('  ✓ cross_val')
except ImportError as e:
    print(f'  ❌ cross_val: {e}')
    print(f'\nDEBUG: acos_id location: {acos_id.__file__}')
    raise

try:
    from acos_id.experiment_runner import (
        prepare_all_data, run_all_experiments, aggregate_cv_results,
    )
    print('  ✓ experiment_runner')
except ImportError as e:
    print(f'  ❌ experiment_runner: {e}')
    raise

try:
    from acos_id import model_wrappers
    print('  ✓ model_wrappers')
except ImportError as e:
    print(f'  ❌ model_wrappers: {e}')
    raise

print(f'\n{"="*60}')
print('✅ ALL IMPORTS SUCCESSFUL!')
print("=" * 60)

# ============================================================
# SEED GLOBAL
# ============================================================
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if ROCM_BENCHMARK:
        torch.backends.cudnn.benchmark = True

# ============================================================
# PATH DIRECTORIES
# ============================================================
data_dir        = os.path.join(indo_root, 'data', 'Apps-ACOS')
processed_dir   = os.path.join(data_dir, 'processed')
tokenized_base  = os.path.join(indo_root, 'tokenized_data')
results_base    = os.path.join(indo_root, 'results')
experiments_dir = os.path.join(results_base, 'experiments')
bert_cache_dir  = os.path.join(indo_root, 'backbones', 'indobert_base_p1')

os.makedirs(experiments_dir, exist_ok=True)

print(f'\n{"="*60}')
print('Directory paths:')
print("=" * 60)
print(f'  data_dir        : {data_dir}')
print(f'  tokenized_base  : {tokenized_base}')
print(f'  experiments_dir : {experiments_dir}')
print(f'  bert_cache_dir  : {bert_cache_dir}')
print(f'\n✅ Setup complete!')
```

## Debugging Tips

Jika masih error setelah restart kernel, jalankan ini di cell terpisah:

```python
# DEBUG: Check Python path dan module
import sys
from pathlib import Path

print("Python executable:", sys.executable)
print("\nPython version:", sys.version)
print("\nCurrent working dir:", Path.cwd())
print("\nsys.path (first 5):")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}] {p}")

# Check if acos_id is importable
try:
    import acos_id
    print(f"\n✓ acos_id found at: {acos_id.__file__}")
    print(f"  Version: {acos_id.__version__}")
    print(f"  Modules: {dir(acos_id)}")
except ImportError as e:
    print(f"\n❌ acos_id NOT found: {e}")

# Check if cross_val exists
acos_id_path = Path('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/acos_id')
print(f"\n✓ acos_id directory exists: {acos_id_path.exists()}")
print(f"  cross_val.py exists: {(acos_id_path / 'cross_val.py').exists()}")
print(f"  model_wrappers.py exists: {(acos_id_path / 'model_wrappers.py').exists()}")
```

## Penyebab Umum

1. **Jupyter kernel menggunakan Python environment yang berbeda**
   - Solusi: Pastikan kernel menggunakan env yang sama dengan instalasi packages

2. **sys.path tidak include indo_root**
   - Solusi: Gunakan Cell 3 versi eksplisit di atas

3. **Python bytecode cache (.pyc) corrupted**
   - Solusi: Hapus folder `acos_id/__pycache__/` dan restart kernel

4. **Case-sensitivity di Windows**
   - Solusi: Gunakan absolute path dengan `.resolve()`

## Quick Fix Command

Jalankan di terminal/command prompt:

```bash
cd d:\laragon\www\ACOS-ASLI\ACOS-IndoBERT

# Hapus cache Python
rd /s /q acos_id\__pycache__

# Restart Jupyter
jupyter notebook notebooks/01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb
```

Lalu di notebook:
1. Kernel → Restart & Clear Output
2. Run Cell 1, 2, 3 secara berurutan
