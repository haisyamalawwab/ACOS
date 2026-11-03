# Pemetaan **Triplet dan Subtugas ABSA**

## 1. Introduction

**Ekstraksi triplet memperluas ATE, AOE, dan ASC dengan menghasilkan aspek, opini terkait, serta polaritas sentimennya secara terhubung.** Dibandingkan pembahasan ACOS sebelumnya, fokus di sini adalah hubungan antarsubtugas dan perbedaan informasi yang masing-masing hasilkan. Taksonomi ABSA membedakan tugas berdasarkan unsur yang diprediksi—istilah aspek, kategori aspek, ungkapan opini, dan sentimen—serta relasi antarunsur tersebut (Zhang et al., 2022; Zhang et al., 2024).

Perbedaan terpenting bukan jumlah singkatan, melainkan **masukan yang sudah tersedia dan keluaran yang harus ditemukan**. ASC memprediksi sentimen untuk aspek yang diberikan, sedangkan ekstraksi pasangan aspek–sentimen juga harus menemukan aspeknya (Xu et al., 2021; Šmíd & Král, 2025). AOE dalam pengertian *aspect-oriented opinion extraction* mencari opini untuk aspek yang diberikan, sementara AOPE mengekstraksi pasangan aspek–opini tanpa aspek acuan sebagai masukan (Peng et al., 2019; Wang et al., 2021).

**ASE dan ACO perlu didefinisikan secara operasional**, bukan dianggap mempunyai kepanjangan seragam. Literatur menggunakan AESC, ATSE, ASPE, atau E2E-ABSA untuk keluaran aspek–sentimen; bahkan ASPE digunakan sebagian penelitian untuk pasangan kategori–sentimen (Jing et al., 2021; Chakraborty et al., 2025; Fu et al., 2021). Untuk ACO, istilah dalam sebagian sumber tidak sejalan dengan taksonomi yang lebih eksplisit mengenai TASD dan ACOS (Li et al., 2023; Šmíd & Král, 2025). Karena itu, notasi tuple lebih aman daripada singkatan saja.


**Figure 1:** Bukti pemodelan bersama dibandingkan pipeline ekstraksi triplet

Banyak eksperimen mendukung pemodelan bersama, tetapi terdapat pipeline yang mengungguli beberapa model bersama; keunggulannya tidak universal (Xu et al., 2020; Li et al., 2021).

## 2. Methods

Penelusuran menggunakan Consensus, yang mencakup lebih dari 220 juta makalah melalui Semantic Scholar, PubMed, dan sumber lainnya. Pencarian menggabungkan terminologi ABSA, definisi subtugas, ekstraksi pasangan dan triplet, serta singkatan yang berpotensi ambigu. Referensi publikasi awal ditelusuri untuk mengklarifikasi hubungan antartugas.

Seleksi mengutamakan kesesuaian masukan–keluaran, bukan kemiripan nama. Teks lengkap digunakan untuk memeriksa definisi, struktur anotasi, dan batasan model apabila tersedia. Temuan berbasis abstrak dipisahkan dari rincian eksperimen yang dapat diperiksa langsung. Angka kinerja dibaca dalam pengaturan masing-masing, terutama versi dataset, bahasa, domain, tingkat supervisi, dan jenis keluaran.

| Retrieved | Eligible | Included |
|-----------|----------|----------|
| 1.4M | 286 | 100 | 

**Figure 2:** Alur penelusuran literatur subtugas dan ekstraksi triplet

Strategi menggabungkan pencarian singkatan, pemeriksaan definisi masukan–keluaran, penelusuran referensi, dan pembandingan bukti generalisasi lintas domain serta bahasa.

## 3. Results

Hasil berikut memisahkan taksonomi tugas, representasi model, dan bukti evaluasinya.

### 3.1 Key Papers

*Knowing What, How and Why* memperkenalkan ASTE untuk menghubungkan sasaran, sentimen, dan ungkapan yang menjelaskannya (Peng et al., 2019). Survei Zhang dan kolega menyediakan taksonomi unsur, sedangkan Dual-MRC memperjelas perbedaan ekstraksi aspek, opini bersyarat aspek, pasangan, dan triplet (Zhang et al., 2022; Mao et al., 2021).

| Paper | Summary |
|---|---|
| (Peng et al., 2019) | Merumuskan sasaran, sentimen, dan alasan tekstual (Peng et al., 2019) |
| (Zhang et al., 2022) | Menyatukan taksonomi unsur dan tugas gabungan (Zhang et al., 2022) |
| (Mao et al., 2021) | Mengintegrasikan subtugas melalui pembelajaran Dual-MRC (Mao et al., 2021) |

**Figure 3:** Publikasi landasan taksonomi dan ekstraksi triplet sentimen

### 3.2 Pemetaan Istilah

