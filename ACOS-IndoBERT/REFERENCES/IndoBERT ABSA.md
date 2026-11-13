
# IndoBERT **meningkatkan akurasi ABSA** perbankan, tetapi bukti 13 bank belum ada

**Figure 1:** Tingkat konsensus keunggulan IndoBERT pada tugas ABSA teks perbankan Indonesia

IndoBERT secara konsisten meningkatkan akurasi *Aspect-Based Sentiment Analysis* (ABSA) pada ulasan aplikasi perbankan digital dan *fintech* berbahasa Indonesia dibandingkan model *machine learning* konvensional maupun model multibahasa (Pardamean et al., 2025; Yulianti & Nissa, 2024; Fatihaturrahmah & Tania, 2025; Doewes & Widoyono, 2026). Kendati demikian, literatur yang ada saat ini baru mengevaluasi aplikasi secara individual atau dalam kelompok 1–5 platform (seperti blu, BRImo, DANA, dan GoPay), sehingga bukti empiris spesifik yang mencakup sekaligus **13 bank digital Indonesia** masih belum tersedia dalam publikasi ilmiah (Pardamean et al., 2025; Fatihaturrahmah & Tania, 2025; Simarmata & Sasongko, 2025; Casanova et al., 2026; Thobibuddin & Dewi, 2026).

## Keunggulan IndoBERT dalam ABSA Perbankan

Model berbasis IndoBERT mampu menangani kompleksitas linguistik bahasa Indonesia informal, singkatan, dan campur kode (*code-mixing*) yang umum ditemukan pada ulasan pengguna Play Store (Simarmata & Sasongko, 2025; Casanova et al., 2026; Yuniarto et al., 2026). Pada evaluasi ulasan aplikasi bank digital blu, *fine-tuned* IndoBERT menghasilkan akurasi hingga **99% pada klasifikasi aspek** serta skor F1 sebesar 84%, 96%, dan 94% pada klasifikasi sentimen tiap aspek (Pardamean et al., 2025). Di aplikasi dompet digital DANA, IndoBERT mencatatkan akurasi 98% dan skor F1 sebesar 0.974 pada klasifikasi sentimen aspek keamanan, mengungguli arsitektur SVM, Random Forest, CNN, dan BiLSTM (Fatihaturrahmah & Tania, 2025).

Pengujian lintas-domain dan pengujian temporal juga menunjukkan stabilitas performa IndoBERT yang konsisten saat diuji dari ulasan DANA ke ulasan GoPay (Fatihaturrahmah & Tania, 2025). Peningkatan performa ini berpijak pada prapelatihan IndoBERT pada korpus bahasa Indonesia berskala besar (Indo4B), yang memberikan representasi kontekstual lebih baik daripada model *Multilingual BERT* (mBERT) maupun representasi statis seperti Word2Vec (Yulianti & Nissa, 2024; Citra & Ghifari, 2026; Jayadianti et al., 2022). Selain itu, formulasi klasifikasi pasangan kalimat (*sentence-pair classification*) dengan kalimat bantu (*auxiliary sentences*) menghasilkan peningkatan skor F1 sebesar 23.6% dibanding *baseline* Word2Vec-CNN-XGBoost (Yulianti & Nissa, 2024).

**Table 6.** This two-stage labeling approach ensured the accuracy of the dataset through manual validation. An example of the labeled data is presented in Table 6. (Jazuli et al., 2024)

*How to read: Tabel menampilkan contoh anotasi ulasan umpan balik dalam bahasa Indonesia yang dipetakan ke dalam kategori aspek spesifik beserta polaritas sentimennya.*

Model IndoBERT juga terbukti unggul pada domain layanan publik dan ulasan aplikasi lain di Indonesia, seperti Access by KAI dengan akurasi klasifikasi aspek 92.8% (Doewes & Widoyono, 2026), serta ulasan *e-commerce* dengan akurasi 94.79% melampaui LSTM dan CNN (Wijaya et al., 2026; Dar & Hasibuan, 2025).

## Benchmark Model pada Domain Layanan Digital Indonesia

Berbagai eksperimen empiris mengonfirmasi bahwa IndoBERT menjadi arsitektur paling efektif untuk analisis sentimen berbutir halus (*fine-grained*) di ranah teks ulasan Indonesia dibandingkan metode dasar lainnya.

