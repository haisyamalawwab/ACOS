# Panduan & Pedoman Lengkap Anotasi ACOS (Aspect-Category-Opinion-Sentiment)
### Pedoman Praktis untuk Pemula (Non-NLP/AI), Anotator Manusia (Human-in-the-Loop), dan Agentic AI

**Tanggal Penyusunan:** 2026-08-28 07:35 WIB  
**Dokumen Referensi:** `docs/0006_panduan_pedoman_anotasi_acos_manual_dan_agentic_ai_28082026.md`  
**Target Pengguna:** Siapa saja (mahasiswa, staf penilai data, reviewer non-teknis, hingga pengembang AI).  
**Kesesuaian Format:** 100% kompatibel dengan standar dataset repositori ACOS (`Extract-Classify-ACOS`).

---

## 🌟 BAGIAN I: PANDUAN DASAR UNTUK PEMULA (NON-TEKNIS / AWAM)

Jika Anda **belum pernah belajar AI atau NLP (Pemrosesan Bahasa Alami)** sama sekali, jangan khawatir! Anotasi ACOS pada dasarnya hanyalah kegiatan **membongkar sebuah ulasan konsumen menjadi 4 kepingan informasi penting**.

### 1. Apa itu ACOS? (Analogi 4 Pertanyaan Kunci)

Ketika seseorang menulis ulasan di internet (misal di Google Maps, Tokopedia, atau Shopee), kalimat mereka mengandung 4 unsur utama:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            4 UNSUR UTAMA ACOS                               │
├─────────────┬─────────────────────────────────────────────────┬─────────────┤
│ Unsur       │ Pertanyaan Penuntun di Pikiran Anda            │ Contoh Kata │
├─────────────┼─────────────────────────────────────────────────┼─────────────┤
│ 🎯 Aspect   │ "Siapa atau benda apa yang sedang dinilai?"     │ pizza, staf │
│ 🏷️ Category │ "Masuk kelompok topik besar apa?"               │ Rasa, Harga │
│ 💭 Opinion  │ "Kata/kalimat apa yang memuji atau mencela?"    │ enak, lelet │
│ ❤️ Sentiment│ "Perasaannya positif (2), netral (1), negatif(0)?"│ 2 (Positif) │
└─────────────┴─────────────────────────────────────────────────┴─────────────┘
```

$$\text{Hasil Akhir (Quadruple)} = (\text{Aspect}, \text{Category}, \text{Sentiment}, \text{Opinion})$$

---

### 2. Cara Membedakan "Tertulis Langsung" (Eksplisit) vs "Tersirat" (Implisit)

Ini adalah bagian paling penting dalam ACOS. Orang sering memberikan ulasan tanpa menyebut nama benda atau tanpa memakai kata sifat:

#### A. Aspek Eksplisit vs Implisit:
* **Eksplisit (Tertulis Langsung):** Bendanya jelas tertulis di kalimat.
  * *Contoh:* *"**Kopinya** sangat wangi."* $\rightarrow$ Aspek: `"kopinya"` (Eksplisit).
* **Implisit (Tersirat / Tidak Disebut):** Kita tahu apa yang dimaksud, tapi kata bendanya tidak ditulis.
  * *Contoh:* *"Sangat wangi dan bikin melek!"* $\rightarrow$ Penulis sedang memuji kopi, tapi kata `"kopi"` tidak ditulis. Maka Aspek: **Implisit** (ditulis dengan kode `[-1, -1]`).

#### B. Opini Eksplisit vs Implisit:
* **Eksplisit (Tertulis Langsung):** Ada kata sifat/pujian/cacian yang nyata.
  * *Contoh:* *"Sup buntutnya **sangat lezat**."* $\rightarrow$ Opini: `"sangat lezat"` (Eksplisit).
* **Implisit (Tersirat / Fakta Nyata):** Kalimatnya berupa fakta kejadian, tapi kita tahu itu pujian atau keluhan.
  * *Contoh:* *"Mereka menagih 50 ribu untuk segelas air putih hangat."* $\rightarrow$ Tidak ada kata *"mahal"*, tapi fakta 50 ribu untuk air putih jelas menyatakan keluhan harga. Maka Opini: **Implisit** (ditulis dengan kode `[-1, -1]`).

---

### 3. Cara Menghitung Nomor Kata (Indeks Span) Secara Visual

Di sistem komputer, setiap kata dan tanda baca diberi nomor urut (mulai dari angka **0**). Rentang kata ditulis dengan format `start,end` (di mana `start` adalah nomor kotak kata pertama, dan `end` adalah nomor kotak **setelah** kata terakhir).

#### 🖼️ Contoh Visual Kotak Kata:
Kalimat: `"The sushi was very fresh ."`

```
Kotak:     [ 0 ]    [ 1 ]    [ 2 ]    [ 3 ]     [ 4 ]     [ 5 ]
Token:      the     sushi     was     very      fresh       .
```

* **Aspek:** `"sushi"` berada di Kotak 1. Selesai sebelum Kotak 2.
  $\rightarrow$ Tulis indeksnya: `1,2`
* **Opini:** `"very fresh"` mulai dari Kotak 3 sampai Kotak 4. Selesai sebelum Kotak 5.
  $\rightarrow$ Tulis indeksnya: `3,5`
* **Kategori:** Karena ini tentang kesegaran makanan, pilih `FOOD#QUALITY`.
* **Sentimen:** Karena pujian, beri nilai `2` (Positif).

