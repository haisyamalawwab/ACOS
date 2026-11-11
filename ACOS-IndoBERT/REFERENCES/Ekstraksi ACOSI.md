
# Ekstraksi **ACOS dan Emosi** pada Ulasan Aplikasi

ACOSQE, ACOS, dan ACOSI berkaitan dengan ekstraksi opini terstruktur, tetapi **ACOSI bukan penambahan emosi pada ACOS**. Untuk ulasan Google Play berbahasa Indonesia, bukti mendukung IndoBERT sebagai dasar pemodelan, sedangkan ekstraksi lima unsur aspek–kategori–opini–sentimen–emosi masih memerlukan validasi tersendiri.

## 1. Introduction

Ekstraksi *aspect–category–opinion–sentiment* (ACOS) menghasilkan himpunan quadruple `(aspek, kategori, opini, sentimen)`, termasuk kasus ketika aspek atau opini tidak dinyatakan secara eksplisit (Cai et al., 2021). ACOSQE merupakan nama tugas ekstraksi quadruple tersebut, bukan singkatan yang memasukkan *emotion* sebagai unsur kelima (Zhang et al., 2024). ASQP (*aspect sentiment quad prediction*) menargetkan empat unsur serupa, meskipun benchmark ACOS lebih menekankan aspek dan opini implisit (Zhou et al., 2023; Gou et al., 2023).

Sebaliknya, Shoes-ACOSI memperluas ACOS menjadi quintuple dengan melokalisasi dan membedakan opini implisit serta eksplisit, bukan dengan menambahkan kategori emosi (Peper et al., 2024). Istilah *quintuple* juga tidak menjamin skema yang sama: UAN-OACIS memasukkan *irrealis*, sedangkan penelitian lain memasukkan pemilik opini dan waktu (Dey & Jenamani, 2024; Tran et al., 2025).

Pada ulasan aplikasi Indonesia, klasifikasi sentimen dan emosi sudah memiliki dataset bersama, tetapi anotasi tersebut belum dengan sendirinya menyediakan hubungan lengkap aspek–kategori–opini–sentimen–emosi (Riccosan & Saputra, 2023). Penelitian aplikasi pinjaman menghubungkan klasifikasi aspek dan emosi, sementara penelitian aplikasi pemerintah mengekstraksi triplet aspek–opini–sentimen lalu memprediksi kategori secara terpisah (Almuhibb et al., 2025; Arnanda et al., 2026). Karena itu, kajian ini membedakan **definisi tugas, keluaran model, dan kekuatan evaluasi**, agar akurasi klasifikasi tidak disamakan dengan keberhasilan ekstraksi tuple.

**Figure 1:** Konsensus perbandingan IndoBERT dan BiLSTM pada ulasan Indonesia

Perbandingan langsung cenderung mengunggulkan IndoBERT untuk klasifikasi sentimen, tetapi hasil tersebut bukan bukti otomatis untuk ekstraksi quintuple (Ramadhan & Kusnawi, 2026; Anadra et al., 2025).

## 2. Methods

Penelusuran menggunakan Consensus, yang mencakup lebih dari 220 juta makalah dari Semantic Scholar, PubMed, dan sumber lainnya. Istilah pencarian menggabungkan ACOSQE, ACOS, ACOSI, ekstraksi quadruple dan quintuple, opini implisit, analisis emosi, ulasan Google Play, serta model bahasa Indonesia. Penelusuran tematik dilengkapi penelusuran sitasi, ko-sitasi, dan kesamaan referensi untuk menghubungkan formulasi awal dengan pengembangan model berikutnya.

Sintesis membedakan penelitian ekstraksi rentang dan relasi dari klasifikasi tingkat ulasan atau kategori. Hasil dibandingkan hanya dalam konteks tugas, dataset, pelabelan, dan metrik masing-masing. Teks lengkap diprioritaskan ketika tersedia; temuan berbasis abstrak diperlakukan sesuai keterbatasan informasi yang diberikan. Angka berikut merepresentasikan korpus gabungan dan seleksi relevansi yang disediakan, bukan audit penyaringan sistematis independen.

| Retrieved | Eligible | Included |
| --------- | -------- | -------- |
| 569.9K    | 323      | 100      |

**Figure 2:** Alur korpus gabungan menuju makalah terpilih berdasarkan relevansi

Strategi menggabungkan pencarian terminologi tugas, konteks aplikasi Indonesia, perbandingan model, dan penelusuran jejaring referensi penelitian terkait.

## 3. Results

Hasil memperlihatkan dua jalur yang saling melengkapi: ekstraksi opini terstruktur dan klasifikasi sentimen–emosi berbahasa Indonesia.

### 3.1 Key Papers

Formulasi ACOS menyediakan anotasi aspek dan opini implisit melalui Restaurant-ACOS serta Laptop-ACOS (Cai et al., 2021). Formulasi ASQP menunjukkan ekstraksi empat unsur melalui generasi parafrasa, sedangkan IndoNLU menyediakan benchmark dan prapelatihan bahasa Indonesia (Zhang et al., 2021; Wilie et al., 2020). Survei ABSA menegaskan bahwa tugas majemuk membutuhkan pengenalan korespondensi antarelemen, bukan sekadar pendeteksian label individual (Zhang et al., 2022).