| Domain Ulasan                        | Model Terbaik       | Metrik Utama                                          | Model Pembanding                                     |
| ------------------------------------ | ------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| **Bank Digital (blu)**         | Fine-tuned IndoBERT | Akurasi aspek 99% (Pardamean et al., 2025)            | Frozen IndoBERT (Pardamean et al., 2025)             |
| **Fintech Keamanan (DANA)**    | IndoBERT            | Akurasi 98%, F1 0.974 (Fatihaturrahmah & Tania, 2025) | BiLSTM, CNN, SVM, RF (Fatihaturrahmah & Tania, 2025) |
| **Mobile Banking (blu)**       | IndoBERT            | Akurasi 87%, AUC 0.89 (Casanova et al., 2026)         | SVM, CNN (Casanova et al., 2026)                     |
| **Bank Syariah (NTB Syariah)** | IndoBERT            | Akurasi 88%, F1 0.86 (Assani et al., 2025)            | Naïve Bayes (Assani et al., 2025)                   |
| **Transportasi (KAI)**         | IndoBERT            | Akurasi aspek 92.8% (Doewes & Widoyono, 2026)         | mBERT, XLM-R, SVM (Doewes & Widoyono, 2026)          |

**Figure 2:** Perbandingan performa model klasifikasi ulasan pada beberapa aplikasi digital Indonesia

## Keterbatasan dan Tantangan untuk 13 Bank Digital

Penerapan langsung pipeline IndoBERT pada skala 13 bank digital menghadapi beberapa hambatan metodologis dan komputasi penting:

- **Ketiadaan dataset acuan 13 bank**: Riset komparatif multi-aplikasi di Indonesia umumnya hanya mencakup 3 hingga 5 penyedia layanan, seperti perbandingan lima *e-wallet* dengan akurasi IndoBERT sebesar 84.36% (Thobibuddin & Dewi, 2026).
- **Ketergantungan pada weak labels**: Banyak kajian perbankan memanfaatkan rating bintang aplikasi sebagai proksi polaritas sentimen alih-alih anotasi aspek manual yang tervalidasi manusia (Casanova et al., 2026; Thobibuddin & Dewi, 2026; Safitri et al., 2026; Setyawati et al., 2026).
- **Ketidakseimbangan kelas dan ambiguitas**: Kelas netral dan ulasan multiaspek sering memicu kesalahan klasifikasi, yang membutuhkan mitigasi tambahan seperti teknik penyeimbangan data atau *ensemble stacking* (Kusumaningtyas et al., 2026; Safitri et al., 2026; Yuniarto et al., 2026).
- **Biaya komputasi pemrosesan**: Arsitektur IndoBERT membutuhkan daya komputasi besar saat inferensi skala masif, mendorong perlunya teknik distilasi pengetahuan seperti ABSA-MiniIndoBERT untuk menekan parameter hingga 98.5% (Wijaya et al., 2026; Ayesh et al., 2026).

Teknik augmentasi seperti *Back-Translation* terbukti mampu menaikkan akurasi IndoBERT sebesar 3% pada teks campur kode (Yuniarto et al., 2026), sementara penggabungan grafik pengetahuan (*knowledge graph*) meningkatkan pengenalan aspek implisit dengan akurasi 94.3% dibanding 88.7% pada IndoBERT standar (Fredyan & Achmad, 2025). Model hibrida ensembel IndoBERT–LLaMA juga mencatatkan akurasi 0.950 pada ulasan perbankan seluler (Natália et al., 2026). Secara metodologis, IndoBERT sangat siap meningkatkan akurasi ABSA perbankan digital, tetapi studi khusus yang menguji performanya secara serentak di seluruh 13 bank digital Indonesia masih perlu dilakukan.

*These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at <https://consensus.app>. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.*

## References

Assani, M. Y., Rudiyan, A., & Radiyah, U. (2025). NLP-Based Sentiment Analysis of Islamic Mobile BankingReviews for Digital Service Quality Enhancement. *Jurnal Bumigora Information Technology (BITe)*. <https://doi.org/10.30812/bite.v7i2.5943>

Ayesh, M. K. M., Iskandar, R. M., & Cenggoro, T. W. (2026). ABSA-MiniIndoBERT: Distilled Version of IndoBERT-lite using MiniALBERT Knowledge Distillation for Efficient Indonesian ABSA. *2026 13th International Conference on ICT for Smart Society (ICISS)*, 1-10. <https://doi.org/10.1109/iciss71466.2026.11715363>

Casanova, M. P., Meiriza, A., Tania, K. D., Oktadini, N. R., & Kurniawan, D. (2026). Comparative Sentiment Analysis of Digital Banking Reviews Using Knowledge Discovery IndoBERT. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v10i2.12436>

Citra, M. B., & Ghifari, N. T. A. (2026). Fine-Grained Aspect-Based Sentiment Analysis on Indonesian E-Commerce Reviews Using Multi-Task Learning with Pretrained Transformer Models. *2026 International Conference on Smart Computing, IoT, and Machine Learning (SIML)*, 1-6. <https://doi.org/10.1109/siml69834.2026.11621828>

Dar, M. H., & Hasibuan, M. N. S. (2025). Implementation of Deep Learning Models in Conducting Aspect-Based Sentiment Analysis. *International Journal of Science, Technology & Management*. <https://doi.org/10.46729/ijstm.v6i4.1251>

