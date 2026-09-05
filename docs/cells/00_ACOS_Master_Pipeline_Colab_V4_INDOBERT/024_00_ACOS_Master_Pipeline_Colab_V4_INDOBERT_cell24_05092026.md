# Sel 24 — Eksekusi EDA (Cache Memori → Cache Disk → acos_id.eda / colab_utils)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 24 dari 80 (indeks JSON `cells[23]`) |
| Tipe sel | code |
| Bagian | 4. EDA |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menjalankan EDA hanya bila belum ada hasilnya, dengan fungsi EDA yang berbeda untuk domain Indonesia.

## Apa yang dilakukan

1. Cabang 1: `df_stats` & `df_records` sudah di memori → CACHE HIT.
2. Cabang 2: ketiga berkas (2 CSV + plot utama) ada → muat `df_stats`, `df_ringkas` dari CSV; `df_records = DataFrame()` kosong.
3. Cabang 3 (V4): `acos_taxonomy.is_id_domain(DOMAIN)` → `acos_eda.analyze_and_plot_eda_id(data_dir=data_root, domain, output_plots_dir, output_csv_dir)` — karena `colab_utils.analyze_and_plot_eda` memetakan domain lewat tabel tertutup {rest16, laptop} dan diam-diam fallback ke Restaurant-ACOS.
4. Cabang 4 (kontrol Inggris): `analyze_and_plot_eda(data_dir=acos_root, ...)`.

## Keluaran / variabel yang dihasilkan

- `df_stats`, `df_records` (+ plot 01/02/02b/02c PNG 300 DPI dan CSV di folder sesi).

## Prasyarat (sel yang harus sudah berjalan)

- Sel 12 (`acos_eda`, `acos_taxonomy`), sel 17 (`plots_dir`, `csv_dir`).

---
← [Sel 23](023_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell23_05092026.md) | [Indeks](README.md) | [Sel 25](025_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell25_05092026.md) →