ATE dan OTE menemukan rentang teks, sedangkan ASC mengklasifikasikan sentimen terhadap sasaran tertentu (Xu et al., 2021; Aziz et al., 2024). Menemukan aspek dan opini secara bersamaan belum berarti memasangkannya: ko-ekstraksi dapat menghasilkan dua kumpulan unsur tanpa relasi yang benar (Xu et al., 2021; Zhao et al., 2020).

| Istilah | Masukan | Keluaran | Batas Penting | Bukti |
|---|---|---|---|---|
| ATE | Teks | Aspek \(a\) | Tanpa opini atau sentimen | (Gao et al., 2021) |
| ASC / ALSC | Teks dan aspek | Sentimen \(s\) | Aspek sudah diberikan | (Šmíd & Král, 2025) |
| AOE / TOWE | Teks dan aspek | Opini terkait \(o\) | Bersyarat aspek tertentu | (Wang et al., 2021) |
| ASE, jika aspek–sentimen | Teks | Pasangan \((a,s)\) | Tetapkan kepanjangan eksplisit | (Zhang et al., 2024) |
| AOPE | Teks | Pasangan \((a,o)\) | Tanpa polaritas | (Šmíd & Král, 2025) |
| ASTE | Teks | Triplet \((a,o,s)\) | Pengaitan wajib benar | (Šmíd & Král, 2025) |
| TASD / ACSD | Teks | Triplet \((a,c,s)\) | Tidak mengekstraksi opini | (Šmíd & Král, 2025) |
| ACOS | Teks | Kuadruplet \((a,c,o,s)\) | Mendukung unsur implisit | (Cai et al., 2021) |

**Figure 4:** Perbedaan masukan dan keluaran berbagai subtugas ABSA

Jika **ACO dimaksudkan sebagai Aspect–Category–Opinion**, keluarannya adalah \((a,c,o)\), bukan ASTE, karena tidak mengandung polaritas. Untuk penulisan ilmiah, tuliskan definisi ini secara eksplisit: taksonomi yang tersedia lebih jelas membedakan triplet aspek–kategori–sentimen dari kuadruplet ACOS (Zhang et al., 2024; Šmíd & Král, 2025).

### 3.3 Representasi dan Pengaitan

Pendekatan awal ASTE mengekstraksi unsur sebelum mengklasifikasikan pasangan; JET kemudian memakai penandaan berorientasi posisi, sementara model multitugas menggunakan pengurai dependensi sentimen (Zhang et al., 2022; Xu et al., 2020; Zhang et al., 2020). Penandaan spesifik sasaran juga digunakan untuk triplet bertumpang tindih dan hubungan jarak jauh (Chen et al., 2022).

| Representasi | Cara Kerja | Kekuatan yang Ditargetkan | Bukti |
|---|---|---|---|
| Span | Menghubungkan rentang aspek–opini | Ungkapan multi-kata | (Xu et al., 2021; Li et al., 2022) |
| Grid | Melabeli pasangan token | Relasi dan polaritas bersama | (Izadi et al., 2026) |
| MRC | Menjawab pertanyaan ekstraksi | Pengaitan bersyarat dua arah | (Chen et al., 2021; Gao et al., 2021) |
| Pointer | Menghasilkan batas rentang | Triplet bertumpang tindih | (Mukherjee et al., 2021) |
| Generatif | Menghasilkan urutan tuple | Keluaran terstruktur langsung | (Xu et al., 2023) |

**Figure 5:** Representasi utama untuk menghubungkan unsur triplet sentimen

Penyaringan kelas kata dan sintaksis mengurangi kandidat span yang tidak relevan; Dual-Span melaporkan pengurangan enumerasi hampir separuh (Li et al., 2024; Li et al., 2023). Model lain memperbaiki hubungan melalui representasi dua arah, batas span, serta dependensi antarkeputusan pengklasifikasi (Dai et al., 2022; Xiao et al., 2024; Naglik & Lango, 2024).

### 3.4 Sintaksis dan Supervisi

Informasi sintaksis digunakan untuk menghindari pemasangan opini yang tidak relevan, termasuk tipe dependensi, jarak konstituen, dan representasi graf multi-kanal (Yuan et al., 2024; Hao et al., 2024; Chen et al., 2022). ES-ASTE, SynSem-ASTE, dan SE-ASTE menggabungkan sintaksis dengan representasi semantik, sedangkan SAAG menggunakan AMR serta SenticNet sebagai alternatif informasi sintaksis (Wang et al., 2023; Liu et al., 2024; Shang et al., 2025; Sun et al., 2025).

Penguatan lain mencakup pembelajaran kontrastif pasangan, augmentasi data, umpan balik antartugas, dan bantuan penandaan pada generator (Yang et al., 2023; Liu et al., 2024; Luo et al., 2023). GAC dan MPGM menargetkan ungkapan multi-kata, sedangkan MiniConGTS dan SimSTAR menunjukkan bahwa desain lebih sederhana tetap kompetitif (Xu et al., 2024; Yang et al., 2025; Sun et al., 2024; Li et al., 2023). AttGTS melaporkan pengurangan memori GPU 29% dan pelatihan per epoch 21–27% lebih cepat dalam perbandingan terkontrolnya (Izadi et al., 2026).

