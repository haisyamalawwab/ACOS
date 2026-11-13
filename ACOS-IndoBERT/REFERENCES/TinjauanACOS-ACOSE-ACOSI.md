
# Tinjauan **ACOS/ACOSQE** dan **ACOSI**

## 1. Introduction

Aspect-Category-Opinion-Sentiment (ACOS) atau Aspect Category Opinion Sentiment Quadruple Extraction (ACOSQE) adalah tugas ABSA yang mengekstrak empat elemen sekaligus—aspek, kategori, opini, dan polaritas sentimen—dengan penekanan khusus pada aspek dan opini implisit; istilah “quintuple” umumnya tidak merujuk pada ACOS asli, tetapi pada perluasan baru seperti ACOSI yang menambahkan indikator implisit/eksplisit opini (Cai et al., 2021; Zhang et al., 2024; Peper et al., 2024). Dua garis keturunan utama muncul hampir serentak pada 2021: ACOS dari Cai et al. berfokus pada dukungan eksplisit untuk aspek dan opini implisit, sedangkan ASQP dari Zhang et al. merumuskan tugas yang sama sebagai prediksi kuadruplet generatif; survei 2024 memperlakukan keduanya sebagai tugas yang ekuivalen secara konseptual (Zhang et al., 2024; Zhou et al., 2023; Zhang et al., 2021).

Korpus ini juga menunjukkan bahwa tugas tersebut memang sulit secara intrinsik, bukan sekadar masalah formulasi. Pada dataset ACOS asli, sekitar sepertiga hingga hampir setengah contoh memuat aspek atau opini implisit, dan baseline awal hanya mencapai F1 exact-match 0.4461 pada Restaurant-ACOS dan 0.3580 pada Laptop-ACOS (Cai et al., 2021). Sesudah itu, literatur bergerak dari pipeline dua tahap ke model generatif, grid/table-filling, MRC, prompting multi-view, contrastive learning, dan akhirnya ekstensi quintuple ACOSI yang melokalisasi opini implisit dan menambahkan flag implisit/eksplisit (Xiong et al., 2023; Zhang et al., 2021; Su et al., 2025; Zhang et al., 2024; Gou et al., 2023; Peper et al., 2024).

**Figure 1:** Konsensus riset tentang nilai tambah ACOSQE

## 2. Methods

Tinjauan ini mensintesis 50 paper teratas yang diambil dari pencarian Deep Search di Consensus, yang berjalan di atas lebih dari 220 juta paper dari Semantic Scholar, PubMed, dan sumber lain.

| Retrieved | Eligible | Included |
| --------- | -------- | -------- |
| 910.5K    | 165      | 50       |

**Figure 2:** Alur seleksi studi untuk tinjauan ACOSQE

Pencarian menggabungkan istilah ACOS, ACOSQE, ASQP, ACOSI, implicit aspect/opinion, benchmark, prompting, robustness, dan evaluation untuk mencakup definisi tugas, dataset, metode, evaluasi, serta perluasan quintuple.

## 3. Results

### 3.1 Key Papers

Empat paper jangkar membentuk bidang ini: paper ACL 2021 yang memperkenalkan ACOS dan dataset implisit, paper EMNLP 2021 yang memformulasikan ASQP sebagai paraphrase generation, survei 2024 yang menyatukan nomenklatur ACOS/ASQP/ACOSQE, dan paper EMNLP 2024 yang memperluas tugas ke ACOSI quintuple extraction (Cai et al., 2021; Zhang et al., 2021; Zhang et al., 2024; Peper et al., 2024). Sebagian besar metode berikutnya memodifikasi salah satu dari empat fondasi ini, baik dengan memperbaiki error propagation, urutan generasi, penanganan implisit, atau evaluasi exact match (Xiong et al., 2023; Zhang et al., 2024; Peper et al., 2024).

| Paper                | Summary                                                            |
| -------------------- | ------------------------------------------------------------------ |
| (Cai et al., 2021)   | Memperkenalkan tugas dan dataset ACOS implisit (Cai et al., 2021)  |
| (Zhang et al., 2021) | Meresmikan ASQP sebagai paraphrase generation (Zhang et al., 2021) |
| (Peper et al., 2024) | Memperluas ACOS menjadi ACOSI quintuple (Peper et al., 2024)       |

