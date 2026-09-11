# 030 — Analisis Komparatif Kritis: Baseline BERT vs IndoBERT pada ACOS Quadruple Extraction

> Tanggal: 10 September 2026
> Status: **analisis statis** — tidak ada pelatihan dijalankan di mesin ini
> Metode: inspeksi output cell notebook + laporan terdahulu + metrik dari sesi Colab
> Dataset yang dibandingkan: rest16 (BERT) vs appsid (IndoBERT)

---

## 1. Ringkasan Eksekutif (TL;DR)

Perbandingan langsung antara Baseline BERT dan IndoBERT **tidak dapat dilakukan secara apples-to-apples**. Kedua eksperimen berjalan di atas dataset, domain, bahasa, granularitas input, dan kualitas label yang sepenuhnya berbeda. Satu-satunya metrik yang tersedia untuk BERT adalah Step 1 Micro-F1 = **81.23%** pada rest16 (Inggris, restoran, 2.484 training quadruple, A100), itupun tanpa hasil Step 2 karena pipeline crash. Sementara IndoBERT mencapai Step 1 Micro-F1 = **97.94%** dan Step 2 Quadruple F1 = **67.86%** pada appsid (Indonesia, bank digital, 72.973 training quadruple, T4), dengan catatan Step 2 baru berjalan 1 dari 15 epoch yang direncanakan.

Angka-angka ini tidak bisa dibandingkan secara langsung karena **ukuran dataset mendominasi**: appsid memiliki 25× lebih banyak training quadruple daripada rest16, dan menggunakan input klausa pendek yang secara inheren lebih mudah untuk span extraction. Gap 16.7 poin di Step 1 (97.94% vs 81.23%) adalah artefak dari perbedaan dataset, bukan bukti keunggulan IndoBERT atas BERT.

Tiga temuan kritis: (1) bug `KeyError: 'a--1,-1'` menggagalkan BERT baseline sebelum menghasilkan metrik end-to-end; (2) dual-head metrics bug membuat evaluasi independen kategori dan sentimen di IndoBERT menghasilkan 0.00%; (3) risiko silent random encoder akibat prefix `bert.` yang hilang di IndoBERT checkpoint belum diverifikasi (Gate 1). Sebelum ketiga masalah ini diselesaikan, klaim apapun tentang "model mana yang lebih baik" bersifat prematur.

---

## 2. Matriks Perbandingan Penuh

| Dimensi | BERT Baseline | IndoBERT V4 |
|---|---|---|
| **Dataset** | rest16 (Restaurant-ACOS) | appsid (Apps-ACOS) |
| **Bahasa** | Inggris | Indonesia |
| **Domain** | Ulasan restoran | Ulasan aplikasi bank digital |
| **Sumber data** | SemEval-2016 Task 5 + anotasi manual | 43.673 ulasan dari 13 aplikasi (App Store + Play Store) |
| **Unit input** | Kalimat penuh (full sentence) | Klausa (clause-level split) |
| **Jumlah train** | 1.530 kalimat / 2.484 quadruple | 60.159 klausa / 72.973 quadruple |
| **Jumlah dev** | 171 kalimat / 261 quadruple | 8.027 klausa / 9.587 quadruple |
| **Jumlah test** | 583 kalimat / 916 quadruple | 7.891 klausa / 9.514 quadruple |
| **Rasio train:test** | 2.7 : 1 | 7.7 : 1 |
| **Jumlah kategori** | 13 (`ENTITY#ATTRIBUTE`) | 13 (flat, tanpa `#`) |
| **Kualitas label** | Manual (gold standard) | Weak labeling otomatis (floor=0.3, saturation=2.0) |
| **Implicit aspect** | Ada (jumlah rendah) | 30.1% dari seluruh aspect |
| **Implicit opinion** | Ada (jumlah rendah) | 40.6% dari seluruh opinion |
| **Distribusi sentimen** | Tidak terdokumentasi di repo | Negatif 49.8% / Netral 11.3% / Positif 38.9% |
| **Arsitektur backbone** | `bert-base-uncased` (110M param) | `indobert-base-p1` (~124M param) |
| **Encoder** | 12 layer, 768 hidden, 12 head | **Identik** (12/768/12) |
| **Vocab** | 30.522 token | 50.000 (30.521 terpakai) |
| **Step 2 head** | Single-head: `Linear(1536, 39)` | Dual-head: `Linear(1536, 13)` + `Linear(1536, 3)` |
| **GPU saat training** | NVIDIA A100-SXM4-40GB | Tesla T4 14.46 GB |
| **Step 1 — epoch selesai** | 15/15 | 8/15 (terminasi dini) |
| **Step 1 — best Micro-F1** | **81.23%** (epoch 6) | **97.94%** (epoch 8) |
| **Step 2 — epoch selesai** | 0 (crash) | 1/15 (MAX_EPOCHS_THIS_RUN=1) |
| **Step 2 — Quadruple F1** | **Tidak tersedia** | **67.86%** (epoch 1) |
| **Dual-head metrics** | N/A (single-head) | 0.00% (bug — `latest_cat_logits` tidak terisi) |
| **Bug diketahui** | `KeyError: 'a--1,-1'` di Step 2 | Prefix `bert.` hilang (Gate 1 pending) + dual-head metrics null |
| **Resume checkpointing** | Tidak ada | Per-epoch (level 3: weight + optimizer + LR) |
| **Early stopping** | Tidak ada | PATIENCE=5, MIN_EPOCHS_BEFORE_STOP=5 |
| **Mixed precision** | FP32 (default) | AMP/FP16 (di Step 2) |
| **Batch size** | Tidak tercatat (default paper) | 32 (Step 1 & 2) |

