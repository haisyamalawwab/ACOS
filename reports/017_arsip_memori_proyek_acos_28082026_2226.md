# Arsip Memori Proyek ACOS: 17 Catatan Persisten dalam Bentuk Markdown

**Nomor Dokumen:** `reports/017_arsip_memori_proyek_acos_28082026_2226.md`
**Tanggal:** 2026-08-28 22:26 WIB
**Sumber:** memori persisten agen di `~/.zcode/cli/memories/projects/acos-asli-476304a252c7886b/memory/`
**Isi:** 17 berkas memori (1 indeks + 16 catatan), diarsipkan apa adanya ke dalam repositori

---

## 1. Tujuan Dokumen

Memori agen tersimpan di luar repositori, di direktori profil pengguna. Akibatnya
catatan itu tidak ikut dalam `git`, tidak terlihat oleh kolaborator, dan hilang
bila profil dibersihkan. Dokumen ini menyalin seluruh isinya ke dalam `reports/`
supaya menjadi bagian dari riwayat proyek yang bisa dilacak.

Perlu dicatat perbedaan sifat dokumen ini dengan laporan lain di `reports/`:

- Laporan `001`–`016` adalah **analisis dan rencana** — beberapa klaimnya belum
  pernah diverifikasi (lihat §4.7).
- Dokumen ini adalah **arsip temuan yang sudah diverifikasi terhadap berkas
  atau eksekusi nyata**, plus dua aturan kerja dari pengguna. Setiap catatan
  menyebutkan cara verifikasinya.

Empat kategori memori: `user` (siapa penggunanya), `feedback` (arahan cara
kerja), `project` (pekerjaan berjalan dan kendalanya), `reference` (penunjuk ke
sumber luar).

---

## 2. Indeks Memori

| # | Catatan | Jenis | Inti |
|---|---|---|---|
| 1 | Larangan kontribusi ke NUSTM | feedback | jangan pernah PR ke NUSTM/ACOS |
| 2 | Topologi jaringan fork ACOS | project | checkout lokal adalah parent, bukan fork |
| 3 | Pola fast-forward untuk PR fork kosong | project | PR "No conflicts" tanpa tombol merge |
| 4 | PRD migrasi IndoBERT | project | checkpoint, taksonomi, dua kegagalan senyap |
| 5 | Rencana arsitektur alternatif | project | CNN/LSTM/XLM-R ditunda, bukan ditolak |
| 6 | Dependensi ML hanya di Colab | project | mesin lokal tanpa torch |
| 7 | Laporan rencana belum terverifikasi | project | `reports/` = ekspektasi, bukan ukuran |
| 8 | Keputusan desain quintuple ACOSE | project | label head terfaktor, kelas netral |
| 9 | Cacat data & metrik upstream | project | span nol-lebar, dua bug eval_metrics |
| 10 | Sitasi absa5 diverifikasi Crossref | reference | tiga karya tanpa DOI, empat DOI rawan |
| 11 | Artefak ganda notebook PRO | project | PRO_Resume kembar sampai Step 1 dipecah |
| 12 | Tiga salinan colab_utils | project | salinan root kurang 10 dari 16 simbol |
| 13 | Akar KeyError Step 2 | project | penyebabnya eval_gold, bukan parser tab |
| 14 | Caching PRO butuh session root | project | cek cache mati karena folder selalu baru |
| 15 | Jebakan idempotensi skrip patch | feedback | periksa string baru sebelum yang lama |
| 16 | Notebook V2 adalah keluaran generator | project | edit generator, bukan `.ipynb` |

---

## 3. Aturan Kerja dari Pengguna (jenis `feedback`)

### 3.1 Larangan Kontribusi ke NUSTM Upstream

**Berkas memori:** `no-contributions-to-nustm-upstream.md`

Jangan pernah membuka pull request atau berkontribusi ke `NUSTM/ACOS`. Pengguna
menyatakan ini eksplisit pada 2026-08-28: pekerjaan berhenti di
`haisyamalawwab/ACOS`, meskipun NUSTM tetap menjadi akar jaringan fork.

**Mengapa:** `haisyamalawwab/ACOS` sendiri adalah fork yang `parent` dan
`source`-nya sama-sama `NUSTM/ACOS` (203 bintang, terakhir di-push 2022-10-20,
nol PR sepanjang sejarahnya). Karena metadata itu, GitHub mengarahkan beberapa
aksi secara default ke NUSTM, sehingga satu klik salah atau `gh pr create` tanpa
argumen akan mengirim riset privat pengguna ke upstream akademik publik.

**Cara menerapkan:** selalu berikan `--repo haisyamalawwab/ACOS` secara eksplisit
pada `gh pr create`. `gh repo set-default haisyamalawwab/ACOS` sudah dijalankan di
`D:\laragon\www\ACOS-ASLI` pada 2026-08-28 sebagai pengaman. Dua jalur sisa tidak
bisa ditutup oleh konfigurasi dan harus dihindari manual: tombol **"Contribute"**
di antarmuka web, dan banner "This branch is N commits ahead of NUSTM:main" di
halaman repositori. Hubungan fork itu sendiri tidak mengirim apa pun, jadi tidak
perlu meminta GitHub Support memutusnya.

### 3.2 Jebakan Idempotensi Skrip Patch Notebook

**Berkas memori:** `pro-patch-scripts-idempotency-trap.md`

