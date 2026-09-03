# Bagian 022f — Format Data: Bagaimana Mencatat Semuanya

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Sebelumnya:** [022e — Emosi](./022e_emosi.md)

---

> **Sebentar, masalahnya apa?**
> - **Masalah:** Kita sudah tahu *apa* yang harus diambil dari sebuah ulasan (lima
>   lapis ACOSE). Tapi kalau tiap orang mencatat dengan caranya sendiri-sendiri,
>   hasilnya jadi kacau dan tidak bisa dipakai siapa pun.
> - **Kenapa ini berat:** Komputer hanya bisa belajar dari data yang *rapi dan
>   seragam.* Satu orang menulis "makanan" di baris, orang lain menulis "food",
>   orang lain lagi menulis angka beda — komputer tidak akan pernah paham.
> - **Solusinya:** Ada satu cara mencatat yang disepakati, sederhana dan konsisten.
>   Intinya cuma satu: **memberi nomor pada setiap kata dalam kalimat.** Bab ini
>   membongkar aturan ini sampai tuntas, dengan contoh nyata.

---

## Puncak dari semua yang sudah kita pelajari

Kita sudah menguasai kelima lapis: benda (aspek), nama resmi (kategori), kata rasa
(opini), suka/tidak (sentimen), dan perasaan (emosi). Sekarang tiba saat yang kita
tunggu-tunggu: **bagaimana menuliskannya** supaya rapi dan bisa dibaca komputer.

Kalau selama ini kita "berpikir seperti anotator", sekarang kita "menulis seperti
anotator." Dan kabar baiknya: **menuliskannya tidak sulit sama sekali.** Hanya ada
satu hal kecil yang perlu diingat, dan begitu Anda paham, sisanya mengalir.

Hal kecil itu: **memberi nomor pada setiap kata dalam kalimat.** Mari kita bongkar.

## Aturan #1: setiap kata dapat nomor, mulai dari nol

Di sini kita harus melatih satu hal yang sedikit berbeda dari kebiasaan sehari-hari:
kita menghitung **mulai dari nol**, bukan satu. Dan tanda baca seperti koma atau
titik **bukan termasuk kata** — kita abaikan.

Ambil kalimat ini:

> `makanan nya enak sekali`

Pecah jadi kata-kata, lalu beri nomor:

| Nomor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Kata | makanan | nya | enak | sekali |

Perhatikan: "makanan" dapat angka 0, "nya" angka 1, "enak" angka 2, "sekali"
angka 3. **Kata pertama selalu 0.** Ini aturan pertama yang wajib diingat.

Kenapa mulai dari nol? Ini salah satu hal yang membuat orang non-teknis bingung
tapi sebenarnya sangat wajar di dunia komputer — komputer memang suka menghitung
dari nol. Kita cukup ikut saja; nanti semua jadi konsisten.

## Aturan #2: rentang ditulis "AngkaMulai,AngkaAkhir"

Untuk menunjukkan potongan kata (aspek atau opini), kita menulis dua angka:

```
angkaMulai,angkaAkhir
```

Tapi ada satu aturan tambahan yang paling sering membuat orang tersandung, jadi
mari kita pahamkan baik-baik: **angkaAkhir artinya "sampai sebelum kata ini" —
bukan termasuk.**

Istilah kerennya di dunia teknis: *akhir eksklusif.* Tapi jangan takut dengan
istilahnya — mari kita lihat contohnya sampai benar-benar terang.

**Contoh:** kita ingin menunjuk "enak sekali" — kata nomor 2 dan 3.

- Mulai di kata 2 ("enak").
- Berhenti *sebelum* kata nomor 4. Kata nomor 4 tidak ada (kalimat kita cuma
  sampai 3), jadi kita tulis 4 sebagai angka akhir.
- Rentangnya: **`2,4`.**

Kenapa bukan `2,3`? Karena `2,3` artinya "mulai di 2, berhenti sebelum 3" = cuma
kata "enak" saja. Padahal kita mau dua kata. Jadi akhirnya harus melompat satu lagi
ke 4.

**Pola yang perlu diingat:**

| Yang ingin ditunjuk | Tulis |
|---|---|
| 1 kata, kata nomor 0 | `0,1` |
| 2 kata, kata 0 dan 1 | `0,2` |
| 3 kata, kata 2,3,4 | `2,5` |

Lihat polanya? **Akhir = posisi kata terakhir + 1.** Sekali paham pola ini, sisanya
mudah.

## Aturan #3: benda tersembunyi ditulis penanda khusus

Ingat dari 022b, ada kasus di mana benda (aspek) atau kata rasa (opini) **tidak
tertulis** — tersembunyi. Kalau begitu, kita tidak bisa menunjuk angka. Maka kita
pakai penanda "alamat rahasia":

```
-1,-1
```

Artinya: **tidak ada kata yang ditunjuk, tapi kita tahu maksudnya dari konteks.**
Contoh di data sungguhan: kalimat "saya selalu kembali ke sini setiap minggu" — aspeknya
restoran, tapi kata "restoran" tidak muncul, jadi aspeknya ditulis `-1,-1`. Opini
tersembunyi juga pakai `-1,-1` dengan cara yang sama.

Jangan khawatir: `-1,-1` bukan angka "aneh". Ini semacam kode khusus yang disepakati
untuk menyatakan "ini tersembunyi." Komputer tahu artinya.

## Aturan #4: sentimen ditulis angka

Sentimen sudah kita kenal di 022d. Saat mencatat, kita pakai angka:

| Sentimen | Angka |
|---|---|
| Negatif | `0` |
| Netral | `1` |
| Positif | `2` |

Kenapa 0, 1, 2? Ini kesepakatan internasional dari para peneliti yang merancang
tugas ini. Kita tinggal mengikutinya — tidak perlu menemukan ulang.

## Susun menjadi satu "paket" ACOSE

Semua yang kita catat untuk satu potongan pembicaraan dirangkai **dalam satu baris,
dengan urutan tetap**:

```
aspek   kategori   sentimen   opini   emosi
```

Urutannya:

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

## Satu kalimat bisa punya banyak paket

Ingat kunci dari 022a: satu kalimat bisa dinilai di banyak benda. Cara mencatatnya:
tulis semua paket **berurutan di baris yang sama**, setelah teks kalimatnya.

Contoh lengkap dari data sungguhan di proyek ini:

```
makanan nya enak sekali tapi pelayanan nya lambat banget   0,1 MAKANAN#KUALITAS 2 2,4 senang   5,6 PELAYANAN#UMUM 0 7,9 marah
```

Mari kita bedah perlahan:

- Teks kalimat: `makanan nya enak sekali tapi pelayanan nya lambat banget`
- **Paket 1:** `0,1 MAKANAN#KUALITAS 2 2,4 senang`
  → soal **makanan** (kata 0-1), positif, opini "enak sekali" (2-4), senang.
- **Paket 2:** `5,6 PELAYANAN#UMUM 0 7,9 marah`
  → soal **pelayanan** (kata 5-6), negatif (0), opini "lambat banget" (7-9), marah.

Dua paket dalam satu baris. Rapi, bukan?

Kalau Anda penasaran kenapa "pelayanan" dapat angka 5: mari kita hitung bersama.
`makanan`=0, `nya`=1, `enak`=2, `sekali`=3, `tapi`=4, `pelayanan`=5. Betul!
Kemudian `nya`=6, `lambat`=7, `banget`=8. Jadi opini "lambat banget" = `7,9`.
Semua masuk akal.

## Merangkum semua aturan menulis

1. Setiap kata dapat nomor, **mulai dari 0**; abaikan tanda baca.
2. Rentang = `mulai,akhir` dengan **akhir eksklusif** (akhir = posisi terakhir + 1).
3. Tersembunyi = `-1,-1`.
4. Sentimen = `0` (negatif), `1` (netral), `2` (positif).
5. Urutan paket: `aspek  kategori  sentimen  opini  emosi`.
6. Beberapa paket ditulis berurutan setelah teks kalimat.

## Tabel konversi cepat (boleh difoto / ditempel)

| Kalau menunjuk | Tulis |
|---|---|
| kata nomor 3 saja | `3,4` |
| kata nomor 0 dan 1 | `0,2` |
| kata nomor 5, 6, 7 | `5,8` |
| tidak ada kata (tersembunyi) | `-1,-1` |

---

## ▪️ BAGI YANG MAU LEBIH DALAM: bagaimana data "dibaca" komputer

Sekarang formatnya sudah jelas. Ini lapisan tentang apa yang terjadi setelah data
Anda jadi — opsional, untuk yang penasaran dengan sisi teknis.

- **Anda baru saja belajar *token offset*.** "Memberi nomor pada tiap kata" itulah
  yang peneliti sebut penanda posisi token. Ini bukan cara iseng — inilah bahasa
  yang dipakai data untuk menunjukkan *di mana* aspek dan opini berada. Proyek ini
  bahkan sanggup memindahkan penanda ini dengan tepat ke tingkatan yang lebih halus
  (sub-kata) saat teks disiapkan untuk model bahasa — detail kecil, tapi menjaga
  ketepatan.

- **Menemukan aspek/opini di kalimat secara teknis disebut *span extraction* atau
  *tagging* — dan sering pakai skema "BIO".** BIO singkatan dari *Begin, Inside,
  Outside* (Mulai, Di dalam, Di luar). Komputer menandai tiap token: mana yang
  "awal" dari aspek, mana yang "lanjutan" aspek, dan mana yang "di luar". Itu cara
  lain menyatakan rentang yang Anda tulis sebagai `0,1` atau `2,4`.

- **Untuk menjaga batas-batas itu tetap konsisten, proyek sering memakai satu alat
  bernama CRF** (*Conditional Random Field*; Lafferty et al., 2001). Ini semacam
  "penjaga aturan" yang memastikan hasil penandaan tetap masuk akal berurutan —
  misalnya tidak mungkin ada "akhir aspek" tanpa "awal aspek".

- **Yang Anda catat (`0,1 MAKANAN#KUALITAS 2 2,4 senang`) adalah *satu baris contoh
  (instance)* untuk model.** Gabungan ratusan baris inilah yang akhirnya "dibaca"
  model untuk belajar. Semakin konsisten baris-baris Anda, semakin baik modelnya.

Format selesai. Lanjut ke 022g untuk menghadapi kasus-kasus bahasa yang "nakal".

---

**Latihan.** Pecah kalimat `kopi nya pahit sekali` jadi kata + nomor, lalu
tuliskan satu paket ACOSE yang benar untuk "kopi pahit" dengan sentimen negatif.

*(Kunci: `0,1 MINUMAN#KUALITAS 0 2,4 sedih` — tapi coba selesaikan sendiri dulu!
Petunjuk: kopi=makanan/minuman yang mana? pahit=rasa apa?)*

---
*Lanjut ke [022g — Kasus sulit dan tanya-jawab.](./022g_kasus_sulit_dan_faq.md)*
