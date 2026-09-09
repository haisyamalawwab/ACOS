# Dev Plan: Analisis Arsitektur Pipeline ACOS — 2 Step vs 4 Sub-Task

**File:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb`  
**Tanggal:** 2026-09-09  
**Status:** Analisis — belum diimplementasikan  

---

## 1. Latar Belakang & Masalah

Notebook memiliki **80 sel total**, namun hanya terdapat **2 model training step**:

- **Step 1** (Sel 5a–5f): BERT-CRF → Aspect + Opinion Extraction  
- **Step 2** (Sel 8a–8f): `CategorySentiClassification` → Category + Sentiment

Padahal ACOS (Aspect-Category-Opinion-Sentiment) secara standar memiliki **4 komponen** yang seharusnya dapat dievaluasi secara independen:

| Kode | Sub-Task | Status di Notebook |
|---|---|---|
| **A** | Aspect span extraction | ✅ Step 1 (BERT-CRF) |
| **C** | Category classification | ⚠️ Digabung di Step 2 |
| **O** | Opinion span extraction | ✅ Step 1 (BERT-CRF, bersama A) |
| **S** | Sentiment classification | ⚠️ Digabung di Step 2 |

---

## 2. Root Cause: Label Gabungan di Step 2

### 2a. Bukti dari Cell 59 (8a — Inisialisasi Step 2)

```python
processor_step2 = processors["categorysenti"]()
label_list_step2 = processor_step2.get_labels(DOMAIN)
num_labels_step2 = len(label_list_step2[0])
```

`processors["categorysenti"]` menghasilkan label **gabungan** bertipe `{category}-{sentiment}`,
misalnya `food-positive`, `service-negative`, `ambience-neutral`.  
Ini berarti **1 model** memprediksi Category dan Sentiment **sekaligus** — bukan 2 head terpisah.

### 2b. Bukti dari Cell 55 (7a — Bridge Pasangan Kandidat)

```python
for pa in asp:
    for po in opi:
        wf.write(f"{text}####{pa} {po}\n")
```

Input Step 2 = `(teks, aspect_span, opinion_span)`. Step 2 langsung melompat ke prediksi
`category+sentiment` tanpa ada intermediate step untuk:
- Mapping **Aspect → Category** (A→C)
- Mapping **Opinion → Sentiment** (O→S)
- Cross-validasi **Category ↔ Opinion** (C↔O)

### 2c. Arsitektur Pipeline Saat Ini

```
Input Text
    │
    ▼
┌──────────────────────────────────────┐
│  STEP 1: BERT-CRF  (Sel 5a–5f)      │
│  Output: aspect spans + opinion spans│
│  → pred4pipeline.txt                 │
└───────────────────┬──────────────────┘
                    │  Bridge 7a: Cartesian (aspect, opinion) pairs
                    ▼
┌──────────────────────────────────────┐
│  STEP 2: CategorySentiClassification │
│  (Sel 8a–8f)                         │
│  Input:  (text, aspect_span,         │
│           opinion_span)              │
│  Output: label gabungan              │
│          "{category}-{sentiment}"    │
└───────────────────┬──────────────────┘
                    │
                    ▼
             ACOS Quadruple
     (aspect, category, opinion, sentiment)
```

---

## 3. Dampak pada Evaluasi

### 3a. Sub-Task yang Tidak Bisa Diukur Secara Mandiri

Karena Category dan Sentiment digabung dalam 1 label, tidak ada cara untuk mengukur:

- **A+C** (Aspect-Category pair) F1 secara terpisah
- **C+S** (Category-Sentiment pair) F1 secara terpisah
- **A+O+C** triplet F1
- **A+O+S** triplet F1

Padahal Cell 9a dan 9b mengklaim mengukur **15 sub-task** — ini adalah
**kombinasi post-hoc dari output** yang sudah digabung, bukan evaluasi model terpisah
per komponen.

### 3b. Error Propagation Tidak Terdeteksi

Dengan arsitektur 2-step:
- Jika Category salah → Sentiment otomatis ikut salah (label gabungan rusak)
- Tidak ada cara membedakan: apakah error berasal dari prediksi Category atau Sentiment?
- Bottleneck pipeline sulit di-diagnosa

---

## 4. Perbandingan dengan Paper ACOS Asli

| Komponen | Pipeline Paper | Pipeline Notebook Ini |
|---|---|---|
| A + O joint extraction | Step 1 (BERT-CRF) | ✅ Step 1 (sama) |
| A → C mapping | Step terpisah | ❌ Tidak ada |
| O → S mapping | Step terpisah | ❌ Tidak ada |
| (A,C,O,S) evaluation | Per sub-task | ⚠️ Hanya post-hoc combo |

---

## 5. Opsi Solusi

### Opsi A: Tambah Step 3 + Step 4 (Refactor Besar)

Pipeline 4-step penuh:

```
STEP 1: BERT-CRF
  Input:  teks ulasan
  Output: aspect spans + opinion spans

