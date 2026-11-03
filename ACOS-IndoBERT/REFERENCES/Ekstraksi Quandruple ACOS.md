# Ekstraksi **Kuadruplet ACOS** dalam Analisis Sentimen

## 1. Introduction

**Ekstraksi tuple ACOS mengidentifikasi dan menghubungkan empat unsur: aspek, kategori aspek, ungkapan opini, dan polaritas sentimen.** Tugas ini menghasilkan sekumpulan kuadruplet \((a,c,o,s)\) dari sebuah teks, termasuk ketika aspek atau opininya tidak disebutkan secara eksplisit (Cai et al., 2021). ACOS bukan sekadar menemukan empat label secara terpisah: model harus memasangkan unsur-unsur tersebut menjadi struktur opini yang benar (Cai et al., 2021).

Sebagai contoh dari dataset awal, kalimat “Looks nice, and the surface is smooth, but certain apps take seconds to respond” memuat kuadruplet `surface–Design–smooth–Positive`, `NULL–Design–nice–Positive`, dan `apps–Software–NULL–Negative` (Cai et al., 2021). Nilai `NULL` menandai aspek atau opini yang tidak mempunyai rentang teks eksplisit; kategori dan polaritas tetap menyampaikan sasaran serta orientasi penilaiannya (Cai et al., 2021).

Istilah **Aspect Sentiment Quad Prediction—ASQP** sering digunakan untuk struktur empat unsur yang sama (Zhou et al., 2023). Namun, benchmark awalnya tidak identik: ACOS mendukung opini implisit, sedangkan dataset ASQP awal membuang kuadruplet dengan opini implisit (Qin & Lv, 2024; Zhang et al., 2021). Perbedaan ini menentukan apakah hasil dua model layak dibandingkan langsung.

Kepentingan ilmiahnya terletak pada pengaitan unsur: survei ABSA membedakan ekstraksi aspek dan opini tanpa relasi dari ekstraksi pasangan yang benar-benar menghubungkan keduanya (Zhang et al., 2022). Karena itu, keberhasilan ACOS harus dinilai pada struktur lengkap, bukan hanya ketepatan klasifikasi sentimen.


**Figure 1:** Bukti pemodelan terpadu untuk mengurangi propagasi kesalahan

Perbandingan awal mendukung pemodelan terpadu dibandingkan pipeline yang diuji, tetapi tidak menetapkan satu arsitektur terbaik untuk seluruh benchmark (Zhang et al., 2021; Cai et al., 2021).

## 2. Methods

Penelusuran dilakukan pada basis lebih dari 220 juta makalah penelitian di Consensus, yang mencakup Semantic Scholar, PubMed, dan sumber lainnya. Istilah pencarian menggabungkan ACOS, ASQP, ekstraksi kuadruplet, aspek dan opini implisit, penandaan terstruktur, serta pembangkitan teks.

Seleksi menekankan kesesuaian struktur keluaran, cakupan unsur implisit, dataset, dan aturan evaluasi. Penelusuran sitasi menghubungkan publikasi pendiri dengan pengembangan berikutnya. Teks lengkap diprioritaskan untuk memeriksa definisi tugas dan rincian eksperimen; bukti yang tersedia hanya melalui abstrak dipertahankan dengan batasan tersebut. Perbandingan kinerja dibatasi pada pengaturan yang sepadan, terutama granularitas kategori dan pencocokan tepat.

| Retrieved | Eligible | Included |
|-----------|----------|----------|
| 50.2K | 200 | 50 | 

**Figure 2:** Alur seleksi literatur ekstraksi kuadruplet sentimen ACOS

Strategi menggabungkan pencarian terminologi, penelusuran sitasi, pemeriksaan benchmark, serta evaluasi keterbandingan hasil ekstraksi eksplisit dan implisit.

## 3. Results

Literatur mencakup formulasi tugas, pengembangan model, dan pengujian pada kondisi anotasi serta domain yang berbeda (Zhang et al., 2024).

### 3.1 Key Papers

Cai, Xia, dan Yu memperkenalkan ACOS beserta Restaurant-ACOS dan Laptop-ACOS untuk mendukung unsur implisit (Cai et al., 2021). Zhang dan kolega mengembangkan formulasi ASQP sebagai pembangkitan parafrasa, sementara survei berikutnya menyatukan terminologi dan taksonomi pendekatannya (Zhang et al., 2021; Zhang et al., 2024).

