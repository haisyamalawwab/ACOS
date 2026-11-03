# Alternatif **Pelabelan ACOS** dan Pengendalian Mutunya

Selain *weak labeling* dan *pseudo-labeling*, pilihan untuk Aspect–Category–Opinion–Sentiment (ACOS) mencakup **distant supervision, anotasi LLM, active learning, proyeksi lintas bahasa, dan generasi data sintetis**. Namun, metode yang menghasilkan kategori–sentimen saja belum tentu menyediakan label ACOS lengkap.

## 1. Introduction

Untuk melanjutkan pembahasan sebelumnya, perbedaan terpenting bukan sekadar “manual versus otomatis”, melainkan **dari mana label berasal, elemen mana yang dilabeli, dan bagaimana relasinya diverifikasi**. ACOS membutuhkan satu himpunan kuadruplet yang saling terhubung, bukan empat daftar label terpisah (Cai et al., 2021). Keterbatasan data berlabel menjadi persoalan khusus karena prediksi kuadruplet membutuhkan anotasi yang lebih rinci daripada klasifikasi sentimen biasa (Zhang et al., 2024; Yu et al., 2023).

Batas cakupan ini penting. SB-ASC menghasilkan kategori aspek dan sentimen, sedangkan UAOS menangani ekstraksi aspek, opini, pasangan, dan triplet tanpa memasukkan kategori aspek sebagai keluaran kelima tugasnya (Wallaart et al., 2025; Chakraborty et al., 2025). AX-MABSA juga menghasilkan pasangan kategori–sentimen, bukan kuadruplet lengkap (Kamila et al., 2022). Sebaliknya, *pseudo-label scorer* secara langsung mengevaluasi kecocokan ulasan dengan label ASQP lengkap (Zhang et al., 2024).

Karena itu, alternatif pelabelan perlu dibedakan dari teknik pelatihan: *active learning* memilih contoh untuk dianotasi, generasi sintetis membuat contoh baru, dan pembelajaran kontrasif memperbaiki representasi dari label yang tersedia (Alturayeif & Ahmad, 2024; Wang et al., 2023; Li et al., 2023). Ketiganya dapat membantu, tetapi bukan sinonim *pseudo-labeling*.


**Figure 1:** Bukti pengurangan anotasi manual melalui pelabelan otomatis

Hasil penelitian mendukung pengurangan kebutuhan anotasi, tetapi tidak menunjukkan bahwa semua alternatif otomatis dapat menggantikan anotator untuk ACOS lengkap.

## 2. Methods

Penelusuran menggunakan Consensus, yang mencakup lebih dari 220 juta publikasi penelitian dari Semantic Scholar, PubMed, dan sumber lainnya. Sintesis berfokus pada penelitian pelabelan ACOS/ASQP serta tugas ABSA terkait yang dapat menyumbangkan supervisi parsial.

Temuan dipisahkan menurut sumber label, kebutuhan anotasi awal, kelengkapan elemen keluaran, penyaringan kesalahan, dan evaluasi hilir. Hasil kategori–sentimen, ekstraksi aspek, dan triplet tidak diperlakukan sebagai bukti langsung keberhasilan kuadruplet lengkap. Publikasi jurnal dibedakan dari preprint dan laporan konferensi ketika menilai kepastian kesimpulan.

| Retrieved | Eligible | Included |
|-----------|----------|----------|
| 81.3K | 269 | 100 | 

**Figure 2:** Strategi penelusuran metode pelabelan dan validasi ACOS

Strategi menggabungkan pencarian supervisi lemah, label semu, anotasi LLM, pembelajaran aktif, generasi sintetis, serta transfer lintas bahasa.

## 3. Results

Literatur memperlihatkan beberapa jalur pelabelan yang dapat dikombinasikan, dengan kebutuhan supervisi dan cakupan keluaran berbeda.

### 3.1 Key Papers