**Figure 3:** Paper dasar yang membentuk literatur ACOSQE

### 3.2 Benchmark Dan Dataset

Literatur awal menunjukkan bahwa nilai utama ACOS dibanding tugas ABSA sebelumnya adalah kemampuan merepresentasikan aspek dan opini implisit secara eksplisit melalui penanda NULL dan kategori (Cai et al., 2021; Zhou et al., 2023). Restaurant-ACOS memiliki 2,286 kalimat dan 3,658 quadruple, sedangkan Laptop-ACOS memiliki 4,076 kalimat dan 5,758 quadruple, dengan proporsi kasus implisit yang substansial di kedua domain (Cai et al., 2021).

| Dimensi                  | Restaurant-ACOS | Laptop-ACOS | Shoes-ACOSI | Citations            |
| ------------------------ | --------------- | ----------- | ----------- | -------------------- |
| Format                   | ACOS            | ACOS        | ACOSI       | (Peper et al., 2024) |
| Tokens/example           | 15.1            | 15.7        | 37.4        | (Peper et al., 2024) |
| Tuples/example           | 1.6             | 1.4         | 4.3         | (Peper et al., 2024) |
| IA/IO tuples             | 9.56%           | 5.92%       | 16.67%      | (Peper et al., 2024) |
| Mixed polarities/example | 1.08            | 1.05        | 1.73        | (Peper et al., 2024) |

**Figure 4:** Perbandingan dataset ACOS dan ACOSI utama

Dataset yang lebih baru sengaja dibuat lebih sulit. Shoes-ACOSI menambah span opini implisit yang dapat dilokalisasi, input paragraf yang lebih panjang, lebih banyak tuple per sampel, dan lebih banyak contoh mixed polarity daripada benchmark ACOS lama (Peper et al., 2024).

### 3.3 Evolusi Metode

Pada fase awal, pendekatan pipeline dan rule-based dipakai sebagai baseline, tetapi error propagation segera diidentifikasi sebagai keterbatasan utama (Cai et al., 2021; Li et al., 2023; Huang, 2023). Extract-Classify-ACOS menjadi baseline kuat pertama dengan strategi co-extraction lalu klasifikasi kategori-sentimen, dan mengungguli baseline awal pada dua dataset asli (Cai et al., 2021).

Model generatif kemudian menjadi arus utama karena lebih end-to-end dan dapat memanfaatkan semantik label melalui target natural-language atau template terstruktur (Zhang et al., 2021; Jian et al., 2025). Perbaikan generatif bergerak lewat beberapa jalur: optimasi urutan template dan augmentasi data (Hu et al., 2022; Wang et al., 2023), contrastive learning dan format keluaran yang lebih natural (Peper & Wang, 2022), prompting multi-view (Gou et al., 2023), serta decoding non-autoregresif atau multi-order untuk efisiensi dan generalisasi (Nie et al., 2024; Wang et al., 2026).

Pendekatan non-generatif juga tetap kompetitif bila dirancang end-to-end. Model berbasis grid tagging, MRC decomposition, dan unified tagging melaporkan hasil state-of-the-art atau mengungguli generatif tertentu pada benchmark publik (Zhu et al., 2023; Zhang et al., 2024; Su et al., 2025).

### 3.4 Quintuple, LLM, Dan Evaluasi

“Quintuple extraction” dalam literatur ini paling jelas merujuk pada ACOSI, bukan ACOSQE. ACOSI menambahkan indikator implisit/eksplisit opini dan, bila mungkin, melokalisasi span opini implisit alih-alih hanya memberi label NULL (Peper et al., 2024; Han et al., 2023). Perluasan ini relevan karena benchmark ACOS lama mengakui adanya opini implisit tetapi sering kehilangan informasi opinion span yang masih bisa dilokalisasi (Peper et al., 2024).

