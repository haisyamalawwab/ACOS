# Sel 14 — Konfigurasi V4: DOMAIN, BACKBONE, Hyperparameter & Seeding

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 14 dari 80 (indeks JSON `cells[13]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menetapkan seluruh parameter run V4 dan aturan konsistensi domain ↔ backbone.

## Apa yang dilakukan

1. `DOMAIN = 'appsid'` (pilihan: `appsid` Indonesia; `rest16`/`laptop` Inggris sebagai kontrol).
2. `BACKBONE = 'indobert'` (pilihan: `indobert` → indobenchmark/indobert-base-p1; `indobert-large`; `bert-en` → bert-base-uncased).
3. Hyperparameter: `MAX_SEQ_LENGTH=128, STEP1_BATCH_SIZE=24, STEP2_BATCH_SIZE=16, STEP1_LR=2e-5, STEP2_LR=5e-5, NUM_EPOCHS=15, SEED=42, DO_LOWER_CASE=True` (lowercase wajib karena `tokenizer_config.json` indobert-base-p1 kosong).
4. `_IS_ID_DOMAIN` — bila domain Inggris tetapi backbone bukan `bert-en`, BACKBONE **dipaksa** `bert-en` (vocab IndoBERT pada teks Inggris → [UNK] masif).
5. `BACKBONE_DIRNAME` — satu folder cache per backbone (`indobert_base_p1`, `indobert_large_p1`, `bert_base_uncased`) agar checkpoint/vocab tidak saling timpa; helper `_backbone_dirname()` dipakai juga sel pemulihan.
6. `tokenized_base = indo_root if _IS_ID_DOMAIN else extract_dir` — argumen `data_dir` untuk processor upstream (processor menambah `/tokenized_data/...` sendiri).
7. Seeding `random/np/torch(+cuda)`; `active_save_dir = indo_root`; `RESUME_LAST_SESSION = True`; `results_base = indo_root/results`.

## Keluaran / variabel yang dihasilkan

- Semua konstanta hyperparameter, `BACKBONE`, `tokenized_base`, `results_base`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 12 (`indo_root`, `extract_dir`).

---
← [Sel 13](013_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell13_05092026.md) | [Indeks](README.md) | [Sel 15](015_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell15_05092026.md) →
