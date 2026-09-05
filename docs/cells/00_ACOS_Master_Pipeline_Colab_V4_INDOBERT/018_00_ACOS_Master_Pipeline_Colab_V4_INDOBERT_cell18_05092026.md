# Sel 18 — Inisialisasi `MarkdownReport`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 18 dari 80 (indeks JSON `cells[17]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Membuat akumulator laporan Markdown `rep` yang menampung seluruh tabel, gambar, dan catatan pipeline.

## Apa yang dilakukan

1. `rep = MarkdownReport('00 - Master Pipeline ACOS End-to-End [DOMAIN]', md_dir, filename='00_master_pipeline.md', meta={...})` dengan meta domain, epoch, batch, lr, max_seq_length, seed, device, session_dir.

## Keluaran / variabel yang dihasilkan

- Objek global `rep`; berkas `md/00_master_pipeline.md` akan ditulis bertahap.

---
← [Sel 17](017_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell17_05092026.md) | [Indeks](README.md) | [Sel 19](019_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell19_05092026.md) →
