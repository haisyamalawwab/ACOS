# Dokumentasi Metode & Teknik per Cell — 00. Master Pipeline ACOS

Tanggal: 2026-08-27
Objek: `notebooks/00_ACOS_Master_Pipeline_Colab.ipynb`
Metode: pembacaan statis seluruh cell (10 code + 11 markdown). Tidak dieksekusi.
Konteks: notebook master ini adalah orkestrator satu-klik yang menggabungkan isi notebook 01–05 ke dalam satu alur end-to-end.

---

## 0. Ringkasan Eksekutif

Notebook master (`00`) menyusun pipeline ACOS dua-tahap dalam **10 cell kode**:

1. Setup environment & mount Drive
2. Resolusi path + import `colab_utils`
3. Konfigurasi + init direktori timestamped + cache BERT
4. EDA
5. Step 1 — training BERT-CRF (co-extraction aspect+opinion)
6. Jembatan — cross-product pasangan kandidat
7. Step 2 — training multi-label category-sentiment
8. Evaluasi final + capture metrik 15 sub-task
9. Inferensi dua-tahap pada teks bebas
10. Ringkasan artefak & batasan

Setiap cell kode menghasilkan **dua output**: artefak fisik (plot PNG 300dpi, CSV, Markdown) dan laporan terstruktur lewat objek `MarkdownReport`.

---

## 1. Diagram Alur Konseptual

```
┌─────────────────────────────────────────────────────────────────┐
│                     ACOS MASTER PIPELINE (00)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Cell 2]  Env: Drive mount + pip install + device cuda/cpu      │
│      │                                                           │
│  [Cell 4]  Path: deteksi repo, sys.path, import colab_utils      │
│      │                                                           │
│  [Cell 6]  Konfigurasi: DOMAIN, hyperparam, seed                 │
│      │     → setup_timestamped_run_dir() + download BERT         │
│      │                                                           │
│  [Cell 8]  EDA: analyze_and_plot_eda() → 4 plot + CSV            │
│      │                                                           │
│  [Cell 10] STEP 1 (BERT+CRF):                                    │
│      │     BertForQuadABSA → train loop → pred_eval()            │
│      │     → checkpoint step1_best + pred4pipeline.txt           │
│      ▼                                                           │
│  [Cell 12] JEMBATAN: parse pred4pipeline.txt                     │
│      │     → Cartesian aspect×opinion → test_pair_1st.tsv        │
│      ▼                                                           │
│  [Cell 14] STEP 2 (Category-Sentiment):                          │
│      │     CategorySentiClassification → train → pair_eval()     │
│      │     → checkpoint step2_best                               │
│      ▼                                                           │
│  [Cell 16] EVALUASI FINAL: reload step2_best                     │
│      │     → SubtaskMetricCapture(pair_eval) → 15 subtask        │
│      │     → metric JSON                                          │
│      ▼                                                           │
│  [Cell 18] INFERENSI: tokenize → step1 (CRF span) → step2        │
│      │     → dataframe quadruple terurut skor logit              │
│      ▼                                                           │
│  [Cell 20] ARTEFAK: walk dirs → daftar artefak + report.save()   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Detail Metode/Teknik per Cell

### Cell 2 — Environment & Dependency Setup
- **Teknik**: `try/except` mount Google Drive (toleran terhadap environment non-Colab).
- Instalasi: `pytorch-crf`, `transformers`, `huggingface_hub`, `seaborn`, `scikit-learn`, `matplotlib`, `pandas`, `boto3`.
- Pemilihan device: `torch.cuda.is_available()` → `cuda`/`cpu`, tampilkan nama GPU bila ada.
- **Sifat**: non-essential; dirancang agar aman dijalankan di Colab maupun lokal.

### Cell 4 — Path Resolution & Import Fallback
- **Teknik**: deteksi lokasi repo bertingkat (`Extract-Classify-ACOS` di cwd / parent / `ACOS/` / `/content/`).
- Auto-clone `github.com/haisyamalawwab/ACOS.git` bila repo belum ada.
- `sys.path.insert` untuk `base_project_dir`, `extract_dir`, `notebooks_dir`.
- **Import fallback**: bila `colab_utils` tidak ada, unduh dari raw GitHub (`urllib.request`).
- **Sifat**: robust terhadap perbedaan struktur folder Colab vs lokal.

### Cell 6 — Konfigurasi & Session Init
- **Teknik**: parameter terpusat (`DOMAIN`, `MAX_SEQ_LENGTH=128`, `STEP1_BATCH=24`, `STEP2_BATCH=16`, LR 2e-5/5e-5, `NUM_EPOCHS=15`, `SEED=42`).
- Seeding penuh (python/numpy/torch + `cuda.manual_seed_all`).
- `setup_timestamped_run_dir()` → buat `results/<domain>_<DDMMYYYY_HMS>/` dengan subfolder `plots/csv/md/logs/checkpoints/{step1_best,step2_best}`.
- `download_bert_pretrained()` → cache `config.json`, `pytorch_model.bin`, `vocab.txt` dari HuggingFace Hub.
- Instansiasi `MarkdownReport` sebagai akumulator laporan.

### Cell 8 — EDA
- **Teknik**: `analyze_and_plot_eda()` menghitung statistik per split (jumlah kalimat, quadruple, explicit/implicit aspect & opinion, distribusi sentimen, kategori).
- Menghasilkan 4 plot: distribusi dataset, kategori×sentimen, panjang kalimat+kombinasi implicit, heatmap kategori×sentimen.
- Tabel ringkas: total quadruple, implicit aspect/opinion, keduanya implicit, kategori unik, median panjang kalimat.
- **Output**: CSV + Markdown + `display(Image(...))`.

### Cell 10 — Step 1 (Aspect-Opinion Co-Extraction)
- **Model**: `BertForQuadABSA` — BERT encoder + CRF sequence tagger (6 tag: `[CLS] O I-A B-A I-O B-O`) + 2 classifier biner implicit (aspect/opinion dari token `[CLS]`/`[SEP]`).
- **Data**: `processors["quad"]` → `get_train_examples`/`get_dev_examples`; fitur via wrapper `features_step1`.
- **Gold parsing**: membangun `aspect_labels` sepanjang `max_seq_length`, tagging span `B-A/I-A` dan `B-O/I-O`, flag implicit.
- **Optimizer**: `BertAdam` dengan weight decay terpisah (0.01 umum, 0.0 untuk bias/LayerNorm), warmup 0.1.
- **Training loop**: manual (bukan `transformers.Trainer`), pakai `tqdm`; `unpack_model_output` ambil skalar loss dari `([loss],[logits])`.
- **Evaluasi per epoch**: `pred_eval(..., eval_type='test')` → micro-F1.
- **Checkpoint**: simpan state_dict, config.json, vocab saat F1 terbaik → `checkpoints/step1_best/`.
- **Output**: plot kurva loss/F1 + CSV riwayat + tabel Markdown.

### Cell 12 — Jembatan (Candidate Pair Generation)
- **Teknik**: parse `pred4pipeline.txt` (kolom text + span `a...`/`o...`).
- Kartesius: cross-product semua aspect span × semua opinion span.
- Fallback implicit: bila aspect/opinion kosong → `-1,-1`.
- Tulis `{DOMAIN}_test_pair_1st.tsv` format `text####aspan ospan`.
- **Analisis**: klasifikasi tipe pasangan (Explicit/Implicit × Explicit/Implicit) + distribusi.
- **Output**: bar chart distribusi pasangan + CSV.

