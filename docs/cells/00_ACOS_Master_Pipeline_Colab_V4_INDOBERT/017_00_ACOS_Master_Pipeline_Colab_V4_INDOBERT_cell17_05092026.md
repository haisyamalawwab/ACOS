# Sel 17 — Resume/Buat Sesi, Verifikasi Izin Simpan & Path Backbone

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 17 dari 80 (indeks JSON `cells[16]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memilih sesi yang dilanjutkan (atau membuat sesi bertimestamp baru) dan menetapkan `bert_cache_dir` per backbone.

## Apa yang dilakukan

1. `candidate_result_roots` — hanya di bawah `indo_root` (+ path Drive `ACOS-IndoBERT/results` varian) agar sesi Inggris dengan vocab berbeda tidak ikut terpilih.
2. `find_resumable_session(candidate_result_roots, DOMAIN)` bila `RESUME_LAST_SESSION` → `session_dirs_from_root(...)`; jika tidak → `setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)`.
3. `verify_session_save_paths(session_dirs, domain=DOMAIN)` — cek integritas & izin tulis.
4. `bert_cache_dir = backbones_dir/<_backbone_dirname(BACKBONE)>`; untuk `bert-en` panggil `download_bert_pretrained`; untuk IndoBERT hanya laporkan berapa dari 3 berkas (`config.json, pytorch_model.bin, vocab.txt`) ada — unduh & rekey dilakukan di sel 4c.
5. Alias: `plots_dir, csv_dir, md_dir, logs_dir`.

## Keluaran / variabel yang dihasilkan

- `session_dirs, bert_cache_dir, plots_dir, csv_dir, md_dir, logs_dir`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 14–16, `colab_utils`.

## Catatan

- Jangan pakai `download_bert_pretrained` untuk IndoBERT — fungsi itu selalu mengunduh bert-base-uncased.

---
← [Sel 16](016_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell16_05092026.md) | [Indeks](README.md) | [Sel 18](018_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell18_05092026.md) →
