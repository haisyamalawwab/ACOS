# ASTE **lebih informatif** daripada ABSA standar, tetapi **keunggulan akurasi** terutama terlihat pada benchmark terkontrol, bukan otomatis pada ulasan informal lintas-domain.


Literaturnya mendukung bahwa ASTE memberi keluaran yang lebih lengkap dan lebih dapat ditindaklanjuti daripada sub-tugas ABSA standar, karena ASTE mengekstrak aspek, opini, dan polaritas sekaligus. Namun, untuk ulasan informal lintas-domain, bukti tidak menunjukkan bahwa ASTE otomatis lebih robust; performa tetap turun pada review yang lebih panjang, lebih kompleks, mengandung aspek implisit, atau bergeser domain (Zhang et al., 2022; Lai et al., 2026; Xu et al., 2023; Chia et al., 2023).
**Figure 1:** Konsensus tentang keunggulan ASTE atas ABSA standar

## Keunggulan Representasi

ASTE adalah sub-tugas ABSA yang paling terintegrasi, karena mengekstrak triplet aspek-opini-sentimen dalam satu keluaran, bukan hanya aspek atau polaritas secara terpisah (Jiang et al., 2023; Xu et al., 2021; Zhang et al., 2022; Hong et al., 2026). Dibanding ABSA standar yang sering memecah masalah menjadi ATE, OTE, dan ASC, ASTE memberi jawaban atas “apa yang dinilai, bagaimana sentimennya, dan mengapa” dalam satu struktur yang lebih interpretabel (Yuan et al., 2024; Lai et al., 2026; Wang et al., 2021; Chen et al., 2021).

ASTE juga lebih dekat ke kebutuhan aplikasi nyata seperti analisis opini, rekomendasi yang dapat dijelaskan, analisis atribut produk, dan ringkasan review, karena opini span dipertahankan sebagai rasional eksplisit untuk label sentimen (Lai et al., 2026; Liang et al., 2022; Ahmad et al., 2025). Beberapa survei menyimpulkan bahwa ASTE memberi “more complete sentiment information” daripada model ABSA yang hanya menangani elemen tunggal atau pasangan elemen (Zhang et al., 2022; Zhang et al., 2024).

Perbandingan fungsi tugas ABSA dan ASTE

| Tugas | Keluaran | Keterbatasan utama vs ASTE | Bukti |
|---|---|---|---|
| ATE/OTE/ASC terpisah | aspek, opini, atau polaritas saja | perlu digabungkan lagi; relasi antarelemen tidak eksplisit | (Jiang et al., 2023) |
| ABSA dua-elemen seperti AOPE/AESC | pasangan aspek-opini atau aspek-sentimen | tidak memodelkan ketiga elemen sekaligus | (Huang et al., 2026) |
| ASTE | aspek + opini + polaritas | lebih sulit, tetapi paling lengkap | (Jiang et al., 2023) |

**Figure 2:** Perbandingan keluaran ASTE dan sub-tugas ABSA

## Benchmark Kinerja

Pada benchmark ASTE-Data-V2 klasik di domain restaurant dan laptop, model ASTE modern biasanya berada di kisaran F1 sekitar 0.63–0.74, tergantung domain dan arsitektur (Mukherjee et al., 2023; Li et al., 2023). Dalam tabel komparatif yang luas, CONTRASTE-MTL mencapai F1 0.740 pada 14Res, 0.661 pada 15Res, 0.742 pada 16Res, dan 0.629 pada Lap14, melampaui PARAPHRASE, SBSK-ASTE, dan Span-BiDir pada kumpulan data itu (Mukherjee et al., 2023).

Kenaikan performa ASTE terbaru umumnya inkremental, bukan lompatan besar. SE-ASTE melaporkan rata-rata peningkatan F1 1.45% atas baseline di ASTE-Data-V2 (Shang et al., 2025). Template yang lebih baik dan pretraining kontrasif berbasis aspek pada CONTRASTE memberi kenaikan sekitar 0.9% atas PARAPHRASE hanya dari template, lalu tambahan sekitar 0.6% dibanding contrastive pretraining di level kalimat, dan total 4.4% di atas PARAPHRASE untuk model multi-task final (Mukherjee et al., 2023).

Benchmark ASTE terpilih pada dataset klasik