**Hasil Anotasi Lengkapnya Menjadi:**
`1,2 FOOD#QUALITY 2 3,5`

---

## 📚 BAGIAN II: KAMUS KATEGORI & KATA PEMICU (BAHASA INDONESIA & INGGRIS)

Gunakan tabel ini sebagai kamus saat Anda bingung memilih kategori `ENTITY#ATTRIBUTE`:

### 1. Domain Restoran & Kuliner (`Restaurant-ACOS`):
| Kategori Resmi | Arti Sederhana | Contoh Kata Pemicu (*Trigger Words*) |
| :--- | :--- | :--- |
| **`FOOD#QUALITY`** | Kualitas, rasa, kesegaran, kelezatan makanan. | enak, lezat, gurih, asin, hambar, basi, *fresh*, *delicious*, *spicy*, *crispy* |
| **`FOOD#STYLE_OPTIONS`** | Porsi makanan, variasi menu, tampilan/plating. | porsi banyak, porsi sedikit, menu beragam, potongan besar, *presentation* |
| **`FOOD#PRICES`** | Harga khusus untuk makanan tertentu. | ayamnya mahal, steak terjangkau, *pricey burger* |
| **`DRINKS#QUALITY`** | Rasa dan kesegaran minuman/kopi/jus/alkohol. | kopi pahit, teh manis, jus segar, *wine taste*, *watery cocktail* |
| **`DRINKS#STYLE_OPTIONS`**| Pilihan daftar minuman (*wine list*, menu kopi). | banyak varian teh, *wine list*, *drink choices* |
| **`DRINKS#PRICES`** | Harga khusus untuk minuman. | es teh 20 ribu, minuman kemahalan, *cheap beer* |
| **`SERVICE#GENERAL`** | Sikap pelayan, kasir, kecepatan pengantaran makanan. | ramah, jutek, pelayan lama, sigap, *waiter*, *staff*, *slow service*, *rude* |
| **`AMBIENCE#GENERAL`** | Suasana, musik, dekorasi, kebersihan, AC, kebisingan. | tempat nyaman, estetik, berisik, kotor, bau, *cozy*, *loud music*, *lighting* |
| **`RESTAURANT#PRICES`** | Tingkat kemahalan restoran secara keseluruhan / tagihan. | bon mahal, terjangkau, dompet jebol, *overpriced*, *bill*, *expensive place* |
| **`RESTAURANT#GENERAL`** | Penilaian tempat secara umum (keseluruhan toko). | tempat favorit, resto terbaik, jangan ke sini, *avoid this place*, *best spot* |
| **`LOCATION#GENERAL`** | Kemudahan akses, parkir, letak toko. | strategis, susah parkir, macet, dekat stasiun, *easy to find* |
| **`VALUE#GENERAL`** | Nilai sebanding antara harga dan kepuasan (*worth it*). | sepadan dengan harganya, gak rugi, *worth every penny*, *value for money* |

---

