# Lokasi Fase Word Embedding & Fine-Tuning di ACOS-ASLI

Tanggal: 2026-08-27 17:15
Fokus: di mana (file & baris) word embedding dan fine-tuning terjadi dalam repo.
Metode: penelusuran kode (`modeling.py`, `run_step1.py`, `run_step2.py`,
`run_classifier_dataset_utils.py`, notebook `00_ACOS_Master_Pipeline_Colab_ASLI.ipynb`).

---

## 1. Klarifikasi: tidak ada "fase word embedding" terpisah

Di BERT, istilah "word embedding" sering membingungkan dua hal berbeda:

- **Tokenisasi WordPiece** (kata → token ID): lookup deterministik di vocab,
  **tidak dilatih**.
- **Layer embedding BERT** (`BertEmbeddings`): layer `nn.Module` sungguhan,
  dijalankan di awal SETIAP `model.forward()` (training & inferensi), dan bobotnya
  **ikut diperbarui saat fine-tuning**.

Jadi embedding bukan "tahap" tersendiri, melainkan bagian dari forward pass.

---

## 2. Word Embedding — lokasinya

### 2a. Tokenisasi WordPiece (input → token ID)
- Kode: `bert_utils/tokenization.py` → class `BertTokenizer` (legacy).
- Dipanggil saat konversi fitur:
  - Step 1: `run_classifier_dataset_utils.py:346` —
    `tokenizer.convert_tokens_to_ids(aspect_tokens)`
  - Step 2: `run_classifier_dataset_utils.py:444` —
    `tokenizer.convert_tokens_to_ids(aspect_tokens)`
  - Notebook 00: **cell 10** (`BertTokenizer.from_pretrained(...)`, lalu
    `convert_tokens_to_ids`); **cell 18** (inferensi, `convert_tokens_to_ids`).

### 2b. Layer embedding BERT (`BertEmbeddings`)
- `modeling.py:283-311`:
  - `word_embeddings` (line 288)
  - `position_embeddings` (line 289)
  - `token_type_embeddings` (line 290)
  - dijumlahkan → LayerNorm → dropout (lines 308-310)
- Dieksekusi di awal `BertModel.forward` untuk setiap batch (train & infer).
- Karena bagian dari model, **bobotnya di-update saat fine-tuning** (lihat §3).

---

## 3. Fine-Tuning — lokasinya (training loop, 2 stage)

Fine-tuning = loop di mana gradien menyebar ke seluruh model (embedding + encoder
+ head task), bukan hanya head.

### Step 1 — `run_step1.py` / notebook 00 **cell 10**
- `model.train()` — `run_step1.py:398`
- `loss.backward()` — `run_step1.py:428` (notebook cell 10: `loss.backward()`)
- `optimizer.step()` — `run_step1.py:439` (notebook cell 10: `optimizer_1.step()`)

### Step 2 — `run_step2.py` / notebook 00 **cell 14**
- `model.train()` — `run_step2.py:276`
- `loss.backward()` — `run_step2.py:301` (notebook cell 14: `loss.backward()`)
- `optimizer.step()` — `run_step2.py:306` (notebook cell 14: `optimizer_2.step()`)

### Optimizer menerima SELURUH parameter model
- `param_optimizer = list(model.named_parameters())` di `run_step1.py:383` &
  `run_step2.py:257`, lalu `BertAdam`.
- Artinya: **seluruh BERT (embeddings + encoder) + head task di-fine-tune, tidak
  di-freeze.**
- Titik awal = checkpoint pretrained via `from_pretrained(bert_cache_dir)` — itu
  "embeddings sudah jadi"; fine-tuning menyesuaikannya ke tugas ACOS.

---

## 4. Catatan penting

- **Tidak ada stage "training word embedding" tersendiri.** Embedding BERT itu
  pretrained (untuk `bert-base-uncased`: korpus Inggris; untuk IndoBERT: korpus
  Indonesia), lalu di-update bersama saat fine-tuning. Tokenizer WordPiece sendiri
  **tetap fix** (tidak dilatih).
- Fine-tuning terjadi **dua kali** (Stage 1 & Stage 2), masing-masing mulai dari
  checkpoint base pretrained — bukan berantai. Step 2 TIDAK melanjutkan dari bobot
  Step 1; keduanya berangkat dari `bert-base-uncased`. Itu desain pipeline
  (co-extraction lalu classification).
- Untuk IndoBERT: layer embedding & tokenizer cukup diganti sumber checkpoint-nya
  (`indobenchmark/indobert-base-p1`); **kode fine-tuning tetap sama** — hanya path
  model + vocab yang berubah. Menyambung ke `reports/008_persiapan_rencana_indobert_...`.

---

## 5. Ringkasan cepat

| Bagian | Lokasi |
|---|---|
| Tokenisasi WordPiece | `bert_utils/tokenization.py` (`BertTokenizer`); dipakai di `run_classifier_dataset_utils.py:346/444` & notebook cell 10/18 |
| Layer embedding BERT | `modeling.py:283-311` (jalan tiap `forward`) |
| Fine-tuning Step 1 | `run_step1.py:398/428/439` (notebook cell 10) |
| Fine-tuning Step 2 | `run_step2.py:276/301/306` (notebook cell 14) |
| Optimizer (semua param) | `run_step1.py:383` & `run_step2.py:257` (`BertAdam`) |

## 6. Batas verifikasi

- Lokasi di atas dari pembacaan statis + grep `modeling.py`, `run_step1.py`,
  `run_step2.py`, `run_classifier_dataset_utils.py`, dan notebook 00.
- Notebook 00 saat ini bernama `00_ACOS_Master_Pipeline_Colab_ASLI.ipynb`
  (sudah di-rename dari `00_ACOS_Master_Pipeline_Colab.ipynb`).
