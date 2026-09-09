# 027 — Analisis Arsitektur Pipeline ACOS: 2-Step vs 4 Sub-Task & Rencana Dual-Head Step 2

**Tanggal:** 2026-09-09  
**File yang Dianalisis:**
- `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb`
- `ACOS-IndoBERT/acos_id/taxonomy.py`
- `ACOS-IndoBERT/notebooks/_build_v4_indobert.py`

**DEV_PLAN Terkait:**
- `ACOS-IndoBERT/notebooks/DEV_PLAN_acos_pipeline_4step_analysis.md`
- `ACOS-IndoBERT/notebooks/DEV_PLAN_dualhead_step2.md`

---

## 1. Pertanyaan Awal

> "Mengapa notebook ACOS hanya ada 2 step (BERT-CRF dan Category-Sentiment)?  
> Padahal untuk ACOS dibutuhkan: Aspect Category? Category Opinion? Opinion Sentiment?"

---

## 2. Temuan: Arsitektur Pipeline Saat Ini

Notebook memiliki **80 sel**, namun hanya ada **2 model training step**:

| Step | Sel | Model | Output |
|---|---|---|---|
| **Step 1** | 5a–5f | `BertForQuadABSA` (BERT-CRF) | Aspect spans + Opinion spans → `pred4pipeline.txt` |
| **Bridge** | 7a–7b | — | Cartesian pairs `(aspect_span, opinion_span)` |
| **Step 2** | 8a–8f | `CategorySentiClassification` | Label gabungan `{CATEGORY}#{SENTIMENT}` |

Pipeline ini adalah **desain yang disengaja** — bukan bug. Namun ada **masalah serius** pada granularitas evaluasi ACOS.

---

## 3. Root Cause: Label Gabungan di Step 2

### 3.1 Bukti Cell 59 (8a)

```python
processor_step2 = processors["categorysenti"]()
label_list_step2 = processor_step2.get_labels(DOMAIN)
num_labels_step2 = len(label_list_step2[0])
# → 39 label: 13 kategori × 3 sentimen → "AUTH_ACCESS#0", "APP_PERFORMANCE#2", dst.
```

### 3.2 Bukti taxonomy.py

```python
def catsenti_labels() -> list:
    return [f"{cat}#{senti}" for cat in CATEGORIES for senti in SENTIMENTS]
# → ["ONBOARDING_KYC#0", "ONBOARDING_KYC#1", "ONBOARDING_KYC#2",
#    "AUTH_ACCESS#0", ..., "ACCOUNT_MANAGEMENT#2"]  # 39 item
```

### 3.3 Implikasi

**1 model** memprediksi Category dan Sentiment **sekaligus** — bukan 2 head terpisah.
Tidak ada intermediate step untuk:
- Mapping **Aspect → Category** (A→C)
- Mapping **Opinion → Sentiment** (O→S)
- Cross-validasi **Category ↔ Opinion** (C↔O)

---

## 4. Pemetaan Sub-Task ACOS

| Kode | Sub-Task | Seharusnya | Di Notebook | Dapat Diukur Mandiri? |
|---|---|---|---|---|
| **A** | Aspect span extraction | Step terpisah | ✅ Step 1 (BERT-CRF) | ✅ Ya |
| **C** | Category classification | Step terpisah | ⚠️ Digabung di Step 2 | ❌ Tidak |
| **O** | Opinion span extraction | Step terpisah | ✅ Step 1 (BERT-CRF, bersama A) | ✅ Ya |
| **S** | Sentiment classification | Step terpisah | ⚠️ Digabung di Step 2 | ❌ Tidak |

---

## 5. Dampak pada Evaluasi

### 5.1 Sub-Task yang Tidak Bisa Diukur

Karena C dan S digabung dalam 1 label, sub-task berikut **tidak bisa dievaluasi secara mandiri**:

- **A+C** (Aspect-Category pair) F1
- **C+S** (Category-Sentiment pair) F1
- **A+O+C** triplet F1
- **A+O+S** triplet F1

### 5.2 "15 Sub-Task" di Cell 9b Adalah Post-Hoc

Cell 9a/9b mengklaim mengukur 15 sub-task via `SubtaskMetricCapture`, namun ini
adalah **kombinasi post-hoc dari output gabungan** — bukan evaluasi dari model
terpisah per komponen ACOS.

