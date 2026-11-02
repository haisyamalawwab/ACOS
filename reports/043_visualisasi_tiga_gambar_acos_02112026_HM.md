# 043 — Dokumentasi Visualisasi: Tiga Gambar (Arsitektur, Granularitas Input, Ketercakupan Span)

**Tanggal:** 02/11/2026
**Penulis:** HM
**Branch:** `arena/461c288a-acos` (berbasis `main` @ `196e3fb1`)
**Commit rentang:** `948c584` → `0b9c0df`
**Rujukan terkait:** [`042`](042_kesiapan_publikasi_q2_s2_02112026_HM.md) (penilaian kesiapan), [`035`](035_Artikel_Revisi_ACOS_IndoBERT_12092026.md) (naskah), [`023`](023_pipeline_acos_indobert_dataset_indonesia_04092026.md) (pengukuran granularitas)

> **Putusan satu baris:** tiga gambar selesai, ter-render, dan ter-commit (PNG 300 dpi + SVG + WebP), tetapi **angka yang divisualkan tetap berstatus E1** — hanya satu dari lima angka (0 `[UNK]`) yang dapat dilacak langsung ke artefak JSON; sisanya (61,5% / 48,0% / 100%) hanya hidup di tabel naratif `023 §2.2` tanpa skrip penghitung, sehingga gambar ini **belum boleh diklaim reproducible** sampai `R-V02` dikerjakan.

---

## 1. Lingkup permintaan

| # | Permintaan | Wujud yang diminta | Status |
|---|---|---|---|
| 1 | Diagram arsitektur dua tahap ACOS-IndoBERT | tiga panel: Tahap 1, Bridge, Tahap 2 | selesai (`fig18`) |
| 2 | Diagram alir komparatif granularitas input | kiri review-level, kanan clause-level | selesai (`fig19`) |
| 3 | Grafik batang perbandingan ketercakupan span | batang berkelompok + penanda eliminasi truncation loss | selesai (`fig20`) |

Ketiganya diminta sebagai "visual / diagram placeholder", yaitu **boleh skematik**, tetapi wajib memuat elemen yang disebutkan secara eksplisit pada tiap permintaan (diperiksa di §5). Format keluaran: PNG (utama), SVG (penyuntingan), WebP (distribusi ringan).

---

## 2. Inventaris berkas

Seluruh berkas berada di `reports/` dan `scripts/`; tidak ada berkas biner lain yang ditambahkan ke repo pada sesi ini.

| Berkas | Format | Ukuran (byte) | SHA-256 (10 digit) | Commit |
|---|---|---|---|---|
| `reports/fig18_arsitektur_dua_tahap_acos_indobert.png` | PNG 3780×2139 @300 dpi | 523.180 | `52f1df47db` | `948c584` |
| `reports/fig18_arsitektur_dua_tahap_acos_indobert.svg` | SVG (teks hidup) | 34.083 | `9adc7bf027` | `948c584` |
| `reports/fig19_granularitas_input_ulasan_vs_klausa.png` | PNG 3780×2139 @300 dpi | 445.182 | `b70a8636b7` | `0b9c0df` |
| `reports/fig19_granularitas_input_ulasan_vs_klausa.svg` | SVG (teks hidup) | 36.596 | `fdc778aedc` | `0b9c0df` |
| `reports/fig19_granularitas_input_ulasan_vs_klausa.webp` | WebP kualitas 92 | 342.738 | `6d4a1e6588` | `0b9c0df` |
| `reports/fig20_ketercakupan_span_mapping.png` | PNG 3780×2139 @300 dpi | 340.537 | `bc59e40788` | `0b9c0df` |
| `reports/fig20_ketercakupan_span_mapping.svg` | SVG (teks hidup) | 16.741 | `202aecb184` | `0b9c0df` |
| `reports/fig20_ketercakupan_span_mapping.webp` | WebP kualitas 92 | 267.822 | `dfb15c10e0` | `0b9c0df` |
| `scripts/fig18_arsitektur.py` | Python, 223 baris | 9.935 | `3e3d354c73` | `948c584` |
| `scripts/fig19_granularitas.py` | Python, 234 baris | 11.349 | `8793b273a2` | `0b9c0df` |
| `scripts/fig20_ketercakupan_span.py` | Python, 171 baris | 8.095 | `77c11a6ccc` | `0b9c0df` |

Catatan ukuran berkas: `fig18` belum punya varian WebP — ketidaklengkapan ini disengaja setelah dievaluasi (§7, `V-06`), bukan kelalaian yang tidak disadari.

---

## 3. Spesifikasi teknis

