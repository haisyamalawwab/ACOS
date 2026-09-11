# 031 — Keterkaitan absa5 vs ACOS-IndoBERT: Sumbu Tugas vs Sumbu Bahasa/Data

> Tanggal: 11 September 2026
> Status: **analisis statis** — dibangun dari report markdown + inspeksi folder fisik, tanpa pelatihan
> Metode: pembacaan report 017/022/023/027/028/030 + `RENCANA_QUINTUPLE_ABSA5.md` + `absa5/README.md` + struktur fisik `absa5/` dan `ACOS-IndoBERT/`

---

## 1. Ringkasan Eksekutif (TL;DR)

`absa5/` dan `ACOS-IndoBERT/` **berkaitan tetapi tidak saling membangun**. Keduanya
mewarisi basis yang sama — backbone **IndoBERT** (`indobenchmark/indobert-base-p1`)
dan kode pipeline `Extract-Classify-ACOS/` yang dibaca saja — namun masing-masing
mengubah **dua sumbu yang berbeda**:

- `absa5/` mengubah **sumbu tugas (task)**: menambah elemen ke-5 (**emosi**) ke tuple
  ACOS 4-elemen menjadi quintuple ACOSE (Aspek–Kategori–Opini–Sentimen–Emosi).
- `ACOS-IndoBERT/` mengubah **sumbu bahasa/data**: membawa pipeline ACOS 4-elemen
  *yang sama* (`BertForQuadABSA`) ke dataset Indonesia **Apps-ACOS/appsid** dengan
  backbone IndoBERT, menghasilkan notebook V4.

Titik sambung terverifikasi: backbone yang sama, basis kode yang sama, dan cadangan
kolom emosi pada dataset appsid (report 023 §6) yang **belum** dijalankan lewat
jalur ACOSE/absa5. Konfigurasi preset `quint_indobert_id` (absa5/config.py:211)
menggabungkan IndoBERT + quintuple tetapi menargetkan data demo restoran
`resto_id`, **bukan** appsid. **Tidak ada run yang menggabungkan appisd + absa5 +
IndoBERT — sambungan itu belum direalisasikan.**

Perbandingan langsung metrik BERT vs IndoBERT **tidak valid secara apples-to-apples**
(report 030): dataset, domain, bahasa, granularitas input, dan kualitas label
berbeda drastis. Angka IndoBERT juga bergantung pada **Gate 1** (verifikasi prefiks
`bert.` di checkpoint) yang belum pernah dijalankan di Colab.

---

## 2. Matriks Perbandingan Dua Folder

| Dimensi | `absa5/` | `ACOS-IndoBERT/` |
|---|---|---|
| **Sumbu yang diubah** | Tugas (task) | Bahasa & data |
| **Elemen tuple** | 5 (Aspek, Kategori, Opini, Sentimen, **Emosi**) | 4 (Aspek, Kategori, Opini, Sentimen) |
| **Model** | `absa5/models.py` (tuple-as-data) + `BertForQuintupleABSA` | `BertForQuadABSA` (upstream) |
| **Backbone default** | `indobenchmark/indobert-base-p1` | `indobenchmark/indobert-base-p1` |
| **Dataset target** | rest16 / resto_id (demo) | appsid (Apps-ACOS, bank digital) |
| **Bahasa** | Inggris (rest16) / Indonesia (resto_id) | Indonesia |
| **Output notebook** | V3 ACOSE (`00_..._V3_ACOSE.ipynb`) | V4 (`00_..._V4_INDOBERT.ipynb` + V4.1) |
| **Kode basis** | `Extract-Classify-ACOS/` (read-only) | `Extract-Classify-ACOS/` via `acos_id/upstream.py` |
| **Dependensi ML** | torch lazy di 3 modul atas | torch-free kecuali `checkpoint.py` |

---

## 3. Analisis Per Sumbu

### 3.1 `absa5/` — Sumbu Tugas (Quadruple → Quintuple ACOSE)

Misi (dari `absa5/README.md`): mengubah tuple ACOS 4-elemen menjadi 5 elemen dengan
menambahkan emosi. Perbedaan fundamental dari upstream: di `Extract-Classify-ACOS/`
jumlah elemen di-hardcode di sepanjang kode; di `absa5` bentuk tuple adalah **data**:

```python
QUAD  = TupleSchema(elements=(ASPECT, CATEGORY, SENTIMENT, OPINION), ...)
QUINT = QUAD.extend(EMOTION)   # satu jalur kode melayani 4 maupun 5 elemen
```

Keputusan desain terverifikasi:
- **Factored label head, bukan joint.** Joint atas 13×3 = 39 output; menambah 5 emosi
  menjadikan 195 (atau 234 dengan `emot_id_netral` 6 label). Pada ~2.4k tuple rest16,
  mayoritas sel joint kosong → default `factored` (13+3+5 = 21 output).
- **Emosi butuh kelas netral.** EmoT (5 label) dari tweet yang terseleksi bermuatan
  emosi; tuple ABSA tidak ("harganya wajar" positif tanpa muatan emosi). `emot_id_netral`
  menambah "netral".
- **Risiko redundansi emosi↔sentimen terukur.** `sentiment_redundancy` menghitung
  H(emosi|sentimen); pada output leksikon terjadi "deterministic renaming" — harus dicek
  ulang pada anotasi manusia sebelum emosi layak dilatih.

