# Strategi **Optimasi Hyperparameter** untuk Fine-Tuning BERT pada ABSA

<experiment_design>
| Feature | Result / Value |
|---|---|
| Jenis studi | Tinjauan sistematis 62 artikel Scopus (PRISMA/VOSviewer) (Bahari et al., 2026) |
| Cakupan | ABSA berbasis BERT, publikasi 2020–pertengahan 2025 (Bahari et al., 2026) |
| Optimizer dominan | Adam pada hampir semua studi; satu studi memakai SGD (Bahari et al., 2026) |
| Learning rate khas | 1e-5 sampai 2e-5 (Bahari et al., 2026) |
| Batch size khas | 16 (Bahari et al., 2026) |
| Hyperparameter paling diperhatikan | Optimizer, learning rate, batch size (Bahari et al., 2026) |
| Metrik standar | Accuracy dan F1-Score (Bahari et al., 2026) |
| Faktor pemilihan setting | Kapasitas perangkat keras, ukuran korpus, jenis tugas, jenis model (Bahari et al., 2026) |
</experiment_design>

## Pola Konfigurasi yang Muncul

Tinjauan sistematis terhadap 62 artikel Scopus menemukan bahwa **Adam adalah optimizer yang dominan**, biasanya dipasangkan dengan learning rate 1e-5 hingga 2e-5 dan batch size 16 (Bahari et al., 2026). Hampir semua studi yang ditinjau memakai Adam, kecuali satu yang memilih SGD dengan alasan grid search dan random search (Bahari et al., 2026), dan Adam dilaporkan mengungguli SGD pada beberapa studi (Bahari et al., 2026). Tiga hyperparameter yang paling banyak dipertimbangkan adalah optimizer, learning rate, dan batch size (Bahari et al., 2026).

Namun, angka "khas" itu bukan resep universal. Penulis tinjauan menekankan bahwa pemilihan setting harus mempertimbangkan kapasitas perangkat keras, ukuran dataset, jenis tugas NLP, dan jenis model yang dikembangkan (Bahari et al., 2026), serta menyarankan penetapan tujuan optimasi sebelum memilih konfigurasi (Bahari et al., 2026).

## Strategi Pencarian: Dari Manual hingga Metaheuristik

**Table 2.** Comparison of Bert Hyperparameter Model (Irmawan et al., 2024)

*How to read: Setiap baris adalah satu kombinasi learning rate dan jumlah epoch yang diuji pada IndoBERT; kolom skor menunjukkan kinerja validasi untuk kombinasi tersebut, dan nilai tertinggi menandai konfigurasi terbaik.*

Pendekatan paling sederhana adalah **tuning manual dan grid search**, tetapi keduanya lemah pada ruang hyperparameter BERT yang berdimensi tinggi. Pada benchmark Sentiment140, SSA-BERT mencapai akurasi 96,4%, jauh di atas manual tuning (65,0%), grid search (69,5%), dan random search (72,0%) (El-Demerdash & Hamid, 2025). Penulisnya menegaskan bahwa interaksi rumit antar hyperparameter—learning rate, batch size, dropout, attention heads—membuat optimasi manual sulit (El-Demerdash & Hamid, 2025).

Pendekatan probabilistik juga dipakai. Pada klasifikasi sentimen finansial, grid search dihindari karena ledakan kombinatorial, lalu Bayesian optimization via Optuna dijalankan 100 trial per model dengan early stopping dan pruning (Nasiopoulos et al., 2025). Ruang pencariannya mencakup batch size 4–64, learning rate 5e-6 sampai 1e-4, epoch 2–10, Adam versus AdamW, weight decay, warmup ratio, dan dropout (Nasiopoulos et al., 2025); konfigurasi terbaik mencapai akurasi validasi 0,8275 (Nasiopoulos et al., 2025). Bayesian optimization juga dipakai untuk memilih dropout, learning rate, dan hidden unit LSTM pada model BERT-LSTM-AM (Wicaksana et al., 2024).

## Bukti Spesifik pada Tugas ABSA

**Fig 5.** Results on the impact of training epochs and dropout value in post-trained BERT for ASC task (Karimi et al., 2020)

*How to read: Grafik memetakan jumlah epoch pada sumbu horizontal dan kinerja pada sumbu vertikal, dengan setiap kurva mewakili satu nilai dropout; arah ke atas menandakan kinerja lebih baik.*

