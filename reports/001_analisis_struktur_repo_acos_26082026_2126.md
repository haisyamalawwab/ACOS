# Analisis Repo ACOS-ASLI

Tanggal analisis: 2026-08-26
Metode: pembacaan kode statis. Tidak ada eksekusi pipeline (environment ini Python 3.14 tanpa `torch`).
Status: belum ada file yang diubah oleh analisis ini.

## 1. Identitas repo

Fork/copy dari repo resmi paper ACL 2021 *Aspect-Category-Opinion-Sentiment Quadruple
Extraction with Implicit Aspects and Opinions* (Cai, Xia, Yu).

Isi: dua dataset ACOS + implementasi **satu** baseline saja (Extract-Classify-ACOS).
Tiga baseline lain yang disebut di `README.md` (Double-Propagation-ACOS, JET-ACOS,
TAS-BERT-ACOS) **tidak ada** di repo ini.

## 2. Struktur

```
data/                          # dataset mentah, TIDAK dipakai kode mana pun
  Restaurant-ACOS/rest16_quad_{train,dev,test}.tsv     1530/171/583 baris
  Laptop-ACOS/laptop_quad_{train,dev,test}.tsv         2934/326/816 baris
Extract-Classify-ACOS/
  run.sh                            # orkestrator 3 langkah
  run_step1.py                      # step 1: co-extraction aspect+opinion (CRF)
  run_step2.py                      # step 2: klasifikasi category-sentiment
  tokenized_data/get_1st_pairs.py   # jembatan step1 -> step2
  modeling.py (1646 baris)          # port pytorch_pretrained_bert + 2 head task
  run_classifier_dataset_utils.py   # processor & feature conversion
  eval_metrics.py                   # metrik + penulis pred4pipeline.txt
  dataset_utils.py                  # pembaca gold pair
  manager.py                        # pemilih GPU
  file_utils.py                     # duplikat bert_utils/file_utils.py
  bert_utils/                       # tokenization, optimization, file_utils
  tokenized_data/*.tsv              # data siap-pakai (sudah ter-wordpiece)
img/                                # gambar untuk README
README.md
.agents/skills/                     # guideline agent (coding + karpathy)
```

## 3. Alur pipeline

Dua tahap terpisah, bukan end-to-end.

### Step 1 — `run_step1.py` + `BertForQuadABSA`

- BERT + CRF dengan 6 tag: `[CLS] O I-A B-A I-O B-O` untuk span aspect/opinion.
- Dua classifier biner untuk mendeteksi *implicit*:
  - implicit aspect dibaca dari posisi `[CLS]`
  - implicit opinion dibaca dari posisi `[SEP]` terakhir
- Loss total = CRF loss + 2 cross-entropy.
- Prediksi test ditulis ke `{output_dir}/pred4pipeline.txt` (lihat `eval_metrics.py:133`).

### Step 2 — `get_1st_pairs.py` (jembatan)

- Membaca `pred4pipeline.txt`.
- Melakukan cross-product **semua** aspect x **semua** opinion yang terprediksi.
- Menulis `{domain}_test_pair_1st.tsv`.

### Step 3 — `run_step2.py` + `CategorySentiClassification`

- BERT, lalu mean-pool span aspect dan span opinion secara terpisah.
- Concat kedua representasi (768 x 2), satu `nn.Linear` ke `len(kategori) x 3`.
- Label gabungan `CATEGORY#SENTIMENT`, `BCEWithLogitsLoss` (multi-label).
  - rest16: 13 kategori x 3 = **39 kelas**
  - laptop: 121 kategori x 3 = **363 kelas**
- Training memakai pasangan **gold** (`_train_pair.tsv`), evaluasi test memakai
  pasangan **hasil step 1** (`_test_pair_1st.tsv`). Error step 1 memang dipropagasi
  ke step 2 — ini sesuai desain paper (pipeline, bukan joint).

## 4. Format data

| Jenis | Format |
|---|---|
| quad | `text \t start,end CATEGORY#ASPECT sentiment start,end` |
| pair | `text####aspan ospan \t CATEGORY#SENTIMENT` |

- `-1,-1` menandai *implicit* aspect atau opinion.
- Sentiment `0`/`1`/`2` = negative / neutral / positive.
- Offset span mengacu ke indeks token hasil WordPiece, bukan kata asli.

## 5. Kondisi working tree

Lima file termodifikasi dan belum di-commit. Semuanya bersifat *porting* agar dapat
berjalan di luar environment penulis aslinya.

### `modeling.py` + `bert_utils/tokenization.py`

URL S3 `models.huggingface.co` yang sudah mati diganti ke
`huggingface.co/.../resolve/main`. Sekaligus 6-7 entri varian BERT
(`german-cased`, `whole-word-masking`, `finetuned-squad`, `finetuned-mrpc`)
dihapus dari map. **Tidak berdampak** pada repo ini karena `run.sh` memakai
path lokal (`BERT_BASE_DIR`), bukan nama model.