> **Catatan kritis**: Kedua eksperimen berjalan di GPU yang berbeda (A100 vs T4), tetapi ini tidak memengaruhi metrik F1 — hanya durasi pelatihan. Tidak ada hasil untuk laptop (Laptop-ACOS) dari backbone manapun.

---

## 3. Analisis Dataset: rest16 vs appsid

### 3.1 Skala — Faktor Dominan

Perbedaan skala antara kedua dataset sangat ekstrem:

| Metrik | rest16 | appsid | Rasio |
|---|---|---|---|
| Training quadruple | 2.484 | 72.973 | **1 : 29** |
| Training kalimat/klausa | 1.530 | 60.159 | **1 : 39** |
| Test quadruple | 916 | 9.514 | **1 : 10** |
| Rata-rata quad per unit | 1.62 | 1.21 | — |

Dengan hanya 2.484 training quadruple, BERT baseline pada rest16 beroperasi dalam rezim **low-resource**. Sebaliknya, appsid dengan 72.973 training quadruple berada di rezim **data-abundant**. Ini adalah faktor tunggal terbesar yang menjelaskan gap F1, jauh melampaui perbedaan arsitektur model.

Dalam NLP, aturan praktisnya: menggandakan data biasanya memberikan peningkatan yang lebih besar daripada mengganti arsitektur. Di sini kita berbicara tentang **29× lebih banyak data**, bukan sekadar 2×.

### 3.2 Domain — Dampak pada Kompleksitas Linguistik

**rest16 (restoran)**:
- Aspek bernama entitas seperti `RESTAURANT#GENERAL`, `FOOD#QUALITY`, `SERVICE#GENERAL`, `AMBIENCE#GENERAL`
- Opinion sering berupa frasa adjektiva kompleks: "reasonably priced", "not particularly friendly", "perfectly cooked"
- Kalimat cenderung panjang (review restoran naratif)
- Aspek dan opinion bisa terpisah jauh dalam satu kalimat

**appsid (bank digital)**:
- Aspek teknis singkat: `ONBOARDING_KYC`, `TRANSACTION_TRANSFER`, `UI_UX_DESIGN`, `APP_PERFORMANCE`
- Opinion cenderung pendek dan formulaik: "bagus", "lambat", "error terus", "mantap"
- Klausa pendek (hasil split) — rata-rata mungkin 5-10 token
- Aspek dan opinion sering berdekatan dalam klausa yang sama

**Implikasi**: Domain restoran secara inheren lebih sulit untuk span extraction karena:
1. Aspek multi-kata ("dulce de leche gelato") vs aspek sering implisit di appsid ("aplikasinya" → `APP_PERFORMANCE`)
2. Opinion panjang dengan negasi dan hedging vs opinion singkat dan langsung
3. Jarak aspek-opinion yang lebih jauh

### 3.3 Granularitas Unit — Klausa vs Kalimat

Keputusan desain paling berdampak di appsid adalah memecah ulasan menjadi klausa:

- **Satu baris ACOS = satu klausa**, bukan satu ulasan penuh
- Ini menghasilkan 80.260 klausa dari 43.673 ulasan
- Pemecahan klausa mencapai **100% mapping** aspek/opinion eksplisit; tanpa pemecahan, hanya 61.5% aspek dan 48.0% opinion yang terpetakan

Konsekuensi untuk Step 1 (span extraction): klausa pendek berarti:
- Lebih sedikit token per input → ruang pencarian span lebih kecil
- Lebih sedikit kandidat pasangan aspek-opinion → lebih sedikit peluang false positive
- Konteks lebih fokus → representasi BERT lebih tajam

Ini menjelaskan mengapa Step 1 di appsid mencapai 97.94% F1 — tugasnya secara fundamental lebih mudah. Bandingkan dengan rest16 yang harus mengekstrak span dari kalimat restoran naratif yang panjang.

### 3.4 Kualitas Label — Manual vs Weak

