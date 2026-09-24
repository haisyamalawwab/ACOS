# Analisis Konfigurasi Notebook ACOS IndoBERT — Run GPU AMD MI300X
> **File Notebook:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`
> **Tanggal Analisis:** 2026-09-24
> **GPU:** AMD Instinct MI300X VF — 191.69 GB VRAM (ROCm HIP 7.14)

---

## 🖥️ Spesifikasi Hardware Terdeteksi

| Parameter | Nilai |
|-----------|-------|
| **Model GPU** | AMD Instinct MI300X VF |
| **Total VRAM** | 191.69 GB |
| **Akselerator** | AMD ROCm HIP |
| **ROCm HIP Build** | 7.14.60850 |
| **Kategori** | 🚀 Large GPU / Enterprise |
| **PyTorch Version** | 2.12.0+rocm7.14.0 |
| **`is_large_gpu`** | `True` (kriteria: VRAM >= 16 GB atau GPU nama MI300X/A100/H100/dll) |

---

## 📋 Kondisi Konfigurasi Saat Ini (Sel 3)

```python
NUM_EPOCHS = 50      # kode sumber sudah diubah ke 50
PATIENCE = 5         # ⚠️ early stopping masih AKTIF
MIN_EPOCHS_BEFORE_STOP = 5
RESUME_LAST_SESSION = True
```

> **⚠️ Inkonsistensi Kode vs Output Tersimpan**
> Output tersimpan di notebook menunjukkan **`num_epochs: 15`** — artinya notebook
> pernah dijalankan dengan `NUM_EPOCHS=15`, tetapi kode sumber sudah diubah ke `50`
> namun belum dieksekusi ulang.

---

## ❓ Pertanyaan & Jawaban

### 1. Jika NUM_EPOCHS berbeda → Perlu Folder Baru Bertimestamp?

**✅ BENAR — tapi tidak otomatis.**

Ada mekanisme deteksi perubahan epoch di **Sel 5b**:

```python
if _total != NUM_EPOCHS:
    print(f"⚠️  [RESUME] NUM_EPOCHS berubah ({_total}→{NUM_EPOCHS}). "
          f"Resume diabaikan — training dari awal.")
```

#### Perilaku berdasarkan kondisi:

| Kondisi | Perilaku |
|---------|---------|
| `RESUME_LAST_SESSION = True` dan epoch berubah | Resume **diabaikan**, training dari awal, **folder lama masih dipakai** |
| `RESUME_LAST_SESSION = False` | Folder timestamp **baru** dibuat via `setup_timestamped_run_dir()` |

#### Solusi untuk Folder Baru:
Set di **Sel 3**:
```python
RESUME_LAST_SESSION = False  # paksa buat folder timestamp baru
```
Folder baru akan dibuat di: `ACOS-IndoBERT/results/appsid_<timestamp>/`

---

### 2. GPU Besar → Perlu Training Full (No Early Stopping)?

**✅ BENAR — nonaktifkan early stopping untuk GPU MI300X.**

#### Kondisi saat ini (masih aktif):
```python
PATIENCE               = 5   # early stopping aktif setelah 5 epoch tanpa improvement
MIN_EPOCHS_BEFORE_STOP = 5
```

Training loop di **Sel 5e** akan `break` jika:
```python
if (PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and
    epochs_since_best_1 >= PATIENCE):
    # ⏹️ Early stopping terpicu → training berhenti
    break
```

#### Mengapa GPU Besar Harus No Early Stopping?

| Alasan | Penjelasan |
|--------|-----------|
| **VRAM 191 GB** | Tidak ada risiko OOM, batch besar aman |
| **Kecepatan per epoch tinggi** | Jauh lebih cepat dari T4/A100 kecil |
| **Tidak ada timeout** | Tidak seperti Colab gratis yang sering disconnect |
| **Konvergensi lebih optimal** | Model bisa eksplorasi kurva loss lebih jauh sebelum plateau |
| **Dataset besar** | 60.159 kalimat train → butuh lebih banyak epoch untuk konvergen |

#### Perbandingan Strategi:

```
Colab T4 (16 GB)    :  PATIENCE=5  → hemat kuota runtime, cegah timeout
AMD MI300X (191 GB) :  PATIENCE=0  → full 50 epoch, F1 maksimal tanpa batasan
```

---

## 🔧 Perubahan yang Direkomendasikan (Sel 3)

```python
# ============================================================
#  Konfigurasi V4 — IndoBERT fine-tuned + dataset Indonesia
#  [Dioptimalkan untuk GPU AMD MI300X 191 GB VRAM]
# ============================================================
DOMAIN   = "appsid"
BACKBONE = "indobert"

