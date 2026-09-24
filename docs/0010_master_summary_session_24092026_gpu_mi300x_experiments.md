# Master Summary — Sesi Analisis & Implementasi GPU AMD MI300X
> **Tanggal Sesi:** 2026-09-24 pukul 21:03–21:32 WIB
> **Notebook:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`
> **GPU:** AMD Instinct MI300X VF — 191.69 GB VRAM (ROCm HIP 7.14)

---

## 1. Pertanyaan Awal & Temuan Kunci

### Pertanyaan:
1. Jika `NUM_EPOCHS` berbeda, apakah perlu folder baru bertimestamp?
2. Untuk GPU besar (MI300X), perlu no early stopping?

### Temuan:

#### Mengapa Training Berhenti di Epoch 3?
**Bukan early stopping!** Early stopping tidak mungkin terpicu di epoch 3 karena:
```python
PATIENCE               = 5   # butuh 5 epoch tanpa improvement
MIN_EPOCHS_BEFORE_STOP = 5   # baru aktif setelah epoch ke-5
```

Penyebab sebenarnya: **Cache hit aktif** (`RESUME_LAST_SESSION = True`) — notebook melanjutkan sesi `appsid_24092026_0901` yang hanya tersimpan 3 epoch.

#### Inkonsistensi yang Ditemukan
| Item | Nilai di Kode | Nilai di Output Tersimpan |
|------|--------------|--------------------------|
| `NUM_EPOCHS` | 50 | 15 (sesi lama) |
| Epoch berjalan | belum run | 3 epoch |
| Early stopping | PATIENCE=5 (aktif) | belum terpicu |

---

## 2. Hardware & Dataset

### GPU AMD MI300X VF
| Parameter | Nilai |
|-----------|-------|
| Total VRAM | 191.69 GB |
| Akselerator | AMD ROCm HIP 7.14.60850 |
| PyTorch | 2.12.0+rocm7.14.0 |
| `is_large_gpu` | True |
| VRAM dipakai (sesi lama) | ~5.308 MB (2.8% dari total!) |

### Dataset Apps-ACOS (appsid)
| Split | Baris/Klausa | Rasio |
|-------|-------------|-------|
| train | 60.159 | 79.1% |
| dev | 8.027 | 10.6% |
| test | 7.891 | 10.4% |
| **TOTAL** | **76.077** | 100% |

Split berdasarkan `review_id` dari `stage2_{train,val,test}.jsonl`.

---

## 3. Perubahan Konfigurasi yang Diperlukan

### Ubah di Sel 3 Notebook (5 menit)
```python
# ─── SEBELUM (konfigurasi lama) ───────────────────────
NUM_EPOCHS          = 50    # kode sudah 50, tapi output lama = 15
PATIENCE            = 5     # early stopping AKTIF
RESUME_LAST_SESSION = True  # melanjutkan sesi lama (3 epoch)

# ─── SESUDAH (optimasi untuk GPU MI300X) ──────────────
NUM_EPOCHS          = 50    # full 50 epoch
PATIENCE            = 0     # NONAKTIFKAN early stopping
RESUME_LAST_SESSION = False # buat folder timestamp BARU

