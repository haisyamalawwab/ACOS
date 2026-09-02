# Bagian 022c — Kategori: Memberi Nama Resmi pada Benda

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Tanggal:** 2026-09-02
**Sebelumnya:** [022b: Aspek dan Opini](./022b_aspek_dan_opini.md)

---

## Soal Nama-Nama

Di bagian 022b, kita menemukan **aspek** — bendanya, misalnya "makanan",
"pelayanan", "harga". Tapi ada masalah: setiap orang menulis kata yang
berbeda-beda untuk benda yang sama.

- Ada yang bilang "makanannya", ada yang "masakannya", ada yang "nasi
  gorengnya".
- Ada yang bilang "pelayanannya", ada yang "karyawannya", ada yang "orangnya".

Kalau komputer disuruh belajar dari banyak kata yang beda-beda ini, dia bingung.
Karena itu kita butuh satu langkah perantara: **mengelompokkan** semua kata itu
ke dalam **nama resmi** yang sama. Nama resmi inilah yang disebut **kategori**.

Analoginya seperti menyortir cucian. Anda punya banyak baju, tapi cuma dua
keranjang: "baju dipakai ke luar" dan "baju tidur". Semua jenis baju masuk ke
salah satu keranjang. Kita tidak peduli mereknya — yang penting keranjangnya
benar.

## Bentuk Nama Kategorinya

Nama kategori restoran selalu berbentuk dua bagian yang dipisah tanda pagar (`#`):

```
NAMA-UMUM # SIFAT
```

- **Bagian kiri** = benda besarnya (makanan, minuman, pelayanan, dll).
- **Bagian kanan** = sifat atau aspek spesifiknya (kualitas, harga, pilihan...).

Contoh: `MAKANAN#KUALITAS` artinya "kualitas makanan". `HARGA#MAKANAN` mungkin
dua bagian yang sama tapi posisinya beda — jadi perhatikan urutannya,
`MAKANAN#HARGA` (harga makanan) dan `MAKANAN#KUALITAS` (kualitas makanan) itu
beda.

## Daftar 13 Kategori Restoran

Untuk buku ini kita pakai 13 kategori yang **sudah disiapkan khusus bahasa
Indonesia**. Semuanya tentang restoran. Ini dia tabel lengkapnya — baca santai,
jangan dihafal:

| Kategori | Kapan Dipakai | Contoh Kata dalam Ulasan |
|---|---|---|
| **RESTORAN#UMUM** | soal tempat makan secara umum | "tempat ini", "restonya" |
| **RESTORAN#HARGA** | soal harga keseluruhan | "harganya", "ngebantu kantong" |
| **RESTORAN#LAINNYA** | soal resto yang tak masuk kategori lain | "kebersihan dapurnya", "jangkauan" |
| **PELAYANAN#UMUM** | soal pelayanan / karyawan | "pelayanannya", "orangnya", "ramah" |
| **MAKANAN#UMUM** | soal makanan secara umum | "makanannya", "masakannya" |
| **MAKANAN#KUALITAS** | soal rasa / mutu makanan | "enak", "gurih", "hambar" |
| **MAKANAN#PILIHAN** | soal variasi / banyaknya pilihan menu | "menunya sedikit", "pilihan lengkap" |
| **MAKANAN#HARGA** | soal harga makanan tertentu | "nasi gorengnya mahal" |
| **MINUMAN#PILIHAN** | soal variasi minuman | "es tehnya aja yang ada" |
| **MINUMAN#HARGA** | soal harga minuman | "es jeruknya mahal" |
| **MINUMAN#KUALITAS** | soal rasa / mutu minuman | "es tehnya manis", "kopinya pahit" |
| **SUASANA#UMUM** | soal suasana / kenyamanan tempat | "tempatnya adem", "ramenya rame" |
| **LOKASI#UMUM** | soal lokasi / letak | "susah dicari", "deket kampus" |

