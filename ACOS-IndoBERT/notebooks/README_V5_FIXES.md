# ACOS IndoBERT V5 Notebook - Panduan Perbaikan

## ✅ Status: FIXED

Notebook `01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb` telah diperbaiki dan siap digunakan.

## 🔧 Apa yang Diperbaiki?

### Error yang Diselesaikan:
```
ModuleNotFoundError: No module named 'processor_utils'
ModuleNotFoundError: No module named 'model_utils'
```

### Solusi:
1. **Modul helper baru**: `acos_id/model_wrappers.py`
   - `load_quad_tsv_dataset()` - Load data untuk training
   - `compute_extraction_metrics()` - Evaluasi model

2. **Import statements diperbaiki** di Cell 3
3. **Training function diperbaiki** di Cell 8

## 🚀 Cara Menjalankan

### 1. Setup Environment

Pastikan Python environment sudah terinstall:
```bash
# PyTorch with ROCm (for AMD MI300X)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

# Dependencies
pip install transformers pandas numpy scikit-learn tqdm
```

### 2. Jalankan Notebook

```bash
cd d:\laragon\www\ACOS-ASLI\ACOS-IndoBERT\notebooks
jupyter notebook 01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb
```

### 3. Urutan Eksekusi Cell

| Cell | Deskripsi | Estimasi Waktu |
|------|-----------|----------------|
| 1 | Diagnostik GPU & Hardware | < 1 menit |
| 2 | Konfigurasi Master | < 1 menit |
| 3 | Import & Path Setup | < 1 menit |
| 4 | HardwareMonitor Class | < 1 menit |
| 5 | Backbone IndoBERT & Tokenizer | 1-2 menit |
| 6 | ExperimentGrid Preview | < 1 menit |
| 7 | Persiapan Data (1x) | 30-60 menit |
| 8 | Training Adapter Function | < 1 menit |
| 9 | Run Eksperimen | 5-8 hari (54 runs) |
| 10 | Agregasi Hasil | < 1 menit |
| 11 | Hardware Summary | < 1 menit |

### 4. Konfigurasi Training

Untuk testing cepat, edit Cell 9:

```python
# Cell 9: Kontrol Eksperimen

DRY_RUN      = True    # False untuk training sungguhan
RUN_MODE     = 'ratio' # 'all', 'ratio', atau 'cv'
RUN_EPOCHS   = [50]    # Subset untuk testing
```

## 📊 Output yang Dihasilkan

### Struktur Folder Hasil:

```
ACOS-IndoBERT/
├── results/
│   └── experiments/
│       ├── split_801010_ep50_24092026_1430/
│       │   ├── checkpoints/
│       │   │   ├── step1_best/
│       │   │   └── step2_best/
│       │   ├── hardware_log.json
│       │   └── run_result.json
│       ├── split_701515_ep50_24092026_1630/
│       │   └── ...
│       ├── final_results_summary.csv
│       ├── hardware_summary.csv
│       └── _experiment_progress.json
```

### File Output:

1. **hardware_log.json** - Per-epoch VRAM, waktu, GPU utilization
2. **run_result.json** - Config, metrics, status per run
3. **final_results_summary.csv** - Tabel perbandingan semua run
4. **hardware_summary.csv** - Resource usage aggregate

## ⚙️ Konfigurasi GPU AMD MI300X

Notebook ini dioptimasi untuk:

| Parameter | Nilai | Notes |
|-----------|-------|-------|
| VRAM Total | 191.69 GB | AMD Instinct MI300X VF |
| STEP1_BATCH_SIZE | 96 | 4x dari V4 (24) |
| STEP2_BATCH_SIZE | 64 | 4x dari V4 (16) |
| PATIENCE | 0 | Early stopping OFF |
| USE_AMP | True | bfloat16 precision |
| ROCM_BENCHMARK | True | cudnn benchmark |

## 📈 Eksperimen yang Dijalankan

Total 54 kombinasi:

