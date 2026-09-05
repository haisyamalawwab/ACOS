# 023 — Pipeline ACOS IndoBERT untuk Dataset Indonesia (Apps-ACOS)

> Tanggal: 4 September 2026
> Deliverable: folder `ACOS-IndoBERT/` — paket `acos_id/` + notebook
> `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`
> Status: **belum pernah dilatih** — semua verifikasi di bawah torch-free atau berbasis berkas

---

## 1. Yang dibangun

Dataset Indonesia baru (96.417 quintuple lemah dari 43.673 ulasan aplikasi bank
digital) dijalankan lewat pipeline ACOS dua tahap yang sudah ada, dengan backbone
IndoBERT yang di-fine-tune di notebook ini. Pola penyimpanan, penamaan sesi,
caching per tahap, tabel `master_*`, dan plot 300 DPI persis mengikuti V2 STAGED,
supaya angkanya bisa diletakkan berdampingan dengan baseline BERT Inggris.

Seluruhnya berada di folder terpisah **`ACOS-IndoBERT/`**. Repo pipeline Inggris
`ACOS-ASLI/` di folder induk dipakai hanya untuk dibaca: tidak satu berkas pun di
sana diubah, dan tidak satu artefak run pun ditulis ke sana.

```
ACOS-IndoBERT/
  acos_id/          7 modul; torch-free kecuali checkpoint.py
  data/Apps-ACOS/   raw/, processed/, lexicon/ + appsid_quad_{train,dev,test}.tsv
  tokenized_data/   appsid_{split}_quad_bert.tsv + appsid_{split}_pair.tsv
  backbones/        indobert_base_p1/ (hasil rekey) + bert_base_uncased/ (vocab gate 2)
  notebooks/        _build_v4_indobert.py + .ipynb V4 (80 sel / 48 kode, MD5 7de03d6c…)
  build/            skrip verifikasi + keluaran sementara
  results/          appsid_<timestamp>/ (checkpoints, csv, md, plots, logs)
```

| Modul | Isi |
|---|---|
| `acos_id/taxonomy.py` | 13 kategori, label sekuens, patch `get_labels`, gate vs `label_maps.json` |
| `acos_id/build_acos.py` | `processed/*.csv` + `*.jsonl` → `appsid_quad_{train,dev,test}.tsv` |
| `acos_id/tokenize_data.py` | generator `*_quad_bert.tsv` + `*_pair.tsv`, tokenizer-agnostik |
| `acos_id/checkpoint.py` | adapter rekey prefiks `bert.`, `ensure_vocab()`, Gate 1 numerik |
| `acos_id/eda.py` | EDA Indonesia, kontrak keluaran identik `colab_utils.analyze_and_plot_eda` |
| `acos_id/selftest.py` | 5 gate torch-free + Gate 1, `default_paths()` dua-root |
| `acos_id/upstream.py` | menemukan & memasang `Extract-Classify-ACOS/` ke `sys.path` |

Jalur Inggris tetap berjalan sebagai kontrol: ubah `DOMAIN` ke `rest16` di sel 3,
`BACKBONE` otomatis dipaksa ke `bert-en`, `tokenized_base` beralih ke repo
upstream, dan ketiga sel Indonesia (4c, 4d, 5d2) melewati dirinya sendiri.

---

## 2. Keputusan yang menentukan hasil

### 2.1 Dua root, dan `tokenized_base` yang memisahkannya

Berkas Indonesia ada di `indo_root` (`ACOS-IndoBERT/`), modul pipeline dibaca dari
`acos_root` (`ACOS-ASLI/`). Yang tidak jelas sampai dicoba: processor upstream
menyusun path-nya **sendiri**

```python
os.path.join(data_dir, "tokenized_data/" + domain_type + "_train_quad_bert.tsv")
```

sehingga yang bisa dialihkan bukan folder `tokenized_data`-nya, melainkan argumen
`data_dir`. Karena itu ada satu variabel `tokenized_base` — `indo_root` untuk
domain Indonesia, `extract_dir` untuk kontrol Inggris — dan generator notebook
mengalihkan enam sel V2 ke variabel itu. Tanpa itu Step 1 membaca
`Extract-Classify-ACOS/tokenized_data/`, yang tidak memuat berkas `appsid_*`
sama sekali.

