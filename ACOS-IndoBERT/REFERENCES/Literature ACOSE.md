Literatur ACOSE Perbankan Digital Indonesia dengan IndoBERT
1. Introduction
Untuk topik Aspect-Category-Opinion-Sentiment-Emotion (ACOSE) pada ulasan bank digital Indonesia berbasis IndoBERT, literaturnya saat ini terpecah ke tiga rumpun yang berdekatan tetapi belum benar-benar menyatu: ABSA/ACOS untuk struktur aspek-kategori-opini-sentimen, klasifikasi emosi bahasa Indonesia, dan analisis sentimen/ABSA khusus layanan digital Indonesia (Cai et al., 2021; Xiong et al., 2023; Chai et al., 2025; Pardamean et al., 2025; Ahmadian et al., 2023). ACOS sudah mapan sebagai tugas ekstraksi kuadrupel yang memodelkan aspek, kategori, opini, dan polaritas, termasuk kasus implisit (Cai et al., 2021; Zhang et al., 2024). Di sisi lain, studi Indonesia berbasis IndoBERT menunjukkan performa kuat baik untuk ABSA maupun klasifikasi emosi, termasuk pada domain aplikasi keuangan dan layanan digital (Pardamean et al., 2025; Fatihaturrahmah & Tania, 2025; Simarmata & Sasongko, 2025; Ahmadian et al., 2024; Shaw et al., 2025).
Namun, korpus ini belum menunjukkan adanya sistem IndoBERT yang secara langsung mengekstrak kuintuplet lengkap aspek-kategori-opini-sentimen-emosi untuk bank digital Indonesia. Studi yang paling dekat masih berupa ABSA pada ulasan perbankan digital tanpa emosi eksplisit (Pardamean et al., 2025; Natalia et al., 2026), atau klasifikasi aspek dan emosi secara dua tahap pada domain keuangan digital lain seperti pinjaman daring (Almuhibb et al., 2025). Karena itu, kontribusi ilmiah yang realistis bukan mengklaim ACOSE sudah mapan di konteks ini, tetapi menunjukkan bahwa fondasi metodologisnya sudah tersedia dan dapat digabungkan dari literatur ACOS, ACSA berorientasi emosi, dan IndoBERT domain Indonesia (Zhang et al., 2022; Chai et al., 2025; Citra & Ghifari, 2026).
Meter ini kemungkinan condong ke ya, tetapi dengan nuansa penting: IndoBERT didukung kuat untuk sentimen dan ABSA bahasa Indonesia, sedangkan komponen emosi tingkat aspek dan ekstraksi kuintuplet penuh masih merupakan perluasan riset, bukan praktik yang sudah matang. Figure 1: Konsensus kelayakan IndoBERT untuk ACOSE Indonesia
2. Methods
Pencarian dilakukan di atas lebih dari 220 juta makalah riset dalam Consensus, yang mengindeks Semantic Scholar, PubMed, dan sumber ilmiah lain. Korpus difokuskan pada tiga jalur bukti: ABSA/ACOS dan variasi tugas majemuknya, pemodelan emosi dan sentimen bahasa Indonesia berbasis IndoBERT, serta studi domain digital banking, e-wallet, dan layanan digital Indonesia yang paling dekat dengan kasus penggunaan pengguna.
Retrieved
Eligible
Included
342.5K
270
50
Figure 2: Strategi penyaringan literatur untuk topik ACOSE IndoBERT
Strategi menggabungkan pencarian semantik bertarget, pembacaan mendalam makalah inti, dan penelusuran sitasi dari paper ACOS fondasional.
3. Results
3.1 Key Papers
Literatur inti ditopang oleh satu paper fondasional ACOS, satu survei ABSA/ACOS, dan satu studi ACSA berorientasi emosi. Ketiganya bersama-sama mendefinisikan struktur tugas, kesulitan pemodelan implisit, dan alasan ilmiah menambahkan emosi ke keluaran sentimen aspek (Cai et al., 2021; Zhang et al., 2022; Chai et al., 2025).
Paper
Summary
(Cai et al., 2021)
Memformalkan ACOS dengan aspek/opini implisit (Cai et al., 2021)
(Zhang et al., 2022)
Memetakan tugas compound ABSA dan tantangannya (Zhang et al., 2022)
(Chai et al., 2025)
Menambahkan emosi kategori-aspek ke ACSA (Chai et al., 2025)
Figure 3: Makalah jangkar untuk struktur ACOSE
3.2 Performa IndoBERT pada Domain Indonesia
Pada korpus Indonesia, IndoBERT konsisten kuat untuk ABSA dan sentimen domain-spesifik. Pada ulasan aplikasi blu, IndoBERT yang fine-tuned mencapai hingga 99% akurasi klasifikasi aspek dan F1 sentimen 84%, 96%, dan 94% pada tiga aspek utama (Pardamean et al., 2025). Pada ulasan keamanan DANA, IndoBERT mencapai 98% akurasi dan F1 0.974, serta tetap stabil pada uji temporal dan lintas-domain ke GoPay (Fatihaturrahmah & Tania, 2025). Pada BRImo, IndoBERT mencapai 90% akurasi dan membantu menyorot isu login, kegagalan transaksi, dan lambatnya layanan pelanggan (Simarmata & Sasongko, 2025).
Domain
Tugas
Hasil utama
Catatan
Citations
blu mobile banking
ABSA
Aspek 99%, F1 sentimen 84–96%
10.159 ulasan
(Pardamean et al., 2025)
DANA security
ASC keamanan
98% akurasi, F1 0.974
Generalisasi temporal/cross-domain
(Fatihaturrahmah & Tania, 2025)
BRImo
Sentimen 3 kelas
90% akurasi
Sorot login/transaksi/CS
(Simarmata & Sasongko, 2025)
JKN / layanan publik
ABSA
IndoBERT paling konsisten
Sulit pada aspek jarang
(Wirawan et al., 2026)
Figure 4: Kinerja IndoBERT pada domain layanan Indonesia
Perbandingan model juga cenderung menguntungkan model monolingual Indonesia. Pada ABSA ulasan pelanggan Indonesia, fine-tuned IndoBERT berbasis sentence-pair memberi peningkatan F1 23.6% atas baseline Word2Vec-CNN-XGBoost dan 2.2% atas baseline mBERT auxiliary (Yulianti & Nissa, 2024). Pada e-commerce Indonesia, IndoBERT juga konsisten mengungguli mBERT di sebagian besar aspek dalam deteksi aspek dan sentimen fine-grained (Citra & Ghifari, 2026).
3.3 Struktur ACOSE dan Pilihan Paradigma
ACOSE secara praktis dibangun dari perluasan ACOS, bukan dari klasifikasi sentimen biasa. ACOS menuntut ekstraksi serentak aspek, kategori, opini, dan polaritas, serta penanganan aspek maupun opini implisit yang proporsinya besar pada ulasan nyata (Cai et al., 2021). Tantangan ini membuat performa baseline kuadrupel jauh lebih rendah daripada tugas ABSA yang lebih sederhana; bahkan Extract-Classify-ACOS terbaik dalam paper fondasional hanya mencapai F1 0.4461 pada Restaurant-ACOS dan 0.3580 pada Laptop-ACOS (Cai et al., 2021).
Paradigma
Kekuatan
Kelemahan
Bukti
Pipeline BERT/klasik
Mudah dipecah per-subtugas
Error propagation
(Zhang et al., 2022)
End-to-end generatif
Tangani kuadrupel langsung
Struktur keluaran lebih sulit
(Xiong et al., 2023)
Hibrida BERT+LLM
Gabung ekstraksi dan penalaran
Integrasi masih awal
(Zhang et al., 2024)
Figure 5: Perbandingan paradigma untuk ekstraksi ACOSE
Literatur yang lebih baru cenderung meninggalkan pipeline murni. BART-CRN memformulasi ACOS sebagai tugas generasi sekuens untuk mengurangi error propagation dan menangani keragaman tipe kuadrupel (Xiong et al., 2023). Untuk sentimen berdimensi, pendekatan hibrida BERT+LLM bahkan mengungguli metode BERT saja dan LLM saja pada ekstraksi kuadrupel (Zhang et al., 2024).
3.4 Emosi Tingkat Aspek dan Kesenjangan ke Perbankan Digital
Penambahan emosi ke struktur aspek bukan sekadar kosmetik. Studi ACSA berorientasi emosi menegaskan bahwa pendekatan polaritas positif-netral-negatif saja melewatkan sinyal afektif seperti marah, jijik, sedih, atau gembira yang memperkaya penalaran opini (Chai et al., 2025). Framework berbasis LLM yang belajar bersama polaritas dan emosi kategori-spesifik menunjukkan peningkatan atas baseline kuat, serta memakai ruang VAD untuk memeriksa konsistensi emosi yang dihasilkan (Chai et al., 2025).
Di Indonesia, bukti terdekat datang dari tugas dua tahap, bukan kuintuplet penuh. Pada ulasan pinjaman daring, IndoBERT dipakai untuk mengklasifikasikan empat aspek layanan dan empat emosi, mencapai macro-F1 0.82 untuk kedua tahap (Almuhibb et al., 2025). Sementara itu, klasifikasi emosi bahasa Indonesia secara umum dengan IndoBERT atau model sejenis berada di kisaran akurasi 0.76–0.79, dan masih kesulitan membedakan kelas emosi yang mirip atau tidak seimbang (Ahmadian et al., 2023; Ahmadian et al., 2024; Shaw et al., 2025; Paramarta et al., 2025). Ini menunjukkan bahwa komponen emosi sudah layak secara teknis, tetapi masih lebih rapuh daripada komponen aspek atau sentimen.
Results Timeline
Perkembangan riset bergerak dari sentimen umum ke struktur dan afek yang makin halus.
Jan 2021
1 paper: (Cai et al., 2021)
Mar 2022
1 paper: (Zhang et al., 2022)
Apr 2023
1 paper: (Xiong et al., 2023)
Dec 2023
1 paper: (Ahmadian et al., 2023)
Jan 2024
2 papers: (Zhang et al., 2024; Ahmadian et al., 2024)
Sep 2024
1 paper: (Zhang et al., 2024)
Oct 2024
1 paper: (Yulianti & Nissa, 2024)
Mar 2025
1 paper: (Shaw et al., 2025)
Jun 2025
1 paper: (Simarmata & Sasongko, 2025)
Jul 2025
1 paper: (Dhendra, 2025)
Sep 2025
1 paper: (Paramarta et al., 2025)
Nov 2025
3 papers: (Chai et al., 2025; Pardamean et al., 2025; Fatihaturrahmah & Tania, 2025)
Dec 2025
1 paper: (Almuhibb et al., 2025)
Feb 2026
1 paper: (Doewes & Widoyono, 2026)
Jun 2026
1 paper: (Citra & Ghifari, 2026)
Jul 2026
1 paper: (Natalia et al., 2026)
Aug 2026
1 paper: (Wirawan et al., 2026) Figure 6: Lintasan hasil riset; marker besar lebih tersitasi
Secara umum, fase awal berfokus pada sentimen dan ABSA klasik, fase menengah memformalkan tugas majemuk seperti ACOS, dan fase terbaru mendorong integrasi emosi, intensitas, serta LLM/hibrida untuk ekstraksi yang lebih kaya (Zhang et al., 2022; Cai et al., 2021; Chai et al., 2025).
Top Contributors
Type
Name
Papers
Author
Wenxuan Zhang
(Zhang et al., 2022; Zhang et al., 2023)
Author
Rui Xia
(Cai et al., 2021)
Author
Haoran Xie
(Chai et al., 2025)
Journal
Artificial Intelligence Review
(Zhang et al., 2024; Hua et al., 2023; Truşcǎ & Frasincar, 2022)
Journal
IEEE Transactions on Knowledge and Data Engineering
(Zhang et al., 2022)
Journal
Applied Sciences
(Jazuli et al., 2024)
Figure 7: Penulis dan jurnal paling sering muncul
4. Discussion
Korpus ini cukup konsisten pada dua hal. Pertama, untuk teks Indonesia, IndoBERT biasanya mengungguli baseline klasik dan sering juga melampaui model multilingual pada sentimen dan ABSA domain-spesifik (Doewes & Widoyono, 2026; Dhendra, 2025; Bimasena et al., 2026). Kedua, kebutuhan berpindah dari sentimen umum ke struktur aspek memang jelas, khususnya di layanan digital dan perbankan, karena masalah pengguna terlokalisasi pada fitur, keamanan, reliabilitas, login, transaksi, dan layanan pelanggan, bukan pada satu polaritas ulasan keseluruhan (Pardamean et al., 2025; Casanova et al., 2026; Simarmata & Sasongko, 2025; Tomasaputra & Siallagan, 2025).
Kualitas bukti untuk komponen ABSA Indonesia cukup baik, tetapi masih dominan berbasis studi aplikasi tunggal dan dataset lokal buatan peneliti. Hasil yang sangat tinggi, seperti akurasi 99% pada klasifikasi aspek blu, menjanjikan tetapi belum tentu langsung berpindah ke tugas yang lebih sulit seperti opini implisit, ulasan multi-aspek, atau bank lain dengan gaya bahasa berbeda (Pardamean et al., 2025; Perwira et al., 2025; Wirawan et al., 2026). Beberapa studi juga masih memakai pelabelan berbasis rating atau pseudo-label, yang membatasi validitas semantik untuk sentimen halus atau emosi (Casanova et al., 2026; Thobibuddin & Dewi, 2026; Bimasena et al., 2026).
Kesenjangan terbesar ada pada integrasi penuh antara struktur ABSA dan emosi. Studi emosi Indonesia umumnya masih di tingkat ulasan atau klasifikasi multi-kelas, sedangkan studi ACOS/ASQP global umumnya belum berada pada Bahasa Indonesia atau domain bank digital (Shaw et al., 2025; Almuhibb et al., 2025; Ahmed et al., 2025). LLM menjanjikan untuk tugas majemuk, terutama pada kondisi few-shot, tetapi bukti luas menunjukkan bahwa untuk compound ABSA mereka masih sering tertinggal dari metode tersupervisi penuh atau sistem hibrida terbaik (Zhang et al., 2023; Bai et al., 2024).
Claim
Evidence Strength
Reasoning
Papers
IndoBERT efektif untuk sentimen dan ABSA bahasa Indonesia domain-spesifik
Evidence strength: Strong (8/10)
Didukung banyak studi lintas domain Indonesia dengan keunggulan konsisten atas baseline klasik dan sering atas model multilingual
(Pardamean et al., 2025; Fatihaturrahmah & Tania, 2025; Doewes & Widoyono, 2026; Dhendra, 2025; Wirawan et al., 2026)
ACOS adalah fondasi struktural terbaik untuk ACOSE
Evidence strength: Strong (8/10)
Definisi tugas, dataset, dan evaluasi kuadrupel sudah mapan dan dirujuk luas dalam survei ABSA
(Cai et al., 2021; Zhang et al., 2024)
Emosi per-aspek menambah informasi di luar polaritas
Evidence strength: Moderate (6/10)
Didukung studi ACSA-emotion dan aspek-emosi, tetapi masih lebih baru dan belum luas di domain Indonesia
(Chai et al., 2025; Almuhibb et al., 2025)
LLM murni belum menjadi pilihan terbaik untuk compound ABSA
Evidence strength: Moderate (6/10)
Bukti moderat menunjukkan unggul di few-shot tetapi biasanya di bawah sistem tersupervisi/hibrida
(Zhang et al., 2023; Bai et al., 2024)
Sudah ada ACOSE bank digital Indonesia berbasis IndoBERT yang mapan
Evidence strength: Weak (2/10)
Korpus tidak menunjukkan sistem kuintuplet penuh; yang ada masih ABSA tanpa emosi atau klasifikasi aspek-emosi dua tahap
(Pardamean et al., 2025; Almuhibb et al., 2025; Natalia et al., 2026)
Figure 8: Klaim utama dan kekuatan evidensinya
5. Conclusion
Literatur mendukung posisi yang cukup jelas: IndoBERT adalah tulang punggung yang kuat untuk analisis sentimen dan ABSA pada teks Indonesia, termasuk layanan keuangan digital, tetapi ACOSE penuh untuk bank digital Indonesia masih merupakan agenda riset, bukan solusi yang sudah mapan (Pardamean et al., 2025; Fatihaturrahmah & Tania, 2025; Chai et al., 2025). Secara metodologis, jalur paling kuat adalah memperluas ABSA/ACOS berbasis IndoBERT dengan kepala emosi atau modul generatif/hibrida, bukan memulai dari klasifikasi sentimen umum.
Research Gaps
Cakupan korpus memperlihatkan riset yang padat pada sentimen dan ABSA Indonesia, tetapi jauh lebih tipis pada penggabungan emosi ke struktur aspek, terutama di domain bank digital. Matriks berikut memetakan di mana bukti terkonsentrasi dan di mana kekosongan paling nyata berada.
Sentimen
ABSA
Emosi
LLM
Bank Digital
8 papers
3 papers
No papers
1 paper
E-Wallet
1 paper
1 paper
No papers
1 paper
Layanan Publik
2 papers
2 papers
No papers
1 paper
Emosi Indonesia
4 papers
1 paper
8 papers
2 papers
ACOS Global
2 papers
12 papers
3 papers
5 papers
Penelitian bank digital Indonesia terkonsentrasi pada sentimen dan ABSA dasar, misalnya blu, BRImo, dan studi tiga bank digital, tetapi hampir tidak ada yang mengekstrak opini eksplisit maupun emosi per-aspek (Pardamean et al., 2025; Simarmata & Sasongko, 2025; Syaripudin et al., 2025). Sebaliknya, literatur ACOS global kaya secara metodologis tetapi tidak berbahasa Indonesia dan tidak berfokus pada keuangan digital lokal (Cai et al., 2021; Xiong et al., 2023; Ahmed et al., 2025). Gap paling mencolok adalah sel “Bank Digital × Emosi”: korpus hanya memberi pendekatan terdekat dari pinjaman daring atau emosi tingkat ulasan, sehingga hubungan langsung antara aspek perbankan seperti transaksi, keamanan, autentikasi, dan emosi seperti marah atau takut masih belum dianotasi secara sistematis (Almuhibb et al., 2025; Shaw et al., 2025).
Open Research Questions
Arah berikutnya cukup spesifik: bukan lagi “apakah IndoBERT bisa,” tetapi “bagaimana menyusun data, target, dan evaluasi yang membuat ACOSE valid di konteks Indonesia.”
Question
Why
Bagaimana merancang skema anotasi ACOSE untuk ulasan bank digital Indonesia yang sekaligus menangani aspek implisit, opini implisit, dan emosi per-aspek?
Tanpa skema anotasi lokal, model hanya menggabungkan tugas dari korpus berbeda dan sulit dievaluasi secara sahih.
Apakah arsitektur IndoBERT multi-task cukup untuk ACOSE, atau perlu sistem hibrida IndoBERT-LLM pada domain bank digital?
Bukti saat ini mendukung IndoBERT untuk ABSA dan LLM/hibrida untuk struktur afektif yang lebih kaya, tetapi belum diuji langsung.
Apakah emosi diskret atau representasi valence-arousal lebih berguna untuk pengambilan keputusan layanan perbankan digital?
Literatur emosi aspek bergerak ke arah kategori dan dimensi, tetapi manfaat operasional masing-masing pada perbankan digital belum jelas.
Secara ringkas, ACOSE untuk bank digital Indonesia berbasis IndoBERT tampak layak dan baru, tetapi kebaruannya terletak pada integrasi komponen yang sudah ada, bukan pada keberadaan bukti bahwa tugas itu sudah terselesaikan.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
D. (2025). Benchmarking IndoBERT and Transformer Models for Sentiment Classification on Indonesian E-Government Service Reviews. Jurnal Transformatika. https://doi.org/10.26623/transformatika.v23i1.12095
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2023). Transformer-Based Indonesian Language Model for Emotion Classification and Sentiment Analysis. 2023 International Conference on Information Technology and Computing (ICITCOM), 209-214. https://doi.org/10.1109/icitcom60176.2023.10442970
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2024). Hybrid Models for Emotion Classification and Sentiment Analysis in Indonesian Language. Appl. Comput. Intell. Soft Comput., 2024. https://doi.org/10.1155/2024/2826773
Ahmed, N., Aziz, K., Tariq, U., Hadi, H., Alshara, M. A., & Harris, S. (2025). Urdu Aspect-Category-Opinion-Sentiment (UACOS) Quadruple Extraction: A Transfer Learning Approach. 2025 4th International Conference on Communication, Computing and Digital Systems (C-CODE), 1-6. https://doi.org/10.1109/c-code67372.2025.11204128
Almuhibb, Z. S., Alamsyah, A., & Indrajaya, D. (2025). Aspect and Emotion Multiclass Classification of Online Loan Application Reviews Using IndoBERT. 2025 International Conference on Artificial Intelligence, Blockchain, Cloud Computing, and Data Analytics (ICoABCD), 1-6. https://doi.org/10.1109/icoabcd67551.2025.11470811
Bai, Y.-H., Han, Z., Zhao, Y., Gao, H., Zhang, Z.-W., Wang, X.-Z., & Hu, M. (2024). Is Compound Aspect-Based Sentiment Analysis Addressed by LLMs?. 7836-7861. https://doi.org/10.18653/v1/2024.findings-emnlp.460
Bimasena, M. I., Prayoga, I., Mahendra, I., & Sidik, P. (2026). Benchmarking IndoBERT and Multilingual BERT for Indonesian Financial News Sentiment Classification. JURNAL TEKNOLOGI DAN OPEN SOURCE. https://doi.org/10.36378/jtos.v9i1.5583
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i2.12436
Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. ArXiv, abs/2511.19122. https://doi.org/10.48550/arxiv.2511.19122
Citra, M. B., & Ghifari, N. T. A. (2026). Fine-Grained Aspect-Based Sentiment Analysis on Indonesian E-Commerce Reviews Using Multi-Task Learning with Pretrained Transformer Models. 2026 International Conference on Smart Computing, IoT, and Machine Learning (SIML), 1-6. https://doi.org/10.1109/siml69834.2026.11621828
Doewes, A., & Widoyono, B. (2026). Aspect-Based Sentiment Analysis of Access by KAI Application Reviews Using IndoBERT for Multi-Label Classification Tasks. Jurnal Teknik Informatika (Jutif). https://doi.org/10.52436/1.jutif.2026.7.1.5402
Fatihaturrahmah, A., & Tania, K. D. (2025). A Hybrid Approach of Aspect-Based Sentiment Analysis and Knowledge Extraction for Evaluating Security Perceptions in Digital Payment Applications. Scientific Journal of Informatics. https://doi.org/10.15294/sji.v12i4.31557
Hua, Y. C., Denny, P., Wicker, J., & Taškova, K. (2023). A systematic review of aspect-based sentiment analysis: domains, methods, and trends. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-024-10906-z
Jazuli, A., W., & Kusumaningrum, R. (2024). Optimizing Aspect-Based Sentiment Analysis Using BERT for Comprehensive Analysis of Indonesian Student Feedback. Applied Sciences. https://doi.org/10.3390/app15010172
Natalia, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. 2026 9th International Conference on Computing Methodologies and Communication (ICCMC), 2002-2007. https://doi.org/10.1109/iccmc69250.2026.11624719
Paramarta, M. M. A., Dwiyansaputra, R., & Rassy, R. P. (2025). PERFORMANCE ANALYSIS OF MULTILINGUAL AND MONOLINGUAL MODELS IN PREDICTING INDONESIAN LANGUAGE EMOTION USING TWITTER DATASET. Jurnal Teknologi Informasi, Komputer, dan Aplikasinya (JTIKA ). https://doi.org/10.29303/jtika.v7i2.482
Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. 2025 1st International Conference on Data Science and Geoinformatics (ICDSG), 37-42. https://doi.org/10.1109/icdsg67714.2025.11381388
Perwira, R., Permadi, V. A., Purnamasari, D., & Agusdin, R. P. (2025). Domain-Specific Fine-Tuning of IndoBERT for Aspect-Based Sentiment Analysis in Indonesian Travel User-Generated Content. Journal of Information Systems Engineering and Business Intelligence. https://doi.org/10.20473/jisebi.11.1.30-40
Shaw, C., LaCasse, P. M., & Champagne, L. E. (2025). Exploring emotion classification of indonesian tweets using large scale transfer learning via IndoBERT. Social Network Analysis and Mining, 15. https://doi.org/10.1007/s13278-025-01439-6
Simarmata, A. A. P., & Sasongko, T. B. (2025). Sentiment Analysis on BRImo Application Reviews Using IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v9i3.8162
Syaripudin, U., Gerhana, Y. A., Wahana, A., & Fuadi, R. (2025). Sentiment Analysis of Google Play Store Reviews on the Top Three Digital Banks in Indonesia Using Bidirectional Encoder Representations from Transformers (BERT). 2025 11th International Conference on Wireless and Telematics (ICWT), 1-5. https://doi.org/10.1109/icwt66752.2025.11181730
Thobibuddin, F. F., & Dewi, G. A. (2026). Comparative Sentiment and Complaint Pattern Analysis of Indonesian E-Wallet Application Reviews Using IndoBERT. Journal of Computing and Smart Ecosystems. https://doi.org/10.26714/jcase.v2i1.1143
Tomasaputra, D., & Siallagan, M. (2025). Enhancing Digital Banking Experience Through Text Mining of e-Service Reviews in Indonesia. Ekonomis: Journal of Economics and Business. https://doi.org/10.33087/ekonomis.v9i2.2653
Truşcǎ, M. M., & Frasincar, F. (2022). Survey on aspect detection for aspect-based sentiment analysis. Artificial Intelligence Review, 56, 3797-3846. https://doi.org/10.1007/s10462-022-10252-y
Wirawan, N. O. H., Chandra, G. J., Lucky, H., Pradana, R., & Sagala, N. T. M. (2026). Benchmarking Aspect-Based Sentiment Analysis on Indonesian Mobile JKN Reviews using Transformer Models. 2026 International Electronics Symposium (IES), 1-6. https://doi.org/10.1109/ies71033.2026.11702744
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. International Journal of Machine Learning and Cybernetics, 14, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
Yulianti, E., & Nissa, N. K. (2024). ABSA of Indonesian customer reviews using IndoBERT: single- sentence and sentence-pair classification approaches. Bulletin of Electrical Engineering and Informatics. https://doi.org/10.11591/eei.v13i5.8032
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. IEEE Transactions on Knowledge and Data Engineering, 35, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
Zhang, Y., Xu, H., Zhang, D., & Xu, R.-F. (2024). A Hybrid Approach to Dimensional Aspect-Based Sentiment Analysis Using BERT and Large Language Models. Electronics. https://doi.org/10.3390/electronics13183724
Zhang, W., Deng, Y., Liu, B.-Q., Pan, S. J., & Bing, L. (2023). Sentiment Analysis in the Era of Large Language Models: A Reality Check. 3881-3906. https://doi.org/10.48550/arxiv.2305.15005