Kemampuan LLM umum pada tugas ini masih terbatas. Pada Shoes-ACOSI, GPT-3.5 hanya mencapai F1 10.98 dan GPT-4 14.14, jauh di bawah model supervised terbaik (Peper et al., 2024). Analisis lebih luas juga menyimpulkan bahwa LLM cukup baik pada tugas sentimen sederhana tetapi tertinggal pada tugas terstruktur yang menuntut pemahaman relasi yang lebih dalam (Zhang et al., 2023).

Evaluasi exact match tetap dominan, tetapi beberapa paper menekankan bahwa metrik ini menghukum keras prediksi yang hampir benar, terutama pada span opini dan kasus implisit (Cai et al., 2021; Zhang et al., 2021; Jian et al., 2025). Karena itu, sebagian kritik terbaru menyatakan kemampuan model—terutama LLM—bisa diremehkan oleh anotasi bias dan metrik yang terlalu kaku (Jian et al., 2025).

### Results Timeline

- **Jan 2021**
  - 1 paper: (Cai et al., 2021)
- **Oct 2021**
  - 1 paper: (Zhang et al., 2021)
- **Oct 2022**
  - 1 paper: (Hu et al., 2022)
- **Nov 2022**
  - 1 paper: (Peper & Wang, 2022)
- **Jan 2023**
  - 1 paper: (Wang et al., 2023)
- **Apr 2023**
  - 1 paper: (Xiong et al., 2023)
- **May 2023**
  - 2 papers: (Gou et al., 2023; Zhang et al., 2023)
- **Jun 2023**
  - 3 papers: (Zhou et al., 2023; Li et al., 2023; Han et al., 2023)
- **Jul 2023**
  - 2 papers: (Huang, 2023; Zhu et al., 2023)
- **Jan 2024**
  - 2 papers: (Zhang et al., 2024; Peper et al., 2024)
- **Apr 2024**
  - 1 paper: (Nie et al., 2024)
- **Jul 2024**
  - 1 paper: (Zhang et al., 2024)
- **Apr 2025**
  - 1 paper: (Jian et al., 2025)
- **Jul 2025**
  - 1 paper: (Su et al., 2025)
- **Apr 2026**
  - 1 paper: (Wang et al., 2026)
    **Figure 5:** Linimasa perkembangan ACOSQE; marker besar lebih banyak sitasi

### Top Contributors

| Type    | Name                               | Papers                                                    |
| ------- | ---------------------------------- | --------------------------------------------------------- |
| Author  | Wenxuan Zhang                      | (Zhang et al., 2021; Zhang et al., 2023)                  |
| Author  | Rui Xia                            | (Cai et al., 2021)                                        |
| Author  | Joseph J. Peper                    | (Peper & Wang, 2022; Peper et al., 2024)                  |
| Journal | *ArXiv*                          | (Peper & Wang, 2022; Zhang et al., 2021; Xu et al., 2023) |
| Journal | *ACL*                            | (Cai et al., 2021)                                        |
| Journal | *Artificial Intelligence Review* | (Zhang et al., 2024)                                      |

**Figure 6:** Penulis dan jurnal paling sering muncul

## 4. Discussion

Bukti sangat kuat bahwa ACOS/ASQP memperluas ABSA ke struktur empat elemen yang lebih lengkap daripada pair atau triplet extraction, dan bahwa perhatian pada aspek/opini implisit adalah kontribusi sentral, bukan tambahan kecil (Cai et al., 2021; Zhang et al., 2021; Zhang et al., 2024). Bukti juga kuat bahwa benchmark awal masih cukup sulit: exact-match F1 rendah, opinion span sering menjadi sumber kesalahan utama, dan kasus implisit tetap lebih keras daripada kasus eksplisit penuh (Cai et al., 2021; Zhang et al., 2021; Peper & Wang, 2022).

Di sisi metode, konsensusnya lebih moderat. Generatif menjadi arus utama dan sering unggul, tetapi bukan karena ada satu desain yang menang telak di semua setting; kinerja tampak sensitif terhadap template, urutan elemen, mekanisme voting, penanganan implicitness, dan formulasi decoding (Hu et al., 2022; Gou et al., 2023; Nie et al., 2024; Zhang et al., 2024). Pendekatan non-generatif yang kuat—grid tagging, MRC, atau unified tagging—tetap kompetitif dan kadang melaporkan keunggulan atas baseline generatif tertentu (Zhu et al., 2023; Zhang et al., 2024; Su et al., 2025).