Pada ABSA, tuning yang dilaporkan biasanya berupa **ablasi hyperparameter**, bukan pencarian otomatis. Studi ABSA untuk elisitasi kebutuhan perangkat lunak melakukan fine-tuning BERT dengan studi ablasi komprehensif untuk memperoleh hyperparameter terbaik, mencapai F1 rata-rata 0,83 untuk ACD dan 0,94 untuk ACP (Taj et al., 2025). Pada ABSA Arab, fine-tuning AraBERT lebih cocok untuk setting sumber daya rendah, dan lapisan downstream kustom meningkatkan hasil fine-tuning default (Bensoltane & Zaki, 2021).

Bukti dari BAT menunjukkan bahwa jumlah epoch optimal bergantung domain: peningkatan F1 restoran (+2,16) lebih besar daripada laptop (+0,81) karena dataset restoran membaik dengan pelatihan lebih lama, sementara laptop mencapai puncak pada epoch lebih awal (Karimi et al., 2020). Ukuran perturbasi juga berperan penting terhadap kinerja (Karimi et al., 2020). Pada ABSA yang dapat dijelaskan, RoBERTa yang di-fine-tune dengan hyperparameter optimal mencapai akurasi 89,16% pada MAMS/SemEval dan 97,62% pada Naver (Perikos & Diamantopoulos, 2024).

## Perbandingan Studi Tuning

| Studi | Domain/Tugas | Strategi Tuning | Konfigurasi Kunci | Hasil |
|---|---|---|---|---|
| Bahari *et al.* (2026) | Tinjauan ABSA-BERT | Sintesis 62 artikel | Adam, LR 1e-5–2e-5, batch 16 | Standar de facto (Bahari et al., 2026) |
| El-Demerdash & Abdel-Hamid (2025) | Sentiment140 | Metaheuristik SSA | Ruang multidimensi | Acc 96,4% (El-Demerdash & Hamid, 2025) |
| Nasiopoulos *et al.* (2025) | Finansial (FiQA/PhraseBank) | Bayesian (Optuna, 100 trial) | Batch 16, LR 4,99e-5, 3 epoch, Adam (Nasiopoulos et al., 2025) | Val. acc 0,8275 (Nasiopoulos et al., 2025) |
| Zaidan *et al.* (2024) | Ulasan MyTelkomsel | Uji LR dan epoch | LR 1e-6, 3 epoch, batch 16 | Acc 96% (Zaidan et al., 2024) |
| Irmawan *et al.* (2024) | Aplikasi travel Indonesia | Uji LR 2e-5–5e-5, epoch 1–5 | LR 5e-5, epoch 4, batch 32 | Acc 0,91; F1 0,74 (Irmawan et al., 2024) |
| Nugroho *et al.* (2021) | Ulasan aplikasi Indonesia | Tuning hyperparameter | LR 2e-5, batch 16, 25 epoch | Acc 84% (Nugroho et al., 2021) |
| Li *et al.* (2021) | Klasifikasi sentimen | Static + layer freezing | LR 2e-5, batch 32 | Akurasi naik setelah layer freezing (Li et al., 2021) |
| Liu (2025) | MRPC | Dua tahap: arsitektur lalu parameter | Batch size paling kritis | Val. accuracy meningkat (Liu, 2025) |

## Implikasi dan Titik Lemah

Temuan-temuan ini tidak sepenuhnya sepakat. Satu studi melaporkan bahwa **membekukan BERT dapat mengungguli fine-tuning penuh** untuk analisis sentimen, dengan penurunan waktu latih besar (Galal et al., 2024), sementara studi lain menemukan bahwa fine-tuning penuh plus peningkatan learning rate, penurunan batch size, dan penambahan epoch memberi perbaikan besar (Cs224n et al.). Batch size dan panjang sekuens juga dilaporkan memengaruhi akurasi secara signifikan, dengan konfigurasi terbaik pada batch 32 dan panjang 384 (Areshey & Mathkour, 2023).

Untuk tesis, celah yang paling jelas adalah **kelangkaan studi yang membandingkan strategi pencarian secara langsung pada tugas ABSA**, bukan pada klasifikasi sentimen umum. Sebagian besar bukti ABSA berasal dari ablasi manual (Taj et al., 2025), sedangkan bukti metaheuristik dan Bayesian berasal dari dataset non-ABSA (El-Demerdash & Hamid, 2025; Nasiopoulos et al., 2025). Selain itu, akurasi tinggi tidak selalu diikuti F1 yang sebanding ketika data tidak seimbang (Irmawan et al., 2024), sehingga pelaporan Macro-F1 perlu dijadikan syarat.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Areshey, A., & Mathkour, H. (2023). Transfer Learning for Sentiment Classification Using Bidirectional Encoder Representations from Transformers (BERT) Model. *Sensors (Basel, Switzerland), 23*. https://doi.org/10.3390/s23115232
 