### 3.2 `ACOS-IndoBERT/` — Sumbu Bahasa/Data (Dataset Indonesia + IndoBERT)

Misi (dari report 023): menjalankan pipeline ACOS dua tahap yang sudah ada pada
dataset Indonesia baru (appsid, 72.973 quadruple dari 43.673 ulasan aplikasi bank
digital) dengan backbone IndoBERT yang di-fine-tune. Pola penyimpanan, penamaan
sesi, caching per tahap, dan tabel `master_*` mengikuti V2 STAGED supaya angkanya
bisa diletakkan berdampingan dengan baseline BERT Inggris.

Keputusan yang menentukan hasil (report 023 §2):
- **Satu baris = satu klausa**, bukan satu ulasan (100% aspek/opini eksplisit terpetakan
  vs 61.5%/48.0% pada ulasan utuh).
- **Tokenisasi memisahkan tanda baca** (`\w+|[^\w\s]`) — tanpa ini 31.4% span hilang.
- **Kategori datar tanpa `#`** aman karena `eval_metrics.py:226` me-re-split dengan `#`.
- **Satu folder cache per backbone** — cache bersama akan di-timpa tanpa error.

---

## 4. Titik Sambung Terverifikasi

### 4.1 Backbone identik

`absa5/config.py:42-43`:

```python
kind: str = "indobert"
model_name_or_path: str = "indobenchmark/indobert-base-p1"
```

Persis backbone yang dipakai `ACOS-IndoBERT/`. Akibatnya keduanya berbagi **risiko bug
prefiks `bert.` yang sama** — encoder bisa acak tanpa satu pesan error karena logging
`missing_keys` di-comment. Ini masalah tunggal yang muncul di tiga tempat: report 023 §4
Gate 1, `absa5/README.md` §5, dan report 030 §4.3.

### 4.2 Basis kode sama

Keduanya melapis read-only di atas `Extract-Classify-ACOS/`. `ACOS-IndoBERT/`
menyisipkannya ke `sys.path` lewat `acos_id/upstream.py` (report 023 §2.1) dan menuntut
empat berkas kunci ada sebelum pemasangan path.

### 4.3 Cadangan emosi di appsid (sambungan yang belum direalisasi)

Report 023 §6 mencatat dataset appsid membawa kolom emosi (anger 43.5%, joy 36.9%,
fear 0.9%) yang **tidak** dipakai jalur ACOS Step 1/2 (itu jalur ACOSE/absa5), dan akan
relevan "bila dataset ini nanti dijalankan lewat V3". Ini adalah **celah sambungan
potensial**: appsid adalah calon dataset quintuple Indonesia terbesar yang kolom
emosinya sudah ada (anotasi lemah), berpotensi mengisi blocker terbesar absa5 (README:
"dataset quintuple Indonesia"). Hanya hipotesis — belum ada run yang membuktikannya.

### 4.4 Preset yang menghubungkan secara konsep

`absa5/config.py:211` mendefinisikan preset `quint_indobert_id` (name
`indobert_quint_resto`) yang menggabungkan backbone IndoBERT + schema quint, tetapi
menargetkan data demo restoran `resto_id`, bukan appsid. Jadi belum ada konfigurasi yang
menyatukan **appsid + absa5 + IndoBERT** dalam satu run.

---

## 5. Nuansa Penting yang Menahan Overclaim

1. **Dua jalur quintuple tak tertaut.** Untuk tugas quintuple ada dua implementasi:
   paket mandiri `absa5/` **dan** kelas `BertForQuintupleABSA` di `modeling.py` (± baris
   1591, jalur mandiri, belum di-wire ke run script). Keduanya belum tertaut satu sama
   lain (dari `RENCANA_QUINTUPLE_ABSA5.md`).
2. **Metrik IndoBERT bergantung Gate 1.** Jika adapter prefiks `bert.` gagal dan encoder
   terinisialisasi acak, semua angka (Step 1 97.94%, Step 2 67.86%) runtuh. Gate 1 belum
   dijalankan di Colab.
3. **Report adalah ekspektasi analitis.** Sebagian klaim di report gagal diverifikasi
   (memori `acos-plan-reports-are-unverified`); angka F1 khususnya tidak boleh dipakai
   sebagai konklusi "IndoBERT lebih baik dari BERT" karena datasetnya berbeda.

---

## 6. Kesimpulan

`absa5/` dan `ACOS-IndoBERT/` adalah **dua eksperimen independen di atas bahan yang
sama** — backbone IndoBERT dan kode pipeline ACOS — yang masing-masing memperluas satu
sumbu (tugas vs bahasa/data). Nilai gabungannya belum dimanfaatkan: dataset appsid
dengan kolom emosinya adalah kandidat kuat untuk menjalankan jalur quintuple ACOSE pada
skala Indonesia, tetapi sampai ada run yang benar-benar menggabungkan appsid + absa5 +
IndoBERT, keterkaitan itu hanya potensi, bukan fakta terukur.

---

> **Catatan akhir**: Laporan ini tidak menyatakan bahwa satu folder lebih berguna dari
> yang lain, dan tidak mengklaim sambungan yang belum dijalankan. Ia memetakan titik
> sambung yang terverifikasi dari kode/report dan batas-batas yang masih harus dibuktikan.
