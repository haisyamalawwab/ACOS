# Sel 28 — Audit Struktur Folder Drive/Dataset/Cache/Sesi

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 28 dari 80 (indeks JSON `cells[27]`) |
| Tipe sel | code |
| Bagian | 4b. Diagnostik Drive |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memanggil `inspect_acos_drive_structure(base_project_dir=base_project_dir, domain=DOMAIN, verbose=True)` untuk mencetak peta folder dan mendeteksi salah simpan/salah muat.

## Keluaran / variabel yang dihasilkan

- `drive_audit_report` (dict laporan).

## Catatan

- Fungsi ini memeriksa `base_project_dir` (root ASLI), bukan `indo_root` — di V4 hasilnya bersifat informatif untuk sisi upstream.

---
← [Sel 27](027_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell27_05092026.md) | [Indeks](README.md) | [Sel 29](029_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell29_05092026.md) →