Landasan tugas ACOS memasukkan aspek dan opini implisit secara eksplisit dalam dataset Restaurant-ACOS dan Laptop-ACOS (Cai et al., 2021). Pengembangan berikutnya berfokus pada kualitas label semu dan keterbatasan anotasi otomatis untuk relasi antarelemen (Zhang et al., 2024; Negi et al., 2026).

| Paper | Summary |
|---|---|
| (Cai et al., 2021) | Menetapkan tugas ACOS dengan elemen implisit (Cai et al., 2021) |
| (Zhang et al., 2024) | Menyaring label semu berdasarkan kecocokan teks (Zhang et al., 2024) |
| (Negi et al., 2026) | Menguji anotator dan adjudikator LLM untuk ACOS (Negi et al., 2026) |

**Figure 3:** Publikasi inti mengenai tugas dan pelabelan ACOS

### 3.2 Weak dan Pseudo Label

*Weak labels* dapat berasal dari aturan dependensi, leksikon, atau contoh representatif (Chakraborty et al., 2025; Kumar et al., 2021; Wallaart et al., 2025). *Pseudo-labels* berasal dari prediksi model pada data tak berlabel yang kemudian dimasukkan ke pelatihan berikutnya (Zhang et al., 2024).

| Dimensi | Weak Labeling | Pseudo-Labeling | Bukti |
|---|---|---|---|
| Sumber utama | Aturan, leksikon, fungsi pelabelan | Prediksi model awal | (Ruffolo & Visalli, 2020; He et al., 2023) |
| Penggabungan label | Model probabilistik Snorkel | Seleksi dan pelatihan ulang | (Ruffolo & Visalli, 2020; Yu et al., 2023) |
| Pengendalian noise | Model tahan derau | Scorer atau peer teacher | (Kumar et al., 2021; Ouyang & Shen, 2023) |
| Batas utama | Cakupan aturan dan tata bahasa | Label keliru mengarahkan pembelajaran | (Zhang et al., 2024; Xu & Ibrahim, 2024) |

**Figure 4:** Perbedaan sumber label lemah dan label semu

Supervisi lemah meningkatkan kinerja *few-shot* hingga **15.84 poin F1 absolut** pada tugas ABSA yang lebih sulit dalam satu evaluasi (Vacareanu et al., 2023). Namun, pada metode Snorkel tertentu, aspek dan sentimen masih diprediksi terpisah sehingga belum menghasilkan sentimen yang terkait dengan aspek (Subbaih & Bolla, 2023).

### 3.3 Alternatif Pelabelan

Alternatif berikut berbeda dalam objek yang dianotasi: teks asli, contoh terpilih, teks terjemahan, atau teks sintetis.

| Pendekatan | Sumber Label | Kegunaan untuk ACOS | Batas Bukti |
|---|---|---|---|
| **Distant supervision** | Rating atau anotasi eksternal | Supervisi parsial aspek/sentimen | Bukan kuadruplet otomatis (Bhattacharjee & Gangadharaiah, 2023; Imani & Noferesti, 2022) |
| **LLM-as-annotator** | Instruksi dan demonstrasi | Anotasi kuadruplet pada teks asli | Relasi tetap sulit (Hellwig et al., 2026; Negi et al., 2026) |
| **Active learning** | Anotator pada contoh informatif | Menghemat anggaran anotasi | Bukti sering pada subtugas (Alturayeif & Ahmad, 2024; Venugopalan & Gupta, 2022) |
| **Label projection** | Data bahasa sumber | Menambah supervisi bahasa target | Banyak dataset tanpa opini (Zhang et al., 2021; Šmíd & Král, 2025) |
| **Synthetic labeling** | Label dikondisikan menjadi teks | Membuat pasangan teks–kuadruplet baru | Perlu penyaringan keselarasan (Wang et al., 2023) |

**Figure 5:** Alternatif pelabelan berdasarkan sumber dan cakupan supervisi

