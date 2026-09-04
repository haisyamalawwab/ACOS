# Bagian 022h — Di Balik Layar: Kenapa Semua Ini Berharga, dan Jujur Soal Batasannya

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Sebelumnya:** [022g — Kasus Sulit dan FAQ](./022g_kasus_sulit_dan_faq.md)

---

> **Sebentar, masalahnya apa?**
> - **Masalah:** Anda sudah bisa menandai. Tapi pertanyaan yang menggantung sejak
>   awal belum dijawab: *terus, apa gunanya?* Tanpa jawaban ini, pekerjaan anotasi
>   terasa seperti kerja teliti tanpa tujuan.
> - **Kenapa ini berat:** Kerja anotasi memang melelahkan. Kalau tidak tahu ke mana
>   hasilnya pergi, orang berhenti di tengah jalan — dan data setengah jadi tidak
>   berguna bagi siapa pun.
> - **Solusinya:** Bab penutup ini membuka layar: bagaimana catatan Anda berubah
>   menjadi kemampuan komputer, bagaimana kualitasnya diukur, kenapa ini "tepat
>   guna" untuk Indonesia — dan, dengan jujur, apa saja **batasannya**.

---

## Mari kita mundur sejenak dan melihat

Kita sudah menempuh perjalanan panjang. Anda sekarang bisa mengambil kalimat ulasan
yang berantakan dan mengubahnya menjadi **paket ACOSE** yang rapi — lengkap dengan
benda, nama resmi, kata rasa, suka/tidak, dan perasaan. Itu bukan pencapaian sepele.

Tapi pertanyaan yang mungkin menggelitik Anda sejak awal akhirnya harus dijawab:

> **Terus, apa gunanya semua ini? Kenapa ada orang yang repot-repot melakukannya?**

Di bab penutup ini, saya ingin membawa Anda ke balik layar — memperlihatkan bagaimana kerja Anda berubah menjadi sesuatu yang bernilai, dan (biar jujur) juga batasannya.
Karena buku yang jujur tidak menyembunyikan keterbatasannya.

---

## Bagaimana sebenarnya komputer "belajar" dari data Anda

Bayangkan komputer sebagai seorang anak yang sedang belajar menilai makanan. Anda
tidak bisa "menginstal" rasa makanan ke kepalanya. Tapi Anda bisa **memberi contoh**
dalam jumlah yang sangat banyak.

Tiap paket ACOSE yang Anda buat adalah **satu contoh.** Paket:

```
0,1 MAKANAN#KUALITAS 2 2,4 senang
```

...berkata pada komputer: "Begini lho — kalau ada kata 'makanan' yang berdekatan
dengan 'enak', biasanya positif, kategorinya kualitas makanan, dan perasaannya
senang."

Satu contoh saja, komputer belum mengerti. Tapi beri **ribuan** contoh, dan komputer
mulai melihat **pola**: "enak" sering muncul dengan positif, "lambat" sering dengan
negatif, dan seterusnya. Dari pola inilah ia belajar menebak sendiri.

Ini prinsip yang sama seperti mengajari anak kecil membedakan senang dan sedih
dengan menunjuk-nunjuk contoh (kita bicarakan di 022a). Bedanya, komputer butuh
contoh **jauh lebih banyak** daripada anak kecil.

**Jadi peran Anda sangat penting.** Komputer tidak punya pengalaman hidup; Anda yang
menyuntikkan pengetahuan itu lewat contoh. Anda adalah gurunya.

## Satu hal yang harus kita akui dengan jujur

Mari bicara jujur tentang satu hal yang sering disembunyikan di artikel-artikel
populer: **membuat data anotasi yang baik itu kerja keras dan butuh ketelitian.**

Tidak ada jalan pintas. Setiap kalimat, setiap aspek, setiap label harus dibaca dan
diputuskan dengan hati-hati. Kadang membosankan, kadang melelahkan. Makanya pekerjaan
ini justru **cocok untuk manusia**, bukan komputer — karena butuh perasaan dan
penilaian yang tidak bisa diprogram.

Dan justru karena ini kerja keras, menjadi penting bagi kita untuk **tidak
membuang-buang usaha** dengan aturan yang berantakan atau label yang salah. Semakin
rapi dan jujur data kita, semakin berharga hasilnya. Inilah alasan mengapa buku ini
menekankan aturan dengan sabar sepanjang 022b sampai 022g: supaya kerja keras Anda
bernilai, bukan sia-sia.

