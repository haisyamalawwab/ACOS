# Optimasi **UMAP–HDBSCAN** menyeimbangkan koherensi dan cakupan, tetapi pengurangan outlier tidak otomatis meningkatkan Cv atau NPMI.

Optimasi hiperparameter UMAP dan HDBSCAN dapat meningkatkan koherensi topik BERTopic pada ulasan pendek informal, tetapi pengaruhnya **tidak monoton dan bergantung pada korpus**. Pengurangan *outlier* terutama meningkatkan jumlah dokumen yang terwakili; peningkatan koherensi kata kunci merupakan hasil terpisah yang harus diukur, bukan diasumsikan (Janssens et al., 2025; Feng et al., 2025). Tiga hal perlu dibedakan: geometri hasil UMAP, selektivitas klaster HDBSCAN, dan representasi kata melalui c-TF-IDF.

## Pengaruh terhadap Koherensi

| Evidence Strength | Claim |
|---|---|
| Evidence strength: Moderate (7/10) | Optimasi klaster dapat meningkatkan koherensi, tetapi hubungan jumlah topik–NPMI tidak monoton dan konfigurasi terbaik berbeda menurut data (Janssens et al., 2025; Yan & Zhang, 2023). |
| Evidence strength: Moderate (6/10) | Pemisahan klaster yang lebih baik tidak menjamin NPMI lebih tinggi: optimasi dimensi UMAP sendiri menghasilkan NPMI **0.1627**, dibanding baseline **0.1882** (Feng et al., 2025). |
| Evidence strength: Weak (3/10) | c-TF-IDF dapat mengurangi outlier hampir menjadi nol, tetapi bukti peningkatan **Cv/NPMI yang terisolasi** dari strategi tersebut masih terbatas (Medvecki et al., 2024). |

**Figure 1:** Kekuatan bukti pengaruh optimasi terhadap koherensi dan cakupan

BERTopic memisahkan pengelompokan dokumen dari pembentukan representasi topik: embedding dikelompokkan terlebih dahulu, kemudian c-TF-IDF mengekstraksi kata representatif (Grootendorst, 2022). Karena itu, perubahan penempatan dokumen dan perubahan koherensi kata bukan ukuran yang identik.

Pembedaan ini penting pada teks informal yang singkat, jarang, dan berdensitas rendah, sebagaimana dirangkum dalam tinjauan pemodelan topik teks pendek (Murshed et al., 2022). Dalam ulasan pelanggan, BERTopic menghasilkan koherensi di atas 0.56 pada dua dataset, tetapi variasi parameter yang diuji dalam penelitian tersebut hanya berdampak terbatas terhadap koherensi (Krishnan, 2023). Jadi, keunggulan BERTopic terhadap model lain tidak dengan sendirinya membuktikan besarnya manfaat penyetelan setiap komponennya.

## Optimasi Dimensi UMAP

| Bukti | Hasil | Implikasi |
|---|---|---|
| Tweet kesehatan remaja | Silhouette −0.6309 pada 2 dimensi, maksimum 0.6180 pada 13 | Dimensi sangat rendah merusak pemisahan (Feng et al., 2025) |
| Ablasi UMAP adaptif | NPMI 0.1882 → 0.1627 | Optimasi silhouette tidak mengoptimalkan NPMI (Feng et al., 2025) |
| Pipeline klaster dokumen | Sedikitnya 15 dimensi memberi dasar yang baik | Hasil berbeda menurut korpus (Eklund et al., 2023) |
| Deskripsi berita pendek | Tanpa UMAP, Cv 0.582 → 0.521 | Keberadaan UMAP membantu pada dataset tersebut (Meng, 2025) |

**Figure 2:** Hasil optimasi UMAP dan perbedaan antara ukuran kualitas

Bukti paling rinci menunjukkan bahwa pemilihan `n_components` perlu mengikuti struktur data, bukan kebutuhan visualisasi. Pada BERTopic_Teen, silhouette meningkat hingga 13 dimensi, kemudian menurun pada beberapa dimensi yang lebih tinggi; hasil tersebut menunjukkan titik kompromi, bukan aturan “semakin banyak dimensi semakin baik” (Feng et al., 2025). Namun, ablasi yang memilih dimensi berdasarkan silhouette justru menurunkan NPMI, sehingga hasil geometri yang baik tidak cukup untuk menyimpulkan kata-kata topiknya lebih koheren (Feng et al., 2025).

