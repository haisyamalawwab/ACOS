# 047 — Ringkasan Pekerjaan: Verifikasi Jalur A, Koreksi Artikel, dan Figur Arsitektur

**Tanggal:** 03/11/2026
**Ruang lingkup:** seluruh pekerjaan pada 02–03/11/2026, sesi verifikasi Jalur A sampai pembuatan figur arsitektur.
**Metode:** pembacaan kode dan keluaran tersimpan notebook (`execution_count`), pembacaan dokumen repo, validasi tabel Markdown, inspeksi berkas PNG. **Tidak ada sel notebook yang dijalankan ulang dan tidak ada data atau bobot yang diunduh.**
**Tingkat bukti:** **E2** untuk klaim yang dapat ditunjuk ke kode atau keluaran tersimpan; **E1** untuk klaim yang hanya bersandar pada riwayat git; **E0** untuk opini dan rekomendasi.

> **Putusan satu baris:** tiga dari empat butir Jalur A terbukti sampai nomor baris dan **satu klaim salah besarnya** — "1–3 poin" terukur hanya **0,07–0,56 poin**; koreksi sudah masuk ke `045` dan `042` melalui PR yang **sudah di-merge** (`dcaae58`), satu figur arsitektur baru sudah dibuat dengan label yang diverifikasi ke kode, dan **empat butir pra-submit masih belum tersentuh**.

---

## 1. Berkas yang berubah

| Berkas | Status | Isi perubahan |
|---|---|---|
| `reports/046_verifikasi_jalur_a_02112026_HM.md` | baru, sudah di `main` | Verifikasi 10 klaim Jalur A dengan tabel klaim–bukti–status, deret F1 per epoch, daftar "yang belum dapat diklaim", dan koreksi K-01…K-04 |
| `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md` | dikoreksi, sudah di `main` | "1–3 poin" diganti angka terukur di 5 titik; rentang turunan 64–67 / 45–48 / 78–81 dihapus; §5.1 ditulis ulang |
| `reports/042_kesiapan_publikasi_q2_s2_02112026_HM.md` | dikoreksi, sudah di `main` | Paragraf "Koreksi 046" ditambahkan pada catatan T03 di §14 (baris 257) |
| `reports/046` (baris 7, 55, 57) | dikoreksi pada 03/11/2026 | Penulisan "0,4–0,6 poin" diselaraskan menjadi **0,07–0,56 poin** — lihat K-05 di §3 |
| `reports/fig24/fig24_arsitektur_acos_indobert_detail.png` | baru, belum di-commit | Figur arsitektur dua tahap, 2688 × 1536 piksel, 6.754.405 bita |
| `reports/fig24/fig24_arsitektur_acos_indobert_detail.webp` | baru, belum di-commit | Versi terkompresi untuk penyisipan dokumen, 232.930 bita, kualitas 90 |

---

## 2. Verifikasi Jalur A — ringkasan

Rincian lengkap ada di `reports/046`; tabel di bawah hanya meringkas statusnya.

| Klaim yang diuji | Status | Bukti utama (E2) |
|---|---|---|
| `02` memilih *checkpoint* dengan mengevaluasi **test set** setiap epoch | terbukti | sel 7 (ec=5) `get_dev_examples` → `run_classifier_dataset_utils.py:151–156` membaca `{domain}_test_quad_bert.tsv`; sel 11 (ec=7) `eval_type="test"` + `torch.save` saat F1 naik |
| `04` memakai pola yang sama | terbukti | sel 6 (ec=3) `resolve_eval_pair_file` → `colab_utils.py:1178–1192` mengembalikan `{domain}_test_pair_1st.tsv` |
| 81,27% dan 48,24% berasal dari seleksi tersebut | terbukti | `02` sel 11 mencetak "Epoch terbaik: 8 (81.27%)"; `04` sel 10 mencetak "Epoch terbaik: 12 (48.24%)" |
| Dev tersedia tetapi tidak dipakai | terbukti | `rest16_quad_dev.tsv` 171 baris, `rest16_dev_quad_bert.tsv`, `rest16_dev_pair.tsv` semuanya ada |
| Dampak seleksi **1–3 poin** | **salah besarnya** | terukur **0,56** poin (`02`) dan **0,07** poin (`04`) |
| Angka terkoreksi 64–67 / 45–48 / 78–81 | **tanpa dasar** | turunan klaim di atas, tidak ada pengukuran |

**Deret yang menjadi dasar pengukuran (E2, keluaran tersimpan):**

| Run | Maksimum | Epoch terakhir | Selisih | Plateau (rata-rata) | Selisih |
|---|---:|---:|---:|---:|---:|
| `02` Step-1 rest16, 15 epoch | 81,27 (ep 8) | 80,71 | **0,56** | 80,83 | 0,44 |
| `04` Step-2 rest16, 15 epoch | 48,24 (ep 12) | 48,17 | **0,07** | 47,86 | 0,38 |

---