**Landasan Penelitian ACOS**

| Paper | Summary |
|---|---|
| (Cai et al., 2021) | Mendefinisikan tugas dan benchmark unsur implisit (Cai et al., 2021) |
| (Zhang et al., 2021) | Mengubah prediksi kuadruplet menjadi parafrasa (Zhang et al., 2021) |
| (Zhang et al., 2024) | Menyintesis pendekatan model bahasa untuk ACOS (Zhang et al., 2024) |

**Figure 3:** Publikasi landasan formulasi dan pemodelan kuadruplet ACOS

### 3.2 Struktur dan Benchmark

Aspek merupakan sasaran penilaian, kategori merupakan kelas domain yang telah ditentukan, opini merupakan ungkapan subjektif, dan sentimen biasanya positif, netral, atau negatif (Cai et al., 2021; Zhu et al., 2023). Bentuk tuple yang lebih sederhana tetap berbeda: ASTE menghasilkan aspek–opini–sentimen, sedangkan TASD menghasilkan aspek–kategori–sentimen (Zhang et al., 2021; Mao et al., 2022).

**Perbandingan Benchmark Awal**

| Dimensi | Restaurant-ACOS | Laptop-ACOS | Bukti |
|---|---|---|---|
| Kalimat | 2.286 | 4.076 | (Cai et al., 2021) |
| Kuadruplet | 3.658 | 5.758 | (Cai et al., 2021) |
| Kategori | 13 | 121 | (Cai et al., 2021) |
| Sumber | Perluasan SemEval Restaurant | Ulasan Amazon Laptop | (Cai et al., 2021) |

**Figure 4:** Ukuran dan struktur dua benchmark awal ACOS

Laptop-L1 menggunakan hanya 21 kategori tingkat atas, sehingga hasilnya tidak identik dengan pengaturan Laptop lengkap (Peper & Wang, 2022). Dataset ASQP yang lebih panjang dan padat menyingkap kelemahan baseline pada jumlah opini yang lebih besar (Zhou et al., 2023). Shoes-ACOSI memperluas ACOS dengan lokalisasi opini implisit dalam paragraf, bukan sekadar mengganti nilai `NULL` (Peper et al., 2024).

### 3.3 Keluarga Model

Pipeline awal mengekstraksi pasangan aspek–opini sebelum memprediksi kategori–sentimen (Cai et al., 2021). Model dua tahap pada ulasan Mandarin menambahkan pengklasifikasi relasi untuk memvalidasi pasangan tersebut (Zhang et al., 2022). Pendekatan hibrida lain menggunakan MRC untuk ekstraksi pasangan dan pembangkitan teks untuk kategori serta polaritas (Lil et al., 2023).

**Pendekatan Ekstraksi Kuadruplet**

| Pendekatan | Representasi Utama | Kontribusi |
|---|---|---|
| Generatif | Parafrasa T5 atau BART | Memanfaatkan semantik label (Zhang et al., 2021; Hoang et al., 2022) |
| Grid tagging | Relasi pasangan token | Mengaitkan unsur secara bersama (Zhu et al., 2023) |
| MRC multitugas | Enam subtugas berbasis pertanyaan | Mengoptimalkan pengaitan dan klasifikasi (Zhang et al., 2024) |
| Generatif paralel | Pointer non-autoregresif | Mengurangi ketergantungan decoding berurutan (Nie et al., 2024) |
| Seq2Path | Jalur pohon independen | Merepresentasikan relasi satu-ke-banyak (Mao et al., 2022) |

**Figure 5:** Perbandingan representasi pada keluarga model ekstraksi ACOS

Pengembangan grid mencakup token khusus untuk aspek dan opini implisit serta koreksi hierarkis probabilitas antarpengklasifikasi (Su et al., 2025; Huang, 2023). One-ASQP mendukung aspek atau opini implisit secara terpisah, tetapi formulasi langsungnya belum menyelesaikan kasus ketika keduanya implisit (Zhou et al., 2023).

### 3.4 Penyempurnaan dan Hasil