Penelitian konfigurasi pipeline lain menemukan penyetelan UMAP hanya sedikit mengubah kinerja keseluruhan dan menyarankan perhatian pada efisiensi waktu (Eklund et al., 2023). Bukti ini membatasi klaim bahwa pencarian hiperparameter UMAP yang luas selalu menghasilkan peningkatan besar. Sebaliknya, keberadaan reduksi dimensi tetap dapat berguna: ablasi berita pendek menunjukkan penurunan koherensi ketika UMAP dihapus, tetapi itu bukan eksperimen sensitivitas parameter pada ulasan informal (Meng, 2025).

Untuk `n_neighbors` dan `min_dist`, bukti numerik yang langsung mengisolasi perubahan Cv/NPMI pada ulasan masih lebih sedikit. Pada transkrip panggilan darurat, pengujian iteratif memilih lingkungan 4 tetangga dan `min_dist=0.005`, tetapi konfigurasi itu dioptimalkan untuk konteks yang berbeda dan proses pemilihannya tidak deterministik (Flores Sanchez et al., 2026). Nilai tersebut bukan rekomendasi universal untuk ulasan game atau pelanggan.

## Selektivitas Klaster HDBSCAN

| `min_cluster_size` | Jumlah Topik | Outlier |
|---|---:|---:|
| 30 | 325 | 6.67% |
| 50 | 175 | 14.01% |
| 100 | 50 | 27.43% |
| 200 | 36 | 39.63% |
| 300 | 23 | 45.50% |

Seluruh nilai berasal dari eksperimen sensitivitas BERTopic_Teen (Feng et al., 2025).

**Figure 3:** Perubahan granularitas topik dan outlier akibat ukuran klaster

Menaikkan `min_cluster_size` mengurangi fragmentasi, tetapi dapat mengecualikan lebih banyak dokumen. Dalam eksperimen tersebut, ukuran kecil menghasilkan banyak topik yang kurang koheren atau sulit ditafsirkan, sedangkan ukuran besar menghasilkan lebih sedikit topik dengan lebih banyak outlier (Feng et al., 2025). Nilai 100 dipilih sebagai kompromi pada korpus itu, bukan sebagai optimum yang berlaku lintas dataset (Feng et al., 2025).

Bukti lintas dataset, termasuk Yelp, menunjukkan tidak ada hubungan monoton antara jumlah topik dan NPMI (Janssens et al., 2025). Pemilihan `leaf` menghasilkan lebih banyak outlier daripada `eom`, tetapi tidak memberikan perbedaan koherensi yang konsisten (Janssens et al., 2025). Pengecualian dokumen juga mengubah bahan untuk menghitung c-TF-IDF dan kata-kata topik akhirnya (Janssens et al., 2025).

Optimasi `min_cluster_size` berbasis silhouette meningkatkan koherensi rata-rata 12.24% dalam tiga dataset berita, tetapi penelitian tersebut hanya mengoptimalkan parameter itu dan menggunakan teks berita panjang (Yan & Zhang, 2023). Untuk `min_samples`, literatur menunjukkan sensitivitas jumlah dan stabilitas topik, tetapi kutipan yang tersedia tidak memberikan besaran peningkatan Cv/NPMI yang terisolasi (Ajinaja et al., 2025).

Alternatif tanpa penolakan dokumen juga relevan sebagai pembanding. Pada respons evaluasi kuliah pendek, penggantian HDBSCAN dengan k-means menghasilkan kinerja serupa tanpa outlier (De Groot et al., 2022). Pada umpan balik pasien yang kecil, BERTopic mencapai Cv 0.46, sedangkan pendekatan BERT–k-means mencapai 0.53 (Islam et al., 2025). Ini menunjukkan bahwa mempertahankan HDBSCAN bukan prasyarat koherensi terbaik.

## c-TF-IDF dan Pemulihan Outlier

