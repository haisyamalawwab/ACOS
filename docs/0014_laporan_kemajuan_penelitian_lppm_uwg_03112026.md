# LAPORAN KEMAJUAN PENELITIAN

**Format:** mengikuti Lampiran 7 dan Lampiran 8 LPPM Universitas Widya Gama Malang — *Format halaman sampul laporan kemajuan (Laporan Penelitian 70%)* dan *Format Template Laporan Kemajuan (Laporan Penelitian 70%)*.
**Berkas acuan:** `LaporanKemajuanPenelitian.docx` (Google Drive, 39.703 bita).
**Tanggal penyusunan:** 03/11/2026.

**Catatan penomoran.** Dokumen ini semula bernomor 0013; nomor itu dipakai `docs/0013_laporan_penelitian_literatur_acos_acose_indobert_03112026.md`, sehingga berkas ini dinomori ulang menjadi 0014.

> **Catatan kesetiaan format.** Judul poin C sampai H, kalimat penjelas di setiap poin, dan urutan bagian dipertahankan apa adanya sesuai template; isian ditempatkan setelah kalimat penjelas. Bagian yang tidak ada pada berkas acuan (poin A dan B, serta lembar pengesahan) tidak ditambahkan.

---

## LAMPIRAN 7 — HALAMAN SAMPUL

Format sampul laporan kemajuan **berwarna merah muda**.

<div align="center">

FAKULTAS .....................

UNIVERSITAS WIDYA GAMA MALANG

November 2026

<br>

**TIM PENELITI**

(Nama ketua dan anggota tim, lengkap dengan gelar dan NIDN/NIDK/NIM)

<br>

**EKSTRAKSI KUADRUPLET ASPECT–CATEGORY–OPINION–SENTIMENT BERBAHASA INDONESIA PADA ULASAN BANK DIGITAL MENGGUNAKAN INDOBERT DUA TAHAP**

<br>

**LAPORAN KEMAJUAN**

**PROGRAM PENELITIAN DANA INTERNAL**

**PERINTIS**

</div>

---

## LAMPIRAN 8 — TEMPLATE LAPORAN KEMAJUAN

Pengisian poin C sampai dengan poin H mengikuti template berikut dan tidak dibatasi jumlah kata atau halaman namun disarankan seringkas mungkin. Dilarang menghapus/memodifikasi template ataupun menghapus penjelasan di setiap poin.

### C. HASIL PELAKSANAAN PENELITIAN

Tuliskan secara ringkas hasil pelaksanaan penelitian yang telah dicapai sesuai tahun pelaksanaan penelitian. Penyajian meliputi data, hasil analisis, dan capaian luaran (wajib dan atau tambahan). Seluruh hasil atau capaian yang dilaporkan harus berkaitan dengan tahapan pelaksanaan penelitian sebagaimana direncanakan pada proposal. Penyajian data dapat berupa gambar, tabel, grafik, dan sejenisnya, serta analisis didukung dengan sumber pustaka primer yang relevan dan terkini.

#### C.1 Capaian terhadap tahapan rencana

| Tahapan pada proposal | Target | Realisasi | Bukti |
|---|---|---|---|
| Pengumpulan data ulasan | 13 aplikasi bank digital | 43.673 ulasan bersih terkumpul | `reviews_clean.csv` |
| Praproses dan segmentasi klausa | Satu ulasan dipecah menjadi klausa | 76.077 klausa | `scripts/eda_044_appsid.py` |
| Anotasi kuadruplet ACOS | Empat elemen per tuple, termasuk `NULL` | 92.074 kuadruplet, 13 kategori, 3 sentimen | sama |
| Adaptasi IndoBERT tahap 1 | Ekstraksi rentang aspek dan opini | Model terlatih, micro-F1 81,27% | `notebooks/02` sel 13 |
| Adaptasi IndoBERT tahap 2 | Klasifikasi kategori dan sentimen | Model terlatih, F1 67,69% | sesi `appsid_24092026_0901` |
| Analisis data eksploratif | Profil sumber dan hasil | Selesai, 4 gambar | `reports/044`, `reports/fig21`–`fig23` |
| Penyusunan draf artikel | Draf sesuai kaidah SINTA 2 | Draf lengkap 410 baris, 8 tabel, 24 rujukan | `reports/045` |

