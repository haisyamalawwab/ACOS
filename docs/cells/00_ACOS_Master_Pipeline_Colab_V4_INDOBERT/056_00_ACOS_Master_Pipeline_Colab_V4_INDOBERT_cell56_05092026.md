# Sel 56 — 7a. Pembentukan / Pemuatan Pasangan Kandidat

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 56 dari 80 (indeks JSON `cells[55]`) |
| Tipe sel | code |
| Bagian | 7. Jembatan Pasangan |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menghasilkan berkas input Step 2 `{DOMAIN}_test_pair_1st.tsv` dari prediksi Step 1, dengan cache memori/disk.

## Apa yang dilakukan

1. `ensure_objects()`, `require_vars('step_stage','session_dirs','extract_dir')`.
2. Path: `pred_file = logs/pred4pipeline.txt`, `target_tokenized_tsv = tokenized_base/tokenized_data/{DOMAIN}_test_pair_1st.tsv`, `candidate_csv = csv/candidate_pairs_summary.csv`.
3. Cache: `df_pairs` di memori + TSV ada → hit; CSV + TSV ada → muat CSV.
4. Jika `pred_file` tidak ada → `auto_find_file('pred4pipeline.txt')` dan salin; gagal → `FileNotFoundError` (jalankan 5a–5f).
5. `TAG_RE = ^(a|o)-(-?\d+,-?\d+)$`; token yang cocok masuk `asp`/`opi`, sisanya teks; baris tanpa teks dilewati (`n_skip`).
6. Bila aspek/opini kosong → tambahkan `-1,-1` (implicit). Tulis `text####pa po` untuk setiap kombinasi; kumpulkan `pair_records`.
7. `df_pairs` → simpan `candidate_pairs_summary.csv`; laporkan jumlah pasangan.

## Keluaran / variabel yang dihasilkan

- `tokenized_data/{DOMAIN}_test_pair_1st.tsv`, `csv/candidate_pairs_summary.csv`, `df_pairs`.

## Prasyarat (sel yang harus sudah berjalan)

- Step 1 selesai (`pred4pipeline.txt`).

---
← [Sel 55](055_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell55_05092026.md) | [Indeks](README.md) | [Sel 57](057_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell57_05092026.md) →