### Results Timeline

Linimasa memperlihatkan pergeseran dari klasifikasi aspek menuju ekstraksi relasi terstruktur.

- **Nov 2019**
  - 1 paper: (Peng et al., 2019)
- **Jul 2020**
  - 1 paper: (Zhao et al., 2020)
- **Oct 2020**
  - 2 papers: (Xu et al., 2020; Zhang et al., 2020)
- **Jan 2021**
  - 3 papers: (Fu et al., 2021; Mao et al., 2021; Cai et al., 2021)
- **Mar 2021**
  - 1 paper: (Li et al., 2021)
- **May 2021**
  - 1 paper: (Gao et al., 2021)
- **Jul 2021**
  - 1 paper: (Xu et al., 2021)
- **Oct 2021**
  - 1 paper: (Wang et al., 2021)
- **Nov 2021**
  - 1 paper: (Jing et al., 2021)
- **Jan 2022**
  - 1 paper: (Chen et al., 2022)
- **Feb 2022**
  - 1 paper: (Li et al., 2022)
- **Mar 2022**
  - 1 paper: (Zhang et al., 2022)
- **Jul 2023**
  - 1 paper: (Li et al., 2023)
- **Jan 2024**
  - 1 paper: (Zhang et al., 2024)
- **Jun 2024**
  - 1 paper: (Aziz et al., 2024)
- **Mar 2025**
  - 1 paper: (Šmíd & Král, 2025)
- **Jul 2025**
  - 1 paper: (Chakraborty et al., 2025)
**Figure 6:** Linimasa penelitian; penanda besar menunjukkan lebih banyak sitasi

Model perhatian awal memusatkan representasi pada aspek tertentu; perkembangan berikutnya menghubungkan seluruh unsur menjadi triplet (Wang et al., 2016; Dehong et al., 2017; Chen et al., 2017). Benchmark kemudian memperluas pengujian menuju domain tak terlihat dan ulasan yang lebih realistis (Chia et al., 2023; Xu et al., 2023).

### Top Contributors

Kontributor berikut diurutkan berdasarkan visibilitas dan sitasi publikasi terkait dalam korpus 100 makalah, bukan dampak seluruh bidang.

| Type | Name | Papers |
|------|------|--------|
| Author | Lidong Bing | (Peng et al., 2019; Zhang et al., 2022; Xu et al., 2020; Xu et al., 2021) |
| Author | Wei Lu | (Peng et al., 2019; Xu et al., 2020) |
| Author | Lu Xu | (Peng et al., 2019; Xu et al., 2020; Xu et al., 2021) |
| Journal | *IEEE Transactions on Affective Computing* | (Nazir et al., 2020; Yuan et al., 2024; Liu et al., 2024) |
| Journal | *Neurocomputing* | (Zhao et al., 2023; Akhtar et al., 2020; Chen et al., 2022) |
| Journal | *Knowledge-Based Systems* | (Li et al., 2022; Li et al., 2023; Xu et al., 2024) |

**Figure 7:** Penulis dan jurnal yang menonjol dalam korpus

## 4. Discussion

**Keuntungan model bersama harus dibedakan dari klaim bahwa pipeline selalu buruk.** Pipeline rentan propagasi kesalahan, tetapi ASOTE dan PASTEL memperlihatkan kegunaan dekomposisi yang dirancang secara khusus (Xu et al., 2021; Li et al., 2021; Bodke et al., 2025). Model span sederhana juga dapat mengungguli arsitektur yang lebih rumit, sehingga kompleksitas bukan ukuran kualitas (Xu et al., 2022). Pembelajaran bersama ATE–ASC, transfer representasi ekstraksi, dan supervisi hierarkis membantu tugas pasangan, tetapi hasilnya tidak otomatis membuktikan keberhasilan triplet lengkap (Zhao et al., 2023; Majumder et al., 2020; Xu et al., 2021; Yong & Yang, 2021).

**Semantik anotasi juga menentukan makna hasil.** ASOTE menempatkan sentimen pada pasangan aspek–opini, sedangkan ASMOTE mengelompokkan seluruh opini untuk suatu aspek (Li et al., 2021; Wang et al., 2021). Satu aspek dapat memiliki opini dengan polaritas bertentangan; skema penandaan tertentu tidak dapat merepresentasikannya dengan baik (Li et al., 2023). Demikian pula, dukungan aspek atau opini implisit pada ACOS tidak boleh diasumsikan tersedia pada semua dataset ASTE (Cai et al., 2021; Xiong et al., 2023).

