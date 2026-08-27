# Analisis & Solusi Error `KeyError: 'a--1,-1'` pada `00*.ipynb`

Tanggal: 2026-08-27 15:54
Fokus: error `KeyError: 'a--1,-1'` di cell 14 notebook `00_ACOS_Master_Pipeline_Colab.ipynb`
Metode: penelusuran alur data + simulasi parsing lokal (mock tokenizer). Tidak ada
eksekusi pipeline Colab (environment tanpa `torch`).

---

## 1. Bukti error (dari output tersimpan notebook 00)

Notebook 00 dieksekusi di Colab (GPU A100). Step 1 & pair-generation sukses,
lalu **cell 14 (Step 2) crash**:

```
/content/ACOS/Extract-Classify-ACOS/run_classifier_dataset_utils.py
    in convert_examples_to_features2nd
    444     aspect_input_ids = tokenizer.convert_tokens_to_ids(aspect_tokens)
tokenization.py in convert_tokens_to_ids
    127     ids.append(self.vocab[token])
KeyError: 'a--1,-1'
```

Stack: `cell 14 → features_step2 → convert_examples_to_features2nd →
tokenizer.convert_tokens_to_ids` gagal karena satu elemen `aspect_tokens` adalah
string `'a--1,-1'`, yang bukan token BERT mana pun.

`aspect_tokens` dibangun di `convert_examples_to_features2nd` (baris 437-441):

```python
aspect_tokens = ["[CLS]"]
for i, token in enumerate(bert_tokens_a):   # bert_tokens_a = orig_tokens (text kiri '####')
    aspect_tokens.append(token)
aspect_tokens.append("[CLS]")
```

dan `orig_tokens` diambil dari bagian **kiri** dari `####` di baris `_test_pair_1st.tsv`:

```python
orig_tokens, ao_tags = example.text_a.strip().split('####')   # baris 420
orig_tokens = orig_tokens.split()
```

Jadi `text_a` (baris `_test_pair_1st.tsv`) memuat string `a--1,-1` di **sebelah
kiri** `####`. Artinya tag implicit-aspect bocor ke dalam kolom teks.

---

## 2. Alur data yang bermasalah

```
pred_eval (eval_metrics.py:134)            menulis pred4pipeline.txt
        │   format: "<tokens> \t a-3,5 \t o-2,3 \t a--1,-1 \t o--1,-1"
        ▼
cell 12 notebook 00                        membaca & mem-parsing manual
        │   parts = line.strip().split('\t'); text = parts[0]
        │   for ele in parts[1:]:
        │       if ele.startswith('a'): asp.append(ele[2:])   # 'a--1,-1' -> '-1,-1'
        │       else:                    opi.append(ele[2:])
        │   wf.write(f"{text}####{pa} {po}\n")
        ▼
rest16_test_pair_1st.tsv                   (kolom tunggal: "text####aspan ospan")
        ▼
convert_examples_to_features2nd            split('####') -> orig_tokens = text (kiri)
        │   tokenizer.convert_tokens_to_ids(aspect_tokens)   # CRASH di sini
```

`a--1,-1` adalah format **tag implicit** yang diproduksi `pred_eval`
(eval_metrics.py:117-123):

```python
pred_tag.append('a-'+str(ele.start()-1) + ',' + str(ele.end()-1))  # explicit: a-3,5
if pred_imp_aspect[i] == 1:
    pred_tag.append('a--1,-1')                                    # implicit
```

Catatan: `a--1,-1` = prefix `a-` (2 karakter) + koordinat `-1,-1`. Jadi
`ele[2:]` memang benar menghasilkan `-1,-1`. Parsing `ele[2:]` bukan sumber
bug — yang salah adalah **pemisahan teks dari tag**.

---

## 3. Akar penyebab (terbukti via simulasi)

`get_1st_pairs.py` (sudah ada di repo) menggunakan logika parsing **persis sama**
dengan cell 12 (`ele.startswith('a')` → `ele[2:]`), jadi cell 12 bukan unik
bermasalah. Yang salah adalah **pemisah antara teks dan tag di `pred4pipeline.txt`**.