`upstream.py` menuntut keempat berkas kunci (`modeling.py`,
`run_classifier_dataset_utils.py`, `eval_metrics.py`,
`bert_utils/tokenization.py`) ada sebelum memasang `sys.path`, jadi folder yang
namanya benar tapi isinya tidak lengkap ditolak di sel 2c — bukan nanti saat
`import modeling`, di mana pesannya tidak menunjuk penyebabnya.

### 2.2 Satu baris ACOS = satu klausa, bukan satu ulasan

`quintuples_weak.csv` memberi kolom `clause` per tuple. Diukur langsung:

| Unit | Baris ACOS | Aspek terpetakan | Opini terpetakan |
|---|---|---|---|
| Klausa | 80.260 | **100 %** dari yang eksplisit | **100 %** |
| Ulasan utuh (`text_norm`) | 43.673 | 61,5 % | 48,0 % |

Hanya 37,6 % klausa yang bisa dicocokkan kembali ke token `text_norm` — sebagian
klausa berasal dari varian normalisasi yang berbeda dari berkas `reviews_clean`.
Memakai ulasan utuh sebagai baris berarti ~40 % span aspek berubah menjadi
implisit palsu tanpa pesan apa pun. Klausa dipilih.

### 2.3 Tokenisasi harus memisahkan tanda baca

Dengan `str.split()` biasa, aspek/opini terpetakan hanya 68,6 % / 60,0 %.
Penyebabnya `text_norm` menyimpan `ribet,bebas` tanpa spasi di sekitar koma,
sehingga `bebas` tidak pernah cocok sebagai token. Dengan pola
`\w+|[^\w\s]` — kata atau tanda baca sebagai token terpisah — angkanya menjadi
100 % dari yang eksplisit. Ini bukan pilihan gaya; 31,4 % span hilang tanpanya.

### 2.4 Kategori tanpa `#` justru jalur paling aman

Kategori Apps-ACOS memakai nama datar (`AUTH_ACCESS`), berbeda dari rest16 yang
memakai `ENTITAS#ATRIBUT`. Itu aman: `eval_metrics.py:226` memecah label gabungan
dengan `ele.split('#')` lalu menyatukan kembali semua bagian kecuali yang terakhir
sebagai kategori, jadi kategori tanpa `#` tidak pernah ambigu.

Jumlah kategori dijaga **13**, sama dengan rest16, sehingga `num_labels` Step 2
tetap 13 × 3 = **39** dan dimensi head tidak berubah terhadap baseline Inggris.

### 2.5 Satu folder cache per backbone

`bert_cache_dir` di V2 selalu `bert_base_uncased`. Di V4 namanya diturunkan dari
`BACKBONE` (`indobert_base_p1`, `bert_base_uncased`, …) dan letaknya di
`indo_root/backbones/`. Kalau keduanya berbagi folder, checkpoint yang satu
menimpa yang lain dan tokenizer tetap memuat vocab yang salah **tanpa error**:
yang terlihat hanya F1 rendah. `BACKBONE`, `indo_root`, dan `tokenized_dir`
karena itu ikut disimpan ke `pipeline_state.pkl` dan dipulihkan bersamanya.

Bobot backbone (±500 MB) tidak dilacak git, jadi `ensure_vocab()` mengunduh
`vocab.txt` (±230 KB) sendiri saat gate membutuhkannya. Sudah diuji: menghapus
kedua folder backbone lalu menjalankan `python -m acos_id.selftest` tetap
menghasilkan lima gate hijau.

---

## 3. Hasil konversi

```
sumber : ACOS-IndoBERT/data/Apps-ACOS/processed/
split diambil dari stage2_{train,val,test}.jsonl berdasarkan review_id

         baris    tuple    aspek eksplisit   opini eksplisit
train    60.159   72.973   51.184            43.271
dev       8.027    9.587    6.588             5.836
test      7.891    9.514    6.576             5.693

dibuang : 4.183 klausa (review_id tidak ada di split mana pun)
[UNK]   : 0 pada seluruh split setelah retokenisasi IndoBERT
span    : 0 rusak, 0 tuple hilang saat retokenisasi
```

