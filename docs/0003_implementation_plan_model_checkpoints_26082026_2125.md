# Implementation Plan: Google Colab Notebooks with Model Checkpoint Persistence, Rich Visualizations & Timestamped Storage

**Timestamp:** 26-08-2026 21:25 WIB  
**Repository:** `haisyamalawwab/ACOS` (`ACOS-ASLI`)  
**Objective:** Create a structured suite of serialized Jupyter Notebooks (`.ipynb`) for Google Colab and local execution, with guaranteed persistence of model checkpoints (weights, configuration, vocabulary, state dicts) for both training and testing runs, accompanied by publication-grade visualizations, structured CSV reports, and automated timestamped directory organization (`results/<domain>_<DDMMYYYY_HMS>/`).

---

## 1. Overview & Execution Architecture

The Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction pipeline consists of:
1. **Step 1 (Aspect-Opinion Co-Extraction):** Sequence tagging (BERT + Linear + CRF) for explicit aspect & opinion spans, with `[CLS]` multi-label classification for implicit aspect & opinion detection.
2. **Bridge (Candidate Pair Generation):** Cartesian product generation of aspect spans and opinion spans (including `[-1, -1]` for implicit entities) to form candidate pairs $(a, o)$.
3. **Step 2 (Category-Sentiment Classification):** Multi-label classification (BERT with span embeddings) predicting category and sentiment for each candidate pair.
4. **End-to-End Evaluation & Visualization:** Evaluation across 15 subtask permutations, 4 implicit/explicit subsets, generation of benchmark CSV tables, and interactive inference.

---

## 2. Model Persistence Strategy (Training & Testing)

Setiap proses training dan testing dipastikan menyimpan seluruh artefak model dan hasil evaluasi secara otomatis:

### A. Step 1 (Aspect-Opinion Extraction Model)
- **Saat Training (`do_train`):**
  - Model mengevaluasi dev set pada setiap epoch.
  - Saat mencapai performa Micro-F1 tertinggi, model otomatis menyimpan:
    - `pytorch_model.bin` (PyTorch state dict)
    - `config.json` (Konfigurasi arsitektur BERT)
    - `vocab.txt` (Kamus vocabulary tokenizer)
    - `checkpoint_metadata.json` (Informasi epoch, tanggal, best F1 score)
    ke dalam subfolder `checkpoints/step1_best/`.
  - Riwayat metrik per-epoch disimpan ke `csv/step1_training_history.csv`.
- **Saat Testing / Evaluasi (`do_eval`):**
  - Model dapat dimuat langsung dari `checkpoints/step1_best/` tanpa perlu melatih ulang.
  - Menghasilkan dan menyimpan `logs/pred4pipeline.txt`, `logs/valid.txt`, `logs/Test_results.txt`, dan `csv/step1_extracted_spans.csv`.

### B. Step 2 (Category-Sentiment Classification Model)
- **Saat Training (`do_train`):**
  - Mengevaluasi akurasi dan Micro-F1 klasifikasi gabungan kategori-sentimen.
  - Menyimpan model terbaik ke dalam subfolder `checkpoints/step2_best/` (`pytorch_model.bin`, `config.json`, `vocab.txt`).
  - Riwayat metrik per-epoch disimpan ke `csv/step2_training_history.csv`.
- **Saat Testing / Evaluasi (`do_eval`):**
  - Model dimuat dari `checkpoints/step2_best/`.
  - Mengevaluasi pasangan kandidat dan menghitung metrik quadruple lengkap.
  - Menyimpan `logs/result.txt`, `logs/Test_results.txt`, `csv/full_quadruple_predictions.csv`, `csv/benchmark_15_subtasks_summary.csv`, dan `csv/benchmark_implicit_subsets_summary.csv`.

---

## 3. Automated Timestamped Result Directory Architecture (`DDMMYYYY_HMS`)

Setiap eksekusi akan membuat folder sesi unik berformat timestamp:

