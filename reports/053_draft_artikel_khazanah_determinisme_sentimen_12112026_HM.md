# Seberapa Jauh Kategori Menentukan Sentimen? Baseline Majority-per-Category pada Korpus Kuadruplet Ulasan Aplikasi Bank Digital Indonesia

> **CATATAN DRAF v1 — 12/11/2026 (hapus sebelum submit).**
> Target: **Khazanah Informatika (SINTA 3)**, alternatif tier sama: JOINTECS, JTMI, Barekeng (ejaan sesuai daftar pengguna: "Baukereng" — konfirmasi nama jurnal), INFORM naik ke SINTA 2 — cek panduan penulis saat submit.
> Basis: artefak repositori `main` `6704cbf`. Angka baseline dihitung baru oleh `scripts/eda_053_majority_baseline_implisit.py` (stdlib, deterministik, 12/11/2026; keluaran `reports/053_data/majority_baseline.csv`). Teks ditulis segar; **Turnitin/iThenticate belum dijalankan** — wajib sebelum submit.
> Wajib sebelum submit: (1) anotasi manusia + κ — klaim "determinisme" atas label lemah perlu dibatasi sampai κ diketahui [`reports/049` #2]; (2) verifikasi DOI rujukan (`reports/050` T1).
> Konvensi angka: pemisah ribuan titik, desimal koma (ID).

## Abstrak

Pada tugas kuadruplet aspek–kategori–opini–sentimen (ACOS), komponen sentimen lazim dilaporkan sebagai bukti pemahaman bahasa. Artikel ini menguji seberapa jauh sentimen sebenarnya dapat diprediksi dari kategori aspek saja, tanpa membaca teks, pada korpus 92.074 kuadruplet berlabel lemah dari ulasan 13 aplikasi bank digital Indonesia. Kami memasang baseline majority-per-category: sentimen diprediksi sebagai kelas mayoritas kategori pada data latih, lalu dievaluasi pada 9.514 kuadruplet uji. Baseline sederhana ini mencapai akurasi 59,93%, dibandingkan 50,33% untuk mayoritas global, dan mencapai 78–79% pada kategori teknis (APP_PERFORMANCE 78,03%; AUTH_ACCESS 79,47%) yang bersifat keluhan fungsi. Temuan ini mengindikasikan bahwa metrik sentimen pada korpus domain sempit sebagian mengukur korelasi kategori–sentimen, bukan pemahaman opini, sehingga evaluasi model ACOS perlu melaporkan baseline trivial ini sebagai ambang batas bawah. Karena label dihasilkan supervisi lemah tanpa verifikasi manusia, seluruh angka dilaporkan sebagai properti korpus berlabel lemah.

**Kata kunci:** analisis sentimen berbasis aspek; ACOS; baseline trivial; shortcut learning; bank digital

## 1. Pendahuluan

Model klasifikasi citra dan bahasa diketahui memanfaatkan korelasi pintas (shortcut) antara fitur mudah dan label [1], [2]. Pada analisis sentimen berbasis aspek (ABSA) [3], [4], format kuadruplet ACOS [5] menuntut model menentukan sentimen dari opini. Namun pada domain sempit seperti ulasan aplikasi, kategori aspek dan sentimen berkorelasi kuat: keluhan tentang kinerja aplikasi hampir selalu negatif, pujian tentang antarmuka hampir selalu positif. Jika korelasi ini kuat, metrik sentimen yang tinggi dapat dicapai tanpa membaca span opini — sebuah kegagalan diagnosis yang tidak terdeteksi oleh metrik agregat.

Kami mengkuantifikasi korelasi tersebut pada korpus kuadruplet berlabel lemah dari ulasan aplikasi bank digital Indonesia (92.074 kuadruplet; 13 kategori; 3 kelas sentimen) dengan memasang baseline majority-per-category: untuk setiap kategori, prediksikan sentimen mayoritas kategori tersebut pada data latih. Pertanyaan penelitian: **(RQ1)** berapa akurasi baseline majority-per-category pada data uji, dibandingkan mayoritas global? **(RQ2)** kategori mana yang paling tinggi dan paling rendah determinismenya? **(RQ3)** apa implikasinya bagi pelaporan metrik sentimen pada tugas ACOS?

Kontribusi: (1) baseline trivial terkuantifikasi pada korpus ACOS bahasa Indonesia (59,93% akurasi uji); (2) tabel determinisme 13 kategori; (3) rekomendasi pelaporan: metrik sentimen ACOS pada domain sempit wajib disertai baseline ini.

## 2. Kajian Pustaka

ABSA ber-evolusi dari klasifikasi aspek-berbasis SemEval [3] menuju struktur keluaran triplet hingga kuadruplet [4], [5]. Survei mutakhir mencatat bahwa evaluasi ABSA sering mengabaikan baseline trivial dan distribusi kelas [6]. Fenomena korelasi pintas dipelajari sistematis di penglihatan komputer dan NLP [1], [2]; pada klasifikasi teks, model diketahui memanfaatkan petunjuk leksikal alih-alih target semantik. Untuk bahasa Indonesia, tolok ukur IndoNLU [7] menyertakan tugas sentimen berbasis aspek, tetapi tidak pada format kuadruplet. Studi ini berbeda dari yang tersebut di atas karena mengukur determinisme kategori–sentimen langsung pada level kuadruplet, bukan pada level kalimat, dan menjadikannya baseline eksplisit.

## 3. Metode

### 3.1 Data

Korpus Apps-ACOS (korpus penulis, berlabel lemah) memuat 92.074 kuadruplet berlabel lemah (supervisi lemah, tanpa verifikasi manusia; κ belum diukur) dari 76.077 klausa ulasan 13 aplikasi bank digital: data latih 72.973, dev 9.587, uji 9.514 kuadruplet. Distribusi sentimen: negatif 49,77%, positif 38,93%, netral 11,30%.

### 3.2 Baseline

Dua baseline trivial dipasang: **(B1) mayoritas global** — satu kelas sentimen mayoritas data latih untuk semua kuadruplet; **(B2) majority-per-category** — untuk setiap kategori, kelas mayoritas kategori tersebut pada data latih (tie-break deterministik: urutan leksikografis nama kelas). Keduanya dievaluasi pada seluruh kuadruplet uji. B2 dihitung dengan skrip stdlib deterministik (`scripts/eda_053_majority_baseline_implisit.py`); karena baseline tidak melibatkan pembelajaran, tidak ada seed atau pelatihan.

### 3.3 Ukuran determinisme

Selain akurasi, kami melaporkan pangsa kelas sentimen dominan per kategori (gabungan split) sebagai ukuran determinisme korpus, dan membandingkan akurasi uji B2 per kategori dengan pangsa mayoritas pada data latih untuk mendeteksi pergeseran distribusi.

## 4. Hasil

### 4.1 Baseline

**Tabel 1.** Baseline trivial pada 9.514 kuadruplet uji.

| Baseline | Benar | Akurasi |
|---|---:|---:|
| B1 — mayoritas global (negatif) | 4.788 | 50,33% |
| B2 — majority-per-category | 5.702 | **59,93%** |

B2 unggul 9,60 poin atas B1 dan dev menghasilkan angka konsisten (60,74%), menandakan pola stabil antar split.

### 4.2 Determinisme per kategori

**Tabel 2.** Majority-per-category per kategori: mayoritas dihitung pada latih, akurasi diuji pada uji; kolom terakhir = pangsa kelas dominan gabungan.

| Kategori | n uji | Mayoritas (latih) | Pangsa mayoritas latih | Akurasi uji | Dominan gabungan |
|---|---:|---|---:|---:|---|
| AUTH_ACCESS | 682 | negatif | 78,26% | **79,47%** | negatif 78,5% |
| APP_PERFORMANCE | 1.006 | negatif | 79,43% | **78,03%** | negatif 79,4% |
| PROMO_MARKETING | 189 | positif | 69,45% | 69,31% | positif 68,9% |
| UI_UX_DESIGN | 657 | positif | 70,97% | 68,34% | positif 71,1% |
| ONBOARDING_KYC | 659 | negatif | 64,59% | 65,71% | negatif 64,4% |
| NOTIFICATION_INFO | 388 | negatif | 63,44% | 64,69% | negatif 63,8% |
| CUSTOMER_SERVICE | 511 | negatif | 66,68% | 65,36% | negatif 66,4% |
| ACCOUNT_MANAGEMENT | 189 | negatif | 58,74% | 63,49% | negatif 59,5% |
| INTEREST_RETURNS | 342 | positif | 68,66% | 63,74% | positif 67,9% |
| SECURITY_FRAUD | 182 | positif | 57,05% | 55,49% | positif 57,2% |
| FEES_CHARGES | 298 | positif | 56,20% | 55,37% | positif 55,5% |
| FEATURES_PRODUCT | 2.919 | positif | 51,40% | 50,60% | positif 51,3% |
| TRANSACTION_TRANSFER | 1.492 | negatif | 45,89% | 46,65% | negatif 46,2% |

Akurasi uji per kategori mendekati pangsa mayoritas latih (selisih <1,9 poin pada 9 dari 13 kategori; terbesar 4,92 poin pada INTEREST_RETURNS) — pergeseran distribusi antar split kecil pada sebagian besar kategori. Determinisme tertinggi pada kategori teknis keluhan fungsi (AUTH_ACCESS, APP_PERFORMANCE, ±79%) dan terendah pada TRANSACTION_TRANSFER (46,2%), kategori terbesar kedua yang memuat campuran keberhasilan dan kegagalan transaksi.

### 4.3 Jejak leksikal determinisme

Korpus didominasi keluhan berbentuk ketidakberhasilan tindakan: istilah opini paling frekuent adalah "tidak bisa" (6.343) di atas "bagus" (5.246). Kelas netral (11,30%) berperilaku sebagai kelas sisa: kosakatanya memuat kata bermuatan negatif seperti "lambat" dan "gagal", indikasi label netral menampung kasus ambigu, bukan polaritas tengah sejati.

## 5. Pembahasan

**(RQ1)** Baseline majority-per-category mencapai 59,93% — 9,60 poin di atas mayoritas global. Angka ini adalah ambang yang harus dilampaui model apabila klaim "memahami opini" ingin dibuat; selisih metrik sentimen model terhadap 59,93% itulah, bukan angka absolutnya, yang menunjukkan kontribusi teks. **(RQ2)** Determinisme menumpuk pada kategori teknis (±79%): keluhan kinerja dan autentikasi hampir selalu negatif pada domain aplikasi. Kategori besar seperti TRANSACTION_TRANSFER justru paling sulit (46,2%) karena memuat keberhasilan dan kegagalan — area di mana bacaan opini sesungguhnya diperlukan. **(RQ3)** Implikasinya: pelaporan metrik sentimen ACOS pada domain sempit tanpa baseline trivial adalah tidak lengkap; kami merekomendasikan B2 dilaporkan sebagai baris wajib pada tabel hasil.

Pada pipeline dua tahap kami sendiri (berbasis IndoBERT [8]), akurasi kepala sentimen tidak dapat dibandingkan dengan baseline ini karena bug persistensi metrik (nilai tercatat 0,0), sehingga perbandingan model–baseline ditunda hingga perbaikan selesai; ini kami laporkan terbuka agar pembaca tidak menganggap pembandingan telah dilakukan.

Keterbatasan: (i) label lemah tanpa verifikasi manusia — determinisme yang terukur dapat sebagian berasal dari aturan pelabelan, bukan bahasa; (ii) satu domain (perbankan digital) dan satu bahasa; (iii) level kuadruplet, bukan klausa, sehingga angka tidak langsung dibandingkan dengan akurasi klasifikasi kalimat.

## 6. Kesimpulan

Pada korpus kuadruplet ACOS ulasan aplikasi bank digital Indonesia berlabel lemah, sentimen dapat diprediksi dari kategori saja dengan akurasi 59,93% (mayoritas global 50,33%), dan mencapai ±79% pada kategori teknis. Baseline majority-per-category karenanya wajib dilaporkan pada evaluasi ACOS domain sempit, dan klaim pemahaman opini harus diukur sebagai kelebihan di atas baseline ini. Pekerjaan lanjutan: verifikasi manusia atas label (κ), replikasi pada korpus independen, dan perbandingan model–baseline setelah bug metrik dirapikan.

## Daftar Pustaka

[4] R. Geirhos, J.-D. Jacobsen, C. Michaelis, R. Zemel, W. Brendel, M. Bethge, dan F. A. Wichmann, "Shortcut Learning in Deep Neural Networks," *Nature Machine Intelligence*, vol. 2, no. 11, hlm. 665–673, 2020.

[5] T. McCoy, E. Pavlick, dan T. Linzen, "Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in Natural Language Inference," dalam *Proc. ACL*, 2019.

[1] M. Pontiki, D. Galanis, J. Pavlopoulos, H. Papageorgiou, I. Androutsopoulos, dan S. Manandhar, "SemEval-2014 Task 4: Aspect Based Sentiment Analysis," dalam *Proc. SemEval*, 2014.

[2] B. Liu, *Sentiment Analysis and Opinion Mining*. Morgan & Claypool, 2012.

[3] H. Cai, R. Xia, dan J. Yu, "Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions," dalam *Proc. ACL-IJCNLP*, 2021, hlm. 340–350.

[6] W. Zhang, X. Li, Y. Deng, L. Bing, dan W. Lam, "A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges," *IEEE Trans. Knowl. Data Eng.*, 2022.

[7] B. Wilie, K. Vincentio, G. I. Hadiwijaya, J. B. Jie, M. C. Purwarianti, dan S. Aji, "IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding," dalam *Proc. AACL-IJCNLP*, 2020, hlm. 843–857.

[8] F. Koto, A. Rahimi, J. H. Lau, dan T. Baldwin, "IndoLEM and IndoBERT: A Benchmark Dataset and Pre-trained Language Model for Indonesian NLP," dalam *Proc. COLING*, 2020, hlm. 757–770.

## Lampiran A — Provenance angka (hapus sebelum submit)

| Angka | Sumber artefak | Bukti |
|---|---|---|
| 92.074 / 72.973 / 9.587 / 9.514; sentimen 49,77/38,93/11,30 | `reports/044_data/eda_summary.json`, `sentiment_counts.csv` (skrip `scripts/eda_044_appsid.py`) | E2 |
| B1 50,33% · B2 59,93% · dev 60,74% · Tabel 2 seluruh kolom | `scripts/eda_053_majority_baseline_implisit.py` (12/11/2026), `reports/053_data/majority_baseline.csv` | E2 (hitungan baru) |
| "tidak bisa" 6.343 · "bagus" 5.246 | `reports/044_data/top_opinion_terms.csv` | E2 |
| Kelas netral sebagai kelas sisa (kualitatif) | wordcloud `reports/fig23`; `docs/0011` §4.5 | E2 (kualitatif) |
| Bug persistensi metrik sentimen 0,0 | `docs/0012` §4.2 | E2 (via 0012) |
| Label lemah, κ belum diukur | `reports/049` #2; `docs/0012` | E1 |
