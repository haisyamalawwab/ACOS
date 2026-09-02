# Bagian 022a — Apa Itu ACOSE? (Gambaran Besarnya)

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Tanggal:** 2026-09-02
**Sebelumnya:** [022aa: Kata Pengantar](./022aa_halaman_judul_dan_kata_pengantar.md)

---

## Mulai dari Sebuah Pertanyaan Sederhana

Bayangkan ini: pemilik restoran "Warung Mbak Sri" buka laman ulasan dan menemukan
ratusan kalimat seperti:

> "Makanannya enak banget tapi pelayanannya lambat."

Apa yang dia ingin tahu? Pastinya bukan sekadar "orang senang atau tidak".
Dia ingin tahu **bagian mana** yang disukai (makanan) dan **bagian mana** yang
tidak (pelayanan). Kalau cuma dikasih tahu "ulasan positif", dia bingung: yang
positif itu makanannya atau pelayanannya?

Inilah masalah yang ingin dipecahkan oleh ilmu yang namanya
**Analisis Sentimen Berbasis Aspek** — istilah kerennya ABSA (dibaca "ab-sa").
Terlalu panjang? Oke, kita sebut saja **"membaca ulasan secara rinci"**.

Inti masalahnya gampang:

> Komputer hanya perlu tahu **5 hal** dari tiap ucapan orang tentang sebuah tempat.
> Kalau komputer tahu 5 hal ini, dia bisa merangkum ratusan ulasan jadi ringkasan
> yang berguna.

## 5 Hal Itu Apa Saja?

Kita sebut 5 hal ini sebagai satu paket dan kita beri nama keren: **ACOSE**.
Huruf-hurufnya diambil dari kata-kata Inggris, tapi jangan takut — kita akan
pakai bahasa Indonesia saja.

| Huruf | Istilah | Artinya dalam bahasa santai |
|---|---|---|
| **A** | *Aspect* | **Bendanya** apa — makanan? pelayanan? harga? tempat? |
| **C** | *Category* | **Nama resmi** benda itu (mis. "kualitas makanan") |
| **O** | *Opinion* | **Kata-kata yang mengungkapkan rasa** (enak, lambat, mahal...) |
| **S** | *Sentiment* | **Suka / biasa aja / tidak suka** |
| **E** | *Emotion* | **Perasaannya** — senang, marah, sedih, takut... |

Kelima hal ini diambil dari **satu potongan kecil** pembicaraan orang. Bukan dari
seluruh ulasan, tapi dari tiap bagian yang dibicarakan.

## Contoh Supaya Kebayang

Ambil kalimat tadi:

> "Makanannya enak banget tapi pelayanannya lambat."

Kalau kita baca dengan mata manusia, kita langsung tahu isinya. Coba kita isi
tabel ACOSE-nya:

**Potongan 1 (tentang makanan):**

- A (benda): **makanan**
- C (nama resmi): **kualitas makanan**
- O (kata rasa): **enak banget**
- S (suka/tidak): **suka** (positif)
- E (perasaan): **senang**

**Potongan 2 (tentang pelayanan):**

- A (benda): **pelayanan**
- C (nama resmi): **pelayanan**
- O (kata rasa): **lambat**
- S (suka/tidak): **tidak suka** (negatif)
- E (perasaan): **marah** (atau setidaknya kesal)

Perhatikan dua hal penting:

1. Satu kalimat bisa berisi **lebih dari satu paket ACOSE**. Di sini ada dua:
   tentang makanan dan tentang pelayanan.
2. Satu orang bisa merasa **senang dan kesal sekaligus** — senang soal makanan,
   kesal soal pelayanan. Itu wajar dan boleh.

## Kenapa Komputer Butuh Bantuan Anda?

Anda mungkin berpikir: "Kalau gampang gitu, kenapa komputer nggak bisa sendiri?"

Jawabannya lucu: komputer itu **pintar tapi kaku**. Dia bisa menghitung jutaan
angka dalam sekejap, tapi dia **tidak punya pengalaman hidup**. Dia tidak pernah
makan, tidak pernah kesal karena dapat pelayanan lambat. Jadi dia tidak "tahu"
bahwa "lambat" itu biasanya hal buruk, atau bahwa "enak" itu hal yang baik.

Justru karena itu, komputer butuh **contoh**. Banyak contoh. Dan contoh-contoh
itu harus dibuat oleh **manusia** yang punya perasaan dan pengalaman — yaitu
**Anda**.

Pekerjaan membuat contoh yang rapi ini namanya **anotasi**. Anda yang menandai,
komputer yang belajar dari tanda-tanda Anda.

## Analogi: Mengajari Anak Kecil

Bayangkan Anda mengajari anak kecil apa itu "sedih". Anda tidak menjelaskan
definisi kamus. Anda malah menunjuk dan bilang:

> "Lihat, waktu dia kehilangan mainan, mukanya cemberut gitu — itu namanya sedih."

Anda memberi **contoh**, bukan **teori**. Anak kecil belajar dari banyak contoh.

Komputer persis seperti itu — lebih dari anak kecil. Dia butuh ribuan contoh
sebelum bisa menebak sendiri. Dan setiap contoh yang Anda beri adalah "anotasi".
Tanpa contoh-contoh ini, komputer tidak akan pernah bisa membaca ulasan sendiri.

## Ke Depan: Apa yang Akan Kita Pelajari

Sekarang Anda sudah paham gambaran besarnya. Sisanya tinggal detail:

- 👉 **022b** — belajar menemukan **benda** (aspek) dan **kata rasa** (opini).
- 👉 **022c** — belajar memberi **nama resmi** (kategori) pada benda.
- 👉 **022d** — belajar menentukan **suka / biasa / tidak suka** (sentimen).
- 👉 **022e** — belajar meraba **perasaan** (emosi).
- 👉 **022f** — belajar **mencatat** semuanya supaya rapi.
- 👉 **022g** — latihan soal-soal sulit dan tanya jawab.
- 👉 **022h** — melihat apa gunanya semua ini di dunia nyata.

Santai saja. Tiap bagian pendek dan penuh contoh. Kalau ada yang belum jelas di
bagian ini, itu wajar — kita baru mulai. Bagian berikutnya akan membuat semuanya
jauh lebih konkret.

---

**Latihan singkat:** Baca lagi kalimat "Makanannya enak banget tapi pelayanannya
lambat." Sebutkan dua benda (aspek) yang dibicarakan dan satu kata rasa (opini)
untuk tiap benda, tanpa lihat jawaban di atas. Kalau bisa, selamat — Anda sudah
menguasai dasar ACOSE!

---

*Lanjut ke [022b: Aspek dan Opini — menemukan benda dan kata rasanya](./022b_aspek_dan_opini.md).*