`notebooks/_fix_pro_bugs.py` dan `notebooks/_apply_pro_caching.py` menyunting
notebook PRO dengan penggantian string persis. Fungsi `replace_once()`-nya semula
menguji `if old not in text` lebih dulu, baru memeriksa apakah `new` sudah ada.
Beberapa hunk adalah penyisipan murni yang nilai `new`-nya memuat `old` sebagai
awalan (misalnya menambahkan `import re` setelah `import codecs as cs`), sehingga
`old` tetap ada setelah patch berhasil dan eksekusi kedua menambahkan baris yang
sama lagi. Menjalankan ulang skrip diam-diam menghasilkan import ganda.

**Mengapa:** skrip inilah satu-satunya cara notebook disunting, dan skrip
diputar ulang setiap kali notebook dibangun kembali dari HEAD, jadi
non-idempotensi merusak artefak, bukan cuma membuang satu eksekusi.

**Cara menerapkan:** di `replace_once()`, periksa `if new in text: return`
sebelum memeriksa `old`. Saat menambah hunk, pilih anchor yang dikonsumsi oleh
penggantinya; bila hunk berupa penyisipan murni, verifikasi idempotensi dengan
menjalankan skrip dua kali lalu `grep` baris yang disisipkan dan pastikan
jumlahnya 1. Validasi notebook sebaiknya mem-parse setiap sel kode dengan
`ast.parse` **setelah** mengganti baris yang dimulai `!` atau `%` dengan `pass` —
`ast.parse` mentah melaporkan "unexpected indent" palsu pada shell magic Colab.

---

## 4. Konteks Proyek (jenis `project`)

### 4.1 Topologi Jaringan Fork ACOS

**Berkas memori:** `acos-fork-network-topology.md`

Direktori kerja `D:\laragon\www\ACOS-ASLI` adalah repositori **parent**, bukan
fork. `origin`-nya `https://github.com/haisyamalawwab/ACOS`. Rantai fork:
`rozanhaisyam/ACOS` → parent `haisyamalawwab/ACOS` → akar `NUSTM/ACOS`; fork
ketiga `zoom2uwg/ACOS` juga mengirim PR ke parent.

**Mengapa:** dokumen serah-terima (`CARA_MENYELESAIKAN_MERGE_ACOS.md`)
menggambarkan checkout ini sebagai fork dan meresepkan "sync fork, lalu
`git push origin main`" — itu salah dan tidak bisa dijalankan di sini. Akun
terautentikasi `haisyamalawwab` punya admin penuh di parent, tetapi hanya
`pull: true, push: false` di `rozanhaisyam/ACOS`, jadi tidak ada yang bisa
di-push ke fork itu dari mesin ini.

**Cara menerapkan:** selesaikan merge lintas-fork dengan me-merge *ke dalam*
parent dari checkout ini, jangan pernah dengan push ke fork. Untuk mengambil
pekerjaan fork, tambahkan remote baca-saja
(`git remote add fork https://github.com/rozanhaisyam/ACOS.git`) lalu fetch. Bila
sebuah fork perlu menyusul, pemilik fork harus menekan tombol "Sync fork" di
GitHub sendiri.

Remote yang kini terkonfigurasi: `origin` (parent), `fork` (rozanhaisyam),
`zoom` (zoom2uwg). Serah-terima "Sync fork" terbukti berjalan — setelah PR #7
kedua fork diminta sync dan keempat repositori memegang pohon identik, jadi
meminta pemiliknya adalah jalur penyelesaian nyata, bukan jalan buntu.

### 4.2 Pola Fast-Forward untuk PR Fork Kosong

**Berkas memori:** `empty-fork-pr-ff-merge-pattern.md`

PR fork terhadap `haisyamalawwab/ACOS` berulang kali datang dengan
`changed_files: 0` dan hash pohon identik dengan `main`. GitHub menyembunyikan
tombol merge untuk PR seperti itu, sehingga antarmuka web hanya menampilkan "No
conflicts with base branch" dan pengguna terjebak. Ini terjadi pada PR #5 (dari
`rozanhaisyam`) dan PR #6 (dari `zoom2uwg`), keduanya pada 2026-08-28.

**Mengapa:** PR itu tidak membawa apa pun selain commit merge yang tercipta saat
pemilik fork me-merge parent kembali ke fork-nya. Kontennya sudah ada di `main`,
jadi memang tidak ada yang perlu di-merge — hanya riwayat yang perlu dimajukan.
Pemeriksaan mergeability GitHub juga lebih lemah dalam deteksi rename ketimbang
Git lokal: PR #4 dilaporkan `mergeable: false, dirty` pada tiga kali polling API,
padahal `git merge --no-commit --no-ff` lokal melaporkan "Automatic merge went
well" tanpa satu pun penanda konflik, karena Git mencocokkan notebook yang
di-rename.

**Cara menerapkan:** verifikasi kekosongan lebih dulu dengan
`gh api repos/haisyamalawwab/ACOS/pulls/N --jq '{changed_files,mergeable_state}'`
dan bandingkan hash pohon (`git rev-parse main^{tree} <head>^{tree}`). Bila
identik dan head adalah keturunan, selesaikan secara lokal:
`git fetch <remote> && git merge --ff-only <sha> && git push origin main`. GitHub
menandai PR **merged** otomatis dalam hitungan detik setelah push. Konfirmasi
hash pohon tidak berubah sesudahnya sebagai bukti tidak ada konten yang bergeser.
Jangan percaya verdict `dirty` dari GitHub tanpa mereproduksi merge secara lokal.

**PR tidak kosong: head bisa bergerak saat Anda me-merge.** PR #7 dari
`zoom2uwg` (merged 2026-08-28) **tidak** kosong — 4.198 penyisipan di notebook,
docs, dan reports. Me-merge lokal lalu push *tidak* membuatnya berstatus merged,
karena pemilik fork sementara itu me-merge `main` parent ke fork-nya dua kali,
memajukan head PR melewati SHA yang sudah saya cakup. GitHub hanya menandai PR
merged begitu `head.sha` **terkini**-nya bisa dicapai dari base yang di-push.

