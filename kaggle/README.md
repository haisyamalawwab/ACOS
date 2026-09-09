# Panduan Menjalankan ACOS Pipeline V4 di Kaggle (Dual-Head IndoBERT)

Dokumen ini berisi panduan untuk menjalankan notebook **`00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb`** pada platform **Kaggle Notebooks**.

---

## 1. Fitur Utama Versi V4-Kaggle

- **Sub-task Dual-Head Step 2:** Memisahkan klasifikasi Aspect Category (13 kelas, BCE loss) dan Sentiment (3 kelas, CE loss) dengan fusi representasi span kandidat pasangan $(a, o)$.
- **Arsitektur Zero Hardcoding Path:** Otomatis mendeteksi direktori kerja Kaggle (`/kaggle/working/`) dan auto-clone repositori bila modul belum tersedia.
- **Dukungan Akselerator Kaggle:** Optimal pada GPU NVIDIA Tesla T4 (2x) maupun GPU P100 dengan alokasi VRAM yang terpantau real-time.
- **Ekspor Artefak Otomatis:** Menghasilkan file ringkasan, riwayat per-epoch (`.csv`), checkpoint (`.bin`), matriks evaluasi final (`.json`), kurva pelatihan (`.png`), serta bundel `.zip` langsung di tab **Output** Kaggle.

---

## 2. Langkah Demi Langkah Menjalankan di Kaggle

### Langkah 1: Upload Notebook ke Kaggle
1. Buka [Kaggle](https://www.kaggle.com/) dan login ke akun Anda.
2. Klik tombol **"+ Create"** di pojok kiri atas, lalu pilih **"New Notebook"**.
3. Di editor notebook Kaggle, klik menu **File** $\rightarrow$ **Import Notebook** $\rightarrow$ tab **Upload**.
4. Unggah berkas:
   `kaggle/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb`

### Langkah 2: Konfigurasi Sesi (Wajib)
Di panel samping kanan (**Notebook Settings**):
1. **Accelerator**: Pilih **GPU T4 x2** (atau **GPU P100**).
2. **Language**: Python.
3. **Environment**: Always use latest environment.
4. **Internet**: Geser ke **ON** (Wajib aktif agar notebook dapat mengunduh pustaka Python dan bobot pretrained IndoBERT).

### Langkah 3: Eksekusi Pipeline (1-Click Run)
- Klik **Run All** (atau jalankan sel secara berurutan dari atas ke bawah).
- Notebook akan secara otomatis:
  1. Menginstal pustaka yang diperlukan (`transformers`, `pytorch-crf`, `scikit-learn`, dll.).
  2. Menyinkronkan modul `Extract-Classify-ACOS` dan paket `ACOS-IndoBERT` ke `/kaggle/working/`.
  3. Mempersiapkan taksonomi 13 kategori Apps-ACOS dan tokenizer IndoBERT.
  4. Melatih Step 1 (BERT + CRF Sequence Labeling) dan mengekstraksi kandidat $(a, o)$.
  5. Menghubungkan kandidat ke Step 2 dan melatih model `CategorySentiDualHead`.
  6. Melaporkan metrik evaluasi per epoch (Quadruple F1, Category micro-F1, dan Sentiment Accuracy).
  7. Menjalankan evaluasi akhir dan menyimpan semua metrik ke `master_metrics.json`.

---

## 3. Struktur Direktori di Kaggle

```
/kaggle/
├── working/                               <-- Direktori Output Utama (Writable)
│   ├── ACOS/
│   │   ├── Extract-Classify-ACOS/        <-- Modul Upstream
│   │   └── ACOS-IndoBERT/                <-- Modul Indonesia & Taksonomi
│   │       ├── results/
│   │       │   └── appsid_<timestamp>/   <-- Sesi Run Aktif
│   │       │       ├── checkpoints/      <-- Model Checkpoints (.bin)
│   │       │       ├── csv/              <-- Riwayat Training & Subtask (.csv)
│   │       │       ├── logs/             <-- master_metrics.json, progress
│   │       │       └── plots/            <-- Kurva Pelatihan PNG
│   └── acos_run_results.zip              <-- Bundel Arsip Siap Download
└── input/                                <-- Direktori Read-Only (Opsional Datasets)
```

---

## 4. Cara Mengunduh Hasil Training

Setelah eksekusi selesai:
1. Buka tab **Output** di panel kanan Kaggle.
2. Anda dapat langsung mengklik tombol download pada file `acos_run_results.zip` atau mengunduh masing-masing tabel `.csv`, grafik `.png`, dan file metrik `.json`.
