# Implementation Plan: Google Colab Jupyter Notebooks with Rich Visualizations, CSV Tables & Timestamped Result Directory

**Timestamp:** 26-08-2026 21:24 WIB  
**Repository:** `haisyamalawwab/ACOS` (`ACOS-ASLI`)  
**Objective:** Create a structured suite of serialized Jupyter Notebooks (`.ipynb`) for Google Colab and local execution, enriched with publication-grade visualizations (Matplotlib/Seaborn), structured CSV reports for tabular analysis, and an automated timestamped run directory architecture (`results/<domain>_<DDMMYYYY_HMS>/`).

---

## 1. Overview & Execution Workflow

The Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction pipeline consists of:
1. **Step 1 (Aspect-Opinion Co-Extraction):** Sequence tagging (BERT + Linear + CRF) for explicit aspect & opinion spans, with `[CLS]` multi-label classification for implicit aspect & opinion detection.
2. **Bridge (Candidate Pair Generation):** Cartesian product generation of aspect spans and opinion spans (including `[-1, -1]` for implicit entities) to form candidate pairs $(a, o)$.
3. **Step 2 (Category-Sentiment Classification):** Multi-label classification (BERT with span embeddings) predicting category and sentiment for each candidate pair.
4. **End-to-End Evaluation & Visualization:** Evaluation across 15 subtask permutations, 4 implicit/explicit subsets, generation of benchmark CSV tables, and interactive inference.

---

## 2. Automated Timestamped Result Directory Architecture (`DDMMYYYY_HMS`)

Every execution dynamically initializes a timestamped run directory to store all artifacts systematically without collision:

```
results/
└── <domain>_<DDMMYYYY_HMS>/   (Contoh: rest16_26082026_213045/)
    ├── plots/                 # Visualisasi grafik resolusi tinggi (PNG/PDF 300 DPI)
    │   ├── 01_eda_dataset_distribution.png
    │   ├── 02_explicit_vs_implicit_ratio.png
    │   ├── 03_step1_training_loss_f1_curve.png
    │   ├── 04_step2_training_loss_f1_curve.png
    │   ├── 05_benchmark_15_subtasks_f1.png
    │   ├── 06_implicit_subsets_breakdown_f1.png
    │   └── 07_category_sentiment_confusion_heatmap.png
    ├── csv/                   # Tabel CSV terstruktur untuk analisis metrik & data
    │   ├── eda_dataset_statistics.csv
    │   ├── step1_training_history.csv
    │   ├── step1_extracted_spans.csv
    │   ├── candidate_pairs_summary.csv
    │   ├── step2_training_history.csv
    │   ├── full_quadruple_predictions.csv
    │   ├── benchmark_15_subtasks_summary.csv
    │   └── benchmark_implicit_subsets_summary.csv
    ├── checkpoints/           # Bobot model terlatih & file konfigurasi
    │   ├── step1_bert_crf_best.bin
    │   ├── step2_category_senti_best.bin
    │   └── config.json
    └── logs/                  # Log eksekusi dan output evaluasi mentah
        ├── pipeline_execution.log
        ├── pred4pipeline.txt
        └── raw_evaluation_result.txt
```

### Python Directory Manager Function:
```python
import os
from datetime import datetime

def setup_timestamped_run_dir(base_dir="results", domain="rest16"):
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    run_dir = os.path.join(base_dir, f"{domain}_{timestamp}")
    dirs = {
        "root": run_dir,
        "plots": os.path.join(run_dir, "plots"),
        "csv": os.path.join(run_dir, "csv"),
        "checkpoints": os.path.join(run_dir, "checkpoints"),
        "logs": os.path.join(run_dir, "logs")
    }
    for path in dirs.values():
        os.makedirs(path, exist_ok=True)
    print(f"📁 Session run directory initialized at: {run_dir}")
    return dirs
```

---

## 3. Visualisasi Grafik & Tabel CSV yang Dihasilkan

### A. Exploratory Data Analysis (EDA)
- **Visualisasi (`plots/`):**
  - Perbandingan jumlah sampel dan quadruples pada Train, Dev, dan Test set.
  - Diagram Donat / Bar perbandingan rasio Explicit vs Implicit (Aspect & Opinion).
  - Distribusi frekuensi Aspect Category dan Sentiment Polarity (Positive, Neutral, Negative).
  - Distribusi panjang kalimat (token sequence length) dengan batas `max_seq_length=128`.
- **Tabel CSV (`csv/`):**
  - `eda_dataset_statistics.csv`: Ringkasan ukuran dataset, total quadruple, jumlah aspek/opini implisit dan eksplisit.
  - `category_sentiment_frequency.csv`: Matriks frekuensi kategori aspek berpasangan dengan polaritas sentimen.

### B. Training & Validation Curves
- **Visualisasi (`plots/`):**
  - Kurva Training Loss vs Validation Loss per epoch untuk Step 1 dan Step 2.
  - Grafik pergerakan Precision, Recall, dan Micro-F1 per epoch.