| Strategi | Temuan Terukur | Batas Kesimpulan |
|---|---|---|
| Reassignment c-TF-IDF | Outlier hampir nol | Tidak tersedia ablasi perubahan Cv/NPMI (Medvecki et al., 2024) |
| Reassignment probabilistik | Outlier 27.43% → 5.23% | NPMI sendiri tetap 0.1882 (Feng et al., 2025) |
| Penekanan kata generik | NPMI 0.1882 → 0.2013 | Perubahan pembobotan, bukan reassignment (Feng et al., 2025) |
| Seluruh modul digabung | NPMI 0.1882 → 0.2184 | Manfaat gabungan, bukan efek tunggal (Feng et al., 2025) |
| Gibbs-BERTopic pada ulasan | Koherensi meningkat hampir 20% | Penyempurnaan distribusi multilangkah (Zhu & Liu, 2025) |

**Figure 4:** Perbedaan efek pemulihan dokumen dan pembobotan kata topik

**Reassignment outlier berbeda dari pengurangan jumlah topik dan pembobotan ulang kata.** Pada tweet Serbia, fungsi `reduce_outliers` dengan strategi c-TF-IDF mengurangi outlier hampir menjadi nol; hasil ini membuktikan peningkatan cakupan, tetapi kutipan tersebut tidak menyatakan selisih Cv atau NPMI sebelum–sesudah (Medvecki et al., 2024). Pada ulasan Steam, strategi yang digunakan justru berbasis probabilitas HDBSCAN, disertai penggabungan topik, sehingga hasilnya tidak dapat dianggap sebagai ablasi c-TF-IDF (Tong et al., 2025).

Ablasi BERTopic_Teen memperjelas perbedaannya: reassignment sendiri tidak mengubah NPMI atau keragaman topik, meskipun retensi dokumen membaik (Feng et al., 2025). Penekanan kata generik sendiri meningkatkan NPMI, sementara seluruh modul bersama-sama menghasilkan peningkatan sekitar 16% (Feng et al., 2025). Dengan demikian, manfaat gabungan tidak boleh seluruhnya diatribusikan kepada penanganan outlier.

Pembobotan representasi juga tidak selalu memberikan hasil sama. Pada Twitter Kongres AS, `reduce_frequent_words` meningkatkan koherensi rata-rata 0.75 menjadi 0.79, tetapi menurunkan stabilitas; BM25 tidak memperbaiki kinerja secara jelas (Mendonça & Figueira, 2024). Sebaliknya, integrasi IndoBERT, BM25, dan BIRCH menghasilkan koherensi lebih tinggi pada X, Google Reviews, dan YouTube, tetapi perubahan beberapa komponen sekaligus membatasi atribusi efek (Muhajir et al., 2025).

## Interpretasi Cv dan NPMI

| Konteks | Hasil Koherensi | Pelajaran |
|---|---|---|
| Ulasan Steam | NPMI BERTopic 0.093 | Cv justru mengunggulkan NMF–BoW (Tong et al., 2025) |
| Ulasan film Tiongkok | Cv 0.4747; NPMI 0.0394 | Benchmark pipeline, bukan efek tuning terisolasi (Lyu et al., 2026) |
| Komentar kesehatan Tiongkok | Cv 0.4211; NPMI −0.0908 | Cv positif tidak menjamin NPMI positif (Xiao et al., 2026) |
| Teks pendek Hindi | Peringkat Cv dan NPMI berbeda | Jumlah topik mengubah kesimpulan metrik (Mutsaddi et al., 2025) |
| Ujaran kelompok fokus | Koherensi dan stabilitas berkonflik | Pemilihan perlu beberapa kriteria (Arfaoui et al., 2025) |

**Figure 5:** Ketidaksepakatan metrik koherensi pada berbagai korpus teks pendek

Cv dan NPMI harus dilaporkan bersama karena keduanya dapat menghasilkan peringkat model berbeda, bahkan pada data ulasan game yang sama (Tong et al., 2025). Pada teks Arab, model embedding terbaik menurut Cv juga berbeda dari yang terbaik menurut NPMI, menunjukkan bahwa pilihan representasi dapat mengubah kesimpulan evaluasi (Dawood & Mahmood, 2026). Bahkan korelasi metrik otomatis dengan penilaian manusia tergolong rendah pada korpus media sosial psikologis (Couto et al., 2026).

Evaluasi yang dapat dibandingkan perlu mempertahankan prosedur koherensi yang konsisten. Salah satu kerangka menggunakan teks tertokenisasi, jendela geser tetap, penyaringan kosakata, dan aturan pengecualian topik yang kekurangan kata valid (Demir & Saran, 2026). Stabilitas juga perlu diperiksa lintas pengulangan, karena hasil BERTopic pada ulasan game bersifat stokastik (Tong et al., 2025).