#### C.2 Data penelitian

Dataset akhir terdiri atas tiga bagian dengan sebaran sebagai berikut.

| Bagian | Klausa | Kuadruplet |
|---|---:|---:|
| Latih | 60.159 | 72.973 |
| Dev | 8.027 | 9.587 |
| Uji | 7.891 | 9.514 |
| **Total** | **76.077** | **92.074** |

Data berasal dari ulasan publik 13 aplikasi bank digital Indonesia. Setiap tuple memuat empat elemen: span aspek, kategori, span opini, dan sentimen. Unsur yang tidak memiliki rentang teks ditandai `NULL`, sesuai konvensi tugas ACOS [1].

Profil data sumber menunjukkan tiga ciri yang perlu dilaporkan apa adanya:

| Ciri | Nilai | Implikasi |
|---|---:|---|
| Baris uji yang berbagi teks dengan data latih | 14,66% | Klaim generalisasi harus dibatasi |
| Istilah aspek unik | 362 | Kosakata tertutup, sulit menangkap istilah baru |
| Istilah opini unik | 202 | Sama |
| Klausa opini yang memuat negasi | 16,68% | Risiko kesalahan polaritas pada kalimat bernegasi |

#### C.3 Hasil model

Tahap 1 mengekstraksi rentang aspek dan opini menggunakan IndoBERT dengan kepala CRF enam label (`[CLS]`, `O`, `B-A`, `I-A`, `B-O`, `I-O`) serta dua kepala klasifikasi untuk aspek dan opini implisit. Penggunaan CRF pada tugas sekuens berbahasa Indonesia pernah dilaporkan menurunkan galat dependensi label sebesar 7% pada domain keuangan [2]. Tahap 2 mengklasifikasi kategori dan sentimen atas pasangan kandidat aspek–opini.

| Metrik | Tahap 1 (rest16) | Tahap 2 (appsid) |
|---|---:|---:|
| Micro-F1 | 81,27% | 67,69% |
| Presisi | 78,16% | — |
| Recall | 84,64% | — |
| Epoch terbaik | 8 dari 15 | 12 dari 15 |
| TP / FP / FN | — | 6.681 / 4.052 / 2.325 |

Dekomposisi atas 15 sub-tugas memperlihatkan penurunan bertahap: 91,08% ketika hanya satu elemen harus diprediksi, turun menjadi 66,08% ketika keempat elemen harus diprediksi bersama. Elemen terlemah adalah sentimen (85,72%). Pola ini sejalan dengan literatur bahwa pengaitan relasi antarelemen lebih sulit daripada pengenalan rentang, dan bahwa unsur implisit adalah sumber kesalahan utama [1], [3], [4].

Arsitektur lengkap dua tahap disajikan pada Gambar 1.

**Gambar 1.** Diagram arsitektur ACOS-IndoBERT dua tahap: (kiri) tahap 1 dengan CRF enam label dan dua kepala implisit; (tengah) jembatan pasangan kandidat; (kanan) tahap 2 dengan kepala multi-label 39 kelas. Berkas: `reports/fig24/fig24_arsitektur_acos_indobert_detail.png`.

Profil data hasil dan komponen ACOS disajikan pada Gambar 2 sampai Gambar 4.

**Gambar 2.** Sebaran data sumber Apps-ACOS. Berkas: `reports/fig21/fig21_eda_sumber_appsid.png`.

**Gambar 3.** Word cloud istilah aspek dan opini. Berkas: `reports/fig22/fig22_wordcloud_acos.png`.

**Gambar 4.** Word cloud sentimen. Berkas: `reports/fig23/fig23_wordcloud_sentimen.png`.

#### C.4 Analisis dan posisi terhadap pustaka terkini

Pemilihan IndoBERT dapat dipertahankan dengan bukti empiris pada domain yang sama: pada 22.923 ulasan aplikasi blu, IndoBERT mencapai akurasi sekitar 0,87 dan AUC-ROC 0,89, mengungguli CNN dan SVM [5]; pada ulasan bank syariah, akurasi 88% berbanding 78% untuk Naive Bayes [6]; pada 10.159 ulasan, akurasi klasifikasi aspek mencapai 99% dengan F1 sentimen 84–96% pada tiga aspek utama [7]. Skema hibrida IndoBERT–LLaMA dilaporkan mencapai akurasi 0,950 dan Macro F1 0,862 pada 5.513 ulasan mobile banking [8].