| Aspek | Nilai | Catatan |
|---|---|---|
| Interpreter | Python 3.11.2 | sama dengan lingkungan kerja repo |
| Pustaka | matplotlib 3.11.2 | **bukan stdlib** — lihat `V-04` |
| Kanvas logis | 160 × 90 unit | semua koordinat ditulis manual, tanpa layout engine |
| Ukuran fisik | `figsize=(16, 9)` inci | `bbox_inches="tight"` memangkas margin → keluaran 3780×2139 px |
| Resolusi | 300 dpi (118,11 px/cm) | terverifikasi lewat metadata `identify` |
| Font | DejaVu Sans | satu-satunya keluarga font yang dipakai; tidak ada font eksternal |
| SVG | `svg.fonttype="none"` | teks tetap teks (dapat diedit), tetapi reflow bila font tidak tersedia (`V-05`) |
| Determinisme | tidak ada `random`, tidak ada I/O data | keluaran identik untuk masukan skrip yang sama |
| Palet | biru `#2b6cb0`, merah `#c53030`, hijau `#2f855a`, emas `#b7791f`, tinta `#1a202c` | setiap peran warna selalu disertai label teks, tidak bergantung warna saja |

Tidak ada satu pun gambar yang membaca dataset, checkpoint, atau keluaran model. Semua angka **ditulis sebagai literal di dalam skrip**. Konsekuensinya: gambar tidak dapat "menyesuaikan diri" bila angka induk berubah — sinkronisasi bersifat manual (`R-V03`).

---

## 4. Isi tiap gambar

### 4.1 `fig18` — Gambar 1: Arsitektur dua tahap

| Blok | Elemen yang digambar |
|---|---|
| Tahap 1 (biru) | klausa contoh → `IndoBERT · indobert-base-p1` (12 layer · 768 hidden · 12 head · vocab 50.000) → bercabang: **6-label BIO-CRF** (B/I-A · B/I-O · penanda implisit) dan **Head IA/Head IO biner** dari vektor `[CLS]` |
| Tahap 1 (keluaran) | kotak "Kandidat entitas": a₁…aₙ + IA, o₁…oₘ + IO; kotak putus-putus "Contoh keluaran Tahap 1" |
| Bridge (emas) | matriks 3×3 (a₁,a₂,IA) × (o₁,o₂,IO), sel **−1,−1** terisi; `P = A × O = {(aᵢ, oⱼ)}`; kotak "Skala kandidat" (rest16 10.735/895; appsid 10.991/9.006) |
| Tahap 2 (hijau) | klausa + pasangan → encoder IndoBERT (`mean-pool span → h_pair ∈ ℝ¹⁵³⁶`) → **Multi-Label Head 39-d** (`13 kategori × 3 sentimen · Linear(1536, 39) + BCEWithLogits`) → strip 39 logit → tuple `(a, c, s, o)` dengan dua contoh baris (eksplisit dan implisit) |

Catatan representasi: gambar menampilkan head 39 dimensi **tunggal**, sedangkan implementasi repo memakai **dual-head** (13 BCE + 3 CE dengan rekonstruksi fused-39). Ini kompromi keterbacaan yang disengaja; bila gambar dipakai di bagian metode, wajib disertai keterangan agar tidak dibaca sebagai klaim arsitektur yang berbeda dari `035 §IV-C`.

### 4.2 `fig19` — Gambar 2: Granularitas input

| Sisi | Alur yang digambar |
|---|---|
| Sumber (atas) | satu ulasan utuh, bercabang ke dua perlakuan |
| A · review-level (merah) | ulasan utuh → WordPiece `max_seq_length = 128` → strip 24 sel dengan 6 sel ekor bergaris putus-putus dan label "batas 128 token"/"sisa ulasan hilang" → **Span truncation loss** → bar 61,5% (aspek) dan 48,0% (opini) |
| B · clause-level (hijau) | empat klausa independen → retokenisasi WordPiece per klausa (≤128 token) → "Tidak ada pemotongan" → **100%** ketercakupan + lencana **0 token `[UNK]`** |

### 4.3 `fig20` — Gambar 3: Ketercakupan span mapping

| Elemen | Detail |
|---|---|
| Batang berkelompok | dua kelompok atribut (Aspek, Opini); tiap kelompok satu batang merah dan satu batang hijau |
| Nilai | 61,5% → 100,0% (aspek); 48,0% → 100,0% (opini) |
| Area bergaris | komplemen terhadap 100%: 38,5% (aspek) dan 52,0% (opini) = span tidak terpetakan |
| Penanda selisih | Δ +38,5 poin dan +52,0 poin, dicetak di bawah label kelompok |
| Panel kanan | "Eliminasi truncation loss": angka besar **0**, rincian per tingkat, dan catatan bahwa penanda = 100% − ketercakupan |
| Plafon | garis putus-putus pada 100% sebagai batas teoretis |

