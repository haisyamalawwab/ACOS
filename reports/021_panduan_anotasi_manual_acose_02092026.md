# Panduan Anotasi Manual ACOSE untuk Bahasa Indonesia

**Versi:** 1.0
**Tanggal:** 2026-09-02
**Proyek:** ACOS-ASLI (`absa5/`)
**Tugas:** ACOSE — *Aspect-Category-Opinion-Sentiment-Emotion* (Quintuple) Extraction

---

## 1. Apa itu ACOSE?

ACOSE adalah tugas **analisis sentimen berbasis aspek (ABSA)** yang memperluas
tugas ACOS (Cai et al., 2021, doi:10.18653/v1/2021.acl-long.29) dengan satu elemen
tambahan: **emosi**. Hasilnya, setiap unit anotasi (disebut **tuple**) memiliki
**lima elemen**:

```
(aspek, kategori, opini, sentimen, emosi)
```

Definisi elemen di proyek ini (lihat `absa5/schema.py`):

| Elemen | Jenis | Makna |
|---|---|---|
| **aspek** (*aspect*) | rentang kata (span) | frasa dalam teks yang menjadi objek yang diopinikan |
| **kategori** (*category*) | label | klasifikasi aspek ke dalam taksonomi ENTITY#ATTRIBUTE |
| **opini** (*opinion*) | rentang kata (span) | frasa dalam teks yang memuat ekspresi sentimen/emosi |
| **sentimen** (*sentiment*) | label | polaritas penulis terhadap aspek (negatif / netral / positif) |
| **emosi** (*emotion*) | label | emosi penulis terhadap aspek tersebut |

Elemen **aspek** dan **opini** berupa *rentang kata* (offset token whitespace,
format `mulai,akhir` dengan `akhir` eksklusif). Elemen **kategori**, **sentimen**,
dan **emosi** berupa *label*.

Satu kalimat dapat memiliki **lebih dari satu tuple**. Video dari data demo
(`data/Demo-Resto-ID/resto_id_quint_train.tsv`):

```
makanan nya enak sekali tapi pelayanan nya lambat banget
```

Kalimat di atas mengandung **dua tuple**:

1. `0,1 MAKANAN#KUALITAS 2 2,4 senang` — aspek "makanan", kategori
   MAKANAN#KUALITAS, sentimen positif, opini "enak sekali", emosi `senang`.
2. `5,6 PELAYANAN#UMUM 0 7,9 marah` — aspek "pelayanan", kategori
   PELAYANAN#UMUM, sentimen negatif, opini "lambat banget", emosi `marah`.

> **Catatan tentang rentang:** offset adalah indeks token hasil pemisahan
> whitespace (`text.split()`), bukan indeks karakter, dan `akhir` bersifat
> eksklusif. Contoh: dalam `makanan nya enak sekali`, token ke-2 adalah "enak"
> dan ke-4 (eksklusif) mencakup "enak sekali" = indeks 2,4.

---

## 2. Format data anotasi

### 2.1 Format tuple pada satu baris

Setiap baris file `.tsv` terdiri dari:

```
[Teks ulasan]\t[tuple-1]\t[tuple-2]...
```

Setiap tuple memiliki lima kolom yang urutannya tetap (lihat `QUINT` di
`schema.py`, urutan on-disk):

```
aspek kategori sentimen opini emosi
```

- `aspek` — rentang `mulai,akhir` (mis. `0,1`), atau `-1,-1` jika aspek **implisit**.
- `kategori` — label dari taksonomi (mis. `FOOD#QUALITY` / `MAKANAN#KUALITAS`).
- `sentimen` — `0` (negatif), `1` (netral), atau `2` (positif).
- `opini` — rentang `mulai,akhir`, atau `-1,-1` jika opini **implisit**.
- `emosi` — label dari set emosi (mis. `senang`, `marah`, `netral`).

Contoh satu tuple:

```
0,1 MAKANAN#KUALITAS 2 2,4 senang
```

