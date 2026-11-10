# Audit Ulang `ACOS-IndoBERT/REFERENCES/` — Verifikasi Indeks, Duplikasi, dan Kelayakan Sitasi

> Tanggal: 4 November 2026  
> Penyusun: Arena AI (mode profesor reviewer / lead researcher)  
> Sifat: audit read-only terhadap sumber; laporan ini adalah satu-satunya perubahan yang diusulkan pada PR.  
> Indeks yang diaudit: `ACOS-IndoBERT/REFERENCES/INDEX_REFERENCES.md` dan indeks saudara `ACOS-IndoBERT/REFERENSI/INDEX_REFERENSI.md`.

## 1. Ringkasan eksekutif

Indeks `REFERENCES/` terbukti akurat secara inventaris: seluruh angka jumlah berkas, heading, DOI per dokumen, dan tautan/anchor yang diklaim indeks cocok dengan hasil audit ulang. Namun, kelayakan folder ini sebagai basis sitasi artikel SINTA 2 masih tertahan oleh empat masalah substansial: (1) 501 DOI belum diverifikasi eksternal dan terdapat entri bibliografi rusak; (2) 19 PDF bukan paper primer melainkan ekspor aplikasi Consensus/cetak-ulang tinjauan Markdown; (3) duplikasi/near-duplikat antar dokumen dan PDF belum ditetapkan versi kanoniknya; (4) 127 caption Figure/Table berdiri tanpa gambar tertanam. Laporan ini tidak mengubah berkas sumber; ia hanya mendokumentasikan temuan dan urutan perbaikan.

## 2. Metode audit

Audit dilakukan secara read-only dengan langkah terukur:

- Inventaris berkas `.md` dan `.pdf` pada `REFERENCES/`, serta pembanding pada `REFERENSI/`.
- Hash SHA-256 untuk deteksi duplikat identik.
- Ekstraksi pola DOI (`10.xxxx/...`) dan deduplikasi case-insensitive; hitungan unik-per-dokumen dan unik-global.
- Uji kemiripan teks (`difflib.SequenceMatcher`) pada teks ternormalisasi, dengan dan tanpa marker Markdown.
- Pemeriksaan tautan dan anchor indeks terhadap berkas/heading aktual.
- Metadata dan ekstraksi teks PDF memakai `pypdf` 6.21.4 (venv sementara, tidak mengubah repo).
- Pencarian pola bibliografi rusak dan klaim funnel `Retrieved/Eligible/Included`.

Batas metode: audit ini tidak memverifikasi keberadaan/metadata DOI ke Crossref atau penerbit; angka DOI adalah hitungan pola teks. Ekstraksi teks PDF dapat meleset untuk halaman hasil pindai, tetapi metadata dan sampel teks konsisten.

## 3. Verifikasi klaim indeks

| Klaim indeks | Hasil audit | Status |
|---|---|---|
| 27 MD sumber + 19 PDF | 27 MD sumber + 19 PDF (28 MD termasuk indeks) | Cocok |
| 17 MD ber-heading, 10 tanpa heading | 17 ber-heading, 10 tanpa heading | Cocok |
| 844 DOI unik-per-dokumen; 501 DOI unik global | 844; 501 | Cocok |
| Hitungan DOI per dokumen (27 baris tabel) | 0 mismatch dari 27 | Cocok |
| 254 tautan/anchor indeks | 0 rusak | Cocok |
| Duplikat identik `ABSA Bank Digital.md` = `Deep Critical and Mapping ABSA.md` | Hash SHA-256 sama | Cocok |
| Duplikat lintas-folder `Limitation ACOS.md` = `ACOS Menangkap Struktur Implicit Explicit BUKAN EMOSI.md` | Hash SHA-256 sama | Cocok |

Kesimpulan: indeks layak dipertahankan sebagai inventaris kanonik. Masalah ada pada isi dan kelayakan pakai sumber, bukan pada akurasi indeks.

## 4. Temuan dan rencana perbaikan

