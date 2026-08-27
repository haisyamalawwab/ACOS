# Konsep & Rencana Adaptasi ACOS-ASLI ke IndoBERT (Konsolidasi + Verifikasi Lanjut)

Tanggal: 2026-08-27 17:20
Latar: lanjutan dari `reports/008_persiapan_rencana_indobert_...` dan
`reports/009_lokasi_fase_embedding_finetuning_...` (dibuat di sesi paralel,
belum di-commit). Dokumen ini menyatukan temuan tersebut, **menambahkan
verifikasi mekanis** pada `modeling.py`, dan menyajikan dua strategi migrasi
serta peta perubahan per file. Berbasis pembacaan statis; tidak ada eksekusi.

---

## 0. Status Penomoran (perlu dibersihkan)

Ditemukan tabrakan nomor di `reports/`:
- Dua file nomor `007`: `007_dokumentasi_metode_per_file_py_...` dan `007_solusi_error_keyerror_...`
- Dua file nomor `008`: `008_gambaran_konsep_repo_...` dan `008_persiapan_rencana_indobert_...`

Rekomendasi (di luar scope saat ini): jalankan renumber satu kali agar
urutan kronologis tidak ambigu. Laporan ini pakai `010` agar tidak menimpa
`008`/`009` yang sudah ada.

---

## 1. Konsep Target: Apa Itu IndoBERT di Sini

IndoBERT = checkpoint BERT yang **di-pretrain di korpus Bahasa Indonesia**
(bukan Inggris). Tujuannya menggantikan `bert-base-uncased` (Inggris) sebagai
titik awal *fine-tuning* pipeline ACOS, sehingga model menangkap morfologi &
kosakata Indonesia (afiks `me-, ber-, -nya, -kan`, dll.).

**Fakta arsitektur yang menentukan (umum & terverifikasi dari dimensi repo):**
- `indobenchmark/indobert-base-p1` adalah arsitektur **BERT-base**: 12 layer,
  768 hidden, 12 head, 512 posisi, **uncased**, WordPiece.
- `bert-base-uncased` juga 12/768/12/512, uncased, WordPiece.
- **Kesimpulan**: dimensi identik → arsitektur *mekanis kompatibel*. Tidak
  perlu ubah jumlah layer/head/dim encoder. Yang berubah: **vocab** (IDA
  vs ENG), **bobot pretrained**, dan **taksonomi label** (Step 2).

---

## 2. Verifikasi Mekanis pada `modeling.py` (BARU dari audit ini)

Saya cek apakah head task bergantung hardcode dimensi:

| Baris | Kode | Implikasi untuk IndoBERT |
|-------|------|--------------------------|
| 1545 | `nn.Linear(768, self.crf_num)` (`dense_output`) | **Hardcode 768** — aman karena IndoBERT-base = 768; sebaiknya `config.hidden_size` |
| 1608 | `nn.Linear(768*2, num_labels)` (`classifier`) | **Hardcode 768** — sama; ganti `config.hidden_size*2` |
| 1268 | `nn.Linear(config.hidden_size*2, num_labels)` (`BertForSequenceClassification`) | Sudah config-driven ✓ |
| 283-311 | `BertEmbeddings` | config-driven ✓ |
| 1541 | `CRF(self.crf_num=6, batch_first=True)` | tidak bergantung dim Bahasa |

**Verdict**: IndoBERT-base (768) bisa langsung dipakai tanpa ubah `modeling.py`,
asal checkpoint dimuat. Untuk robustness, ubah 2 hardcode `768` → `config.hidden_size`.

**Catatan loader**: `modeling.py` memakai `pytorch_pretrained_bert` (legacy,
pre-`transformers`). `BertPreTrainedModel.from_pretrained` memakai `cached_path`
+ `torch.load(state_dict)` lalu `load_from_state_dict`. Selama IndoBERT
dirilis dengan *standard BERT weight naming* (`bert.embeddings.*`,
`bert.encoder.*`, `bert.pooler.*`), state_dict bisa dimuat ke `BertModel`
kita **tanpa port ke transformers** — asal diberi direktori lokal berisi
`config.json` + `pytorch_model.bin` + `vocab.txt`.

---

## 3. DUA Strategi Migrasi (nilai tambah vs laporan 008)

### Strategi A — Light Swap (minimal, tanpa port kode)
- Unduh IndoBERT (`config.json`, `pytorch_model.bin`, `vocab.txt`) → folder lokal
  (`indobert_base_uncased/`).
- Arahkan `bert_model_dir` / `BERT_BASE_DIR` ke folder itu.
- Pakai `bert_utils/tokenization.py` (legacy) dengan `vocab.txt` IndoBERT.
- Loader legacy memuat state_dict; head task di-init ulang (CRF, classifier).
- **Syarat**: legacy loader bisa cocokkan key state_dict IndoBERT.
- **Kelebihan**: cepat, tidak ubah `modeling.py` (kecuali 2 hardcode 768).
- **Risiko**: legacy loader tidak handle format HF modern; perlu uji load.

### Strategi B — Full Port ke `transformers` (robust, lebih kerja)
- Ganti base class `BertPreTrainedModel`/`BertModel` legacy → `transformers`.
- `BertForQuadABSA`/`CategorySentiClassification` tetap sama, tapi `super()`
  ke `transformers.BertPreTrainedModel`; muat `from_pretrained("indobenchmark/indobert-base-p1")`.
- Ganti `bert_utils/tokenization.py` → `transformers.BertTokenizer(IndoBERT)`.
- **Kelebihan**: kompatibel masa depan, mudah swap model (RoBERTa-ID bila perlu).
- **Risiko**: perubahan mekanis lebih besar; butuh uji ulang.

