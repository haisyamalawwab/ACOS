# **ACOS dan ACOSE** dalam Analisis Sentimen

## 1. Introduction

**ACOS mengekstraksi empat unsur—Aspect, Category, Opinion, dan Sentiment—sedangkan ACOSE menambahkan Emotion sebagai unsur kelima.** Perbedaannya adalah status terminologinya: ACOS memiliki definisi tugas dan tolok ukur yang jelas, sementara kumpulan literatur ini belum menetapkan ACOSE sebagai nama tugas standar. ACOS diperkenalkan untuk mengekstraksi seluruh kuadruplet dalam kalimat ulasan, termasuk aspek dan opini yang tidak dinyatakan secara eksplisit (Cai et al., 2021).

Empat unsur tersebut adalah **istilah aspek**, **kategori aspek**, **ungkapan opini**, dan **polaritas sentimen**. Tugasnya tidak berhenti pada menemukan unsur, tetapi juga memasangkan unsur yang benar menjadi struktur opini (Cai et al., 2021). Istilah *Aspect Sentiment Quad Prediction* atau ASQP merujuk pada struktur empat unsur yang sama, walaupun dataset dan konvensi representasinya perlu diperiksa sebelum membandingkan hasil (Zhou et al., 2023; Zhang et al., 2024).

