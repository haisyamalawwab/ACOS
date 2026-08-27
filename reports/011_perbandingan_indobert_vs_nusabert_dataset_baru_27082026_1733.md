# Perbandingan: Implementasi ACOS pada IndoBERT vs NusaBERT (dengan Dataset Baru)

Tanggal: 2026-08-27 17:33
Skenario: membangun **dataset quadruple baru** (Indonesia / Nusantara) lalu
melatih pipeline ACOS dengan encoder IndoBERT atau NusaBERT. Membandingkan
kedua pilihan backbone.
Metode: fakta dari kartu HuggingFace (`indobenchmark/indobert-base-p1`,
`LazarusNLP/NusaBERT-base`) + analisis pipeline ACOS-ASLI.

---

## 1. Fakta Terverifikasi (setara untuk dua model)

| Atribut | IndoBERT-base-p1 | NusaBERT-base |
|---|---|---|
| ID HF | `indobenchmark/indobert-base-p1` | `LazarusNLP/NusaBERT-base` |
| Arsitektur | BERT base (124.5M) | BERT base (turunan **IndoBERT p1**) |
| Cased/uncased | **uncased** (phase1) | kemungkinan uncased (turunan p1) |
| Bahasa pretrain | **Indonesia saja** (Indo4B, 23.43 GB teks) | Indonesia + 12+ daerah (~16B token: IndoWiki+KoPI-NLLB+CulturaX) |
| Tokenizer | BertTokenizer (WordPiece) | BertTokenizer (inherit IndoBERT p1) |
| Lisensi | **MIT** | **Apache 2.0** |
| Varian besar | ✅ `indobert-large-p1` (335.2M) | ❌ hanya base (belum ada large) |
| Encoder `transformers` | ✅ AutoModel | ✅ AutoModel |

**Insight kunci:** NusaBERT-base adalah **IndoBERT-base-p1 yang dilanjutkan
pretrain-nya** pada korpus Nusantara. Secara pretrain, NusaBERT = *superset*
IndoBERT p1 (memiliki kekuatan Indonesia p1 + ekspos bahasa daerah).

---

## 2. Pemetaan ke Pipeline ACOS (sama untuk keduanya)

Terlepas dari pilihan encoder, dengan dataset baru berlaku hal yang sama:
- `modeling.py` harus di-port `pytorch_pretrained_bert` → `transformers`.
- `tokenized_data` di-regenerasi dengan tokenizer masing-masing; span = indeks
  subword.
- Anotasi quadruple (aspek+kategori+opini+sentimen) tetap harus dibuat (NusaX
  hanya gratiskan sentimen).
- Taksonomi kategori Indonesia/Nusantara mengganti list hardcode.
- Fix Step 2 (`KeyError: 'a--1,-1'`) wajib diterapkan.
- Evaluasi pakai `eval_metrics.py` (measureQuad/pair_eval).

Jadi **effort persiapan identik**; perbedaan murni di kualitas representasi encoder
& cakupan bahasa.

---

## 3. Perbandingan per Dimensi

| # | Dimensi | IndoBERT | NusaBERT | Verdict |
|---|---|---|---|---|
| 1 | Garis keturunan | Indonesia monolingual base | IndoBERT p1 + continued Nusantara | NusaBERT (superset) |
| 2 | Kapasitas arsitektur | base + **large (335M)** | hanya base | IndoBERT (jika butuh besar) |
| 3 | Korpus pretrain | Indo4B ~23 GB teks ID | ~16B token multilingual | NusaBERT (lebih banyak token) |
| 4 | Cakupan bahasa | Indonesia saja | ID + 12+ daerah | NusaBERT (jika ada daerah) |
| 5 | Tokenizer Indonesia | WordPiece ID | **sama** (inherit p1) | Seri (token ID identik) |
| 6 | Lisensi | MIT | Apache 2.0 | Seri (keduanya permisif) |
| 7 | Kematangan/benchmark | mapan (banyak literatur) | lebih baru | IndoBERT (comparability) |
| 8 | Compute (base) | sama | sama | Seri |
| 9 | Effort porting kode | sama | sama | Seri |