Memaksa topik menjadi sangat sedikit bukan solusi otomatis: pada tweet pelanggan bank, penetapan 10 topik dan 20 istilah menurunkan koherensi pipeline UMAP–HDBSCAN dari sekitar 0.67 menjadi 0.54 (Ogunleye et al., 2023). Optimasi metrik geometris pun dapat memilih hanya dua klaster besar yang sulit dikenali sebagai topik bermakna (Schäfer et al., 2024). Karena itu, koherensi perlu dibaca bersama cakupan, granularitas, stabilitas, dan pemeriksaan ulasan representatif.

**Pergeseran terpenting ialah dari memaksimalkan satu skor menuju menyeimbangkan koherensi dan keterwakilan ulasan. Pertanyaan terbuka terbesar adalah besarnya perubahan Cv/NPMI yang benar-benar disebabkan reassignment c-TF-IDF saja, dengan komponen lain dan prosedur evaluasi tetap sama.**
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Ajinaja, M., Fakoya, J., Ogunwale, Y., Omoniyi, J. K., Ibiyomi, M. A., Abiona, A., & Akinola, D. E. (2025). A Comparative Evaluation of Probabilistic and Transformer-Based Topic Models Across Diverse and Multilingual Text Corpora. *Neural Processing Letters, 58*. https://doi.org/10.1007/s11063-025-11820-3
 
Arfaoui, H., Hergli, M. I., Benzina, B., & BenMiled, S. (2025). A Reproducible Framework for Neural Topic Modeling in Focus Group Analysis. *ArXiv, abs/2511.18843*. https://doi.org/10.48550/arxiv.2511.18843
 
Couto, M., Parapar, J., & Losada, D. E. (2026). Exploiting topic analysis models to explore psychological dimensions in social media data. *Scientific Reports, 16*. https://doi.org/10.1038/s41598-026-36339-y
 
Dawood, N., & Mahmood, S. (2026). A Hybrid BERTopic–NAMAA Framework for Arabic News Topic Modeling, Classification, and Evaluation. *International Journal of Natural-Applied Sciences  and Engineering*. https://doi.org/10.22399/ijnasen.38
 
De Groot, M., Aliannejadi, M., & Haas, M. (2022). Experiments on Generalizability of BERTopic on Multi-Domain Short Text. *ArXiv, abs/2212.08459*. https://doi.org/10.48550/arxiv.2212.08459
 
Demir, O., & Saran, M. (2026). An Uncertainty-Gated Neuro-Symbolic Framework for High-Coverage Topic Modeling and Trend Analysis in Scholarly Corpora With LLM Assistance. *IEEE Access, 14*, 66445-66464. https://doi.org/10.1109/access.2026.3687277
 
Eklund, A., Forsman, M., & Drewes, F. (2023). An Empirical Configuration Study of a Common Document Clustering Pipeline. *Northern European Journal of Language Technology*. https://doi.org/10.3384/nejlt.2000-1533.2023.4396
 
Feng, Y.-Q., Chen, Z., Zhang, Y., Huang, W., Zhang, X.-M., & He, S. (2025). BERTopic_Teen: a multi-module optimization approach for short text topic modeling in adolescent health. *Frontiers in Public Health, 13*. https://doi.org/10.3389/fpubh.2025.1608241
 
Flores Sanchez, J. G., Orellana, M., García-Montero, P. S., & Zambrano-Martinez, J. L. (2026). AI-Driven Hierarchical Taxonomy Generation from Emergency Call Transcripts. *J. Braz. Comput. Soc., 32*, 472-483. https://doi.org/10.5753/jbcs.2026.6635
 
Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. *ArXiv, abs/2203.05794*. https://doi.org/10.48550/arxiv.2203.05794
 
Islam, K. S. M., Karri, R. T., Vegesna, S., Wu, J., & Madiraju, P. (2025). Contextual Embedding-based Clustering to Identify Topics for Healthcare Service Improvement. *2025 IEEE 49th Annual Computers, Software, and Applications Conference (COMPSAC)*, 794-799. https://doi.org/10.1109/compsac65507.2025.00106
 
