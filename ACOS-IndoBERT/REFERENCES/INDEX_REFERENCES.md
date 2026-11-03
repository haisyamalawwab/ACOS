# Indeks dan Pemetaan Literatur — ACOS-IndoBERT/REFERENCES

> **Tanggal inventaris:** 3 November 2026
> **Ruang lingkup:** semua berkas `.md` di `ACOS-IndoBERT/REFERENCES/` beserta daftar PDF yang menyertainya.
> **Indeks saudara:** [REFERENSI/INDEX_REFERENSI.md](../REFERENSI/INDEX_REFERENSI.md) memetakan tiga dokumen Markdown berbahasa Indonesia di direktori `REFERENSI/`.

## Daftar isi indeks

- [Ikhtisar dan statistik](#ikhtisar-dan-statistik)
- [Peta tema dan kematangan bukti](#peta-tema-dan-kematangan-bukti)
- [Temuan konsistensi/prioritas audit](#temuan-konsistensiprioritas-audit)
- [Daftar isi setiap Markdown](#daftar-isi-setiap-markdown)
- [Inventaris PDF pendukung](#inventaris-pdf-pendukung)
- [Batas survei](#batas-survei)

## Ikhtisar dan statistik

- **27 dokumen Markdown**; **17** memakai heading Markdown dan **10** tidak memiliki heading Markdown eksplisit.
- **19 PDF** berada di folder ini.
- Pustaka memuat **844 DOI unik-per-dokumen**; setelah deduplikasi lintas dokumen terdapat **501 DOI unik**. Angka ini hanya menghitung string DOI, bukan validasi metadata.
- Scope literatur mencakup ABSA/ASTE/ACOS/ACOSE, IndoBERT/perbankan, emosi, label/data, domain game/hotel, BERTopic, hyperparameter, robustness, dan NLP Indonesia/code-mixing.
- Teridentifikasi dua pasangan `.md` identik byte-per-byte (satu di folder ini, satu di folder saudara) serta dua pasangan near-duplicate lintas-folder dengan set DOI sama; lihat temuan audit.

### Peta dokumen (nama file, fokus, sitasi DOI)

| Markdown | Fokus ringkas | DOI unik pada file | Status TOC |
|---|---|---:|---|
| [ABSA Bank Digital.md](./ABSA%20Bank%20Digital.md) | ABSA perbankan digital Indonesia; sintesis metode dan studi bank | 23 | heading Markdown |
| [ABSA Dual Extraction.md](./ABSA%20Dual%20Extraction.md) | ABSA/ASTE dual extraction pada ulasan game | 58 | heading Markdown |
| [ABSA Hotel.md](./ABSA%20Hotel.md) | ABSA pada ulasan hotel | 11 | heading Markdown |
| [ABSEA.md](./ABSEA.md) | Aspect-based sentiment and emotion analysis pada game | 16 | heading Markdown |
| [ACOS dan ACOSE Analisis Sentimen.md](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md) | Formulasi ACOS/ACOSE, dataset, ekstraksi dan gap | 35 | heading Markdown |
| [ACOSE Paling Kuat.md](./ACOSE%20Paling%20Kuat.md) | Pilihan paradigma implementasi ACOSE (ML/DL/LLM) | 38 | outline sintetis; tanpa heading |
| [ACOSQE Adalah Tugas Bukan Model.md](./ACOSQE%20Adalah%20Tugas%20Bukan%20Model.md) | Pembedaan formulasi tugas ACOSQE dan keluarga model | 17 | outline sintetis; tanpa heading |
| [Analisi IndoBERT.md](./Analisi%20IndoBERT.md) | IndoBERT untuk 13 bank digital (versi tanpa heading Markdown) | 62 | outline sintetis; tanpa heading |
| [Analisis ACOS.md](./Analisis%20ACOS.md) | Batas ACOS terkait intensitas emosi, trigger, perilaku | 15 | outline sintetis; tanpa heading |
| [ASTE vs ABSA.md](./ASTE%20vs%20ABSA.md) | Perbedaan ASTE dan ABSA; robustness/domain shift | 35 | heading Markdown |
| [BERT lebih Unggul dari ML.md](./BERT%20lebih%20Unggul%20dari%20ML.md) | Klaim perbandingan BERT dengan model klasik untuk ABSA bank | 14 | heading Markdown |
| [BERTopic X ABSA.md](./BERTopic%20X%20ABSA.md) | Integrasi BERTopic dengan ABSA dan batas bukti | 50 | heading Markdown |
| [Deep Critical and Mapping ABSA.md](./Deep%20Critical%20and%20Mapping%20ABSA.md) | Salinan identik tinjauan ABSA bank digital | 23 | heading Markdown |
| [Ekstraksi Quandruple ACOS.md](./Ekstraksi%20Quandruple%20ACOS.md) | Formulasi quadruple ACOS dan keluarga model | 44 | heading Markdown |
| [Implementasi ACOSE.md](./Implementasi%20ACOSE.md) | Rancangan alur implementasi ACOSE lintas paradigma | 17 | outline sintetis; tanpa heading |
| [IndoBERT Unggul.md](./IndoBERT%20Unggul.md) | Kinerja IndoBERT, ekstraksi aspek, dan opsi hybrid ACOSE | 6 | outline sintetis; tanpa heading |
| [Indonesia AI NLP Mixed Code.md](./Indonesia%20AI%20NLP%20Mixed%20Code.md) | Pemetaan NLP/AI untuk Indonesia, bahasa daerah, dan code-mixing | 24 | heading Markdown |
| [Integrasi ACOSE.md](./Integrasi%20ACOSE.md) | Rasionalisasi integrasi aspek, sentimen, emosi; ML/DL/LLM | 18 | outline sintetis; tanpa heading |
| [Labeling ACOS.md](./Labeling%20ACOS.md) | Strategi pelabelan ACOS/weak labels dan quality control | 47 | heading Markdown |
| [Limitation ACOS.md](./Limitation%20ACOS.md) | Batas ACOS terhadap emosi, cause, dan intensity | 49 | heading Markdown |
| [Literature ACOSE.md](./Literature%20ACOSE.md) | Literatur ACOSE pada perbankan digital Indonesia | 32 | outline sintetis; tanpa heading |
| [Matrix ABSA.md](./Matrix%20ABSA.md) | Matriks literatur ABSA dan fine-tuning BERT | 29 | heading Markdown |
| [Optimasi Hyperparameter BERT.md](./Optimasi%20Hyperparameter%20BERT.md) | Strategi tuning hyperparameter BERT untuk ABSA | 15 | heading Markdown |
| [Optimasi UMAP BERTopic.md](./Optimasi%20UMAP%20BERTopic.md) | Parameter UMAP/HDBSCAN, coherence, dan outlier BERTopic | 26 | heading Markdown |
| [Pemetaan ABSA.md](./Pemetaan%20ABSA.md) | Taksonomi triplet dan subtask ABSA | 70 | heading Markdown |
| [Rekomendasi ACOSE.md](./Rekomendasi%20ACOSE.md) | Rekomendasi arah pengembangan ACOSE dan intensitas | 12 | outline sintetis; tanpa heading |
| [TinjauanABSA.md](./TinjauanABSA.md) | Tinjauan ABSA dual extraction pada game (versi tanpa heading Markdown) | 58 | outline sintetis; tanpa heading |

## Peta tema dan kematangan bukti

| Klaster | Dokumen representatif | Fungsi dalam kajian | Catatan kritis |
|---|---|---|---|
| ABSA/ASTE dan dual extraction | `ABSA Dual Extraction`, `TinjauanABSA`, `ASTE vs ABSA`, `Pemetaan ABSA`, `Matrix ABSA` | Terminologi subtugas, joint extraction, dataset/domain game, dan pemetaan metode | `ABSA Dual Extraction` dan `TinjauanABSA` berbagi seluruh 58 DOI dan teks sangat mirip (sekitar 98% normalized-text similarity); jangan dihitung sebagai dua evidence syntheses independen tanpa versioning. |
| ACOS/ACOSQE/quadruple | `Ekstraksi Quandruple ACOS`, `ACOSQE Adalah Tugas Bukan Model`, `ACOS dan ACOSE Analisis Sentimen` | Formulasi quadruple, implicit aspect/opinion, model generatif/non-generatif, benchmark ACOS | Bedakan definisi tugas, arsitektur model, dan hasil per dataset. Beberapa dokumen menyajikan klaim kinerja tanpa locator halaman/tabel. |
| ACOSE/emosi | `ACOSE Paling Kuat`, `Implementasi ACOSE`, `Integrasi ACOSE`, `Literature ACOSE`, `Rekomendasi ACOSE`, `Limitation ACOS` | Desain penambahan emosi, trigger/intensity, pipeline ML/DL/LLM, research gap | Mayoritas sintesis konseptual; validasi ACOSE manusia/benchmark bank masih perlu dibuktikan terpisah. |
| IndoBERT/perbankan | `ABSA Bank Digital`, `Analisi IndoBERT`, `IndoBERT Unggul`, `BERT lebih Unggul dari ML` | Benchmark/sintesis layanan finansial dan klaim kemampuan IndoBERT | Angka lintas studi mencampur task, metrik, label, dan split; bukan perbandingan langsung. `ABSA Bank Digital` identik dengan `Deep Critical and Mapping ABSA`. |
| Topik/modeling dan tuning | `BERTopic X ABSA`, `Optimasi UMAP BERTopic`, `Optimasi Hyperparameter BERT`, `ABSA Hotel` | Pemodelan topik, parameter, hotel review dan tuning model | Bukti dari domain berdekatan tidak otomatis berpindah ke 13-bank Apps-ACOS. |
| Pelabelan dan data | `Labeling ACOS`, `Indonesia AI NLP Mixed Code` | Strategi weak/pseudo-label, quality control, resource bahasa | Pisahkan bukti berdasarkan label gold, weak label, rating-proxy, dan dataset sumber. |

## Temuan konsistensi/prioritas audit

### Duplikasi dan versi dokumen

- **Duplikat identik:** `ABSA Bank Digital.md` = `Deep Critical and Mapping ABSA.md`.
- **Kandidat near-duplicate lintas berkas:** `ABSA Dual Extraction.md` ↔ `TinjauanABSA.md`; DOI bersama **58**; kemiripan teks setelah normalisasi spasi **98.2%**. Periksa perubahan substansi dan tetapkan satu versi kanonik.
- `ACOS-IndoBERT/REFERENSI/ACOS Menangkap Struktur Implicit Explicit BUKAN EMOSI.md` identik byte-per-byte dengan `REFERENCES/Limitation ACOS.md` (diduplikasi lintas folder).
- File `Analisi IndoBERT.md` di folder ini memiliki 62 DOI yang sama dan kemiripan teks sekitar 98,5% dengan `REFERENSI/Analisis IndoBERT 13 BANK DIGITAL.md`; indikasi salinan/versi.

### Mutu struktur dan provenance

- **10/27 Markdown tidak menggunakan heading `#`.** Untuk dokumen tersebut indeks berikut menyajikan outline hasil pemetaan dari title dan label paragraf/tabel, bukan TOC yang sudah tertulis di sumber. Disarankan menambahkan heading Markdown di sumber secara konsisten.
- Banyak dokumen berformat sintesis Consensus mengulang funnel `Retrieved/Eligible/Included`; query, tanggal pencarian, inklusi-eksklusi, deduplikasi, daftar studi included, dan locator klaim belum seragam. Jangan menganggap angka tersebut systematic review yang dapat direplikasi tanpa log pencarian.
- Caption `Figure`/`Table` muncul dalam beberapa Markdown sebagai teks, tetapi gambar/table pendukung tidak selalu embedded atau ditautkan. Verifikasi setiap figure/table sebelum dikutip.
- Sebagian besar daftar pustaka adalah kumpulan citation inline dan DOI; **tidak semua DOI/metadata diverifikasi terhadap sumber penerbit** oleh survei ini.
- Folder mencampur bahasa dan domain berbeda (Indonesia/Inggris; bank, e-commerce, game, hotel, layanan publik). Catat transferability sebagai evidence berdekatan, bukan bukti langsung untuk Apps-ACOS.
- Folder memiliki PDF pendukung, termasuk nama berakhiran `(1)` dan berkas berukuran sama. Audit hash/edisi PDF; nama/ukuran sama tidak membuktikan isi identik.

### Saran perapihan

1. Pertahankan satu file kanonik untuk setiap kelompok duplikat/near-duplicate; arsipkan versi lama dengan tanggal/status jika perlu.
2. Tambahkan heading Markdown dan TOC pada 10 dokumen yang belum memiliki heading eksplisit.
3. Buat master bibliography `.bib`/RIS/CSL JSON dengan metadata lengkap dan DOI, bukan hanya tautan DOI yang disalin ke beberapa ringkasan.
4. Buat claim-to-source matrix yang mencatat halaman/tabel, dataset, unit, label, split, metrik, batasan, dan relevansi langsung/berdekatan.
5. Simpan query/search date dan screening log untuk setiap literature review yang mengklaim retrieval funnel.

## Daftar isi setiap Markdown

> Link mengarah ke heading sumber asli apabila heading Markdown ada. Untuk file tanpa heading, butir diberi label outline sintetis dan tidak mengarah ke anchor yang tidak tersedia.

### 1. [ABSA Bank Digital.md](./ABSA%20Bank%20Digital.md)

> ABSA perbankan digital Indonesia; sintesis metode dan studi bank | 23 DOI unik-per-dokumen.
- [1. Introduction](./ABSA%20Bank%20Digital.md#1-introduction)
- [2. Methods](./ABSA%20Bank%20Digital.md#2-methods)
- [3. Results](./ABSA%20Bank%20Digital.md#3-results)
  - [3.1 Evolution of ABSA: From Classical ML to Deep Learning](./ABSA%20Bank%20Digital.md#31-evolution-of-absa-from-classical-ml-to-deep-learning)
  - [3.2 The Rise of Transformer Models: BERT & Variants](./ABSA%20Bank%20Digital.md#32-the-rise-of-transformer-models-bert-variants)
  - [3.3 Indonesian Digital Banking Case Studies](./ABSA%20Bank%20Digital.md#33-indonesian-digital-banking-case-studies)
  - [3.4 Critical Perspectives: Challenges & Limitations](./ABSA%20Bank%20Digital.md#34-critical-perspectives-challenges-limitations)
    - [Results Timeline](./ABSA%20Bank%20Digital.md#results-timeline)
    - [Top Contributors](./ABSA%20Bank%20Digital.md#top-contributors)
- [4. Discussion](./ABSA%20Bank%20Digital.md#4-discussion)
  - [Claims and Evidence Table](./ABSA%20Bank%20Digital.md#claims-and-evidence-table)
- [5. Conclusion](./ABSA%20Bank%20Digital.md#5-conclusion)
  - [Research Gaps](./ABSA%20Bank%20Digital.md#research-gaps)
  - [Open Research Questions](./ABSA%20Bank%20Digital.md#open-research-questions)
- [References](./ABSA%20Bank%20Digital.md#references)

### 2. [ABSA Dual Extraction.md](./ABSA%20Dual%20Extraction.md)

> ABSA/ASTE dual extraction pada ulasan game | 58 DOI unik-per-dokumen.
- [1. Introduction](./ABSA%20Dual%20Extraction.md#1-introduction)
- [2. Methods](./ABSA%20Dual%20Extraction.md#2-methods)
- [3. Results](./ABSA%20Dual%20Extraction.md#3-results)
  - [3.1 Key Papers](./ABSA%20Dual%20Extraction.md#31-key-papers)
  - [3.2 Perkembangan Metode](./ABSA%20Dual%20Extraction.md#32-perkembangan-metode)
  - [3.3 Temuan Domain Game](./ABSA%20Dual%20Extraction.md#33-temuan-domain-game)
  - [3.4 Keterbatasan dan Robustness](./ABSA%20Dual%20Extraction.md#34-keterbatasan-dan-robustness)
  - [Results Timeline](./ABSA%20Dual%20Extraction.md#results-timeline)
  - [Top Contributors](./ABSA%20Dual%20Extraction.md#top-contributors)
- [4. Discussion](./ABSA%20Dual%20Extraction.md#4-discussion)
- [5. Conclusion](./ABSA%20Dual%20Extraction.md#5-conclusion)
  - [Research Gaps](./ABSA%20Dual%20Extraction.md#research-gaps)
  - [Open Research Questions](./ABSA%20Dual%20Extraction.md#open-research-questions)
- [References](./ABSA%20Dual%20Extraction.md#references)

### 3. [ABSA Hotel.md](./ABSA%20Hotel.md)

> ABSA pada ulasan hotel | 11 DOI unik-per-dokumen.
- [Ringkasan Komparatif](./ABSA%20Hotel.md#ringkasan-komparatif)
- [Aspek yang Digunakan](./ABSA%20Hotel.md#aspek-yang-digunakan)
- [Tipe Model Dominan](./ABSA%20Hotel.md#tipe-model-dominan)
- [Sumber Dataset](./ABSA%20Hotel.md#sumber-dataset)
- [Metrik](./ABSA%20Hotel.md#metrik)
- [Keterbatasan Umum](./ABSA%20Hotel.md#keterbatasan-umum)

### 4. [ABSEA.md](./ABSEA.md)

> Aspect-based sentiment and emotion analysis pada game | 16 DOI unik-per-dokumen.
- [Ekstraksi Aspek Spesifik Game](./ABSEA.md#ekstraksi-aspek-spesifik-game)
- [Pemodelan Emosi dan Valensi Pemain](./ABSEA.md#pemodelan-emosi-dan-valensi-pemain)
- [Paradigma Model dan Tantangan Analisis](./ABSEA.md#paradigma-model-dan-tantangan-analisis)
- [References](./ABSEA.md#references)

### 5. [ACOS dan ACOSE Analisis Sentimen.md](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md)

> Formulasi ACOS/ACOSE, dataset, ekstraksi dan gap | 35 DOI unik-per-dokumen.
- [1. Introduction](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#1-introduction)
- [2. Methods](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#2-methods)
- [3. Results](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#3-results)
  - [3.1 Key Papers](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#31-key-papers)
  - [3.2 Struktur dan Dataset](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#32-struktur-dan-dataset)
  - [3.3 Pendekatan Ekstraksi](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#33-pendekatan-ekstraksi)
  - [3.4 ACOSE dan Formulasi Berdekatan](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#34-acose-dan-formulasi-berdekatan)
  - [Results Timeline](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#results-timeline)
  - [Top Contributors](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#top-contributors)
- [4. Discussion](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#4-discussion)
- [5. Conclusion](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#5-conclusion)
  - [Research Gaps](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#research-gaps)
  - [Open Research Questions](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#open-research-questions)
- [References](./ACOS%20dan%20ACOSE%20Analisis%20Sentimen.md#references)

### 6. [ACOSE Paling Kuat.md](./ACOSE%20Paling%20Kuat.md)

> Pilihan paradigma implementasi ACOSE (ML/DL/LLM) | 38 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Alur ACOSE dan diagram implementasi
  - Pipeline machine learning: kekuatan, kelemahan, bentuk realistis
  - Deep learning: BERT/CRF, generatif, multitugas, sintaks/graf
  - LLM generatif
  - Desain rekomendasi menurut skenario
  - Implikasi praktis
  - References

### 7. [ACOSQE Adalah Tugas Bukan Model.md](./ACOSQE%20Adalah%20Tugas%20Bukan%20Model.md)

> Pembedaan formulasi tugas ACOSQE dan keluarga model | 17 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Paradigma model
  - Tantangan opini implisit
  - Perbandingan arsitektur (Extract-Classify, SG-ACOS, GEN-SCL-NAT, DPML, MRC-CLRI)
  - Arah perkembangan ekstraksi
  - References

### 8. [Analisi IndoBERT.md](./Analisi%20IndoBERT.md)

> IndoBERT untuk 13 bank digital (versi tanpa heading Markdown) | 62 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Introduction
  - Methods dan angka retrieval/eligibility/inclusion
  - Results: key papers, performa, temuan perbankan, opinion/emotion
  - Results timeline dan top contributors
  - Discussion dan tabel kekuatan bukti
  - Conclusion: research gaps dan open questions
  - References

### 9. [Analisis ACOS.md](./Analisis%20ACOS.md)

> Batas ACOS terkait intensitas emosi, trigger, perilaku | 15 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Dimensi intensitas emosi
  - Pemicu perilaku konsumen
  - Kompleksitas sentimen dan bahasa alami
  - Perbandingan dimensi/metode
  - Opini dan aspek implisit
  - Regulasi respons manajerial
  - References

### 10. [ASTE vs ABSA.md](./ASTE%20vs%20ABSA.md)

> Perbedaan ASTE dan ABSA; robustness/domain shift | 35 DOI unik-per-dokumen.
- [Keunggulan Representasi](./ASTE%20vs%20ABSA.md#keunggulan-representasi)
- [Benchmark Kinerja](./ASTE%20vs%20ABSA.md#benchmark-kinerja)
- [Di Mana ASTE Unggul](./ASTE%20vs%20ABSA.md#di-mana-aste-unggul)
- [Ulasan Informal dan Pergeseran Domain](./ASTE%20vs%20ABSA.md#ulasan-informal-dan-pergeseran-domain)
- [Generalisasi dan Robustness](./ASTE%20vs%20ABSA.md#generalisasi-dan-robustness)
- [Batasan dan Implikasi Praktis](./ASTE%20vs%20ABSA.md#batasan-dan-implikasi-praktis)
- [References](./ASTE%20vs%20ABSA.md#references)

### 11. [BERT lebih Unggul dari ML.md](./BERT%20lebih%20Unggul%20dari%20ML.md)

> Klaim perbandingan BERT dengan model klasik untuk ABSA bank | 14 DOI unik-per-dokumen.
- [Perbandingan Kinerja Model](./BERT%20lebih%20Unggul%20dari%20ML.md#perbandingan-kinerja-model)
- [Arsitektur Pemodelan Sentimen Perbankan](./BERT%20lebih%20Unggul%20dari%20ML.md#arsitektur-pemodelan-sentimen-perbankan)
- [Faktor Keunggulan dan Keterbatasan](./BERT%20lebih%20Unggul%20dari%20ML.md#faktor-keunggulan-dan-keterbatasan)
- [References](./BERT%20lebih%20Unggul%20dari%20ML.md#references)

### 12. [BERTopic X ABSA.md](./BERTopic%20X%20ABSA.md)

> Integrasi BERTopic dengan ABSA dan batas bukti | 50 DOI unik-per-dokumen.
- [Keunggulan yang Terbukti](./BERTopic%20X%20ABSA.md#keunggulan-yang-terbukti)
- [Benchmark Penemuan Topik](./BERTopic%20X%20ABSA.md#benchmark-penemuan-topik)
- [Benchmark Ulasan Pelanggan](./BERTopic%20X%20ABSA.md#benchmark-ulasan-pelanggan)
- [Benchmark Ulasan Gaming](./BERTopic%20X%20ABSA.md#benchmark-ulasan-gaming)
- [Batas dan Evaluasi Pembanding](./BERTopic%20X%20ABSA.md#batas-dan-evaluasi-pembanding)
- [References](./BERTopic%20X%20ABSA.md#references)

### 13. [Deep Critical and Mapping ABSA.md](./Deep%20Critical%20and%20Mapping%20ABSA.md)

> Salinan identik tinjauan ABSA bank digital | 23 DOI unik-per-dokumen.
- [1. Introduction](./Deep%20Critical%20and%20Mapping%20ABSA.md#1-introduction)
- [2. Methods](./Deep%20Critical%20and%20Mapping%20ABSA.md#2-methods)
- [3. Results](./Deep%20Critical%20and%20Mapping%20ABSA.md#3-results)
  - [3.1 Evolution of ABSA: From Classical ML to Deep Learning](./Deep%20Critical%20and%20Mapping%20ABSA.md#31-evolution-of-absa-from-classical-ml-to-deep-learning)
  - [3.2 The Rise of Transformer Models: BERT & Variants](./Deep%20Critical%20and%20Mapping%20ABSA.md#32-the-rise-of-transformer-models-bert-variants)
  - [3.3 Indonesian Digital Banking Case Studies](./Deep%20Critical%20and%20Mapping%20ABSA.md#33-indonesian-digital-banking-case-studies)
  - [3.4 Critical Perspectives: Challenges & Limitations](./Deep%20Critical%20and%20Mapping%20ABSA.md#34-critical-perspectives-challenges-limitations)
    - [Results Timeline](./Deep%20Critical%20and%20Mapping%20ABSA.md#results-timeline)
    - [Top Contributors](./Deep%20Critical%20and%20Mapping%20ABSA.md#top-contributors)
- [4. Discussion](./Deep%20Critical%20and%20Mapping%20ABSA.md#4-discussion)
  - [Claims and Evidence Table](./Deep%20Critical%20and%20Mapping%20ABSA.md#claims-and-evidence-table)
- [5. Conclusion](./Deep%20Critical%20and%20Mapping%20ABSA.md#5-conclusion)
  - [Research Gaps](./Deep%20Critical%20and%20Mapping%20ABSA.md#research-gaps)
  - [Open Research Questions](./Deep%20Critical%20and%20Mapping%20ABSA.md#open-research-questions)
- [References](./Deep%20Critical%20and%20Mapping%20ABSA.md#references)

### 14. [Ekstraksi Quandruple ACOS.md](./Ekstraksi%20Quandruple%20ACOS.md)

> Formulasi quadruple ACOS dan keluarga model | 44 DOI unik-per-dokumen.
- [1. Introduction](./Ekstraksi%20Quandruple%20ACOS.md#1-introduction)
- [2. Methods](./Ekstraksi%20Quandruple%20ACOS.md#2-methods)
- [3. Results](./Ekstraksi%20Quandruple%20ACOS.md#3-results)
  - [3.1 Key Papers](./Ekstraksi%20Quandruple%20ACOS.md#31-key-papers)
  - [3.2 Struktur dan Benchmark](./Ekstraksi%20Quandruple%20ACOS.md#32-struktur-dan-benchmark)
  - [3.3 Keluarga Model](./Ekstraksi%20Quandruple%20ACOS.md#33-keluarga-model)
  - [3.4 Penyempurnaan dan Hasil](./Ekstraksi%20Quandruple%20ACOS.md#34-penyempurnaan-dan-hasil)
  - [Results Timeline](./Ekstraksi%20Quandruple%20ACOS.md#results-timeline)
  - [Top Contributors](./Ekstraksi%20Quandruple%20ACOS.md#top-contributors)
- [4. Discussion](./Ekstraksi%20Quandruple%20ACOS.md#4-discussion)
- [5. Conclusion](./Ekstraksi%20Quandruple%20ACOS.md#5-conclusion)
  - [Research Gaps](./Ekstraksi%20Quandruple%20ACOS.md#research-gaps)
  - [Open Research Questions](./Ekstraksi%20Quandruple%20ACOS.md#open-research-questions)
- [References](./Ekstraksi%20Quandruple%20ACOS.md#references)

### 15. [Implementasi ACOSE.md](./Implementasi%20ACOSE.md)

> Rancangan alur implementasi ACOSE lintas paradigma | 17 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Alur implementasi ACOSE lintas paradigma
  - Pipeline machine learning tradisional
  - Representasi terpadu deep learning
  - Generasi quintuplet menggunakan LLM
  - References

### 16. [IndoBERT Unggul.md](./IndoBERT%20Unggul.md)

> Kinerja IndoBERT, ekstraksi aspek, dan opsi hybrid ACOSE | 6 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Kinerja IndoBERT pada sentimen perbankan
  - Ekstraksi aspek dan struktur entitas
  - Integrasi hibrida menuju ACOSE
  - Perbandingan paradigma, bukti, dan limitasi operasional
  - References

### 17. [Indonesia AI NLP Mixed Code.md](./Indonesia%20AI%20NLP%20Mixed%20Code.md)

> Pemetaan NLP/AI untuk Indonesia, bahasa daerah, dan code-mixing | 24 DOI unik-per-dokumen.
- [1. Introduction](./Indonesia%20AI%20NLP%20Mixed%20Code.md#1-introduction)
- [2. Methods](./Indonesia%20AI%20NLP%20Mixed%20Code.md#2-methods)
- [3. Results](./Indonesia%20AI%20NLP%20Mixed%20Code.md#3-results)
  - [3.1 Foundational Datasets and Models (Bahasa Indonesia)](./Indonesia%20AI%20NLP%20Mixed%20Code.md#31-foundational-datasets-and-models-bahasa-indonesia)
  - [3.2 Regional and Low-Resource Languages](./Indonesia%20AI%20NLP%20Mixed%20Code.md#32-regional-and-low-resource-languages)
  - [3.3 Domain-Specific and Cultural Benchmarks](./Indonesia%20AI%20NLP%20Mixed%20Code.md#33-domain-specific-and-cultural-benchmarks)
  - [3.4 Model Innovations and Evaluation](./Indonesia%20AI%20NLP%20Mixed%20Code.md#34-model-innovations-and-evaluation)
    - [Results Timeline](./Indonesia%20AI%20NLP%20Mixed%20Code.md#results-timeline)
    - [Top Contributors](./Indonesia%20AI%20NLP%20Mixed%20Code.md#top-contributors)
- [4. Discussion](./Indonesia%20AI%20NLP%20Mixed%20Code.md#4-discussion)
  - [Claims and Evidence Table](./Indonesia%20AI%20NLP%20Mixed%20Code.md#claims-and-evidence-table)
- [5. Conclusion](./Indonesia%20AI%20NLP%20Mixed%20Code.md#5-conclusion)
  - [Research Gaps](./Indonesia%20AI%20NLP%20Mixed%20Code.md#research-gaps)
  - [Open Research Questions](./Indonesia%20AI%20NLP%20Mixed%20Code.md#open-research-questions)
- [References](./Indonesia%20AI%20NLP%20Mixed%20Code.md#references)

### 18. [Integrasi ACOSE.md](./Integrasi%20ACOSE.md)

> Rasionalisasi integrasi aspek, sentimen, emosi; ML/DL/LLM | 18 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Rasionalitas formalisasi elemen ACOSE
  - Hubungan machine learning dan deep learning
  - Perbandingan paradigma dan karakteristik operasional
  - Relevansi pendekatan LLM generatif
  - References

### 19. [Labeling ACOS.md](./Labeling%20ACOS.md)

> Strategi pelabelan ACOS/weak labels dan quality control | 47 DOI unik-per-dokumen.
- [1. Introduction](./Labeling%20ACOS.md#1-introduction)
- [2. Methods](./Labeling%20ACOS.md#2-methods)
- [3. Results](./Labeling%20ACOS.md#3-results)
  - [3.1 Key Papers](./Labeling%20ACOS.md#31-key-papers)
  - [3.2 Weak dan Pseudo Label](./Labeling%20ACOS.md#32-weak-dan-pseudo-label)
  - [3.3 Alternatif Pelabelan](./Labeling%20ACOS.md#33-alternatif-pelabelan)
  - [3.4 Hasil dan Kontrol Mutu](./Labeling%20ACOS.md#34-hasil-dan-kontrol-mutu)
  - [Results Timeline](./Labeling%20ACOS.md#results-timeline)
  - [Top Contributors](./Labeling%20ACOS.md#top-contributors)
- [4. Discussion](./Labeling%20ACOS.md#4-discussion)
- [5. Conclusion](./Labeling%20ACOS.md#5-conclusion)
  - [Research Gaps](./Labeling%20ACOS.md#research-gaps)
  - [Open Research Questions](./Labeling%20ACOS.md#open-research-questions)
- [References](./Labeling%20ACOS.md#references)

### 20. [Limitation ACOS.md](./Limitation%20ACOS.md)

> Batas ACOS terhadap emosi, cause, dan intensity | 49 DOI unik-per-dokumen.
- [1. Introduction](./Limitation%20ACOS.md#1-introduction)
- [2. Methods](./Limitation%20ACOS.md#2-methods)
- [3. Results](./Limitation%20ACOS.md#3-results)
  - [3.1 Key Papers](./Limitation%20ACOS.md#31-key-papers)
  - [3.2 ACOS Coverage Versus Emotional Coverage](./Limitation%20ACOS.md#32-acos-coverage-versus-emotional-coverage)
  - [3.3 Emotion, Cause, and Intensity Alternatives](./Limitation%20ACOS.md#33-emotion-cause-and-intensity-alternatives)
  - [3.4 Behavioral Stakes](./Limitation%20ACOS.md#34-behavioral-stakes)
  - [Results Timeline](./Limitation%20ACOS.md#results-timeline)
  - [Top Contributors](./Limitation%20ACOS.md#top-contributors)
- [4. Discussion](./Limitation%20ACOS.md#4-discussion)
- [5. Conclusion](./Limitation%20ACOS.md#5-conclusion)
  - [Research Gaps](./Limitation%20ACOS.md#research-gaps)
  - [Open Research Questions](./Limitation%20ACOS.md#open-research-questions)
- [References](./Limitation%20ACOS.md#references)

### 21. [Literature ACOSE.md](./Literature%20ACOSE.md)

> Literatur ACOSE pada perbankan digital Indonesia | 32 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Introduction
  - Methods dan alur pencarian
  - Results: key papers, benchmark IndoBERT, paradigma, emosi per-aspek
  - Results timeline dan top contributors
  - Discussion dan tabel evidence
  - Conclusion: research gaps dan open questions
  - References

### 22. [Matrix ABSA.md](./Matrix%20ABSA.md)

> Matriks literatur ABSA dan fine-tuning BERT | 29 DOI unik-per-dokumen.
- [1. ABSA Berbasis Transformer](./Matrix%20ABSA.md#1-absa-berbasis-transformer)
- [2. Fine-Tuning dan Hyperparameter](./Matrix%20ABSA.md#2-fine-tuning-dan-hyperparameter)
- [3. Ulasan Gim dan Dinamika Sentimen](./Matrix%20ABSA.md#3-ulasan-gim-dan-dinamika-sentimen)
- [4. Sintesis dan Celah Tesis](./Matrix%20ABSA.md#4-sintesis-dan-celah-tesis)
  - [Rancangan yang Direkomendasikan](./Matrix%20ABSA.md#rancangan-yang-direkomendasikan)
- [References](./Matrix%20ABSA.md#references)

### 23. [Optimasi Hyperparameter BERT.md](./Optimasi%20Hyperparameter%20BERT.md)

> Strategi tuning hyperparameter BERT untuk ABSA | 15 DOI unik-per-dokumen.
- [Pola Konfigurasi yang Muncul](./Optimasi%20Hyperparameter%20BERT.md#pola-konfigurasi-yang-muncul)
- [Strategi Pencarian: Dari Manual hingga Metaheuristik](./Optimasi%20Hyperparameter%20BERT.md#strategi-pencarian-dari-manual-hingga-metaheuristik)
- [Bukti Spesifik pada Tugas ABSA](./Optimasi%20Hyperparameter%20BERT.md#bukti-spesifik-pada-tugas-absa)
- [Perbandingan Studi Tuning](./Optimasi%20Hyperparameter%20BERT.md#perbandingan-studi-tuning)
- [Implikasi dan Titik Lemah](./Optimasi%20Hyperparameter%20BERT.md#implikasi-dan-titik-lemah)
- [References](./Optimasi%20Hyperparameter%20BERT.md#references)

### 24. [Optimasi UMAP BERTopic.md](./Optimasi%20UMAP%20BERTopic.md)

> Parameter UMAP/HDBSCAN, coherence, dan outlier BERTopic | 26 DOI unik-per-dokumen.
- [Pengaruh terhadap Koherensi](./Optimasi%20UMAP%20BERTopic.md#pengaruh-terhadap-koherensi)
- [Optimasi Dimensi UMAP](./Optimasi%20UMAP%20BERTopic.md#optimasi-dimensi-umap)
- [Selektivitas Klaster HDBSCAN](./Optimasi%20UMAP%20BERTopic.md#selektivitas-klaster-hdbscan)
- [c-TF-IDF dan Pemulihan Outlier](./Optimasi%20UMAP%20BERTopic.md#c-tf-idf-dan-pemulihan-outlier)
- [Interpretasi Cv dan NPMI](./Optimasi%20UMAP%20BERTopic.md#interpretasi-cv-dan-npmi)
- [References](./Optimasi%20UMAP%20BERTopic.md#references)

### 25. [Pemetaan ABSA.md](./Pemetaan%20ABSA.md)

> Taksonomi triplet dan subtask ABSA | 70 DOI unik-per-dokumen.
- [1. Introduction](./Pemetaan%20ABSA.md#1-introduction)
- [2. Methods](./Pemetaan%20ABSA.md#2-methods)
- [3. Results](./Pemetaan%20ABSA.md#3-results)
  - [3.1 Key Papers](./Pemetaan%20ABSA.md#31-key-papers)
  - [3.2 Pemetaan Istilah](./Pemetaan%20ABSA.md#32-pemetaan-istilah)
  - [3.3 Representasi dan Pengaitan](./Pemetaan%20ABSA.md#33-representasi-dan-pengaitan)
  - [3.4 Sintaksis dan Supervisi](./Pemetaan%20ABSA.md#34-sintaksis-dan-supervisi)
  - [Results Timeline](./Pemetaan%20ABSA.md#results-timeline)
  - [Top Contributors](./Pemetaan%20ABSA.md#top-contributors)
- [4. Discussion](./Pemetaan%20ABSA.md#4-discussion)
- [5. Conclusion](./Pemetaan%20ABSA.md#5-conclusion)
  - [Research Gaps](./Pemetaan%20ABSA.md#research-gaps)
  - [Open Research Questions](./Pemetaan%20ABSA.md#open-research-questions)
- [References](./Pemetaan%20ABSA.md#references)

### 26. [Rekomendasi ACOSE.md](./Rekomendasi%20ACOSE.md)

> Rekomendasi arah pengembangan ACOSE dan intensitas | 12 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Rekomendasi ekspansi ACOSE/intensitas
  - Integrasi ruang afektif berdimensi
  - Resolusi dependensi implisit konteks
  - References

### 27. [TinjauanABSA.md](./TinjauanABSA.md)

> Tinjauan ABSA dual extraction pada game (versi tanpa heading Markdown) | 58 DOI unik-per-dokumen.
- **Outline sintetis (sumber tidak memiliki heading Markdown):**
  - Introduction
  - Methods dan alur pencarian
  - Results: key papers, perkembangan metode, game domain, robustness
  - Results timeline dan top contributors
  - Discussion dan klaim/evidence table
  - Conclusion: research gaps dan open questions
  - References

## Inventaris PDF pendukung

> PDF dicatat sebagai lampiran/referensi; isi PDF belum diekstrak atau diverifikasi dalam survei Markdown ini.

- [ABOSA_Aspect_Based_Opinion_and_Sentiment_Analysis.pdf](./ABOSA_Aspect_Based_Opinion_and_Sentiment_Analysis.pdf) (523,492 bytes)
- [ACOS_ACOSQE_Aspect_Category_Opinion_Sentiment_Qu (1).pdf](./ACOS_ACOSQE_Aspect_Category_Opinion_Sentiment_Qu%20%281%29.pdf) (408,074 bytes)
- [ACOS_ACOSQE_Aspect_Category_Opinion_Sentiment_Qu.pdf](./ACOS_ACOSQE_Aspect_Category_Opinion_Sentiment_Qu.pdf) (408,074 bytes)
- [apa_saran_nya_Aspect_Category_Opinion_Sentimen.pdf](./apa_saran_nya_Aspect_Category_Opinion_Sentimen.pdf) (131,010 bytes)
- [Apakah_IndoBERT_unggul_untuk_ACOSE_di_domain_perba.pdf](./Apakah_IndoBERT_unggul_untuk_ACOSE_di_domain_perba.pdf) (172,455 bytes)
- [aspect_based_sentiment_analysis_with_bert_indobert.pdf](./aspect_based_sentiment_analysis_with_bert_indobert.pdf) (214,945 bytes)
- [Aspect_Category_Opinion_Sentiment_Emotion_Bank_Dig.pdf](./Aspect_Category_Opinion_Sentiment_Emotion_Bank_Dig.pdf) (456,059 bytes)
- [aspect_sentiment_triplet_extraction.pdf](./aspect_sentiment_triplet_extraction.pdf) (368,501 bytes)
- [Bagaimana_ACOSE_dapat_dilakukan_Pipeline_Machine_.pdf](./Bagaimana_ACOSE_dapat_dilakukan_Pipeline_Machine_.pdf) (211,714 bytes)
- [Current_fine-grained_opinion_mining_systems_like (1).pdf](./Current_fine-grained_opinion_mining_systems_like%20%281%29.pdf) (170,801 bytes)
- [Current_fine-grained_opinion_mining_systems_like.pdf](./Current_fine-grained_opinion_mining_systems_like.pdf) (156,840 bytes)
- [Does_ACOSQE_outperform_generative_models_on_implic.pdf](./Does_ACOSQE_outperform_generative_models_on_implic.pdf) (352,130 bytes)
- [Kesenjangan_paling_mencolok_dalam_literatur_adalah.pdf](./Kesenjangan_paling_mencolok_dalam_literatur_adalah.pdf) (170,990 bytes)
- [Mengapa_harus_Aspect_Category_Opinion_Sentiment.pdf](./Mengapa_harus_Aspect_Category_Opinion_Sentiment.pdf) (164,607 bytes)
- [Relevansi_Kolerasi_Masalah_Dampak_Analisis_Aspe.pdf](./Relevansi_Kolerasi_Masalah_Dampak_Analisis_Aspe.pdf) (496,466 bytes)
- [Secara_Fundamental_Mengapa_ACOSE_diperlukan_bukan.pdf](./Secara_Fundamental_Mengapa_ACOSE_diperlukan_bukan.pdf) (190,877 bytes)
- [Survey_and_Mapping_Deep_Critical_Analysis_Aspect.pdf](./Survey_and_Mapping_Deep_Critical_Analysis_Aspect.pdf) (421,578 bytes)
- [What_are_the_state-of-the-art_approaches_for_Multi.pdf](./What_are_the_state-of-the-art_approaches_for_Multi.pdf) (205,378 bytes)
- [what_is_aspect_based_sentiment_analysis.pdf](./what_is_aspect_based_sentiment_analysis.pdf) (162,509 bytes)

## Batas survei

Indeks ini menginventaris nama/ukuran file, heading Markdown, DOI yang tertulis, overlap referensi, hash berkas, dan kemiripan teks untuk menandai duplikasi. Pemeriksaan ini **bukan verifikasi bibliografi eksternal**: keberadaan DOI, akurasi metadata, kualitas peer-review, dan kebenaran metrik paper harus diperiksa terhadap halaman penerbit atau naskah sumber. Outline sintetis ditandai eksplisit dan tidak mengubah sumber.