## Mengukur kualitas: kenapa sampai perlu dua anotator?

Karena manusia tidak selalu sepakat, ada satu cara untuk memastikan data kita tidak
asal: **dua orang mengerjakan bagian yang sama, lalu hasilnya dibandingkan.**

Bayangkan dua orang menandai kalimat yang sama. Kalau mereka sepakat hampir selalu,
itu tanda aturannya jelas dan data bagus. Kalau mereka sering berbeda, itu tanda ada
bagian pedoman yang membingungkan dan perlu diperbaiki — bukan berarti salah satunya
bodoh.

Ada istilah teknis untuk angka kesepakatan ini (disebut "koefisien kappa"), tapi
Anda tidak perlu menghafalnya. Yang penting konsepnya:

> **Perbedaan pendapat antar-manusia diukur, bukan disembunyikan.**
> Dan hasilnya dipakai untuk memperbaiki pedoman.

Di dunia akademik pun ini dilakukan. Semakin tinggi kesepakatan antar-anotator,
semakin bisa dipercaya data kita. Inilah kenapa di 022g saya bilang "keraguan Anda
adalah aset" — bukan basa-basi.

## Kenapa ini "tepat guna" untuk Indonesia

Sekarang mari kita kaitkan dengan judul besar buku: **Teknologi Tepat Guna.**

Indonesia kaya akan bahasanya, dan ulasan restoran berbahasa Indonesia jumlahnya
banyak sekali — di aplikasi pesan antar makanan, Google Maps, media sosial, dan
lain-lain. Tapi komputer **belum tentu bisa memahami bahasa Indonesia dengan baik**,
karena banyak teknologi ini mula-mula dikembangkan untuk bahasa Inggris.

Cara terbaik untuk memperbaikinya? **Membuat data bahasa Indonesia yang bagus**,
dengan format yang sama seperti standar internasional. Dengan begitu:

- Teknologi bisa dibangun untuk bahasa Indonesia, bukan cuma terjemahan dari Inggris.
- Hasilnya masih bisa dibandingkan dengan penelitian di seluruh dunia (karena
  formatnya sama).
- Banyak orang bisa ikut serta — karena membuat datanya tidak butuh keahlian
  komputer, hanya keahlian berbahasa.

Inilah inti "tepat guna" di sini: **teknologi yang hasilnya bisa dipakai banyak
orang, dan proses pembuatannya juga bisa dijalankan banyak orang.** Bukan milik
segelintir orang di balik layar kaca.

## Peringatan jujur: buku ini pedoman, bukan hasil akhir

Supaya tidak ada salah paham, saya perlu katakan terus terang:

- Buku ini mengajarkan **cara menandai** — aturan format dan aturan penilaian.
- Buku ini **bukan** klaim bahwa semua data di proyek ini sudah jadi dan sempurna.

Di proyek yang sesungguhnya, data anotasi bahasa Indonesia yang **benar-benar siap
dipakai** masih dibuat bertahap oleh banyak orang. Data contoh yang kita pakai di
buku ini hanyalah **pemanasan** untuk mengetes alur kerjanya — bukan hasil akhir
yang sudah divalidasi.

Jadi anggap buku ini sebagai **peta dan tata cara.** Anda yang akan berjalan di
atasnya. Hasil langkah Andalah yang nantinya menjadi data yang berguna. Buku ini
hanya menyiapkan Anda supaya langkah itu tidak tersesat.

---

## ▪️ BAGI YANG MAU LEBIH DALAM: peta istilah AI/NLP dan ke mana melangkah

Karena ini bab penutup, blok teknisnya sekaligus menjadi **peta istilah** untuk
seluruh buku — kumpulan nama teknis yang sudah kita singgung, dalam satu tempat.
Tetap opsional; melewatinya tidak mengurangi apa pun.

**Nama tugasnya.**

| Yang kita sebut | Nama teknisnya |
|---|---|
| Membaca ulasan secara rinci | ABSA (*Aspect-Based Sentiment Analysis*) |
| Empat lapis (tanpa emosi) | ACOS (*Aspect-Category-Opinion-Sentiment*) |
| Lima lapis (dengan emosi) | ACOSE (ACOS + *Emotion*) |
| Satu paket lima lapis | *tuple* / *quintuple* |
| Potongan kata yang ditunjuk | *span*; tiap katanya disebut *token* |
| Benda/rasa yang tersembunyi | *implicit aspect* / *implicit opinion* |
| Keranjang kategori | *taxonomy* / *label set* (kosa kata tertutup) |
| Suka/tidak | *polarity* (polaritas sentimen) |
| Memilih satu dari beberapa label | *classification*; pelakunya *classifier* |
| Angka kesepakatan antar-anotator | *Cohen's kappa* |

