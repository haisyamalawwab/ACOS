Implementasi ACOSE membandingkan tiga paradigma komputasi utama.
Implementasi Aspect-Category-Opinion-Sentiment-Emotion (ACOSE) berfokus pada tiga aspek utama: alur proses pipeline machine learning konvensional, model gabungan deep learning, serta kerangka generatif Large Language Models (LLM) (Zhang et al., 2022; Liu et al., 2020; Takallou et al., 2026).
Alur Implementasi ACOSE Lintas Paradigma
flowchart LR; A[Teks Mentah] --> B[Pipeline ML Tradisional]; A --> C[Deep Learning Bersama]; A --> D[LLM Generatif]; B --> E[Ekstraksi Bertingkat]; C --> F[Multi-Task Representation]; D --> G[Pembangkitan Kuintuplet Teks]
Figure 1: Komparasi alur kerja ekstraksi ACOSE menggunakan arsitektur ML, DL, dan LLM.
Pipeline Machine Learning Tradisional
Pendekatan machine learning (ML) tradisional memecah ACOSE ke dalam subtugas terpisah yang dieksekusi berurutan menggunakan rekayasa fitur manual (Zhang et al., 2022; H. et al., 2019; Hemmatian & Sohrabi, 2017).
Metode pipeline menghubungkan modul ekstraksi entitas dan klasifikasi secara modular dengan memanfaatkan algoritma seperti pohon keputusan atau SVM linier (Zhang et al., 2022; Brauwers & Frasincar, 2021).
Kinerja sistem sangat bergantung pada operasi pra-pemrosesan data seperti penyandian dan rekayasa fitur manual (Gregori et al., 2025).
Kelemahan mendasar model bertingkat ini adalah kerentanan terhadap akumulasi perambatan galat (error propagation) dari langkah awal ke langkah hilir (Zhang et al., 2022; Xu et al., 2026).
Representasi Terpadu Deep Learning
Arsitektur deep learning (DL) mengatasi pemisahan fitur dengan menangkap representasi semantik dan sintaksis tingkat tinggi secara otomatis (Chauhan et al., 2023; H. et al., 2019; Brauwers & Frasincar, 2021).
Model sekuensial seperti CNN, LSTM, dan Transformer memungkinkan ekstraksi elemen sentimen secara terpadu (end-to-end) (Truşcǎ & Frasincar, 2022; Ray & Chakrabarti, 2020; Brauwers & Frasincar, 2021).
Mekanisme atensi bersama (co-attention) menghubungkan deteksi aspek implisit dengan polaritas sentimen dalam representasi laten gabungan (Truşcǎ & Frasincar, 2022; Brauwers & Frasincar, 2021).
Kebutuhan data latih berskala besar serta sumber daya komputasi tinggi menjadi kendala utama pelatihannya dari awal (Brauwers & Frasincar, 2021).
Generasi Kuintuplet Menggunakan LLM
Model bahasa besar (LLM) mereformulasi ekstraksi elemen menjadi tugas pembangkitan teks bebas (sequence-to-sequence) yang terpadu (Zhang et al., 2024; Mughal et al., 2024; Jurado, 2024).
Penggunaan prompting dan dekomposisi kalimat memungkinkan instruksi LLM memetakan kuintuplet afektif secara simultan (Said et al., 2025; Zhang et al., 2024; Mughal et al., 2024).
Teknik parameter-efficient fine-tuning seperti QLoRA atau Adalora memfasilitasi adaptasi domain efisien di bawah keterbatasan perangkat keras (Zhang et al., 2024; Xu et al., 2026; Fang et al., 2024).
Arsitektur hibrida yang menggabungkan representasi encoder BERT dengan inferensi generatif LLM terbukti menghasilkan performa paling optimal (Said et al., 2025; Zhang et al., 2024).
Secara komparatif, evolusi metodologi bergerak dari modularitas pipeline ML menuju penalaran konteks holistik berbasis LLM generatif terpandu (Zhang et al., 2022; Gu et al., 2024).
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Brauwers, G., & Frasincar, F. (2021). A Survey on Aspect-Based Sentiment Classification. ACM Computing Surveys, 55, 1 - 37. https://doi.org/10.1145/3503044
Chauhan, G., Nahta, R., Meena, Y., & Gopalani, D. (2023). Aspect based sentiment analysis using deep learning approaches: A survey. Comput. Sci. Rev., 49, 100576. https://doi.org/10.1016/j.cosrev.2023.100576
Fang, Z.-H., Lin, Z., Chen, Z., Chen, X.-H., Gao, Y., & Fang, Y.-G. (2024). Automated Federated Pipeline for Parameter-Efficient Fine-Tuning of Large Language Models. IEEE Transactions on Mobile Computing, 25, 8782-8797. https://doi.org/10.1109/tmc.2025.3649881
Gregori, L., Lazzaro, P., Lazzaro, M., Missier, P., & Torlone, R. (2025). An LLM-guided platform for multi-granular collection and management of data provenance. Journal of Big Data, 12. https://doi.org/10.1186/s40537-025-01209-3
Gu, Y., You, H.-Y., Cao, J., Yu, M.-R., Fan, H.-R., & Qian, S.-Y. (2024). Large Language Models for Constructing and Optimizing Machine Learning Workflows: A Survey. ArXiv, abs/2411.10478. https://doi.org/10.48550/arxiv.2411.10478
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. Expert Syst. Appl., 118, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
Hemmatian, F., & Sohrabi, M. (2017). A survey on classification techniques for opinion mining and sentiment analysis. Artificial Intelligence Review, 52, 1495 - 1545. https://doi.org/10.1007/s10462-017-9599-6
Jurado, I. C. (2024). LLM Prompting Strategies in Automated Machine Learning. 2024 IEEE International Conference on Machine Learning and Applied Network Technologies (ICMLANT), 74-79. https://doi.org/10.1109/icmlant63295.2024.00018
Liu, H., Chatterjee, I., Zhou, M., Lu, X., & Abusorrah, A. (2020). Aspect-Based Sentiment Analysis: A Survey of Deep Learning Methods. IEEE Transactions on Computational Social Systems, 7, 1358-1375. https://doi.org/10.1109/tcss.2020.3033302
Mughal, N., Mujtaba, G., Shaikh, S., Kumar, A., & Daudpota, S. (2024). Comparative Analysis of Deep Natural Networks and Large Language Models for Aspect-Based Sentiment Analysis. IEEE Access, 12, 60943-60959. https://doi.org/10.1109/access.2024.3386969
Ray, P., & Chakrabarti, A. (2020). A Mixed approach of Deep Learning method and Rule-Based method to improve Aspect Level Sentiment Analysis. Applied Computing and Informatics. https://doi.org/10.1016/j.aci.2019.02.002
Said, M., Smairi, N., & Abadlia, H. (2025). LLM Powered DeepSeek and BiLSTM Pipeline Used in Aspect Based Sentiment Analysis. 2025 IEEE 37th International Conference on Tools with Artificial Intelligence (ICTAI), 813-817. https://doi.org/10.1109/ictai66417.2025.00118
Takallou, M. A., Gautam, A., & Shirolkar, P. (2026). LLMs for End-to-End Machine Learning: A Comprehensive Review. IEEE Access, 14, 47717-47738. https://doi.org/10.1109/access.2026.3678429
Truşcǎ, M. M., & Frasincar, F. (2022). Survey on aspect detection for aspect-based sentiment analysis. Artificial Intelligence Review, 56, 3797-3846. https://doi.org/10.1007/s10462-022-10252-y
Xu, C., Wang, M., Ren, Y., & Zhu, S. (2026). Enhancing Aspect-Based Sentiment Analysis in Tourism Using Large Language Models and Positional Information. Tsinghua Science and Technology. https://doi.org/10.26599/tst.2024.9010138
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. IEEE Transactions on Knowledge and Data Engineering, 35, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
Zhang, Y., Xu, H., Zhang, D., & Xu, R.-F. (2024). A Hybrid Approach to Dimensional Aspect-Based Sentiment Analysis Using BERT and Large Language Models. Electronics. https://doi.org/10.3390/electronics13183724