| Model | 14Res F1 | 15Res F1 | 16Res F1 | Lap14 F1 | Catatan | Bukti |
|---|---:|---:|---:|---:|---|---|
| PARAPHRASE | 0.715 | 0.621 | 0.719 | 0.604 | baseline generatif kuat | (Mukherjee et al., 2023) |
| Span-ASTE | 0.719 | 0.633 | 0.703 | 0.594 | kuat pada span multi-kata | (Mukherjee et al., 2023; Xu et al., 2021) |
| Span-BiDir | 0.743 | 0.648 | 0.721 | 0.627 | kuat pada multi-triplet | (Mukherjee et al., 2023; Chen et al., 2022) |
| CONTRASTE-MTL | 0.740 | 0.661 | 0.742 | 0.629 | SOTA pada tabel ini | (Mukherjee et al., 2023) |
| DGCNAP | 0.7072 | 0.6119 | 0.6958 | 0.5757 | graph + affective knowledge | (Li et al., 2023) |

**Figure 3:** Benchmark ASTE pada dataset restaurant dan laptop

## Di Mana ASTE Unggul

Keunggulan teknis ASTE paling konsisten muncul saat model harus menjaga hubungan antara span aspek dan span opini, terutama jika keduanya multi-kata atau saling tumpang tindih (Xu et al., 2021; Chen et al., 2022; Liu et al., 2025). Span-ASTE menunjukkan perbaikan yang lebih besar pada triplet dengan target atau opini multi-kata (Xu et al., 2021). Span-BiDir juga melaporkan hasil lebih baik pada entitas multi-token dan kalimat dengan banyak triplet (Chen et al., 2022).

Banyak paper menekankan bahwa pipeline ABSA tradisional rentan terhadap error propagation ketika subtugas ditumpuk, sedangkan ASTE end-to-end berusaha mengurangi masalah ini dengan memodelkan elemen secara bersama (Jiang et al., 2023; Li et al., 2024; Huan et al., 2022; Li et al., 2023; Chen et al., 2021). Namun keuntungan itu datang dengan biaya pemodelan yang lebih sulit: batas span, pairing aspek-opini, dan polaritas harus benar secara simultan agar triplet dihitung benar (Lai et al., 2026; Mukherjee et al., 2023).

Fitur sintaktik, relasi kata, dan pembelajaran span tampak menjadi sumber perbaikan paling konsisten di ASTE modern (Yuan et al., 2024; Chen et al., 2022; Xia et al., 2024; Shi et al., 2023). Banyak model baru menyasar titik lemah yang sama: boundary multi-kata, pairing yang salah pada kalimat multi-aspek, dan dependensi jarak jauh (Zhang et al., 2022; Yang et al., 2023; Li & Luo, 2026; Li et al., 2026).

## Ulasan Informal dan Pergeseran Domain

Bukti terkuat untuk ulasan informal domain-spesifik justru menunjukkan bahwa benchmark klasik terlalu mudah. DMASTE dibangun karena dataset ASTE lama terutama hanya dua domain, review pendek sekitar 16 kata, tanpa aspek implisit, dan ekspresi yang relatif sederhana (Xu et al., 2023). DMASTE memperluas ini menjadi delapan domain, rata-rata hampir 60 kata per review, kosa kata sekitar tiga kali lebih besar, dan 11,945 triplet dengan aspek implisit (Xu et al., 2023).

Pada DMASTE, performa model ASTE turun tajam. Span-ASTE yang mencapai 59.38 pada laptop klasik hanya mendapat 47.86 pada domain Electronics DMASTE (Xu et al., 2023). Dalam setting in-domain DMASTE, F1 rata-rata hanya 41.64 untuk BMRC, 42.24 untuk BART-ABSA, 46.61 untuk GAS, dan 48.46 untuk Span-ASTE (Xu et al., 2023). Penurunan ini terutama didorong oleh review panjang, kalimat lebih kompleks, dan aspek implisit (Xu et al., 2023).

Realisme dataset ASTE lintas-domain

| Dataset | Domain | Panjang rata-rata | Aspek implisit | Implikasi | Bukti |
|---|---:|---:|---:|---|---|
| ASTE klasik | 2 | ~16 kata | tidak ada | benchmark sempit | (Xu et al., 2023) |
| DMASTE | 8 | 59.68 kata | 11,945 triplet | lebih dekat ke review dunia nyata | (Xu et al., 2023) |
| Domain-expanded ASTE | 4 | 16.37–21.92 token | eksplisit saja | uji in/out-of-domain lebih realistis | (Chia et al., 2023) |

**Figure 4:** Perbedaan benchmark klasik dan dataset ASTE realistis

## Generalisasi dan Robustness

