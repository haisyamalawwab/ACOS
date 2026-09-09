# 028 — Implementasi Arsitektur Dual-Head Step 2 dan Training Loop Pipeline ACOS IndoBERT

**Tanggal:** 09 September 2026  
**Topik:** Implementasi Dual-Head Classifier (Category & Sentiment) pada Step 2 Pipeline ACOS IndoBERT  
**Dokumen Terkait:**  
- `reports/027_analisis_arsitektur_pipeline_acos_dualhead_step2_09092026.md`  
- `ACOS-IndoBERT/notebooks/DEV_PLAN_dualhead_step2.md`  
- `ACOS-IndoBERT/notebooks/WALKTHROUGH_dualhead_step2.md`  
- `ACOS-IndoBERT/acos_id/taxonomy.py`  
- `ACOS-IndoBERT/notebooks/_build_v4_indobert.py`  
- `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`  

---

## 1. Eksekutif Ringkasan

Berdasarkan analisis arsitektur pada Laporan No. 027, Step 2 pada pipeline standar ACOS (`Extract-Classify-ACOS`, Cai et al. 2021) menggunakan **label gabungan** `{CATEGORY}#{SENTIMENT}` (39 kelas gabungan untuk domain Indonesia Apps-ACOS: 13 kategori × 3 sentimen). Model upstream `CategorySentiClassification` menggunakan satu layer linear head `Linear(1536, 39)` dengan multi-label BCE loss. Keterbatasan utama pendekatan single-head gabungan ini adalah:
1. Performa klasifikasi Aspect Category (`C`) dan Sentiment (`S`) tidak dapat dievaluasi secara mandiri.
2. Error pada prediksi kategori mendistorsi metrik evaluasi sentimen dan sebaliknya.
3. Sub-task ACOS parsial (`A+C` dan `O+S`) tidak dapat diukur secara presisi.

Solusi **Opsi B: Dual-Head Classifier** kini telah berhasil diimplementasikan penuh secara in-place pada generator `_build_v4_indobert.py` tanpa merusak kompatibilitas backward kontrol bahasa Inggris (`rest16`, `laptop`) dan tanpa mengubah berkas upstream repo (`modeling.py`, `dataset_utils.py`, `eval_metrics.py`).

---

## 2. Arsitektur Teknis `CategorySentiDualHead`

### 2.1 Representasi Fusi Span Pasangan (Aspect-Opinion)
Model `CategorySentiDualHead` mempertahankan mekanisme ekstraksi representasi span kandidat yang digunakan oleh baseline ACOS:
- Mengambil sequence hidden states dari `BertModel` (`pooled_outputs`, dimensi `(B, L, H)`).
- Menghitung representasi rata-rata span aspect kandidat (`candidate_aspect_rep`, ukuran `H = 768`).
- Menghitung representasi rata-rata span opinion kandidat (`candidate_opinion_rep`, ukuran `H = 768`).
- Menggabungkan keduanya menjadi representasi pasangan berukuran `1536` (`H * 2`):
  $$\mathbf{h}_{\text{pair}} = \text{Dropout}([\mathbf{r}_{\text{aspect}} \,\|\, \mathbf{r}_{\text{opinion}}])$$

### 2.2 Dua Output Head Terpisah
Dari $\mathbf{h}_{\text{pair}}$, fitur diproyeksikan ke dua head independen:
1. **Category Head**: $\mathbf{z}_{\text{cat}} = \mathbf{W}_{\text{cat}} \mathbf{h}_{\text{pair}} \in \mathbb{R}^{13}$
   - Loss: Multi-label Binary Cross-Entropy with Logits (`nn.BCEWithLogitsLoss`)
   - Mengizinkan ulasan memiliki lebih dari satu kategori untuk pasangan span yang sama.
2. **Sentiment Head**: $\mathbf{z}_{\text{senti}} = \mathbf{W}_{\text{senti}} \mathbf{h}_{\text{pair}} \in \mathbb{R}^{3}$
   - Loss: Multi-class Cross-Entropy (`nn.CrossEntropyLoss(ignore_index=-1)`)
   - Memprediksi distribusi kelas sentimen (0: negatif, 1: netral, 2: positif). Sampel negatif (pasangan tanpa kategori aktif) diabaikan via masking `ignore_index = -1`.

### 2.3 Rekonstruksi `fused_logits` (39 Dimensi) untuk Kompatibilitas Penuh
Agar upstream `pair_eval` di `eval_metrics.py` (yang mengevaluasi quadruple micro-F1) tetap bekerja 100% tanpa modifikasi kode upstream, `CategorySentiDualHead` merekonstruksi logit gabungan:
$$\hat{s} = \arg\max(\mathbf{z}_{\text{senti}})$$
$$\mathbf{z}_{\text{fused}}[c \cdot 3 + s] = \begin{cases} \mathbf{z}_{\text{cat}}[c], & \text{jika } s = \hat{s} \\ \mathbf{z}_{\text{cat}}[c] - 10000.0, & \text{jika } s \neq \hat{s} \end{cases}$$

