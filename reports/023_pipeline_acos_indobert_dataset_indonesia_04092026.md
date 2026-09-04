# 023 — Pipeline ACOS IndoBERT untuk Dataset Indonesia (Apps-ACOS)

> Tanggal: 4 September 2026
> Deliverable: paket `acos_id/`, notebook `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`
> Status: **belum pernah dilatih** — semua verifikasi di bawah torch-free atau berbasis berkas

---

## 1. Yang dibangun

Dataset Indonesia baru (`data/Apps-ACOS/`, 96.417 quintuple lemah dari 43.673
ulasan aplikasi bank digital) dijalankan lewat pipeline ACOS dua tahap yang sudah
ada, dengan backbone IndoBERT yang di-fine-tune di notebook ini. Pola
penyimpanan, penamaan sesi, caching per tahap, tabel `master_*`, dan plot 300 DPI
persis mengikuti V2 STAGED, supaya angkanya bisa diletakkan berdampingan dengan
baseline BERT Inggris.

| Berkas | Isi |
|---|---|
| `acos_id/taxonomy.py` | 13 kategori, label sekuens, patch `get_labels`, gate vs `label_maps.json` |
| `acos_id/build_acos.py` | `processed/*.csv` + `*.jsonl` → `appsid_quad_{train,dev,test}.tsv` |
| `acos_id/tokenize_data.py` | generator `tokenized_data/*_quad_bert.tsv` + `*_pair.tsv`, tokenizer-agnostik |
| `acos_id/checkpoint.py` | adapter rekey prefiks `bert.` + Gate 1 perbandingan bobot numerik |
| `acos_id/eda.py` | EDA Indonesia dengan kontrak keluaran identik `colab_utils.analyze_and_plot_eda` |
| `acos_id/selftest.py` | 5 gate torch-free + Gate 1 |
| `notebooks/_build_v4_indobert.py` | generator notebook, berlapis di atas `_build_staged_v2.py` |
| `notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` | 80 sel / 48 kode, MD5 `8b2b72e4…` |

Tidak satu pun berkas di `Extract-Classify-ACOS/` diubah. Seluruh perbedaan
Indonesia masuk lewat patch runtime atau berkas data baru, sehingga jalur Inggris
tetap berjalan sebagai kontrol: cukup ubah `DOMAIN` kembali ke `rest16` di sel 3.

---

## 2. Keputusan yang menentukan hasil

### 2.1 Satu baris ACOS = satu klausa, bukan satu ulasan

`quintuples_weak.csv` memberi kolom `clause` per tuple. Diukur langsung:

| Unit | Baris ACOS | Aspek terpetakan | Opini terpetakan |
|---|---|---|---|
| Klausa | 80.260 | **100 %** dari yang eksplisit | **100 %** |
| Ulasan utuh (`text_norm`) | 43.673 | 61,5 % | 48,0 % |

Hanya 37,6 % klausa yang bisa dicocokkan kembali ke token `text_norm` — sebagian
klausa berasal dari varian normalisasi yang berbeda dari berkas `reviews_clean`.
Memakai ulasan utuh sebagai baris berarti ~40 % span aspek berubah menjadi
implisit palsu tanpa pesan apa pun. Klausa dipilih.

### 2.2 Tokenisasi harus memisahkan tanda baca

Dengan `str.split()` biasa, aspek/opini terpetakan hanya 68,6 % / 60,0 %.
Penyebabnya `text_norm` menyimpan `ribet,bebas` tanpa spasi di sekitar koma,
sehingga `bebas` tidak pernah cocok sebagai token. Dengan pola
`\w+|[^\w\s]` — kata atau tanda baca sebagai token terpisah — angkanya menjadi
100 % dari yang eksplisit. Ini bukan pilihan gaya; 31,4 % span hilang tanpanya.

### 2.3 Kategori tanpa `#` justru jalur paling aman

Kategori Apps-ACOS memakai nama datar (`AUTH_ACCESS`), berbeda dari rest16 yang
memakai `ENTITAS#ATRIBUT`. Itu aman: `eval_metrics.py:226` memecah label gabungan
dengan `ele.split('#')` lalu menyatukan kembali semua bagian kecuali yang terakhir
sebagai kategori, jadi kategori tanpa `#` tidak pernah ambigu.

Jumlah kategori dijaga **13**, sama dengan rest16, sehingga `num_labels` Step 2
tetap 13 × 3 = **39** dan dimensi head tidak berubah terhadap baseline Inggris.

### 2.4 Satu folder cache per backbone

`bert_cache_dir` di V2 selalu `bert_base_uncased`. Di V4 namanya diturunkan dari
`BACKBONE` (`indobert_base_p1`, `bert_base_uncased`, …). Kalau keduanya berbagi
folder, checkpoint yang satu menimpa yang lain dan tokenizer tetap memuat vocab
yang salah **tanpa error**: yang terlihat hanya F1 rendah. `BACKBONE` karena itu
juga ikut disimpan ke `pipeline_state.pkl` dan dipulihkan bersamanya.

---

## 3. Hasil konversi

```
sumber : data/Apps-ACOS/processed/
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

- 5 gate torch-free hijau (`python -m acos_id.selftest`)
- Regenerasi data Inggris identik dengan berkas repo, kecuali satu kalimat cacat
- 48 sel kode notebook lolos `compile()`, tidak ada shell-magic berindentasi
- Generator deterministik: dua build berurutan menghasilkan MD5 identik
  (`8b2b72e4a36ded2d707459d20825ea17`); V2 dan V3 tidak berubah
- Sel 3 (impor), 4 (GPU), 1b (pelacak), 1s (paket), 3 (konfigurasi), sesi, dan
  4d (gerbang) dieksekusi nyata dengan stub torch — `DOMAIN=appsid`,
  `BACKBONE=indobert`, folder sesi `results/appsid_<ts>/`
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

```
Colab:  buka notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb
        jalankan berurutan; 1s dan 1b wajib diulang setiap restart kernel
        sel 4c mengunduh + merekey IndoBERT, 4d menjalankan 5 gate
        sel 5d2 adalah Gate 1 — kalau merah, berhenti, jangan lanjut

Lokal:  python -m acos_id.selftest .                # 5 gate torch-free
        python -m acos_id.build_acos data           # konversi ulang berkas ACOS
        python -m acos_id.eda . build/_eda_id       # EDA + 4 plot
        python build/_verify_id_features.py         # fitur upstream vs data ID
        python notebooks/_build_v4_indobert.py      # bangun ulang notebook
```

Kontrol Inggris: ubah `DOMAIN = "rest16"` di sel 3. `BACKBONE` otomatis dipaksa
ke `bert-en` dengan pesan, dan ketiga sel Indonesia (4c, 4d, 5d2) melewati
dirinya sendiri.