Untuk domain shift, hasilnya campuran. Pada benchmark domain-expanded empat domain, metode generatif seperti GAS dan Paraphrase cenderung lebih robust ke domain tak terlihat daripada metode diskriminatif, dengan gap in-domain ke out-of-domain lebih kecil, 14.58 vs 16.80 rata-rata (Chia et al., 2023). Di sana, GAS memperoleh rata-rata F1 62.41 in-domain dan 47.76 out-of-domain; dengan CASE naik menjadi 63.13 dan 48.60 (Chia et al., 2023).

Tetapi tidak ada bukti kuat bahwa ASTE sebagai kelas tugas otomatis lebih robust daripada ABSA standar terhadap bahasa informal, typo, slang, atau domain drift. Survei robustness ABSA menegaskan bahwa model ABSA dengan akurasi in-house tinggi sering gagal pada konteks dunia nyata yang berubah, dan perbaikannya perlu data sintetis, adversarial training, dan contrastive learning (Fei et al., 2022). Survei implicit ABSA juga menyebut compound tasks seperti triplet extraction masih kurang dieksplorasi untuk implicit sentiment dan generalisasi domain (Jia et al., 2026).

Setting lintas-domain ASTE yang lebih realistis bahkan menunjukkan negative transfer dan korelasi positif antara similarity domain dan F1 transfer (Xu et al., 2023). Adversarial training sederhana tidak menyelesaikan masalah ini; pada DMASTE, ia malah menurunkan performa karena feature collapse dan hilangnya diskriminasi kategori halus yang dibutuhkan ASTE (Xu et al., 2023).

Benchmark generalisasi ASTE lintas-domain

| Setting | Model kuat | F1 rata-rata | Inti temuan | Bukti |
|---|---|---:|---|---|
| DMASTE in-domain | Span-ASTE | 48.46 | real-world jauh lebih sulit | (Xu et al., 2023) |
| Domain-expanded in-domain | GAS+CAGE/CASE | 63.13 | generatif kompetitif | (Chia et al., 2023) |
| Domain-expanded out-of-domain | GAS+CAGE/CASE | 48.60 | robust, tetapi tetap turun besar | (Chia et al., 2023) |
| DMASTE single-source cross-domain | Span-ASTE | 42.09 | transfer masih lemah | (Xu et al., 2023) |

**Figure 5:** Performa ASTE pada setting lintas-domain dan realistis

## Batasan dan Implikasi Praktis

ASTE bukan sekadar “ABSA yang lebih akurat”; ASTE adalah formulasi yang lebih kaya, tetapi juga lebih keras dievaluasi karena triplet hanya benar bila aspek, opini, dan sentimen semuanya tepat serta konsisten (Lai et al., 2026; Zhang et al., 2022). Karena itu, angka F1 ASTE tidak sebanding langsung dengan skor pada tugas ABSA yang lebih mudah seperti ASC atau AESC (Mukherjee et al., 2023).

Ada juga keterbatasan konseptual pada ASTE itu sendiri. Beberapa penulis menunjukkan bahwa ASTE bisa membingungkan bila satu aspek memiliki beberapa opini dengan sentimen berbeda, atau bila sentimen triplet mewakili sentimen kalimat terhadap aspek alih-alih sentimen pasangan aspek-opini secara ketat (Li et al., 2021; Wang et al., 2021). Ini mendorong tugas turunan seperti ASOTE dan ASMOTE yang mencoba membuat rasional opini lebih lengkap (Li et al., 2021; Wang et al., 2021).

Bahasa dan domain baru juga masih menjadi bottleneck. Paper ASTE untuk Bangla dan Polish menekankan kelangkaan dataset dan perlunya benchmark bahasa non-Inggris untuk review e-commerce nyata (Islam et al., 2025; Lango et al., 2024). Bahkan studi “train once for all” terbaru masih menyatakan sistem terbaik ASTE umumnya hanya berada di sekitar 60–70% pada benchmark umum, jadi akurasi praktis belum matang sepenuhnya (Hou et al., 2024).

Secara keseluruhan, keuntungan utama ASTE atas ABSA standar pada ulasan informal domain-spesifik adalah **kelengkapan struktur keluaran**, bukan jaminan **robustness** atau **akurasi lebih tinggi** di semua kondisi. Pergeseran terpenting dalam literatur adalah perpindahan dari subtugas ABSA terpisah ke ekstraksi triplet terintegrasi yang menyimpan alasan opini. Pertanyaan terbuka terbesarnya adalah bagaimana mempertahankan kelengkapan itu pada review yang panjang, implisit, informal, dan lintas-domain tanpa penurunan F1 yang besar.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Ahmad, W., Khan, H. U., Alarfaj, F., & Alreshoodi, M. (2025). Aspect-Based Sentiment Analysis: A Comprehensive Review and Open Research Challenges. *IEEE Access, 13*, 65138-65182. https://doi.org/10.1109/access.2025.3555744
 