**Rekomendasi**: mulai **Strategi A** untuk validasi cepat; bila legacy loader
gagal cocokkan key, naik ke **Strategi B**. Keduanya tetap butuh dataset & taksonomi ID (Blok 1).

---

## 4. Peta Perubahan per File

| File | Perubahan untuk IndoBERT |
|------|--------------------------|
| `run.sh` | `BERT_BASE_DIR` → path IndoBERT lokal (Strategi A) atau nama HF (B) |
| `modeling.py` | (opsional) `768` → `config.hidden_size` di 1545 & 1608; (B) base class → `transformers` |
| `bert_utils/tokenization.py` | (A) pakai `vocab.txt` IndoBERT; (B) ganti `transformers.BertTokenizer` |
| `colab_utils.download_bert_pretrained` | arahkan ke IndoBERT HF / local cache |
| `run_classifier_dataset_utils.py` | **ganti list kategori hardcode** rest16(13)/laptop(121) → taksonomi ID |
| `data/` + `tokenized_data/` | **regenerasi** dengan vocab IndoBERT (offset WordPiece berubah) |
| `eval_metrics.py` | tidak perlu ubah (model-agnostik) |
| `get_1st_pairs.py` | tidak perlu ubah (hanya di-harden, lihat Blok 5) |
| notebook `00`–`05` | `DOMAIN` → domain ID; `bert_model_dir` → IndoBERT; perbaiki bug Step 2 |

---

## 5. Blok Penentu (dari laporan 008, dipertahankan)

### Blok 1 — DATASET QUADRUPLE INDONESIA (BLOKER UTAMA)
Tidak ada dataset ACOS (quadruple) Bahasa Indonesia yang dipublikasi. Tanpa
data beranotasi `(aspect, category, opinion, sentiment)` — termasuk implisit —
IndoBERT **tidak bisa dilatih**. Ini pekerjaan anotasi, bukan teknis.

Opsi (butuh diputuskan):
- Anotasi baru dari review ID (GoFood, Tokopedia, Google Maps).
- Perluas dataset ABSA Indonesia existing ke format quadruple (perluas, bukan
  pakai langsung).
- Bootstrap LLM lalu validasi manusia (perlu audit IAA).

### Blok 2 — Porting kode
Lihat Strategi A/B §3.

### Blok 3 — Tokenizer & regenerasi data
`tokenized_data/*.tsv` sekarang ter-WordPiece pakai vocab ENG → **wajib generate
ulang** dengan vocab IndoBERT. Format quad/pair tetap; offset mengacu subword ID.

### Blok 4 — Taksonomi kategori Indonesia
Ganti hardcode `RESTAURANT#...`/`LAPTOP#...` dengan kategori domain ID
(mis. `RESTORAN#MAKANAN`, `RESTORAN#PELAYANAN`, `PRODUK#HARGA`).
Ukuran layer Step 2 = `|kategori| × 3`.

### Blok 5 — Fix bug Step 2 dulu
Notebook 00 crash `KeyError: 'a--1,-1'` (lihat `007_solusi_error_keyerror_...`).
Terapkan fix parser sebelum validasi port IndoBERT — kalau tidak, pipeline
tidak bisa dijalankan end-to-end untuk divalidasi.

---

## 6. Roadmap Bertahap

```
Fase 0  SCOPE        → domain ID, sumber data, pedoman anotasi (tangani implisit ID)
Fase 1  DATA         → kumpulkan + anotasi quadruple ID            [BLOKER]
Fase 2  PORT         → Strategi A (light) / B (transformers)       [BLOKER teknis]
Fase 3  PREP DATA    → generator tokenized_data dgn vocab IndoBERT + taksonomi ID
Fase 4  FIX+VALIDASI → terapkan fix Step 2, jalankan end-to-end di domain kecil
Fase 5  TRAIN+EVAL   → 2-stage pipeline IndoBERT; ukur vs baseline (EN / zero-shot?)
```

---

## 7. Catatan Konseptual Penting

- **Embedding bukan "tahap" terpisah**: layer `BertEmbeddings` jalan tiap
  `forward` & di-update saat fine-tuning; tokenizer WordPiece **tetap fix**.
  (Detail: laporan 009.)
- **Step 1 & Step 2 berangkat dari checkpoint base yang SAMA** (IndoBERT),
  bukan berantai — desain pipeline co-extraction → classification.
- **IndoBERT varian RoBERTa** (`w11wo/indonesian-roberta-base`) hindari kecuali
  perlu: beda arsitektur (no `token_type_ids`, casing berbeda) → butuh ubah
  class model + penanganan input. Pilih varian BERT untuk kemudahan mekanis.
- Bahasa Indonesia afiksatif: aspek/opini kaya morfologi; anotasi & evaluasi
  harus konsisten (WordPiece tetap bisa asal seragam).

---

## 8. Batas Verifikasi

- Dimensi `modeling.py` (hardcode 768 di 1545/1608) & config-driven di tempat
  lain: dari pembacaan statis + grep.
- Klaim "IndoBERT-base = BERT-base 768" merujuk konvensi arsitektur HF umum;
  validasi pasti (nama checkpoint, ukuran vocab) dilakukan saat implementasi
  (Fase 2).
- Tidak ada eksekusi pipeline; tidak ada download IndoBERT dalam sesi ini.
- Strategi A bergantung legacy loader bisa cocokkan key state_dict IndoBERT —
  perlu uji saat Fase 2.
