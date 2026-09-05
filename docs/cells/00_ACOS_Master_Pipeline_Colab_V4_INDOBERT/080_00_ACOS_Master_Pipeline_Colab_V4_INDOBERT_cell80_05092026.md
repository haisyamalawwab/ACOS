# Sel 80 — Audit Akhir Artefak Sesi (Drive/Lokal)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 80 dari 80 (indeks JSON `cells[79]`) |
| Tipe sel | code |
| Bagian | 11. Audit Artefak |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menelusuri semua subfolder sesi dan mencetak inventaris berkas beserta ukurannya.

## Apa yang dilakukan

1. Cetak lokasi sesi dan status persistensi (`/content/drive/MyDrive` di path → 'TERSIMPAN DI DRIVE', selain itu 'LOKAL / EPHEMERAL').
2. `os.walk` pada setiap `session_dirs[sub]` (kecuali root) → kumpulkan `Subfolder, File, Size (KB/MB), Path`.
3. `df_audit` → cetak per subfolder (`[CHECKPOINTS]`, `[CSV]`, `[LOGS]`, `[MD]`, `[PLOTS]`, ...), atau peringatan bila kosong.

## Keluaran / variabel yang dihasilkan

- `df_audit`, keluaran teks inventaris.

## Prasyarat (sel yang harus sudah berjalan)

- `session_dirs`.

---
← [Sel 79](079_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell79_05092026.md) | [Indeks](README.md)