Supervisi rating juga diterapkan melalui *multiple-instance learning*, sedangkan pasangan target–opini dari parser digunakan sebagai supervisi alternatif (Angelidis & Lapata, 2018; Zeng et al., 2019). Pendekatan berbasis nama kelas, pemodelan topik, dan pengelompokan menyediakan label kategori dengan supervisi minimal (Kamila et al., 2022; Lu et al., 2011; Park & Kim, 2025). Pemilihan kategori melalui pemodelan topik juga dapat melibatkan pemeriksaan manusia sebelum deteksi istilah aspek (Haq et al., 2023).

### 3.4 Hasil dan Kontrol Mutu

Pada ASQP, gabungan penyaringan dan *reranking* meningkatkan GAS rata-rata **4.60 poin F1**, tetapi peningkatan tersebut bukan efek scorer saja (Zhang et al., 2024). Memilih hanya label dengan skor tertinggi juga tidak optimal karena contoh yang sangat mudah memberi manfaat pelatihan terbatas (Zhang et al., 2024).

Generasi kuadruplet-ke-teks mengatasi keterbatasan penulisan ulang teks, sedangkan generasi triplet-ke-teks memakai diskriminator kelancaran dan keselarasan (Wang et al., 2023; Zhang et al., 2023). Penyaringan refleksi, pemilihan sintetis iteratif, dan diskriminator supervisi lemah juga dilaporkan membantu kualitas data (Zhong et al., 2024; Mai et al., 2024; Lu et al., 2024).

Untuk efisiensi anotasi, EASE melaporkan pengurangan **88–94%** contoh berlabel, LETS mengurangi upaya **2–3 kali**, dan metode ATE lain menggunakan **9–13%** data pelatihan (Alturayeif & Ahmad, 2024; Shim et al., 2021; Venugopalan & Gupta, 2022). Angka-angka ini berasal dari tugas dan protokol berbeda, bukan estimasi penghematan universal ACOS.

### Results Timeline

Perkembangan bergerak dari kata benih dan rating menuju kontrol kualitas kuadruplet.

- **Jan 2020**
  - 1 paper: (Ruffolo & Visalli, 2020)
- **Jan 2021**
  - 1 paper: (Cai et al., 2021)
- **Jul 2021**
  - 1 paper: (Kumar et al., 2021)
- **Jun 2022**
  - 1 paper: (Imani & Noferesti, 2022)
- **Nov 2022**
  - 1 paper: (Kamila et al., 2022)
- **Jan 2023**
  - 1 paper: (Wang et al., 2023)
- **May 2023**
  - 2 papers: (Li et al., 2023; Vacareanu et al., 2023)
- **Jun 2023**
  - 1 paper: (Yu et al., 2023)
- **Jul 2023**
  - 1 paper: (He et al., 2023)
- **Oct 2023**
  - 1 paper: (Bhattacharjee & Gangadharaiah, 2023)
- **Dec 2023**
  - 2 papers: (Ouyang & Shen, 2023; Subbaih & Bolla, 2023)
- **Jan 2024**
  - 1 paper: (Zhang et al., 2024)
- **Jun 2024**
  - 1 paper: (Zhang et al., 2024)
- **Jul 2024**
  - 1 paper: (Xu & Ibrahim, 2024)
- **Oct 2024**
  - 1 paper: (Alturayeif & Ahmad, 2024)
- **Apr 2025**
  - 1 paper: (Wallaart et al., 2025)
- **Jul 2025**
  - 1 paper: (Chakraborty et al., 2025)
- **Jan 2026**
  - 1 paper: (Negi et al., 2026)
**Figure 6:** Perkembangan metode; penanda besar menunjukkan lebih banyak sitasi

Generasi terkini menggabungkan perluasan data dan pemeriksaan kecocokan label, bukan sekadar memperbanyak anotasi otomatis (Zhang et al., 2024).