# Bonus: naikkan batch size (VRAM hanya 2.8% terpakai)
STEP1_BATCH_SIZE    = 96    # dari 24 → 4x lebih cepat
STEP2_BATCH_SIZE    = 64    # dari 16 → 4x lebih cepat
```

---

## 4. Rencana Eksperimen Lengkap

### Dimensi Eksperimen
| Dimensi | Nilai |
|---------|-------|
| **Epochs** | 50, 75, 100 |
| **Train:Dev:Test Split** | 80:10:10, 70:15:15, 60:20:20 |
| **Cross Validation** | 5-Fold, 10-Fold (berbasis review_id) |

### Total Kombinasi
```
9 run  = 3 epoch × 3 split-ratio
15 run = 3 epoch × 5-fold CV
30 run = 3 epoch × 10-fold CV
─────────────────────────────────
54 run TOTAL (berjalan serial, 1-per-1)
```

---

## 5. File yang Dibuat

### File Baru di `acos_id/`

#### `acos_id/cross_val.py` ← BARU
Modul K-Fold Cross Validation + split ratio custom.

| Fungsi/Kelas | Deskripsi |
|-------------|-----------|
| `build_with_ratio()` | Build TSV dengan rasio custom (80:10:10, dll) |
| `build_kfold_splits()` | Generate semua fold K-Fold CV (5 atau 10 fold) |
| `tokenize_all_splits()` | Tokenisasi semua split/fold sekaligus |
| `ExperimentGrid` | Daftar + iterasi semua kombinasi eksperimen |

**Desain kritis:** CV dilakukan pada level **`review_id`** (bukan klausa) — semua klausa dari 1 ulasan selalu masuk fold yang sama → **tidak ada data leakage**.

#### `acos_id/experiment_runner.py` ← BARU
Auto-runner untuk semua kombinasi.

| Fungsi | Deskripsi |
|--------|-----------|
| `prepare_all_data()` | Build TSV + tokenisasi semua (fase persiapan, 1x) |
| `run_all_experiments()` | Runner otomatis 1-per-1 dengan logging progress |
| `aggregate_cv_results()` | Hitung mean ± std F1 per fold |

### Dokumen di `docs/`

| File | Isi |
|------|-----|
| `docs/0007_analisis_konfigurasi_gpu_mi300x_no_early_stopping_24092026.md` | Analisis notebook: mengapa stop epoch 3, fix PATIENCE & RESUME |
| `docs/0008_rencana_eksperimen_full_training_crossval_mi300x_24092026.md` | Rencana eksperimen lengkap (epoch, split, CV) |
| `docs/0009_implementasi_cross_val_split_ratio_experiment_runner_24092026.md` | Panduan implementasi cara pakai di notebook |
| `docs/0010_master_summary_session_24092026_gpu_mi300x_experiments.md` | **File ini** — ringkasan sesi lengkap |

---

## 6. Cara Penggunaan di Notebook (Ringkasan)

### Fase 0 — Fix Cepat (Jalankan sekarang)
```python
# Sel 3 notebook — ubah 3 baris ini:
PATIENCE            = 0
RESUME_LAST_SESSION = False
# NUM_EPOCHS sudah 50
```

### Fase 1 — Import Modul Baru (Sel baru setelah 1s)
```python
from acos_id.cross_val import (
    build_with_ratio, build_kfold_splits,
    ExperimentGrid, tokenize_all_splits,
)
from acos_id.experiment_runner import (
    prepare_all_data, run_all_experiments, aggregate_cv_results,
)
```

### Fase 2 — Preview Semua Eksperimen (Dry Run)
```python
grid = ExperimentGrid()
grid.add_epochs([50, 75, 100])
grid.add_ratios([(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)])
grid.add_cv(n_splits=5)
grid.add_cv(n_splits=10)
grid.print_summary()  # tampilkan 54 run tanpa training
```

### Fase 3 — Persiapan Data (1x, ±30-60 menit)
```python
prepared = prepare_all_data(
    indo_root=indo_root,
    tokenizer=tokenizer,
    ratio_list=[(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)],
    cv_configs=[{"n_splits": 5}, {"n_splits": 10}],
    seed=42,
)
```

### Fase 4 — Training Semua Eksperimen (otomatis)
```python
def train_one_run(cfg: dict) -> dict:
    # Adapter: set NUM_EPOCHS, tokenized_base, session_dirs
    # dari cfg["epochs"], cfg["tokenized_dir"], cfg["result_dir"]
    # lalu panggil fungsi training Step 1 & Step 2
    return {"step1_f1": ..., "step2_f1": ...}

