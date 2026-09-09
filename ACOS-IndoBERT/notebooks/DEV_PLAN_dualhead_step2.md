# Dev Plan: Dual-Head Step 2 — Pisah Category & Sentiment Classifier

**File Target:** `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` (patch in-place)  
**Tanggal:** 2026-09-09  
**Status:** Rencana — belum diimplementasikan  
**Merujuk ke:** `DEV_PLAN_acos_pipeline_4step_analysis.md` → Opsi B

---

## 1. Latar Belakang

Step 2 saat ini menggunakan **label gabungan** `{CATEGORY}#{SENTIMENT}` (contoh: `AUTH_ACCESS#0`,
`APP_PERFORMANCE#2`) — 39 label dari 13 kategori × 3 sentimen. Satu model head memprediksi
keduanya sekaligus sehingga:

- Category F1 dan Sentiment F1 tidak dapat diukur secara terpisah
- Error pada Category langsung mempengaruhi Sentiment (tidak bisa dibedakan)
- Sub-task `A+C`, `O+S` tidak dapat dievaluasi secara mandiri

Solusi: **Dual-Head** — satu `BertModel` encoder bersama, dua linear head terpisah.

---

## 2. Arsitektur Target (Dual-Head)

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

**Key decisions:**
- **Category**: multi-label BCE (satu ulasan bisa punya beberapa kategori)
- **Sentiment**: multi-class softmax CE (per kategori hanya 1 sentimen)
- Encoder tetap `indobert-base-p1` yang sama — tidak perlu retrain backbone dari nol

---

## 3. File yang Dimodifikasi

### 3a. `acos_id/taxonomy.py` — Tambah Fungsi Label Terpisah

Tambah di bawah `label_list_step2()`:

```python
def label_list_category() -> list:
    """13 label kategori untuk head Category."""
    return list(CATEGORIES)

def label_list_sentiment() -> list:
    """3 label sentimen: ['0', '1', '2'] (neg, neu, pos)."""
    return list(SENTIMENTS)

def num_labels_category() -> int:
    return len(CATEGORIES)   # 13

def num_labels_sentiment() -> int:
    return len(SENTIMENTS)   # 3
```

Patch `patch_processor_labels()` tambah fungsi baru untuk dual-head:

```python
def patch_processor_labels_dualhead(processors: dict) -> dict:
    """Patch tambahan: sediakan get_labels_dualhead() pada CategorySentiProcessor."""
    cs_cls = processors["categorysenti"]
    cs_cls.get_labels_category = lambda self, domain_type: (
        label_list_category() if is_id_domain(domain_type) else None
    )
    cs_cls.get_labels_sentiment = lambda self, domain_type: (
        label_list_sentiment() if is_id_domain(domain_type) else None
    )
    return {"patched_dualhead": True}
```

---

### 3b. `_build_v4_indobert.py` — Patch Sel 8a (Inisialisasi Step 2)

**Lokasi anchor (baris ~455):**
```python
"num_labels_step2": acos_taxonomy.num_labels_step2()
```

Tambah variabel baru di setelah baris 8a yang set `num_labels_step2`:

```python
# Dual-Head: label category dan sentiment terpisah
if _IS_ID_DOMAIN:
    label_list_cat   = processor_step2.get_labels_category(DOMAIN)
    label_list_senti = processor_step2.get_labels_sentiment(DOMAIN)
    num_labels_cat   = len(label_list_cat)   # 13
    num_labels_senti = len(label_list_senti)  # 3
    USE_DUAL_HEAD    = True
    st.step(f"Dual-Head aktif: {num_labels_cat} kategori | {num_labels_senti} sentimen")
else:
    USE_DUAL_HEAD    = False
    st.step(f"Single-Head (domain Inggris): {num_labels_step2} label gabungan")
```

---

### 3c. `_build_v4_indobert.py` — Patch Sel 8d (Model Step 2)

**Lokasi anchor:** `CategorySentiClassification` instantiation di RESUME_SPECS / sel 8d

Ganti:
```python
model_step2 = CategorySentiClassification.from_pretrained(
    bert_cache_dir, num_labels=num_labels_step2).to(device)
```

Menjadi:
```python
if USE_DUAL_HEAD:
    model_step2 = CategorySentiDualHead.from_pretrained(
        bert_cache_dir,
        num_categories=num_labels_cat,
        num_sentiments=num_labels_senti).to(device)
else:
    model_step2 = CategorySentiClassification.from_pretrained(
        bert_cache_dir, num_labels=num_labels_step2).to(device)
st.step(f"Model Step 2: {'DualHead' if USE_DUAL_HEAD else 'SingleHead'} | device={device}")
```

---

### 3d. `_build_v4_indobert.py` — String Kode Model `CategorySentiDualHead`

Tambah konstanta baru (mirip pola string kode di file ini untuk sel lain):