| Aspek | rest16 | appsid |
|---|---|---|
| Metode anotasi | Manual oleh ahli (gold) | Otomatis dengan lexicon + heuristik |
| Parameter weak labeling | N/A | floor=0.3, saturation_evidence=2.0 |
| Implicit aspect | Ditandai manual | 30.1% (deteksi otomatis) |
| Implicit opinion | Ditandai manual | 40.6% (deteksi otomatis) |
| Multi-label | Tidak ada | 0.4% (255 dari 65.423 pair rows) |

**Konsekuensi kritis**: Label di appsid mengandung noise dari weak labeling. Model dilatih pada target yang tidak 100% akurat. Efeknya paradoksal:
- **Menguntungkan**: noise bertindak sebagai regularisasi, mencegah overfitting pada dataset besar
- **Merugikan**: metrik evaluasi mengukur seberapa baik model mereplikasi noise, bukan seberapa baik model menangkap fenomena linguistik sebenarnya

Ini berarti 67.86% Quadruple F1 di appsid tidak bisa dibandingkan dengan ekspektasi metrik di rest16. Weak label cenderung menaikkan recall (banyak true positive yang "benar" menurut gold tapi tidak ada di weak label dihitung sebagai false negative) dan menurunkan precision (weak label bisa salah menandai negatif sebagai positif).

### 3.5 Distribusi Sentimen

**appsid**:
- Negatif (0): 49.8%
- Netral (1): 11.3%
- Positif (2): 38.9%

Ketidakseimbangan sentimen (netral hanya 11.3%) membuat sentimen netral rentan terhadap poor recall. Model bisa mencapai akurasi tinggi hanya dengan memprediksi negatif dan positif, mengabaikan netral sama sekali. Dual-head seharusnya bisa mendeteksi ini, tapi bug metrics membuat evaluasi independen tidak tersedia.

Untuk rest16, distribusi sentimen tidak tercatat dalam repo, sehingga tidak bisa dibandingkan.

### 3.6 Implicit vs Explicit

appsid memiliki proporsi implisit yang sangat tinggi:
- **30.1% implicit aspect** — aspect tidak disebutkan eksplisit dalam teks, harus diinferensi
- **40.6% implicit opinion** — opinion tidak muncul sebagai span tekstual

Ini adalah tantangan besar untuk Step 1 (span extraction). BERT-CRF hanya bisa mengekstrak span eksplisit. Untuk kasus implisit, model harus:
1. Mengenali bahwa ada quadruple tanpa span tekstual
2. Menyerahkan penanganan ke Step 2 untuk klasifikasi

Proporsi implisit yang tinggi di appsid bisa menjadi faktor yang menekan Step 1 F1 — tapi anehnya tidak, karena F1 mencapai 97.94%. Ini mengindikasikan bahwa sebagian besar quadruple dengan implicit aspect/opinion tetap memiliki setidaknya satu span eksplisit (aspect atau opinion) yang bisa diekstrak, dan BERT-CRF cukup untuk itu.

---

## 4. Analisis Arsitektur Model

### 4.1 Backbone — Hampir Identik

| Komponen | BERT (`bert-base-uncased`) | IndoBERT (`indobert-base-p1`) | Dampak |
|---|---|---|---|
| Encoder layers | 12 | 12 | Nol |
| Hidden size | 768 | 768 | Nol |
| Attention heads | 12 | 12 | Nol |
| Max position | 512 | 512 | Nol |
| Vocab size (config) | 30.522 | 50.000 | +19.478 embedding |
| Vocab tokens aktual | 30.522 | 30.521 | Hampir sama |
| Embedding params | ~23.8M | ~38.4M | +14.6M (15%) |
| Total params | ~110M | ~124M | +14M (13%) |
| `bert.` prefix | **Ada** | **Tidak ada** | ⚠️ Bug risiko |

Encoder 12-layer keduanya identik secara arsitektur. Perbedaan hanya di lapisan embedding — IndoBERT memiliki 50.000 slot embedding (meski hanya 30.521 yang terpakai) vs 30.522 di BERT.

**Dampak 14M parameter tambahan**:
- VRAM tambahan: ~56 MB (14M × 4 bytes/param FP32)
- Dari total 14.56 GB di T4, ini kurang dari 0.4% — **dampak terhadap training hampir nol**
- Kecepatan per step hampir identik, seperti yang sudah dianalisis di laporan 025

### 4.2 Single-Head vs Dual-Head Step 2

Ini adalah **perbedaan arsitektur paling signifikan** antara kedua pipeline:

**BERT Baseline — Single-Head (39 label)**:
```
BERT pooled output (768) × 2 = 1536 → Linear(1536, 39) → BCEWithLogitsLoss
```
- 39 label = 13 kategori × 3 sentimen (fused)
- Tidak bisa mengevaluasi kategori dan sentimen secara independen
- Error propagation tersembunyi: salah kategori → salah sentimen

