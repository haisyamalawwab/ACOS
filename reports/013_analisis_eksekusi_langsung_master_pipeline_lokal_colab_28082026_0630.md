# Analisis Eksekusi Langsung Master Pipeline ACOS (Lokal & Google Colab)

**Tanggal:** 2026-08-28 06:30 WIB  
**Objek Analisis:** `notebooks/00_ACOS_Master_Pipeline_Colab_ASLI.ipynb`  
**Karakteristik Utama:** Eksekusi langsung (*in-memory*) tanpa ketergantungan script CLI eksternal `.py`, kompatibilitas dual-environment (Lokal & Google Colab), dan kepastian penyimpanan otomatis ke Google Drive pada folder `/content/drive/MyDrive/ACOS`.

---

## 1. Ringkasan Eksekutif

Notebook `00_ACOS_Master_Pipeline_Colab_ASLI.ipynb` berfungsi sebagai orkestrator terpadu (1-Click Pipeline) untuk menjalankan keseluruhan benchmark **Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction** (mendukung aspek/opini eksplisit dan implisit). 

Seluruh alur kerja—mulai dari data preparation, exploratory data analysis (EDA), pelatihan & evaluasi Step 1 (BERT-CRF), jembatan pembentukan pasangan kandidat kartesian $(a, o)$, pelatihan & evaluasi Step 2 (Multi-label Classification), penangkapan metrik 15 sub-tugas, hingga demo inferensi dua-tahap interaktif—dijalankan secara langsung (*direct execution*) di dalam sel notebook tanpa memerlukan eksekusi CLI script (`run.sh`, `run_step1.py`, atau `run_step2.py`).

---

## 2. Matriks Kompatibilitas Lingkungan (Lokal vs. Google Colab)

| Dimensi Operasional | Google Colab | Komputer Lokal (Windows / Linux) |
| :--- | :--- | :--- |
| **Mount Google Drive** | `drive.mount('/content/drive')` dimuat otomatis. | Ditangkap secara aman dalam blok `try...except`, beralih ke *local mode*. |
| **Direktori Proyek Dasar** | `/content/drive/MyDrive/ACOS` | Path repositori lokal (`d:/laragon/www/ACOS-ASLI` atau `./`). |
| **Direktori Output Hasil** | `/content/drive/MyDrive/ACOS/Output/results/...` | `./results/...` di folder kerja lokal. |
| **Cache Model Pretrained** | `/content/drive/MyDrive/ACOS/Output/bert_base_uncased` | `./bert_base_uncased` di direktori lokal. |
| **Akselerasi Komputasi** | GPU Google Colab (`cuda` - T4 / A100 / V100). | `cuda` jika ada GPU NVIDIA lokal, atau `cpu` secara otomatis. |
| **Pustaka & Dependensi** | `pip install -q pytorch-crf transformers ...` | Memanfaatkan *environment* lokal (Conda / venv) atau inline pip. |
| **Modul & Utilitas Pendukung** | Diambil dari repo Drive / clone GitHub fallback. | Diambil langsung dari `Extract-Classify-ACOS` & `notebooks`. |

---

## 3. Arsitektur Folder Penyimpanan Google Drive (`/content/drive/MyDrive/ACOS`)

Saat dijalankan di Google Colab, semua artefak hasil eksekusi dikelompokkan secara terisolasi ke dalam folder bertanda waktu (*timestamped session folder*) `results/<domain>_<DDMMYYYY_HMS>/`:

```
/content/drive/MyDrive/ACOS/
├── bert_base_uncased/                  # Cache bobot HuggingFace (config.json, pytorch_model.bin, vocab.txt)
├── Extract-Classify-ACOS/              # Dataset TSV, tokenized data, & modul inti
└── Output/
    └── results/
        └── rest16_DDMMYYYY_HHMMSS/     # Folder Sesi Terisolasi
            ├── checkpoints/
            │   ├── step1_best/         # Bobot terbaik model Step 1 (BERT-CRF)
            │   │   ├── pytorch_model.bin
            │   │   ├── config.json
            │   │   └── vocab.txt
            │   └── step2_best/         # Bobot terbaik model Step 2 (Cat-Senti)
            │       ├── pytorch_model.bin
            │       ├── config.json
            │       └── vocab.txt
            ├── plots/                  # Visualisasi publikasi 300 DPI (PNG)
            │   ├── 01_dataset_statistics_summary.png
            │   ├── 02_aspect_category_sentiment_distributions.png
            │   ├── 03_step1_training_loss_f1_curve.png
            │   ├── 04_candidate_pairs_distribution.png
            │   ├── 04_step2_training_loss_f1_curve.png
            │   └── 05_benchmark_subtasks_f1.png
            ├── csv/                    # Seluruh data tabular & metrik (CSV)
            │   ├── eda_dataset_statistics.csv
            │   ├── master_00_konfigurasi.csv
            │   ├── step1_training_history.csv
            │   ├── candidate_pairs_summary.csv
            │   ├── step2_training_history.csv
            │   ├── master_07_metrik_quadruple_final.csv
            │   ├── master_08_metrik_subtask.csv
            │   └── master_11_daftar_artefak.csv
            ├── md/                     # Laporan terstruktur per tahap (Markdown)
            │   ├── 00_master_pipeline.md
            │   └── master_*.md
            └── logs/                   # Log teks & JSON ringkasan
                ├── pred4pipeline.txt   # Prediksi Step 1 untuk jembatan Step 2
                └── master_metrics.json # Nilai evaluasi lengkap 15 sub-tugas
```

---

