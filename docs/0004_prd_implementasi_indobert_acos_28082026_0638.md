# PRD — Implementasi IndoBERT pada Pipeline ACOS

> Dokumen: `docs/0004_prd_implementasi_indobert_acos_28082026_0638.md`
> Tanggal: 28 Agustus 2026 · Status: **Draft untuk implementasi**
> Menggantikan rencana di `reports/008`, `009`, `010_konsep`, `010_survey`, `011`
> pada bagian-bagian yang dikoreksi di §2.

---

## 1. Tujuan & hasil yang diharapkan

Mengganti backbone pipeline ACOS 2-tahap (co-extraction → category-sentiment
classification) dari `bert-base-uncased` ke **IndoBERT**, sehingga pipeline dapat
dilatih dan dievaluasi pada data ulasan berbahasa Indonesia dengan anotasi
quadruple `(aspek, kategori, opini, sentimen)` termasuk kasus implisit.

Kriteria sukses akhir (bukan per-fase):

1. `run_step1.py` dan `run_step2.py` berjalan end-to-end dengan checkpoint
   IndoBERT tanpa error, di Colab GPU.
2. Bobot encoder IndoBERT **terbukti termuat** (bukan random init) — diverifikasi
   oleh gate wajib di §7.1.
3. `tokenized_data/` ter-regenerasi memakai vocab IndoBERT, dan span
   aspek/opini tetap konsisten setelah regenerasi (gate §7.2).
4. Step 2 tidak lagi crash `KeyError` (gate §7.3).
5. Metrik quadruple dilaporkan terpisah untuk kasus eksplisit dan implisit.

---

## 2. Temuan verifikasi yang mengoreksi rencana sebelumnya

Tiga temuan berikut saya peroleh dari pemeriksaan langsung ke kode dan ke
checkpoint di HuggingFace. Keduanya membatalkan sebagian asumsi laporan 008–011.

### 2.1 BLOKER BARU — "Strategi A light swap" akan gagal secara SENYAP

Laporan `010_konsep` §3 menyimpulkan Strategi A (cukup arahkan `--bert_model` ke
folder IndoBERT) bisa jalan "asal IndoBERT memakai standard BERT weight naming".
Saya cek penamaan key state_dict kedua checkpoint dan **asumsi itu tidak berlaku**:

| Checkpoint | Prefix key state_dict |
|---|---|
| `bert-base-uncased` | 414 key **dengan** prefix `bert.` (+ `cls.*`) |
| `indobenchmark/indobert-base-p1` | 414 key **tanpa** prefix — mulai dari `embeddings.*`, `encoder.*`, `pooler.*` |

Sekarang perhatikan loader legacy di `Extract-Classify-ACOS/modeling.py:745-747`:

```python
start_prefix = ''
if not hasattr(model, 'bert') and any(s.startswith('bert.') for s in state_dict.keys()):
    start_prefix = 'bert.'
load(model, prefix=start_prefix)
```

`BertForQuadABSA` punya atribut `self.bert` (`modeling.py:1535`), jadi
`hasattr(model, 'bert')` bernilai True dan `start_prefix` tetap `''`. Rekursi
`load()` lalu mencari key `bert.embeddings.word_embeddings.weight`. Key itu ada
di checkpoint English, tetapi **tidak ada** di checkpoint IndoBERT.

Akibatnya seluruh bobot encoder masuk ke `missing_keys` — dan tiga blok logging
yang seharusnya melaporkannya (`modeling.py:750-755`) **dalam keadaan
di-comment**. Jadi training akan berjalan mulus, tanpa error, tanpa warning,
**dengan encoder ter-inisialisasi acak**. Hasil eksperimen akan tampak "jalan"
tapi tidak ada IndoBERT di dalamnya.

Konsekuensi untuk PRD: Strategi A **tidak boleh** dipakai apa adanya. Wajib ada
lapisan re-keying state_dict + gate verifikasi numerik (§7.1).

### 2.2 Anomali vocab pada `indobert-base-p1`

| Model | `config.vocab_size` | token di `vocab.txt` | konsisten? |
|---|---|---|---|
| `indobenchmark/indobert-base-p1` | 50000 | 30521 | **tidak** (selisih 19479) |
| `indobenchmark/indobert-large-p1` | 30522 | 30521 | ya (selisih 1) |
| `LazarusNLP/NusaBERT-base` | 32032 | 30521 + 1511 `added_tokens.json` | ya (tepat) |

Ukuran `pytorch_model.bin` base-p1 (497.810.400 byte) cocok dengan hitungan
parameter untuk matriks embedding **50000×768** (124.441.344 param × 4 byte =
497.765.376, selisih 45 KB = overhead pickle). Jadi matriks 50000 baris memang
nyata; `vocab.txt` hanya mengisi id 0–30520 dan sisanya tidak pernah terpakai.