Keterbatasan terbesar bidang ini adalah data dan evaluasi. Dataset awal relatif kecil, domain-sempit, dan sering berfokus pada kalimat pendek; benchmark baru seperti Shoes-ACOSI, FSQP, dan lintas-domain retrieval/prompting muncul justru karena model yang tampak kuat di benchmark lama turun pada input yang lebih panjang, lebih padat, atau domain baru (Zhou et al., 2023; Bai et al., 2024; Peper et al., 2024; Huang & Wang, 2025). Selain itu, exact match dapat meremehkan prediksi yang semantik benar tetapi span-nya tidak identik, sehingga klaim kemajuan kecil antarmodel perlu dibaca hati-hati (Zhang et al., 2021; Jian et al., 2025).

| Claim                                                                                  | Evidence Strength                  | Reasoning                                                         | Papers                                        |
| -------------------------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------- | --------------------------------------------- |
| ACOSQE/ASQP memberi formulasi ABSA yang lebih lengkap daripada pair/triplet extraction | Evidence strength: Strong (9/10)   | Didefinisikan konsisten di banyak paper foundational dan survey   | Cai 2021; Zhang 2021; Survey 2024             |
| Penanganan aspek/opini implisit adalah tantangan inti, bukan kasus tepi                | Evidence strength: Strong (8/10)   | Dataset awal dan lanjutan menunjukkan proporsi implisit besar     | Cai 2021; Peper 2024; Qin 2024                |
| Metode generatif sering mencapai hasil terbaik benchmark                               | Evidence strength: Moderate (7/10) | Banyak paper melaporkan SOTA generatif, tetapi tidak universal    | Zhang 2021; Gou 2023; Nie 2024                |
| LLM umum few-shot masih tertinggal pada ACOS/ACOSI                                     | Evidence strength: Moderate (6/10) | Beberapa evaluasi menunjukkan gap jelas terhadap model supervised | Peper 2024; Zhang et al. 2023; Xu et al. 2023 |
| Exact-match evaluation cukup membatasi penilaian kemampuan sebenarnya                  | Evidence strength: Weak (3/10)     | Kritiknya masuk akal tetapi bukti metrik alternatif masih awal    | SimRP 2025; Zhang 2021 error analysis         |

**Figure 7:** Klaim utama dan kekuatan evidensinya

## 5. Conclusion

ACOS/ACOSQE kini mapan sebagai formulasi ABSA empat-elemen untuk mengekstrak aspek, kategori, opini, dan sentimen secara bersama, terutama ketika aspek atau opini bersifat implisit. “Quintuple extraction” dalam korpus ini paling tepat merujuk pada ACOSI, yang menambahkan indikator implisit/eksplisit opini dan span opini implisit yang dapat dilokalisasi (Peper et al., 2024). Secara metodologis, bidang ini telah bergerak dari baseline pipeline ke campuran model generatif, tagging, MRC, prompting, dan reasoning, tetapi bottleneck terbesar tetap pada implicitness, domain shift, dan evaluasi.

### Research Gaps

Lanskap penelitian sangat padat pada benchmark empat-elemen berbahasa Inggris dan optimasi arsitektur, tetapi jauh lebih tipis pada generalisasi lintas-domain, bahasa rendah-sumber, dan evaluasi yang melampaui exact match. Matrix berikut memetakan area yang paling sering dipelajari versus dimensi yang paling jarang disentuh.

|              | Generative | Tagging   | Prompting | Implicit Span | New Metrics |
| ------------ | ---------- | --------- | --------- | ------------- | ----------- |
| ACOS         | 10 papers  | 3 papers  | 5 papers  | 8 papers      | No papers   |
| ASQP         | 14 papers  | 7 papers  | 9 papers  | 4 papers      | 3 papers    |
| ACOSI        | 1 paper    | 2 papers  | No papers | 6 papers      | 1 paper     |
| Cross-domain | 2 papers   | No papers | 2 papers  | No papers     | No papers   |
| Low-resource | 2 papers   | No papers | 2 papers  | No papers     | 1 paper     |