**IndoBERT V4 — Dual-Head (13 + 3 label)**:
```
BERT pooled output (768) × 2 = 1536 → ┬─ Linear(1536, 13) → BCEWithLogitsLoss (kategori)
                                       └─ Linear(1536, 3)  → CrossEntropyLoss (sentimen)
```
- Kategori: 13 label, multi-label BCE
- Sentimen: 3 kelas, multi-class CE (dengan masking untuk sampel negatif)
- Fused logits (39-d) direkonstruksi untuk backward compatibility dengan `pair_eval`
- Seharusnya bisa melaporkan Category Micro-F1 dan Sentiment Accuracy per epoch

**Bug kritis**: Dual-head metrics melaporkan 0.00% untuk category_micro_f1 dan sentiment_accuracy. Root cause: `latest_cat_logits` dan `latest_senti_logits` adalah atribut side-effect yang hanya diisi selama `forward()` di training loop. Saat evaluasi dari cache, `model_step2_best.eval()` tidak memicu side-effect ini, sehingga metric extraction membaca tensor kosong.

### 4.3 Bug Prefix `bert.` — Silent Random Encoder

Ini adalah **risiko paling serius** yang belum diverifikasi:

- `BertForQuadABSA` di `modeling.py` mengekspektasi checkpoint dengan prefix `bert.` pada semua 199 kunci encoder
- IndoBERT checkpoint menyimpan kunci **tanpa** prefix `bert.`
- Notebook V4 memiliki adapter yang menambahkan prefix — tapi Gate 1 (verifikasi numerik dengan torch) **belum pernah dijalankan**
- Jika adapter gagal: seluruh 199 kunci encoder masuk ke `missing_keys`, encoder diinisialisasi random, dan training berjalan di atas representasi acak
- Logging yang seharusnya melaporkan ini **di-comment out** di `modeling.py:749-755`

Konsekuensi jika bug ini aktif: semua metrik IndoBERT (97.94% Step 1, 67.86% Step 2) menjadi tidak berarti — model hanya belajar dari representasi random.

---

## 5. Dinamika Training: Step 1 (BERT-CRF Span Extraction)

### 5.1 BERT Baseline — rest16 (A100, 15 epoch)

| Epoch | Loss | Micro-F1 |
|---|---|---|
| 1 | — | — |
| ... | ... | ... |
| **6** | — | **81.23%** |
| 7-15 | — | — |

Hanya best F1 yang tercatat di output notebook. Tidak ada tabel per-epoch, tidak ada precision/recall, tidak ada TP/FP/FN. Keterbatasan serius untuk analisis — kita tidak tahu apakah F1 masih naik atau sudah plateau di epoch 6.

Dengan 1.530 kalimat training, 15 epoch ≈ 22.950 langkah. Untuk dataset sekecil ini, 81.23% adalah angka yang wajar — bukan state-of-the-art tapi bukan juga kegagalan.

### 5.2 IndoBERT V4 — appsid (T4, 8/15 epoch)

| Epoch | Loss | TP | FP | FN | Precision% | Recall% | Micro-F1% |
|---|---|---|---|---|---|---|---|
| 1 | 2.1422 | 16.084 | 993 | 689 | 94.19 | 95.89 | 95.03 |
| 2 | 0.5881 | 16.311 | 630 | 462 | 96.28 | 97.25 | 96.76 |
| 3 | 0.3933 | 16.487 | 633 | 286 | 96.30 | 98.29 | 97.29 |
| 4 | 0.2903 | 16.463 | 491 | 310 | 97.10 | 98.15 | 97.63 |
| 5 | 0.2213 | 16.462 | 518 | 311 | 96.95 | 98.15 | 97.54 |
| 6 | 0.1763 | 16.445 | 450 | 328 | 97.34 | 98.04 | 97.69 |
| 7 | 0.1330 | 16.485 | 485 | 288 | 97.14 | 98.28 | 97.71 |
| **8** | **0.0999** | **16.514** | **434** | **259** | **97.44** | **98.46** | **97.94** |

**Analisis loss curve**:
- Loss turun drastis dari 2.14 → 0.59 dalam 1 epoch (72% penurunan) — sangat cepat
- Setelah epoch 3, loss sudah di bawah 0.40, dan F1 sudah di atas 97%
- Dari epoch 4 ke 8, peningkatan F1 hanya 0.31 poin (97.63% → 97.94%) — mendekati plateau
- FN turun dari 689 → 259 (62% pengurangan) — model semakin jarang melewatkan span
- TP stabil di sekitar 16.500 — jumlah total span entity yang bisa diekstrak mendekati maksimum

