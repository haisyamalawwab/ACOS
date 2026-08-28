# Rencana Konsep Adaptasi ACOS-ASLI ke IndoBERT (Dokumen Terpadu / Actionable)

Tanggal: 2026-08-27 17:45
Latar: penggabung seluruh groundwork di sesi paralel — `001`–`009` (analisis repo
& rencana IndoBERT), `010_konsep_rencana_indobert` (verifikasi mekanis),
`010_survey_nusabert_nusax` & `011_perbandingan` (opsi encoder Nusantara).
Dokumen ini adalah **satu-gaya panduan implementasi** yang siap dieksekusi,
bukan sekadar deskripsi. Semua klaim arsitektur sudah diverifikasi pada
`modeling.py` (hardcode dim), `run_classifier_dataset_utils.py` (taksonomi),
`bert_utils/tokenization.py` (legacy tokenizer).

> Catatan penomoran: induk `010` bertabrakan (dua file `010`, dua `007`). Dokumen
> ini `012` agar tak menimpa file yang sudah ada. Renumber disarankan terpisah.

---

## 0. TL;DR

Mengganti backbone `bert-base-uncased` (Inggris) dengan **IndoBERT**
(`indobenchmark/indobert-base-p1`, uncased) agar pipeline ACOS menangkap
morfologi & kosakata Bahasa Indonesia. **Secara mekanis kompatibel** (keduanya
BERT-base 12/768/12/512, WordPiece). Yang berubah: **vocab + bobot pretrained +
taksonomi label**. Tapi ada **satu blocker non-teknis**: dataset quadruple
Bahasa Indonesia belum ada. Tanpa data itu, model tidak bisa dilatih.

---

## 1. Kenapa IndoBERT & Fakta Arsitektur (terverifikasi)

| Atribut | `bert-base-uncased` (sekarang) | `indobert-base-p1` (target) |
|---|---|---|
| Arsitektur | BERT-base (12 layer, 768 hidden, 12 head) | **BERT-base** (12/768/12) |
| Max posisi | 512 | 512 |
| Cased/uncased | uncased | **uncased** (phase1) |
| Tokenizer | WordPiece (BertTokenizer) | WordPiece (BertTokenizer, vocab ID) |
| Dimensi head | 768 hidden | 768 hidden (sama) |
| Bahasa pretrain | Inggris | Indonesia (Indo4B, ~23 GB teks) |

**Verdict mekanis:** dimensi identik → arsitektur kompatibel. Tidak perlu ubah
jumlah layer/head/dim encoder. Yang berubah: vocab, bobot, taksonomi label.

---

## 2. Verifikasi Hardcode di `modeling.py` (sudah dicek)

Dua task-head memakai `768` literal — **tetap aman** karena IndoBERT-base = 768,
tapi sebaiknya di-robotisasi jadi `config.hidden_size`:

| Baris | Kode | Catatan |
|-------|------|---------|
| 1545 | `nn.Linear(768, self.crf_num)` | ganti → `config.hidden_size` |
| 1608 | `nn.Linear(768*2, num_labels)` | ganti → `config.hidden_size*2` |
| 1268 | `config.hidden_size*2` (BertForSeqCls) | sudah config-driven ✓ |
| 283–311 | `BertEmbeddings` | config-driven ✓ |
| 1541 | `CRF(6, batch_first=True)` | independen bahasa ✓ |

**Loader note:** `modeling.py` memakai `pytorch_pretrained_bert` (legacy).
Syarat memuat IndoBERT lewat loader ini: file lokal `config.json` +
`pytorch_model.bin` + `vocab.txt` dan `state_dict` memakai **standard BERT
naming** (`bert.embeddings.*`, `bert.encoder.*`). Bila tidak cocok → naik ke
port `transformers` (Strategi B).

---

## 3. Blok Penentu (urutan keputusan)

### Blok 1 — DATASET QUADRUPLE INDONESIA (BLOKER UTAMA, non-teknis)
Belum ada dataset ACOS (quadruple) Bahasa Indonesia yang dipublikasi. Tanpa
anotasi `(aspect, category, opinion, sentiment)` termasuk **implicit**, IndoBERT
tidak bisa dilatih/dievaluasi.

**Keputusan yang harus diambil (drag user):**
1. **Domain:** restoran? e-commerce? umum?
2. **Sumber data:** Google Maps ID, Tokopedia, GoFood, Twitter?
3. **Pedoman anotasi** yang menangani aspek/opini **implisit** versi Indonesia
   (bahasa yang afiksatif — ambiguitas tinggi).