---

## 5. Kepatuhan terhadap elemen wajib

| Elemen yang diminta | Gambar | Status |
|---|---|---|
| Tahap 1: klausa → IndoBERT → 6-label BIO-CRF | `fig18` | ada |
| Dua head biner IA/IO dari `[CLS]` | `fig18` | ada |
| Bridge: produk Kartesian termasuk pasangan `[-1,-1]` | `fig18` | ada (sel disorot) |
| Tahap 2: IndoBERT kedua + Multi-Label Head 39-d (13×3) | `fig18` | ada |
| Tuple kuadrupel `(a, c, s, o)` | `fig18` | ada (dua contoh) |
| Review-level: satu ulasan diinput langsung | `fig19` | ada |
| Pemotongan pada batas `seq_length` | `fig19` | ada (strip token + garis batas) |
| Ketercakupan aspek 61,5% | `fig19`, `fig20` | ada |
| Ketercakupan opini 48,0% | `fig19`, `fig20` | ada |
| Clause-level: dekomposisi menjadi klausa | `fig19` | ada (4 kartu klausa) |
| Retokenisasi WordPiece per klausa | `fig19` | ada |
| 0 token `[UNK]` | `fig19` | ada |
| 100% ketercakupan seluruh tuple | `fig19`, `fig20` | ada |
| Penanda eliminasi total truncation loss | `fig20` | ada (panel khusus) |

---

## 6. Riwayat iterasi dan cacat visual yang diperbaiki

Verifikasi **hanya** melalui pembacaan PNG hasil render; SVG tidak dapat dipratinjau di lingkungan ini (`V-07`).

| Gambar | Iterasi | Cacat yang ditemukan secara visual | Tindakan |
|---|---|---|---|
| `fig18` | 1 | label "hidden states"/"[CLS]" bertumpuk; judul masuk ke dalam kotak kuadrupel; strip 39 logit melebar sampai tepi panel | label `[CLS]` dibuang, panah bridge diluruskan tanpa label, blok "Skala kandidat" dinaikkan, strip logit diturunkan, panah logit→teks dihapus |
| `fig18` | 2 | tidak ada tumpang-tindih tersisa; ruang kosong di panel bridge masih lebar | diterima (kekosongan disengaja sebagai jeda visual antar-tahap) |
| `fig19` | 1 | judul panel tertimpa panah diagonal dari kotak sumber; label "batas 128 token" menabrak judul tokenizer; label "sisa ulasan dibuang" menimpa keterangan bawah strip | panah dipendekkan ke tepi panel + panah pendek di dalam panel, judul panel dipendekkan, label dipindah |
| `fig19` | 2 | label batas masih menimpa sel strip token | label dijadikan horizontal di atas garis batas |
| `fig19` | 3 | tidak ada tumpang-tindih tersisa | diterima |
| `fig20` | 1 | legenda bertumpuk (perkiraan lebar teks salah); nilai 61,5% jatuh di dalam area bergaris; blok teks panel kanan berdesakan | legenda dua baris dengan posisi tetap + item berpola garis; nilai dipindah ke dalam batang; jarak vertikal panel kanan diatur ulang |
| `fig20` | 2 | tidak ada tumpang-tindih tersisa | diterima |

Jumlah total iterasi: **7 render** untuk 3 gambar (2 + 3 + 2). Setiap iterasi dijalankan ulang dari skrip; tidak ada penyuntingan gambar secara manual.

---

## 7. Provenance angka dan tingkat bukti

Tingkat bukti mengikuti konvensi 041/042: **E2** = dijalankan ulang di sesi ini, **E1** = artefak/berkas terbaca langsung tetapi tidak dieksekusi ulang, **E0** = klaim tanpa sumber terlacak.

