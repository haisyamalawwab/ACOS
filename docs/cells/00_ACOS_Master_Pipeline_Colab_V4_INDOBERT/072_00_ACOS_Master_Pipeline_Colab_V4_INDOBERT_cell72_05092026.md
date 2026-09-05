# Sel 72 — 9a. Evaluasi Quadruple Final dengan Checkpoint Terbaik + 15 Sub-Task

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 72 dari 80 (indeks JSON `cells[71]`) |
| Tipe sel | code |
| Bagian | 9. Evaluasi Final |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menghasilkan metrik akhir pipeline dan rincian sub-task, dengan multi-tier recovery checkpoint.

## Apa yang dilakukan

1. `FORCE_REEVAL = False`; impor `eval_metrics as _em_final, CategorySentiClassification, pair_eval, SubtaskMetricCapture, plot_subtask_metrics`.
2. Cache: bila `logs/master_metrics.json` ada dan tidak dipaksa → muat `final_res`, `subtask_metrics`, bangun `df_subtasks`.
3. Jika evaluasi: wajib `eval_loader_2`/`eval_gold_2` (kalau tidak → jalankan 8c dulu), `args_h`, `num_labels_step2`, `label_list_step2`.
4. Recovery checkpoint 4 tingkat: (1) simpan dari `model_step2` di memori; (2) `auto_find_file(... must_contain='step2_best', domain=DOMAIN)` lintas sesi; (3) fallback darurat salin `bert_cache_dir/pytorch_model.bin`; (4) pastikan `config.json` & `vocab.txt` ada; masih tidak ada → `FileNotFoundError`.
5. `model_step2_best = CategorySentiClassification.from_pretrained(step2_checkpoint, num_labels).to(device).eval()`.
6. `patch_eval_metrics_counts()`; `with SubtaskMetricCapture(logger_final) as cap: final_res = pair_eval('final', ...)`; `subtask_metrics = cap.to_dict()`, `df_subtasks = cap.to_frame()`.
7. Simpan `logs/master_metrics.json` (overall, subtasks, difficulty_breakdown, step1/2_history, sumber_kandidat, saved_at); cetak metrik (hitungan mentah untuk tp/fp/fn, persen untuk laju).

## Keluaran / variabel yang dihasilkan

- `final_res, subtask_metrics, df_subtasks, model_step2_best`; `logs/master_metrics.json`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 64 (8c) atau cache metrik; checkpoint Step 2.

## Catatan

- Fallback tingkat 3 (pretrained cache) hanya mencegah crash — hasilnya tidak bermakna sebagai skor pipeline.

---
← [Sel 71](071_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell71_05092026.md) | [Indeks](README.md) | [Sel 73](073_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell73_05092026.md) →