Namun hasil tersebut tidak sebanding dengan angka penelitian ini. Seluruh studi di atas mengukur klasifikasi sentimen atau aspek, bukan pencocokan kuadruplet secara tepat. Pada tugas kuadruplet, baseline pipeline dua tahap hanya mencapai 44,6% dan 35,8% pada benchmark asal [1]. Karena itu, angka 67,69% pada domain Indonesia dilaporkan sebagai hasil domain-spesifik, bukan sebagai state of the art.

Tiga hal yang membatasi klaim hasil dilaporkan terbuka:

| Batasan | Uraian | Status penanganan |
|---|---|---|
| Seleksi *checkpoint* pada himpunan uji | Evaluasi uji dijalankan di dalam siklus epoch, sehingga angka yang dilaporkan adalah maksimum atas 15 evaluasi | Belum diperbaiki; dampak terukur 0,07–0,56 poin |
| Kebocoran teks 14,66% | Baris uji berbagi teks dengan data latih | Belum diperbaiki |
| Kosakata tertutup | 362 istilah aspek dan 202 istilah opini | Belum diperbaiki |

Dampak batasan pertama diukur dari deret epoch yang tersimpan, bukan diperkirakan: pada tahap 1, F1 maksimum 81,27% dibandingkan 80,71% pada epoch terakhir (selisih 0,56 poin); pada tahap 2, 48,24% dibandingkan 48,17% (selisih 0,07 poin). Dengan demikian, perbaikan protokol tetap wajib dilakukan, tetapi tidak mengubah kesimpulan secara besar.

### D. STATUS LUARAN

Tuliskan jenis, identitas dan status ketercapaian setiap luaran wajib dan luaran tambahan (jika ada) yang dijanjikan. Jenis luaran dapat berupa publikasi, perolehan kekayaan intelektual, hasil pengujian atau luaran lainnya yang telah dijanjikan pada proposal. Uraian status luaran harus didukung dengan bukti kemajuan ketercapaian luaran sesuai dengan luaran yang dijanjikan. Lengkapi isian jenis luaran yang dijanjikan serta mengunggah bukti dokumen ketercapaian luaran wajib dan luaran tambahan melalui BIMA.

| Jenis luaran | Identitas yang dijanjikan | Status ketercapaian | Bukti |
|---|---|---|---|
| Publikasi ilmiah (luaran wajib) | Artikel pada jurnal nasional terakreditasi SINTA 2 | **Sebagian** — draf lengkap, belum diajukan | `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md` (410 baris, 8 tabel, 4 gambar, 24 rujukan) |
| Dataset (luaran tambahan) | Dataset kuadruplet ACOS berbahasa Indonesia | **Tercapai (internal)** — belum dipublikasikan | `data/Apps-ACOS/appsid_quad_train.tsv`, `_dev`, `_test` (92.074 tuple) |
| Kode dan model (luaran tambahan) | Pipeline dua tahap dan bobot model | **Tercapai (internal)** | `Extract-Classify-ACOS/`, bobot pada arsip sesi pelatihan |
| Dokumentasi ilmiah (luaran tambahan) | Laporan penelitian dan audit evaluasi | **Tercapai** | `docs/0011`, `docs/0012`, `reports/041`–`047` |

Keterangan status publikasi: draf artikel sudah memuat judul dua bahasa, abstrak dua bahasa, struktur IMRaD, dan lampiran kesesuaian SINTA 2. Yang belum selesai: pengisian metadata penulis, penyisipan DOI pada 24 rujukan, dan penyelarasan abstrak laporan lama yang masih memuat angka sebelum audit.

### E. PERAN MITRA

Tuliskan realisasi kerjasama dan kontribusi Mitra baik in-kind maupun in-cash (untuk Penelitian Terapan, Penelitian Pengembangan, PTUPT, PPUPT serta KRUPT). Bukti pendukung realisasi kerjasama dan realisasi kontribusi mitra dilaporkan sesuai dengan kondisi yang sebenarnya. Bukti dokumen realisasi kerjasama dengan Mitra diunggah melalui BIMA.