> Bagian `Teks ulasan` tidak ikut di-anotasi ulang; ia adalah sumber rentang dan
> konteks untuk menentukan label. Tugas anotator adalah mengisi **kelima** elemen
> (atau menilai ulang elemen yang sudah terisi).

### 2.2 Aspek dan opini implisit

Tidak semua ulasan menyebut aspek atau opini secara eksplisit. Dua kasus khusus:

- **Aspek implisit** (`-1,-1`): objek yang diopinikan tidak disebut sebagai kata
  dalam teks, tapi dapat disimpulkan dari konteks. Contoh (dari data demo):
  `saya selalu kembali ke sini setiap minggu` — aspeknya "restoran" (`RESTORAN#UMUM`)
  tidak tertulis, tapi jelas dari kata "kembali ke sini".
- **Opini implisit** (`-1,-1`): tidak ada kata yang mengekspresikan sentimen secara
  langsung. Contoh (data demo): `tidak akan pernah datang lagi ke tempat ini` —
  opini diimplikasikan oleh seluruh kalimat, ditandai `-1,-1`.

Konvensi ini diwarisi dari ACOS. Panjang opini implisit (`-1,-1`) sama-sama
menggunakan penanda yang sama dengan aspek implisit (lihat `schema.IMPLICIT`).

---

## 3. Taksonomi label

Label harus berasal dari kosa kata tertutup yang terdaftar di `absa5/taxonomy.py`.
Gunakan versi bahasa Indonesia untuk anotasi manual.

### 3.1 Kategori (13 label restoran Indonesia)

Taksonomi `resto_id` — pemetaan 1:1 dari SemEval-2016 Task 5 restaurant
(Pontiki et al., 2016, doi:10.18653/v1/S16-1002). 13 label yang **terdaftar di
registry** (`absa5/taxonomy.py`):

| Label Indonesia | Padanan Inggris |
|---|---|
| `RESTORAN#UMUM` | RESTAURANT#GENERAL |
| `RESTORAN#HARGA` | RESTAURANT#PRICES |
| `RESTORAN#LAINNYA` | RESTAURANT#MISCELLANEOUS |
| `PELAYANAN#UMUM` | SERVICE#GENERAL |
| `MAKANAN#UMUM` | FOOD#GENERAL |
| `MAKANAN#KUALITAS` | FOOD#QUALITY |
| `MAKANAN#PILIHAN` | FOOD#STYLE_OPTIONS |
| `MAKANAN#HARGA` | FOOD#PRICES |
| `MINUMAN#PILIHAN` | DRINKS#STYLE_OPTIONS |
| `MINUMAN#HARGA` | DRINKS#PRICES |
| `MINUMAN#KUALITAS` | DRINKS#QUALITY |
| `SUASANA#UMUM` | AMBIENCE#GENERAL |
| `LOKASI#UMUM` | LOCATION#GENERAL |

