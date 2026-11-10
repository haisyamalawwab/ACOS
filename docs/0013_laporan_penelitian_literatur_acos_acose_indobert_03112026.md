# Laporan Penelitian — ACOS dan Arah ACOSE pada Ulasan Bank Digital Indonesia: Sintesis Literatur dan Bukti Empiris

**Tanggal:** 03/11/2026
**Disusun oleh:** HM
**Sumber utama:** 13 catatan riset di Google Drive (`Labeling ACOS`, `Ekstraksi Quandruple ACOS`, `Limitation ACOS`, `ACOS dan ACOSE Analisis Sentimen`, `Analisi IndoBERT`, `IndoBERT Unggul`, `ACOSE Paling Kuat`, `Literature ACOSE`, `Rekomendasi ACOSE`, `Integrasi ACOSE`, `Implementasi ACOSE`, `Analisis ACOS`, `ACOSQE Adalah Tugas Bukan Model`) dan 4 berkas PDF pendukung.
**Pelengkap:** berkas repositori ACOS (`docs/0011`, `reports/042`–`047`, kode `Extract-Classify-ACOS`, keluaran notebook tersimpan).
**Catatan penomoran.** Dokumen ini semula bernomor 0012; nomor itu sudah dipakai `docs/0012_laporan_penelitian_acos_indobert_03112026.md` (survey artefak, 03/11/2026), sehingga berkas ini dinomori ulang menjadi 0013.

**Legenda tingkat bukti.** **E2** = terverifikasi di repositori lewat kode, keluaran tersimpan, atau hitungan ulang. **E1** = dokumen repositori belum diverifikasi ulang. **D2** = klaim catatan Drive yang merujuk publikasi ber-DOI sehingga dapat ditelusuri. **D1** = klaim catatan Drive yang rujukannya tidak dirinci. **D0** = sintesis naratif mesin pencari Consensus, bukan temuan studi primer.

> **Putusan satu baris:** literatur mendukung bahwa ACOS menyelesaikan struktur empat unsur — bukan emosi, bukan intensitas — dan bahwa IndoBERT layak dipakai sebagai *encoder* domain bank digital Indonesia; **namun tidak satu pun catatan Drive memberi bukti bahwa ACOS berbahasa Indonesia sudah pernah dikerjakan**, sehingga kontribusi dataset Apps-ACOS berdiri pada celah yang nyata, dengan syarat tiga cacat evaluasi dibereskan sebelum diklaim.

---

## 1. Abstrak

Ekstraksi kuadruplet Aspect–Category–Opinion–Sentiment (ACOS) memformalkan pengaitan empat unsur opini menjadi satu struktur, termasuk ketika aspek atau opininya implisit (Cai et al., 2021). Laporan ini menyintesis 13 catatan literatur untuk menjawab tiga pertanyaan: sejauh mana bukti mendukung ACOS sebagai tugas, sejauh mana IndoBERT terbukti pada domain bank digital Indonesia, dan di mana letak batas ACOS yang membuka jalan ke ACOSE (penambahan elemen emosi).

Tiga temuan pokok. **Pertama**, bukti ACOS sebagai formulasi tugas kuat (8–9 dari 10 menurut penilaian catatan), sedangkan bukti bahwa satu arsitektur mengungguli seluruh arsitektur lain lemah — pemodelan terpadu hanya terbukti lebih baik daripada pipeline tertentu, bukan daripada semua (D2). **Kedua**, bukti IndoBERT pada ulasan bank digital Indonesia berlimpah untuk klasifikasi sentimen dan klasifikasi aspek, tetapi **tidak satu pun studi yang dirujuk mengerjakan kuadruplet ACOS berbahasa Indonesia**; studi yang ada berhenti pada polaritas, aspek, atau triplet (D2). **Ketiga**, batas ACOS bukan pada unsur implisit, melainkan pada lapisan antara polaritas dan perilaku: emosi diskret, pemicu emosi, dan intensitas (D2). Justru lapisan itulah yang punya nilai perilaku, karena emosi diskret memprediksi keluhan dan perpindahan pengguna secara berbeda-beda (D2).

Pada sisi empiris repositori, dataset Apps-ACOS berisi 43.673 ulasan, 76.077 klausa, dan 92.074 kuadruplet dengan 13 kategori dan 3 sentimen (E2). Kinerja yang dapat dipertahankan adalah 81,27% micro-F1 pada ekstraksi rentang dan 67,69% F1 pada klasifikasi kuadruplet (E2), dengan dua catatan penting: keduanya adalah skor maksimum atas 15 evaluasi himpunan uji, dan 14,66% baris uji berbagi teks dengan data latih (E2). Laporan ini tidak mengklaim hasil tingkat SOTA dan tidak menyatakan bahwa pipeline bebas cacat.