4. **Rute anotasi:**
   - Anotasi baru penuh (paling mahal).
   - Perluas dataset ABSA Indonesia existing → quadruple.
   - **Bonus (dari laporan NusaX):** pakai `indonlp/NusaX-senti` untuk
     sentimen gratis (label positive/neutral/negative), lalu anotasi hanya
     aspek+kategori+opini. Atau proyeksi lintas-bahasa via aligned NusaX.

### Blok 2 — Porting kode (lihat §4, dua strategi)
### Blok 3 — Tokenizer + regenerasi data (§5)
### Blok 4 — Taksonomi kategori Indonesia (§6)
### Blok 5 — Fix bug Step 2 dulu (§7)

---

## 4. Dua Strategi Migrasi

### Strategi A — Light Swap (minimal, tanpa port kode)
```
indobert_base_uncased/
├── config.json        # config arsitektur (768)
├── pytorch_model.bin  # bobot IndoBERT
└── vocab.txt          # vocab WordPiece Indonesia
```
1. Unduh 3 file di atas (bisa lewat `download_bert_pretrained` diarahkan ke
   IndoBERT, atau manual).
2. Arahkan `bert_model_dir` / `BERT_BASE_DIR` ke folder itu (bukan `bert_base_uncased/`).
3. `bert_utils/tokenization.py` memuat `vocab.txt` IndoBERT (API-nya sudah cocok —
   WordPiece generic).
4. Loader legacy `from_pretrained` memuat state_dict.
- **Kelebihan:** cepat, tidak ubah `modeling.py` kecuali 2 hardcode 768.
- **Risiko:** loader legacy mungkin tak cocokkan key state_dict IndoBERT → perlu
  uji tunggal (load lalu bandingkan jumlah param termuat).
- **Cara uji cepat:** `m = BertForQuadABSA.from_pretrained("indobert_base_uncased",
  num_labels=6.order)` → cek tidak ada error `missing_keys` besar / size mismatch.

### Strategi B — Full Port ke `transformers` (robust)
1. Ganti base class `BertPreTrainedModel`/`BertModel` legacy → `transformers`.
2. `BertForQuadABSA`/`CategorySentiClassification` struktur sama, tapi
   `super().__init__(config)` ke `transformers.BertPreTrainedModel`.
3. Muat `AutoModel.from_pretrained("indobenchmark/indobert-base-p1")`.
4. Ganti `bert_utils/tokenization.py` → `transformers.AutoTokenizer` (IndoBERT).
- **Kelebihan:** kompatibel masa depan; mudah ganti ke NusaBERT / RoBERTa-ID.
- **Risiko:** perubahan lebih besar; butuh uji ulang penuh.

**Rekomendasi:** mulai **A** untuk validasi cepat, naik ke **B** jika loader
legacy gagal. Keduanya tetap butuh Blok 1 & 4.

---

## 5. Tokenizer & Regenerasi Data (wajib)

`tokenized_data/*.tsv` sekarang ter-WordPiece vocab **English** → **wajib
di-generate ulang dengan vocab IndoBERT** (offset `a_st`/`a_ed` mengacu indeks
**subword IndoBERT**, yang berbeda dari English).

Alur regenerasi:
```
(Data quad ID: text \t aspect-span category sentiment opinion-span)
   │ (contoh: "Makanannya enak \t 0,1 MAKANAN#RASA 2 2,2")
   ▼
tokenizer_indo = load vocab IndoBERT
   ▼
bangun aspect_labels (B-A/I-A/B-O/I-O) & flag implicit → convert_examples_to_features
   ▼
tulis tokenized_data/{domain}_{train,dev,test}_quad_bert.tsv
```
Format quad/pair **tidak berubah** (`text \t start,end CATEGORY#ASPECT sentiment
start,end`). Hanya nilai offset yang beda.

---

## 6. Taksonomi Kategori Indonesia (ganti hardcode)

File: `run_classifier_dataset_utils.py:235` (rest16) & `:241-259` (laptop).
Ganti list `RESTAURANT#...` / `LAPTOP#...` dengan taksonomi domain ID.
Jumlah output Step 2 = `|kategori| × 3`.

Contoh taksonomi restoran Indonesia:
```
MAKANAN#KUALITAS, MAKANAN#RASA, MAKANAN#HARGA, MAKANAN#PORS
PELAYANAN#KECEPATAN, PELAYANAN#KERAMAHAN
MINUMAN#KUALITAS, MINUMAN#HARGA
SUASANA#GENERAL, LOKASI#GENERAL, HARGA#GENERAL
    (tiap kategori ⇒ ×3 sentimen pos/neu/neg)
```
> Ini placeholder — final ditentukan di Blok 1 oleh pedoman/persebaran data.