| Paper                  | Summary                                                                    |
| ---------------------- | -------------------------------------------------------------------------- |
| (Cai et al., 2021)     | Memformalkan ACOS dengan unsur implisit (Cai et al., 2021)                 |
| (Peper et al., 2024)   | Memperluas ekstraksi melalui opini implisit (Peper et al., 2024)           |
| (Arnanda et al., 2026) | Menguji ekstraksi triplet ulasan aplikasi Indonesia (Arnanda et al., 2026) |

**Figure 3:** Makalah fondasional dan penghubung menuju ulasan aplikasi Indonesia

### 3.2 Definisi dan Keluaran

Quadruple ACOS menggabungkan dua masalah ekstraksi dan dua masalah klasifikasi (Cai et al., 2021). Aspek merupakan target tekstual, kategori merupakan kelas domain, opini merupakan ungkapan evaluatif, dan sentimen merupakan orientasi seperti positif, negatif, atau netral (Cai et al., 2021).

| Dimensi            | ACOS/ACOSQE                      | ACOSI                          | Sentimen–Emosi Indonesia | Bukti                                                              |
| ------------------ | -------------------------------- | ------------------------------ | ------------------------- | ------------------------------------------------------------------ |
| Keluaran           | Empat unsur berelasi             | Lima unsur terkait opini       | Label sentimen dan emosi  | (Peper & Wang, 2022; Peper et al., 2024; Riccosan & Saputra, 2025) |
| Informasi implisit | Aspek/opini dapat tidak tertulis | Opini implisit dilokalisasi    | Bergantung skema anotasi  | (Peper & Wang, 2022; Peper et al., 2024)                           |
| Domain contoh      | Restoran dan laptop              | Ulasan sepatu                  | Ulasan aplikasi Indonesia | (Peper & Wang, 2022; Peper et al., 2024; Riccosan & Saputra, 2023) |
| Tantangan          | Hubungan empat unsur             | Paragraf dan sentimen campuran | Pembedaan kategori emosi  | (Cai et al., 2021; Peper et al., 2024; Saputra et al., 2025)       |

**Figure 4:** Perbedaan skema ekstraksi dan klasifikasi sentimen serta emosi

Triplet ASTE menambahkan ungkapan opini untuk menjelaskan evaluasi terhadap aspek (Peng et al., 2019). ASOTE memperjelas bahwa sentimen harus melekat pada pasangan aspek–opini tertentu (Li et al., 2021). Skema lain memisahkan entitas dari aspek atau menambahkan target percakapan; keduanya tidak identik dengan ACOS (Dan et al., 2023; Li et al., 2022).

### 3.3 Arsitektur Ekstraksi

Model ekstraksi berkembang melalui pipeline, pelabelan bersama, pembacaan mesin, dan generasi terstruktur (Li et al., 2023; Zhang et al., 2024).

| Pendekatan        | Representasi Utama                | Keunggulan yang Dilaporkan  | Batasan Penting                    | Bukti                                                    |
| ----------------- | --------------------------------- | --------------------------- | ---------------------------------- | -------------------------------------------------------- |
| Extract–Classify | Rentang lalu kategori–sentimen   | Mendukung unsur implisit    | Propagasi kesalahan                | (Zhang et al., 2024; Xiong et al., 2023)                 |
| Grid tagging      | Relasi pasangan token             | Ekstraksi bersama           | Memerlukan skema relasi            | (Zhu et al., 2023)                                       |
| MRC               | Pertanyaan ekstraksi–klasifikasi | Menghubungkan subtugas      | Inferensi bertahap                 | (Mao et al., 2021; Chen et al., 2021)                    |
| Generatif         | Urutan atau pohon tuple           | Memanfaatkan semantik label | Urutan keluaran dan biaya decoding | (Zhang et al., 2021; Mao et al., 2022; Nie et al., 2024) |

**Figure 5:** Pendekatan pemodelan untuk ekstraksi opini berstruktur empat unsur

BART dan T5 memungkinkan formulasi generatif terpadu, termasuk adaptasi untuk ACOS (Yan et al., 2021; Zhang et al., 2021; Hoang et al., 2022). Seq2Path dan pohon opini merepresentasikan hubungan antarelemen secara terstruktur (Mao et al., 2022; Bao et al., 2022). Augmentasi urutan template dan *multi-view prompting* mengatasi ketergantungan pada urutan linear tunggal (Hu et al., 2022; Gou et al., 2023).

Pembelajaran kontrastif, contoh negatif adaptif, dan pengendalian ketidakpastian meningkatkan pemodelan kasus sulit (Peper & Wang, 2022; Xu et al., 2023; Hu et al., 2023). Alternatif lain menggunakan jarak aspek–opini, struktur laten, semantik label, atau grid sebagai tugas bantu (Li et al., 2023; Nie et al., 2024; Fu et al., 2024; Zhu et al., 2025).

### 3.4 Model Bahasa Indonesia

Pada Access by KAI, IndoBERT menghasilkan F1 aspek 0.785, sentimen 0.752, dan gabungan aspek–sentimen 0.549 (Doewes & Widoyono, 2026). Benchmark NEWSAKPOLE melaporkan F1 0.882, sedangkan Mobile JKN menemukan penurunan pada kategori registrasi–verifikasi yang jarang (Dhendra, 2025; Wirawan et al., 2026). Untuk emosi–sentimen aplikasi, IndoBERT memperoleh micro-F1 0.77, dibandingkan mBERT 0.72 dan BERT bahasa Inggris 0.69 (Riccosan & Saputra, 2025).

