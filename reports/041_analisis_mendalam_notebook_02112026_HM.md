# Laporan 041 — Analisis Mendalam 45 Notebook `.ipynb` dan Komparasi Tabel

**Repositori:** `rozanhaisyam/ACOS` · **Branch:** `arena/7b92b123-acos` · **Tanggal:** 2 November 2026, 23.35 WIB · **Sifat:** analisis statis (tanpa menjalankan ulang sel)

**Ruang lingkup:** seluruh 45 berkas `.ipynb` di repositori (37,7 MB), 1.748 sel (1037 kode + 711 markdown), 469 sel beroutput, 13 sel bererror, dan 88 baris metrik numerik.

**Berkas pendukung:** `reports/041_data/` (`notebooks_inventaris.csv`, `notebooks_metrik.csv`, `notebooks_galat.csv`, `notebooks_jejak.csv`, `notebooks_kemiripan.csv`, `provenance_angka.csv`, `kontradiksi_angka.csv`, `subtask_15_perbandingan.csv`) dan skrip audit `scripts/audit_041_notebooks.py` + `scripts/gen_report_041.py`. Laporan 036–040 tidak diubah.

---

## 1. Ringkasan eksekutif

1. **Notebook bukan bukti yang bersih.** Dari 1.037 sel kode, 575 (55,4%) tidak pernah dieksekusi; 89 output tidak memiliki `execution_count` (output "yatim" — ditempel atau berasal dari kernel lain). 19 notebook sama sekali tidak punya sel tereksekusi, 24 notebook menjalankan kurang dari separuh selnya.
2. **Angka besar di notebook V4 adalah cache-hit, bukan training.** `97,94%` dan `67,86%` dimuat dengan pesan `[CACHE HIT]` / `dilewati — training tidak dijalankan` (sel 5e/8e). Hanya `V4_1_03` (1 epoch) dan `V4_INDOBERT` (3 epoch) yang benar-benar melatih Step-2.
3. **Kontaminasi lintas domain terdokumentasi di dalam notebook.** `V5_EN_REST16_LAPTOP` menyalin checkpoint `appsid_08092026_150437xxx` ke folder sesi rest16, mencetak riwayat Step-1 appsid (8 baris, 97,94%) sebagai milik rest16, lalu menghasilkan `fp = 165.728` dan F1 0,00%.
4. **Tiga run BERT-rest16 yang konsisten justru ada di notebook lokal.** `02` (Step-1 81,27%, 15 epoch) dan `04` (Step-2 48,24%, 15 epoch) dieksekusi penuh tanpa cache; nilainya berdekatan dengan artefak Drive 27/08 (81,23% dan 47,68%). Ini baseline yang paling dapat dipertahankan.
5. **Duplikasi masif.** 4 pasang berkas identik per-hash dan 19 pasang berkas dengan kemiripan kode ≥0,90. V4.1, V4.2, dan V4.3 adalah satu basis kode yang sama (Jaccard 0,965–0,968) dengan output metrik yang identik — bukan tiga replikasi.
6. **Nama berkas tidak mencerminkan isi.** `..._V4_INDOBERT_run08092026.ipynb` seluruhnya berjalan pada sesi `appsid_24092026_0901` (24 September), bukan 8 September; `..._V4_INDOBERT copy.ipynb` hanya 2 sel dieksekusi tetapi memuat 19 output.
7. **Satu-satunya dekomposisi 15 sub-task yang lengkap dan segar ada di dua tempat:** `04_ACOS_Step2` (rest16, 78,95% → 48,24%) dan `MI300X 2409` (appsid, 94,21% → 67,69%). Keduanya memakai TP/FP/FN, sehingga dapat direkonsiliasi.

**Putusan satu baris:** notebook menjelaskan *bagaimana* angka 67–69% dan 47–48% diperoleh, tetapi tidak menambah klaim baru yang lebih tinggi; klaim 97,94% (Step-1) dan 66,28% (quadruple appsid) adalah artefak cache/agregasi yang harus tetap diberi tanda bintang.

---

## 2. Metode, definisi, dan batas

**Yang dilakukan.** (a) Inventaris seluruh `.ipynb` (ukuran, hash SHA-1 16 karakter atas gabungan teks sel kode). (b) Ekstraksi setiap output `text/plain`/`text`, lalu penandaan sel beroutput, sel tanpa `execution_count`, monotonsitas `execution_count`, dan gambar. (c) Regex metrik (`micro-F1`, `quad-F1`, `sentiment_acc`, `accuracy`, `precision`, `recall`) beserta nomor sel dan `exec_count`. (d) Klasifikasi traceback menjadi 13 sel error. (e) Deteksi jejak sesi (`appsid_*`, `rest16_*`), akar Drive (`ACOS`, `ACOS-ASLI`, `/shared-docker`, `ACOSE`), flag (`DRY_RUN`, `USE_DUAL_HEAD`, `SKIP_TRAINING`), dan pemakaian `save_pretrained`/`SubtaskMetricCapture`. (f) Kemiripan kode antar notebook dengan Jaccard 8-gram atas seluruh sel kode (108 pasang ≥0,40).

**Yang tidak dilakukan.** Sel tidak dijalankan ulang; tidak ada data atau bobot yang diunduh; tidak ada kesimpulan tentang performa model di luar angka yang tercetak di berkas. Analisis ini melengkapi — bukan menggantikan — pemeriksaan artefak Drive pada Laporan 040.

**Tingkat bukti yang dipakai konsisten di seluruh tabel:**

| Tingkat | Arti | Contoh pemakaian |
| --- | --- | --- |
| **E2** | Angka tercetak dari eksekusi yang punya `execution_count`, dengan sesi/path jelas | `02` sel 13 ec=8 → 81,27% |
| **E3** | Angka dimuat dari cache/berkas, bukan dihitung di sel itu | `V4_1` sel 71 ec=43 → `[CACHE HIT]` 67,86% |
| **E1** | Output ada tetapi tanpa `execution_count` (yatim) atau sesi tidak dapat dilacak | `UPDATE` sel 13 → 81,23% |
| **E0** | Tidak ada eksekusi / gagal / dry-run | `V5.2.1` sel 35 → `Belum ada run OK` |

---

## 3. Tabel 1 — Inventaris 45 notebook menurut keluarga

Kolom *Jalan* hanya menghitung sel kode yang memiliki `execution_count`; *Yatim* = sel beroutput tanpa `execution_count`.

