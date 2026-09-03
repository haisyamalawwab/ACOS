# Bagian 022c — Kategori: Memberi Nama Resmi pada Benda

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Sebelumnya:** [022b — Aspek & Opini](./022b_aspek_dan_opini.md)

---

## Sebuah masalah kecil yang ternyata besar

Di bab 022b, kita belajar menemukan **benda** (aspek). Makanan. Pelayanan. Harga.
Tempat. Kedengarannya mudah, bukan?

Tapi sekarang mari saya ceritakan masalah yang muncul begitu kita mulai bekerja
dengan banyak ulasan sungguhan: **setiap orang menyebut benda yang sama dengan
kata yang berbeda.**

Coba kumpulkan beberapa ulasan tentang satu hal yang sama — katakanlah soal
pelayanan:

> "Pelayanannya ramah banget."
> "Karyawannya baik."
> "Orangnya nempel terus, agak ganggu."
> "Kasirnya jutek banget."

Semua ini sebenarnya membicarakan hal yang sama: **bagaimana pihak restoran
melayani.** Tapi kata-katanya beda-beda: pelayanannya, karyawannya, orangnya,
kasirnya.

Sekarang bayangkan Anda harus menaruh semuanya ke dalam satu kotak bernama
"pelayanan." Kalau Anda menyimpannya mentah-mentah, Anda punya puluhan kata
berbeda yang membingungkan. Tapi kalau Anda menyortirnya ke satu nama yang sama,
semuanya jadi rapi.

**Nama resmi yang menampung semua kata beda ini kita sebut kategori.**

## Analogi menyortir cucian

Cara paling gampang memahaminya: bayangkan Anda punya banyak baju dan cuma dua
keranjang — "baju keluar" dan "baju tidur." Anda tidak peduli mereknya. Yang
penting setiap baju masuk ke keranjang yang benar.

Kategori itu persis keranjang itu. Kita tidak peduli apakah orang bilang
"pelayanannya", "karyawannya", atau "kasirnya" — yang penting semuanya masuk ke
keranjang bernama **pelayanan**.

Kenapa ini penting untuk komputer? Karena komputer kesulitan mengerti bahwa
"karyawan" dan "pelayan" itu maksudnya sama. Manusia tahu dari pengalaman; komputer
tidak punya pengalaman itu. Dengan mengelompokkan semuanya ke satu kategori yang
sama, kita **menerjemahkan keberagaman bahasa menjadi satu bahasa yang seragam** —
bahasa yang bisa dipahami komputer.

## Bentuk nama kategorinya

Nama kategori di proyek ini selalu terdiri dari **dua bagian** yang dipisah tanda
pagar (`#`):

```
BENDA-BESAR # SIFAT/ATRIBUT
```

- **Bagian kiri** — benda besarnya: makanan, minuman, pelayanan, suasana, lokasi,
  atau restoran itu sendiri.
- **Bagian kanan** — sifat spesifiknya: kualitas, harga, pilihan... atau "umum"
  kalau tidak spesifik.

Contoh: `MAKANAN#KUALITAS` (kualitas makanan), `MAKANAN#HARGA` (harga makanan),
`MAKANAN#PILIHAN` (pilihan menu). Perhatikan: posisinya penting. `MAKANAN#HARGA`
bukan `HARGA#MAKANAN`.

## Empat belas? Tiga belas? Mari kita hitung dengan teliti

Sekarang bagian yang harus kita sepakati bersama: berapa banyak "keranjang"
kategori yang kita punya?

Untuk buku ini, semuanya sudah ditentukan sebelumnya — dan jumlahnya **tiga belas**
untuk domain restoran. Semua tiga belas kategori ini dirancang agar cocok
*satu-lawan-satu* dengan standar internasional yang sudah dipakai peneliti di seluruh
dunia. Alasannya penting: supaya hasil penelitian dari bahasa Indonesia bisa
**dibandingkan** secara adil dengan penelitian bahasa lain.

Ini tabel ketiga belas keranjangnya, dengan contoh kata yang biasanya masuk ke
masing-masing:

| Kategori | Kapan dipakai | Contoh kata dalam ulasan |
|---|---|---|
| **RESTORAN#UMUM** | tentang tempat makan secara umum | "tempat ini", "restonya" |
| **RESTORAN#HARGA** | tentang harga keseluruhan | "harganya" |
| **RESTORAN#LAINNYA** | tentang resto yang tak masuk kategori lain | "kebersihan dapurnya" |
| **PELAYANAN#UMUM** | tentang pelayanan / karyawan | "pelayanannya", "karyawannya" |
| **MAKANAN#UMUM** | tentang makanan secara umum | "makanannya", "masakannya" |
| **MAKANAN#KUALITAS** | tentang rasa / mutu makanan | "enak", "gurih", "hambar" |
| **MAKANAN#PILIHAN** | tentang variasi / banyaknya menu | "menunya sedikit" |
| **MAKANAN#HARGA** | tentang harga makanan tertentu | "nasi gorengnya mahal" |
| **MINUMAN#PILIHAN** | tentang variasi minuman | "cuma es teh aja" |
| **MINUMAN#HARGA** | tentang harga minuman | "es jeruknya mahal" |
| **MINUMAN#KUALITAS** | tentang rasa / mutu minuman | "es tehnya manis", "kopinya pahit" |
| **SUASANA#UMUM** | tentang suasana / kenyamanan | "tempatnya adem" |
| **LOKASI#UMUM** | tentang lokasi / letak | "susah dicari", "deket kampus" |

