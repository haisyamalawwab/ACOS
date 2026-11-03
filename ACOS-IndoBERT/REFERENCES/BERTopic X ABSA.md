# Integrasi BERTopic–ABSA memberi **wawasan lebih terperinci**, tetapi peningkatan akurasi dibanding klasifikasi tingkat dokumen belum terbukti langsung.

Integrasi pemodelan topik BERTopic dengan analisis sentimen berbasis aspek (*aspect-based sentiment analysis*, ABSA) berbasis transformer menawarkan dua keuntungan berbeda: menemukan tema yang dibicarakan pelanggan dan mengaitkan sentimen dengan aspek tertentu. Namun, bukti harus dipisahkan menjadi **kualitas topik, kinerja klasifikasi aspek, dan manfaat analitis**—bukan dianggap sebagai satu peningkatan akurasi yang sama. Literatur ABSA mendukung analisis opini yang lebih terarah, tetapi juga menunjukkan keterbatasan keragaman domain dan ketidakcocokan dataset (Hua et al., 2023; Brauwers & Frasincar, 2021; Zhang et al., 2022).

## Keunggulan yang Terbukti

| Kekuatan Bukti | Klaim |
|---|---|
| Evidence strength: Strong (8/10) | ABSA mempertahankan sentimen berbeda terhadap beberapa aspek dalam satu ulasan, yang tidak direpresentasikan oleh satu label keseluruhan (Mughal et al., 2024; Apostol et al., 2025). |
| Evidence strength: Moderate (6/10) | BERTopic menghasilkan tema semantis yang lebih terperinci dan berguna bagi pengembang, meskipun topiknya dapat berlebihan atau redundan (Tong et al., 2025). |
| Evidence strength: Weak (2/10) | Keunggulan akurasi **integrasi itu sendiri** belum terisolasi: studi terdekat melaporkan kualitas topik, keunggulan terhadap baseline tertentu, atau wawasan tematis, bukan perbandingan terkontrol yang sama dengan klasifikasi dokumen (Puvvula & Rodda, 2026; Tong et al., 2025; Priambodo et al., 2026). |

**Figure 1:** Kekuatan bukti manfaat dan batas integrasi BERTopic dengan ABSA

Keuntungan utama ABSA bukan sekadar mengganti algoritma, melainkan mengubah keluaran: dari “ulasan negatif” menjadi “produk positif, pengiriman negatif”. Pembedaan tersebut relevan ketika opini terhadap fitur saling bertentangan, sementara klasifikasi dokumen merangkum kecenderungan keseluruhan (Mughal et al., 2024; Kumar et al., 2026; Koundal & Ranjan, 2026). Hubungan aspek–opini juga memungkinkan ekstraksi pasangan atau triplet, bukan hanya polaritas teks (Aziz et al., 2024; Zhu et al., 2022).

BERTopic dan ABSA tetap menjalankan fungsi berbeda. BERTopic mengelompokkan teks berdasarkan representasi semantis dan membentuk representasi topik, sedangkan ABSA harus menentukan sentimen terhadap target tertentu (Tong et al., 2025; Yu et al., 2023). Karena itu, menempelkan sentimen dokumen pada kelompok topik **tidak otomatis membuktikan atribusi sentimen per aspek**; misalnya, kerangka Steam menggunakan BERT untuk sentimen tingkat ulasan lalu BERTopic untuk tema (Priambodo et al., 2026). Pendekatan aspek membutuhkan pengondisian target atau mekanisme perhatian yang benar-benar menghubungkan konteks dengan aspek (Chong et al., 2026; Ahmed et al., 2024; Koundal & Ranjan, 2026).

## Benchmark Penemuan Topik

| Konteks | Hasil yang Dilaporkan | Makna |
|---|---|---|
| *No Man’s Sky*, Steam | Koherensi UCI BERTopic **0.279**, tertinggi dibanding LDA/NMF | Bukti langsung kualitas topik game (Tong et al., 2025) |
| Teks pendek Indonesia | C_v **0.7539**, keragaman topik **0.9285** | Integrasi IndoBERTweet, bukan ulasan pelanggan/game (Adam et al., 2026) |
| Ulasan film Tiongkok | NPMI **0.0394**, versus LDA **−0.0048**, NMF **0.0312** | Keunggulan koherensi, bukan akurasi ABSA (Lyu et al., 2026) |
| Gibbs-BERTopic | Silhouette meningkat **>20%**, koherensi hampir **20%** | Perbaikan terhadap BERTopic standar (Zhu & Liu, 2025) |
| *Elden Ring*, Metacritic | LDA-BERT: koherensi **1%** lebih tinggi daripada LDA | LDA tetap terbaik pada silhouette (Dehghani & Zaman, 2024) |