| Keluarga | Nb | Sel | Kode | Jalan | % | Output | Error | Metrik | Yatim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V4.1 | 5 | 174 | 99 | 82 | 82.8% | 65 | 1 | 13 | 2 |
| Kaggle (2 salinan) | 2 | 160 | 96 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| ACOS-BERT V1 | 10 | 145 | 114 | 7 | 6.1% | 7 | 1 | 0 | 0 |
| V4.2 | 3 | 124 | 69 | 58 | 84.1% | 49 | 0 | 10 | 1 |
| V4.3 | 1 | 86 | 51 | 44 | 86.3% | 37 | 0 | 5 | 1 |
| Lokal 01-05 | 5 | 83 | 42 | 28 | 66.7% | 33 | 0 | 52 | 5 |
| V5 EN rest16 | 1 | 82 | 49 | 21 | 42.9% | 38 | 1 | 18 | 23 |
| V3 ACOSE | 1 | 82 | 49 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| V4 BERT MI300X | 1 | 81 | 49 | 29 | 59.2% | 38 | 1 | 2 | 17 |
| V4 IndoBERT 0809 | 1 | 81 | 49 | 49 | 100.0% | 38 | 0 | 1 | 0 |
| V4 IndoBERT MI300X | 1 | 81 | 49 | 47 | 95.9% | 38 | 0 | 2 | 2 |
| V4 IndoBERT (copy) | 1 | 80 | 48 | 2 | 4.2% | 21 | 2 | 0 | 19 |
| V4 IndoBERT | 1 | 80 | 48 | 40 | 83.3% | 32 | 0 | 9 | 1 |
| V2 STAGED | 1 | 72 | 44 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| PRO Resume | 1 | 62 | 42 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| V5.2.1 | 1 | 40 | 20 | 17 | 85.0% | 18 | 1 | 0 | 1 |
| V5.3 | 1 | 40 | 20 | 13 | 65.0% | 18 | 1 | 0 | 5 |
| V5.2 | 1 | 35 | 18 | 3 | 16.7% | 3 | 1 | 0 | 0 |
| PRO | 1 | 29 | 14 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| V5.1 | 1 | 27 | 14 | 3 | 21.4% | 3 | 1 | 0 | 0 |
| UPDATE | 1 | 26 | 14 | 0 | 0.0% | 10 | 1 | 1 | 10 |
| V5 MI300X | 1 | 24 | 12 | 3 | 25.0% | 4 | 1 | 0 | 1 |
| ASLI | 1 | 24 | 12 | 6 | 50.0% | 7 | 0 | 0 | 1 |
| Colab dasar | 1 | 23 | 12 | 10 | 83.3% | 10 | 1 | 2 | 0 |
| Utilitas | 1 | 7 | 3 | 0 | 0.0% | 0 | 0 | 0 | 0 |
| **Total (24 keluarga)** | 45 | 1748 | 1037 | 462 | 44.6% | 469 | 13 | 88 | 89 |

**Bacaan.** Dua belas notebook keluarga V4 (V4, V4.1, V4.2, V4.3, copy, 0809, 2409) memuat 625 sel, tetapi hanya 275 sel yang benar-benar dieksekusi. Sebaliknya, keluarga `Lokal 01-05` kecil (83 sel) tetapi menyumbang 52 dari 88 baris metrik — karena setiap epoch dicetak, bukan karena hasilnya lebih baik.

---

## 4. Tabel 2 — Matriks 45 notebook

| No | Notebook | Keluarga | Sel | Kode | Jalan | Yatim | Err | Met | Peran |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 00_ACOS_Master_Pipeline_V1_1_BERT.ipynb | ACOS-BERT V1 | 24 | 20 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 2 | 00_ACOS_Master_Pipeline_V1_BERT.ipynb | ACOS-BERT V1 | 18 | 13 | 7 | 0 | 1 | 0 | Kerangka V1 + 1 error |
| 3 | V1_01_setup.ipynb | ACOS-BERT V1 | 8 | 6 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 4 | V1_02_step1_train.ipynb | ACOS-BERT V1 | 11 | 8 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 5 | V1_03_step2_train.ipynb | ACOS-BERT V1 | 12 | 9 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 6 | V1_04_eval_inference.ipynb | ACOS-BERT V1 | 11 | 8 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 7 | V1_1_01_setup.ipynb | ACOS-BERT V1 | 12 | 10 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 8 | V1_1_02_step1_train.ipynb | ACOS-BERT V1 | 16 | 13 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 9 | V1_1_03_step2_train.ipynb | ACOS-BERT V1 | 17 | 14 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 10 | V1_1_04_eval_inference.ipynb | ACOS-BERT V1 | 16 | 13 | 0 | 0 | 0 | 0 | Kerangka V1 (0 sel) |
| 11 | 00_ACOS_Master_Pipeline_Colab_ASLI.ipynb | ASLI | 24 | 12 | 6 | 1 | 0 | 0 | Kerangka |
| 12 | 00_ACOS_Master_Pipeline_Colab.ipynb | Colab dasar | 23 | 12 | 10 | 0 | 1 | 2 | Kanonik parsial (Step-2 0,00) |
| 13 | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb | Kaggle (2 salinan) | 80 | 48 | 0 | 0 | 0 | 0 | Kerangka (0 sel) |
| 14 | kaggle:00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb | Kaggle (2 salinan) | 80 | 48 | 0 | 0 | 0 | 0 | Kerangka (0 sel) |
| 15 | 01_ACOS_Setup_and_Data_Exploration.ipynb | Lokal 01-05 | 17 | 8 | 8 | 0 | 0 | 0 | Kanonik EDA |
| 16 | 02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb | Lokal 01-05 | 16 | 8 | 8 | 0 | 0 | 18 | Kanonik 15 epoch |
| 17 | 03_ACOS_Step1_to_Step2_Pair_Generation.ipynb | Lokal 01-05 | 11 | 5 | 5 | 0 | 0 | 0 | Kanonik pair-gen |
| 18 | 04_ACOS_Step2_Category_Sentiment_Classification.i… | Lokal 01-05 | 15 | 7 | 7 | 0 | 0 | 34 | Kanonik 15 epoch |
| 19 | 05_ACOS_Evaluation_and_Interactive_Inference.ipynb | Lokal 01-05 | 24 | 14 | 0 | 5 | 0 | 0 | Kerangka + output yatim |
| 20 | 00_ACOS_Master_Pipeline_Colab_PRO.ipynb | PRO | 29 | 14 | 0 | 0 | 0 | 0 | Kerangka |
| 21 | 00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb | PRO Resume | 62 | 42 | 0 | 0 | 0 | 0 | Kerangka |
| 22 | 00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb | UPDATE | 26 | 14 | 0 | 10 | 1 | 1 | Output yatim + KeyError |
| 23 | GPU_Status.ipynb | Utilitas | 7 | 3 | 0 | 0 | 0 | 0 | Utilitas |
| 24 | 00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb | V2 STAGED | 72 | 44 | 0 | 0 | 0 | 0 | Kerangka |
| 25 | 00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb | V3 ACOSE | 82 | 49 | 0 | 0 | 0 | 0 | Kerangka |
| 26 | 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_run2… | V4 BERT MI300X | 81 | 49 | 29 | 17 | 1 | 2 | Gate-1 gagal, lanjut eval |
| 27 | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb | V4 IndoBERT | 80 | 48 | 40 | 1 | 0 | 9 | Kanonik (IndoBERT 0509) |
| 28 | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT copy.ip… | V4 IndoBERT (copy) | 80 | 48 | 2 | 19 | 2 | 0 | Output yatim (2 sel jalan) |
| 29 | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run0809… | V4 IndoBERT 0809 | 81 | 49 | 49 | 0 | 0 | 1 | Cache sesi 2409 (67,69) |
| 30 | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run2409… | V4 IndoBERT MI300X | 81 | 49 | 47 | 2 | 0 | 2 | Pair-eval 2409 (67,69) |
| 31 | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb | V4.1 | 80 | 48 | 44 | 1 | 0 | 5 | Echo cache 67,86 |
| 32 | V4_1_01_setup.ipynb | V4.1 | 33 | 22 | 22 | 0 | 0 | 0 | Kanonik setup |
| 33 | V4_1_02_step1_train.ipynb | V4.1 | 23 | 11 | 0 | 1 | 1 | 0 | Kerangka + error |
| 34 | V4_1_03_step2_train.ipynb | V4.1 | 21 | 9 | 8 | 0 | 0 | 3 | Kanonik (1 epoch) |
| 35 | V4_1_04_eval_inference.ipynb | V4.1 | 17 | 9 | 8 | 0 | 0 | 5 | Kanonik eval (2× jalan) |
| 36 | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipynb | V4.2 | 86 | 51 | 44 | 1 | 0 | 5 | Echo cache 67,86 |
| 37 | V4_2_05_acos_classification_indobert.ipynb | V4.2 | 21 | 9 | 7 | 0 | 0 | 0 | Duplikat V4_1_03 |
| 38 | V4_2_06_prediction_indobert.ipynb | V4.2 | 17 | 9 | 7 | 0 | 0 | 5 | Duplikat V4_1_04 |
| 39 | 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ipynb | V4.3 | 86 | 51 | 44 | 1 | 0 | 5 | Echo cache 67,86 |
| 40 | 00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP… | V5 EN rest16 | 82 | 49 | 21 | 23 | 1 | 18 | Kontaminasi lintas domain |
| 41 | 01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.i… | V5 MI300X | 24 | 12 | 3 | 1 | 1 | 0 | IndentationError |
| 42 | 01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_DriveSy… | V5.1 | 27 | 14 | 3 | 0 | 1 | 0 | 3 sel, import gagal |
| 43 | 02_ACOS_V5_2_Universal_FullExperiment_AllPlatform… | V5.2 | 35 | 18 | 3 | 0 | 1 | 0 | 3 sel, import gagal |
| 44 | 02_ACOS_V5_2_1_Embedding_Classification_Predictio… | V5.2.1 | 40 | 20 | 17 | 1 | 1 | 0 | Dry-run grid 54 |
| 45 | 03_ACOS_V5_3_Classification_Prediction_IndoBERT.i… | V5.3 | 40 | 20 | 13 | 5 | 1 | 0 | Dry-run grid 54 |

