# Ya, **BERT mengungguli model klasik** pada analisis sentimen berbasis aspek perbankan digital Indonesia.


Bukti empiris menunjukkan model berbasis BERT secara konsisten melampaui algoritma machine learning tradisional dalam ekstraksi aspek maupun klasifikasi polaritas pada korpus ulasan finansial berbahasa Indonesia (Natália et al., 2026; Pardamean et al., 2025; Wirawan et al., 2026).
**Figure 1:** Tingkat konsensus literatur mengenai keunggulan performa BERT atas model klasik.

## Perbandingan Kinerja Model

Model transformer seperti IndoBERT secara konsisten mencatatkan metrik akurasi dan F1-score yang lebih tinggi dibandingkan algoritma klasik seperti Support Vector Machine (SVM) dan Naïve Bayes (Pardamean et al., 2025; Wirawan et al., 2026; , 2025). Evaluasi ulasan aplikasi mobile banking blu menunjukkan IndoBERT yang di-fine-tune mencapai akurasi hingga 99% pada klasifikasi aspek serta F1-score antara 84% hingga 96% pada polaritas sentimen (Pardamean et al., 2025). Pada studi perbandingan komprehensif ulasan aplikasi Mobile JKN di ranah layanan publik, arsitektur IndoBERT-base terbukti paling tangguh dibanding kombinasi TF-IDF dengan SVM serta Word2Vec dengan BiLSTM (Wirawan et al., 2026). Selain itu, representasi BERT mentransformasikan teks ke dalam vektor kontekstual yang jauh lebih rapat dan terpisah antar kelas dibanding representasi berbasis embedding standar (Murfi et al., 2022).

**Fig 5.** T-SNE visualization of the text representation from BERT and embedding method in each dataset (Murfi et al., 2022)

*How to read: Plot t-SNE memvisualisasikan sebaran klaster representasi teks: panel kiri dan kanan membandingkan pemisahan fitur embedding standar versus representasi BERT. Pemisahan klaster yang lebih tegas dan terisolasi merefleksikan kualitas pemisahan semantik yang lebih baik.*

Meski demikian, efektivitas BERT sangat dipengaruhi oleh distribusi data latih dan teknik penyesuaian bobot. Pada pengujian ulasan aplikasi berbahasa Indonesia dengan ketidakseimbangan kelas ekstrem, varian BERT yang menggunakan pembekuan lapisan terkadang menghasilkan F1-score yang lebih rendah dibandingkan model SVM atau Naïve Bayes teroptimasi (, 2025). Prapelatihan spesifik domain finansial menjadi krusial untuk mengatasi keterbatasan korpus umum dan istilah perbankan yang spesifik (Maharani et al., 2023).

## Arsitektur Pemodelan Sentimen Perbankan

| Model | Domain / Korpus | Metrik Utama | Keunggulan Utama | Sitasi |
| :--- | :--- | :--- | :--- | :--- |
| **IndoBERT–LLaMA Hybrid** | Ulasan m-banking (5.513 data) | 0,950 Akurasi, 0,862 F1 | Menggabungkan kepekaan konteks dan penalaran | (Natália et al., 2026) |
| **Fine-tuned IndoBERT** | Ulasan blu BCA (10.159 data) | 99% Akurasi aspek, 84–96% F1 | Generalisasi kuat pada ulasan aplikasi perbankan | (Pardamean et al., 2025) |
| **IndoBERT Sent-Pair** | Ulasan pelanggan Indonesia | +23,6% F1 vs XGBoost | Efektif mengekstrak aspek berbasis kalimat bantu | (Yulianti & Nissa, 2024) |
| **IndoBERT Base** | Dompet digital DANA (6.106 data) | 91,24% Akurasi, 0,91 F1 | Menangani ragam bahasa informal dan singkatan | (Susanto et al., 2026) |
| **TF-IDF + SVM** | Ulasan publik & perbankan | Baseline kompetitif | Cepat dilatih namun rentan kehilangan konteks lokal | (Wirawan et al., 2026) |

**Figure 2:** Ringkasan komparasi kinerja arsitektur model ABSA pada ulasan layanan perbankan dan finansial.

## Faktor Keunggulan dan Keterbatasan

* **Pemahaman Konteks Dwiarah**: BERT menangkap makna kata berdasarkan urutan kalimat dan posisi secara dinamis, melampaui asumsi independensi konteks pada model bag-of-words klasik (Murfi et al., 2022; Gao et al., 2019).
* **Keunggulan Korpus Lokal**: Varian unilingual seperti IndoBERT secara konsisten mengungguli multilingual BERT (mBERT) karena dilatih langsung pada miliaran kata bahasa Indonesia informal (Azhar & Khodra, 2020; Citra & Ghifari, 2026; Maharani et al., 2023).
* **Integrasi Pengetahuan Tambahan**: Kombinasi representasi BERT dengan graf pengetahuan (*knowledge graph*) atau ensemble pohon keputusan meningkatkan deteksi sentimen implisit hingga 23% dibanding model tunggal (Fredyan & Achmad, 2025; Ahmed et al., 2024).
* **Sensitivitas Keterbatasan Data**: Penurunan performa masih terjadi pada aspek verifikasi atau registrasi yang memiliki data sampel minim akibat *data sparsity* (Natália et al., 2026; Wirawan et al., 2026).

