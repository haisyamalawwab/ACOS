# Matriks Literatur **ABSA dan Fine-Tuning BERT**

Literatur 2021–2026 yang tersedia mencakup tiga kebutuhan tesis: **ABSA/ACSA berbasis BERT, optimasi fine-tuning, dan analisis ulasan gim**. Namun, kelengkapan pelaporan tidak merata: beberapa studi menyediakan konfigurasi dan hasil numerik, sedangkan lainnya hanya tersedia sebagai abstrak.

**Catatan verifikasi:** peringkat Q1/Q2 dan CORE A/B tidak tercantum dalam bahan yang tersedia, sehingga tidak dapat dipastikan di sini. DOI hanya ditampilkan ketika identifikatornya tersedia secara eksplisit; “belum terverifikasi” bukan berarti artikel tidak memiliki DOI. Matriks berikut membedakan **parameter yang diuji** dari **konfigurasi tetap**, serta keterbatasan penulis dari implikasi metodologis untuk tesis.

## 1. ABSA Berbasis Transformer

ABSA perlu dibedakan menurut tugasnya: klasifikasi sentimen terhadap aspek yang sudah diketahui tidak sama dengan ekstraksi aspek, opini, dan sentimen secara bersama-sama. Survei Zhang *et al.* mengorganisasikan perbedaan tersebut berdasarkan aspek, kategori aspek, opini, dan polaritas (Zhang et al., 2022).

| Author(s) & Year — Harvard | Tujuan & Domain/Dataset | Arsitektur & Model Pralatih | Strategi Tuning & Parameter | Hasil Evaluasi | Keterbatasan / Research Gap | DOI Valid |
|---|---|---|---|---|---|---|
| Dai *et al.* (2021), *Does syntax matter?*; NAACL-HLT | Menguji kebutuhan sintaks eksplisit untuk ALSC; Rest14, Laptop14, Twitter, dan tiga dataset non-Inggris | BERT/RoBERTa + MLP; pembanding ASGCN, PWCN, RGAT | **Konfigurasi tetap:** batch 32, dropout 0.1, LR 2e-4, AdamW; validasi 20% data latih (Dai et al., 2021) | RoBERTa–MLP: Rest14 Acc 87.37%, Macro-F1 80.96%; Laptop14 83.78%/80.73%; Twitter 77.17%/76.20% (Dai et al., 2021) | Hanya ALSC; sampel berpolaritas konflik dan aspek NULL dikeluarkan; bukan evaluasi ekstraksi end-to-end (Dai et al., 2021) | Belum terverifikasi |
| Mao *et al.* (2021), *A Joint Training Dual-MRC Framework* | Menyatukan ekstraksi aspek, opini, dan sentimen pada benchmark ABSA | Dua BERT-MRC dengan berbagi parameter | Detail LR, batch, optimizer, dan ruang pencarian tidak tersedia dalam kutipan | Melaporkan peningkatan atas metode pembanding; angka tidak tersedia (Mao et al., 2021) | Relevan untuk ABSA lengkap, tetapi belum menunjukkan transfer ke ulasan gim atau evaluasi temporal (Mao et al., 2021) | Belum terverifikasi |
| Murtadha *et al.* (2022), *BERT-ASC*; **Expert Systems with Applications** | Kategorisasi aspek dan sentimen, khususnya aspek implisit; benchmark ABSA/TABSA | BERT dengan konstruksi kalimat bantu otomatis | Strategi representasi dijelaskan; rentang hyperparameter tidak tersedia | Melaporkan peningkatan pada kategorisasi aspek dan sentimen; angka tidak tersedia (Murtadha et al., 2022) | Ketersediaan label berkualitas untuk pemetaan aspek implisit menjadi motivasi utama (Murtadha et al., 2022) | Belum terverifikasi |
| Aziz *et al.* (2024); **Scientific Reports** | Menyatukan berbagai subtugas ABSA | BERT + biaffine attention + Multi-Layered Enhanced GCN | Rentang tuning tidak tersedia; menguji pemurnian representasi pasangan kata | Melaporkan peningkatan pada benchmark; angka tidak tersedia (Aziz et al., 2024) | Kompleksitas relasi ditangani melalui fitur linguistik; manfaatnya pada bahasa informal gim belum ditunjukkan dalam kutipan (Aziz et al., 2024) | Belum terverifikasi |
| Perikos dan Diamantopoulos (2024); **Big Data and Cognitive Computing** | Membandingkan transformer dan menjelaskan prediksi; MAMS, SemEval, Naver; >16,100 kalimat | BERT, RoBERTa, DistilBERT, XLNet; LIME, SHAP, integrated gradients, Grad-CAM | Fine-tuning dengan hyperparameter optimal; nilai/rentang tidak tersedia dalam kutipan | RoBERTa: Acc 89.16% pada MAMS/SemEval dan 97.62% pada Naver (Perikos & Diamantopoulos, 2024) | Interpretabilitas dan bias tetap menjadi perhatian; penjelasan bukan bukti ketahanan temporal (Perikos & Diamantopoulos, 2024) | Belum terverifikasi |
| Alhadlaq dan Altheneyan (2024); **PeerJ Computer Science** | ABSA multibahasa; Rest14, Rest15, Rest16-EN, Rest16-ESP | DistilRoBERTa + GNN | Strategi prapemrosesan empat fase; rentang tuning tidak tersedia | F1: 77.98%, 76.86%, 84.96%, 74.87%, berurutan; jenis averaging tidak disebutkan (Alhadlaq & Altheneyan, 2024) | Kelangkaan anotasi domain dan nuansa bahasa masih menjadi masalah (Alhadlaq & Altheneyan, 2024) | Belum terverifikasi |

