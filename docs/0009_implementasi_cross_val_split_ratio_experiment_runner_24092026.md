# Implementasi: Cross-Validation, Split Ratio & Experiment Runner
> **Tanggal:** 2026-09-24 | **GPU:** AMD MI300X 191 GB VRAM
> **Lanjutan dari:** `docs/0008_rencana_eksperimen_full_training_crossval_mi300x_24092026.md`

---

## File Baru yang Dibuat

| File | Deskripsi |
|------|-----------|
| `acos_id/cross_val.py` | K-Fold CV + split ratio + ExperimentGrid |
| `acos_id/experiment_runner.py` | Auto-runner semua kombinasi eksperimen |

---

## Jawaban: Otomatis atau 1-per-1?

**Otomatis, berjalan 1-per-1 secara berurutan** via `ExperimentGrid` + `run_all_experiments()`.

Alasannya:
- GPU hanya 1 unit → tidak bisa paralel
- Setiap run butuh GPU penuh → harus serial
- Progress disimpan ke JSON setelah setiap run → bisa resume jika putus

---

## Total Kombinasi Eksperimen

```
Epochs × Ratio = 3 × 3 = 9 run split-ratio
Epochs × 5-Fold = 3 × 5 = 15 run
Epochs × 10-Fold = 3 × 10 = 30 run
─────────────────────────────────────
TOTAL = 54 run
```

| Tipe | Konfigurasi | Jumlah Run |
|------|-------------|-----------|
| **Split Ratio** | 50/75/100 epoch × 80:10:10 / 70:15:15 / 60:20:20 | 9 run |
| **5-Fold CV** | 50/75/100 epoch × fold 1-5 | 15 run |
| **10-Fold CV** | 50/75/100 epoch × fold 1-10 | 30 run |
| | **TOTAL** | **54 run** |

---

## Cara Penggunaan di Notebook

### Langkah 1: Import modul baru (Sel baru setelah Sel 1s)

```python
# Sel baru: Import modul eksperimen
from acos_id.cross_val import (
    build_with_ratio,
    build_kfold_splits,
    ExperimentGrid,
    tokenize_all_splits,
)
from acos_id.experiment_runner import (
    prepare_all_data,
    run_all_experiments,
    aggregate_cv_results,
)
print("Modul eksperimen siap.")
```

### Langkah 2: Lihat rencana eksperimen (Dry Run)

```python
# Tampilkan semua 54 run TANPA training
grid = ExperimentGrid()
grid.add_epochs([50, 75, 100])
grid.add_ratios([(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)])
grid.add_cv(n_splits=5)
grid.add_cv(n_splits=10)
grid.print_summary()
```

**Output:**
```
ExperimentGrid — 54 total run
   Split-ratio runs : 9
     split_801010_ep50       → epochs=50, train=80% dev=10% test=10%
     split_701515_ep50       → epochs=50, train=70% dev=15% test=15%
     split_602020_ep50       → epochs=50, train=60% dev=20% test=20%
     split_801010_ep75       → epochs=75, ...
     ...
   CV runs          : 45
     cv5fold_fold1_ep50      → epochs=50, 5-fold, fold 1
     ...
```

### Langkah 3: Siapkan semua data (1 kali saja)

```python
# Bangun TSV mentah + tokenisasi untuk semua eksperimen
# (jalankan 1x, setelah itu semua di-cache)
prepared = prepare_all_data(
    indo_root=indo_root,
    tokenizer=tokenizer,       # tokenizer dari sel 4c
    epochs_list=[50, 75, 100], # tidak diproses di sini, hanya dicatat
    ratio_list=[(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)],
    cv_configs=[{"n_splits": 5}, {"n_splits": 10}],
    seed=42,
    force_rebuild=False,       # True untuk rebuild semua
)
```

**Struktur yang dihasilkan:**
```
ACOS-IndoBERT/
├── data/Apps-ACOS/
│   ├── split_801010/          appsid_quad_{train,dev,test}.tsv
│   ├── split_701515/          appsid_quad_{train,dev,test}.tsv
│   ├── split_602020/          appsid_quad_{train,dev,test}.tsv
│   ├── cv_5fold/
│   │   ├── fold_1/ ... fold_5/  appsid_quad_{train,dev,test}.tsv
│   └── cv_10fold/
│       └── fold_1/ ... fold_10/ appsid_quad_{train,dev,test}.tsv
│
└── tokenized_data/
    ├── split_801010/          appsid_{train,dev,test}_quad_bert.tsv + pair.tsv
    ├── split_701515/
    ├── split_602020/
    ├── cv_5fold/
    │   └── fold_1/ ... fold_5/
    └── cv_10fold/
        └── fold_1/ ... fold_10/
```

### Langkah 4: Definisikan fungsi training (adapter)