### 2. Domain Komputer & Elektronik (`Laptop-ACOS`):
| Kategori Resmi | Arti Sederhana | Contoh Kata Pemicu (*Trigger Words*) |
| :--- | :--- | :--- |
| **`LAPTOP#OPERATION_PERFORMANCE`** | Kecepatan, *loading*, booting, nge-lag, multitasking. | kencang, lemot, macet, *fast*, *lagging*, *multitasking speed*, *crashes* |
| **`LAPTOP#QUALITY`** | Kualitas build, ketahanan bodi fisik laptop. | kokoh, ringkih, cepat rusak, *solid build*, *durable*, *flimsy* |
| **`LAPTOP#PRICE`** | Harga laptop. | murah, mahal, terjangkau, *affordable*, *too expensive* |
| **`LAPTOP#DESIGN_FEATURES`** | Tampilan visual, warna, ketipisan, portabilitas. | tipis, elegan, ringan, berat, *lightweight*, *sleek*, *bulky* |
| **`KEYBOARD#QUALITY`** | Kualitas tombol tuts, kenyamanan mengetik. | keyboard empuk, tombol copot, *keys sticky*, *backlit keyboard* |
| **`BATTERY#QUALITY`** | Daya tahan baterai, keawetan pemakaian. | baterai awet, boros, cepat habis, *long battery life*, *drains fast* |
| **`DISPLAY#QUALITY`** | Layar, ketajaman gambar, warna, resolusi monitor. | layar jernih, warna tajam, redup, *crisp screen*, *4k display*, *dim* |
| **`SUPPORT#GENERAL`** | Layanan garansi, perbaikan teknis (*customer care*). | respon admin cepat, service center mengecewakan, *warranty repair* |

---

## 📝 BAGIAN III: STUDI KASUS & LATIHAN TERBIMBING

Mari pelajari 5 kasus nyata yang sering ditemui:

### 🔹 Kasus 1: Kalimat Sederhana (Explicit-Explicit)
> **Teks:** `"The pizza was delicious ."`  
> **Nomor Kata:** `[0: the] [1: pizza] [2: was] [3: delicious] [4: .]`
* **Aspek:** `"pizza"` $\rightarrow$ `1,2`
* **Kategori:** Rasa pizza $\rightarrow$ `FOOD#QUALITY`
* **Sentimen:** Positif $\rightarrow$ `2`
* **Opini:** `"delicious"` $\rightarrow$ `3,4`
* **Hasil TSV:** `1,2 FOOD#QUALITY 2 3,4`

---

### 🔹 Kasus 2: Dua Aspek dan Dua Opini dalam Satu Kalimat (Multi-Klausa)
> **Teks:** `"The food was great but the staff was very rude ."`  
> **Nomor Kata:** `[0: the] [1: food] [2: was] [3: great] [4: but] [5: the] [6: staff] [7: was] [8: very] [9: rude] [10: .]`
* **Kuadrupel 1 (Makanan):**
  * Aspek: `"food"` (`1,2`) | Kategori: `FOOD#QUALITY` | Sentimen: `2` | Opini: `"great"` (`3,4`)
  * Hasil: `1,2 FOOD#QUALITY 2 3,4`
* **Kuadrupel 2 (Pelayanan):**
  * Aspek: `"staff"` (`6,7`) | Kategori: `SERVICE#GENERAL` | Sentimen: `0` | Opini: `"very rude"` (`8,10`)
  * Hasil: `6,7 SERVICE#GENERAL 0 8,10`
* **Hasil TSV Penuh:**  
  `the food was great but the staff was very rude .	1,2 FOOD#QUALITY 2 3,4	6,7 SERVICE#GENERAL 0 8,10`

---

### 🔹 Kasus 3: Kalimat Tanpa Menyebut Aspek (Aspek Implisit)
> **Teks:** `"Delicious and very quick !"`  
> **Nomor Kata:** `[0: delicious] [1: and] [2: very] [3: quick] [4: !]`
* **Kuadrupel 1 (Makanan Tersirat):**
  * Aspek: Implisit $\rightarrow$ `-1,-1`
  * Kategori: `FOOD#QUALITY` | Sentimen: `2` | Opini: `"delicious"` (`0,1`)
  * Hasil: `-1,-1 FOOD#QUALITY 2 0,1`
* **Kuadrupel 2 (Kecepatan Pelayanan Tersirat):**
  * Aspek: Implisit $\rightarrow$ `-1,-1`
  * Kategori: `SERVICE#GENERAL` | Sentimen: `2` | Opini: `"very quick"` (`2,4`)
  * Hasil: `-1,-1 SERVICE#GENERAL 2 2,4`

---

