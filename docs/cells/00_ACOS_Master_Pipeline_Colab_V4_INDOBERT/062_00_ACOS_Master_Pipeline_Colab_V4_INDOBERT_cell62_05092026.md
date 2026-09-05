# Sel 62 — 8b. Deteksi Cache Step 2 (Sesi Aktif → Sesi Lama)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 62 dari 80 (indeks JSON `cells[61]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memutuskan apakah Step 2 dilatih; menarik checkpoint `step2_best` dari sesi lain bila ada.

## Apa yang dilakukan

1. `step2_already_done = exists(step2_bin)`.
2. Bila belum: `auto_find_file('pytorch_model.bin', must_contain='step2_best', ...)`; salin bin/config/vocab dan `step2_training_history.csv`.
3. `STEP2_SKIP_TRAINING = (not FORCE_RETRAIN_STEP2) and step2_already_done`.
4. Cache hit: muat `step2_history` dari CSV; `best_epoch_row` → `best_step2_f1, best2_epoch`; tandai apakah kolom tp/fp/fn tersedia; peringatan bila riwayat tidak penuh.

## Keluaran / variabel yang dihasilkan

- `STEP2_SKIP_TRAINING, step2_history, best_step2_f1, best2_epoch`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 60 (8a).

---
← [Sel 61](061_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell61_05092026.md) | [Indeks](README.md) | [Sel 63](063_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell63_05092026.md) →
