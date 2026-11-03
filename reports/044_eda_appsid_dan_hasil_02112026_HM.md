# 044 — EDA Apps-ACOS: Data Sumber, Data Hasil, dan Wordcloud per Komponen ACOS

**Tanggal:** 02/11/2026
**Penulis:** HM
**Branch:** `arena/461c288a-acos`
**Skrip:** `scripts/eda_044_appsid.py` (stdlib murni), `scripts/fig21_eda_appsid.py`, `scripts/fig22_wordcloud_acos.py`
**Artefak data:** `reports/044_data/` (9 berkas CSV/JSON)
**Gambar:** `fig21` (EDA sumber), `fig22` (wordcloud A/C/O/S), `fig23` (wordcloud per polaritas)
**Rujukan:** [`042`](042_kesiapan_publikasi_q2_s2_02112026_HM.md), [`043`](043_visualisasi_tiga_gambar_acos_02112026_HM.md), [`023`](023_pipeline_acos_indobert_dataset_indonesia_04092026.md), [`035`](035_Artikel_Revisi_ACOS_IndoBERT_12092026.md)

> **Putusan satu baris:** EDA berjalan penuh (43.673 ulasan sumber, 92.074 tuple hasil, 76.077 klausa), tetapi **angka andalan 61,5% / 48,0% tidak dapat direplikasi** dari artefak yang ada — 10 kombinasi definisi tokenisasi dicoba, tidak satu pun mendekat — sementara **37,6% justru tereproduksi persis** dan terbukti merupakan artefak `str.split()`, bukan sifat data; konsekuensinya Gambar 2 dan Gambar 3 (PR #6) saat ini memvisualkan angka yang **tidak lolos uji**.

---

## 1. Lingkup dan metode

| Aspek | Keterangan |
|---|---|
| Data sumber | `ACOS-IndoBERT/data/Apps-ACOS/processed/reviews_clean.csv` (43.673 ulasan), `reviews_labeled.csv`, `quintuples_weak.csv` (96.417 baris tuple pra-split) |
| Data hasil | `appsid_quad_{train,dev,test}.tsv` — format yang benar-benar dibaca model; artefak pendukung `_build_report_appsid.json`, `_build_acos_report.json` |
| Tokenisasi | dua definisi diuji berdampingan: `str.split()` dan `\w+` + `[^\w\s]` (kata **atau** tanda baca sebagai token) |
| Wordcloud | `wordcloud 1.9.6`, frekuensi dari hitungan sendiri (bukan teks mentah), `random_state=42`, hanya istilah satu kata (frasa multi-kata memicu tabrakan tata letak pada pustaka ini) |
| Tingkat bukti | seluruh angka di §2–§5 = **E2** (dihitung ulang di sesi ini oleh skrip stdlib); angka yang dikutip dari artefak JSON = **E1** |
| Larangan yang dipatuhi | tidak menjalankan sel notebook, tidak mengunduh data/bobot, tidak menulis ke direktori data |

Waktu eksekusi: `eda_044_appsid.py` ≈ 5,1 detik untuk 43.673 ulasan + 96.417 tuple + 76.077 baris hasil.

---

## 2. EDA data sumber (43.673 ulasan, 13 aplikasi)

**Gambar 21** — `reports/fig21_eda_sumber_appsid.png`: distribusi rating, panjang ulasan, volume per tahun, sebaran per aplikasi.

### 2.1 Dimensi dasar

| Metrik | Nilai | Catatan |
|---|---|---|
| Ulasan | 43.673 | seluruh `review_id` unik (0 duplikat id) |
| Aplikasi | 13 bank digital | rentang 2.514–4.202 ulasan per aplikasi |
| Platform | Google Play 37.825 (86,61%), App Store 5.848 (13,39%) | timpang 6,5 : 1 |
| Kata per ulasan | median 15 · rerata 20,26 · p95 59 · maks 307 · min 3 | ekor panjang tipis (1.010 ulasan ≥ 60 kata) |
| Ulasan dengan emoji | 3.524 (8,07%) · 6.748 emoji | emoji tidak dipakai sebagai fitur — potensi sinyal terbuang |
| Duplikat teks (`text_norm` identik) | 455 (1,04%) | belum dideduplikasi |

### 2.2 Distribusi rating dan polaritas

| Rating | Jumlah | Pangsa | Polaritas turunan |
|---|---|---|---|
| 1 | 12.266 | 28,09% | negatif 18.818 (43,09%) |
| 2 | 6.552 | 15,00% | — |
| 3 | 6.386 | 14,62% | netral 6.386 (14,62%) |
| 4 | 5.248 | 12,02% | positif 18.469 (42,29%) |
| 5 | 13.221 | 30,27% | — |

Distribusi **bimodal**, bukan normal: 43,09% negatif dan 42,29% positif dengan lembah di bintang 4 (12,02%). Konsekuensi praktis: akurasi mentah tidak bermakna, F1 makro wajib dilaporkan, dan kelas bintang 4 adalah kelas paling rentan salah label.

### 2.3 Sebaran waktu dan aplikasi

| Tahun | Ulasan | Pangsa |
|---|---|---|
| ≤ 2023 | 3.836 | 8,78% |
| 2024 | 3.329 | 7,62% |
| 2025 | 9.447 | 21,63% |
| 2026 | 27.061 | 61,96% |

**61,96% ulasan berasal dari tahun 2026.** Ini bukan sampel historis yang merata: temuan tentang "aplikasi bank digital" pada dataset ini secara de facto adalah temuan tentang **kondisi 2026**, dan klaim temporal apa pun di naskah harus dibatasi eksplisit.

| Aplikasi | Ulasan | Rating rata-rata |
|---|---|---|
| bnc neobank | 4.202 | 3,50 |
| allo bank | 4.088 | — |
| jenius | 3.893 | — |
| superbank | 3.831 | — |
| wondr bni | 3.089 | 2,58 (terendah) |
| bank raya | 2.514 | — |

Rentang rating rata-rata 2,58–3,50; sebaran volume relatif merata (rasio 1,67 : 1), sehingga tidak ada satu aplikasi yang mendominasi kosakata.

---

## 3. EDA data hasil (92.074 tuple, 76.077 klausa)

### 3.1 Statistik per split

| Split | Baris | Tuple | Tuple/baris | Aspek implisit | Opini implisit | Klausa median (kata) | Klausa p95 | Klausa maks |
|---|---|---|---|---|---|---|---|---|
| train | 60.159 | 72.973 | 1,213 | 21.789 (29,86%) | 29.702 (40,70%) | 6 | 18 | 77 |
| dev | 8.027 | 9.587 | 1,194 | 2.999 (31,28%) | 3.751 (39,13%) | 6 | 18 | 73 |
| test | 7.891 | 9.514 | 1,206 | 2.938 (30,88%) | 3.821 (40,16%) | 6 | 18 | 79 |
| **total** | **76.077** | **92.074** | **1,210** | **27.726 (30,11%)** | **37.274 (40,48%)** | 6 | 18 | 79 |

Poin penting: **tidak ada klausa yang mendekati batas 128 token** (maksimum 79 kata). Klaim "klausa jauh di bawah `seq_length`" pada Gambar 2 **terbukti** di sini — tetapi bukti itu justru melemahkan narasi "truncation loss" sebagai penyebab utama kehilangan span (§5).

### 3.2 Kategori dan sentimen

| Kategori | Total | Pangsa | Positif | Negatif | Netral |
|---|---|---|---|---|---|
| FEATURES_PRODUCT | 27.694 | 30,08% | 51,3% | 40,4% | 8,3% |
| TRANSACTION_TRANSFER | 14.752 | 16,02% | 39,9% | 46,2% | 13,8% |
| APP_PERFORMANCE | 9.718 | 10,55% | 9,3% | **79,4%** | 11,3% |
| AUTH_ACCESS | 6.615 | 7,18% | 7,1% | **78,5%** | 14,4% |
| ONBOARDING_KYC | 6.585 | 7,15% | 22,4% | 64,4% | 13,2% |
| UI_UX_DESIGN | 6.225 | 6,76% | **71,1%** | 22,5% | 6,4% |
| CUSTOMER_SERVICE | 4.845 | 5,26% | 18,3% | 66,4% | 15,3% |
| INTEREST_RETURNS | 3.749 | 4,07% | **67,9%** | 20,0% | 12,1% |
| NOTIFICATION_INFO | 3.414 | 3,71% | 21,9% | 63,8% | 14,4% |
| FEES_CHARGES | 2.881 | 3,13% | 55,5% | 30,4% | 14,2% |
| ACCOUNT_MANAGEMENT | 1.952 | 2,12% | 20,0% | 59,5% | 20,5% |
| PROMO_MARKETING | 1.822 | 1,98% | 68,9% | 24,3% | 6,8% |
| SECURITY_FRAUD | 1.822 | 1,98% | 57,2% | 35,9% | 6,9% |

| Sentimen | Jumlah | Pangsa |
|---|---|---|
| negatif | 45.824 | 49,77% |
| positif | 35.846 | 38,93% |
| netral | 10.404 | 11,30% |

**Pola yang menonjol:** kategori teknis (APP_PERFORMANCE 79,4%, AUTH_ACCESS 78,5%) hampir selalu negatif, sedangkan kategori pengalaman/tampilan (UI_UX 71,1%, INTEREST_RETURNS 67,9%, PROMO_MARKETING 68,9%) hampir selalu positif. Artinya sentimen pada dataset ini sangat dapat diprediksi dari kategori — hal ini **membatasi validitas** metrik sentimen sebagai ukuran pemahaman bahasa: model dapat menebak polaritas dari kategori tanpa membaca opini.

### 3.3 Span, kosakata, dan konsentrasi

| Metrik | Aspek | Opini |
|---|---|---|
| Span eksplisit | 64.348 | 54.800 |
| Panjang span (token) | median 1 · rerata 1,20 · maks 4 | median 1 · rerata 1,27 · maks 3 |
| Istilah unik | 362 | 202 |
| Pangsa 10 istilah teratas | 37,1% | 45,2% |

Kosakata sangat sempit untuk 92.074 tuple: **362 istilah aspek dan 202 istilah opini**. Sepuluh istilah teratas menyumbang 37,1% (aspek) dan 45,2% (opini) dari seluruh span eksplisit; istilah opini teratas adalah frasa `tidak bisa` (6.343). Implikasi: tugas ini secara efektif adalah klasifikasi **kosakata tertutup**; F1 tinggi tidak otomatis berarti generalisasi ke kosakata baru, dan evaluasi pada subset kosakata langka perlu dilaporkan terpisah.

### 3.4 Integritas split

| Pemeriksaan | Hasil | Tafsir |
|---|---|---|
| Kebocoran teks train→test | 1.157 baris test (**14,66%**) | konsisten dengan 035; belum ditangani |
| Klausa unik | 66.198 dari 76.077 baris | 9.879 baris (12,98%) merupakan teks berulang |
| Ulasan tanpa tuple | 3.136 dari 43.673 (7,18%) | hilang tanpa penjelasan di dokumentasi |
| Ulasan dengan ≥1 tuple | 40.537 (92,82%) | — |
| Klausa dibuang (tanpa split) | 4.183 | tercatat di `_build_acos_report.json` (E1) |

---

## 4. Wordcloud per komponen ACOS

**Gambar 22** — `reports/fig22_wordcloud_acos.png`: empat panel A/C/O/S.
**Gambar 23** — `reports/fig23_wordcloud_sentimen.png`: kosakata opini per polaritas.

### 4.1 A — aspek

`transaksi`, `transfer`, `fitur`, `saldo`, `login`, `pinjaman`, `bunga`, `pembaruan`, `daftar`, `tabungan` mendominasi. Kosakata berpusat pada **transaksi dan akses akun**; istilah non-fungsional (promo, tampilan) muncul jauh lebih kecil. Cloud ini hampir seluruhnya merupakan kata benda konkret — wajar untuk span aspek, tetapi sekaligus menjelaskan mengapa 30,11% aspek berlabel implisit: ulasan mengeluh tanpa menyebut objek ("kok tidak bisa transfer" menunjuk `TRANSACTION_TRANSFER` tanpa kata "transaksi").

### 4.2 C — kategori

`FEATURES_PRODUCT` menonjol jauh di atas yang lain (30,08%), disusul `TRANSACTION_TRANSFER` (16,02%) dan `APP_PERFORMANCE` (10,55%). `SECURITY_FRAUD` dan `PROMO_MARKETING` berbagi posisi terbawah (1,98% masing-masing). Cloud kategori **tidak** mencerminkan kepentingan pengguna, melainkan granularitas taksonomi: satu label besar (`FEATURES_PRODUCT`) menyerap sepertiga data, sehingga head 13-dimensi pada praktiknya didominasi oleh satu kelas.

### 4.3 O — opini

`tidak bisa` (6.343) merupakan frasa opini paling sering — bukan kata sifat, melainkan **penanda ketidakmampuan fungsional**. Setelahnya baru kata sifat polaritas: `bagus`, `mudah`, `lambat`, `lama`, `sulit`, `gagal`, `buruk`, `cepat`. Komposisi ini menandakan bahwa keluhan pengguna aplikasi bank lebih sering berbentuk *ketidakberhasilan tindakan* daripada penilaian estetis — dan kata sifat murni hanya sebagian kecil kosakata opini.

### 4.4 S — sentimen

Hanya tiga nilai (negatif 49,77%, positif 38,93%, netral 11,30%), sehingga "cloud" di sini menampilkan proporsi, bukan kosakata. Analisis yang lebih informatif ada di Gambar 23:

| Polaritas | Istilah satu kata | Kemunculan (45 teratas) | Tiga teratas |
|---|---|---|---|
| positif | 45 | 19.943 | bagus, mudah, cepat |
| netral | 45 | 2.214 | jelas, berhasil, besar |
| negatif | 42 | 15.225 | lambat, gagal, buruk |

**Temuan penting:** kelas **netral bertumpang-tindih dengan kedua kutub** — dari 60 istilah opini teratas, 31 juga muncul di kelas negatif dan 29 di kelas positif (`bagus`, `buruk`, `gagal`, `error` semuanya ada di netral). Netral bukan kelas "tanpa polaritas"; netral adalah **kelas sisa** yang menampung kalimat ambigu. Ini menjelaskan mengapa sentimen menjadi bottleneck (lihat 042/035) tanpa perlu berhipotesis tentang arsitektur: masalahnya ada pada definisi label.

---

## 5. Uji replikasi angka lama — temuan utama

Angka 61,5% (aspek) dan 48,0% (opini) pada ulasan utuh dikutip berantai di `023 §2.2`, `030 §3.3`, `032`, `035 §III-C`, dan menjadi isi Gambar 2 serta Gambar 3. Uji replikasi dilakukan dengan menghitung langsung: setiap span aspek/opini dari `quintuples_weak.csv` dicari sebagai **sub-urutan token** di dalam teks induknya, di bawah empat definisi.

| Definisi | Sumber teks | Tokenisasi | Aspek | Opini | Klausa |
|---|---|---|---|---|---|
| raw/split | `review_text` | `str.split()` | 70,18% | 49,08% | — |
| raw/punct | `review_text` | `\w+` + `[^\w\s]` | 80,71% | 68,52% | — |
| norm/split | `text_norm` | `str.split()` | 89,25% | 79,72% | **37,57%** |
| norm/punct | `text_norm` | `\w+` + `[^\w\s]` | **100,00%** | **100,00%** | **100,00%** |
| patokan laporan lama | `text_norm` | tidak didokumentasikan | 61,5% | 48,0% | 37,6% |

Uji tambahan (token hanya `\w+`, pencocokan substring karakter) juga dilakukan: hasilnya 80,76/68,53 (raw), 80,77/70,85 (clean), 100/100 (norm). **Tidak ada satu pun kombinasi yang menghasilkan 61,5% / 48,0%.**

Sebaliknya, **37,6% tereproduksi persis**: 37,57% pada `norm/split`. Artinya angka klausa itu memang benar — tetapi benar sebagai **artefak pemilihan tokenizer**, bukan sebagai sifat data. `023 §2.3` sendiri sudah menyatakan hal ini (68,6%/60,0% → 100% setelah tanda baca dipisah), hanya saja §2.2 tetap memakai angka versi `str.split()` tanpa keterangan.

### 5.1 Apa yang sebenarnya terjadi

1. Pada `text_norm` dengan tokenisasi sadar-tanda-baca, **seluruh span terpetakan 100%**, baik pada klausa maupun pada ulasan utuh. Tidak ada kehilangan span struktural.
2. Kehilangan yang nyata hanya muncul bila span hasil normalisasi dicocokkan ke **teks mentah** (`review_text`): 80,71% aspek dan 68,52% opini — yaitu **19,3% dan 31,5% hilang**, dan penyebabnya adalah **perbedaan normalisasi** (`gimana`→`bagaimana`), bukan pemotongan `seq_length`.
3. Karena klausa maksimum 79 kata (§3.1), **truncation pada 128 token tidak pernah terjadi** pada unit klausa, dan pada unit ulasan pun hanya menyentuh 1,98% ulasan (≥ 80 kata).

### 5.2 Dampak pada pekerjaan sebelumnya

| Artefak | Dampak | Tindakan |
|---|---|---|
| `023 §2.2`, `030 §3.3`, `032`, `035 §III-C` | memuat angka 61,5/48,0 tanpa metode | koreksi teks atau dokumentasikan metode aslinya |
| Gambar 2 (`fig19`) dan Gambar 3 (`fig20`), PR #6 | memvisualkan 61,5/48,0 dan Δ +38,5/+52,0 poin | **jangan dipasang ke naskah** sebelum diganti angka E2 |
| `ACOS-IndoBERT/acos_id/build_acos.py` docstring | menulis "membuang ~62% span" — bertentangan dengan kedua versi angka | perbaiki |
| 042 §14 | T03 (seleksi checkpoint di test set) tidak terpengaruh | tetap berlaku |

---

## 6. Temuan audit EDA

| ID | Temuan | Tingkat | Bukti |
|---|---|---|---|
| `E-01` | 61,5%/48,0% tidak dapat direplikasi (10 definisi diuji) | tinggi | §5, `coverage_replication.csv` |
| `E-02` | 37,6% tereproduksi persis dan merupakan artefak `str.split()` | tinggi | norm/split = 37,57% |
| `E-03` | Dengan tokenisasi sadar-tanda-baca, cakupan span pada `text_norm` = 100% (klausa **dan** ulasan) | tinggi | norm/punct = 100/100 |
| `E-04` | Kehilangan riil hanya saat mencocokkan ke teks mentah: 19,3% aspek, 31,5% opini, disebabkan normalisasi | sedang | raw/punct = 80,71/68,52 |
| `E-05` | Truncation 128 token tidak relevan: klausa maks 79 kata; hanya 1,98% ulasan ≥ 80 kata | sedang | §3.1 |
| `E-06` | Kelas netral bertumpang dengan negatif (31/60) dan positif (29/60) — netral adalah kelas sisa | tinggi | Gambar 23 |
| `E-07` | Kosakata tertutup: 362 istilah aspek, 202 opini; top-10 = 37,1%/45,2% | sedang | §3.3 |
| `E-08` | Kebocoran teks 1.157 baris test (14,66%) belum ditangani | tinggi | §3.4 |
| `E-09` | 12,98% baris merupakan klausa berulang (66.198 unik dari 76.077) | sedang | §3.4 |
| `E-10` | 3.136 ulasan (7,18%) tidak menghasilkan tuple, tanpa dokumentasi | rendah | §3.4 |

---

## 7. Rekomendasi

| ID | Rekomendasi | Prioritas |
|---|---|---|
| `R-01` | Ganti angka 61,5/48,0 di `023`, `030`, `032`, `035` dengan angka yang dapat direproduksi (E2): 80,71/68,52 (mentah) atau nyatakan 100% pada `text_norm` dan jelaskan bahwa kehilangan berasal dari normalisasi | **tinggi** |
| `R-02` | Perbaiki `fig19`/`fig20` atau tarik dari PR #6 sampai angkanya sinkron | **tinggi** |
| `R-03` | Perbaiki docstring `build_acos.py` ("~62%" → definisi eksplisit) | sedang |
| `R-04` | Definisikan ulang kelas netral (aturan label eksplisit) atau laporkan sentimen sebagai biner positif/negatif dengan kelas netral dilaporkan terpisah | **tinggi** |
| `R-05` | Laporkan metrik pada subset klausa unik (66.198) di samping baris penuh | sedang |
| `R-06` | Deduplikasi teks lintas split atau laporkan metrik dengan/tanpa 1.157 baris bocor | **tinggi** |
| `R-07` | Audit 3.136 ulasan tanpa tuple: dibuang, gagal ekstraksi, atau di luar cakupan anotator | rendah |
| `R-08` | Jadikan `reports/044_data/eda_summary.json` artefak rilis dan jalankan `eda_044_appsid.py` di CI agar angka naskah selalu tersinkron | sedang |

---

## 8. Inventaris berkas

| Berkas | Ukuran (byte) | SHA-256 (10) |
|---|---|---|
| `reports/fig21_eda_sumber_appsid.png` | 512.417 | `1886f34be0` |
| `reports/fig21_eda_sumber_appsid.svg` | 55.028 | `3ecec2cfd0` |
| `reports/fig21_eda_sumber_appsid.webp` | 273.386 | `20216feda9` |
| `reports/fig22_wordcloud_acos.png` | 1.945.699 | `56e46e3d72` |
| `reports/fig22_wordcloud_acos.webp` | 646.096 | `4796194191` |
| `reports/fig23_wordcloud_sentimen.png` | 1.278.396 | `68fc0621d4` |
| `reports/fig23_wordcloud_sentimen.webp` | 411.682 | `dc2e93efe0` |
| `reports/044_data/eda_summary.json` | 4.524 | `ce6e85265e` |
| `reports/044_data/split_stats.csv` | 325 | `dc12c468f5` |
| `reports/044_data/category_counts.csv` | 587 | `99faf47880` |
| `reports/044_data/sentiment_counts.csv` | 91 | `f1fcc89365` |
| `reports/044_data/span_length_dist.csv` | 123 | `dd6818940c` |
| `reports/044_data/top_aspect_terms.csv` | 2.928 | `bb99b00cd3` |
| `reports/044_data/top_opinion_terms.csv` | 2.909 | `5eb12b584c` |
| `reports/044_data/opinion_terms_by_sentiment.csv` | 3.936 | `c9df11da98` |
| `reports/044_data/review_stats.csv` | 379 | `99c24c68de` |
| `reports/044_data/coverage_replication.csv` | 244 | `a9650a458e` |

Gambar 22 dan 23 hanya disediakan sebagai PNG/WebP: objek `wordcloud` adalah raster di dalam matplotlib, sehingga SVG hanya akan membungkus bitmap dan tidak memberi manfaat penyuntingan.

---

## 9. Reproduksi

```bash
python3 scripts/eda_044_appsid.py        # 9 berkas di reports/044_data/ (~5 detik)
python3 scripts/fig21_eda_appsid.py      # matplotlib
python3 scripts/fig22_wordcloud_acos.py  # matplotlib + wordcloud 1.9.6

convert reports/fig21_eda_sumber_appsid.png -quality 88 reports/fig21_eda_sumber_appsid.webp
convert reports/fig22_wordcloud_acos.png  -quality 88 reports/fig22_wordcloud_acos.webp
convert reports/fig23_wordcloud_sentimen.png -quality 88 reports/fig23_wordcloud_sentimen.webp
```

Prasyarat tambahan (di luar stdlib, sama seperti 043): `matplotlib`, `wordcloud`, `Pillow`. Pemasangan memerlukan `--break-system-packages` pada lingkungan ini dan tidak persisten di snapshot.
