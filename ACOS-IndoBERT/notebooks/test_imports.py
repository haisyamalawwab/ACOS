#!/usr/bin/env python
# coding=utf-8
"""Test if imports work correctly after sys.path setup."""

import os
import sys
from pathlib import Path

print("=" * 60)
print("Testing Import Sequence (mimicking notebook Cell 3)")
print("=" * 60)

# Step 1: Setup paths (same as notebook)
_ROOT_CANDIDATES = [
    '/shared-docker/ACOS',
    'd:/laragon/www/ACOS-ASLI',
    str(Path.cwd().parent.parent),
]

base_project_dir = None
for _c in _ROOT_CANDIDATES:
    if (Path(_c) / 'Extract-Classify-ACOS').exists() and (Path(_c) / 'ACOS-IndoBERT').exists():
        base_project_dir = str(Path(_c))
        break

if base_project_dir is None:
    print("❌ Root proyek tidak ditemukan")
    sys.exit(1)

upstream_root = os.path.join(base_project_dir, 'Extract-Classify-ACOS')
indo_root     = os.path.join(base_project_dir, 'ACOS-IndoBERT')

for p in [base_project_dir, upstream_root, indo_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

print(f"\n✓ Paths configured:")
print(f"  base_project_dir : {base_project_dir}")
print(f"  upstream_root    : {upstream_root}")
print(f"  indo_root        : {indo_root}")

# Step 2: Test upstream imports
print(f"\n{'='*60}")
print("Testing Upstream Imports")
print("=" * 60)

try:
    from bert_utils.tokenization import BertTokenizer
    print("✓ BertTokenizer imported")
except ImportError as e:
    print(f"❌ BertTokenizer import failed: {e}")
    sys.exit(1)

try:
    from modeling import BertForQuadABSA, CategorySentiClassification
    print("✓ BertForQuadABSA imported")
    print("✓ CategorySentiClassification imported")
except ImportError as e:
    print(f"❌ modeling import failed: {e}")
    sys.exit(1)

# Step 3: Test acos_id imports
print(f"\n{'='*60}")
print("Testing acos_id Imports")
print("=" * 60)

try:
    import acos_id
    print(f"✓ acos_id imported (version: {getattr(acos_id, '__version__', 'unknown')})")
except ImportError as e:
    print(f"❌ acos_id import failed: {e}")
    sys.exit(1)

try:
    from acos_id import taxonomy as acos_taxonomy
    print("✓ acos_taxonomy imported")
    print(f"  - ASPECT_LABELS: {len(acos_taxonomy.ASPECT_LABELS)} labels")
    print(f"  - OPINION_LABELS: {len(acos_taxonomy.OPINION_LABELS)} labels")
except ImportError as e:
    print(f"❌ acos_taxonomy import failed: {e}")
    sys.exit(1)

try:
    from acos_id import checkpoint as acos_ckpt
    print("✓ acos_checkpoint imported")
except ImportError as e:
    print(f"❌ acos_checkpoint import failed: {e}")
    sys.exit(1)

try:
    from acos_id.cross_val import (
        build_with_ratio, build_kfold_splits,
        ExperimentGrid, tokenize_all_splits,
    )
    print("✓ cross_val functions imported")
except ImportError as e:
    print(f"❌ cross_val import failed: {e}")
    sys.exit(1)

try:
    from acos_id.experiment_runner import (
        prepare_all_data, run_all_experiments, aggregate_cv_results,
    )
    print("✓ experiment_runner functions imported")
except ImportError as e:
    print(f"❌ experiment_runner import failed: {e}")
    sys.exit(1)

# Step 4: Test model_wrappers import (the problematic one)
print(f"\n{'='*60}")
print("Testing model_wrappers Import (THE KEY TEST)")
print("=" * 60)

try:
    from acos_id import model_wrappers
    print("✓ model_wrappers imported successfully!")
    
    # Check if functions exist
    if hasattr(model_wrappers, 'load_quad_tsv_dataset'):
        print("  ✓ load_quad_tsv_dataset() found")
    else:
        print("  ❌ load_quad_tsv_dataset() NOT found")
    
    if hasattr(model_wrappers, 'compute_extraction_metrics'):
        print("  ✓ compute_extraction_metrics() found")
    else:
        print("  ❌ compute_extraction_metrics() NOT found")
        
except ImportError as e:
    print(f"❌ model_wrappers import failed: {e}")
    print(f"\nDEBUG INFO:")
    print(f"  Python version: {sys.version}")
    print(f"  sys.path: {sys.path[:3]}...")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'='*60}")
print("✅ ALL IMPORTS SUCCESSFUL!")
print("=" * 60)
print("\nThe notebook should work now. If it still fails, the issue is")
print("likely with torch not being installed in your environment.")
