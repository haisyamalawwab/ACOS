# Analisis Mendalam & Kritis: Struktur Proyek ACOS-ASLI

Tanggal analisis: 2026-08-27
Metode: pembacaan kode statis (README, colab_utils, seluruh source di `Extract-Classify-ACOS/`, notebook, docs, reports). Tidak ada eksekusi pipeline (environment Python 3.14 tanpa `torch`).
Status: laporan analisis, tanpa perubahan file.

## 1. Identitas Repo

- Fork/copy dari repo resmi paper ACL 2021 *Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions* (Cai, Xia, Yu).
- Isi: dua dataset ACOS + implementasi **satu** baseline saja (`Extract-Classify-ACOS`).
- Tiga baseline lain di `README.md` (Double-Propagation-ACOS, JET-ACOS, TAS-BERT-ACOS) **tidak ada** di repo ini.

## 2. Struktur Direktori

```
ACOS-ASLI/
├── .agents/skills/              # Agent guidelines (coding + karpathy)
├── Extract-Classify-ACOS/       # KODE UTAMA (baseline Extract-Classify)
│   ├── run.sh                   # Orchestrator 3 langkah
│   ├── run_step1.py             # Step 1: co-extraction aspect+opinion (BERT+CRF)
│   ├── run_step2.py             # Step 2: klasifikasi category-sentiment
│   ├── tokenized_data/get_1st_pairs.py  # Jembatan step1→step2
│   ├── modeling.py (1646 baris) # Port pytorch_pretrained_bert + 2 head task
│   ├── run_classifier_dataset_utils.py # Processor & feature conversion
│   ├── eval_metrics.py          # Metrik + penulis pred4pipeline.txt
│   ├── dataset_utils.py         # Pembaca gold pair
│   ├── manager.py               # Pemilih GPU (sudah diperbaiki)
│   ├── file_utils.py            # **Duplikat** bert_utils/file_utils.py
│   ├── bert_utils/              # tokenization, optimization, file_utils
│   └── tokenized_data/*.tsv     # Data siap-pakai (sudah ter-wordpiece)
├── data/                        # Dataset mentah (TIDAK dipakai kode manapun)
│   ├── Restaurant-ACOS/         # 1530/171/583 baris
│   └── Laptop-ACOS/             # 2934/326/816 baris
├── notebooks/                   # 6 notebook Colab (00-05)
├── colab_utils.py               # Helper: EDA, plotting, checkpoint, inferensi
├── docs/                        # 3 implementation plan markdown
├── reports/                     # Laporan analisis (001, 002, 003)
├── img/                         # Gambar untuk README
├── backups/                     # Backup notebooks & colab_utils.py
├── .gitignore                   # Minimal
└── README.md
```

## 3. Alur Pipeline (2-Tahap, Bukan End-to-End)

| Tahap | File Utama | Model | I/O |
|-------|------------|-------|-----|
| Step 1 | `run_step1.py` + `BertForQuadABSA` | BERT + CRF (6 tag: `[CLS] O I-A B-A I-O B-O`) + 2 classifier biner implicit | Input: `*_quad_bert.tsv` → Output: `pred4pipeline.txt` |
| Jembatan | `get_1st_pairs.py` | Cross-product aspect × opinion (termasuk `-1,-1`) | Input: `pred4pipeline.txt` → Output: `*_test_pair_1st.tsv` |
| Step 2 | `run_step2.py` + `CategorySentiClassification` | BERT + mean-pool span → concat (1536-d) → Linear(39/363 kelas) | Train: gold pair (`*_train_pair.tsv`); Test: pred pair (`*_test_pair_1st.tsv`) |

- Loss Step 1: CRF loss + 2×CE (implicit aspect/opinion).
- Loss Step 2: `BCEWithLogitsLoss` multi-label (`CATEGORY#SENTIMENT`).
- Format label: `0/1/2` = negative/neutral/positive; `-1,-1` = implicit.
- Error propagation Step 1 → Step 2 **by design** (pipeline, bukan joint).

## 4. Kondisi Working Tree

Lima file termodifikasi untuk porting agar jalan di mesin lain:

1. `modeling.py` + `bert_utils/tokenization.py` — URL S3 mati → HuggingFace Hub; 6-7 varian BERT dihapus (tidak berdampak karena `run.sh` pakai path lokal).
2. `dataset_utils.py` — hardcode path `/mnt/nfs...` dihapus, import lokal `bert_utils.tokenization`.
3. `manager.py` — blocking loop GPU dihapus; fallback CPU; `_sort_by_custom` unused dihapus.
4. `tokenized_data/get_1st_pairs.py` — output path hardcode → fallback 3 lokasi; tambah mode 3-argumen; `encoding='utf-8'`.

Masalah upstream (bug asli, bukan dari porting):

