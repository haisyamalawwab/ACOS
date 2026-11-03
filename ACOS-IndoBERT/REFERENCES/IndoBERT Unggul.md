ndoBERT unggul untuk ABSA, tetapi bukti ACOSE perbankan langsung belum ada.
Bukti riset secara konsisten menunjukkan ya: IndoBERT terbukti melampaui algoritma konvensional dan deep learning dasar pada tugas ABSA dan klasifikasi sentimen perbankan digital Indonesia, kendati ekstraksi kuintuplet ACOSE secara terpadu belum banyak dipublikasikan. Figure 1: Konsensus efektivitas arsitektur IndoBERT pada domain perbankan digital Indonesia
Kinerja IndoBERT pada Sentimen Perbankan
Evaluasi empiris menegaskan keunggulan IndoBERT dibanding model pembelajaran mesin konvensional pada korpus ulasan finansial lokal (Casanova et al., 2026; Assani et al., 2025). Pada dataset ulasan aplikasi blu sebanyak 22.923 data, arsitektur IndoBERT-base-p1 mencatatkan skor akurasi, presisi, recall, dan F1 sekitar 0,87 serta AUC-ROC 0,89, mengungguli CNN dan SVM (Casanova et al., 2026). Model ini memperlihatkan presisi 0,85 dan recall 0,90 untuk ulasan negatif, serta presisi 0,89 dan recall 0,83 untuk sentimen positif (Casanova et al., 2026).
Keunggulan serupa terkonfirmasi pada aplikasi perbankan syariah, di mana IndoBERT meraih akurasi 88% dan F1-score 0,86 pada ulasan Bank NTB Syariah, melampaui Naïve Bayes yang hanya memperoleh akurasi 78% dan F1-score 0,74 (Assani et al., 2025). IndoBERT efektif mengenali variasi bahasa nonbaku dan fenomena campur kode (code-mixing) khas pengguna internet Indonesia (Casanova et al., 2026). Kendati demikian, sensitivitas model pada ulasan negatif yang belum sempurna menunjukkan potensi keluhan pengguna yang luput jika pemantauan hanya mengandalkan klasifikasi biner pasif (Casanova et al., 2026).
Ekstraksi Aspek dan Struktur Entitas
Pada ranah ABSA multi-aspek, IndoBERT membuktikan kapabilitas adaptasi representasi kontekstual yang sangat solid (Pardamean et al., 2025). Pengujian terhadap 10.159 ulasan aplikasi blu menunjukkan bahwa IndoBERT fine-tuned mencapai akurasi hingga 99% pada klasifikasi aspek, serta F1-score berturut-turut 84%, 96%, dan 94% untuk polaritas sentimen pada aspek Feature, App Interface, dan User Experience (Pardamean et al., 2025).
Integrasi IndoBERT dengan Conditional Random Field (CRF) terbukti mengurangi galat relasi ketergantungan label entitas sebesar 7% (Dave & Chowanda, 2024).
Arsitektur IndoBERT-BiGRU-CRF mencatat peningkatan F1-score sebesar 0,23 berkat representasi semantik dwiarah dalam membedakan konteks entitas keuangan yang ambigu (Dave & Chowanda, 2024).
Penggabungan IndoBERT dalam knowledge graph menghasilkan F1-score sentimen optimal 0,9373 tanpa rekayasa oversampling (Saputra et al., 2026).
Integrasi Hibrida Menuju ACOSE
Meskipun IndoBERT sangat dominan dalam ekstraksi aspek, kategori, dan sentimen, pembentukan elemen opini (opinion) dan emosi (emotion) yang bernalar kompleks mulai beralih ke kolaborasi bersama model bahasa besar (Natalia et al., 2026). Evaluasi terhadap 5.513 ulasan perbankan seluler membuktikan bahwa ensembel hibrida IndoBERT–LLaMA mencapai akurasi 0,950 dan Macro F1 0,862, melampaui performa model tunggal mandiri (Natalia et al., 2026).
Paradigma Model
Keunggulan Utama
Limitasi Operasional
Bukti Studi
IndoBERT Mandiri
Ekstraksi fitur kontekstual dan klasifikasi aspek akurat (Pardamean et al., 2025; Casanova et al., 2026)
Memerlukan anotasi terpisah untuk emosi granular (Pardamean et al., 2025)
Ulasan blu & Bank XYZ (Pardamean et al., 2025; Saputra et al., 2026)
IndoBERT + CRF / GRU
Penanganan dependensi sekuens entitas keuangan (Dave & Chowanda, 2024)
Terbatas pada ekstraksi rentang teks eksplisit (Dave & Chowanda, 2024)
Korpus IPerFEX-2023 (Dave & Chowanda, 2024)
Hibrida IndoBERT–LLM
Penalaran relasi emosi dan sentimen aspek superior (Natalia et al., 2026)
Beban komputasi inferensi lebih tinggi (Natalia et al., 2026)
Ulasan Mobile Banking 2025 (Natalia et al., 2026)
Figure 2: Komparasi arsitektur berbasis IndoBERT untuk pemrosesan ulasan perbankan digital
IndoBERT terbukti sangat unggul sebagai fondasi encoder representasi teks perbankan digital Indonesia, namun implementasi ACOSE yang menyeluruh paling efektif diraih lewat skema hibrida guna menangkap dimensi afektif yang lebih mendalam (Natalia et al., 2026).
These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.
References
Assani, M. Y., Rudiyan, A., & Radiyah, U. (2025). NLP-Based Sentiment Analysis of Islamic Mobile BankingReviews for Digital Service Quality Enhancement. Jurnal Bumigora Information Technology (BITe). https://doi.org/10.30812/bite.v7i2.5943
Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. Journal of Applied Informatics and Computing. https://doi.org/10.30871/jaic.v10i2.12436
Dave, E., & Chowanda, A. (2024). IPerFEX-2023: Indonesian personal financial entity extraction using indoBERT-BiGRU-CRF model. Journal of Big Data, 11. https://doi.org/10.1186/s40537-024-00987-6
Natalia, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. 2026 9th International Conference on Computing Methodologies and Communication (ICCMC), 2002-2007. https://doi.org/10.1109/iccmc69250.2026.11624719
Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. 2025 1st International Conference on Data Science and Geoinformatics (ICDSG), 37-42. https://doi.org/10.1109/icdsg67714.2025.11381388
Saputra, Z., Enhartana, A. C., Sensuse, D., Lusa, S., Mailinda, I., & Sofia, N. (2026). User Review-Based Knowledge Discovery Model Using Knowledge Graph to Support Proactive Decision-Making in Digital Banking: A Case Study of Bank XYZ. 2026 5th International Conference on Electronics Representation and Algorithm (ICERA), 59-67. https://doi.org/10.1109/icera72709.2026.11666594