Penambahan emosi bukan sekadar memperbanyak label polaritas. Sentimen, emosi, dan ungkapan opini merupakan dimensi yang berbeda dan perlu direpresentasikan secara terpisah (D'Aniello & Gaeta, 2022). Literatur terkait telah mengembangkan ekstraksi aspek–emosi serta pembelajaran bersama sentimen dan emosi per kategori, tetapi kedua pendekatan itu belum otomatis berarti ekstraksi lengkap lima unsur ACOSE (Schmidt et al., 2025; Chai et al., 2025).

Dengan demikian, pertanyaan utamanya adalah bagaimana kuadruplet ACOS dibentuk, bagaimana keberhasilannya diukur, dan sejauh mana penelitian emosi mendukung perluasannya.


**Figure 1:** Kesepakatan penelitian mengenai empat unsur terstruktur dalam ACOS

Literatur konsisten mengenai struktur empat unsur ACOS; ketidakpastian terutama menyangkut perluasan emosi dan konsistensi evaluasinya.

## 2. Methods

Penelusuran mencakup basis lebih dari 220 juta makalah penelitian di Consensus, yang mengintegrasikan Semantic Scholar, PubMed, dan sumber lainnya. Strategi penelusuran menggabungkan istilah ACOS, ASQP, ekstraksi kuadruplet, aspek dan opini implisit, serta analisis emosi berbasis aspek.

Penilaian relevansi memprioritaskan kesesuaian unsur keluaran, bukan hanya kemiripan nama tugas. Studi yang mengekstraksi aspek–emosi dibedakan dari studi yang memprediksi kategori–sentimen atau kuadruplet lengkap. Penelusuran sitasi digunakan untuk menghubungkan formulasi awal dengan pengembangan model dan dataset berikutnya. Bukti teks lengkap diprioritaskan apabila tersedia; temuan yang hanya tersedia melalui abstrak ditafsirkan sesuai keterbatasan rincian tersebut. Angka kinerja diperlakukan sebagai hasil dalam pengaturan masing-masing, bukan peringkat lintas studi.

| Retrieved | Eligible | Included |
|-----------|----------|----------|
| 6.3M | 225 | 50 | 

**Figure 2:** Alur seleksi literatur mengenai ACOS dan perluasan emosi

Pencarian menggabungkan terminologi tugas, penelusuran sitasi, pemeriksaan dataset, serta pembandingan struktur keluaran dan aturan evaluasi antarpublikasi.

## 3. Results

Hasil membedakan definisi struktur, perkembangan pendekatan ekstraksi, dan posisi emosi sebagai perluasan.

### 3.1 Key Papers

Cai dan kolega menyediakan definisi ACOS serta dataset yang mendukung aspek dan opini implisit (Cai et al., 2021). Zhang dan kolega merumuskan ASQP sebagai prediksi empat unsur sekaligus melalui pembangkitan parafrasa, sedangkan survei ABSA menempatkannya sebagai tugas gabungan yang lebih lengkap daripada ekstraksi pasangan atau triplet (Zhang et al., 2021; Zhang et al., 2022).

| Paper | Summary |
|---|---|
| (Cai et al., 2021) | Definisi ACOS dan dataset unsur implisit (Cai et al., 2021) |
| (Zhang et al., 2021) | Prediksi kuadruplet melalui pembangkitan parafrasa (Zhang et al., 2021) |
| (Schmidt et al., 2025) | Tolok ukur ekstraksi aspek dan emosi (Schmidt et al., 2025) |

**Figure 3:** Landasan kuadruplet ACOS dan penelitian emosi berbasis aspek

### 3.2 Struktur dan Dataset

Dalam ACOS, kategori berasal dari himpunan domain yang ditentukan, sedangkan sentimen biasanya positif, netral, atau negatif (Cai et al., 2021). Aspek atau opini yang tidak mempunyai rentang teks eksplisit direpresentasikan sebagai `NULL`, bukan kata yang diciptakan model (Cai et al., 2021).

| Dimensi | Restaurant-ACOS | Laptop-ACOS | Sumber |
|---|---|---|---|
| Kalimat | 2.286 | 4.076 | (Cai et al., 2021) |
| Kuadruplet | 3.658 | 5.758 | (Cai et al., 2021) |
| Kategori | 13 | 121 | (Cai et al., 2021) |
| Asal data | Perluasan SemEval Restaurant | Ulasan Amazon Laptop | (Cai et al., 2021) |

**Figure 4:** Perbandingan struktur dua dataset awal kuadruplet ACOS

Granularitas kategori memengaruhi pengaturan eksperimen: Laptop-L1 menggunakan 21 kategori tingkat atas, sehingga tidak identik dengan label hierarkis Laptop asli (Peper & Wang, 2022). Dataset ASQP yang lebih panjang dan padat memperlihatkan kelemahan baseline yang tidak terlihat pada sampel pendek (Zhou et al., 2023). Shoes-ACOSI memperluas struktur dengan lokalisasi opini implisit dalam paragraf, bukan dengan menambahkan emosi (Peper et al., 2024).

### 3.3 Pendekatan Ekstraksi

Pendekatan awal *extract-then-classify* mengekstraksi aspek–opini sebelum mengklasifikasikan kategori–sentimen (Cai et al., 2021). Model dua tahap lain menambahkan pengklasifikasi relasi untuk memvalidasi pasangan aspek–opini, termasuk pada ulasan produk berbahasa Mandarin (Zhang et al., 2022).

| Keluarga Model | Representasi atau Strategi | Tantangan yang Ditangani | Sumber |
|---|---|---|---|
| Generatif | BART dan pembelajaran kontrastif | Ketergantungan serta keragaman kuadruplet | (Xiong et al., 2023) |
| Penandaan grid | Relasi pasangan kata | Ekstraksi eksplisit dan implisit | (Zhu et al., 2023) |
| MRC multitugas | Enam subtugas berbasis pertanyaan | Pencocokan unsur dan klasifikasi | (Zhang et al., 2024) |
| Generatif paralel | Pointer dan variabel laten | Efisiensi serta unsur implisit | (Nie et al., 2024) |

**Figure 5:** Keluarga pendekatan pemodelan ekstraksi kuadruplet sentimen berbasis aspek

Pengembangan lain mencakup pemendekan urutan keluaran, variasi urutan templat, contoh negatif adaptif, dan pengurangan token keluaran yang keliru (Li et al., 2023; Hu et al., 2022; Xu et al., 2023; Hu et al., 2023). Model berbasis penalaran menambahkan strategi ekstraksi-lalu-penetapan dan pemilihan keluaran yang konsisten (Kim et al., 2024).

### 3.4 ACOSE dan Formulasi Berdekatan

Jika ACOSE digunakan untuk **Aspect–Category–Opinion–Sentiment–Emotion**, representasinya dapat ditulis sebagai \((a,c,o,s,e)\), tetapi harus dinyatakan sebagai definisi operasional, bukan diasumsikan sebagai standar literatur. Dasar konseptualnya adalah pemisahan polaritas dari keadaan afektif (D'Aniello & Gaeta, 2022).

EmoGRACE menggunakan 2.621 tweet dengan label anger, sadness, happiness, fear, dan none; F1 ekstraksi bersama aspek–emosi mencapai 46,9%, dibandingkan 70,1% untuk ekstraksi aspek saja (Schmidt et al., 2025). Penelitian ACSA berbantuan emosi menggunakan enam emosi Ekman dan penyempurnaan berbasis *Valence–Arousal–Dominance*, tetapi bukan ekstraksi lengkap rentang aspek dan opini (Chai et al., 2025).

Istilah “quintuple” juga tidak selalu berarti ACOSE: OACIS menambahkan *irrealis*, sementara formulasi klasik memakai entitas, aspek, sentimen, pemegang opini, dan waktu (Dey & Jenamani, 2024; , 2020). DiaASQ bahkan memakai target–aspect–opinion–sentiment, bukan kategori ACOS (Li et al., 2022).

### Results Timeline

Perkembangan literatur bergerak dari ekstraksi empat unsur menuju pemodelan implisit dan perluasan afektif.

- **Jan 2021**
  - 1 paper: (Cai et al., 2021)
- **Oct 2021**
  - 1 paper: (Zhang et al., 2021)
- **Jan 2022**
  - 1 paper: (D'Aniello & Gaeta, 2022)
- **Mar 2022**
  - 1 paper: (Zhang et al., 2022)
- **Apr 2022**
  - 1 paper: (Zhang et al., 2022)
- **Oct 2022**
  - 1 paper: (Hu et al., 2022)
- **Nov 2022**
  - 1 paper: (Peper & Wang, 2022)
- **Apr 2023**
  - 1 paper: (Xiong et al., 2023)
- **Jun 2023**
  - 3 papers: (Zhou et al., 2023; Li et al., 2023; Hu et al., 2023)
- **Jul 2023**
  - 1 paper: (Zhu et al., 2023)
- **Nov 2023**
  - 1 paper: (Xu et al., 2023)
- **Jan 2024**
  - 2 papers: (Zhang et al., 2024; Peper et al., 2024)
- **Mar 2024**
  - 1 paper: (Kim et al., 2024)
- **Apr 2024**
  - 1 paper: (Nie et al., 2024)
- **Jul 2024**
  - 1 paper: (Zhang et al., 2024)
- **Mar 2025**
  - 1 paper: (Schmidt et al., 2025)
- **Nov 2025**
  - 1 paper: (Chai et al., 2025)
**Figure 6:** Linimasa penelitian; penanda lebih besar menunjukkan lebih banyak sitasi

Perkembangan metode tidak menghapus perbedaan struktur tugas: ekstraksi entitas–aspek, misalnya, memisahkan target dan atribut alih-alih menambahkan kategori atau emosi (Dan et al., 2023).

### Top Contributors

Kontributor berikut menunjukkan visibilitas dalam korpus, bukan peringkat dampak seluruh bidang; urutannya mengikuti jumlah sitasi publikasi terkait yang tersedia.

| Type | Name | Papers |
|------|------|--------|
| Author | Wenxuan Zhang | (Zhang et al., 2023; Zhang et al., 2022; Zhang et al., 2021) |
| Author | Lidong Bing | (Zhang et al., 2023; Zhang et al., 2022; Zhang et al., 2021) |
| Author | Wai Lam | (Zhang et al., 2022; Zhang et al., 2021) |
| Journal | *Expert Systems with Applications* | (H. et al., 2019; Xu et al., 2025) |
| Journal | *IEEE Transactions on Knowledge and Data Engineering* | (Zhang et al., 2022) |
| Journal | *IEEE Transactions on Affective Computing* | (Nazir et al., 2020) |

**Figure 7:** Penulis dan jurnal yang menonjol dalam korpus penelitian

## 4. Discussion

Kekuatan bukti terletak pada kesepakatan definisi ACOS dan evaluasi gabungan seluruh unsur. Kuadruplet dinilai benar hanya jika keempat unsur beserta kombinasinya cocok persis dengan anotasi acuan (Cai et al., 2021; Lai et al., 2025). Karena itu, peningkatan klasifikasi sentimen saja tidak membuktikan keberhasilan ekstraksi kuadruplet: SetFitQuad melaporkan F1 0,532 untuk pencocokan parsial tetapi hanya 0,083 untuk pencocokan tepat (Chuang & Lin, 2025).

Klaim keunggulan model perlu dibaca secara lokal. GEN-SCL-NAT melaporkan peningkatan rata-rata F1 1,48%, sedangkan SG-ACOS melaporkan peningkatan absolut 3,52% dan 2,74% pada dua dataset; baseline dan pengaturannya berbeda (Peper & Wang, 2022; Li et al., 2023). Informasi jarak aspek–opini juga meningkatkan hasil dibandingkan baseline tertentu, tetapi bukan bukti bahwa satu arsitektur unggul universal (Li et al., 2023). Benchmark LLM menunjukkan bahwa tugas sentimen sederhana lebih mudah daripada prediksi informasi terstruktur, meskipun LLM mempunyai keuntungan dalam kondisi sedikit contoh (Zhang et al., 2023).

Validitas anotasi dan transfer domain tetap membatasi interpretasi. Dataset Laptop awal mencatat kesepakatan antar-anotator berupa F1 pencocokan kuadruplet 75,86%, menunjukkan bahwa anotasi sendiri tidak trivial (Cai et al., 2021). EmoGRACE mengaitkan keterbatasan generalisasi dengan ukuran data dan kompleksitas label emosi, sedangkan survei deteksi aspek menekankan portabilitas domain (Schmidt et al., 2025; Truşcǎ & Frasincar, 2022).

**Klaim Utama dan Dukungan**

| Claim | Evidence Strength | Reasoning | Papers |
|---|---|---|---|
| ACOS memiliki empat unsur terhubung | Evidence strength: Strong (9/10) | Definisi konsisten lintas formulasi | (Peper & Wang, 2022; Zhu et al., 2023) |
| Unsur implisit membutuhkan penanganan khusus | Evidence strength: Strong (8/10) | Terlihat pada benchmark dan survei | (Cai et al., 2021; Jia et al., 2026) |
| Pengayaan representasi meningkatkan hasil lokal | Evidence strength: Moderate (6/10) | Berbagai studi, pengaturan berbeda | (Zhang et al., 2024; Zhu et al., 2023) |
| Emosi melengkapi polaritas sentimen | Evidence strength: Moderate (5/10) | Dukungan konseptual dan studi awal | (Chai et al., 2025) |
| ACOSE sudah menjadi benchmark standar | Evidence strength: Weak (1/10) | Belum ditetapkan dalam korpus | (Schmidt et al., 2025; Chai et al., 2025) |

**Figure 8:** Kekuatan bukti untuk klaim ACOS dan perluasan emosi

## 5. Conclusion

ACOS dan ASQP menyediakan kerangka mapan untuk ekstraksi empat unsur opini. ACOSE masuk akal sebagai perluasan lima unsur, tetapi penggunaan istilah tersebut perlu disertai definisi label, aturan pengaitan emosi, dan evaluasi tersendiri.

### Research Gaps

Cakupan penelitian jauh lebih kuat pada kuadruplet ulasan daripada ekstraksi lengkap yang menambahkan emosi. Matriks berikut membedakan struktur keluaran dan keluarga pemodelan yang benar-benar muncul dalam korpus.

| | Pipeline | Penandaan Bersama | Generasi Terstruktur | Pembelajaran Kontrastif |
|---|---|---|---|---|
| Kuadruplet ACOS | 12 papers | 5 papers | 19 papers | 4 papers |
| Aspek Emosi | No papers | 2 papers | 2 papers | No papers |
| Kategori Sentimen Emosi | No papers | No papers | No papers | No papers |
| Opini Implisit ACOSI | 4 papers | 1 paper | 2 papers | No papers |
**Figure 9:** Cakupan struktur keluaran dan pendekatan ekstraksi dalam literatur

Kesenjangan terpenting adalah dataset yang menghubungkan kelima unsur secara konsisten; kelangkaan anotasi emosi sudah membatasi tugas aspek–emosi yang lebih sederhana (Schmidt et al., 2025). Opini implisit juga memerlukan kebijakan berbeda: Shoes-ACOSI melokalisasi bukti implisit, sedangkan ACOS awal menggunakan `NULL`, sehingga perluasan emosi tidak cukup dengan menambahkan kolom label (Peper et al., 2024; Cai et al., 2021). Untuk teks panjang, relasi satu-ke-banyak dan ekspresi multi-kata merupakan tantangan tambahan dalam pengaitan aspek–opini (Li et al., 2022).

### Open Research Questions

Prioritasnya adalah memperjelas anotasi dan menguji keluaran lengkap, bukan hanya akurasi tiap komponen. Perbedaan sentimen pada tingkat aspek dan pasangan aspek–opini juga perlu dijaga (Li et al., 2021).

| Pertanyaan | Why |
|---|---|
| **Bagaimana emosi sebaiknya ditautkan pada kuintupel ACOSE?** | Pengaitan perlu membedakan emosi per aspek dari sentimen pasangan aspek–opini agar keluaran tidak ambigu atau kehilangan konteks (Li et al., 2021). |
| **Bagaimana mengevaluasi kelima unsur secara bersama?** | Ketepatan komponen individual tidak menjamin ketepatan struktur lengkap, sebagaimana terlihat dari perbedaan besar antara pencocokan parsial dan tepat (Chuang & Lin, 2025). |
| **Apakah perluasan emosi tetap andal lintas domain?** | Kelangkaan anotasi dan keterbatasan generalisasi menuntut pengujian transfer, bukan mengandalkan keberhasilan pada satu dataset berlabel kecil saja (Truşcǎ & Frasincar, 2022; Schmidt et al., 2025). |

**Figure 10:** Pertanyaan terbuka untuk pengembangan ekstraksi lima unsur ACOSE

**Intinya: gunakan ACOS untuk tugas empat unsur yang mapan; gunakan ACOSE dengan definisi eksplisit sebagai perluasan yang masih perlu divalidasi.**
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
(2020). Aspect and Entity Extraction. *Sentiment Analysis*. https://doi.org/10.1017/9781108639286.007
 
D., Xu, J., Wang, Z., Cao, X.-Z., & Xian, Y. (2023). Entity-Aspect-Opinion-Sentiment Quadruple Extraction for Fine-grained Sentiment Analysis. *ArXiv, abs/2311.16678*. https://doi.org/10.48550/arxiv.2311.16678
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chai, Y., Xie, H., & Qin, S. (2025). Emotion-Enhanced Multi-Task Learning with LLMs for Aspect Category Sentiment Analysis. *ArXiv, abs/2511.19122*. https://doi.org/10.48550/arxiv.2511.19122
 
Chuang, H.-M., & Lin, J.-K. (2025). SetFitQuad: A Few-Shot Framework for Aspect Sentiment Quad Prediction With Sampling Strategies. *IEEE Access, 13*, 146204-146217. https://doi.org/10.1109/access.2025.3600351
 
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. *Artificial Intelligence Review, 55*, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
 
Dey, A., & Jenamani, M. (2024). Aspect based sentiment analysis of consumer reviews using unsupervised attention neural framework. *Appl. Soft Comput., 167*, 112259. https://doi.org/10.1016/j.asoc.2024.112259
 
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. *Expert Syst. Appl., 118*, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
 
Hu, M.-T., Wu, Y., Gao, H., Bai, Y.-H., & Zhao, S. (2022). Improving Aspect Sentiment Quad Prediction via Template-Order Data Augmentation. *ArXiv, abs/2210.10291*. https://doi.org/10.48550/arxiv.2210.10291
 
Hu, M.-T., Bai, Y.-H., Wu, Y., Zhang, Z., Zhang, L., Gao, H., Zhao, S., & Huang, M.-T. (2023). Uncertainty-Aware Unlikelihood Learning Improves Generative Aspect Sentiment Quad Prediction. 13481-13494. https://doi.org/10.48550/arxiv.2306.00418
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Kim, J., Heo, R., Seo, Y., Kang, S., Yeo, J., & Lee, D.-H. (2024). Self-Consistent Reasoning-based Aspect-Sentiment Quad Prediction with Extract-Then-Assign Strategy. *ArXiv, abs/2403.00354*. https://doi.org/10.18653/v1/2024.findings-acl.435
 
Lai, W., Xie, H.-R., Xu, G., Li, Q., & Qin, S. (2025). Listwise Preference Optimization with Element-wise Confusions for Aspect Sentiment Quad Prediction. *ArXiv, abs/2511.23184*. https://doi.org/10.48550/arxiv.2511.23184
 
Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191098
 
Li, B., Fei, H., Li, F., Wu, Y.-H., Zhang, J.-S., Wu, S.-Q., Li, J., Liu, Y., Liao, L.-Z., Chua, T.-S., & Ji, D.-H. (2022). DiaASQ : A Benchmark of Conversational Aspect-based Sentiment Quadruple Analysis. *ArXiv, abs/2211.05705*. https://doi.org/10.48550/arxiv.2211.05705
 
Li, J., Li, X.-Y., Du, Y.-J., Fan, Y., Chen, X.-L., & Huang, D. (2023). An Aspect-Category-Opinion-Sentiment Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. *Inf. Technol. Control., 52*, 445-456. https://doi.org/10.5755/j01.itc.52.2.32903
 
Li, Y., Lin, Y.-D., Lin, Y.-M., Chang, L., & Zhang, H. (2022). A span-sharing joint extraction framework for harvesting aspect sentiment triplets. *Knowl. Based Syst., 242*, 108366. https://doi.org/10.1016/j.knosys.2022.108366
 
Li, Y., Wang, F., Zhang, W., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). A More Fine-Grained Aspect-Sentiment-Opinion Triplet Extraction Task. *ArXiv, abs/2103.15255*. https://doi.org/10.3390/math11143165
 
Nazir, A., Rao, Y., Wu, L., & Sun, L. (2020). Issues and Challenges of Aspect-based Sentiment Analysis: A Comprehensive Survey. *IEEE Transactions on Affective Computing, 13*, 845-863. https://doi.org/10.1109/taffc.2020.2970399
 
Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. *Neurocomputing, 586*, 127642. https://doi.org/10.1016/j.neucom.2024.127642
 
Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. *ArXiv, abs/2211.07743*. https://doi.org/10.48550/arxiv.2211.07743
 
Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. https://doi.org/10.18653/v1/2024.findings-emnlp.907
 
Schmidt, S., Hanny, D., & Resch, B. (2025). EmoGRACE: aspect-based emotion analysis for social media data. *Social Network Analysis and Mining, 16*. https://doi.org/10.1007/s13278-026-01585-5
 
Truşcǎ, M. M., & Frasincar, F. (2022). Survey on aspect detection for aspect-based sentiment analysis. *Artificial Intelligence Review, 56*, 3797-3846. https://doi.org/10.1007/s10462-022-10252-y
 
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
 
Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. *ArXiv, abs/2311.03896*. https://doi.org/10.48550/arxiv.2311.03896
 
Xu, C., Wang, M., & Zhu, S. (2025). Tourism sentiment quadruple extraction via new neural ordinary differential equation networks with multitask learning and implicit sentiment enhancement. *Expert Syst. Appl., 270*, 126417. https://doi.org/10.1016/j.eswa.2025.126417
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, W., Deng, Y., Li, X., Yuan, Y., Bing, L., & Lam, W. (2021). Aspect Sentiment Quad Prediction as Paraphrase Generation. *ArXiv, abs/2110.00796*. https://doi.org/10.18653/v1/2021.emnlp-main.726
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhang, H., Chen, Z., Chen, B., Hu, B., Li, M., Yang, C., & Jiang, B. (2022). Complete quadruple extraction using a two-stage neural model for aspect-based sentiment analysis. *Neurocomputing, 492*, 452-463. https://doi.org/10.1016/j.neucom.2022.04.027
 
Zhang, H., Song, X.-W., Jia, X., Yang, C., Chen, Z., Chen, B., Jiang, B., Wang, Y., & Feng, R. (2024). Query-induced multi-task decomposition and enhanced learning for aspect-based sentiment quadruple prediction. *Eng. Appl. Artif. Intell., 133*, 108609. https://doi.org/10.1016/j.engappai.2024.108609
 
Zhang, W., Deng, Y., Liu, B.-Q., Pan, S. J., & Bing, L. (2023). Sentiment Analysis in the Era of Large Language Models: A Reality Check. 3881-3906. https://doi.org/10.48550/arxiv.2305.15005
 
Zhou, J., Yang, H., He, Y., Mou, H., & Yang, J. (2023). A Unified One-Step Solution for Aspect Sentiment Quad Prediction. *ArXiv, abs/2306.04152*. https://doi.org/10.48550/arxiv.2306.04152
 
Zhu, L., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. *World Wide Web, 26*, 3303 - 3320. https://doi.org/10.1007/s11280-023-01185-9
 
