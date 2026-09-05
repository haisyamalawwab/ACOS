# Sel 60 — 8a. Inisialisasi Step 2: Patch Tokenizer OOV, Patch Metrik, Label & Path

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 60 dari 80 (indeks JSON `cells[59]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan prasyarat Step 2 dan membuat tokenisasi tahan terhadap token di luar vocab.

## Apa yang dilakukan

1. `ensure_objects()`; impor `CategorySentiClassification, read_pair_gold, pair_eval, BertTokenizer, BertAdam, processors, output_modes`.
2. `FORCE_RETRAIN_STEP2 = False`; bersihkan cache GPU.
3. Monkey-patch `BertTokenizer.convert_tokens_to_ids` → token OOV dipetakan ke `[UNK]` (id 100 fallback) dan dicatat sekali di `_oov_seen`, bukan `KeyError`.
4. `patch_eval_metrics_counts()` (idempoten).
5. `processor_step2 = processors['categorysenti']()`; `label_list_step2 = get_labels(DOMAIN)`; `num_labels_step2 = len(label_list_step2[0])` (39 untuk 13 kategori × 3 sentimen).
6. Path: `step2_ckpt, step2_bin, step2_csv = csv/step2_training_history.csv, step2_progress_json`.
7. `logger2 = logging.getLogger('Step2')`; `args_h` dibangun di sini bila belum ada (karena 8d dilewati saat cache hit tetapi 8e/9a membutuhkannya).

## Keluaran / variabel yang dihasilkan

- `processor_step2, label_list_step2, num_labels_step2, step2_ckpt, step2_bin, step2_csv, step2_progress_json, logger2, args_h, FORCE_RETRAIN_STEP2`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 7, 17, 54 (`ensure_objects`).

---
← [Sel 59](059_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell59_05092026.md) | [Indeks](README.md) | [Sel 61](061_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell61_05092026.md) →