Simulasi lokal (mock tokenizer, vocab lengkap dari file upstream):

| Skenario | Input `pred4pipeline.txt` | Hasil parse cell 12 | `convert…` |
|---|---|---|---|
| A. Format benar (ada `\t`) | `yu ##m !\ta--1,-1\to--1,-1` | `yu ##m !####-1,-1 -1,-1` | **0 error** |
| C. **TRIGGER** (tanpa `\t`) | `yu ##m ! a--1,-1 o--1,-1` | `yu ##m ! a--1,-1 o--1,-1####-1,-1 -1,-1` | **`KeyError: 'a--1,-1'`** |

Test A: dengan pemisah `\t` yang benar, parsing menghasilkan file bersih → tidak
error. Test C: **saat `pred4pipeline.txt` tidak dipisah `\t` antara teks dan tag
pertama**, `line.strip().split('\t')` mengembalikan seluruh baris sebagai
`parts[0]`; `parts[1:]` kosong; maka `text` = seluruh baris (termasuk tag
`a--1,-1 o--1,-1`) → ditulis ke kiri `####` → saat di-tokenize keluar
`KeyError: 'a--1,-1'` **persis seperti di Colab**.

Kesimpulan: error terjadi karena **tag implicit `a--1,-1` bocor ke kolom teks**
akibat kegagalan pemisahan teks/tag. Ini reproducible persis dengan skenario
"tanpa pemisah `\t`". Penyebab tingkat-akar di sesi Colab: file `pred4pipeline.txt`
yang dibaca cell 12 tidak memiliki tab pemisah antara teks dan tag pertama
(kemungkinan besar versi/penulisan `pred4pipeline.txt` di sesi tersebut berbeda
dari yang ada di repo saat ini, yang memang menulis `\t`).

Poin kritis: **parsing manual cell 12 rapuh** — ia mengasumsikan struktur
`pred4pipeline.txt` persis benar. Begitu ada penyimpangan pemisah, tag bocor ke
teks dan crash terjadi jauh di hilir (step 2), sulit dilacak.

---

## 4. Solusi

### 4.1 Pendekatan: parser tahan-banting berbasis regex (separator-agnostik)

Ganti parsing manual cell 12 dengan parser yang:
- Memecah baris pada **sebarang whitespace** (tab maupun spasi) → tahan terhadap
  hilangnya `\t`.
- Mengenali tag dengan regex `^(a|o)-(-?\d+,-?\d+)$` → tag **pasti** dipisahkan
  dari teks, sehingga tidak mungkin bocor ke kolom teks.
- Menjaga kata biasa yang kebetulan diawali `a`/`o` tetap di teks (karena butuh
  koordinat `-?\d+,-?\d+` agar dianggap tag).

Regex `^(a|o)-(-?\d+,-?\d+)$`:
- `a-3,5`     → prefix `a-`, coord `3,5`
- `a--1,-1`   → prefix `a-`, coord `-1,-1`  (implicit)
- `o-2,3`     → prefix `o-`, coord `2,3`
- `o--1,-1`   → prefix `o-`, coord `-1,-1`  (implicit)

### 4.2 Kode pengganti untuk cell 12 (notebook 00)

```python
import re, codecs as cs

TAG_RE = re.compile(r'^(a|o)-(-?\d+,-?\d+)$')   # prefix a-/o- + coord

pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")
target_tokenized_tsv = os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")

with cs.open(pred_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

pair_records = []
with cs.open(target_tokenized_tsv, 'w', encoding='utf-8') as wf:
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # Pemisahan separator-agnostik: split di whitespace apa pun,
        # lalu klasifikasikan tiap token sebagai tag (a-/o-) atau teks.
        asp, opi, text_parts = [], [], []
        for tok in line.split():
            m = TAG_RE.match(tok)
            if m:
                coord = m.group(2)                 # = ele[2:]
                (asp if m.group(1) == 'a' else opi).append(coord)
            else:
                text_parts.append(tok)
        if not asp:
            asp.append('-1,-1')
        if not opi:
            opi.append('-1,-1')
        text = ' '.join(text_parts)               # teks bersih, tanpa tag
        for pa in asp:
            for po in opi:
                wf.write(f"{text}####{pa} {po}\n")
                pair_records.append({"Text": text, "Aspect_Span": pa, "Opinion_Span": po})

# (kelanjutan: DataFrame, ekspor CSV, plot — sama seperti cell 12 asli)
```

