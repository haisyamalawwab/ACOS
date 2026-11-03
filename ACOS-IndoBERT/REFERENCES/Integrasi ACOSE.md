Integrasi ACOSE diperlukan untuk pemetaan afektif granular yang terstruktur.
Penyelidikan ini mengkaji alasan mendasar pemilihan elemen ACOSE, perbandingannya dengan paradigma pembelajaran mesin konvensional, serta peran arsitektur berbasis Large Language Models (LLM) generatif (Zhang et al., 2022; D'Aniello & Gaeta, 2022; Chai et al., 2025).
Rasionalitas Formalisasi Elemen ACOSE
Konseptualisasi Aspect-Category-Opinion-Sentiment-Emotion (ACOSE) membedakan aspek semantik obyektif dari respon psikologis jangka pendek maupun disposisi afektif tahan lama (D'Aniello & Gaeta, 2022). Tugas alternatif sering kali hanya menyelesaikan sebagian dimensi linguistik secara terfragmentasi (Zhang et al., 2022; Zhang et al., 2024; Wankhade et al., 2024).
Polaritas positif-negatif tidak memadai untuk menggambarkan kondisi afektif seperti kemarahan atau rasa jijik yang berakar pada teori enam emosi dasar Ekman (Chai et al., 2025; D'Aniello & Gaeta, 2022).
Alternatif tugas majemuk seperti Opinion-Aspect-Category-Irrealis-Sentiment (OACIS) mengintegrasikan elemen modalisasi irrealis, tetapi fokus utamanya memodifikasi skor polaritas leksikal dan bukan mengidentifikasi jenis emosi spesifik (Dey & Jenamani, 2024).
Skema kuintuplet menggabungkan keunggulan ekstraksi tersurat dan tersirat dalam satu kesatuan struktur data guna mencegah kesalahan interpretasi evaluasi konsumen (D'Aniello & Gaeta, 2022; Xiong et al., 2023; Wankhade et al., 2024).
Hubungan Machine Learning dan Deep Learning
Deep learning (DL) secara fundamental merupakan cabang dari machine learning (ML) yang memanfaatkan arsitektur jaringan saraf tiruan berlapis banyak (Janiesch et al., 2021; Möller, 2019; Taye, 2023). Perbedaan fungsional keduanya terletak pada mekanisme representasi fitur dan skalabilitas data teks (H. et al., 2019; Janiesch et al., 2021; Taye, 2023).
Paradigma
Ekstraksi Fitur
Kebutuhan Komputasi
Kapasitas Kontekstual
Machine Learning
Rekayasa fitur manual (BoW, TF-IDF) (Taye, 2023; Corak et al., 2025)
Rendah, efisien pada data kecil (Janiesch et al., 2021; Corak et al., 2025)
Terbatas pada dependensi lokal (Afriyie & Weyori, 2026; Corak et al., 2025)
Deep Learning
Ekstraksi hierarkis otomatis (Chauhan et al., 2023; Dargan et al., 2019)
Tinggi, butuh akselerasi GPU (Salur & Aydin, 2020; Taye, 2023)
Menangkap dependensi jangka panjang (Salur & Aydin, 2020; Corak et al., 2025)
Figure 1: Perbandingan karakteristik operasional machine learning tradisional dan deep learning.
Studi empiris menunjukkan bahwa algoritma pembelajaran mesin tradisional seperti SVM dan Naive Bayes bersaing ketat pada korpus kecil berbiaya rendah, namun metode deep learning unggul konsisten dalam memetakan relasi teks bertingkat (Minaee et al., 2020; Seo et al., 2020; Corak et al., 2025).
Relevansi Pendekatan LLM Generatif
Alih-alih bersaing, LLM generatif justru menjadi instrumen utama dalam mengatasi kendala propagasi galat (error propagation) pada metode pipeline sebelumnya (Chai et al., 2025; Xiong et al., 2023). Kerangka kerja modern mereformulasikan tugas ACOS dan ekstraksi afektif ke dalam format pembangkitan sekuens (sequence-to-sequence) secara end-to-end (Zhang et al., 2022; Chai et al., 2025; Xiong et al., 2023).
Penggunaan prompting dan dekomposisi kalimat pada LLM memungkinkan pemisahan konteks yang tumpang tindih untuk menghasilkan anotasi emosi akurat per kategori aspek (Chai et al., 2025).
Arsitektur multi-tugas berbasis LLM memanfaatkan kerangka Valence-Arousal-Dominance (VAD) untuk melakukan penyempurnaan konsistensi emosi sebelum menghasilkan prediksi akhir (Chai et al., 2025).
Formulasi generatif secara simultan memetakan pasangan sentimen dan emosi tanpa memerlukan pipeline terpisah, sehingga secara signifikan mengungguli metode dasar terdahulu (Chai et al., 2025).
Integrasi formalisme ACOSE melalui LLM generatif menyatukan granularitas linguistik dan kapabilitas penalaran afektif yang tidak dapat diakomodasi oleh model klasifikasi polaritas konvensional.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Afriyie, Y., & Weyori, B. (2026). Sentiment analysis based on deep learning approaches for text classification. Journal of Electrical Systems and Information Technology, 13. https://doi.org/10.1186/s43067-026-00322-4
Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. ArXiv, abs/2511.19122. https://doi.org/10.48550/arxiv.2511.19122
Chauhan, G., Nahta, R., Meena, Y., & Gopalani, D. (2023). Aspect based sentiment analysis using deep learning approaches: A survey. Comput. Sci. Rev., 49, 100576. https://doi.org/10.1016/j.cosrev.2023.100576
Corak, M., Wang, C., & Zhang, X. (2025). A Comparative Study of Sentiment Analysis on Amazon Customer Reviews: Deep Learning vs. Machine Learning with Balanced and Imbalanced Datasets. 2025 IEEE 16th Annual Ubiquitous Computing, Electronics & Mobile Communication Conference (UEMCON), 0014-0020. https://doi.org/10.1109/uemcon67449.2025.11267657
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. Artificial Intelligence Review, 55, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
Dargan, S., Kumar, M., Ayyagari, M. R., & Kumar, G. (2019). A Survey of Deep Learning and Its Applications: A New Paradigm to Machine Learning. Archives of Computational Methods in Engineering, 27, 1071 - 1092. https://doi.org/10.1007/s11831-019-09344-w
Dey, A., & Jenamani, M. (2024). Aspect based sentiment analysis of consumer reviews using unsupervised attention neural framework. Appl. Soft Comput., 167, 112259. https://doi.org/10.1016/j.asoc.2024.112259
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. Expert Syst. Appl., 118, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
Janiesch, C., Zschech, P., & Heinrich, K. (2021). Machine learning and deep learning. Electronic Markets, 31, 685 - 695. https://doi.org/10.1007/s12525-021-00475-2
Minaee, S., Kalchbrenner, N., Cambria, E., Nikzad, N., Chenaghlu, M., & Gao, J.-F. (2020). Deep Learning--based Text Classification. ACM Computing Surveys (CSUR), 54, 1 - 40. https://doi.org/10.1145/3439726
Möller, D. (2019). Machine Learning and Deep Learning. Cybersecurity in Digital Transformation. https://doi.org/10.35940/ijitee.l3550.1081219
Salur, M. U., & Aydin, I. (2020). A Novel Hybrid Deep Learning Model for Sentiment Classification. IEEE Access, 8, 58080-58093. https://doi.org/10.1109/access.2020.2982538
Seo, S., Kim, C., Kim, H., Mo, K., & Kang, P. (2020). Comparative Study of Deep Learning-Based Sentiment Classification. IEEE Access, 8, 6861-6875. https://doi.org/10.1109/access.2019.2963426
Taye, M. (2023). Understanding of Machine Learning with Deep Learning: Architectures, Workflow, Applications and Future Directions. Comput., 12, 91. https://doi.org/10.3390/computers12050091
Wankhade, M., Kulkarni, C., & Rao, A. C. S. (2024). A survey on aspect base sentiment analysis methods and challenges. Appl. Soft Comput., 167, 112249. https://doi.org/10.1016/j.asoc.2024.112249
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. International Journal of Machine Learning and Cybernetics, 14, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. IEEE Transactions on Knowledge and Data Engineering, 35, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x