IndoRoBERTa mencapai macro-F1 agregat 0.826 pada evaluasi beberapa tugas, tetapi bukan ekstraksi ACOS (Sihombing et al., 2026). XLM-RoBERTa mengungguli IndoBERTa dalam ulasan ritel, sementara pada SATUSEHAT weighted-F1 IndoBERT dan XLM-R hampir sama (Faiqoh, 2026; Ananda et al., 2025). IndoBERTweet mengungguli IndoBERT pada ulasan Gojek tingkat kalimat (Aqiilah et al., 2026).

BERT–BiLSTM melaporkan akurasi 0.98 pada klasifikasi tiga aspek Gojek, bukan exact-match quadruple (Mahardian et al., 2025). Hibrida IndoBERT–RNN mencapai akurasi emosi 78%, sedangkan BiLSTM juga telah digunakan langsung dalam ekstraksi quadruple (Ahmadian et al., 2024; Zhang et al., 2022).

### Results Timeline

Perkembangan penelitian menghubungkan ekstraksi triplet, quadruple, opini implisit, dan aplikasi Indonesia.

- **Nov 2019**
  - 1 paper: (Peng et al., 2019)
- **Sep 2020**
  - 1 paper: (Wilie et al., 2020)
- **Jan 2021**
  - 1 paper: (Cai et al., 2021)
- **Mar 2021**
  - 1 paper: (Li et al., 2021)
- **Oct 2021**
  - 1 paper: (Zhang et al., 2021)
- **Mar 2022**
  - 1 paper: (Zhang et al., 2022)
- **Nov 2022**
  - 1 paper: (Peper & Wang, 2022)
- **May 2023**
  - 1 paper: (Gou et al., 2023)
- **Jun 2023**
  - 1 paper: (Zhou et al., 2023)
- **Sep 2023**
  - 1 paper: (Riccosan & Saputra, 2023)
- **Jan 2024**
  - 2 papers: (Zhang et al., 2024; Peper et al., 2024)
- **Sep 2024**
  - 1 paper: (Dey & Jenamani, 2024)
- **Jan 2025**
  - 1 paper: (Saputra et al., 2025)
- **Oct 2025**
  - 1 paper: (Riccosan & Saputra, 2025)
- **Dec 2025**
  - 3 papers: (Tran et al., 2025; Almuhibb et al., 2025; Anadra et al., 2025)
- **Apr 2026**
  - 2 papers: (Arnanda et al., 2026; Ramadhan & Kusnawi, 2026)
    **Figure 6:** Linimasa penelitian dengan penanda lebih besar menunjukkan lebih banyak sitasi

Ekstraksi bersama berawal dari triplet dan berkembang menuju quadruple serta anotasi implisit yang lebih rinci (Peng et al., 2019; Zhang et al., 2021; Peper et al., 2024). Pengujian terbaru juga menunjukkan bahwa skor agregat dapat menyembunyikan perbedaan antartipe implisit (Ghimire & Jin, 2026).

### Top Contributors

Kontributor berikut menonjol berdasarkan kemunculan dan sitasi makalah dalam korpus ini, bukan pemeringkatan dampak seluruh bidang.

| Type    | Name                                                    | Papers                                                                                        |
| ------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Author  | Lidong Bing                                             | (Peng et al., 2019; Zhang et al., 2022; Zhang et al., 2021; Xu et al., 2021; Xu et al., 2020) |
| Author  | Wenxuan Zhang                                           | (Zhang et al., 2022; Zhang et al., 2021)                                                      |
| Author  | Lu Xu                                                   | (Peng et al., 2019; Xu et al., 2021; Xu et al., 2020)                                         |
| Journal | *IEEE Transactions on Knowledge and Data Engineering* | (Zhang et al., 2022)                                                                          |
| Journal | *Neurocomputing*                                      | (Zhang et al., 2022; Nie et al., 2024; Chen et al., 2022)                                     |
| Journal | *Artificial Intelligence Review*                      | (Zhang et al., 2024)                                                                          |

**Figure 7:** Kontributor dan jurnal menonjol dalam korpus makalah tersedia

Kontribusinya mencakup formulasi triplet, generasi quadruple, survei tugas majemuk, dan interaksi tingkat rentang (Peng et al., 2019; Zhang et al., 2022; Xu et al., 2021).

## 4. Discussion

**Bukti terkuat adalah kelayakan tugas dan manfaat representasi kontekstual, bukan kemenangan universal satu arsitektur.** IndoBERT mengungguli pembanding dalam ulasan blu, kesehatan, dan perbandingan berulang Tokopedia (Pardamean et al., 2025; Imaduddin et al., 2023; Anadra et al., 2025). Namun, XLM-R lebih baik daripada IndoBERT-Lite pada data sangat timpang dan ulasan campuran bahasa (Butar & Lhaksmana, 2026). Representasi statis kadang mencapai akurasi lebih tinggi, sementara IndoBERT lebih seimbang pada kelas minoritas (Kadarsih & Pujianto, 2025). SVM dan TF-IDF tetap relevan sebagai baseline ringan (Wulandari et al., 2025; Tangdilomban et al., 2026).

Pelabelan merupakan sumber ketidakpastian utama. Studi Ruparupa secara eksplisit mengukur kesesuaian terhadap label turunan rating, bukan sentimen aspek tervalidasi manusia (Setyawati et al., 2026). Penelitian lain menggunakan leksikon, pseudo-label, atau RoBERTa sebagai pemberi label awal (Asri et al., 2025; Citra & Ghifari, 2026; Maretta & Meiriza, 2025). Pada TikTok, 2,430 dari 4,414 ulasan dikeluarkan karena tidak memperoleh label emosi leksikal, sehingga evaluasi mencakup subset terseleksi (Athyabunnaja et al., 2026). Sebaliknya, anotasi manusia AHM Mobile menghasilkan akurasi 0.7831 tetapi macro-F1 0.5582, memperlihatkan pentingnya evaluasi kelas minoritas (Safitri & Arsyad, 2026).