| Prioritas | File:Line | Masalah |
|-----------|-----------|---------|
| P2 | `run_step1.py:420-428` | `ae_loss` undefined di jalur `gradient_accumulation_steps > 1` / `--fp16` |
| P2 | `run_classifier_dataset_utils.py:176-179` | `pdb.set_trace()` di bare `except` → menggantung run non-interaktif |
| Catatan | `file_utils.py` duplikat | `Extract-Classify-ACOS/file_utils.py` byte-identik dengan `bert_utils/file_utils.py` |
| Catatan | `run.sh` path absolut | Harus diedit manual sebelum jalan |
| Catatan | Path-mismatch jembatan | `get_1st_pairs.py` output ke `BASE_DIR`, `run_step2.py` baca dari `DATA_DIR/tokenized_data/` — bisa silent write ke tempat salah |
| Catatan | Tidak ada `requirements.txt` | Dep: `torch`, `pytorch-crf`/`torchcrf`, `scikit-learn`, `tqdm`, `numpy`, `boto3`/`requests` |
| Catatan | `.gitignore` minim | 16 file `.pyc` di `__pycache__/` ter-track (CRLF line endings) |
| Catatan | `data/` tidak dipakai | Kode pakai `Extract-Classify-ACOS/tokenized_data/` |

## 5. Temuan Notebook

Enam notebook (`notebooks/00-05`) belum pernah dieksekusi (`execution_count` = `None`, tanpa `outputs`).

Lima blocker kritis yang diperbaiki di `colab_utils.py`:

| # | Masalah | Solusi di `colab_utils.py` |
|---|---------|----------------------------|
| 2.1 | `convert_examples_to_features_categorysenti` tidak ada (yg ada: `convert_examples_to_features2nd`) | Wrapper `features_step2` |
| 2.2 | `processor.get_test_examples` / `get_test_1st_examples` tidak ada di `CategorySentiProcessor` | Wrapper `pair_examples_from_file` + `resolve_eval_pair_file` |
| 2.3 | `domain_type=` kwarg tidak diterima `convert_examples_to_features` | Wrapper `features_step1/2` menyerap kwarg berlebih |
| 2.4 | `model(...)` return `([loss], [logits])` → `loss.backward()` gagal (list) | `unpack_model_output` ambil skalar |
| 2.5 | Benchmark 15 subtask & 4 subset angka ditulis manual (bukan dihitung) | `SubtaskMetricCapture` tangkap dari log `pair_eval` |
| 2.6 | Inferensi pakai keyword matching, bukan model | `analyze_review_quadruples` ditulis ulang: tokenisasi → Step1 CRF → span → Step2 klasifikasi |

Tambahan `colab_utils.py`:

- `setup_timestamped_run_dir`: tambah subfolder `md/`.
- `analyze_and_plot_eda`: +2 plot (panjang kalimat, heatmap kategori×sentimen).
- `plot_training_history`: return dict path plot/CSV/DataFrame.
- Helper baru: `df_to_markdown`, `export_step_table`, `MarkdownReport`, `SubtaskMetricCapture`, `plot_subtask_metrics`.

## 6. Gaps Kritis (Belum Terverifikasi/Eksekusi)

1. Pipeline belum dijalankan — environment Python 3.14 tanpa `torch`/`pandas`/`matplotlib`.
2. Angka metrik belum pernah dihasilkan — notebook sekarang menyediakan jalurnya, bukan hasilnya.
3. Bug P2 belum di-fix: `ae_loss`, `pdb.set_trace()`, duplikasi `file_utils`, path mismatch jembatan.
4. Tidak ada test/unit test di repo.
5. CRLF line endings di semua `.tsv` di `tokenized_data/`.

## 7. Rekomendasi Prioritas

| Prioritas | Aksi | Alasan |
|-----------|------|--------|
| P0 | Fix `ae_loss` di `run_step1.py:422,426` (pakai `loss` atau `losses[0]`) | Blocker kalau pakai grad accumulation/FP16 |
| P0 | Hapus `pdb.set_trace()` di `run_classifier_dataset_utils.py:179` | Blocker run batch/non-interaktif |
| P1 | Hapus duplikasi `file_utils.py` (pertahankan `bert_utils/`) | Kebersihan, hindari confusion import |
| P1 | Selaraskan path jembatan: `get_1st_pairs.py` output ke `DATA_DIR/tokenized_data/` | Hindari silent mismatch |
| P1 | Buat `requirements.txt` minimal | Reproducibility |
| P2 | Commit `.gitignore` yang proper (abaikan `__pycache__/`, `*.pyc`, `results/`, `bert_base_uncased/`) | Hygiene |
| P2 | Normalisasi line ending `.tsv` → LF | Konsistensi parsing |

## 8. Catatan Karakteristik Kode

- Legacy codebase: porting `pytorch_pretrained_bert` (pre-`transformers`), bukan pakai `transformers` library modern.
- Hardcode-heavy: `run.sh`, category list di `run_classifier_dataset_utils.py` (13 rest16, 121 laptop), max_seq_length=128.
- No config file: semua hyperparameter lewat CLI args di `run_step1.py` / `run_step2.py`.
- CRF dependency: `torchcrf` (pytorch-crf 0.7.2 per Readme).
- Two-stage pipeline design: error propagation Step 1 → Step 2 by design (bukan joint).

## Kesimpulan

Repo ini adalah kode penelitian (research code) yang sudah di-porting minimal agar jalan di Colab/lokal, tetapi masih punya bug upstream, tidak ada test, belum pernah dieksekusi end-to-end di environment bersih, dan notebook baru siap pakai setelah patch `colab_utils.py`. Jika targetnya reproduksi paper → fix P0/P1 dulu, baru jalankan pipeline.
