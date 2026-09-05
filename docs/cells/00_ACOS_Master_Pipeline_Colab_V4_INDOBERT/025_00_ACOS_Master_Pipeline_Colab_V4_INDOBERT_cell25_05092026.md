# Sel 25 — Tabel Statistik, Ringkasan EDA & Tampilan Plot

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 25 dari 80 (indeks JSON `cells[24]`) |
| Tipe sel | code |
| Bagian | 4. EDA |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Mengekspor statistik per split dan ringkasan EDA ke CSV/MD, lalu menampilkan 4 plot ke notebook dan laporan.

## Apa yang dilakukan

1. `rep.section('2. Eksplorasi data')`; bila `df_stats` kosong → peringatan folder `data/` tidak ada.
2. `export_step_table(df_stats, 'master_01_statistik_dataset')`.
3. Bila `df_records` ada: hitung `Total_Quadruple, Implicit_Aspect, Implicit_Opinion, Keduanya_Implicit, Kategori_Unik, Panjang_Kalimat_Median` → `master_02_ringkasan_eda`.
4. Tampilkan & catat ke `rep.image`: `01_eda_dataset_distribution.png`, `02_eda_category_sentiment.png`, `02b_eda_length_and_implicit_combo.png`, `02c_eda_category_sentiment_heatmap.png`.

## Keluaran / variabel yang dihasilkan

- `df_ringkas`; CSV/MD `master_01`, `master_02`.

---
← [Sel 24](024_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell24_05092026.md) | [Indeks](README.md) | [Sel 26](026_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell26_05092026.md) →
