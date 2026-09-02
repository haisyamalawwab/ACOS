# Bagian 022f — Format Data: Cara Mencatat Supaya Rapi

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Tanggal:** 2026-09-02
**Sebelumnya:** [022e: Emosi](./022e_emosi.md)

---

## Sekarang Kita Belajar Mencatat

Kita sudah tahu *apa* yang dicari (aspek, opini, kategori, sentimen, emosi).
Sekarang kita belajar **bagaimana mencatatnya** supaya komputer bisa membacanya.

Percayalah: cara mencatatnya **tidak sulit**. Kuncinya cuma satu aturan:
**memberi nomor pada tiap kata dalam kalimat.**

## Aturan #1: Setiap Kata Dapat Nomor, Mulai dari 0

Cara menghitung di sini sedikit beda dari biasanya: kita mulai dari **nol**,
bukan satu. Dan tanda baca seperti koma atau titik **bukan termasuk kata** — kita
abaikan.

Ambil kalimat ini:

> `makanan nya enak sekali`

Kita pecah jadi kata-kata dan beri nomor:

| Nomor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Kata | makanan | nya | enak | sekali |

Perhatikan: "makanan" dapat angka 0, "nya" angka 1, "enak" angka 2, "sekali"
angka 3. Ini penting, jadi ulangi sekali lagi: **kata pertama = 0**.

## Aturan #2: Rentang Ditulis "AngkaMulai,AngkaAkhir"

Untuk menunjukkan potongan kata (aspek atau opini), kita tulis:

```
angkaMulai,angkaAkhir
```

Dengan satu aturan tambahan yang sering bikin bingung: **angkaAkhir artinya "sampai
sebelum kata ini"** (bukan termasuk). Nama kerennya untuk anak IT: *akhir eksklusif*.
Mari kita jelaskan dengan contoh agar terang.

**Contoh:** kita ingin mencatat "enak sekali" (kata nomor 2 dan 3).

- Mulai di kata 2 ("enak").
- Berhenti *sebelum* kata nomor 4. Karena kata nomor 4 tidak ada (cuma sampai 3),
  kita tulis 4 sebagai angka akhir.
- Jadi rentangnya: **`2,4`**.

Kenapa bukan `2,3`? Karena `2,3` artinya "mulai di 2, berhenti sebelum 3" = cuma
kata "enak" saja. Sedangkan kita mau dua kata ("enak sekali"), jadi akhirnya harus
melompat satu lagi ke 4.

**Ingat pola ini:**

| Yang ingin kita tunjuk | Tulis |
|---|---|
| 1 kata, kata nomor 0 | `0,1` |
| 2 kata, kata 0 dan 1 | `0,2` |
| 3 kata, kata 2,3,4 | `2,5` |

Polanya: **akhir = posisi kata terakhir + 1**.

## Aturan #3: Aspek Tersembunyi Ditulis Petunjuk Khusus

Kalau aspeknya tersembunyi (tidak tertulis, dari 022b), kita tidak bisa menulis
angka. Kita pakai penanda khusus:

```
-1,-1
```

Ini "alamat rahasia" komputer yang artinya: **tidak ada kata yang ditujuk, tapi
kita tahu bendanya dari konteks.** Contoh di data sungguhan: kalimat
"saya selalu kembali ke sini setiap minggu" aspeknya restoran, tapi kata
"restoran" tidak muncul → aspek ditulis `-1,-1`.

Opini tersembunyi juga pakai `-1,-1` dengan cara yang sama.

## Aturan #4: Sentimen Ditulis Angka

Sentimen sudah kita kenal di 022d. Saat mencatat, pakai angka ini:

| Sentimen | Angka |
|---|---|
| Negatif | `0` |
| Netral | `1` |
| Positif | `2` |

Kenapa 0,1,2? Itu kesepakatan internasional dari peneliti yang membuat tugas
ini. Kita tinggal ikut saja.

