## Goal
Tambah kelas **`BertForQuintupleABSA`** baru di `Extract-Classify-ACOS/modeling.py` yang mampu melayani tugas ACOSE quintuple **Aspek–Category–Opinion–Sentiment–Emotion** (5 elemen), tanpa mengubah `BertForQuadABSA` yang ada.

## Pendekatan (sesuai jawaban Anda)
- **Kelas baru** di `modeling.py`, meniru idiom `BertForQuadABSA` + `CategorySentiClassification`.
- **Factored** head label: satu classifier per elemen label (category, sentiment, emotion), bukan joint cross-product.
- Menggunakan BERT backbone yang sama (`BertModel`), CRF untuk span aspect+opinion, 2 head implicit, dan head label factored untuk 5 elemen.

## Apa yang diimplementasikan

### 1. Kelas `BertForQuintupleABSA(BertPreTrainedModel)` di modeling.py (setelah baris 1588 / di dekat `BertForQuadABSA`)
Constructor `__init__(self, config, num_labels=2, num_category=13, num_sentiment=3, num_emotion=6, output_attentions=False, keep_multihead_output=False)`:
- `self.bert = BertModel(config, ...)` — backbone sama.
- `self.crf_num = 6` + `self.crf = CRF(6, batch_first=True)` — span aspect+opinion (BI tagging untuk 2 span → 6 tag: B-A/I-A/B-O/I-O/O + implicit marker), identik dengan `BertForQuadABSA`.
- `self.dense_output` — Dropout + Linear(768, 6) → emisi CRF.
- `self.imp_asp_classifier`, `self.imp_opi_classifier` — binary implicit (sama seperti Quad).
- **Factored label head** (per elemen):
  - `self.fused = nn.Linear(768*2, 768)` + `nn.Tanh()` (atau langsung Linear 768*2→head), dipakai bersama untuk category/sentiment/emotion — konsisten dengan `CategorySentiClassification` yang pooling+fused aspect&opinion span.
  - `self.category_classifier` → Linear(768, num_category)
  - `self.sentiment_classifier` → Linear(768, num_sentiment)
  - `self.emotion_classifier` → Linear(768, num_emotion)
- `self.apply(self.init_bert_weights)`.

### 2. `forward(self, aspect_input_ids, aspect_token_type_ids, aspect_attention_mask, aspect_labels, candidate_aspect, candidate_opinion, exist_imp_aspect, exist_imp_opinion, category_ids, sentiment_ids, emotion_ids)`
Gabungan alur Quad (step-1) dan faktored head (step-2):
- Jalankan `self.bert` → `(pooled_outputs, pooled_output)`.
- Implicit aspect/opinion: `CrossEntropyLoss` (sama seperti Quad).
- CRF span: `ae_loss = -self.crf(emissions, aspect_labels, mask, reduction='mean')`, `pred_tags = self.crf.decode(...)`.
- Fused span representation (dari `CategorySentiClassification`): pooling mask aspect & opinion → concat `[candidate_aspect_rep, candidate_opinion_rep]` → `fused_feature`.
- **Factored losses** (masing-masing BCEWithLogitsLoss, konsisten dengan head step-2 upstream):
  - `category_loss = BCE(category_logits, category_ids.float())`
  - `sentiment_loss = BCE(sentiment_logits, sentiment_ids.float())`
  - `emotion_loss = BCE(emotion_logits, emotion_ids.float())`
- `total_loss = ae_loss + imp_aspect_loss + imp_opinion_loss + category_loss + sentiment_loss + emotion_loss`
- Return `[total_loss], [pred_tags, imp_aspect_exist, imp_opinion_exist, category_logits, sentiment_logits, emotion_logits]`.

Semua argumen label dibuat opsional (bertipe None di awal) sehingga model tetap bisa dipakai untuk inference span-only bila jalur label tidak disuplai — meminimalkan gangguan pada pemanggil lain.

## Tidak diubah
- `BertForQuadABSA` dan `CategorySentiClassification` dibiarkan utuh (backward-compat registrasi `'quad': BertForQuadABSA` di run_step1.py tetap berlaku).
- Tidak menyentuh paket `absa5/` (stack quintuple yang sudah ada). `BertForQuintupleABSA` adalah jalur mandiri yang melayani tugas yang sama.

## Catatan
- `CRF`, `CrossEntropyLoss`, `BCEWithLogitsLoss` sudah diimpor di modeling.py (baris 31-32) — tidak perlu import baru.
- Nilai default num_category=13, num_sentiment=3, num_emotion=6 diambil dari absa5 taxonomy (`emot_id_netral` = 6 label: sedih/marah/cinta/takut/senang/netral), sesuai keputusan desain ACOSE yang sudah terekam.
- Penulisan hanya menambah satu kelas baru; tidak ada perubahan build notebook atau run scripts. Verifikasi: `python -c "from modeling import BertForQuintupleABSA"` dari folder `Extract-Classify-ACOS` (import berhasil tanpa torch runtime karena class hanya didefinisikan).