---

## 5. Tabel 3 — Integritas eksekusi

Sepuluh notebook teratas menurut jumlah output yatim (total 89 di seluruh repo):

| Notebook | Kode | Jalan | Tak pernah jalan | Yatim | ec tidak monoton | Rentang ec |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP… | 49 | 21 | 28 | 23 | ya | 2..30 |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT copy.ip… | 48 | 2 | 46 | 19 | tidak | 1..2 |
| 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_run2… | 49 | 29 | 20 | 17 | tidak | 1..29 |
| 00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb | 14 | 0 | 14 | 10 | tidak | — |
| 03_ACOS_V5_3_Classification_Prediction_IndoBERT.i… | 20 | 13 | 7 | 5 | tidak | 1..13 |
| 05_ACOS_Evaluation_and_Interactive_Inference.ipynb | 14 | 0 | 14 | 5 | tidak | — |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run2409… | 49 | 47 | 2 | 2 | tidak | 119..167 |
| 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb | 48 | 44 | 4 | 1 | tidak | 1..48 |
| 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipynb | 51 | 44 | 7 | 1 | tidak | 1..48 |
| 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ipynb | 51 | 44 | 7 | 1 | tidak | 1..48 |

- **19 notebook tanpa satu pun sel tereksekusi:** `00_ACOS_Master_Pipeline_V1_1_BERT.ipynb`, `V1_01_setup.ipynb`, `V1_02_step1_train.ipynb`, `V1_03_step2_train.ipynb`, `V1_04_eval_inference.ipynb`, `V1_1_01_setup.ipynb`, `V1_1_02_step1_train.ipynb`, `V1_1_03_step2_train.ipynb`, `V1_1_04_eval_inference.ipynb`, `00_ACOS_Master_Pipeline_Kaggle_V4_INDOB…`, `V4_1_02_step1_train.ipynb`, `GPU_Status.ipynb`, dan sisanya di Lampiran A.
- **24 notebook menjalankan <50% sel kode.** Yang mencolok: `V4_INDOBERT copy` (2 dari 48 sel) dan `V5_EN_REST16_LAPTOP` (21 dari 49, 23 yatim) — keduanya tetap memuat angka final yang tampak lengkap.
- `V4_1_04_eval_inference` adalah satu-satunya notebook dengan `execution_count` tidak monoton (32…53): sel 8 jalan pada ec=44, sel 10 pada ec=52 — evaluasi quadruple dan evaluasi 15 sub-task berasal dari dua eksekusi berbeda dalam satu berkas.
- Notebook lokal `01` mulai dari `execution_count = 97`, yaitu lanjutan kernel sesi lain; `V4_1_03`/`V4_2_05` mulai dari 32/35 (dijalankan di tengah sesi master), bukan sesi bersih.

---

## 6. Tabel 4 — Duplikasi kode

`notebooks_kemiripan.csv` mencatat **108 pasang** notebook dengan Jaccard ≥0,40. Pasangan identik (hash sel kode sama) dan pasangan dengan kemiripan ≥0,90:

| Hash / Jaccard | Notebook A | Notebook B | Nilai |
| --- | --- | --- | --- |
| 993464480c6c7ab6 | 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | identik (sha1 16 char) |
| 4850e59ec29f776a | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | identik (sha1 16 char) |
| ae701da3a7c53e88 | V4_1_03_step2_train.ipynb | V4_2_05_acos_classification_indobert.ipynb | identik (sha1 16 char) |
| 11072416eea615c1 | V4_1_04_eval_inference.ipynb | V4_2_06_prediction_indobert.ipynb | identik (sha1 16 char) |
| — | 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | 0.988 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | 0.988 |
| — | 02_ACOS_V5_2_1_Embedding_Classification_Predi… | 03_ACOS_V5_3_Classification_Prediction_IndoBE… | 0.988 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | 0.976 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ip… | 0.968 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | 0.965 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.957 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.957 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | 0.941 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.935 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.935 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ip… | 0.933 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ip… | 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | 0.911 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.903 |
| — | 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | 0.903 |

**Klaster yang terbentuk:**

| Klaster | Anggota | Kemiripan | Implikasi |
| --- | --- | --- | --- |
| Master V4 IndoBERT | V4 (asli), V4_1, V4_2, V4_3, copy, run0809, run2409, Kaggle ×2 | 0,755–0,976 | Satu basis kode; perbedaan terutama konfigurasi & output |
| Pipeline modular V4 | V4_1_03 ≡ V4_2_05 · V4_1_04 ≡ V4_2_06 | 1,000 / 1,000 | Berkas disalin, bukan versi baru |
| MI300X | V4_BERT_rest16 ≡ V4_INDOBERT_run2409 | 1,000 | Kode sama; hanya variabel backbone yang berbeda → rawan tertukar |
| Kaggle | 2 salinan di dua direktori | 1,000 | Redundansi murni |
| V5 | V5.2.1 ≡ V5.3 (0,988) · V5.1 ≡ V5.2 (0,811) | 0,811–0,988 | V5.3 hanya menambah sel klasifikasi di atas V5.2.1 |

