# Bagian 022g — Kasus Sulit dan Tanya-Jawab: Saat Bahasa Mulai Nakal

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Sebelumnya:** [022f — Format Data](./022f_format_data.md)

---

> **Sebentar, masalahnya apa?**
> - **Masalah:** Aturan yang sudah kita pelajari bekerja rapi pada kalimat yang
>   sopan. Tapi manusia tidak selalu bicara rapi — ada sarkasme, kalimat dobel
>   makna, dan kasus yang bikin berhenti dan bertanya "ini yang mana?"
> - **Kenapa ini berat:** Kalau anotator bingung dan menebak asal, data jadi
>   berisik. Kalau ia berhenti terlalu lama, pekerjaan tidak selesai.
> - **Solusinya:** Kumpulkan pertanyaan yang paling sering muncul, jawab dengan
>   aturan praktis, dan — yang paling penting — perlakukan keraguan sebagai
>   **informasi yang dicatat**, bukan kegagalan yang disembunyikan.

---

## Bahasa itu tidak selalu sopan — dan itu justru yang menarik

Sebelum menutup bagian teknis, mari kita jujur tentang satu hal: manusia tidak
selalu bicara dengan rapi. Ada sarkasme, ada kata yang bisa diartikan dua, ada
kalimat yang dobel makna, ada orang yang malah bercanda soal sesuatu yang serius.

Kalau bahasa selalu rapi, pekerjaan anotasi akan membosankan — dan komputer akan
cepat bosan mengalahkan kita. Tapi justru karena bahasa "nakal", keahlian manusia
menjadi tak tergantikan. Di bab ini kita bahas pertanyaan-pertanyaan yang paling
sering muncul dan situasi yang paling sering membuat anotator berhenti dan
berpikir.

Satu hal yang ingin saya tegaskan di awal: **merasa ragu itu BUKAN tanda Anda
salah. Ragu adalah tanda Anda berpikir.** Dan di akhir bab ini kita akan melihat
bahwa keraguan anotator sebenarnya *bernilai* — bukan dibuang.

---

## FAQ #1: "Kalau satu kalimat menyebut banyak aspek, bagaimana?"

Tulis **satu paket ACOSE untuk tiap aspek**, semuanya di baris yang sama. Contohnya
sudah kita lihat berkali-kali: "makanan enak tapi pelayanan lambat" punya dua paket.
Tidak ada batasan jumlah paket per kalimat, selama tiap paket benar-benar tentang
aspek yang berbeda.

## FAQ #2: "Bagaimana kalau aspek dan opini sama-sama tersembunyi?"

Boleh, dan ini lebih umum daripada yang Anda kira. Dua-duanya ditulis `-1,-1`.
Contoh nyata dari data proyek:

> "Tidak akan pernah datang lagi ke tempat ini."

Di sini aspeknya (restoran) dan opininya (rasa tidak suka) sama-sama tidak tertulis.
Jadi aspek = `-1,-1`, opini = `-1,-1`, kategorinya `RESTORAN#UMUM`, sentimennya
negatif. Emosinya Anda baca dari nada kalimat — bisa `marah`.

## FAQ #3: "Kapan saya memakai emosi 'netral'?"