Vocab IndoBERT menangani teks ini dengan baik: 0 token `[UNK]` dari 5.619 token
pada sampel 500 kalimat, dan pemecahan subword-nya masuk akal
(`appsnya` → `apps ##nya`, `fitur2nya` → `fitur ##2 ##nya`).

---

## 4. Gerbang verifikasi

Enam gate; lima torch-free dijalankan di laptop ini, satu butuh GPU Colab.

| Gate | Yang diperiksa | Hasil di sini |
|---|---|---|
| `taxonomy` | 13 kategori kode == `label_maps.json`, **urutan sama** | ✅ |
| `dataset` | berkas sumber ada; `review_id` train/dev/test saling lepas | ✅ 0 tumpang tindih |
| `acos_build` | tiap span menunjuk token nyata | ✅ 0 rusak |
| `tokenized` | retokenisasi tidak menghilangkan satu tuple pun | ✅ 0 hilang |
| `gate2_english` | regenerasi data Inggris identik dengan berkas repo | ✅ (1 kalimat, dijelaskan §5) |
| `weights` (Gate 1) | bobot encoder model == checkpoint, numerik | ⏳ butuh torch/Colab |

Semuanya `raise_on_fail=True` di notebook. Alasannya seragam: setiap kegagalan di
daftar ini tidak terlihat dari kurva loss maupun metrik training.

### Gate 1 adalah yang paling penting

`BertForQuadABSA` punya atribut `self.bert` (`modeling.py:1536`), sehingga loader
legacy menetapkan `start_prefix = ''` (`modeling.py:745`) dan mencari key `bert.*`.
Checkpoint `indobenchmark/indobert-base-p1` menyimpan key **tanpa** prefiks itu,
jadi seluruh 414 bobot encoder masuk `missing_keys` — dan logging yang akan
melaporkannya di-comment out di `modeling.py:749-755`. Training berjalan mulus di
atas encoder **acak**, dan F1 yang keluar mengukur kemampuan head belajar dari
representasi acak.

Karena itu sel 4c merekey checkpoint dan sel 5d2 membandingkan tiga tensor
(embedding kata, `layer.0` query, `layer.11` output) dengan `torch.equal`, bukan
sekadar memeriksa nama key. Rekey dijaga idempoten lewat penanda `_rekey.json`:
menjalankannya dua kali menghasilkan `bert.bert.embeddings...`, sama buruknya
dengan tidak merekey.

---

## 5. Temuan yang mengoreksi asumsi sebelumnya

### 5.1 Aturan pengelompokan `*_pair.tsv` bukan yang diduga

Berkas pair di repo ternyata dikelompokkan dengan dua aturan yang tidak
terdokumentasi, keduanya ditemukan dengan membandingkan berkas repo terhadap
`*_quad_bert.tsv`-nya:

1. **Kunci pengelompokan mencakup teks**, bukan hanya `(span_aspek, span_opini)`.
   Dua baris quad berbeda dengan kalimat identik menyatu menjadi satu baris pair.
   Itulah asal `FOOD#QUALITY#2 FOOD#QUALITY#2` pada baris pertama
   `rest16_test_pair.tsv`: kalimat `yu ##m !` muncul dua kali di berkas quad.
2. **Urutan baris di dalam satu kalimat dikelompokkan per label**, mengikuti
   urutan kemunculan pertama label itu — bukan urutan quad apa adanya. Tanpa
   aturan ini, 20 dari 2.279 kalimat rest16 keluar dengan urutan berbeda; isinya
   sama, tapi gate 2 gagal.

Kedua aturan itu ditemukan lewat tiga iterasi gate 2, bukan dari membaca kode.

### 5.2 Cacat data upstream: span lebar-nol