Konsekuensi metodologis: **jumlah notebook tidak boleh dipakai sebagai ukuran jumlah eksperimen.** 45 berkas hanya menghasilkan 41 hash kode berbeda, dan setelah dikelompokkan menurut kemiripan ≥0,75 tinggal enam kelompok fungsional: ACOS-BERT V1 (10), lokal 01–05 (5), master Colab V4/V5_EN (13), pipeline modular V4 (6), V5 eksperimen (5), serta salinan/utilitas (3).

---

## 7. Tabel 5 — Provenance angka kunci

Setiap baris menjawab: angka ini datang dari notebook mana, sel berapa, dengan `exec_count` berapa, dan pada sesi apa.

| ID | Angka | Notebook | Sel | ec | Sesi | Tingkat |
| --- | --- | --- | ---: | ---: | --- | ---: |
| P01 | Step-1 97,94 | V4_INDOBERT | 46 | 69 | appsid_05092026_122741 | E2 |
| P02 | Step-1 97,94 (echo) | V4_1_INDOBERT; V4_2_GUARDS; V4_3_SESSION | 58;58;58 | — | appsid_05092026_122741 | E3 |
| P03 | Step-1 97,94 di sesi rest16 | V5_EN_REST16_LAPTOP | 48 | — | rest16_12092026_104518 | E0 |
| P04 | Step-1 97,19 | run08092026; run24092026_MI300X | 45;45 | 37;148 | appsid_24092026_0901 | E3 |
| P05 | Step-2 67,16 | V4_INDOBERT | 67 | — | appsid_05092026_122741 | E2 |
| P06 | Step-2 67,86 | V4_1_03_step2_train | 19 | 41 | appsid_08092026_150437 | E2 |
| P07 | Step-2 67,86 (echo) | V4_1_INDOBERT; V4_2_GUARDS; V4_3_SESSION; V4_1_04; V4_2_06 | 71;71;71;8;11 | 43;43;43;44;43 | appsid_08092026_150437 | E3 |
| P08 | Step-2 67,69 | run08092026 | 72 | 51 | appsid_24092026_0901 | E3 |
| P09 | Step-2 67,69 (hitung ulang) | run24092026_MI300X | 72 | 162 | appsid_24092026_1426 | E2 |
| P10 | 15 sub-task 66,28 / 96,29 | V4_1_04_eval_inference | 10 | 52 | appsid_08092026_150437 | E2 |
| P11 | 15 sub-task 94,21 … 67,69 | run24092026_MI300X | 74 | 163 | appsid_24092026_1426 | E2 |
| P12 | Step-1 81,27 | 02_ACOS_Step1 | 13 | 8 | rest16_31082026_144800 | E2 |
| P13 | Step-2 48,24 | 04_ACOS_Step2 | 10 & 12 | 5 & 6 | rest16_02092026_135007 | E2 |
| P14 | 15 sub-task rest16 | 04_ACOS_Step2 | 12 | 6 | rest16_02092026_135007 | E2 |
| P15 | Step-1 81,23 | 00_..._UPDATE | 13 | — | rest16_27082026_090134 | E1 |
| P16 | Step-1 80,76 / Step-2 0,00 | 00_ACOS_Master_Pipeline_Colab | 12 & 16 | 7 & 9 | rest16_24092026_0849 | E2 |
| P17 | Step-2 0,00 + fp 165.728 | V5_EN_REST16_LAPTOP | 75 | — | rest16_12092026_104518 | E0 |
| P18 | Grid 54 run | V5.2.1; V5.3; V5.1; V5.2 | 19;19;7;7 | 10;—;52;52 | — | E0 |
| P19 | Dual-head 0,00 | V4_1; V4_2; V4_3; V4_1_04; V4_2_06 | 71;71;71;8;11 | 43;43;43;44;43 | — | E0 |
| P20 | 47,68 (tanpa notebook) | — | — | — | rest16_27082026_070817 | E2 |

**Pola yang terlihat.** Sembilan dari dua puluh angka kunci berstatus E3/E1/E0 — yaitu dimuat dari cache, yatim, atau tidak pernah dihitung. Hanya `02`, `04`, `V4_1_03`, `V4_INDOBERT` (Step-2 3 epoch), dan MI300X 2409 yang benar-benar menghitung ulang di selnya.

---

## 8. Tabel 6 — Angka yang sama muncul di banyak notebook

| Angka | Jml notebook | Notebook |
| --- | ---: | --- |
| 97,94 | 5 | 00_ACOS_Master_Pipeline_Colab_V4_1_INDO…; 00_ACOS_Master_Pipeline_Colab_V4_2_GUAR…; 00_ACOS_Master_Pipeline_Colab_V4_3_SESS…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE… … |
| 97,19 | 3 | 00_ACOS_Master_Pipeline_Colab_V4_BERT_r…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE… |
| 67,86 | 8 | 00_ACOS_Master_Pipeline_Colab_V4_1_INDO…; 00_ACOS_Master_Pipeline_Colab_V4_2_GUAR…; 00_ACOS_Master_Pipeline_Colab_V4_3_SESS…; 00_ACOS_Master_Pipeline_Colab_V5_EN_RES… … |
| 67,69 | 3 | 00_ACOS_Master_Pipeline_Colab_V4_BERT_r…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE… |
| 67,16 | 1 | 00_ACOS_Master_Pipeline_Colab_V4_INDOBE… |
| 66,28 | 5 | 00_ACOS_Master_Pipeline_Colab_V4_1_INDO…; 00_ACOS_Master_Pipeline_Colab_V4_2_GUAR…; 00_ACOS_Master_Pipeline_Colab_V4_3_SESS…; V4_1_04_eval_inference.ipynb … |
| 48,24 | 1 | 04_ACOS_Step2_Category_Sentiment_Classi… |
| 81,27 | 1 | 02_ACOS_Step1_Aspect_Opinion_Extraction… |
| 81,23 | 1 | 00_ACOS_Master_Pipeline_Colab_UPDATE.ip… |
| 80,76 | 2 | 00_ACOS_Master_Pipeline_Colab.ipynb; 02_ACOS_Step1_Aspect_Opinion_Extraction… |
| 78,95 | 1 | 04_ACOS_Step2_Category_Sentiment_Classi… |
| 94,21 | 3 | 00_ACOS_Master_Pipeline_Colab_V4_BERT_r…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE…; 00_ACOS_Master_Pipeline_Colab_V4_INDOBE… |

`67,86` muncul di 8 berkas dan `97,94` / `66,28` di 5 berkas — bukan karena direplikasi, tetapi karena rantai cache: `V4_INDOBERT` → `V4_1` → `V4_2` → `V4_3` → `V5_EN` → Kaggle. Sebaliknya `47,68` tidak muncul di satu notebook pun: angka itu hanya hidup di `master_metrics.json` Drive (P20), sehingga tidak dapat diverifikasi ulang dari repositori.