Jawabannya: ketika **tidak ada bukti perasaan** pada aspek itu — bukan karena Anda
malas memilih. "Harganya wajar" atau "menunya standar" cenderung `netral`. Kalau ada
sedikit rasa (senang/marah/dll), pilih yang paling dekat. **Jangan pernah
membiarkan kolom emosi kosong.** Kalau ragu antara dua emosi, pilih yang paling
mendekati, lalu catat keraguan Anda (lihat FAQ #8).

## FAQ #4: "Bagaimana dengan sarkasme?"

Sarkasme adalah musuh semua orang — termasuk para peneliti. Contoh:

> "Bagus banget, makanannya sampai aku gak bisa tidur karena sakit perut."

Kata "bagus" kedengarannya pujian, tapi maksudnya jelas keluhan.

Aturan praktisnya: **baca seluruh kalimat, bukan cuma satu kata.** Kalau nada
keseluruhan mengejek, sentimennya **negatif**, bukan positif. Untuk emosi biasanya
`marah` atau `sedih`, tergantung nadanya. Ini kasus yang **dianggap sulit bahkan oleh
komputer**, jadi jangan berkecil hati kalau ragu — tuliskan keraguan Anda di catatan.

## FAQ #5: "Kalau ulasannya campur — memuji makanan tapi mengeluh harga?"

Wajar banget. Tulis **dua paket**: satu makanan (positif), satu harga (negatif).
Komputer justru *senang* melihat ini, karena mengajarinya bahwa satu orang bisa
punya dua pendapat yang berbeda dalam satu napas.

## FAQ #6: "Bagaimana kalau kategorinya tidak ada yang pas?"

Pilih yang **paling dekat.** Misalnya "kebersihan dapur" → tidak ada kategori
kebersihan, gunakan `RESTORAN#LAINNYA`. Aturan yang dilarang: **membuat kategori
baru** di luar 13 yang sudah ada, atau memakai `MINUMAN#UMUM` yang memang tidak
terdaftar. Kalau ragu antara dua kategori, pilih yang **lebih umum** (yang
ber-`UMUM`).

## FAQ #7: "Sentimen dan emosi itu beda apa, sih? Suka = senang kan?"

**Beda, dan ini pertanyaan terpenting di buku ini.** Suka/tidak (sentimen) hanyalah
arah. Perasaan (emosi) lebih dalam dan bisa bermacam-macam meski arahnya sama.
Ingat contoh tiga orang yang sama-sama tidak suka harga: satu marah, satu sedih,
satu takut. Jadi:

- Jangan menurunkan emosi otomatis dari sentimen ("positif = senang").
- Baca emosi dari **kata-kata**, bukan dari plus/minus.

Secara teori, perasaan dan arah suka/tidak adalah dua sumbu yang berbeda dalam ilmu
emosi. Praktisnya: lihat kata-kata dengan teliti.

## FAQ #8: "Bagaimana kalau saya ragu / tidak yakin?"

Ragu itu informasi berharga, bukan kegagalan. Dua hal yang bisa Anda lakukan:

1. **Isi tetap satu pilihan** yang paling masuk akal (jangan kosong).
2. **Catat keraguan Anda** di kolom catatan (misal: "ragu antara sedih dan marah").

Catatan ini tidak dibuang. Di 022h kita akan lihat bagaimana catatan ini justru
dipakai untuk mengukur kualitas data — termasuk untuk menghitung seberapa sering
manusia sepakat. Jadi catatlah dengan jujur.

## FAQ #9: "Boleh bertanya ke teman saat ragu?"

Boleh, bahkan **dianjurkan** untuk kasus yang sangat sulit. Kalau dua orang bisa
sepakat setelah berdiskusi, itu petunjuk bahwa teksnya bisa dibaca dengan jelas.
Kalau dua orang yang sama-sama teliti tetap tidak sepakat, itu petunjuk bahwa teksnya
secara objektif ambigu — dan itu temuan berharga, bukan kegagalan siapa pun.

## FAQ #10: "Rasanya saya butuh latihan lebih."

Itu kabar baik! Baca ulang 022b sampai 022f dengan santai. Kerjakan ulang semua
latihannya. Mulai dari kalimat pendek dan jelas, lalu naik ke yang panjang dan
campur. Kecepatan bukan tujuannya — **konsistensi** yang utama.

---

## Ringkasan: jebakan yang perlu diingat

| Jebakan | Yang benar |
|---|---|
| Menurunkan emosi dari sentimen | Baca emosi dari kata-kata |
| Mengosongkan kolom emosi | Selalu isi, pilih yang paling dekat |
| Membuat kategori baru | Pilih dari 13 yang sudah ada |
| Menilai satu kalimat jadi satu sentimen saja | Satu paket per aspek |
| Menghitung kata mulai dari 1 | Mulai dari 0 |
| Mengira `2,3` = "2 kata" | `2,3` cuma 1 kata (akhir eksklusif) |

---

## Penutup: keraguan Anda adalah aset

Saya ingin mengakhiri dengan satu pemikiran yang mungkin mengubah cara Anda melihat
pekerjaan ini. Dalam dunia anotasi, **keraguan bukan musuh — ia adalah bahan.** Ketika
sekelompok anotator mengerjakan data yang sama secara terpisah, perbedaan pendapat
mereka diukur dengan cermat. Semakin sering mereka sepakat, semakin tepercaya
datanya. Semakin sering mereka berbeda, semakin jelas bahwa ada bagian pedoman yang
perlu diperjelas atau teks yang memang ambigu.

Jadi ketika Anda menulis catatan "ragu antara sedih dan marah", Anda tidak sedang
mengurangi nilai data Anda. Anda sedang **memberi tanda pada titik di mana manusia
sendiri kesulitan** — dan itu informasi yang sangat berharga bagi siapa pun yang
memakai data ini.

---

## ▪️ BAGI YANG MAU LEBIH DALAM: kenapa sarkasme dan ambiguitas "menakutkan" bagi AI

Kasus-kasus "bahasa nakal" di bab ini bukan cuma menyulitkan Anda — mereka adalah
masalah terbuka yang dikenal dalam riset NLP. Penutup teknis ini opsional.

- **Sarkasme adalah tantangan yang *sulit dan terbuka* bagi komputer.** Banyak
  sistem bisa membaca kalimat datar dengan baik, tapi gagal saat kalimat
  menyiratkan kebalikan dari kata yang tertulis. Inilah sebabnya anotasi manusia
  pada kasus sarkasme sangat bernilai: Anda menangkap maksud yang tidak bisa
  ditangkap dari permukaan kata.

- **Ambiguitas disebut juga *ambiguity* atau *annotation difficulty*.** Saat dua
  anotator ragu dan berbeda pendapat, itu bukan kegagalan — dalam riset, tingkat
  kesulitan anotasi ini bisa diukur dan justru dilaporkan. Beberapa dataset bahkan
  menandai baris "sulit" secara khusus, karena baris itu membedakan model yang baik
  dari model yang hanya menebak.

- **Keraguan Anda ikut menghitung *kesepakatan antar-anotator*.** Ini melanjutkan
  apa yang kita singgung di 022e (Cohen's kappa). Hasilnya dipakai untuk
  memperbaiki aturan: kalau banyak anotator sering berbeda di satu jenis kalimat,
  berarti pedomannya di sana kurang jelas dan perlu ditulis ulang — bukan berarti
  salah satu anotator bodoh.

- **Satu prinsip yang membuat semua ini mungkin: kerja *dengan* data yang jujur,
  bukan *menyembunyikan* kesulitannya.** Inilah ciri data penelitian yang bisa
  dipercaya: keraguan dicatat, diukur, dan dipakai untuk memperbaiki proses — bukan
  dibuang.

Itu dunia teknisnya. Sekarang kita menutup buku di 022h.

---
*Lanjut ke [022h — Di Balik Layar: kenapa semua ini berharga, dan jujur soal batasannya.](./022h_di_balik_layar_dan_manfaat.md)*