Validitas eksternal masih menjadi batas besar: tinjauan 727 studi menemukan kekurangan keragaman domain, dan benchmark ASTE awal terutama mencakup dua domain (Hua et al., 2023; Chia et al., 2023). Pengujian ARTS menemukan penurunan akurasi hingga 69,73% pada model yang diuji; bias aspek dan perhatian pada kata tak relevan turut menjelaskan kerapuhan klasifikasi (Xing et al., 2020; Zhou et al., 2024; Fangjie et al., 2021). Pelatihan adversarial dan augmentasi memperbaiki ketahanan pada pengaturan tertentu, bukan menjamin transfer universal (Fei et al., 2022; Karimi et al., 2020; Xu et al., 2024).

**Klaim dan Batas Bukti**

| Claim | Evidence Strength | Reasoning | Papers |
|---|---|---|---|
| ASTE memerlukan aspek, opini, sentimen terhubung | Evidence strength: Strong (9/10) | Definisi konsisten lintas formulasi | (Xu et al., 2021; Yang et al., 2024) |
| Representasi span membantu ungkapan multi-kata | Evidence strength: Moderate (7/10) | Dukungan beberapa benchmark | (Xu et al., 2021; Wang et al., 2023) |
| Kinerja benchmark tidak menjamin generalisasi | Evidence strength: Moderate (7/10) | Didukung evaluasi domain dan ketahanan | (Fei et al., 2022; Xu et al., 2023) |
| LLM tanpa pelatihan selalu menggantikan model khusus | Evidence strength: Weak (2/10) | Bukti tidak mendukung klaim universal | (Sun et al., 2024; Nour et al., 2025) |

**Figure 8:** Kekuatan bukti definisi, representasi, dan generalisasi ASTE

## 5. Conclusion

ATE menemukan aspek; ASC mengklasifikasikan aspek yang tersedia; AOE menemukan opini untuk aspek tertentu; dan ASTE menghasilkan hubungan aspek–opini–sentimen. ASE serta ACO sebaiknya selalu disertai kepanjangan dan notasi keluaran agar tidak tertukar dengan tugas lain.

### Research Gaps

Penelitian jauh lebih padat pada ekstraksi terawasi daripada transfer lintas bahasa dan domain. Survei lintas bahasa menilai area transfer ini masih kurang dieksplorasi (Šmíd & Král, 2025).

| | Supervisi Penuh | Supervisi Lemah | Lintas Domain | Lintas Bahasa |
|---|---|---|---|---|
| ATE | 17 papers | 1 paper | 4 papers | 2 papers |
| ASC | 10 papers | No papers | 1 paper | 1 paper |
| AOPE | 7 papers | 1 paper | 1 paper | No papers |
| ASTE | 52 papers | 5 papers | 9 papers | 2 papers |
| ACOS | 7 papers | No papers | 1 paper | 1 paper |
**Figure 9:** Cakupan subtugas ABSA menurut pengaturan supervisi dan transfer

Ketergantungan pada anotasi membatasi skala, meskipun UAOS menunjukkan ASTE lintas domain tanpa penyetelan dalam domain dengan macro-F1 60,56 pada refleksi mahasiswa (Chakraborty et al., 2025). Adaptasi sintaksis lintas delapan domain menawarkan bukti transfer tambahan, tetapi tetap memerlukan pengujian yang berbeda dari pembagian acak dalam domain (Wang et al., 2024).

Bukti Indonesia mencakup adaptasi ko-ekstraksi pada ulasan hotel, sedangkan penelitian Inggris–Hindi dan Arab menunjukkan bahwa kelayakan multilingual belum berarti kesetaraan kinerja antartugas (Khodra, 2022; Akhtar et al., 2020; Bensoltane & Zaki, 2024). Pada ASTE Arab, GPT-4.1 mencapai F1 0,5025 dalam pengaturan lima contoh, dengan pengaitan aspek–opini tetap menjadi hambatan (Nour et al., 2025).

### Open Research Questions

Prioritasnya adalah memperjelas anotasi, menguji pengaitan, dan membandingkan model pada supervisi setara. Instruksi yang menyesatkan menurunkan kinerja InstructABSA sekitar 10%, menunjukkan pentingnya kualitas demonstrasi (Scaria et al., 2023).

| Pertanyaan | Why |
|---|---|
| **Bagaimana menetapkan sentimen untuk opini yang bertentangan pada aspek sama?** | Label tingkat aspek dan tingkat pasangan dapat menghasilkan interpretasi berbeda, sehingga aturan anotasi harus menjelaskan unit sentimen secara eksplisit (Li et al., 2021). |
| **Bagaimana menguji transfer ASTE tanpa mengandalkan domain restoran dan laptop?** | Benchmark yang lebih beragam diperlukan agar peningkatan skor mencerminkan kemampuan menghadapi ulasan nyata, bukan hanya pola domain pelatihan yang berulang (Xu et al., 2023). |
| **Kapan model sederhana lebih efisien daripada pipeline LLM?** | Efisiensi memori, kecepatan, kualitas pengaitan, dan kebutuhan anotasi perlu dibandingkan bersama agar pilihan arsitektur sesuai keterbatasan penggunaan nyata (Izadi et al., 2026). |