```python
CODE_DUAL_HEAD_MODEL = '''
class CategorySentiDualHead(BertPreTrainedModel):
    """Step 2 dengan dua head terpisah: Category (BCE) dan Sentiment (CE).

    Memungkinkan evaluasi Category F1 dan Sentiment F1 secara independen,
    berbeda dari CategorySentiClassification yang memprediksi label gabungan.
    """
    def __init__(self, config, num_categories=13, num_sentiments=3):
        super().__init__(config)
        self.num_categories = num_categories
        self.num_sentiments = num_sentiments
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.category_head  = nn.Linear(config.hidden_size, num_categories)
        self.sentiment_head = nn.Linear(config.hidden_size, num_sentiments)
        self.init_weights()

    def forward(self, input_ids, attention_mask=None, token_type_ids=None,
                category_labels=None, sentiment_labels=None):
        outputs  = self.bert(input_ids, attention_mask=attention_mask,
                             token_type_ids=token_type_ids)
        pooled   = self.dropout(outputs[1])
        cat_logits   = self.category_head(pooled)   # (B, 13)
        senti_logits = self.sentiment_head(pooled)  # (B, 3)

        loss = None
        if category_labels is not None and sentiment_labels is not None:
            # BCE untuk multi-label category
            bce   = nn.BCEWithLogitsLoss()
            cat_loss   = bce(cat_logits, category_labels.float())
            # CE untuk sentimen (single-label per prediksi)
            ce    = nn.CrossEntropyLoss()
            senti_loss = ce(senti_logits, sentiment_labels)
            loss  = cat_loss + senti_loss

        return (loss, cat_logits, senti_logits) if loss is not None \
               else (cat_logits, senti_logits)
'''
```

---

### 3e. `_build_v4_indobert.py` — Patch Evaluasi Sel 9a

Tambah evaluasi per head di `pair_eval` atau setelah evaluasi akhir:

```python
if USE_DUAL_HEAD:
    # Pisah metrik: category-only F1 & sentiment-only F1
    from eval_metrics import f1_score_category, f1_score_sentiment
    cat_f1   = f1_score_category(eval_gold_2, cat_preds)
    senti_f1 = f1_score_sentiment(eval_gold_2, senti_preds)
    st.step(f"Category F1: {cat_f1*100:.2f}% | Sentiment F1: {senti_f1*100:.2f}%")
    final_res["category_f1"]  = cat_f1
    final_res["sentiment_f1"] = senti_f1
```

---

## 4. File yang TIDAK Diubah

| File | Alasan |
|---|---|
| `modeling.py` (upstream) | Tidak boleh dimodifikasi — pipeline Inggris (kontrol) masih bergantung pada `CategorySentiClassification` asli |
| `dataset_utils.py` (upstream) | Preprocessing pasangan `(text, asp, opi)` tetap sama |
| `eval_metrics.py` (upstream) | `pair_eval` tetap dipakai; metrik per head ditambah sebagai post-process |
| `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` | Di-generate ulang dari `_build_v4_indobert.py` setelah patch |

---

## 5. Backward Compatibility

- Domain Inggris (`rest16`, `laptop`) tetap menggunakan `CategorySentiClassification` (single-head)
  melalui flag `USE_DUAL_HEAD = False`
- Checkpoint lama tetap bisa dimuat untuk evaluasi; hanya training baru yang pakai dual-head
- State file `pipeline_state.pkl` tidak berubah format

---

## 6. Urutan Implementasi

```
[ ] 1. Update taxonomy.py — tambah label_list_category(), label_list_sentiment(),
        num_labels_category(), num_labels_sentiment(), patch_processor_labels_dualhead()
[ ] 2. Tambah CODE_DUAL_HEAD_MODEL ke _build_v4_indobert.py
[ ] 3. Patch sel 8a — deteksi USE_DUAL_HEAD + inisialisasi label terpisah
[ ] 4. Patch sel 8d — conditional model instantiation (DualHead vs SingleHead)
[ ] 5. Patch sel 8e — forward pass dual-head (category_labels + sentiment_labels)
[ ] 6. Patch sel 9a — evaluasi per head + simpan category_f1 & sentiment_f1
[ ] 7. Jalankan _build_v4_indobert.py → regenerate .ipynb
[ ] 8. Verifikasi: DOMAIN=appsid → DualHead aktif | DOMAIN=rest16 → SingleHead
```

---

## 7. File yang Dibuat Baru

| File | Isi |
|---|---|
| `notebooks/DEV_PLAN_dualhead_step2.md` | Dokumen ini |
| `notebooks/WALKTHROUGH_dualhead_step2.md` | Dibuat setelah implementasi selesai |

---

## 8. Referensi

| File | Relevansi |
|---|---|
| `DEV_PLAN_acos_pipeline_4step_analysis.md` | Root cause analysis (sumber dokumen ini) |
| `acos_id/taxonomy.py` | `CATEGORIES`, `SENTIMENTS`, `catsenti_labels()` |
| `notebooks/_build_v4_indobert.py` | Generator notebook V4 — target utama patch |
| `notebooks/DEV_PLAN_resume_training_per_epoch.md` | Contoh pola implementasi sebelumnya |
