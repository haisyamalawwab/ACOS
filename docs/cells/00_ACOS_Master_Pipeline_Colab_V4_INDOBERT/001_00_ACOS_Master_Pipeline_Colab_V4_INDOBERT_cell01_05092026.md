# Sel 01 — Judul & Gambaran Umum Notebook (V2 → V4 IndoBERT)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 1 dari 80 (indeks JSON `cells[0]`) |
| Tipe sel | markdown |
| Bagian | 0. Pembuka |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Sel pembuka yang menjelaskan tujuan notebook: eksekusi end-to-end pipeline ACOS (Aspect-Category-Opinion-Sentiment quadruple extraction) dengan satu klik di Google Colab atau lokal, kini dengan backbone **IndoBERT** dan dataset Indonesia **Apps-ACOS**.

## Apa yang dilakukan

1. Mendaftar 11 kapabilitas notebook: setup & diagnostik GPU, arsitektur path dinamis, caching BERT offline, EDA 300 DPI, Step 1 BERT-CRF, smart state checkpoint, jembatan pasangan kandidat, Step 2 category-sentiment, dashboard 15 sub-task, manifest MCP, dan inferensi interaktif.
2. Bagian **Versi V2** menjelaskan pola eksekusi bertahap: tabel pemetaan tahap → sel (1b, 5a-5f, 7a-7b, 8a-8f, 9a-9b), log progres per epoch ke `logs/step*_progress.json`, dan patch `patch_eval_metrics_counts()` agar TP/FP/FN ikut tersimpan.
3. Bagian **Versi V4** menampilkan tabel perbedaan V2 vs V4: backbone `bert-base-uncased` → `indobenchmark/indobert-base-p1`, domain `rest16/laptop` → `appsid`, 13 kategori datar (mis. `AUTH_ACCESS`), `num_labels` Step 2 tetap 39, sumber data `data/Apps-ACOS/processed/`, folder sesi `results/appsid_/`.
4. Tabel sel baru dibanding V2: sinkronisasi paket `acos_id/` (disebut '1s', pada notebook ini muncul sebagai sel 2c), 4c adapter checkpoint IndoBERT, 4d gerbang data, 5d2 Gate 1 bobot encoder.
5. Menjelaskan dua kegagalan senyap yang dijaga: (1) key checkpoint IndoBERT tanpa prefiks `bert.` sehingga loader legacy (`modeling.py:745`, `start_prefix=''`) mengabaikan seluruh encoder → training dengan encoder acak; (2) `get_labels()` upstream hanya mengenal `rest*`/`laptop` sehingga domain lain menghasilkan daftar kategori `None`.

## Catatan

- Sel ini murni dokumentasi; tidak ada eksekusi.
- Penamaan '1s' di tabel tidak konsisten dengan heading aktual '2c. Dua Root & Paket acos_id/' — isinya sama.

---
[Indeks](README.md) | [Sel 02](002_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell02_05092026.md) →