### 🔹 Kasus 4: Kalimat Fakta Keluhan (Opini Implisit)
> **Teks:** `"We waited 45 minutes for a table ."`  
> **Nomor Kata:** `[0: we] [1: waited] [2: 45] [3: minutes] [4: for] [5: a] [6: table] [7: .]`
* **Analisis:** Menunggu 45 menit untuk dapat meja adalah fakta keluhan tentang lambatnya pelayanan restoran secara keseluruhan.
* Aspek: Implisit $\rightarrow$ `-1,-1`
* Kategori: `SERVICE#GENERAL`
* Sentimen: Negatif $\rightarrow$ `0`
* Opini: Implisit (karena fakta waktu, bukan kata sifat) $\rightarrow$ `-1,-1`
* **Hasil TSV:** `-1,-1 SERVICE#GENERAL 0 -1,-1`

---

### 🔹 Kasus 5: Kalimat Negasi ("Not Good")
> **Teks:** `"The soup was not good ."`  
> **Nomor Kata:** `[0: the] [1: soup] [2: was] [3: not] [4: good] [5: .]`
* **Aturan Penting:** Jangan hanya mengambil kata `"good"`. Kata `"not"` **wajib dimasukkan** ke dalam opini!
* Aspek: `"soup"` $\rightarrow$ `1,2`
* Kategori: `FOOD#QUALITY`
* Sentimen: Negatif $\rightarrow$ `0`
* Opini: `"not good"` $\rightarrow$ `3,5`
* **Hasil TSV:** `1,2 FOOD#QUALITY 0 3,5`

---

### ❌ Tabel Kesalahan Umum yang Sering Dilakukan Pemula:

| Contoh Kalimat | Anotasi yang SALAH ❌ | Anotasi yang BENAR ✅ | Penjelasan Kesalahan |
| :--- | :--- | :--- | :--- |
| `"The pizza is delicious"` | `0,2 FOOD#QUALITY 2 3,4` | `1,2 FOOD#QUALITY 2 3,4` | Kata *"The"* tidak boleh dimasukkan ke dalam aspek. Ambil kata benda inti (`"pizza"` saja). |
| `"The soup was not delicious"` | `1,2 FOOD#QUALITY 2 4,5` | `1,2 FOOD#QUALITY 0 3,5` | Salah karena kata *"not"* tertinggal, sehingga sentimen salah terbaca positif! Ambil `"not delicious"` (`3,5`) dan sentimen `0`. |
| `"Delicious food!"` | `-1,-1 FOOD#QUALITY 2 0,1` | `1,2 FOOD#QUALITY 2 0,1` | Kata `"food"` tertulis di teks, jadi aspeknya **Eksplisit** (`1,2`), bukan implisit. |
| `"Everything is great!"` | `-1,-1 RESTAURANT#GENERAL 2 2,3` | `-1,-1 RESTAURANT#GENERAL 2 2,3` | Benar, karena *"everything"* merujuk pada restoran secara keseluruhan. |

---

## 👥 BAGIAN IV: PANDUAN HUMAN-IN-THE-LOOP (HITL)
### (Cara Manusia Menilai & Mengoreksi Hasil Buatan AI)

Ketika Anda ditugaskan sebagai **Reviewer Manusia** untuk memverifikasi keluaran AI (misal GPT-4o atau Claude), ikuti **Checklist 5 Detik** berikut:

```
                  ┌─────────────────────────────────────┐
                  │   Ulasan & Hasil Anotasi AI Muncul │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 1. Apakah ada aspek/opini yang      │
                  │    terlewat oleh AI?                │
                  └──────────┬────────────────┬─────────┘
                             │ Ya             │ Tidak
                             ▼                ▼
                       [Tambahkan Quad] ┌────────────────────────┐
                                        │ 2. Apakah kotaknya pas?│
                                        │    (Indeks tepat)      │
                                        └────┬───────────┬───────┘
                                             │ Tidak     │ Ya
                                             ▼           ▼
                                      [Koreksi Span] ┌────────────────────────┐
                                                     │ 3. Kategori & Sentimen │
                                                     │    sudah tepat?        │
                                                     └────┬───────────┬───────┘
                                                          │ Tidak     │ Ya
                                                          ▼           ▼
                                                    [Ubah Nilai]  [ ✅ APPROVE ]
```