**Figure 10:** Pertanyaan terbuka mengenai anotasi, transfer, dan efisiensi

**Untuk ekstraksi triplet yang dimaksudkan dalam pertanyaan ini, istilah paling jelas adalah ASTE dengan keluaran \((aspek, opini, sentimen)\).**
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
D., Li, S., Zhang, X., & Wang, H.-F. (2017). Interactive Attention Networks for Aspect-Level Sentiment Classification. *ArXiv, abs/1709.00893*. https://doi.org/10.24963/ijcai.2017/568
 
F., Zhang, C., & Song, D.-W. (2021). Exploiting Position Bias for Robust Aspect Sentiment Classification. 1352-1358. https://doi.org/10.18653/v1/2021.findings-acl.116
 
Akhtar, M. S., Garg, T., & Ekbal, A. (2020). Multi-task learning for aspect term extraction and aspect sentiment classification. *Neurocomputing, 398*, 247-256. https://doi.org/10.1016/j.neucom.2020.02.093
 
Aziz, K., Ji, D.-H., Chakrabarti, P., Chakrabarti, T., Iqbal, M. S., & Abbasi, R. (2024). Unifying aspect-based sentiment analysis BERT and multi-layered graph convolutional networks for comprehensive sentiment dissection. *Scientific Reports, 14*. https://doi.org/10.1038/s41598-024-61886-7
 
Bensoltane, R., & Zaki, T. (2024). Neural multi-task learning for end-to-end Arabic aspect-based sentiment analysis. *Comput. Speech Lang., 89*, 101683. https://doi.org/10.1016/j.csl.2024.101683
 
Bodke, A., Kohli, A. S., Pardeshi, H., & Bhosale, P. (2025). PASTEL : Polarity-Aware Sentiment Triplet Extraction with LLM-as-a-Judge. 25523-25533. https://doi.org/10.18653/v1/2025.findings-acl.1309
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chakraborty, M., Kulkarni, A., & Li, Q. (2025). Weakly Supervised Open-Domain Aspect-Based Sentiment Analysis. *ACM Transactions on Knowledge Discovery from Data, 19*, 1 - 29. https://doi.org/10.1145/3747849
 
Chen, F., Yang, Z., & Huang, Y. (2022). A multi-task learning framework for end-to-end aspect sentiment triplet extraction. *Neurocomputing, 479*, 12-21. https://doi.org/10.1016/j.neucom.2022.01.021
 
Chen, S., Wang, Y., Liu, J., & Wang, Y.-L. (2021). Bidirectional Machine Reading Comprehension for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2103.07665*. https://doi.org/10.1609/aaai.v35i14.17500
 
Chen, H., Zhai, Z., Feng, F., Li, R., & Wang, X. (2022). Enhanced Multi-Channel Graph Convolutional Network for Aspect Sentiment Triplet Extraction. 2974-2985. https://doi.org/10.18653/v1/2022.acl-long.212
 
Chen, P., Sun, Z.-Q., Bing, L., & Yang, W. (2017). Recurrent Attention Network on Memory for Aspect Sentiment Analysis. 452-461. https://doi.org/10.18653/v1/d17-1047
 
Chia, Y. K., Chen, H., Han, W., Chen, G., Aljunied, S. M., Poria, S., & Bing, L. (2023). Domain-Expanded ASTE: Rethinking Generalization in Aspect Sentiment Triplet Extraction. *ArXiv, abs/2305.14434*. https://doi.org/10.48550/arxiv.2305.14434
 
Dai, D., Chen, T., Xia, S., Wang, G., & Chen, Z.-Z. (2022). Double embedding and bidirectional sentiment dependence detector for aspect sentiment triplet extraction. *Knowl. Based Syst., 253*, 109506. https://doi.org/10.1016/j.knosys.2022.109506
 
Fei, H., Chua, T.-S., Li, C., Ji, D.-H., Zhang, M., & Ren, Y.-F. (2022). On the Robustness of Aspect-based Sentiment Analysis: Rethinking Model, Data, and Training. *ACM Transactions on Information Systems, 41*, 1 - 32. https://doi.org/10.1145/3564281
 
Fu, Y., Liao, J., Li, Y., Wang, S.-G., Li, D.-Y., & Li, X. (2021). Multiple perspective attention based on double BiLSTM for aspect and sentiment pair extract. *Neurocomputing, 438*, 302-311. https://doi.org/10.1016/j.neucom.2021.01.079
 
Gao, L., Wang, Y., Liu, T., Wang, J.-Y., Zhang, L., & Liao, J. (2021). Question-Driven Span Labeling Model for Aspect-Opinion Pair Extraction. 12875-12883. https://doi.org/10.1609/aaai.v35i14.17523
 
