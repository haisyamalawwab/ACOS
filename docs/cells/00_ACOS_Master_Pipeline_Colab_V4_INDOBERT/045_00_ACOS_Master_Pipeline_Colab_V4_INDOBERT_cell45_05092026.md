# Sel 45 — 5e. Training BERT-CRF per Epoch + Checkpoint Terbaik + Ringkasan Run

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 45 dari 80 (indeks JSON `cells[44]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Loop training utama Step 1; setelahnya (di kedua cabang) menulis `step1_run_result.json`.

## Apa yang dilakukan

1. Cache hit → cetak F1 terbaik tersimpan, lewati training.
2. Untuk setiap epoch 1..`NUM_EPOCHS`: `model.train()`; per batch → `model_step1(aspect_input_ids, aspect_labels, aspect_token_type_ids, aspect_attention_mask, exist_imp_aspect, exist_imp_opinion)` → `unpack_model_output` → `loss.backward(); optimizer_1.step(); zero_grad()`; postfix loss tiap 10 batch.
3. Evaluasi: `pred_eval(epoch, args_h, logger, tokenizer, model_step1, eval_loader_1, eval_gold_1, label_list_step1, device, 'quad', eval_type='test')` → `micro-F1, precision, recall, tp, fp, fn`; `peak_vram` via `max_memory_allocated`.
4. Tambah ke `step1_history`; bila F1 naik → `torch.save(state_dict, step1_bin)`, `config.to_json_file`, `tokenizer.save_vocabulary(step1_ckpt)`.
5. Setiap epoch: tulis CSV riwayat, `write_stage_progress(step1_progress_json, stage='STEP1_TRAINING', ...)`, `update_mcp_manifest('STEP1_TRAINING', 3, {...})`.
6. Setelah loop (kedua cabang): tulis `logs/step1_run_result.json` (mode trained/cache_hit, epoch terbaik, best_row, history, checkpoint, csv).

## Keluaran / variabel yang dihasilkan

- `checkpoints/step1_best/{pytorch_model.bin, config.json, vocab.txt}`, `logs/pred4pipeline.txt` (ditulis `pred_eval`), `csv/step1_training_history.csv`, `logs/step1_progress.json`, `logs/step1_run_result.json`, `step1_history, best_step1_f1, best1_epoch`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 41 (`model_step1, optimizer_1, train_loader_1, eval_loader_1`).

## Catatan

- Tidak aman diulang tanpa sengaja — melatih ulang dari bobot terakhir di memori (jalankan 5d dulu untuk reset).

---
← [Sel 44](044_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell44_05092026.md) | [Indeks](README.md) | [Sel 46](046_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell46_05092026.md) →