**Kata kunci:** ACOS, ACOSE, IndoBERT, bank digital Indonesia, ekstraksi kuadruplet, evaluasi kritis.

---

## 2. Ringkasan eksekutif

| # | Temuan | Tingkat bukti | Implikasi |
|---|---|---|---|
| 1 | ACOS memprediksi empat unsur yang saling terhubung, bukan empat daftar label terpisah | D2 (Cai et al., 2021; Zhang et al., 2024) | Metrik yang sah adalah *exact match*, bukan F1 unsur per unsur |
| 2 | Exact match mendominasi kesulitan: baseline Extract-Classify hanya 44,6% dan 35,8% pada benchmark asal | D2 | Angka 40–50 F1 adalah batas atas realistis untuk domain restoran/laptop |
| 3 | Tidak ada studi ACOS berbahasa Indonesia dalam korpus catatan | D1 (absen, bukan bukti absen) | Celah yang diklaim hanya sah bila dinyatakan sebagai "tidak ditemukan pada korpus ini" |
| 4 | IndoBERT unggul untuk sentimen dan aspek pada ulasan bank digital Indonesia | D2 (Casanova et al., 2026; Pardamean et al., 2025; Assani et al., 2025) | Pemilihan IndoBERT dapat dipertahankan dengan rujukan, bukan dengan asumsi |
| 5 | Bukti emosi perbankan Indonesia masih tipis dan sebagian berbasis leksikon | D2 | ACOSE harus diposisikan sebagai rencana, bukan hasil |
| 6 | ACOS tidak mengkodekan emosi, pemicu emosi, atau intensitas | D2 (Limitation ACOS, penilaian 8/10) | Kritik yang sah adalah kritik lapisan afektif, bukan kritik unsur implisit |
| 7 | Dataset Apps-ACOS: 43.673 ulasan, 76.077 klausa, 92.074 kuadruplet, 13 kategori | E2 (`eda_044_appsid.py`) | Kontribusi data nyata dan dapat dihitung ulang |
| 8 | Kinerja 81,27% dan 67,69% adalah maksimum atas 15 evaluasi uji, bukan hasil protokol dev | E2 (`notebooks/02` sel 11, `notebooks/04` sel 10) | Wajib dilaporkan sebagai batas atas, bukan angka netral |
| 9 | 14,66% baris uji berbagi teks dengan data latih | E2 | Klaim generalisasi harus dibatasi |
| 10 | Kosakata tertutup: 362 istilah aspek dan 202 istilah opini | E2 | Model tidak akan mengenali istilah baru di luar daftar |

---

## 3. BAB I — Pendahuluan

### 1.1 Latar belakang

Penambangan opini berbasis aspek berkembang dari polaritas dokumen menuju struktur yang makin kaya. ACOS adalah titik ketika empat unsur digabung menjadi satu kuadruplet (aspek, kategori, opini, sentimen) dan unsur implisit diakui sebagai bagian sah dari tugas (Cai et al., 2021). Formulasi yang sama juga disebut ASQP (Aspect Sentiment Quad Prediction); perbedaannya, dataset ASQP awal membuang kuadruplet dengan opini implisit, sehingga hasil kedua keluarga benchmark tidak otomatis sebanding (D2).

Catatan Drive menegaskan satu koreksi konseptual yang sering keliru dipakai dalam perbandingan: **ACOSQE adalah nama tugas, bukan nama model**, sehingga tidak dapat "dikalahkan" oleh model generatif; model generatif justru salah satu keluarga metode untuk menyelesaikannya (D2).

### 1.2 Rumusan masalah

1. Sejauh mana literatur mendukung klaim bahwa ACOS adalah formulasi tugas yang mapan, dan sejauh mana ia mendukung klaim keunggulan satu arsitektur?
2. Sejauh mana IndoBERT terbukti pada domain bank digital Indonesia, dan pada kedalaman tugas apa bukti itu berhenti?
3. Di mana batas ACOS yang membuka jalan ke ACOSE, dan bukti apa yang masih hilang untuk menjustifikasinya?

### 1.3 Tujuan

Menyusun peta bukti yang dapat dipakai dua arah: sebagai landsasan teoritis artikel ACOS berbahasa Indonesia, dan sebagai penentu apakah penambahan elemen emosi (ACOSE) layak dikerjakan sekarang atau harus menunggu.

### 1.4 Kontribusi