### 5.3 Error Propagation Tidak Terdeteksi

Jika Category salah → Sentiment otomatis ikut salah (label gabungan rusak).
Tidak ada cara membedakan sumber error per komponen.

---

## 6. Perbandingan dengan Paper ACOS Asli

| Komponen | Pipeline Paper (Zhang et al., 2021) | Pipeline Notebook V4 |
|---|---|---|
| A + O joint extraction | Step 1 (BERT-CRF) | ✅ Step 1 (sama) |
| A → C mapping | Step/head terpisah | ❌ Tidak ada |
| O → S mapping | Step/head terpisah | ❌ Digabung C dalam 1 step |
| Evaluasi per sub-task | Terpisah per komponen | ⚠️ Hanya post-hoc combo |

---

## 7. Solusi yang Dipilih: Dual-Head Step 2 (Opsi B)

**Keputusan:** Patch in-place pada `_build_v4_indobert.py` — tidak membuat V5.

Arsitektur target:

```
                 ┌─────────────────────┐
    (text,       │    BertModel         │
     asp_span, ──►  [CLS] pooled output│
     opi_span)   └──────────┬──────────┘
                            │ dropout
                 ┌──────────┴──────────┐
                 │                     │
          ┌──────▼──────┐       ┌──────▼──────┐
          │ category_    │       │ sentiment_   │
          │ head         │       │ head         │
          │ Linear(H,13) │       │ Linear(H,3)  │
          └──────┬───────┘       └──────┬───────┘
                 │                      │
          13 category logits     3 sentiment logits
          (multi-label BCE)      (multi-class CE)
```

### 7.1 Mengapa Dual-Head Lebih Baik dari Menambah Step Baru

| Aspek | Dual-Head (Opsi B) | Step Terpisah (Opsi A) |
|---|---|---|
| Effort | Menengah | Tinggi |
| Dataset preprocessing | Tidak berubah | Perlu preprocessing ulang |
| Backward compat domain Inggris | ✅ Via `USE_DUAL_HEAD` flag | ❌ Pipeline baru seluruhnya |
| Evaluasi mandiri per komponen | ✅ Ya | ✅ Ya |
| Arsitektur notebook | Tetap 2-step | Jadi 4-step |

---

## 8. File yang Akan Dimodifikasi

| File | Perubahan |
|---|---|
| `acos_id/taxonomy.py` | Tambah `label_list_category()`, `label_list_sentiment()`, `num_labels_category()`, `num_labels_sentiment()` |
| `notebooks/_build_v4_indobert.py` | Tambah `CODE_DUAL_HEAD_MODEL`, patch sel 8a (label init), 8d (model init), 8e (forward dual), 9a (eval per head) |
| `notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` | Di-regenerate dari build script setelah patch |

**File yang TIDAK diubah:** `modeling.py`, `dataset_utils.py`, `eval_metrics.py` (upstream)

---

## 9. Checklist Implementasi

- [ ] 1. Update `taxonomy.py` — tambah 4 fungsi label terpisah
- [ ] 2. Tambah `CODE_DUAL_HEAD_MODEL` ke `_build_v4_indobert.py`
- [ ] 3. Patch sel 8a — deteksi `USE_DUAL_HEAD` + inisialisasi label terpisah
- [ ] 4. Patch sel 8d — conditional model: DualHead vs SingleHead
- [ ] 5. Patch sel 8e — forward pass dual-head (`category_labels` + `sentiment_labels`)
- [ ] 6. Patch sel 9a — evaluasi per head + simpan `category_f1` & `sentiment_f1`
- [ ] 7. Jalankan `_build_v4_indobert.py` → regenerate `.ipynb`
- [ ] 8. Verifikasi: `DOMAIN=appsid` → DualHead | `DOMAIN=rest16` → SingleHead

---

## 10. Referensi

| File | Keterangan |
|---|---|
| `ACOS-IndoBERT/notebooks/DEV_PLAN_acos_pipeline_4step_analysis.md` | Root cause analysis lengkap |
| `ACOS-IndoBERT/notebooks/DEV_PLAN_dualhead_step2.md` | Rencana implementasi teknis detail |
| `reports/026_devlog_resume_training_dan_early_stopping_indobert_08092026.md` | Pola devlog sebelumnya |
