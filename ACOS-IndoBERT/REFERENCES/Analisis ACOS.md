Analisis ACOS belum menangkap intensitas emosi dan pemicu perilaku pelanggan secara menyeluruh.
Sistem Aspect-Category-Opinion-Sentiment (ACOS) konvensional berfokus pada polaritas sentimen diskret tiga kelas (positif, netral, negatif), sehingga membatasi pemahaman terhadap nuansa afektif mendalam (Zhang et al., 2024; Han & Moghaddam, 2024). Analisis ini meninjau dimensi intensitas emosi, pemicu perilaku konsumen seperti risiko churn, serta tantangan pemodelan aspek implisit dalam bahasa alami termasuk konteks Bahasa Indonesia.
Dimensi Intensitas Emosi
Model ACOS standar mereduksi emosi manusia ke dalam polaritas biner atau triner, yang mengabaikan variasi leksikal seperti kata pengubah atau derajat afeksi (Lee et al., 2026). Pendekatan berbasis sains afektif menggantikan klasifikasi kaku ini dengan pemetaan ruang berkelanjutan numerik (Lee et al., 2026; Alshawi et al., 2026).
Analisis sentimen dimensi (dimensional aspect-based sentiment analysis atau DimABSA) memetakan emosi sepanjang sumbu valensi (valence) dan ketergugahan (arousal) untuk mengukur intensitas afektif riil (Lee et al., 2026; Alshawi et al., 2026).
Kerangka valensi-ketergugahan mampu membedakan teks dengan polaritas sama, seperti memisahkan ungkapan sangat bahagia dari pemulihan biasa, serta sangat kasar dari sekadar berjarak agak jauh (Lee et al., 2026).
Evaluasi terkini pada korpus multibahasa menunjukkan bahwa skor numerik berkelanjutan (continuous scores) menuntut integrasi metrik terpadu seperti continuous F1 (cF1) guna mengevaluasi ketepatan regresi intensitas afektif (Lee et al., 2026; Yu et al., 2026).
Pemicu Perilaku Konsumen
Membedakan emosi spesifik seperti kemarahan (anger) versus kekecewaan atau frustrasi sangat menentukan kemampuan organisasi dalam memprediksi retensi dan tindakan pelanggan (Crolic et al., 2021; González‐Gómez et al., 2021). Sentimen negatif seragam menyembunyikan perbedaan antara pengguna yang ingin beralih penyedia layanan (churn) dan pengguna yang mencari penyelesaian masalah (Slof et al., 2021; González‐Gómez et al., 2021).
Eksperimen pada interaksi bot layanan menunjukkan bahwa pelanggan dalam kondisi emosi marah mengalami penurunan kepuasan drastis saat menghadapi agen berkarakter antropomorfik, suatu efek yang tidak terjadi pada pelanggan non-marah (Crolic et al., 2021).
Integrasi teks transkrip panggilan layanan ke dalam pemodelan risiko bersaing (competing risks model) secara signifikan meningkatkan akurasi prediksi alasan pelanggan memutuskan berhenti berlangganan (Slof et al., 2021; Vo et al., 2021).
Analisis tindakan tutur (speech act theory) membuktikan bahwa arahan negatif (negative directives) berdampak jauh lebih merusak terhadap penjualan produk dibandingkan sekadar kata bersentimen negatif biasa (Ordenes et al., 2017).
Kompleksitas Sentimen dan Bahasa Alami
Teks ulasan daring kerap tidak menyebutkan target aspek atau opini secara eksplisit, melainkan tersirat dalam konteks situasi atau tuturan pragmatis (Zhang et al., 2024; Han & Moghaddam, 2024). Dalam konteks bahasa alami yang kaya ragam dialek dan bentuk percakapan seperti Bahasa Indonesia, penanganan elemen implisit memerlukan arsitektur pengayaan semantik eksternal (Aziz et al., 2024; Ahmed et al., 2023).
Dimensi Pendekatan
Metode Representasi
Manfaat Perilaku & Nuansa
Sumber Utama
Dimensi Valensi-Arousal
Regresi ruang kontinu VA
Membedakan level intensitas kemarahan ekstrem
(Lee et al., 2026; Zhou et al., 2026)
Pembedaan Emosi Diskrit
Anotasi frustrasi vs kemarahan
Mengukur retensi dan efektivitas pemulihan layanan
(Mccoll-Kennedy et al., 2018; González‐Gómez et al., 2021)
Opini & Aspek Implisit
Graf dependensi & modul posisi
Menangkap sentimen tanpa kata penanda eksplisit
(Han & Moghaddam, 2024; Ahmed et al., 2023)
Regulasi Respons Manajerial
Pemodelan sistematis-heuristik
Menentukan intervensi empati untuk menekan churn
(Hung et al., 2023)
Figure 1: Perbandingan dimensi afektif dan penanganan aspek implisit dalam sistem penambangan opini tingkat lanjut.
Integrasi dimensi valensi-ketergugahan dan representasi pengetahuan implisit membuktikan bahwa sistem berbasis ACOS harus bertransformasi dari sekadar kategorisasi polaritas statis menjadi pemodelan afektif komprehensif demi mendukung mitigasi perilaku konsumen secara tepat.
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Ahmed, K., Nadeem, M. I., Zheng, Z., Li, D., Ullah, I., Assam, M., Ghadi, Y., & Mohamed, H. G. (2023). Breaking down linguistic complexities: A structured approach to aspect-based sentiment analysis. Journal of King Saud University Computer and Information Sciences, 35. https://doi.org/10.1016/j.jksuci.2023.101651
Alshawi, R., Raj, A., Kudelya, A., & Shirnin, A. (2026). The Classics at SemEval-2026 Task 3: Combining Transformer Models and LLM-Generated Annotations for Dimensional Aspect-Based Sentiment Analysis. 2648-2656. https://doi.org/10.18653/v1/2026.semeval-1.334
Aziz, M., Bakar, A. A., & Yaakub, M. R. (2024). CoreNLP dependency parsing and pattern identification for enhanced opinion mining in aspect-based sentiment analysis. Journal of King Saud University Computer and Information Sciences, 36. https://doi.org/10.1016/j.jksuci.2024.102035
Crolic, C., Thomaz, F., Hadi, R., & Stephen, A. (2021). Blame the Bot: Anthropomorphism and Anger in Customer–Chatbot Interactions. Journal of Marketing, 86, 132 - 148. https://doi.org/10.1177/00222429211045687
González‐Gómez, H. V., Hudson, S., & Rychalski, A. (2021). The psychology of frustration: Appraisals, outcomes, and service recovery. Psychology & Marketing. https://doi.org/10.1002/mar.21528
Han, Y., & Moghaddam, M. (2024). Design Knowledge as Attention Emphasizer in Large Language Model-Based Sentiment Analysis. J. Comput. Inf. Sci. Eng., 25. https://doi.org/10.1115/1.4067212
Hung, H.-Y., Hu, Y., Lee, N., & Tsai, H.-T. (2023). Exploring online consumer review-management response dynamics: A heuristic-systematic perspective. Decis. Support Syst., 177, 114087. https://doi.org/10.1016/j.dss.2023.114087
Lee, L.-H., Yu, L.-C., Loukashevich, N., Alimova, I., Panchenko, A., Lin, T.-M., Xu, Z.-Y., Zhou, J.-Y., Zheng, G., Wang, J., Awasthi, S., Becker, J., Wahle, J. P., Ruas, T., Muhammad, S. H., & Mohammad, S. (2026). DimABSA: Building Multilingual and Multidomain Datasets for Dimensional Aspect-Based Sentiment Analysis. ArXiv, abs/2601.23022. https://doi.org/10.48550/arxiv.2601.23022
Mccoll-Kennedy, J., Zaki, M., Lemon, K. N., Urmetzer, F., & Neely, A. (2018). Gaining Customer Experience Insights That Matter. Journal of Service Research, 22, 26 - 8. https://doi.org/10.1177/1094670518812182
Ordenes, F. V., Ludwig, S., De Ruyter, K., Grewal, D., & Wetzels, M. (2017). Unveiling What Is Written in the Stars: Analyzing Explicit, Implicit, and Discourse Patterns of Sentiment in Social Media. Journal of Consumer Research, 43, 875-894. https://doi.org/10.1093/jcr/ucw070
Slof, D., Frasincar, F., & Matsiiako, V. (2021). A competing risks model based on latent Dirichlet Allocation for predicting churn reasons. Decis. Support Syst., 146, 113541. https://doi.org/10.1016/j.dss.2021.113541
Vo, N., Liu, S., Li, X.-T., & Xu, G.-D. (2021). Leveraging unstructured call log data for customer churn prediction. Knowl. Based Syst., 212, 106586. https://doi.org/10.1016/j.knosys.2020.106586
Yu, L.-C., Becker, J., Muhammad, S. H., Abdulmumin, I., Lee, L.-H., Lin, Y.-L., Wang, J., Wahle, J. P., Ruas, T., Loukachevitch, N., Panchenko, A., Alimova, I., Wanzare, L., Onyango, N. O., Gipp, B., Chang, K.-W., & Mohammad, S. (2026). SemEval-2026 Task 3: Dimensional Aspect-Based Sentiment Analysis (DimABSA). 3753-3778. https://doi.org/10.48550/arxiv.2604.07066
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. Artificial Intelligence Review, 57. https://doi.org/10.1007/s10462-023-10633-x
Zhou, Z., He, X., & Bai, C. (2026). SCUZANE at SemEval-2026 Task 3: Dimensional Aspect-based Sentiment Analysis with Supervised Contrastive Regression and R-Drop Regularization. 1992-1996. https://doi.org/10.18653/v1/2026.semeval-1.251