Tiga belas keranjang. Tidak kurang, tidak lebih — untuk buku ini.

## Petunjuk memilih yang tepat (tiga pertanyaan)

Kalau Anda tidak yakin sebuah aspek masuk keranjang mana, cukup tanyakan tiga hal
berurutan:

1. **Benda besarnya apa?** Makanan, minuman, pelayanan, suasana, lokasi, atau
   restoran itu sendiri? → Pilih bagian kiri.

2. **Sifatnya apa?** Soal rasa → `KUALITAS`. Soal harga → `HARGA`. Soal variasi
   → `PILIHAN`. Kalau tidak spesifik → `UMUM`.

3. **Masih ragu?** Ambil yang paling umum. Lebih aman memilih `MAKANAN#UMUM`
   daripada memaksakan `MAKANAN#KUALITAS` padahal tidak jelas soal rasa.

## Contoh langkah demi langkah

**Contoh 1:** "Rasanya enak banget."

- Benda besarnya? **Makanan** (rasa soal makanan).
- Sifatnya? Soal **rasa** → `KUALITAS`.
- Jadinya: **`MAKANAN#KUALITAS`**.

**Contoh 2:** "Es teh-nya manisnya kurang."

- Benda besarnya? **Minuman**.
- Sifatnya? Soal **rasa** → `KUALITAS`.
- Jadinya: **`MINUMAN#KUALITAS`**.

**Contoh 3:** "Tempatnya nyaman dan bersih."

- Benda besarnya? **Suasana / tempat**.
- Sifatnya? Umum → `UMUM`.
- Jadinya: **`SUASANA#UMUM`**.

## Satu larangan penting: jangan membuat keranjang baru

Ini godaan terbesar anotator pemula. Saat aspek tidak masuk keranjang mana pun,
muncul keinginan untuk "membuat kategori baru." **Jangan dulu.**

Tiga belas kategori ini sudah disepakati dan dipakai di seluruh dunia. Membuat
kategori baru di luar daftar justru berbahaya, karena komputer tidak mengenalnya,
dan hasilnya jadi tidak bisa dibandingkan dengan data lain.

Kalau tidak ada yang pas, pilih yang **paling dekat**. Misalnya soal "kebersihan
dapur" — tidak ada keranjang "kebersihan", jadi gunakan `RESTORAN#LAINNYA`.
Memaksakan yang agak kurang pas itu lebih aman daripada membuat keranjang baru.

> **Catatan kecil yang menggelitik:** satu nama *terdengar* logis tapi **tidak
> dipakai**, yaitu `MINUMAN#UMUM`. Kenapa? Karena keranjang `UMUM` untuk minuman
> tidak ada di versi standar internasional, dan versi bahasa Indonesia kita
> menyalin persis versi internasional itu. Jadi kalau menemukan ulasan soal
> minuman secara umum, gunakan `MINUMAN#PILIHAN`, `MINUMAN#HARGA`, atau
> `MINUMAN#KUALITAS` yang paling cocok — jangan `MINUMAN#UMUM`.

## Mengapa pekerjaan kecil ini sebenarnya penting besar

Mungkin Anda berpikir: "Ah, cuma ngelompok-kelompokin kata." Tapi percayalah, ini
bukan pekerjaan sepele.

Di balik keranjang-keranjang ini ada alasan yang dalam: manusia itu kreatif dalam
berbahasa, dan kreativitas itu indah — tapi juga rimbun dan membingungkan. Kategori
adalah cara kita **merapikan rimbunnya bahasa** tanpa menghilangkan kekayaannya.
Kita tidak melarang orang menulis "karyawan" atau "kasir"; kita hanya menampung
semuanya ke satu nama yang bisa dipahami komputer.

Inilah penerjemahan diam-diam yang membuat segalanya mungkin. Dan Anda, sebagai
anotator, adalah penerjemahnya.

---

**Latihan.** Tentukan kategori untuk kalimat-kalimat berikut:
1. "Pelayanannya ramah banget."
2. "Menunya cuma dikit."
3. "Nasi gorengnya seharga langit."

*(Jawaban: 1. `PELAYANAN#UMUM`. 2. `MAKANAN#PILIHAN`. 3. `MAKANAN#HARGA`.)*

---
*Lanjut ke [022d — Sentimen: suka, biasa aja, atau tidak suka.](./022d_sentimen.md)*
