# Sel 15 — Helper `session_dirs_from_root()`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 15 dari 80 (indeks JSON `cells[14]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Membangun peta direktori sesi dari root yang sudah ada tanpa membuat folder timestamp baru (dipakai saat resume).

## Apa yang dilakukan

1. Kunci: `root, checkpoints, step1_checkpoint (checkpoints/step1_best), step2_checkpoint, plots, csv, md, logs`.
2. `os.makedirs(..., exist_ok=True)` untuk setiap path.

## Keluaran / variabel yang dihasilkan

- Fungsi `session_dirs_from_root(run_dir) -> dict`.

---
← [Sel 14](014_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell14_05092026.md) | [Indeks](README.md) | [Sel 16](016_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell16_05092026.md) →
