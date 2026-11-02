# Korelasi Plot (PNG) ↔ Hasil CSV pada `ACOS-IndoBERT/results`

> **Tanggal:** 03112026
> **Pertanyaan:** apakah gambar plot yang dihasilkan *berkorelasi* dengan hasil-hasil CSV?
> **Cakupan plot:** 4 PNG, semuanya di `results/_eda/plots/` (0 dari 94 folder run CV memiliki plot)
> **Metode:** pembacaan visual tiap PNG + penghitungan ulang nilai dari CSV sumber (`eda_dataset_statistics.csv`, `eda_category_sentiment_counts.csv`, `eda_length_describe.csv`, `eda_all_samples_annotated.csv` 92.074 baris) secara independen, lalu cocokan sel-per-sel
> **Prasyarat baca:** `reports/038` (verdict hasil), `reports/039` (indeks partisi & ablasi)

---

## 0. Jawaban Singkat

**Ya — keempat plot berkorelasi PERSIS (1:1) dengan CSV sumbernya, nol selisih.** Namun korelasi itu **terjadi sepenuhnya di lapisan EDA**: tidak ada satu pun plot yang mewakili hasil training, karena 94 folder run CV tidak menghasilkan plot maupun metrik sah. Jadi "plot ↔ CSV hasil" hanya bermakna untuk CSV *pra-pemrosesan*, dan di situ pun kecocokannya sempurna.

Tingkat kecocokan per plot:

| Plot | CSV sumber | Derajat korelasi |
|---|---|---|
| `01_eda_dataset_distribution.png` | `eda_dataset_statistics.csv` | **Identik** (12/12 bar) |
| `02_eda_category_sentiment.png` | `eda_category_sentiment_counts.csv` + `eda_dataset_statistics.csv` | **Identik** (bar = jumlah baris; pie = jumlah kolom) |
| `02b_eda_length_and_implicit_combo.png` | `eda_length_describe.csv` + `eda_all_samples_annotated.csv` | **Identik** + mengungkap struktur joint yang tidak terlihat di CSV marginal |
| `02c_eda_category_sentiment_heatmap.png` | `eda_category_sentiment_counts.csv` | **Identik** (39/39 sel angka tercetak sama) |

---

## 1. Verifikasi Per Plot

### 1.1 `01_eda_dataset_distribution.png` ↔ `eda_dataset_statistics.csv`

Panel kiri "Kalimat & Quadruple per Split" dan kanan "Aspek Eksplisit vs Implisit" membaca kolom yang sama. Nilai terbaca dari gambar vs CSV:

| Split | Sentences (plot/CSV) | Total_Quad (plot/CSV) | Aspek Ekspl. (plot/CSV) | Aspek Impl. (plot/CSV) |
|---|---|---|---|---|
| train | 60.159 / 60.159 ✅ | 72.973 / 72.973 ✅ | 51.184 / 51.184 ✅ | 21.789 / 21.789 ✅ |
| dev | 8.027 / 8.027 ✅ | 9.587 / 9.587 ✅ | 6.588 / 6.588 ✅ | 2.999 / 2.999 ✅ |
| test | 7.891 / 7.891 ✅ | 9.514 / 9.514 ✅ | 6.576 / 6.576 ✅ | 2.938 / 2.938 ✅ |

**12/12 bar cocok.** Konsistensi internal: tiap split, Eksplisit + Implisit = Total_Quadruples (mis. train 51.184+21.789 = 72.973 ✅).

> ⚠️ **Satu jebakan interpretasi:** sumbu "Sentences" memakai kolom `Sentences` (60.159), **bukan** jumlah baris `eda_all_samples_annotated.csv` (92.074). CSV anotasi itu **per-quadruple**, bukan per-kalimat. Siapa pun yang menghitung ulang "jumlah kalimat" dari CSV anotasi akan mendapat 92.074 dan mengira plot 01 salah — padahal keduanya benar pada satuan berbeda.

### 1.2 `02_eda_category_sentiment.png` ↔ dua CSV

**Panel kiri (bar "Kategori Aspek")** = jumlah tiga kolom sentimen (0+1+2) per kategori dari `eda_category_sentiment_counts.csv`, diurutkan menurun:

