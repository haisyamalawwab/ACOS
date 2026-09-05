# Sel 12 — Resolusi `indo_root`/`acos_root` & Impor Paket `acos_id`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 12 dari 80 (indeks JSON `cells[11]`) |
| Tipe sel | code |
| Bagian | 2c. Dua Root (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menemukan (atau menyinkronkan) folder `ACOS-IndoBERT`, memvalidasi 7 modul `acos_id`, mengimpornya, dan menetapkan ulang seluruh path tulis/baca.

## Apa yang dilakukan

1. `ACOS_ID_MODULES = (taxonomy, build_acos, tokenize_data, checkpoint, selftest, eda, upstream)`.
2. `_cari_indo_root()` — kandidat: `/content/drive/MyDrive/ACOS-IndoBERT`, `.../ACOS/ACOS-IndoBERT`, `.../ACOS-ASLI/ACOS-IndoBERT`, `<base>/ACOS-IndoBERT`, `./ACOS-IndoBERT`, `../ACOS-IndoBERT`, `.`; penanda satu-satunya adalah subfolder `acos_id/`.
3. Bila tidak ditemukan → `git clone --depth 1` repo `ACOS_REPO_URL`, salin `ACOS-IndoBERT/` ke target; gagal → `RuntimeError` minta unggah manual.
4. Cek setiap `acos_id/<modul>.py` ada dan tidak kosong → jika kurang, `RuntimeError` menyebut modul yang hilang.
5. `_prepend_path(indo_root)`, hapus cache `sys.modules['acos_id*']`, impor `acos_id, acos_id.taxonomy, .selftest, .checkpoint, .eda, .upstream`.
6. `extract_dir = acos_upstream.ensure_path(acos_root=base_project_dir)` — menuntut 4 berkas kunci upstream ada; `acos_root = dirname(extract_dir)`.
7. Menimpa: `save_dir = indo_root`, `data_root = indo_root/data`, `tokenized_dir = indo_root/tokenized_data`, `backbones_dir = indo_root/backbones`; membuat juga `results/` dan `build/`.
8. Mencetak versi `acos_id`, kedua root, domain Indonesia, jumlah kategori → `num_labels_step2`, label sekuens Step 1, dan daftar gate torch-free.

## Keluaran / variabel yang dihasilkan

- `indo_root, acos_root, extract_dir, save_dir, data_root, tokenized_dir, backbones_dir`; modul `acos_id, acos_taxonomy, acos_selftest, acos_ckpt, acos_eda, acos_upstream`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 9 dan 10.

## Catatan

- Paket `acos_id/` **sudah memiliki ketujuh modul** yang dituntut sel ini, termasuk `upstream.py` (`find_upstream` / `ensure_path` untuk memasang `Extract-Classify-ACOS/` ke `sys.path`). `acos_id.REQUIRED_MODULES` dan `acos_id.missing_modules()` adalah padanan pemeriksaan kelengkapan di luar notebook.
- Jalankan sekali setiap restart kernel, sama seperti 1b.

---
← [Sel 11](011_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell11_05092026.md) | [Indeks](README.md) | [Sel 13](013_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell13_05092026.md) →