**Figure 2:** Benchmark kualitas topik dan variasi hasil antar konteks

Bukti gaming paling langsung menunjukkan BERTopic mampu memisahkan laporan bug dan gangguan menjadi masalah yang lebih spesifik. Wawancara dengan tujuh pengembang juga menunjukkan kegunaan informasi tersebut untuk perbaikan game dan pemantauan opini pemain (Tong et al., 2025). Namun, granularitas berlebihan memerlukan pemeriksaan dan pengurangan topik agar hasil tetap ringkas (Tong et al., 2025).

Dalam layanan pelanggan, embedding khusus domain seperti FinBERT menghasilkan topik pengaduan keuangan yang lebih baik daripada embedding umum (Raju et al., 2022). Pada perbankan digital, 160 topik BERTopic harus digabung menjadi 20 makrotopik dan divalidasi dua pakar (Yu et al., 2026). Pada hotel, pendekatan dinamis menemukan perubahan topik dan sentimen, tetapi klasifikatornya LSTM—bukan transformer—sehingga tidak menjadi uji langsung konfigurasi yang ditanyakan (Kundana et al., 2026).

Angka koherensi tersebut tidak mengukur ketepatan polaritas. Selain itu, BERTopic standar masih menghadapi sparsitas, kebisingan, dan ketidakpastian pada dataset kecil (Zhu & Liu, 2025). Dengan demikian, kualitas kelompok topik perlu dinilai terpisah dari keberhasilan ABSA.

## Benchmark Ulasan Pelanggan

| Model dan Dataset | Benchmark | Batas Interpretasi |
|---|---|---|
| RoBERTa, 3,500 ulasan Trustpilot | Akurasi **>90%**, 14 aspek | ABSA teranotasi, tanpa BERTopic (Davoodi et al., 2025) |
| LDA–semantik–BERT, hotel | F1 kategorisasi **0.89**, sentimen **0.97** | Integrasi topik, tetapi menggunakan LDA (Andono et al., 2022) |
| LSA+DeBERTa, SemEval-2014 | Restoran **90.33%**, laptop **86.21%** akurasi | Benchmark aspek, bukan integrasi BERTopic (Jayakody et al., 2024) |
| TASCI, restoran/laptop | Macro-F1 **83.38% / 78.63%** | Integrasi konteks intensi (Chaudhry et al., 2025) |
| DeBERTa-v3–BiGRU–perhatian aspek, Amazon | Akurasi **0.737**, macro-F1 **0.757** | Tiga aspek operasional (Moushi et al., 2026) |

**Figure 3:** Benchmark ABSA pelanggan dengan tugas dan batas pembandingnya

Transformer menunjukkan keuntungan yang konsisten dalam pemodelan konteks, tetapi besarnya bervariasi. DC-BERT melaporkan akurasi 84.48% pada laptop dan 92.86% pada restoran; model RoBERTa–CNN–BiLSTM melaporkan 92.33% pada evaluasi tiga dataset (Rajan & Manur, 2024; Rana et al., 2024). Evaluasi transformer lain menghasilkan akurasi RoBERTa 89.16% pada MAMS/SemEval dan 97.62% pada Naver, menegaskan ketergantungan hasil pada dataset (Perikos & Diamantopoulos, 2024).

Perbandingan terkontrol **di dalam tugas ABSA** lebih informatif daripada membandingkan angka lintas studi. RoBERTa mencapai F1 0.92 dibanding LSTM 0.82 dan CNN 0.84; AraBERT mencapai F1 0.97 untuk kebersihan dibanding LinearSVC 0.91 (Astri et al., 2026; Zaid et al., 2025). Ablasi DeBERTa-v3 juga mendukung kontribusi perhatian khusus aspek dan pemrosesan sekuensial, tetapi bukan kontribusi BERTopic (Moushi et al., 2026).

