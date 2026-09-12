# 033 — Studi Perbandingan: ACOS-BERT (Baseline rest16) vs. ACOS-IndoBERT (Apps-ACOS)

> Tanggal: 12 September 2026
> Status: **analisis statis** — tidak ada pelatihan baru; seluruh angka dikutip dari artefak yang ada
> Metode: inspeksi output notebook V4/V4_1 + reports 023/025/027/028/030/031 + verifikasi berkas lokal (`_build_report_appsid.json`, `eda_dataset_statistics.csv`)

---

## 1. Putusan di depan (TL;DR)

Perbandingan langsung **tidak valid secara apples-to-apples**. Satu-satunya metrik BERT yang ada (Step-1 81,23% rest16, A100) dan metrik IndoBERT (Step-1 97,94% + Step-2 67,86% ep-1 appsid, T4) berasal dari dataset, bahasa, domain, granularitas input, dan kualitas label yang **semuanya berbeda**. Gap 16,7 poin di Step-1 dijelaskan oleh karakteristik dataset (klausa pendek +8–10, data 29× +5–7, domain +2–3), dengan kontribusi backbone **~0** — estimasi analitis (rep. 030 §5.2), bukan ablasi terukur. Klaim "IndoBERT lebih baik dari BERT" **ditolak** di dokumen ini.

---

## 2. Matriks perbandingan penuh

### Tabel 1 — Dataset dan input

| Dimensi | ACOS-BERT (baseline) | ACOS-IndoBERT (penelitian ini) |
|---|---|---|
| Dataset | rest16 (Restaurant-ACOS, SemEval-2016 + anotasi manual) | appsid (Apps-ACOS, 43.673 ulasan 13 aplikasi bank digital) |
| Bahasa / domain | Inggris / restoran | Indonesia / bank digital |
| Unit input | Kalimat penuh | Klausa (1 baris = 1 klausa; 80.260 klausa, 4.183 dibuang) |
| Train / dev / test | 1.530 kal / 2.484 quad; 171 / 261; 583 / 916 | 60.159 kl / 72.973 quad; 8.027 / 9.587; 7.891 / 9.514 |
| Rasio train:test (quad) | 2,7 : 1 | 7,7 : 1 |
| Kategori | 13 (`ENTITY#ATTRIBUTE`) | 13 (datar, tanpa `#`) |
| Kualitas label | Manual (gold) | Lemah otomatis (floor 0,3, saturation 2,0) |
| Implisit | Rendah (manual) | Aspek 30,1% / opini 40,5% (deteksi otomatis, Tabel V di 032) |
| Sentimen | Tak terdokumentasi | Neg 49,8 / net 11,3 / pos 38,9% (total 92.074 tuple) |

Sumber: rep. 030 §2–3; rep. 023 §2–3, §6; `_build_report_appsid.json`; `eda_dataset_statistics.csv`.

### Tabel 2 — Arsitektur

| Komponen | ACOS-BERT | ACOS-IndoBERT |
|---|---|---|
| Backbone | `bert-base-uncased` (~110M) | `indobert-base-p1` (~124M; +14M hanya embedding) |
| Encoder | 12L / 768H / 12H / pos 512 | **identik** |
| Vocab (config / aktual) | 30.522 / 30.522 | 50.000 / 30.521 |
| Prefix `bert.` | Ada (aman) | Hilang → rekey + Gate-1 numerik (belum dijalankan) |
| Step-1 | `BertForQuadABSA` (BERT-CRF 6-tag + 2 head implisit) | Sama |
| Step-2 | Single-head Linear(1536,39), BCE gabungan | Dual-head Linear(1536,13) BCE + Linear(1536,3) CE + fused-39 (Fig.7 di 032: 59.943 vs. 24.592 param) |
| Bridge | Cartesian pairs, parsing manual (`ele[2:]`) | + 2 aturan grouping (kunci mencakup teks; order per-label) |

Sumber: rep. 025; rep. 027/028; rep. 023 §2, §4–5.

### Tabel 3 — Dinamika training Step-1

| Aspek | ACOS-BERT (A100) | ACOS-IndoBERT (T4 14,46 GB) |
|---|---|---|
| Epoch selesai | 15/15 | 8/15 (terhenti; resume level-3 tersedia) |
| Riwayat per-epoch | Tidak tersimpan (hanya best) | Lengkap 8 baris (Tabel III di 032; Fig.3) |
| Best Micro-F1 | **81,23%** (ep-6) | **97,94%** (ep-8; P 97,44 R 98,46; loss 0,0999) |
| Pola | Tak diketahui (tanpa kurva) | 95,03% sejak ep-1; +0,31 ep-4→8 (plateau); FN −62% |

Sumber primer IndoBERT: `V4_1_02_step1_train.ipynb` sel 20 (sesi `appsid_08092026_150437`) → `csv/master_03_step1_riwayat.csv`. Sumber BERT: output notebook baseline (rep. 004/030).

### Tabel 4 — Step-2 dan hasil akhir