- **Tabel CSV (`csv/`):**
  - `step1_training_history.csv`: Catatan epoch, train_loss, val_loss, precision, recall, f1 untuk Step 1.
  - `step2_training_history.csv`: Catatan epoch, train_loss, val_loss, precision, recall, f1 untuk Step 2.

### C. Benchmark & Detailed Evaluation
- **Visualisasi (`plots/`):**
  - **15 Subtasks Benchmark Bar Chart:** Visualisasi metrik Precision, Recall, dan F1 untuk seluruh 15 kombinasi sub-task (Aspect, Opinion, Category, Sentiment, Aspect-Opinion, Category-Sentiment, Quadruple, dll.).
  - **4 Implicit Subsets Performance Chart:** Grafik perbandingan performa model pada:
    - *Subset 0:* Explicit Aspect + Explicit Opinion
    - *Subset 1:* Implicit Aspect + Explicit Opinion
    - *Subset 2:* Explicit Aspect + Implicit Opinion
    - *Subset 3:* Implicit Aspect + Implicit Opinion
    - *Subset 4:* Overall Total Quadruples
  - **Category-Sentiment Co-occurrence Heatmap:** Matriks korelasi/kebingungan antara prediksi dan gold category-sentiment.
- **Tabel CSV (`csv/`):**
  - `benchmark_15_subtasks_summary.csv`: Tabel metrik lengkap (TP, FP, FN, Precision, Recall, F1) seluruh 15 subtask.
  - `benchmark_implicit_subsets_summary.csv`: Tabel metrik lengkap performa 4 subset implisit/eksplisit.
  - `full_quadruple_predictions.csv`: Prediksi kalimat per kalimat lengkap: `Review_Text`, `Aspect_Span`, `Category`, `Opinion_Span`, `Sentiment_Polarity`, `Is_Implicit_Aspect`, `Is_Implicit_Opinion`, `Match_Status`.

---

## 4. Serial Numbered Google Colab Notebook Suite (`notebooks/`)

1. **`00_ACOS_Master_Pipeline_Colab.ipynb`** *(All-in-One Master Runner)*
   - Satu notebook lengkap untuk mengeksekusi pipeline end-to-end dengan 1-klik di Google Colab.
   - Menginisialisasi folder `results/<domain>_<DDMMYYYY_HMS>/`, melatih Step 1 & Step 2, mengekstrak kandidat pasangan, menghitung metrik benchmark, mengekspor semua grafik & CSV, serta menyediakan form demo inferensi interaktif.

2. **`01_ACOS_Setup_and_Data_Exploration.ipynb`** *(Setup & EDA)*
   - Pengecekan hardware GPU Colab (`torch.cuda`), instalasi dependensi, unduh & cache model `bert-base-uncased`.
   - Analisis mendalam dataset `Restaurant-ACOS` (`rest16`) dan `Laptop-ACOS` (`laptop`) disertai plot EDA dan ekspor `eda_dataset_statistics.csv`.

3. **`02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb`** *(Step 1: Co-Extraction)*
   - Arsitektur `BertForQuadABSA` (BERT + CRF Sequence Tagger + Implicit Heads).
   - Training loop & evaluasi validasi, plot kurva loss/F1, ekspor `step1_extracted_spans.csv` dan `pred4pipeline.txt`.

4. **`03_ACOS_Step1_to_Step2_Pair_Generation.ipynb`** *(Pipeline Bridge)*
   - Pemrosesan hasil Step 1 menjadi pasangan kandidat Cartesian $(a, o)$ termasuk entitas implisit `[-1, -1]`.
   - Analisis statistik pasangan kandidat dan ekspor `[domain]_test_pair_1st.tsv` serta `candidate_pairs_summary.csv`.

5. **`04_ACOS_Step2_Category_Sentiment_Classification.ipynb`** *(Step 2: Classification)*
   - Arsitektur `CategorySentiClassification` (BERT multi-label classification).
   - Training & evaluasi pada pasangan kandidat, plot kurva klasifikasi, dan penyimpanan checkpoint.

6. **`05_ACOS_Evaluation_and_Interactive_Inference.ipynb`** *(Evaluasi & Demo)*
   - Evaluasi komprehensif 15 subtask dan 4 subset implisit/eksplisit.
   - Pembuatan seluruh visualisasi benchmark dan ekspor tabel CSV akhir.
   - Widget Inferensi Interaktif: Masukkan ulasan teks kustom -> Proses model end-to-end -> Tampilkan kartu sentimen & tabel quadruples terstruktur.

---

## 5. Rencana Verifikasi & Validasi

1. **Validasi Skema Notebook:** Memastikan seluruh file `.ipynb` memiliki format JSON Notebook v4 yang valid.
2. **Validasi Sintaks Python:** Memeriksa seluruh sel kode Python di dalam notebook agar bebas dari syntax error.
3. **Pengujian Pembuatan Folder:** Memastikan helper `setup_timestamped_run_dir` membuat folder `DDMMYYYY_HMS` beserta subfolder `plots/`, `csv/`, `checkpoints/`, dan `logs/` dengan sempurna.
4. **Resolusi Grafik & Encoding CSV:** Memastikan visualisasi disimpan dengan `dpi=300` dan CSV disimpan dalam format `utf-8` dengan header yang rapi.
