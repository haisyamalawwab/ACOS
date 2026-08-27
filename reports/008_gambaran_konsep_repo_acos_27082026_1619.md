# Gambaran Konsep Repositori ACOS-ASLI

Tanggal: 2026-08-27
Sifat: dokumen konseptual — ringkasan arsitektur, alur data, dan hubungan antar komponen. Disusun dari pembacaan statis; pipeline belum dieksekusi.

---

## 1. Apa yang Dikerjakan Repo Ini (Satu Kalimat)

Repo ini mengimplementasikan **ekstraksi quadruple ABSA** — dari sebuah kalimat ulasan produk, mesin mengekstrak semua *quadruple* `(aspect expression, aspect category, opinion expression, sentiment polarity)` termasuk entitas **implicit** (aspek/opini yang tidak tertulis eksplisit).

Contoh:
```
"The sushi was fresh and delicious, but the service was slow."
→ (sushi, FOOD#QUALITY, fresh/delicious, positive)
→ (service, SERVICE#GENERAL, slow, negative)
```

---

## 2. Konsep Inti: Tugas "Quadruple" dan Masalah Implicit

```
             QUADRUPLE = (aspect, category, opinion, sentiment)

  "Sushi is fresh"   →  aspect="sushi"   opinion="fresh"
                        category=FOOD#QUALITY
                        sentiment=positive

  "It's overpriced"  →  aspect=NULL (implicit)   opinion="overpriced"
                        category=FOOD#PRICES     sentiment=negative
                            ↑
                     aspek tidak tertulis → harus ditebak model
```

**Dua jenis implicit** yang jadi kontribusi utama paper:
- **Implicit aspect** — opini ada tapi targetnya tidak disebut ("It's overpriced" → aspek = food).
- **Implicit opinion** — aspek disebut tapi opininya tersirat ("The fish was..." tanpa kata opini).

---

## 3. Pendekatan: "Extract-Classify" Dua Tahap

Paper membandingkan 4 baseline; repo ini hanya berisi **satu**: **Extract-Classify-ACOS**. Ide dasarnya memecah tugas sulit menjadi dua tugas lebih mudah yang berurutan:

```
                    ┌─────────────────────────────────────────────┐
                    │        "Extract-Classify" (2 tahap)         │
                    └─────────────────────────────────────────────┘

  Kalimat ──► [STEP 1: EXTRACT] ──► [BRIDGE] ──► [STEP 2: CLASSIFY] ──► Quadruples
              temukan SPAN            pasangkan        beri LABEL
              aspect & opinion       aspect×opinion    category+sentiment

  "Sushi is fresh"  →  span: "sushi", "fresh"  →  (sushi,fresh)  →  FOOD#QUALITY/positive
```

**Kenapa dua tahap, bukan satu model?**
- Step 1 (co-extraction) hanya soal **menemukan rentang kata** (sequence tagging + deteksi implicit) — tidak perlu tahu kategori.
- Step 2 (classification) hanya soal **memberi label** pada pasangan yang sudah ada — tidak perlu menemukan span.
- Masing-masing lebih mudah dilatih dan di-debug; trade-off: error Step 1 **propagasi** ke Step 2 (desain pipeline, bukan joint).

---

## 4. Arsitektur Model per Tahap

### Step 1 — `BertForQuadABSA` (BERT + CRF)

```
                  Kalimat (token WordPiece)
                          │
                    ┌─────▼─────┐
                    │  BERT     │  encoder (12 layer, 768 hidden)
                    └─┬───────┬─┘
             sequence │       │ pooled [CLS]
             output   │       │
        ┌─────────────▼──┐    ├──────────────┬───────────────┐
        │ Linear(768→6)  │    │ imp_aspect   │ imp_opinion   │
        │ + CRF decoder  │    │ clf(768→2)   │ clf(768→2)    │
        └─────────────┬──┘    │ [CLS] token  │ [SEP] terakhir│
                      │       └──────┬───────┴───────┬───────┘
            Tag sekuens:             │   "apakah     │  "apakah
            B-A/I-A/B-O/I-O          │   ada aspek   │   ada opini
            (span explicit)          │   implicit?"  │   implicit?"
                                     ▼               ▼
                    ┌────────────────────────────────────────────┐
                    │  Loss total = CRF_loss + CE(aspect) + CE(opinion) │
                    └────────────────────────────────────────────┘
```