> `MINUMAN#UMUM` (DRINKS#GENERAL) **tidak** terdaftar di set `resto_id` saat ini
> (set rest16 asli juga tidak memilikinya). Jika cakupan minuman umum diperlukan,
> itu adalah perluasan taksonomi yang harus didaftarkan dulu, bukan label ad hoc.

**Format `${ENTITAS}#${ATRIBUT}`.** Ada enam entitas: RESTORAN, PELAYANAN,
MAKANAN, MINUMAN, SUASANA, LOKASI. `ATRIBUT` umumnya UMUM, dengan varian
KUALITAS, PILIHAN, HARGA. `UMUM` dipakai ketika atribut tidak spesifik
(misalnya "makanannya enak" → `MAKANAN#UMUM`, bukan hanya kualitas).

### 3.2 Sentimen (3 label)

| Nilai | Makna |
|---|---|
| `0` | negatif |
| `1` | netral |
| `2` | positif |

Ini adalah pengkodean numerik ACOS (Cai 2021). Untuk anotasi manual, Anda dapat
menulis `negatif` / `netral` / `positif` pada tahap isian, namun saat disimpan ke
file jadikan numerik (`0`/`1`/`2`) menyesuaikan registry `SENTIMENTS['id']` yang
bisa diterima parser (lihat `taxonomy.SENTIMENTS`).

### 3.3 Emosi (5 + netral)

Set emosi default untuk anotasi adalah `emot_id_netral`:
**sedih, marah, cinta, takut, senang, netral**.

Alasan set ini dipakai: EmoT dibangun dari tweet yang dipilih karena bermuatan
emosi (Saputri et al., 2018, doi:10.1109/IALP.2018.8629262). Tuple ABSA **tidak**
selalu bermuatan emosi — "harganya wajar" bersentimen positif tapi tanpa muatan
emosi. Memaksanya masuk salah satu dari lima kelas EmoT akan menyuntikkan noise.
GoEmotions mempertahankan kelas `neutral` dengan alasan yang sama (Demszky et al.,
2020, doi:10.18653/v1/2020.acl-main.372). Karena itu `emot_id_netral` menambahkan
kelas `netral`.

| Label | Petunjuk umum |
|---|---|
| `sedih` | kekecewaan, penyesalan, kesedihan |
| `marah` | kemarahan, kekesalan, jengkel |
| `cinta` | afeksi kuat, kesukaan mendalam, "favorit" |
| `takut` | kekhawatiran, kecemasan, keraguan |
| `senang` | kebahagiaan, kepuasan |
| `netral` | **tidak ada muatan emosi** (faktual) |

> Set lain tersedia (`emot_id` tanpa netral, `nusaparagraph`, `ekman`,
> `plutchik`, `goemotions`) — lihat `taxonomy.py`. Untuk panduan ini, default
> adalah `emot_id_netral`.

---

## 4. Aturan anotasi elemen per elemen

### 4.1 Mencari aspek (span)

- Pilih **rentang kata minimal yang merujuk pada entitas yang diopinikan**.
- Sertakan kata penunjuk seperti "nya" bila bagian dari frasa aspek alami
  (mis. `makanan` dalam "makanan nya enak" → aspek indeks 0,1 "makanan").
  Konsistensi lebih penting daripada kemewahan: pilih konvensi dan terapkan seragam.
- Jika entitas tidak muncul sebagai kata → aspek implisit `-1,-1`.

### 4.2 Menentukan kategori (label)

- Selalu **satu kategori per aspek**. Jika sebuah aspek memuat lebih dari satu
  makna, pecah menjadi tuple terpisah hanya jika aspeknya berbeda.
- Pilih dari 13 label Indonesia pada §3.1. Saat ragu antara `UMUM` dan atribut
  spesifik, pilih yang paling netral yang tetap benar (`UMUM` untuk umum).
- Contoh: "rasa nya mantap" → `MAKANAN#KUALITAS` (rasa = kualitas makanan);
  "menu nya sedikit" → `MAKANAN#PILIHAN`.

### 4.3 Menemukan opini (span)

- **Span opini adalah kata-kata yang mengekspresikan sentimen atau emosi penulis
  terhadap aspek**, mis. "enak sekali", "lambat banget", "mahal".
- Rentang biasanya berdekatan dengan aspek, namun bisa di mana saja.
- Jika tidak ada kata yang mengekspresikan sikap → opini implisit `-1,-1`.

### 4.4 Menentukan sentimen (label)

- Evaluasi polaritas **penulis terhadap aspek pada tuple itu**, bukan tone
  keseluruhan kalimat.
- `2` positif, `0` negatif, `1` netral (tidak memihak / faktual).

### 4.5 Menentukan emosi (label)

- Beri label emosi **penulis terhadap aspek pada baris itu**, bukan emosi
  keseluruhan ulasan. Satu ulasan dengan dua aspek boleh punya dua emosi berbeda.
- Gunakan `opini` sebagai bukti utama. Jika opini implisit, gunakan kalimat penuh;
  jika tetap tidak ada bukti emosi, pilih label terdekat — **jangan mengosongkan**.
- **Sentimen dan emosi tidak boleh disamakan begitu saja.** "harganya wajar"
  sentimennya positif tetapi emosinya bukan `senang` yang kuat; jangan memetakan
  positif → `senang` secara mekanis. Dasar teoretis: valensi hanyalah satu sumbu
  dari ruang afek, bukan seluruh ruangnya (Russell, 1980, doi:10.1037/h0077714).

---

## 5. Aturan umum dan kasus tepi

1. **Satu tuple per (aspek, opini) yang independen.** Jika sebuah kalimat punya
   dua aspek berbeda, tulis dua tuple.
2. **Jangan mengosongkan kolom.** Jika tidak yakin, isi dan beri catatan di kolom
   `notes`.
3. **Konsistensi rentang.** Offset token whitespace, `akhir` eksklusif,
   dihitung dari awal kalimat. Jangan menyertakan tanda baca yang tidak perlu
   kecuali merupakan bagian dari frasa aspek/opini.
4. **Emosi vs sentimen.** Emosi tidak dijatuhkan dari sentimen; pilih berdasarkan
   bukti teks, bukan mekanisme.
5. **Aspek/opini implisit** hanya bila benar-benar tidak ada kata yang merujuk.
   Jangan menjadikan implisit sebagai jalan pintas.

---

## 6. Kutipan & referensi untuk panduan ini

Proyek mencatat sitasi machine-readable di `absa5/references.py` (DOI diverifikasi
via Crossref, 2026-08-28):

- **Cai, Xia & Yu 2021** — *Aspect-Category-Opinion-Sentiment Quadruple Extraction
  with Implicit Aspects and Opinions*. ACL 2021. doi:10.18653/v1/2021.acl-long.29
  (sumber tugas ACOS yang diperluas).
- **Pontiki et al. 2016** — *SemEval-2016 Task 5: Aspect Based Sentiment
  Analysis*. doi:10.18653/v1/S16-1002 (sumber taksonomi ENTITY#ATTRIBUTE).
- **Saputri, Mahendra & Adriani 2018** — *Emotion Classification on Indonesian
  Twitter Dataset*. IALP 2018. doi:10.1109/IALP.2018.8629262 (korpus EmoT).
- **Demszky et al. 2020** — *GoEmotions: A Dataset of Fine-Grained Emotions*.
  ACL 2020. doi:10.18653/v1/2020.acl-main.372 (alasan kelas netral).
- **Russell 1980** — *A circumplex model of affect*. JPSP.
  doi:10.1037/h0077714 (valensi vs emosi sebagai sumbu berbeda).

> **Ketelitian:** pernyataan di atas seluruhnya dirangkum langsung dari berkas
> kode `absa5/taxonomy.py`, `absa5/schema.py`, `absa5/emotion.py`,
> `absa5/references.py`, dan data `data/Demo-Resto-ID/*.tsv` di repo ini. Ini
> adalah penjelasan aturan anotasi yang sudah diimplementasikan di kode; panduan
> ini tidak mengklaim validasi empiris terhadap data anotasi nyata — dataset
> quintuple bahasa Indonesia yang sesungguhnya masih menunggu anotasi (lihat
> `absa5/README.md`).

---

## 7. Catatan verifikasi dan keterbatasan

- Data demo `Demo-Resto-ID` hanya untuk membuktikan pipeline berjalan; warnanya
  **bukan** dataset dan angka apa pun darinya tidak disiplin. Panduan ini
  menjelaskan format dan aturan yang dipakai kode, bukan hasil anotasi final.
- Taksonomi `resto_id` adalah pemetaan 1:1 dari `rest16` untuk keterbandingan
  dengan baseline Inggris. Perbedaannya hanya pada label `MINUMAN#UMUM`
  (DRINKS#GENERAL): tidak ada di set `rest16` asli **dan** tidak terdaftar di
  set `resto_id` saat ini — ia bukan label yang sah hingga didaftarkan di
  `taxonomy.py`.
