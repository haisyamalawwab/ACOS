# Dev Report 037 — Komposisi Dataset AppsID (26-09-2026)

Sumber: `ACOS-IndoBERT/data/Apps-ACOS/processed/` (dibaca langsung 26-09-2026).
Pertanyaan: apakah ada database dengan kolom `komentar asli | cleaned | ASPECT | Category | Opinion | Sentiment | Emotion` + pasangan `AC | AO | AS | AE`?

Jawaban singkat: tidak ada satu file dengan format persis itu.

## 1. Inventaris file

| File | Ukuran (byte) | Grain | Kunci |
|---|---:|---|---|
| `reviews_clean.csv` | 23.300.216 | 1 baris = 1 ulasan | `review_id` |
| `reviews_labeled.csv` | 25.651.629 | 1 baris = 1 ulasan | `review_id` |
| `quintuples_weak.csv` | 39.682.832 | 1 baris = 1 tuple (96.417 baris) | `(review_id, clause)` |
| `label_maps.json` | 730 | taksonomi | — |
| `stage1_{train,val,test}.jsonl` / `stage2_{train,val,test}.jsonl` | 1,8–16,9 MB | split `review_id` | `review_id` |

## 2. Matriks kolom yang ditanya

| Kolom diminta | `reviews_clean.csv` | `reviews_labeled.csv` | `quintuples_weak.csv` |
|---|---|---|---|
| komentar asli (`review_text`) | ✅ | ✅ | ❌ (hanya `clause` + `text_norm`; join via `review_id`) |
| cleaned (`text_clean` / `text_norm`) | ✅ `text_clean`, `text_norm` | ✅ `text_clean`, `text_norm` | ✅ `text_norm` + `clause` |
| ASPECT (`aspect`) | ❌ | ❌ | ✅ |
| Category (`category`) | ❌ | ✅ agregat `categories` (`A\|B`) | ✅ per-tuple |
| Opinion (`opinion`, `[NULL]` bila implisit) | ❌ | ❌ | ✅ |
| Sentiment | ❌ (`polarity_rating` level ulasan) | ✅ `sentiment_major` + `polarity_rating` | ✅ per-tuple (`positive/neutral/negative`) |
| Emotion | ❌ | ✅ `emotion_major` | ✅ per-tuple (`joy/trust/anger/sadness/fear/disgust/neutral`) |
| Pasangan `AC/AO/AS/AE` | ❌ | ❌ | ❌ tidak ada |

Header aktual:

| File | Header |
|---|---|
| `reviews_clean.csv` | `review_id,app_name,app_slug,platform,store_id,rating,polarity_rating,review_text,text_clean,text_norm,n_words,emoji_count,helpful,review_date,review_year,app_version` |
| `reviews_labeled.csv` | `...sama + n_quintuple,categories,sentiment_major,emotion_major,evidence_mean` |
| `quintuples_weak.csv` | `review_id,app_name,app_slug,platform,rating,review_year,aspect,category,opinion,sentiment,emotion,aspect_implicit,pairing,lex_score,evidence,margin,clause,text_norm` |

## 3. Isi `pairing` (`quintuples_weak.csv`, N=96.417, hitungan penuh via `csv.DictReader`)

| `pairing` | N | % |
|---|---:|---:|
| `aspek_implisit` | 29.927 | 31,0 |
| `tanpa_opini` | 28.389 | 29,4 |
| `langsung` | 28.175 | 29,2 |
| `tak_langsung` | 9.926 | 10,3 |

Grepping `AC/AO/AS/AE` di `processed/` hanya mengenai kode error `AE-1200` di teks ulasan (1 baris contoh SeaBank), bukan kolom pasangan.

## 4. Contoh satu tuple

| Kolom | Nilai |
|---|---|
| `review_id` | `011deacb-…` / Bank Jago / 5 |
| `clause` | `bagaimana cara login nya` |
| `text_norm` | `bagaimana cara login nya` |
| `aspect` / `category` / `opinion` / `sentiment` / `emotion` | `login` / `AUTH_ACCESS` / `[NULL]` / `positive` / `joy` |
| `pairing` | `tanpa_opini` |

Contoh agregat ulasan (`reviews_labeled.csv`): `011deacb-…`: `n_quintuple=1.0`, `categories=AUTH_ACCESS`, `sentiment_major=positive`, `emotion_major=joy`.

## 5. Kesimpulan

- Tidak ada satu tabel `komentar asli | cleaned | ASPECT | Category | Opinion | Sentiment | Emotion | AC/AO/AS/AE`.
- Terdekat: `quintuples_weak.csv` + join `review_id` ke `reviews_clean.csv` untuk `review_text/text_clean`.
- Kode pasangan yang ada adalah 4 nilai `pairing` di atas, bukan `AC/AO/AS/AE`.

## Metode verifikasi

- `Get-ChildItem data/Apps-ACOS/processed` untuk ukuran file.
- Baris pertama tiap CSV untuk header; 2 baris sampel `quintuples_weak.csv` + 1 baris `reviews_labeled.csv`.
- Hitungan penuh `pairing` dengan `csv.DictReader` (96.417 baris).
- `label_maps.json`: 13 `categories`, 3 `sentiments`, 7 `emotions`, `null_term=[NULL]`.
