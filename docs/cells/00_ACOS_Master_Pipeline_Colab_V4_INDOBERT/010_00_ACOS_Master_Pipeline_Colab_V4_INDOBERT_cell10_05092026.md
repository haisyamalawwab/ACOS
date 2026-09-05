# Sel 10 — Impor `colab_utils` yang Lengkap & Robust

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 10 dari 80 (indeks JSON `cells[9]`) |
| Tipe sel | code |
| Bagian | 2. Path Dinamis |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memilih salinan `colab_utils.py` yang memenuhi kontrak 21 simbol wajib, memasangnya di depan `sys.path`, dan mengekspor simbolnya ke global.

## Apa yang dilakukan

1. `REQUIRED_UTILS` — 21 nama (mis. `setup_timestamped_run_dir, download_bert_pretrained, analyze_and_plot_eda, plot_training_history, MarkdownReport, SubtaskMetricCapture, features_step1/2, find_resumable_session, auto_find_file`).
2. Memulihkan variabel path bila sel sebelumnya berhenti di tengah.
3. `_utils_missing_symbols(path)` — memeriksa **teks berkas** dengan regex `^(def|class)\s+NAMA\b` (bukan impor) agar aman sebelum torch terpasang.
4. Kandidat urut: `notebooks_dir, extract_dir, base_project_dir, cwd`; salinan pertama tanpa simbol hilang dipilih.
5. Bila tak ada yang lengkap → unduh dari 3 URL raw GitHub ke `<base>/_acos_utils/`, verifikasi ulang; gagal semua → `RuntimeError`.
6. `_prepend_sys_path` menaruh sumber terpilih paling depan; `sys.modules.pop('colab_utils')` lalu `importlib.import_module`.
7. Bila `ModuleNotFoundError` untuk dependensi (bukan colab_utils sendiri) → pesan agar jalankan sel instalasi dulu.
8. Validasi `hasattr` untuk 21 simbol, lalu `globals().update(...)`; cetak path aktif.

## Keluaran / variabel yang dihasilkan

- Modul `colab_utils` + 21 fungsi/kelas di namespace global.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 9 (path), sel 3 (torch terpasang karena colab_utils mengimpor torch).

---
← [Sel 09](009_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell09_05092026.md) | [Indeks](README.md) | [Sel 11](011_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell11_05092026.md) →