## 3. Koreksi yang diterapkan

| ID | Berkas dan titik | Tindakan |
|---|---|---|
| K-01 | `045` baris 27 (abstrak ID), baris 37 (abstrak EN) | "1–3 poin" → "0,07–0,56 poin (selisih maksimum terhadap epoch terakhir)", ditambah pernyataan bahwa bias lintas-run tidak terukur |
| K-02 | `045` baris 265 (§5.1) | Menghapus rentang turunan 64–67% / 45–48% / 78–81%; menggantinya dengan deret epoch dan dua hal yang tidak dapat diukur |
| K-03 | `045` baris 294 (Tabel 8), baris 305 (simpulan) | Sel estimasi dan kalimat simpulan diganti angka terukur |
| K-04 | `042` baris 257 (§14 catatan T03) | Paragraf "Koreksi 046" ditambahkan; T03 dinyatakan tetap P0 karena protokolnya keliru, bukan karena besarnya selisih |
| K-05 | `046` baris 7, 55, 57 | "0,4–0,6 poin" → "0,07–0,56 poin" agar konsisten dengan `045` dan dengan angka terukur |

**Catatan atas K-05.** Laporan 046 semula menulis rentang "0,4–0,6 poin". Rentang itu **tidak mencakup** hasil Step-2 yang hanya 0,07 poin, jadi bertentangan dengan pengukurannya sendiri. Koreksi ini contoh persis masalah yang laporan 046 coba cegah: angka yang ditulis ulang dari ingatan, bukan dari tabel. Sumber angka tunggal sekarang hanya §2 laporan 046.

---

## 4. Temuan sampingan yang perlu diingat

| Temuan | Bukti | Implikasi |
|---|---|---|
| Nama fungsi menyesatkan: `get_dev_examples` membaca **berkas test** | `run_classifier_dataset_utils.py:151–156` | Tidak boleh menyimpulkan "dev dipakai" dari nama metode; harus dibaca isi berkasnya |
| `get_test_1st_examples` hanya alias dari `get_dev_examples` | `run_classifier_dataset_utils.py:161–163` | Dua nama berbeda, satu perilaku; memperbesar peluang salah baca |
| Tag CNN/CRF pada tahap 1 memang ada di kode | `modeling.py:1538–1541` (`crf_num = 6`, `CRF(6)`) | Klaim "BIO-CRF 6 label" pada figur sah, bukan sekadar label pemasaran |
| Label sekuens berjumlah 6 | `run_classifier_dataset_utils.py:172` (`['[CLS]', 'O', 'I-A', 'B-A', 'I-O', 'B-O']`) | Jumlah kelas pada figur = 6, sesuai kode |
| Kepala implisit tidak seragam | `modeling.py:1546–1555`: aspek dari `pooled_output`, opini dari token terakhir | Menulis "CLS head" untuk keduanya adalah penyederhanaan; perlu dicatat bila figur masuk artikel |

---

## 5. Figur arsitektur (`reports/fig24`)

**Spesifikasi berkas.**

| Atribut | Nilai |
|---|---|
| Berkas | `fig24_arsitektur_acos_indobert_detail.png` dan `.webp` |
| Dimensi PNG | 2688 × 1536 piksel |
| Ukuran | 6.754.405 bita (PNG), 232.930 bita (WebP) |
| Palet | navy gelap, cyan, putih |
| Gaya | kotak alur isometrik, vektor bergaya, latar kisi halus |

**Isi tiga zona.** Kiri: `Input Clause` → `IndoBERT-base Encoder` → dua cabang, yaitu `BIO-CRF Sequence Tagger` (6 label: `[CLS]`, `O`, `B-A`, `I-A`, `B-O`, `I-O`) dan dua kepala implisit (aspek, opini). Tengah: `Candidate Pair Bridge` dengan pasangan Cartesian (aᵢ, oⱼ). Kanan: `Candidate Pair + Clause` → `IndoBERT Encoder` → `39-class Multi-label Head` (13 kategori × 3 sentimen) → empat chip keluaran `Aspect`, `Category`, `Opinion`, `Sentiment`.

**Verifikasi label figur ke kode (semua E2).**

| Label pada figur | Sumber |
|---|---|
| "BIO-CRF Sequence Tagger" | `Extract-Classify-ACOS/modeling.py:1538–1541` |
| 6 label sekuens | `run_classifier_dataset_utils.py:172` |
| Dua kepala implisit aspek dan opini | `modeling.py:1546–1555` |
| "39-class Multi-label Head, 13 kategori × 3 sentimen" | 13 × 3 = 39, sesuai `reports/045` Tabel 8 |

**Dua keterbatasan figur yang harus disebut bila dipakai di artikel.**

1. Label "CLS head" untuk opini implisit tidak akurat — kode memakai token terakhir, bukan `[CLS]`. Usulan penggantian: "pooled / last-token heads".
2. Urutan chip label pada figur adalah B sebelum I, sedangkan kode mendaftar I sebelum B. Isinya sama, tetapi penulisan berbeda dari `seqlabs` aslinya.

