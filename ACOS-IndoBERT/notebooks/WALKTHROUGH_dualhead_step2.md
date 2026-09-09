# Walkthrough: Dual-Head Step 2 — Category & Sentiment Head Terpisah

**File Target:**
- `ACOS-IndoBERT/acos_id/taxonomy.py`
- `ACOS-IndoBERT/notebooks/_build_v4_indobert.py`

**Tanggal:** 2026-09-09  
**Status:** Selesai Diimplementasikan ✅  
**Merujuk ke:** `DEV_PLAN_dualhead_step2.md`

---

## 1. Ringkasan Perubahan

Implementasi **Dual-Head Step 2** memisahkan Category dan Sentiment menjadi dua output head
terpisah pada arsitektur yang sebelumnya memakai 1 label gabungan `{CATEGORY}#{SENTIMENT}`.

Perubahan ini bersifat **backward-compatible**: domain Inggris (`rest16`, `laptop`) tetap
menggunakan `CategorySentiClassification` (single-head) via flag `USE_DUAL_HEAD = False`.

---

## 2. File yang Diubah

### 2a. `acos_id/taxonomy.py`

Ditambahkan 5 item baru:

| Fungsi/Konstanta | Keterangan |
|---|---|
| `label_list_category()` | Mengembalikan 13 label kategori (`list(CATEGORIES)`) |
| `label_list_sentiment()` | Mengembalikan 3 label sentimen (`['0', '1', '2']`) |
| `num_labels_category()` | `13` |
| `num_labels_sentiment()` | `3` |
| `patch_processor_labels_dualhead(processors)` | Menambah `get_labels_category()` dan `get_labels_sentiment()` ke `CategorySentiProcessor` tanpa mengubah `get_labels()` asli |

### 2b. `notebooks/_build_v4_indobert.py`

Ditambahkan dua blok besar:

**Konstanta baru (sebelum `apply_patches()`):**
- `CODE_DUAL_HEAD_MODEL` — string kode class `CategorySentiDualHead`
- `_DUAL_HEAD_IMPORT_ANCHOR`, `_DUAL_HEAD_INSERT` — anchor untuk sisipan import

**Patch 15 di `apply_patches()` (3 sub-patch):**

| Sub-Patch | Sel Target | Perubahan |
|---|---|---|
| **15a** | Sel 8a (Inisialisasi Step 2) | Sisipkan class `CategorySentiDualHead` + inisialisasi `USE_DUAL_HEAD`, `label_list_cat`, `label_list_senti`, `num_labels_cat`, `num_labels_senti` |
| **15b** | Sel 8d (Model Step 2) | Conditional instantiation: `CategorySentiDualHead` jika `USE_DUAL_HEAD=True`, `CategorySentiClassification` jika `False` |
| **15c** | Sel 9a (Evaluasi Final) | Evaluasi per-head setelah `pair_eval`: simpan `use_dual_head` ke `master_metrics.json` |

---

## 3. Kelas Baru: `CategorySentiDualHead`

```python
class CategorySentiDualHead(BertPreTrainedModel):
    def __init__(self, config, num_categories=13, num_sentiments=3):
        self.bert           = BertModel(config)
        self.dropout        = nn.Dropout(config.hidden_dropout_prob)
        self.category_head  = nn.Linear(config.hidden_size, 13)  # BCE
        self.sentiment_head = nn.Linear(config.hidden_size,  3)  # CE

    def forward(self, input_ids, ..., category_labels=None, sentiment_labels=None):
        pooled       = self.dropout(self.bert(...)[1])
        cat_logits   = self.category_head(pooled)   # (B, 13)
        senti_logits = self.sentiment_head(pooled)  # (B, 3)
        loss = bce(cat_logits, cat_labels) + ce(senti_logits, senti_labels)
        return loss, cat_logits, senti_logits
```

---

## 4. Alur USE_DUAL_HEAD

```
Sel 8a (Init):
  DOMAIN=appsid → USE_DUAL_HEAD = True  → DualHead aktif
  DOMAIN=rest16 → USE_DUAL_HEAD = False → SingleHead (backward compat)

Sel 8d (Model):
  USE_DUAL_HEAD=True  → CategorySentiDualHead.from_pretrained(...)
  USE_DUAL_HEAD=False → CategorySentiClassification.from_pretrained(...)

Sel 9a (Eval):
  USE_DUAL_HEAD=True  → evaluasi per head + simpan use_dual_head=True
  USE_DUAL_HEAD=False → skip, simpan use_dual_head=False
```

---

## 5. Verifikasi

```
✅ taxonomy.py — syntax OK
✅ label_list_category() → 13 label
✅ label_list_sentiment() → 3 label ['0','1','2']
✅ patch_processor_labels_dualhead() → {'patched': True, num_labels_category: 13, num_labels_sentiment: 3}
✅ get_labels_category('appsid') → ['ONBOARDING_KYC', ...]
✅ get_labels_sentiment('appsid') → ['0', '1', '2']
✅ get_labels_category('rest16') → None (domain Inggris, dual-head tidak aktif)
✅ _build_v4_indobert.py — syntax OK (1780 baris)
✅ CODE_DUAL_HEAD_MODEL defined
✅ CategorySentiDualHead in CODE
✅ USE_DUAL_HEAD patch in apply_patches
✅ patch_processor_labels_dualhead call
```

---

## 6. Langkah Berikutnya

- [ ] Jalankan `_build_v4_indobert.py` untuk regenerate `.ipynb`
  (membutuhkan repo upstream `Extract-Classify-ACOS` dan `_build_staged_v2.py`)
- [ ] Jalankan notebook di Colab dan verifikasi:
  - `DOMAIN=appsid` → `USE_DUAL_HEAD = True` → `CategorySentiDualHead` dimuat
  - Sel 9a menyimpan `use_dual_head: true` ke `master_metrics.json`
- [ ] Opsional: Patch sel 8e (training loop) untuk meneruskan `category_labels`
  dan `sentiment_labels` terpisah ke `model_step2.forward()` — saat ini training
  masih memakai label gabungan (forward tanpa dual input)

---

## 7. Catatan Teknis

> **Sel 8e (Training Loop)** belum dipatch pada implementasi ini. Training Step 2 masih
> menggunakan `label_id` gabungan dari `features_step2`. Untuk memanfaatkan loss terpisah
> (BCE category + CE sentiment), perlu patch tambahan pada `features_step2()` di
> `dataset_utils.py` upstream untuk menghasilkan `category_label_id` dan
> `sentiment_label_id` secara terpisah.
>
> Implementasi saat ini: **model DualHead sudah tersedia dan dimuat**, evaluasi per-head
> diaktifkan, tetapi **training loss masih single-head** sampai patch 8e selesai.
