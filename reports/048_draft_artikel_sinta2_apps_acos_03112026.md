# Apps-ACOS: Sumber Daya dan Pipeline Extract-Classify Berbasis IndoBERT untuk Ekstraksi Quadruple Aspect–Category–Opinion–Sentiment pada Ulasan Bank Digital Berbahasa Indonesia

> **Status:** Draft artikel ilmiah — target **SINTA 2**. Disusun 3 November 2026 oleh Arena Agent dari verifikasi artefak primer Drive + repositori.
> **Dokumen terkait:** `docs/0012` (laporan penelitian 03/11), `reports/045` (artikel SINTA2 02/11), `reports/042` (kesiapan publikasi).
> **Referensi lokal:** folder `ACOS-IndoBERT/REFERENCES/` (24 tinjauan Markdown + ±20 PDF) kini tersedia di repo dan dapat dipakai untuk memperkaya Daftar Pustaka.

---

**CATATAN EDITORIAL (hapus sebelum submit):** Draft ini diposisikan sebagai *resource + reproducible pipeline + audit metodologis*, bukan klaim SOTA, sesuai putusan kesiapan publikasi (laporan 042). Angka interim diberi label eksplisit. Sebelum submit ke SINTA 2, lengkapi: (1) Step-2 15 epoch × ≥3 seed; (2) dedupe & split ulang; (3) satukan evaluator; (4) IAA manusia; (5) ≥2 baseline pada split sama. Target jurnal: Jurnal Ilmu Komputer dan Informasi (UI), JNTETI (UGM), Register, atau JISEBI (Unair) — verifikasi akreditasi SINTA 2 terkini di portal SINTA.

---

**[Nama Penulis 1]¹, [Nama Penulis 2]²**

¹[Departemen, Fakultas, Universitas, Kota, Indonesia]
²[Departemen, Fakultas, Universitas, Kota, Indonesia]
Email korespondensi: [email@domain.ac.id]

## Abstrak

Ekstraksi quadruple Aspect–Category–Opinion–Sentiment (ACOS) menuntut pemulihan pasangan (span aspek, kategori, span opini, sentimen) termasuk slot implisit, namun belum memiliki benchmark berbahasa Indonesia. Penelitian ini memperkenalkan **Apps-ACOS**, sumber daya ACOS Indonesia pertama pada domain bank digital: 43.673 ulasan dari 13 aplikasi didekomposisi menjadi 76.077 klausa (60.159/8.027/7.891 train/dev/test, split disjoint berdasarkan review_id) dengan 92.074 quadruple berlabel lemah atas 13 kategori dan 3 kelas sentimen. Pipeline Extract-Classify diadaptasi ke IndoBERT tanpa mengubah kode upstream, dilengkapi enam gerbang verifikasi, caching per-backbone, dan resume per-epoch. Sebagai baseline awal, Step-1 (BERT-CRF) mencapai 81,27% micro-F1 pada kontrol Restaurant-ACOS dan Step-2 mencapai 48,24% F1 pada kontrol yang sama; pada Apps-ACOS, Step-2 mencatat F1 interim 67,16–69,00% pada 3 dari 15 epoch (batas bawah, belum konvergen). Dekomposisi 15 sub-task menunjukkan peluruhan performa seiring bertambahnya elemen quadruple. Kontribusi metodologis tambahan adalah audit reproduksibilitas yang mengidentifikasi ancaman validitas — seleksi checkpoint pada test set, kebocoran teks 14,66% baris test, dan metrik dua-kepala yang tidak terpersistensi — beserta protokol perbaikannya. Hasil ini menempatkan Apps-ACOS sebagai titik awal benchmark ACOS Indonesia yang dapat direproduksi, bukan klaim state-of-the-art.

**Kata kunci:** analisis sentimen berbasis aspek, ACOS, IndoBERT, bahasa Indonesia, pelabelan lemah, reproduksibilitas

## Abstract