| Kontribusi | Sifat |
|---|---|
| Peta bukti literatur ACOS yang memisahkan klaim kuat, sedang, dan lemah | Sintesis, D2 |
| Peta bukti IndoBERT khusus domain bank digital Indonesia | Sintesis, D2 |
| Perumusan batas ACOS menuju ACOSE beserta urutan kerjanya | Rekomendasi, D0 |
| Penghubung antara literatur dan angka empiris repositori | Integrasi, E2 |

### 1.5 Batasan

1. Sumber literatur adalah catatan sintesis Consensus atas basis data pihak ketiga; catatan itu sendiri **bukan publikasi peer-review**, dan sebagian besar isinya merujuk paper yang baru terbit pada 2025–2026 sehingga belum punya riwayat sitasi panjang (D0).
2. Banyak klaim bersandar pada abstrak, bukan teks penuh; catatan aslinya pun menandai batasan ini (D1).
3. Klaim "tidak ada studi Indonesia" adalah hasil pencarian pada korpus terbatas, bukan bukti negatif yang kuat.
4. Angka empiris repositori diambil dari keluaran tersimpan; tidak ada pelatihan ulang dalam penyusunan laporan ini (E2 dengan batasan protokol, lihat 5.1).

---

## 4. BAB II — Kajian pustaka

### 2.1 Formulasi tugas dan definisi unsur

Aspek adalah sasaran penilaian, kategori adalah kelas domain yang telah ditentukan, opini adalah ungkapan subjektif, dan sentimen biasanya terdiri atas tiga kelas (Cai et al., 2021). Nilai `NULL` menandai unsur yang tidak memiliki rentang teks eksplisit. Contoh dari dataset asal: kalimat "Looks nice, and the surface is smooth, but certain apps take seconds to respond" memuat kuadruplet `surface–Design–smooth–Positive`, `NULL–Design–nice–Positive`, dan `apps–Software–NULL–Negative` (D2).

Konsekuensi metodologisnya langsung: karena `NULL` adalah label yang sah, model yang tidak pernah memprediksi `NULL` akan tampak rapi pada F1 per unsur tetapi gagal pada pencocokan kuadruplet.

### 2.2 Benchmark dan skala

| Dimensi | Restaurant-ACOS | Laptop-ACOS | Sumber |
|---|---:|---:|---|
| Kalimat | 2.286 | 4.076 | D2 (Cai et al., 2021) |
| Kuadruplet | 3.658 | 5.758 | D2 (Cai et al., 2021) |
| Kategori | 13 | 121 | D2 (Cai et al., 2021) |
| Sumber data | Perluasan SemEval Restaurant | Ulasan Amazon Laptop | D2 |

Catatan juga memperingatkan bahwa Laptop-L1 hanya memakai 21 kategori tingkat atas, sehingga hasilnya tidak sebanding dengan Laptop lengkap (D2). Pada dataset asal, 44% kalimat ulasan laptop memuat aspek atau opini implisit (D2).

### 2.3 Keluarga model

| Pendekatan | Representasi utama | Catatan batas |
|---|---|---|
| Pipeline dua tahap (Extract-Classify) | Ekstraksi pasangan lalu klasifikasi kategori–sentimen | Baseline; rawan propagasi galat antartahap |
| Generatif sekuens-ke-sekuens | Parafrasa T5 atau BART | Memanfaatkan semantik label; kuat, tetapi mahal saat inferensi |
| Grid tagging | Relasi pasangan token | Mengaitkan unsur secara bersama |
| MRC multitugas | Enam subtugas berbasis pertanyaan | Mengoptimalkan pengaitan dan klasifikasi |
| Generatif paralel non-autoregresif | Pointer non-autoregresif | Mengurangi ketergantungan decoding berurutan |
| Seq2Path | Jalur pohon independen | Merepresentasikan relasi satu-ke-banyak |

Sumber: D2 (`Ekstraksi Quandruple ACOS`, `ACOSQE Adalah Tugas Bukan Model`). Yang penting untuk laporan ini: catatan **tidak** memberi dasar untuk menyatakan satu keluarga unggul secara universal; pemodelan terpadu dinilai "Moderate" karena hanya diuji terhadap pipeline tertentu.

### 2.4 Pelabelan dan kendali mutu

Catatan `Labeling ACOS` membedakan lima jalur: weak labeling, pseudo-labeling, anotasi LLM, active learning, dan generasi sintetis. Temuan yang relevan bagi dataset berbahasa Indonesia:

| Klaim | Kekuatan bukti menurut catatan | Alasan |
|---|---|---|
| Penyaringan meningkatkan self-training ASQP | Moderate (7/10) | Diuji pada empat benchmark |
| Active learning menghemat anotasi | Moderate (7/10) | Direplikasi pada beberapa subtugas |
| Data sintetis membantu kondisi sumber daya rendah | Moderate (6/10) | Manfaat bergantung anggaran awal |
| LLM menggantikan seluruh anotator ACOS | Weak (2/10) | Batas struktur dan mutu relasi |

