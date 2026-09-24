# Test script for Cell 3 path detection and imports
import os
import sys
import importlib
from pathlib import Path

print("="*70)
print("TESTING CELL 3 - PATH DETECTION AND IMPORTS")
print("="*70)

# ============================================================
# DETEKSI ROOT DAN SETUP PATH (MULTI-TIER DEFENSIVE)
# ============================================================

def _cari_base_project():
    """Cari root proyek yang mengandung Extract-Classify-ACOS dan ACOS-IndoBERT."""
    kandidat = [
        '/shared-docker/ACOS',
        'd:/laragon/www/ACOS-ASLI',
        'D:/laragon/www/ACOS-ASLI',
        str(Path.cwd().parent.parent),
        str(Path.cwd().parent),
        str(Path.cwd()),
    ]
    
    print("\n[1] Searching for base project directory...")
    for _c in kandidat:
        p = Path(_c)
        print(f"  Trying: {_c}")
        if not p.exists():
            print(f"    ✗ Path doesn't exist")
            continue
        extract = p / 'Extract-Classify-ACOS'
        indo = p / 'ACOS-IndoBERT'
        print(f"    Extract-Classify-ACOS exists: {extract.exists()}")
        print(f"    ACOS-IndoBERT exists: {indo.exists()}")
        # Verifikasi subfolder kunci ada
        if (extract.exists() and (extract / 'modeling.py').exists() and
            indo.exists() and (indo / 'acos_id').is_dir()):
            print(f"    ✓ VALID - Found all required components")
            return str(p.resolve())
        else:
            print(f"    ✗ Missing required components")
    return None


def _cari_indo_root():
    """Cari folder ACOS-IndoBERT dengan subfolder acos_id/."""
    kandidat = []
    _base = globals().get('base_project_dir') or str(Path.cwd())
    kandidat += [
        str(Path(_base) / 'ACOS-IndoBERT'),
        str(Path('ACOS-IndoBERT').absolute()),
        str((Path.cwd().parent / 'ACOS-IndoBERT').absolute()),
        str(Path.cwd()),
    ]
    print("\n[2] Searching for ACOS-IndoBERT directory...")
    for _d in kandidat:
        p = Path(_d)
        print(f"  Trying: {_d}")
        if p.is_dir() and (p / 'acos_id').is_dir():
            print(f"    ✓ VALID - Found acos_id subdirectory")
            return str(p.resolve())
        else:
            print(f"    ✗ Invalid or missing acos_id")
    return None


# Find base project
base_project_dir = _cari_base_project()
if base_project_dir is None:
    print("\n❌ ERROR: Root proyek tidak ditemukan!")
    print("Pastikan struktur:")
    print("  ACOS-ASLI/")
    print("    Extract-Classify-ACOS/modeling.py")
    print("    ACOS-IndoBERT/acos_id/")
    sys.exit(1)

upstream_root = str((Path(base_project_dir) / 'Extract-Classify-ACOS').resolve())
indo_root = _cari_indo_root()

if indo_root is None:
    print(f"\n❌ ERROR: Folder ACOS-IndoBERT/acos_id tidak ditemukan di {base_project_dir}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ PATHS DETECTED SUCCESSFULLY")
print("="*70)
print(f"base_project_dir : {base_project_dir}")
print(f"upstream_root    : {upstream_root}")
print(f"indo_root        : {indo_root}")

# Verifikasi file penting ada
print("\n[3] Verifying critical modules...")
ACOS_ID_MODULES = ['taxonomy', 'checkpoint', 'cross_val', 'experiment_runner', 'model_wrappers']
_acos_id_dir = Path(indo_root) / 'acos_id'
_missing = []
for m in ACOS_ID_MODULES:
    fpath = _acos_id_dir / f"{m}.py"
    exists = fpath.is_file()
    size = fpath.stat().st_size if exists else 0
    status = "✓ OK" if exists and size > 0 else "✗ MISSING"
    print(f"  {m:20s}: {status} ({size:,} bytes)")
    if not exists or size == 0:
        _missing.append(f"{m}.py")