### `dataset_utils.py`

`sys.path.insert('/mnt/nfs-storage-titan/...')` + import `pytorch_pretrained_bert`
diganti ke `bert_utils.tokenization` lokal. **Perbaikan nyata** — sebelumnya file
ini tidak mungkin diimpor di mesin lain.

### `manager.py`

Dipangkas ~90 baris. Perubahan yang penting:

- `auto_choice` dulunya *blocking loop* yang menunggu GPU dengan free memory >= 18
  sebelum lanjut. Sekarang langsung memilih GPU dengan free memory terbesar.
- Fallback ke index `"0"` plus dict GPU dummy kalau `nvidia-smi` tidak ada.
- Efeknya: skrip tidak lagi menggantung di mesin tanpa GPU NVIDIA.
- `_sort_by_custom` (tidak terpakai) dihapus.

### `tokenized_data/get_1st_pairs.py`

- Output path yang tadinya hardcode
  `base_dir + '/ACOS-main/Extract-Classify-ACOS/tokenized_data/'`
  diganti jadi rantai fallback 3 lokasi.
- Ditambah mode 3-argumen eksplisit: `pred_file domain out_file`.
- Ditambah `os.makedirs(..., exist_ok=True)` dan `encoding='utf-8'`.

## 6. Temuan

### Bug upstream (bukan dari perubahan di atas)

**P2 — `ae_loss` undefined di jalur gradient accumulation / fp16**
`run_step1.py:420-428`. Baris 422 dan 426 memakai variabel `ae_loss` yang tidak
pernah didefinisikan di scope loop training; yang ada hanya `loss = losses[0]`.
Selama `gradient_accumulation_steps == 1` dan `--fp16` tidak dipakai (default
`run.sh`), kedua baris ini tidak tereksekusi. Begitu salah satu diaktifkan,
langsung `NameError`.

**P2 — `pdb.set_trace()` di jalur except menggantung run non-interaktif**
`run_classifier_dataset_utils.py:176-179`. Bare `except` yang memanggil
`pdb.set_trace()` saat `line[0]` gagal dibaca. Kalau ada baris TSV malformed,
proses tidak error tapi masuk prompt debugger dan menggantung selamanya — sulit
didiagnosis di batch run.

### Catatan lain

- **Duplikasi file_utils.** `Extract-Classify-ACOS/file_utils.py` byte-identik
  dengan `bert_utils/file_utils.py` (279 baris). `modeling.py` mengimpor yang
  top-level, `bert_utils/tokenization.py` mengimpor yang di dalam package.
- **`run.sh` masih path absolut** environment penulis (`/mnt/nfs-storage-titan/...`)
  untuk `BERT_BASE_DIR`, `BASE_DIR`, `DATA_DIR`. Harus diedit manual sebelum jalan;
  `Readme.md` memang menginstruksikan begitu.
- **Risiko path-mismatch di jembatan step1 -> step2.** `get_1st_pairs.py` menentukan
  output dari `BASE_DIR`, sementara `run_step2.py` membaca dari
  `DATA_DIR/tokenized_data/`. Kalau `$BASE_DIR/tokenized_data` kebetulan ada tapi
  bukan `DATA_DIR`, cabang fallback pertama menulis ke tempat yang salah
  **tanpa error**.
- **Tidak ada `requirements.txt`.** Dependensi dari hasil baca import: `torch`,
  `pytorch-crf` (`torchcrf`), `scikit-learn`, `tqdm`, `numpy`, `boto3`/`requests`
  (dipakai `file_utils`). `Readme.md` menyebut Python 3.7 / PyTorch 1.8.
- **Tidak ada `.gitignore`**, dan 16 file `.pyc` di `__pycache__/` ter-track di git
  (termasuk `.cpython-37/38/39` — artefak dari beberapa versi Python).
- **Semua `.tsv` di `tokenized_data/` ber-CRLF.** Tertangani karena semua parser
  memakai `.strip()`, tapi `dataset_utils.py` maupun `get_1st_pairs.py` tidak akan
  toleran kalau cara parsing diubah.
- **Folder `data/` tidak direferensikan kode mana pun.** Dataset yang benar-benar
  dipakai adalah versi ter-tokenisasi di `Extract-Classify-ACOS/tokenized_data/`.
  `data/` murni untuk distribusi/publikasi.

## 7. Batas verifikasi

- Tidak ada test di repo.
- Environment analisis: Python 3.14, `torch` tidak terinstal. Tidak ada kode yang
  dijalankan.
- Semua temuan di atas hasil pembacaan kode statis, bukan hasil eksekusi.
- Belum ada file kode yang diubah. Sesuai `.agents/skills`, perubahan struktural
  butuh konfirmasi lebih dulu, dan tidak ada yang terbukti broken sampai pipeline
  benar-benar dijalankan.

