# Rencana Eksperimen Full Training + Cross-Validation — GPU AMD MI300X
> **Target Notebook:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`
> **Tanggal:** 2026-09-24
> **GPU:** AMD Instinct MI300X VF — 191.69 GB VRAM

---

## 🔍 Klarifikasi: Mengapa Training Berhenti di Epoch 3?

Bukan early stopping yang menyebabkan berhenti di epoch 3. Berdasarkan kode:

```
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5
```

Early stopping TIDAK BISA terpicu sebelum epoch ke-5. Training berhenti di epoch 3 karena:

| Penyebab | Penjelasan |
|----------|-----------|
| **Cache Hit aktif** | `STEP1_SKIP_TRAINING = True` — notebook mendeteksi model sudah ada dari sesi sebelumnya |
| **`RESUME_LAST_SESSION = True`** | Notebook melanjutkan sesi `appsid_24092026_0901` yang hanya punya 3 epoch tersimpan |

**Solusi langsung:** Set `RESUME_LAST_SESSION = False` + `PATIENCE = 0` → training full 50 epoch dari awal.

---

## 📊 Statistik Dataset Saat Ini

| Split | Baris (Klausa) | Rasio |
|-------|---------------|-------|
| **train** | 60.159 | 79.1% |
| **dev** | 8.027 | 10.6% |
| **test** | 7.891 | 10.4% |
| **TOTAL** | **76.077** | 100% |

Split berasal dari `stage2_{train,val,test}.jsonl` berdasarkan `review_id` — tidak ada bocor antar split.

---

## 🎯 Rencana Eksperimen Lengkap

### Dimensi Eksperimen

| Dimensi | Nilai |
|---------|-------|
| **Epochs** | 50, 75, 100 |
| **Train:Test Split** | 80:20, 70:30, 60:40 |
| **Cross Validation** | 5-Fold, 10-Fold |
| **Early Stopping** | OFF (PATIENCE=0) |

### Total Kombinasi Eksperimen

```
Epochs × Split = 3 × 3 = 9 eksperimen split biasa
Epochs × CV   = 3 × 2  = 6 konfigurasi CV × (5 atau 10 fold) = ~60 training run
```

---

## 🔧 Perubahan Konfigurasi Minimal (Langkah 1 — Paling Mudah)

**Ubah di Sel 3 notebook:**

```python
NUM_EPOCHS          = 50    # atau 75 atau 100
PATIENCE            = 0     # NONAKTIFKAN early stopping
RESUME_LAST_SESSION = False # folder baru bertimestamp
```

Ini saja sudah cukup untuk menjalankan **full 50 epoch tanpa early stopping** dengan split yang ada (80:20 approx).

---

## 📋 Implementasi Split Ratio Berbeda (60:40 / 70:30 / 80:20)

### Pendekatan

Dataset Apps-ACOS sudah punya split tetap dari `stage2_{train,val,test}.jsonl`.
Untuk eksperimen dengan rasio berbeda, perlu **rebuild split dari data mentah**.

### Modul yang Perlu Dimodifikasi: `acos_id/build_acos.py`

Tambahkan fungsi `build_with_ratio()`:

```python
# acos_id/build_acos.py — tambahan fungsi
import random

def build_with_ratio(data_root: str, out_dir: str, *,
                     train_ratio: float = 0.8,
                     dev_ratio: float = 0.1,
                     seed: int = 42,
                     report_path: str = None) -> dict:
    """Build dataset dengan rasio split custom.

    Args:
        train_ratio: Proporsi data training (misal 0.8 untuk 80%)
        dev_ratio  : Proporsi data dev/val (sisanya jadi test)
        seed       : Random seed untuk reproducibility
    """
    processed = os.path.join(data_root, "Apps-ACOS", "processed")
    if out_dir is None:
        out_dir = os.path.join(data_root, "Apps-ACOS")

    # Kumpulkan semua review_id dari seluruh split
    all_ids = set()
    for split, fname in SPLIT_FILES.items():
        path = os.path.join(processed, fname)
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_ids.add(json.loads(line)["review_id"])

    # Shuffle deterministik
    all_ids_list = sorted(all_ids)  # sort dulu agar deterministik
    random.seed(seed)
    random.shuffle(all_ids_list)

    n = len(all_ids_list)
    n_train = int(n * train_ratio)
    n_dev   = int(n * dev_ratio)

    train_ids = set(all_ids_list[:n_train])
    dev_ids   = set(all_ids_list[n_train:n_train + n_dev])
    test_ids  = set(all_ids_list[n_train + n_dev:])

    # Override id_to_split
    id_to_split = {}
    for rid in train_ids: id_to_split[rid] = "train"
    for rid in dev_ids:   id_to_split[rid] = "dev"
    for rid in test_ids:  id_to_split[rid] = "test"

    # Build menggunakan id_to_split baru
    groups = group_quintuples(processed)
    categories = set(CATEGORIES)
    lines = {"train": [], "dev": [], "test": []}
    # ... (logika sama dengan build_quad_lines tapi pakai id_to_split baru)
