# 024 — Dev Log: Rencana Notebook ACOS-IndoBERT untuk Rest16 & Laptop

> Tanggal: 5 September 2026
> Deliverable yang direncanakan: notebook `.ipynb` baru di `ACOS-IndoBERT-Rest16/`
> Status: **analisis & desain** — belum ada notebook yang ditulis, belum ada yang dilatih
> Catatan: laporan ini mencatat hasil analisis sebagai **dev log / dev report awal**,
> bukan klaim bahwa sesuatu sudah berjalan.

---

## 1. Ringkasan permintaan

Menyiapkan **file notebook `.ipynb` baru untuk ACOS-IndoBERT** dengan:
- dataset **rest16** dan **laptop** (dua-duanya teks Inggris, SemEval);
- dilatih dengan **IndoBERT** (`indobenchmark/indobert-base-p1`);
- seluruh hasil disimpan di folder khusus **`ACOS-IndoBERT-Rest16/`**.

Permintaan ini dibedakan dari notebook V4 (`00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`)
yang sudah ada, yang memakai dataset **appsid** (Indonesia, ulasan aplikasi bank)
dan menyimpan hasilnya di `ACOS-IndoBERT/results/appsid_<ts>/`.

---

## 2. Kondisi awal yang terukur di mesin ini

| Item | Kondisi |
|---|---|
| `ACOS-IndoBERT-Rest16/` | **kosong** (hanya folder, 0 berkas) |
| `data/Restaurant-ACOS/rest16_quad_{train,dev,test}.tsv` | ada (train 181 KB, dev 18 KB, test 68 KB) |
| `data/Laptop-ACOS/laptop_quad_{train,dev,test}.tsv` | ada (train 362 KB, dev 39 KB, test 99 KB) |
| `ACOS-IndoBERT/` | paket `acos_id/` (7 modul) + notebook V4 + `tokenized_data` appsid |
| `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` | generator notebook V4 (908 baris), lapis di atas V2 STAGED |

Kedua dataset Inggris sudah ada di repo, jadi notebook Rest16/Laptop tidak perlu
mengunduh data — hanya perlu **menunjuk ke berkas yang sudah ada** (atau menyalin
ke root sendiri bila ingin sepenuhnya mandiri).

---

## 3. Bagaimana notebook V4 dibangun (pola yang harus diikuti)

Notebook V4 **bukan ditulis tangan**; ia dihasilkan oleh generator
`_build_v4_indobert.py` yang:

1. menjalankan `_build_staged_v2.main()` lebih dulu (membangun notebook V2),
2. memuat sel-selnya, lalu
3. menyisipkan/menimpa sel yang berubah untuk domain/bahkan backbone Indonesia.

Konsekuensinya ada **dua kemungkinan pola** untuk notebook baru — dan keduanya
belum diputuskan:

- **(A) Satu generator baru** `_build_rest16_laptop.py` yang berlapis di atas V4
  (jadi V4 → Rest16/Laptop). Hasil: satu notebook yang memuat kedua domain sekaligus
  (ganti `DOMAIN` `rest16`/`laptop`), hasil di `ACOS-IndoBERT-Rest16/`.
- **(B) Salin/pisah** V4 menjadi notebook mandiri rest16/laptop dengan jalan
  simpan sendiri. Lebih sederhana tetapi menyalin 80 sel dan rentan divergensi.

Belum dipilih; ini keputusan desain yang perlu dimatangkan sebelum menulis kode.

---

## 4. Konflik desain yang menentukan (dan keputusan yang diambil)

### 4.1 Rest16 & laptop adalah teks **Inggris**, IndoBERT adalah model **Indonesia**

V4 memaksa `BACKBONE = "bert-en"` untuk semua domain Inggris (`rest16`, `laptop`)
tepat karena alasannya: vocab IndoBERT hampir seluruh token Inggris menjadi `[UNK]`,
dan F1 yang keluar tidak bisa dibandingkan dengan baseline BERT Inggris.

Permintaan ini justru memakai **IndoBERT asli** pada teks Inggris. Karena itu
diklarifikasi ke pengguna, dan **keputusan yang diambil: `IndoBERT asli pada
rest16/laptop`** — yaitu eksperimen **cross-lingual** (model Indonesia melihat teks
Inggris), bukan kontrol valid.

### 4.2 Apa artinya bagi angka yang nanti keluar

Karena konflik di atas, laporan hasil harus jujur: notebook ini menghasilkan
eksperimen cross-lingual, dengan risiko:
- vocab IndoBERT memetakan sebagian besar token Inggris ke `[UNK]`;
- F1 yang mungkin jauh di bawah baseline BERT Inggris pada dataset yang sama;
- perbandingan "Rest16+IndoBERT vs Rest16+BERT" TIDAK imparsial — backbone berbeda
  dan material berbeda.

Padding label `[UNK]` yang masif juga membuat prosesor/konversi data perlu
diperiksa, bukan diasumsikan (lihat §6).

