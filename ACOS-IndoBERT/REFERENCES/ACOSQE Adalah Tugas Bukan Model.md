ACOSQE adalah tugas, bukan arsitektur model pembanding
Tinjauan literatur menunjukkan bahwa pertanyaan ini didasarkan pada perbandingan kategori yang keliru: ACOSQE adalah formulasi tugas, sedangkan model generatif merupakan salah satu keluarga metode untuk menyelesaikannya. Figure 1: Konsensus literatur mengenai kategorisasi tugas ACOSQE vs pendekatan generatif
ACOSQE (Aspect-Category-Opinion-Sentiment Quadruple Extraction) merujuk pada tugas mendeteksi target aspek, kategori aspek, istilah opini, dan polaritas sentimen sekaligus, khususnya ketika aspek atau opini tidak tertulis secara eksplisit (Li et al., 2023; Cai et al., 2021; Zhang et al., 2024). Oleh karena itu, ACOSQE tidak bersaing melawan model generatif; model generatif justru menjadi salah satu paradigma utama yang paling banyak digunakan untuk menyelesaikan ACOSQE (Li et al., 2023; Xiong et al., 2023; Peper & Wang, 2022).
Paradigma Model
Penelitian ACOSQE umumnya membandingkan metode generatif berbasis sequence-to-sequence dengan metode non-generatif seperti pipeline klasifikasi atau penandaan kisi (grid tagging) (Li et al., 2023; Peper & Wang, 2022; Zhu et al., 2023). Pendekatan non-generatif bertahap sering mengalami perambatan galat (error propagation) antartahap (Li et al., 2023; Xu et al., 2026; Xiong et al., 2023). Sebaliknya, model generatif menyelesaikan ekstraksi kuadruplet secara terpadu (end-to-end), memanfaatkan semantik label bahasa alami secara fleksibel (Li et al., 2023; Nie et al., 2024; Hoang et al., 2022).
Model generatif modern sering mengungguli metode ekstraksi diskriminatif tradisional pada tolak ukur ACOS (Li et al., 2023; Xiong et al., 2023; Lei et al., 2024). Pengecualian terjadi pada arsitektur non-generatif khusus yang dirancang dengan dekomposisi pemahaman bacaan mesin (machine reading comprehension atau MRC) atau grid tagging, yang dapat menandingi atau melampaui beberapa varian generatif standar (Zhu et al., 2023; Zhang et al., 2024).
Fig 1. An example of the aspectcategory-opinion-sentiment quadruple extraction task with implicit aspects and opinions (Zhang et al., 2024)
How to read: Diagram ini mengilustrasikan contoh kalimat ulasan yang memuat elemen aspek dan opini implisit beserta keterhubungannya dalam struktur kuadruplet ACOSQE.
Tantangan Opini Implisit
Opini implisit (implicit opinion) menjadi bagian paling menantang dalam dataset ACOSQE karena tidak memiliki rentang kata nyata di dalam teks (Cai et al., 2021; Peper & Wang, 2022; Wang et al., 2024). Pada dataset ACOS standar, elemen implisit dipetakan ke token penanda khusus seperti NULL (Cai et al., 2021; Xu et al., 2023). Kalimat dengan opini implisit kerap mencatat skor performa terendah dibandingkan kalimat yang seluruh elemennya tersurat (Cai et al., 2021; Peper & Wang, 2022).
Untuk mengatasi kelemahan model generatif dasar dalam menangani kasus implisit, berbagai teknik augmentasi representasi telah dikembangkan (Peper & Wang, 2022; Wang et al., 2024; Lei et al., 2024). Penambahan supervised contrastive learning (SCL) mendorong representasi terpisah antara kalimat eksplisit dan implisit (Peper & Wang, 2022; Lei et al., 2024). Model generatif non-autoregresif dengan variabel laten juga dikembangkan untuk mengoptimalkan penangkapan struktur emosi laten tanpa penurunan efisiensi (Nie et al., 2024).
Perbandingan Arsitektur
Model
Paradigma
Penanganan Implisit
Peningkatan Utama
Citations
Extract-Classify
Pipeline Non-generatif
Token khusus klasifikasi
Baseline terstruktur awal
(Cai et al., 2021; Peper & Wang, 2022)
SG-ACOS
Generatif T5
Khusus token peringkas
Linearisasi target pendek
(Li et al., 2023)
GEN-SCL-NAT
Generatif autoregresif
Contrastive learning
Target berurutan kausal
(Peper & Wang, 2022)
DPML
Generatif terpandu prompt
Pembelajaran timbal-balik
Interaksi dual-template
(Lei et al., 2024)
MRC-CLRI
Non-generatif multi-tugas
Dekomposisi relasi query
Inferensi dua arah teroptimasi
(Zhang et al., 2024)
Figure 2: Perbandingan model penyelesai tugas ACOSQE pada ulasan implisit
Table 1. Dataset statistics. Over 33% of REST quadruples contain implicit language, as do 43% in LAPTOP*. E: explicit, I: implicit, A: aspect, O: opinion. E.g., IAEO refers to 'implicit aspect, explicit opinion'. (Peper & Wang, 2022)
How to read: Tabel ini merangkum statistik subset data ulasan restoran dan laptop, mengelompokkan proporsi kuadruplet berdasarkan aspek dan opini eksplisit versus implisit.
Arah Perkembangan Ekstraksi
Berbagai model generatif menunjukkan keunggulan konsisten dibanding metode pipeline klasik pada subset implisit (Li et al., 2023; Lei et al., 2024; Wang et al., 2023).
Penggunaan contoh negatif adaptif (adaptive negative sampling) secara signifikan meningkatkan F1 score ekstraksi kuadruplet (Xu et al., 2023).
Model bahasa besar tanpa penyesuaian khusus mengalami kesulitan evaluasi akibat ketatnya metrik pencocokan tepat (exact match) (Zhang et al., 2024).
Formulasi multi-tugas berbantuan prompt memperbaiki adaptabilitas lintas bahasa dan domain spesifik (Xu et al., 2025; Jia et al., 2026; Van Dang et al., 2024).
Secara ringkas, ACOSQE tidak mengungguli model generatif karena ACOSQE merupakan nama tugasnya, sementara model generatif merupakan teknik yang terbukti paling kompetitif dalam menyelesaikan ekstraksi opini implisit tersebut (Li et al., 2023; Peper & Wang, 2022; Lei et al., 2024).
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
Hoang, C. D., Dinh, Q. V., & Tran, N. H. (2022). Aspect-Category-Opinion-Sentiment Extraction Using Generative Transformer Model. 2022 RIVF International Conference on Computing and Communication Technologies (RIVF), 1-6. https://doi.org/10.1109/rivf55975.2022.10013820
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. ACM Comput. Surv., 58, 262:1-262:37. https://doi.org/10.1145/3799234
Lei, Z., Zhang, Y., & Chen, S. (2024). A Dual-Template Prompted Mutual Learning Generative Model for Implicit Aspect-Based Sentiment Analysis. Applied Sciences. https://doi.org/10.3390/app14198719
Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. 2023 International Joint Conference on Neural Networks (IJCNN), 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191098
Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. Neurocomputing, 586, 127642. https://doi.org/10.1016/j.neucom.2024.127642
Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. ArXiv, abs/2211.07743. https://doi.org/10.48550/arxiv.2211.07743
Van Dang, T., Duong, H., & Nguyen, N. (2024). Vi-AbSQA: Multi-task Prompt Instruction Tuning Model for Vietnamese Aspect-based Sentiment Quadruple Analysis. ACM Transactions on Asian and Low-Resource Language Information Processing. https://doi.org/10.1145/3676886
Wang, X., Li, X., Yin, Y., & Li, Y. (2024). Implicit aspect-based generative model for sentiment analysis based on prompt learning. 2024 5th International Conference on Big Data & Artificial Intelligence & Software Engineering (ICBASE), 94-97. https://doi.org/10.1109/icbase63199.2024.10762313
Wang, J., Yang, A., Zhou, D., Lin, N.-K., Wang, Z.-P., Huang, W., & Chen, B. (2023). Simplifying Aspect-Sentiment Quadruple Prediction with Cartesian Product Operation. 707-719. https://doi.org/10.1007/978-981-99-4752-2_58
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. International Journal of Machine Learning and Cybernetics, 14, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
Xu, C., Wang, M., Ren, Y., & Zhu, S. (2026). Enhancing Aspect-Based Sentiment Analysis in Tourism Using Large Language Models and Positional Information. Tsinghua Science and Technology. https://doi.org/10.26599/tst.2024.9010138
Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. ArXiv, abs/2311.03896. https://doi.org/10.48550/arxiv.2311.03896
Xu, C., Wang, M., & Zhu, S. (2025). Tourism sentiment quadruple extraction via new neural ordinary differential equation networks with multitask learning and implicit sentiment enhancement. Expert Syst. Appl., 270, 126417. https://doi.org/10.1016/j.eswa.2025.126417
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhang, H., Song, X.-W., Jia, X., Yang, C., Chen, Z., Chen, B., Jiang, B., Wang, Y., & Feng, R. (2024). Query-induced multi-task decomposition and enhanced learning for aspect-based sentiment quadruple prediction. Eng. Appl. Artif. Intell., 133, 108609. https://doi.org/10.1016/j.engappai.2024.108609
Zhu, L., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. World Wide Web, 26, 3303 - 3320. https://doi.org/10.1007/s11280-023-01185-9