`data/Restaurant-ACOS/rest16_quad_train.tsv` baris 451 memuat span opini `3,3`
(lebar nol). Berkas `tokenized_data` di repo memetakan baris itu **tidak
konsisten**: `*_quad_bert.tsv` memakai remap yang benar (`3,4`, `9,10`, `16,17`)
sementara `*_pair.tsv` memakai offset dari revisi lain (`3,5`, `10,11`) dan
kehilangan satu pasangan sama sekali. Generator mengikuti berkas quad — yang
dipakai Step 1 — dan gate 2 memberi toleransi tepat satu kalimat pada berkas pair
dengan alasan tercatat.

Ini melengkapi catatan cacat upstream sebelumnya (span lebar-nol di rest16 baris
451 memang sudah pernah dicatat, tetapi ketidakkonsistenan quad-vs-pair belum).

### 5.3 `colab_utils.analyze_and_plot_eda` gagal senyap untuk domain baru

```python
domain_map = {"rest16": ("Restaurant-ACOS", "rest16"),
              "laptop": ("Laptop-ACOS", "laptop")}
folder_name, prefix = domain_map.get(domain, ("Restaurant-ACOS", "rest16"))
```

Domain `appsid` tidak error di sana — ia diam-diam membaca Restaurant-ACOS dan
melaporkan statistik dataset Inggris sebagai statistik dataset Indonesia. Karena
tiga salinan `colab_utils.py` di repo harus tetap byte-identik, jalur Indonesia
memakai `acos_id.eda.analyze_and_plot_eda_id` dengan kontrak keluaran yang sama
(nama kolom, nama CSV, keempat nama PNG), bukan patch pada `colab_utils`.

### 5.4 `get_labels` harus dipatch di dua tempat

`CategorySentiProcessor.get_labels()` hanya mengenal `rest*` dan `laptop`; domain
lain membiarkan daftar kategori `None` lalu meledak di `for cate in l`. Patch di
sel 5a saja tidak cukup: `ensure_objects()` dipanggil dari sel 7a, 8a, 8c, dan 9a,
dan setelah restart kernel salah satu dari sel itu bisa menjadi yang pertama
berjalan. `QuadProcessor` tidak terpengaruh (ia mengabaikan `domain_type`), jadi
gejalanya hanya muncul di Step 2 — jauh dari penyebabnya.

### 5.5 Sel dua-root harus disisipkan sesudah sel path V2, bukan sebelum

Percobaan pertama menempatkan sel 2c tepat setelah sel 1b (pelacak progres), yang
tampak wajar karena sel gate di bawahnya memakai keduanya. Hasilnya salah: dua sel
path V2 di antaranya menetapkan `base_project_dir` dan `extract_dir` dari hasil
deteksi Drive, jadi nilai dua-root yang baru ditulis sel 2c justru **ditimpa
kembali** — tanpa pesan apa pun. Sel 2c sekarang berada setelah sel impor
`colab_utils`, sebagai penimpa terakhir.

---

## 6. Sifat dataset yang perlu dilaporkan saat menulis hasil

Tiga hal ini bukan bug, tetapi harus disebut di bagian metode:

**Anotasi lemah, bukan manual.** Kolom `weight` dan `evidence` di
`quintuples_weak.csv` menunjukkan label dibuat otomatis dengan skema pembobotan
(`floor: 0.3`, `saturation_evidence: 2.0`). Angka apa pun yang keluar adalah
kesepakatan dengan pelabelan lemah itu, bukan dengan anotasi manusia.

**Klausa pendek berulang lintas split.** 9,0 % teks klausa unik di test juga ada
di train, menyentuh 14,7 % baris test. Yang berulang adalah klausa sangat pendek
(median 3 kata: `bagus`, `bebas iklan`, `mantap`) — hasil wajar dari
mengklausakan ulasan pendek berbahasa Indonesia. Pemisahan split sendiri bersih
di tingkat `review_id` (0 tumpang tindih, sudah diverifikasi), jadi ini bukan
kebocoran ulasan; tetapi F1 pada baris-baris itu lebih mudah dan sebaiknya
dilaporkan terpisah.

**Multi-label sangat jarang.** Hanya 0,4 % baris pair train (255 dari 65.423)
punya lebih dari satu label berbeda. Head Step 2 tetap multi-label
(`nn.Linear(hidden*2, 39)` + sigmoid) seperti baseline, jadi tidak ada perubahan
arsitektur — hanya perlu diketahui bahwa kapasitas multi-label itu hampir tidak
terpakai.