```

### Konvensi Penamaan File Output

```
data/Apps-ACOS/
├── appsid_quad_train.tsv          ← split original (79:11:10)
├── appsid_quad_dev.tsv
├── appsid_quad_test.tsv
├── split_8020/
│   ├── appsid_quad_train.tsv     ← 80% train, 10% dev, 10% test
│   ├── appsid_quad_dev.tsv
│   └── appsid_quad_test.tsv
├── split_7030/
│   └── ...                       ← 70% train, 15% dev, 15% test
└── split_6040/
    └── ...                       ← 60% train, 20% dev, 20% test
```

---

## 🔁 Implementasi K-Fold Cross Validation

### Pendekatan CV untuk NLP

Cross-validation pada dataset NLP seperti ACOS dilakukan pada level **review_id** (bukan baris), untuk memastikan semua klausa dari satu ulasan masuk ke fold yang sama (menghindari data leakage).

### Modul Baru: `acos_id/cross_val.py`

```python
"""K-Fold Cross Validation untuk dataset Apps-ACOS.

Strategi:
- CV dilakukan pada level review_id (bukan klausa)
- Setiap fold: (k-1) bagian train + 1 bagian test
- Dev set diambil 10% dari bagian train setiap fold
- Menghasilkan folder: tokenized_data/cv_5fold/fold_1/ ... fold_5/
"""
import json, os, random
from sklearn.model_selection import KFold


def build_kfold_splits(processed_dir: str, out_base: str, *,
                       n_splits: int = 5,
                       dev_ratio: float = 0.1,
                       seed: int = 42) -> dict:
    """Generate K-Fold splits dari semua review_id.

    Args:
        processed_dir : folder Apps-ACOS/processed/
        out_base      : folder output, mis. data/Apps-ACOS/cv_5fold/
        n_splits      : jumlah fold (5 atau 10)
        dev_ratio     : proporsi dev dari bagian train setiap fold
        seed          : random seed

    Returns:
        dict berisi info setiap fold
    """
    # Kumpulkan semua review_id
    all_ids = set()
    for fname in ("stage2_train.jsonl", "stage2_val.jsonl", "stage2_test.jsonl"):
        path = os.path.join(processed_dir, fname)
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_ids.add(json.loads(line)["review_id"])

    all_ids_arr = sorted(all_ids)
    random.seed(seed)
    random.shuffle(all_ids_arr)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    report = {"n_splits": n_splits, "total_reviews": len(all_ids_arr), "folds": {}}

    for fold_idx, (train_val_idx, test_idx) in enumerate(kf.split(all_ids_arr), 1):
        fold_dir = os.path.join(out_base, f"fold_{fold_idx}")
        os.makedirs(fold_dir, exist_ok=True)

        train_val_ids = [all_ids_arr[i] for i in train_val_idx]
        test_ids      = set(all_ids_arr[i] for i in test_idx)

        # Ambil dev dari train_val
        n_dev = int(len(train_val_ids) * dev_ratio)
        dev_ids   = set(train_val_ids[:n_dev])
        train_ids = set(train_val_ids[n_dev:])

        report["folds"][f"fold_{fold_idx}"] = {
            "train": len(train_ids),
            "dev"  : len(dev_ids),
            "test" : len(test_ids),
            "dir"  : fold_dir,
        }

        # Simpan mapping id → split untuk fold ini
        id_to_split = {}
        for rid in train_ids: id_to_split[rid] = "train"
        for rid in dev_ids:   id_to_split[rid] = "dev"
        for rid in test_ids:  id_to_split[rid] = "test"

        mapping_path = os.path.join(fold_dir, "id_to_split.json")
        with open(mapping_path, "w", encoding="utf-8") as fh:
            json.dump(id_to_split, fh, indent=2)

    return report
```

### Struktur Folder CV

```
ACOS-IndoBERT/
├── data/Apps-ACOS/
│   ├── cv_5fold/
│   │   ├── fold_1/
│   │   │   ├── appsid_quad_train.tsv
│   │   │   ├── appsid_quad_dev.tsv
│   │   │   └── appsid_quad_test.tsv
│   │   ├── fold_2/ ... fold_5/
│   └── cv_10fold/
│       ├── fold_1/ ... fold_10/
│
└── tokenized_data/
    ├── cv_5fold/
    │   ├── fold_1/
    │   │   ├── appsid_train_quad_bert.tsv
    │   │   ├── appsid_dev_quad_bert.tsv
    │   │   └── appsid_test_quad_bert.tsv
    │   └── fold_2/ ... fold_5/
    └── cv_10fold/
        └── fold_1/ ... fold_10/
