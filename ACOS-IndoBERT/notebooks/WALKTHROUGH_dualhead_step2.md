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
    def __init__(self, config, num_categories=13, num_sentiments=3, ...):
        super().__init__(config)
        self.bert           = BertModel(config)
        self.dropout        = nn.Dropout(config.hidden_dropout_prob)
        self.category_head  = nn.Linear(config.hidden_size * 2, num_categories)  # Multi-label BCE
        self.sentiment_head = nn.Linear(config.hidden_size * 2, num_sentiments)  # Multi-class CE
        self.apply(self.init_bert_weights)

    def forward(self, tokenizer, _e, aspect_input_ids, aspect_token_type_ids,
                aspect_attention_mask, candidate_aspect, candidate_opinion, label_id=None):
        # 1. Ekstraksi representasi BERT dan pooling rata-rata token span kandidat aspect & opinion
        fused_rep = self.dropout(torch.cat([candidate_aspect_rep, candidate_opinion_rep], -1))
        cat_logits = self.category_head(fused_rep)     # (B, 13)
        senti_logits = self.sentiment_head(fused_rep)  # (B, 3)

        # 2. Dual Loss: BCE (Category) + CE (Sentiment, ignore_index=-1 untuk sampel negatif)
        # dihitung otomatis dari tensor ground truth label_id (39-dim)
        loss = bce_loss(cat_logits, cat_targets) + ce_loss(senti_logits, senti_targets)

        # 3. Rekonstruksi fused_logits (39-dim) agar 100% kompatibel dengan pair_eval upstream
        return [loss], [fused_logits]
```

---

## 4. Alur USE_DUAL_HEAD

```
Sel 8a (Init):
  DOMAIN=appsid → USE_DUAL_HEAD = True  → DualHead aktif, label terpisah 13 cat + 3 senti
  DOMAIN=rest16 → USE_DUAL_HEAD = False → SingleHead (backward compat)

Sel 8d (Model):
  USE_DUAL_HEAD=True  → CategorySentiDualHead.from_pretrained(...)
  USE_DUAL_HEAD=False → CategorySentiClassification.from_pretrained(...)

Sel 8e (Training Loop):
  USE_DUAL_HEAD=True  → Dual loss (BCE cat + CE senti), evaluasi per epoch menghitung:
                        - Category micro-F1
                        - Sentiment Accuracy
                        Tersimpan di step2_training_history.csv & step2_run_result.json
  USE_DUAL_HEAD=False → Single loss (BCE 39 kelas gabungan)

Sel 9a (Final Eval):
  USE_DUAL_HEAD=True  → Model terbaik dimuat sebagai CategorySentiDualHead,
                        evaluasi mandiri per head: Category micro/macro-F1 & Sentiment accuracy/macro-F1
                        Tersimpan ke master_metrics.json
  USE_DUAL_HEAD=False → Model terbaik dimuat sebagai CategorySentiClassification
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
✅ _build_v4_indobert.py — syntax OK & UTF-8 safe
✅ CategorySentiDualHead dengan fused aspect-opinion representation & dual loss (BCE + CE)
✅ Rekonstruksi fused_logits (39 kelas) untuk kompatibilitas pair_eval tanpa breaking changes
✅ Patch sel 8e: loop training Step 2 mencatat category_micro_f1 dan sentiment_acc per epoch
✅ Patch sel 9a: conditional model loading & evaluasi per-head lengkap ke master_metrics.json
✅ Regenerasi 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb berhasil (80 sel, 48 kode)
✅ ZERO SYNTAX ERRORS pada seluruh 48 sel kode notebook (ast.parse verified)
```

---

## 6. Status Akhir

- [x] Tambah helper taksonomi dual-head di `acos_id/taxonomy.py`
- [x] Buat kelas `CategorySentiDualHead` dengan representasi kandidat pasangan yang presisi
- [x] Hubungkan dual loss (BCE kategori 13 kelas + CE sentimen 3 kelas ber-masking)
- [x] Patch sel 8a (inisialisasi & patch processor)
- [x] Patch sel 8d (conditional model instantiation)
- [x] Patch sel 8e (loop training + per-epoch per-head evaluation)
- [x] Patch sel 9a (conditional best model loading + final per-head benchmark)
- [x] Regenerasi `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` dan verifikasi AST penuh
- [x] Dokumentasikan hasil implementasi ke laporan resmi `reports/028_implementasi_dualhead_step2_dan_training_loop_09092026.md`