---

## 7. Fix Bug Step 2 (PRA-SYARAT)

Notebook 00 crash `KeyError: 'a--1,-1'` (lihat `reports/007_solusi_error_keyerror_step2_...`).
Terapkan fix parser regex di `get_1st_pairs.py` / cell 12 **sebelum** validasi
port IndoBERT — kalau tidak pipeline tak bisa dijalankan end-to-end untuk
divalidasi. Tanpa ini, semua usaha di atas tak teruji.

---

## 8. Peta Perubahan per File (konsolidasi)

| File | Aksi |
|------|------|
| `run.sh` | `BERT_BASE_DIR` → `indobert_base_uncased/` (A) atau HF name (B) |
| `modeling.py` | (opsional) 2× hardcode 768 → `config.hidden_size`; (B) base class → `transformers` |
| `bert_utils/tokenization.py` | (A) vocab ID; (B) → `transformers.AutoTokenizer` |
| `colab_utils.download_bert_pretrained` | arahkan ke IndoBERT / local cache |
| `run_classifier_dataset_utils.py` | ganti list kategori hardcode → taksonomi ID |
| `data/` + `tokenized_data/*.tsv` | **regenerasi** dengan vocab IndoBERT |
| `eval_metrics.py` | tidak perlu ubah (model-agnostik) |
| `get_1st_pairs.py` | tidak perlu ubah (hanya di-harden — Blok 5) |
| notebook `00`–`05` | `DOMAIN` → ID; `bert_model_dir` → IndoBERT; fix Step 2 |

---

## 9. Roadmap Eksekusi (dengan kriteria selesai)

```
Fase 0  SCOPE
        → putuskan domain, sumber, pedoman anotasi (handle implicit ID)
        ✅ selesai bila: dokumen scope disetujui
Fase 1  DATA  [BLOKER]
        → kumpulkan + anotasi quadruple ID (memanfaatkan NusaX sentimen bila mau)
        ✅ selesai bila: train/dev/test tersusun, IAA dapat
Fase 2  PORT
        → Strategi A (fail = lanjut B)
        ✅ selesai bila: from_pretrained(IndoBERT) tanpa missing/shape error
Fase 3  PREP DATA
        → generator tokenized_data dgn vocab ID + taksonomi ID
        ✅ selesai bila: offset subword benar (spot-check few samples)
Fase 4  FIX + VALIDASI
        → fix Step 2; jalankan pipeline di subset kecil
        ✅ selesai bila: 1 epoch selesai tanpa crash, metrik keluar
Fase 5  TRAIN + EVAL
        → 2-stage pipeline IndoBERT; bandingkan vs baseline EN / cross-lingual
        ✅ selesai bila: micro-F1 tercatat, dapat dibandingkan
```

---

## 10. Pertanyaan yang Harus Di-Jawab User (blocking)

1. **Domain dataset** Indonesia apa? (ini menentukan seluruh taksonomi & anotasi)
2. **Sumber data** mana? (GoFood/Tokopedia/Google Maps/Twitter)
3. **Strategi migrasi**: A (cepat) atau B (robust)?
4. **Cakupan**: Indonesia saja, atau **Nusantara** (→ ini menggeser keputusan ke
   NusaBERT, lihat `010/011`) — IndoBERT hanya Indonesia.
5. **Target performa**: cukup dibandingkan baseline, atau kejar angka maksimal
   (maka `indobert-large-p1` 335M sebagai opsi, kalau GPU cukup)?

---

## 11. Ringkasan Verifikasi & Batası

- Dimensi & hardcode `modeling.py`, hardcode taksonomi, legacy tokenizer:
  **pembacaan statis + grep terverifikasi**.
- IndoBERT = BERT-base 768: konvensi arsitektur HF (validasi nama/vocab saat
  implementasi).
- **Dan NusaBERT (opsi):** `LazarusNLP/NusaBERT-base` = IndoBERT p1 +
  continued-pretrain Nusantara (12+ bahasa). Untuk Indonesia-saja, keduanya
  berdekatan; NusaBERT menang di bahasa daerah. (Detail: `010_survey` & `011`.)
- Tidak ada eksekusi/download dalam sesi ini. Statement performa = ekspektasi
  analitis, bukan ukur.

---

**Bottom line:** Untuk IndoBERT, siapkan 2 hal wajib duluan — **(1) dataset
quadruple Bahasa Indonesia** (belum ada, non-teknis) dan **(2) mekanisme memuat
IndoBERT** (Strategi A/B). Setelah itu regenerasi data + taksonomi + fix Step 2
bisa dieksekusi bertahap per roadmaps di atas.