**6 tag sekuens**: `[CLS] O I-A B-A I-O B-O` — B/I = begin/inside, A = aspect, O = opinion.

### Step 2 — `CategorySentiClassification` (BERT + mean-pool)

```
  Pasangan kandidat (aspect span, opinion span)
                          │
                    ┌─────▼─────┐
                    │  BERT     │
                    └─┬─────────┘
              pooled_outputs [B, L, 768]
                        │
        ┌───────────────┴───────────────┐
        │ mean-pool span aspect         │ mean-pool span opinion
        │ (mask candidate_aspect)       │ (mask candidate_opinion)
        ▼                               ▼
     aspect_rep [768]              opinion_rep [768]
        └───────────────┬───────────────┘
                        ▼
              concat [1536]
                        ▼
          Linear(1536 → num_labels)
          = 39 (rest16) / 363 (laptop)
                        ▼
        BCEWithLogitsLoss (multi-label)
        label = "CATEGORY#SENTIMENT"  (mis. FOOD#QUALITY#positive)
```

---

## 5. Alur Data End-to-End

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          ALUR DATA PIPELINE                               │
└──────────────────────────────────────────────────────────────────────────┘

 data/                         Extract-Classify-ACOS/tokenized_data/
 ────────                      ──────────────────────────────────────
 (distribusi,                   rest16_quad_{train,dev,test}.tsv
  TIDAK dipakai kode)           laptop_quad_{train,dev,test}.tsv
        │                          (sudah ter-WordPiece)
        │                          │
        │                          ▼
        │              ┌─────────────────────────────┐
        │              │  STEP 1 (run_step1.py)      │
        │              │  BertForQuadABSA            │
        │              └──────────────┬──────────────┘
        │                             │
        │                   pred4pipeline.txt
        │                   ("text \t a-span \t o-span")
        │                             │
        │                             ▼
        │              ┌─────────────────────────────┐
        │              │  BRIDGE (get_1st_pairs.py)  │
        │              │  cross-product aspect×opinion│
        │              └──────────────┬──────────────┘
        │                             │
        │                   {domain}_test_pair_1st.tsv
        │                   ("text####aspan ospan")
        │                             │
        │                             ▼
        │              ┌─────────────────────────────┐
        │              │  STEP 2 (run_step2.py)      │
        │              │  CategorySentiClassification│
        │              └──────────────┬──────────────┘
        │                             │
        │                             ▼
        │                    Quadruples akhir
        │                    (aspect, category, opinion, sentiment)
        │                    + 15 subtask + 4 subset implicit
        │
        └──► (EDA saja, untuk visualisasi distribusi dataset)
```

---

## 6. Peta Komponen Kode

```
ACOS-ASLI/
│
├── data/                          # dataset mentah (publikasi/EDA)
├── Extract-Classify-ACOS/         # ★ inti implementasi
│   ├── modeling.py                #   arsitektur BERT + 2 head task
│   ├── run_classifier_dataset_utils.py  # processor + konversi fitur
│   ├── eval_metrics.py            #   metrik P/R/F1 + 15 subtask + 4 subset
│   ├── dataset_utils.py           #   pembaca gold pair step 2
│   ├── run_step1.py               #   CLI training step 1
│   ├── run_step2.py               #   CLI training step 2
│   ├── tokenized_data/            #   data siap-pakai + jembatan get_1st_pairs.py
│   ├── manager.py                 #   pemilih GPU
│   ├── file_utils.py              #   (duplikat) cache/download
│   └── bert_utils/                #   tokenization + optimization + file_utils
│
├── notebooks/                     # ★ antarmuka pengguna (Colab/local)
│   ├── 00 master (all-in-one)
│   ├── 01 setup & EDA
│   ├── 02 step 1
│   ├── 03 jembatan
│   ├── 04 step 2
│   └── 05 evaluasi & inferensi
│
├── colab_utils.py                 # helper bersama notebook (EDA, plot, wrapper)
├── docs/                          # rencana implementasi (riwayat)
├── reports/                       # laporan analisis (001–007)
├── backups/                       # backup fisik sebelum edit
└── img/                           # gambar README
```

**Dua jalur penggunaan:**
1. **CLI** (`run.sh`) — untuk reproduksi/benchmark di server GPU (path absolut perlu diedit).
2. **Notebook** (`00`–`05`) — untuk Colab/local, lebih interaktif + visualisasi + inferensi.

Keduanya memakai **inti yang sama** (`modeling.py`, `run_classifier_dataset_utils.py`, `eval_metrics.py`).

---

## 7. Hubungan Ketergantungan Antar Modul

```
        run_step1.py ──────► modeling.BertForQuadABSA
              │                    │
              ├──► run_classifier_dataset_utils (QuadProcessor, features)
              ├──► eval_metrics (pred_eval)
              └──► bert_utils.tokenization / optimization

        run_step2.py ──────► modeling.CategorySentiClassification
              │                    │
              ├──► run_classifier_dataset_utils (CategorySentiProcessor, features2nd)
              ├──► dataset_utils (read_pair_gold)
              ├──► eval_metrics (pair_eval)
              └──► bert_utils.tokenization / optimization

        get_1st_pairs.py ─► (standalone, baca pred4pipeline.txt)

        notebooks/00–05 ──► colab_utils.py ──► inti di atas (via wrapper)