Keuntungan praktisnya mencakup pemetaan kebutuhan regional: integrasi BERTopic–ABSA pada 100,000 ulasan aplikasi menemukan 12 topik dan perbedaan perhatian antarnegara (Kotsifas et al., 2025). Analisis hotel berbasis sentimen–topik menemukan 26 tema dengan hubungan berbeda terhadap rating, sedangkan model banking menunjukkan bahwa konteks topik memoderasi hubungan sentimen–rating (Kumar, 2025; Yu et al., 2026). Hasil tersebut mendukung diagnosis pengalaman pelanggan, bukan klaim peningkatan akurasi universal.

## Benchmark Ulasan Gaming

| Pendekatan | Data dan Hasil | Apa yang Diukur |
|---|---|---|
| LDA + BERT-TFM ABSA | 1.6 juta ulasan; micro-F1 **75.48%**, macro-F1 **60.46%** | Aspek dan sentimen gaming (Yu et al., 2023) |
| Word2Vec + SVM, RPG Steam | Macro-F1 **88.6%** | Polaritas ulasan keseluruhan (Alfarisyi et al., 2025) |
| SBERT–TF-IDF–Naïve Bayes | 147,586 ulasan; F1 **94.0%**, ROC-AUC **95.0%** | Klasifikasi sentimen Steam (Moattar, 2026) |
| BiLSTM + perhatian | 50,000 ulasan; akurasi **83%**, weighted-F1 **85%** | Sentimen dokumen, recall negatif 90% (Oktarian et al., 2026) |
| SVM + SMOTE | Akurasi **98.18%** | Sentimen dan unsur promosi (Nalluri et al., 2025) |

**Figure 4:** Benchmark gaming yang membedakan ABSA dari klasifikasi ulasan

Studi esports paling relevan menggunakan **LDA, bukan BERTopic**, dengan sekitar 3,000 kalimat teranotasi untuk pelatihan ABSA dan hanya aspek eksplisit yang diberi polaritas (Yu et al., 2023). Pemilihan model berdasarkan skor set uji merupakan keterbatasan tambahan dalam menafsirkan estimasi generalisasi (Yu et al., 2023).

Nilai analitisnya jelas: grafik dan gameplay dinilai relatif positif, sementara optimasi, pembaruan, server, kecurangan, dan matchmaking menunjukkan masalah berbeda (Yu et al., 2023). Penggabungan prevalensi dan sentimen menghasilkan prioritas spesifik untuk setiap game, bukan sekadar daftar ulasan negatif (Yu et al., 2023).

**Macro-F1 60.46% tidak boleh dibandingkan langsung dengan F1 dokumen 94.0%.** Target keluaran, anotasi, dan agregasi metrik berbeda. Bahkan klasifikasi dokumen menunjukkan variasi besar: Random Forest menghasilkan F1 62%, sementara BiLSTM pada *Marvel Rivals* mencapai akurasi 89% tetapi F1 kelas negatif hanya 0.72 (Purbolaksono, 2024; Soetasad & Fernando, 2025). Sinyal rekomendasi Steam juga tidak selalu sesuai dengan isi teks (Yu et al., 2023; Haditira et al., 2024).

## Batas dan Evaluasi Pembanding

| Dimensi Evaluasi | Pengukuran yang Diperlukan | Dasar Empiris |
|---|---|---|
| Penemuan aspek | Koherensi, keragaman, validasi manusia | Topik semantis tetap memerlukan interpretasi (Yu et al., 2023) |
| Ekstraksi dan polaritas | F1 aspek, macro-F1 sentimen, evaluasi gabungan | Akurasi ekstraksi dan sentimen dapat berbeda (Samia et al., 2022) |
| Ketahanan domain | Uji lintas game, layanan, dan bahasa | Kinerja model sensitif terhadap domain (Mughal et al., 2024) |
| Efisiensi | Latensi, memori, biaya anotasi | Transformer menambah biaya dan latensi (Astri et al., 2026) |
| Atribusi manfaat | Ablasi komponen pada data yang sama | Tahap terpisah berisiko propagasi kesalahan (Gupta et al., 2026) |

