# Konstruksi Korpus Kuadruplet Aspek–Kategori–Opini–Sentimen Berlabel Lemah dari Ulasan Aplikasi Bank Digital Indonesia: Pipeline, Gerbang Verifikasi, dan Karakteristik Data

> **CATATAN DRAF v1 — 12/11/2026 (hapus sebelum submit).**
> Target: **RESTI (SINTA 2)**, alternatif tier yang sama: JTIIK, INFORM — cek panduan penulis & lingkup jurnal saat submit.
> Basis: artefak repositori pada `main` `6704cbf`; seluruh angka punya provenance di Lampiran A. Draf ditulis ulang dari nol (bukan salinan 045/048); **pemeriksaan Turnitin/iThenticate belum dijalankan** — wajib sebelum submit (target <20%).
> Wajib dikerjakan sebelum submit (pemetaan temuan `reports/049`): (1) protokol pencarian literatur sistematis untuk klaim "sejauh penelusuran kami" [#1 BLOCKER]; (2) anotasi manusia 500 klausa × 2 anotator + Cohen's κ [#2 BLOCKER]; (3) keputusan lisensi/izin redistribusi [#3 BLOCKER]; (4) verifikasi DOI seluruh rujukan (`reports/050` T1).
> Konvensi angka: pemisah ribuan titik, desimal koma (ID); Abstract EN memakai konvensi Inggris.

## Abstrak

Tugas aspect–category–opinion–sentiment (ACOS) menuntut korpus dengan anotasi empat komponen sekaligus, termasuk slot aspek dan opini implisit. Korpus semacam itu belum tersedia untuk bahasa Indonesia pada domain perbankan digital, sejauh penelusuran kami. Artikel ini menyajikan Apps-ACOS, korpus ACOS berbahasa Indonesia yang dibangun dari 43.673 ulasan 13 aplikasi bank digital (37.825 Google Play; 5.848 App Store) melalui pipeline supervisi lemah: pelabelan lemah 96.417 baris, pemecahan klausa menjadi 80.260 klausa, dan penyaringan menjadi 76.077 klausa final yang memuat 92.074 kuadruplet pada 13 kategori dan 3 kelas sentimen. Reproduksibilitas konstruksi dijaga enam gerbang verifikasi otomatis: gerbang bobot encoder (199/199 kunci cocok, rerata tensor identik), lima gerbang data (taksonomi, dataset, pembangunan ACOS, tokenisasi, paritas bahasa Inggris), nol kuadruplet hilang saat retokenisasi, dan nol tumpang tindih `review_id` antar split. Kami melaporkan pula kelemahan yang terukur: 14,66% baris uji berbagi teks dengan data latih, 30,11% slot aspek dan 40,48% slot opini implisit, serta belum adanya verifikasi label oleh manusia (κ belum diukur). Korpus ini diposisikan sebagai sumber daya berlabel lemah dengan metode konstruksi yang dapat diaudit, bukan benchmark berlabel emas.

**Kata kunci:** ACOS; analisis sentimen berbasis aspek; supervisi lemah; bank digital; bahasa Indonesia

## Abstract

The aspect–category–opinion–sentiment (ACOS) task requires corpora annotated with four components at once, including implicit aspect and opinion slots. To the best of our knowledge, no such corpus exists for Indonesian in the digital-banking domain. This paper presents Apps-ACOS, an Indonesian ACOS corpus built from 43,673 reviews of 13 mobile-banking apps (37,825 Google Play; 5,848 App Store) through a weak-supervision pipeline: 96,417 weakly labeled rows, clause segmentation into 80,260 clauses, and filtering to 76,077 final clauses carrying 92,074 quadruples over 13 categories and 3 sentiment classes. Construction reproducibility is guarded by six automated gates: an encoder-weight gate (199/199 keys matched, identical tensor means), five data gates (taxonomy, dataset, ACOS build, tokenization, English parity), zero quadruples lost during re-tokenization, and zero `review_id` overlap across splits. We also report measured weaknesses: 14.66% of test rows share text with training data, 30.11% of aspect slots and 40.48% of opinion slots are implicit, and no human verification of labels has yet been performed (κ not measured). The corpus is positioned as a weakly labeled resource with an auditable construction method, not a gold benchmark.

**Keywords:** ACOS; aspect-based sentiment analysis; weak supervision; digital banking; Indonesian

## 1. Pendahuluan

Analisis sentimen berbasis aspek (ABSA) [1] berkembang dari klasifikasi polaritas per aspek [2] menjadi struktur keluaran yang semakin kaya. Format terkaya yang lazim dipakai adalah kuadruplet aspek–kategori–opini–sentimen (ACOS) [3], yang juga mengakomodasi aspek dan opini implisit melalui slot khusus. Untuk bahasa Indonesia, sumber daya ABSA yang tersedia menitikberatkan klasifikasi kalimat atau pasangan aspek–sentimen pada domain umum [4], sehingga pelatihan dan evaluasi model kuadruplet pada domain aplikasi keuangan belum dapat dilakukan.

Kami membangun korpus ACOS dari ulasan aplikasi bank digital Indonesia dengan tiga keputusan desain: (i) unit anotasi berupa klausa (median 6–7 kata, maksimum 79 kata) agar span tetap berada di dalam jendela model; (ii) label dihasilkan oleh pipeline supervisi lemah, bukan anotasi manual penuh; (iii) setiap tahap konstruksi dikawal gerbang verifikasi otomatis yang keluarannya dapat diaudit. Konsekuensi keputusan (ii) dinyatakan eksplisit: label belum diverifikasi manusia, sehingga korpus ini adalah sumber daya berlabel lemah.

Pertanyaan penelitian: **(R1)** bagaimana membangun korpus ACOS berlabel lemah dari ulasan toko aplikasi secara teraudit? **(R2)** apa karakteristik linguistik dan distribusional korpus yang dihasilkan? **(R3)** integritas mana yang terverifikasi dan mana yang masih terbuka? Kontribusi: (1) metode konstruksi bertahap dengan enam gerbang verifikasi; (2) korpus 92.074 kuadruplet berbahasa Indonesia domain perbankan digital; (3) audit integritas yang melaporkan kelemahan secara kuantitatif, termasuk kebocoran teks 14,66% yang belum diremediasi.

## 2. Kajian Pustaka

ABSA dimulai dari tugas SemEval aspek-berbasis [2], [5]. Struktur keluaran kemudian diperkaya menjadi triplet hingga kuadruplet; Cai dkk. [3] merumuskan ACOS dengan slot `NULL` untuk aspek dan opini implisit dan merilis korpus Restaurant/Laptop-ACOS. Pendekatan generatif berikutnya memformalkan prediksi kuadruplet sebagai pembangkitan parafrasa [6]. Survei mutakhir merangkum pergeseran tugas, metode, dan tantangan evaluasi [7].

Untuk bahasa Indonesia, tolok ukur IndoNLU [4] dan IndoLEM [8] menyediakan dataset klasifikasi dan pemahaman bahasa, termasuk tugas sentimen berbasis aspek pada domain umum, tetapi tidak mencakup kuadruplet ACOS. Dataset multi-elemen lintas domain pernah dirakit untuk ABSA [9], namun tidak berbahasa Indonesia. Sejauh penelusuran kami, belum tersedia korpus ACOS kuadruplet berbahasa Indonesia pada domain perbankan digital; klaim ini akan diperkuat dengan protokol pencarian sistematis pada versi akhir naskah.

## 3. Metode

### 3.1 Sumber data

Ulasan dikumpulkan dari 13 aplikasi bank digital di Google Play (37.825 ulasan; 86,61%) dan App Store (5.848; 13,39%), lalu dibersihkan menjadi 43.673 ulasan (Tabel 1). Distribusi rating bimodal (1–2 bintang 43,09%; 4–5 bintang 42,29%) dan 61,96% ulasan berasal dari tahun 2026, sehingga klaim temporal korpus dibatasi pada periode pengumpulan.

**Tabel 1.** Statistik sumber (43.673 ulasan bersih; `reviews_clean.csv`).

| Metrik | Nilai |
|---|---|
| Aplikasi | 13 |
| Google Play / App Store | 37.825 (86,61%) / 5.848 (13,39%) |
| Rating 1–2 / 3 / 4–5 | 43,09% / 14,62% / 42,29% |
| Tahun terbanyak | 2026 (27.061; 61,96%) |
| Kata per ulasan | median 15 · rerata 20,26 · p95 59 · maks 307 |
| Ulasan memuat emoji | 3.524 (8,07%; total 6.748 emoji) |
| Duplikat teks ulasan | 455 (1,04%) |

### 3.2 Pipeline konstruksi

Pipeline terdiri atas lima tahap (Tabel 2). Pelabelan lemah menghasilkan 96.417 baris `quintuples_weak.csv`; pemecahan klausa menghasilkan 80.260 klausa; 4.183 klausa tanpa pemisah dibuang (tercatat di `_build_acos_report.json`); hasil akhir 76.077 klausa memuat 92.074 kuadruplet.

**Tabel 2.** Tahap konstruksi dan jumlah keluaran.

| Tahap | Keluaran | Jumlah |
|---|---|---|
| Pengumpulan & pembersihan | `reviews_clean.csv` | 43.673 ulasan |
| Pelabelan lemah | `quintuples_weak.csv` | 96.417 baris (pra-pemecahan) |
| Pemecahan klausa | klausa berlabel | 80.260 |
| Penyaringan klausa tanpa split | dibuang (tercatat) | 4.183 |
| Dataset final (klausa) | train / dev / test | 60.159 / 8.027 / 7.891 = 76.077 |
| Kuadruplet | train / dev / test | 72.973 / 9.587 / 9.514 = 92.074 |

### 3.3 Skema anotasi

Satu baris dataset adalah satu klausa; satu klausa dapat memuat lebih dari satu kuadruplet (rerata 1,210 kuadruplet per klausa). Setiap kuadruplet memuat empat field: span aspek (indeks token, batas akhir eksklusif), kategori (13 kelas), sentimen (3 kelas: negatif/netral/positif), dan span opini. Slot implisit diberi indeks `(-1,-1)` mengikuti konvensi ACOS [3]; 3.136 ulasan (7,18%) tidak menghasilkan kuadruplet dan tidak dimasukkan.

### 3.4 Gerbang verifikasi

Enam gerbang otomatis mengawal konstruksi: (G1) gerbang bobot encoder — 199/199 kunci cocok dan rerata tensor identik antara bobot dimuat dan referensi; (G2–G6) lima gerbang data (taksonomi, dataset, pembangunan ACOS, tokenisasi, paritas Inggris) dengan status ok=true; retokenisasi tidak kehilangan satu pun kuadruplet; tidak ada tumpang tindih `review_id` antar split. Rencana rilis: ID ulasan + anotasi + tautan sumber (bukan teks mentah), mengikuti batasan ketentuan layanan toko aplikasi; keputusan lisensi final sedang diproses dan akan dicantumkan sebelum publikasi.

## 4. Hasil dan Pembahasan

### 4.1 Distribusi kategori dan sentimen

**Tabel 3.** Distribusi 13 kategori dan sentimennya (92.074 kuadruplet; gabungan split).

| Kategori | Kuadruplet | Pangsa | Sentimen dominan (pangsa) |
|---|---:|---:|---|
| FEATURES_PRODUCT | 27.694 | 30,08% | positif (51,3%) |
| TRANSACTION_TRANSFER | 14.752 | 16,02% | negatif (46,2%) |
| APP_PERFORMANCE | 9.718 | 10,55% | negatif (79,4%) |
| AUTH_ACCESS | 6.615 | 7,18% | negatif (78,5%) |
| ONBOARDING_KYC | 6.585 | 7,15% | negatif (64,4%) |
| UI_UX_DESIGN | 6.225 | 6,76% | positif (71,1%) |
| CUSTOMER_SERVICE | 4.845 | 5,26% | negatif (66,4%) |
| INTEREST_RETURNS | 3.749 | 4,07% | positif (67,9%) |
| NOTIFICATION_INFO | 3.414 | 3,71% | negatif (63,8%) |
| FEES_CHARGES | 2.881 | 3,13% | positif (55,5%) |
| ACCOUNT_MANAGEMENT | 1.952 | 2,12% | negatif (59,5%) |
| PROMO_MARKETING | 1.822 | 1,98% | positif (68,9%) |
| SECURITY_FRAUD | 1.822 | 1,98% | positif (57,2%) |

Sentimen keseluruhan: negatif 45.824 (49,77%), positif 35.846 (38,93%), netral 10.404 (11,30%). Kategori teknis (kinerja aplikasi, autentikasi) hampir selalu negatif, sedangkan kategori pengalaman (antarmuka, bunga/hasil) condong positif — pola yang membatasi validitas metrik sentimen karena sentimen sebagian dapat diprediksi dari kategori saja; baseline kuantitatifnya dilaporkan pada draf terpisah.

### 4.2 Slot implisit dan panjang klausa

**Tabel 4.** Slot implisit per split (kuadruplet gold).

| Split | Kuadruplet | Aspek implisit | Opini implisit |
|---|---:|---:|---:|
| train | 72.973 | 21.789 (29,86%) | 29.702 (40,70%) |
| dev | 9.587 | 2.999 (31,28%) | 3.751 (39,13%) |
| test | 9.514 | 2.938 (30,88%) | 3.821 (40,16%) |
| **total** | **92.074** | **27.726 (30,11%)** | **37.274 (40,48%)** |

Proporsi slot implisit stabil antar split (selisih <1,6 poin), menandakan pemecahan klausa dan pembagian split tidak menggeser komposisi fenomena implisit. Panjang klausa median 6–7 kata dan maksimum 79 kata, jauh di bawah `max_seq_length` 128, sehingga tidak ada span yang terpotong.

### 4.3 Integritas data

**Tabel 5.** Audit integritas: yang terverifikasi dan yang terbuka.

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Tumpang tindih `review_id` antar split | 0 | Terverifikasi |
| Kuadruplet hilang saat retokenisasi | 0 | Terverifikasi |
| Gerbang bobot encoder (G1) | 199/199 kunci, rerata identik | Terverifikasi |
| Lima gerbang data (G2–G6) | ok=true | Terverifikasi |
| Baris uji berbagi teks dengan latih | 1.157 (14,66%) | **Terbuka — belum dideduplikasi** |
| Klausa dengan teks berulang | 9.879 (12,98%) | Terbuka |
| Verifikasi label oleh manusia (κ) | belum ada | **Terbuka — direncanakan 500 klausa × 2 anotator** |
| Lisensi redistribusi | belum ditetapkan | **Terbuka** |

Kebocoran teks 14,66% berasal dari klausa pendek berulang (mis. "tidak bisa login"); seluruh metrik yang dilaporkan korpus ini adalah prak-deduplikasi dan akan dilengkapi metrik pada subset uji bersih pada pekerjaan lanjutan.

### 4.4 Keterbatasan

Tiga keterbatasan utama: (i) label lemah tanpa verifikasi manusia — κ belum diukur, sehingga mutu label belum dapat dikuantifikasi; (ii) kebocoran teks 14,66% belum diremediasi; (iii) cakupan temporal 61,96% tahun 2026 membatasi generalisasi waktu. Kosakata aspek (362 istilah unik) dan opini (202 istilah unik) relatif tertutup, mengikuti sifat domain perbankan.

## 5. Kesimpulan

Korpus Apps-ACOS menyediakan 92.074 kuadruplet ACOS berbahasa Indonesia dari 76.077 klausa ulasan 13 aplikasi bank digital, dibangun dengan pipeline supervisi lemah yang setiap tahapnya dikawal gerbang verifikasi otomatis. Karakteristik utamanya: dominasi kategori fitur dan transaksi, 30,11% slot aspek dan 40,48% slot opini implisit, serta sentimen yang sebagian deterministik terhadap kategori. Kelemahan terukur (kebocoran teks 14,66%, belum ada verifikasi manusia, lisensi belum ditetapkan) dilaporkan terbuka dan menjadi prasyarat sebelum korpos ini digunakan sebagai benchmark. Pekerjaan lanjutan: anotasi manusia 500 klausa dengan dua anotator dan pelaporan κ, deduplikasi lintas split, serta evaluasi ulang pada subset uji bersih.

## Daftar Pustaka

[1] B. Liu, *Sentiment Analysis and Opinion Mining*. Morgan & Claypool, 2012.

[2] M. Pontiki, D. Galanis, J. Pavlopoulos, H. Papageorgiou, I. Androutsopoulos, dan S. Manandhar, "SemEval-2014 Task 4: Aspect Based Sentiment Analysis," dalam *Proc. SemEval*, 2014.

[4] H. Cai, R. Xia, dan J. Yu, "Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions," dalam *Proc. ACL-IJCNLP*, 2021, hlm. 340–350.

[6] B. Wilie, K. Vincentio, G. I. Hadiwijaya, J. B. Jie, M. C. Purwarianti, dan S. Aji, "IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding," dalam *Proc. AACL-IJCNLP*, 2020, hlm. 843–857.

[3] M. Pontiki dkk., "SemEval-2016 Task 5: Aspect Based Sentiment Analysis," dalam *Proc. SemEval*, 2016.

[5] W. Zhang, X. Li, Y. Deng, L. Bing, dan W. Lam, "Aspect Sentiment Quad Prediction as Paraphrase Generation," dalam *Proc. EMNLP*, 2021.

[11] W. Zhang, X. Li, Y. Deng, L. Bing, dan W. Lam, "A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges," *IEEE Trans. Knowl. Data Eng.*, 2022.

[7] F. Koto, A. Rahimi, J. H. Lau, dan T. Baldwin, "IndoLEM and IndoBERT: A Benchmark Dataset and Pre-trained Language Model for Indonesian NLP," dalam *Proc. COLING*, 2020, hlm. 757–770.

[9] H. Hu dkk., "MEMD-ABSA: A Multi-Element Multi-Domain Dataset for Aspect-Based Sentiment Analysis," *arXiv:2306.16956*, 2023 (pra-cetak).

## Lampiran A — Provenance angka (hapus sebelum submit)

| Angka | Sumber artefak | Bukti |
|---|---|---|
| 43.673 / 37.825 / 5.848 / rating / tahun / emoji / duplikat | `reports/044_data/eda_summary.json` (skrip `scripts/eda_044_appsid.py`, stdlib) | E2 |
| 96.417 · 80.260 · 4.183 · 76.077 · 92.074 · split | `docs/0011` §3.1; TSV `ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_*.tsv` (60.159/8.027/7.891 baris terhitung ulang) | E2 |
| Distribusi kategori & sentimen (Tabel 3) | `reports/044_data/category_counts.csv`, `sentiment_counts.csv` | E2 |
| Slot implisit per split (Tabel 4) | `reports/044_data/split_stats.csv` | E2 |
| Kebocoran 14,66% · klausa unik 66.198 · ulasan tanpa tuple 3.136 | `docs/0011` §3.2 (audit artefak) | E2 |
| Gerbang G1–G6 · 199/199 · 0 quad hilang | `docs/0012` §3.4 (survey artefak Drive) | E2 (via 0012) |
| 362 istilah aspek · 202 opini | `docs/0012` §EDA (survey artefak) | E1 |
