ACOSE paling kuat dilakukan dengan arsitektur hibrida: ekstraksi terstruktur oleh deep learning/BERT, emosi oleh LLM atau kepala afektif khusus.
Pertanyaannya mencakup tiga hal: bagaimana merancang ACOSE secara teknis, bagaimana membandingkan pipeline machine learning, deep learning, dan LLM, serta kapan masing-masing paradigma paling tepat. Bukti yang tersedia menunjukkan bahwa belum ada standar ACOSE yang mapan, tetapi jalur implementasinya sudah cukup jelas dari gabungan literatur ACOS, dimensional ABSA, dan aspect-level emotion modeling (Cai et al., 2021; Zhang et al., 2024; Chai et al., 2025).
Alur ACOSE
ACOSE paling masuk akal dibangun sebagai tugas ekstraksi terstruktur yang memetakan teks menjadi (aspect, category, opinion, sentiment, emotion) per unit opini, bukan sebagai klasifikasi kalimat tunggal (Cai et al., 2021; Zhang et al., 2022; Zhang et al., 2024). Secara praktik, alurnya adalah: deteksi kandidat aspek-opini, pelabelan kategori, penetapan polaritas sentimen, lalu penetapan emosi per pasangan aspek-kategori, karena literatur menunjukkan ketiga komponen pertama sudah matang di ACOS sedangkan komponen emosi baru mapan di ACSA atau analisis emosi tingkat aspek (Zhang et al., 2022; Chai et al., 2025).
Alur Implementasi ACOSE
flowchart LR; A[Teks Ulasan] --> B[Ekstraksi Aspek Opini]; B --> C[Klasifikasi Kategori]; C --> D[Klasifikasi Sentimen]; D --> E[Prediksi Emosi]; E --> F[Validasi Struktur]; F --> G[Kuintuplet ACOSE]
Figure 1: Alur teknis pembentukan kuintuplet ACOSE
Jika ingin emosi diskret, pendekatan terdekat adalah menambahkan label emosi kategori-spesifik seperti enam emosi dasar Ekman ke keluaran sentimen aspek (Chai et al., 2025). Jika ingin emosi berdimensi, pendekatan terdekat adalah mengganti atau melengkapi polaritas dengan intensitas valensi-arousal kontinu, lalu mengaitkannya ke tuple aspek-kategori-opini (Zhang et al., 2024; Chai et al., 2025).
Pipeline Machine Learning
Pipeline machine learning (ML) adalah opsi paling mudah dijelaskan dan diimplementasikan, tetapi paling rapuh untuk ACOSE. Paradigma ini memecah tugas menjadi modul berurutan, misalnya ekstraksi aspek, ekstraksi opini, klasifikasi kategori, lalu klasifikasi sentimen, dengan prediksi tahap awal menjadi masukan tahap berikutnya (Zhang et al., 2022; Akhtar et al., 2017). Di ACOS, bentuk ini tampak pada Extract-Classify-ACOS, yang lebih dulu mengekstrak pasangan aspek-opini lalu memprediksi kategori-sentimen dari pasangan itu (Cai et al., 2021).
Kekuatan
Kelemahan
Bentuk ACOSE yang realistis
Mudah diaudit dan modular (Zhang et al., 2022; Brauwers & Frasincar, 2021)
Rawan error propagation (Zhang et al., 2022; Li et al., 2023)
A→O→C/S→E
Cocok untuk data kecil dan fitur manual (Akhtar et al., 2017)
Sulit menangkap ketergantungan lintas-elemen (Zhang et al., 2022; Zhang et al., 2024)
Emosi diprediksi di tahap akhir
Interpretabilitas lebih baik dari model besar (Brauwers & Frasincar, 2021)
Kinerja turun pada tugas majemuk kompleks (Zhang et al., 2022; Zhang et al., 2024)
Baik untuk baseline
Figure 2: Trade-off utama pipeline machine learning untuk ACOSE
Kelemahan utamanya konsisten: kesalahan awal akan merusak semua tahap hilir (Zhang et al., 2022; Xu et al., 2026). Masalah itu membesar pada komponen implisit, karena ACOS sendiri sudah menuntut penanganan aspek dan opini yang tidak selalu hadir sebagai span eksplisit (Cai et al., 2021; Xiong et al., 2023; Zhu et al., 2023).
Meski begitu, ML klasik masih berguna sebagai baseline atau sistem data-kecil. Pendekatan berantai berbasis CRF, SVM, Maximum Entropy, dan rekayasa fitur tetap efektif untuk ekstraksi aspek dan klasifikasi sentimen dua-tahap pada domain terbatas (Akhtar et al., 2017). Untuk ACOSE, bentuk realistisnya adalah pipeline lima langkah dengan kepala emosi terpisah di tahap akhir, tetapi bukti saat ini menunjukkan itu akan tertinggal dari pendekatan terpadu.
Deep Learning
Deep learning adalah jalur paling aman bila targetnya ACOSE yang stabil, terukur, dan dapat dilatih supervised. Literatur ABSA luas menunjukkan bahwa model dalam keluarga CNN, RNN, LSTM, BiLSTM, dan terutama Transformer dapat belajar fitur sintaktik-semantik tanpa rekayasa fitur manual tingkat tinggi (Chauhan et al., 2023; H. et al., 2019; Brauwers & Frasincar, 2021). Literatur juga bergerak dari komponen tunggal ke model ujung-ke-ujung (end-to-end) yang jointly mempelajari deteksi dan klasifikasi (Truşcǎ & Frasincar, 2022; Brauwers & Frasincar, 2021).
Dalam ACOS, varian deep learning terbaik umumnya mengurangi pipeline error dengan pemodelan terpadu. BART-CRN memperlakukan ACOS sebagai tugas generasi sekuens ujung-ke-ujung untuk mengatasi error propagation dan keberagaman tipe kuadrupel (Xiong et al., 2023). SG-ACOS juga memakai generasi sekuens, tetapi memendekkan target dengan token khusus agar lebih efisien ketika jumlah kuadrupel bertambah (Li et al., 2023). iACOS menambahkan token implisit dan multi-task learning untuk mengekstrak aspek/opini implisit sekaligus memprediksi kategori-sentimen (Xu et al., 2023).
Pendekatan DL
Ide inti
Relevansi untuk ACOSE
BERT/CRF dua-tahap
Ekstraksi lalu linking (Zhang et al., 2022)
Dasar kuat untuk ACOSE supervisi
End-to-end generatif
Keluarkan tuple langsung (Xiong et al., 2023; Hoang et al., 2022)
Paling dekat ke kuintuplet
Multi-task implisit
Belajar aspek/opini implisit bersama (Xu et al., 2023)
Penting untuk emosi implisit
Sintaks/graf
Tambahkan dependensi kata (Zhang et al., 2023; Huang et al., 2022)
Membantu linking opini-emosi
Figure 3: Keluarga deep learning yang relevan untuk ACOSE
Untuk ACOSE, ekstensi paling masuk akal adalah model shared encoder dengan beberapa kepala keluaran: satu untuk span aspek-opini, satu untuk kategori, satu untuk sentimen, dan satu untuk emosi. Pola ini konsisten dengan multi-task learning yang sudah dipakai untuk ABSA dan pengayaan afektif (Truşcǎ & Frasincar, 2022; He et al., 2023; Chai et al., 2025). Jika data sedikit, teacher-student atau self-training juga relevan: MSM menunjukkan 50% data berlabel masih bisa mendekati SOTA, dan kerangka pseudo-label lintas domain meningkatkan ketahanan model (He et al., 2023; Ouyang & Shen, 2023).
Pada bahasa Indonesia, jalur ini juga paling terbukti. Fine-tuning mBERT dan IndoBERT meningkatkan ABSA dibanding pendekatan non-transfer, dan IndoBERT domain-spesifik mencapai performa kuat untuk deteksi aspek dan klasifikasi sentimen pada pariwisata serta umpan balik mahasiswa (Azhar & Khodra, 2020; Perwira et al., 2025; Jazuli et al., 2024). Untuk komponen emosi, IndoBERT hibrida juga sudah bekerja cukup baik pada klasifikasi emosi bahasa Indonesia, sehingga kepala emosi ACOSE dapat dibangun di atas encoder yang sama (Ahmadian et al., 2023; Ahmadian et al., 2024; Shaw et al., 2025).
LLM Generatif
LLM paling menarik untuk ACOSE karena dapat mengubah tugas menjadi pembangkitan teks terstruktur ujung-ke-ujung. Dalam dimensional ABSA, metode berbasis LLM tidak memecah ekstraksi kuadrupel ke subtugas, tetapi langsung memperlakukan masalah sebagai pembangkitan teks (Zhang et al., 2024). Pola serupa muncul pada ACOS generatif berbasis T5, BART, dan instruction tuning (Hoang et al., 2022; Xiong et al., 2023; Van Dang et al., 2024).
Bukti mendukung ya terhadap pipeline klasik, tetapi tidak terhadap semua model terspesialisasi. LLM dan model generatif umumnya mengungguli pipeline modular, namun sering masih tertinggal dari model generatif tersetel halus atau sistem hibrida terbaik (Xu et al., 2023; Bai et al., 2024). Figure 4: Consensus on LLM gains over pipeline ABSA
Kekuatan LLM ada pada instruction following, few-shot adaptation, dan fleksibilitas lintas domain atau bahasa (Simmering & Huoviala, 2023; Wuisang & Pangestu, 2025). Fine-tuned GPT-3.5 bahkan mencapai F1 83.8 pada tugas ABSA gabungan aspek-polaritas, tetapi dengan biaya inferensi jauh lebih tinggi (Simmering & Huoviala, 2023). Dalam pengaturan sumber daya terbatas, QLoRA memungkinkan penyetelan LLM untuk dimensional ABSA tanpa kebutuhan pelatihan penuh (Zhang et al., 2024).
Namun, literatur juga jelas bahwa LLM mentah belum cukup. ChatGPT mengalahkan beberapa model pipeline, tetapi kalah dari model T5 generatif yang dilatih penuh pada data tugas (Xu et al., 2023). Evaluasi lintas tugas majemuk juga menunjukkan LLM unggul atas metode few-shot supervised lain, tetapi dalam banyak kasus masih di bawah SOTA tersupervisi penuh (Bai et al., 2024). Pada ABSA halus, beberapa studi bahkan menegaskan bahwa pemakaian langsung LLM bukan pilihan optimal karena halusinasi dan reliabilitas struktur keluaran (Zhong et al., 2024; Peper & Wang, 2022).
Desain Rekomendasi
Skenario
Pilihan terbaik
Alasan utama
Data kecil, butuh baseline transparan
Pipeline ML
Murah, mudah audit (Zhang et al., 2022; Brauwers & Frasincar, 2021)
Data berlabel cukup, target stabil
Deep learning multi-task
Paling seimbang akurasi dan kontrol (Truşcǎ & Frasincar, 2022; Xu et al., 2023)
Domain baru, bahasa rendah-sumber
LLM atau hibrida
Adaptif dan cepat dipindah (Wuisang & Pangestu, 2025; Šmíd et al., 2025)
Emosi berdimensi + tuple terstruktur
Hibrida BERT+LLM
Bukti terbaik saat ini (Zhang et al., 2024)
Produksi biaya rendah
Student distilled
Lebih murah dari teacher LLM (Haralović et al., 2026)
Figure 5: Pilihan paradigma menurut kondisi implementasi ACOSE
Rekomendasi teknis paling kuat saat ini adalah hibrida. Pada dimensional ABSA, strategi pipeline ensemble yang memakai BERT untuk tuple dan LLM untuk intensitas memberi hasil terbaik di antara strategi ensembel (Zhang et al., 2024). Studi pariwisata juga menunjukkan penambahan pengetahuan dari LLM ke model multitugas dapat meningkatkan F1, terutama pada data implisit (Xu et al., 2025). Bahkan pada generasi terbaru, integrasi sintaks langkah-demi-langkah ke LLM meningkatkan kinerja prediksi kuadrupel dibanding basis generatif murni (Chen et al., 2026).
Untuk ACOSE, bentuk hibrida yang paling defensibel adalah: encoder BERT/IndoBERT untuk ekstraksi span dan relasi, kepala kategori-sentimen terawasi, lalu modul emosi berbasis LLM atau kepala afektif khusus yang divalidasi dengan ruang VAD (Azhar & Khodra, 2020; Chai et al., 2025). Jika anotasi emosi belum tersedia, LLM lebih berguna sebagai pembuat pseudo-label atau pengetahuan bantu daripada sebagai prediktor final tunggal (He et al., 2023; Zhong et al., 2024; Šmíd et al., 2025).
Implikasi Praktis
Secara praktis, ACOSE tidak sebaiknya dimulai dari ML klasik kecuali sebagai baseline. Bukti paling konsisten mendukung pergeseran dari pipeline modular menuju model terpadu, lalu menuju sistem hibrida yang memakai kekuatan ekstraksi encoder kecil dan fleksibilitas generatif LLM (Zhang et al., 2022; Xiong et al., 2023; Zhang et al., 2024).
Untuk Bahasa Indonesia, kombinasi yang paling menjanjikan adalah IndoBERT sebagai tulang punggung ekstraksi aspek-opini-sentimen dan modul emosi terpisah, karena kinerja IndoBERT pada ABSA dan klasifikasi emosi sudah kuat, sementara bukti LLM Indonesia lebih menonjol pada kecepatan adaptasi daripada efisiensi biaya jangka panjang (Perwira et al., 2025; Jazuli et al., 2024; Ahmadian et al., 2024; Wuisang & Pangestu, 2025).
Perubahan terpenting yang ditunjukkan literatur adalah pergeseran dari ekstraksi polaritas empat elemen ke representasi afektif yang lebih kaya dan lebih generatif (Chai et al., 2025). Pertanyaan terbuka terbesarnya adalah belum adanya korpus ACOSE standar yang sekaligus memberi anotasi aspek, opini, kategori, sentimen, dan emosi sehingga perbandingan antarparadigma masih harus disusun dari tugas-tugas yang berdekatan.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2023). Transformer-Based Indonesian Language Model for Emotion Classification and Sentiment Analysis. 2023 International Conference on Information Technology and Computing (ICITCOM), 209-214. https://doi.org/10.1109/icitcom60176.2023.10442970
Ahmadian, H., Abidin, T., Riza, H., & Muchtar, K. (2024). Hybrid Models for Emotion Classification and Sentiment Analysis in Indonesian Language. Appl. Comput. Intell. Soft Comput., 2024. https://doi.org/10.1155/2024/2826773
Akhtar, M. S., Gupta, D., Ekbal, A., & Bhattacharyya, P. (2017). Feature selection and ensemble construction: A two-step method for aspect based sentiment analysis. Knowl. Based Syst., 125, 116-135. https://doi.org/10.1016/j.knosys.2017.03.020
Azhar, A. N., & Khodra, M. L. (2020). Fine-tuning Pretrained Multilingual BERT Model for Indonesian Aspect-based Sentiment Analysis. 2020 7th International Conference on Advance Informatics: Concepts, Theory and Applications (ICAICTA), 1-6. https://doi.org/10.1109/icaicta49861.2020.9428882
Bai, Y.-H., Han, Z., Zhao, Y., Gao, H., Zhang, Z.-W., Wang, X.-Z., & Hu, M. (2024). Is Compound Aspect-Based Sentiment Analysis Addressed by LLMs?. 7836-7861. https://doi.org/10.18653/v1/2024.findings-emnlp.460
Brauwers, G., & Frasincar, F. (2021). A Survey on Aspect-Based Sentiment Classification. ACM Computing Surveys, 55, 1 - 37. https://doi.org/10.1145/3503044
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. ArXiv, abs/2511.19122. https://doi.org/10.48550/arxiv.2511.19122
Chauhan, G., Nahta, R., Meena, Y., & Gopalani, D. (2023). Aspect based sentiment analysis using deep learning approaches: A survey. Comput. Sci. Rev., 49, 100576. https://doi.org/10.1016/j.cosrev.2023.100576
Chen, B., Qiu, C.-J., Xie, Y., Xu, B., Cai, R.-C., & Hao, Z.-F. (2026). 𝒮2IT: Stepwise Syntax Integration Tuning for Large Language Models in Aspect Sentiment Quad Prediction. ArXiv, abs/2604.23296. https://doi.org/10.18653/v1/2025.findings-naacl.379
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. Expert Syst. Appl., 118, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
Haralović, M., Akça, O., Yücetürk, S. E., Li, M.-S., & Theune, M. (2026). CrisisKD: Five-Stage Knowledge Distillation for Aspect-Level Sentiment and Emotion Analysis in Crisis Discourse. https://doi.org/10.48550/arxiv.2609.05757
He, K., Mao, R., Gong, T., Li, C., & Cambria, E. (2023). Meta-Based Self-Training and Re-Weighting for Aspect-Based Sentiment Analysis. IEEE Transactions on Affective Computing, 14, 1731-1742. https://doi.org/10.1109/taffc.2022.3202831
Hoang, C. D., Dinh, Q. V., & Tran, N. H. (2022). Aspect-Category-Opinion-Sentiment Extraction Using Generative Transformer Model. 2022 RIVF International Conference on Computing and Communication Technologies (RIVF), 1-6. https://doi.org/10.1109/rivf55975.2022.10013820
Huang, B., Zhang, J., Ju, J., Guo, R., Fujita, H., & Liu, J. (2022). CRF-GCN: An effective syntactic dependency model for aspect-level sentiment analysis. Knowl. Based Syst., 260, 110125. https://doi.org/10.1016/j.knosys.2022.110125
Jazuli, A., W., & Kusumaningrum, R. (2024). Optimizing Aspect-Based Sentiment Analysis Using BERT for Comprehensive Analysis of Indonesian Student Feedback. Applied Sciences. https://doi.org/10.3390/app15010172
Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. 2023 International Joint Conference on Neural Networks (IJCNN), 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191098
Ouyang, F., & Shen, B. (2023). A mutual mean teacher framework for cross-domain aspect-based sentiment analysis. The Journal of Supercomputing, 80, 9073 - 9095. https://doi.org/10.1007/s11227-023-05792-1
Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. ArXiv, abs/2211.07743. https://doi.org/10.48550/arxiv.2211.07743
Perwira, R., Permadi, V. A., Purnamasari, D., & Agusdin, R. P. (2025). Domain-Specific Fine-Tuning of IndoBERT for Aspect-Based Sentiment Analysis in Indonesian Travel User-Generated Content. Journal of Information Systems Engineering and Business Intelligence. https://doi.org/10.20473/jisebi.11.1.30-40
Shaw, C., LaCasse, P. M., & Champagne, L. E. (2025). Exploring emotion classification of indonesian tweets using large scale transfer learning via IndoBERT. Social Network Analysis and Mining, 15. https://doi.org/10.1007/s13278-025-01439-6
Simmering, P. F., & Huoviala, P. (2023). Large language models for aspect-based sentiment analysis. ArXiv, abs/2310.18025. https://doi.org/10.48550/arxiv.2310.18025
Šmíd, J., Přibáň, P., & Král, P. (2025). LACA: Improving Cross-lingual Aspect-Based Sentiment Analysis with LLM Data Augmentation. 839-853. https://doi.org/10.18653/v1/2025.acl-long.41
Truşcǎ, M. M., & Frasincar, F. (2022). Survey on aspect detection for aspect-based sentiment analysis. Artificial Intelligence Review, 56, 3797-3846. https://doi.org/10.1007/s10462-022-10252-y
Van Dang, T., Duong, H., & Nguyen, N. (2024). Vi-AbSQA: Multi-task Prompt Instruction Tuning Model for Vietnamese Aspect-based Sentiment Quadruple Analysis. ACM Transactions on Asian and Low-Resource Language Information Processing. https://doi.org/10.1145/3676886
Wuisang, M. C., & Pangestu, G. (2025). Aspect-Based Sentiment Analysis in Indonesian Hotel Reviews: Machine Learning versus Large Language Models. 2025 International Seminar on Application for Technology of Information and Communication (iSemantic), 444-449. https://doi.org/10.1109/isemantic67418.2025.11292470
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. International Journal of Machine Learning and Cybernetics, 14, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
Xu, C., Wang, M., Ren, Y., & Zhu, S. (2026). Enhancing Aspect-Based Sentiment Analysis in Tourism Using Large Language Models and Positional Information. Tsinghua Science and Technology. https://doi.org/10.26599/tst.2024.9010138
Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. ArXiv, abs/2311.03896. https://doi.org/10.48550/arxiv.2311.03896
Xu, X., Zhang, J.-D., Xiao, R., & Xiong, L. (2023). The Limits of ChatGPT in Extracting Aspect-Category-Opinion-Sentiment Quadruples: A Comparative Analysis. ArXiv, abs/2310.06502. https://doi.org/10.48550/arxiv.2310.06502
Xu, C., Wang, M., & Zhu, S. (2025). Tourism sentiment quadruple extraction via new neural ordinary differential equation networks with multitask learning and implicit sentiment enhancement. Expert Syst. Appl., 270, 126417. https://doi.org/10.1016/j.eswa.2025.126417
Zhang, Y., Xu, H., Zhang, D., & Xu, R.-F. (2024). A Hybrid Approach to Dimensional Aspect-Based Sentiment Analysis Using BERT and Large Language Models. Electronics. https://doi.org/10.3390/electronics13183724
Zhang, H., Chen, Z., Chen, B., Hu, B., Li, M., Yang, C., & Jiang, B. (2022). Complete quadruple extraction using a two-stage neural model for aspect-based sentiment analysis. Neurocomputing, 492, 452-463. https://doi.org/10.1016/j.neucom.2022.04.027
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. IEEE Transactions on Knowledge and Data Engineering, 35, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
Zhang, X., Xu, J., Cai, Y., Tan, X., & Zhu, C. (2023). Detecting Dependency-Related Sentiment Features for Aspect-Level Sentiment Classification. IEEE Transactions on Affective Computing, 14, 196-210. https://doi.org/10.1109/taffc.2021.3063259
Zhong, Q.-H., Li, H., Zhuang, L.-Y., Liu, J.-H., & Du, B. (2024). Iterative Data Generation with Large Language Models for Aspect-based Sentiment Analysis. https://doi.org/10.48550/arxiv.2407.00341
Zhu, L., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. World Wide Web, 26, 3303 - 3320. https://doi.org/10.1007/s11280-023-01185-9