```

---

## 8. Format Data (Kontrak antar Tahap)

| Jenis | Format | Contoh |
|-------|--------|--------|
| Quad (input step 1) | `text \t start,end CATEGORY#ASPECT sentiment start,end` | `... \t 0,5 FOOD#QUALITY 2 10,15` |
| Pair (input step 2) | `text####aspan ospan \t CATEGORY#SENTIMENT` | `...####0,5 10,15 \t FOOD#QUALITY#2` |
| Span implicit | `-1,-1` | `-1,-1` (aspect/opini tak tertulis) |
| Sentiment | `0/1/2` | negative/neutral/positive |
| Offset span | indeks token WordPiece (bukan kata asli) | `0,5` = token ke-0..4 |

---

## 9. Evaluasi: 15 Subtask + 4 Subset

### 9.1 Empat subset implicit/explicit

```
  Kalimat dibagi berdasarkan kombinasi implisit:

  Subset 0 : explicit aspect + explicit opinion   (paling mudah)
  Subset 1 : implicit aspect + explicit opinion
  Subset 2 : explicit aspect + implicit opinion
  Subset 3 : implicit aspect + implicit opinion   (paling sulit)
  Subset 4 : overall (semua)
```

### 9.2 Lima belas subtask

Evaluasi bukan hanya quadruple penuh, tapi **semua kombinasi elemen** `{category, sentiment, aspect, opinion}` (2⁴−1 = 15 kombinasi). Ini mengukur kontribusi parsial tiap elemen.

```
  Kombinasi 1 elemen : category | sentiment | aspect | opinion       (4)
  Kombinasi 2 elemen : category+sentiment, category+aspect, ...      (6)
  Kombinasi 3 elemen : category+sentiment+aspect, ...                (4)
  Kombinasi 4 elemen : quadruple penuh                                (1)
                                                          Total = 15
```

---

## 10. Intuisi Kenapa Desain Ini Masuk Akal

1. **CRF untuk span** — tag sekuens punya struktur dependensi lokal (B harus diikuti I); CRF memodelkan transisi antar tag, lebih baik dari softmax independen per token.
2. **Implicit dari `[CLS]`/`[SEP]`** — keputusan "apakah ada aspek/opini yang tersirat" adalah klasifikasi level kalimat, sehingga diambil dari representasi agregat (pooled/akhir).
3. **Mean-pool span** — representasi aspek/opini dirangkum dari rata-rata hidden state token dalam span; sederhana tapi efektif.
4. **Multi-label category-sentiment** — satu pasangan bisa punya beberapa kategori+sentimen; `BCEWithLogitsLoss` menangani ini (bukan softmax single-label).
5. **Pipeline (bukan joint)** — memungkinkan melatih dan mengevaluasi tiap tahap terpisah; harga yang dibayar: error kaskade.

---

## 11. Batasan & Karakteristik Repo (Jujur)

- **Research code**, bukan library produksi: path absolut, `pdb.set_trace()`, dead code, duplikasi file.
- **Port legacy BERT** (`pytorch_pretrained_bert`), bukan `transformers` modern — butuh `torchcrf`, Python 3.7/PyTorch 1.8 asli.
- **Belum pernah dieksekusi** di environment bersih (Python 3.14 tanpa `torch`); notebook disiapkan "jalur", bukan "hasil".
- **Error Step 1 propagasi** ke Step 2 secara by-design.
- Tiga baseline lain (Double-Propagation, JET, TAS-BERT) **tidak disertakan** meski disebut di README.