| Aspek | ACOS-BERT | ACOS-IndoBERT |
|---|---|---|
| Epoch selesai | 0 (crash `KeyError: 'a--1,-1'`) | 1/15 |
| Quadruple F1 | — (tak tersedia) | **67,86%** (P 62,74 R 73,88; loss 0,5544; lower bound) |
| Category-F1 / Sentiment-acc | N/A (single-head) | 0,00% (bug side-effect, rep. 030 §4.2) |
| 15 subtask | — | Lengkap (Tabel IV di 032; Fig.4): 1-el 91,89 → 4-el 66,28; bottleneck sentimen 84,97% |

Sumber primer: `V4_1_04_eval_inference.ipynb` sel 6–10 → `csv/master_06_step2_riwayat.csv`, `csv/master_08_metrik_subtask.csv`, `logs/master_metrics.json`.

---

## 3. Gambar perbandingan

- **Fig.1 (konsep):** `reports/img_diagram_bert_vs_indobert.png` — alur baseline vs. penelitian ujung-ke-ujung.
- **Fig.8:** `reports/fig8_compare_step1.png` — 81,23% vs. 97,94% **dengan 5 confounder tertulis di badan gambar** (ukuran data, unit input, bahasa/domain, kualitas label, status Step-2). Gambar ini sengaja tidak bisa dibaca sebagai kemenangan model.
- **Fig.9:** `reports/fig9_gap_decomposition.png` — dekomposisi gap 16,7 poin menjadi +9,0 (klausa) +6,0 (data) +2,5 (domain) +0,0 (backbone) = ~17,5 vs. 16,7 teramati. **Estimasi analitis (rep. 030 §5.2), bukan ablasi terukur** — ditulis di badan gambar.

---

## 4. Cerita perbandingan (narasi)

**Babak 1 — Start yang tak seimbang.** BERT bertarung di rezim low-resource (2.484 quadruple, kalimat naratif restoran, gold manual) dan gugur di Step-2 karena parser rapuh — bahkan skor akhirnya pun tak ada. IndoBERT bertarung di rezim data-abundant (72.973 quadruple, klausa pendek formulaik, label lemah) dengan 6 gate dan resume per-epoch. Membandingkan skor keduanya seperti membandingkan pelari maraton dan pelari 100 m lewat catatan waktu mentah.

**Babak 2 — Mengapa 97,94% bukan prestasi backbone.** Encoder keduanya kembar (Tabel 2). Yang membuat span mudah ditemukan: klausa 5–10 token (ruang span kecil), 60 ribu contoh per epoch (generalisasi), opini seperti "bagus"/"error terus" (tanpa negasi kompleks). Dekomposisi Fig.9 menaruh backbone di angka nol — dengan sadar, agar pembaca tak tergoda.

**Babak 3 — Yang benar-benar beda: Step-2.** Di sinilah penelitian ini melampaui baseline secara struktural, bukan numerik: dual-head memisahkan apa yang selama ini digabung, 2,4× lebih kecil, dan kompatibel mundur via fused-39. Ironisnya hadiahnya langsung berupa bug yang terlihat (metrik 0,00%) — justru bukti instrumentasi bekerja.

**Babak 4 — Harga yang belum dibayar.** Tiga utang sebelum perbandingan sah: Gate-1 (apakah encoder benar-benar IndoBERT?), 14 epoch tersisa Step-2, dan kontrol cross-lingual (IndoBERT di rest16 Inggris — ekspektasi: kalah dari BERT karena vocab — sebagai batas atas efek backbone).

---

## 5. Kesimpulan studi

1. Tidak ada dasar untuk menyatakan salah satu backbone lebih baik; pertanyaan itu belum terjawab dan dokumen ini menjelaskan syarat menjawabnya.
2. Keunggulan IndoBERT-V4 yang sah diklaim: dataset + infrastruktur verifikasi + dual-head + diagnosis bottleneck — semuanya berbasis artefak terverifikasi di atas.
3. Rekomendasi berurutan: Gate-1 → 15 epoch + bugfix metrik → kontrol rest16-IndoBERT → gold manusia + uji signifikansi.

---

## Apendiks — Jejak sumber tiap angka

| Angka | Sumber primer |
|---|---|
| 81,23% (BERT Step-1) | output notebook baseline via rep. 004/030 |
| 97,94% + riwayat 8 epoch | `V4_1_02_step1_train.ipynb` sel 20 → `master_03_step1_riwayat.csv` |
| 67,86% + TP/FP/FN | `V4_1_04_eval_inference.ipynb` sel 6–10 → `master_06_step2_riwayat.csv`, `master_metrics.json` |
| 15 subtask | sel 10 → `master_08_metrik_subtask.csv` |
| Split/quad/UNK/span | `_build_report_appsid.json` (`span_invalid: 0`, `unk: 0`); `_build_acos_report.json` (dibuang 4.183) |
| Sentimen/implisit | `build/_eda_id/csv/eda_dataset_statistics.csv` (dihitung ulang, cocok) |
| Dekomposisi gap | estimasi analitis rep. 030 §5.2 (bukan hasil ukur) |