**Mengapa konvergensi sangat cepat?**
1. Klausa pendek → BERT-CRF hanya perlu melabeli 5-10 token per input
2. Dataset besar (60K klausa) → model melihat banyak variasi dalam 1 epoch
3. Sequence labeling untuk 6 label (O, B-A, I-A, B-O, I-O) adalah tugas yang relatif mudah dengan pretrained encoder
4. F1 sudah 95% di epoch 1 — sebagian besar "pembelajaran" terjadi di epoch pertama

**Mengapa 97.94% vs 81.23%? Analisis kontribusi:**

| Faktor | Estimasi Kontribusi | Justifikasi |
|---|---|---|
| Klausa pendek vs kalimat penuh | +8-10 poin | Rentang token lebih pendek → lebih sedikit kandidat span |
| 29× lebih banyak data | +5-7 poin | Generalisasi lebih baik, lebih sedikit overfitting |
| Domain lebih sederhana (bank vs restoran) | +2-3 poin | Opinion pendek dan formulaik, bukan frasa adjektiva kompleks |
| IndoBERT vs BERT (backbone) | **~0 poin** | Arsitektur encoder identik; embedding tambahan tidak relevan untuk span extraction |
| Jumlah parameter (+14M) | **~0 poin** | Embedding tambahan hanya memengaruhi token langka, bukan kualitas representasi kontekstual |

**Kesimpulan**: Gap 16.7 poin hampir seluruhnya berasal dari karakteristik dataset, bukan dari model. Jika BERT dilatih pada appsid (dalam bahasa Inggris), kemungkinan akan mencapai F1 yang sebanding.

---

## 6. Dinamika Training: Step 2 (Category-Sentiment Classification)

### 6.1 BERT Baseline — CRASH

Pipeline BERT gagal di Step 2 dengan `KeyError: 'a--1,-1'`. Root cause:
- `eval_metrics.py` menulis implicit aspect sebagai token literal `a--1,-1`
- Cell 12 notebook mem-parsing `pred4pipeline.txt` dengan logika manual (`ele[2:]`)
- Cell 14 memanggil `convert_tokens_to_ids(aspect_tokens)` — `a--1,-1` tidak ada di vocab

**Tidak ada metrik Step 2 untuk BERT**. Ini berarti kita tidak tahu:
- Apakah 81.23% Step 1 F1 cukup untuk menghasilkan quadruple yang baik?
- Berapa F1 end-to-end BERT baseline di rest16?
- Apakah error propagation dari Step 1 signifikan?

Bug ini sudah diperbaiki di generator V2 STAGED (mengganti parsing manual dengan panggilan `get_1st_pairs.py`), tapi BERT baseline tidak pernah dilatih ulang.

### 6.2 IndoBERT V4 — appsid (T4, 1/15 epoch, Dual-Head)

| Epoch | Loss | TP | FP | FN | Precision% | Recall% | Micro-F1% | Cat-F1% | Sent-Acc% |
|---|---|---|---|---|---|---|---|---|---|
| **1** | 0.5544 | 6.654 | 3.951 | 2.352 | 62.74 | 73.88 | **67.86** | 0.00 ⚠️ | 0.00 ⚠️ |

**Konteks kritis**: Ini hanya **1 epoch dari 15**. Dengan 65.423 training pairs dan batch_size 32, satu epoch = 2.045 langkah. Model baru melihat setiap contoh training sekali. Angka ini hampir pasti akan naik signifikan dengan lebih banyak epoch.

**Analisis per-difficulty-slot** (epoch 1):

| Slot | TP | FP | FN | Precision% | Recall% | F1% |
|---|---|---|---|---|---|---|
| 0 (easiest) | 2.782 | 239 | 349 | 92.09 | 88.85 | 90.44 |
| 1 | 2.336 | 182 | 248 | 92.77 | 90.40 | 91.57 |
| 2 | 3.655 | 160 | 250 | 95.81 | 93.60 | 94.69 |
| 3 | 0 | 0 | 0 | — | — | — |
| 4 (hardest) | 7.704 | 561 | 716 | 93.21 | 91.50 | 92.35 |

**Anomali**: Slot 4 ("paling sulit") justru memiliki F1 92.35%, lebih tinggi dari slot 0 ("paling mudah") yang 90.44%. Ini bertentangan dengan ekspektasi bahwa slot yang lebih sulit seharusnya memiliki F1 lebih rendah. Kemungkinan penyebab:
1. Definisi "difficulty" berdasarkan jumlah token dalam span, bukan kesulitan klasifikasi
2. Slot 4 memiliki jumlah sampel lebih banyak (8.981 vs 3.370 di slot 0) — dominasi kuantitas
3. Quadruple dengan span pendek (slot 0) mungkin melibatkan implicit aspect/opinion yang lebih sulit diklasifikasi