```

---

## 🗺️ Roadmap Implementasi (Urutan Prioritas)

### Fase 1 — Paling Cepat (Hari ini) ✅

**Jalankan full 50 epoch dengan split existing:**

Ubah **3 baris** di Sel 3 notebook:
```python
NUM_EPOCHS          = 50
PATIENCE            = 0     # ← ubah dari 5
RESUME_LAST_SESSION = False # ← ubah dari True
```

### Fase 2 — Split Ratio (1-2 hari)

1. Tambahkan `build_with_ratio()` ke `acos_id/build_acos.py`
2. Buat sel baru di notebook untuk memilih rasio
3. Jalankan tokenisasi untuk setiap split
4. Training per split: 60:40, 70:30, 80:20 × epoch 50/75/100

### Fase 3 — Cross Validation (3-5 hari)

1. Buat `acos_id/cross_val.py`
2. Generate semua fold (5-fold dan 10-fold)
3. Tokenisasi semua fold
4. Loop training per fold
5. Agregasi metrik (mean ± std F1 per fold)

---

## ⏱️ Estimasi Waktu dengan AMD MI300X

Berdasarkan data sesi sebelumnya:
- **VRAM terpakai per epoch:** ~5.308 MB dari 191.690 MB (≈2.8%)
- **Batch size Step 1:** 24, **Step 2:** 16
- **Dataset train:** 60.159 klausa

> VRAM masih sangat lapang. Bisa naik batch size 4-8x untuk mempercepat training.

| Eksperimen | Estimasi Durasi |
|-----------|----------------|
| 50 epoch (full, 1 run) | ~3-5 jam |
| 75 epoch (full, 1 run) | ~4-7 jam |
| 100 epoch (full, 1 run) | ~6-10 jam |
| 5-Fold CV × 50 epoch | ~15-25 jam |
| 10-Fold CV × 50 epoch | ~30-50 jam |
| Semua kombinasi (3×3 split + 2 CV) | ~3-5 hari |

### Optimasi Batch Size untuk MI300X

Dengan VRAM 191 GB yang sangat besar, bisa tingkatkan batch size:

```python
# Konfigurasi agresif untuk MI300X (ganti di Sel 3):
STEP1_BATCH_SIZE = 96   # naik dari 24 → 4x lebih cepat per epoch
STEP2_BATCH_SIZE = 64   # naik dari 16 → 4x lebih cepat per epoch
```

---

## 📊 Template Hasil Perbandingan Eksperimen

| Config | Epochs | Split | Fold | Step1 F1% | Step2 F1% | Durasi |
|--------|--------|-------|------|-----------|-----------|--------|
| Baseline | 3 | 79:10:10 | - | 97.19 | ? | ? |
| MI300X-50e | 50 | 79:10:10 | - | ? | ? | ? |
| MI300X-75e | 75 | 79:10:10 | - | ? | ? | ? |
| MI300X-100e | 100 | 79:10:10 | - | ? | ? | ? |
| 80:20-50e | 50 | 80:20 | - | ? | ? | ? |
| 70:30-50e | 50 | 70:30 | - | ? | ? | ? |
| 60:40-50e | 50 | 60:40 | - | ? | ? | ? |
| 5Fold-50e | 50 | CV | 1-5 | ? ± ? | ? ± ? | ? |
| 10Fold-50e | 50 | CV | 1-10 | ? ± ? | ? ± ? | ? |

---

## 🚀 Langkah Segera (Action Items)

### Sekarang (5 menit)
- [ ] Ubah `PATIENCE = 0` di Sel 3
- [ ] Ubah `RESUME_LAST_SESSION = False` di Sel 3
- [ ] Restart kernel & jalankan ulang dari Sel 1b

### Besok
- [ ] Optionally: Naikkan `STEP1_BATCH_SIZE = 96` dan `STEP2_BATCH_SIZE = 64`
- [ ] Tambahkan `build_with_ratio()` ke `acos_id/build_acos.py`
- [ ] Test split 80:20 manual

### Minggu ini
- [ ] Buat `acos_id/cross_val.py`
- [ ] Jalankan pipeline lengkap 5-fold CV

---

## 📎 Referensi

| File | Path |
|------|------|
| Notebook | `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb` |
| Build ACOS | `ACOS-IndoBERT/acos_id/build_acos.py` |
| Tokenize Data | `ACOS-IndoBERT/acos_id/tokenize_data.py` |
| Dataset Train | `ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_train.tsv` (60.159 baris) |
| Dataset Dev | `ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_dev.tsv` (8.027 baris) |
| Dataset Test | `ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_test.tsv` (7.891 baris) |
| Processed | `ACOS-IndoBERT/data/Apps-ACOS/processed/` (stage2_*.jsonl) |
| Dok sebelumnya | `docs/0007_analisis_konfigurasi_gpu_mi300x_no_early_stopping_24092026.md` |

---

*Disimpan oleh Antigravity IDE — 2026-09-24*