Satu angka penting untuk desain anotasi: pada ASQP, gabungan penyaringan dan reranking menaikkan F1 rata-rata 4,60 poin, tetapi kenaikan itu bukan efek scorer semata (D2). Catatan juga mencatat bahwa anotasi LLM relatif kuat pada span, namun lebih lemah dalam **menghubungkan span secara benar** (D2) — persis kelemahan yang paling mahal untuk tugas kuadruplet.

### 2.5 IndoBERT pada domain bank digital Indonesia

Bukti untuk klasifikasi sentimen dan aspek cukup konsisten, walau berasal dari studi berskala kecil dan sering hanya satu aplikasi:

| Studi | Data | Hasil | Tingkat |
|---|---|---|---|
| Casanova et al., 2026 | 22.923 ulasan aplikasi blu | Akurasi, presisi, recall, F1 sekitar 0,87; AUC-ROC 0,89; mengungguli CNN dan SVM | D2 |
| Assani et al., 2025 | Ulasan bank syariah | Akurasi 88%, F1 0,86; Naive Bayes 78%, F1 0,74 | D2 |
| Pardamean et al., 2025 | 10.159 ulasan blu | Akurasi aspek hingga 99%; F1 sentimen 84%, 96%, 94% pada Feature, App Interface, User Experience | D2 |
| Dave & Chowanda, 2024 | IPerFEX-2023 | IndoBERT-BiGRU-CRF menurunkan galat dependensi label 7%; F1 naik 0,23 | D2 |
| Saputra et al., 2026 | Ulasan bank XYZ | F1 sentimen 0,9373 tanpa oversampling | D2 |
| Natalia et al., 2026 | 5.513 ulasan mobile banking | Ensembel IndoBERT–LLaMA: akurasi 0,950, Macro F1 0,862 | D2 |

Tiga peringatan yang harus melekat pada tabel itu. Satu, angka 87–95% adalah **akurasi klasifikasi sentimen atau aspek**, bukan F1 kuadruplet; menyandingkannya langsung dengan 67,69% F1 kuadruplet adalah perbandingan yang tidak sepadan. Dua, pada data kecil atau tidak seimbang, mBERT atau linear SVC kadang menang, sehingga "IndoBERT selalu unggul" tidak sah (D2). Tiga, catatan menegaskan bahwa **ekstraksi kuintuplet ACOSE terpadu pada domain ini belum banyak dipublikasikan**, dan sebagian studi emosi perbankan masih berbasis leksikon (D2).

### 2.6 Batas ACOS: dari polaritas ke emosi

Catatan `Limitation ACOS` mempertajam klaim yang sering ditulis terlalu lebar. Versi yang didukung bukti: sistem ABSA/ACOS **tidak** buta terhadap unsur implisit — itu justru bidang yang sudah mapan — melainkan tidak mengkodekan emosi diskret, pemicu emosi, dan intensitas (D2). Versi yang tidak didukung: bahwa ACOS gagal menangani implisit secara umum.

Mengapa lapisan itu penting:

| Dimensi | ABSA/ACOS | Kerja emosi–penyebab | ABSA dimensi/emosi |
|---|---|---|---|
| Target utama | Struktur aspek–polaritas | Pasangan emosi–penyebab | Kelas atau intensitas emosi |
| Menangani emosi implisit | Terbatas | Tujuan eksplisit | Sering eksplisit dan implisit |
| Mengekstraksi pemicu | Umumnya tidak | Ya | Jarang |
| Memodelkan intensitas | Jarang | Jarang | Ya |

Bukti perilaku melengkapi argumen ini: emosi diskret memprediksi tindakan berbeda — kemarahan pada kegagalan layanan memprediksi keluhan, *word of mouth* negatif, dan perpindahan penyedia, sedangkan kekhawatiran dan frustrasi pada studi yang sama hanya memprediksi *word of mouth* negatif (D2). Teks ber-*arousal* tinggi juga menurunkan peluang ucapan terima kasih setelah respons perusahaan, sehingga strategi penanganannya berbeda (D2).

### 2.7 Celah yang tersisa