# Hyperparameter Pelatihan
MAX_SEQ_LENGTH     = 128
STEP1_BATCH_SIZE   = 24
STEP2_BATCH_SIZE   = 16
STEP1_LR           = 2e-5
STEP2_LR           = 5e-5
NUM_EPOCHS         = 50    # sudah diubah ke 50
SEED               = 42
DO_LOWER_CASE      = True

# ────────────────────────────────────────────────────────────
# PERUBAHAN UNTUK GPU AMD MI300X (Large GPU, No Early Stop):
# ────────────────────────────────────────────────────────────

# UBAH: Nonaktifkan early stopping
PATIENCE               = 0   # 0 = early stopping DINONAKTIFKAN
MIN_EPOCHS_BEFORE_STOP = 5   # tidak relevan bila PATIENCE=0

# UBAH: Paksa folder sesi baru bertimestamp
RESUME_LAST_SESSION = False  # buat folder appsid_<timestamp_baru>/
```

---

## 📁 Struktur Folder yang Dihasilkan

```
ACOS-IndoBERT/
└── results/
    ├── appsid_24092026_0901/          ← sesi LAMA (3 epoch, NUM_EPOCHS=15)
    │   ├── checkpoints/
    │   │   ├── step1_best/            ← F1=97.19% (epoch 3)
    │   │   └── step2_best/
    │   ├── csv/
    │   ├── logs/
    │   └── pipeline_state.pkl
    │
    └── appsid_<timestamp_baru>/       ← sesi BARU (50 epoch, no early stop)
        ├── checkpoints/
        │   ├── step1_best/
        │   └── step2_best/
        ├── csv/
        ├── logs/
        └── pipeline_state.pkl
```

---

## 📊 Hasil Sesi Sebelumnya (appsid_24092026_0901)

Step 1 berjalan **3 epoch** (sesi sebelumnya dengan `NUM_EPOCHS=15`):

| Epoch | Loss | TP | FP | FN | Precision% | Recall% | **Micro-F1%** |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2.1476 | 16.106 | 1.079 | 667 | 93.72 | 96.02 | 94.86 |
| 2 | 0.5908 | 16.299 | 707 | 474 | 95.84 | 97.17 | 96.50 |
| **3** | **0.3910** | **16.456** | **635** | **317** | **96.28** | **98.11** | **97.19** ✅ |

- **F1 terbaik:** 97.19% di epoch 3
- **VRAM terpakai:** ~5.308 MB dari 191.690 MB yang tersedia (≈2.8%)
- Training berhenti di epoch 3 karena **cache hit** aktif (bukan early stopping)

> **Catatan:** Dengan `PATIENCE=5` dan `MIN_EPOCHS_BEFORE_STOP=5`, early stopping sebenarnya belum bisa terpicu di epoch 3. Sesi terhenti karena notebook dijalankan kembali dalam kondisi cache hit (`STEP1_SKIP_TRAINING = True`).

---

## ✅ Checklist Sebelum Run Baru

- [ ] Set `NUM_EPOCHS = 50` *(sudah di kode)*
- [ ] Set `PATIENCE = 0` *(ubah dari 5)*
- [ ] Set `RESUME_LAST_SESSION = False` *(ubah dari True)*
- [ ] Verifikasi backbone IndoBERT: `backbones/indobert_base_p1/` (3/3 berkas: `config.json`, `pytorch_model.bin`, `vocab.txt`)
- [ ] Pastikan data sudah ter-tokenisasi: `tokenized_data/appsid_train_quad_bert.tsv`, `appsid_test_quad_bert.tsv`, dll.
- [ ] Jalankan ulang **Sel 1b** dan **Sel 1s** setelah kernel restart
- [ ] Jalankan **Sel 3** → konfirmasi output menampilkan `num_epochs: 50`

---

## 📎 Referensi Sel Notebook

| Sel | Deskripsi | Relevansi |
|-----|-----------|-----------|
| **Sel 3** | `## 3. Master Pipeline Parameters` | Tempat ubah `NUM_EPOCHS`, `PATIENCE`, `RESUME_LAST_SESSION` |
| **Sel 5b** | `### 5b. Deteksi cache Step 1` | Logika deteksi perubahan epoch & cache hit |
| **Sel 5e** | `### 5e. Loop Training Step 1` | Loop training + logika early stopping |
| **Sel 8e** | `### 8e. Loop Training Step 2` | Sama seperti 5e tapi untuk Step 2 (Category-Sentiment) |

---

*Disimpan otomatis oleh Antigravity IDE — 2026-09-24*