## Petunjuk Memilih yang Tepat

Tiga aturan sederhana:

1. **Tanya dulu: benda besarnya apa?** Makanan, minuman, pelayanan, suasana,
   lokasi, atau restoran itu sendiri? Pilih bagian kiri yang cocok.

2. **Tanya lagi: sifatnya apa?** Kalau soal rasa → `KUALITAS`. Soal harga →
   `HARGA`. Soal variasi menu → `PILIHAN`. Kalau tidak spesifik / "ya begitulah
   secara umum" → `UMUM`.

3. **Kalau ragu, pilih yang paling umum.** Lebih aman memilih `MAKANAN#UMUM`
   daripada memaksakan `MAKANAN#KUALITAS` padahal tidak jelas itu soal rasa.

## Contoh Langkah Demi Langkah

**Contoh 1:** "Rasanya enak banget."

- Benda besarnya? **Makanan** (rasa itu soal makanan).
- Sifatnya? Soal **rasa** → `KUALITAS`.
- Jadi kategorinya: **`MAKANAN#KUALITAS`**.

**Contoh 2:** "Es tehnya manisnya kurang."

- Benda besarnya? **Minuman**.
- Sifatnya? Soal **rasa** → `KUALITAS`.
- Jadi: **`MINUMAN#KUALITAS`**.

**Contoh 3:** "Tempatnya nyaman dan bersih."

- Benda besarnya? **Suasana / tempat**.
- Sifatnya? Umum (nyaman) → `UMUM`.
- Jadi: **`SUASANA#UMUM`**.

## Satu Hal yang Dilarang: Membuat Kategori Baru

Sangat menggoda untuk "membuat" kategori baru saat tidak ada yang pas. **Jangan
dulu.** 13 kategori ini sudah ditentukan sebelumnya (mengikuti standar yang
dipakai peneliti seluruh dunia, supaya hasilnya bisa dibandingkan dengan
penelitian lain).

Kalau tidak ada yang pas, pilih yang **paling dekat**. Misalnya soal "kebersihan
dapur" — tidak ada kategori "kebersihan", jadi masuk `RESTORAN#LAINNYA`
(soal tempat makan secara umum). Memaksakan kategori yang salah punya risiko
sendiri, tapi membuat kategori baru di luar daftar lebih berbahaya karena
komputer tidak mengenalnya.

> **Catatan kecil:** ada satu nama yang *terdengar* logis tapi **tidak dipakai**,
> yaitu `MINUMAN#UMUM`. Kenapa? Karena versi standar internasional tidak
> memilikinya, dan versi bahasa Indonesia kita menyalin persis versi
> internasional itu (13 label, semuanya dipasangkan 1:1). Jadi kalau menemukan
> ulasan soal minuman secara umum, gunakan `MINUMAN#PILIHAN`, `MINUMAN#HARGA`,
> atau `MINUMAN#KUALITAS` yang paling cocok — jangan `MINUMAN#UMUM`.

## Kesimpulan Singkat

1. **Kategori** adalah nama resmi untuk mengelompokkan aspek yang berbeda-beda
   kata tapi maksudnya sama.
2. Bentuknya `BENDA#SIFAT`, seperti `MAKANAN#KUALITAS`.
3. Ada 13 kategori dan semuanya sudah ditentukan — jangan membuat yang baru.
4. Tanya "benda besarnya apa" lalu "sifatnya apa", pilih paling umum kalau ragu.

---

**Latihan:** Tentukan kategori untuk kalimat-kalimat berikut:
1. "Pelayanannya ramah banget."
2. "Menunya cuma dikit."
3. "Nasi gorengnya seharga langit."

(Jawaban: 1. `PELAYANAN#UMUM`. 2. `MAKANAN#PILIHAN`. 3. `MAKANAN#HARGA`.)

---

*Lanjut ke [022d: Sentimen — suka, biasa aja, atau tidak suka](./022d_sentimen.md).*