| Celah | Bukti statusnya | Konsekuensi bagi penelitian ini |
|---|---|---|
| ACOS berbahasa Indonesia | Tidak ditemukan pada korpus catatan (D1) | Celah yang diklaim, tetapi harus dinyatakan sebagai hasil pencarian terbatas |
| Integrasi aspek–emosi–perilaku dalam satu sistem | Catatan menyebut literatur bergerak terpisah (D2) | ACOSE layak sebagai rencana jangka menengah, bukan hasil |
| Evaluasi lintas bank | Studi yang ada menilai 1–3 aplikasi (D2) | Generalisasi lintas 13 bank tidak boleh diasumsikan |
| Metrik fuzzy vs exact match | Anotasi dan pencocokan tepat dapat meremehkan keluaran yang wajar (D2) | Perlu pelaporan ganda bila memungkinkan |

---

## 5. BAB III — Metode yang dipakai pada repositori

### 3.1 Data dan konstruksi

Dataset Apps-ACOS dibangun dari ulasan 13 aplikasi bank digital Indonesia: 43.673 ulasan bersih, dipecah menjadi 76.077 klausa, dan menghasilkan 92.074 kuadruplet dengan 13 kategori serta tiga kelas sentimen (E2, `eda_044_appsid.py`; rincian di `docs/0011` §3.1). Segmentasi klausa dipakai agar satu ulasan multi-aspek tidak menghasilkan kuadruplet yang saling bertabrakan.

### 3.2 Arsitektur dua tahap

Tahap 1 mengekstraksi rentang aspek dan opini dengan IndoBERT ditambah kepala CRF enam label (`[CLS]`, `O`, `B-A`, `I-A`, `B-O`, `I-O`) serta dua kepala klasifikasi untuk aspek dan opini implisit (E2, `Extract-Classify-ACOS/modeling.py:1538–1555`). Tahap 2 mengklasifikasi kategori dan sentimen atas pasangan kandidat hasil perkalian Cartesian aspek–opini, dengan kepala multi-label 39 kelas (13 kategori × 3 sentimen). Diagram alurnya ada pada `reports/fig24`.

Poin yang sering salah ditulis: kepala implisit **tidak** seragam. Aspek implisit memakai representasi `pooled_output`, sedangkan opini implisit memakai representasi token terakhir (E2, `modeling.py:1546–1555`).

### 3.3 Protokol evaluasi dan cacatnya

Ada cacat protokol yang harus dinyatakan sebelum angka apa pun dikutip. Nama fungsinya menyesatkan: `get_dev_examples` pada pemroses kuadruplet membaca berkas **test** (`run_classifier_dataset_utils.py:151–156`), dan `resolve_eval_pair_file` mengembalikan berkas **test** (`colab_utils.py:1178–1192`). Akibatnya evaluasi uji dijalankan di dalam siklus epoch, dan *checkpoint* disimpan setiap kali F1 uji naik (E2, `notebooks/02` sel 11, `notebooks/04` sel 10). Himpunan dev tersedia — 171 kalimat rest16, 8.027 klausa appsid — tetapi tidak dipakai untuk seleksi.

Besarnya dampak terukur dari deret epoch yang tersimpan: pada tahap 1, maksimum 81,27% berbanding 80,71% pada epoch terakhir, selisih **0,56 poin**; pada tahap 2, 48,24% berbanding 48,17%, selisih **0,07 poin** (E2, laporan 046). Angka "1–3 poin" yang pernah ditulis pada artikel **tidak punya dasar** dan sudah dikoreksi.

---

## 6. BAB IV — Hasil

### 4.1 Angka yang dapat dipertahankan

| Butir | Nilai | Tingkat | Sumber |
|---|---:|---|---|
| Ulasan bersih | 43.673 | E2 | `eda_044_appsid.py` |
| Klausa | 76.077 | E2 | sama |
| Kuadruplet | 92.074 (72.973 / 9.587 / 9.514) | E2 | sama |
| Kategori / sentimen | 13 / 3 | E2 | sama |
| Tahap 1 rest16 | 81,27% micro-F1 (epoch 8 dari 15; P 78,16 / R 84,64) | E2 | `notebooks/02` sel 13 (ec=8) |
| Tahap 2 appsid | 67,69% F1; TP/FP/FN 6.681/4.052/2.325 | E2 | sesi `appsid_24092026_0901` |
| Dekomposisi 15 sub-tugas | 91,08% (satu elemen) → 66,08% (empat elemen) | E2 | sel 74 (ec=163) |
| Elemen terlemah | Sentimen 85,72% | E2 | sama |
| Kebocoran teks uji | 14,66% baris | E2 | `eda_044_appsid` |
| Kosakata | 362 istilah aspek, 202 istilah opini | E2 | sama |

### 4.2 Posisi terhadap literatur