## 4. Rincian Metode & Logika per Cell (10 Tahap Terpadu)

### Cell 1–2: Setup Lingkungan & Deteksi Komputasi
- **Google Drive Mount:** Menggunakan `try...except` agar aman dijalankan baik di Colab maupun komputer lokal.
- **Deteksi Perangkat:** `torch.device("cuda" if torch.cuda.is_available() else "cpu")`.
- **Resolusi Path Dinamis:** Memeriksa keberadaan folder `/content/drive/MyDrive/ACOS`, folder lokal, atau melakukan auto-clone dari GitHub jika folder `Extract-Classify-ACOS` belum ditemukan.

### Cell 3: Konfigurasi & Inisialisasi Sesi
- **Hyperparameter Terpusat:** `DOMAIN = "rest16"`, `MAX_SEQ_LENGTH = 128`, `STEP1_BATCH_SIZE = 24`, `STEP2_BATCH_SIZE = 16`, `NUM_EPOCHS = 15`, `STEP1_LR = 2e-5`, `STEP2_LR = 5e-5`, `SEED = 42`.
- **Reproducibility:** Pengaturan seed untuk `random`, `numpy`, `torch`, dan `cuda.manual_seed_all`.
- **BERT Caching:** Mengunduh `bert-base-uncased` dari HuggingFace Hub secara offline-safe untuk mencegah kegagalan unduh legacy S3 AWS.

### Cell 4: Exploratory Data Analysis (EDA)
- Membaca dataset TSV per split (`train`, `dev`, `test`).
- Menghitung statistik aspek/opini eksplisit vs. implisit, kategori unik, dan polaritas sentimen (Negatif, Netral, Positif).
- Mengekspor tabel statistik CSV dan diagram batang/heatmap beresolusi tinggi (300 DPI).

### Cell 5: Step 1 (Aspect & Opinion Co-Extraction)
- **Arsitektur Model:** `BertForQuadABSA` (BERT Encoder + Linear-Chain CRF Sequence Tagger + 2 Binary Implicit Classifier).
- **Proses Training:** Loop PyTorch murni dengan `BertAdam` optimizer dan evaluasi `pred_eval()` per epoch.
- **Checkpointing:** Checkpoint model terbaik disimpan ke subfolder `checkpoints/step1_best/` ketika micro-F1 meningkat.
- **Prediksi Jembatan:** Menuliskan berkas `pred4pipeline.txt` ke dalam direktori `logs/`.

### Cell 6: Candidate Pair Generation Bridge
- Membaca berkas `pred4pipeline.txt` dari Step 1.
- Membangun kombinasi perkalian kartesian $(a, o)$ dengan penanganan khusus entitas implisit `[-1, -1]`.
- Menyimpan berkas pasangan evaluasi ke `tokenized_data/<domain>_test_pair_1st.tsv` dan membuat ringkasan CSV `candidate_pairs_summary.csv`.

### Cell 7: Step 2 (Category & Sentiment Classification)
- **Arsitektur Model:** `CategorySentiClassification` (Multi-label Sigmoid Classifier berbasis BERT).
- **Proses Training:** Melatih klasifikasi kategori-sentimen pada pasangan kandidat $(a, o)$ dari Step 1.
- **Checkpointing:** Checkpoint model terbaik disimpan ke subfolder `checkpoints/step2_best/`.
- **Visualisasi:** Mengekspor kurva loss & F1 ke `plots/04_step2_training_loss_f1_curve.png`.

### Cell 8: Benchmark 15 Sub-Tasks & Metrik Akhir
- Memuat checkpoint terbaik `step2_best` untuk evaluasi final.
- Menggunakan `SubtaskMetricCapture` untuk menangkap seluruh 15 kombinasi sub-tugas ACOS (A, C, O, S, AC, AO, AS, CO, CS, OS, ACO, ACS, AOS, COS, ACOS).
- Mengekspor metrik ke format terstruktur `master_metrics.json` dan diagram batang `05_benchmark_subtasks_f1.png`.

### Cell 9: Inferensi Dua-Tahap pada Teks Bebas (Live Demo)
- Menyediakan fungsi `analyze_review_quadruples(review_text)`.
- Menggabungkan model Step 1 (ekstraksi span aspek & opini) dan Step 2 (klasifikasi kategori & sentimen) untuk memproses teks ulasan baru tanpa label (*raw text*).
- Menghasilkan DataFrame terurut berdasarkan skor logit keyakinan model.

### Cell 10: Ringkasan Artefak Sesi & Finalisasi Laporan
- Menginventarisasi seluruh berkas output yang dihasilkan (Checkpoint, CSV, Plot, Markdown, Log).
- Menyimpan berkas laporan utama `00_master_pipeline.md` di folder `md/`.

---

## 5. Kesimpulan & Rekomendasi Penggunaan

1. **Mandiri & Terintegrasi (*Self-Contained*):** Notebook `00_ACOS_Master_Pipeline_Colab_ASLI.ipynb` sepenuhnya dapat dijalankan sel per sel tanpa memerlukan pemanggilan script `.py` via terminal/bash.
2. **Fleksibilitas Lingkungan:** Pengguna dapat beralih antara Google Colab (untuk komputasi GPU berkecepatan tinggi) dan komputer lokal (untuk penyesuaian kode dan pengujian cepat) tanpa mengubah baris kode path.
3. **Integritas Penyimpanan:** Output tersimpan konsisten dan aman di folder `/content/drive/MyDrive/ACOS` saat di Colab, sehingga tidak akan hilang saat runtime Colab berakhir (*disconnect*).