all_results = run_all_experiments(
    train_fn=train_one_run,
    indo_root=indo_root,
    epochs_list=[50, 75, 100],
    mode="all",   # "all", "ratio", atau "cv"
)
```

### Fase 5 — Agregasi Hasil CV
```python
cv5_agg = aggregate_cv_results(all_results, n_splits=5)
# → {"cv_5fold": {50: {"step1_f1_mean": ..., "step1_f1_std": ...}, ...}}
```

---

## 7. Arsitektur Folder yang Dihasilkan

```
ACOS-IndoBERT/
├── acos_id/
│   ├── cross_val.py            ← BARU
│   ├── experiment_runner.py    ← BARU
│   ├── build_acos.py           (existing)
│   ├── tokenize_data.py        (existing)
│   └── ...
│
├── data/Apps-ACOS/
│   ├── appsid_quad_{train,dev,test}.tsv   ← split original (79:11:10)
│   ├── split_801010/           ← 80:10:10
│   ├── split_701515/           ← 70:15:15
│   ├── split_602020/           ← 60:20:20
│   ├── cv_5fold/
│   │   ├── fold_1/ ... fold_5/
│   └── cv_10fold/
│       └── fold_1/ ... fold_10/
│
├── tokenized_data/
│   ├── appsid_{train,dev,test}_quad_bert.tsv  ← existing
│   ├── split_801010/           ← tokenized
│   ├── split_701515/
│   ├── split_602020/
│   ├── cv_5fold/fold_1/ ... fold_5/
│   └── cv_10fold/fold_1/ ... fold_10/
│
└── results/
    ├── appsid_24092026_0901/           ← sesi LAMA (3 epoch)
    └── experiments/                    ← BARU: semua 54 run
        ├── split_801010_ep50_<ts>/
        │   ├── checkpoints/
        │   └── run_result.json
        ├── ...
        ├── cv5fold_fold1_ep50_<ts>/
        ├── ...
        └── _experiment_progress.json   ← progress real-time
```

---

## 8. Template Perbandingan Hasil Eksperimen

| Config | Epoch | Split | Fold | Step1 F1% | Step2 F1% |
|--------|-------|-------|------|-----------|-----------|
| **Baseline** | 3 | 79:11:10 | - | **97.19** | ? |
| Split 80:10:10 | 50 | 80:10:10 | - | ? | ? |
| Split 70:15:15 | 50 | 70:15:15 | - | ? | ? |
| Split 60:20:20 | 50 | 60:20:20 | - | ? | ? |
| Split 80:10:10 | 75 | 80:10:10 | - | ? | ? |
| Split 80:10:10 | 100 | 80:10:10 | - | ? | ? |
| 5-Fold CV | 50 | CV | mean±std | ?±? | ?±? |
| 10-Fold CV | 50 | CV | mean±std | ?±? | ?±? |

---

## 9. Checklist Prioritas

### Hari ini (5 menit)
- [ ] Set `PATIENCE = 0` di Sel 3
- [ ] Set `RESUME_LAST_SESSION = False` di Sel 3
- [ ] Restart kernel, jalankan ulang Sel 1b → 1s → 3
- [ ] Konfirmasi output Sel 3: `num_epochs: 50`

### Besok / minggu ini
- [ ] Opsional: naikkan `STEP1_BATCH_SIZE = 96`, `STEP2_BATCH_SIZE = 64`
- [ ] Tambahkan sel import `cross_val` + `experiment_runner` ke notebook
- [ ] Jalankan `prepare_all_data()` untuk build semua TSV + tokenisasi
- [ ] Jalankan dry_run `ExperimentGrid` untuk konfirmasi 54 run
- [ ] Implement adapter `train_one_run()` yang membungkus training loop

### Minggu depan
- [ ] Jalankan `run_all_experiments()` untuk semua 54 run
- [ ] Agregasi hasil CV dengan `aggregate_cv_results()`
- [ ] Buat tabel perbandingan lengkap

---

## 10. Referensi Cepat

| Item | Path / Nilai |
|------|-------------|
| Notebook | `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb` |
| Sel konfigurasi | Sel 3 — `## 3. Master Pipeline Parameters` |
| Modul CV | `ACOS-IndoBERT/acos_id/cross_val.py` |
| Modul Runner | `ACOS-IndoBERT/acos_id/experiment_runner.py` |
| Dataset processed | `ACOS-IndoBERT/data/Apps-ACOS/processed/` |
| Total review_id | 76.077 klausa (dari stage2_*.jsonl) |
| VRAM terpakai | 5.308 MB / 191.690 MB (2.8%) |

---

*Disimpan oleh Antigravity IDE — 2026-09-24 21:32 WIB*