### Cell 14 — Step 2 (Category-Sentiment Classification)
- **Model**: `CategorySentiClassification` — BERT + mean-pool span aspect & opinion terpisah → concat (768×2) → Linear ke `len(kategori)×3` (39 rest16 / 363 laptop).
- **Loss**: `BCEWithLogitsLoss` multi-label (`CATEGORY#SENTIMENT`).
- **Data eval**: `resolve_eval_pair_file` pilih `_test_pair_1st.tsv` (prediksi step 1) atau fallback `_test_pair.tsv` (gold).
- **Gold**: `read_pair_gold` dari `_test_pair.tsv`.
- **Evaluasi per epoch**: `pair_eval(..., eval_type='test')` → metrik quadruple lengkap.
- **Checkpoint**: `checkpoints/step2_best/`.
- **Catatan penting**: metrik memakai `args_h` (objek `ArgsH` dari cell 10) untuk `output_dir`.

### Cell 16 — Evaluasi Final & Capture 15 Sub-task
- **Teknik**: reload model terbaik dari checkpoint (`step2_best`), bukan state training terakhir.
- `SubtaskMetricCapture` (context manager) menangkap blok `"***** <subtask> results *****"` dari log `pair_eval`, karena `pair_eval` hanya `return` metrik keseluruhan (metrik 15 kombinasi ditulis ke logger).
- **Output**: `master_metrics.json` berisi overall + subtasks + history kedua step + sumber kandidat.
- Bila tidak ada subtask tertangkap → pesan jujur, tabel dilewati (tidak ada angka palsu).
- Agregasi Micro-F1 per jumlah elemen (1–4).

