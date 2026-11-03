Analisis IndoBERT untuk 13 Bank Digital Indonesia
1. Introduction
Analisis aspect category, opinion, sentiment, dan emotion dengan IndoBERT sangat relevan untuk 13 bank digital Indonesia, tetapi bukti yang tersedia saat ini lebih kuat untuk kelayakan teknis klasifikasi daripada untuk inferensi bisnis lintas-bank atau pemetaan emosi yang tervalidasi. Literatur menunjukkan bahwa ulasan aplikasi dan percakapan media sosial memang menangkap kepuasan, keluhan teknis, kualitas layanan, dan kepercayaan pengguna, sementara pendekatan berbasis IndoBERT umumnya mengungguli model klasik untuk klasifikasi sentimen dan banyak tugas ABSA (aspect-based sentiment analysis) berbahasa Indonesia (Yulianti & Nissa, 2024; Pardamean et al., 2025; Dhendra, 2025; Casanova et al., 2026; Saputra et al., 2026; Jazuli et al., 2024).
Namun, korpus ini juga menunjukkan tiga batas besar. Pertama, studi perbankan Indonesia yang benar-benar mencakup banyak bank masih sedikit, dan yang ada biasanya hanya menilai 1–3 aplikasi atau satu platform data, bukan 13 bank digital sekaligus (Andrian et al., 2022; Syaripudin et al., 2025; Tomasaputra & Siallagan, 2025; Zahratussyafitri et al., 2026). Kedua, banyak studi memberi label sentimen dari rating bintang atau pseudo-label otomatis, sehingga hubungan antara opinion, sentiment, emotion, dan kepuasan dapat sebagian “dibangun” oleh desain anotasi, bukan sepenuhnya ditemukan dari data alami (Casanova et al., 2026; Setyawati et al., 2026; Maretta & Meiriza, 2025; Hazz & Wahyuningsih, 2026). Ketiga, generalisasi lintas domain, lintas waktu, dan lintas platform masih menjadi masalah terbuka, terutama untuk teks Indonesia yang informal, bercampur kode, tidak seimbang kelasnya, dan sering memuat multi-aspek dalam satu ulasan (Susanto et al., 2026; Nataprawira & Nurhaida, 2026; Mozetič et al., 2018; Al-Moslmi et al., 2017).
Figure 1: Konsensus relevansi IndoBERT untuk evaluasi bank digital
2. Methods
Tinjauan ini mensintesis korpus Deep Search Consensus atas literatur tentang sentiment analysis, aspect-based sentiment analysis, klasifikasi emosi, dan kualitas layanan pada perbankan digital Indonesia serta domain Indonesia yang berdekatan. Pencarian dijalankan di atas lebih dari 220 juta paper dalam Consensus, yang mengindeks Semantic Scholar, PubMed, dan sumber ilmiah lain, lalu dipersempit ke studi yang relevan dengan IndoBERT, ulasan aplikasi bank, evaluasi lintas-bank, pelabelan sentimen/emosi, serta isu validitas seperti class imbalance, domain shift, dan privasi.
Retrieved
Eligible
Included
1.1M
399
100
Figure 2: Strategi pencarian dan penyaringan studi
Strategi menggabungkan pencarian topik bank digital Indonesia, benchmark IndoBERT, studi ABSA, dan paper validitas evaluasi lintas-domain.
3. Results
3.1 Key Papers
Fondasi korpus ini bertumpu pada empat jenis studi: studi kepuasan bank digital Indonesia lintas merek, studi ABSA IndoBERT berbahasa Indonesia, studi kualitas layanan mobile banking, dan studi metodologi evaluasi model pada data temporal atau lintas-domain (Andrian et al., 2022; Yulianti & Nissa, 2024; Tomasaputra & Siallagan, 2025; Mozetič et al., 2018).
Paper
Summary
(Andrian et al., 2022)
Tiga bank digital, distribusi sentimen berbeda (Andrian et al., 2022)
(Yulianti & Nissa, 2024)
IndoBERT unggul untuk ABSA Indonesia (Yulianti & Nissa, 2024)
(Tomasaputra & Siallagan, 2025)
Sentimen dipetakan ke dimensi E-S-QUAL (Tomasaputra & Siallagan, 2025)
Figure 3: Paper jangkar dalam korpus ini
3.2 Performa Model
Sebagian besar studi Indonesia menemukan IndoBERT kuat untuk sentimen dan ABSA, sering mengungguli mBERT, SVM, CNN, BiLSTM, atau XLM-R pada data ulasan dan layanan berbahasa Indonesia (Doewes & Widoyono, 2026; Citra & Ghifari, 2026; Doewes & Widoyono, 2026; Dhendra, 2025; Sihombing et al., 2026). Pada domain perbankan atau fintech yang dekat, IndoBERT mencapai akurasi sekitar 87% pada ulasan blu, 88% pada mobile banking syariah, 90% pada BRImo, 91.24% pada DANA, 94%–95% pada beberapa tugas bank/dompet digital, dan F1 0.9373 pada knowledge-discovery pipeline bank (Casanova et al., 2026; Assani et al., 2025; Simarmata & Sasongko, 2025; Susanto et al., 2026; Sanjaya et al., 2025; Saputra et al., 2026).
Tetapi keunggulan IndoBERT tidak universal. Pada data kecil atau setup tidak seimbang, mBERT atau linear SVC kadang unggul, terutama bila ada sinyal tambahan seperti rating atau sampling yang tidak setara antar model (Afandy et al., 2026; Zahra et al., 2026; Kadarsih & Pujianto, 2025).
3.3 Temuan Substantif Perbankan
Di studi perbankan Indonesia, sinyal yang paling konsisten adalah bahwa ulasan negatif menumpuk pada reliability: login, verifikasi, crash, error transaksi, performa lambat, dan respons customer service yang lemah (Prasetyo & Agastya, 2024; Simarmata & Sasongko, 2025; Tania & Afrina, 2026; Zahratussyafitri et al., 2026; Arif et al., 2026; Adiningtyas & Auliani, 2024).
Sebaliknya, ulasan positif biasanya terkait efisiensi transaksi, kemudahan penggunaan, kenyamanan, fitur, dan antarmuka (Casanova et al., 2026; Prasetyo & Agastya, 2024; Tomasaputra & Siallagan, 2025; Arif et al., 2026; Oh & Kim, 2022).
Perbandingan lintas bank juga menunjukkan heterogenitas besar, sehingga studi 13 bank tidak boleh mengasumsikan pola sentimen yang seragam. Dalam korpus Indonesia, Jago pernah dominan positif di Twitter 2021, tetapi pada ulasan aplikasi periode lain bisa dominan negatif; SeaBank tampak unggul pada beberapa studi review-store, sedangkan Blu, Livin’, Neo, dan bank lain menunjukkan pola yang lebih problematik atau bercampur tergantung platform dan waktu (Andrian et al., 2022; Syaripudin et al., 2025; Tomasaputra & Siallagan, 2025; Zahratussyafitri et al., 2026; Mulyanto et al., 2025).
3.4 Opinion Dan Emotion
ABSA jelas lebih informatif daripada polaritas dokumen tunggal karena satu ulasan sering memuat beberapa aspek dan sentimen campuran (Pardamean et al., 2025; Wirawan et al., 2026; Halik et al., 2026; Hayatin et al., 2024). Literatur juga menunjukkan bahwa level yang lebih kaya—opinion term, aspect category, bahkan quadruple extraction—secara konseptual lebih cocok bila tujuan studi 13 bank adalah mengetahui aspek apa, opini apa, dan sentimen apa yang muncul bersama, termasuk aspek atau opini implisit (Cai et al., 2021; Zhang et al., 2024; Zhang et al., 2022).
Bukti untuk analisis emosi ada, tetapi lebih tipis di konteks perbankan Indonesia. IndoBERT dapat mengklasifikasi emosi Indonesia dengan F1 sekitar 0.76–0.79 pada benchmark tweet dan hingga 0.93 pada tugas multi-label tertentu (Ahmadian et al., 2023; Shaw et al., 2025; Amalia et al., 2025). Dalam layanan finansial, emosi seperti trust, joy, anticipation, anger, fear, dan sadness memang muncul dan berhubungan dengan persepsi layanan, tetapi sebagian studi emosi perbankan masih berbasis leksikon, bukan model bank-Indonesia yang tervalidasi secara khusus (Omotosho, 2021; Perea-Khalifi et al., 2024; Dhar & Bose, 2022).
Results Timeline
2017
1 paper: (Al-Moslmi et al., 2017)
2018
1 paper: (Mozetič et al., 2018)
2022
1 paper: (Andrian et al., 2022)
2024
2 papers: (Yulianti & Nissa, 2024; Jazuli et al., 2024)
2025
5 papers: (Pardamean et al., 2025; Dhendra, 2025; Syaripudin et al., 2025; Tomasaputra & Siallagan, 2025; Maretta & Meiriza, 2025)
2026
10 papers: (Casanova et al., 2026; Saputra et al., 2026; Zahratussyafitri et al., 2026; Setyawati et al., 2026; Hazz & Wahyuningsih, 2026; Susanto et al., 2026; Nataprawira & Nurhaida, 2026; Doewes & Widoyono, 2026; Citra & Ghifari, 2026; Sihombing et al., 2026) Figure 4: Linimasa hasil riset, marker besar lebih tersitasi
Top Contributors
Type
Name
Papers
Author
Hendri Ahmadian
(Ahmadian et al., 2024; Ahmadian et al., 2023)
Author
Ken Ditha Tania
(Casanova et al., 2026; Tania & Afrina, 2026; Fatihaturrahmah & Tania, 2025)
Author
Allsela Meiriza
(Casanova et al., 2026; Maretta & Meiriza, 2025)
Journal
Journal of Applied Informatics and Computing
(Casanova et al., 2026; Maretta & Meiriza, 2025; Simarmata & Sasongko, 2025; Tania & Afrina, 2026)
Journal
International Journal of Bank Marketing
(Ghadiridehkordi et al., 2024; Çallı, 2022)
Journal
Neural Computing and Applications
(Mahmood et al., 2023; Alrizq & Alghamdi, 2024)
Figure 5: Penulis dan jurnal paling sering muncul
4. Discussion
Secara metodologis, analisis ini sangat relevan untuk 13 bank digital karena langsung memetakan suara pelanggan ke dimensi layanan yang bisa ditindaklanjuti, terutama reliability, responsiveness, efficiency, usability, security, dan trust (Tomasaputra & Siallagan, 2025; Oh & Kim, 2022; Al-Kamal et al., 2025; Da Costa Martins, 2026). Korelasinya juga masuk akal: sentimen dan topik tertentu berkaitan dengan rating, kepuasan, kepercayaan, dan niat adopsi, dengan keamanan, kemudahan, dan kualitas layanan berulang kali muncul sebagai determinan utama (Dhar & Bose, 2022; Oh & Kim, 2022; Desiraju et al., 2024; Kantika et al., 2022).
Namun, bukti kausal tentang “dampak” masih terbatas. Sebagian besar paper menunjukkan bahwa analisis sentimen/ABSA membantu mengidentifikasi prioritas perbaikan, bukan bahwa penerapannya terbukti menyebabkan retensi, loyalitas, atau perbaikan performa bank di dunia nyata (Casanova et al., 2026; Tania & Afrina, 2026; Leem & Eum, 2021; Albesher & Alsanousi, 2026). Ini penting karena banyak studi berhenti pada klasifikasi dan interpretasi, tanpa evaluasi intervensi sesudah bank memperbaiki fitur tertentu.
Masalah validitas juga nyata. Banyak dataset memakai weak labels dari rating, pseudo-label otomatis, atau model lain, yang bisa menambah noise dan circularity; neutral dan mixed sentiment juga tetap paling sulit; dan evaluasi acak pada data temporal dapat melebihkan performa dibanding skenario produksi nyata (Setyawati et al., 2026; Bimasena et al., 2026; Perwira et al., 2025; Maretta & Meiriza, 2025; Mozetič et al., 2018; Hazz & Wahyuningsih, 2026).
Akhirnya, studi 13 bank juga harus memperhitungkan etika dan privasi. Ulasan publik tetap membawa risiko re-identifikasi, dan anonimisasi sederhana tidak cukup; praktik yang lebih aman memerlukan minimisasi bahaya, transparansi, dan audit risiko privasi (Ford et al., 2021; Gadotti et al., 2024; Manzanares-Salor et al., 2024; Shahriar et al., 2025).
Claim
Evidence Strength
Reasoning
Papers
IndoBERT efektif untuk sentimen/ABSA bahasa Indonesia
Evidence strength: Strong (8/10)
Didukung banyak benchmark dan domain Indonesia
(Yulianti & Nissa, 2024; Doewes & Widoyono, 2026; Dhendra, 2025; Sihombing et al., 2026)
Keluhan bank digital terkonsentrasi pada reliability dan support
Evidence strength: Strong (8/10)
Konsisten lintas studi bank, e-wallet, dan kualitas layanan
(Simarmata & Sasongko, 2025; Tania & Afrina, 2026; Zahratussyafitri et al., 2026; Adiningtyas & Auliani, 2024)
ABSA lebih berguna daripada polaritas tunggal untuk 13 bank
Evidence strength: Moderate (7/10)
Ulasan multi-aspek dan mixed sentiment berulang kali dilaporkan
(Pardamean et al., 2025; Wirawan et al., 2026; Halik et al., 2026)
Analisis emosi menambah sinyal di luar sentimen
Evidence strength: Moderate (5/10)
Ada bukti teknis dan konseptual, tetapi validasi perbankan Indonesia masih terbatas
(Amalia et al., 2025; Omotosho, 2021; Dhar & Bose, 2022)
Dampak bisnis kausal langsung sudah terbukti kuat
Evidence strength: Weak (2/10)
Mayoritas studi observasional tanpa evaluasi intervensi
(Casanova et al., 2026; Albesher & Alsanousi, 2026; Alrizq & Alghamdi, 2024)
Figure 6: Klaim kunci dan kekuatan evidensinya
5. Conclusion
Secara keseluruhan, analisis aspect category, opinion, sentiment, dan emotion dengan IndoBERT relevan untuk menilai 13 bank digital Indonesia karena dapat mengubah ulasan mentah menjadi peta masalah layanan yang spesifik. Korelasinya dengan kepuasan, trust, rating, dan kualitas layanan tampak cukup konsisten, tetapi dampak kausal pada hasil bisnis masih belum mapan dan desain studi lintas-13-bank yang kuat belum tersedia.
Research Gaps
Literatur saat ini padat pada klasifikasi sentimen aplikasi tunggal atau 2–3 bank, tetapi tipis pada evaluasi komparatif 13 bank dengan anotasi manusia yang kaya. Celah terbesar bukan lagi “apakah IndoBERT bisa bekerja,” melainkan “apakah hasilnya valid, sebanding lintas bank, dan cukup rinci untuk keputusan operasional.”
Google Play
Twitter X
Manual Label
Cross Bank
Intervensi
Sentimen Bank
29 papers
8 papers
12 papers
2 papers
No papers
ABSA Bank
7 papers
1 paper
6 papers
1 paper
No papers
Emosi Bank
4 papers
3 papers
3 papers
No papers
No papers
Trust Adoption
1 paper
No papers
2 papers
No papers
No papers
Privasi Teks
No papers
No papers
No papers
No papers
No papers
Studi lintas-bank besar masih jarang, dan kebanyakan hanya mencakup satu aplikasi atau tiga bank (Syaripudin et al., 2025; Tomasaputra & Siallagan, 2025; Andrian et al., 2022). Studi emosi juga tertinggal jauh dibanding sentimen dan ABSA pada konteks bank Indonesia, meski emosi seperti trust, anger, dan joy tampak relevan secara teoritis dan empiris di domain finansial lain (Omotosho, 2021; Perea-Khalifi et al., 2024; Amalia et al., 2025). Kesenjangan lain adalah kurangnya validasi temporal, lintas-platform, dan privasi-terjaga, padahal domain shift dan risiko re-identifikasi sudah jelas terdokumentasi (Mozetič et al., 2018; Fatihaturrahmah & Tania, 2025; Manzanares-Salor et al., 2024).
Open Research Questions
Pertanyaan berikut paling bernilai untuk studi lanjutan pada 13 bank digital Indonesia.
Question
Why
Apakah model IndoBERT yang dilatih pada satu bank tetap akurat ketika diuji pada 12 bank digital Indonesia lain?
Ini menguji generalisasi lintas-bank, bukan hanya kecocokan pada satu korpus pelatihan.
Apakah aspect-category-opinion-sentiment quadruple extraction memberi wawasan operasional yang lebih baik daripada ABSA biasa pada ulasan bank digital Indonesia?
Ini dapat menangkap opini implisit dan hubungan aspek-opini yang hilang pada label polaritas sederhana.
Apakah perbaikan pada aspek reliability yang diidentifikasi model benar-benar menurunkan keluhan dan menaikkan kepuasan pada periode berikutnya?
Ini mengubah literatur dari deteksi deskriptif menjadi evaluasi dampak kausal yang praktis.
Tinjauan ini menunjukkan bahwa IndoBERT sudah cukup matang untuk studi 13 bank digital Indonesia, tetapi nilai ilmiah tertinggi akan datang dari desain yang ketat, anotasi valid, dan evaluasi lintas-bank yang benar-benar adil.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
D. (2025). Benchmarking IndoBERT and Transformer Models for Sentiment Classification on Indonesian E-Government Service Reviews. Jurnal Transformatika. https://doi.org/10.26623/transformatika.v23i1.12095
Adiningtyas, H., & Auliani, A. S. (2024). Sentiment analysis for mobile banking service quality measurement. Procedia Computer Science. https://doi.org/10.1016/j.procs.2024.02.150
Afandy, S. N., Hindrayani, K. M., & Damaliana, A. T. (2026). Comparison of the Effectiveness IndoBERT and mBERT for Sentiment Analysis of SME Customer Reviews. bit-Tech. https://doi.org/10.32877/bt.v8i3.3501
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2023). Transformer-Based Indonesian Language Model for Emotion Classification and Sentiment Analysis. 2023 International Conference on Information Technology and Computing (ICITCOM), 209-214. https://doi.org/10.1109/icitcom60176.2023.10442970
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2024). Hybrid Models for Emotion Classification and Sentiment Analysis in Indonesian Language. Appl. Comput. Intell. Soft Comput., 2024. https://doi.org/10.1155/2024/2826773
Al-Kamal, A. M., Samsuri, A., Arshad, I., Hadi, N., & Wijaya, M. W. (2025). EVALUATING SERVICE QUALITY, CUSTOMER SATISFACTION, AND PERCEIVED TRUST OF ISLAMIC DIGITAL BANKS: INDONESIA AND MALAYSIA. Jurnal Ekonomi dan Bisnis Islam (Journal of Islamic Economics and Business). https://doi.org/10.20473/jebis.v11i2.80239
Al-Moslmi, T., Omar, N., Abdullah, S., & Albared, M. (2017). Approaches to Cross-Domain Sentiment Analysis: A Systematic Literature Review. IEEE Access, 5, 16173-16192. https://doi.org/10.1109/access.2017.2690342
Albesher, A., & Alsanousi, B. (2026). Retrieval-augmented generation analysis of user reviews in Saudi mobile banking apps: a comparative user experience study of iOS and Android. PeerJ Comput. Sci., 12, e3565. https://doi.org/10.7717/peerj-cs.3565
Alrizq, M., & Alghamdi, A. (2024). Customer satisfaction analysis with Saudi Arabia mobile banking apps: a hybrid approach using text mining and predictive learning techniques. Neural Computing and Applications, 36, 6005 - 6023. https://doi.org/10.1007/s00521-023-09400-4
Amalia, A., Lydia, M. S., Nainggolan, P. I., & Ginting, D. S. B. (2025). Multi-Label Emotion Classification for Indonesian Text using IndoBERT Fine-Tuning. 2025 9th International Conference on Electrical, Telecommunication and Computer Engineering (ELTICOM), 293-299. https://doi.org/10.1109/elticom67568.2025.11336043
Andrian, B., Simanungkalit, T., Budi, I., & Wicaksono, A. (2022). Sentiment Analysis on Customer Satisfaction of Digital Banking in Indonesia. International Journal of Advanced Computer Science and Applications. https://doi.org/10.14569/ijacsa.2022.0130356
Arif, E., Suherman, S., & Widodo, A. P. (2026). Analyzing Public Sentiment on Digital Banks in Indonesia via Social Media X. Aptisi Transactions on Technopreneurship (ATT). https://doi.org/10.34306/att.v8i1.530
Assani, M. Y., Rudiyan, A., & Radiyah, U. (2025). NLP-Based Sentiment Analysis of Islamic Mobile BankingReviews for Digital Service Quality Enhancement. Jurnal Bumigora Information Technology (BITe). https://doi.org/10.30812/bite.v7i2.5943
Bimasena, M. I., Prayoga, I., Mahendra, I., & Sidik, P. (2026). Benchmarking IndoBERT and Multilingual BERT for Indonesian Financial News Sentiment Classification. JURNAL TEKNOLOGI DAN OPEN SOURCE. https://doi.org/10.36378/jtos.v9i1.5583
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
Çallı, L. (2022). Exploring mobile banking adoption and service quality features through user-generated content: the application of a topic modeling approach to Google Play Store reviews. International Journal of Bank Marketing. https://doi.org/10.1108/ijbm-08-2022-0351
Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i2.12436
Citra, M. B., & Ghifari, N. T. A. (2026). Fine-Grained Aspect-Based Sentiment Analysis on Indonesian E-Commerce Reviews Using Multi-Task Learning with Pretrained Transformer Models. 2026 International Conference on Smart Computing, IoT, and Machine Learning (SIML), 1-6. https://doi.org/10.1109/siml69834.2026.11621828
Da Costa Martins, A. (2026). Mobile Banking Service Quality and Trust as Determinants of Customer Satisfaction in the Digital Banking Era. PERCIPIENCE International Journal of Social, Administration, & Entrepreneurship. https://doi.org/10.33474/percipience.v5i2.25203
Desiraju, K., Mishra, A. N., & Sengupta, P. (2024). Customer perceptions on open banking apps: Insights using Structural topic modeling. Journal of Retailing and Consumer Services. https://doi.org/10.1016/j.jretconser.2024.104029
Dhar, S., & Bose, I. (2022). Walking on air or hopping mad? Understanding the impact of emotions, sentiments and reactions on ratings in online customer reviews of mobile apps. Decis. Support Syst., 162, 113769. https://doi.org/10.1016/j.dss.2022.113769
Doewes, A., & Widoyono, B. (2026). Aspect-Based Sentiment Analysis of Access by KAI Application Reviews Using IndoBERT for Multi-Label Classification Tasks. Jurnal Teknik Informatika (Jutif). https://doi.org/10.52436/1.jutif.2026.7.1.5402
Fatihaturrahmah, A., & Tania, K. D. (2025). A Hybrid Approach of Aspect-Based Sentiment Analysis and Knowledge Extraction for Evaluating Security Perceptions in Digital Payment Applications. Scientific Journal of Informatics. https://doi.org/10.15294/sji.v12i4.31557
Ford, E., Shepherd, S., Jones, K., & Hassan, L. (2021). Toward an Ethical Framework for the Text Mining of Social Media for Health Research: A Systematic Review. Frontiers in Digital Health, 2. https://doi.org/10.3389/fdgth.2020.592237
Gadotti, A., Rocher, L., Houssiau, F., Creţu, A.-M., & De Montjoye, Y.-A. (2024). Anonymization: The imperfect science of using data while preserving privacy. Science Advances, 10. https://doi.org/10.1126/sciadv.adn7053
Ghadiridehkordi, A., Shao, J., Boojihawon, R., Wang, Q., & Li, H. (2024). Leveraging sentiment analysis via text mining to improve customer satisfaction in UK banks. International Journal of Bank Marketing. https://doi.org/10.1108/ijbm-05-2024-0323
Halik, M., Hazriani, H., Nasrullah, N., Achmad, A., Nurtanio, I., & Wardi, W. (2026). Aspect-Based Sentiment Analysis of Indonesian Electric Vehicles on Media Social. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i4.13055
Hayatin, N., Alias, S., Lai, P.-H., & Setiowati, Y. (2024). Multi-aspect Extraction in Indonesian Reviews Through Multi-label Classification Using Pre-trained BERT Models. 17-31. https://doi.org/10.1007/978-981-97-0293-0_2
Hazz, H. S., & Wahyuningsih, D. (2026). Comparative Analysis of IndoBERT and BiLSTM For Public Sentiment Classification Toward The Indonesian National Police on Youtube. Journal of Deep Learning, Computer Vision and Digital Image Processing. https://doi.org/10.61255/decoding.v4i2.1144
Jazuli, A., W., & Kusumaningrum, R. (2024). Optimizing Aspect-Based Sentiment Analysis Using BERT for Comprehensive Analysis of Indonesian Student Feedback. Applied Sciences. https://doi.org/10.3390/app15010172
Kadarsih, K., & Pujianto, D. (2025). APPLICATION OF TRANSFORMER MODEL AND WORD EMBEDDING IN SENTIMENT ANALISYS OF INDONESIAN E-COMMERCE APPLICATION REVIEW. Journal of Computer Networks, Architecture and High Performance Computing. https://doi.org/10.47709/cnahpc.v7i3.6354
Kantika, K., Kurniasari, F., & Mulyono, M. (2022). The Factors Affecting Digital Bank Services Adoption Using Trust as Mediating Variable. Journal of Business and Management Review. https://doi.org/10.47153/jbmr310.4882022
Leem, B., & Eum, S.-W. (2021). Using text mining to measure mobile banking service quality. Ind. Manag. Data Syst., 121, 993-1007. https://doi.org/10.1108/imds-09-2020-0545
Mahmood, T., Naseem, S., Ashraf, R., Asif, M., Umair, M., & Shah, M. (2023). Recognizing factors effecting the use of mobile banking apps through sentiment and thematic analysis on user reviews. Neural Computing and Applications, 35, 19885-19897. https://doi.org/10.1007/s00521-023-08827-z
Manzanares-Salor, B., Sánchez, D., & Lison, P. (2024). Evaluating the disclosure risk of anonymized documents via a machine learning-based re-identification attack. Data Mining and Knowledge Discovery, 38, 4040 - 4075. https://doi.org/10.1007/s10618-024-01066-3
Maretta, A., & Meiriza, A. (2025). Aspect-Based Sentiment Analysis of Hospital Service Reviews Using Fine-Tuned IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v9i5.10765
Mozetič, I., Torgo, L., Cerqueira, V., & Smailovic, J. (2018). How to evaluate sentiment classifiers for Twitter time-ordered data?. PLoS ONE, 13. https://doi.org/10.1371/journal.pone.0194317
Mulyanto, S., Yonia, D. L., Situmorang, K. L., & Sutejo, B. (2025). Sentiment Classification of Livin’ by Mandiri Reviews in Indonesia Using LSTM for Digital Banking Service Improvement. JURNAL EKONOMI KREATIF DAN MANAJEMEN BISNIS DIGITAL. https://doi.org/10.55047/jekombital.v4i1.1011
Nataprawira, H. I., & Nurhaida, I. (2026). IndoBERT-Based Sentiment Analysis of Indonesian Social Media Discourse on AI-Generated Images. sinkron. https://doi.org/10.33395/sinkron.v10i3.16242
Oh, Y., & Kim, J.-M. (2022). What Improves Customer Satisfaction in Mobile Banking Apps? An Application of Text Mining Analysis. Asia Marketing Journal. https://doi.org/10.53728/2765-6500.1581
Omotosho, B. S. (2021). Analysing User Experience of Mobile Banking Applications in Nigeria: A Text Mining Approach. Central Bank of Nigeria Journal of Applied Statistics. https://doi.org/10.33429/cjas.12121.4/6
Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. 2025 1st International Conference on Data Science and Geoinformatics (ICDSG), 37-42. https://doi.org/10.1109/icdsg67714.2025.11381388
Perea-Khalifi, D., Irimia-Diéguez, A. I., & Palos-Sanchez, P. (2024). Exploring the determinants of the user experience in P2P payment systems in Spain: a text mining approach. Financial Innovation, 10, 1-32. https://doi.org/10.1186/s40854-023-00496-0
Perwira, R., Permadi, V. A., Purnamasari, D., & Agusdin, R. P. (2025). Domain-Specific Fine-Tuning of IndoBERT for Aspect-Based Sentiment Analysis in Indonesian Travel User-Generated Content. Journal of Information Systems Engineering and Business Intelligence. https://doi.org/10.20473/jisebi.11.1.30-40
Prasetyo, M. J., & Agastya, I. M. D. (2024). Sentiment Analysis of Banking Application Reviews on Google Play Store using Support Vector Machine Algorithm. SISTEMASI. https://doi.org/10.32520/stmsi.v13i6.4536
Sanjaya, S., Guntara, R. G., & Maesaroh, S. S. (2025). Sentiment Analysis of LinkAja Digital Wallet Application Reviews on Google Play Store using Transfer Learning IndoBERT. INOVTEK Polbeng - Seri Informatika. https://doi.org/10.35314/afjx7b16
Saputra, Z., Enhartana, A. C., Sensuse, D., Lusa, S., Mailinda, I., & Sofia, N. (2026). User Review-Based Knowledge Discovery Model Using Knowledge Graph to Support Proactive Decision-Making in Digital Banking: A Case Study of Bank XYZ. 2026 5th International Conference on Electronics Representation and Algorithm (ICERA), 59-67. https://doi.org/10.1109/icera72709.2026.11666594
Setyawati, E., B., & Saputra, D. (2026). Rule-Based Aspect Extraction and IndoBERT-Based Sentiment Classification of Ruparupa Mobile Application Reviews. Journal of Information Systems and Informatics. https://doi.org/10.63158/journalisi.v8i4.1816
Shahriar, S., Dara, R. A., & Akalu, R. (2025). A comprehensive review of current trends, challenges, and opportunities in text data privacy. Comput. Secur., 151, 104358. https://doi.org/10.1016/j.cose.2025.104358
Shaw, C., LaCasse, P. M., & Champagne, L. E. (2025). Exploring emotion classification of indonesian tweets using large scale transfer learning via IndoBERT. Social Network Analysis and Mining, 15. https://doi.org/10.1007/s13278-025-01439-6
Sihombing, Y. O., Muchlisin, K., Arya, T., Mubarok, M. J., & Rachmadi, R. F. (2026). A Systematic Evaluation of BERT Classifiers for Indonesia-based Text Data. Techno.Com. https://doi.org/10.62411/tc.v25i2.15843
Simarmata, A. A. P., & Sasongko, T. B. (2025). Sentiment Analysis on BRImo Application Reviews Using IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v9i3.8162
Susanto, H., Dharmawan, W., Annisa, R., & Fitriana, L. A. (2026). Performance Evaluation of the BERT Model in Sentiment Analysis of DANA Application User Reviews. Journal of Artificial Intelligence and Engineering Applications (JAIEA). https://doi.org/10.59934/jaiea.v5i3.2359
Syaripudin, U., Gerhana, Y. A., Wahana, A., & Fuadi, R. (2025). Sentiment Analysis of Google Play Store Reviews on the Top Three Digital Banks in Indonesia Using Bidirectional Encoder Representations from Transformers (BERT). 2025 11th International Conference on Wireless and Telematics (ICWT), 1-5. https://doi.org/10.1109/icwt66752.2025.11181730
Tania, K. D., & Afrina, M. (2026). Knowledge Discovery in Sharia Mobile Banking Reviews Using Aspect-Based Sentiment Analysis and Machine Learning. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i1.11753
Tomasaputra, D., & Siallagan, M. (2025). Enhancing Digital Banking Experience Through Text Mining of e-Service Reviews in Indonesia. Ekonomis: Journal of Economics and Business. https://doi.org/10.33087/ekonomis.v9i2.2653
Wirawan, N. O. H., Chandra, G. J., Lucky, H., Pradana, R., & Sagala, N. T. M. (2026). Benchmarking Aspect-Based Sentiment Analysis on Indonesian Mobile JKN Reviews using Transformer Models. 2026 International Electronics Symposium (IES), 1-6. https://doi.org/10.1109/ies71033.2026.11702744
Yulianti, E., & Nissa, N. K. (2024). ABSA of Indonesian customer reviews using IndoBERT: single- sentence and sentence-pair classification approaches. Bulletin of Electrical Engineering and Informatics. https://doi.org/10.11591/eei.v13i5.8032
Zahra, N., Farhanatussaidah, S., Afifah, N. N., Muthoharoh, L., Satria, A., & Manullang, M. C. T. (2026). Benchmarking Logistic Regression, SVM, Naive Bayes, and IndoBERT Fine-Tuning for Sentiment Analysis on Indonesian Product Reviews. ArXiv, abs/2605.03439. https://doi.org/10.48550/arxiv.2605.03439
Zahratussyafitri, Z., Hartomo, K., & Nataliani, Y. (2026). Analysis of Banking Application Reviews Using a Topic-based Sentiment Analysis Approach with Rule-based Lexicon and LDA. International Journal of Advances in Data and Information Systems. https://doi.org/10.59395/ijadis.v7i2.1548
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhang, H., Chen, Z., Chen, B., Hu, B., Li, M., Yang, C., & Jiang, B. (2022). Complete quadruple extraction using a two-stage neural model for aspect-based sentiment analysis. Neurocomputing, 492, 452-463. https://doi.org/10.1016/j.neucom.2022.04.027