### Validitas Evaluasi Terstruktur

Exact-match harus membedakan tuple lengkap dari keberhasilan subtugas: Seq2Path menghitung prediksi benar hanya ketika semua unsur benar (Mao et al., 2022). SetFitQuad melaporkan F1 partial-match 0.532 tetapi exact-match hanya 0.083 (Chuang & Lin, 2025). Pada aplikasi pemerintah Indonesia, IndoBERT-large mencapai F1 triplet 0.760, tetapi klasifikasi kategori dilakukan terpisah sehingga angka itu bukan F1 quadruple (Arnanda et al., 2026). Ketimpangan kategori dan ketidakpastian batas opini juga nyata dalam dataset tersebut (Arnanda et al., 2026).

Biaya anotasi dan generalisasi tetap membatasi klaim. MEMD memperluas cakupan menjadi hampir 20,000 kalimat dan 30,000 quadruple, tetapi domain terbuka serta unsur implisit tetap sulit (Cai et al., 2023). Adaptasi Urdu dan LASQ menunjukkan kelayakan transfer bahasa berdaya rendah, bukan validasi langsung bahasa Indonesia (Ahmed et al., 2025; Yusufu et al., 2026). Augmentasi perlu menjaga konsistensi teks–tuple, sedangkan oversampling dapat meningkatkan risiko overfitting (Wang et al., 2023; Alfinsyah & Hartato, 2025).

**Klaim dan Dukungan**

| Claim                                                        | Evidence Strength                  | Reasoning                                       | Papers                                            |
| ------------------------------------------------------------ | ---------------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| ACOS mengekstraksi empat unsur berelasi                      | Evidence strength: Strong (9/10)   | Definisi konsisten lintas formulasi             | (Zhu et al., 2023; Zhou et al., 2023)             |
| IndoBERT merupakan baseline Indonesia yang kuat              | Evidence strength: Moderate (7/10) | Replikasi lintas domain, dataset berbeda        | (Yulianti & Nissa, 2024; Nugroho et al., 2021)    |
| Emosi aplikasi dapat diklasifikasikan                        | Evidence strength: Moderate (6/10) | Ada dataset dan evaluasi langsung               | (Almuhibb et al., 2025; Safitri & Arsyad, 2026)   |
| Hibrida BiLSTM selalu lebih baik                             | Evidence strength: Weak (2/10)     | Bukti tugas-spesifik, bukan konsensus           | (Ahmadian et al., 2024; Doewes & Widoyono, 2026)  |
| Quintuple berbasis emosi sudah tervalidasi untuk konteks ini | Evidence strength: Weak (1/10)     | Studi terdekat belum mengevaluasi tuple lengkap | (Riccosan & Saputra, 2025; Almuhibb et al., 2025) |

**Figure 8:** Kekuatan klaim utama dan batas dukungan empirisnya

## 5. Conclusion

ACOSQE tepat untuk ekstraksi empat unsur, sedangkan ACOSI harus dipahami sebagai perluasan pemahaman opini implisit, bukan emosi. Untuk Google Play Indonesia, IndoBERT, IndoRoBERTa, BERT–BiLSTM, dan BiLSTM perlu dibandingkan pada **anotasi dan exact-match tuple yang sama**, bukan melalui akurasi lintas penelitian.

### Research Gaps

Korpus memperlihatkan pemisahan antara benchmark ekstraksi terstruktur dan penelitian emosi aplikasi. Dataset Indonesia menyediakan sentimen–emosi, sedangkan benchmark ACOSI menyediakan lokalisasi opini implisit (Riccosan & Saputra, 2023; Peper et al., 2024).

|                                                                               | Restoran Laptop | Sepatu    | Aplikasi Indonesia |
| ----------------------------------------------------------------------------- | --------------- | --------- | ------------------ |
| ACOS                                                                          | 17 papers       | No papers | No papers          |
| ACOSI                                                                         | 1 paper         | 1 paper   | No papers          |
| Sentimen Aplikasi                                                             | 1 paper         | No papers | 36 papers          |
| Emosi Aplikasi                                                                | No papers       | No papers | 12 papers          |
| **Figure 9:** Cakupan tugas opini terstruktur menurut domain penelitian |                 |           |                    |

Celah paling relevan ialah dataset aplikasi Indonesia yang menghubungkan emosi dengan setiap pasangan aspek–opini, bukan hanya dengan keseluruhan ulasan (Almuhibb et al., 2025; Riccosan & Saputra, 2023). Anotasi lengkap mahal, dan penambahan unsur implisit meningkatkan kesulitan, sehingga pengembangan dataset sama pentingnya dengan pemilihan encoder (Chuang & Lin, 2025; Ghimire & Jin, 2026). Skema emosi juga harus dinyatakan eksplisit karena EmoT menggunakan lima kelas, sedangkan dataset aplikasi menggunakan enam kelas berbeda (Wilie et al., 2020; Riccosan & Saputra, 2025).

### Open Research Questions

Arah utama ialah menguji hubungan antarunsur, ketahanan bahasa informal, dan manfaat tambahan arsitektur hibrida. Model span dan pelabelan bersama menyediakan dasar untuk pengujian hubungan tersebut (Xu et al., 2021; Chen et al., 2022).