| Pembanding | Angka | Domain | Catatan kesepadanan |
|---|---:|---|---|
| Extract-Classify (Cai et al., 2021) | 44,61% / 35,80% | Restaurant / Laptop | D2; sumber lain mencatat 44,52% / 35,48% |
| Angka yang sama, sumber kedua | 44,52% / 35,48% | Restaurant / Laptop | D2 (itc.ktu.lt, 2023); **selisih 0,09 dan 0,32 poin belum dijelaskan** |
| SetFitQuad | 0,532 parsial; 0,083 exact | ASQP | D2; contoh mengapa metrik harus disebut |
| JET, Double-Prop, TAS-BERT | 39,28 / 24,61 / 35,77 | Restaurant | D2 |
| MEMD-ABSA (generatif T5) | 36,21–67,15 bergantung domain | Lima domain | D2; patokan kelas atas yang riil |
| Penelitian ini | 67,69% F1 kuadruplet | Apps-ACOS Indonesia | E2, dengan cacat protokol pada 3.3 |

Dua hal wajib dikatakan lurus. Pertama, **67,69% tidak dapat diklaim sebagai SOTA**, karena domain, bahasa, dan konstruksi labelnya berbeda, dan tidak ada pembanding berbahasa Indonesia. Kedua, selisih 0,09 dan 0,32 poin pada angka baseline yang dikutip dari dua sumber adalah **inkonsistensi yang belum diselesaikan**; artikel harus memilih satu sumber dan menyebut versinya.

### 4.3 Mengapa dekomposisi 15 sub-tugas penting

Penurunan 91,08% → 66,08% memperlihatkan bahwa kehilangan terbesar terjadi ketika keempat unsur harus diprediksi bersama, bukan ketika tiap unsur diprediksi sendiri. Ini sejalan dengan temuan literatur bahwa pengaitan relasional lebih sulit daripada pengenalan span (D2). Konsekuensinya, perbaikan yang hanya menaikkan F1 per unsur tidak akan otomatis menaikkan F1 kuadruplet.

---

## 7. BAB V — Pembahasan

### 5.1 Tiga masalah struktural

| Masalah | Bukti | Status |
|---|---|---|
| Seleksi *checkpoint* pada himpunan uji | `02` sel 7 + `11`, `04` sel 6 + `10` | Belum diperbaiki; dampak terukur 0,07–0,56 poin |
| Kebocoran teks 14,66% | `eda_044_appsid` | Belum diperbaiki; klaim generalisasi harus dibatasi |
| Kosakata tertutup 362 / 202 istilah | `eda_044_appsid` | Struktural; butuh skema terbuka atau augmentasi |

### 5.2 Implikasi metodologis

Karena ACOS dinilai dengan pencocokan tepat, setiap laporan wajib menyebut (a) metrik mana yang dipakai, (b) apakah unsur `NULL` dihitung, dan (c) apakah seleksi model memakai dev atau uji. Tanpa tiga hal itu, dua angka F1 tidak dapat dibandingkan — persoalan yang juga muncul pada literatur, misalnya perbedaan antara F1 parsial 0,532 dan exact match 0,083 pada model yang sama (D2).

### 5.3 Ancaman validitas

| Jenis | Ancaman | Mitigasi yang disarankan |
|---|---|---|
| Internal | Seleksi model pada data uji | Ganti ke dev, uji satu kali di akhir |
| Internal | Kebocoran teks | Deduplikasi lintas split sebelum pelatihan |
| Eksternal | Satu domain, 13 aplikasi, satu periode | Uji lintas waktu dan lintas bank |
| Konstruk | Label lemah dari aturan dan LLM | Audit sampel; laporkan kesepakatan antaranotator |
| Statistik | Satu run per konfigurasi | Ulangi dengan beberapa seed; laporkan sebaran |

### 5.4 Yang tidak boleh diklaim

1. Hasil tingkat SOTA, atau keunggulan atas model generatif, pada tugas ini.
2. Bahwa ACOS gagal menangani unsur implisit secara umum.
3. Bahwa IndoBERT selalu mengungguli model lain pada domain perbankan Indonesia.
4. Bahwa penambahan elemen emosi (ACOSE) sudah terbukti meningkatkan keputusan bisnis.
5. Bahwa dataset bebas kebocoran atau bebas bias anotasi.

---

## 8. BAB VI — Kesimpulan dan rencana

### 6.1 Kesimpulan

1. ACOS adalah formulasi tugas yang mapan; klaim keunggulan arsitektur tunggal tidak didukung literatur yang disintesis.
2. IndoBERT punya dasar empiris yang cukup sebagai *encoder* untuk ulasan bank digital Indonesia, tetapi dasar itu berasal dari studi berskala kecil dan berhenti pada sentimen atau aspek.
3. Celah ACOS berbahasa Indonesia tetap terbuka pada korpus yang diperiksa; kontribusi dataset berdiri di sana, dengan syarat cacat evaluasi dibereskan lebih dulu.
4. Batas ACOS adalah lapisan afektif — emosi diskret, pemicu, intensitas — bukan lapisan implisit.