Ini tidak menyebabkan error (semua id < 50000), tetapi harus dicatat: `vocab.txt`
di ketiga repo di atas **byte-identik** (sha256 `35cfc7be…`, 229.167 byte).
NusaBERT mewarisi vocab IndoBERT, sesuai klaim laporan 011.

Catatan tambahan yang belum tercatat di laporan mana pun: `modeling.py:966` dan
`:1095` meng-hardcode `vocab_size_or_config_json_file=32000`. Keduanya hanya
dipakai di helper konversi/test, bukan di jalur `from_pretrained`, jadi
**out of scope** — tapi jangan dijadikan acuan.

### 2.3 Skrip pembuat `tokenized_data/` TIDAK ADA di repo

Laporan 008 dan 010 memerintahkan "regenerasi `tokenized_data`", seolah tinggal
menjalankan ulang generator. Saya cari generator itu dan **tidak ada**. Satu-satunya
skrip di `tokenized_data/` adalah `get_1st_pairs.py`, yang tugasnya lain
(cross-product hasil prediksi Step 1 → input Step 2).

Bukti bahwa `tokenized_data/*_quad_bert.tsv` memang hasil pra-tokenisasi WordPiece
English, bukan salinan `data/`:

```
data/Restaurant-ACOS/rest16_quad_test.tsv          : yum !            <TAB> -1,-1 FOOD#QUALITY 2 0,1
tokenized_data/rest16_test_quad_bert.tsv           : yu ##m !          <TAB> -1,-1 FOOD#QUALITY 2 0,2
data/Restaurant-ACOS/rest16_quad_test.tsv          : serves really good sushi .   <TAB> 3,4 ... 2,3
tokenized_data/rest16_test_quad_bert.tsv           : serves really good su ##shi . <TAB> 3,5 ... 2,3
```

Perhatikan span ikut bergeser (`0,1`→`0,2`, `3,4`→`3,5`) karena `sushi` pecah
menjadi dua token. Ini mengonfirmasi mekanismenya: **offset adalah indeks
whitespace-token pada teks yang SUDAH ter-WordPiece**, bukan indeks karakter dan
bukan indeks subword hasil tokenizer saat runtime. Di `run_classifier_dataset_utils.py:298`
teks memang hanya di-`split()`:

```python
orig_tokens = example.text_a.strip().split()
```

Konsekuensi: menulis generator ini adalah **deliverable baru** (§6.2), bukan
sekadar "menjalankan ulang". Ini pekerjaan paling rawan di seluruh migrasi.

---

## 3. Keputusan yang diambil

Laporan 011 berhenti pada rekomendasi bersyarat. PRD ini memutuskan:

| Keputusan | Pilihan | Alasan |
|---|---|---|
| Checkpoint utama | **`indobenchmark/indobert-base-p1`** | standar benchmark Indonesia (comparability ke literatur), lisensi MIT, tersedia sebagai `pytorch_model.bin` sehingga bisa dibaca `torch.load` legacy |
| Checkpoint pembanding | `LazarusNLP/NusaBERT-base` | untuk A/B setelah baseline stabil; vocab identik sehingga `tokenized_data` **tidak perlu dibuat ulang** saat membandingkan |
| Ditunda | `indobert-large-p1` | 335M param, ~2.7× VRAM/waktu; baru dipertimbangkan setelah base terbukti |
| Ditolak | `w11wo/indonesian-roberta-base` | beda arsitektur (tanpa `token_type_ids`), butuh ubah kelas model |
| Strategi porting | **Strategi B (port ke `transformers`)** untuk tokenizer + **re-keying state_dict** untuk model | konsekuensi langsung §2.1; Strategi A murni ditolak |
| Ukuran taksonomi | **13 kategori** domain restoran Indonesia | mempertahankan `num_labels = 13×3 = 39` seperti rest16, sehingga dimensi head Step 2 tidak berubah dan angka bisa dibandingkan langsung dengan baseline English |

`NusaBERT-base` hanya merilis `model.safetensors` (tanpa `pytorch_model.bin`),
jadi jalur legacy `torch.load` tidak bisa membacanya. Itu alasan tambahan
menjadikannya pembanding tahap dua, bukan target pertama.

### 3.1 Pre-trained IndoBERT (bukan fine-tuned) — ditegaskan

Yang dipakai adalah **checkpoint pre-trained murni**
`indobenchmark/indobert-base-p1`, lalu **kita sendiri** yang mem-fine-tune-nya
pada data ACOS. Checkpoint IndoBERT yang sudah di-fine-tune orang lain untuk
tugas lain (mis. `*/indobert-absa`, `*/indobert-sentiment-*` di HF) **tidak
dipakai**.

