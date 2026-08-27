# Dokumentasi Metode & Teknik per Cell — 02. Step 1: Aspect & Opinion Co-Extraction (BERT-CRF)

Tanggal: 2026-08-27
Objek: `notebooks/02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb`
Metode: pembacaan statis seluruh cell (7 code + 8 markdown). Tidak dieksekusi.

---

## 0. Ringkasan Eksekutif

Notebook 02 adalah **tahap pertama pipeline**: melatih `BertForQuadABSA` (BERT + Linear + CRF) untuk mengekstrak span aspect & opinion, plus mendeteksi implicit aspect/opinion. Output kuncinya adalah `logs/pred4pipeline.txt` — jembatan ke notebook 03.

Tujuh cell kode:
1. Environment, path, import (identik pola notebook 01)
2. Konfigurasi hyperparameter + init session
3. Load data + konversi fitur + parsing gold test
4. Inisialisasi model `BertForQuadABSA`
5. Training loop dengan checkpoint berbasis micro-F1
6. Pemuatan checkpoint + inferensi final + profil `pred4pipeline.txt`
7. Render plot + simpan laporan

---

## 1. Diagram Alur Konseptual

```
┌───────────────────────────────────────────────────────────────────┐
│            NOTEBOOK 02: STEP 1 (ASPECT-OPINION CO-EXTRACTION)      │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [Cell 2]  Env: pip install, path, import                          │
│            → modeling.BertForQuadABSA, tokenization, BertAdam      │
│            → run_classifier_dataset_utils, eval_metrics.pred_eval  │
│      │                                                             │
│  [Cell 4]  Config: DOMAIN, batch, LR 2e-5, 15 epoch, SEED 42       │
│            → cache BERT → setup_timestamped_run_dir()              │
│            → MarkdownReport                                        │
│      │                                                             │
│  [Cell 6]  Data: processor.get_dev_examples → features_step1()     │
│            → TensorDataset(7 field) → eval_dataloader              │
│            → Parse gold test → B-A/I-A/B-O/I-O + flag implicit     │
│            → Tabel fitur + distribusi tag + plot profil data       │
│      │                                                             │
│  [Cell 8]  Model: BertForQuadABSA.from_pretrained(num_labels)      │
│      │                                                             │
│  [Cell 10] TRAIN (DO_TRAIN=True):                                  │
│            for epoch:                                              │
│              forward → unpack_model_output(loss) → backward        │
│              → optimizer.step()                                    │
│              pred_eval(eval_type='test') → micro-F1                │
│              if F1 best: save state_dict+config+vocab+metadata     │
│            → plot kurva + CSV riwayat + statistik loss             │
│      │                                                             │
│  [Cell 12] EVAL FINAL: reload checkpoint step1_best                │
│            → pred_eval → pred4pipeline.txt                         │
│            → profil: N_Aspect/N_Opinion/implicit/calon pasangan    │
│      │                                                             │
│  [Cell 14] Render 3 plot + rep.save()                              │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Detail Metode/Teknik per Cell

### Cell 2 — Environment & Imports
- Pola path/import **identik** dengan notebook 00/01: auto-clone bila repo kosong, deteksi `base_project_dir` 6 cabang, `sys.path.insert`, fallback unduh `colab_utils` dari raw GitHub.
- Import spesifik task: `BertForQuadABSA`, `BertTokenizer`, `BertAdam`, `processors`/`output_modes`/`convert_examples_to_features`, `pred_eval`.
- Deteksi device + nama GPU.

### Cell 4 — Konfigurasi & Session Init
- Parameter: `DOMAIN="rest16"`, `TASK_NAME="quad"`, `DO_TRAIN=True`, `DO_EVAL=True`, `MAX_SEQ_LENGTH=128`, `TRAIN_BATCH_SIZE=24`, `EVAL_BATCH_SIZE=16`, `LEARNING_RATE=2e-5`, `NUM_TRAIN_EPOCHS=15`, `WARMUP=0.1`, `SEED=42`.
- Seeding penuh; `download_bert_pretrained` cache lokal; `setup_timestamped_run_dir`.
- `MarkdownReport` dengan meta lengkap; tabel konfigurasi via `export_step_table`.

### Cell 6 — Data Loading & Feature Conversion
- `processor = processors["quad"]()`; `label_list` = 6 tag sekuens `['[CLS]','O','I-A','B-A','I-O','B-O']`.
- **Wrapper `features_step1`**: membungkus `convert_examples_to_features` karena signature asli tidak menerima `domain_type` (lihat laporan 002 §2.2). Komentar di cell menjelaskan alasan ini.
- 7 field tensor per fitur: `aspect_input_ids`, `aspect_input_mask`, `aspect_segment_ids`, `aspect_ids` (label sekuens), `exist_imp_aspect`, `exist_imp_opinion`, `tokens_len`.
- **Parsing gold test manual**: bangun `aspect_labels` sepanjang `max_seq_length`, tag `B-A`/`I-A` untuk span aspect, `B-O`/`I-O` untuk opinion, set flag implicit bila span `-1`.
- Struktur `eval_gold` = `[input_text, pairgold]` — format yang diharapkan `pred_eval`.
- **Output analisis**: tabel ringkasan fitur test (jumlah sampel, min/median/maks token, kalimat implicit), tabel distribusi tag gold (dengan catatan tag `O` mendominasi karena padding), dan plot profil data (histogram panjang token + bar tag entitas non-O).

### Cell 8 — Model Initialization
- `BertForQuadABSA.from_pretrained(bert_model_dir, num_labels=num_labels)`.
- Cetak jumlah total parameter (`sum(p.numel())`).

### Cell 10 — Training Loop
- `if DO_TRAIN:` → bangun train dataloader (`RandomSampler`), hitung `num_train_optimization_steps`.
- Optimizer `BertAdam` dengan **weight decay terpisah**: 0.01 untuk parameter umum, 0.0 untuk `bias`/`LayerNorm.*` (praktik standar BERT fine-tuning).
- **Teknik kunci `unpack_model_output`**: `BertForQuadABSA.forward` mengembalikan `([total_loss], [pred_tags, imp_a, imp_o])`; helper mengambil skalar loss agar `.backward()` tidak dipanggil pada list (fix bug §2.3 laporan 002).
- Per epoch: forward → backward → step → zero_grad; log loss per step.
- Evaluasi: `pred_eval(..., eval_type="test")` mengembalikan `precision/recall/micro-F1`.
- **Checkpoint berbasis micro-F1**: simpan `pytorch_model.bin` + `config.json` + `vocab.txt` + `checkpoint_metadata.json` (epoch, F1, P, R, domain, task) saat F1 baru > terbaik.
- **Output**: kurva loss/F1 via `plot_training_history`, CSV riwayat epoch, statistik loss per epoch (`groupby("epoch")["loss"].describe()`), baris epoch terbaik.

### Cell 12 — Standalone Checkpoint Loading & Final Inference
- Reload `BertForQuadABSA.from_pretrained(step1_checkpoint_dir)` (bukan state training terakhir).
- `pred_eval(..., eval_type="test")` → menulis `logs/pred4pipeline.txt` (lewat `args.output_dir`).
- **Profil prediksi**: parse `pred4pipeline.txt`, hitung `N_Aspect`/`N_Opinion` per kalimat, flag implicit (`a--1,-1`/`o--1,-1`), estimasi calon pasangan (`max(n_a,1) * max(n_o,1)`).
- **Output**: ringkasan prediksi, detail 30 kalimat pertama, CSV lengkap, plot distribusi aspect/opinion per kalimat.
- Fallback: bila `pred4pipeline.txt` tidak ada, catat di laporan (notebook 03 akan fallback).

### Cell 14 — Render Plot & Save
- Render 3 plot (`02a` profil data, `03` kurva training, `03b` distribusi prediksi) secara selektif (skip bila file tak ada).
- `rep.save()` → tulis `02_step1_ekstraksi.md`.

---

## 3. Pola Teknis Menonjol

| Pola | Penerapan |
|------|-----------|
| **Wrapper adaptasi API** | `features_step1` menyerap mismatch `domain_type`; `unpack_model_output` ambil skalar loss |
| **Checkpoint metadata** | `checkpoint_metadata.json` menyimpan epoch/F1/P/R/domain/task — lebih informatif dari sekadar state_dict |
| **Weight decay terpisah** | 0.01 umum vs 0.0 bias/LayerNorm (best-practice BERT) |
| **Profil output jembatan** | `pred4pipeline.txt` langsung dianalisis (N span, implicit, estimasi pasangan) sebelum masuk notebook 03 |
| **Defensive fallback** | Bila `pred4pipeline.txt` kosong, laporan mencatat bukan crash |
| **Dual output konsisten** | Setiap tabel → `export_step_table` (CSV+MD+display) |

---

## 4. Artefak yang Dihasilkan

| Jenis | File |
|-------|------|
| Checkpoint | `checkpoints/step1_best/{pytorch_model.bin, config.json, vocab.txt, checkpoint_metadata.json}` |
| Log | `logs/pred4pipeline.txt` |
| CSV | `step1_00`–`step1_07` + `step1_training_history.csv`, `step1_loss_per_step.csv`, `step1_prediksi_per_kalimat_lengkap.csv` |
| Plot | `02a_step1_data_profile.png`, `03_step1_training_loss_f1_curve.png`, `03b_step1_prediksi_distribusi.png` |
| Markdown | `02_step1_ekstraksi.md` |

---

## 5. Catatan Kritis

1. **Evaluasi memakai test set tiap epoch** (`eval_type="test"`), bukan dev set — tabel mencatat ini secara eksplisit. Praktis untuk demo, tapi berarti **pemilihan checkpoint bocor ke test** (risiko overfitting; hasil tidak sebanding langsung dengan paper yang memakai dev untuk seleksi).
2. **`num_labels = len(label_list[1])`** — jumlah label sekuens (6), bukan sentimen; konsisten dengan head CRF model.
3. **`step_loss_log` menyimpan loss per step** — tabel statistik per epoch dihasilkan dari `describe()`, tapi CSV per-step penuh juga disimpan (bisa besar untuk dataset laptop).
4. **Checkpoint hanya tersimpan bila F1 > 0.0 pertama kali** — bila epoch 1 F1 = 0 dan tidak pernah naik, tidak ada checkpoint; notebook 03/05 akan gagal memuat. (Kasus edge; praktis jarang.)
5. **`ArgsHelper` dibuat ulang di cell 10 dan 12** — duplikasi kecil; keduanya hanya butuh `output_dir` dan `max_seq_length`.
6. **CRF memakai `torchcrf`** — dependensi non-standar; harus terpasang (sudah ada di `!pip install`).
7. **Perbedaan vs `run_step1.py` asli**: notebook memakai `EVAL_BATCH_SIZE=16` dan 15 epoch (paper 30), jadi angka tidak langsung sebanding dengan Tabel paper.