Jadi untuk setiap penyelesaian merge lokal, jalankan ulang `git fetch <remote>`
dan bandingkan dengan
`gh api repos/haisyamalawwab/ACOS/pulls/N --jq .head.sha` persis sebelum
me-merge; bila head maju, merge lagi untuk mencakup commit baru.
`merged: false, state: open` tepat setelah push berhasil berarti head bergerak,
bukan push gagal.

Dua langkah telaah yang layak dipertahankan untuk PR fork tidak kosong, keduanya
mengubah tingkat keyakinan saya pada #7:

- Commit berjudul "remove deprecated and unused utility files" menghapus 8
  berkas / 4.073 baris. Memeriksa masing-masing dengan
  `git cat-file -e main:<path>` menunjukkan **tidak satu pun pernah ada di
  `main`**, jadi merge tidak kehilangan apa pun. Jangan menilai commit
  penghapusan dari diffstat-nya terhadap fork.
- `git diff --name-only main <remote>/main | grep -E '^(absa5|data|configs|Extract)'`
  memastikan PR tidak menyentuh direktori kode atau data — itulah yang membuat
  merge aman diambil tanpa telaah baris per baris.

**Menutup lingkaran: verifikasi seluruh jaringan lewat hash pohon.** Setelah
pemilik fork memakai tombol "Sync fork", periksa keadaan jaringan dengan hash
pohon, bukan hitungan ahead/behind:

```bash
for r in main origin/main fork/main zoom/main; do
  printf "%-14s %s  %s\n" "$r" "$(git rev-parse $r^{tree})" "$(git rev-parse --short $r)"
done
```

Pohon identik di keempatnya membuktikan konten cocok; `git rev-list
--left-right --count` sendirian tidak, karena ia melaporkan `0 0` pada kasus di
mana head PR sebenarnya sudah bergerak (persis seperti tampilan penyelesaian #7
di tengah merge). Setelah #7 keempatnya duduk di commit sama dengan pohon sama.

### 4.3 PRD Migrasi IndoBERT & Keputusan yang Dikunci

**Berkas memori:** `indobert-migration-prd-and-decisions.md`

Migrasi IndoBERT dispesifikasikan di
`docs/0004_prd_implementasi_indobert_acos_28082026_0638.md` (ditulis 2026-08-28,
kini 594 baris, 13 bagian). Dokumen itu menggantikan sebagian `reports/008`,
`009`, `010_konsep`, `010_survey`, dan `011`. Keputusan yang dikuncinya, yang di
laporan-laporan tersebut masih kondisional:

- Checkpoint utama `indobenchmark/indobert-base-p1`, dipakai sebagai **encoder
  pre-trained yang kita fine-tune sendiri**; checkpoint Indonesia pihak ketiga
  yang sudah di-fine-tune ditolak. Terverifikasi sebagai encoder telanjang:
  `state_dict`-nya nol kunci `cls.*` (head MLM) berbanding 14 pada
  `bert-base-uncased`, cocok dengan `"architectures": ["BertModel"]`.
- `LazarusNLP/NusaBERT-base` hanya komparator A/B fase dua (ia mengirim
  `model.safetensors` tanpa `pytorch_model.bin`, sehingga jalur `torch.load`
  lama tidak bisa membacanya). `indobert-large-p1` ditunda;
  `w11wo/indonesian-roberta-base` ditolak.
- Taksonomi Indonesia dipatok **13 kategori** yang dipetakan satu-satu dari
  rest16, mempertahankan `num_labels = 39` di Step 2 agar dimensi head tidak
  berubah dan hasilnya tetap sebanding dengan baseline Inggris.
- Lima deliverable baru (adapter checkpoint, modul taksonomi, generator
  `tokenized_data`, skrip verifikasi, notebook Colab) plus tiga gate wajib;
  perubahan kode upstream dijaga minimal agar pipeline Inggris tetap jalan
  sebagai kontrol.
- Fase F0–F3 sudah bisa dieksekusi sekarang terhadap data Inggris yang ada;
  hanya F4 ke atas yang menunggu dataset quadruple Indonesia (yang belum ada).
  Tidak ada target angka F1 yang ditetapkan, dan itu disengaja — belum ada
  dataset Indonesia, jadi angka apa pun cuma terkaan.
- §13 **menunda**, bukan menolak, arsitektur deep learning lain (CNN, LSTM,
  BiLSTM, XLM-RoBERTa, IndoRoBERTa), lengkap dengan urutan yang disarankan dan
  set publikasi minimal IndoBERT + XLM-R + BiLSTM-CRF (lihat §4.4).

**Mengapa:** dua penghambat yang ditemukan lewat verifikasi langsung akan
membuat migrasi naif gagal secara senyap, dan keduanya mendorong seluruh desain.

Pertama, `indobenchmark/indobert-base-p1` menyimpan 414 kunci `state_dict`-nya
**tanpa** awalan `bert.` yang dipakai `bert-base-uncased`, sementara loader lama
di `Extract-Classify-ACOS/modeling.py:745` hanya menambahkan awalan itu bila
model tidak punya atribut `bert` — yang justru dimiliki `BertForQuadABSA`
(`modeling.py:1535`). Setiap bobot encoder mendarat di `missing_keys`, dan
logging yang seharusnya melaporkannya dikomentari di `modeling.py:750-755`,
sehingga training berjalan bersih dengan encoder terinisialisasi acak.

