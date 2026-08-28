# absa5 — ACOS quadruple → ACOSE quintuple

Menambahkan elemen **emosi** ke pipeline ACOS, sehingga tuple berubah dari
4 elemen `(aspek, kategori, opini, sentimen)` menjadi 5 elemen
`(aspek, kategori, opini, sentimen, emosi)`.

Perbedaan mendasar dari cara upstream (Cai 2021,
[doi:10.18653/v1/2021.acl-long.29](https://doi.org/10.18653/v1/2021.acl-long.29)):
di `Extract-Classify-ACOS/` jumlah elemen di-hardcode di sepanjang kode
(`quad.split(' ')[0]`, `label_map_senti`, `nn.Linear(768*2, 39)`). Di sini bentuk
tuple adalah **data**, bukan kode:

```python
QUAD  = TupleSchema(elements=(ASPECT, CATEGORY, SENTIMENT, OPINION), ...)
QUINT = QUAD.extend(EMOTION)          # itu saja
```

Satu jalur kode melayani keduanya. Menambah elemen keenam nanti tidak menyentuh
tokenizer, remapper span, encoder fitur, maupun metrik.

Kode upstream **tidak diubah sama sekali**, jadi pipeline English 4-elemen tetap
bisa dijalankan sebagai kontrol.

## Status yang sudah terverifikasi

```
$ python -m absa5.selftest --repo .
13/13 gates passed
```

Semua gate berjalan **tanpa torch, numpy, atau GPU** — mesin lokal ini memang
tidak punya paket ML (Python 3.14.2). Yang belum terverifikasi: training
sesungguhnya, karena butuh Colab. Gate `torch_free` menjaga batas itu agar tidak
bocor secara diam-diam.

| Gate | Yang dibuktikan |
|---|---|
| `schema` | quad dan quint parse + round-trip identik; cell quad terbaca sebagai quint |
| `span_remap` | **18.862 span di 6.359 baris** ter-remap tepat sama dengan `tokenized_data/*_quad_bert.tsv` bawaan repo |
| `pair_format` | 2.417 baris pair direkonstruksi identik dengan `rest16_train_pair.tsv` |
| `tag_parsing` | 3 bentuk tag valid diterima, 8 bentuk rusak ditolak (akar `KeyError` Step 2) |
| `features` | encoding tag/mask round-trip; urutan tag sama dengan upstream |
| `metrics` | scoring multiset, proyeksi subset elemen, breakdown eksplisit/implisit |
| `decode` | decoding label joint dan factored, perakitan tuple |
| `rekey` | re-keying `state_dict` untuk dua konvensi prefix, idempoten |
| `emotion` | tagger membedakan dua tuple dalam satu kalimat |
| `config` | round-trip JSON, override bertitik, penolakan key tak dikenal |
| `references` | 24 sitasi well-formed, 21 ber-DOI, 3 terdokumentasi tidak punya DOI |
| `torch_free` | 18 modul terimpor tanpa dependensi ML |
| `prepare` | jalur persiapan data end-to-end pada data demo Indonesia |

## Temuan dari analisis kode

Empat hal yang ditemukan dengan membaca kode dan data, bukan mengasumsikannya.

### 1. Ruang label meledak, dan itu keputusan arsitektur utama

Upstream memakai satu classifier atas **cross product** kategori × sentimen:
13 × 3 = 39 output (`modeling.py:1608`). Menambahkan 5 emosi menjadikannya
13 × 3 × 5 = **195 output**. Diukur pada data rest16 yang ada:

```
$ python -m absa5 inspect --schema quad --category rest16 \
    --data data/Restaurant-ACOS/rest16_quad_train.tsv

joint cells seen       34/39 (87.2%)
cells with under 10    10
```

Pada 4 elemen, 87% sel joint pernah muncul. Menambah emosi membagi 2.484 tuple
yang sama ke 195 sel — mayoritas sel akan kosong atau berisi satu contoh.
Karena itu head `factored` (13 + 3 + 5 = **21 output**, satu classifier per
elemen) adalah default untuk quint, dan `joint` tetap tersedia untuk
membandingkan pada 4 elemen. Pilihannya satu baris config:

```json
"heads": { "label_mode": "factored" }
```

### 2. Emosi bisa jadi hanya nama lain dari sentimen — dan itu terukur

Ini risiko terbesar secara ilmiah, bukan teknis. Secara teori keduanya memang
sumbu yang berbeda — valensi hanya satu dimensi dari ruang afek, bukan
keseluruhannya (Russell 1980, [doi:10.1037/h0077714](https://doi.org/10.1037/h0077714)).
Tapi teori hanya bilang perbedaan itu *bisa* ada; apakah sebuah file anotasi
benar-benar mempertahankannya adalah pertanyaan empiris.

Kalau setiap nilai sentimen memetakan ke tepat satu emosi, elemen kelima tidak
menambah informasi apa pun. `absa5.emotion.sentiment_redundancy` menghitung
H(emosi | sentimen) dalam bit, dan pada output leksikon sendiri hasilnya jujur:

```
$ python -m absa5 extend-emotion --in data/Restaurant-ACOS/rest16_quad_train.tsv ...
emotion given sentiment: {'0': {'marah': 733}, '1': {'netral': 95}, '2': {'senang': 1656}}
redundancy check: the emotion column is a deterministic renaming of sentiment and
adds no information
```

Angka itu muncul karena leksikon Indonesia tidak cocok untuk teks English,
sehingga semuanya jatuh ke fallback sentimen. Tapi fungsinya justru itu: kalau
data hasil anotasi manusia nanti memberi verdict yang sama, elemen emosi tidak
layak dilatih.

### 3. Skrip pembuat `tokenized_data/` tidak ada di repo — dan sekarang ada

Offset di `tokenized_data/*.tsv` menunjuk **token whitespace pada teks yang sudah
ter-WordPiece**, bukan indeks karakter dan bukan subword runtime:

```
data/…/rest16_quad_test.tsv       : serves really good sushi .      → span 3,4
tokenized_data/…_quad_bert.tsv    : serves really good su ##shi .   → span 3,5
```

Generatornya tidak pernah dirilis. `absa5.spans` + `absa5.data.convert_file`
mengisi celah itu, dan gate `span_remap` membuktikannya terhadap 18.862 span
ground truth yang sudah ada di repo. Tokenizer masuk sebagai **parameter**, jadi
XLM-R atau IndoRoBERTa nanti tidak perlu generator baru.

### 4. Bug yang ditemukan di data dan di metrik upstream

**Data.** `rest16_quad_train.tsv` baris 451 punya span opini `3,3` — lebar nol.
File turunan penulisnya sendiri tidak sepakat: `rest16_train_quad_bert.tsv`
menulis `3,4`, `rest16_train_pair.tsv` menulis `3,5`, dan file pair juga
menghilangkan satu dari tiga tuple kalimat itu. Span dilebarkan ke satu token dan
perbaikannya dicatat, tidak disembunyikan; baris itu dikecualikan dari gate
dengan nama, dan sisanya dipegang pada kesamaan persis.

**Metrik.** `measureQuad` (`eval_metrics.py:32`) menghitung kecocokan dengan
`in`, sehingga prediksi duplikat dihitung dua kali terhadap satu gold tuple.
`measureQuad_imp` (`:215-221`) mencetak lima bucket tapi hanya me-return bucket
**terakhir**, jadi empat breakdown terbuang. Keduanya diperbaiki di
`absa5.metrics` dan diuji di gate `metrics`.

**Parsing tag.** `get_1st_pairs.py:42-47` memakai `ele.startswith('a')` lalu
`ele[2:]`, dan cabang `else` memasukkan apa pun ke daftar opini — termasuk token
rusak. `absa5.data.parse_tag` memvalidasi pola secara eksplisit.

### 5. Bobot encoder bisa gagal termuat tanpa satu pun pesan error

`indobenchmark/indobert-base-p1` menyimpan key mulai dari `embeddings.*` tanpa
prefix `bert.`. Loader legacy hanya menambahkan prefix bila model **tidak** punya
atribut `bert` (`modeling.py:744-747`) — padahal model tugas punya. Tiga blok
logging `missing_keys` yang seharusnya melaporkan ini dalam keadaan
**di-comment** (`modeling.py:748-753`). Hasilnya: training jalan mulus dengan
encoder acak.

`absa5.encoders.verify_encoder_weights` membandingkan tensor hidup dengan
checkpoint di disk secara numerik (`torch.allclose`) pada tiga probe key, lalu
memastikan tidak ada key `bert.*` yang hilang. Dipanggil otomatis oleh
`build_extraction_model` dan `build_classification_model`, dan gagal keras.

## Arsitektur

Tiap lapisan hanya bergantung pada lapisan di bawahnya. Torch hanya masuk di
tiga modul teratas, diimpor secara lazy.

```
config      satu pohon dataclass yang menentukan seluruh run
pipeline    orkestrasi end-to-end
engine      loop training dan inferensi                    ← torch
models      model per tahap, dirakit dari config            ← torch
heads       head span / implisit / label                   ← torch
─────────────────────────────────────────────────────────── batas torch
encoders    penyiapan checkpoint + gate pemuatan bobot
emotion     bootstrap quad→quint + alur kerja anotasi
decode      output model kembali menjadi tuple
metrics     scoring tuple per subset elemen dan implisitness
features    record → array integer, skema tagging pluggable
data        baca/tulis dua format on-disk
spans       remap span kata → subword
tokenizers  adapter atas satu metode: tokenize(word)
references  sitasi ber-DOI, terverifikasi Crossref
taxonomy    kosakata label, joint vs factored
schema      elemen tuple dan serialisasinya
registry    pencarian nama → factory
```

Kontrak yang membuat encoder bisa ditukar: hasilkan
`(batch, seq, hidden)` + satu vektor kalimat. `SequenceEncoder` di
`absa5/models.py` menyembunyikan backbone di belakang kontrak itu, jadi BiLSTM
atau XLM-R nanti tidak menyentuh head. Yang sudah reusable dari upstream adalah
CRF-nya (Lafferty 2001, tanpa DOI — lihat §Referensi) — `torchcrf` tidak
bergantung pada BERT. Arsitektur BiLSTM-CRF untuk tagging span mengikuti
Lample 2016, [doi:10.18653/v1/N16-1030](https://doi.org/10.18653/v1/N16-1030).

Semua titik pluggable adalah registry bernama:

```
$ python -m absa5 registries
schema           quad, quint
category set     rest16, resto_id
sentiment set    acos, id
emotion set      ekman, emot, emot_id, emot_id_netral, goemotions, none,
                 nusaparagraph, plutchik
tokenizer        hf, legacy_bert, whitespace, wordpiece
tagging          bio
emotion tagger   constant, lexicon
preset           quad_bert_en, quint_dryrun_en, quint_indobert_id
```

## Taksonomi emosi

Tidak ada dataset publik dengan 5 elemen (aspek, kategori, opini, sentimen,
emosi). "Quintuple" di literatur ABSA sudah dipakai untuk dua hal lain: ACOSI —
elemen kelimanya penanda implisit, bukan emosi (Peper 2024,
[doi:10.18653/v1/2024.findings-emnlp.907](https://doi.org/10.18653/v1/2024.findings-emnlp.907))
— dan COQE untuk opini komparatif. Karya terdekat yang menggabungkan emosi dengan
ekstraksi terstruktur adalah emotion-cause pair extraction, tapi bekerja pada
klausa bukan aspek (Xia 2019,
[doi:10.18653/v1/P19-1096](https://doi.org/10.18653/v1/P19-1096)). Jadi elemen
emosi ini memang baru, dan kolomnya harus dibuat.

Pilihan taksonomi yang tersedia, dan konfliknya:

| Registry | Label | Sumber |
|---|---|---|
| `emot` | sadness, anger, love, fear, happy | IndoNLU EmoT, verbatim (`happy`, bukan `joy`) — [doi:10.18653/v1/2020.aacl-main.85](https://doi.org/10.18653/v1/2020.aacl-main.85), korpus [doi:10.1109/IALP.2018.8629262](https://doi.org/10.1109/IALP.2018.8629262) |
| `emot_id` | sedih, marah, cinta, takut, senang | EmoT diterjemahkan, untuk anotator |
| `emot_id_netral` | + netral | **default tagger** |
| `nusaparagraph` | angry, disgusted, fear, happy, sad, shame, surprise | NusaWrites — [doi:10.18653/v1/2023.ijcnlp-main.60](https://doi.org/10.18653/v1/2023.ijcnlp-main.60); satu-satunya set Indonesia dengan disgust dan surprise |
| `ekman` | anger, disgust, fear, happiness, sadness, surprise | [doi:10.1080/02699939208411068](https://doi.org/10.1080/02699939208411068) |
| `plutchik` | 8 kelas dalam 4 pasangan bipolar | [doi:10.1016/B978-0-12-558701-3.50007-7](https://doi.org/10.1016/B978-0-12-558701-3.50007-7) |
| `goemotions` | 27 + neutral | [doi:10.18653/v1/2020.acl-main.372](https://doi.org/10.18653/v1/2020.acl-main.372); terdaftar untuk kelengkapan, tidak realistis di sini (28 × 13 × 3 = 1.092 sel joint) |
| `none` | netral saja | membuat run quint tereduksi menjadi quad |

`emot_id_netral` menambahkan kelas netral karena EmoT dibangun dari tweet, yang
memang terseleksi bermuatan emosi. Tuple ABSA tidak: "harganya wajar" bersentimen
positif tanpa muatan emosi, dan memaksanya masuk salah satu dari lima kelas akan
menyuntikkan noise ke kelas yang dipaksa itu. GoEmotions mempertahankan kelas
neutral dengan alasan yang sama. Konsekuensinya `netral` jadi kelas mayoritas pada
ulasan faktual — karena itu keduanya tersedia, ukur dulu sebelum memilih.

Setiap label set menyebut sumbernya, dan bisa dicek:

```bash
python -m absa5 registries              # label set → sitasi
python -m absa5 references --module taxonomy
```

## Referensi

24 sitasi, 21 ber-DOI yang diverifikasi lewat Crossref REST API pada 2026-08-28
(`absa5/references.py`). Tiga karya memang tidak punya DOI, dan itu dicatat
sebagai keputusan bukan kelalaian:

- **Lafferty, McCallum & Pereira 2001** (CRF) — proceedings ICML 2001 tidak pernah
  didaftarkan DOI. Pakai URL repositori.
- **Loshchilov & Hutter 2019** (AdamW) — paper ICLR/OpenReview tidak ber-DOI.
  Pakai `arXiv:1711.05101`.
- **Ekman 1971** — bab buku dalam seri Nebraska Symposium on Motivation. Jangan
  disubstitusi dengan paper JPSP 1987 yang berbeda.

Akses:

```bash
python -m absa5 references                    # bibliografi lengkap
python -m absa5 references --table            # tabel key → DOI
python -m absa5 references --grouped          # dikelompokkan per modul pemakai
python -m absa5 references --bibtex           # BibTeX
python -m absa5 references --module heads     # hanya yang disitasi modul tertentu
```

Dari Python:

```python
from absa5 import cite, REFERENCES
cite("cai2021acos")                  # 'Cai 2021, doi:10.18653/v1/2021.acl-long.29'
REFERENCES.get("russell1980circumplex").link
```

Gate `references` memeriksa bentuk setiap entri secara offline — prefix DOI,
field tidak kosong, tidak ada identifier ganda, dan setiap `cited_by` menunjuk
modul yang benar-benar ada. Gate **tidak** memanggil Crossref, karena seluruh gate
harus jalan tanpa jaringan; verifikasi DOI dilakukan sekali dan tanggalnya
tercatat di `references.CROSSREF_CHECKED`.

## Alur anotasi

Satu-satunya jalur yang menghasilkan data layak publikasi: leksikon mengusulkan,
manusia memutuskan.

```bash
# 1. ekspor tugas anotasi (CSV + pedoman bahasa Indonesia)
python -m absa5 annotate \
  --in data/Restaurant-ACOS/rest16_quad_train.tsv \
  --out work/tasks.csv --limit 200

# 2. isi kolom emotion_final, lalu gabungkan kembali
python -m absa5 import-annotations \
  --in data/Restaurant-ACOS/rest16_quad_train.tsv \
  --tasks work/tasks_done.csv --out work/train_quint.tsv
```

CSV memuat `emotion_suggested` beserta `evidence` (kata pemicunya), sehingga
usulan yang salah terlihat, bukan tersembunyi. Pedoman anotasi berbahasa
Indonesia ikut dibuat otomatis, lengkap dengan sitasi sumber label set-nya.

`absa5.emotion.agreement` menghitung Cohen's kappa (Cohen 1960,
[doi:10.1177/001316446002000104](https://doi.org/10.1177/001316446002000104)) dan
membacanya dengan pita Landis & Koch (1977,
[doi:10.2307/2529310](https://doi.org/10.2307/2529310)). Pita itu konvensi yang
lazim dipakai, bukan ambang yang diturunkan dari teori — penulis aslinya sendiri
menyebutnya arbitrer. Di bawah 0.4 perbaiki pedoman atau kurangi jumlah label
sebelum melanjutkan.

`extend-emotion` yang mengisi otomatis **bukan** jalur untuk menghasilkan data
latih. Ia ada untuk dua hal: membuat file quad valid secara struktural sebagai
quint, dan mengukur seberapa banyak kerja yang sebenarnya dihemat anotasi.

## Cara pakai

Tanpa torch (mesin lokal):

```bash
python -m absa5.selftest --repo .              # 13 gate
python -m absa5 registries                     # semua nama pluggable + sumbernya
python -m absa5 references                     # bibliografi ber-DOI
python -m absa5 inspect --schema quint --data <file.tsv>
python -m absa5 prepare --config configs/demo_resto_id.json
```

Dengan torch (Colab):

```bash
python -m absa5 prepare-backbone --encoder indobert --output work/indobert
python -m absa5 train --config configs/demo_resto_id.json --checkpoint work/indobert
```

Config bisa dibuat dari preset dengan override bertitik:

```bash
python -m absa5 write-config --preset quint_indobert_id \
  --set train.epochs=3 --set heads.label_mode=joint \
  --output configs/ablation_joint.json
```

## Data demo

`data/Demo-Resto-ID/` berisi 20 kalimat ulasan restoran berbahasa Indonesia
dengan anotasi quintuple lengkap (12 train / 4 dev / 4 test). Fungsinya
**hanya** untuk membuktikan pipeline berjalan — ini bukan dataset, dan angka apa
pun darinya tidak berarti. Data latih sesungguhnya masih menunggu anotasi.

## Yang belum dikerjakan

- **Dataset quintuple Indonesia.** Blocker terbesar; semua yang di atas dibuat
  agar risiko teknis tuntas sebelum anotasi selesai, bukan sesudah.
- Verifikasi training di Colab, termasuk gate bobot pada checkpoint IndoBERT asli.
- Encoder alternatif (BiLSTM-CRF, XLM-R). Kontraknya sudah ada; implementasinya
  belum.
- Ablasi `joint` vs `factored` pada data nyata. Argumennya baru aritmetika ruang
  label, belum angka F1.