Bukti bahwa checkpoint ini memang encoder pre-trained polos: saya pindai
state_dict-nya dan **tidak ada satu pun key `cls.*`** (head MLM), berbeda dari
`bert-base-uncased` yang membawa 14 key `cls.*`. Isinya hanya `embeddings.*`,
`encoder.*`, `pooler.*` — konsisten dengan `config.json` yang menyatakan
`"architectures": ["BertModel"]`. Jadi tidak ada head tugas apa pun yang perlu
dibuang.

Alasan menolak checkpoint yang sudah fine-tuned:

1. **Arsitektur head tidak cocok.** ACOS Step 1 butuh tagging token-level
   6-tag BIO (`['[CLS]','O','I-A','B-A','I-O','B-O']`) di atas CRF, plus dua head
   biner untuk aspek/opini implisit. Model ABSA di HF umumnya head klasifikasi
   sentence-level 2–3 kelas. Head-nya pasti dibuang, jadi tidak ada yang diwarisi.
2. **Encoder sudah bergeser (task/domain drift).** Bobot encoder-nya sudah
   teroptimasi untuk objektif dan domain lain (IoT pertanian, PLN, berita).
   Untuk domain restoran/e-commerce itu bias, bukan keuntungan.
3. **Comparability hilang.** Nilai ilmiah pembandingan ke literatur Indonesia
   bertumpu pada pemakaian checkpoint standar `indobert-base-p1`. Memulai dari
   turunan pihak ketiga membuat angka tidak bisa dibandingkan.
4. **Provenance tidak terverifikasi.** Model komunitas dengan unduhan puluhan
   tidak punya jaminan data latih, lisensi, maupun kebocoran test set.

Penegasan istilah agar tidak rancu di laporan nanti: pipeline ini **memang
melakukan fine-tuning**, dan seluruh parameter dilatih tanpa freeze —
`param_optimizer = list(model.named_parameters())` di `run_step1.py:383` dan
`run_step2.py:257` mencakup `bert.embeddings.*` sampai head tugas. Jadi
"pre-trained IndoBERT" mengacu pada **titik awal**, sementara "fine-tuned
IndoBERT" adalah **hasil** yang kita produksi sendiri dan yang nanti disimpan
sebagai checkpoint eksperimen.

Konsekuensi lanjutan: Step 1 dan Step 2 masing-masing memulai dari
`indobert-base-p1` yang sama (tidak berantai), sehingga menghasilkan **dua**
model fine-tuned terpisah.


---

## 4. Ruang lingkup

**Termasuk:** porting loader + tokenizer ke IndoBERT, generator `tokenized_data`
berbasis vocab IndoBERT, taksonomi kategori Indonesia, fix bug Step 2, gate
verifikasi, dan file baru `.py` + `.ipynb` untuk menjalankannya.

**Tidak termasuk (dikerjakan terpisah):**

- Pengumpulan & anotasi dataset quadruple Indonesia. Ini blocker terbesar dan
  merupakan proyek anotasi tersendiri (lihat §8).
- Ekspansi ke bahasa daerah / NusaX.
- Konversi TF→PyTorch: tidak relevan, semua kandidat sudah menyediakan bobot
  PyTorch.
- SentencePiece: tidak relevan, semua kandidat memakai WordPiece.
- Mengubah `eval_metrics.py`: model-agnostik, cukup dipakai apa adanya.
- Mengubah `modeling.py:966` / `:1095` (hardcode `vocab_size=32000`): di luar
  jalur eksekusi.

---

## 5. File yang akan dibuat (deliverable baru)

Semua file baru diletakkan agar **tidak menyentuh** kode upstream lebih dari
yang perlu, sehingga pipeline English tetap bisa dijalankan sebagai kontrol.

| # | File | Isi |
|---|---|---|
| D1 | `Extract-Classify-ACOS/indobert_adapter.py` | unduh + siapkan checkpoint, re-keying state_dict, verifikasi bobot |
| D2 | `Extract-Classify-ACOS/id_taxonomy.py` | taksonomi 13 kategori restoran Indonesia + resolver domain |
| D3 | `Extract-Classify-ACOS/build_tokenized_data.py` | generator `tokenized_data/*_quad_bert.tsv` dengan remap span (§6.2) |
| D4 | `Extract-Classify-ACOS/verify_indobert.py` | 3 gate verifikasi (§7) sebagai skrip yang bisa dijalankan CI-style |
| D5 | `notebooks/06_IndoBERT_Migration_and_Verification.ipynb` | notebook Colab: setup → gate → train Step 1 → pair → train Step 2 → eval |

