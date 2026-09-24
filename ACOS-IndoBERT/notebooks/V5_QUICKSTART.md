# V5 Notebook Quickstart Guide

## 🚀 Quick Start (3 Steps)

### 1. Open the Notebook
```bash
jupyter notebook 01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb
```

### 2. Run Cells 1-3
- **Cell 1**: Hardware diagnostics (validates GPU)
- **Cell 2**: Configuration (set hyperparameters)
- **Cell 3**: Imports (✅ FIXED - now works correctly)

### 3. Review the Plan
- **Cell 6**: Preview all 54 experiment runs (dry run)

---

## 📋 What's Fixed in Cell 3

**Previous Issue:**
```python
ModuleNotFoundError: No module named 'acos_id.cross_val'
ModuleNotFoundError: No module named 'acos_id.model_wrappers'
```

**Solution Applied:**
- ✅ Robust path detection with module validation
- ✅ Skips incomplete Docker locations automatically
- ✅ Validates all 5 required modules before proceeding
- ✅ Clear error messages if something is missing

**Now it works in:**
- ✅ Windows local development
- ✅ Docker production environment
- ✅ Google Colab
- ✅ Any Jupyter environment

---

## 🔧 Configuration Highlights (Cell 2)

**Optimized for AMD MI300X (191 GB VRAM):**
```python
STEP1_BATCH_SIZE = 96     # 4x larger than V4
STEP2_BATCH_SIZE = 64     # 4x larger than V4
PATIENCE = 0              # No early stopping
USE_AMP = True            # bfloat16 mixed precision
```

**Experiment Matrix:**
- **Epochs**: 50, 75, 100
- **Split Ratios**: 80:10:10, 70:15:15, 60:20:20
- **Cross-Validation**: 5-fold, 10-fold
- **Total Runs**: 54 experiments

---

## 📊 Execution Overview

### Cell Order
```
Cell 1  ✓ GPU diagnostics (30 sec)
Cell 2  ✓ Configuration (instant)
Cell 3  ✓ Imports & paths (10 sec)
Cell 4  ✓ HardwareMonitor class (instant)
Cell 5  ✓ Load backbone (5 min)
Cell 6  ✓ Preview experiments (instant, DRY_RUN)
Cell 7  ⏱ Prepare data (30-60 min, 1x only)
Cell 8  ✓ Training functions (instant)
Cell 9  ⏱ Run all experiments (5-8 DAYS for 54 runs)
Cell 10 ✓ Aggregate results
Cell 11 ✓ Hardware summary
```

### Quick Test Run (Before Full Training)
```python
# In Cell 9, set:
DRY_RUN = True
RUN_MODE = 'ratio'  # Only 9 runs instead of 54
RUN_EPOCHS = [50]   # Only 50 epochs instead of [50, 75, 100]
```

---

## 🐛 Troubleshooting

### Cell 3 Still Fails?

**Check 1: Verify files exist**
```bash
cd d:\laragon\www\ACOS-ASLI\ACOS-IndoBERT\acos_id
dir *.py
```

Expected files:
- `taxonomy.py`
- `checkpoint.py`
- `cross_val.py` ⚠️ Must exist
- `experiment_runner.py` ⚠️ Must exist
- `model_wrappers.py` ⚠️ Must exist

**Check 2: File sizes not zero**
```bash
# Files should have content (> 1 KB each)
ls -lh acos_id/*.py
```

**Check 3: Run test script**
```bash
cd notebooks
python test_cell3_imports.py
```

### Cell 3 Output Shows Warnings?

If you see:
```
⚠️  Skipping /shared-docker/ACOS: acos_id incomplete 
    (missing: ['cross_val.py', ...])
```

This is **NORMAL** - it means the notebook correctly skipped an incomplete location and will use the next valid one.

### Cell 9 Takes Too Long?

**Subset options:**
```python
# Test with smallest subset first
DRY_RUN = False
RUN_MODE = 'ratio'      # 9 runs (vs 'all' = 54 runs)
RUN_EPOCHS = [50]       # 1 epoch setting (vs [50, 75, 100])
```

**Estimated durations:**
- 1 run (50 epochs): ~4 hours
- 9 runs (ratio only): ~36 hours (1.5 days)
- 54 runs (all): ~216 hours (9 days)

---

## 📈 Monitoring During Training

**Real-time stats printed every epoch:**
```
Ep  Phase   Loss      F1%   VRAM          Util%  Samp/s    Dur
1   step1   0.4235   96.50  12.34/191.69G  87%   1250      2m15s
```

**Hardware logs saved automatically:**
- `experiments/<run_id>/hardware_log.json`
- Contains VRAM, GPU util, timing for every epoch

**Check progress:**
```bash
# See completed runs
ls -lt experiments/

# View latest hardware log
cat experiments/*/hardware_log.json | grep step1_f1
```

---

## 💾 Output Structure

```
ACOS-IndoBERT/
  results/
    experiments/
      split_801010_ep50/
        checkpoints/
          step1_best/
          step2_best/
        hardware_log.json
        results_step1.json
        results_step2.json
      split_801010_ep75/
      split_801010_ep100/
      ...
      final_results_summary.csv
      hardware_summary.csv
```

---

## 🎯 Success Indicators

**Cell 3 successful:**
```
✅ PATHS DETECTED SUCCESSFULLY
✅ ALL IMPORTS SUCCESSFUL!
✅ Setup complete!
```

**Training successful:**
```
[Step 1] SELESAI | Best F1=97.23% di ep47
[Step 2] SELESAI | Best F1=95.81% di ep42
```

**Full run successful:**
```
Total run: 54 | OK: 54 | Error: 0 | Skip: 0
Top 10 berdasarkan Step1 F1:
  run_id               step1_f1  step2_f1
  split_801010_ep100   97.45     96.12
  ...
```

---

## 📚 Additional Resources

- **Full Fix Details**: See `V5_CELL3_FIX_COMPLETE.md`
- **Test Script**: Run `python test_cell3_imports.py`
- **V4 Working Example**: `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`

---

**Last Updated:** 2026-09-24  
**Status:** ✅ Ready for Production Use