| Pertanyaan                                                                                          | Why                                                                                                                                                                                                 |
| --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Apakah penambahan emosi meningkatkan kegunaan ACOS pada ulasan aplikasi Indonesia?**        | Studi aspek–emosi menunjukkan potensi, tetapi belum mengukur keberhasilan ekstraksi seluruh unsur sebagai satu tuple berelasi (Almuhibb et al., 2025).                                             |
| **Apakah IndoRoBERTa atau IndoBERT–BiLSTM mengungguli IndoBERT pada exact-match quintuple?** | Benchmark agregat dan hasil hibrida menjanjikan, tetapi mengevaluasi tugas berbeda sehingga belum menetapkan pemenang pada ekstraksi lengkap (Sihombing et al., 2026; Ahmadian et al., 2024).       |
| **Seberapa kuat model menghadapi slang, campuran bahasa, dan aspek atau opini implisit?**     | Adaptasi bahasa informal membantu klasifikasi, sementara kasus kedua unsur tidak tertulis tetap belum menunjukkan perbaikan melampaui variasi antarrun (Aqiilah et al., 2026; Ghimire & Jin, 2026). |

**Figure 10:** Pertanyaan terbuka untuk ekstraksi quintuple ulasan aplikasi Indonesia

Kontribusi penelitian paling jelas adalah **benchmark quintuple berbasis emosi yang terdefinisi dan tervalidasi**, bukan sekadar penggabungan nama model.

*These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at <https://consensus.app>. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.*

## References

R., & Saputra, K. (2023). Multilabel multiclass sentiment and emotion dataset from indonesian mobile application review. *Data in Brief, 50*. <https://doi.org/10.1016/j.dib.2023.109576>

D., Xu, J., Wang, Z., Cao, X.-Z., & Xian, Y. (2023). Entity-Aspect-Opinion-Sentiment Quadruple Extraction for Fine-grained Sentiment Analysis. *ArXiv, abs/2311.16678*. <https://doi.org/10.48550/arxiv.2311.16678>

D. (2025). Benchmarking IndoBERT and Transformer Models for Sentiment Classification on Indonesian E-Government Service Reviews. *Jurnal Transformatika*. <https://doi.org/10.26623/transformatika.v23i1.12095>

Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2024). Hybrid Models for Emotion Classification and Sentiment Analysis in Indonesian Language. *Appl. Comput. Intell. Soft Comput., 2024*. <https://doi.org/10.1155/2024/2826773>

Ahmed, N., Aziz, K., Tariq, U., Hadi, H., Alshara, M. A., & Harris, S. (2025). Urdu Aspect-Category-Opinion-Sentiment (UACOS) Quadruple Extraction: A Transfer Learning Approach. *2025 4th International Conference on Communication, Computing and Digital Systems (C-CODE)*, 1-6. <https://doi.org/10.1109/c-code67372.2025.11204128>

Alfinsyah, D. R., & Hartato, B. P. (2025). Evaluating the Impact of Random Over Sampling on IndoBERT Performance for Indonesian Sentiment Analysis. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v9i6.11488>

Almuhibb, Z. S., Alamsyah, A., & Indrajaya, D. (2025). Aspect and Emotion Multiclass Classification of Online Loan Application Reviews Using IndoBERT. *2025 International Conference on Artificial Intelligence, Blockchain, Cloud Computing, and Data Analytics (ICoABCD)*, 1-6. <https://doi.org/10.1109/icoabcd67551.2025.11470811>

Anadra, R., Wijayanto, H., & Sadik, K. (2025). Sentiment Analysis of Tokopedia Customer Reviews Using BiLSTM and IndoBERT with Comparative Analysis of Preprocessing and Labeling Methods. *International Journal of Advances in Data and Information Systems*. <https://doi.org/10.59395/ijadis.v6i3.1458>

Ananda, D., Budi, I., Santoso, A., & Qureshi, A. A. (2025). SENTIMENT ANALYSIS OF PUBLIC HEALTH APP REVIEWS USING INDOBERT AND XLM-ROBERTA: A STUDY ON SATUSEHAT MOBILE APP. *JIKO (Jurnal Informatika dan Komputer)*. <https://doi.org/10.33387/jiko.v8i3.10083>

Aqiilah, I. N., Saptono, R., & Syaifuddin, A. (2026). Sentence-Level Sentiment Analysis of Indonesian App Reviews Using IndoBERTweet. *Journal of Computing Theories and Applications*. <https://doi.org/10.62411/jcta.16240>

Arnanda, F. R., Suadaa, L. H., Widya, A., & Pramana, S. (2026). SPAN-LEVEL ASPECT-BASED SENTIMENT TRIPLET ANALYSIS IN GOVERNMENT APPLICATION REVIEWS. *AL ULUM: JURNAL SAINS DAN TEKNOLOGI*. <https://doi.org/10.31602/jst.v12i1.22767>

Asri, Y., Kuswardani, D., Suliyanti, W. N., Manullang, Y. O., & Ansyari, A. R. (2025). Sentiment analysis based on Indonesian language lexicon and IndoBERT on user reviews PLN mobile application. *Indonesian Journal of Electrical Engineering and Computer Science*. <https://doi.org/10.11591/ijeecs.v38.i1.pp677-688>