### Top Contributors

Kontributor berikut memiliki beberapa publikasi relevan dalam korpus; kemunculan ini bukan peringkat dampak seluruh bidang.

| Type | Name | Papers |
|------|------|--------|
| Author | Ruifeng Xu | (He et al., 2023; Zhang et al., 2024; Zhang et al., 2023) |
| Author | Nils Constantin Hellwig | (Hellwig et al., 2024; Hellwig et al., 2025; Hellwig et al., 2026) |
| Author | Jakob Fehle | (Hellwig et al., 2024; Hellwig et al., 2025; Hellwig et al., 2026) |
| Journal | *Expert Systems with Applications* | (Venugopalan & Gupta, 2022; Hellwig et al., 2024; Alturayeif & Ahmad, 2024) |
| Journal | *Knowledge-Based Systems* | (Wallaart et al., 2025; Mai et al., 2024; Liu et al., 2023) |
| Journal | *IEEE Access* | (Kastrati et al., 2020; Shim et al., 2021) |

**Figure 7:** Penulis dan jurnal dengan kontribusi berulang dalam korpus

## 4. Discussion

**Bukti paling langsung untuk ACOS mendukung pelabelan otomatis dengan verifikasi relasional.** Anotasi LLM relatif kuat pada span, tetapi lebih lemah dalam menghubungkan span secara benar (Negi et al., 2026). Pada Rest16, prompting 20-shot mencapai F1 **51.54**, dibanding **60.39** untuk model fine-tuned pembanding (Hellwig et al., 2025). Pelatihan model ringan dengan anotasi LLM mencapai **49.85**, mendekati prompting **51.10**, tetapi tetap bukan bukti penggantian manusia tanpa kehilangan mutu (Hellwig et al., 2026).

Validasi manusia tetap penting karena persetujuan antar-LLM tidak menjamin kesesuaian dengan anotator manusia, dan bias netral ditemukan pada ulasan hotel (Voutsa et al., 2025). Bahkan label benchmark memerlukan audit: dalam sampel terpilih berisi 100 contoh ACOS-Laptop berskor rendah, 73% bertentangan dengan pedoman; angka ini **tidak mewakili seluruh dataset** (Zhang et al., 2024). Anotasi berbantuan manusia–LLM dengan saran berbasis contoh terdahulu menyediakan alternatif operasional yang mempertahankan kontrol anotator (Hellwig et al., 2026).

Untuk domain atau bahasa baru, aturan sintaksis dapat melengkapi aspek yang terlewat LLM, sementara proyeksi terjemahan dan generasi bahasa target menawarkan jalur berbeda (Negi et al., 2024; Šmíd & Král, 2025; Šmíd et al., 2025). Namun, keberhasilan Urdu, Vietnam, atau transfer multibahasa tidak otomatis menetapkan efektivitas ACOS bahasa Indonesia (Ya et al., 2025; Van Dang et al., 2024; Yusufu et al., 2026).

**Klaim dan Kepastian Bukti**

| Claim | Evidence Strength | Reasoning | Papers |
|---|---|---|---|
| Filter meningkatkan self-training ASQP | Evidence strength: Moderate (7/10) | Evaluasi empat benchmark | (Zhang et al., 2024) |
| Active learning menghemat anotasi | Evidence strength: Moderate (7/10) | Replikasi pada beberapa subtugas | (Alturayeif & Ahmad, 2024; Shim et al., 2021) |
| Data sintetis membantu kondisi low-resource | Evidence strength: Moderate (6/10) | Manfaat bergantung anggaran awal | (Hellwig et al., 2024) |
| LLM menggantikan seluruh anotator ACOS | Evidence strength: Weak (2/10) | Keterbatasan struktur dan mutu | (Hellwig et al., 2025; Negi et al., 2026) |

**Figure 8:** Kepastian klaim pelabelan otomatis dan penghematan anotasi

