# Sel 70 — 8f. Plot Kurva, Tabel `master_06`, Manifest & State Step 2

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 70 dari 80 (indeks JSON `cells[69]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Merangkum hasil Step 2 ke artefak publikasi dan state.

## Apa yang dilakukan

1. `plot_training_history(step2_history, 'Step 2 (Category-Sentiment)', plots/04_step2_training_loss_f1_curve.png, step2_csv)`.
2. `rep.section('5. Step 2: klasifikasi category & sentiment')`; `history_display_frame` → `export_step_table('master_06_step2_riwayat', notes memuat sumber kandidat)`.
3. `rep.kv` epoch/F1/TP-FP-FN terbaik & checkpoint; tampilkan plot.
4. `update_mcp_manifest('STEP2_COMPLETED', 5, {...})`; `save_pipeline_state({'best_step2_f1','best_step2_epoch'})`.

## Keluaran / variabel yang dihasilkan

- `plots/04_step2_training_loss_f1_curve.png`, CSV/MD `master_06`, manifest, state.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 68 (8e).

---
← [Sel 69](069_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell69_05092026.md) | [Indeks](README.md) | [Sel 71](071_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell71_05092026.md) →
