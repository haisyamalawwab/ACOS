# Sel 07 — Definisi `step_stage`, `require_vars`, Patch Metrik & Helper Tabel

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 7 dari 80 (indeks JSON `cells[6]`) |
| Tipe sel | code |
| Bagian | 1b. Pelacak Progres |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Sel fondasi: mendefinisikan kelas/fungsi utilitas yang menjadi tulang punggung pola eksekusi bertahap V2/V4.

## Apa yang dilakukan

1. `class step_stage` — context manager: mencetak judul (`▶️`), langkah bernomor `[n/total]` dengan detik berjalan lewat `.step(msg)`, catatan `.note(msg)`, dan durasi total (`✅`/`❌`) saat keluar. Exception tetap dilempar (`return False`).
2. `require_vars(*names)` — melempar `RuntimeError` bila variabel prasyarat belum ada di `globals()`.
3. `write_stage_progress(path, **fields)` — menulis JSON progres + `updated_at` yang bertahan meski runtime terputus.
4. `METRIC_COUNT_COLS = ('tp','fp','fn')`, `METRIC_RATE_COLS = ('precision','recall','micro-F1','f1')`.
5. `patch_eval_metrics_counts()` — monkey-patch modul `eval_metrics`: `measureQuad` dan `measureQuad_imp` ditulis ulang agar mengembalikan dict berisi precision/recall/micro-F1 **plus tp/fp/fn**; memperbaiki bug upstream (return di luar loop pada `measureQuad_imp`, KeyError pada teks yang tidak ada di `text_type` → `text_type.get(text,[4])`); menyimpan rincian per slot difficulty di `_em.LAST_DIFFICULTY_BREAKDOWN`; idempoten lewat flag `_ACOS_COUNTS_PATCHED`.
6. `history_display_frame(history)` — riwayat per epoch → DataFrame dengan kolom TP/FP/FN mentah dan Precision_%/Recall_%/Micro_F1_% (dikali 100 bila skala ≤ 1).
7. `metrics_display_frame(res)` — satu dict metrik → tabel dua jenis ('hitungan' vs 'laju').
8. `best_epoch_row(history)` — baris epoch terbaik menurut `micro-F1`, toleran terhadap riwayat lama berskala persen.

## Keluaran / variabel yang dihasilkan

- Fungsi/kelas global: `step_stage, require_vars, write_stage_progress, patch_eval_metrics_counts, history_display_frame, metrics_display_frame, best_epoch_row`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 4 (`pd`, `json`, `datetime`).

## Catatan

- Wajib dijalankan ulang setiap restart kernel — hampir semua sel tahap memanggil `require_vars('step_stage', ...)`.

---
← [Sel 06](006_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell06_05092026.md) | [Indeks](README.md) | [Sel 08](008_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell08_05092026.md) →
