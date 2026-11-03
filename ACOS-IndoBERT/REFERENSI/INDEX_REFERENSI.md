# Indeks dan Pemetaan Referensi — ACOS-IndoBERT

> **Tanggal survei:** 3 November 2026
> **Ruang lingkup:** seluruh berkas Markdown di `ACOS-IndoBERT/REFERENSI/`
> **Catatan path:** nama direktori di repo adalah `REFERENSI` (bukan `REFERENCE` atau `REFERENCES`). Indeks ini tidak mengubah nama direktori maupun isi dokumen sumber.

## Daftar isi indeks

- [Navigasi cepat](#1-navigasi-cepat)
- [Daftar isi semua dokumen Markdown](#2-daftar-isi-semua-dokumen-markdown)
- [Peta isi dan jenis bukti](#3-peta-isi-dan-jenis-bukti)
- [Audit konsistensi dan prioritas perbaikan](#4-audit-konsistensi-dan-prioritas-perbaikan)
- [Batas survei](#5-batas-survei)

---

## 1. Navigasi cepat

| Dokumen | Fokus | Ukuran / struktur | Jumlah entri pustaka |
|---|---|---|---:|
| [Analisis IndoBERT 13 BANK DIGITAL.md](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md) | Sintesis literatur IndoBERT, ABSA/ACOS, kualitas layanan, emosi, generalisasi, dan gap studi 13 bank | 264 baris; 5 bagian utama, subbagian hasil/gap | 62 DOI |
| [IndoBERT 13 Bank Belum Ada.md](./IndoBERT%2013%20Bank%20Belum%20Ada.md) | Ringkasan klaim efektivitas IndoBERT, benchmark layanan digital, dan keterbatasan bukti 13-bank | 88 baris; 3 bagian utama | 20 DOI |

**Cakupan pustaka statis:** 82 kemunculan DOI di dua dokumen; 10 DOI berulang di keduanya; **72 DOI unik** setelah deduplikasi lintas dokumen. Penghitungan ini memeriksa pola DOI yang tertulis, bukan memverifikasi bahwa metadata/DOI benar-benar cocok dengan rekaman penerbit.

---

## 2. Daftar isi semua dokumen Markdown

### 2.1 `Analisis IndoBERT 13 BANK DIGITAL.md`

- [Introduction](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#1-introduction)
- [Methods](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#2-methods)
- [Results](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#3-results)
  - [Key Papers](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#31-key-papers)
  - [Performa Model](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#32-performa-model)
  - [Temuan Substantif Perbankan](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#33-temuan-substantif-perbankan)
  - [Opinion dan Emotion](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#34-opinion-dan-emotion)
  - [Results Timeline](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#results-timeline)
  - [Top Contributors](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#top-contributors)
- [Discussion](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#4-discussion)
- [Conclusion](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#5-conclusion)
  - [Research Gaps](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#research-gaps)
  - [Open Research Questions](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#open-research-questions)
- [References](./Analisis%20IndoBERT%2013%20BANK%20DIGITAL.md#references)

### 2.2 `IndoBERT 13 Bank Belum Ada.md`

- [Keunggulan IndoBERT dalam ABSA Perbankan](./IndoBERT%2013%20Bank%20Belum%20Ada.md#keunggulan-indobert-dalam-absa-perbankan)
- [Benchmark Model pada Domain Layanan Digital Indonesia](./IndoBERT%2013%20Bank%20Belum%20Ada.md#benchmark-model-pada-domain-layanan-digital-indonesia)
- [Keterbatasan dan Tantangan untuk 13 Bank Digital](./IndoBERT%2013%20Bank%20Belum%20Ada.md#keterbatasan-dan-tantangan-untuk-13-bank-digital)
- [References](./IndoBERT%2013%20Bank%20Belum%20Ada.md#references)

---

## 3. Peta isi dan jenis bukti

| Tema | Lokasi utama | Jenis bukti / fungsi | Batas interpretasi |
|---|---|---|---|
| IndoBERT untuk ABSA Indonesia | Dokumen panjang §3.2; dokumen ringkas §Keunggulan dan tabel benchmark | Hasil dari tugas/domain Indonesia yang berdekatan: perbankan, fintech, layanan publik, e-commerce | Dataset, task, split, kelas, dan metrik berbeda; angka akurasi/F1/AUC bukan benchmark head-to-head. |
| Perbankan digital dan kualitas layanan | Dokumen panjang §3.3–4; dokumen ringkas benchmark | Pola keluhan reliability, login/verifikasi, transaksi, performa, layanan pelanggan; topik kualitas layanan | Bukti observasional tidak membuktikan kausalitas atau dampak intervensi pada retensi/kepuasan. |
| Multi-bank / generalisasi lintas bank | Dokumen panjang §Introduction, §3.3, §Research Gaps, §Open Research Questions; dokumen ringkas §Keterbatasan | Menyatakan gap penelitian komparatif yang mencakup 13 bank sekaligus | Perlu mendefinisikan daftar 13 bank, periode, platform, dan rancangan transfer/evaluasi lintas-bank. |
| ACOS / quadruple | Dokumen panjang §3.4; sitasi Cai et al. (2021), Zhang et al. (2022, 2024) | Dasar konseptual untuk aspect-category-opinion-sentiment dan implicit slots | Bukan bukti bahwa model ACOS untuk 13 bank telah dievaluasi oleh paper yang disitasi. |
| Emosi | Dokumen panjang §3.4, Discussion, evidence-strength table | Benchmark emosi bahasa Indonesia dan literatur finansial terkait | Bukti perbankan Indonesia lebih tipis; perlu membuktikan emosi menambah sinyal di luar sentimen. |
| Weak label dan validitas | Kedua dokumen; khususnya dokumen panjang §Introduction/Discussion dan ringkasan §Keterbatasan | Peringatan tentang rating/pseudo-label, imbalance, domain/time shift | Perlu mengaitkan tiap angka hasil ke skema label, ukuran sampel, split, dan metrik primer. |
| Privasi/etika | Dokumen panjang §Discussion | Rujukan pada risiko re-identifikasi dan etika data ulasan | Belum menjadi protokol operasional spesifik bagi pengumpulan dan penyimpanan Apps-ACOS. |
| Kausalitas bisnis | Dokumen panjang §Discussion dan §Open Research Questions | Mengidentifikasi bahwa klaim dampak bisnis langsung masih lemah | Tidak ada desain intervensi/kausal yang dirangkum untuk menyatakan ABSA meningkatkan loyalitas atau kinerja bank. |

---

## 4. Audit konsistensi dan prioritas perbaikan

### P0 — Keterlacakan metode tinjauan

Dokumen panjang menyatakan `Retrieved 1.1M → Eligible 399 → Included 100`, tetapi belum memberi tanggal pencarian, query lengkap, kriteria inklusi/eksklusi, alur deduplikasi, cara screening, atau daftar studi yang termasuk. Daftar pustaka memuat 62 entri dan timeline hanya merangkum 20 studi; relasi antara tiga jumlah ini belum dijelaskan. Perlakukan angka tersebut sebagai klaim laporan pencarian, bukan hitungan systematic review yang dapat diaudit, sampai log pencarian dan daftar screening tersedia.

### P0 — Referensi yang perlu dikoreksi sebelum sitasi akademik

1. Pada dokumen panjang, isi mengutip **Dhendra (2025)**, sedangkan entri bibliografi pertama tertulis hanya **`D. (2025)`**. Nama penulis tidak lengkap dan tidak bisa dicocokkan dari format yang ada.
2. Entri Jazuli ditulis `Jazuli, A., W., & Kusumaningrum, R.` pada kedua dokumen; format nama/inisial tampak rusak atau tidak standar. Cocokkan dengan metadata penerbit.
3. Entri Wijaya pada dokumen ringkas berakhir `& D.`; nama/inisial penulis tidak lengkap.
4. Judul Assani memuat `Mobile BankingReviews` tanpa spasi pada kedua dokumen.
5. Dokumen ringkas mengutip “Table 6” dari Jazuli et al. (2024), tetapi tabel yang dimaksud tidak disertakan; jangan gunakan kalimat itu sebagai bukti hasil tanpa membuka paper sumber dan menunjuk tabel yang benar.

Temuan di atas adalah audit teks bibliografi; **validitas semua DOI dan metadata belum dicek terhadap penerbit/Crossref**.

### P1 — Hati-hati membandingkan angka performa

Tabel benchmark mencampur akurasi aspek, akurasi klasifikasi, F1, AUC, task single-/multi-label, dan dataset berbeda. Beri kolom minimal: paper/DOI, domain/platform, ukuran data, unit analisis, label dan sumbernya, split, task/head, metrik persis, baseline, serta hasil utama. Hindari menyimpulkan “IndoBERT terbaik” dari perbandingan angka lintas paper yang setup-nya berbeda.

### P1 — Aset dan struktur dokumen

- Caption Figure 1–6 di dokumen panjang dan Figure 1–2 di dokumen ringkas tidak disertai gambar atau tautan gambar; saat ini itu placeholder, bukan figur yang dapat diperiksa.
- Kedua dokumen memiliki 10 DOI yang sama. Tetapkan satu dokumen sebagai sintesis utama dan jadikan yang lain ringkasan/brief; hindari dua versi klaim yang berubah tanpa riwayat.
- Catatan Consensus pada kedua dokumen menyebut penggunaan personal/nonkomersial dan bahwa redistribusi memerlukan izin pemegang hak. Periksa izin dan ketentuan sebelum memaketkan atau menerbitkan ulang teks/hasil pencarian tersebut.
- Tinjauan ini belum menautkan setiap klaim kuantitatif ke lokasi spesifik dalam sumber (tabel/halaman/section); tambahkan locator supaya audit klaim lebih cepat.

### P2 — Rencana penguatan isi

1. Simpan query, tanggal, database/sumber, hasil ekspor, dedup log, screening dua reviewer, dan daftar studi excluded/included.
2. Buat master bibliography BibTeX/RIS/CSL JSON dengan DOI, judul, penulis lengkap, venue, tahun, status publikasi, dan URL penerbit.
3. Buat claim-to-source matrix: klaim, sitasi, halaman/tabel sumber, metode sumber, batasan, dan tingkat relevansi untuk Apps-ACOS.
4. Pisahkan evidence langsung (bank digital Indonesia/ABSA) dari evidence berdekatan (e-commerce, transportasi, paper metode umum, negara lain).
5. Tambahkan gambar aktual atau hapus caption placeholder; periksa kembali konsistensi nomor Figure/Table.
6. Tambahkan kesimpulan operasional khusus proyek: apa yang dapat ditransfer ke dataset 13 bank, apa yang perlu diuji ulang, dan apa yang sama sekali belum didukung bukti.

---

## 5. Batas survei

Survei ini menghitung struktur heading, pola DOI, overlap daftar pustaka, dan konsistensi teks di dua berkas Markdown. Survei ini **tidak** mengklaim telah memverifikasi keberadaan, metadata, peer-review status, atau akurasi angka di setiap paper terhadap situs penerbit. Untuk penggunaan tesis/paper, verifikasi bibliografi satu per satu tetap diperlukan.
