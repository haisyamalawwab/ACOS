# Bagian 022e — Emosi: Perasaan Sesungguhnya

**Seri:** Buku Panduan TTG "ACOSE untuk Semua Orang"
**Tanggal:** 2026-09-02
**Sebelumnya:** [022d: Sentimen](./022d_sentimen.md)

---

## Ini Bagian yang Membuat ACOSE Istimewa

Di 022d, kita baru tahu orang **suka, biasa, atau nggak suka** (sentimen). Dari
situ muncul pertanyaan menarik: kalau dia tidak suka, *perasaannya yang mana?*
Marah? Sedih? Takut? Kecewa?

Nah, **semua ini dialami komponen kelima** yang membuat tugas kita jadi "ACOSE" —
bukan sekadar "ACOS" (tanpa E). Komponen kelima itu namanya **emosi**.

Perbedaan kuncinya:

- **Sentimen** = arah suka/tidak. Cuma bisa "+", "0", atau "-".
- **Emosi** = perasaan apa adanya. Bisa macam-macam, dan yang penting:
  **dua orang bisa memilih arah yang sama tapi perasaan yang berbeda.**

Contoh: tiga orang memberi sentimen **negatif** pada harga:

- "Mahalnya gila, gue kesel." → emosi **marah**.
- "Harganya mahal, gue sedih gak bisa beli." → emosi **sedih**.
- "Takut aja tagihannya boncos." → emosi **takut**.

Semuanya negatif, tapi perasaannya beda. **Inilah kenapa emosi itu berguna**:
ia menceritakan *lebih banyak* daripada sekadar suka/tidak.

## Enam Emosi yang Kita Pakai

Untuk anotasi, kita pakai **enam pilihan** emosi. Ini sudah disepakati dan
disesuaikan untuk bahasa Indonesia (dikembangkan dari penelitian EmoT,
yang cuma punya lima, lalu kita tambah satu: **netral**).

| Emosi | Arti santai | Contoh Kata dalam Ulasan |
|---|---|---|
| **senang** | bahagia, puas, gembira | "enak banget", "puas", "mantap", "nyaman" |
| **marah** | kesal, jengkel, geram | "kesel", "ngeselin", "parah", "semena-mena" |
| **sedih** | kecewa, menyesal, murung | "kecewa", "sayang sekali", "mengecewakan" |
| **takut** | khawatir, cemas, ragu | "khawatir", "takut kotor", "cemas" |
| **cinta** | suka banget, sayang, jatuh cinta | "favorit", "suka banget", "langganan", "cinta" |
| **netral** | tidak ada perasaan kuat | "standar", "biasa aja", pernyataan fakta |

## Kenapa Ada Emosi "Netral"?

Ini pertanyaan bagus. Jawabannya penting.

Banyak ulasan restoran **tidak membawa perasaan sama sekali**. Ulasan seperti:

> "Harganya wajar."

...adalah pernyataan netral. Kalau dipaksakan masuk ke salah satu dari lima
emosi (senang/marah/sedih/takut/cinta), kita akan **memaksakan perasaan yang
tidak ada**. Itu namanya menambah "noise" (keriuhan) yang bikin data jadi
kurang jujur.

Karena itu kita sediakan kelas **netral**: untuk dipakai saat **tidak ada
muatan emosi** pada aspek itu. Ini keputusan desain yang disengaja — sama
seperti kenapa aplikasi chat punya tombol "biasa aja" dan bukan hanya
"🤗" / "😡" / "😢".

Poin penting: **netral (emosi) BUKAN sama dengan netral (sentimen).** "Harganya
wajar" bisa jadi sentimennya netral DAN emosinya netral. Tapi "harganya wajar
tapi saya lega" bisa sentimen netral, emosi... ya tergantung. Jangan mencampur
keduanya.

## Aturan Emas Menentukan Emosi

Mirip sentimen, tapi satu lapis lebih dalam:

1. **Lihat opininya dulu.** Opini adalah "rongga" tempat emosi bersembunyi.
   Kata "enak" → senang. "Kesel" → marah.

2. **Kalau opini tersembunyi (implisit), lihat seluruh kalimat.** Opini implisit
   tidak punya kata yang bisa ditunjuk, jadi kita baca kalimat penuhnya untuk
   meraba perasaannya.

3. **Kalau tetap tidak ada emosi, pilih yang paling dekat — jangan kosong.**

   Ini penting: **kolom emosi tidak boleh kosong.** Kalau sangat datar dan tidak
   ada bukti emosi apa pun, pilih `netral`. Kalau sedikit ada rasa marah, pilih
   `marah`. Selalu ada satu jawaban.

## Emosi Diukur PER Aspek, Sama Seperti Sentimen

Ingat aturan dari 022d: semuanya **per benda**, bukan per kalimat.

> "Saya senang makanannya, tapi kesal pelayanannya."

- Aspek **makanan**: emosi **senang**.
- Aspek **pelayanan**: emosi **marah** (kesal).

Satu orang, dua emosi, dua aspek berbeda. Wajar.

## Contoh Langkah Demi Langkah

**Contoh 1:** "Ayam bakarnya gurih banget, puas!"

- Opini: "gurih banget, puas" → ada kata puas.
- Emosi: **senang**.

**Contoh 2:** "Pelayanannya lambat banget, kesel."

- Opini: "lambat banget, kesel" → ada kata kesel.
- Emosi: **marah**.

**Contoh 3:** "Harganya wajar."

- Opini: "wajar" → tidak ada emosi.
- Emosi: **netral**.

## Hati-Hati: Jangan Memetakan Sentimen → Emosi Secara Mesin

Ini perangkap paling umum. Jangan otomatis bilang:

> "Sentimen positif berarti emosinya senang. Negatif berarti marah."

Itu **salah**! Ingat contoh tiga orang di awal bagian: semua negatif tapi
perasaannya beda-beda (marah, sedih, takut). Emosi **tidak bisa disimpulkan
hanya dari sentimen**. Emosi harus dibaca dari **kata-katanya**.

Secara teori, perasaan dan arah suka/tidak itu dua sumbu yang berbeda (ini
berbasis riset tentang emosi; dijelaskan lebih teknis di buku teknis 021).
Kita cukup pegang aturan praktisnya: **baca bahasa tubuh kata-katanya, bukan
tebak dari plus/minus.**

## Kesimpulan Singkat

1. **Emosi** = perasaan apa adanya; inilah yang membedakan ACOSE dari ACOS.
2. Ada **enam** pilihan: senang, marah, sedih, takut, cinta, dan **netral**.
3. **netral** dipakai saat tidak ada muatan emosi — jangan dipaksakan isi lima
   yang lain.
4. Diukur **per aspek**, tidak boleh kosong, dan **tidak boleh diturunkan
   mekanis dari sentimen**.

---

**Latihan:** Tentukan emosi untuk tiap aspek:
1. "Saya khawatir soal kebersihan dapurnya."
2. "Restoran favorit saya sejak dulu."
3. "Menunya standar lah."

(Jawaban: 1. takut (khawatir). 2. cinta (favorit). 3. netral.)

---

*Lanjut ke [022f: Format Data — cara mencatat supaya rapi](./022f_format_data.md).*
