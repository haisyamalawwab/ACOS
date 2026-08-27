# Survey, Pemetaan & Analisis: Implementasi ACOS-ASLI dengan NusaBERT + NusaX

Tanggal: 2026-08-27 17:22
Tujuan: survey resource NusaBERT & NusaX, petakan ke pipeline ACOS, analisis
kedalaman, dan susun persiapan implementasi.
Metode: fakta diambil dari kartu HuggingFace (`indonlp/NusaX-senti`,
`LazarusNLP/NusaBERT-base`) + pembacaan statis repo ACOS-ASLI
(`modeling.py`, `run.sh`, `run_classifier_dataset_utils.py`).

---

## 1. TL;DR (temuan sentral)

- **NusaBERT-base** = encoder BERT pengganti `bert-base-uncased`. Bisa dipasang
  setelah kode di-port ke `transformers`. ✅
- **NusaX-senti** = dataset **klasifikasi sentimen 3-kelas** (pos/neu/neg) untuk
  Indonesia + ~12 bahasa daerah. **TIDAK punya anotasi quadruple** (aspek, opini,
  kategori). ❌
- Konsekuensi: NusaX **tidak bisa langsung melatih model ACOS**. Ia hanya
  menyumbang **dimensi sentimen** + **cakupan bahasa**. Untuk ACOS tetap
  diperlukan anotasi quadruple (aspek + kategori + opini); sentimennya bisa
  diambil gratis dari NusaX.

Jadi "implementasi dengan NusaBERT + NusaX" = (a) ganti backbone ke NusaBERT,
(b) **bangun dataset quadruple di atas NusaX** (sentimen sudah ada), (c) sesuaikan
pipeline. Ini bukan swap model, melainkan proyek anotasi + porting.

---

## 2. Hasil Survey (fakta terverifikasi)

### 2.1 NusaX-senti
- ID: `indonlp/NusaX-senti`
- Tugas: text classification → sentiment-classification (3 kelas: positive,
  neutral, negative)
- Bahasa: Indonesia + ~12 bahasa daerah (Acehnese, Balinese, Banjarese, Buginese,
  Madurese, Minangkabau, Javanese, Ngaju, Sundanese, Toba Batak; kartu HF juga
  mencantumkan English)
- Jumlah: ~12.000 baris
- Lisensi: **cc-by-sa-4.0** (share-alike)
- **Tidak ada anotasi aspek/opini/kategori (quadruple).**

### 2.2 NusaBERT-base
- ID: `LazarusNLP/NusaBERT-base`
- Arsitektur: **BERT base** (turunan `indobert-base-p1`), encoder-based, usable
  via `AutoModelForMaskedLM` / `BertModel`
- Bahasa: Indonesia + Acehnese, Balinese, Banjarese, Buginese, Gorontalo, Javanese,
  Banyumasan, Minangkabau, Malay, Nias, Sundanese, Tetum
- Korpus pretrain: IndoWiki + KoPI-NLLB + CulturaX (~16B token)
- Lisensi: **Apache 2.0**
- Cased/uncased tidak dinyatakan di kartu; karena turunan IndoBERT p1 (uncased),
  kemungkinan **uncased** (`do_lower_case=True`) — verifikasi saat load.
- Tidak ada varian large yang disebut.

### 2.3 Catatan cakupan bahasa (gap)
Daftar bahasa NusaX dan NusaBERT **tidak identik**:
- Hanya di NusaX: Madurese, Ngaju, Toba Batak, English
- Hanya di NusaBERT: Gorontalo, Banyumasan, Malay, Nias, Tetum
- Irisan: Indonesia, Acehnese, Balinese, Banjarese, Buginese, Javanese,
  Minangkabau, Sundanese

Implikasi: untuk bahasa NusaX yang tidak dilatih di NusaBERT (mis. Madurese,
Toba Batak), encoder tidak pernah melihat bahasa itu saat pretrain → andalkan
transfer lintas-bahasa (bahasa serumah). Ini risiko kualitas per bahasa.

---

## 3. Pemetaan (ACOS ↔ NusaBERT / NusaX)

| Komponen ACOS | NusaBERT | NusaX | Status / Gap |
|---|---|---|---|
| Encoder BERT (`BertForQuadABSA`) | ✅ ganti `bert-base-uncased` | — | Perlu port ke `transformers` |
| Tokenizer WordPiece + `tokenized_data` | ✅ tokenizer NusaBERT | — | Regenerasi offset subword |
| Sentimen (elemen ke-4 quadruple) | — | ✅ pos/neu/neg | Cocok; map label `0/1/2` |
| Aspect span (eksplisit) | — | ❌ | Perlu anotasi |
| Opinion span (eksplisit) | — | ❌ | Perlu anotasi |
| Aspect category | — | ❌ | Perlu taksonomi + anotasi |
| Implicit aspect / opinion | — | ❌ | Perlu anotasi (paling sulit) |
| Cakupan bahasa Nusantara | ✅ 12+ | ✅ 12 (sebagian beda) | Tidak identik (lihat 2.3) |
| Evaluasi metrik (measureQuad) | — | — | Tetap pakai `eval_metrics.py` |

**Kesimpulan pemetaan:** NusaBERT menutupi sisi *encoder*, NusaX menutupi sisi
*sentimen + bahasa*. Dua elemen quadruple (aspect, opinion, category) tetap kosong
tanpa anotasi baru.

---

## 4. Analisis Mendalam

