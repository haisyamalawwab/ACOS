# Bagian 022g — Kasus Sulit dan Tanya-Jawab (FAQ)

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Tanggal:** 2026-09-02
**Sebelumnya:** [022f: Format Data](./022f_format_data.md)

---

## Pendahuluan: Bahasa Itu Kotor, dan Itu Wajar

Orang tidak selalu bicara dengan rapi. Ada kata sarkasme, ada kata yang bisa
diartikan dua, ada kalimat yang dobel makna. Jadi buku ini menutup bagian teknis
dengan deretan **pertanyaan yang sering muncul** dan **situasi jebakan** yang
paling sering membuat anotator ragu.

Tidak apa-apa kalau Anda ragu. Justru bagus. Ragu itu tanda Anda berpikir, bukan
tanda Anda salah. Di bagian "Catatan Belakang" (022h) kita akan lihat bagaimana
keraguan anotator sebenarnya *dimanfaatkan* untuk mengukur kualitas data.

---

## FAQ #1: "Kalau satu kalimat menyebut banyak aspek, bagaimana?"

Tulis **satu paket ACOSE untuk tiap aspek**, semua di baris yang sama.
Contohnya sudah kita lihat di 022f: kalimat "makanan enak tapi pelayanan lambat"
punya 2 paket (makanan + pelayanan). Tidak ada batasan jumlah paket per kalimat,
asalkan tiap paket benar-benar tentang aspek yang berbeda.

## FAQ #2: "Bagaimana kalau aspek dan opini sama-sama tersembunyi?"

Boleh. Keduanya sama-sama ditulis `-1,-1`. Contoh nyata di data demo:

> "Tidak akan pernah datang lagi ke tempat ini."

Di sini aspeknya (restoran) dan opininya (rasa tidak suka) sama-sama tidak
tertulis. Jadi aspek = `-1,-1`, opini = `-1,-1`, kategorinya `RESTORAN#UMUM`,
sentimennya negatif. Emosinya Anda baca dari nada kalimat (bisa `marah`).

## FAQ #3: "Kapan saya memakai emosi 'netral'?"

Gunakan `netral` ketika **tidak ada bukti perasaan** pada aspek itu — bukan
karena Anda malas memilih. Contoh "harganya wajar" atau "menunya standar" cenderung
`netral`. Kalau ada sedikit rasa (senang/marah/dll), pilih yang paling dekat.
**Jangan pernah membiarkan kolom emosi kosong.** Saat ragu antara dua emosi,
pilih yang paling mendekati, lalu catat keraguan Anda (lihat FAQ #8).

## FAQ #4: "Bagaimana dengan sarkasme?"

Sarkasme itu musuh semua orang, termasuk peneliti. Contoh:

> "Bagus banget, makanannya sampai aku gak bisa tidur karena sakit perut."

Kata "bagus" kedengaran pujian, tapi maksudnya keluhan.

Aturan praktis: **baca seluruh kalimat, bukan cuma satu kata.** Kalau nada
keseluruhan jelas mengejek, sentimennya **negatif**, bukan positif. Untuk emosi
di sini biasanya `marah` atau `sedih` (tergantung nadanya). Ini kasus yang
**dianggap sulit bahkan oleh komputer**, jadi jangan berkecil hati kalau ragu —
tulis keraguan Anda di catatan.

## FAQ #5: "Kalau ulasannya campur: memuji makanannya tapi mengeluh harga?"

Wajar banget. Tulis **dua paket** — satu untuk makanan (positif), satu untuk
harga (negatif). Komputer justru *senang* melihat ini karena mengajarinya bahwa
satu orang bisa punya dua pendapat berbeda.

## FAQ #6: "Bagaimana kalau kategorinya tidak ada yang pas?"

Pilih yang **paling dekat**. Misalnya "kebersihan dapur" → tidak ada kategori
kebersihan, pakai `RESTORAN#LAINNYA`. Aturan yang dilarang: **membuat kategori
baru** di luar 13 yang sudah ditentukan, atau memakai `MINUMAN#UMUM` yang memang
tidak terdaftar. Saat ragu memilih dua kategori, pilih yang **lebih umum** (yang
ber-`UMUM`).

## FAQ #7: "Sentimen dan emosi itu beda apa, sih? Suka = senang kan?"

Ini pertanyaan paling penting. **Beda.** Suka/tidak (sentimen) hanyalah arah.
Perasaan (emosi) itu lebih dalam dan bisa bermacam-macam meski arahnya sama.
Ingat contoh tiga orang yang sama-sama "tidak suka harga": satu marah, satu
sedih, satu takut. Jadi:
- Jangan menurunkan emosi otomatis dari sentimen ("positif = senang").
- Baca emosi dari **kata-kata**, bukan dari plus/minus.

Secara teori, perasaan dan arah suka/tidak adalah dua sumbu yang berbeda dalam
ilmu emosi. Praktisnya: lihat kata-katanya dengan teliti.

## FAQ #8: "Bagaimana kalau saya ragu / tidak yakin?"

Ragu itu informasi berharga, bukan kegagalan. Dua hal yang bisa Anda lakukan:

1. **Isi tetap satu pilihan** yang paling masuk akal (jangan kosong).
2. **Catat keraguan Anda** di kolom catatan / notes (misal: "ragu antara sedih
   dan marah").

Catatan ini tidak dibuang. Justru dipakai di tahap akhir untuk mengukur seberapa
sulit sebuah teks dan untuk menghitung kesepakatan antar-anotator (dibahas di
022h). Jadi catatlah dengan jujur.

## FAQ #9: "Apakah saya boleh bertanya ke teman saat ragu?"

Boleh, bahkan **dianjurkan** untuk kasus yang sangat sulit. Kalau dua orang bisa
sepakat setelah diskusi, itu petunjuk bahwa teksnya memang bisa dibaca dengan
jelas. Kalau sampai dua orang yang pintar tetap tidak sepakat, itu petunjuk
bahwa teksnya secara objektif ambigu — dan itu temuan yang berharga, bukan
kegagalan Anda.

## FAQ #10: "Rasanya saya butuh latihan lebih."

Itu bagus! Baca lagi 022b sampai 022f dengan santai. Kerjakan ulang semua
latihannya. Mulai dari kalimat-kalimat pendek dan jelas, baru naik ke yang
panjang dan campur. Kecepatan bukan tujuan — **konsistensi** yang utama.

---

## Ringkasan Jebakan yang Perlu Diingat

| Jebakan | Yang benar |
|---|---|
| Menurunkan emosi dari sentimen | Baca emosi dari kata-kata |
| Mengosongkan kolom emosi | Selalu isi, pilih yang paling dekat |
| Membuat kategori baru | Pilih dari 13 yang sudah ada |
| Menilai satu kalimat jadi satu sentimen saja | Satu paket per aspek |
| Menghitung kata mulai dari 1 | Mulai dari 0 |
| Mengira `2,3` = "2 kata" | `2,3` cuma 1 kata (akhir eksklusif) |

---

*Lanjut ke [022h: Di Balik Layar — apa gunanya semua ini](./022h_di_balik_layar_dan_manfaat.md).*