Kedua, tidak ada generator `tokenized_data/*_quad_bert.tsv` di repositori,
sehingga "regenerasi tokenized_data" adalah deliverable baru, bukan pengulangan;
offset di sana adalah indeks token spasi atas teks yang **sudah** ter-WordPiece
(`yum !` → `yu ##m !`, span `0,1` → `0,2`).

**Cara menerapkan:** perlakukan gate 1 (perbandingan numerik bobot yang termuat
terhadap checkpoint mentah) dan gate 2 (jalankan generator baru dengan vocab
Inggris lalu diff terhadap `tokenized_data` yang sudah ada di repositori) sebagai
tidak bisa ditawar, karena kedua mode kegagalan itu senyap dan hanya muncul
sebagai penurunan metrik tanpa penjelasan. Generator (deliverable D3) menerima
tokenizer sebagai parameter alih-alih mengeraskan IndoBERT, supaya komparator
keluarga RoBERTa nanti tidak memaksa penulisan ulang.

Catat juga `config.vocab_size` untuk base-p1 menyebut 50000 sementara `vocab.txt`
memuat 30521 token — matriks embedding yang kebesaran itu nyata, jadi jangan
pernah pakai `vocab_size` sebagai rujukan vocab. Saat menulis hasil, jaga
ketepatan istilah: "pre-trained" adalah titik awal, "fine-tuned" adalah yang
dihasilkan pipeline ini, dan karena Step 1 dan Step 2 masing-masing mulai dari
checkpoint dasar yang sama (tidak dirantai), satu eksekusi menghasilkan dua model
fine-tuned yang terpisah.

### 4.4 Rencana Arsitektur Alternatif

**Berkas memori:** `acos-alternative-architectures-plan.md`

Pengguna bertanya apakah proyek ACOS juga perlu menyiapkan CNN, LSTM, BiLSTM,
XLM-RoBERTa, dan IndoRoBERTa. Jawaban yang tercatat di §13 PRD IndoBERT adalah
**ya tetapi ditunda**, bukan ditolak, dengan urutan yang disarankan: IndoBERT-base
→ NusaBERT-base → XLM-RoBERTa-base → BiLSTM-CRF + FastText ID → IndoBERT-large →
IndoRoBERTa → CNN dan LSTM satu arah paling akhir sebagai ablasi saja. Untuk
tesis atau artikel, set minimal yang kuat adalah **IndoBERT + XLM-R +
BiLSTM-CRF**: satu model khusus Indonesia, satu multibahasa, satu pra-Transformer.

Kelima metode itu bukan jenis perubahan yang sama. CNN/LSTM/BiLSTM mengganti
encoder dan memerlukan jalur embedding baru (Word2Vec/FastText ID); XLM-RoBERTa
dan IndoRoBERTa hanya menukar checkpoint pre-trained, jadi jauh lebih murah.
XLM-R berperingkat tinggi karena penelaah bisa diprediksi akan bertanya "mengapa
tidak sekadar pakai model multibahasa?", dan tanpa angka itu klaim apa pun
tentang perlunya model khusus Indonesia tidak punya dukungan.

Dua temuan dari membaca `Extract-Classify-ACOS/modeling.py` yang mengubah
estimasi biaya: untuk keluarga RoBERTa penghambat sebenarnya adalah
`token_type_ids`, bukan tokenizer — `aspect_segment_ids` diteruskan ke `forward`
sebagai `aspect_token_type_ids` (`modeling.py:1558`) dan harus dinetralkan. Untuk
BiLSTM/CNN ada perancah sebagian tetapi belum teruji: `class CNNLayer`
(`modeling.py:1174`) tidak pernah diinstansiasi di mana pun (kode upstream mati),
dan `self_attention_layer` (`:1129`) hanya diinstansiasi di dalam
`BertForSequenceClassification` (`:1263`), yang tidak terdaftar di `model_dict`.
Yang benar-benar bisa dipakai ulang lintas encoder adalah CRF
(`modeling.py:1541`, dari `torchcrf`, independen dari BERT) dan head implicit
aspect/opinion, yang hanya butuh vektor `hidden_size`.

**Mengapa:** menambah arsitektur sebelum IndoBERT menghasilkan satu angka yang
bisa dipercaya akan membuat setiap anomali ambigu antara remap span yang salah,
encoder yang senyap tidak termuat, dan arsitektur yang memang tidak cocok.
Perbandingan lintas arsitektur yang sah juga mengandaikan pembagian data yang
tetap, yang tidak mungkin sebelum dataset Indonesia ada.

**Cara menerapkan:** hanya satu hal yang langsung bisa dikerjakan dan sudah ada
di PRD: generator `tokenized_data` (D3) menerima tokenizer sebagai parameter,
karena XLM-R dan RoBERTa butuh data ter-tokenisasi sendiri sementara IndoBERT dan
NusaBERT bisa berbagi satu berkas (vocab identik byte per byte). Tulis analisis
mendalam per arsitektur sebagai PRD terpisah hanya setelah ketiga gate verifikasi
lulus, ketika kontrak encoder yang bekerja sudah diketahui alih-alih diterka.
Perbandingan juga harus memaku pembagian data, melaporkan seed dan jumlah
eksekusi, serta menyetarakan anggaran komputasi.

### 4.5 Dependensi ML Hanya Tersedia di Colab

**Berkas memori:** `acos-ml-deps-only-in-colab.md`

Lingkungan lokal untuk `D:\laragon\www\ACOS-ASLI` **tidak** punya `torch`,
`transformers`, `torchcrf`, `numpy`, maupun `sklearn` — Python 3.14.2 tanpa satu
pun tumpukan ML terpasang (diperiksa 2026-08-28). Tidak ada bagian pipeline ACOS
yang bisa dieksekusi atau diverifikasi secara numerik di mesin lokal.