**Catatan teknis.** Konversi WebP memakai Pillow 11.x yang dipasang di sandbox dengan `--break-system-packages`. Paket itu **tidak persisten** (batasan `V-04`), tetapi berkas WebP sudah tersimpan permanen di repo.

---

## 6. Status repositori dan pull request

| Butir | Keadaan | Tingkat bukti |
|---|---|---|
| PR koreksi 042/045/046 | **sudah di-merge**; `main` pada `dcaae58` berjudul "Merge pull request #14 from rozanhaisyam/arena/17ccb1ea-acos" | E1 (riwayat git lokal) |
| Cabang kerja sekarang | `arena/7a7f8e99-acos`, bersih kecuali `reports/fig24/` yang belum di-commit | E1 |
| Isi koreksi benar-benar ada di `main` | `045` baris 27, 294, 305 memuat `0,07–0,56`; baris 37 (abstrak EN) memuat `0.07–0.56`; baris 265 memuat batas `0,44–0,56` dan `0,07–0,38`; `042` baris 257 memuat paragraf koreksi | E2 (grep pada berkas) |
| Validasi tabel Markdown | `045` 12 tabel, `046` 4 tabel, `042` 15 tabel, semuanya 0 masalah kolom | E2 (skrip pemeriksa) |

Catatan jujur soal penomoran: nomor PR pada riwayat lokal tidak cocok dengan nomor yang sempat saya sebut di percakapan. Yang dapat dipegang adalah **isi commit `dcaae58`**, bukan nomornya.

---

## 7. Yang belum dikerjakan

| Butir | Alasan belum dikerjakan | Pemilik tindakan |
|---|---|---|
| **T03** — ubah `eval_type` dan loader ke `dev` pada `02` dan `04` | Butuh eksekusi ulang dengan GPU; tanpa itu angka baru tidak sah diklaim | Pengguna |
| DOI untuk 24 rujukan `045` | Butuh pencarian metadata per rujukan; tidak boleh dikarang | Pengguna atau sesi khusus |
| Sinkronisasi abstrak `035` (97,94% → 81,27%; 67,86% → 67,69%) | Belum diputuskan apakah `035` diperbarui atau dibekukan | Pengguna |
| Metadata penulis `045` baris 5–8 | Masih placeholder `[Nama Penulis Kedua]`, `[Afiliasi ...]`, `[email@institusi.ac.id]` | Pengguna |
| Penyisipan `fig24` ke dalam `045` | Menunggu keputusan apakah menggantikan atau mendampingi `fig18` | Pengguna |

---

## 8. Cara memverifikasi ulang laporan ini

Semua perintah dijalankan dari akar repo dan tidak mengubah berkas.

```bash
# 1. Klaim angka: deret epoch dan status seleksi tersimpan di keluaran notebook
grep -n "Epoch terbaik" notebooks/02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb
grep -n "Epoch terbaik" notebooks/04_ACOS_Step2_Category_Sentiment_Classification.ipynb

# 2. Klaim kode: berkas test dipakai sebagai "dev", CRF, dan jumlah label
sed -n 151,156p Extract-Classify-ACOS/run_classifier_dataset_utils.py
sed -n 1178,1192p Extract-Classify-ACOS/colab_utils.py
sed -n 1538,1555p Extract-Classify-ACOS/modeling.py

# 3. Klaim koreksi: tidak ada lagi angka "1–3 poin" di 045
grep -c "1–3 poin" reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md   # harus 0
grep -n "0,07–0,56" reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md   # baris 27, 294, 305

# 4. Figur: dimensi dan ukuran
python3 -c "import struct;d=open('reports/fig24/fig24_arsitektur_acos_indobert_detail.png','rb').read(33);print(struct.unpack('>II',d[16:24]))"
```

---

## 9. Batasan laporan ini

1. **Tidak ada eksekusi ulang.** Seluruh angka model berasal dari keluaran yang sudah tersimpan; angka baru hanya boleh diklaim setelah T03 dikerjakan.
2. **Bias lintas-run tidak terukur.** Laporan ini hanya mengukur selisih maksimum terhadap epoch terakhir pada dua run yang deretnya tersedia. Tidak ada dasar untuk menyimpulkan besarnya bias pemilihan run terbaik dari banyak run.
3. **Deret epoch appsid tidak tersedia.** Angka 67,69% berasal dari artefak tanpa deret per epoch di repositori, sehingga tidak dapat diuji dengan cara yang sama.
4. **Figur bersifat ilustratif, bukan presisi struktural.** Ia tidak menggambarkan dimensi tensor, jumlah lapisan, atau alur dropout; semua itu harus dibaca dari `modeling.py`.
5. **Verifikasi merge bersandar pada riwayat git lokal**, bukan pada API GitHub, karena nomor PR pada riwayat tidak konsisten dengan sebutan di percakapan.
