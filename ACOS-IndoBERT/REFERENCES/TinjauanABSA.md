Tinjauan ABSA Dual Extraction pada Ulasan Game
1. Introduction
Aspect-based sentiment analysis (ABSA) pada ulasan game bertujuan mengekstrak aspek yang dibahas pemain, opini yang menjelaskan aspek itu, dan polaritas sentimennya, sehingga sinyal umpan balik menjadi lebih rinci daripada label positif-negatif tingkat dokumen (Hua et al., 2023; Ahmad et al., 2025; Yuan et al., 2024; Chebolu et al., 2022). Dalam literatur mutakhir, fokus metodologis bergeser dari subtugas terpisah seperti aspect term extraction, opinion term extraction, dan aspect sentiment classification ke tugas gabungan seperti aspect-opinion pair extraction, aspect sentiment triplet extraction (ASTE), dan quadruple extraction untuk mengurangi error propagation dan menangkap keterkaitan antarelemen sentimen (Zhu et al., 2022; Jing et al., 2021; Chakraborty et al., 2025).
Untuk domain game, bukti aplikatif paling langsung masih didominasi kerangka analisis topik plus sentimen pada Steam atau platform sejenis, bukan ekstraksi triplet aspek-opini-sentimen yang tervalidasi khusus pada korpus game (Yu et al., 2023; Li et al., 2021; Tong et al., 2025; Phillips et al., 2021). Studi esports Steam skala besar menunjukkan bahwa ulasan pemain memang kaya aspek desain dan layanan, tetapi evaluasi modelnya masih berupa E2E-ABSA berbasis dataset anotasi baru yang tidak melaporkan pembandingan langsung dengan ASTE khusus game (Yu et al., 2023). Karena itu, pertanyaan kunci literatur ini bukan apakah ABSA berguna untuk ulasan game, melainkan seberapa jauh metode dual extraction dan joint extraction dari literatur umum benar-benar sudah terbukti berpindah ke ulasan game pengguna.
Figure 1: Konsensus riset tentang dual extraction pada ulasan game
2. Methods
Pencarian dijalankan di atas lebih dari 220 juta paper penelitian di Consensus, mencakup Semantic Scholar, PubMed, dan sumber lain. Korpus difokuskan pada tiga irisan: metode ABSA/ASTE dengan joint atau dual extraction, studi domain ulasan game pengguna, dan paper tentang robustnes, generalisasi domain, serta keterbatasan anotasi. Sintesis memprioritaskan paper yang secara langsung menguji ekstraksi aspek-opini-sentimen, lalu menilai apakah bukti itu benar-benar berasal dari domain game atau hanya dapat ditransfer secara konseptual.
Retrieved
Eligible
Included
795.3K
183
100
Figure 2: Alur pencarian dan penyaringan literatur
Strategi memakai kueri paralel untuk game reviews, dual extraction, ASTE, robustness, dan dataset lintas domain.
3. Results
3.1 Key Papers
Literatur inti ditopang oleh satu paper domain game yang sangat relevan dan beberapa paper metodologis ASTE yang mendefinisikan bagaimana joint atau dual extraction dilakukan. Paper esports Steam memberi pijakan aplikasi domain, sedangkan SimSTAR, SBN, PASTE, dan EMC-GCN menambatkan perkembangan arsitektur triplet extraction modern (Yu et al., 2023; Li et al., 2023; Chen et al., 2022; Mukherjee et al., 2021; Chen et al., 2022).
Paper
Summary
(Yu et al., 2023)
ABSA game Steam berskala besar (Yu et al., 2023)
(Li et al., 2023)
Dual extractor independen untuk ASTE (Li et al., 2023)
(Chen et al., 2022)
GCN relasional kuat untuk ASTE (Chen et al., 2022)
Figure 3: Paper kunci pada korpus ini
3.2 Perkembangan Metode
Secara konsisten, paper ASTE menggambarkan kelemahan pipeline dua tahap: kesalahan pada ekstraksi aspek atau opini akan terbawa ke tahap pencocokan atau klasifikasi sentimen (Khodra, 2022; Huan et al., 2022; Li et al., 2023; Chen et al., 2021; Liu et al., 2025). Karena itu, banyak model baru beralih ke joint extraction, span-based decoding, grid tagging, machine reading comprehension, atau generative modeling agar aspek, opini, dan polaritas dipelajari bersama (Zhu et al., 2022; Xia et al., 2024; Li et al., 2024; Liu et al., 2022; Jiang et al., 2026).
Dimension
Pipeline
Joint / Dual
Citations
Kesalahan berantai
Tinggi
Lebih rendah
(Khodra, 2022; Jing et al., 2021)
Pemodelan interaksi
Terbatas
Eksplisit
(Zhu et al., 2022; Jing et al., 2021)
Triplet tumpang tindih
Sulit
Lebih baik
(Yu et al., 2021; Mukherjee et al., 2021)
Multi-word span
Lemah
Fokus utama
(Chen et al., 2022; Liu et al., 2025)
Generalisasi domain
Tetap sulit
Tetap sulit
(Chakraborty et al., 2025; Peng et al., 2024)
Figure 4: Perbandingan pipeline dan joint extraction
Perbedaan terbesarnya adalah bahwa “dual extraction” tidak selalu berarti dua tugas klasik aspek dan sentimen; pada paper baru, istilah itu sering berarti dua encoder, dua arah decoding, atau dua extractor yang dipisah untuk term dan sentiment extraction (Huan et al., 2022; Li et al., 2025; Li et al., 2023; Alqusair et al., 2026).
3.3 Temuan Domain Game
Pada ulasan game, sinyal aspek yang paling sering muncul berulang kali adalah gameplay, graphics, story, community, performa teknis, update, server, cheating, dan monetisasi atau price (Yu et al., 2023; Yuan et al., 2025; Saputra et al., 2025; Batumalay, 2025). Studi esports Steam menemukan bahwa topik yang berkaitan dengan layanan pemain seperti server, ranking, community, teamwork, dan cheating sering menerima sentimen lebih buruk daripada aspek desain inti seperti graphics dan gameplay (Yu et al., 2023).
Literatur game juga cukup konsisten bahwa ulasan negatif cenderung muncul lebih awal dan lebih panjang daripada ulasan positif, sehingga fase pengalaman awal pemain sangat penting untuk deteksi masalah (Yu et al., 2023; Guzsvinecz & Szűcs, 2023; Guzsvinecz & Szűcs, 2026). Namun, sebagian besar studi game masih memakai sentiment classification, topic modeling, atau klasifikasi multi-label aspek, bukan ASTE penuh dengan pasangan aspek-opini yang tervalidasi pada data game (Nalluri et al., 2025; Xing et al., 2025; Setiawan & Yuliansyah, 2024; Zhang & Takada, 2023).
3.4 Keterbatasan dan Robustness
Feature
Result
Fokus robustness
Model ABSA sering rapuh di konteks nyata (Fei et al., 2022)
Sumber masalah
Model, data, dan training sama-sama membatasi (Fei et al., 2022)
Solusi diuji
Data sintetis, adversarial, contrastive (Fei et al., 2022)
Efek utama
Uji robust membaik ~10% dengan data sintetis (Fei et al., 2022)
Relevansi ke game
Slang, sarkasme, dan istilah domain mempersulit klasifikasi (Moattar, 2026; Wang, 2023)
Gangguan domain
Review bombing mengubah pola temporal dan linguistik (Ribeiro, 2026; Cantone et al., 2024)
Figure 5: Sumber utama kelemahan robustness ABSA
Implikasinya, performa ASTE yang tinggi pada benchmark restoran atau laptop belum cukup untuk menjamin kinerja pada ulasan game yang sarat slang, opini implisit, ketidakseimbangan kelas, dan peristiwa anomali seperti review bombing (Jiang et al., 2026; Huynh-Cam et al., 2026; Cai et al., 2021; Ribeiro, 2026).
Results Timeline
Riset ini bergerak dari subtugas terpisah ke triplet extraction dan lalu ke robustness.
Mar 2021
1 paper: (Li et al., 2021)
Jun 2021
1 paper: (Chen et al., 2021)
Oct 2021
2 papers: (Phillips et al., 2021; Mukherjee et al., 2021)
Nov 2021
1 paper: (Jing et al., 2021)
Jan 2022
1 paper: (Chen et al., 2022)
Apr 2022
3 papers: (Chebolu et al., 2022; Chen et al., 2022; Khodra, 2022)
Jul 2022
2 papers: (Zhu et al., 2022; Huan et al., 2022)
Jul 2023
2 papers: (Yu et al., 2023; Li et al., 2023)
Aug 2023
1 paper: (Li et al., 2023)
Nov 2023
1 paper: (Hua et al., 2023)
Apr 2024
1 paper: (Yuan et al., 2024)
Mar 2025
2 papers: (Tong et al., 2025; Liu et al., 2025)
Jul 2025
2 papers: (Ahmad et al., 2025; Chakraborty et al., 2025) Figure 6: Lintasan hasil ASTE; marker besar berarti lebih banyak sitasi
Top Contributors
Type
Name
Papers
Author
Qing He
(Li et al., 2024; Li et al., 2023; Peng & Su, 2024; Jiang et al., 2026)
Author
Tapas Nayak
(Yu et al., 2021; Mukherjee et al., 2021)
Author
Flavius Frasincar
(Truşcǎ & Frasincar, 2022; Brauwers & Frasincar, 2021)
Journal
IEEE Access
(Yu et al., 2023; Huan et al., 2022; Zhao et al., 2021)
Journal
Artificial Intelligence Review
(Hua et al., 2023; Truşcǎ & Frasincar, 2022; Zhang et al., 2024; D'Aniello & Gaeta, 2022)
Journal
IEEE Transactions on Affective Computing
(Yuan et al., 2024)
Figure 7: Penulis dan jurnal paling sering muncul
4. Discussion
Bukti kuat mendukung satu kesimpulan metodologis: joint extraction atau dual-style extraction pada ASTE umumnya lebih masuk akal daripada pipeline murni karena mengurangi error propagation dan lebih baik memodelkan ketergantungan aspek-opini-sentimen (Khodra, 2022; Jing et al., 2021; Li et al., 2023; Chen et al., 2021; Mukherjee et al., 2021). Bukti juga cukup kuat bahwa span-based, graph-based, dan syntax-aware model sekarang mendominasi frontier ASTE karena lebih baik menangani span multi-kata, interaksi relasional, dan dependensi jarak jauh (Chen et al., 2022; Yuan et al., 2024; Shi et al., 2023; Zhang et al., 2025).
Tetapi untuk pertanyaan yang lebih sempit tentang ulasan game, bukti langsung masih terbatas. Paper domain game terbesar memakai LDA ditambah model sentimen BERT-TFM untuk menemukan topik dan polaritas, bukan benchmark ASTE khusus game dengan pembandingan antarmetode dual extraction (Yu et al., 2023). Studi game lain terutama berhenti pada analisis sentimen dokumen, dimensi aspek manual, atau topic modeling, sehingga transfer klaim dari benchmark restoran/laptop ke game masih berupa inferensi, bukan validasi langsung (Yuan et al., 2025; Setiawan & Yuliansyah, 2024; Dehghani & Zaman, 2024; Tong et al., 2025).
Kualitas data menjadi titik lemah utama. Survei dataset menunjukkan korpus ABSA tersebar, domainnya tidak seimbang, dan pergeseran dari sentence-level ke review-level masih menjadi kebutuhan penting (Chebolu et al., 2022). Ini relevan untuk game, karena review pemain sering panjang, tidak baku, multilingual, kadang sarkastik, dan dapat terdistorsi oleh review bombing atau mismatch antara sinyal vote dan isi teks (Yu et al., 2023; Purbolaksono, 2024; Wang, 2023; Ribeiro, 2026).
Literatur juga mulai bergerak ke aspek yang selama ini diabaikan, terutama opini implisit, aspek implisit, transfer domain, dan dokumen panjang. Arah ini penting untuk game karena pemain sering menulis keluhan atau pujian secara tidak langsung, lintas kalimat, atau dipengaruhi konteks komunitas dan budaya platform (Zhang et al., 2024; Cai et al., 2021; Peng et al., 2024; Hu et al., 2024).
Claim
Evidence Strength
Reasoning
Papers
Joint or dual extraction reduces pipeline limitations in ABSA/ASTE
Evidence strength: Strong (8/10)
Banyak paper metodologis sepakat soal error propagation dan keuntungan pemodelan bersama.
(Khodra, 2022; Huan et al., 2022; Jing et al., 2021; Liu et al., 2022)
Syntactic and graph-enhanced ASTE models improve benchmark performance
Evidence strength: Strong (8/10)
Konsisten di banyak benchmark publik, meski hampir semua pada domain non-game.
(Li et al., 2023; Yuan et al., 2024; Shi et al., 2023; Izadi et al., 2026)
Game reviews contain rich aspect signals useful for ABSA
Evidence strength: Moderate (7/10)
Beberapa studi domain game menemukan tema aspek stabil dan actionable.
(Yu et al., 2023; Yuan et al., 2025; Batumalay, 2025; Abdelqader, 2025)
Dual extraction is already proven superior on game-review ASTE
Evidence strength: Weak (2/10)
Hampir tidak ada benchmark ASTE game yang membandingkan model dual extraction secara langsung.
(Yu et al., 2023; Setiawan & Yuliansyah, 2024; Zhang & Takada, 2023)
Robustness and domain transfer remain unresolved in real-world deployment
Evidence strength: Moderate (6/10)
Bukti moderat menunjukkan kelemahan pada context shift, implicitness, dan domain shift.
(Fei et al., 2022; Chakraborty et al., 2025; Jiang et al., 2026; Ribeiro, 2026)
Figure 8: Klaim utama dan kekuatan evidensinya
5. Conclusion
Secara keseluruhan, literatur menunjukkan bahwa ABSA dual extraction dan ASTE telah matang secara metodologis, tetapi validasi langsungnya pada ulasan game pengguna masih tertinggal. Jadi, jawaban singkat untuk topik “ABOSA dual extraction, game, user reviews” adalah: metodenya menjanjikan dan kuat pada benchmark umum, tetapi bukti langsung khusus game masih terbatas dan belum konklusif.
Research Gaps
Kesenjangan utama bukan pada kurangnya model, melainkan pada ketidakselarasan antara frontier metode ASTE dan jenis data game yang benar-benar tersedia. Matriks di bawah memetakan bahwa literatur ini padat pada metode dan cukup padat pada analisis game, tetapi tipis pada titik temu keduanya.
Triplet Labels
Game Domain
Robustness
Long Text
Steam Reviews
No papers
28 papers
3 papers
4 papers
ASTE Models
33 papers
3 papers
7 papers
2 papers
Implicit Sentiment
4 papers
2 papers
No papers
1 paper
Cross-Domain
1 paper
1 paper
2 papers
No papers
Review Bombing
No papers
2 papers
No papers
No papers
Kesenjangan paling menonjol adalah tidak adanya dataset ASTE game berskala besar dengan label triplet eksplisit seperti yang tersedia untuk restoran, laptop, atau otomotif (Usmani et al., 2025; Chebolu et al., 2022). Kesenjangan ini bertahan karena anotasi triplet mahal, opini pemain sering implisit atau lintas kalimat, dan review game terpapar slang, sarkasme, serta gangguan sosial seperti review bombing (Zhang et al., 2024; Hu et al., 2024; Ribeiro, 2026; Wang, 2023). Artinya, bidang ini belum bisa memastikan bahwa kenaikan F1 pada benchmark ASTE umum akan bertahan saat dipindahkan ke ulasan game nyata (Fei et al., 2022; Peng et al., 2024).
Open Research Questions
Arah berikutnya paling masuk akal berfokus pada jembatan antara metode ASTE canggih dan data game realistis.
Question
Why
Dapatkah dataset ASTE khusus ulasan game Steam dengan label triplet eksplisit dan implisit meningkatkan validitas eksternal model dual extraction?
Tanpa benchmark domain game, performa model saat ini sulit diterjemahkan menjadi bukti aplikasi nyata.
Seberapa robust model ASTE terhadap slang, sarkasme, dan review bombing pada ulasan game?
Tiga faktor ini muncul berulang sebagai sumber pergeseran domain dan kegagalan generalisasi.
Apakah model generatif atau weakly supervised dapat mengurangi biaya anotasi untuk ABSA game skala besar?
Biaya anotasi adalah hambatan utama, dan weak supervision mulai menunjukkan generalisasi lintas domain.
Singkatnya, riset tentang ABSA dual extraction untuk ulasan game sudah memiliki fondasi metode yang kuat, tetapi masih membutuhkan dataset, evaluasi, dan uji robustness yang benar-benar khusus pada game.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Abdelqader, H. (2025). Using generative AI to uncover what drives player enjoyment. Multimedia Tools and Applications, 85. https://doi.org/10.1007/s11042-026-21207-8
Ahmad, W., Khan, H. U., Alarfaj, F., & Alreshoodi, M. (2025). Aspect-Based Sentiment Analysis: A Comprehensive Review and Open Research Challenges. IEEE Access, 13, 65138-65182. https://doi.org/10.1109/access.2025.3555744
Alqusair, D., Taileb, M., Sayed, A., & Alotaibi, H. (2026). Integrating syntactic and semantic features for dual-task extraction in Arabic aspect-based sentiment analysis using graph convolutional networks. Information Processing & Management. https://doi.org/10.1016/j.ipm.2026.105183
Batumalay, M. (2025). Harnessing Sentiment Analysis with VADER for Gaming Insights: Analyzing User Reviews of Call of Duty Mobile through Data Mining. International Journal Research on Metaverse. https://doi.org/10.47738/ijrm.v2i2.27
Brauwers, G., & Frasincar, F. (2021). A Survey on Aspect-Based Sentiment Classification. ACM Computing Surveys, 55, 1 - 37. https://doi.org/10.1145/3503044
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
Cantone, G. G., Tomaselli, V., & Mazzeo, V. (2024). Review bombing: ideology-driven polarisation in online ratings: The case study of The Last of Us (part II). Quality & Quantity, 59, 315 - 341. https://doi.org/10.1007/s11135-024-01981-z
Chakraborty, M., Kulkarni, A., & Li, Q. (2025). Weakly Supervised Open-Domain Aspect-Based Sentiment Analysis. ACM Transactions on Knowledge Discovery from Data, 19, 1 - 29. https://doi.org/10.1145/3747849
Chebolu, S. U. S., Dernoncourt, F., Lipka, N., & Solorio, T. (2022). A Review of Datasets for Aspect-based Sentiment Analysis. 611-628. https://doi.org/10.18653/v1/2023.ijcnlp-main.41
Chen, Y., Chen, K., Sun, X., & Zhang, Z. (2022). A Span-level Bidirectional Network for Aspect Sentiment Triplet Extraction. 4300-4309. https://doi.org/10.18653/v1/2022.emnlp-main.289
Chen, H., Zhai, Z., Feng, F., Li, R., & Wang, X. (2022). Enhanced Multi-Channel Graph Convolutional Network for Aspect Sentiment Triplet Extraction. 2974-2985. https://doi.org/10.18653/v1/2022.acl-long.212
Chen, Z.-X., Huang, H., Liu, B., Shi, X.-H., & Jin, H. (2021). Semantic and Syntactic Enhanced Aspect Sentiment Triplet Extraction. 1474-1483. https://doi.org/10.18653/v1/2021.findings-acl.128
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. Artificial Intelligence Review, 55, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
Dehghani, F., & Zaman, L. (2024). Exploring Players' Perspectives: A Comprehensive Topic Modeling Case Study on Elden Ring. Inf., 15, 573. https://doi.org/10.3390/info15090573
Fei, H., Chua, T.-S., Li, C., Ji, D.-H., Zhang, M., & Ren, Y.-F. (2022). On the Robustness of Aspect-based Sentiment Analysis: Rethinking Model, Data, and Training. ACM Transactions on Information Systems, 41, 1 - 32. https://doi.org/10.1145/3564281
Guzsvinecz, T., & Szűcs, J. (2023). Length and sentiment analysis of reviews about top-level video game genres on the steam platform. Comput. Hum. Behav., 149, 107955. https://doi.org/10.1016/j.chb.2023.107955
Guzsvinecz, T., & Szűcs, J. (2026). Emotions in play: A length and sentiment analysis of steam reviews by player engagement mode. Heliyon. https://doi.org/10.1016/j.heliyon.2026.e45258
Hu, X., Zhu, Q., Xiao, Y., & Zhu, W.-T. (2024). Research on the Method and Dataset for Aspect Sentiment Triplet Extraction from Documents. Procedia Computer Science. https://doi.org/10.1016/j.procs.2024.08.137
Hua, Y. C., Denny, P., Wicker, J., & Taškova, K. (2023). A systematic review of aspect-based sentiment analysis: domains, methods, and trends. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-024-10906-z
Huan, H., He, Z., Xie, Y.-Q., & Guo, Z.-L. (2022). A Multi-Task Dual-Encoder Framework for Aspect Sentiment Triplet Extraction. IEEE Access, 10, 103187-103199. https://doi.org/10.1109/access.2022.3210180
Huynh-Cam, T.-T., Chen, L., Huang, H.-J., & Ko, H.-C. (2026). A Hybrid Feature-Weighting and Resampling Model for Imbalanced Sentiment Analysis in User Game Reviews. Mathematics. https://doi.org/10.3390/math14081273
Izadi, A., Shahrokhzadeh, B., & Masoumi, B. (2026). AttGTS: A Lightweight Contrastive-Free Grid-Tagging Model With Scheduled Token-Level Attention for Aspect Sentiment Triplet Extraction. IEEE Access, 14, 114845-114855. https://doi.org/10.1109/access.2026.3713095
Jiang, T., He, Q., Lv, M., & He, Q. (2026). A generative framework for aspect sentiment triplet extraction via implicit reasoning and boundary-aware regularization. Journal of King Saud University Computer and Information Sciences, 38. https://doi.org/10.1007/s44443-026-00888-z
Jing, H., Li, Z.-C., Zhao, H., & Jiang, S. (2021). Seeking Common but Distinguishing Difference, A Joint Aspect-based Sentiment Analysis Model. 3910-3922. https://doi.org/10.18653/v1/2021.emnlp-main.318
Khodra, M. L. (2022). Opinion Triplet Extraction for Aspect-Based Sentiment Analysis Using Co-Extraction Approach. Journal of Information and Communication Technology. https://doi.org/10.32890/jict2022.21.2.5
Li, X., Zhang, Z.-Y., & Stefanidis, K. (2021). A Data-Driven Approach for Video Game Playability Analysis Based on Players' Reviews. Inf., 12, 129. https://doi.org/10.3390/info12030129
Li, D., Yang, Z.-H., Lan, Y., Zhang, Y.-Q., Zhao, H., & Zhao, G. (2023). Simple Approach for Aspect Sentiment Triplet Extraction Using Span-Based Segment Tagging and Dual Extractors. Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. https://doi.org/10.1145/3539618.3592060
Li, Y.-B., He, Q., & Zhang, D.-M. (2023). Dual graph convolutional networks integrating affective knowledge and position information for aspect sentiment triplet extraction. Frontiers in Neurorobotics, 17. https://doi.org/10.3389/fnbot.2023.1193011
Li, Y.-B., He, Q., & Yang, L. (2024). Part-of-speech based label update network for aspect sentiment triplet extraction. Journal of King Saud University Computer and Information Sciences, 36. https://doi.org/10.1016/j.jksuci.2023.101908
Li, X., Zhang, K., & Han, D.-J. (2025). Duality-Driven Aspect Sentiment Triplet Extraction with LLM and Iterative Reinforcement. Symmetry, 17, 642. https://doi.org/10.3390/sym17050642
Liu, G., Zhao, Y., & Shen, B. (2025). A Span-based Enhanced Bidirectional Extraction Framework for Multi-word Aspect Sentiment Triplets. Journal of Internet Technology. https://doi.org/10.70003/160792642025032602005
Liu, S., Li, K.-W., & Li, Z.-H. (2022). A Robustly Optimized BMRC for Aspect Sentiment Triplet Extraction. 272-278. https://doi.org/10.18653/v1/2022.naacl-main.20
Moattar, M. (2026). Lightweight hybrid adaptive weighted ensemble integrating fine-tuned SBERT with lexical and statistical models for robust steam review sentiment classification. Discover Computing, 29. https://doi.org/10.1007/s10791-026-10296-6
Mukherjee, R., Nayak, T., Butala, Y., Bhattacharya, S., & Goyal, P. (2021). PASTE: A Tagging-Free Decoding Framework Using Pointer Networks for Aspect Sentiment Triplet Extraction. 9279-9291. https://doi.org/10.18653/v1/2021.emnlp-main.731
Nalluri, V., Wang, Y.-Y., Jeng, W.-D., & Chen, L.-S. (2025). Extracting Advertising Elements and the Voice of Customers in Online Game Reviews. J. Theor. Appl. Electron. Commer. Res., 20, 321. https://doi.org/10.3390/jtaer20040321
Peng, K., Jiang, L., Li, Q., Li, H., Yu, X., Sun, L., Sun, S., Bi, Y.-X., & Peng, H. (2024). Table-Filling via Mean Teacher for Cross-domain Aspect Sentiment Triplet Extraction. Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. https://doi.org/10.1145/3627673.3679543
Peng, J., & Su, B.-H. (2024). Aspect Sentiment Triplet Extraction Based on Deep Relationship Enhancement Networks. Applied Sciences. https://doi.org/10.3390/app14052221
Phillips, C. J., Klarkowski, M., Frommel, J., Gutwin, C., & Mandryk, R. (2021). Identifying Commercial Games with Therapeutic Potential through a Content Analysis of Steam Reviews. Proceedings of the ACM on Human-Computer Interaction, 5, 1 - 21. https://doi.org/10.1145/3474682
Purbolaksono, M. D. (2024). Sentiment Analysis of Game Review in Steam Platform using Random Forest. International Journal on Information and Communication Technology (IJoICT). https://doi.org/10.21108/ijoict.v10i2.1007
Ribeiro, M. V. G. (2026). Defusing the bomb: a large-scale analysis and machine learning approach to review bombing in video games on Steam. https://doi.org/10.47328/ufvbbt.2026.466
Saputra, A. K., Handayani, M. R., Wibowo, N. C. H., & Umam, K. (2025). Sentiment Analysis of User Reviews on the Game GTA V Using Support Vector Machine. Jurnal Sisfokom (Sistem Informasi dan Komputer). https://doi.org/10.32736/sisfokom.v14i3.2368
Setiawan, H. A., & Yuliansyah, H. (2024). Aspect-Based Sentiment Analysis of User Reviews on the Game “Honkai: Star Rail” Using Naïve Bayes Classifier. SISTEMASI. https://doi.org/10.32520/stmsi.v13i5.4343
Shi, X., Hu, M., Deng, J., Ren, F.-J., Shi, P., & Yang, J.-Y. (2023). Integration of Multi-Branch GCNs Enhancing Aspect Sentiment Triplet Extraction. Applied Sciences. https://doi.org/10.3390/app13074345
Tong, X., Willcock, I., & Sun, Y. (2025). Unraveling Player's Insights: A Comparative Analysis of Topic Modeling Techniques on Game Reviews and Video Game Developers' Perspectives. IEEE Transactions on Games, 17, 167-180. https://doi.org/10.1109/tg.2024.3411154
Truşcǎ, M. M., & Frasincar, F. (2022). Survey on aspect detection for aspect-based sentiment analysis. Artificial Intelligence Review, 56, 3797-3846. https://doi.org/10.1007/s10462-022-10252-y
Usmani, A., Alsamhi, S., Khan, M. J., Breslin, J. G., & Curry, E. (2025). MuSe-CarASTE: A comprehensive dataset for aspect sentiment triplet extraction in automotive review videos. Expert Syst. Appl., 262, 125695. https://doi.org/10.1016/j.eswa.2024.125695
Wang, H.-S. (2023). Sentiment analysis of Chinese game reviews based on SKEP. Advances in Engineering Technology Research. https://doi.org/10.56028/aetr.6.1.507.2023
Xia, T., Sun, X., Yang, Y., Long, Y., & Sutcliffe, R. F. E. (2024). A dual relation-encoder network for aspect sentiment triplet extraction. Neurocomputing. https://doi.org/10.1016/j.neucom.2024.128064
Xing, Y., W., You, Q., & Li, J.-X. (2025). Modeling Affective Mechanisms in Relaxing Video Games: Sentiment and Topic Analysis of User Reviews. Syst., 13, 540. https://doi.org/10.3390/systems13070540
Yu, Y., Dinh, D.-T., Nguyen, B.-H., Yu, F.-Y., & Huynh, V. (2023). Mining Insights From Esports Game Reviews With an Aspect-Based Sentiment Analysis Framework. IEEE Access, 11, 61161-61172. https://doi.org/10.1109/access.2023.3285864
Yu, S., Nayak, T., Majumder, N., & Poria, S. (2021). Aspect Sentiment Triplet Extraction Using Reinforcement Learning. Proceedings of the 30th ACM International Conference on Information & Knowledge Management. https://doi.org/10.1145/3459637.3482058
Yuan, L., Wang, J., Yu, L.-C., & Zhang, X. (2024). Encoding Syntactic Information into Transformers for Aspect-Based Sentiment Triplet Extraction. IEEE Transactions on Affective Computing, 15, 722-735. https://doi.org/10.1109/taffc.2023.3291730
Yuan, L., Ding, M., Meng, F., & Tian, Y. (2025). Sentiment Analysis and Rating Video Game Dimensions via NLP. Applied and Computational Engineering. https://doi.org/10.54254/2755-2721/2024.20540
Zhang, Y., & Takada, S. (2023). Review Classification Based on Machine Learning: Classifying Game User Reviews. IEEE Access, 11, 142447-142463. https://doi.org/10.1109/access.2023.3342294
Zhang, J., Xu, S.-W., Gao, X., & Tang, Z. (2025). Aspect Sentiment Triplet Extraction with Syntax-Semantics Graph Convolutional Network. International Journal of Computational Intelligence Systems, 18. https://doi.org/10.1007/s44196-025-00900-w
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhao, N., Gao, H., Wen, X.-C., & Li, H. (2021). Combination of Convolutional Neural Network and Gated Recurrent Unit for Aspect-Based Sentiment Analysis. IEEE Access, 9, 15561-15569. https://doi.org/10.1109/access.2021.3052937
Zhu, L., Xu, M.-H., Bao, Y., Xu, Y., & Kong, X. (2022). Deep learning for aspect-based sentiment analysis: a review. PeerJ Computer Science, 8. https://doi.org/10.7717/peerj-cs.1044