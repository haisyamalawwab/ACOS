# 046 — Verifikasi Bukti untuk Jalur A (Empat Blocker Pra-Submit)

**Tanggal:** 02/11/2026
**Metode:** pembacaan kode notebook dan keluaran tersimpan (`execution_count`), tanpa menjalankan ulang sel.
**Sasaran:** memastikan setiap butir pada "Jalur A" punya bukti yang dapat ditunjuk — berkas, sel, dan baris.

> **Putusan satu baris:** tiga klaim terbukti kuat dan dapat ditunjuk sampai nomor baris; **satu klaim salah besarnya** ("1–3 poin") dan harus diganti dengan **0,4–0,6 poin** yang terukur, sementara dua angka turunannya tidak punya dasar dan dihapus.

---

## 1. Hasil verifikasi per klaim

| # | Klaim | Bukti | Status |
|---|---|---|---|
| 1 | `02` memilih checkpoint dengan mengevaluasi **test set** setiap epoch | `notebooks/02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb` sel 7 (ec=5) memanggil `processor.get_dev_examples(data_dir, DOMAIN)`; fungsi itu membaca `tokenized_data/{domain}_test_quad_bert.tsv` — `Extract-Classify-ACOS/run_classifier_dataset_utils.py:151–156`. Sel 11 (ec=7) memanggil `pred_eval(..., eval_type="test")` lalu `if val_f1 > best_val_f1: torch.save(...)` | **terbukti** |
| 2 | `04` memakai pola yang sama | Sel 6 (ec=3) memanggil `resolve_eval_pair_file(...)`; fungsi itu mengembalikan `{domain}_test_pair_1st.tsv` atau `{domain}_test_pair.tsv` — `Extract-Classify-ACOS/colab_utils.py:1178–1192`. Sel 10 (ec=5) `pair_eval(..., eval_type="test")` + simpan saat naik | **terbukti** |
| 3 | Angka 81,27% berasal dari seleksi tersebut | `02` sel 11 (ec=7) mencetak deret 15 epoch dan `Epoch terbaik: 8 (micro-F1 81.27%)`; sel 13 (ec=8) memuat `step1_best` → `micro-F1: 81.27%` | **terbukti** |
| 4 | Angka 48,24% berasal dari seleksi tersebut | `04` sel 10 (ec=5) `Epoch terbaik: 12 (micro-F1 48.24%)`; sel 12 (ec=6) `micro-F1: 48.24%` + 15 sub-task | **terbukti** |
| 5 | Dev tersedia tetapi tidak dipakai | `data/Restaurant-ACOS/rest16_quad_dev.tsv` (171 baris), `Extract-Classify-ACOS/tokenized_data/rest16_dev_quad_bert.tsv`, `rest16_dev_pair.tsv` | **terbukti** |
| 6 | Praktik ini menggelembungkan hasil **1–3 poin** | Tidak ada sumber. Pengukuran dari keluaran: Step-1 maksimum 81,27 vs epoch terakhir 80,71 → **0,56 poin**; Step-2 maksimum 48,24 vs 48,17 → **0,07 poin** | **salah besarnya** |
| 7 | Angka terkoreksi: 64–67% appsid, 45–48% rest16, 78–81% tahap 1 | Turunan dari klaim #6; tidak ada pengukuran | **tanpa dasar** |
| 8 | Abstrak `035` masih memuat 97,94% dan 67,86% | `reports/035_...` baris 21 (abstrak), 248, 304, 327, 360 (97,94%); baris 21, 258, 260, 368 (67,86%) | **terbukti** |
| 9 | 24 rujukan `045` belum ber-DOI | 24 entri `[n]`; kata "DOI" hanya muncul 1 kali, yaitu pada Lampiran B | **terbukti** |
| 10 | Metadata penulis masih placeholder | `045` baris 5–8 (`[Nama Penulis Kedua]`, `[Afiliasi ...]`, `[email@institusi.ac.id]`) | **terbukti** |

---

## 2. Bukti kuantitatif untuk klaim #6

Deret F1 per epoch dari keluaran yang tersimpan:

| Run | Deret F1 (15 epoch) | Maks | Epoch terakhir | Selisih maks − terakhir | Plateau (ep 6–15 / 7–15) |
|---|---|---:|---:|---:|---:|
| `02` Step-1 rest16 | 50,82 · 76,40 · 78,88 · 80,50 · 80,44 · 81,14 · 80,62 · **81,27** · 81,02 · 80,19 · 80,76 · 80,80 · 80,46 · 80,96 · 80,71 | 81,27 (ep 8) | 80,71 | **0,56** | 80,83 (selisih 0,44) |
| `04` Step-2 rest16 | 0,00 · 39,07 · 44,41 · 42,86 · 46,60 · 46,09 · 47,44 · 47,09 · 48,10 · 47,99 · 47,90 · **48,24** · 48,05 · 48,12 · 48,17 | 48,24 (ep 12) | 48,17 | **0,07** | 47,86 (selisih 0,38) |

Kesimpulan yang sah: pada dua run ini, memilih maksimum alih-alih epoch terakhir menaikkan F1 sebesar **0,07–0,56 poin** (0,38–0,44 poin bila dibandingkan dengan rata-rata plateau). Klaim "1–3 poin" tidak didukung dan terlalu besar.

---

## 3. Yang belum dapat diklaim

| # | Hal | Alasan |
|---|---|---|
| 1 | Bias **lintas-run** (memilih run terbaik dari banyak run berdasarkan test) | Jumlah run dan korelasinya tidak terukur; hanya bisa diukur bila protokol dev diterapkan lalu dibandingkan |
| 2 | Sebaran epoch untuk 67,69% (appsid) | Angka berasal dari artefak Drive; deret 15 epoch tidak ada di repositori |
| 3 | Efek perbaikan T03 terhadap angka final | Belum dijalankan ulang; hanya dapat diketahui setelah eksekusi dengan `eval_type="dev"` |

---

## 4. Koreksi yang diterapkan

| ID | Berkas | Tindakan |
|---|---|---|
| K-01 | `reports/045` abstrak ID & EN | "1–3 poin" → "0,4–0,6 poin (terukur pada run yang tersedia)" + pernyataan bias lintas-run tidak terukur |
| K-02 | `reports/045` §5.1 | Menghapus rentang turunan 64–67% / 45–48% / 78–81%, menggantinya dengan angka terukur |
| K-03 | `reports/045` Tabel 8 | Sel "estimasi 1–3 poin" → "0,4–0,6 poin (terukur)" |
| K-04 | `reports/042` §14 catatan T03 | Menambahkan paragraf koreksi angka dan rujukan ke laporan ini |

---

## 5. Yang tidak berubah

T03 tetap pekerjaan prioritas **P0**, tetapi alasannya bergeser dari "angka turun 1–3 poin" menjadi "protokolnya keliru meski dampak terukurnya kecil". Alasan yang tetap berdiri:

1. Test set dipakai untuk pemilihan model — pelanggaran protokol, apa pun besarnya dampak.
2. Dengan uji kecil (rest16: 583 kalimat, 895 kuadruple), varians antar-run besar, sehingga memilih maksimum dari banyak run berisiko memilih titik yang beruntung; risiko ini tidak terukur dari data yang ada.
3. Perbaikan bersifat satu baris per notebook dan menghapus seluruh perdebatan saat review.