Janssens, W., Bogaert, M., & Van Den Poel, D. (2025). A Comparative Analysis of Topic Reduction Techniques for BERTopic. *IEEE Access, 13*, 204087-204103. https://doi.org/10.1109/access.2025.3638956
 
Krishnan, A. (2023). Exploring the Power of Topic Modeling Techniques in Analyzing Customer Reviews: A Comparative Analysis. *ArXiv, abs/2308.11520*. https://doi.org/10.48550/arxiv.2308.11520
 
Lyu, Y., Xiao, L.-Y., Luo, D.-S., & Wang, H.-J. (2026). BERTopic-Enhanced Joint Topic-Sentiment Analysis of Chinese Short Texts: A Comparative Computational Framework. *Proceedings of the 3rd International Conference on Machine Intelligence and Digital Applications*. https://doi.org/10.1145/3801438.3805833
 
Medvecki, D., Bašaragin, B., Ljajić, A., & Milošević, N. (2024). Multilingual transformer and BERTopic for short text topic modeling: The case of Serbian. *ArXiv, abs/2402.03067*. https://doi.org/10.1007/978-3-031-50755-7_16
 
Mendonça, M., & Figueira, Á. (2024). Topic Extraction: BERTopic's Insight into the 117th Congress's Twitterverse. *Informatics, 11*, 8. https://doi.org/10.3390/informatics11010008
 
Meng, W. (2025). Evaluating Topic Modeling Approaches for News Analysis. *Proceedings of the 2025 International Conference on Generative Artificial Intelligence for Business*. https://doi.org/10.1145/3766918.3766974
 
Muhajir, M., Gunardi, G., Danardono, D., & Rosadi, D. (2025). Integrating IndoBERT and balanced iterative reducing and clustering using hierarchies of BERTopic in Indonesian short text. *IAES International Journal of Artificial Intelligence (IJ-AI)*. https://doi.org/10.11591/ijai.v14.i5.pp4192-4201
 
Murshed, B. A. H., Mallappa, S., Abawajy, J., Saif, M. A. N., Al-Ariki, H. D. E., & Abdulwahab, H. M. (2022). Short text topic modelling approaches in the context of big data: taxonomy, survey, and analysis. *Artificial Intelligence Review, 56*, 5133 - 5260. https://doi.org/10.1007/s10462-022-10254-w
 
Mutsaddi, A., Jamkhande, A., Thakre, A., & Haribhakta, Y. (2025). BERTopic for Topic Modeling of Hindi Short Texts: A Comparative Study. *ArXiv, abs/2501.03843*. https://doi.org/10.48550/arxiv.2501.03843
 
Ogunleye, B., Maswera, T., Hirsch, L., Gaudoin, J., & Brunsdon, T. (2023). Comparison of Topic Modelling Approaches in the Banking Context. *ArXiv, abs/2402.03176*. https://doi.org/10.3390/app13020797
 
Schäfer, K., Choi, J.-E., Vogel, I., & Steinebach, M. (2024). Unveiling the Potential of BERTopic for Multilingual Fake News Analysis - Use Case: Covid-19. *ArXiv, abs/2407.08417*. https://doi.org/10.48550/arxiv.2407.08417
 
Tong, X., Willcock, I., & Sun, Y. (2025). Unraveling Player's Insights: A Comparative Analysis of Topic Modeling Techniques on Game Reviews and Video Game Developers' Perspectives. *IEEE Transactions on Games, 17*, 167-180. https://doi.org/10.1109/tg.2024.3411154
 
Xiao, L.-Y., Lyu, Y., Jiang, H.-Y., & Shi, Y.-L. (2026). BERTopic-Enhanced Topic Modeling for Social Media Health Discourse Analysis. *Proceedings of the 3rd International Conference on Machine Intelligence and Digital Applications*. https://doi.org/10.1145/3801438.3801481
 
Yan, H., & Zhang, Y. (2023). An optimized BERTopic framework based on cluster silhouette for improving topic coherence. *Proceedings of the 4th International Conference on Artificial Intelligence and Computer Engineering*. https://doi.org/10.1145/3652628.3652721
 
Zhu, Y., & Liu, Y. (2025). Gibbs-BERTopic: A Hybrid Approach for Short Text Topic Modeling. *IEEE Access, 13*, 49162-49173. https://doi.org/10.1109/access.2025.3552221
 