Secara keseluruhan, model berbasis IndoBERT menawarkan akurasi semantik superior dibanding algoritma machine learning klasik untuk domain perbankan digital, asalkan didukung prapemrosesan teks informal dan strategi penanganan ketidakseimbangan kelas yang tepat (Susanto et al., 2026; Syaripudin et al., 2025).
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
(2025). Performance Comparison Of BERT Metrics and Classical Machine Learning Models (SVM,Naive Bayes) for Sentiment Analysis. *INOVTEK Polbeng - Seri Informatika*. https://doi.org/10.35314/wmh3rg23
 
Ahmed, S., Samia, M. M., Sayma, M. H., Kabir, M. M., & Mridha, M. F. (2024). tRF-BERT: A transformative approach to aspect-based sentiment analysis in the bengali language. *PLOS ONE, 19*, e0308050 - e0308050. https://doi.org/10.1371/journal.pone.0308050
 
Azhar, A. N., & Khodra, M. L. (2020). Fine-tuning Pretrained Multilingual BERT Model for Indonesian Aspect-based Sentiment Analysis. *2020 7th International Conference on Advance Informatics: Concepts, Theory and Applications (ICAICTA)*, 1-6. https://doi.org/10.1109/icaicta49861.2020.9428882
 
Citra, M. B., & Ghifari, N. T. A. (2026). Fine-Grained Aspect-Based Sentiment Analysis on Indonesian E-Commerce Reviews Using Multi-Task Learning with Pretrained Transformer Models. *2026 International Conference on Smart Computing, IoT, and Machine Learning (SIML)*, 1-6. https://doi.org/10.1109/siml69834.2026.11621828
 
Fredyan, R., & Achmad, S. (2025). Integration of Knowledge Graph and BERT for Sentiment Analysis of Indonesian Product Reviews. *2025 International Conference on Information Management and Technology (ICIMTech)*, 270-275. https://doi.org/10.1109/icimtech67074.2025.11265009
 
Gao, Z., Feng, A., Song, X.-Y., & Wu, X. (2019). Target-Dependent Sentiment Classification With BERT. *IEEE Access, 7*, 154290-154299. https://doi.org/10.1109/access.2019.2946594
 
Maharani, N., Purwarianti, A., Yustiawan, Y., & Rochim, F. C. (2023). Domain-Specific Language Model Post-Training for Indonesian Financial NLP. *2023 International Conference on Electrical Engineering and Informatics (ICEEI)*, 1-6. https://doi.org/10.1109/iceei59426.2023.10346625
 
Murfi, H., S., Gowandi, T., Ardaneswari, G., & Nurrohmah, S. (2022). BERT-Based Combination of Convolutional and Recurrent Neural Network for Indonesian Sentiment Analysis. *ArXiv, abs/2211.05273*. https://doi.org/10.48550/arxiv.2211.05273
 
Natália, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. *2026 9th International Conference on Computing Methodologies and Communication (ICCMC)*, 2002-2007. https://doi.org/10.1109/iccmc69250.2026.11624719
 
Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. *2025 1st International Conference on Data Science and Geoinformatics (ICDSG)*, 37-42. https://doi.org/10.1109/icdsg67714.2025.11381388
 
Susanto, H., Dharmawan, W., Annisa, R., & Fitriana, L. A. (2026). Performance Evaluation of the BERT Model in Sentiment Analysis of DANA Application User Reviews. *Journal of Artificial Intelligence and Engineering Applications (JAIEA)*. https://doi.org/10.59934/jaiea.v5i3.2359
 
Syaripudin, U., Gerhana, Y. A., Wahana, A., & Fuadi, R. (2025). Sentiment Analysis of Google Play Store Reviews on the Top Three Digital Banks in Indonesia Using Bidirectional Encoder Representations from Transformers (BERT). *2025 11th International Conference on Wireless and Telematics (ICWT)*, 1-5. https://doi.org/10.1109/icwt66752.2025.11181730
 
Wirawan, N. O. H., Chandra, G. J., Lucky, H., Pradana, R., & Sagala, N. T. M. (2026). Benchmarking Aspect-Based Sentiment Analysis on Indonesian Mobile JKN Reviews using Transformer Models. *2026 International Electronics Symposium (IES)*, 1-6. https://doi.org/10.1109/ies71033.2026.11702744
 
Yulianti, E., & Nissa, N. K. (2024). ABSA of Indonesian customer reviews using IndoBERT: single- sentence and sentence-pair classification approaches. *Bulletin of Electrical Engineering and Informatics*. https://doi.org/10.11591/eei.v13i5.8032
 