STEP 2: Aspect-Category Classifier  [BARU]
  Input:  teks + aspect_span
  Output: category

STEP 3: Opinion-Sentiment Classifier  [BARU]
  Input:  teks + opinion_span + category
  Output: sentiment

STEP 4: Evaluasi per Sub-Task
  - A only          (P/R/F1)
  - A+C             (P/R/F1)
  - A+O             (P/R/F1)
  - C+S             (P/R/F1)
  - A+O+C           (P/R/F1)
  - Full ACOS quad  (P/R/F1)
```

**Effort:** Tinggi — perlu model baru, dataset preprocessing baru, evaluasi ulang.

---

### Opsi B: Dual-Head pada Step 2 (Refactor Minimal) ✅ Direkomendasikan

Pisahkan output head di `CategorySentiClassification` menjadi 2 head terpisah:

```python
class CategorySentiClassification(BertPreTrainedModel):
    def __init__(self, config, num_categories, num_sentiments):
        super().__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        # Dua head terpisah — bukan 1 joint label
        self.category_head = nn.Linear(config.hidden_size, num_categories)
        self.sentiment_head = nn.Linear(config.hidden_size, num_sentiments)

    def forward(self, input_ids, attention_mask, token_type_ids,
                category_labels=None, sentiment_labels=None):
        pooled = self.bert(input_ids, attention_mask, token_type_ids)[1]
        pooled = self.dropout(pooled)
        cat_logits = self.category_head(pooled)    # → num_categories
        senti_logits = self.sentiment_head(pooled)  # → num_sentiments
        ...
```

**Keuntungan:**
- Evaluasi **Category F1** dan **Sentiment F1** bisa terpisah
- Arsitektur tetap 2-step (tidak perlu dataset preprocessing ulang)
- Lebih mudah diagnosa error per komponen

**Effort:** Menengah — modifikasi `modeling.py`, `dataset_utils.py`, `eval_metrics.py`.

---

### Opsi C: Tidak Mengubah Arsitektur (Dokumentasi Saja)

Dokumentasikan limitasi ini secara eksplisit di notebook:
- Clarifikasi bahwa "15 sub-task" adalah *kombinasi post-hoc*, bukan *independent classifier*
- Tambahkan catatan pada Cell 9b bahwa A→C dan O→S tidak dievaluasi secara mandiri

**Effort:** Rendah — hanya perubahan markdown/komentar di notebook.

---

## 6. Rekomendasi

Untuk keperluan **penelitian** dan **publikasi**, gunakan **Opsi B (Dual-Head)**.  
Ini memenuhi standar evaluasi ACOS sub-task tanpa perlu refactor pipeline secara menyeluruh.

Jika waktu terbatas, gunakan **Opsi C** sebagai interim sambil menyiapkan Opsi B.

---

## 7. File Terkait

| File | Relevansi |
|---|---|
| `notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb` | File utama yang dianalisis |
| `acos_id/taxonomy.py` | Definisi label category & sentiment |
| `_build_v4_indobert.py` → `modeling.py` | Implementasi `CategorySentiClassification` |
| `_build_v4_indobert.py` → `run_classifier_dataset_utils.py` | `processors["categorysenti"]` |
| `_build_v4_indobert.py` → `eval_metrics.py` | `pair_eval`, `SubtaskMetricCapture` |