Doewes, A., & Widoyono, B. (2026). Aspect-Based Sentiment Analysis of Access by KAI Application Reviews Using IndoBERT for Multi-Label Classification Tasks. *Jurnal Teknik Informatika (Jutif)*. <https://doi.org/10.52436/1.jutif.2026.7.1.5402>

Fatihaturrahmah, A., & Tania, K. D. (2025). A Hybrid Approach of Aspect-Based Sentiment Analysis and Knowledge Extraction for Evaluating Security Perceptions in Digital Payment Applications. *Scientific Journal of Informatics*. <https://doi.org/10.15294/sji.v12i4.31557>

Fredyan, R., & Achmad, S. (2025). Integration of Knowledge Graph and BERT for Sentiment Analysis of Indonesian Product Reviews. *2025 International Conference on Information Management and Technology (ICIMTech)*, 270-275. <https://doi.org/10.1109/icimtech67074.2025.11265009>

Jayadianti, H., Kaswidjanti, W., Utomo, A. T., Saifullah, S., Dwiyanto, F., & Dreżewski, R. (2022). Sentiment analysis of Indonesian reviews using fine-tuning IndoBERT and R-CNN. *ILKOM Jurnal Ilmiah*. <https://doi.org/10.33096/ilkom.v14i3.1505.348-354>

Jazuli, A., W., & Kusumaningrum, R. (2024). Optimizing Aspect-Based Sentiment Analysis Using BERT for Comprehensive Analysis of Indonesian Student Feedback. *Applied Sciences*. <https://doi.org/10.3390/app15010172>

Kusumaningtyas, E., Barakbah, A., Fariza, A., Edelani, R., & Nabila, M. (2026). Aspect-Based Sentiment Analysis of Indonesian Internet Service Provider Reviews Using FineTuned IndoBERT and Clause Segmentation. *2026 International Electronics Symposium (IES)*, 1-8. <https://doi.org/10.1109/ies71033.2026.11702659>

Natália, B., Sunaryono, D., & Purwananto, Y. (2026). Hybrid IndoBERT–LLaMA for Aspect-based Sentiment Analysis of Indonesian Mobile Banking Reviews. *2026 9th International Conference on Computing Methodologies and Communication (ICCMC)*, 2002-2007. <https://doi.org/10.1109/iccmc69250.2026.11624719>

Pardamean, R. K., Bunyamin, B., & Hasmawati, H. (2025). Aspect-Based Sentiment Analysis of blu Application Reviews Using IndoBERT. *2025 1st International Conference on Data Science and Geoinformatics (ICDSG)*, 37-42. <https://doi.org/10.1109/icdsg67714.2025.11381388>

Safitri, A., Risaldi, M., Alwi, M., Surianto, D. F., Fadilah, N., & Parenreng, J. (2026). Improving Sentiment Classification of Kredit Pintar Reviews Using IndoBERT, SMOTE, and Stacking Ensemble. *Jurnal Teknik Informatika (Jutif)*. <https://doi.org/10.52436/1.jutif.2026.7.3.5342>

Setyawati, E., B., & Saputra, D. (2026). Rule-Based Aspect Extraction and IndoBERT-Based Sentiment Classification of Ruparupa Mobile Application Reviews. *Journal of Information Systems and Informatics*. <https://doi.org/10.63158/journalisi.v8i4.1816>

Simarmata, A. A. P., & Sasongko, T. B. (2025). Sentiment Analysis on BRImo Application Reviews Using IndoBERT. *Journal of Applied Informatics and Computing*. <https://doi.org/10.30871/jaic.v9i3.8162>

Thobibuddin, F. F., & Dewi, G. A. (2026). Comparative Sentiment and Complaint Pattern Analysis of Indonesian E-Wallet Application Reviews Using IndoBERT. *Journal of Computing and Smart Ecosystems*. <https://doi.org/10.26714/jcase.v2i1.1143>

Wijaya, S., Edbert, I. S., & D. (2026). Deep Learning Approaches for Aspect-Based Sentiment Analysis on Indonesian E-Commerce Product Reviews. *2026 International Conference on Information Management and Technology (ICIMTech)*, 90-95. <https://doi.org/10.1109/icimtech202671078.2026.11699003>

Yulianti, E., & Nissa, N. K. (2024). ABSA of Indonesian customer reviews using IndoBERT: single- sentence and sentence-pair classification approaches. *Bulletin of Electrical Engineering and Informatics*. <https://doi.org/10.11591/eei.v13i5.8032>

Yuniarto, A. H. P., Achsanti, A. S., Susanto, R., Pratama, A., & Utomo, F. (2026). Mitigating Data Sparsity in Code-Mixed Text through Back-Translation Augmentation for Aspect-Based Sentiment Analysis in Tokopedia Reviews. *Journal of Artificial Intelligence and Engineering Applications (JAIEA)*. <https://doi.org/10.59934/jaiea.v5i2.2197>