## 5. Conclusion

Untuk kebutuhan ACOS, pilihan paling defensibel adalah **label awal otomatis → pemeriksaan kelengkapan kuadruplet → penyaringan → koreksi manusia pada kasus sulit**. *Weak labeling*, *pseudo-labeling*, dan alternatif lainnya sebaiknya diperlakukan sebagai komponen yang saling melengkapi, bukan kategori eksklusif.

### Research Gaps

Kesenjangan utama terletak pada perpindahan dari label parsial menuju kuadruplet lengkap, terutama untuk ekspresi implisit dan bahasa rendah sumber daya.

| | Category sentiment | Aspect extraction | Triplet extraction | Quadruple extraction |
|---|---|---|---|---|
| Weak supervision | 12 papers | 11 papers | 3 papers | 1 paper |
| Pseudo labeling | 4 papers | 8 papers | 2 papers | 2 papers |
| LLM annotation | 4 papers | 5 papers | 6 papers | 5 papers |
| Synthetic generation | 3 papers | 4 papers | 5 papers | 4 papers |
| Label projection | No papers | 1 paper | No papers | No papers |
**Figure 9:** Cakupan pendekatan pelabelan menurut kompleksitas keluaran sentimen

Dataset multibahasa sering tidak memiliki anotasi opini sehingga membatasi evaluasi tugas gabungan (Šmíd & Král, 2025). Opini implisit juga tetap sulit bagi model supervised dan LLM, terutama pada input panjang dengan sentimen campuran (Peper et al., 2024). Ketidakseimbangan kategori membutuhkan perhatian tersendiri karena label langka memerlukan augmentasi terarah, bukan hanya penambahan volume data (Yang et al., 2025; Zhang et al., 2024).

### Open Research Questions

Prioritas berikutnya ialah menguji kualitas kuadruplet dan efisiensi anotasi secara bersamaan.

| Pertanyaan | Why |
|---|---|
| **Bagaimana menggabungkan scorer dan active learning untuk pelabelan ACOS?** | Seleksi contoh informatif dan pemeriksaan kecocokan label diuji terpisah, sehingga manfaat gabungannya perlu diukur langsung (Zhang et al., 2024; Alturayeif & Ahmad, 2024). |
| **Bagaimana mengevaluasi label ACOS implisit dalam bahasa Indonesia?** | Bukti Indonesia yang dibahas masih berbeda dari supervisi kuadruplet lengkap dengan span target dan opini eksplisit (Yusufu et al., 2026). |
| **Kapan label sintetis lebih bermanfaat daripada koreksi label asli?** | Jumlah data tambahan memiliki batas manfaat, sementara kualitas dan keragaman perlu diseimbangkan dalam pelatihan ulang (Zhang et al., 2024). |

**Figure 10:** Pertanyaan lanjutan untuk pelabelan ACOS yang andal

Intinya: **pilih metode berdasarkan kelengkapan label ACOS yang dihasilkan, bukan hanya kecepatan menghasilkan label.**
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Alturayeif, N., & Ahmad, I. (2024). EASE: An enhanced active learning framework for aspect-based sentiment analysis based on sample diversity and data augmentation. *Expert Syst. Appl., 261*, 125525. https://doi.org/10.1016/j.eswa.2024.125525
 
Angelidis, S., & Lapata, M. (2018). Summarizing Opinions: Aspect Extraction Meets Sentiment Prediction and They Are Both Weakly Supervised. *ArXiv, abs/1808.08858*. https://doi.org/10.18653/v1/d18-1403
 
Bhattacharjee, K., & Gangadharaiah, R. (2023). Document-Level Supervision for Multi-Aspect Sentiment Analysis Without Fine-grained Labels. *ArXiv, abs/2310.06940*. https://doi.org/10.48550/arxiv.2310.06940
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chakraborty, M., Kulkarni, A., & Li, Q. (2025). Weakly Supervised Open-Domain Aspect-Based Sentiment Analysis. *ACM Transactions on Knowledge Discovery from Data, 19*, 1 - 29. https://doi.org/10.1145/3747849
 