**Mengapa:** ini membentuk cara kerja harus diserahkan: gate verifikasi, eksekusi
training, dan pemeriksaan apa pun yang butuh tensor nyata semuanya harus terjadi
di Google Colab — itulah alasan rencana migrasi menjadikan notebook sebagai jalur
eksekusi utama.

**Cara menerapkan:** jangan mencoba menjalankan atau mengimpor kode pipeline
secara lokal; pembacaan statis, pekerjaan `gh`/git, dan probe HTTP metadata
HuggingFace adalah yang bisa dilakukan mesin ini. Tulis modul `.py` baru supaya
bisa diimpor dari notebook **dan** dijalankan sebagai CLI, dengan logika di luar
sel notebook agar tetap bisa diuji.

### 4.6 Laporan Rencana di `reports/` Belum Terverifikasi

**Berkas memori:** `acos-plan-reports-are-unverified.md`

Dokumen rencana bernomor di bawah `reports/` (khususnya 008–011 tentang migrasi
IndoBERT/NusaBERT) mencampur rujukan kode terverifikasi dengan asumsi yang belum
diverifikasi, tanpa membedakan keduanya. Klaim nomor baris tentang berkas
`Extract-Classify-ACOS/` memang terbukti benar, tetapi beberapa klaim teknis
penyangga tidak lolos verifikasi pada Agustus 2026: premis "swap ringan akan
bekerja bila IndoBERT memakai penamaan bobot BERT standar" salah, "regenerasi
tokenized_data" mengandaikan generator yang tidak ada, dan laporan-laporan itu
tidak memuat ukuran vocab, hyperparameter, maupun target metrik meski dibaca
seperti rencana implementasi. Nomor urutnya pun berduplikat (dua `010`, plus
tabrakan di `007` dan `008`).

**Mengapa:** bertindak langsung atas dokumen itu akan menghasilkan migrasi yang
tampak berhasil padahal melatih encoder terinisialisasi acak. Laporan itu sendiri
mencatat bahwa angka performa adalah "ekspektasi analitis, bukan hasil ukur" —
peringatan itu berlaku lebih luas daripada tempat ia dituliskan.

**Cara menerapkan:** sebelum mengandalkan klaim apa pun dari `reports/`,
verifikasi terhadap kode atau artefak sebenarnya (config HuggingFace, kunci
checkpoint, berkas data). Utamakan PRD di `docs/` sebagai rencana otoritatif,
karena klaimnya sudah diperiksa.

### 4.7 Keputusan Desain Quintuple ACOSE

**Berkas memori:** `acose-quintuple-design-decisions.md`

Perluasan quintuple (aspect-category-opinion-sentiment-**emotion**) berada di
`absa5/`, ditambahkan 2026-08-28, dengan `Extract-Classify-ACOS/` upstream
dibiarkan utuh sebagai kontrol 4 elemen. Tiga keputusan yang tidak terlihat dari
kodenya:

**Label head terfaktor, bukan gabungan.** Upstream mengklasifikasi atas produk
silang kategori × sentimen (13 × 3 = 39 keluaran). Menambahkan 5 emosi
menjadikannya 195 keluaran atas ~2,4 ribu tuple training yang sama. Terukur pada
rest16: pada 4 elemen 87,2% sel gabungan terisi; pemecahan quint meninggalkan
sebagian besar sel kosong. Karena itu `heads.label_mode` berdefault `factored`
(13 + 3 + 5 = 21 keluaran, satu klasifier per elemen). `joint` tetap tersedia
untuk perbandingan 4 elemen.

**Emosi butuh kelas netral eksplisit.** Lima label EmoT dari IndoNLU
(sadness/anger/love/fear/happy) berasal dari tweet, yang terseleksi karena muatan
emosionalnya. Tuple ABSA tidak — "harganya wajar" bernilai positif tanpa muatan
emosi. Entri registry `emot_id_netral` menambahkan `netral`; `emot_id` biasa
dipertahankan untuk perbandingan. Tagger leksikon menolak set label yang tidak
memuat kelas yang dituju oleh fallback sentimennya.

**Risiko redundansi adalah risiko ilmiah yang sebenarnya, dan itu diukur.** Bila
setiap nilai sentimen memetakan tepat ke satu emosi, elemen kelima tidak
menambahkan informasi apa pun. `absa5.emotion.sentiment_redundancy` melaporkan
H(emotion | sentiment) dalam bit dan menyatakan verdict. Atas keluaran leksikon
itu sendiri pada rest16 Inggris, verdict-nya "penamaan ulang sentimen yang
deterministik" — itu adalah tagger yang gagal pada teks asing, tetapi pemeriksaan
yang sama harus dijalankan pada data beranotasi manusia sebelum elemen emosi
dianggap layak dilatih.

Tidak ada dataset terbitan yang punya kelima elemen ini. "Quintuple" dalam
literatur ABSA sudah berarti ACOSI (elemen ke-5 = penanda opini implisit,
Shoes-ACOSI, Findings of EMNLP 2024) atau COQE (opini komparatif).

### 4.8 Cacat Data & Metrik pada Rilis Upstream

**Berkas memori:** `upstream-acos-data-and-metric-defects.md`

Ditemukan lewat perbandingan langsung berkas yang dikirim, 2026-08-28. Ketiganya
ada di kode/data upstream, bukan di apa pun yang kita tulis.