| Kategori | Σ 3 kolom (CSV) | Tinggi bar (plot) |
|---|---|---|
| FEATURES_PRODUCT | 27.694 | ≈27.700 ✅ (tertinggi, melewati grid 25.000) |
| TRANSACTION_TRANSFER | 14.752 | ≈14.750 ✅ |
| APP_PERFORMANCE | 9.718 | ≈9.700 ✅ |
| AUTH_ACCESS | 6.615 | ✅ |
| ONBOARDING_KYC | 6.585 | ✅ |
| UI_UX_DESIGN | 6.225 | ✅ |
| … (7 sisanya menurun) | 4.845 → 1.822 | ✅ urutan sama |

**Panel kanan (pie "Sebaran Polaritas Sentimen")**: Negative 49,8% · Positive 38,9% · Neutral 11,3%. Diverifikasi dari **dua sumber berbeda**:
- Jumlah kolom `eda_category_sentiment_counts.csv`: 45.824 / 35.846 / 10.404 → 49,8% / 38,9% / 11,3% ✅
- Jumlah kolom `eda_dataset_statistics.csv` (baris 0/1/2): 45.824 / 35.846 / 10.404 → identik ✅
- Hitung ulang langsung dari 92.074 baris `eda_all_samples_annotated.csv`: 45.824 / 35.846 / 10.404 ✅

**Tiga sumber independen menghasilkan angka sama** — ini sinyal integritas data yang kuat, bukan sekadar plot menyalin satu CSV.

### 1.3 `02b_eda_length_and_implicit_combo.png` ↔ `eda_length_describe.csv` + CSV anotasi

**Panel kiri (histogram "Distribusi Panjang Klausa")**: garis putus-putus `median = 7 kata`. Cocok dengan `eda_length_describe.csv` (`50% = 7,0`). Distribusi menceng kanan, puncak 5–7 kata, ekor memanjang — konsisten mean 8,92 > median 7, dan sumbu x berhenti sebelum ~80 (CSV `max = 79`). Hitung ulang dari CSV anotasi: mean 8,92; median 7; min 1; max 79; p25 4; p75 11 — **enam-enamnya cocok.**

**Panel kanan (bar "Kombinasi Implisit/Eksplisit")** — **ini korelasi paling menarik.** Tiga bar:

| Bar (plot) | Nilai (plot) | Padanan di CSV |
|---|---|---|
| Eksplisit Aspek + Implisit Opini | 37.274 (40,5%) | = `Implicit_Opinions` Σ (29.702+3.751+3.821) ✅ |
| Implisit Aspek + Eksplisit Opini | 27.726 (30,1%) | = `Implicit_Aspects` Σ (21.789+2.999+2.938) ✅ |
| Eksplisit Aspek + Eksplisit Opini | 27.074 (29,4%) | = residual 92.074 − 37.274 − 27.726 ✅ |

Diverifikasi langsung dari **distribusi joint** dua kolom flag di `eda_all_samples_annotated.csv`:

```
(Is_Implicit_Aspect, Is_Implicit_Opinion):
  (False, False) = 27.074   → Eksplisit Aspek + Eksplisit Opini
  (False, True ) = 37.274   → Eksplisit Aspek + Implisit Opini
  (True,  False) = 27.726   → Implisit Aspek + Eksplisit Opini
  (True,  True ) =      0   → Implisit Aspek + Implisit Opini  (TIDAK muncul di plot)
```

**Kesimpulan analitis:** plot ini **bukan** sekadar visualisasi marginal — ia adalah *joint count* nyata, dan keabsahannya terbukti karena `(True,True) = 0`. Artinya **tidak ada satu pun quadruple yang memiliki aspek implisit DAN opini implisit sekaligus**. Itu sebabnya hanya 3 bar yang muncul dan ketiganya berjumlah tepat 92.074. Fakta ini **tidak bisa** disimpulkan dari `eda_dataset_statistics.csv` (yang hanya menyimpan marginal) — jadi plot 02b **menambah informasi** di atas CSV marginal, sekaligus mengonfirmasi CSV anotasi dan CSV statistik saling konsisten.