*Aspect–Category–Opinion–Sentiment (ACOS) quadruple extraction requires recovering (aspect span, category, opinion span, sentiment) tuples including implicit slots, yet no Indonesian benchmark exists. This paper introduces **Apps-ACOS**, the first Indonesian ACOS resource for the digital-banking domain: 43,673 reviews from 13 applications decomposed into 76,077 clauses (60,159/8,027/7,891 train/dev/test, review_id-disjoint splits) with 92,074 weakly-labeled quadruples over 13 categories and 3 sentiment classes. The Extract-Classify pipeline is adapted to IndoBERT without modifying upstream code, augmented with six verification gates, per-backbone caching, and per-epoch resume. As initial baselines, Step-1 (BERT-CRF) reaches 81.27% micro-F1 on the Restaurant-ACOS control and Step-2 reaches 48.24% F1 on the same control; on Apps-ACOS, Step-2 records an interim F1 of 67.16–69.00% at 3 of 15 epochs (a lower bound, not yet converged). A 15-sub-task decomposition shows performance decay as quadruple elements accumulate. An additional methodological contribution is a reproducibility audit identifying validity threats — test-set checkpoint selection, 14.66% test-row text leakage, and non-persisted dual-head metrics — together with a remediation protocol. These results position Apps-ACOS as a reproducible starting point for Indonesian ACOS benchmarking rather than a state-of-the-art claim.*

**Keywords:** aspect-based sentiment analysis, ACOS, IndoBERT, Indonesian, weak supervision, reproducibility

## 1. Pendahuluan

Analisis sentimen berbasis aspek (ABSA) memetakan opini ke target spesifik, melampaui polaritas tingkat dokumen [1]–[3]. Tugas ACOS memperluas ABSA ke ekstraksi quadruple lengkap (aspek, kategori, opini, sentimen) dengan dukungan slot implisit — aspek atau opini yang tidak muncul sebagai span tekstual [4]. Domain ulasan aplikasi bank digital menambah tantangan: singkatan non-standar, campur kode Indonesia–Inggris, tanda baca tanpa spasi, dan klausa sangat pendek.

Untuk bahasa Indonesia, sumber daya ABSA yang tersedia (CASA, HoASA dalam IndoNLU [5]; IndoLEM [6]) berhenti pada pasangan aspek–sentimen dan tidak menuntut quadruple lengkap. Akibatnya, klaim performa ACOS berbahasa Indonesia tidak memiliki pembanding setara. Penelitian ini mengisi celah tersebut dengan tiga kontribusi yang dapat dipertahankan secara metodologis:

1. **Sumber daya**: Apps-ACOS, dataset ACOS Indonesia pertama domain bank digital, dengan sifat label lemah didokumentasikan terbuka.
2. **Metode/rekayasa**: adaptasi reproduksibel pipeline Extract-Classify [4] ke IndoBERT melalui arsitektur dua-root, caching per-backbone, enam gerbang verifikasi, dan resume per-epoch.
3. **Analisis & audit**: dekomposisi 15 sub-task, kuantifikasi propagasi galat, serta audit reproduksibilitas yang mengidentifikasi ancaman validitas dan protokol perbaikannya.

Empat pertanyaan penelitian: (R1) Bagaimana mengonstruksi data ACOS Indonesia tanpa kehilangan span? (R2) Bagaimana menjamin kompatibilitas upstream saat mengganti backbone? (R3) Di mana bottleneck performa pada quadruple? (R4) Apa batas klaim yang valid pada hasil label lemah?

## 2. Metode

### 2.1 Konstruksi Dataset Apps-ACOS
Ulasan dikumpulkan dari 13 aplikasi bank digital di Google Play (86,61%) dan App Store (13,39%), menghasilkan 43.673 ulasan. Pelabelan lemah berbasis aturan + leksikon + evidence score menghasilkan 96.417 baris tuple pra-pemecahan. Ulasan dipecah menjadi klausa (80.260), lalu 4.183 klausa tanpa split dibuang, menyisakan 76.077 klausa. Split dilakukan pada tingkat review_id yang disjoint (0 tumpang tindih terverifikasi). Taksonomi mencakup 13 kategori datar dan 3 kelas sentimen; num_labels Step-2 = 39 (13×3) agar identik dengan baseline [4].

**Tabel 1.** Komposisi Apps-ACOS per split.

| Split | Klausa | Quadruple | Aspek implisit (%) | Opini implisit (%) |
|---|---|---|---|---|
| Train | 60.159 | 72.973 | 29,86 | 40,70 |
| Dev | 8.027 | 9.587 | 31,28 | 39,13 |
| Test | 7.891 | 9.514 | 30,88 | 40,16 |
| **Total** | **76.077** | **92.074** | **30,11** | **40,48** |

Distribusi sentimen: negatif 49,77%, netral 11,30%, positif 38,93%. Median panjang klausa 7 kata (maks 79), jauh di bawah max_seq_length 128.