Perubahan pada file existing dibatasi pada:

| File | Perubahan | Baris acuan |
|---|---|---|
| `modeling.py` | `768` → `config.hidden_size`; buka kembali logging `missing_keys` | `1545`, `1608`, `750-755` |
| `bert_utils/tokenization.py` | fallback `[UNK]` pada `convert_tokens_to_ids` | `127` |
| `run_classifier_dataset_utils.py` | `get_labels` memanggil D2 untuk domain Indonesia | `230-259` |
| `tokenized_data/get_1st_pairs.py` | parsing tag `a-`/`o-` yang benar | `44-48` |
| `colab_utils.py` | `download_bert_pretrained` menerima parameter model | `60-81` |

---

## 6. Rancangan teknis

### 6.1 Adapter checkpoint (D1) — menjawab bloker §2.1

Fungsi `prepare_indobert(model_name, target_dir)`:

1. Unduh `config.json`, `pytorch_model.bin`, `vocab.txt` dari HF ke `target_dir`.
2. Muat state_dict, lalu **tambahkan prefix `bert.`** pada setiap key yang belum
   memilikinya, karena kelas target punya atribut `self.bert`:

   ```python
   remapped = OrderedDict()
   for k, v in state_dict.items():
       remapped[k if k.startswith('bert.') else f'bert.{k}'] = v
   ```

3. Simpan ulang sebagai `pytorch_model.bin` di `target_dir`.
4. Kembalikan `target_dir` beserta laporan: jumlah key sebelum/sesudah,
   `config.vocab_size`, jumlah baris `vocab.txt`.

Loader legacy sudah menormalkan `gamma`/`beta` → `weight`/`bias`
(`modeling.py:715-720`), jadi tidak perlu ditangani lagi. `CONFIG_NAME` legacy
sudah `config.json` (`bert_utils/file_utils.py:51`), cocok dengan nama file HF —
tidak perlu rename ke `bert_config.json`.

Head task (CRF, classifier, implicit head) memang harus ter-init acak; itu
perilaku benar via `self.apply(self.init_bert_weights)` (`modeling.py:1612`).
Yang tidak boleh acak adalah `bert.*`.

### 6.2 Generator `tokenized_data` (D3) — menjawab bloker §2.3

Input: `data/<Domain>/<domain>_quad_<split>.tsv` (format mentah, offset merujuk
whitespace-token teks asli). Output: `tokenized_data/<domain>_<split>_quad_bert.tsv`
(teks ter-WordPiece, offset merujuk whitespace-token teks ter-WordPiece).

**Tokenizer-agnostik (wajib).** Tanda tangan fungsinya menerima objek tokenizer,
bukan mengunci IndoBERT:

```python
def build_tokenized_data(tokenizer, in_path, out_path, *, do_lower_case=True):
```

Satu-satunya yang dituntut dari `tokenizer` adalah metode
`tokenize(word) -> list[str]`, yang dimiliki baik oleh `BertTokenizer` legacy
maupun `transformers`. Alasannya ada di §13.4: XLM-RoBERTa dan IndoRoBERTa nanti
butuh `tokenized_data` versi sendiri karena tokenizer-nya berbeda, dan menulis
ulang generator untuk itu adalah pemborosan yang bisa dihindari sekarang dengan
satu parameter.

Algoritma per baris:

1. Pisahkan `text` dan daftar quad dengan `split('\t')`.
2. `words = text.strip().split()` → daftar token asli.
3. Untuk setiap `words[i]`, jalankan `tokenizer.tokenize(words[i])` → daftar
   subword. Catat `new_start[i]` = indeks subword pertama dan `new_end[i]` =
   indeks setelah subword terakhir, sambil membangun daftar subword global.
4. Remap tiap span `(st, ed)`:
   - `-1,-1` diteruskan apa adanya (penanda implisit).
   - selain itu: `st' = new_start[st]`, `ed' = new_end[ed-1]`.
     Perhatikan konvensi upstream: `ed` adalah eksklusif (`3,4` untuk satu kata
     ke-3), dan setelah remap `sushi` menjadi `3,5` — cocok dengan contoh §2.3.
5. Tulis ulang baris dengan teks = `' '.join(subwords)` dan span hasil remap.

Aturan wajib:

- Jika `tokenizer.tokenize(word)` mengembalikan daftar kosong (bisa terjadi pada
  karakter kontrol), sisipkan `[UNK]` agar indeks tidak bergeser. Ini yang
  membuat remap tetap valid.