### 4.1 Mismatch fundamental: NusaX ≠ ACOS
ACOS mengekstrak **quadruple** `(aspek, kategori, opini, sentimen)`. NusaX hanya
memberi **sentimen level kalimat**. Tiga dari empat elemen (aspek, kategori,
opini) tidak ada di NusaX. Memaksa NusaX ke ACOS tanpa anotasi = metrik akan
kosong/riam. Ini adalah blocker #1 (sama seperti IndoBERT, tapi NusaX minimal
memberi sentimen gratis).

### 4.2 Peluang efisiensi dari NusaX
Karena NusaX sudah berlabel sentimen, anotasi quadruple di atas NusaX hanya perlu
menambah: (1) span aspek, (2) kategori, (3) span opini. Sentimen sudah ada.
Lebih jauh: NusaX adalah **parallel** (kalimat setara lintas bahasa) → anotasi
quadruple bisa dibuat di Indonesia lalu **diproyeksikan** ke bahasa daerah via
alignmen paralel (cross-lingual annotation projection). Ini pangkas biaya anotasi
lokal secara drastis.

### 4.3 Feasibilitas substitusi encoder
NusaBERT-base adalah BERT base standar (hidden 768). `BertForQuadABSA` &
`CategorySentiClassification` di `modeling.py` memakai `BertModel` + CRF + head.
Setelah `modeling.py` di-port dari `pytorch_pretrained_bert` ke `transformers`,
NusaBERT-base dapat dimuat via `from_pretrained("LazarusNLP/NusaBERT-base")`.
CRF & head di-init ulang; encoder di-freeze-train (fine-tune). **Tidak ada
perubahan arsitektur**, hanya checkpoint + tokenizer.

### 4.4 Implicit aspect/opinion (tantangan terbesar)
Skema ACOS menangani aspek/opini implisit (`-1,-1`). Menganotasi implisit dalam
bahasa daerah butuh pedoman bilingual yang ketat + IAA. NusaX tidak membantu di
sisi ini. Ini bagian tersulit dari anotasi.

### 4.5 Lisensi
- NusaBERT: Apache 2.0 → bebas untuk riset & turunan.
- NusaX: cc-by-sa-4.0 → turunan harus dibagikan dgn lisensi sama (share-alike).
  Catat saat merilis dataset ACOS-Nusantara hasil anotasi di atas NusaX.

---

## 5. Persiapan Implementasi (bertahap)

- **Fase 0 — Scope.** Pilih bahasa & domain. Rekomendasi: Indonesia dulu
  (restoran/e-commerce), lalu perluas ke daerah via parallel NusaX. Tentukan
  taksonomi kategori Indonesia/Nusantara.
- **Fase 1 — Data (blocker).** Ambil teks NusaX (Indonesia), anotasi quadruple
  `(aspek, kategori, opini, sentimen)`. Sentimen ambil dari label NusaX. Untuk
  bahasa daerah: anotasi Indonesia lalu proyeksi paralel, atau anotasi langsung.
- **Fase 2 — Port kode.** `modeling.py` + `bert_utils/tokenization.py` →
  `transformers`. Muat `LazarusNLP/NusaBERT-base`. (Lihat `reports/008_...`
  untuk pola porting serupa IndoBERT.)
- **Fase 3 — Prep data.** Generator `tokenized_data` dengan NusaBERT tokenizer;
  span = indeks subword NusaBERT. Format `text \t start,end CATEGORY#ASPECT
  sentiment start,end` tetap.
- **Fase 4 — Taksonomi.** Ganti list hardcode rest16/laptop
  (`run_classifier_dataset_utils.py:235,241`) dengan kategori domain ID.
- **Fase 5 — Fix Step 2 (wajib).** Terapkan fix `KeyError: 'a--1,-1'` di
  `reports/007_solusi_error_keyerror_step2_acos_27082026_1554.md` sebelum
  mengandalkan pipeline.
- **Fase 6 — Train/eval.** 2-stage pipeline; bisa per-bahasa (`DOMAIN` = kode
  bahasa) atau multilingual tunggal. Ukur vs baseline.
- **Fase 7 — Cross-lingual.** Manfaatkan parallel NusaX untuk proyeksi anotasi
  ke bahasa daerah.

## 6. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| NusaX tanpa quadruple → tak bisa train ACOS langsung | Anotasi di atas NusaX; sentimen gratis |
| Cakupan bahasa NusaX ≠ NusaBERT | Pakai bahasa irisan dulu; sisanya via transfer lintas-bahasa |
| Legacy `pytorch_pretrained_bert` tak punya NusaBERT | Port ke `transformers` (Fase 2) |
| Step 2 crash (`KeyError`) | Fix parser regex (Fase 5) |
| Anotasi implisit sulit di daerah | Pedoman ketat + IAA; mulai dari eksplisit dulu |
| Lisensi cc-by-sa NusaX | Bagikan turunan dgn lisensi sama |

---

## 7. Batas Verifikasi

- Fakta NusaX & NusaBERT dari kartu HuggingFace (di-fetch 2026-08-27). Paper NusaX
  (Wariboko et al., EMNLP 2022 Findings) tidak di-fetch langsung; rujukan berdasar
  kartu dataset.
- Cased/uncased NusaBERT tidak dinyatakan eksplisit di kartu; diasumsikan uncased
  (turunan IndoBERT p1) — verifikasi saat `from_pretrained`.
- Belum ada eksekusi/implementasi; ini murni survey + rencana.
- File pendukung: `004` (analisis kritis repo), `007` (fix KeyError Step 2),
  `008` (rencana IndoBERT), `009` (lokasi embedding/fine-tuning).