**Figure 5:** Dimensi evaluasi untuk mengisolasi manfaat tambahan integrasi model

Klaim performa harus mempertimbangkan ketimpangan kelas: model BERT-ABSA mencapai akurasi hotel 96.95%, tetapi pada domain buku F1 hanya 54.97%, dibanding 81.36% untuk pendekatan multitugas (Chong et al., 2026). Bahasa juga mengubah benchmark: BERT melaporkan akurasi hotel Arab 89.51% tetapi buku Arab 73.23%, sedangkan ConvBERT terbaik untuk sentimen restoran Turki mencapai 86.91% (Abdelgwad et al., 2021; Bilgin & Turan, 2025).

Aspek implisit, ambiguitas, dan transfer domain tetap menjadi kelemahan, meskipun disambiguasi makna kata menunjukkan manfaat melalui ablasi (Jia et al., 2026; Nadeem et al., 2025; Kumari, 2025). Pendekatan tanpa anotasi aspek mengurangi kebutuhan supervisi, tetapi sebagian masih memerlukan aspek yang ditentukan sebelumnya dan hanya mendukung polaritas biner (Prete et al., 2025).

Biaya komputasi bukan keuntungan otomatis integrasi. DistilBERT berbasis perhatian mempertahankan sekitar 98.4% akurasi BERT-base sambil mengurangi memori sekitar 40%, memperlihatkan alternatif efisiensi yang perlu diperbandingkan (Kausar et al., 2026). Interpretabilitas juga perlu diuji, misalnya melalui SHAP atau LIME, bukan diasumsikan muncul karena model menggunakan perhatian (Perikos & Diamantopoulos, 2024).

**Pergeseran terpenting adalah dari label kepuasan keseluruhan menuju diagnosis masalah per aspek. Pertanyaan terbuka terbesar ialah seberapa besar BERTopic menambah ketepatan ABSA—di luar transformer itu sendiri—dalam uji pelanggan dan gaming dengan data, label, serta anggaran komputasi yang sama.**
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Abdelgwad, M. M., Soliman, T., & Taloba, A. (2021). Arabic aspect sentiment polarity classification using BERT. *Journal of Big Data, 9*, 1-15. https://doi.org/10.1186/s40537-022-00656-6
 
Adam, N., Gernowo, R., & Surarso, B. (2026). Integration of BERTopic and IndoBERTweet for Aspect-Based Sentiment Analysis (ABSA) on Short Text Data: A Case Study of Responses to Government Policies in 2025. *Jurnal Ekonomi Teknologi dan Bisnis (JETBIS)*. https://doi.org/10.57185/k9s34530
 
Ahmed, S., Samia, M. M., Sayma, M. H., Kabir, M. M., & Mridha, M. F. (2024). tRF-BERT: A transformative approach to aspect-based sentiment analysis in the bengali language. *PLOS ONE, 19*, e0308050 - e0308050. https://doi.org/10.1371/journal.pone.0308050
 
Alfarisyi, A. A., Purbolaksono, M. D., & Gozali, A. A. (2025). WORD EMBEDDING ANALYSIS IN SENTIMENT ANALYSIS USING MACHINE LEARNING: A CASE STUDY OF STEAM RPG GAME REVIEWS. *JSiI (Jurnal Sistem Informasi)*. https://doi.org/10.30656/jsii.v12i2.10917
 
Andono, P. N., Nugroho, R. A., & Harjo, B. (2022). Aspect-Based Sentiment Analysis for Hotel Review Using LDA, Semantic Similarity, and BERT. *International Journal of Intelligent Engineering and Systems*. https://doi.org/10.22266/ijies2022.1031.21
 
Apostol, E.-S., Pisica, A.-G., & Truică, C.-O. (2025). ATESA-BÆRT: A heterogeneous ensemble learning model for Aspect-Based Sentiment Analysis. *Knowl. Based Syst., 326*, 113987. https://doi.org/10.1016/j.knosys.2025.113987
 
Astri, R., Kamal, A., F., Z., Sari, I. U., Anggraini, P., & Budiman, A. (2026). Aspect-Based Sentiment Analysis for Product Review Mining with Transformer-Based Models. *Journal of Electrical Engineering and Computer Science (JEECS) | E-ISSN : 3089-5952*. https://doi.org/10.62379/jeecs.v2i1.37
 