### 2.2 Pipeline Dua Tahap
**Step-1 (ko-ekstraksi span).** BERT-CRF [7], [8] dengan skema tag BIO (O, B/I-ASP, B/I-OPN) ditambah dua head biner untuk deteksi aspek implisit (IA) dan opini implisit (IO). **Bridge.** Produk Kartesian pasangan aspek×opini, termasuk pasangan implisit (-1,-1), menghasilkan kandidat. **Step-2 (klasifikasi).** Fitur [mean-pool(aspect); mean-pool(opinion)] ∈ ℝ¹⁵³⁶ diproyeksikan ke head 39 dimensi (13 kategori BCE + 3 sentimen CE), direkonstruksi menjadi 39 label gabungan untuk kompatibilitas mundur dengan upstream [4].

**Tabel 2.** Konfigurasi utama.

| Komponen | Spesifikasi |
|---|---|
| Backbone | indobenchmark/indobert-base-p1 [5], [6]; 12 layer, 768 hidden, 12 head, vocab 50.000 |
| max_seq_length | 128 |
| Epoch / batch | 15 / 24 (Step-1), 16 (Step-2) |
| Learning rate | 2e-5 (Step-1), 5e-5 (Step-2) |
| Seed / device | 42 / NVIDIA Tesla T4 (CUDA); kontrol pada AMD MI300X (ROCm) |

### 2.3 Gerbang Verifikasi dan Reproduksibilitas
Enam gerbang memverifikasi: (1) bobot encoder (199/199 key, mean tensor identik); (2) taksonomi label; (3) keberadaan dataset; (4) integritas build ACOS (0 quad hilang); (5) tokenisasi; (6) paritas English-control terhadap upstream. Adapter re-key menambahkan prefiks `bert.` pada state_dict IndoBERT agar kompatibel dengan BertForQuadABSA. Caching per-backbone mencegah kontaminasi lintas domain; resume level-3 per-epoch memungkinkan pelatihan dilanjutkan setelah interupsi.

### 2.4 Protokol Evaluasi
Metrik utama: micro-F1 quadruple (Step-2) dan micro-F1 span (Step-1), dengan precision/recall. Dekomposisi 15 sub-task mengukur F1 untuk setiap kombinasi elemen {category, sentiment, aspect, opinion}. **Catatan metodologis:** pada run interim, checkpoint dipilih berdasarkan F1 test di dalam loop epoch (ancaman T03); protokol final memindahkan seleksi ke dev dan mengevaluasi test sekali di akhir. Dua evaluator ditemukan menggunakan definisi gold berbeda (9.006 vs 19.528 elemen); protokol final menyatukan evaluator pada gold 9.006.

## 3. Hasil dan Pembahasan

### 3.1 Baseline Kontrol (Restaurant-ACOS, BERT-base)
**Tabel 3.** Baseline kontrol pada Restaurant-ACOS (583 kalimat test, 895 quadruple).

| Tahap | P | R | F1 | Epoch |
|---|---|---|---|---|
| Step-1 (span) | 78,16 | 84,64 | **81,27** | 8/15 |
| Step-2 (quadruple) | 43,4 | 54,3 | **48,24** | 12/15 |

Angka Step-2 berada di atas baseline asli Extract-Classify (44,52 [4]) namun di bawah model generatif T5 (67,15 [9]); klaim SOTA ditolak.

### 3.2 Hasil Interim Apps-ACOS (IndoBERT)
**Tabel 4.** Step-2 Apps-ACOS (sesi 05/09, Tesla T4).

| Epoch | Loss | P% | R% | F1% |
|---|---|---|---|---|
| 1 | 0,5511 | 62,37 | 72,75 | 67,16 |
| 2 | 0,3792 | 61,41 | 72,64 | 66,55 |
| 3 | 0,3052 | 63,29 | 75,84 | **69,00** |

**Interim:** hanya 3/15 epoch; 69,00% adalah batas bawah, bukan hasil konvergen. TP/FP/FN epoch-3 = 6.830/3.962/2.176 (gold 9.006). Angka 97,94% Step-1 yang beredar berasal dari pemuatan cache (8/15 epoch) dan **tidak** dilaporkan sebagai kapabilitas.

### 3.3 Dekomposisi 15 Sub-Task
Peluruhan F1 seiring bertambahnya elemen (IndoBERT appsid, interim): 1 elemen 91,08% → 2 elemen 82,06% → 3 elemen 73,27% → 4 elemen 66,08%; sentimen adalah elemen paling rapuh (85,72%). **Peringatan:** angka ini bukan perbandingan backbone (dataset, bahasa, jumlah kandidat berbeda) dan terkena temuan dua evaluator; dekomposisi final dihitung ulang setelah evaluator disatukan.