- **Jangan** memotong sequence di tahap ini. Truncation adalah tanggung jawab
  `_truncate_seq_pair` saat runtime (`run_classifier_dataset_utils.py:323`).
  Tapi catat: span yang jatuh di luar `max_seq_length - 2` akan hilang setelah
  truncation. Generator harus **melaporkan jumlah baris** yang subword-nya
  melebihi 126 agar dampaknya terukur, bukan tersembunyi.
- Simpan file laporan `tokenized_data/_build_report.json`: jumlah baris,
  distribusi panjang subword, jumlah span yang di-remap, jumlah `[UNK]`.

### 6.3 Taksonomi Indonesia (D2)

13 kategori mengikuti pola `ENTITAS#ATRIBUT` SemEval, dipetakan satu-satu dari
rest16 agar hasil bisa dibandingkan:

```python
RESTORAN_ID = [
    'RESTORAN#UMUM', 'PELAYANAN#UMUM', 'MAKANAN#UMUM', 'MAKANAN#KUALITAS',
    'MAKANAN#PILIHAN', 'MINUMAN#PILIHAN', 'MINUMAN#HARGA', 'SUASANA#UMUM',
    'RESTORAN#HARGA', 'MAKANAN#HARGA', 'RESTORAN#LAINNYA', 'MINUMAN#KUALITAS',
    'LOKASI#UMUM',
]
```

`get_labels` diubah agar `domain_type` yang dimulai `resto` memakai list ini,
sementara `rest`/`laptop` tetap seperti aslinya. Sentimen tetap `['0','1','2']`.
`num_labels` Step 2 = 39, identik dengan rest16 → head `nn.Linear(hidden*2, 39)`
tidak berubah dimensi.

### 6.4 Fix Step 2 (`KeyError`)

Akar masalah ada di `get_1st_pairs.py:44-48`. Tag prediksi berbentuk `a-3,4` dan
`o-0,1`, tetapi kondisinya `ele.startswith('a')` lalu memotong `ele[2:]`. Untuk
tag `a--1,-1` (aspek implisit), `ele[2:]` menghasilkan `-1,-1` — kebetulan benar.
Masalahnya kondisi `startswith('a')` juga menangkap kasus lain dan cabang `else`
memasukkan apa pun ke `opi`. Perbaikan: parsing eksplisit dengan pemisah `-`
pertama, dan tolak token yang tidak cocok pola `^[ao]-(-?\d+),(-?\d+)$`.

Pertahanan kedua di `bert_utils/tokenization.py:127`: ganti lookup langsung
menjadi `self.vocab.get(token, self.vocab['[UNK]'])`. Ini mengubah crash menjadi
degradasi yang terukur — penting saat vocab berganti ke IndoBERT, karena token
apa pun yang lolos dari generator tidak akan meledakkan training.

---

## 7. Gate verifikasi (wajib, D4)

Setiap gate harus lulus sebelum fase berikutnya. Gate 1 adalah yang paling
penting karena §2.1 membuat kegagalan bersifat senyap.

### 7.1 Gate 1 — bobot IndoBERT benar-benar termuat

```
1. Muat model via from_pretrained(target_dir hasil D1).
2. Baca state_dict checkpoint asli, ambil bert.embeddings.word_embeddings.weight.
3. Bandingkan dengan model.bert.embeddings.word_embeddings.weight secara numerik
   (torch.allclose).
4. Ulangi untuk encoder.layer.0.attention.self.query.weight dan
   encoder.layer.11.output.dense.weight.
LULUS bila ketiganya identik. GAGAL bila salah satu berbeda.
```

Tambahan: patch `modeling.py:750-755` agar `missing_keys` / `unexpected_keys`
kembali di-log, lalu **assert bahwa tidak ada key `bert.*` di `missing_keys`**.

### 7.2 Gate 2 — regenerasi `tokenized_data` konsisten

```
1. Jalankan D3 memakai vocab bert-base-uncased pada data English.
2. Bandingkan output dengan tokenized_data/*_quad_bert.tsv yang ada di repo.
LULUS bila identik atau selisih terjelaskan (mis. hanya baris ber-[UNK]).
```

Ini pengujian generator terhadap ground truth yang sudah ada di repo, sebelum
generator dipercaya untuk vocab IndoBERT. Tanpa gate ini, kesalahan remap span
tidak akan terdeteksi sampai metrik anjlok tanpa sebab jelas.

### 7.3 Gate 3 — end-to-end tanpa crash

```
1. Subset kecil (100 baris train, 20 dev, 20 test), 1 epoch.
2. run_step1.py → get_1st_pairs.py → run_step2.py → eval_metrics.
LULUS bila selesai tanpa exception dan eval_metrics mengeluarkan angka.
```

---

## 8. Fase kerja & ketergantungan