Aziz, K., Ji, D.-H., Chakrabarti, P., Chakrabarti, T., Iqbal, M. S., & Abbasi, R. (2024). Unifying aspect-based sentiment analysis BERT and multi-layered graph convolutional networks for comprehensive sentiment dissection. *Scientific Reports, 14*. https://doi.org/10.1038/s41598-024-61886-7
 
Bilgin, M., & Turan, M. (2025). Aspect-Based Sentiment Analysis for Turkish Reviews Using Token and Sequential Classification Methods. *International Journal of Computer and Information Technology(2279-0764)*. https://doi.org/10.24203/2drscx54
 
Brauwers, G., & Frasincar, F. (2021). A Survey on Aspect-Based Sentiment Classification. *ACM Computing Surveys, 55*, 1 - 37. https://doi.org/10.1145/3503044
 
Chaudhry, H., Kulsoom, F., Khan, Z. U., Aman, M., Khan, S. U., & Albanyan, A. (2025). TASCI: transformers for aspect-based sentiment analysis with contextual intent integration. *PeerJ Computer Science, 11*. https://doi.org/10.7717/peerj-cs.2760
 
Chong, W.-K., Ng, H., Yap, T., Tan, I. K. T., Goh, V., Wong, L.-K., & Cher, D. T. (2026). Multitask Learning and BERT Embedding: A Comprehensive Approach to Subjectivity Detection and Aspect-Based Sentiment Analysis. *International Journal of Computational Intelligence Systems, 19*. https://doi.org/10.1007/s44196-026-01153-x
 
Davoodi, L., Mezei, J., & Heikkilä, M. (2025). Aspect-based sentiment classification of user reviews to understand customer satisfaction of e-commerce platforms. *Electron. Commer. Res., 26*, 1417-1459. https://doi.org/10.1007/s10660-025-09948-4
 
Dehghani, F., & Zaman, L. (2024). Exploring Players' Perspectives: A Comprehensive Topic Modeling Case Study on Elden Ring. *Inf., 15*, 573. https://doi.org/10.3390/info15090573
 
Gupta, S., Kumar, P., Rawat, S., Singh, A., Singhal, N., & Kumar, G. (2026). Hybrid classifier with aspect based feature set for sentiment analysis. *Discover Artificial Intelligence, 6*. https://doi.org/10.1007/s44163-026-01907-8
 
Haditira, R., Murdiansyah, D. T., & Astuti, W. (2024). Analisis Sentimen pada Steam Review Menggunakan Multinomial NaÃ¯ve Bayes dan Seleksi Fitur Gini Index Text. *KOMPUTEK*. https://doi.org/10.24269/jkt.v8i2.2981
 
Hua, Y. C., Denny, P., Wicker, J., & Taškova, K. (2023). A systematic review of aspect-based sentiment analysis: domains, methods, and trends. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-024-10906-z
 
Jayakody, D., Isuranda, K., Malkith, A., De Silva, N., Ponnamperuma, S. R., Sandamali, G. G. N., & Sudheera, K. (2024). Aspect-based Sentiment Analysis Techniques: A Comparative Study. *2024 Moratuwa Engineering Research Conference (MERCon)*, 205-210. https://doi.org/10.1109/mercon63886.2024.10688631
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Kausar, M. A., Nasar, M., Khairy, S. O. F., Hossain, S. E. M., & Soosaimanickam, A. (2026). A Lightweight DistilBERT-Attention Model for Aspect-Based Sentiment Analysis. *Journal of Computers, Mechanical and Management*. https://doi.org/10.57159/jcmm.5.4.26653
 
Kotsifas, M. F. A., Lüders, R., & Silva, T. H. (2025). How Culture Shapes Customers: A Cross-Continent Analysis of Apps Reviews Using NLP Techniques. 760-766. https://doi.org/10.5753/sbbd.2025.247502
 
Koundal, S., & Ranjan, S. (2026). A Context-Aware Model for Sentiment Analysis of Restaurant Reviews. *International Journal for Research in Applied Science and Engineering Technology*. https://doi.org/10.22214/ijraset.2026.78484
 
