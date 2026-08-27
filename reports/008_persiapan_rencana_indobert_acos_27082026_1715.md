# Persiapan & Rencana Adaptasi ACOS-ASLI ke IndoBERT

Tanggal: 2026-08-27 17:15
Fokus: apa yang harus disiapkan & direncanakan untuk menjalankan pipeline ACOS
dengan IndoBERT (Bahasa Indonesia).
Metode: analisis berbasis fakta terverifikasi di repo (`modeling.py`,
`bert_utils/tokenization.py`, `run.sh`, `run_classifier_dataset_utils.py`).

---

## 1. Fakta repo yang menentukan rencana (terverifikasi)

- `modeling.py` & `bert_utils/tokenization.py` memakai **`pytorch_pretrained_bert`
  (paket LEGACY, pra-`transformers`)**, bukan `transformers`. IndoBERT di HF
  butuh API `transformers`.
- `run.sh` hardcode `BERT_BASE_DIR=.../uncased_L-12_H-768_A-12` (English uncased BERT).
- Kategori **hardcode per domain**: rest16 = 13 kategori (`run_classifier_dataset_utils.py:235`),
  laptop = 121 kategori (baris 241-259). Itu taksonomi Inggris.
- Offset span (`a_st,a_ed`) adalah **indeks WordPiece spesifik tokenizer** → semua
  data prep harus diulang dengan vocab IndoBERT.

---

## 2. Blocker #1: DATA (penentu bisa/tidaknya)

Tidak ada dataset ACOS berbahasa Indonesia (quadruple: aspek–kategori–opini–sentimen)
yang dipublikasi. Tanpa data beranotasi, IndoBERT tidak bisa dilatih apalagi
dievaluasi. Ini pekerjaan annotasi, bukan teknis.

| Opsi | Upaya | Risiko |
|---|---|---|
| Anotasi baru (review ID restoran/e-commerce) jadi quadruple | Tinggi (tim + pedoman + IAA) | Mahal, waktu |
| Adaptasi dataset ABSA Indonesia existing → perluas ke quadruple | Sedang | Sedikit yang punya quadruple penuh |
| LLM bootstrap anotasi lalu validasi manusia | Sedang | Perlu audit kualitas |

**Rencanakan dulu:** domain (restoran? e-commerce? umum?), sumber data
(Google Maps ID, Tokopedia, Twitter?), dan pedoman anotasi yang menangani
**aspek/opini implisit** versi Indonesia.

---

## 3. Blocker #2: Porting kode BERT legacy → transformers

`BertForQuadABSA` (BERT+CRF+2 head+implicit head) & `CategorySentiClassification`
ditulis di atas `pytorch_pretrained_bert`. IndoBERT
(`indobenchmark/indobert-base-p1`, uncased) baru bisa dipakai setelah:
- Ganti base class ke `transformers.BertPreTrainedModel` / `BertModel`.
- Muat weight IndoBERT via `from_pretrained`.
- Ganti `bert_utils/tokenization.py` (legacy) → `transformers.BertTokenizer`.

Rekomendasi: **pakai IndoBERT varian arsitektur BERT** (bukan RoBERTa) supaya
perubahan mekanis. `w11wo/indonesian-roberta-base` butuh ubah class model +
penanganan casing → hindari kecuali perlu.

---

## 4. Blocker #3: Tokenizer & regenerasi data (tokenizer-specific)

- `tokenized_data/*.tsv` sekarang ter-WordPiece pakai vocab English BERT → **harus
  di-generate ulang** dengan `IndoBertTokenizer`.
- Format quad/pair tetap (`text \t start,end CATEGORY#ASPECT sentiment start,end`),
  tapi offset mengacu ke subword IndoBERT.
- Bahasa Indonesia afiksatif (me-, ber-, -nya, -kan): bentuk surface aspek/opini
  kaya morfologi — pedoman anotasi & evaluasi harus memperhitungkannya (WordPiece
  tetap bisa, asal konsisten).

---

## 5. Blocker #4: Taksonomi kategori Indonesia

Ganti list hardcode (rest16/laptop) dengan kategori domain Indonesia, mis.
`RESTORAN#MAKANAN`, `RESTORAN#PELAYANAN`, `PRODUK#HARGA`. Jumlah kelas =
`|kategori| × 3` (sentimen). Menentukan ukuran layer terakhir Step 2.

---

## 6. Blocker #5: Perbaiki dulu bug Step 2

Notebook 00 **crash di Step 2** (`KeyError: 'a--1,-1'`) — belum selesai dieksekusi.
Sebelum mengandalkan pipeline untuk IndoBERT, terapkan fix parser regex di cell 12 /
`get_1st_pairs.py` (lihat `reports/007_solusi_error_keyerror_step2_acos_27082026_1554.md`),
kalau tidak validasi port tidak bisa dilakukan.

---

## 7. Rencana bertahap

1. **Fase 0 — Scope:** domain + sumber data + pedoman anotasi Indonesia.
2. **Fase 1 — Data:** kumpulkan & anotasi quadruple ID (blocker utama).
3. **Fase 2 — Port kode:** `modeling.py` + `tokenization` → `transformers`; muat IndoBERT.
4. **Fase 3 — Prep data:** generator `tokenized_data` dengan IndoBERT tokenizer + taksonomi ID.
5. **Fase 4 — Fix & validasi:** terapkan fix Step 2, jalankan end-to-end di domain kecil.
6. **Fase 5 — Train/eval:** 2-stage pipeline dengan IndoBERT; ukur vs baseline.

---

## 8. Yang tidak perlu diubah

- `eval_metrics.py` (measureQuad/pair_eval) relatif model-agnostik — asal format data cocok.
- Logika cross-product `get_1st_pairs.py` (hanya perlu di-harden, bukan diubah secara linguistic).
- Arsitektur 2-stage (co-extraction → classification) tetap sama.

**Bottom line:** IndoBERT bukan sekadar swap checkpoint. Dua hal wajib disiapkan
lebih dulu = (1) **dataset quadruple Indonesia** (tidak ada sama sekali), dan
(2) **porting kode dari `pytorch_pretrained_bert` ke `transformers`**. Tanpa
keduanya, model tak bisa berjalan.

## 9. Batas verifikasi

- Fakta di §1 dari pembacaan statis `modeling.py`, `tokenization.py`, `run.sh`,
  `run_classifier_dataset_utils.py` (grep + baca). Tidak ada eksekusi pipeline.
- Pilihan varian IndoBERT (indobert-base-p1 dll.) merujuk pada konvensi HF yang
  umum; validasi ketersediaan checkpoint dilakukan saat implementasi.
