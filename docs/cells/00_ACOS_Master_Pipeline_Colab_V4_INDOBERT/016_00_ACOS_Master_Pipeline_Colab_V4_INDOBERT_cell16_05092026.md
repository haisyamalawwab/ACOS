# Sel 16 — Helper `session_cache_score()`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 16 dari 80 (indeks JSON `cells[15]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menghitung berapa artefak kunci (0–6) yang ada di sebuah folder sesi; 0 berarti sesi kosong.

## Apa yang dilakukan

1. Penanda: `pipeline_state.pkl`, `csv/master_01_statistik_dataset.csv`, `logs/pred4pipeline.txt`, `checkpoints/step1_best/pytorch_model.bin`, `checkpoints/step2_best/pytorch_model.bin`, `logs/master_metrics.json`.

## Keluaran / variabel yang dihasilkan

- Fungsi `session_cache_score(run_dir) -> int`.

---
← [Sel 15](015_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell15_05092026.md) | [Indeks](README.md) | [Sel 17](017_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell17_05092026.md) →