Athyabunnaja, S., Thamrin, T., & Mulyo, H. (2026). Implementation of IndoBERT for Text-Based Emotion Classification on TikTok Application Reviews in Google Play Store. *Journal of Dinda : Data Science, Information Technology, and Data Analytics*. <https://doi.org/10.20895/dinda.v6i1.10174>

Bao, X., Wang, Z.-Q., Jiang, X., Xiao, R., & Li, S.-S. (2022). Aspect-based Sentiment Analysis with Opinion Tree Generation. 4044-4050. <https://doi.org/10.24963/ijcai.2022/561>

Butar, J. J. B., & Lhaksmana, K. M. (2026). IndoBERT-Lite vs. XLM-RoBERTa for Indonesian E-commerce Sentiment Classification. *2026 IEEE International Conference on Artificial Intelligence and Mechatronics Systems (AIMS)*, 1-6. <https://doi.org/10.1109/aims71270.2026.11712573>

Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. <https://doi.org/10.18653/v1/2021.acl-long.29>

Cai, H., Song, N., Wang, Z., Xie, Q., Zhao, Q.-K., Li, K., Wu, S., Liu, S.-J., H.-Q., Yu, J.-F., & Xia, R. (2023). MEMD-ABSA: a multi-element multi-domain dataset for aspect-based sentiment analysis. *Language Resources and Evaluation, 59*, 2501 - 2529. <https://doi.org/10.1007/s10579-025-09820-9>

Chen, S.-W., Wang, Y., Liu, J., & Wang, Y.-L. (2021). Bidirectional Machine Reading Comprehension for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2103.07665*. <https://doi.org/10.48550/arxiv.2103.07665>

Chen, F., Yang, Z., & Huang, Y. (2022). A multi-task learning framework for end-to-end aspect sentiment triplet extraction. *Neurocomputing, 479*, 12-21. <https://doi.org/10.1016/j.neucom.2022.01.021>

Chuang, H.-M., & Lin, J.-K. (2025). SetFitQuad: A Few-Shot Framework for Aspect Sentiment Quad Prediction With Sampling Strategies. *IEEE Access, 13*, 146204-146217. <https://doi.org/10.1109/access.2025.3600351>

Citra, M. B., & Ghifari, N. T. A. (2026). Fine-Grained Aspect-Based Sentiment Analysis on Indonesian E-Commerce Reviews Using Multi-Task Learning with Pretrained Transformer Models. *2026 International Conference on Smart Computing, IoT, and Machine Learning (SIML)*, 1-6. <https://doi.org/10.1109/siml69834.2026.11621828>

Dey, A., & Jenamani, M. (2024). Aspect based sentiment analysis of consumer reviews using unsupervised attention neural framework. *Appl. Soft Comput., 167*, 112259. <https://doi.org/10.1016/j.asoc.2024.112259>

Doewes, A., & Widoyono, B. (2026). Aspect-Based Sentiment Analysis of Access by KAI Application Reviews Using IndoBERT for Multi-Label Classification Tasks. *Jurnal Teknik Informatika (Jutif)*. <https://doi.org/10.52436/1.jutif.2026.7.1.5402>

Faiqoh, A. W. (2026). Implementation of IndoBERT, IndoBERTa, and XLM-RoBERTa for Sentiment Classification of Alfagift and KlikIndomaret User Reviews. *Indonesian Journal of Infomatics*. <https://doi.org/10.66472/iji.v1i2.506>

Fu, Y.-H., Chen, X.-L., Miao, D.-Q., Qin, X.-L., Lu, P., & Li, X.-Y. (2024). Label-semantics enhanced multi-layer heterogeneous graph convolutional network for Aspect Sentiment Quadruplet Extraction. *Expert Syst. Appl., 255*, 124523. <https://doi.org/10.1016/j.eswa.2024.124523>

Ghimire, P., & Jin, W. (2026). A Comprehensive Study of Implicit-Aware Methods for Generative Aspect-Category-Opinion-Sentiment Extraction. *Proceedings of the 26th ACM/IEEE Joint Conference on Digital Libraries*. <https://doi.org/10.1145/3805696.3846476>

Gou, Z., Guo, Q., & Yang, Y. (2023). MvP: Multi-view Prompting Improves Aspect Sentiment Tuple Prediction. 4380-4397. <https://doi.org/10.48550/arxiv.2305.12627>

Hoang, C. D., Dinh, Q. V., & Tran, N. H. (2022). Aspect-Category-Opinion-Sentiment Extraction Using Generative Transformer Model. *2022 RIVF International Conference on Computing and Communication Technologies (RIVF)*, 1-6. <https://doi.org/10.1109/rivf55975.2022.10013820>

Hu, M.-T., Wu, Y., Gao, H., Bai, Y.-H., & Zhao, S. (2022). Improving Aspect Sentiment Quad Prediction via Template-Order Data Augmentation. *ArXiv, abs/2210.10291*. <https://doi.org/10.48550/arxiv.2210.10291>

Hu, M.-T., Bai, Y.-H., Wu, Y., Zhang, Z., Zhang, L., Gao, H., Zhao, S., & Huang, M.-T. (2023). Uncertainty-Aware Unlikelihood Learning Improves Generative Aspect Sentiment Quad Prediction. 13481-13494. <https://doi.org/10.48550/arxiv.2306.00418>

Imaduddin, H., A'La, F. Y., & Nugroho, Y. (2023). Sentiment Analysis in Indonesian Healthcare Applications using IndoBERT Approach. *International Journal of Advanced Computer Science and Applications*. <https://doi.org/10.14569/ijacsa.2023.0140813>