Hao, S.-F., Zhou, Y., Liu, P., & Xu, S. (2024). Bi-syntax guided transformer network for aspect sentiment triplet extraction. *Neurocomputing, 594*, 127880. https://doi.org/10.1016/j.neucom.2024.127880
 
Hua, Y. C., Denny, P., Wicker, J., & Taškova, K. (2023). A systematic review of aspect-based sentiment analysis: domains, methods, and trends. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-024-10906-z
 
Izadi, A., Shahrokhzadeh, B., & Masoumi, B. (2026). AttGTS: A Lightweight Contrastive-Free Grid-Tagging Model With Scheduled Token-Level Attention for Aspect Sentiment Triplet Extraction. *IEEE Access, 14*, 114845-114855. https://doi.org/10.1109/access.2026.3713095
 
Jing, H., Li, Z.-C., Zhao, H., & Jiang, S. (2021). Seeking Common but Distinguishing Difference, A Joint Aspect-based Sentiment Analysis Model. 3910-3922. https://doi.org/10.18653/v1/2021.emnlp-main.318
 
Karimi, A., Rossi, L., Prati, A., & Full, K. (2020). Adversarial Training for Aspect-Based Sentiment Analysis with BERT. *2020 25th International Conference on Pattern Recognition (ICPR)*, 8797-8803. https://doi.org/10.1109/icpr48806.2021.9412167
 
Khodra, M. L. (2022). Opinion Triplet Extraction for Aspect-Based Sentiment Analysis Using Co-Extraction Approach. *Journal of Information and Communication Technology*. https://doi.org/10.32890/jict2022.21.2.5
 
Li, J., Li, X.-Y., Du, Y.-J., Fan, Y., Chen, X.-L., & Huang, D. (2023). An Aspect-Category-Opinion-Sentiment Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. *Inf. Technol. Control., 52*, 445-456. https://doi.org/10.5755/j01.itc.52.2.32903
 
Li, Y., Wang, F., Zhang, W., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). A More Fine-Grained Aspect-Sentiment-Opinion Triplet Extraction Task. *ArXiv, abs/2103.15255*. https://doi.org/10.3390/math11143165
 
Li, Y., Lin, Y.-D., Lin, Y.-M., Chang, L., & Zhang, H. (2022). A span-sharing joint extraction framework for harvesting aspect sentiment triplets. *Knowl. Based Syst., 242*, 108366. https://doi.org/10.1016/j.knosys.2022.108366
 
Li, Q., Wen, W.-S., & Qin, J.-H. (2024). Improving span-based Aspect Sentiment Triplet Extraction with part-of-speech filtering and contrastive learning. *Neural networks : the official journal of the International Neural Network Society, 177*, 106381. https://doi.org/10.1016/j.neunet.2024.106381
 
Li, P., Li, P., & Zhang, K. (2023). Dual-Channel Span for Aspect Sentiment Triplet Extraction. 248-261. https://doi.org/10.18653/v1/2023.emnlp-main.17
 
Li, D., Yang, Z.-H., Lan, Y., Zhang, Y.-Q., Zhao, H., & Zhao, G. (2023). Simple Approach for Aspect Sentiment Triplet Extraction Using Span-Based Segment Tagging and Dual Extractors. *Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval*. https://doi.org/10.1145/3539618.3592060
 
Li, P., Li, P., & Xiao, X. (2023). Aspect-Pair Supervised Contrastive Learning for aspect-based sentiment analysis. *Knowl. Based Syst., 274*, 110648. https://doi.org/10.1016/j.knosys.2023.110648
 
Liu, L., Qin, T., Zhou, Y., Wang, C.-X., & Guan, X.-H. (2024). SynSem-ASTE: An Enhanced Multi-Encoder Network for Aspect Sentiment Triplet Extraction With Syntax and Semantics. *IEEE Transactions on Affective Computing, 15*, 2097-2111. https://doi.org/10.1109/taffc.2024.3397961
 
Liu, S., Lu, T.-T., Li, K.-W., & Liu, W. (2024). Aspect sentiment triplet extraction based on data augmentation and task feedback. *Journal of Intelligent Information Systems, 62*, 1659 - 1683. https://doi.org/10.1007/s10844-024-00855-y
 
Luo, X., Yang, M., & Wang, Y.-H. (2023). Tagging-Assisted Generation Model with Encoder and Decoder Supervision for Aspect Sentiment Triplet Extraction. 2078-2093. https://doi.org/10.18653/v1/2023.emnlp-main.129
 
Majumder, N., Bhardwaj, R., Poria, S., Zadeh, A., Gelbukh, A., Hussain, A., & Morency, L. (2020). Improving aspect-level sentiment analysis with aspect extraction. *Neural Computing and Applications, 34*, 8333 - 8343. https://doi.org/10.1007/s00521-020-05287-7
 