| Fase | Isi | Bergantung | Blocking? |
|---|---|---|---|
| F0 | D1 + Gate 1 | — | tidak |
| F1 | D3 + Gate 2 (divalidasi pada data English) | — | tidak |
| F2 | Fix Step 2 + fallback `[UNK]` + Gate 3 pada data English | F1 | tidak |
| F3 | D2 taksonomi Indonesia | — | tidak |
| F4 | **Dataset quadruple Indonesia** | F3 | **YA — blocker** |
| F5 | Regenerasi `tokenized_data` Indonesia dengan vocab IndoBERT | F0,F1,F4 | — |
| F6 | Train + eval Step 1 & Step 2 | F2,F5 | — |
| F7 | A/B dengan NusaBERT-base | F6 | — |

Poin penting: **F0–F3 semuanya bisa dikerjakan sekarang dan diverifikasi memakai
data English yang sudah ada di repo.** Hanya F4 ke atas yang menunggu dataset.
Ini sengaja disusun begitu agar seluruh risiko teknis (§2.1, §2.3) tuntas
sebelum anotasi selesai, bukan sesudah.

Untuk F4, tiga opsi yang tersedia — anotasi baru dari ulasan Indonesia
(GoFood/Tokopedia/Google Maps), memperluas dataset ABSA Indonesia yang ada ke
format quadruple, atau bootstrap LLM lalu divalidasi manusia. Semuanya butuh
pedoman anotasi + pengukuran IAA, terutama untuk kasus implisit yang merupakan
bagian tersulit. Keputusan opsi ada di luar PRD ini.

Catatan arsitektur yang perlu diingat saat F6: Step 1 dan Step 2 **masing-masing
berangkat dari checkpoint base yang sama**, tidak berantai
(`run_step1.py:353`, `run_step2.py:256`). Jadi `--bert_model` harus diarahkan ke
folder IndoBERT hasil D1 di kedua skrip.

---

## 9. Hyperparameter awal

Mengikuti `run.sh` upstream agar perbandingan adil, dengan satu penyesuaian:

| Parameter | Step 1 | Step 2 | Catatan |
|---|---|---|---|
| `max_seq_length` | 128 | 128 | sama seperti upstream |
| `train_batch_size` | 24 | 16 | sama |
| `learning_rate` | 2e-5 | 5e-5 | sama |
| `num_train_epochs` | 30 | 30 | turunkan ke 3 untuk Gate 3 |
| `do_lower_case` | ya | ya | IndoBERT p1 uncased |

`do_lower_case` wajib aktif: `tokenizer_config.json` IndoBERT kosong (`{}`)
sehingga tidak ada default, dan modelnya uncased. Jika lupa, token bermodal
huruf besar akan jadi `[UNK]` dalam jumlah besar — dan dengan fallback §6.4 itu
tidak akan error, hanya menurunkan mutu secara diam-diam. Generator D3 harus
memakai flag yang sama dengan runtime.

---

## 10. Metrik & pelaporan

Pakai `eval_metrics.py` tanpa perubahan. Yang diubah adalah cara melaporkan:

- `measureQuad` (`eval_metrics.py:25`) untuk metrik quadruple keseluruhan.
- `measureQuad_imp` (`:178`) + `getTextType` (`:154`) untuk **breakdown
  eksplisit vs implisit**. Dua fungsi ini sudah ada di repo tapi tidak disebut
  di laporan mana pun. Karena anotasi implisit adalah bagian tersulit,
  breakdown ini dijadikan bagian wajib laporan hasil, bukan opsional.
- `pair_eval` (`:223`) untuk mutu pasangan hasil Step 1 secara terpisah, agar
  jelas apakah kesalahan berasal dari ekstraksi atau klasifikasi.
- Checkpoint terbaik dipilih dengan `max_macro_F1` (`run_step1.py:396`),
  konsisten dengan upstream.

**Tidak ada target angka F1 yang ditetapkan di PRD ini.** Belum ada dataset
Indonesia, sehingga angka apa pun akan jadi tebakan. Baseline pembanding
ditetapkan setelah F6 pertama selesai, dan angka rest16 English dari repo ini
dipakai sebagai referensi sanity-check pipeline, bukan sebagai target.

---

