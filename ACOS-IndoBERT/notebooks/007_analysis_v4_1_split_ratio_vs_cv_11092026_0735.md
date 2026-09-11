# Analisis: Split Ratio Dataset vs Cross-Validation — V4_1 IndoBERT Pipeline

**File sumber:** `00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb`
**Tanggal analisis:** 2026-09-11
**Analis:** Antigravity (AI Coding Assistant)

---

## Kesimpulan Utama

> **Pipeline V4_1 menggunakan pre-split fixed files — bukan split ratio dinamis, dan bukan cross-validation.**

Dataset sudah dibagi secara statis menjadi tiga partisi file `.tsv` terpisah **sebelum** notebook ini dijalankan (di tahap preprocessing/tokenization).

---

## Bukti dari Notebook

### 1. Tidak Ada Konfigurasi Split di Cell Hyperparameter (Cell 13)

```python
# Hyperparameter Pelatihan — Cell 13
DOMAIN            = "appsid"
BACKBONE          = "indobert"
MAX_SEQ_LENGTH    = 128
STEP1_BATCH_SIZE  = 32
STEP2_BATCH_SIZE  = 32
STEP1_LR          = 2e-5
STEP2_LR          = 5e-5
NUM_EPOCHS        = 15
SEED              = 42
PATIENCE          = 5
MIN_EPOCHS_BEFORE_STOP = 5
```

**Tidak ditemukan:** `SPLIT_RATIO`, `train_size`, `test_size`, `KFold`, `StratifiedKFold`, `cross_val_score`, `train_test_split`.

---

### 2. Data Dibaca dari File TSV Statis

| Cell | Fungsi | File yang Dibaca |
|------|--------|-----------------|
| Cell 40 | Step 1 — Training | `{DOMAIN}_train_quad_bert.tsv` via `get_train_examples()` |
| Cell 38 | Step 1 — Evaluasi | `{DOMAIN}_test_quad_bert.tsv` via `get_dev_examples()` |
| Cell 65 | Step 2 — Training | `{DOMAIN}_train_pair.tsv` via `get_train_examples()` |
| Cell 63 | Step 2 — Evaluasi | `{DOMAIN}_test_pair.tsv` / `_test_pair_1st.tsv` |

```python
# Cell 40 — Step 1 Training
train_examples_1 = processor_step1.get_train_examples(tokenized_base, DOMAIN)
train_loader_1   = DataLoader(...)

# Cell 38 — Step 1 Evaluation
eval_examples_1  = processor_step1.get_dev_examples(tokenized_base, DOMAIN)
# -> membaca: tokenized_data/{DOMAIN}_test_quad_bert.tsv

# Cell 65 — Step 2 Training
train_examples_2 = processor_step2.get_train_examples(tokenized_base, DOMAIN)
train_loader_2   = DataLoader(...)
```

---

### 3. Struktur Partisi Dataset (Pre-split)

```
tokenized_data/
├── {DOMAIN}_train_quad_bert.tsv      <- training Step 1
├── {DOMAIN}_test_quad_bert.tsv       <- evaluasi Step 1
├── {DOMAIN}_train_pair.tsv           <- training Step 2
├── {DOMAIN}_test_pair.tsv            <- evaluasi Step 2 (isolated)
└── {DOMAIN}_test_pair_1st.tsv        <- evaluasi Step 2 (full pipeline)
```

Split ini terjadi **di hulu**, di luar scope notebook V4_1.

---

## Klarifikasi: Peran `_split_v4_1.py`

File `_split_v4_1.py` **bukan** untuk split dataset.
Fungsinya adalah **memecah satu master notebook** menjadi 4 sub-notebook serial:

| Output Notebook | Sel yang Tercakup | Isi |
|----------------|-------------------|-----|
| `V4_1_01_setup.ipynb` | Sel 0-31 | Setup, EDA, Gate Data |
| `V4_1_02_step1_train.ipynb` | Recovery + Sel 32-48 | Step 1 Training |
| `V4_1_03_step2_train.ipynb` | Recovery + Sel 54-68 | Step 2 Training |
| `V4_1_04_eval_inference.ipynb` | Recovery + Sel 69-79 | Evaluasi & Inference |

---

## Implikasi & Rekomendasi

### Jika Ingin Menambahkan Cross-Validation

Cross-validation **tidak dapat langsung ditambahkan** ke dalam notebook V4_1 karena:

1. Pipeline bergantung pada file `.tsv` pre-tokenized yang spesifik per fold
2. `processor.get_train_examples()` membaca path statis — perlu dimodifikasi untuk menerima path fold dinamis
3. Tokenized data perlu di-generate ulang sebanyak `K` kali

**Langkah yang diperlukan jika CV diinginkan:**
- [ ] Buat `K` versi folder `tokenized_data/` per fold
- [ ] Modifikasi `processor_step1` dan `processor_step2` agar menerima path dinamis
- [ ] Tambahkan loop fold di sel training (Cell 40 & Cell 65)
- [ ] Agregasi metrik antar fold di Cell 71

### Jika Ingin Mengubah Split Ratio

Split ratio dikendalikan di **preprocessing upstream** (bukan di notebook ini).
Cari dan modifikasi script yang menghasilkan `tokenized_data/` — kemungkinan di:
- `_build_v4_indobert.py`
- `_build_staged_v2.py`
- Atau modul `acos_id.selftest` / `acos_id.upstream`

---

## Ringkasan

| Aspek | Status di V4_1 |
|-------|---------------|
| Split ratio (train/test) | Tidak ada — sudah pre-split di file TSV |
| Cross-validation (KFold) | Tidak ada |
| Early stopping | Ada (`PATIENCE=5`, `MIN_EPOCHS_BEFORE_STOP=5`) |
| Stratified sampling | Tidak ada |
| Random seed untuk split | `SEED=42` (hanya untuk reproducibility model, bukan split) |
| Lokasi split sebenarnya | Di preprocessing upstream (`tokenized_data/`) |