Kadarsih, K., & Pujianto, D. (2025). APPLICATION OF TRANSFORMER MODEL AND WORD EMBEDDING IN SENTIMENT ANALISYS OF INDONESIAN E-COMMERCE APPLICATION REVIEW. *Journal of Computer Networks, Architecture and High Performance Computing*. <https://doi.org/10.47709/cnahpc.v7i3.6354>

Li, Y., Wang, F., Zhang, W., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). A More Fine-Grained Aspect-Sentiment-Opinion Triplet Extraction Task. *ArXiv, abs/2103.15255*. <https://doi.org/10.48550/arxiv.2103.15255>

Li, B., Fei, H., Li, F., Wu, Y.-H., Zhang, J.-S., Wu, S.-Q., Li, J., Liu, Y., Liao, L.-Z., Chua, T.-S., & Ji, D.-H. (2022). DiaASQ : A Benchmark of Conversational Aspect-based Sentiment Quadruple Analysis. *ArXiv, abs/2211.05705*. <https://doi.org/10.48550/arxiv.2211.05705>

Li, S.-D., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. <https://doi.org/10.1109/ijcnn54540.2023.10191098>

Li, J., Li, X.-Y., Du, Y.-J., Fan, Y.-Q., Chen, X.-L., & Huang, D. (2023). An Aspect-Category-Opinion-Sentiment Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. *Inf. Technol. Control., 52*, 445-456. <https://doi.org/10.5755/j01.itc.52.2.32903>

Mahardian, F. N., Sibaroni, Y., & Prasetiyowati, S. (2025). Multi Aspect Sentiment Analysis of User Reviews on the Gojek Application on the Google Play Store using the BERT-BiLSTM Method. *2025 International Conference on Computing and Applied Informatics (ICCAI)*, 1-6. <https://doi.org/10.1109/iccai65301.2025.11279581>

Mao, Y., Shen, Y., Yu, C., & Cai, L. (2021). A Joint Training Dual-MRC Framework for Aspect Based Sentiment Analysis. 13543-13551. <https://doi.org/10.48550/arxiv.2101.00816>

Mao, Y., Shen, Y., Yang, J.-C., Zhu, X., & Cai, L. (2022). Seq2Path: Generating Sentiment Tuples as Paths of a Tree. 2215-2225. <https://doi.org/10.18653/v1/2022.findings-acl.174>

Maretta, A. P., & Meiriza, A. (2025). Aspect-Based Sentiment Analysis of Hospital Service Reviews Using Fine-Tuned IndoBERT. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v9i5.10765>

Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. *Neurocomputing, 586*, 127642. <https://doi.org/10.1016/j.neucom.2024.127642>

Nugroho, K. S., Sukmadewa, A. Y., Dw, H. W., Bachtiar, F., & Yudistira, N. (2021). BERT Fine-Tuning for Sentiment Analysis on Indonesian Mobile Apps Reviews. *Proceedings of the 6th International Conference on Sustainable Information Engineering and Technology*. <https://doi.org/10.1145/3479645.3479679>

Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. *2025 1st International Conference on Data Science and Geoinformatics (ICDSG)*, 37-42. <https://doi.org/10.1109/icdsg67714.2025.11381388>

Peng, H.-Y., Xu, L., Bing, L., Huang, F., Lu, W., & Si, L. (2019). Knowing What, How and Why: A Near Complete Solution for Aspect-based Sentiment Analysis. *ArXiv, abs/1911.01616*. <https://doi.org/10.48550/arxiv.1911.01616>

Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. <https://doi.org/10.18653/v1/2024.findings-emnlp.907>

Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. *ArXiv, abs/2211.07743*. <https://doi.org/10.48550/arxiv.2211.07743>

Ramadhan, T., & Kusnawi, K. (2026). Performance Comparison of IndoBERT and Bi-LSTM Models for Sentiment Analysis of Shopee App Users in Indonesia. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v10i2.10996>

Riccosan, R., & Saputra, K. (2025). Multilabel classification sentiment analysis on Indonesian mobile app reviews. *IAES International Journal of Artificial Intelligence (IJ-AI)*. <https://doi.org/10.11591/ijai.v14.i5.pp4226-4234>

Safitri, A., & Arsyad, A. A. (2026). Pemodelan Emosi Pengguna Berbasis Ulasan Digital Melalui Integrasi Natural Language Processing dan Ilmu Sosial Komputasional. *JURNAL Al-AZHAR INDONESIA SERI SAINS DAN TEKNOLOGI*. <https://doi.org/10.36722/sst.v11i2.5425>

Saputra, A., Saragih, A., & Ronaldo, D. (2025). PREDIKSI EMOSI DALAM TEKS BAHASA INDONESIA MENGGUNAKAN MODEL INDOBERT. *Jurnal Teknologi Informasi: Jurnal Keilmuan dan Aplikasi Bidang Teknik Informatika*. <https://doi.org/10.47111/jti.v19i1.17617>

Setyawati, E., B., & Saputra, D. (2026). Rule-Based Aspect Extraction and IndoBERT-Based Sentiment Classification of Ruparupa Mobile Application Reviews. *Journal of Information Systems and Informatics*. <https://doi.org/10.63158/journalisi.v8i4.1816>

Sihombing, Y. O., Muchlisin, K., Arya, T., Mubarok, M. J., & Rachmadi, R. F. (2026). A Systematic Evaluation of BERT Classifiers for Indonesia-based Text Data. *Techno.Com*. <https://doi.org/10.62411/tc.v25i2.15843>