Penelitian ini **tidak melibatkan mitra kerja sama formal**, sehingga tidak ada kontribusi in-kind maupun in-cash yang dapat dilaporkan. Objek penelitian adalah ulasan publik pada kanal toko aplikasi, bukan data yang diperoleh dari perusahaan perbankan. Konsekuensi metodologisnya dinyatakan terbuka: tidak ada validasi pakar industri terhadap label, dan tidak ada umpan balik operasional atas temuan.

### F. KENDALA PELAKSANAAN PENELITIAN

Tuliskan kesulitan atau hambatan yang dihadapi selama melakukan penelitian dan mencapai luaran yang dijanjikan, termasuk penjelasan jika pelaksanaan penelitian dan luaran penelitian tidak sesuai dengan yang direncanakan atau dijanjikan.

| Kendala | Uraian | Dampak pada luaran |
|---|---|---|
| Keterbatasan akses GPU | Pelatihan ulang tidak dapat dijalankan pada lingkungan penyusunan laporan; seluruh angka berasal dari keluaran tersimpan | Perbaikan protokol evaluasi tertunda |
| Cacat protokol evaluasi | Evaluasi uji berjalan di dalam siklus epoch | Angka yang dilaporkan bersifat batas atas |
| Artefak pelatihan tersebar | Sebagian keluaran hanya tersimpan di penyimpanan awan, bukan di repositori | Beberapa angka tidak dapat diuji ulang per epoch |
| Anotasi berbasis label lemah | Sebagian label berasal dari aturan dan model bahasa, bukan anotator penuh | Kualitas label belum terukur dengan kesepakatan antaranotator |
| Metadata rujukan | Sebagian rujukan belum memiliki DOI yang terverifikasi | Artikel belum siap submit |

Pelaksanaan penelitian tidak menyimpang dari rencana pada tahap pengumpulan data, praproses, dan pemodelan. Penyimpangan terjadi pada tahap pelaporan: luaran publikasi yang ditargetkan selesai pada tahun berjalan baru berstatus draf.

### G. RENCANA TAHAPAN SELANJUTNYA

Tuliskan dan uraikan rencana penelitian di tahun berikutnya berdasarkan indikator luaran yang telah dicapai, rencana realisasi luaran wajib yang dijanjikan dan tambahan (jika ada) di tahun berikutnya serta roadmap penelitian keseluruhan. Pada bagian ini diperbolehkan untuk melengkapi penjelasan dari setiap tahapan dalam metoda yang akan direncanakan termasuk jadwal berkaitan dengan strategi untuk mencapai luaran seperti yang telah dijanjikan dalam proposal. Jika diperlukan, penjelasan dapat juga dilengkapi dengan gambar, tabel, diagram, serta pustaka yang relevan. Jika laporan kemajuan merupakan laporan pelaksanaan tahun terakhir, pada bagian ini dapat dituliskan rencana penyelesaian target yang belum tercapai.

| Tahap | Kegiatan | Indikator selesai | Sasaran waktu |
|---|---|---|---|
| 1 | Perbaikan protokol: evaluasi dev di dalam siklus epoch, evaluasi uji sekali di akhir; pelatihan ulang dan pelaporan angka terkoreksi | Angka baru dengan protokol bersih | Bulan 1–2 |
| 2 | Deduplikasi lintas split dan pelaporan ulang setelah kebocoran 14,66% dihapus | Dataset bersih dan tabel dampak | Bulan 2–3 |
| 3 | Pelaporan ganda: F1 parsial dan *exact match* berdampingan, termasuk penanganan `NULL` | Tabel hasil revisi | Bulan 3 |
| 4 | Penyelesaian artikel: DOI 24 rujukan, metadata penulis, penyelarasan abstrak | Naskah siap submit ke jurnal SINTA 2 | Bulan 3–4 |
| 5 | Perluasan data: penambahan periode dan bank agar uji lintas waktu dapat dilakukan | Protokol uji lintas waktu | Bulan 5–6 |
| 6 | Perancangan ACOSE: penambahan elemen emosi diskret, pemicu emosi, dan intensitas | Skema anotasi dan studi kelayakan | Bulan 7–12 |

