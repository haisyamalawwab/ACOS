# Sel 47 — 5f. Plot Kurva, Tabel `master_03`, Manifest & State Step 1

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 47 dari 80 (indeks JSON `cells[46]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Merangkum hasil Step 1 ke artefak publikasi dan state.

## Apa yang dilakukan

1. `plot_training_history(step1_history, task_name='Step 1 (BERT-CRF)', output_plot_path=plots/03_step1_training_loss_f1_curve.png, output_csv_path=step1_csv)`.
2. `rep.section('3. Step 1: ekstraksi aspect & opinion')`; `df_s1_tabel = history_display_frame(step1_history)` → `export_step_table('master_03_step1_riwayat', notes=..., max_rows_md=NUM_EPOCHS)`.
3. `rep.kv({epoch_terbaik, micro-F1_terbaik, TP_FP_FN_epoch_terbaik, checkpoint})`.
4. Tampilkan plot & `rep.image`.
5. `update_mcp_manifest('STEP1_COMPLETED', 3, {step1_best_micro_f1, step1_checkpoint})`; `save_pipeline_state({'best_step1_f1', 'best_step1_epoch'})`; laporkan apakah `pred4pipeline.txt` ada.

## Keluaran / variabel yang dihasilkan

- `plots/03_step1_training_loss_f1_curve.png`, CSV/MD `master_03_step1_riwayat`, manifest, `pipeline_state.pkl`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 45 (5e) — `step1_history, best_step1_f1, best1_epoch`.

---
← [Sel 46](046_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell46_05092026.md) | [Indeks](README.md) | [Sel 48](048_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell48_05092026.md) →