---

## 9. Tabel 7 — Kontradiksi antar notebook

| ID | Objek | Nilai A | Nilai B | Nilai C | Catatan |
| --- | --- | --- | --- | --- | --- |
| C01 | Step-2 rest16 | 48,24 (nb 04) | 47,68 (Drive 27/08) | 0,00 (V5_EN, cache appsid) | Tiga nilai untuk klaim yang sama; 0,00 adalah artefak cache lintas domain |
| C02 | Step-1 rest16 | 81,27 (nb 02, 31/08) | 81,23 (UPDATE, 27/08) | 97,94 (V5_EN, cache appsid) | Dua nilai wajar berdekatan (Δ0,04); 97,94 milik appsid |
| C03 | Step-2 appsid | 67,16 (0509, 3 ep) | 67,86 (0809, 1 ep) | 67,69 (0901, 3 ep) | TP+FN = 9.006 pada ketiganya, TP berbeda 6.552/6.654/6.681 |
| C04 | Step-1 appsid | 97,94 (0509, 8 ep) | 97,19 (0901, 3 ep) | — | Epoch lebih sedikit tetapi F1 hanya −0,75; tidak ada kurva 2409 |
| C05 | Jumlah metrik per sesi | 8 metrik (V4_1 echo) | 6 metrik (run0809) | 15 sub-task (V4_1_04) | Jumlah metrik tersimpan berbeda antar sesi; '8' dan '6' tidak dapat dibandingkan langsung |
| C06 | Quadruple rest16 vs appsid | 48,24 (nb 04) | 47,68 (Drive) | 66,28 (V4_1_04) / 47,03 (master_08 rest16) | 66,28 memakai gold 19.528 (2,17×) sehingga tidak sebanding |
| C07 | Jumlah pasangan kandidat | 1.450 / 1.451 (rest16) | 10.735 / 10.991 (appsid + V5_EN) | 301 (rest16 24/09) | Rasio pasangan:gold 1,6 vs 1,2 vs 12,0 → presisi anjlok pada 12,0 |
| C08 | Epoch Step-2 dijalankan | 15 (konfigurasi) | 3 (0509, 0901) | 1 (0809) | Tidak ada bukti early-stop eksplisit; '1 epoch' adalah cache-hit yang dipakai ulang |
| C09 | Artefak 15 sub-task rest16 | 78,95/82,51/70,11 (nb 04, 02/09) | 78,72/81,93/69,56 (Drive, 27/08) | — | Dua run berbeda, selisih ≤0,55 poin → konsisten |
| C10 | Status gate-1 | LULUS (V5_EN, IndoBERT) | GAGAL (V4_BERT_rest16) | LULUS (V5_EN rest16 BERT) | Gate lulus/gagal tidak menghentikan eksekusi sel berikutnya |

**C07 adalah temuan baru yang paling menjelaskan kegagalan.** Jumlah pasangan kandidat berbeda satu orde antara jalur lokal/Colab dan jalur V4/V5:

| Jalur | Sesi | Pasangan | Gold | Rasio | Prediksi (Quad num) | Hasil |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Lokal 03 → 04 | rest16_02092026 | 1.451 | 895 | 1,62 | 1.120 | 48,24% |
| Colab dasar | rest16_24092026_0849 | 1.450 | 895 | 1,62 | 301 | 0,00% |
| V4 appsid | appsid_08092026 | 10.735 | 9.006 | 1,19 | — | 67,86% |
| V4 appsid | appsid_24092026_1426 | 10.991 | 9.006 | 1,22 | 10.733 | 67,69% |
| V5_EN rest16 | rest16_12092026 | 10.735 | 895 | **12,0** | 165.728 | 0,00% |

Pada rest16 (583 kalimat, 916 quadruple) jumlah pasangan wajar ada di sekitar 1.450. Pipeline V4/V5 membangkitkan 10.735 pasangan untuk 895 gold — 12× lipat — sehingga FP meledak menjadi 165.728 dan F1 jatuh ke nol. Ini bukan kegagalan model, melainkan **kegagalan pembentukan pasangan** yang tidak pernah dibatasi ketika domain berpindah dari appsid (klausa) ke rest16 (kalimat).

---

## 10. Tabel 8 — Komparasi Step-1 per sesi

| Domain/backbone | Notebook | Sesi | Epoch konfig | Epoch terbaik | TP/FP/FN | P / R / F1 (%) | Catatan |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| rest16 (BERT-base) | 02_ACOS_Step1 | 31/08 14:48 | 15 | 8 | 1.367 / 382 / 248 | 78,16 / 84,64 / **81,27** | 15 epoch nyata; sel 11 (latih) + sel 13 (test) |
| rest16 (BERT-base) | UPDATE | 27/08 09:01 | 15 | 6 | 1.326 / 324 / 289 | **81,23** | output tanpa ec; KeyError 'a--1,-1' di sel 19 |
| rest16 (BERT-base) | Colab dasar | 24/09 08:49 | 15 | 14 | 1.339 / 362 / 276 | **80,76** | sesi 24/09; Step-2 kolaps (Quad num 301) |
| appsid (IndoBERT) | V4_INDOBERT | 05/09 12:27 | 8 | 8 | 16.514 / 434 / 259 | 97,44 / 98,46 / **97,94** | 8 epoch; Step-2 hanya 3 epoch |
| appsid (IndoBERT) | run08092026 / MI300X | 24/09 09:01 | 3 | 3 | — | **97,19** | cache-hit; riwayat 2409 tidak tercetak |

Dua hal yang perlu ditegaskan:

- **Tidak ada penurunan performa pada Step-1 rest16.** Tiga run menghasilkan 81,27 / 81,23 / 80,76 — rentang 0,51 poin. Klaim bahwa baseline rest16 gagal pada tahap ekstraksi tidak didukung notebook.
- **97,94% appsid bukan pembanding yang setara.** F1 appsid dihitung atas 16.773 span gold (TP 16.514 + FN 259; 17.207 prediksi), sedangkan rest16 dihitung atas 1.615 span gold (TP 1.367 + FN 248; 1.997 prediksi). Selisih 16,7 poin lebih mencerminkan granularitas data daripada kualitas model.

---

## 11. Tabel 9 — Komparasi Step-2 (quadruple) per sesi

| Domain | Sesi | Notebook | Epoch jalan | Quad num | TP/FP/FN | P / R / F1 (%) | Catatan |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| appsid | 0509 | V4_INDOBERT | 3 | 10.505 | 6.552 / 3.953 / 2.454 | 62,4 / 72,8 / **67,16** | output yatim (ec —) |
| appsid | 0809 | V4_1_03 | 1 | 10.735 | 6.654 / 3.951 / 2.352 | 62,74 / 73,88 / **67,86** | loss 0,5544; VRAM 3.971 MB |
| appsid | 0901 | run0809 + MI300X | 3 | 10.733 | 6.681 / 4.052 / 2.325 | 62,25 / 74,18 / **67,69** | cache lalu pair_eval 687 batch |
| rest16 | 27/08 | Drive (tanpa nb) | — | — | — | 43,06 / 53,41 / **47,68** | hanya master_metrics.json |
| rest16 | 02/09 | 04_ACOS_Step2 | 15 | 1.120 | 486 / 634 / 409 | 43,4 / 54,3 / **48,24** | 15 epoch, ep terbaik 12 |
| rest16 | 24/09 | Colab dasar | 15 | 301 | 0 / 301 / 895 | 0,00 / 0,00 / **0,00** | prediksi kolaps (301 baris) |
| rest16 | 12/09 | V5_EN | cache | — | 0 / 165.728 / 895 | 0,00 / 0,00 / **0,00** | cache appsid di folder rest16 |