| Angka | Sumber terlacak | Tingkat | Catatan |
|---|---|---|---|
| 61,5% span aspek (ulasan utuh) | [`023`](023_pipeline_acos_indobert_dataset_indonesia_04092026.md) §2.2 tabel; diulang di `030` §3.3, `032` baris 77, `035` §III-C baris 81 | E1 | tidak ada skrip penghitung di repo |
| 48,0% span opini (ulasan utuh) | idem | E1 | idem |
| 100% span aspek/opini (klausa) | idem (80.260 baris klausa) | E1 | idem |
| 0 token `[UNK]` | `build/_indobert_tokenized/_build_report_appsid.json` → `unk_disisipkan: 0` pada train/dev/test; dikutip `035` baris 435 (`unk: 0`) | E1 | artefak build, bukan hasil eksekusi ulang |
| `span_invalid: 0` | JSON yang sama | E1 | memperkuat klaim "tidak ada span hilang saat retokenisasi" |
| Panjang klausa jauh di bawah 128 | JSON yang sama, `histogram_panjang_subword`: bin tertinggi = 80 (train 4 baris, dev 1, test 1) | E1 | implikasinya panjang < 96 token, sehingga batas 128 tidak pernah tersentuh |
| 39 = 13 kategori × 3 sentimen | `035` §IV-C; `_build_acos_report.json` (13 kategori, 3 kelas) | E1 | konsisten |
| 12 layer · 768 hidden · vocab 50.000 | konfigurasi `indobert-base-p1` (dibahas di 042) | E1 | tidak diverifikasi ulang pada sesi ini |

**Implikasi langsung:** dua dari tiga gambar (`fig19`, `fig20`) memuat angka yang **tidak dapat direproduksi dari repo** karena tidak ada skrip yang menghitungnya. Yang dapat direproduksi hanyalah *gambarnya*, bukan *angkanya*. Ini harus dinyatakan jujur bila gambar dipakai di naskah.

---

## 8. Temuan audit atas pekerjaan visualisasi

| ID | Temuan | Dampak | Status |
|---|---|---|---|
| `V-01` | Kaki `fig19` menyebut "naskah 035 §III-C" saja, padahal tabel pengukuran primer ada di `023 §2.2` | jejak bukti terputus bila pembaca hanya menelusuri 035 (yang memuat angka sebagai prosa) | **diperbaiki** di `0b9c0df` |
| `V-02` | Docstring `ACOS-IndoBERT/acos_id/build_acos.py` menulis "membuang ~62% span", tidak cocok dengan 61,5%/48,0% (kerugian sebenarnya 38,5% aspek dan 52,0% opini) | angka ~62% tampaknya berasal dari 37,6% klausa yang *tidak* dapat dipetakan ke `text_norm` — dua metrik berbeda tercampur dalam satu kalimat | **terbuka**, perlu koreksi teks |
| `V-03` | 61,5% / 48,0% / 100% hanya ada di tabel naratif; tidak ada `scripts/audit_span_coverage.py` maupun artefak JSON hasilnya | tidak reproducible; rawan drift bila dataset dibangun ulang | **terbuka** (`R-V02`) |
| `V-04` | Generator memakai matplotlib, melanggar aturan "generator stdlib murni" yang dipakai untuk laporan 041/042 | `python3 scripts/fig1x.py` gagal di lingkungan bersih tanpa matplotlib; pemasangan memerlukan `--break-system-packages` (PEP 668) dan **tidak persisten** pada snapshot | **diterima sadar**, mitigasi di `R-V01` |
| `V-05` | `svg.fonttype="none"` menyimpan teks hidup, tetapi tidak menyertakan font | SVG dapat berubah tata letak bila dibuka tanpa DejaVu Sans | **terbuka**, mitigasi di `R-V05` |
| `V-06` | `fig18` tidak punya varian WebP, sedangkan `fig19`/`fig20` punya | kumpulan deliverable tidak seragam | **terbuka**, keputusan: seragamkan atau hapus WebP |
| `V-07` | Verifikasi visual hanya lewat PNG; SVG tidak dapat dipratinjau di lingkungan sesi | cacat tata letak pada SVG (mis. pergeseran teks) tidak terdeteksi | **terbuka**, mitigasi di `R-V06` |
| `V-08` | Nomor berkas (`fig18`–`fig20`) tidak sama dengan nomor di dalam gambar (Gambar 1–3) | risiko salah rujuk antara naskah dan berkas; `reports/` sudah memuat `fig3`–`fig17` sehingga nomor berkas tidak dapat disamakan begitu saja | **terbuka**, mitigasi di `R-V04` |

Catatan tambahan: `fig19` menampilkan "0 token `[UNK]`" sebagai sifat **varian klausa dengan tokenisasi tanda baca**, bukan sifat universal pipeline. Tanpa pemisahan tanda baca (`str.split()`), `023 §2.3` mencatat ketercakupan turun ke 68,6%/60,0%. Gambar tidak menyebut perbedaan ini, sehingga berpotensi dibaca terlalu luas.

---

## 9. Rekomendasi lanjutan

