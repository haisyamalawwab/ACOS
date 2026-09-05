# Sel 35 — 5a. Inisialisasi Step 1: Tokenizer, Patch Metrik, Taksonomi ID, Label & Path

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 35 dari 80 (indeks JSON `cells[34]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan semua prasyarat Step 1 tanpa menyentuh data training.

## Apa yang dilakukan

1. `FORCE_RETRAIN_STEP1 = False`.
2. Bersihkan cache CUDA & laporkan VRAM bebas (`mem_get_info`, fallback total memory).
3. `tokenizer = BertTokenizer.from_pretrained(bert_cache_dir, do_lower_case=True)` — vocab IndoBERT hasil 4c.
4. `patch_eval_metrics_counts()` — kini `pred_eval` mengembalikan tp/fp/fn.
5. **V4**: `acos_taxonomy.patch_processor_labels(processors)` — menambah cabang domain Indonesia pada `get_labels()` tanpa mengubah berkas upstream.
6. `processor_step1 = processors['quad']()`; `label_list_step1 = get_labels(DOMAIN)`; `num_labels_step1 = len(label_list_step1[1])`; `label_map_seq` (label → indeks).
7. Path: `step1_ckpt = session_dirs['step1_checkpoint']`, `step1_bin`, `step1_csv = csv/step1_training_history.csv`, `pred_file = logs/pred4pipeline.txt`, `step1_progress_json`.

## Keluaran / variabel yang dihasilkan

- `tokenizer, processor_step1, label_list_step1, num_labels_step1, label_map_seq, step1_ckpt, step1_bin, step1_csv, pred_file, step1_progress_json, FORCE_RETRAIN_STEP1`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 7, 12, 17 (dan 4c untuk vocab).

---
← [Sel 34](034_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell34_05092026.md) | [Indeks](README.md) | [Sel 36](036_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell36_05092026.md) →