Pembelajaran kontrastif meningkatkan representasi unsur implisit dalam GEN-SCL-NAT dan BART-CRN; iACOS menggunakan contoh negatif adaptif untuk melatih pengaitan serta klasifikasi bersama (Peper & Wang, 2022; Xiong et al., 2023; Xu et al., 2023). Variasi urutan templat, pemendekan keluaran, informasi jarak, dan penekanan token keliru merupakan strategi tambahan (Hu et al., 2022; Li et al., 2023; Hu et al., 2023).

Augmentasi kuadruplet-ke-teks, *self-training*, dan penyeimbangan kategori langka menargetkan kekurangan data (Wang et al., 2023; Yu et al., 2023; Yang et al., 2025). SCRAP dan Self-Inference Template menambahkan penalaran komposisi kuadruplet, sedangkan optimasi preferensi menargetkan konsistensi relasional (Kim et al., 2024; Qin & Lv, 2024; Lai et al., 2025). SimRP mengambil demonstrasi yang serupa secara sintaksis dan semantis (Jian et al., 2025). Peningkatan lokal juga dilaporkan untuk prompt sentimen implisit dan model multitugas pariwisata (Liu & Zhong, 2023; Xu et al., 2025).

### Results Timeline

Linimasa melacak perkembangan formulasi kuadruplet, pemodelan implisit, dan evaluasi transfer.

- **Jan 2021**
  - 1 paper: (Cai et al., 2021)
- **Oct 2021**
  - 1 paper: (Zhang et al., 2021)
- **Jan 2022**
  - 1 paper: (Mao et al., 2022)
- **Mar 2022**
  - 1 paper: (Zhang et al., 2022)
- **Apr 2022**
  - 1 paper: (Zhang et al., 2022)
- **Oct 2022**
  - 1 paper: (Hu et al., 2022)
- **Nov 2022**
  - 1 paper: (Peper & Wang, 2022)
- **Dec 2022**
  - 1 paper: (Hoang et al., 2022)
- **Apr 2023**
  - 1 paper: (Xiong et al., 2023)
- **Jun 2023**
  - 1 paper: (Zhou et al., 2023)
- **Jul 2023**
  - 2 papers: (Zhu et al., 2023; Huang, 2023)
- **Oct 2023**
  - 1 paper: (Lil et al., 2023)
- **Nov 2023**
  - 1 paper: (Xu et al., 2023)
- **Jan 2024**
  - 2 papers: (Zhang et al., 2024; Peper et al., 2024)
- **Apr 2024**
  - 1 paper: (Nie et al., 2024)
- **Jul 2024**
  - 2 papers: (Qin & Lv, 2024; Zhang et al., 2024)
- **Jul 2025**
  - 1 paper: (Su et al., 2025)
**Figure 6:** Linimasa penelitian; penanda lebih besar menunjukkan lebih banyak sitasi

Perkembangan bergerak dari benchmark empat unsur menuju pembangkitan terstruktur dan adaptasi lintas bahasa, termasuk UACOS untuk Urdu (Cai et al., 2021; Zhang et al., 2021; Ahmed et al., 2025).

### Top Contributors

Visibilitas berikut dibatasi pada korpus, dengan urutan berdasarkan sitasi publikasi terkait, bukan peringkat dampak seluruh bidang.