### Penjelasan poin kritis
- **#5 Tokenizer**: karena NusaBERT diturunkan dari IndoBERT p1, ia mewarisi
  tokenizer/vocab p1. Untuk teks **Indonesia**, tokenisasi (dan oleh karena itu
  `tokenized_data`) **identik** antara kedua model — hanya bobot embedding yang
  berbeda. Keunggulan tokenizer NusaBERT baru muncul pada teks **bahasa daerah**.
- **#3 vs #4**: IndoBERT pretrain murni Indonesia (fokus penuh); NusaBERT pretrain
  multilingual yang jauh lebih besar. Untuk representasi Indonesia, NusaBERT
  kemungkinan ≥ IndoBERT (korpus lebih besar & tetap berisi Indonesia); untuk
  daerah, NusaBERT menang telak karena IndoBERT tidak pernah melihat bahasa daerah.

---

## 4. Performa Ekspektasi (dataset baru)

### 4.1 Dataset baru = Indonesia saja
- IndoBERT p1 vs NusaBERT base: **sangat berdekatan**; NusaBERT bisa sedikit di
  atas (pretrain lebih besar) tanpa pengenceran Indonesia yang berarti.
- `indobert-large-p1` (335M) kemungkinan mengalahkan keduanya **jika compute
  cukup** (kapasitas 2.7×). Ini opsi yang tidak dimiliki NusaBERT (base only).

### 4.2 Dataset baru = Nusantara (Indonesia + daerah)
- **NusaBERT menang jelas** pada bahasa daerah (transfer dari bahasa yang sudah
  dilihat saat pretrain). IndoBERT butuh penanganan khusus / tidak punya representasi.
- Di subset Indonesia, keduanya setara (lihat 4.1).

### 4.3 Catatan
Keduanya **start dari checkpoint pretrained lalu fine-tune** pada quadrupe baru,
jadi jarak performa ditentukan terutama oleh relevansi pretrain + kapasitas, bukan
oleh perbedaan arsitektur (keduanya BERT base).

---

## 5. Rekomendasi / Keputusan

**Gunakan IndoBERT bila:**
- Dataset baru **murni Indonesia** DAN Anda butuh baseline sejalan literatur
  (IndoBERT adalah standar benchmark Indonesia → mudah dibandingkan ke paper).
- Butuh **kapasitas ekstra** → `indobert-large-p1` (NusaBERT tidak punya large).
- Lisensi **MIT** lebih disukai.

**Gunakan NusaBERT bila:**
- Dataset baru **Nusantara** (Indonesia + daerah) atau rencana perluas ke daerah.
- Ingin **satu model** untuk semua bahasa tanpa pipeline per-bahasa terpisah.
- Aman secara representasi: tidak "kehilangan" kekuatan Indonesia karena NusaBERT
  adalah superset IndoBERT p1.

**Pragmatis (default):** untuk cakupan Nusantara, **NusaBERT-base adalah pilihan
aman** (gratis secara arsitektur, menang di daerah, setara di Indonesia). Untuk
tugas Indonesia-saja yang mengejar angka maksimal & comparability, **IndoBERT-large**
adalah opsi terkuat.

---

## 6. Risiko per Pilihan

| Pilihan | Risiko | Mitigasi |
|---|---|---|
| IndoBERT (ID-only) | tak bisa langsung ke daerah | pakai NusaBERT bila perluas |
| IndoBERT-large | VRAM/waktu 2.7× | pastikan GPU cukup |
| NusaBERT | lebih baru, kurang benchmark downstream | validasi dengan dev set; bandingkan ke IndoBERT |
| Keduanya | legacy `pytorch_pretrained_bert` belum di-port | Fase porting (lihat 002/008) |
| Keduanya | Step 2 crash KeyError | fix (lihat 007) |

---

## 7. Batas Verifikasi

- IndoBERT p1 & NusaBERT base: fakta dari kartu HF (di-fetch 2026-08-27).
- "NusaBERT = IndoBERT p1 continued-pretrain" per kartu NusaBERT ("fine-tuned
  from IndoBERT base p1").
- Perkiraan performa bersifat **ekspektasi analitis**, bukan hasil ukur (belum ada
  training). Perlu eksperimen A/B nyata (IndoBERT p1 vs NusaBERT base vs
  IndoBERT-large) pada dataset baru untuk konfirmasi.
- File terkait: `007` (fix Step 2), `008` (rencana IndoBERT), `009` (embedding/
  fine-tuning), `010` (survey NusaBERT+NusaX).
