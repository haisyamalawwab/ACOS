# Sel 74 — 9b. Tabel `master_07/08/09`, Plot Sub-Task, Manifest & State

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 74 dari 80 (indeks JSON `cells[73]`) |
| Tipe sel | code |
| Bagian | 9. Evaluasi Final |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Mengekspor dashboard benchmark.

## Apa yang dilakukan

1. `rep.section('6. Hasil akhir pipeline')`; `df_overall = metrics_display_frame(final_res)` → `export_step_table('master_07_metrik_quadruple_final', notes sumber kandidat & keterangan TP/FP/FN)`.
2. Bila `df_subtasks` tidak kosong: konversi P/R/F1 ke persen, bulatkan TP/FP/FN → `rep.section('7. Metrik per sub-task')`, `export_step_table('master_08_metrik_subtask', max_rows_md=20)`.
3. `plot_subtask_metrics(df_subtasks, plots/05_benchmark_subtasks_f1.png, title='[DOMAIN] Micro-F1 per Sub-Task')`, `rep.image`.
4. Agregasi per `N_Elements`: jumlah sub-task, mean/min/max Micro-F1, total TP/FP/FN → `export_step_table('master_09_agregasi_elemen')`.
5. `update_mcp_manifest('FINAL_EVAL_COMPLETED', 6, {final_metrics, metrics_json_path})`; `save_pipeline_state({'final_res': final_res})`.

## Keluaran / variabel yang dihasilkan

- CSV/MD `master_07`, `master_08`, `master_09`; `plots/05_benchmark_subtasks_f1.png`; manifest; state.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 72 (9a) — `final_res, df_subtasks`.

---
← [Sel 73](073_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell73_05092026.md) | [Indeks](README.md) | [Sel 75](075_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell75_05092026.md) →