if _missing:
    print(f"\n❌ ERROR: acos_id tidak lengkap di {_acos_id_dir}")
    print(f"Missing: {_missing}")
    sys.exit(1)

# Clear sys.path dan module cache
print("\n[4] Setting up Python paths...")
def _prepend_path(p):
    """Paksa p ke posisi terdepan sys.path."""
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

_prepend_path(indo_root)
_prepend_path(upstream_root)

print(f"  sys.path[0]: {sys.path[0]}")
print(f"  sys.path[1]: {sys.path[1]}")

# Clear acos_id cache
print("\n[5] Clearing module cache...")
cleared = []
for _m in list(sys.modules):
    if _m == 'acos_id' or _m.startswith('acos_id.'):
        del sys.modules[_m]
        cleared.append(_m)
print(f"  Cleared {len(cleared)} modules")

# ============================================================
# TEST IMPORTS
# ============================================================
print("\n" + "="*70)
print("TESTING IMPORTS")
print("="*70)

errors = []

# Test 1: bert_utils.tokenization
print("\n[Import 1/7] bert_utils.tokenization.BertTokenizer")
try:
    from bert_utils.tokenization import BertTokenizer
    print("  ✓ SUCCESS")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("bert_utils.tokenization", str(e)))

# Test 2: modeling
print("\n[Import 2/7] modeling.BertForQuadABSA, CategorySentiClassification")
try:
    from modeling import BertForQuadABSA, CategorySentiClassification
    print("  ✓ SUCCESS")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("modeling", str(e)))

# Test 3: acos_id
print("\n[Import 3/7] acos_id")
try:
    acos_id = importlib.import_module('acos_id')
    version = getattr(acos_id, '__version__', 'unknown')
    print(f"  ✓ SUCCESS (version: {version})")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id", str(e)))

# Test 4: acos_id.taxonomy
print("\n[Import 4/7] acos_id.taxonomy")
try:
    acos_taxonomy = importlib.import_module('acos_id.taxonomy')
    n_aspects = len(getattr(acos_taxonomy, 'ASPECT_LABELS', []))
    print(f"  ✓ SUCCESS ({n_aspects} aspects)")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id.taxonomy", str(e)))

# Test 5: acos_id.checkpoint
print("\n[Import 5/7] acos_id.checkpoint")
try:
    acos_ckpt = importlib.import_module('acos_id.checkpoint')
    print("  ✓ SUCCESS")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id.checkpoint", str(e)))

# Test 6: acos_id.cross_val
print("\n[Import 6/7] acos_id.cross_val")
try:
    acos_cross_val = importlib.import_module('acos_id.cross_val')
    build_with_ratio = acos_cross_val.build_with_ratio
    build_kfold_splits = acos_cross_val.build_kfold_splits
    ExperimentGrid = acos_cross_val.ExperimentGrid
    tokenize_all_splits = acos_cross_val.tokenize_all_splits
    print("  ✓ SUCCESS (all functions imported)")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id.cross_val", str(e)))

# Test 7: acos_id.experiment_runner
print("\n[Import 7/7] acos_id.experiment_runner")
try:
    acos_experiment_runner = importlib.import_module('acos_id.experiment_runner')
    prepare_all_data = acos_experiment_runner.prepare_all_data
    run_all_experiments = acos_experiment_runner.run_all_experiments
    aggregate_cv_results = acos_experiment_runner.aggregate_cv_results
    print("  ✓ SUCCESS (all functions imported)")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id.experiment_runner", str(e)))

# Test 8: acos_id.model_wrappers
print("\n[Import 8/8] acos_id.model_wrappers")
try:
    model_wrappers = importlib.import_module('acos_id.model_wrappers')
    print("  ✓ SUCCESS")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    errors.append(("acos_id.model_wrappers", str(e)))

# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "="*70)
print("FINAL REPORT")
print("="*70)

if errors:
    print(f"\n❌ FAILED: {len(errors)} import error(s)")
    for module, error in errors:
        print(f"\n  Module: {module}")
        print(f"  Error: {error}")
    sys.exit(1)
else:
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print("\nCell 3 is working correctly. The notebook is ready to use.")
    sys.exit(0)