### 6.2 Rencana tindak lanjut

| Prioritas | Tindakan | Alasan |
|---|---|---|
| P0 | Perbaiki seleksi *checkpoint*: evaluasi dev di dalam siklus, uji sekali di akhir | Menghapus perdebatan protokol; berlaku untuk semua angka |
| P0 | Deduplikasi lintas split dan laporkan ulang 14,66% | Klaim generalisasi tidak sah tanpanya |
| P1 | Satukan sumber angka baseline (44,61/35,80 vs 44,52/35,48) | Inkonsistensi rujukan mudah ditemukan penelaah |
| P1 | Laporkan F1 parsial dan exact match berdampingan | Menunjukkan di mana kehilangan terjadi |
| P2 | Rancang ACOSE: emosi diskret + pemicu + intensitas | Arah literatur, tetapi butuh data baru |
| P2 | Skema kosakata terbuka untuk aspek dan opini | Menembus batas 362 / 202 istilah |

---

## 9. Rujukan terpilih

Rujukan di bawah dicatat ulang dari berkas sumber; DOI disalin apa adanya dari catatan. Bila DOI tidak tercatat pada catatan, baris ditandai.

1. Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. ACL-IJCNLP. https://doi.org/10.18653/v1/2021.acl-long.29
2. Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2021). Towards Generative Aspect-Based Sentiment Analysis. (DOI tidak tercatat di catatan)
3. Zhang, W., et al. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
4. Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. ACM Computing Surveys, 58. https://doi.org/10.1145/3799234
5. Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for ACOS Quadruple Extraction. IJCNN. https://doi.org/10.1109/ijcnn54540.2023.10191098
6. Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. (DOI tidak tercatat di catatan)
7. Zhu, H., et al. (2023). Grid Tagging Scheme for Aspect-Category-Opinion-Sentiment Quadruple Extraction. (DOI tidak tercatat di catatan)
8. Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. Neurocomputing, 586, 127642. https://doi.org/10.1016/j.neucom.2024.127
9. Xiong, H., et al. (2023). BART-based contrastive and retrospective network for ACOS quadruple extraction. International Journal of Machine Learning and Cybernetics, 14, 3243–3255. https://doi.org/10.1007/s13042-023-01831-8
10. Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. arXiv. https://doi.org/10.48550/arxiv.2311.03896
11. Hoang, C. D., Dinh, Q. V., & Tran, N. H. (2022). ACOS Extraction Using Generative Transformer Model. RIVF. https://doi.org/10.1109/rivf55975.2022.10013820
12. Lei, Z., Zhang, Y., & Chen, S. (2024). A Dual-Template Prompted Mutual Learning Generative Model for Implicit ABSA. Applied Sciences. https://doi.org/10.3390/app14198719
13. Li, J., Li, X.-Y., Du, Y.-J., Fan, Y., Chen, X.-L., & Huang, D. (2023). ACOS Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. Information Technology and Control, 52, 445–456. https://doi.org/10.5755/j01.itc.52.2.32903
14. Fu, J., et al. (2024). An implicit aspect-based sentiment analysis method using supervised contrastive learning and knowledge embedding. Applied Soft Computing, 167, 112233. https://doi.org/10.1016/j.asoc.2024.112233
15. D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and ABSA. Artificial Intelligence Review, 55, 5543–5574. https://doi.org/10.1007/s10462-021-10134-9
16. Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. arXiv. https://doi.org/10.48550/arxiv.2511.19122
17. Mamta, & Ekbal, A. (2023). Aspect sentiment intensity analysis. (DOI tidak tercatat di catatan)
18. Herhausen, D., et al. (2022). Complaint handling and arousal in social media service encounters. (DOI tidak tercatat di catatan)
19. Zeelenberg, M., & Pieters, R. (2004). Beyond valence in customer dissatisfaction. Journal of Business Research. (DOI tidak tercatat di catatan)
20. Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i2.12436
21. Assani, M. Y., Rudiyan, A., & Radiyah, U. (2025). NLP-Based Sentiment Analysis of Islamic Mobile Banking Reviews. Jurnal Bumigora Information Technology. https://doi.org/10.30812/bite.v7i2.5943
22. Dave, E., & Chowanda, A. (2024). IPerFEX-2023: Indonesian personal financial entity extraction using IndoBERT-BiGRU-CRF. Journal of Big Data, 11. https://doi.org/10.1186/s40537-024-00987-6
23. Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. ICDSG. https://doi.org/10.1109/icdsg67714.2025.11381388
24. Saputra, Z., et al. (2026). User Review-Based Knowledge Discovery Model Using Knowledge Graph in Digital Banking. ICERA. https://doi.org/10.1109/icera72709.2026.11666594
25. Natalia, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. ICCMC. https://doi.org/10.1109/iccmc69250.2026.11624719
26. Janiesch, C., Zschech, P., & Heinrich, K. (2021). Machine learning and deep learning. Electronic Markets, 31, 685–695. https://doi.org/10.1007/s12525-021-00475-2
27. Ahmed, K., et al. (2023). Breaking down linguistic complexities: A structured approach to aspect-based sentiment analysis. Journal of King Saud University Computer and Information Sciences, 35. https://doi.org/10.1016/j.jksuci.2023.101651