### Cell 18 — Inferensi Dua Tahap pada Teks Bebas
- **Teknik kunci**: versi lama memakai keyword-matching; versi ini benar-benar memanggil model.
- **Step 1**: tokenisasi WordPiece (`[CLS]`+tokens+`[SEP]`, pad ke `max_len`), forward `BertForQuadABSA`, ambil `pred_tags` (argmax CRF), decode span via regex `r"32*"` (aspect) dan `r"54*"` (opinion) — mengikuti konvensi `eval_metrics.pred_eval`, offset −1 karena `[CLS]`.
- Deteksi implicit dari dua logit biner (`argmax`).
- **Step 2**: untuk tiap pasangan kandidat, bangun `candidate_aspect`/`candidate_opinion`, forward `CategorySentiClassification`, ambil indeks `skor > ambang` (default 0.0), decode `CATEGORY#SENTIMENT`.
- **Output**: DataFrame terurut `Skor_Logit` menurun; `Skor_Logit` = logit mentah sebelum sigmoid.

### Cell 20 — Ringkasan Artefak & Batasan
- **Teknik**: `os.walk` checkpoint + list dir CSV/Plot/Markdown/Log → tabel daftar artefak (nama + ukuran KB).
- Batasan dinyatakan eksplisit (epoch 15 vs paper 30, sumber kandidat, tidak dibandingkan langsung dengan paper).
- `report.save()` → tulis file Markdown akhir.

---

## 3. Pola Teknis yang Menonjol

| Pola | Penerapan |
|------|-----------|
| **Wrapper adaptasi API** | `features_step1/2`, `pair_examples_from_file`, `resolve_eval_pair_file`, `unpack_model_output` menyerap mismatch antara notebook dan API `run_classifier_dataset_utils.py` |
| **Jujur soal angka** | Subtask di-capture dari log nyata; bila gagal, dilewati — tidak ada angka manual |
| **Timestamped isolation** | Setiap run membuat folder unik `DDMMYYYY_HMS`, tidak ada tabrakan antar sesi |
| **Dual output** | Setiap step → artefak fisik (PNG/CSV) + laporan Markdown (`rep.*`) |
| **Fallback berlapis** | Path repo, import `colab_utils`, pemilihan file pair eval |
| **Manual training loop** | Tidak pakai `Trainer`; loop eksplisit dengan `tqdm` + checkpoint berbasis F1 |

---

## 4. Peta Notebook (01–05) yang Dirangkum Master

| Notebook | Cell code | Fokus | Dirangkum di cell master |
|----------|-----------|-------|--------------------------|
| 01 Setup & EDA | 7 | env, path, cache BERT, EDA | 2, 4, 6, 8 |
| 02 Step 1 | 6 | BERT-CRF training + checkpoint | 10 |
| 03 Jembatan | 5 | pair generation + statistik | 12 |
| 04 Step 2 | 6 | category-sentiment training | 14 |
| 05 Evaluasi + Inferensi | 8 | 15 subtask + demo inferensi | 16, 18, 20 |

---

## 5. Catatan Kritis

1. **Ketergantungan antar-cell tinggi**: cell 14 memakai `args_h` (dibuat di cell 10) dan `tokenizer` (cell 10); cell 16/18 memakai `label_list_step2`, `model_step2_best`. Menjalankan cell secara terisolasi akan gagal.
2. **Checkpoint load vs training**: cell 16/18 reload dari `step2_checkpoint`/`step1_checkpoint` — mengasumsikan cell 10/14 pernah menulis checkpoint. Bila epoch gagal F1, checkpoint tidak ada.
3. **`args_h` dipakai untuk `output_dir=logs_dir`**: `pred_eval`/`pair_eval` menulis `pred4pipeline.txt`/`result.txt` ke `logs/` lewat `args.output_dir`.
4. **Metrik dihitung di test set tiap epoch** (bukan dev) — catatan di tabel menyebutkan ini; praktik ini membuat pemilihan checkpoint berbasis test (risiko overfitting ke test, meski praktis untuk demo).
5. **Batch size eval hardcoded 16** di cell 10 dan 14, terpisah dari batch train.
6. **Inferensi implicit aspect** menandai `cand_a[0]=1` (posisi `[CLS]`) dan implicit opinion `cand_o[len(tokens)+1]=1` — konsisten dengan konvensi `convert_examples_to_features2nd`.
