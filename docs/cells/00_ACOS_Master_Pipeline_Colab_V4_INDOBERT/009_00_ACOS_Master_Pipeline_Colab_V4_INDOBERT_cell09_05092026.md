# Sel 09 — Deteksi Root Proyek (Drive / Colab / Lokal) & Auto-Clone Repo

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 9 dari 80 (indeks JSON `cells[8]`) |
| Tipe sel | code |
| Bagian | 2. Path Dinamis |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menentukan `base_project_dir` secara dinamis dan memastikan folder inti repo (`Extract-Classify-ACOS`, `absa5`) tersedia.

## Apa yang dilakukan

1. `IS_COLAB` (modul `google.colab` atau `/content` ada) dan `HAS_DRIVE` (`/content/drive/MyDrive` ada).
2. Kandidat Drive: `/content/drive/MyDrive/ACOS`, `.../ACOS-ASLI`, plus semua subfolder MyDrive yang namanya memuat 'acos'.
3. Prioritas: (1) kandidat Drive yang punya `Extract-Classify-ACOS/` atau `data/`; (2) `/content/ACOS` (Colab ephemeral); (3) `./Extract-Classify-ACOS`; (4) `../Extract-Classify-ACOS`; (5) fallback buat folder `ACOS/` baru.
4. Menetapkan `save_dir = <base>/Output` dan membuat foldernya.
5. Bila `extract_dir` atau `absa5_dir` belum ada → `git clone https://github.com/haisyamalawwab/ACOS.git /tmp/ACOS_clone` lalu `cp -r` ke base.
6. Menetapkan `data_root = <base>/data` dan `notebooks_dir = <base>/notebooks`.

## Keluaran / variabel yang dihasilkan

- `base_project_dir, save_dir, extract_dir, absa5_dir, data_root, notebooks_dir`.

## Catatan

- Nilai `save_dir`, `data_root`, `extract_dir` akan **ditimpa lagi** oleh sel 12 (Dua Root) untuk jalur Indonesia.

---
← [Sel 08](008_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell08_05092026.md) | [Indeks](README.md) | [Sel 10](010_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell10_05092026.md) →