Dengan formulasi ini:
- Jika $\mathbf{z}_{\text{cat}}[c] > 0$ (kategori aktif) dan $s = \hat{s}$, maka logit gabungan bernilai positif.
- Upstream `np.where(logits[i] > 0)` secara otomatis memilih pasangan kategori dan sentimen argmax yang tepat!
- Tidak ada breaking change terhadap struktur quadruple `[cate, senti, asp, opi]`.

---

## 3. Rincian Implementasi per Komponen

### 3.1 `ACOS-IndoBERT/acos_id/taxonomy.py`
Menambahkan helper taksonomi dual-head:
- `label_list_category()`: mengembalikan 13 label kategori appsid.
- `label_list_sentiment()`: mengembalikan 3 label sentimen `['0', '1', '2']`.
- `num_labels_category()`: `13`.
- `num_labels_sentiment()`: `3`.
- `patch_processor_labels_dualhead(processors)`: mem-patch `CategorySentiProcessor` secara dinamis agar memiliki method `get_labels_category()` dan `get_labels_sentiment()`.

### 3.2 `ACOS-IndoBERT/notebooks/_build_v4_indobert.py`
Menerapkan 4 patch utama di notebook V4:
1. **Sel 8a (Inisialisasi Step 2):**
   - Sisipkan class `CategorySentiDualHead`.
   - Inisialisasi flag `USE_DUAL_HEAD = acos_taxonomy.is_id_domain(DOMAIN)`.
   - Inisialisasi `label_list_cat`, `label_list_senti`, `num_labels_cat`, `num_labels_senti`.
2. **Sel 8d (Model Step 2):**
   - Instansiasi kondisional:
     ```python
     if globals().get("USE_DUAL_HEAD", False):
         model_step2 = CategorySentiDualHead.from_pretrained(
             bert_cache_dir,
             num_categories=num_labels_cat,
             num_sentiments=num_labels_senti).to(device)
     else:
         model_step2 = CategorySentiClassification.from_pretrained(...)
     ```
3. **Sel 8e (Training Loop Step 2):**
   - Forward pass memanfaatkan loss dual-head (BCE + CE ber-masking).
   - Evaluasi per epoch: selain quadruple F1 via `pair_eval`, ditambahkan evaluasi per-head mandiri pada `eval_loader_2`:
     - `Category micro-F1`
     - `Sentiment Accuracy`
   - Log visual real-time di progress bar: `st.step(f"   🎯 Dual-Head [Epoch {epoch:02d}]: Category micro-F1: ... | Sentiment Acc: ...")`
   - Metrik tersimpan ke `step2_training_history.csv` dan `step2_run_result.json` (`use_dual_head: true`).
4. **Sel 9a (Evaluasi Final Step 2):**
   - Conditional best model loading: memuat bobot model terbaik dari `session_dirs["step2_checkpoint"]` menggunakan `CategorySentiDualHead`.
   - Evaluasi mandiri benchmark akhir per-head:
     - `category_micro_f1` & `category_macro_f1`
     - `sentiment_accuracy` & `sentiment_macro_f1`
   - Hasil disimpan ke `logs/master_metrics.json` dalam blok `"dual_head"`.

---

## 4. Hasil Verifikasi & Uji Mutu

| Komponen Pengujian | Metode | Hasil | Status |
|---|---|---|---|
| Taksonomi Dual-Head | Unit test method `label_list_*` | 13 kategori, 3 sentimen | ✅ LULUS |
| Parser Build Script | `python -X utf8 _build_v4_indobert.py` | Generator V4 selesai, MD5 `d66469d7a4fdc2310361cfb5067b553d` | ✅ LULUS |
| Kelengkapan Sel Notebook | Verifikasi JSON cell count | 80 sel (48 kode, 32 markdown) | ✅ LULUS |
| Sintaks Seluruh Sel Kode | `ast.parse` pada 48 sel kode | 0 syntax errors, 0 undefined escapes | ✅ LULUS |
| Backward Compatibility | Conditional branching flag `USE_DUAL_HEAD` | Domain Inggris tetap memakai single-head asli | ✅ LULUS |

---

## 5. Panduan Eksekusi di Google Colab

Notebook target yang siap dijalankan di Google Colab:
`ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`

Saat dijalankan pada lingkungan Colab:
1. `DOMAIN = "appsid"` akan secara otomatis mengaktifkan `USE_DUAL_HEAD = True`.
2. Model Step 2 akan menampilkan: `Model: CategorySentiDualHead (13 cat + 3 senti)`.
3. Loop training Step 2 (sel 8e) akan melaporkan metrik Category micro-F1 dan Sentiment Accuracy di samping Quadruple Micro-F1 pada setiap epoch.
4. Evaluasi akhir (sel 9a) akan menghasilkan metrik lengkap yang tersimpan di `master_metrics.json`.