Arah jangka panjang penelitian ini mengikuti celah yang terdokumentasi pada literatur. ACOS menyelesaikan struktur empat unsur, tetapi tidak mengkodekan emosi, pemicu emosi, atau intensitas [3], [9]. Padahal emosi diskret memprediksi perilaku pengguna secara berbeda: kemarahan pada kegagalan layanan memprediksi keluhan, *word of mouth* negatif, dan perpindahan penyedia [10]. Pengembangan menuju ACOSE, yaitu penambahan elemen emosi pada struktur kuadruplet, merupakan kelanjutan yang wajar dan sudah dirintis pada literatur melalui pemodelan multi-tugas berbasis model bahasa besar [11] dan integrasi ruang afektif berdimensi [12]. Roadmap tersebut ditempatkan pada tahun berikutnya, bukan pada laporan ini, karena membutuhkan data berlabel baru.

### H. DAFTAR PUSTAKA

Penyusunan Daftar Pustaka berdasarkan sistem nomor sesuai dengan urutan pengutipan. Hanya pustaka yang disitasi pada laporan kemajuan yang dicantumkan dalam Daftar Pustaka.

1. Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. *Proceedings of ACL-IJCNLP 2021*, 340–350. https://doi.org/10.18653/v1/2021.acl-long.29
2. Dave, E., & Chowanda, A. (2024). IPerFEX-2023: Indonesian personal financial entity extraction using IndoBERT-BiGRU-CRF model. *Journal of Big Data*, 11. https://doi.org/10.1186/s40537-024-00987-6
3. Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Computing Surveys*, 58. https://doi.org/10.1145/3799234
4. Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *IJCNN 2023*, 1–8. https://doi.org/10.1109/ijcnn54540.2023.10191098
5. Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. *Journal of Applied Informatics and Computing*. https://doi.org/10.30871/jaic.v10i2.12436
6. Assani, M. Y., Rudiyan, A., & Radiyah, U. (2025). NLP-Based Sentiment Analysis of Islamic Mobile Banking Reviews for Digital Service Quality Enhancement. *Jurnal Bumigora Information Technology*, 7(2). https://doi.org/10.30812/bite.v7i2.5943
7. Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. *ICDSG 2025*, 37–42. https://doi.org/10.1109/icdsg67714.2025.11381388
8. Natalia, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. *ICCMC 2026*, 2002–2007. https://doi.org/10.1109/iccmc69250.2026.11624719
9. Zhang, W., et al. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review*, 57. https://doi.org/10.1007/s10462-023-10633-x
10. Zeelenberg, M., & Pieters, R. (2004). Beyond valence in customer dissatisfaction: a review and new findings on behavioral responses to regret and disappointment in failed services. *Journal of Business Research*, 57, 445–455. (DOI tidak tercatat pada berkas acuan)
11. Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. *arXiv*. https://doi.org/10.48550/arxiv.2511.19122
12. D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. *Artificial Intelligence Review*, 55, 5543–5574. https://doi.org/10.1007/s10462-021-10134-9

---

## LAMPIRAN TAMBAHAN — Daftar Berkas Bukti

Bagian ini bukan bagian dari template LPPM; disertakan hanya sebagai rujukan berkas bukti yang akan diunggah melalui BIMA.

| Keperluan | Berkas |
|---|---|
| Dataset dan hasil EDA | `scripts/eda_044_appsid.py`, `reports/044_data/`, `reports/044_eda...md` |
| Keluaran model | `notebooks/02_...ipynb` (sel 11, 13), `notebooks/04_...ipynb` (sel 10, 12) |
| Audit evaluasi | `reports/046_verifikasi_jalur_a_02112026_HM.md`, `reports/042_kesiapan_publikasi_q2_s2_02112026_HM.md` |
| Draf artikel | `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md` |
| Laporan penelitian | `docs/0011_laporan_penelitian_acos_indobert_02112026.md`, `docs/0013_laporan_penelitian_literatur_acos_acose_indobert_03112026.md` |
| Gambar | `reports/fig24/`, `reports/fig21/`, `reports/fig22/`, `reports/fig23/` |