**Dual-head bug** — Category Micro-F1 = Sentiment Accuracy = 0.00%:
- Atribut `latest_cat_logits` dan `latest_senti_logits` adalah side-effect dari `model.forward()` di training loop
- Saat evaluasi membaca dari cache (file CSV), model tidak di-`forward()` ulang → atribut kosong
- Dampak: kita tidak tahu apakah bottleneck di kategori (multi-label BCE pada 13 kelas) atau di sentimen (multi-class CE pada 3 kelas)

**Prediksi untuk epoch berikutnya:**
- Dengan loss 0.55 di epoch 1, masih ada ruang signifikan untuk perbaikan
- Jika pola Step 1 berlaku (loss turun ~70% dari epoch 1 ke 2), F1 bisa naik ke 72-75% di epoch 2
- Plateau kemungkinan di epoch 6-8 dengan F1 75-80% — tapi ini spekulatif
- Early stopping (PATIENCE=5, MIN_EPOCHS_BEFORE_STOP=5) akan menghentikan training jika tidak ada improvement setelah epoch 10

---

## 7. Dekomposisi 15 Subtask & Agregasi

### 7.1 15 Subtask — Gradasi dari Termudah ke Tersulit

Data dari evaluasi final IndoBERT setelah 1 epoch Step 2:

| # | Sub-task | Elemen | TP | FP | FN | Prec% | Rec% | Micro-F1% |
|---|---|---|---|---|---|---|---|---|
| 7 | opinion | 1 | 16.896 | 516 | 786 | 97.04 | 95.55 | **96.29** |
| 3 | aspect | 1 | 18.019 | 853 | 1.498 | 95.48 | 92.32 | **93.88** |
| 0 | category | 1 | 16.477 | 1.142 | 1.563 | 93.52 | 91.34 | **92.41** |
| 4 | category aspect | 2 | 17.491 | 1.644 | 2.026 | 91.41 | 89.62 | **90.51** |
| 1 | sentiment | 1 | 13.137 | 2.248 | 2.398 | 85.39 | 84.56 | **84.97** |
| 8 | category opinion | 2 | 16.878 | 4.659 | 1.994 | 78.37 | 89.43 | **83.54** |
| 9 | sentiment opinion | 2 | 14.703 | 2.905 | 2.979 | 83.50 | 83.15 | **83.33** |
| 11 | aspect opinion | 2 | 17.604 | 6.164 | 1.924 | 74.07 | 90.15 | **81.32** |
| 5 | sentiment aspect | 2 | 15.402 | 3.769 | 4.126 | 80.34 | 78.87 | **79.60** |
| 2 | category sentiment | 2 | 14.142 | 3.755 | 3.947 | 79.02 | 78.18 | **78.60** |
| 12 | category aspect opinion | 3 | 17.079 | 6.987 | 2.449 | 70.97 | 87.46 | **78.35** |
| 6 | category sentiment aspect | 3 | 14.920 | 4.514 | 4.608 | 76.77 | 76.40 | **76.59** |
| 10 | category sentiment opinion | 3 | 14.425 | 7.149 | 4.447 | 66.86 | 76.44 | **71.33** |
| 13 | sentiment aspect opinion | 3 | 14.929 | 8.839 | 4.599 | 62.81 | 76.45 | **68.96** |
| 14 | **cat+sent+asp+opin** | **4** | **14.448** | **9.618** | **5.080** | **60.03** | **73.99** | **66.28** |

### 7.2 Agregasi per Jumlah Elemen

| # Elemen | N Subtask | Avg F1% | Min F1% | Max F1% | Total TP | Total FP | Total FN |
|---|---|---|---|---|---|---|---|
| 1 | 4 | **91.89** | 84.97 (sent) | 96.29 (opin) | 64.529 | 4.759 | 6.245 |
| 2 | 6 | **82.82** | 78.60 (cat+sent) | 90.51 (cat+asp) | 96.220 | 22.896 | 16.996 |
| 3 | 4 | **73.81** | 68.96 (sent+asp+opin) | 78.35 (cat+asp+opin) | 61.353 | 27.489 | 16.103 |
| 4 | 1 | **66.28** | 66.28 (full quad) | 66.28 | 14.448 | 9.618 | 5.080 |

### 7.3 Pola Error Propagation

Setiap tambahan elemen menurunkan F1 rata-rata ~8-9 poin:
- 1 elemen → 2 elemen: −9.07 poin
- 2 elemen → 3 elemen: −9.01 poin  
- 3 elemen → 4 elemen: −7.53 poin

Penurunan yang hampir linear ini menunjukkan bahwa error bersifat **compound**: kesalahan di satu elemen mengakibatkan seluruh tuple dihitung salah. Model tidak bisa "benar sebagian" — prediksi kategori benar tapi sentimen salah tetap dihitung sebagai false negative untuk sub-task `category+sentiment`.