| ID | Rekomendasi | Prioritas | Alasan |
|---|---|---|---|
| `R-V01` | Tambahkan `scripts/requirements-figs.txt` (`matplotlib>=3.8`) dan catatan pemasangan `--break-system-packages` atau venv | tinggi | mencegah kegagalan reproduksi yang membingungkan |
| `R-V02` | Tulis `scripts/audit_span_coverage.py` yang menghitung ulang 61,5%/48,0%/100% dari `data/Apps-ACOS/processed/*` dan menyimpan `reports/043_data/span_coverage.json` | tinggi | menaikkan bukti dari E1 ke E2 dan menutup `V-03` |
| `R-V03` | Jadikan angka pada skrip gambar dibaca dari JSON hasil `R-V02` alih-alih literal | sedang | menghapus risiko drift manual |
| `R-V04` | Tetapkan konvensi: rujuk berkas sebagai `fig18` dan naskah sebagai "Gambar 1 (berkas `fig18`)" di daftar gambar | sedang | menutup `V-08` |
| `R-V05` | Untuk versi cetak, simpan SVG dengan `svg.fonttype="path"` sebagai alternatif | rendah | menghilangkan ketergantungan font saat dikirim ke penerbit |
| `R-V06` | Render PDF vektor (`savefig(".pdf")`) sebagai jalur verifikasi tata letak yang dapat diperiksa tanpa font sistem | rendah | menutup `V-07` |
| `R-V07` | Seragamkan format keluaran: semua gambar `png + svg + webp`, atau semua `png + svg` | rendah | menutup `V-06` |
| `R-V08` | Perbaiki docstring `build_acos.py` ("~62%" → "38,5% aspek / 52,0% opini hilang pada ulasan utuh; 37,6% klausa tidak dapat dipetakan ke `text_norm`") | sedang | menutup `V-02`, mencegah salah kutip di masa depan |

---

## 10. Reproduksi

```bash
# prasyarat (sekali per lingkungan; tidak persisten pada snapshot)
python3 -m pip install --quiet --break-system-packages matplotlib

# dari akar repo
python3 scripts/fig18_arsitektur.py
python3 scripts/fig19_granularitas.py
python3 scripts/fig20_ketercakupan_span.py

# varian WebP (memerlukan ImageMagick)
convert reports/fig19_granularitas_input_ulasan_vs_klausa.png -quality 92 \
        reports/fig19_granularitas_input_ulasan_vs_klausa.webp
convert reports/fig20_ketercakupan_span_mapping.png -quality 92 \
        reports/fig20_ketercakupan_span_mapping.webp
```

Keluaran bersifat deterministik: tidak ada pembacaan data, tidak ada pemanggilan jaringan, tidak ada `random`. Perbedaan hasil antar-mesin hanya dapat berasal dari versi matplotlib dan ketersediaan font DejaVu Sans.

---

## 11. Lampiran — peta permintaan ke berkas

| Permintaan pengguna | Berkas gambar | Judul di dalam gambar |
|---|---|---|
| "Diagram Arsitektur Dua Tahap ACOS-IndoBERT" | `fig18_arsitektur_dua_tahap_acos_indobert.*` | Gambar 1. Arsitektur Dua Tahap ACOS-IndoBERT |
| "Diagram Alir Komparatif Granularitas Input" | `fig19_granularitas_input_ulasan_vs_klausa.*` | Gambar 2. Granularitas Input: Ulasan Utuh vs Segmentasi Klausa |
| "Grafik Batang Perbandingan Ketercakupan Span Mapping" | `fig20_ketercakupan_span_mapping.*` | Gambar 3. Ketercakupan Span Mapping: Ulasan Utuh vs Klausa |

### Caption siap pakai (untuk naskah)

- **Gambar 1.** Arsitektur dua tahap ACOS-IndoBERT: ekstraksi span berbasis BIO-CRF dengan deteksi slot implisit (kiri), pembentukan pasangan kandidat Kartesian (tengah), dan klasifikasi quadruple multi-label 39 dimensi (kanan).
- **Gambar 2.** Perbandingan granularitas input: pemrosesan tingkat ulasan memicu kehilangan span pada batas `seq_length` (ketercakupan aspek 61,5%, opini 48,0%), sedangkan segmentasi klausa dengan retokenisasi WordPiece menghasilkan 0 token `[UNK]` dan ketercakupan span 100%.
- **Gambar 3.** Ketercakupan span mapping pada unit ulasan utuh dan unit klausa. Area bergaris menunjukkan proporsi span aspek/opini di luar jendela model pada pendekatan review-level (38,5% dan 52,0%); pada unit klausa truncation loss tereliminasi sepenuhnya (0%).

Ketiga caption menyebut angka, sehingga **tidak boleh dipasang di naskah sebelum `R-V02` selesai** dan angkanya cocok dengan hasil hitung ulang.