## 11. Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| **Bobot IndoBERT tidak termuat secara senyap** (§2.1) | eksperimen tidak valid tapi tampak sukses | Gate 1 numerik; buka logging `missing_keys` |
| **Remap span salah di generator baru** (§2.3) | metrik turun tanpa sebab jelas | Gate 2 terhadap `tokenized_data` English yang ada |
| Span hilang akibat truncation 126 subword | recall turun | generator melaporkan jumlah baris terdampak |
| `vocab.txt` base-p1 hanya mengisi 30521 dari 50000 baris (§2.2) | 19479 baris embedding tak terpakai | terima; catat di laporan, jangan dijadikan acuan `vocab_size` |
| Fallback `[UNK]` menyembunyikan masalah vocab | mutu turun diam-diam | hitung & laporkan rasio `[UNK]`; gagalkan build bila > 5% |
| Dataset Indonesia belum ada | F5–F7 tertunda | F0–F3 dikerjakan lebih dulu dengan data English |
| NusaBERT hanya `safetensors` | jalur legacy tak bisa baca | jadikan pembanding tahap dua; konversi bila perlu |
| Anotasi implisit sulit & subjektif | label bising | pedoman ketat + IAA; mulai dari kasus eksplisit |

---

## 12. Lingkungan

Repo lokal tidak punya `torch`, `transformers`, `torchcrf`, `numpy`, maupun
`sklearn` (Python 3.14.2 tanpa paket ML). Jadi semua eksekusi dan gate
dijalankan di **Google Colab**, dan D5 adalah jalur eksekusi utamanya. File
`.py` (D1–D4) ditulis agar bisa diimpor dari notebook maupun dijalankan sebagai
CLI, sehingga logikanya tidak terkunci di dalam sel notebook.

---

## 13. Metode Deep Learning lain: perlu atau tidak?

Jawaban singkat: **perlu, tapi bukan sekarang, dan tidak semuanya setara nilainya.**
Menyiapkan lima arsitektur sekaligus sebelum ada satu angka pun dari IndoBERT
adalah pemborosan — dan lebih buruk, membuat kegagalan sulit dilokalisasi.

### 13.1 Kenapa ditunda, bukan ditolak

Pipeline ini punya dua bloker yang belum tuntas (§2.1 bobot senyap, §2.2/§2.3
generator span) dan satu bloker data (§8 F4). Menambah arsitektur sekarang
berarti setiap hasil aneh punya banyak tersangka: apakah salah remap span, salah
muat bobot, atau memang arsitekturnya kurang cocok. Urutan yang benar adalah
memastikan satu jalur bersih dulu, jadikan ia **baseline terkalibrasi**, baru
tambah pembanding.

Ada juga alasan struktural. Kelima metode yang kamu sebut **tidak sejenis**:

- **CNN, LSTM, BiLSTM** = encoder sekuens yang menggantikan peran BERT di dalam
  pipeline yang sama.
- **XLM-RoBERTa, IndoRoBERTa** = pengganti checkpoint pre-trained, tetap
  Transformer.

Yang kedua jauh lebih murah dikerjakan karena hanya menukar backbone. Yang
pertama menuntut penulisan encoder + jalur embedding baru dari nol.

### 13.2 Biaya nyata per metode di repo ini

| Metode | Perubahan yang dibutuhkan | Biaya | Nilai ilmiah |
|---|---|---|---|
| **BiLSTM-CRF** | encoder baru; embedding non-BERT (Word2Vec/FastText ID); `modeling.py` head disambungkan ulang | sedang | **tinggi** — baseline pra-Transformer yang lazim diminta reviewer |
| **LSTM (uni)** | sama seperti BiLSTM, tanpa arah balik | rendah setelah BiLSTM ada | rendah — hampir selalu di bawah BiLSTM; nilainya cuma ablasi |
| **CNN** | encoder konvolusional; tidak natural untuk span panjang | sedang | rendah untuk tagging span; wajar hanya sebagai ablasi |
| **XLM-RoBERTa** | tukar tokenizer (SentencePiece), hapus `token_type_ids` | sedang | **tinggi** — pembanding multilingual, relevan untuk klaim "butuh model khusus Indonesia" |
| **IndoRoBERTa** (`flax-community/indonesian-roberta-base`, `cahya/roberta-base-indonesian-522M`) | sama seperti XLM-R | sedang | sedang — menguji apakah objektif RoBERTa > BERT pada bahasa yang sama |

Dua catatan teknis yang mengubah perkiraan biaya:

**Untuk keluarga RoBERTa, hambatannya bukan tokenizer, tapi `token_type_ids`.**
Laporan 008 dan 010 sudah benar menandai ini. Di repo, `token_type_ids` dipakai
di jalur wajib: `aspect_segment_ids` dibangun di
`run_classifier_dataset_utils.py` dan diteruskan sebagai
`aspect_token_type_ids` ke `forward` (`modeling.py:1558`). RoBERTa tidak punya
`type_vocab_size` yang bermakna, jadi jalur ini harus dinetralkan — bukan
sekadar mengganti nama checkpoint. Ini pekerjaan mekanis yang jelas, bukan riset.