Mao, Y., Shen, Y., Yu, C., & Cai, L. (2021). A Joint Training Dual-MRC Framework for Aspect Based Sentiment Analysis. *ArXiv, abs/2101.00816*. https://doi.org/10.1609/aaai.v35i15.17597
 
Mukherjee, R., Nayak, T., Butala, Y., Bhattacharya, S., & Goyal, P. (2021). PASTE: A Tagging-Free Decoding Framework Using Pointer Networks for Aspect Sentiment Triplet Extraction. 9279-9291. https://doi.org/10.18653/v1/2021.emnlp-main.731
 
Naglik, I., & Lango, M. (2024). ASTE Transformer Modelling Dependencies in Aspect-Sentiment Triplet Extraction. *ArXiv, abs/2409.15202*. https://doi.org/10.48550/arxiv.2409.15202
 
Nazir, A., Rao, Y., Wu, L., & Sun, L. (2020). Issues and Challenges of Aspect-based Sentiment Analysis: A Comprehensive Survey. *IEEE Transactions on Affective Computing, 13*, 845-863. https://doi.org/10.1109/taffc.2020.2970399
 
Nour, R., Abdalgwad, S., Noseer, M., Abobakr, A., Galhom, A., & Fares, A. (2025). Evaluating Large Language Models for Arabic Aspect Sentiment Triplet Extraction using Zero, One, and Few-Shot Prompting. *2025 13th International Japan-Africa Conference on Electronics, Communications, and Computations (JAC-ECC)*, 327-330. https://doi.org/10.1109/jac-ecc67970.2025.11417612
 
Peng, H.-Y., Xu, L., Bing, L., Huang, F., Lu, W., & Si, L. (2019). Knowing What, How and Why: A Near Complete Solution for Aspect-based Sentiment Analysis. 8600-8607. https://doi.org/10.1609/aaai.v34i05.6383
 
Scaria, K., Gupta, H., Goyal, S., Sawant, S. A., Mishra, S., & Baral, C. (2023). InstructABSA: Instruction Learning for Aspect Based Sentiment Analysis. *ArXiv, abs/2302.08624*. https://doi.org/10.48550/arxiv.2302.08624
 
Shang, J.-X., Zhang, Y., Zhong, L., & Li, R.-Y. (2025). Syntactic-Enhanced Multi-Task Learning Model for Aspect Sentiment Triplet Extraction. *Data Science and Engineering, 10*, 515 - 531. https://doi.org/10.1007/s41019-025-00289-8
 
Šmíd, J., & Král, P. (2025). Cross-lingual aspect-based sentiment analysis: A survey on tasks, approaches, and challenges. *ArXiv, abs/2508.09516*. https://doi.org/10.1016/j.inffus.2025.103073
 
Sun, X., Qi, J.-T., Zhu, Z.-F., Li, M., Pei, H., & Meng, J. (2025). SenticNet and Abstract Meaning Representation driven Attention-Gate semantic framework for aspect sentiment triplet extraction. *Eng. Appl. Artif. Intell., 139*, 109625. https://doi.org/10.1016/j.engappai.2024.109625
 
Sun, Q., Yang, L., M., Ye, N.-Y., & Gu, Q.-Y. (2024). MiniConGTS: A Near Ultimate Minimalist Contrastive Grid Tagging Scheme for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2406.11234*. https://doi.org/10.48550/arxiv.2406.11234
 
Wang, F., Li, Y., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). Aspect-Sentiment-Multiple-Opinion Triplet Extraction. 583-594. https://doi.org/10.1007/978-3-030-88480-2_46
 
Wang, Y.-D., Chen, Z.-T., & Chen, S. (2023). ES-ASTE: enhanced span-level framework for aspect sentiment triplet extraction. *Journal of Intelligent Information Systems*, 1-20. https://doi.org/10.1007/s10844-023-00783-3
 
Wang, Y., Huang, M., Zhu, X.-Y., & Zhao, L. (2016). Attention-based LSTM for Aspect-level Sentiment Classification. 606-615. https://doi.org/10.18653/v1/d16-1058
 
Wang, G.-J., Wang, B., Xu, F.-Y., Wang, R., Zhu, Z.-F., & Liu, P. (2024). Domain-consistent syntactic representation for cross-domain aspect sentiment triplet extraction. *Expert Syst. Appl., 256*, 124854. https://doi.org/10.1016/j.eswa.2024.124854
 
Xiao, X., Gao, B., Su, Z., Li, L., Li, Y.-T., Liu, S.-T., & Liu, Z.-J. (2024). STBA: span-based tagging scheme with biaffine attention for enhanced aspect sentiment triplet extraction. *Pattern Analysis and Applications, 27*. https://doi.org/10.1007/s10044-024-01377-7
 
