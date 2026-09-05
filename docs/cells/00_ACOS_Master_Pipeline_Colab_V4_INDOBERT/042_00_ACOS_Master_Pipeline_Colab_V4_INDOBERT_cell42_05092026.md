# Sel 42 — Heading: 5d2. Gate 1 — Bobot Encoder Benar-Benar Termuat

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 42 dari 80 (indeks JSON `cells[41]`) |
| Tipe sel | markdown |
| Bagian | 5d2. Gate 1 (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menjelaskan gate paling penting: membandingkan tiga tensor encoder model yang sudah dimuat dengan tensor di checkpoint memakai `torch.equal` (embedding kata, `layer.0` query, `layer.11` output). Bila merah, semua metrik di bawahnya hanya mengukur head yang belajar dari representasi acak; logging `missing_keys` upstream di-comment out sehingga tidak ada gejala lain.

---
← [Sel 41](041_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell41_05092026.md) | [Indeks](README.md) | [Sel 43](043_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell43_05092026.md) →