**Yang dapat disimpulkan.** Pada appsid, tiga sesi menghasilkan 67,16 / 67,86 / 67,69 dengan TP+FN konstan 9.006 — variasi 0,7 poin, wajar untuk seed dan jumlah epoch berbeda. Pada rest16, hanya sesi 02/09 yang benar-benar melatih 15 epoch (48,24%); sesi 27/08 hanya tercatat di Drive (47,68%), sedangkan sesi 24/09 dan 12/09 gagal karena masalah pasangan/cache.

Perhatikan bahwa **67,69% bukan hasil baru**: MI300X 2409 menghitung ulang checkpoint yang sama dengan cache 0901 (TP/FP/FN identik: 6.681 / 4.052 / 2.325). Yang baru hanyalah dekomposisi 15 sub-task-nya.

---

## 12. Tabel 10 — 15 sub-task: IndoBERT-appsid vs BERT-rest16

Sumber: `MI300X 2409` sel 74 (ec=163, `master_08`) dan `04_ACOS_Step2` sel 12 (ec=6, `step2_07_metrik_15_subtask`). Keduanya memakai TP/FP/FN.

| Sub-task | Elemen | IndoBERT appsid | BERT rest16 | Selisih |
| --- | ---: | ---: | ---: | ---: |
| opinion | 1 | 94,21 | 78,88 | +15,33 |
| aspect | 1 | 92,57 | 78,31 | +14,26 |
| category | 1 | 91,84 | 78,95 | +12,89 |
| sentiment | 1 | 85,72 | 82,51 | +3,21 |
| category + aspect | 2 | 90,27 | 67,24 | +23,03 |
| sentiment + opinion | 2 | 82,72 | 71,74 | +10,98 |
| category + opinion | 2 | 81,37 | 65,27 | +16,10 |
| sentiment + aspect | 2 | 80,01 | 69,18 | +10,83 |
| category + sentiment | 2 | 79,47 | 70,11 | +9,36 |
| aspect + opinion | 2 | 78,52 | 57,87 | +20,65 |
| category + sentiment + aspect | 3 | 77,87 | 60,28 | +17,59 |
| category + aspect + opinion | 3 | 76,56 | 52,39 | +24,17 |
| category + sentiment + opinion | 3 | 70,73 | 59,63 | +11,10 |
| sentiment + aspect + opinion | 3 | 67,92 | 53,18 | +14,74 |
| category + sentiment + aspect + opinion | 4 | 66,08 | 48,24 | +17,84 |

Rata-rata per jumlah elemen:

| Elemen | IndoBERT | BERT | Selisih |
| --- | ---: | ---: | ---: |
| 1 elemen | 91,08 | 79,66 | +11,42 |
| 2 elemen | 82,06 | 66,90 | +15,16 |
| 3 elemen | 73,27 | 56,37 | +16,90 |
| 4 elemen | 66,08 | 48,24 | +17,84 |

**Peringatan komparabilitas.** Tabel ini **bukan** perbandingan backbone. Dataset berbeda (appsid: 9.006 quadruple gold; rest16: 895), bahasa berbeda (Indonesia vs Inggris), dan jumlah kandidat berbeda. Yang dapat dikatakan: pada kedua domain, penurunan F1 mengikuti jumlah elemen (4 elemen paling sulit), dan celah melebar seiring bertambahnya elemen — konsisten dengan akumulasi error pada rantai aspek–kategori–sentimen–opini.

---

## 13. Tabel 11 — Komparasi versi V4.1 / V4.2 / V4.3 / V5

| Versi | Nb | Kode | Jalan | Angka utama | Hitung ulang? | Ciri |
| --- | ---: | ---: | --- | --- | --- | --- |
| V4 (asli) | 1 | 48 | 40 (83%) | 67,16 · 97,94 | Tidak | Manual, tanpa guard |
| V4.1 | 5 | 99 | 82 (83%) | 67,86 · 97,94 | Ya (echo) | Modular 01–04; V4_1_02 kosong |
| V4.2 | 3 | 69 | 58 (84%) | 67,86 · 97,94 | Ya (echo) | GUARDS + 2 file salinan V4.1 |
| V4.3 | 1 | 51 | 44 (86%) | 67,86 · 97,94 | Ya (echo) | SESSION/state; sama dengan V4.2 (0,968) |
| V5.1 / V5.2 | 2 | 32 | 6 (19%) | — | — | 3 sel jalan lalu ModuleNotFoundError |
| V5.2.1 / V5.3 | 2 | 40 | 30 (75%) | — | Dry-run | Grid 54 run dicetak, 0 hasil |
| V5 MI300X | 1 | 12 | 3 (25%) | — | — | IndentationError sel 7 |

V4.1 → V4.2 → V4.3 menambah guard, penanganan sesi, dan modul, tetapi **tidak menambah eksekusi baru**: ketiganya mencetak 67,86 / 97,94 / 0,00 dari cache yang sama. V4.3 identik dengan V4.2 pada tingkat 0,968 — perbedaannya terutama pada sel state/session. V5 adalah percabangan lain: grid 54 run dirancang, tetapi seluruh sesi berhenti di `DRY_RUN` atau `ModuleNotFoundError`.

---

## 14. Tabel 12 — Lokal vs Colab vs MI300X vs Kaggle

| Lingkungan | Backbone dominan | Nb | Sel jalan | Angka | Training nyata | Kualitas bukti |
| --- | --- | ---: | --- | --- | --- | --- |
| Lokal `notebooks/01–05` | BERT-Inggris | 5 | 28/42 (66%) | 81,27 · 48,24 · 78,95 | 15 epoch penuh | Bukti terkuat baseline |
| Master Colab (V4/V4.x/V5_EN) | IndoBERT + BERT | 14 | 260/531 (48%) | 67,86 · 97,94 · 0,00 | Campur cache | Echo; output yatim terbanyak |
| MI300X (GPU AMD) | IndoBERT + BERT | 3 | 79/110 (71%) | 67,69 · 97,19 · 0,00 | Satu pair-eval nyata | Satu gate-1 gagal |
| Kaggle (2 salinan) | IndoBERT | 2 | 0/96 (0%) | — | Tidak pernah jalan | Identik byte-per-byte |
| ACOS-BERT V1 | BERT | 10 | 7/114 (6%) | — | Tidak pernah jalan | 1 error `torchcrf` |