**Span nol-lebar, `data/Restaurant-ACOS/rest16_quad_train.tsv` baris 451.** Span
opini tertulis `3,3`. Berkas turunan milik penulisnya sendiri saling bertentangan
soal perbaikannya: `tokenized_data/rest16_train_quad_bert.tsv` mencatat `3,4`,
`tokenized_data/rest16_train_pair.tsv` mencatat `3,5`, dan berkas pair itu juga
membuang salah satu dari tiga tuple kalimat tersebut. Tidak ada rekonstruksi yang
memenuhi keduanya, jadi `absa5.selftest.KNOWN_UPSTREAM_DEFECTS` mengecualikan
kalimat itu secara eksplisit dan menuntut kesetaraan persis untuk semua sisanya —
18.862 span di 6.359 baris memang cocok persis. Itu satu-satunya span degenerat
di keenam berkas data.

**`measureQuad` menghitung ganda duplikat**
(`Extract-Classify-ACOS/eval_metrics.py:32`). Pencocokannya memakai
`if pair in gold[text]`, sehingga prediksi yang terulang dua kali mencetak dua
true positive terhadap satu tuple gold. `absa5.metrics.multiset_prf` memakai
irisan multiset sebagai gantinya.

**`measureQuad_imp` membuang empat dari lima rincian**
(`eval_metrics.py:215-221`). Ia mencetak kelima bucket implicitness di dalam
loop tetapi hanya mengembalikan `p`/`r`/`f` iterasi terakhir, jadi pemanggil
hanya menerima satu bucket. Ini penting karena aspek dan opini implisit adalah
kasus yang sulit — sekitar 24% pair training rest16 punya aspek implisit, 18%
opini implisit. `absa5.metrics.EvalResult` menyimpan setiap bucket.

Relevan juga: offset di `tokenized_data/*.tsv` mengindeks token spasi dari teks
yang **sudah** dipecah WordPiece, dan generator yang menghasilkannya tidak pernah
dirilis.

### 4.9 Artefak Ganda Notebook PRO

**Berkas memori:** `pro-notebook-duplicate-artifacts.md`

Dua artefak duplikat masuk ke `main` lewat PR #7 zoom2uwg (merged 2026-08-28
sebagai `f6a48f0` dan `4b46803`). Keduanya ditandai di pesan commit merge tetapi
tidak diblokir, karena sifatnya duplikasi bukan kerusakan dan pekerjaannya milik
kolaborator.

- `notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb` dulu **identik byte
  per byte** dengan `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` (keduanya
  sha256 `89a7d3a4…`, 85.472 byte, 29 sel / 14 kode). **Tidak lagi berlaku sejak
  2026-08-28** (commit `deb57ad`): PRO_Resume kini 40 sel karena sel Step 1
  monolitiknya dipecah menjadi 5a-5f oleh `notebooks/_split_step1_cells.py`. PRO
  biasa masih memikul satu sel Step 1 sepanjang 236 baris, jadi kedua notebook
  kini berbeda — tetapi hanya di Step 1.
- `IMPLEMENTATION_PLAN_00_PRO_CACHING.md` di akar repositori identik byte per byte
  dengan `notebooks/IMPLEMENTATION_PLAN_00_PRO_CACHING.md` (sha256 `4d3da291…`).
  Masih terduplikasi.

**Mengapa:** notebook itu dihasilkan skrip generator
(`notebooks/_build_pro_resume.py`, dan `build_pro_notebooks.py` yang dihapus PR
yang sama). Penyebab paling mungkin adalah generator menulis keluaran yang sama
dua kali dengan dua nama, sehingga perilaku caching dan auto-recovery khas resume
yang dijelaskan di `reports/016_…` dan `IMPLEMENTATION_PLAN_00_PRO_CACHING.md`
mungkin sebenarnya tidak ada di keduanya.

**Cara menerapkan:** diff kedua notebook sebelum memperlakukan salah satunya
sebagai otoritatif; harapkan keduanya sepakat di semua tempat kecuali Step 1.
Jangan menjalankan ulang `notebooks/_build_pro_resume.py` terhadap PRO_Resume —
itu akan meregenerasi sel Step 1 monolitik dan diam-diam membuang pemecahan
5a-5f.

### 4.10 Tiga Salinan `colab_utils.py` yang Berbeda

**Berkas memori:** `colab-utils-three-divergent-copies.md`

`colab_utils.py` ada tiga kali dengan isi **berbeda**:
`notebooks/colab_utils.py` (lengkap, 16/16 simbol — yang kanonik),
`Extract-Classify-ACOS/colab_utils.py` (juga 16/16), dan `colab_utils.py` di akar
repositori yang **kehilangan 10 dari 16** simbol yang diimpor notebook master
pipeline: `df_to_markdown`, `export_step_table`, `MarkdownReport`,
`SubtaskMetricCapture`, `plot_subtask_metrics`, `features_step1`,
`features_step2`, `pair_examples_from_file`, `resolve_eval_pair_file`,
`unpack_model_output`.

**Mengapa:** salinan mana pun yang menang balapan `sys.path` menentukan apakah
notebook berjalan, dan hilangnya 10 simbol pada salinan akar membuat balapan itu
diam-diam menjadi penentu. Lebih buruk lagi, pengaman yang dipakai notebook
(`except ModuleNotFoundError`) tidak mungkin menyala untuk kasus ini: from-import
terhadap modul yang **ada tetapi kekurangan nama** memunculkan `ImportError`,
bukan `ModuleNotFoundError`. Jadi notebook mogok persis di sel yang fallback-nya
seharusnya mencegah hal itu. Diverifikasi dengan mereproduksi polanya, bukan
disimpulkan.