Haq, B., Daudpota, S., Imran, A., Kastrati, Z., & Noor, W. (2023). A Semi-Supervised Approach for Aspect Category Detection and Aspect Term Extraction from Opinionated Text. *Computers, Materials & Continua*. https://doi.org/10.32604/cmc.2023.040638
 
He, K., Mao, R., Gong, T., Li, C., & Cambria, E. (2023). Meta-Based Self-Training and Re-Weighting for Aspect-Based Sentiment Analysis. *IEEE Transactions on Affective Computing, 14*, 1731-1742. https://doi.org/10.1109/taffc.2022.3202831
 
Hellwig, N. C., Fehle, J., Kruschwitz, U., & Wolff, C. (2026). LLM-as-an-Annotator: Training Lightweight Models with LLM-Annotated Examples for Aspect Sentiment Tuple Prediction. *ArXiv, abs/2603.01778*. https://doi.org/10.48550/arxiv.2603.01778
 
Hellwig, N. C., Fehle, J., Kruschwitz, U., & Wolff, C. (2025). Do we still need Human Annotators? Prompting Large Language Models for Aspect Sentiment Quad Prediction. *ArXiv, abs/2502.13044*. https://doi.org/10.48550/arxiv.2502.13044
 
Hellwig, N. C., Fehle, J., Kruschwitz, U., & Wolff, C. (2026). AnnoABSA: A Web-Based Annotation Tool for Aspect-Based Sentiment Analysis with Retrieval-Augmented Suggestions. 7985-7998. https://doi.org/10.48550/arxiv.2603.01773
 
Hellwig, N. C., Fehle, J., & Wolff, C. (2024). Exploring large language models for the generation of synthetic training samples for aspect-based sentiment analysis in low resource settings. *Expert Syst. Appl., 261*, 125514. https://doi.org/10.1016/j.eswa.2024.125514
 
Imani, M., & Noferesti, S. (2022). Aspect extraction and classification for sentiment analysis in drug reviews. *Journal of Intelligent Information Systems, 59*, 613 - 633. https://doi.org/10.1007/s10844-022-00712-w
 
Kamila, S., Magdy, W., Dutta, S., & Wang, M. (2022). AX-MABSA: A Framework for Extremely Weakly Supervised Multi-label Aspect Based Sentiment Analysis. 6136-6147. https://doi.org/10.48550/arxiv.2211.03837
 
Kastrati, Z., Imran, A., & Kurti, A. (2020). Weakly Supervised Framework for Aspect-Based Sentiment Analysis on Students’ Reviews of MOOCs. *IEEE Access, 8*, 106799-106810. https://doi.org/10.1109/access.2020.3000739
 
Kumar, A., Gupta, P., Balan, R., Neti, L. B. M., & Malapati, A. (2021). BERT Based Semi-Supervised Hybrid Approach for Aspect and Sentiment Classification. *Neural Processing Letters, 53*, 4207 - 4224. https://doi.org/10.1007/s11063-021-10596-6
 
Li, P., Li, P., & Xiao, X. (2023). Aspect-Pair Supervised Contrastive Learning for aspect-based sentiment analysis. *Knowl. Based Syst., 274*, 110648. https://doi.org/10.1016/j.knosys.2023.110648
 
Liu, B., Lin, T., & Li, M. (2023). Enhancing aspect-category sentiment analysis via syntactic data augmentation and knowledge enhancement. *Knowl. Based Syst., 264*, 110339. https://doi.org/10.1016/j.knosys.2023.110339
 
Lu, B., Ott, M., Cardie, C., & T'sou, B. K.-Y. (2011). Multi-aspect Sentiment Analysis with Topic Models. *2011 IEEE 11th International Conference on Data Mining Workshops*, 81-88. https://doi.org/10.1109/icdmw.2011.125
 