**Sebaran emosi sangat miring.** 7 kelas, tetapi `anger` (43,5 %) dan `joy`
(36,9 %) mendominasi sementara `fear` hanya 0,9 %. Kolom emosi tidak dipakai
Step 1/2 (itu jalur ACOSE/absa5); dicatat di sini karena akan relevan bila
dataset ini nanti dijalankan lewat V3.

---

## 7. Apa yang sudah diverifikasi dan apa yang belum

Sudah, di mesin ini, tanpa torch:

- 5 gate torch-free hijau (`python -m acos_id.selftest`), dijalankan dari
  `ACOS-IndoBERT/`
- Regenerasi data Inggris identik dengan berkas repo, kecuali satu kalimat cacat
- **Jalur klon segar**: kedua folder backbone dihapus, lalu `selftest` tetap
  menghasilkan lima gate hijau — `ensure_vocab()` mengunduh `vocab.txt` IndoBERT
  dan `bert-base-uncased` sendiri, dan `tokenized_data` dibangun ulang dari nol
- 48 sel kode notebook lolos `compile()`, tidak ada shell-magic berindentasi
- Generator deterministik: dua build berurutan menghasilkan MD5 identik
  (`7de03d6c9442162b2f8e5639a34cd7c0`); V2 dan V3 di repo upstream tidak berubah
- Sel impor, GPU, 1b (pelacak), 2c (dua root), 3 (konfigurasi), sesi, dan 4d
  (gerbang) dieksekusi nyata dengan stub torch. Enam pemeriksaan path lulus:
  `indo_root`/`acos_root` benar, `tokenized_base` = `indo_root`, dan
  `results_base`/`bert_cache_dir`/folder sesi semuanya di bawah `indo_root`
- Pembentuk fitur **upstream asli** menerima data Indonesia: 500 contoh Step 1
  menghasilkan keempat jenis tag span, 0 `[UNK]`; 500 pasangan Step 2 menghasilkan
  `num_labels=39`, rata-rata 1,008 label positif, tidak ada label di luar taksonomi

Belum, dan hanya bisa di Colab:

- **Gate 1** (perbandingan bobot numerik) — butuh `torch.load` dan model terpasang
- Rekey checkpoint IndoBERT sesungguhnya — `prepare_backbone()` butuh torch
- Training Step 1/Step 2, `pair_eval`, dan seluruh angka F1
- Perilaku `save_pipeline_state`/`ensure_objects` pada jalur restart kernel nyata

---

## 8. Cara menjalankan

Colab — buka `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`,
jalankan berurutan. Sel 1b dan 2c wajib diulang setiap restart kernel. Sel 4c
mengunduh + merekey IndoBERT, 4d menjalankan lima gate, 5d2 adalah Gate 1 — kalau
merah, berhenti di situ.

Lokal, dari dalam `ACOS-IndoBERT/`:

```bash
python -m acos_id.selftest              # 5 gate torch-free
python -m acos_id.build_acos            # processed/*.csv → appsid_quad_*.tsv
python -m acos_id.tokenize_data         # → tokenized_data/ dengan vocab IndoBERT
python -m acos_id.eda                   # statistik + 4 plot → build/_eda_id/
python build/_sim_v4_cells.py           # eksekusi sel notebook torch-free
python build/_verify_id_features.py     # fitur upstream vs data Indonesia
python notebooks/_build_v4_indobert.py  # bangun ulang notebook (deterministik)
```

Semua perintah menghitung root dari lokasi paket, jadi tidak butuh argumen path.
`python -m acos_id.checkpoint indobert backbones/indobert_base_p1` menyiapkan
checkpoint tetapi butuh torch — jalankan di Colab.

Kontrol Inggris: ubah `DOMAIN = "rest16"` di sel 3. `BACKBONE` otomatis dipaksa ke
`bert-en` dengan pesan, `tokenized_base` beralih ke `Extract-Classify-ACOS/`, dan
ketiga sel Indonesia (4c, 4d, 5d2) melewati dirinya sendiri.
