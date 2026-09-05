# Sel 31 — Heading: 4d. Gerbang Data Indonesia (wajib sebelum training)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 31 dari 80 (indeks JSON `cells[30]`) |
| Tipe sel | markdown |
| Bagian | 4d. Gerbang Data (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menjelaskan lima gate torch-free yang dijalankan berurutan dan melempar exception bila merah: `taxonomy` (13 kategori kode == `label_maps.json`, urutan sama), `dataset` (berkas ada; `review_id` train/dev/test saling lepas), `acos_build` (`appsid_quad_*.tsv` terbentuk, span menunjuk token nyata), `tokenized` (retokenisasi WordPiece tidak menghilangkan tuple), `gate2_english` (regenerasi data Inggris identik dengan `tokenized_data/` repo — dengan toleransi satu kalimat pada `rest16_train_pair.tsv` karena cacat span lebar-nol `3,3` di baris 451 data upstream).

---
← [Sel 30](030_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell30_05092026.md) | [Indeks](README.md) | [Sel 32](032_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell32_05092026.md) →