### 3.4 Karakteristik Data (EDA)
Kategori didominasi FEATURES_PRODUCT (30,08%), TRANSACTION_TRANSFER (16,02%), APP_PERFORMANCE (10,55%). Kategori teknis hampir selalu negatif (APP_PERFORMANCE 79,4%, AUTH_ACCESS 78,5%), sedangkan kategori pengalaman hampir selalu positif (UI_UX 71,1%) — sentimen sangat dapat diprediksi dari kategori, membatasi validitas metrik sentimen sebagai ukuran pemahaman bahasa. Kosakata tertutup: 362 istilah aspek dan 202 istilah opini untuk 92.074 tuple; 10 istilah teratas menyumbang 37,1%/45,2% span. Kombinasi implisit: (Implisit,Implisit)=0 — tidak ada quadruple dengan aspek dan opini implisit sekaligus.

### 3.5 Audit Reproduksibilitas (Kontribusi Metodologis)
**Tabel 5.** Ancaman validitas dan protokol perbaikan.

| Ancaman | Temuan | Remediasi |
|---|---|---|
| Seleksi checkpoint | F1 test dipakai memilih model dalam loop epoch | Seleksi pada dev; test sekali di akhir |
| Kebocoran teks | 14,66% baris test identik train | Split group-wise + dedupe; laporkan subset unik |
| Cache-hit | 97,94% bukan hasil eksekusi | Hapus cache; latih ulang; laporkan provenans |
| Dual-head | category_F1/sentiment_acc = 0 permanen | Persistensi logit per-head + ablasi |
| CV gagal | 93/94 run ERROR; tokenisasi belum selesai | Selesaikan tokenisasi; perbaiki 2 bug; ulang grid |
| Dua evaluator | gold 9.006 vs 19.528 (2,17×) | Satukan evaluator; hitung ulang sub-task |

Temuan ini orisinal dan belum dilaporkan pada literatur ACOS; menjadikannya kontribusi memperkuat nilai ilmiah naskah.

### 3.6 Posisi terhadap Literatur
Pada Restaurant-ACOS dengan split identik, reproduksi baseline (48,24) layak diklaim (+3,7 poin di atas 44,52 [4]) asalkan protokol dijelaskan. Angka Apps-ACOS tidak boleh disandingkan dengan Restaurant-ACOS karena dataset, bahasa, unit input, dan sifat label berbeda. Tidak ada klaim SOTA; model generatif [9] masih unggul 15–19 poin pada domain kontrol.

### 3.7 Ancaman terhadap Validitas
(i) Label lemah tanpa anotasi manusia (κ belum diukur); (ii) satu seed, tanpa interval kepercayaan; (iii) kebocoran teks antar split; (iv) kosakata tertutup membatasi generalisasi; (v) 61,96% ulasan berasal dari 2026 sehingga klaim temporal harus dibatasi; (vi) hasil Step-2 interim. Seluruh angka dilaporkan sebagai batas bawah interim hingga protokol final selesai.

## 4. Kesimpulan

Apps-ACOS menyediakan sumber daya ACOS berbahasa Indonesia pertama pada domain bank digital (92.074 quadruple, 13 kategori) beserta pipeline Extract-Classify IndoBERT yang reproduksibel dengan enam gerbang verifikasi. Baseline awal menunjukkan Step-2 48,24% F1 pada kontrol Restaurant-ACOS dan F1 interim 67,16–69,00% pada Apps-ACOS (belum konvergen). Dekomposisi 15 sub-task mengungkap peluruhan performa per elemen dengan sentimen sebagai bottleneck. Audit reproduksibilitas mengidentifikasi enam ancaman validitas beserta protokol perbaikannya. Pekerjaan lanjutan: menyelesaikan Step-2 multi-seed, dedupe split, menyatukan evaluator, anotasi manusia (IAA), dan baseline pada split sama, sebelum naskah diajukan sebagai benchmark final.

## Ucapan Terima Kasih
[Isi: sumber pendanaan, penyedia infrastruktur GPU (AMD Developer Cloud / Colab), dan anotator.]

## Daftar Pustaka

