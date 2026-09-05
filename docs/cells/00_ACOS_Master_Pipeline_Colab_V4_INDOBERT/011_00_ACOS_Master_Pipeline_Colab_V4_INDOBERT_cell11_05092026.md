# Sel 11 — Heading: 2c. Dua Root & Paket `acos_id/`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 11 dari 80 (indeks JSON `cells[10]`) |
| Tipe sel | markdown |
| Bagian | 2c. Dua Root (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menjelaskan konsep **dua root** V4: `indo_root` (`ACOS-IndoBERT/`, tempat menulis dataset/tokenized/backbones/results) dan `acos_root` (`ACOS-ASLI/`, hanya dibaca: `Extract-Classify-ACOS/` + data rest16). Semua perbedaan Indonesia hidup di paket `acos_id/`, bukan patch pada repo upstream, sehingga jalur Inggris tetap bisa jadi kontrol. Sel ini sengaja diletakkan **setelah** dua sel path karena ia menimpa `base_project_dir`/`extract_dir`; kelengkapan paket diperiksa per modul.

---
← [Sel 10](010_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell10_05092026.md) | [Indeks](README.md) | [Sel 12](012_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell12_05092026.md) →
