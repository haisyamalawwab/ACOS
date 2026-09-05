# Sel 68 — 8e. Training Category-Sentiment per Epoch + Checkpoint + Ringkasan Run

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 68 dari 80 (indeks JSON `cells[67]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Loop training utama Step 2; metrik dihitung pada level quadruple lengkap via `pair_eval`.

## Apa yang dilakukan

1. Cache hit → cetak F1 terbaik, lewati.
2. Per batch: `model_step2(tokenizer, epoch, aspect_input_ids, aspect_token_type_ids, aspect_attention_mask, candidate_aspect, candidate_opinion, label_id)` → loss → step.
3. Evaluasi: `pair_eval(epoch, args_h, logger2, tokenizer, model_step2, eval_loader_2, eval_gold_2, label_list_step2, device, 'categorysenti', eval_type='test')` → F1/P/R/tp/fp/fn; `peak_vram2`.
4. Simpan checkpoint bila F1 naik **atau epoch 1 atau bin belum ada** (menjamin checkpoint selalu tersedia); setelah loop, simpan lagi bila bin masih belum ada.
5. Tiap epoch: CSV riwayat, `write_stage_progress(step2_progress_json, stage='STEP2_TRAINING', ...)`, `update_mcp_manifest('STEP2_TRAINING', 5, ...)`.
6. Setelah loop (kedua cabang): tulis `logs/step2_run_result.json` termasuk `sumber_kandidat` (`step1`/`gold`).

## Keluaran / variabel yang dihasilkan

- `checkpoints/step2_best/*`, `csv/step2_training_history.csv`, `logs/step2_progress.json`, `logs/step2_run_result.json`, `step2_history, best_step2_f1, best2_epoch`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 66 (8d).

---
← [Sel 67](067_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell67_05092026.md) | [Indeks](README.md) | [Sel 69](069_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell69_05092026.md) →