**Precision vs Recall — asimetri**:
- Sub-task yang melibatkan opinion cenderung memiliki **recall tinggi, precision rendah**: opinion (R=95.55%, P=97.04%), aspect+opinion (R=90.15%, P=74.07%)
- Sub-task yang melibatkan sentiment cenderung memiliki **precision dan recall sama-sama rendah**: sentiment (R=84.56%, P=85.39%)
- Kategori cukup seimbang: category (R=91.34%, P=93.52%)

Ini mengindikasikan bahwa **sentimen adalah bottleneck utama** — F1 terendah di antara 4 elemen dasar (84.97%), jauh di bawah opinion (96.29%), aspect (93.88%), dan category (92.41%).

### 7.4 Di Mana Kategori dan Sentimen Gagal?

Karena dual-head metrics bug, kita tidak bisa memisahkan kontribusi kategori vs sentimen secara independen. Tapi dari data subtask, kita bisa menginferensi:

- **Kategori relatif kuat**: category saja mencapai 92.41% F1; category+aspect mencapai 90.51%
- **Sentimen relatif lemah**: sentiment saja hanya 84.97% F1; setiap kombinasi yang melibatkan sentimen turun signifikan
- **Kombinasi keduanya paling buruk**: category+sentiment hanya 78.60% — terendah di antara semua 2-elemen subtask

Ini konsisten dengan hipotesis bahwa noise weak labeling lebih berdampak pada sentimen daripada kategori. Kategori (mis. `TRANSACTION_TRANSFER`) sering bisa diinferensi dari konteks klausa, sementara sentimen ("apakah ini keluhan atau pujian?") lebih ambigu dengan weak labeling.

---

## 8. Empat Critical Insight Sintesis

### Insight 1: Perbandingan Langsung Tidak Valid

**Tidak ada dasar metodologis untuk membandingkan 97.94% (IndoBERT) vs 81.23% (BERT) dan menyimpulkan IndoBERT lebih baik.** Kedua angka berasal dari:
- Dataset berbeda (domain, bahasa, ukuran, granularitas, kualitas label)
- GPU berbeda (tidak memengaruhi F1, tapi menandakan lingkungan eksekusi berbeda)
- Tahap pipeline berbeda (Step 1 saja untuk BERT, Step 1 + 2 untuk IndoBERT)

Satu-satunya perbandingan yang valid secara metodologis adalah **menjalankan kedua backbone pada dataset yang sama**. Eksperimen cross-lingual (IndoBERT dilatih pada rest16 bahasa Inggris, atau BERT dilatih pada appsid bahasa Indonesia via terjemahan) adalah desain kontrol minimum yang diperlukan.

### Insight 2: Ukuran Dataset Mendominasi

Dengan 29× lebih banyak training quadruple, appsid memberikan keuntungan besar yang tidak ada hubungannya dengan pilihan model. Efek ukuran dataset dalam deep learning sudah terdokumentasi luas — model besar dengan data sedikit sering kalah dari model kecil dengan data banyak.

Jika kita menormalisasi untuk ukuran data (misalnya, sampling 2.500 quadruple dari appsid dan melatih IndoBERT), kemungkinan F1 akan turun drastis mendekati 80-85% — sebanding dengan BERT di rest16. Tapi eksperimen kontrol ini belum dilakukan.

### Insight 3: Cross-Lingual — Eksperimen yang Hilang

Eksperimen yang paling informatif justru belum dibangun: **IndoBERT pada rest16/laptop (teks bahasa Inggris)**. Desain ini akan mengisolasi efek backbone, karena dataset dan metrik evaluasi identik dengan BERT baseline.

Ekspektasi: IndoBERT akan underperform dibandingkan BERT pada teks Inggris, karena:
- Vocab IndoBERT dioptimalkan untuk bahasa Indonesia — banyak token Inggris akan menjadi `[UNK]`
- Pretraining IndoBERT pada korpus Indo4B (~23 GB teks Indonesia) — representasi subword untuk bahasa Inggris kurang optimal

Gap antara BERT dan IndoBERT pada dataset Inggris akan menjadi **batas atas** untuk efek backbone — dan kemungkinan jauh lebih kecil daripada gap yang disebabkan oleh perbedaan dataset.

### Insight 4: Tiga Bug Penghalang Sebelum Kesimpulan

Sebelum klaim apapun bisa dibuat, tiga masalah harus diselesaikan:

| # | Bug | Dampak | Prioritas |
|---|---|---|---|
| 1 | Prefix `bert.` (Gate 1) — encoder mungkin random | Semua metrik IndoBERT tidak berarti jika bug aktif | **Kritis** |
| 2 | Dual-head metrics = 0.00% | Tidak bisa mengevaluasi kategori vs sentimen secara independen | **Tinggi** |
| 3 | Step 2 baru 1 epoch | 67.86% F1 adalah lower bound, bukan performa final | **Tinggi** |