Keunggulan: skenario "tanpa `\t`" (trigger Colab) **sembuh sendiri** — tag tetap
terdeteksi dan dipisahkan dari teks.

### 4.3 Harden juga `get_1st_pairs.py` (sumber kebenaran)

`get_1st_pairs.py` punya kerapuhan sama. Ganti blok parsing (baris 33-61) dengan
logika `TAG_RE` di atas agar konsisten dan tahan banting. Cell 12 idealnya cukup
memanggil `get_1st_pairs.py` (single source of truth) alih-alih menduplikasi
logika.

### 4.4 Pertahanan dalam (defense-in-depth, opsional)

Agar crash serupa tidak lagi muncul di hilir, tambahkan guard di
`pair_examples_from_file` / `_create_examples` (CategorySentiProcessor) untuk
melewati baris `_test_pair_1st.tsv` yang kolom kirinya masih mengandung token
berpola tag (`a-/o-` + koordinat) sebelum diteruskan ke tokenizer. Ini mencegah
satu baris rusak menggagalkan seluruh step 2.

---

## 5. Verifikasi simulasi (lokal)

Parser regex diuji terhadap vocab lengkap (semua token wordpiece file upstream):

| Kasus | Input | Output `####` | `convert…` |
|---|---|---|---|
| `\t` benar | `yu ##m !\ta--1,-1\to--1,-1` | `yu ##m !####-1,-1 -1,-1` | OK |
| tanpa `\t` (trigger) | `yu ##m ! a--1,-1 o--1,-1` | `yu ##m !####-1,-1 -1,-1` | OK (sembuh) |
| explicit | `…\ta-3,5\to-2,3` | `…####3,5 2,3` | OK |
| kata `a` biasa | `a restaurant a-3,5 o-2,3` | `a restaurant####3,5 2,3` | OK (`a` tetap teks) |
| koord 2 digit | `…\ta-0,10\to-9,12` | `…####0,10 9,12` | OK |
| roundtrip penuh (1346 baris upstream) | — | — | **0 KeyError** |

Semua skenario lolos; bug `a--1,-1` tidak lagi muncul.

---

## 6. Rekomendasi

1. Terapkan parser regex (4.2) ke cell 12; hindari duplikasi dengan memanggil
   `get_1st_pairs.py` (4.3).
2. Tambahkan guard defensif di `_create_examples` (4.4) agar baris rusak dilewati,
   bukan menggagalkan step 2.
3. Setelah perbaikan, **jalankan ulang notebook 00 hingga selesai** (cell 16/18/20
   belum pernah dieksekusi karena crash ini) sebelum mengklaim pipeline end-to-end
   berhasil.
4. Catat di `requirements.txt` / sel otorisasi bahwa `pred4pipeline.txt` harus
   dipisah `\t`; parser regex di atas membuatnya tidak kritis, tapi baiknya
   tetap konsisten.

## 7. Batas verifikasi

- Tidak ada eksekusi Colab ulang (environment tanpa `torch`). Bukti error berasal
  dari output tersimpan notebook 00.
- Penyebab tingkat-akar pasti (tag bocor ke teks akibat gagalnya pemisahan
  teks/tag) **terbukti reproducible** via simulasi (skenario C). File
  `pred4pipeline.txt` asli dari sesi Colab tidak tersedia di repo, sehingga
  varian pasti pemisahnya tidak bisa dibaca langsung — namun solusi di atas
  menangani semua varian pemisah.