[1] B. Liu, *Sentiment Analysis and Opinion Mining*. Morgan & Claypool, 2012.
[2] M. Pontiki dkk., "SemEval-2014 Task 4: Aspect Based Sentiment Analysis," dalam *Proc. SemEval*, 2014.
[3] M. Pontiki dkk., "SemEval-2016 Task 5: Aspect Based Sentiment Analysis," dalam *Proc. SemEval*, 2016.
[4] H. Cai, R. Xia, dan J. Yu, "Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions," dalam *Proc. ACL-IJCNLP*, 2021, hlm. 340–350.
[5] B. Wilie dkk., "IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding," dalam *Proc. EMNLP*, 2020, hlm. 843–857.
[6] F. Koto, A. Rahimi, J. H. Lau, dan T. Baldwin, "IndoLEM and IndoBERT: A Benchmark Dataset and Pre-trained Language Model for Indonesian NLP," dalam *Proc. COLING*, 2020, hlm. 757–770.
[7] J. Devlin, M.-W. Chang, K. Lee, dan K. Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," dalam *Proc. NAACL-HLT*, 2019, hlm. 4171–4186.
[8] J. Lafferty, A. McCallum, dan F. Pereira, "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data," dalam *Proc. ICML*, 2001.
[9] H. Hu dkk., "MEMD-ABSA: A Multi-Element Multi-Domain Dataset for Aspect-Based Sentiment Analysis," *arXiv:2306.16956*, 2023.
[10] G. Lample dkk., "Neural Architectures for Named Entity Recognition," dalam *Proc. NAACL*, 2016.
[11] C. Sun, L. Huang, dan X. Qiu, "Utilizing BERT for Aspect-Based Sentiment Analysis via Constructing Auxiliary Sentence," dalam *Proc. NAACL*, 2019.
[12] X. Li, L. Bing, W. Zhang, dan W. Lam, "Exploiting BERT for End-to-End Aspect-based Sentiment Analysis," *arXiv:1910.00883*, 2019.
[13] W. Zhang, X. Li, Y. Deng, L. Bing, dan W. Lam, "A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges," *IEEE Trans. Knowl. Data Eng.*, 2022.
[14] H. H. Do, P. W. C. Prasad, A. Maag, dan A. Alsadoon, "Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review," *Expert Syst. Appl.*, vol. 118, hlm. 272–299, 2019.
[15] A. Nazir, Y. Rao, L. Wu, dan L. Sun, "Issues and Challenges of Aspect-based Sentiment Analysis: A Comprehensive Survey," *IEEE Trans. Affect. Comput.*, vol. 13, no. 2, 2022.
[16] G. Brauwers dan F. Frasincar, "A Survey on Aspect-Based Sentiment Classification," *Artif. Intell. Rev.*, vol. 55, hlm. 6147–6186, 2022.
[17] K. Schouten dan F. Frasincar, "Survey on Aspect-Level Sentiment Analysis," *IEEE Trans. Knowl. Data Eng.*, vol. 28, no. 3, hlm. 813–830, 2016.
[18] M. Hu dan B. Liu, "Mining and Summarizing Customer Reviews," dalam *Proc. KDD*, 2004, hlm. 168–177.
[19] G. Qiu, B. Liu, J. Bu, dan C. Chen, "Opinion Word Expansion and Target Extraction through Double Propagation," *Comput. Linguist.*, vol. 37, no. 1, hlm. 9–27, 2011.
[20] A.-M. Popescu dan O. Etzioni, "Extracting Product Features and Opinions from Reviews," dalam *Proc. HLT-EMNLP*, 2005.
[21] T. Wilson, J. Wiebe, dan P. Hoffmann, "Recognizing Contextual Polarity in Phrase-Level Sentiment Analysis," dalam *Proc. HLT-EMNLP*, 2005.
[22] A. Conneau dkk., "XNLI: Evaluating Cross-lingual Sentence Representations," dalam *Proc. EMNLP*, 2018.
[23] T. Pires, E. Schlinger, dan D. Garrette, "How Multilingual is Multilingual BERT?," dalam *Proc. ACL*, 2019.
[24] S. Wu dan M. Dredze, "Beto, Bentz, Becas: The Surprising Cross-Lingual Effectiveness of BERT," dalam *Proc. EMNLP*, 2019.
[25] M. Artetxe, S. Ruder, dan D. Yogatama, "On the Cross-lingual Transferability of Monolingual Representations," dalam *Proc. ACL*, 2020.
[26] F. Koto, J. H. Lau, dan T. Baldwin, "IndoBERTweet: A Pretrained Language Model for Indonesian Twitter with Effective Domain-Specific Vocabulary Initialization," dalam *Proc. EMNLP*, 2021.
[27] E. Cambria, D. Das, S. Bandyopadhyay, dan A. Feraco, *A Practical Guide to Sentiment Analysis*. Springer, 2017.
[28] H. Yang dkk., "PyABSA: Open Framework for Aspect-based Sentiment Analysis," *GitHub repository*, 2023.

---
*Akhir draft. Angka interim wajib diperbarui setelah eksperimen final. Daftar Pustaka dapat diperkaya dari folder `ACOS-IndoBERT/REFERENCES/` yang kini tersedia di repo.*