**Cara menerapkan:** periksa *nama* simbol, bukan keberhasilan import —
`ast.parse` berkasnya dan bandingkan dengan daftar yang dibutuhkan, yang juga
bekerja sebelum `pip install` karena tidak pernah mengeksekusi modulnya. Utamakan
`notebooks/` di `sys.path` dan perlakukan salinan akar sebagai tersangka.
`notebooks/acos_bootstrap.py` (ditambahkan 2026-08-28) melakukan ini di
`ensure_symbols()` / `import_colab_utils()` dan me-rename salinan tidak lengkap
menjadi `.incomplete` alih-alih menghapusnya; `ensure_project()`-nya juga
memperlakukan berkas nol-byte sebagai tidak ada, karena unduhan Drive yang
terputus meninggalkan berkas kosong yang lolos `os.path.exists` lalu gagal jauh
di dalam training.

### 4.11 Akar Penyebab KeyError Step 2 adalah `eval_gold`

**Berkas memori:** `step2-keyerror-root-cause-is-eval-gold.md`

Didiagnosis dan diperbaiki 2026-08-28 di
`notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` dan kembarannya
`_PRO_Resume.ipynb`.

`pred_eval` (`Extract-Classify-ACOS/eval_metrics.py:133`) menulis
`pred4pipeline.txt` sebagai `ids_to_token[text].split(' ')[1:tokens_len-1]`, di
mana `tokens_len` menghitung sekuens fitur yang terbungkus `[CLS]`. Karena itu
`run_step1.py:276` meneruskan `eval_aspect_input_ids` — terbungkus CLS dan
ter-zero-pad — sebagai `eval_gold[0]`. Notebook justru meneruskan
`tokenizer.convert_tokens_to_ids(line[0].split(" "))`, id mentah tanpa `[CLS]`.
Slice tersebut lalu membuang token pertama sesungguhnya dari setiap kalimat dan
menghasilkan teks **kosong** untuk kalimat satu kata (test rest16 punya tiga:
`splendid`, `excellent`, `delicious`), sehingga baris yang tertulis menjadi
`\ta--1,-1\to--1,-1`. `split('\t')[0]` atas baris itu mengembalikan tag itu
sendiri sebagai teks, yang sampai ke `convert_examples_to_features2nd` dan
memunculkan `KeyError: 'a--1,-1'`.

Konsekuensinya di luar crash: dengan teks yang bergeser satu token, **nol** dari
580 kunci teks candidate pair cocok dengan kunci gold yang dibangun
`read_pair_gold`, jadi Step 2 akan mencetak 0 bahkan tanpa exception.
Diverifikasi dengan Python murni terhadap berkas ter-tokenisasi yang dikirim:
583/583 kunci cocok setelah perbaikan.

Laporan di `reports/007_solusi_error_keyerror_step2_*.md` menyalahkan parser tab
di sel 12 dan meresepkan parser regex. Regex itu layak dipertahankan sebagai
pertahanan berlapis (kini ada di sel pembentukan pasangan) tetapi ia bukan akar
penyebabnya — regex itu diam-diam membuang tiga kalimat yang terdampak, bukan
memperbaikinya.

### 4.12 Caching PRO Memerlukan Session Root yang Bisa Dilanjutkan

**Berkas memori:** `pro-caching-resume-session-root.md`

Caching multi-tier di `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` mati
sebagaimana ditulis semula: setiap pemeriksaan cache di sel 8/12/20/22/24 menguji
path di bawah `session_dirs`, tetapi sel 6 memanggil
`setup_timestamped_run_dir()` tanpa syarat, yang mencetak folder
`results/<domain>_<DDMMYYYY_HMS>/` baru pada setiap eksekusi. Runtime baru karena
itu selalu mencari artefak ter-cache di direktori kosong dan selalu gagal. Satu-
satunya yang pernah kena adalah cabang `globals()`, yaitu menjalankan ulang sel di
kernel yang masih hidup.

Diperbaiki pada 2026-08-28 dengan menambahkan `find_resumable_session()` /
`session_cache_score()` / `session_dirs_from_root()` ke sel 6, digerbangi
`RESUME_LAST_SESSION = True`. Pemilihan sesi memeringkat direktori kandidat
berdasarkan jumlah enam artefak kunci (pipeline_state.pkl, CSV statistik EDA,
pred4pipeline.txt, kedua checkpoint step, master_metrics.json), dengan pemecah
seri berupa mtime — yang **paling lengkap** menang, bukan yang paling baru, karena
eksekusi yang gagal di awal menciptakan folder yang lebih baru tetapi lebih
kosong. Direktori disaring dengan awalan `domain + "_"` supaya eksekusi rest16
tidak pernah mengadopsi sesi laptop.

**Mengapa:** memeringkat dengan mtime saja memunculkan kembali bug itu setiap
kali sebuah eksekusi mati lebih awal; menilai dengan skor artefak-lah yang membuat
resume berguna.

**Cara menerapkan:** setiap tahap baru yang menulis artefak yang bisa dilanjutkan
harus menambahkan penandanya ke `session_cache_score`, kalau tidak sesi yang hanya
memuat artefak itu berskor 0 dan terlewat. Set `RESUME_LAST_SESSION = False` untuk
eksekusi benchmark yang bersih.

### 4.13 Notebook V2 Bertahap adalah Keluaran Generator

**Berkas memori:** `staged-v2-notebook-is-generated.md`

`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb` (dibuat 2026-08-28,
56 sel / 28 kode) **dihasilkan** oleh `notebooks/_build_staged_v2.py` dari
`00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`. Generator menulis ulang berkas
tujuan dari nol pada setiap eksekusi dan menghasilkan berkas identik byte per
byte, sehingga suntingan tangan pada `.ipynb` hilang diam-diam pada build
berikutnya. Sunting konstanta string `CODE_*` / `MD_*` di generator sebagai
gantinya.