```python
def train_one_run(cfg: dict) -> dict:
    """Adapter: jalankan 1 run dengan konfigurasi dari ExperimentGrid.

    cfg berisi:
      - cfg["epochs"]         → NUM_EPOCHS untuk run ini
      - cfg["tokenized_dir"]  → folder tokenized_data yang akan dipakai
      - cfg["result_dir"]     → folder untuk menyimpan checkpoint & hasil
      - cfg["run_id"]         → nama unik run ini
    """
    global NUM_EPOCHS, session_dirs, tokenized_base

    # Override konfigurasi untuk run ini
    NUM_EPOCHS = cfg["epochs"]
    tokenized_base = cfg["tokenized_dir"]

    # Buat session_dirs untuk run ini
    this_result_dir = cfg["result_dir"]
    session_dirs = session_dirs_from_root(this_result_dir)

    print(f"  Training: {cfg['run_id']} | {NUM_EPOCHS} epoch | {tokenized_base}")

    # Jalankan Step 1
    # ... (kode training Step 1 dari sel 5d-5e, dibungkus jadi fungsi) ...
    step1_f1 = run_step1_training()   # return best F1

    # Jalankan Step 2
    step2_f1 = run_step2_training()   # return best F1

    return {
        "step1_f1": step1_f1,
        "step2_f1": step2_f1,
    }
```

### Langkah 5: Jalankan semua eksperimen

```python
# Jalankan 54 run secara otomatis, 1-per-1
all_results = run_all_experiments(
    train_fn=train_one_run,
    indo_root=indo_root,
    epochs_list=[50, 75, 100],
    ratio_list=[(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)],
    cv_configs=[{"n_splits": 5}, {"n_splits": 10}],
    seed=42,
    mode="all",    # "all", "ratio", atau "cv"
    dry_run=False, # True untuk test tanpa training
)
```

### Langkah 6: Lihat hasil CV teragregasi

```python
# Agregasi mean±std per epoch untuk 5-fold
cv5_agg = aggregate_cv_results(all_results, n_splits=5)

import pandas as pd
df = pd.DataFrame(cv5_agg["cv_5fold"].values())
print(df[["epoch","step1_f1_mean","step1_f1_std","step2_f1_mean","step2_f1_std"]])
```

---

## Struktur Hasil Eksperimen

```
ACOS-IndoBERT/results/experiments/
├── split_801010_ep50_<timestamp>/
│   ├── checkpoints/step1_best/ step2_best/
│   ├── csv/
│   ├── logs/
│   └── run_result.json           <- metrik + konfigurasi run ini
├── split_701515_ep50_<timestamp>/
├── ...
├── cv5fold_fold1_ep50_<timestamp>/
├── ...
└── _experiment_progress.json     <- progress semua run (update real-time)
```

---

## Arsitektur Modul

```
acos_id/
├── cross_val.py            (BARU)
│   ├── build_with_ratio()      Build TSV dengan split ratio custom
│   ├── build_kfold_splits()    Generate semua fold K-Fold CV
│   ├── tokenize_all_splits()   Tokenisasi semua split/fold sekaligus
│   └── ExperimentGrid          Daftar + iterasi semua kombinasi
│
├── experiment_runner.py    (BARU)
│   ├── prepare_all_data()      Fase persiapan: build TSV + tokenisasi
│   ├── run_all_experiments()   Runner otomatis 1-per-1
│   └── aggregate_cv_results()  Hitung mean±std F1 per fold
│
├── build_acos.py           (existing, tidak diubah)
├── tokenize_data.py        (existing, tidak diubah)
└── taxonomy.py             (existing, tidak diubah)
```

---

## Desain Keputusan Penting

| Keputusan | Alasan |
|-----------|--------|
| **CV pada level review_id** | Semua klausa 1 ulasan = 1 split. Mencegah data leakage |
| **Dev dari dalam train** | Setiap fold: train_val → ambil 10% untuk dev, sisa untuk train |
| **Berjalan 1-per-1 (serial)** | GPU hanya 1, tidak bisa paralel. Progress disimpan setiap run |
| **Tidak pakai sklearn** | Supaya tidak tambah dependensi baru; KFold diimplementasi manual |
| **TSV mentah + tokenisasi terpisah** | Tokenisasi mahal; pisahkan dari training agar bisa di-cache |
| **run_result.json per run** | Monitoring real-time; bisa resume tanpa restart semua |

---

## Estimasi Waktu (AMD MI300X)

| Fase | Durasi Estimasi |
|------|----------------|
| Persiapan data (build TSV + tokenisasi semua) | ~30-60 menit (1x) |
| 9 run split-ratio × 50 epoch | ~27-45 jam |
| 9 run split-ratio × 75 epoch | ~40-67 jam |
| 9 run split-ratio × 100 epoch | ~54-90 jam |
| 15 run CV-5fold × 50 epoch | ~45-75 jam |
| 30 run CV-10fold × 50 epoch | ~90-150 jam |
| **54 run total (50 epoch saja)** | **~5-8 hari** |

> Naikkan `STEP1_BATCH_SIZE=96` dan `STEP2_BATCH_SIZE=64` untuk mempercepat 4x.

---

*Disimpan oleh Antigravity IDE — 2026-09-24*