### 4.3 Folder simpan terpisah

Semua hasil (sesi bertimestamp, checkpoint, csv, md, plots, logs) disimpan di
`ACOS-IndoBERT-Rest16/`, bukan di `ACOS-IndoBERT/results/` (yang dipakai appsid).
Ini menjaga kedua eksperimen tidak saling menimpa, dan folder `results/` di root
upstream tetap bersih.

---

## 5. Komponen yang bisa dipakai ulang dari V4

Dari pembacaan `_build_v4_indobert.py`, sel-sel berikut sudah menangani backbone
IndoBERT dan **tidak** bergantung pada domain Indonesia, sehingga bisa dipakai
ulang untuk Rest16/Laptop dengan penyesuaian:

| Sel | Isi | Perlu ubah untuk rest16/laptop? |
|---|---|---|
| 4c | Adapter checkpoint IndoBERT (rekey prefiks `bert.`) | Ya — ganti target root ke `ACOS-IndoBERT-Rest16/backbones/` |
| 5d2 | Gate 1 numerik (bobot encoder == checkpoint) | Tidak, backbone sama |
| 2 (dua root) | `indo_root` / `acos_root` | Ya — `indo_root` = `ACOS-IndoBERT-Rest16/` |
| 4d | Gerbang data Indonesia (5 gate torch-free) | **Risiko** — gate `taxonomy` & `dataset` spesifik appsid; untuk rest16/laptop sebagian gate perlu disesuaikan/lewat |
| EDA | memakai `acos_id.eda` untuk Indonesia | Harus kembali ke `analyze_and_plot_eda` Inggris (rest16/laptop sudah dikenal `colab_utils`) |

Yang **tidak** boleh ikut: patch `get_labels` Indonesia (`acos_id.taxonomy.patch_processor_labels`),
karena domain `rest16`/`laptop` sudah dikenali `CategorySentiProcessor.get_labels()`
secara native.

---

## 6. Risiko yang harus dijaga gate (calon daftar untuk notebook baru)

Dari pengalaman V4, setiap kegagalan berikut tidak terlihat dari kurva loss maupun
metrik training — harus dijaga oleh gate, bukan diasumsikan:

1. **Rekey prefiks `bert.`** — checkpoint IndoBERT menyimpan key tanpa prefiks,
   dan loader legacy memakai `start_prefix=''` (karena `BertForQuadABSA` punya
   `self.bert`); tanpa rekey seluruh bobot encoder masuk `missing_keys` dan
   logging-nya di-comment out (`modeling.py:749-755`). Threshold: seluruh 414 key
   encoder diberi prefiks, dan Gate 1 (`torch.equal`) LULUS.
2. **`config.vocab_size` ≠ jumlah token `vocab.txt`** — untuk `indobert-base-p1`,
   `config.vocab_size = 50000` sedangkan `vocab.txt` 30.521 token. Jangan pakai
   `config.vocab_size` sebagai jumlah token.
3. **`get_labels()` untuk rest16/laptop** — sudah dikenali upstream, jadi patch
   Indonesia tidak boleh ikut (kalau terlanjur, berpotensi salah taksonomi).
4. **Tingkat `[UNK]`** pada teks Inggris dengan vocab IndoBERT — perlu dukur dan
   dilaporkan, bukan disembunyikan. Ini pembeda utama dari eksperimen appsid.
5. **Satu folder cache per backbone** — IndoBERT dan bert-base-uncased tidak boleh
   berbagi folder, karena checkpoint yang satu menimpa yang lain dan tokenizer
   memuat vocab yang salah tanpa error (gejala hanya F1 rendah).
6. **Cacat upstream rest16** — `rest16_quad_train.tsv` baris 451 memuat span opini
   lebar-nol `3,3`; berkas `tokenized_data` di repo memetakannya tidak konsisten
   antara `*_quad_bert.tsv` dan `*_pair.tsv`. Generator sebaiknya mengikuti berkas
   quad, dan gate 2 memberi toleransi satu kalimat.

---

## 7. Apa yang belum diputuskan / belum ditulis

Agar tidak overclaim, ini yang **belum** dilakukan:

- Notebook `.ipynb` itu sendiri **belum ditulis** (folder target masih kosong).
- Pilihan pola generator (A satu generator terlapis vs B salinan mandiri) **belum
  diputuskan**.
- Jalur simpan dua-root untuk `ACOS-IndoBERT-Rest16/` **belum diimplementasikan**.
- Tidak ada apa pun yang **sudah dilatih** di mesin ini (mesin lokal tak punya
  torch/transformers; training hanya bisa di Colab).

Langkah logis berikutnya, bila diminta: memutuskan pola generator, menulis
`_build_rest16_laptop.py` (atau salinan), membangun notebook, lalu diverifikasi
torch-free dulu (gate + compile) sebelum training di Colab.