Gap paling mencolok adalah sedikitnya studi yang benar-benar menggabungkan implicit opinion localization dengan evaluasi yang lebih toleran terhadap near-miss span; ACOSI memperkenalkan masalahnya (Peper et al., 2024), tetapi usulan metrik fuzzy baru masih sangat baru (Jian et al., 2025). Generalisasi lintas-domain juga tampak tertinggal dibanding optimasi benchmark in-domain; kebutuhan ini dinyatakan eksplisit oleh studi retrieval-augmentation dan tinjauan sistematis terbaru (Huang & Wang, 2025; Jia et al., 2026). Literatur low-resource dan multilingual juga masih tipis; Urdu UACOS menunjukkan arah yang menjanjikan, tetapi bukti lintas-bahasa masih awal (Ahmed et al., 2025).

### Open Research Questions

Arah riset berikut paling langsung mengikuti kekosongan bukti saat ini.

| Question                                                                                                                     | Why                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Bagaimana mengevaluasi prediksi ACOS/ACOSI yang semantik benar tetapi span-nya tidak identik?**                      | Exact match menghukum near-miss span secara keras, terutama pada opini implisit dan output generatif.            |
| **Metode mana yang paling stabil saat berpindah domain, bahasa, dan panjang input?**                                   | Benchmark baru menunjukkan performa turun tajam pada domain yang lebih panjang, padat, dan berbeda distribusi.   |
| **Dapatkah model terpadu mengekstrak implicit opinion span dan flag implicitness tanpa kehilangan akurasi quadruple?** | ACOSI menambah informasi penting, tetapi justru membuat tugas jauh lebih sulit bagi model supervised maupun LLM. |

Sebagai jawaban atas pertanyaan awal, ACOS/ACOSQE adalah tugas quadruple extraction yang sudah mapan, sedangkan versi “quintuple” yang paling jelas dalam korpus ini adalah ACOSI, bukan definisi ACOS asli.

*These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at <https://consensus.app>. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent.*

## References

Ahmed, N., Aziz, K., Tariq, U., Hadi, H., Alshara, M. A., & Harris, S. (2025). Urdu Aspect-Category-Opinion-Sentiment (UACOS) Quadruple Extraction: A Transfer Learning Approach. *2025 4th International Conference on Communication, Computing and Digital Systems (C-CODE)*, 1-6. <https://doi.org/10.1109/c-code67372.2025.11204128>

Bai, Y.-H., Xie, Y.-L., Liu, X., Zhao, Y., Han, Z., Hu, M., Gao, H., & Cheng, R. (2024). BvSP: Broad-view Soft Prompting for Few-Shot Aspect Sentiment Quad Prediction. *ArXiv, abs/2406.07365*. <https://doi.org/10.48550/arxiv.2406.07365>

Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. <https://doi.org/10.18653/v1/2021.acl-long.29>

Gou, Z., Guo, Q., & Yang, Y. (2023). MvP: Multi-view Prompting Improves Aspect Sentiment Tuple Prediction. 4380-4397. <https://doi.org/10.48550/arxiv.2305.12627>

Han, Y., Bruggeman, R., Peper, J., Chehade, E. C., Marion, T., Ciuccarelli, P., & Moghaddam, M. (2023). EXTRACTING LATENT NEEDS FROM ONLINE REVIEWS THROUGH DEEP LEARNING BASED LANGUAGE MODEL. *Proceedings of the Design Society, 3*, 1855 - 1864. <https://doi.org/10.1017/pds.2023.186>

Hu, M.-T., Wu, Y., Gao, H., Bai, Y.-H., & Zhao, S. (2022). Improving Aspect Sentiment Quad Prediction via Template-Order Data Augmentation. *ArXiv, abs/2210.10291*. <https://doi.org/10.48550/arxiv.2210.10291>

Huang, G.-H. (2023). A Fine-grained Sentiment Analysis Method Based On A Unified Framework. *2023 11th International Conference on Information Systems and Computing Technology (ISCTech)*, 21-27. <https://doi.org/10.1109/isctech60480.2023.00012>