Lingkungan lokal (`notebooks/01–05`) adalah satu-satunya tempat di mana seluruh rantai EDA → Step-1 → pair → Step-2 → evaluasi dijalankan berurutan tanpa cache. Dua berkas Kaggle dan 9 dari 10 berkas ACOS-BERT tidak pernah dieksekusi sama sekali; satu berkas ACOS-BERT (master V1) hanya menjalankan 7 sel lalu berhenti pada `ModuleNotFoundError: torchcrf`.

---

## 15. Tabel 13 — 13 sel error dan implikasinya

| Notebook | Sel | ec | Tipe | Pesan |
| --- | ---: | ---: | --- | --- |
| 00_ACOS_Master_Pipeline_V1_BERT.ipynb | 9 | 26 | ModuleNotFoundError | No module named 'torchcrf' |
| 00_ACOS_Master_Pipeline_Colab.ipynb | 18 | 10 | AttributeError | 'NoneType' object has no attribute 'to' |
| 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_ru… | 43 | 29 | RuntimeError | GATE 1 GAGAL: bobot encoder di model tidak sama den… |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT copy.… | 2 | 1 | KeyboardInterrupt |  |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT copy.… | 44 | 2 | NameError | name 'require_vars' is not defined |
| 00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPT… | 44 | 29 | RuntimeError | GATE 1 GAGAL: bobot encoder di model tidak sama den… |
| 01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X… | 7 | — | IndentationError | unexpected indent (890569663.py, line 25) |
| 01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_Drive… | 7 | 52 | ModuleNotFoundError | No module named 'bert_utils' |
| 02_ACOS_V5_2_1_Embedding_Classification_Predict… | 35 | — | AssertionError | Belum ada run OK — jalankan Sel 9 DRY_RUN=False dul… |
| 02_ACOS_V5_2_Universal_FullExperiment_AllPlatfo… | 7 | 52 | ModuleNotFoundError | No module named 'bert_utils' |
| 03_ACOS_V5_3_Classification_Prediction_IndoBERT… | 35 | — | AssertionError | Belum ada run OK — jalankan Sel 9 DRY_RUN=False dul… |
| V4_1_02_step1_train.ipynb | 2 | — | (kosong) |  |
| 00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb | 19 | — | KeyError | 'a--1,-1' |

**Tiga pola penting:**

1. **Kegagalan gate tidak menghentikan pipeline.** Pada `V4_BERT_rest16` (sel 43) dan `V5_EN_REST16_LAPTOP` (sel 44) muncul `RuntimeError: GATE 1 GAGAL: bobot encoder …`, tetapi sel 72/75 tetap dieksekusi dan mencetak metrik final. Gate berfungsi sebagai pencetak pesan, bukan penghenti alur — karena itu angka 0,00% pada V5_EN tetap ditampilkan seolah sah.
2. **Kegagalan import diulang tanpa perbaikan.** `V5.1` dan `V5.2` sama-sama berhenti di sel 7 dengan `ModuleNotFoundError: bert_utils`; sel berikutnya tetap dijalankan (3 sel) dan menghasilkan output yang identik di kedua berkas — indikasi salin-tempel output.
3. **Dry-run dilaporkan sebagai kegagalan, bukan hasil.** `V5.2.1` dan `V5.3` berhenti dengan `AssertionError: Belum ada run OK` — bukti bahwa 54 run pada grid tidak pernah ada yang selesai.

---

## 16. Tabel 14 — Jejak path, sesi, dan flag

| Notebook | Akar path | Flag | GPU | save_pretrained |
| --- | --- | --- | --- | --- |
| 00_ACOS_Master_Pipeline_V1_1_BERT.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_V1_BERT.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| V1_01_setup.ipynb | ACOS-ASLI | — | — | tidak |
| V1_02_step1_train.ipynb | ACOS-ASLI | — | cuda | tidak |
| V1_03_step2_train.ipynb | ACOS-ASLI | — | — | tidak |
| V1_04_eval_inference.ipynb | ACOS-ASLI | — | — | tidak |
| V1_1_01_setup.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| V1_1_02_step1_train.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| V1_1_03_step2_train.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| V1_1_04_eval_inference.ipynb | ACOS, ACOS-ASLI | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab.ipynb | ACOS, Extract-Classify-ACOS, data | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.i… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipy… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ip… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_… | ACOS, ACOS-ASLI, ACOS-IndoBERT, ACOS_BACKUP | — | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT cop… | ACOS, ACOS-ASLI, ACOS-IndoBERT | — | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipy… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | ACOS, ACOS-ASLI, ACOS-IndoBERT, ACOS_BACKUP | — | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run… | ACOS, ACOS-ASLI, ACOS-IndoBERT, ACOS_BACKUP | — | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| 00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LA… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI30… | ACOS | DRY_RUN=True | MI300X;ROCm;cuda;rocm | ya |
| 01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_Dri… | ACOS, ACOS-ASLI | DRY_RUN=True | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| 02_ACOS_V5_2_1_Embedding_Classification_Predi… | ACOS, ACOS-ASLI | DRY_RUN=True | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| 02_ACOS_V5_2_Universal_FullExperiment_AllPlat… | ACOS, ACOS-ASLI | DRY_RUN=True | A100;MI300X;ROCm;T4;cuda;rocm | ya |
| 03_ACOS_V5_3_Classification_Prediction_IndoBE… | ACOS, ACOS-ASLI | DRY_RUN=False | A100;MI300X;ROCm;T4;cuda;rocm | tidak |
| V4_1_01_setup.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | — | A100;T4;cuda | tidak |
| V4_1_02_step1_train.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | — | cuda | tidak |
| V4_1_03_step2_train.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | cuda | tidak |
| V4_1_04_eval_inference.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | — | — | tidak |
| V4_2_05_acos_classification_indobert.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | cuda | tidak |
| V4_2_06_prediction_indobert.ipynb | ACOS, ACOS-ASLI, ACOS-IndoBERT | — | — | tidak |
| GPU_Status.ipynb |  | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ip… | ACOS, ACOS-ASLI, ACOS-IndoBERT | USE_DUAL_HEAD=False | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_ASLI.ipynb | ACOS, Extract-Classify-ACOS, data | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_PRO.ipynb | ACOS | — | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb | ACOS, ACOS-ASLI | — | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb | ACOS | — | cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb | ACOS, ACOS-ASLI | — | A100;T4;cuda | tidak |
| 00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb | ACOS, ACOS-ASLI, ACOSE | — | A100;T4;cuda | tidak |
| 01_ACOS_Setup_and_Data_Exploration.ipynb | ACOS | — | cuda | tidak |
| 02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb |  | — | cuda | tidak |
| 03_ACOS_Step1_to_Step2_Pair_Generation.ipynb | ACOS | — | — | tidak |
| 04_ACOS_Step2_Category_Sentiment_Classificati… | ACOS | — | cuda | tidak |
| 05_ACOS_Evaluation_and_Interactive_Inference.… | ACOS | — | cuda | tidak |

Tiga akar path bercampur dalam satu keluarga berkas: `/content/drive/MyDrive/ACOS`, `/content/drive/MyDrive/ACOS-ASLI`, dan `/shared-docker/ACOS`. Akibatnya artefak sesi yang sama dapat muncul dengan dua path berbeda (mis. `appsid_05092026_122741` di `ACOS/` vs `ACOS-ASLI/`), dan notebook yang namanya menyebut satu tanggal dapat menunjuk sesi tanggal lain.

