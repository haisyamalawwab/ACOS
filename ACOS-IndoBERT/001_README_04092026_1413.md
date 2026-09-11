# ACOS-IndoBERT

Pipeline ACOS dua tahap (Step 1 co-extraction aspek-opini, Step 2 klasifikasi
category-sentiment) untuk **dataset ulasan aplikasi bank digital berbahasa
Indonesia**, dengan backbone **IndoBERT yang di-fine-tune di sini**.

Folder ini berdiri sendiri. Repo pipeline Inggris `ACOS-ASLI/` di folder induk
dipakai **hanya untuk dibaca** — tidak satu berkas pun di sana diubah, dan tidak
satu artefak run pun ditulis ke sana.

## Dua root

| Variabel | Isi | Ditulis? |
|---|---|---|
| `indo_root` | folder ini | ya, semuanya |
| `acos_root` | `../` (ACOS-ASLI) — `Extract-Classify-ACOS/`, `data/Restaurant-ACOS/` | tidak |

```
ACOS-IndoBERT/
  acos_id/          paket lapisan Indonesia (7 modul, torch-free kecuali checkpoint.py)
  data/Apps-ACOS/   dataset: raw/, processed/, lexicon/ + appsid_quad_{train,dev,test}.tsv
  tokenized_data/   appsid_{split}_quad_bert.tsv + appsid_{split}_pair.tsv
  backbones/        indobert_base_p1/ (hasil rekey) + bert_base_uncased/ (vocab untuk gate 2)
  notebooks/        _build_v4_indobert.py + 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb
  build/            skrip verifikasi + keluaran sementara
  results/          folder sesi appsid_<timestamp>/ (checkpoints, csv, md, plots, logs)
```

## Cara pakai

**Colab** — buka `notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`,
jalankan berurutan. Sel 1b (pelacak progres) dan 2c (dua root + `acos_id`) wajib
diulang setiap kali kernel di-restart. Sel 4c mengunduh dan merekey IndoBERT,
4d menjalankan lima gate data, dan 5d2 adalah Gate 1 — kalau merah, berhenti di
situ, jangan lanjut ke training.

**Lokal** — tanpa torch pun keempat perintah pertama jalan:

```bash
python -m acos_id.selftest            # 5 gate torch-free
python -m acos_id.build_acos          # processed/*.csv → appsid_quad_*.tsv
python -m acos_id.tokenize_data       # → tokenized_data/ dengan vocab IndoBERT
python -m acos_id.eda                 # statistik + 4 plot ke build/_eda_id/
python build/_sim_v4_cells.py         # eksekusi sel notebook torch-free
python build/_verify_id_features.py   # fitur upstream vs data Indonesia
python notebooks/_build_v4_indobert.py  # bangun ulang notebook (deterministik)
```

`python -m acos_id.checkpoint indobert backbones/indobert_base_p1` menyiapkan
checkpoint, tetapi butuh torch — jalankan di Colab.

## Dataset

13 kategori datar (`AUTH_ACCESS`, `TRANSACTION_TRANSFER`, …), sentimen `0/1/2`,
`num_labels` Step 2 = 39 — sengaja sama dengan rest16 agar dimensi head tidak
berubah dan angkanya bisa diletakkan berdampingan dengan baseline Inggris.

| Split | Baris (klausa) | Tuple | Aspek eksplisit | Opini eksplisit |
|---|---|---|---|---|
| train | 60.159 | 72.973 | 51.184 | 43.271 |
| dev | 8.027 | 9.587 | 6.588 | 5.836 |
| test | 7.891 | 9.514 | 6.576 | 5.693 |

Satu baris = satu **klausa**, bukan satu ulasan. Span aspek/opini terpetakan 100%
di dalam klausanya sendiri, versus 61,5%/48,0% bila ulasan utuh dipakai sebagai
baris. Retokenisasi WordPiece IndoBERT menghasilkan 0 token `[UNK]` dan tidak
menghilangkan satu tuple pun.

## Gerbang verifikasi

Enam gate. Lima torch-free (`python -m acos_id.selftest`) semuanya hijau di sini;
Gate 1 butuh GPU Colab. Semuanya `raise_on_fail=True` di notebook karena setiap
kegagalan di daftar ini **tidak terlihat** dari kurva loss maupun metrik training.

| Gate | Yang diperiksa |
|---|---|
| `taxonomy` | 13 kategori kode == `label_maps.json`, urutan sama |
| `dataset` | berkas sumber ada; `review_id` train/dev/test saling lepas |
| `acos_build` | tiap span menunjuk token nyata |
| `tokenized` | retokenisasi tidak menghilangkan tuple |
| `gate2_english` | regenerasi data Inggris identik dengan `tokenized_data/` upstream |
| `weights` (Gate 1) | bobot encoder model == checkpoint, dibandingkan numerik |

Gate 1 adalah yang paling penting. `BertForQuadABSA` punya atribut `self.bert`,
sehingga loader legacy menetapkan `start_prefix=''` dan mencari key `bert.*`;
checkpoint IndoBERT menyimpan key tanpa prefiks itu, jadi seluruh bobot encoder
masuk `missing_keys` — dan logging yang akan melaporkannya di-comment out di
`modeling.py:749-755`. Tanpa gate ini, training berjalan mulus di atas encoder
**acak** dan satu-satunya gejala adalah F1 yang rendah tanpa sebab.

## Kontrol Inggris

Ubah `DOMAIN = "rest16"` di sel 3. `BACKBONE` otomatis dipaksa ke `bert-en`
dengan pesan, `tokenized_base` beralih ke `Extract-Classify-ACOS/`, dan ketiga
sel Indonesia (4c, 4d, 5d2) melewati dirinya sendiri.

## Catatan untuk penulisan hasil

Tiga sifat dataset yang harus disebut di bagian metode:

- **Anotasi lemah, bukan manual.** Kolom `weight` dan `evidence` di
  `quintuples_weak.csv` menunjukkan label dibuat otomatis dengan skema
  pembobotan. Angka yang keluar adalah kesepakatan dengan pelabelan itu, bukan
  dengan anotasi manusia.
- **Klausa pendek berulang lintas split.** 9,0% teks klausa unik di test juga ada
  di train, menyentuh 14,7% baris test — semuanya klausa sangat pendek (median 3
  kata: `bagus`, `bebas iklan`). Pemisahan split sendiri bersih di tingkat
  `review_id`, jadi ini bukan kebocoran ulasan, tetapi sebaiknya dilaporkan
  terpisah.
- **Multi-label hampir tidak terpakai.** Hanya 0,4% baris pair train punya lebih
  dari satu label berbeda, walau head Step 2 tetap multi-label seperti baseline.

Laporan lengkap: `../reports/023_pipeline_acos_indobert_dataset_indonesia_04092026.md`