Huang, B., & Wang, Y. (2025). Leveraging Domain Prediction and Retrieval Augmentation for Cross-domain Aspect Sentiment Quad Prediction. *2025 7th International Conference on Frontier Technologies of Information and Computer (ICFTIC)*, 140-143. <https://doi.org/10.1109/icftic68075.2025.11324636>

Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. <https://doi.org/10.1145/3799234>

Jian, Z.-Q., Chen, Y.-H., Li, J., Wang, S.-P., Zeng, X.-J., Yao, J.-F., An, X.-Y., & Wu, Q.-Q. (2025). SimRP: Syntactic and Semantic Similarity Retrieval Prompting Enhances Aspect Sentiment Quad Prediction. 24248-24256. <https://doi.org/10.1609/aaai.v39i23.34601>

Li, S.-D., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. <https://doi.org/10.1109/ijcnn54540.2023.10191098>

Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. *Neurocomputing, 586*, 127642. <https://doi.org/10.1016/j.neucom.2024.127642>

Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. <https://doi.org/10.18653/v1/2024.findings-emnlp.907>

Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. *ArXiv, abs/2211.07743*. <https://doi.org/10.48550/arxiv.2211.07743>

Su, G., Zhang, Y.-C., Wang, T., Wu, M., & Sha, Y. (2025). Unified Grid Tagging Scheme for Aspect Sentiment Quad Prediction. 3997-4010.

Wang, A., Jiang, J., Y., Liu, A., & Okazaki, N. (2023). Generative Data Augmentation for Aspect Sentiment Quad Prediction. *J. Nat. Lang. Process., 31*, 1523-1544. <https://doi.org/10.18653/v1/2023.starsem-1.12>

Wang, R., He, M.-Y., Liu, W., Hao, Y.-X., Hu, L., Chen, M., & Huang, B. (2026). Generative Aspect-Based Sentiment Quadruple Prediction Based on Multi-Order Prompting. *ACM Transactions on Information Systems, 44*, 1 - 29. <https://doi.org/10.1145/3811909>

Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. <https://doi.org/10.1007/s13042-023-01831-8>

Xu, X., Zhang, J.-D., Xiao, R., & Xiong, L. (2023). The Limits of ChatGPT in Extracting Aspect-Category-Opinion-Sentiment Quadruples: A Comparative Analysis. *ArXiv, abs/2310.06502*. <https://doi.org/10.48550/arxiv.2310.06502>

Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. <https://doi.org/10.1007/s10462-023-10633-x>

Zhang, W., Deng, Y., Li, X., Yuan, Y., Bing, L., & Lam, W. (2021). Aspect Sentiment Quad Prediction as Paraphrase Generation. 9209-9219. <https://doi.org/10.18653/v1/2021.emnlp-main.726>

Zhang, H., Song, X.-W., Jia, X., Yang, C., Chen, Z., Chen, B., Jiang, B., Wang, Y., & Feng, R. (2024). Query-induced multi-task decomposition and enhanced learning for aspect-based sentiment quadruple prediction. *Eng. Appl. Artif. Intell., 133*, 108609. <https://doi.org/10.1016/j.engappai.2024.108609>

Zhang, W., Deng, Y., Liu, B.-Q., Pan, S. J., & Bing, L. (2023). Sentiment Analysis in the Era of Large Language Models: A Reality Check. 3881-3906. <https://doi.org/10.48550/arxiv.2305.15005>

Zhou, J., Yang, H., He, Y., Mou, H., & Yang, J. (2023). A Unified One-Step Solution for Aspect Sentiment Quad Prediction. *ArXiv, abs/2306.04152*. <https://doi.org/10.48550/arxiv.2306.04152>

Zhu, L.-N., Bao, Y., Xu, M.-H., Li, J., Zhu, Z., & Kong, X. (2023). Aspect sentiment quadruple extraction based on the sentence-guided grid tagging scheme. *World Wide Web, 26*, 3303 - 3320. <https://doi.org/10.1007/s11280-023-01185-9>