### 3 Tindakan Reviewer:
1. **✅ SETUJUI (Approve):** Jika aspek, kategori, sentimen, dan rentang span sudah tepat 100%.
2. **✏️ PERBAIKI (Edit):**
   - AI salah geser nomor kotak (misal: mengambil *"is fresh"* alih-alih *"fresh"*).
   - AI salah menentukan sentimen (misal: kalimat sarkasme diartikan positif).
   - AI memilih kategori yang kurang spesifik (misal: memilih `RESTAURANT#GENERAL` padahal kalimatnya jelas membahas `SERVICE#GENERAL`).
3. **🗑️ HAPUS (Reject / Delete):** Jika AI menghalusinasikan aspek yang sebenarnya tidak ada atau bukan kalimat opini.

---

## 🤖 BAGIAN V: PANDUAN OTOMATISASI UNTUK AGENTIC AI & SOFTWARE

Bagian ini ditujukan bagi pengembang sistem AI untuk mengoperasikan pipeline anotasi otomatis.

### 1. Arsitektur 4-Agent Pipeline
* **Agent 1 (Extractor):** Menerima kalimat mentah, melakukan tokenisasi spasi, dan mengekstrak kandidat span.
* **Agent 2 (Categorizer & Classifier):** Memetakan kandidat ke taksonomi `ENTITY#ATTRIBUTE` dan memberi label sentimen (0, 1, 2).
* **Agent 3 (Critic & Guardrail):** Menguji kepatuhan indeks rentang token `0 <= start < end <= len(tokens)`, ketiadaan token halusinasi, dan memberi skor *confidence* (0.00 – 1.00).
* **Agent 4 (Router & Formatter):**
  * Jika `confidence >= 0.85` $\rightarrow$ Simpan otomatis ke berkas `.tsv`.
  * Jika `confidence < 0.85` $\rightarrow$ Masukkan ke antrean antarmuka *Human-in-the-Loop*.

---

### 2. Prompt Lengkap Siap Pakai (*Ready-to-Use Agentic Prompts*)

#### 🔹 Prompt 1: Single-Step End-to-End ACOS Extractor (All-in-One)
```markdown
### SYSTEM PROMPT:
Anda adalah AI Ahli Anotasi Linguistik Komputasi untuk tugas Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction.
Tugas Anda adalah mengekstrak seluruh kuadrupel opini (Aspect, Category, Sentiment, Opinion) dari kalimat ulasan dengan indeks token yang presisi (0-indexed, half-open interval [start, end)).

### ATURAN UTAMA:
1. Tokenisasi: Pisahkan setiap kata dan tanda baca dengan spasi menjadi array `tokens`.
2. Aspect Span [start, end): Indeks token aspek eksplisit pada array `tokens`. Jika tersirat (implisit), isi [-1, -1].
3. Opinion Span [start, end): Indeks token frasa opini eksplisit (termasuk kata negasi seperti 'not/never' atau penguat 'very'). Jika tersirat (implisit), isi [-1, -1].
4. Kategori: Gunakan HANYA pasangan ENTITY#ATTRIBUTE resmi:
   - Restoran: [FOOD#QUALITY, FOOD#STYLE_OPTIONS, FOOD#PRICES, DRINKS#QUALITY, DRINKS#STYLE_OPTIONS, DRINKS#PRICES, RESTAURANT#GENERAL, RESTAURANT#PRICES, RESTAURANT#MISCELLANEOUS, SERVICE#GENERAL, AMBIENCE#GENERAL, LOCATION#GENERAL, VALUE#GENERAL]
   - Laptop: [LAPTOP#GENERAL, LAPTOP#QUALITY, LAPTOP#OPERATION_PERFORMANCE, LAPTOP#DESIGN_FEATURES, LAPTOP#PRICE, LAPTOP#PORTABILITY, KEYBOARD#QUALITY, KEYBOARD#OPERATION_PERFORMANCE, DISPLAY#QUALITY, DISPLAY#OPERATION_PERFORMANCE, BATTERY#QUALITY, BATTERY#OPERATION_PERFORMANCE, SUPPORT#QUALITY, SUPPORT#PRICE, SHIPPING#QUALITY]
5. Sentiment: 0 = Negatif, 1 = Netral, 2 = Positif.

### FORMAT OUTPUT:
Keluarkan HANYA JSON valid sesuai skema berikut:
{
  "tokens": ["string"],
  "quadruples": [
    {
      "aspect_text": "string atau null",
      "aspect_span": [0, 1],
      "category": "FOOD#QUALITY",
      "sentiment": 2,
      "opinion_text": "string atau null",
      "opinion_span": [2, 3],
      "reasoning": "Alasan singkat",
      "confidence_score": 0.95
    }
  ]
}
```