| Type | Name | Papers |
|------|------|--------|
| Author | Wenxuan Zhang | (Zhang et al., 2023; Zhang et al., 2022; Zhang et al., 2021) |
| Author | Lidong Bing | (Zhang et al., 2023; Zhang et al., 2022; Zhang et al., 2021) |
| Author | Wai Lam | (Zhang et al., 2022; Zhang et al., 2021) |
| Journal | *IEEE Transactions on Knowledge and Data Engineering* | (Zhang et al., 2022) |
| Journal | *Journal of King Saud University Computer and Information Sciences* | (Mao et al., 2024; Yusufu et al., 2026) |
| Journal | *Artificial Intelligence Review* | (Zhang et al., 2024; D'Aniello & Gaeta, 2022) |

**Figure 7:** Penulis dan jurnal yang menonjol dalam korpus

## 4. Discussion

**Pencocokan tepat merupakan ukuran utama yang paling relevan:** kuadruplet dihitung benar hanya apabila seluruh unsur dan kombinasinya sesuai anotasi acuan (Cai et al., 2021; Zhang et al., 2021; Lai et al., 2025). Baseline Extract-Classify-ACOS menghasilkan F1 44,61% pada Restaurant dan 35,80% pada Laptop, menunjukkan kesulitan tugas lengkap (Cai et al., 2021). SetFitQuad memperlihatkan mengapa metrik perlu diperiksa: F1 pencocokan parsialnya 0,532, tetapi pencocokan tepatnya hanya 0,083 (Chuang & Lin, 2025).

Validitas evaluasi juga bergantung pada anotasi. Kesepakatan antar-anotator Laptop awal mencapai F1 kuadruplet 75,86%, bukan kesesuaian sempurna (Cai et al., 2021). Kesalahan umum mencakup batas rentang opini, kategori semantis yang berdekatan, dan jumlah kuadruplet yang berlebihan atau kurang (Zhang et al., 2021; Qin & Lv, 2024). SimRP mengusulkan metrik fuzzy karena anotasi dan pencocokan tepat dapat meremehkan keluaran yang secara linguistik masuk akal (Jian et al., 2025).

Generalisasi masih lebih lemah daripada bukti dalam benchmark. Evaluasi LLM awal menemukan kelemahan pada tugas terstruktur, meskipun keuntungan muncul dalam kondisi sedikit contoh (Zhang et al., 2023). DPRA melaporkan stabilitas lebih baik pada domain tak terlihat, tetapi bukti yang tersedia di sini terbatas pada abstrak (Huang & Wang, 2025). Selain itu, DiaASQ, LASQ, dan EASQE menggunakan unsur target atau entitas yang berbeda dari kategori ACOS, sehingga tidak boleh diperlakukan sebagai benchmark identik (Li et al., 2022; Yusufu et al., 2026; Dan et al., 2023).

**Klaim dan Batas Bukti**

| Claim | Evidence Strength | Reasoning | Papers |
|---|---|---|---|
| ACOS memprediksi empat unsur terhubung | Evidence strength: Strong (9/10) | Definisi konsisten lintas publikasi | (Zhang et al., 2024; Mao et al., 2024) |
| Unsur implisit merupakan tantangan penting | Evidence strength: Strong (8/10) | Didukung benchmark dan survei | (Cai et al., 2021; Jia et al., 2026) |
| Pemodelan terpadu membantu dibandingkan pipeline tertentu | Evidence strength: Moderate (7/10) | Perbandingan eksperimental, bukan keunggulan universal | (Zhang et al., 2021; Zhang et al., 2024) |
| Perbaikan model meningkatkan skor benchmark lokal | Evidence strength: Moderate (6/10) | Dataset dan baseline berbeda | (Peper & Wang, 2022; Li et al., 2023) |
| Retrieval menjamin transfer lintas domain | Evidence strength: Weak (2/10) | Klaim kuat belum direplikasi luas | (Huang & Wang, 2025) |

**Figure 8:** Klaim utama dan kekuatan bukti penelitian ACOS

## 5. Conclusion

ACOS merupakan tugas ekstraksi **kuadruplet terhubung**, bukan sekadar klasifikasi sentimen per aspek. Bukti mendukung berbagai pendekatan terpadu, tetapi pemilihan model harus mempertimbangkan cakupan unsur implisit, skema kategori, dan F1 pencocokan tepat.

### Research Gaps

Kesenjangan utama muncul ketika ekstraksi lengkap dipindahkan dari ulasan berbahasa Inggris ke bahasa, domain, dan bentuk teks lain (Šmíd & Král, 2025; Jia et al., 2026).

| | Pipeline | Grid Tagging | Generasi Terstruktur | Retrieval Prompting |
|---|---|---|---|---|
| Restaurant | 5 papers | 4 papers | 17 papers | 2 papers |
| Laptop | 3 papers | 3 papers | 13 papers | No papers |
| Pariwisata | No papers | No papers | 1 paper | No papers |
| Sepatu | No papers | No papers | 1 paper | No papers |
| Urdu | No papers | 1 paper | No papers | No papers |
**Figure 9:** Cakupan domain dan keluarga pemodelan ekstraksi ACOS

Kelangkaan anotasi kuadruplet tetap membatasi pengembangan karena pelabelan empat unsur berbiaya tinggi (Wang et al., 2023; Yu et al., 2023). M-ABSA mencakup 21 bahasa dan tujuh domain, tetapi berfokus pada triplet tanpa opini; penerjemahan frasa opini panjang masih menimbulkan pergeseran makna (Wu et al., 2025). Pembelajaran lemah sudah menunjukkan transfer untuk ASTE, tetapi hasil tersebut belum membuktikan ekstraksi kategori ACOS lengkap (Chakraborty et al., 2025).

### Open Research Questions

Arah berikutnya perlu menyeimbangkan ketepatan struktur, kewajaran linguistik, dan transfer. Perluasan dimensional juga mulai mengganti polaritas kategoris dengan skor valensi–arousal, bukan menambahkan label emosi begitu saja (Yu et al., 2026).

**Prioritas Penelitian Berikutnya**

| Pertanyaan | Why |
|---|---|
| **Bagaimana menangani aspek dan opini yang sama-sama implisit?** | Kasus ini belum tercakup langsung oleh beberapa formulasi terpadu, sehingga evaluasi agregat dapat menyembunyikan kelemahan penting model (Zhou et al., 2023). |
| **Bagaimana menggabungkan pencocokan tepat dan kesetaraan linguistik?** | Batas rentang opini menghasilkan kesalahan formal meskipun makna serupa, sehingga ukuran tambahan dibutuhkan tanpa mengorbankan ketelitian struktur (Zhang et al., 2021). |
| **Bagaimana mempertahankan kuadruplet lengkap lintas bahasa dan domain?** | Terjemahan frasa opini kompleks dan kelangkaan anotasi membatasi transfer, terutama ketika kategori domain berubah dan bukti pelatihan sedikit (Wu et al., 2025; Šmíd & Král, 2025). |

**Figure 10:** Pertanyaan terbuka tentang ketepatan dan generalisasi ACOS

Intinya, evaluasi ACOS yang kuat harus memeriksa apakah **seluruh tuple benar dan terhubung**, bukan hanya apakah sentimennya benar.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
D., Xu, J., Wang, Z., Cao, X.-Z., & Xian, Y. (2023). Entity-Aspect-Opinion-Sentiment Quadruple Extraction for Fine-grained Sentiment Analysis. *ArXiv, abs/2311.16678*. https://doi.org/10.48550/arxiv.2311.16678
 
Ahmed, N., Aziz, K., Tariq, U., Hadi, H., Alshara, M. A., & Harris, S. (2025). Urdu Aspect-Category-Opinion-Sentiment (UACOS) Quadruple Extraction: A Transfer Learning Approach. *2025 4th International Conference on Communication, Computing and Digital Systems (C-CODE)*, 1-6. https://doi.org/10.1109/c-code67372.2025.11204128
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chakraborty, M., Kulkarni, A., & Li, Q. (2025). Weakly Supervised Open-Domain Aspect-Based Sentiment Analysis. *ACM Transactions on Knowledge Discovery from Data, 19*, 1 - 29. https://doi.org/10.1145/3747849
 
Chuang, H.-M., & Lin, J.-K. (2025). SetFitQuad: A Few-Shot Framework for Aspect Sentiment Quad Prediction With Sampling Strategies. *IEEE Access, 13*, 146204-146217. https://doi.org/10.1109/access.2025.3600351
 
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. *Artificial Intelligence Review, 55*, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
 
Hoang, C. D., Dinh, Q. V., & Tran, N. H. (2022). Aspect-Category-Opinion-Sentiment Extraction Using Generative Transformer Model. *2022 RIVF International Conference on Computing and Communication Technologies (RIVF)*, 1-6. https://doi.org/10.1109/rivf55975.2022.10013820
 
Hu, M.-T., Wu, Y., Gao, H., Bai, Y.-H., & Zhao, S. (2022). Improving Aspect Sentiment Quad Prediction via Template-Order Data Augmentation. *ArXiv, abs/2210.10291*. https://doi.org/10.48550/arxiv.2210.10291
 
Hu, M.-T., Bai, Y.-H., Wu, Y., Zhang, Z., Zhang, L., Gao, H., Zhao, S., & Huang, M.-T. (2023). Uncertainty-Aware Unlikelihood Learning Improves Generative Aspect Sentiment Quad Prediction. 13481-13494. https://doi.org/10.48550/arxiv.2306.00418
 
Huang, G.-H. (2023). A Fine-grained Sentiment Analysis Method Based On A Unified Framework. *2023 11th International Conference on Information Systems and Computing Technology (ISCTech)*, 21-27. https://doi.org/10.1109/isctech60480.2023.00012
 
Huang, B., & Wang, Y. (2025). Leveraging Domain Prediction and Retrieval Augmentation for Cross-domain Aspect Sentiment Quad Prediction. *2025 7th International Conference on Frontier Technologies of Information and Computer (ICFTIC)*, 140-143. https://doi.org/10.1109/icftic68075.2025.11324636
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Jian, Z.-Q., Chen, Y.-H., Li, J., Wang, S.-P., Zeng, X.-J., Yao, J.-F., An, X.-Y., & Wu, Q.-Q. (2025). SimRP: Syntactic and Semantic Similarity Retrieval Prompting Enhances Aspect Sentiment Quad Prediction. 24248-24256. https://doi.org/10.1609/aaai.v39i23.34601
 
Kim, J., Heo, R., Seo, Y., Kang, S., Yeo, J., & Lee, D.-H. (2024). Self-Consistent Reasoning-based Aspect-Sentiment Quad Prediction with Extract-Then-Assign Strategy. *ArXiv, abs/2403.00354*. https://doi.org/10.18653/v1/2024.findings-acl.435
 
Lai, W., Xie, H.-R., Xu, G., Li, Q., & Qin, S. (2025). Listwise Preference Optimization with Element-wise Confusions for Aspect Sentiment Quad Prediction. *ArXiv, abs/2511.23184*. https://doi.org/10.48550/arxiv.2511.23184
 
Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191098
 
Li, J., Li, X.-Y., Du, Y.-J., Fan, Y., Chen, X.-L., & Huang, D. (2023). An Aspect-Category-Opinion-Sentiment Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. *Inf. Technol. Control., 52*, 445-456. https://doi.org/10.5755/j01.itc.52.2.32903
 
Li, B., Fei, H., Li, F., Wu, Y.-H., Zhang, J.-S., Wu, S.-Q., Li, J., Liu, Y., Liao, L.-Z., Chua, T.-S., & Ji, D.-H. (2022). DiaASQ : A Benchmark of Conversational Aspect-based Sentiment Quadruple Analysis. *ArXiv, abs/2211.05705*. https://doi.org/10.48550/arxiv.2211.05705
 
Lil, Z., Yang, Z., Li, X.-Y., & Li, Y. (2023). Two-Stage Aspect Sentiment Quadruple Prediction Based on MRC and Text Generation. *2023 IEEE International Conference on Systems, Man, and Cybernetics (SMC)*, 2118-2125. https://doi.org/10.1109/smc53992.2023.10394369
 
Liu, Y., & Zhong, J. (2023). Implicit Sentiment Extraction Using Structure Generation with Sentiment Instructor Prompt Template. 94-108. https://doi.org/10.1007/978-3-031-46674-8_7
 
Mao, Y., Shen, Y., Yang, J.-C., Zhu, X., & Cai, L. (2022). Seq2Path: Generating Sentiment Tuples as Paths of a Tree. 2215-2225. https://doi.org/10.18653/v1/2022.findings-acl.174
 
Mao, Y.-Y., Liu, Q., & Zhang, Y. (2024). Sentiment analysis methods, applications, and challenges: A systematic literature review. *Journal of King Saud University Computer and Information Sciences, 36*. https://doi.org/10.1016/j.jksuci.2024.102048
 
Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. *Neurocomputing, 586*, 127642. https://doi.org/10.1016/j.neucom.2024.127642
 
Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. *ArXiv, abs/2211.07743*. https://doi.org/10.48550/arxiv.2211.07743
 
Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. https://doi.org/10.18653/v1/2024.findings-emnlp.907
 
Qin, Y.-S., & Lv, S. (2024). Generative Aspect Sentiment Quad Prediction with Self-Inference Template. *Applied Sciences*. https://doi.org/10.3390/app14146017
 
Šmíd, J., & Král, P. (2025). Cross-lingual aspect-based sentiment analysis: A survey on tasks, approaches, and challenges. *ArXiv, abs/2508.09516*. https://doi.org/10.1016/j.inffus.2025.103073
 
Su, G., Zhang, Y.-C., Wang, T., Wu, M., & Sha, Y. (2025). Unified Grid Tagging Scheme for Aspect Sentiment Quad Prediction. 3997-4010.
 
Wang, A., Jiang, J., Y., Liu, A., & Okazaki, N. (2023). Generative Data Augmentation for Aspect Sentiment Quad Prediction. *J. Nat. Lang. Process., 31*, 1523-1544. https://doi.org/10.18653/v1/2023.starsem-1.12
 
Wu, C., B., Liu, Y., Zhang, Z., Deng, N., Li, Y., Chen, B., Zhang, Y., Plank, B., & Xue, Y. (2025). M-ABSA: A Multilingual Dataset for Aspect-Based Sentiment Analysis. *ArXiv, abs/2502.11824*. https://doi.org/10.48550/arxiv.2502.11824
 
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
 
Xu, X., Zhang, J.-D., Xiong, L., & Liu, Z. (2023). iACOS: Advancing Implicit Sentiment Extraction with Informative and Adaptive Negative Examples. *ArXiv, abs/2311.03896*. https://doi.org/10.48550/arxiv.2311.03896
 
Xu, C., Wang, M., & Zhu, S. (2025). Tourism sentiment quadruple extraction via new neural ordinary differential equation networks with multitask learning and implicit sentiment enhancement. *Expert Syst. Appl., 270*, 126417. https://doi.org/10.1016/j.eswa.2025.126417
 
Yang, J.-J., Li, X., Deng, H., & Zhang, J. (2025). Data and Prompt Dual Enhancement for Aspect Sentiment Quad Prediction. *2025 10th International Conference on Information Science, Computer Technology and Transportation (ISCTT)*, 47-50. https://doi.org/10.1109/isctt66403.2025.11137908
 
Yu, Y., Zhao, M., & Zhou, S.-G. (2023). Boosting Aspect Sentiment Quad Prediction by Data Augmentation and Self-Training. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191634
 
Yu, L.-C., Becker, J., Muhammad, S. H., Abdulmumin, I., Lee, L.-H., Lin, Y.-L., Wang, J., Wahle, J. P., Ruas, T., Loukachevitch, N., Panchenko, A., Alimova, I., Wanzare, L., Onyango, N. O., Gipp, B., Chang, K.-W., & Mohammad, S. (2026). SemEval-2026 Task 3: Dimensional Aspect-Based Sentiment Analysis (DimABSA). 3753-3778. https://doi.org/10.48550/arxiv.2604.07066
 
Yusufu, A., Liu, J., Aziz, K., Ainiwaer, A., Li, B., Li, F., Ji, D., & Yusufu, A. (2026). LASQ: A low-resource aspect-based sentiment quadruple extraction dataset. *Journal of King Saud University Computer and Information Sciences, 38*. https://doi.org/10.1007/s44443-026-00701-x
 
Zhang, W., Deng, Y., Li, X., Yuan, Y., Bing, L., & Lam, W. (2021). Aspect Sentiment Quad Prediction as Paraphrase Generation. *ArXiv, abs/2110.00796*. https://doi.org/10.18653/v1/2021.emnlp-main.726
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, H., Chen, Z., Chen, B., Hu, B., Li, M., Yang, C., & Jiang, B. (2022). Complete quadruple extraction using a two-stage neural model for aspect-based sentiment analysis. *Neurocomputing, 492*, 452-463. https://doi.org/10.1016/j.neucom.2022.04.027
 
Zhang, H., Song, X.-W., Jia, X., Yang, C., Chen, Z., Chen, B., Jiang, B., Wang, Y., & Feng, R. (2024). Query-induced multi-task decomposition and enhanced learning for aspect-based sentiment quadruple prediction. *Eng. Appl. Artif. Intell., 133*, 108609. https://doi.org/10.1016/j.engappai.2024.108609
 
Zhang, W., Deng, Y., Liu, B.-Q., Pan, S. J., & Bing, L. (2023). Sentiment Analysis in the Era of Large Language Models: A Reality Check. 3881-3906. https://doi.org/10.48550/arxiv.2305.15005
 
Zhou, J., Yang, H., He, Y., Mou, H., & Yang, J. (2023). A Unified One-Step Solution for Aspect Sentiment Quad Prediction. *ArXiv, abs/2306.04152*. https://doi.org/10.48550/arxiv.2306.04152
 
Zhu, L., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. *World Wide Web, 26*, 3303 - 3320. https://doi.org/10.1007/s11280-023-01185-9
 