Lu, C., Yang, C.-W., & W.-Y. (2024). Automatic Construction of a Chinese Review Dataset for Aspect Sentiment Triplet Extraction via Iterative Weak Supervision. 1871-1882. https://doi.org/10.63317/4jrun4xweepf
 
Mai, W., Zhang, Z., Chen, Y., Li, K., & Xue, Y. (2024). GeDa: Improving training data with large language models for Aspect Sentiment Triplet Extraction. *Knowl. Based Syst., 301*, 112289. https://doi.org/10.1016/j.knosys.2024.112289
 
Negi, G., Waskow, M., Mccrae, J., Zayed, O., & Buitelaar, P. (2026). Large Language Models as Automatic Annotators and Annotation Adjudicators for Fine-Grained Opinion Analysis. *ArXiv, abs/2601.16800*. https://doi.org/10.48550/arxiv.2601.16800
 
Negi, G., Sarkar, R., Zayed, O., & Buitelaar, P. (2024). A Hybrid Approach to Aspect Based Sentiment Analysis Using Transfer Learning. *ArXiv, abs/2403.17254*. https://doi.org/10.48550/arxiv.2403.17254
 
Ouyang, F., & Shen, B. (2023). A mutual mean teacher framework for cross-domain aspect-based sentiment analysis. *The Journal of Supercomputing, 80*, 9073 - 9095. https://doi.org/10.1007/s11227-023-05792-1
 
Park, J., & Kim, M. (2025). A Scalable Unsupervised Framework for multi-aspect labeling of Multilingual and Multi-Domain Review Data. *Knowl. Based Syst., 335*, 115210. https://doi.org/10.1016/j.knosys.2025.115210
 
Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. https://doi.org/10.18653/v1/2024.findings-emnlp.907
 
Ruffolo, M., & Visalli, F. (2020). A Weak-supervision Method for Automating Training Set Creation in Multi-domain Aspect Sentiment Classification. 249-256. https://doi.org/10.5220/0009165602490256
 
Shim, H., Lowet, D., Luca, S., & Vanrumste, B. (2021). LETS: A Label-Efficient Training Scheme for Aspect-Based Sentiment Analysis by Using a Pre-Trained Language Model. *IEEE Access, 9*, 115563-115578. https://doi.org/10.1109/access.2021.3101867
 
Šmíd, J., & Král, P. (2025). Cross-lingual aspect-based sentiment analysis: A survey on tasks, approaches, and challenges. *ArXiv, abs/2508.09516*. https://doi.org/10.1016/j.inffus.2025.103073
 
Šmíd, J., Přibáň, P., & Král, P. (2025). LACA: Improving Cross-lingual Aspect-Based Sentiment Analysis with LLM Data Augmentation. 839-853. https://doi.org/10.18653/v1/2025.acl-long.41
 
Subbaih, K., & Bolla, B. (2023). Aspect category learning and sentimental analysis using weakly supervised learning. 1246-1257. https://doi.org/10.48550/arxiv.2312.15526
 
Vacareanu, R., Varia, S., Halder, K., Wang, S., Paolini, G., John, N. A., Ballesteros, M., & Muresan, S. (2023). A Weak Supervision Approach for Few-Shot Aspect Based Sentiment Analysis. 2734-2752. https://doi.org/10.48550/arxiv.2305.11979
 
Van Dang, T., Duong, H., & Nguyen, N. (2024). Vi-AbSQA: Multi-task Prompt Instruction Tuning Model for Vietnamese Aspect-based Sentiment Quadruple Analysis. *ACM Transactions on Asian and Low-Resource Language Information Processing*. https://doi.org/10.1145/3676886
 