| # | Severity | Temuan | Akar masalah | Solusi konkret | Effort |
|---|---|---|---|---|---|
| T1 | BLOCKER (untuk submit) | 501 DOI belum diverifikasi eksternal; 66 DOI (13,2%) berprefix arXiv `10.48550` (preprint). Entri rusak: `D. (2025). Benchmarking IndoBERT…` pada `Analisi IndoBERT.md:157` dan `Literature ACOSE.md:216`; format penulis `Jazuli, A., W., & Kusumaningrum, R.` pada `ABSA Bank Digital.md:168`, `ACOSE Paling Kuat.md:95`, `Analisi IndoBERT.md:186`, `Deep Critical and Mapping ABSA.md:168`, `Literature ACOSE.md:230`; judul `…Mobile BankingReviews…` tanpa spasi pada `Analisi IndoBERT.md:169` dan `IndoBERT Unggul.md:33`. | Bibliografi disalin sebagai teks/DOI, bukan metadata terkurasi. | Bangun master bibliography `.bib`/RIS/CSL-JSON; verifikasi tiap DOI ke Crossref/penerbit; lengkapi nama penulis dan perbaiki judul; tandai preprint dan jangan perlakukan setara peer-reviewed. | Sedang–besar |
| T2 | MAYOR | 19 PDF bukan paper primer: metadata Title="Consensus", Producer="Skia/PDF m142"; sebagian adalah cetak-ulang tinjauan Markdown yang sudah ada. Contoh: `ABOSA_….pdf` ≈ `TinjauanABSA.md` (rasio teks 0,945); `Relevansi_Kolerasi_….pdf` ≈ `Analisi IndoBERT.md` (0,940). | PDF hasil print-to-PDF dari tinjauan/pencarian, bukan naskah jurnal. | Perlakukan PDF sebagai laporan pencarian sekunder; untuk klaim kinerja, ambil PDF paper asli yang disitasi; jangan hitung PDF sebagai bukti independen. | Sedang |
| T3 | MAYOR | Duplikasi/near-duplikat belum kanonik: `ABSA Dual Extraction.md` ↔ `TinjauanABSA.md` (58 DOI identik; teks 0,922 mentah / 0,968 setelah marker dibuang); `Analisi IndoBERT.md` ↔ `REFERENSI/Analisis IndoBERT 13 BANK DIGITAL.md` (62 DOI identik; teks 0,959 / 0,979). Pasangan PDF `ACOS_ACOSQE_…(1).pdf` vs tanpa-(1) berteks identik (rasio 1,000) tetapi hash berbeda; `Current_fine-grained_…(1).pdf` vs tanpa-(1) justru berbeda isi (rasio 0,151). | Tidak ada versi kanonik; file (1) hasil unduh ganda. | Tetapkan satu kanonik per kelompok dan arsipkan sisanya; hapus duplikat PDF yang teksnya identik; beri nama berbeda untuk pasangan PDF yang isinya memang beda. | Kecil |
| T4 | MAYOR | 26 dokumen memuat 127 caption Figure/Table tetapi 0 gambar tertanam; semuanya placeholder. | Caption ditulis tanpa aset. | Sematkan gambar nyata dari `reports/fig*`/kode, atau hapus caption; sinkronkan dengan gambar di artikel. | Sedang |
| T5 | MINOR | Klaim funnel `Retrieved/Eligible/Included` (mis. "Included 100") tanpa query, tanggal, log screening, atau daftar studi included. | Format Consensus tidak menyertakan log yang bisa diaudit. | Turunkan klaim menjadi tinjauan naratif, atau lampirkan log pencarian + daftar included agar layak disebut systematic review. | Kecil |
| T6 | NIT | Typo nama berkas: `Quandruple` → `Quadruple`, `Analisi` → `Analisis`, `Kolerasi` → `Korelasi`. Kalimat indeks "dua pasangan near-duplicate lintas-folder" kurang presisi karena satu pasangan near-dup berada di dalam folder yang sama. | Penamaan manual dan kalimat cakupan duplikat. | Rename hati-hati + perbarui tautan indeks; luruskan kalimat cakupan duplikat. | Kecil |

Catatan: pola `D. (tahun)` yang tampak di banyak dokumen sebagian besar adalah inisial penulis yang sah (mis. "Renuka, D. (2021)") dan tidak dihitung sebagai entri rusak. Temuan T1 hanya menunjuk entri yang berdiri sendiri sebagai `D. (2025)` tanpa nama keluarga.

## 5. Rekomendasi urutan perbaikan

1. Kunci kelayakan sitasi (T1): bangun master bibliography terverifikasi; perbaiki entri rusak yang sudah ditunjuk lokatornya; tandai preprint.
2. Bersihkan duplikat dan tetapkan kanonik (T3) supaya tidak ada double-counting bukti.
3. Reposisi PDF (T2) sebagai sekunder; ambil paper asli untuk klaim kinerja.
4. Lengkapi atau hapus caption placeholder (T4) dan log funnel (T5).
5. Perapihan nama/indeks (T6) terakhir.

## 6. Batas keyakinan

- Keberadaan, metadata, status peer-review, dan akurasi angka pada 501 DOI belum diverifikasi terhadap penerbit/Crossref.
- Rasio kemiripan teks bergantung normalisasi; yang pasti adalah set DOI identik untuk pasangan near-dup.
- Ekstraksi teks PDF bisa meleset untuk halaman hasil pindai; namun metadata + sampel teks konsisten menunjukkan ekspor Consensus.
- Audit ini tidak mengubah berkas sumber, tidak menghapus duplikat, dan tidak memverifikasi gambar/placeholder secara visual.

## 7. Kesimpulan

`REFERENCES/` memiliki indeks yang dapat dipercaya, tetapi belum siap menjadi basis sitasi final tanpa verifikasi bibliografi eksternal, pembersihan duplikat, reposisi PDF sekunder, dan penyelesaian caption placeholder. Perbaikan sebaiknya dilakukan bertahap sesuai urutan pada Bagian 5, dengan T1 sebagai prasyarat sebelum submit artikel.