**Bagaimana data Anda dipakai.** Setelah cukup banyak paket terkumpul, data dibagi
menjadi tiga bagian: sebagian untuk **melatih** model (*train*), sebagian kecil
untuk **menyetel** saat latihan (*dev* / validasi), dan sebagian lagi disimpan
rapat untuk **menguji** di akhir (*test*). Bagian penguji tidak boleh dilihat model
selama latihan — itu semacam ujian tertutup, supaya kita tahu model benar-benar
belajar dan bukan sekadar menghafal.

**Bagaimana hasilnya dinilai.** Kualitas model biasanya diukur dengan tiga angka:
*precision* (dari yang ia tebak, berapa yang benar), *recall* (dari yang seharusnya
ditemukan, berapa yang berhasil ia temukan), dan *F1* (gabungan seimbang keduanya).
Ini sebabnya para peneliti tidak pernah cukup berkata "modelnya bagus" — mereka
menyebut angkanya.

**Satu keputusan teknis yang lahir dari emosi.** Menambahkan emosi membuat jumlah
kemungkinan kombinasi label meledak: 13 kategori × 3 sentimen × 6 emosi = **234
kombinasi**. Kalau komputer harus memilih satu dari 234, sebagian besar pilihan
tidak akan pernah punya cukup contoh untuk dipelajari. Karena itu proyek ini memilih
pendekatan yang lebih hemat: **memisah keputusan per lapis** (13 + 3 + 6 = 22
pilihan) alih-alih satu keputusan raksasa. Dalam bahasa teknis, ini disebut memakai
head *factored* alih-alih *joint*.

**Kalau Anda ingin melangkah lebih jauh.** Buku teknis pendamping (**021** di
proyek yang sama) memuat aturan format yang persis, taksonomi lengkap, dan sumber
rujukan ilmiah dengan DOI. Di sanalah tempat untuk memverifikasi setiap klaim
teknis yang kita singgung di sini.

---

## Kesimpulan: seluruh perjalanan dalam satu genggaman

Mari kita rangkum.

- **A (Aspek)** — bendanya apa.
- **C (Kategori)** — nama resminya apa (dari 13 yang sudah ditentukan).
- **O (Opini)** — kata apa yang menunjukkan rasanya.
- **S (Sentimen)** — suka, biasa, atau nggak suka.
- **E (Emosi)** — perasaannya yang mana, dari 6 pilihan.

Semuanya dicatat dengan format rapi (nomor kata, angka sentimen, penanda `-1,-1`
untuk yang tersembunyi). Data rapi inilah "bahan mentah" yang membuat komputer
bisa belajar membaca ulasan restoran berbahasa Indonesia.

Yang Anda lakukan bukan hal sepele. **Anda mengubah bahasa manusia yang berantakan
menjadi data yang rapi dan bisa dipelajari.** Itu keterampilan yang berharga — dan
Anda bisa melakukannya tanpa menjadi programmer.

Terima kasih sudah membaca sampai akhir. Selamat beranotasi — dan selamat menjadi
bagian dari orang-orang yang mengajari mesin membaca perasaan manusia. 🎉

---

## Lampiran: daftar isi buku 022

- **022aa** — Kata Pengantar: untuk siapa buku ini, dan apa itu TTG.
- **022a** — Apa Itu ACOSE: dari pertanyaan besar, kita pecah jadi lima.
- **022b** — Aspek & Opini: menemukan benda dan kata rasanya.
- **022c** — Kategori: memberi nama resmi pada benda (13 label).
- **022d** — Sentimen: suka, biasa, atau tidak suka (3 pilihan).
- **022e** — Emosi: perasaan sesungguhnya (6 pilihan).
- **022f** — Format Data: mencatat supaya rapi (nomor kata, rentang).
- **022g** — Kasus Sulit & FAQ.
- **022h** — Di Balik Layar & Manfaat (bagian ini).

> Untuk pembaca yang ingin detail teknis dan sumber rujukan ilmiah, lihat
> **Buku Teknis 021** di proyek yang sama.
