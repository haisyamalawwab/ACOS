# Sel 37 — 5b. Deteksi Cache Step 1 (Sesi Aktif → Sesi Lama)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 37 dari 80 (indeks JSON `cells[36]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memutuskan apakah Step 1 perlu dilatih, dengan menarik checkpoint sesi lama bila ada.

## Apa yang dilakukan

1. `step1_already_done = exists(step1_bin) and exists(pred_file)`; laporkan ukuran model & jumlah baris prediksi.
2. Bila belum: `auto_find_file('pytorch_model.bin', must_contain='step1_best', search_roots=[results_base, Drive ACOS/Output/results, base/Output/results])`; salin `pytorch_model.bin, config.json, vocab.txt` ke `step1_ckpt`; salin juga `pred4pipeline.txt` dan `step1_training_history.csv` bila ditemukan.
3. `STEP1_SKIP_TRAINING = (not FORCE_RETRAIN_STEP1) and step1_already_done`.
4. Saat cache hit: muat `step1_history` dari CSV, `best_epoch_row` → `best_step1_f1`, `best1_epoch`; peringatan bila riwayat < `NUM_EPOCHS` (run terhenti).
5. Tanpa CSV: `step1_history=[]`, `best_step1_f1=0.0`, `best1_epoch=NUM_EPOCHS`.

## Keluaran / variabel yang dihasilkan

- `STEP1_SKIP_TRAINING, step1_history, best_step1_f1, best1_epoch`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 35 (5a).

---
← [Sel 36](036_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell36_05092026.md) | [Indeks](README.md) | [Sel 38](038_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell38_05092026.md) →