Tangdilomban, C. T., Ramdhan, S. Y., Rizal, M., Suhaeni, C., & Sartono, B. (2026). From Sparse Features to Transformers: A Statistical Evaluation of TF-IDF, FastText, and IndoBERT for Sentiment Classification of Indonesian Travel App Reviews. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v10i3.12610>

Tran, P. Q., Le, H. T. M., & Huynh, H. X. (2025). Relation-Based Quintuple Extraction for Opinion Mining. *2025 RIVF International Conference on Computing and Communication Technologies (RIVF)*, 398-402. <https://doi.org/10.1109/rivf68649.2025.11365056>

Wang, A., Jiang, J., Y., Liu, A., & Okazaki, N. (2023). Generative Data Augmentation for Aspect Sentiment Quad Prediction. *J. Nat. Lang. Process., 31*, 1523-1544. <https://doi.org/10.18653/v1/2023.starsem-1.12>

Wilie, B., Vincentio, K., Winata, G. I., Cahyawijaya, S., Li, X., Lim, Z. Y., Soleman, S., Mahendra, R., Fung, P., Bahar, S., & Purwarianti, A. (2020). IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding. *ArXiv, abs/2009.05387*. <https://doi.org/10.48550/arxiv.2009.05387>

Wirawan, N. O. H., Chandra, G. J., Lucky, H., Pradana, R., & Sagala, N. T. M. (2026). Benchmarking Aspect-Based Sentiment Analysis on Indonesian Mobile JKN Reviews using Transformer Models. *2026 International Electronics Symposium (IES)*, 1-6. <https://doi.org/10.1109/ies71033.2026.11702744>

Wulandari, D. A., Bachtiar, F. A., & Indriati, I. (2025). Aspect Based Sentiment Analysis on Shopee Application Reviews Using Support Vector Machine. *Lontar Komputer : Jurnal Ilmiah Teknologi Informasi*. <https://doi.org/10.24843/lkjiti.2024.v15.i02.p03>

Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. <https://doi.org/10.1007/s13042-023-01831-8>

Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. *ArXiv, abs/2311.03896*. <https://doi.org/10.48550/arxiv.2311.03896>

Xu, L., Chia, Y. K., & Bing, L. (2021). Learning Span-Level Interactions for Aspect Sentiment Triplet Extraction. 4755-4766. <https://doi.org/10.18653/v1/2021.acl-long.367>

Xu, L., Li, H., Lu, W., & Bing, L. (2020). Position-Aware Tagging for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2010.02609*. <https://doi.org/10.48550/arxiv.2010.02609>

Yan, H., Dai, J., Ji, T., Qiu, X., & Zhang, Z. (2021). A Unified Generative Framework for Aspect-based Sentiment Analysis. 2416-2429. <https://doi.org/10.18653/v1/2021.acl-long.188>

Yulianti, E., & Nissa, N. K. (2024). ABSA of Indonesian customer reviews using IndoBERT: single- sentence and sentence-pair classification approaches. *Bulletin of Electrical Engineering and Informatics*. <https://doi.org/10.11591/eei.v13i5.8032>

Yusufu, A., Liu, J., Aziz, K., Ainiwaer, A., Li, B., Li, F., Ji, D., & Yusufu, A. (2026). LASQ: A low-resource aspect-based sentiment quadruple extraction dataset. *Journal of King Saud University Computer and Information Sciences, 38*. <https://doi.org/10.1007/s44443-026-00701-x>

Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. <https://doi.org/10.1007/s10462-023-10633-x>

Zhang, W., Deng, Y., Li, X., Yuan, Y., Bing, L., & Lam, W. (2021). Aspect Sentiment Quad Prediction as Paraphrase Generation. 9209-9219. <https://doi.org/10.18653/v1/2021.emnlp-main.726>

Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. <https://doi.org/10.1109/tkde.2022.3230975>

Zhang, H., Song, X.-W., Jia, X., Yang, C., Chen, Z., Chen, B., Jiang, B., Wang, Y., & Feng, R. (2024). Query-induced multi-task decomposition and enhanced learning for aspect-based sentiment quadruple prediction. *Eng. Appl. Artif. Intell., 133*, 108609. <https://doi.org/10.1016/j.engappai.2024.108609>

Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2021). Towards Generative Aspect-Based Sentiment Analysis. 504-510. <https://doi.org/10.18653/v1/2021.acl-short.64>

Zhang, H., Chen, Z., Chen, B., Hu, B., Li, M., Yang, C., & Jiang, B. (2022). Complete quadruple extraction using a two-stage neural model for aspect-based sentiment analysis. *Neurocomputing, 492*, 452-463. <https://doi.org/10.1016/j.neucom.2022.04.027>

Zhou, J., Yang, H., He, Y., Mou, H., & Yang, J. (2023). A Unified One-Step Solution for Aspect Sentiment Quad Prediction. *ArXiv, abs/2306.04152*. <https://doi.org/10.48550/arxiv.2306.04152>

Zhu, L.-N., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. *World Wide Web, 26*, 3303 - 3320. <https://doi.org/10.1007/s11280-023-01185-9>

Zhu, L.-N., Guo, X., Zhu, Z., Xu, Y., Zhou, Z., Chen, X.-F., & Kong, X.-J. (2025). Generative aspect-based sentiment analysis with a grid tagging matching auxiliary task. *Comput. Speech Lang., 92*, 101776. <https://doi.org/10.1016/j.csl.2025.101776>