Bahari, A. R. S., Utomo, F., & Berlilana, B. (2026). Systematic Review of Hyperparameter Adjustment and Evaluation Metrics in Bert-Based Sentiment Analysis. *Journal La Multiapp*. https://doi.org/10.37899/journallamultiapp.v7i2.3046
 
Bensoltane, R., & Zaki, T. (2021). Towards Arabic aspect-based sentiment analysis: a transfer learning-based approach. *Social Network Analysis and Mining, 12*. https://doi.org/10.1007/s13278-021-00794-4
 
Cs224n, S., Project, D., Zhu, A., Torres, A., & Kraft, K. Implementing and Fine-Tuning BERT for Sentiment Classification, Paraphrase Detection and Semantic Similarity Analysis.
 
El-Demerdash, A. A., & Hamid, N. A. B. (2025). METAHEURISTIC-DRIVEN HYPERPARAMETER OPTIMIZATION FOR BERT IN SENTIMENT ANALYSIS. *Archives for Technical Sciences*. https://doi.org/10.70102/afts.2025.1833.176
 
Galal, O., Abdel-Gawad, A. H., & Farouk, M. (2024). Rethinking of BERT sentence embedding for text classification. *Neural Computing and Applications, 36*, 20245 - 20258. https://doi.org/10.1007/s00521-024-10212-3
 
Irmawan, O. A., Budi, I., Santoso, A., & Putra, P. K. (2024). Improving Sentiment Analysis and Topic Extraction in Indonesian Travel App Reviews Through BERT Fine-Tuning. *Jurnal Nasional Pendidikan Teknik Informatika (JANAPATI)*. https://doi.org/10.23887/janapati.v13i2.77028
 
Karimi, A., Rossi, L., Prati, A., & Full, K. (2020). Adversarial Training for Aspect-Based Sentiment Analysis with BERT. *2020 25th International Conference on Pattern Recognition (ICPR)*, 8797-8803. https://doi.org/10.1109/icpr48806.2021.9412167
 
Li, X.-J., Wang, X., & Liu, H. (2021). Research on fine-tuning strategy of sentiment analysis model based on BERT. *2021 International Conference on Communications, Information System and Computer Engineering (CISCE)*, 798-802. https://doi.org/10.1109/cisce52179.2021.9445882
 
Liu, L. (2025). Optimizing BERT Fine-tuning Strategies: A Hyperparameter and Architecture Analysis for Sentence Pair Classification. *Applied and Computational Engineering*. https://doi.org/10.54254/2755-2721/2025.ld27825
 
Nasiopoulos, D. K., Roumeliotis, K. I., Sakas, D., Toudas, K. S., & Reklitis, P. (2025). Financial Sentiment Analysis and Classification: A Comparative Study of Fine-Tuned Deep Learning Models. *International Journal of Financial Studies*. https://doi.org/10.3390/ijfs13020075
 
Nugroho, K. S., Sukmadewa, A. Y., Bachtiar, F., & Yudistira, N. (2021). BERT Fine-Tuning for Sentiment Analysis on Indonesian Mobile Apps Reviews. *Proceedings of the 6th International Conference on Sustainable Information Engineering and Technology*. https://doi.org/10.1145/3479645.3479679
 
Perikos, I., & Diamantopoulos, A. (2024). Explainable Aspect-Based Sentiment Analysis Using Transformer Models. *Big Data Cogn. Comput., 8*, 141. https://doi.org/10.3390/bdcc8110141
 
Taj, S., Daudpota, S., Imran, A., & Kastrati, Z. (2025). Aspect-based sentiment analysis for software requirements elicitation using fine-tuned Bidirectional Encoder Representations from Transformers and Explainable Artificial Intelligence. *Eng. Appl. Artif. Intell., 151*, 110632. https://doi.org/10.1016/j.engappai.2025.110632
 
Wicaksana, H. S., Kusumaningrum, R., & Gernowo, R. (2024). Determining community happiness index with transformers and attention-based deep learning. *IAES International Journal of Artificial Intelligence (IJ-AI)*. https://doi.org/10.11591/ijai.v13.i2.pp1753-1761
 
Zaidan, M. N., Sibaroni, Y., & Prasetyowati, S. S. (2024). LEARNING RATE AND EPOCH OPTIMIZATION IN THE FINE-TUNING PROCESS FOR INDOBERT’S PERFORMANCE ON SENTIMENT ANALYSIS OF MYTELKOMSEL APP REVIEWS. *Jurnal Teknik Informatika (Jutif)*. https://doi.org/10.52436/1.jutif.2024.5.5.2396
 
