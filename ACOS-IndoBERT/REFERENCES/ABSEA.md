# **ABSEA pada ulasan game** mengekstrak aspek spesifik dan mendeteksi sentimen serta emosi pemain secara granular.

Penerapan *Aspect-Based Sentiment and Emotion Analysis* (ABSEA) pada ulasan video game berfokus pada tiga dimensi utama: pemisahan aspek game (seperti *gameplay*, grafis, dan narasi), pemodelan emosi diskret pemain, serta implementasi arsitektur komputasi untuk mengatasi karakteristik teks ulasan yang kompleks (Yu et al., 2023; D'Aniello & Gaeta, 2022; Xia et al., 2023).

## Ekstraksi Aspek Spesifik Game

Dalam domain video game, ABSA memecah teks ulasan menjadi entitas atau atribut spesifik yang dinilai oleh pemain, alih-alih menggeneralisasi ulasan menjadi satu skor dokumen tunggal (Yu et al., 2023; Strååt et al., 2017; Zhang et al., 2022).

- **Kategori aspek utama** umumnya mencakup *gameplay*, grafik, audio, jalan cerita, dan komunitas pengguna (Yu et al., 2023; Urriza & Clariño, 2021; Strååt et al., 2017; Yuan et al., 2025).
- **Aspek implisit dan eksplisit** memerlukan penanganan terpisah karena opini sering diutarakan tanpa menyebutkan nama fitur secara langsung (Strååt et al., 2017; Hua et al., 2023; Jia et al., 2026).
- **Klasifikasi multi-aspek** menggunakan metode *Support Vector Machine* (SVM) mampu mencapai akurasi hingga 97% saat membedakan kombinasi aspek *gameplay* dan grafis (Urriza & Clariño, 2021).

## Pemodelan Emosi dan Valensi Pemain

Analisis emosi melangkah lebih jauh dari sekadar polaritas positif-negatif standar dengan mengidentifikasi kondisi afektif mendalam yang dirasakan oleh komunitas gamer (Balcıoğlu et al., 2025; D'Aniello & Gaeta, 2022; Xing et al., 2025).

| Dimensi Emosi | Pola Perilaku & Genre Terkait | Metrik & Temuan Kunci |
| :--- | :--- | :--- |
| **Kemarahan & Rasa Jijik** | Ulasan negatif pada game aksi, teknis, dan *Souls-like* | Ulasan bernada jijik menurun 39,95% pada ulasan positif (Balcıoğlu et al., 2025; Guzsvinecz, 2023) |
| **Kegembiraan & Kepercayaan** | Respon positif terhadap aspek cerita dan mekanika inti | Kemunculan rasa gembira meningkat 52,26% pada ulasan yang direkomendasikan (Balcıoğlu et al., 2025; Guzsvinecz, 2023) |
| **Kelegaan Emosional** | Game bertempo lambat (*relaxing games*) seperti simulasi | Mencapai 62,8% sentimen dan memprediksi waktu bermain yang lebih lama (Xing et al., 2025) |
| **Asimetri Panjang Teks** | Ulasan kritis berisi evaluasi teknis dan *bug* | Panjang median ulasan negatif mencapai 40 kata dibanding 19 kata pada ulasan positif (Guzsvinecz & Szűcs, 2023; Guzsvinecz, 2023) |

**Figure 1:** Perbandingan respons emosi diskret dan karakteristik ulasan pemain pada platform game online.

## Paradigma Model dan Tantangan Analisis

Pendekatan komputasi untuk game review telah berevolusi dari metode leksikon dan pembelajaran mesin klasik ke arsitektur *deep learning* terpadu (Yu et al., 2023; H. et al., 2019; Sattarov et al., 2024; Zhang et al., 2022).

**Figure 1.** Flowchart of the entire methodology, including pre-experimental preparation and postexperimental analysis. (Yuan et al., 2025)

*How to read: Diagram alir memperlihatkan tahapan metodologi analisis sentimen ulasan game, mulai dari pra-eksperimen ekstraksi kamus hingga klasifikasi sentimen per dimensi dan evaluasi komparatif.*

Penggunaan model berbasis aturan seperti VADER terbukti lebih peka dalam menangkap dinamika emosional pada komentar singkat platform Steam dibandingkan TextBlob (Yuan et al., 2025). Model *ensemble* seperti Random Forest dan Gradient Boosting menghasilkan akurasi klasifikasi sentimen masing-masing sebesar 83% dan 84% (Sattarov et al., 2024). Untuk penanganan end-to-end tanpa rekayasa fitur manual, arsitektur transformator seperti BERT dan RoBERTa secara efektif mengekstraksi keterkaitan topik dan sentimen afektif secara simultan (Yu et al., 2023; Pınarbaşı, 2025). Kendati demikian, kinerja model kerap menghadapi tantangan signifikan akibat tingginya sarkasme, konteks slang internal game, serta ketergantungan pada ulasan yang tidak informatif (Yu et al., 2023; Xia et al., 2023).

Integrasi ABSEA memungkinkan pengembang game memetakan masalah teknis dan keberhasilan fitur secara terperinci langsung dari umpan balik jutaan pengguna (Yu et al., 2023; Strååt et al., 2017).
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Balcıoğlu, Y. S., Çeli̇k, A. A., & Altındağ, E. (2025). Sentiment Analysis of Reddit Reviews on Mobile Gaming: Insights from the Gaming Community. *International Journal of Human–Computer Interaction, 41*, 12697 - 12709. https://doi.org/10.1080/10447318.2025.2464897
 
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. *Artificial Intelligence Review, 55*, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
 
Guzsvinecz, T. (2023). Sentiment Analysis of Souls-like Role-Playing Video Game Reviews. *Acta Polytechnica Hungarica*. https://doi.org/10.12700/aph.20.5.2023.5.10
 
Guzsvinecz, T., & Szűcs, J. (2023). Length and sentiment analysis of reviews about top-level video game genres on the steam platform. *Comput. Hum. Behav., 149*, 107955. https://doi.org/10.1016/j.chb.2023.107955
 
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. *Expert Syst. Appl., 118*, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
 
Hua, Y. C., Denny, P., Wicker, J., & Taškova, K. (2023). A systematic review of aspect-based sentiment analysis: domains, methods, and trends. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-024-10906-z
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Pınarbaşı, F. (2025). Evaluation of Mobile Game Apps Emotional Side: A Sentiment Analysis on Mobile Game App Reviews. *Yönetim Bilimleri Dergisi*. https://doi.org/10.35408/comuybd.1564966
 
Sattarov, K., Shakhriyorbek, B., Chaudhary, N., Ather, D., Kler, R., & Shukla, B. (2024). Automated Sentiment Analysis and Emotion Recognition of Steam Game Reviews Using Ensemble Machine Learning Techniques. *2024 1st International Conference on Sustainable Computing and Integrated Communication in Changing Landscape of AI (ICSCAI)*, 1-10. https://doi.org/10.1109/icscai61790.2024.10867053
 
Strååt, B., Verhagen, H., & Warpefelt, H. (2017). Probing user opinions in an indirect way: an aspect based sentiment analysis of game reviews. *Proceedings of the 21st International Academic Mindtrek Conference*. https://doi.org/10.1145/3131085.3131121
 
Urriza, I. M., & Clariño, M. (2021). Aspect-Based Sentiment Analysis of User Created Game Reviews. *2021 24th Conference of the Oriental COCOSDA International Committee for the Co-ordination and Standardisation of Speech Databases and Assessment Techniques (O-COCOSDA)*, 76-81. https://doi.org/10.1109/o-cocosda202152914.2021.9660559
 
Xia, X.-C., Huang, Y., & Zhang, Y. (2023). Multi-Task Learning for Game Review Classification with Emotion and Sarcasm Detection. *2023 8th International Conference on Data Science in Cyberspace (DSC)*, 159-165. https://doi.org/10.1109/dsc59305.2023.00032
 
Xing, Y., W., You, Q., & Li, J.-X. (2025). Modeling Affective Mechanisms in Relaxing Video Games: Sentiment and Topic Analysis of User Reviews. *Syst., 13*, 540. https://doi.org/10.3390/systems13070540
 
Yu, Y., Dinh, D.-T., Nguyen, B.-H., Yu, F.-Y., & Huynh, V. (2023). Mining Insights From Esports Game Reviews With an Aspect-Based Sentiment Analysis Framework. *IEEE Access, 11*, 61161-61172. https://doi.org/10.1109/access.2023.3285864
 
Yuan, L., Ding, M., Meng, F.-Y., & Tian, Y. (2025). Sentiment Analysis and Rating Video Game Dimensions via NLP. *Applied and Computational Engineering*. https://doi.org/10.54254/2755-2721/2024.20540
 
Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges. *IEEE Transactions on Knowledge and Data Engineering, 35*, 11019-11038. https://doi.org/10.1109/tkde.2022.3230975
 