Xing, X., Jin, Z., Jin, D., Wang, B.-N., Zhang, Q., & Huang, X. (2020). Tasty Burgers, Soggy Fries: Probing Aspect Robustness in Aspect-Based Sentiment Analysis. *ArXiv, abs/2009.07964*. https://doi.org/10.18653/v1/2020.emnlp-main.292
 
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
 
Xu, L., Chia, Y. K., & Bing, L. (2021). Learning Span-Level Interactions for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2107.12214*. https://doi.org/10.18653/v1/2021.acl-long.367
 
Xu, L., Li, H., Lu, W., & Bing, L. (2020). Position-Aware Tagging for Aspect Sentiment Triplet Extraction. 2339-2349. https://doi.org/10.18653/v1/2020.emnlp-main.183
 
Xu, T., Yang, H., Wu, Z., Chen, J.-Z., Zhao, F., & Dai, X.-Y. (2023). Measuring Your ASTE Models in The Wild: A Diversified Multi-domain Dataset For Aspect Sentiment Triplet Extraction. 2837-2853. https://doi.org/10.48550/arxiv.2305.17448
 
Xu, H., Tang, M., Cai, T., Hu, J., & Zhao, M. (2024). Dual-enhanced generative model with graph attention network and contrastive learning for aspect sentiment triplet extraction. *Knowl. Based Syst., 301*, 112342. https://doi.org/10.1016/j.knosys.2024.112342
 
Xu, K., Li, F., Xie, D., & Ji, D.-H. (2022). Revisiting Aspect-Sentiment-Opinion Triplet Extraction: Detailed Analyses Towards a Simple and Effective Span-Based Model. *IEEE/ACM Transactions on Audio, Speech, and Language Processing, 30*, 2918-2927. https://doi.org/10.1109/taslp.2022.3202122
 
Xu, G.-L., Zhang, Z., Jin, L., & Sun, X. (2021). End-to-end aspect-based sentiment analysis with hierarchical multi-task learning. *Neurocomputing, 455*, 178-188. https://doi.org/10.1016/j.neucom.2021.03.100
 
Xu, E., Zhu, J., Zhang, L., Wang, Y., & Lin, W. (2024). Research on Aspect-Level Sentiment Analysis Based on Adversarial Training and Dependency Parsing. *Electronics*. https://doi.org/10.3390/electronics13101993
 
Yang, F., Zhang, M., Hu, G., & Zhou, X. (2023). A Pairing Enhancement Approach for Aspect Sentiment Triplet Extraction. 399-410. https://doi.org/10.48550/arxiv.2306.10042
 
Yang, K., Zong, L., Tang, M., Hu, J., Zheng, Y., Chen, Y., & Zhao, M. (2025). MPGM:Multi-prompt generation model with self-supervised contrastive learning for aspect sentiment triplet extraction. *Neural networks : the official journal of the International Neural Network Society, 192*, 107894. https://doi.org/10.1016/j.neunet.2025.107894
 
Yang, X., Peng, T., Bi, H.-J., & Han, J. (2024). Span-level bidirectional retention scheme for aspect sentiment triplet extraction. *Inf. Process. Manag., 61*, 103823. https://doi.org/10.1016/j.ipm.2024.103823
 
Yong, B., & Yang, Y. (2021). A multitask multiview neural network for end-to-end aspect-based sentiment analysis. *Big Data Min. Anal., 4*, 195-207. https://doi.org/10.26599/bdma.2021.9020003
 
Yuan, L., Wang, J., Yu, L.-C., & Zhang, X.-J. (2024). Encoding Syntactic Information into Transformers for Aspect-Based Sentiment Triplet Extraction. *IEEE Transactions on Affective Computing, 15*, 722-735. https://doi.org/10.1109/taffc.2023.3291730
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, C., Li, Q., Song, D.-W., & Wang, B. (2020). A Multi-task Learning Framework for Opinion Triplet Extraction. *ArXiv, abs/2010.01512*. https://doi.org/10.18653/v1/2020.findings-emnlp.72
 
Zhao, H., Huang, L., Zhang, R., Lu, Q., & Xue, H. (2020). SpanMlt: A Span-based Multi-Task Learning Framework for Pair-wise Aspect and Opinion Terms Extraction. 3239-3248. https://doi.org/10.18653/v1/2020.acl-main.296
 
Zhao, G.-S., Luo, Y., Chen, Q., & Qian, X. (2023). Aspect-based sentiment analysis via multitask learning for online reviews. *Knowl. Based Syst., 264*, 110326. https://doi.org/10.1016/j.knosys.2023.110326
 
Zhou, J., Lin, Y.-M., Chen, Q., Zhang, Q., Huang, X.-J., & He, L. (2024). CausalABSC: Causal Inference for Aspect Debiasing in Aspect-Based Sentiment Classification. *IEEE/ACM Transactions on Audio, Speech, and Language Processing, 32*, 830-840. https://doi.org/10.1109/taslp.2023.3340606
 