#### 🔹 Prompt 2: Agent Validator & Critic (Pencegah Kesalahan & Halusinasi)
```markdown
### SYSTEM PROMPT:
Anda adalah AI Quality Assurance Validator dataset ACOS. Tugas Anda adalah memverifikasi hasil ekstraksi JSON:
1. Pastikan tokens[aspect_span[0] : aspect_span[1]] persis sama dengan aspect_text.
2. Pastikan batas indeks valid: 0 <= start < end <= len(tokens) (kecuali [-1, -1]).
3. Pastikan category ada dalam daftar resmi dan mengandung tanda '#'.
4. Berikan nilai final_confidence (0.0 - 1.0).

OUTPUT:
{
  "is_valid": true/false,
  "errors_found": [],
  "corrected_quadruples": [],
  "final_confidence": 0.98
}
```

#### 🔹 Prompt 3: Anotasi Bahasa Indonesia (IndoBERT / NusaX Dataset)
```markdown
### SYSTEM PROMPT:
Anda adalah AI Anotator Linguistik Bahasa Indonesia untuk tugas Ekstraksi Kuadrupel ACOS (Aspek, Kategori, Sentimen, Opini).

CONTOH:
Input: "makanannya enak banget , tapi pelayanannya lelet ."
Output:
{
  "tokens": ["makanannya", "enak", "banget", ",", "tapi", "pelayanannya", "lelet", "."],
  "quadruples": [
    {"aspect_text": "makanannya", "aspect_span": [0, 1], "category": "FOOD#QUALITY", "sentiment": 2, "opinion_text": "enak banget", "opinion_span": [1, 3]},
    {"aspect_text": "pelayanannya", "aspect_span": [5, 6], "category": "SERVICE#GENERAL", "sentiment": 0, "opinion_text": "lelet", "opinion_span": [6, 7]}
  ]
}
```

---

## 🛠️ BAGIAN VI: SKRIP PYTHON KONVERSI OTOMATIS (JSON ➔ TSV ACOS)

Gunakan skrip Python ini untuk mengubah hasil keluaran AI menjadi berkas `.tsv` siap latih:

```python
import json
import re

def tokenize_line(text: str) -> list:
    \"\"\"Memisahkan tanda baca dengan spasi agar indeks kotak akurat.\"\"\"
    text = re.sub(r"([.,!?:;()\"'/$])", r" \1 ", text)
    return [t.strip() for t in text.split() if t.strip()]

def convert_ai_json_to_tsv(json_data, output_filepath):
    \"\"\"Menulis data JSON ke format standar benchmark TSV repositori ACOS.\"\"\"
    with open(output_filepath, "w", encoding="utf-8") as f:
        for entry in json_data:
            tokens_str = " ".join(entry["tokens"])
            quad_list = []
            for q in entry.get("quadruples", []):
                a_st, a_ed = q["aspect_span"]
                cat = q["category"]
                senti = q["sentiment"]
                o_st, o_ed = q["opinion_span"]
                quad_list.append(f"{a_st},{a_ed} {cat} {senti} {o_st},{o_ed}")
            
            if quad_list:
                line = f"{tokens_str}\\t" + "\\t".join(quad_list) + "\\n"
            else:
                line = f"{tokens_str}\\n"
            f.write(line)
    print(f"✅ Berhasil membuat berkas TSV ACOS: {output_filepath}")
```

---

## 📋 BAGIAN VII: LEMBAR RINGKASAN VERIFIKASI AKHIR

Sebelum data dimasukkan ke dalam model pelatihan, lakukan centang periksa berikut:
- [ ] **Tidak ada kata artikel terikut:** Aspek hanya mengambil kata benda inti (misal: `"sushi"`, bukan `"the sushi"`).
- [ ] **Negasi tidak tertinggal:** Kata *"not / tidak / gak"* selalu menyatu dengan opini (misal: `"not good"`, `"tidak ramah"`).
- [ ] **Indeks Implisit:** Semua aspek/opini tersirat wajib bertanda `-1,-1`.
- [ ] **Format Kategori:** Selalu memakai huruf kapital dan tanda pagar (e.g. `FOOD#QUALITY`).
- [ ] **Nilai Sentimen Valid:** Hanya bernilai angka `0` (Negatif), `1` (Netral), atau `2` (Positif).