### 1.4 `02c_eda_category_sentiment_heatmap.png` ↔ `eda_category_sentiment_counts.csv`

Heatmap 13×3 dengan **angka tercetak di tiap sel**. Semua 39 sel dibandingkan dengan CSV: **39/39 identik** (mis. FEATURES_PRODUCT 11.178/2.304/14.212; SECURITY_FRAUD 655/125/1.042; UI_UX_DESIGN 1.398/400/4.427). Colorbar "Jumlah quadruple" 0→14.000; sel tergelap = FEATURES_PRODUCT/Positive (14.212), sel terang = PROMO_MARKETING/Neutral (124) — pemetaan warna monoton dan benar. Plot ini secara harfiah adalah render tabular dari CSV tersebut.

---

## 2. Yang TIDAK Berkorelasi (dan mengapa itu penting)

| Kenyataan | Bukti |
|---|---|
| Tidak ada plot untuk 94 run CV | Semua folder `cv5fold_*`/`cv10fold_*` punya subfolder `plots/` **kosong**; hanya run `1424` membuat kerangka folder itupun tanpa isi |
| CSV "hasil" training tidak punya padanan visual | Satu-satunya CSV hasil = 6 `training_log.csv`/`eval_per_epoch.csv` berisi metrik degenerat (F1 100%, `fp=fn=0`) — **tidak ada plot yang menggambarkannya**, dan memang tidak seharusnya |
| Plot ≠ bukti model | Karena 0 run berstatus `OK`, seluruh visual di `results/` menggambarkan **data mentah**, bukan kinerja. Mengutip plot sebagai "hasil eksperimen" adalah kategori kesalahan yang sama dengan mengutip F1 100% di `reports/038` §4 |

---

## 3. Matriks Korelasi Ringkas

| Plot ↔ CSV | `dataset_statistics` | `category_sentiment_counts` | `length_describe` | `all_samples_annotated` |
|---|:---:|:---:|:---:|:---:|
| `01` distribusi split | ● identik | — | — | ○ (sumber berbeda: kalimat vs quadruple) |
| `02` kategori + pie | ● (pie) | ● (bar+pie) | — | ● (pie, konfirmasi ke-3) |
| `02b` panjang + combo | ● (combo marginal) | — | ● (histogram) | ● (combo = joint sejati) |
| `02c` heatmap | — | ● identik 39/39 | — | ● (sumber mentah heatmap) |

● = kecocokan terverifikasi sel-per-sel · ○ = perlu catatan satuan · — = tidak dipakai.

---

## 4. Temuan & Rekomendasi

1. **Integritas lapisan EDA terjamin.** Keempat plot dapat dipertanggungjawabkan: angka di gambar = angka di CSV, dan tiga CSV saling mengonfirmasi. Aman dikutip ke laporan sebagai *data statistics*.
2. **Plot 02b menyimpan informasi struktural** (kenolakan aspek-implisit + opini-implisit) yang tidak ada di CSV marginal. Nilai ini layak dijadikan **asumsi validasi** saat membangun ulang tokenisasi: jika nanti joint `(True,True)` tiba-tiba bukan 0, berarti pipeline anotasi berubah.
3. **Seragamkan satuan "kalimat vs quadruple"** (catatan §1.1) agar plot 01 tidak disalahartikan saat orang menghitung ulang dari CSV anotasi.
4. **Jangan tambahkan plot hasil training sampai 8 gerbang G1–G8 di `reports/039` §5.5 lolos.** Prioritas visual berikutnya seharusnya *learning curve* A1/A3 dan perbandingan antar-fold A2 — semuanya butuh run `OK` yang saat ini nol.
5. **Jadikan heatmap 02c generator-nya berbasis CSV** (bukan hardcode) sehingga EDA per-partisi (item E2.1 di `reports/039`) bisa diproduksi otomatis untuk 18 partisi dengan format sama.

---

*Seluruh angka kecocokan diverifikasi dengan menghitung ulang langsung dari berkas CSV di disk; lihat §1 untuk tabel cocok-per-sel. Dapat direproduksi dengan memuat `eda_all_samples_annotated.csv` dan tiga CSV statistik di `_eda/csv/`.*