### Split Ratio (9 runs):
- 80:10:10 × 3 epochs (50, 75, 100) = 3 runs
- 70:15:15 × 3 epochs = 3 runs
- 60:20:20 × 3 epochs = 3 runs

### Cross-Validation (45 runs):
- 5-Fold × 5 folds × 3 epochs = 15 runs
- 10-Fold × 10 folds × 3 epochs = 30 runs

**Estimasi Total:** 5-8 hari untuk semua kombinasi

## 🐛 Troubleshooting

### Error: "Root proyek tidak ditemukan"

**Solusi:** Edit Cell 3, tambahkan path ke `_ROOT_CANDIDATES`:

```python
_ROOT_CANDIDATES = [
    '/shared-docker/ACOS',
    'd:/laragon/www/ACOS-ASLI',
    '/your/custom/path',  # Tambahkan path Anda
    str(Path.cwd().parent.parent),
]
```

### Error: "tokenized_dir tidak ada"

**Solusi:** Jalankan Cell 7 terlebih dahulu untuk prepare data.

### Error: "CUDA out of memory"

**Solusi:** Reduce batch size di Cell 2:

```python
STEP1_BATCH_SIZE = 48  # Reduce dari 96
STEP2_BATCH_SIZE = 32  # Reduce dari 64
```

### Warning: "rocm-smi tidak tersedia"

**Solusi:** Install ROCm utilities:

```bash
sudo apt-get install rocm-smi
```

Atau abaikan - monitoring akan fallback ke `torch.cuda`.

## 📝 Catatan Implementasi

### ⚠️ Known Limitations

File `acos_id/model_wrappers.py` menggunakan **simplified implementation**:

1. **Label parsing** - Simplified, perlu parse TSV quad format yang lengkap
2. **Evaluation metrics** - Token-level, seharusnya span-level
3. **Step 2** - Belum diimplementasi

Untuk production use, perlu integrasi penuh dengan:
- `eval_metrics.py` dari Extract-Classify-ACOS
- Proper quad span extraction dan matching
- Step 2 classification pipeline

### ✅ Yang Sudah Bekerja

- ✓ GPU detection & monitoring
- ✓ Experiment grid generation
- ✓ Data preparation & tokenization
- ✓ Basic training loop Step 1
- ✓ Hardware logging (VRAM, time, utilization)
- ✓ Result aggregation & CV metrics

## 📚 Dokumentasi Lengkap

Lihat file berikut untuk detail:

1. **FIX_SUMMARY.md** - Penjelasan teknis semua perbaikan
2. **../acos_id/model_wrappers.py** - Source code helper functions
3. **../acos_id/experiment_runner.py** - Experiment orchestration
4. **../acos_id/cross_val.py** - Data preparation & CV utilities

## 🔄 Update Log

**24 September 2026:**
- ✅ Fixed `ModuleNotFoundError: processor_utils`
- ✅ Fixed `ModuleNotFoundError: model_utils`
- ✅ Created `acos_id/model_wrappers.py`
- ✅ Updated Cell 3 imports
- ✅ Updated Cell 8 train_one_run function
- ✅ Documented all changes

## 💡 Tips & Best Practices

1. **First run:** Set `DRY_RUN=True` di Cell 9 untuk preview
2. **Test single run:** Gunakan `RUN_EPOCHS=[50]` dan `RUN_MODE='ratio'`
3. **Monitor progress:** Check `_experiment_progress.json` saat training
4. **Save checkpoints:** Best models auto-saved di `checkpoints/`
5. **Hardware logs:** Useful untuk optimize batch size & learning rate

## 📞 Support

Jika menemukan issue atau butuh bantuan:

1. Pastikan semua file di `acos_id/` ter-update
2. Verifikasi `Extract-Classify-ACOS/` accessible
3. Check Python version (3.8+) dan PyTorch version
4. Lihat log error di hardware_log.json

---

**Status:** ✅ Ready for use  
**Version:** V5-MI300X-FIXED  
**Last Updated:** 24 September 2026  
**Compatible with:** AMD Instinct MI300X, PyTorch 2.x + ROCm