---

## 17. Tabel 15 — Putusan per kelompok notebook

| Kelas | Anggota | Aturan pakai |
| --- | --- | --- |
| E2 — dihitung di selnya | `02`, `04`, `01`, `03`, `V4_1_01`, `V4_1_03`, `V4_INDOBERT`, `MI300X 2409`, Colab dasar | Dapat dikutip dengan menyebut sesi + nomor sel + `exec_count` |
| E3 — echo/cache | `V4_1`, `V4_2`, `V4_3`, `V4_1_04` (bagian eval), `V4_2_06`, `run0809` | Kutip sebagai bukti cache, bukan sebagai run baru |
| E1 — output yatim | `UPDATE`, `05`, `V4_INDOBERT copy` | Butuh artefak Drive untuk menopang; jangan dikutip sendiri |
| E0 — nol/dry-run/kerangka | ACOS-BERT (10), Kaggle (2), ASLI/PRO/PRO_Resume/V2/V3, V4_1_02, V4_2_05, GPU_Status, V5.1, V5.2, V5.2.1, V5.3, V5 MI300X, V5_EN | Jangan dikutip sebagai hasil; sebut hanya sebagai rencana/kerangka |

**Rekomendasi pemakaian angka untuk laporan akhir:**

| Klaim | Angka yang dipakai | Sumber | Yang harus dihindari |
| --- | --- | --- | --- |
| Step-1 rest16 | **81,27%** (rentang 80,76–81,27) | `02` sel 13 ec=8 | Mengutip 97,94% sebagai rest16 |
| Step-2 rest16 | **48,24%** (47,68–48,24) | `04` sel 12 ec=6 + Drive 27/08 | Mengutip 47,03% tanpa menyebut tanpa TP/FP/FN |
| Step-1 appsid | **97,94%** (ep8), 97,19% (ep3) | `V4_INDOBERT` sel 46 ec=69 | Menyebut sebagai hasil baru di V4.1–V4.3 |
| Step-2 appsid | **67,86%** (0809) · 67,69% (0901) · 67,16% (0509) | `V4_1_03` sel 19 ec=41 | Menyebut 66,28% sebagai F1 pipeline |
| 15 sub-task | Tabel 10 | `04` sel 12 & MI300X sel 74 | Menggabungkan dua domain dalam satu rata-rata |
| Grid 54 run | **Tidak ada hasil** | `V5.2.1`/`V5.3` sel 35 | Menyebut "54 run" sebagai eksperimen |

---

## 18. Dampak terhadap laporan 036–040

| Laporan | Status | Penyesuaian dari 041 |
| --- | --- | --- |
| 036 (final report) | Sebagian perlu koreksi | Angka 81,27 / 48,24 kini punya jejak sel+ec lengkap; klaim "rest16 gagal" harus dibatasi pada sesi 24/09 & 12/09, bukan seluruh rest16 |
| 037/038 (hasil & evaluasi) | Ditegaskan | Tidak ada notebook yang menaikkan angka di atas 67,86 / 48,24 |
| 039 (survey repo) | Ditegaskan | Statistik 1.748 sel / 13 error / 575 tak jalan tetap berlaku; laporan ini menambah analisis sebab |
| 040 (Drive) | Ditegaskan + dikoreksi | 47,68 dan 78,72/81,93/69,56 di Drive kini punya padanan notebook: 48,24 dan 78,95/82,51/70,11 (selisih ≤0,55) → konsisten, bukan artefak |
| Klaim 66,28% (quadruple appsid) | **Dikoreksi** | Gold 19.528 = 2,17× gold quadruple (9.006); angka ini agregasi lintas-tingkat, bukan F1 pipeline. Gunakan 67,69% |
| Klaim 97,94% Step-1 | **Dikoreksi** | Cache-hit di semua notebook selain `V4_INDOBERT`; hanya sah sebagai riwayat sesi 0509 ep8 |

---

## 19. Keterbatasan dan langkah lanjut

1. **Tidak ada re-eksekusi.** Semua kesimpulan berasal dari output tersimpan. Notebook yang selnya dihapus outputnya tidak dapat diperiksa (mis. `V4_1_02_step1_train`).
2. **`execution_count` dapat dimanipulasi** (sel dijalankan di kernel lain, output ditempel). Karena itu status E2 tetap lebih lemah daripada artefak CSV/JSON yang diunduh dari Drive (Laporan 040).
3. **Tidak semua sel dapat dipetakan ke sesi.** Hanya `UPDATE` yang menyebut nama sesi di kode; pada 44 notebook lain identitas sesi hanya muncul di output (atau tidak sama sekali), sehingga provenance sebagian hanya dapat ditetapkan sampai tingkat berkas.
4. **Langkah lanjut yang disarankan:** (a) menandai seluruh notebook E3/E0 di README agar tidak dikutip; (b) menambah guard yang menghentikan eksekusi ketika gate-1 gagal; (c) membatasi pembentukan pasangan kandidat per kalimat (≈1,5× gold) sebagai pengaman lintas domain; (d) menjalankan ulang `02`/`04` dengan seed berbeda untuk mengukur varians baseline rest16.

---

## Lampiran A — Daftar notebook tanpa sel tereksekusi

- `ACOS-BERT/notebooks/00_ACOS_Master_Pipeline_V1_1_BERT.ipynb` — 20 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_01_setup.ipynb` — 6 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_02_step1_train.ipynb` — 8 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_03_step2_train.ipynb` — 9 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_04_eval_inference.ipynb` — 8 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_1_01_setup.ipynb` — 10 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_1_02_step1_train.ipynb` — 13 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_1_03_step2_train.ipynb` — 14 sel kode, 0 beroutput
- `ACOS-BERT/notebooks/V1_1_04_eval_inference.ipynb` — 13 sel kode, 0 beroutput
- `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb` — 48 sel kode, 0 beroutput
- `ACOS-IndoBERT/notebooks/V4_1_02_step1_train.ipynb` — 11 sel kode, 1 beroutput
- `GPU_Status.ipynb` — 3 sel kode, 0 beroutput
- `kaggle/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb` — 48 sel kode, 0 beroutput
- `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` — 14 sel kode, 0 beroutput
- `notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb` — 42 sel kode, 0 beroutput
- `notebooks/00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb` — 14 sel kode, 10 beroutput
- `notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb` — 44 sel kode, 0 beroutput
- `notebooks/00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb` — 49 sel kode, 0 beroutput
- `notebooks/05_ACOS_Evaluation_and_Interactive_Inference.ipynb` — 14 sel kode, 5 beroutput

## Lampiran B — Reproduksi

```bash
python3 scripts/audit_041_notebooks.py   # -> reports/041_data/*.csv (45 nb, stdlib saja)
python3 scripts/gen_report_041.py        # -> laporan ini + 3 CSV turunan
```

Semua jalur relatif terhadap akar repositori. Tidak ada dependensi pihak ketiga; tidak ada berkas data yang diunduh atau diubah.