## Susun Menjadi Satu "Paket" ACOSE

Semua hal yang kita catat untuk satu potongan pembicaraan dirangkai **dalam
satu baris urut**, begini:

```
aspek  kategori  sentimen  opini  emosi
```

Artinya urutannya:

1. **aspek** — rentang angka (mis. `0,1` atau `-1,-1`)
2. **kategori** — salah satu dari 13 (mis. `MAKANAN#KUALITAS`)
3. **sentimen** — angka `0`/`1`/`2`
4. **opini** — rentang angka (mis. `2,4` atau `-1,-1`)
5. **emosi** — salah satu dari 6 (mis. `senang`)

Semua dipisah **spasi**. Hasilnya satu "paket" seperti ini:

```
0,1 MAKANAN#KUALITAS 2 2,4 senang
```

Kalau dibaca: "aspek kata 0-1 (=makanan), kategori kualitas makanan, sentimen
positif (2), opini kata 2-4 (=enak sekali), emosi senang." Persis analisis kita
di 022a.

## Satu Kalimat Bisa Punya Banyak Paket

Ingat: satu kalimat bisa dinilai di banyak benda. Cara mencatatnya: tulis semua
paket **berurutan di baris yang sama**, setelah teks kalimatnya.

Contoh lengkap dari data sungguhan:

```
makanan nya enak sekali tapi pelayanan nya lambat banget   0,1 MAKANAN#KUALITAS 2 2,4 senang   5,6 PELAYANAN#UMUM 0 7,9 marah
```

Mari kita bedah:

- Teks kalimat: `makanan nya enak sekali tapi pelayanan nya lambat banget`
- Paket 1: `0,1 MAKANAN#KUALITAS 2 2,4 senang` → soal **makanan** (kata 0-1),
  positif, opini "enak sekali" (2-4), senang.
- Paket 2: `5,6 PELAYANAN#UMUM 0 7,9 marah` → soal **pelayanan** (kata 5-6),
  negatif (0), opini "lambat banget" (7-9), marah.

Dua paket dalam satu baris. Rapi, bukan?

Periksa penomoran kata kedua ("pelayanan" angka 5): dari tabel kata tadi,
`makanan`=0, `nya`=1, `enak`=2, `sekali`=3, `tapi`=4, `pelayanan`=5. Betul,
"pelayanan" memang kata nomor 5, "lambat" 7, "banget" 8 → opini `7,9`.

## Merangkum Semua Aturan Menulis

1. Setiap kata dapat nomor, **mulai dari 0**; abaikan tanda baca.
2. Rentang = `mulai,akhir` dengan **akhir eksklusif** (akhir = posisi terakhir+1).
3. Tersembunyi/implisit = `-1,-1`.
4. Sentimen = `0` (negatif), `1` (netral), `2` (positif).
5. Urutan paket: `aspek kategori sentimen opini emosi`.
6. Beberapa paket ditulis berurutan setelah teks kalimat.

## Tabel Konversi Cepat (Boleh Dilipat / Ditempel)

Untuk kata-kata yang mau ditunjuk, ingat saja:

| Kalau menunjuk | Tulis |
|---|---|
| kata nomor 3 saja | `3,4` |
| kata nomor 0 dan 1 | `0,2` |
| kata nomor 5, 6, 7 | `5,8` |
| tidak ada kata (tersembunyi) | `-1,-1` |

---

**Latihan:** pecah kalimat `kopi nya pahit sekali` jadi kata + nomor, lalu
tuliskan satu paket ACOSE yang benar untuk "kopi pahit" dengan sentimen negatif.
(Kunci: paket: `0,1 MINUMAN#KUALITAS 0 2,4 sedih` — tapi coba selesaikan
sendiri dulu!)

---

*Lanjut ke [022g: Kasus sulit dan tanya-jawab](./022g_kasus_sulit_dan_faq.md).*