Kumar, M., Khan, L., Khan, M. Z., & Aljubayri, I. (2026). AAC-HABSA: An Adaptive Aspect Conditioning Framework for Interpretable and Robust Aspect-Based Sentiment Analysis. *Computer Modeling in Engineering & Sciences*. https://doi.org/10.32604/cmes.2026.081699
 
Kumar, N. (2025). Unpacking the Emotional Landscape of Reviews: Sentiment-Augmented Topic Modeling with Transformer Embeddings. *INTERNATIONAL JOURNAL OF SCIENTIFIC RESEARCH IN ENGINEERING AND MANAGEMENT*. https://doi.org/10.55041/ijsrem46998
 
Kumari, N. (2025). Aspect Based Sentiment Analysis for Product Reviews. *International Journal for Research in Applied Science and Engineering Technology*. https://doi.org/10.22214/ijraset.2025.69491
 
Kundana, D., Sarno, R., & Anggraini, R. N. E. (2026). Dynamic topic modeling for aspect categorization in aspect-based sentiment analysis using BERTopic on hotel reviews. *Procedia Computer Science*. https://doi.org/10.1016/j.procs.2026.07.119
 
Lyu, Y., Xiao, L.-Y., Luo, D.-S., & Wang, H.-J. (2026). BERTopic-Enhanced Joint Topic-Sentiment Analysis of Chinese Short Texts: A Comparative Computational Framework. *Proceedings of the 3rd International Conference on Machine Intelligence and Digital Applications*. https://doi.org/10.1145/3801438.3805833
 
Moattar, M. (2026). Lightweight hybrid adaptive weighted ensemble integrating fine-tuned SBERT with lexical and statistical models for robust steam review sentiment classification. *Discover Computing, 29*. https://doi.org/10.1007/s10791-026-10296-6
 
Moushi, S. S., Bhuiyan, M. S., Akter, N., Chakraborty, U., Akther, S., Islam, R., Shahiduzzaman, M., Kabtia, M., & Keneni, R. (2026). Multi-aspect sentiment classification on USA-based Amazon customer reviews with DeBERTa-v3 encoders and aspect attention. *Discover Analytics, 4*. https://doi.org/10.1007/s44257-026-00077-2
 
Mughal, N., Mujtaba, G., Shaikh, S., Kumar, A., & Daudpota, S. (2024). Comparative Analysis of Deep Natural Networks and Large Language Models for Aspect-Based Sentiment Analysis. *IEEE Access, 12*, 60943-60959. https://doi.org/10.1109/access.2024.3386969
 
Nadeem, A., Missen, M. S., Reshan, M. S. A., Memon, M. A., Asiri, Y., Nizamani, M. A., Alsulami, M., & Shaikh, A. (2025). Resolving ambiguity in natural language for enhancement of aspect-based sentiment analysis of hotel reviews. *PeerJ Computer Science, 11*. https://doi.org/10.7717/peerj-cs.2635
 
Nalluri, V., Wang, Y.-Y., Jeng, W.-D., & Chen, L.-S. (2025). Extracting Advertising Elements and the Voice of Customers in Online Game Reviews. *J. Theor. Appl. Electron. Commer. Res., 20*, 321. https://doi.org/10.3390/jtaer20040321
 
Oktarian, A. A., Wijaya, F. F., Luthfi, D. R., Muthoharoh, L., Satria, A., & Manullang, M. C. T. (2026). Enhancing Game Review Sentiment Classification on Steam Platform with Attention-Based BiLSTM. *ArXiv, abs/2605.01315*. https://doi.org/10.48550/arxiv.2605.01315
 
Perikos, I., & Diamantopoulos, A. (2024). Explainable Aspect-Based Sentiment Analysis Using Transformer Models. *Big Data Cogn. Comput., 8*, 141. https://doi.org/10.3390/bdcc8110141
 
Prete, S., Biancofiore, G. M., Narducci, F., Di Sciascio, E., & Di Noia, T. (2025). From Overall Sentiment to Aspect-Level Insights: A Pretraining Strategy for Unsupervised Aspect-based Sentiment Analysis. *Adjunct Proceedings of the 33rd ACM Conference on User Modeling, Adaptation and Personalization*. https://doi.org/10.1145/3708319.3733693
 