Yang ditambahkan V2 dibanding PRO_Resume: pelacak progres `step_stage` beserta
`require_vars` dan `write_stage_progress` dipindah ke sel tersendiri 1b (sel 3-4)
supaya setiap tahap bisa memakainya, dan pemecahan bertahap diperluas melampaui
Step 1 ke jembatan pasangan (7a-7b), Step 2 (8a-8f), serta evaluasi final
(9a-9b).

**Mengapa:** dua batasan urutan mudah rusak saat menyunting dengan tangan, dan
keduanya ditemukan lewat simulasi, bukan lewat pembacaan:

- `args_h` dan `logger2` harus dibangun di **8a**, bukan 8d. 8d dilewati saat
  cache hit Step 2, tetapi 8e dan 9a sama-sama membutuhkan `args_h`.
- **8c** harus tetap berjalan meski cache hit (ia menggerbangi pada `eval_loader_2`
  yang belum ada, bukan pada `STEP2_SKIP_TRAINING`), karena evaluasi final 9a
  memerlukan `eval_loader_2` dan `eval_gold_2`. Ini berbeda dari 5c, yang aman
  dilewati seluruhnya.

**Cara menerapkan:** setelah mengubah generator, jalankan ulang dan verifikasi
tiga jalur, bukan satu: sesi kosong (semua tahap melatih), artefak lengkap (semua
tahap dilewati), dan kernel-restart-langsung-ke-Step-2-saja (8a harus membangun
`args_h`; `ensure_objects()` di awal 8a/8c harus memulihkan `tokenizer`).

---

## 5. Rujukan Eksternal (jenis `reference`)

### 5.1 Sitasi absa5 Diverifikasi via Crossref

**Berkas memori:** `absa5-citations-verified-via-crossref.md`

Sitasi untuk pekerjaan quintuple adalah kode, bukan prosa: `absa5/references.py`
memuat 24 dataclass `Reference`, masing-masing dengan DOI yang diperiksa terhadap
`https://api.crossref.org/works/<doi>` pada 2026-08-28. Akses lewat
`python -m absa5 references [--table|--bibtex|--grouped|--module <name>]` atau
`absa5.cite("key")`. Gate `references` memvalidasi bentuk entri secara offline —
ia tidak memanggil Crossref, karena semua gate harus bisa jalan tanpa jaringan.

**Tiga karya benar-benar tidak punya DOI.** Dicatat dengan `note` yang
menjelaskan alasannya, dan gate gagal bila penjelasan itu hilang:

- Lafferty, McCallum & Pereira 2001 (CRF) — prosiding ICML 2001 tidak pernah
  terdaftar DOI; pakai https://repository.upenn.edu/cis_papers/159/
- Loshchilov & Hutter 2019 (AdamW) — ICLR/OpenReview tidak punya DOI;
  arXiv:1711.05101. Catat bahwa DOI `10.48550/arXiv.*` terdaftar di DataCite
  sehingga 404 di API Crossref.
- Ekman 1971 — bab buku Nebraska Symposium. **Jangan** menggantinya dengan
  makalah JPSP 1987 yang berbeda, `10.1037/0022-3514.53.4.712`.

**Empat jebakan yang ditemukan saat verifikasi:**

- Penulis pertama Shoes-ACOSI adalah **Peper**, bukan Nguyen atau Wu:
  `10.18653/v1/2024.findings-emnlp.907`.
- NusaWrites dideposit di bawah volume IJCNLP, `2023.ijcnlp-main.60`, bukan id
  `2023.aacl-main.*` mana pun.
- DOI BERT `10.18653/v1/N19-1423` bisa diselesaikan tetapi field `title` yang
  terdeposit di Crossref berupa string kosong; ambil judulnya dari ACL Anthology.
- Plutchik 2001 punya dua rekaman Crossref aktif; `10.1511/2001.4.344` yang
  orisinal, `10.1511/2001.28.344` duplikat tahun 2023.

`absa5.taxonomy.LABEL_SET_SOURCES` memetakan setiap label set terdaftar ke sebuah
kunci referensi, sehingga `python -m absa5 registries` mencetak provenance per
label set dan panduan anotasi yang dihasilkan menyitasi sumbernya sendiri.

---

## 6. Cara Merawat Arsip Ini

Memori agen adalah sumber utama; dokumen ini salinannya. Bila sebuah catatan
memori diperbarui atau dihapus, dokumen ini menjadi kedaluwarsa dan bukan
sebaliknya — jangan menyunting bagian di atas lalu menganggap memorinya ikut
berubah.

Beberapa fakta di sini memang punya tanggal kedaluwarsa dan sudah ditandai:
§4.9 misalnya mencatat bahwa PRO_Resume dulu kembar dengan PRO dan kini tidak
lagi. Bila sebuah catatan menyebut berkas, fungsi, atau flag, pastikan hal itu
masih ada sebelum menjadikannya dasar tindakan.

**Rujukan silang antar bagian:** §3.1 ↔ §4.1 ↔ §4.2 (topologi repositori dan
aturan PR) · §4.3 ↔ §4.4 ↔ §4.5 ↔ §4.6 (migrasi IndoBERT dan batasannya) ·
§4.7 ↔ §4.8 ↔ §5.1 (pekerjaan quintuple absa5) · §4.9 ↔ §4.10 ↔ §4.11 ↔ §4.12
↔ §4.13 ↔ §3.2 (notebook master pipeline dan skrip generatornya).