**Figure 1:** Perbandingan arsitektur transformer untuk berbagai tugas ABSA

**Implikasi untuk pemilihan baseline:** RoBERTa–MLP merupakan pembanding penting sebelum menambahkan GCN, karena penambahan struktur pohon di atas RoBERTa tidak selalu meningkatkan hasil (Dai et al., 2021). Sebaliknya, DualGCN memanfaatkan komplementaritas sintaks dan semantik untuk mengurangi masalah kesalahan parsing, sementara KGAN menambahkan representasi pengetahuan eksternal (Li et al., 2021; Zhong et al., 2022).

## 2. Fine-Tuning dan Hyperparameter

| Author(s) & Year — Harvard | Tujuan & Domain/Dataset | Arsitektur & Model Pralatih | Strategi Tuning & Parameter | Hasil Evaluasi | Keterbatasan / Research Gap | DOI Valid |
|---|---|---|---|---|---|---|
| Liu dan Wang (2021), *An Empirical Study on Hyperparameter Optimization* | Membandingkan HPO untuk fine-tuning dua model bahasa pada GLUE | Dua model bahasa pralatih; nama tidak tersedia dalam kutipan | Membandingkan tiga algoritma HPO dengan grid search pada anggaran waktu setara | HPO sering gagal mengungguli grid search karena anggaran tidak cukup dan overfitting (Liu & Wang, 2021) | Keuntungan HPO bergantung ruang pencarian dan anggaran; overfitting tetap terjadi dalam beberapa kasus (Liu & Wang, 2021) | Belum terverifikasi; rekaman tersedia sebagai preprint |
| Nugroho *et al.* (2021); **SIET** | Sentimen 10,615 ulasan berbahasa Indonesia dari sepuluh aplikasi Google Play | multilingual BERT-base dan IndoBERT-base | Tuning hyperparameter; membandingkan label berbasis skor dan leksikon; rentang lengkap tidak tersedia | IndoBERT mencapai Acc 84%, 25 epoch, waktu latih 24 menit (Nugroho et al., 2021) | Label otomatis perlu dibedakan dari anotasi manusia; bukan ABSA (Nugroho et al., 2021) | [10.1145/3479645.3479679](https://doi.org/10.1145/3479645.3479679) (Sayeed et al., 2023) |
| Zaidan, Sibaroni dan Prasetyowati (2024); **JUTIF** | Optimasi sentimen ulasan MyTelkomsel | IndoBERT berbasis Indo4B | **Diuji:** learning rate dan epoch; terbaik batch 16, LR 1e-6, 3 epoch | Acc 96% (Zaidan et al., 2024) | Rentang pencarian, Macro-F1, dan variasi antarseed tidak tersedia dalam kutipan | Belum terverifikasi |
| Zhao, Gao dan Fang (2024); **Applied Sciences** | Mengoptimalkan akurasi dan waktu fine-tuning pada CPU; CoLA, SST-2, MRPC, RTE, WNLI | BERT | **Diuji:** batch size, learning rate, epoch, CPU/thread | Hyperparameter yang sesuai meningkatkan akurasi; batch lebih besar mempercepat training jika sumber daya memadai (Zhao et al., 2024) | Hasil berorientasi perangkat keras; konfigurasi terbaik tidak otomatis berlaku pada ABSA/gim | Belum terverifikasi |

**Figure 2:** Perbandingan studi tuning BERT dan efisiensi pelatihan

**Kesimpulan metodologis:** jangan menyamakan optimizer pelatihan dengan algoritma pencarian hyperparameter. PSO, misalnya, digunakan untuk mencari konfigurasi pada model PBX berbasis BERT–ConvXGB, yang mencapai Acc 95.0% dan F1 94.9% pada AG News; hasil itu bukan bukti langsung untuk sentimen aspek ulasan gim (Zeng et al., 2025).

Bukti tambahan menunjukkan bahwa konfigurasi terbaik sangat bergantung dataset: IndoBERT pada ulasan aplikasi perjalanan melaporkan epoch 4 dan LR 5e-5, dengan Acc 0.91 tetapi F1 0.74 (Irmawan et al., 2024). Benchmark yang mencakup 42,800 eksperimen juga tidak menyimpulkan bahwa metode sederhana selalu lebih buruk daripada model kompleks (Reusens et al., 2024).

## 3. Ulasan Gim dan Dinamika Sentimen

| Author(s) & Year — Harvard | Tujuan & Domain/Dataset | Arsitektur & Model Pralatih | Strategi Tuning & Parameter | Hasil Evaluasi | Keterbatasan / Research Gap | DOI Valid |
|---|---|---|---|---|---|---|
| Yu *et al.* (2023); **IEEE Access** | ABSA 1.6 juta ulasan Steam: TEKKEN7, Dota2, PUBG, CS:GO; sekitar 3,000 kalimat beranotasi | LDA + bert-base-uncased + downstream Transformer | Membandingkan downstream layer; hingga 1,500 langkah; empat seed; memilih model berdasarkan skor **test set** (Yu et al., 2023) | Micro-F1 75.48%; Macro-F1 60.46% (Yu et al., 2023) | Pemilihan berdasarkan test set mengurangi independensi evaluasi; hanya bahasa Inggris dan Steam (Yu et al., 2023) | [10.1109/ACCESS.2023.3285864](https://doi.org/10.1109/ACCESS.2023.3285864) (Yu et al., 2023) |
| Braja dan Kodar (2023); **Jurnal Informatika Merdeka Pasuruan** | Sentimen ulasan PUBG Mobile di Google Play | IndoBERT-base dan multilingual BERT-base | Membandingkan pelabelan skor/TextBlob; terbaik LR 0.00002, batch 32, 5 epoch | IndoBERT Acc 94%; waktu latih 12 menit (Braja & Kodar, 2023) | Label TextBlob bukan gold standard manusia; klasifikasi keseluruhan, bukan ABSA (Braja & Kodar, 2023) | Belum terverifikasi |
| Guzsvinecz dan Szűcs (2023); **Computers in Human Behavior** | Panjang, emosi, genre, dan playtime; 35,983,481 ulasan Steam, 11 genre | NRC Emotion Lexicon; analisis NLP/statistik di R; **bukan BERT** | Tidak berlaku untuk fine-tuning | Median panjang ulasan negatif 40 kata versus positif 19 kata (Guzsvinecz & Szűcs, 2023) | Landasan karakteristik domain; bukan benchmark akurasi classifier atau adaptasi model temporal | Belum terverifikasi |
| Moattar (2026); **Discover Computing** | Sentimen biner 147,586 ulasan Steam, 160 gim | Fine-tuned all-MiniLM-L6-v2 + TF-IDF/logistic regression + Naïve Bayes | AdamW, scheduler linear, warmup, clipping, weight decay; batch 32, 1 epoch; panjang 128 token (Moattar, 2026) | F1 94.0%; ROC-AUC 95.0%; averaging F1 tidak dinyatakan (Moattar, 2026) | Bobot adaptif berdasarkan validasi tidak membuktikan adaptasi terhadap perubahan waktu (Moattar, 2026) | Belum terverifikasi |

**Figure 3:** Perbandingan analisis ulasan gim dan sentimen pemain

**Dinamika sentimen harus didefinisikan secara tegas.** Perbedaan menurut playtime bukan perubahan kalender: Yu *et al.* menemukan proporsi negatif lebih tinggi ketika playtime kurang dari dua jam, tetapi menempatkan pelacakan feedback dengan unsur waktu sebagai pengembangan selanjutnya (Yu et al., 2023).

Dua kandidat 2026 lebih langsung relevan untuk dimensi temporal. Priambodo, Doewes dan Rohmadi mengagregasi sentimen BERT menjadi skor mingguan, meramalkan empat minggu ke depan, dan memakai walk-forward validation; angka kesalahan tidak tersedia dalam kutipan (Priambodo et al., 2026). Qi *et al.* menggunakan RoBERTa dan agregasi jendela waktu untuk mendeteksi penurunan sentimen pada media sosial, tetapi bukan ABSA Steam (Qi et al., 2026). Kedua kandidat memerlukan pemeriksaan lebih lanjut atas DOI dan mutu venue sebelum dijadikan rujukan inti.

## 4. Sintesis dan Celah Tesis

**Celah paling relevan adalah menghubungkan ACSA ulasan gim dengan evaluasi lintas waktu yang independen.** Benchmark restoran/laptop menyediakan tugas terstruktur, sedangkan studi Steam menyediakan karakteristik domain dan feedback pemain; hasilnya belum dapat dibandingkan sebagai satu leaderboard.

| Celah Penelitian | Bukti yang Mendukung | Implikasi untuk Tesis |
|---|---|---|
| Aspek dan opini implisit | ACOS menyediakan anotasi aspek/opini implisit; supervised contrastive pre-training juga secara khusus menangani sentimen implisit (Cai et al., 2021; Li et al., 2021) | Anotasikan kategori seperti performa, gameplay, pembaruan, dan server meskipun nama aspek tidak muncul eksplisit |
| Ketergantungan pada parsing | Discrete opinion trees dirancang karena parser eksternal bermasalah pada domain atau bahasa rendah sumber daya (Chen et al., 2022) | Bandingkan BERT/RoBERTa sederhana dengan model graf pada slang dan kalimat tidak baku |
| Kinerja kelas minoritas | Studi Steam utama menunjukkan kesenjangan Micro-F1 75.48% dan Macro-F1 60.46%; studi imbalance gim menyoroti kesulitan mendeteksi feedback negatif (Yu et al., 2023; Huynh-Cam et al., 2026) | Laporkan Macro-F1 dan F1 per kelas, bukan accuracy saja |
| Efisiensi versus kompleksitas | BitFit memperbarui hanya bias dan kompetitif pada data kecil–menengah; Span-ASTE menggunakan pruning untuk mengurangi biaya enumerasi span (Zaken et al., 2021; Xu et al., 2021) | Pertimbangkan baseline parameter-efficient dan laporkan waktu serta memori |
| Temporal bukan sekadar bobot dinamis | Forecasting mingguan memakai walk-forward validation, sedangkan ensemble Steam mengubah bobot berdasarkan performa validasi (Priambodo et al., 2026; Moattar, 2026) | Pisahkan analisis tren, forecasting, dan ketahanan classifier terhadap pergeseran distribusi |

**Figure 4:** Celah penelitian untuk ACSA temporal ulasan Steam

### Rancangan yang Direkomendasikan

Rumusan tesis yang terarah adalah: **“Pengaruh optimasi hyperparameter fine-tuning BERT terhadap ACSA ulasan Steam pada evaluasi lintas waktu.”** Gunakan BERT dan RoBERTa dengan kepala klasifikasi sederhana sebagai baseline, kemudian uji apakah penambahan kompleksitas benar-benar memberikan keuntungan.

Untuk menjaga validitas, pisahkan data latih, validasi, dan uji secara kronologis; gunakan validasi untuk pemilihan konfigurasi dan pertahankan test set sebagai evaluasi akhir. Bandingkan strategi pencarian pada anggaran komputasi setara, karena HPO tidak otomatis mengungguli grid search (Liu & Wang, 2021). Ruang pencarian perlu dinyatakan sebelum eksperimen, termasuk learning rate, batch size, epoch, optimizer, dan aturan early stopping.

**Prioritas bacaan:** Dai *et al.* untuk baseline ABSA, Murtadha *et al.* untuk kategori implisit, Liu dan Wang untuk metodologi HPO, serta Yu *et al.* untuk domain Steam. Matriks ini dapat menjadi kerangka awal literatur, tetapi DOI yang belum terverifikasi, detail hyperparameter yang hilang, dan peringkat venue harus dilengkapi dari halaman penerbit sebelum masuk daftar pustaka final.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Alhadlaq, A., & Altheneyan, A. (2024). Distilroberta2gnn: a new hybrid deep learning approach for aspect-based sentiment analysis. *PeerJ Computer Science, 10*. https://doi.org/10.7717/peerj-cs.2267
 
Aziz, K., Ji, D.-H., Chakrabarti, P., Chakrabarti, T., Iqbal, M. S., & Abbasi, R. (2024). Unifying aspect-based sentiment analysis BERT and multi-layered graph convolutional networks for comprehensive sentiment dissection. *Scientific Reports, 14*. https://doi.org/10.1038/s41598-024-61886-7
 
Braja, A. S. P., & Kodar, A. (2023). Implementasi Fine-Tuning BERT untuk Analisis Sentimen terhadap Review Aplikasi PUBG Mobile di Google Play Store. *J I M P - Jurnal Informatika Merdeka Pasuruan*. https://doi.org/10.51213/jimp.v7i3.779
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chen, C., Teng, Z., Wang, Z.-Q., & Zhang, Y. (2022). Discrete Opinion Tree Induction for Aspect-based Sentiment Analysis. 2051-2064. https://doi.org/10.18653/v1/2022.acl-long.145
 
Dai, J., Yan, H., Sun, T., Liu, P.-F., & Qiu, X. (2021). Does syntax matter? A strong baseline for Aspect-based Sentiment Analysis with RoBERTa. 1816-1829. https://doi.org/10.18653/v1/2021.naacl-main.146
 
Guzsvinecz, T., & Szűcs, J. (2023). Length and sentiment analysis of reviews about top-level video game genres on the steam platform. *Comput. Hum. Behav., 149*, 107955. https://doi.org/10.1016/j.chb.2023.107955
 
Huynh-Cam, T.-T., Chen, L.-S., Huang, H.-J., & Ko, H.-C. (2026). A Hybrid Feature-Weighting and Resampling Model for Imbalanced Sentiment Analysis in User Game Reviews. *Mathematics*. https://doi.org/10.3390/math14081273
 
Irmawan, O. A., Budi, I., Santoso, A., & Putra, P. K. (2024). Improving Sentiment Analysis and Topic Extraction in Indonesian Travel App Reviews Through BERT Fine-Tuning. *Jurnal Nasional Pendidikan Teknik Informatika (JANAPATI)*. https://doi.org/10.23887/janapati.v13i2.77028
 
Li, R., Chen, H., Feng, F., Z., Wang, X.-J., & Hovy, E. (2021). Dual Graph Convolutional Networks for Aspect-based Sentiment Analysis. 6319-6329. https://doi.org/10.18653/v1/2021.acl-long.494
 
Li, Z., Zou, Y., Zhang, C., Zhang, Q., & Wei, Z.-Y. (2021). Learning Implicit Sentiment in Aspect-based Sentiment Analysis with Supervised Contrastive Pre-Training. 246-256. https://doi.org/10.18653/v1/2021.emnlp-main.22
 
Liu, X., & Wang, C. (2021). An Empirical Study on Hyperparameter Optimization for Fine-Tuning Pre-trained Language Models. 2286-2300. https://doi.org/10.18653/v1/2021.acl-long.178
 
Mao, Y., Shen, Y., Yu, C., & Cai, L. (2021). A Joint Training Dual-MRC Framework for Aspect Based Sentiment Analysis. *ArXiv, abs/2101.00816*. https://doi.org/10.1609/aaai.v35i15.17597
 
Moattar, M. (2026). Lightweight hybrid adaptive weighted ensemble integrating fine-tuned SBERT with lexical and statistical models for robust steam review sentiment classification. *Discover Computing, 29*. https://doi.org/10.1007/s10791-026-10296-6
 
Murtadha, A., Wen, B., Pan, S., Su, J.-L., Ao, L., & Liu, Y. (2022). BERT-ASC: Auxiliary-Sentence Construction for Implicit Aspect Learning in Sentiment Analysis. *Expert Syst. Appl., 258*, 125195. https://doi.org/10.48550/arxiv.2203.11702
 
Nugroho, K. S., Sukmadewa, A. Y., Bachtiar, F., & Yudistira, N. (2021). BERT Fine-Tuning for Sentiment Analysis on Indonesian Mobile Apps Reviews. *Proceedings of the 6th International Conference on Sustainable Information Engineering and Technology*. https://doi.org/10.1145/3479645.3479679
 
Perikos, I., & Diamantopoulos, A. (2024). Explainable Aspect-Based Sentiment Analysis Using Transformer Models. *Big Data Cogn. Comput., 8*, 141. https://doi.org/10.3390/bdcc8110141
 
Priambodo, M. P., Doewes, A., & Rohmadi, A. (2026). Forecasting User Perception of Steam Game Reviews across Multiple Genres: A BERT Sentiment-Topic Framework with Topic Attribution. *Journal of Embedded Systems, Security and Intelligent Systems*. https://doi.org/10.59562/jessi.v7i3.13290
 
Qi, Y.-L., Zhao, S.-C., Xue, Z.-M., Zeng, X.-L., & Yu, Z.-H. (2026). Detecting Abnormal User Feedback Patterns Through Temporal Sentiment Aggregation. *2026 IEEE 8th International Conference on Communications, Information System and Computer Engineering (CISCE)*, 1323-1328. https://doi.org/10.1109/cisce69494.2026.11504910
 
Reusens, M., Stevens, A., Tonglet, J., De Smedt, J., Verbeke, W., Broucke, S. V., & Baesens, B. (2024). Evaluating text classification: A benchmark study. *Expert Syst. Appl., 254*, 124302. https://doi.org/10.1016/j.eswa.2024.124302
 
Sayeed, M. S., Mohan, V., & Muthu, K. (2023). BERT: A Review of Applications in Sentiment Analysis. *HighTech and Innovation Journal*. https://doi.org/10.28991/hij-2023-04-02-015
 
Xu, L., Chia, Y. K., & Bing, L. (2021). Learning Span-Level Interactions for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2107.12214*. https://doi.org/10.18653/v1/2021.acl-long.367
 
Yu, Y., Dinh, D.-T., Nguyen, B.-H., Yu, F.-Y., & Huynh, V. (2023). Mining Insights From Esports Game Reviews With an Aspect-Based Sentiment Analysis Framework. *IEEE Access, 11*, 61161-61172. https://doi.org/10.1109/access.2023.3285864
 
Zaidan, M. N., Sibaroni, Y., & Prasetyowati, S. S. (2024). LEARNING RATE AND EPOCH OPTIMIZATION IN THE FINE-TUNING PROCESS FOR INDOBERT’S PERFORMANCE ON SENTIMENT ANALYSIS OF MYTELKOMSEL APP REVIEWS. *Jurnal Teknik Informatika (Jutif)*. https://doi.org/10.52436/1.jutif.2024.5.5.2396
 
Zaken, E. B., Goldberg, Y., & Ravfogel, S. (2021). BitFit: Simple Parameter-efficient Fine-tuning for Transformer-based Masked Language-models. *ArXiv, abs/2106.10199*. https://doi.org/10.18653/v1/2022.acl-short.1
 
Zeng, B., Shang, X., Lu, R., & Zhang, Y.-G. (2025). Particle swarm optimization-based NLP methods for optimizing automatic document classification and retrieval. *PLOS One, 20*. https://doi.org/10.1371/journal.pone.0325851
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhao, L.-X., Gao, W.-R., & Fang, J.-B. (2024). Optimizing Large Language Models on Multi-Core CPUs: A Case Study of the BERT Model. *Applied Sciences*. https://doi.org/10.3390/app14062364
 
Zhong, Q.-H., Ding, L., Liu, J.-H., Du, B., Jin, H., & Tao, D.-C. (2022). Knowledge Graph Augmented Network Towards Multiview Representation Learning for Aspect-Based Sentiment Analysis. *IEEE Transactions on Knowledge and Data Engineering, 35*, 10098-10111. https://doi.org/10.1109/tkde.2023.3250499
 