Priambodo, M. P., Doewes, A., & Rohmadi, A. (2026). Forecasting User Perception of Steam Game Reviews across Multiple Genres: A BERT Sentiment-Topic Framework with Topic Attribution. *Journal of Embedded Systems, Security and Intelligent Systems*. https://doi.org/10.59562/jessi.v7i3.13290
 
Purbolaksono, M. D. (2024). Sentiment Analysis of Game Review in Steam Platform using Random Forest. *International Journal on Information and Communication Technology (IJoICT)*. https://doi.org/10.21108/ijoict.v10i2.1007
 
Puvvula, D., & Rodda, S. (2026). A hybrid transformer architecture for unsupervised aspect‐based sentiment analysis. *ETRI Journal*. https://doi.org/10.4218/etrij.2025-0094
 
Rajan, A., & Manur, M. (2024). Aspect based sentiment analysis using fine-tuned BERT model with deep context features. *IAES International Journal of Artificial Intelligence (IJ-AI)*. https://doi.org/10.11591/ijai.v13.i2.pp1250-1261
 
Raju, S., Nayak, D., & Kh, J. (2022). Topic Modelling on Consumer Financial Protection Bureau Data: An Approach Using BERT Based Embeddings. *2022 IEEE 7th International conference for Convergence in Technology (I2CT)*, 1-6. https://doi.org/10.48550/arxiv.2205.07259
 
Rana, M., Nawaz, A., Ali, T., Alattas, A. S., & Abdelminaam, D. (2024). Sentiment Analysis of Product Reviews Using Transformer Enhanced 1D-CNN and BiLSTM. *Cybernetics and Information Technologies, 24*, 112 - 131. https://doi.org/10.2478/cait-2024-0028
 
Samia, M. M., Rajee, A., Hasan, M. R., Faruq, M., & Paul, P. (2022). Aspect-based Sentiment Analysis for Bengali Text using Bidirectional Encoder Representations from Transformers (BERT). *International Journal of Advanced Computer Science and Applications*. https://doi.org/10.14569/ijacsa.2022.01312112
 
Soetasad, A. A., & Fernando, E. (2025). Comparison of machine learning and deep learning algorithms on sentiment analysis in game reviews. *International Journal of Innovative Research and Scientific Studies*. https://doi.org/10.53894/ijirss.v8i7.10401
 
Tong, X., Willcock, I., & Sun, Y. (2025). Unraveling Player's Insights: A Comparative Analysis of Topic Modeling Techniques on Game Reviews and Video Game Developers' Perspectives. *IEEE Transactions on Games, 17*, 167-180. https://doi.org/10.1109/tg.2024.3411154
 
Yu, Y., Dinh, D.-T., Nguyen, B.-H., Yu, F.-Y., & Huynh, V. (2023). Mining Insights From Esports Game Reviews With an Aspect-Based Sentiment Analysis Framework. *IEEE Access, 11*, 61161-61172. https://doi.org/10.1109/access.2023.3285864
 
Yu, R.-Q., Artemev, D., & Yang, C. (2026). Understanding Customer Ratings in Digital Banking via UGC Reviews: RuBERT-Based Sentiment Classification and BERTopic Topic Modeling. *Proceedings of the 2026 International Conference on Big Data and Informatization Education*. https://doi.org/10.1145/3806980.3807114
 
Zaid, S., Alharbi, A., & Samra, H. E. (2025). Multi-Aspect Sentiment Classification of Arabic Tourism Reviews Using BERT and Classical Machine Learning. *Data, 10*, 168. https://doi.org/10.3390/data10110168
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhu, L., Xu, M.-H., Bao, Y., Xu, Y., & Kong, X.-J. (2022). Deep learning for aspect-based sentiment analysis: a review. *PeerJ Computer Science, 8*. https://doi.org/10.7717/peerj-cs.1044
 
Zhu, Y., & Liu, Y. (2025). Gibbs-BERTopic: A Hybrid Approach for Short Text Topic Modeling. *IEEE Access, 13*, 49162-49173. https://doi.org/10.1109/access.2025.3552221
 