Chen, Z.-X., Huang, H., Liu, B., Shi, X.-H., & Jin, H. (2021). Semantic and Syntactic Enhanced Aspect Sentiment Triplet Extraction. 1474-1483. https://doi.org/10.18653/v1/2021.findings-acl.128
 
Chen, Y., Chen, K., Sun, X., & Zhang, Z. (2022). A Span-level Bidirectional Network for Aspect Sentiment Triplet Extraction. 4300-4309. https://doi.org/10.18653/v1/2022.emnlp-main.289
 
Chen, H., Zhai, Z., Feng, F., Li, R., & Wang, X. (2022). Enhanced Multi-Channel Graph Convolutional Network for Aspect Sentiment Triplet Extraction. 2974-2985. https://doi.org/10.18653/v1/2022.acl-long.212
 
Chia, Y. K., Chen, H., Han, W., Chen, G., Aljunied, S. M., Poria, S., & Bing, L. (2023). Domain-Expanded ASTE: Rethinking Generalization in Aspect Sentiment Triplet Extraction. *ArXiv, abs/2305.14434*. https://doi.org/10.48550/arxiv.2305.14434
 
Fei, H., Chua, T.-S., Li, C., Ji, D.-H., Zhang, M., & Ren, Y.-F. (2022). On the Robustness of Aspect-based Sentiment Analysis: Rethinking Model, Data, and Training. *ACM Transactions on Information Systems, 41*, 1 - 32. https://doi.org/10.1145/3564281
 
Hong, A., Wang, L.-H., Yue, Z.-R., Wang, M.-X., Wang, Z.-H., & Liu, H.-D. (2026). MASTE: A Multi-Agent Pipeline for Zero-Shot Aspect Sentiment Triplet Extraction. *ArXiv, abs/2607.08080*. https://doi.org/10.48550/arxiv.2607.08080
 
Hou, X.-M., Fu, L., Meng, C.-H., Du, K., Wang, W.-Q., & Hu, H. (2024). Train Once for All: A Transitional Approach for Efficient Aspect Sentiment Triplet Extraction. *ArXiv, abs/2412.00208*. https://doi.org/10.48550/arxiv.2412.00208
 
Huan, H., He, Z., Xie, Y.-Q., & Guo, Z.-L. (2022). A Multi-Task Dual-Encoder Framework for Aspect Sentiment Triplet Extraction. *IEEE Access, 10*, 103187-103199. https://doi.org/10.1109/access.2022.3210180
 
Huang, Y., Zhou, X., Yin, R., & Shi, P. (2026). External-knowledge enhanced dual encoder and contrastive learning for aspect sentiment triplet extraction. *PLOS One, 21*. https://doi.org/10.1371/journal.pone.0340792
 
Islam, A., Hossen, M. R., Ahmed, A., & Haque, B. T. M. (2025). BanglaASTE: A Novel Framework for Aspect-Sentiment-Opinion Extraction in Bangla E-commerce Reviews Using Ensemble Deep Learning. *2025 IEEE International Conference on Signal Processing, Information, Communication and Systems (SPICSCON)*, 738-743. https://doi.org/10.1109/spicscon69221.2025.11504105
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Jiang, B., Liang, S.-H., Liu, P., Dong, K., & Li, H. (2023). A semantically enhanced dual encoder for aspect sentiment triplet extraction. *ArXiv, abs/2306.08373*. https://doi.org/10.48550/arxiv.2306.08373
 
Lai, W., Xie, H., Xu, G., Li, Q., & Qin, S. (2026). Fine-grained Verification via Diagnostic Reasoning Supervision for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2605.31446*. https://doi.org/10.48550/arxiv.2605.31446
 
Lango, M., Naglik, B., Lango, M., & Naglik, I. (2024). Polish-ASTE: Aspect-Sentiment Triplet Extraction Datasets for Polish. 12821-12828. https://doi.org/10.48550/arxiv.2502.20046
 
Li, Y.-B., He, Q., & Zhang, D.-M. (2023). Dual graph convolutional networks integrating affective knowledge and position information for aspect sentiment triplet extraction. *Frontiers in Neurorobotics, 17*. https://doi.org/10.3389/fnbot.2023.1193011
 
Li, Y.-B., He, Q., & Yang, L. (2024). Part-of-speech based label update network for aspect sentiment triplet extraction. *Journal of King Saud University Computer and Information Sciences, 36*. https://doi.org/10.1016/j.jksuci.2023.101908
 