**Untuk BiLSTM/CNN, ada kejutan yang menguntungkan: kerangkanya sudah setengah
ada.** `modeling.py:1174` mendefinisikan `class CNNLayer`, dan `:1129`
mendefinisikan `class self_attention_layer`. Saya cek pemakaiannya:
`self_attention_layer` diinstansiasi di `modeling.py:1263` (di dalam
`BertForSequenceClassification`, yang **tidak** terdaftar di `model_dict`),
sedangkan `CNNLayer` **tidak pernah diinstansiasi sama sekali** — dead code
warisan upstream. Artinya ada kode CNN yang bisa dijadikan titik awal, tapi
statusnya belum pernah diuji, jadi jangan diasumsikan benar.

Yang benar-benar reusable untuk semua varian encoder adalah **CRF-nya**:
`self.crf = CRF(self.crf_num, batch_first=True)` (`modeling.py:1541`) berasal
dari `torchcrf` dan tidak bergantung pada BERT. Head implisit
(`imp_asp_classifier`, `imp_opi_classifier`) juga hanya butuh vektor
berdimensi `hidden_size`. Jadi kontrak antarmuka untuk encoder pengganti sudah
tersirat: hasilkan tensor `(batch, seq_len, hidden)` plus satu vektor kalimat.

### 13.3 Rekomendasi urutan

Prioritas disusun dari rasio nilai-terhadap-biaya, bukan dari kelengkapan:

1. **IndoBERT-base pre-trained** (PRD ini) — baseline utama.
2. **NusaBERT-base** — sudah ada di §3; biaya paling rendah karena vocab identik,
   `tokenized_data` tidak perlu dibuat ulang.
3. **XLM-RoBERTa-base** — pembanding multilingual. Ini yang paling sering
   ditanyakan reviewer: "kenapa tidak pakai model multilingual saja?" Tanpa angka
   ini, klaim keunggulan model khusus Indonesia tidak berdasar.
4. **BiLSTM-CRF + FastText ID** — baseline pra-Transformer. Nilainya bukan untuk
   menang, tapi untuk menunjukkan besar lompatan yang disumbang pre-training.
5. **IndoBERT-large** — uji kapasitas, hanya jika VRAM Colab mencukupi.
6. **IndoRoBERTa** — opsional; menguji objektif pre-training pada bahasa sama.
7. **CNN dan LSTM uni-direksional** — ablasi saja, prioritas terakhir.

Untuk skripsi/tesis/artikel, kombinasi minimal yang sudah cukup kuat adalah
**#1 + #3 + #4**: satu model khusus Indonesia, satu multilingual, satu
pra-Transformer. Menambah #2 dan #5 memperkuat tanpa menambah risiko besar.
Menjalankan ketujuhnya justru melemahkan laporan karena tiap sel tabel jadi
kurang teruji.

### 13.4 Prasyarat agar perbandingan itu valid

Perbandingan lintas arsitektur hanya bermakna bila hal-hal ini dikunci lebih
dulu — dan sebagian di antaranya adalah alasan lain mengapa ini harus menunggu:

- **Split data identik** dan tetap. Tanpa dataset Indonesia (§8 F4), tidak ada
  yang bisa dikunci.
- **Tokenisasi tercatat per model.** IndoBERT dan NusaBERT boleh berbagi
  `tokenized_data`, tapi XLM-R dan RoBERTa **wajib** punya versi sendiri karena
  tokenizer-nya berbeda. Ini melipatgandakan pekerjaan §6.2, dan generator D3
  harus dirancang menerima tokenizer sebagai parameter sejak awal supaya tidak
  perlu ditulis ulang. **Konsekuensi konkret untuk PRD ini: D3 dibuat
  tokenizer-agnostik, bukan hardcode IndoBERT.**
- **Metrik sama**, termasuk breakdown eksplisit/implisit (§10).
- **Seed dan jumlah run dilaporkan.** Selisih F1 satu-dua poin antar arsitektur
  sering lebih kecil daripada variasi antar seed; tanpa beberapa run, peringkat
  bisa menyesatkan.
- **Anggaran compute setara.** Membandingkan BiLSTM 30 epoch dengan IndoBERT 3
  epoch bukan perbandingan arsitektur.

### 13.5 Yang perlu dikerjakan sekarang

Hanya satu, dan sudah dimasukkan ke §6.2: **buat D3 menerima tokenizer sebagai
parameter**, bukan mengunci IndoBERT. Perubahan kecil hari ini, tapi menghindari
penulisan ulang generator saat XLM-R masuk.

Analisis mendalam per arsitektur (desain encoder, sumber embedding, hyperparameter)
sebaiknya ditulis sebagai PRD terpisah **setelah gate §7 lulus**, karena saat itu
kita sudah tahu bentuk kontrak encoder yang sebenarnya bekerja — bukan menebaknya
dari pembacaan kode.