```
results/
└── <domain>_<DDMMYYYY_HMS>/   (Contoh: rest16_26082026_213045/)
    ├── checkpoints/           # Bobot model terlatih & konfigurasi
    │   ├── step1_best/        # Model Step 1 (Aspect-Opinion Co-Extraction BERT-CRF)
    │   │   ├── pytorch_model.bin
    │   │   ├── config.json
    │   │   ├── vocab.txt
    │   │   └── checkpoint_metadata.json
    │   └── step2_best/        # Model Step 2 (Category-Sentiment Classification)
    │       ├── pytorch_model.bin
    │       ├── config.json
    │       ├── vocab.txt
    │       └── checkpoint_metadata.json
    ├── plots/                 # Visualisasi grafik resolusi tinggi (PNG/PDF 300 DPI)
    │   ├── 01_eda_dataset_distribution.png
    │   ├── 02_explicit_vs_implicit_ratio.png
    │   ├── 03_step1_training_loss_f1_curve.png
    │   ├── 04_step2_training_loss_f1_curve.png
    │   ├── 05_benchmark_15_subtasks_f1.png
    │   ├── 06_implicit_subsets_breakdown_f1.png
    │   └── 07_category_sentiment_confusion_heatmap.png
    ├── csv/                   # Tabel CSV data dan metrik evaluasi
    │   ├── eda_dataset_statistics.csv
    │   ├── step1_training_history.csv
    │   ├── step1_extracted_spans.csv
    │   ├── candidate_pairs_summary.csv
    │   ├── step2_training_history.csv
    │   ├── full_quadruple_predictions.csv
    │   ├── benchmark_15_subtasks_summary.csv
    │   └── benchmark_implicit_subsets_summary.csv
    └── logs/                  # Log eksekusi dan output evaluasi mentah
        ├── pipeline_execution.log
        ├── pred4pipeline.txt
        ├── valid.txt
        ├── result.txt
        └── Test_results.txt
```

---

## 4. Serial Numbered Google Colab Notebook Suite (`notebooks/`)

1. **`00_ACOS_Master_Pipeline_Colab.ipynb`** *(All-in-One Master Runner)*
   - Menjalankan seluruh proses end-to-end dengan penyimpanan model, grafik, CSV, dan demo inferensi interaktif.
2. **`01_ACOS_Setup_and_Data_Exploration.ipynb`** *(Setup Lingkungan, Unduh Pretrained BERT, EDA & Plot)*
   - Download dan cache model pretrained `bert-base-uncased`, visualisasi distribusi dataset, dan ekspor CSV statistik.
3. **`02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb`** *(Training & Testing Step 1)*
   - Training & testing BERT-CRF, penyimpanan checkpoint `checkpoints/step1_best/`, plot kurva loss/F1, dan ekspor hasil ekstraksi span.
4. **`03_ACOS_Step1_to_Step2_Pair_Generation.ipynb`** *(Candidate Pair Generation)*
   - Membentuk pasangan kandidat $(a, o)$ termasuk entitas implisit `[-1, -1]`, analisis statistik recall, dan ekspor file TSV input Step 2.
5. **`04_ACOS_Step2_Category_Sentiment_Classification.ipynb`** *(Training & Testing Step 2)*
   - Training & testing multi-label BERT classifier, penyimpanan checkpoint `checkpoints/step2_best/`, dan plot metrik klasifikasi.
6. **`05_ACOS_Evaluation_and_Interactive_Inference.ipynb`** *(Evaluasi & Demo Inferensi)*
   - Memuat checkpoint tersimpan `step1_best` dan `step2_best` secara mandiri untuk evaluasi penuh 15 subtask & 4 subset, plotting benchmark, serta demo inferensi teks ulasan kustom.

---

## 5. Rencana Verifikasi & Validasi

1. **Verifikasi Integritas Checkpoint Model:** Memastikan model yang disimpan di `checkpoints/step1_best/` dan `checkpoints/step2_best/` dapat dimuat kembali (`loaded`) dengan sukses untuk inferensi/evaluasi.
2. **Validasi Skema Notebook:** Memastikan seluruh file `.ipynb` memiliki format JSON Notebook v4 yang valid.
3. **Penyimpanan Multi-Platform:** Memastikan path direktori berfungsi baik di Google Colab (Linux) maupun Windows lokal.