---

## Lampiran A — Inventaris sumber Drive

| Berkas | Ukuran (bita) | Dibaca | Peran dalam laporan |
|---|---:|---|---|
| `Labeling ACOS.md` | 25.970 | 14.000 dari 25.970 (terpotong) | §2.4 pelabelan |
| `Ekstraksi Quandruple ACOS.md` | 26.400 | 12.000 dari 26.400 (terpotong) | §2.1–2.3 |
| `Limitation ACOS.md` | 26.909 | 11.000 dari 26.909 (terpotong) | §2.6 |
| `Analisi IndoBERT.md` | 30.257 | 8.000 dari 30.257 (terpotong) | §2.5 |
| `IndoBERT Unggul.md` | 6.108 | penuh | §2.5 |
| `Integrasi ACOSE.md` | 8.238 | 7.000 dari 8.238 (terpotong) | §2.6, §8 |
| `ACOSQE Adalah Tugas Bukan Model.md` | 9.786 | 7.000 dari 9.786 (terpotong) | §1.1, §2.3 |
| `Rekomendasi ACOSE.md` | 6.780 | penuh | §8 rencana |
| `ACOS dan ACOSE Analisis Sentimen.md` | 23.321 | tidak dibaca | Cadangan |
| `ACOSE Paling Kuat.md` | 20.794 | tidak dibaca | Cadangan |
| `Literature ACOSE.md` | 24.366 | tidak dibaca | Cadangan |
| `Analisis ACOS.md` | 8.437 | tidak dibaca | Cadangan |
| `Implementasi ACOSE.md` | 7.324 | tidak dibaca | Cadangan |
| 4 berkas PDF | 172–408 KB | tidak dibaca | Berisi versi cetak sebagian catatan |

**Keterbatasan yang harus dinyatakan:** lima catatan belum dibaca, dan enam catatan hanya dibaca sebagian. Laporan ini karena itu **belum** merupakan sintesis lengkap atas seluruh korpus Drive; kesimpulan pada §2 dapat berubah bila sisa berkas memuat temuan yang berlawanan.

## Lampiran B — Klaim Drive yang perlu diperiksa sebelum dikutip di artikel

| Klaim | Masalah | Tindakan |
|---|---|---|
| Baseline 44,61% / 35,80% | Sumber kedua mencatat 44,52% / 35,48% | Pilih satu versi, sebut tabelnya |
| "IndoBERT akurasi 94–95%" | Berasal dari beberapa studi berbeda dengan data berbeda | Jangan dirangkum menjadi satu angka |
| "Studi 13 bank digital belum ada" | Bukti absen pada korpus terbatas | Tulis sebagai "tidak ditemukan pada korpus yang diperiksa" |
| "ACOS gagal pada implisit" | Terbantah catatan sendiri | Pakai versi sempit: batas pada lapisan afektif |
| Angka F1 emosi 0,76–0,93 | Berasal dari benchmark tweet, bukan perbankan | Jangan dipindahkan ke domain perbankan |
| Paper bertahun 2026 | Sebagian besar belum punya riwayat sitasi | Tandai sebagai preprint atau terbitan baru |

## Lampiran C — Cara mereproduksi angka repositori

```bash
# Angka dataset dan EDA (stdlib murni)
python3 scripts/eda_044_appsid.py

# Deret F1 per epoch dan status seleksi checkpoint
grep -n "Epoch terbaik" notebooks/02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb
grep -n "Epoch terbaik" notebooks/04_ACOS_Step2_Category_Sentiment_Classification.ipynb

# Bukti bahwa loader memakai berkas test
sed -n 151,156p Extract-Classify-ACOS/run_classifier_dataset_utils.py
sed -n 1178,1192p Extract-Classify-ACOS/colab_utils.py
```

Semua perintah bersifat baca saja; tidak ada pelatihan ulang dalam penyusunan laporan ini.