Venugopalan, M., & Gupta, D. (2022). A reinforced active learning approach for optimal sampling in aspect term extraction for sentiment analysis. *Expert Syst. Appl., 209*, 118228. https://doi.org/10.1016/j.eswa.2022.118228
 
Voutsa, M. C., Tsapatsoulis, N., & Djouvas, C. (2025). Biased by Design? Evaluating Bias and Behavioral Diversity in LLM Annotation of Real-World and Synthetic Hotel Reviews. *AI*. https://doi.org/10.3390/ai6080178
 
Wallaart, O., Frasincar, F., & Van Der Knaap, F. (2025). Weakly-supervised sentence-based aspect category and sentiment classification. *Knowl. Based Syst., 317*, 113403. https://doi.org/10.1016/j.knosys.2025.113403
 
Wang, A., Jiang, J., Y., Liu, A., & Okazaki, N. (2023). Generative Data Augmentation for Aspect Sentiment Quad Prediction. *J. Nat. Lang. Process., 31*, 1523-1544. https://doi.org/10.18653/v1/2023.starsem-1.12
 
Xu, Y., & Ibrahim, N. F. (2024). Alignment-Based Pseudo-Label Generation With Collaborative Filtering Mechanism for Enhanced Cross-Domain Aspect-Based Sentiment Analysis. *IEEE Access, 12*, 155618-155631. https://doi.org/10.1109/access.2024.3469872
 
Ya, Z., Latif, S., & Latif, R. (2025). Pseudo-Labeling with Large Language Models for Aspect-Based Sentiment Analysis in Urdu. *Data Intelligence*. https://doi.org/10.3724/2096-7004.di.2025.0054
 
Yang, J.-J., Li, X., Deng, H., & Zhang, J. (2025). Data and Prompt Dual Enhancement for Aspect Sentiment Quad Prediction. *2025 10th International Conference on Information Science, Computer Technology and Transportation (ISCTT)*, 47-50. https://doi.org/10.1109/isctt66403.2025.11137908
 
Yu, Y., Zhao, M., & Zhou, S.-G. (2023). Boosting Aspect Sentiment Quad Prediction by Data Augmentation and Self-Training. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191634
 
Yusufu, A., Liu, J., Aziz, K., Ainiwaer, A., Li, B., Li, F., Ji, D., & Yusufu, A. (2026). LASQ: A low-resource aspect-based sentiment quadruple extraction dataset. *Journal of King Saud University Computer and Information Sciences, 38*. https://doi.org/10.1007/s44443-026-00701-x
 
Zeng, Z., Zhou, W., Liu, X., & Song, Y.-Q. (2019). A Variational Approach to Weakly Supervised Document-Level Multi-Aspect Sentiment Classification. *ArXiv, abs/1904.05055*. https://doi.org/10.18653/v1/n19-1036
 
Zhang, Y., Zeng, J., Hu, W.-M., Wang, Z., Chen, S.-W., & Xu, R. (2024). Self-Training with Pseudo-Label Scorer for Aspect Sentiment Quad Prediction. *ArXiv, abs/2406.18078*. https://doi.org/10.48550/arxiv.2406.18078
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, W.-X., He, R.-D., Peng, H.-Y., Bing, L., & Lam, W. (2021). Cross-lingual Aspect-based Sentiment Analysis with Aspect Term Code-Switching. 9220-9230. https://doi.org/10.18653/v1/2021.emnlp-main.727
 
Zhang, Y., Yang, Y., Li, M., Liang, B., Chen, S.-W., & Xu, R.-F. (2023). Target-to-Source Augmentation for Aspect Sentiment Triplet Extraction. 12165-12177. https://doi.org/10.18653/v1/2023.emnlp-main.747
 
Zhong, Q.-H., Li, H., Zhuang, L.-Y., Liu, J.-H., & Du, B. (2024). Iterative Data Generation with Large Language Models for Aspect-based Sentiment Analysis. https://doi.org/10.48550/arxiv.2407.00341
 