Li, S., & Luo, W. (2026). Knowledge-Augmented Graph Convolutional Network for Aspect Sentiment Triplet Extraction. *Applied Sciences*. https://doi.org/10.3390/app16031250
 
Li, Y., Chen, S., Peng, X.-Y., & Lin, Y.-M. (2026). Span labeling with sentiment-aware GCN and multi-channel contrastive learning for aspect sentiment triplet extraction. *Multimedia Systems, 32*. https://doi.org/10.1007/s00530-026-02364-0
 
Li, Y., Wang, F., Zhang, W., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). A More Fine-Grained Aspect-Sentiment-Opinion Triplet Extraction Task. *ArXiv, abs/2103.15255*. https://doi.org/10.3390/math11143165
 
Liang, S., Wei, W., Mao, X.-L., Fu, Y., Fang, R., & Chen, D.-Y. (2022). STAGE: Span Tagging and Greedy Inference Scheme for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2211.15003*. https://doi.org/10.48550/arxiv.2211.15003
 
Liu, G., Zhao, Y., & Shen, B. (2025). A Span-based Enhanced Bidirectional Extraction Framework for Multi-word Aspect Sentiment Triplets. *Journal of Internet Technology*. https://doi.org/10.70003/160792642025032602005
 
Mukherjee, R., Kannen, N., Pandey, S., & Goyal, P. (2023). CONTRASTE: Supervised Contrastive Pre-training With Aspect-based Prompts For Aspect Sentiment Triplet Extraction. *ArXiv, abs/2310.15577*. https://doi.org/10.48550/arxiv.2310.15577
 
Shang, J.-X., Zhang, Y., Zhong, L., & Li, R.-Y. (2025). Syntactic-Enhanced Multi-Task Learning Model for Aspect Sentiment Triplet Extraction. *Data Science and Engineering, 10*, 515 - 531. https://doi.org/10.1007/s41019-025-00289-8
 
Shi, X., Hu, M., Deng, J., Ren, F.-J., Shi, P., & Yang, J.-Y. (2023). Integration of Multi-Branch GCNs Enhancing Aspect Sentiment Triplet Extraction. *Applied Sciences*. https://doi.org/10.3390/app13074345
 
Wang, P., Huang, L., Liu, T.-Y., Dai, D., Xu, R.-X., Wang, H.-F., Chang, B.-B., & Sui, Z.-F. (2021). Explicit Interaction Network for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2106.11148*. https://doi.org/10.48550/arxiv.2106.11148
 
Wang, F., Li, Y., Zhong, S.-T., Yin, C.-X., & He, Y.-C. (2021). Aspect-Sentiment-Multiple-Opinion Triplet Extraction. 583-594. https://doi.org/10.1007/978-3-030-88480-2_46
 
Xia, T., Sun, X., Yang, Y.-D., Long, Y.-F., & Sutcliffe, R. (2024). A dual relation-encoder network for aspect sentiment triplet extraction. *Neurocomputing*. https://doi.org/10.1016/j.neucom.2024.128064
 
Xu, T., Yang, H., Wu, Z., Chen, J.-Z., Zhao, F., & Dai, X.-Y. (2023). Measuring Your ASTE Models in The Wild: A Diversified Multi-domain Dataset For Aspect Sentiment Triplet Extraction. 2837-2853. https://doi.org/10.48550/arxiv.2305.17448
 
Xu, L., Chia, Y. K., & Bing, L. (2021). Learning Span-Level Interactions for Aspect Sentiment Triplet Extraction. *ArXiv, abs/2107.12214*. https://doi.org/10.18653/v1/2021.acl-long.367
 
Yang, F., Zhang, M., Hu, G., & Zhou, X. (2023). A Pairing Enhancement Approach for Aspect Sentiment Triplet Extraction. 399-410. https://doi.org/10.48550/arxiv.2306.10042
 
Yuan, L., Wang, J., Yu, L.-C., & Zhang, X.-J. (2024). Encoding Syntactic Information into Transformers for Aspect-Based Sentiment Triplet Extraction. *IEEE Transactions on Affective Computing, 15*, 722-735. https://doi.org/10.1109/taffc.2023.3291730
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, Y., Yang, Y., Li, Y., Liang, B., Chen, S.-W., Dang, Y., Yang, M., & Xu, R. (2022). Boundary-Driven Table-Filling for Aspect Sentiment Triplet Extraction. 6485-6498. https://doi.org/10.18653/v1/2022.emnlp-main.435
 