Gate 1 adalah yang paling mendesak karena jika bug aktif, seluruh hasil training IndoBERT (termasuk 97.94% Step 1) perlu diulang setelah perbaikan adapter.

---

## 9. Rekomendasi & Next Steps

### Prioritas 1: Verifikasi Gate 1 (Prefix `bert.`) — 🚨 KRITIS

Jalankan cell Gate 1 di Colab dengan torch. Verifikasi bahwa setelah adapter menambahkan prefix `bert.`:
- `missing_keys` = 0 (atau hanya head classifier yang memang tidak ada di checkpoint)
- `unexpected_keys` = 0
- Beberapa bobot encoder dibandingkan secara numerik antara checkpoint asli dan setelah adapter

Jika Gate 1 gagal: perbaiki adapter, bangun ulang notebook, dan **ulangi seluruh training**.

### Prioritas 2: Selesaikan Step 2 Training (15 Epoch)

Dengan AMP+BS32 yang sudah diimplementasikan, target:
- ~1.8 menit/epoch → 15 epoch ≈ 27 menit, atau ~14 menit dengan early stop (8 epoch)
- Gunakan `MAX_EPOCHS_THIS_RUN=1` dan resume per-epoch untuk melewati batas waktu Colab
- Simpan history lengkap per epoch (loss, quadruple F1, category F1, sentiment accuracy)

### Prioritas 3: Perbaiki Dual-Head Metrics Bug

Root cause: `latest_cat_logits` dan `latest_senti_logits` hanya diisi selama `forward()` di training loop, tidak tersedia saat membaca dari cache.

Fix sederhana: alih-alih mengandalkan side-effect atribut, simpan logits ke file CSV/JSON selama training loop (seperti yang sudah dilakukan untuk metrik quadruple).

### Prioritas 4: Bangun & Jalankan Cross-Lingual Control

Notebook `ACOS-IndoBERT-Rest16/` yang direncanakan di laporan 024:
- IndoBERT pada dataset rest16 dan laptop (Inggris)
- Gunakan generator pattern yang sama dengan V4
- Ekspektasi: F1 lebih rendah dari BERT baseline, tapi gap-nya mengukur efek backbone murni

### Prioritas 5 (Jangka Panjang): Efisiensi Training

- Freeze encoder (train head saja) untuk iterasi cepat
- LoRA sebagai alternatif freeze — memungkinkan adaptasi dengan 1-2% parameter trainable
- Mixed precision (AMP) sudah diimplementasikan di Step 2; extend ke Step 1
- Pertimbangkan `gradient_checkpointing` untuk dataset besar

---

## A. Appendix — Daftar File yang Menjadi Sumber Analisis

| File | Kontribusi |
|---|---|
| `ACOS-IndoBERT/notebooks/V4_1_01_setup.ipynb` | Statistik dataset, konfigurasi, Gate 2-5, backbone adapter |
| `ACOS-IndoBERT/notebooks/V4_1_02_step1_train.ipynb` | Step 1 training history (8 epoch) |
| `ACOS-IndoBERT/notebooks/V4_1_03_step2_train.ipynb` | Step 2 training (1 epoch), distribusi pasangan kandidat |
| `ACOS-IndoBERT/notebooks/V4_1_04_eval_inference.ipynb` | Final quadruple metrics, 15 subtask breakdown, agregasi |
| `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` | Konfigurasi generator, konfirmasi struktur |
| `ACOS-IndoBERT/build/_eda_id/csv/eda_dataset_statistics.csv` | Statistik split dataset |
| `reports/004_analisis_kritis_struktur_proyek_acos_27082026_1507.md` | BERT baseline 81.23% + crash Step 2 |
| `reports/023_pipeline_acos_indobert_dataset_indonesia_04092026.md` | Desain pipeline IndoBERT, keputusan dataset |
| `reports/025_devlog_beban_pelatihan_indobert_t4_finetuned_vs_base_05092026.md` | Analisis beban training BERT vs IndoBERT |
| `reports/027_analisis_arsitektur_pipeline_acos_dualhead_step2_09092026.md` | Analisis arsitektur dual-head |
| `reports/028_implementasi_dualhead_step2_dan_training_loop_09092026.md` | Implementasi dual-head |
| `reports/029_rencana_percepatan_training_step2_10092026.md` | Rencana AMP + BS32 |

---

> **Catatan akhir**: Analisis ini tidak menyimpulkan bahwa satu model lebih baik dari yang lain. Ia menyimpulkan bahwa pertanyaan "BERT vs IndoBERT: mana yang lebih baik?" belum bisa dijawab dengan data yang ada — dan menjelaskan dengan tepat apa yang diperlukan untuk bisa menjawabnya.