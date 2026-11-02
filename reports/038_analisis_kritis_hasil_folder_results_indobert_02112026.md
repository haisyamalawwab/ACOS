# Survey & Analisis Kritis Folder `ACOS-IndoBERT/results`

> **Tanggal:** 02112026
> **Target survey:** `D:\laragon\www\ACOS-ASLI\ACOS-IndoBERT\results`
> **Cakupan:** 100 folder, 210 berkas, ±11,0 MB
> **Metode:** enumerasi rekursif berkas, parsing 98 `run_result.json` + `run_config.json`, pembacaan seluruh `training_log.csv`/`eval_per_epoch.csv`, verifikasi silang ke `data/Apps-ACOS/_cv_report.json`, `tokenized_data/`, dan modul sumber `acos_id/{experiment_runner,cross_val,guards,checkpoint}.py`
> **Referensi sesi asal:** `docs/0007`–`docs/0010` (eksperimen GPU AMD MI300X, 24092026)

---

## 1. Verdict Utama

**Nol (0) dari 53 run eksperimen cross-validation menghasilkan hasil training yang sah.**

- 100% `run_result.json` yang ada berisi `"status": "ERROR"`.
- Direktori `results/checkpoints/step1_best`, `results/checkpoints/step2_best`, dan `results/csv/` **kosong total**.
- Tidak ada satu pun artefak `md/`, `plots/`, `reports/`, `inference/` dari `result_saver.py` yang terisi.

Kesimpulan operasional: folder `results/` saat ini **bukan gudang hasil eksperimen**, melainkan **gudang log kegagalan** (53 folder run) yang ditambahi **empat artefak pra-pemrosesan yang benar-benar valid** (`_eda/`, `_backbone/`, `_embedding/`, `_gates/`).

---

## 2. Peta Bagian yang Memiliki Isi

### 2.A. Bagian bernilai penuh (lengkap & konsisten) — 4 bagian

| Bagian | Berkas | Isi & Angka Kunci | Status |
|---|---|---|---|
| `_eda/` | `csv/eda_all_samples_annotated.csv` (10,4 MB), `csv/eda_dataset_statistics.csv`, `csv/eda_category_sentiment_counts.csv`, `csv/eda_length_describe.csv`, `plots/01_eda_dataset_distribution.png` (130,9 KB), `plots/02_eda_category_sentiment.png` (243,4 KB), `plots/02b_eda_length_and_implicit_combo.png` (200,8 KB), `plots/02c_eda_category_sentiment_heatmap.png` (221,2 KB) | 92.074 sampel beranotasi penuh (Domain, Split, Text, Aspect, Category, Sentiment, Opinion, Is_Implicit_Aspect, Is_Implicit_Opinion, Text_Length) | ✅ Lengkap, CSV + PNG berpasangan |
| `_backbone/` (nama aktual `2114ab2eb_backbone`) | `backbone_check.csv` | train 60.159 / dev 8.027 / test 7.891 baris — semua `OK`; `pytorch_model.bin` 474,8 MB `OK`; `config.json` & `vocab.txt` `OK` | ✅ 7 baris audit, semua OK |
| `_embedding/` | `embedding_audit.csv` | `vocab_txt_bariss` 30.521 vs `config_vocab_size` 50.000; `hidden_size` 768; `emb_params_jt` 38,4; `unk_disisipkan` 0; `span_bergeser` **25.992** | ⚠️ Berkas lengkap, tapi isinya menandai masalah (lihat §4 anomali #1 dan §6.1) |
| `_gates/` | `gates.csv` | `taksonomi=True`, `vocab=True`, `tokenized_n=6` | ⚠️ Valid tetapi hanya 3 gate; gate set lengkap (`dataset`, `weights`, `overlap`) tidak terekam |

**Statistik dataset yang terekam dan layak dikutip** (domain `appsid` / Apps-ACOS):

| Split | Kalimat | Total Quadruple | Aspek Eksplisit | Aspek Implisit | Opini Eksplisit | Opini Implisit | Sentimen 0 (neg) | 1 (net) | 2 (pos) |
|---|---|---|---|---|---|---|---|---|---|
| train | 60.159 | 72.973 | 51.184 | 21.789 | 43.271 | 29.702 | 36.217 | 8.274 | 28.482 |
| dev | 8.027 | 9.587 | 6.588 | 2.999 | 5.836 | 3.751 | 4.819 | 1.030 | 3.738 |
| test | 7.891 | 9.514 | 6.576 | 2.938 | 5.693 | 3.821 | 4.788 | 1.100 | 3.626 |
| **Total** | **76.077** | **92.074** | **64.348** | **27.726** | **54.800** | **37.274** | **45.824** | **10.404** | **35.846** |

Distribusi panjang teks (satuan kata): mean 8,92; median 7; std 6,96; min 1; p25 4; p75 11; max 79 (n = 92.074).

13 kategori taksonomi, dengan volume sentimen (0/1/2) terbesar: `FEATURES_PRODUCT` (11.178 / 2.304 / 14.212), `TRANSACTION_TRANSFER` (6.822 / 2.040 / 5.890), `APP_PERFORMANCE` (7.714 / 1.096 / 908), `AUTH_ACCESS` (5.192 / 952 / 471). Terkecil: `PROMO_MARKETING` (443 / 124 / 1.255), `SECURITY_FRAUD` (655 / 125 / 1.042). Kelas negatif mendominasi secara global (49,8% dari seluruh quadruple).

### 2.B. Bagian yang ada tetapi rusak — kerangka eksperimen CV

| Kelompok | Jumlah folder | Berkas per folder | Durasi run | Status |
|---|---|---|---|---|
| `cv10fold_fold{1..10}_ep{50,75,100}` gelombang-1 (`1339`–`1342`) | 15 | `run_config.json` + `run_result.json` | 8,2–8,6 s | ❌ ERROR `'list' object has no attribute 'items'` |
| `cv10fold_fold{1..10}_ep{50,75,100}` gelombang-2 (`1401`–`1404`) | 15 | config + result | 8,1–8,7 s | ❌ ERROR, bug identik |
| `cv5fold_fold{1..4}_ep{50,75,100}` gelombang-1 (`1336`–`1337`) | 11 | config + result | 7,4–7,9 s | ❌ ERROR, bug identik |
| `cv5fold_fold{1..4}_ep{50,75,100}` gelombang-2 (`1358`–`1359`) | 11 | config + result | 7,4–7,9 s | ❌ ERROR, bug identik |
| `cv5fold_fold{1..5}` gelombang-3 (`1413`, `1415`, `1416`, `1418`, `1421`, `1422`) | 6 | config + result + `step1/training_log.csv` + `step1/eval_per_epoch.csv` | 88,7–89,9 s | ⚠️ ERROR `'BertForQuadABSA' object has no attribute 'save_pretrained'` — epoch 1 sempat berjalan |
| `cv5fold_fold3_ep75_…_1424` | 1 | **hanya `run_config.json`** + 9 subfolder kosong (`checkpoints`, `csv`, `inference`, `logs`, `md`, `plots`, `reports`, `step1`, `step2`); tanpa `run_result.json` | – | ❌ Sesi terputus di tengah (kemungkinan interupsi manual / kernel restart) |
| `checkpoints/step1_best`, `checkpoints/step2_best` | 2 dir | – | – | ❌ Direktori kosong |
| `csv/` | 1 dir | – | – | ❌ Direktori kosong |

Total folder run CV = **53** (30 cv10fold + 23 cv5fold), dengan 98 berkas JSON status + 12 berkas CSV log epoch.

### 2.C. Bagian yang hilang sama sekali

| Yang hilang | Bukti ketiadaan | Dampak |
|---|---|---|
| 9 run split-ratio (`80:10:10`, `70:15:15`, `60:20:20` × ep50/75/100) | `run_result.json` mencatat `total_runs: 54`, tetapi tidak ada folder `split_*` di `results/` | Grid dimensi "ratio" tidak menghasilkan jejak; perbandingan rasio split tidak mungkin dilakukan |
| `results/experiments/` sebagai induk run | Semua path internal menunjuk `…/results/experiments/…`, tetapi run berada langsung di akar `results/` | Struktur tidak bisa dipetakan balik ke `experiment_runner._unique_run_dir()` |
| `_experiment_progress.json` | Tidak ditemukan di seluruh `ACOS-IndoBERT/` (hanya `_cv_report.json` ×2 dan `build/_gate2_en/report.json` yang ada) | Progres real-time runner tidak pernah ter-write |
| `tokenized_data/_experiment_manifest.json` | Tidak ada; `tokenized_data/` hanya berisi 6 berkas basis + `_build_report_appsid.json` | `prepare_all_data()` tidak pernah menyelesaikan Fase 3 (tokenisasi) |
| Tokenisasi CV (`tokenized_data/cv_5fold/fold_*`, `cv_10fold/`, `split_*/`) | Direktori tidak ada di mesin ini, padahal `run_result.json` mereferensikan `tokenized_data/cv_5fold/fold_1` | Tidak ada satu pun run yang bisa dilanjutkan/diulang dari repo ini |
| Berkas hasil `result_saver.py` (summary MD, confusion plot, per-category metrics, inference demo) | Hanya muncul sebagai folder kosong di run `1424` | Tidak ada artefak yang bisa dipublikasikan dari sisi training |

---

## 3. Analisis Akar Masalah — Dua Kegagalan yang Berbeda

### Bug #1 — `'list' object has no attribute 'items'` (47 run)

- **Waktu gagal:** 7,4–8,7 detik setelah start, **sebelum satu langkah training pun berjalan**.
- **Posisi:** di dalam `train_fn(full_cfg)` yang dipanggil `run_all_experiments()` (`acos_id/experiment_runner.py:278`). Runner itu sendiri sudah benar — ia mengkonstruksi `full_cfg` sebagai `dict` (`{**cfg, "run_idx":…, "tokenized_dir":…, …}`).
- **Diagnosis:** adapter `train_one_run()` di notebook menerima/mengolah `cfg` dalam bentuk **list**, lalu memanggil `.items()` padanya (pola yang sama ada di `result_saver.py:437` `for k, v in cfg.items()` dan `experiment_runner.py:393`). Jadi kesalahan ada di **samping notebook (sel adapter)**, bukan di modul repo.
- **Catatan penting:** kedua gelombang (1336–1342 dan 1358–1404) gagal dengan bug yang **persis sama**, artinya tidak ada perbaikan yang benar-benar diterapkan di antara kedua gelombang tersebut — hanya diulang.

### Bug #2 — `'BertForQuadABSA' object has no attribute 'save_pretrained'` (6 run)

- **Waktu gagal:** 88,7–89,9 detik — pelatihan epoch 1 **selesai**, `training_log.csv` + `eval_per_epoch.csv` tertulis, crash terjadi pada tahap **penyimpanan checkpoint**.
- **Diagnosis:** `BertForQuadABSA` adalah kelas warisan legacy (`modeling.py`) yang **tidak** mewarisi `PreTrainedModel`, sehingga tidak memiliki `save_pretrained()`.
- **Temuan kritis:** modul [`acos_id/checkpoint.py`](../ACOS-IndoBERT/acos_id/checkpoint.py) secara eksplisit dibuka dengan narasi bahwa inilah masalah yang sudah ia selesaikan (prefiks `bert.*`, gate bobot `gate_weights_loaded`). Artinya **perbaikan sudah tersedia di repo, tetapi sel notebook memanggil `model.save_pretrained()` langsung dan mem-bypass adapter tersebut.** Ini kegagalan integrasi, bukan kegagalan desain.
- **Konsistensi:** 6 run ini adalah satu-satunya yang punya jejak epoch; ia gagal tepat sebelum `step1_best`/`step2_best` terisi — menjelaskan mengapa kedua direktori itu kosong.

---

## 4. Temuan Paling Mengkhawatirkan: Metrik 100% Tidak Mungkin Valid

Seluruh 6 `training_log.csv` (satu-satunya data metrik yang ada) memiliki bentuk identik:

```
epoch,loss,precision,recall,f1,tp,fp,fn,vram_gb,vram_pct,duration_sec,samples_per_sec,is_best,timestamp
1,0.081616,100.0,100.0,100.0,71955,0,0,2.012,0.0,0.0,0.0,False,2026-09-27T14:15:21.706602
```

| Run | loss | P / R / F1 | tp | fp | fn | is_best | duration_sec | samples_per_sec | vram_gb | vram_pct |
|---|---|---|---|---|---|---|---|---|---|---|
| `cv5fold_fold1_ep50_…_1413` | 0,081616 | 100/100/100 | 71.955 | 0 | 0 | False | 0,0 | 0,0 | 2,012 | 0,0 |
| `cv5fold_fold1_ep75_…_1421` | 0,084952 | 100/100/100 | 71.955 | 0 | 0 | False | 0,0 | 0,0 | 2,012 | 0,0 |
| `cv5fold_fold2_ep50_…_1415` | 0,070921 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 | 0,0 | 2,018 | 0,0 |
| `cv5fold_fold2_ep75_…_1422` | 0,104647 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 | 0,0 | 2,018 | 0,0 |
| `cv5fold_fold3_ep50_…_1416` | 0,092173 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 | 0,0 | 2,026 | 0,0 |
| `cv5fold_fold4_ep50_…_1418` | 0,071199 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 | 0,0 | 2,028 | 0,0 |

Empat anomali yang saling menguatkan:

1. **`fp = 0` dan `fn = 0` dengan `tp` puluhan ribu.** Tidak ada model nyata yang menghasilkan nol false-positive dan nol false-negative pada 70 ribu kandidat. Ini tanda perbandingan dua himpunan yang **identik dengan dirinya sendiri** (berkas "prediksi" berisi salinan gold). Pola ini persis yang dideteksi parser [`guards.parse_result_txt()`](../ACOS-IndoBERT/acos_id/guards.py) (baris 185–196, penghitungan TP/FP/FN per kunci `teks+span` → `KAT#SENTI`).
2. **`tp` tidak cocok dengan ukuran fold mana pun.** Verifikasi langsung ke `data/Apps-ACOS/cv_5fold/`:

   | Fold | baris train | quad train | baris dev | quad dev | baris test | quad test |
   |---|---|---|---|---|---|---|
   | fold_1 | 54.879 | 66.333 | 6.195 | 7.505 | 15.003 | 18.236 |
   | fold_2 | 54.796 | 66.196 | 6.072 | 7.443 | 15.209 | 18.435 |
   | fold_3 | 54.727 | 66.147 | 6.072 | 7.443 | 15.278 | 18.484 |

   `tp=71.955` (fold 1) ≠ 66.333 dan ≠ 66.333+7.505=73.838; `tp=70.274` (fold 2/3/4) juga tidak punya padanan. Selain itu **fold 2, 3, dan 4 menghasilkan `tp` yang sama persis (70.274) padahal jumlah quad mereka berbeda** (66.196 / 66.147 / 66.140) — bukti bahwa metrik tidak dihitung per-fold.
3. **`is_best = False` pada epoch dengan F1 = 100.** State "model terbaik" tidak pernah di-set → tidak ada checkpoint yang layak disimpan → konsisten dengan `checkpoints/*_best` yang kosong.
4. **`duration_sec = 0,0`, `samples_per_sec = 0,0`, `vram_pct = 0,0`.** Seluruh kolom pengukuran throughput/VRAM tidak terisi, padahal tujuan sesi MI300X (`docs/0007`–`0010`) justru mengukur percepatan training di GPU besar. `vram_gb` (2,012–2,028) satu-satunya kolom yang terisi, dan nilainya hampir konstan antar-run — mengindikasikan pembacaan sekali, bukan per-epoch.

**Aturan tegas:** angka F1 di folder `cv*` **tidak boleh** dimasukkan ke tabel perbandingan, laporan, atau publikasi apa pun. Angkanya adalah artefak bug penghitungan, bukan kinerja model.

### Catatan metodologis tambahan — skema "5-fold" bukan K-fold murni

Dari `data/Apps-ACOS/cv_5fold/_cv_report.json` (`n_splits: 5`, `dev_ratio: 0.1`, `seed: 42`, `total_reviews: 36.821`): tiap fold menghasilkan train 54.879 / dev 6.195 / **test 15.003** baris, dengan `test_reviews` 7.365 vs `dev_reviews` 2.945 vs `train_reviews` 26.511. Artinya ±20% data ditahan sebagai test **di luar** skema fold dan ukurannya tidak proporsional terhadap dev. Klaim desain "tidak ada data leakage" (`docs/0010` §5) perlu **diaudit ulang secara eksplisit**, bukan diterima mentah — dan jika dipertahankan, skema ini sebaiknya dinamai ulang sebagai *stratified hold-out + inner CV*, bukan K-fold.

---

## 5. Problem Sinkronisasi & Struktur Lintas Mesin

1. **Path Linux vs Windows.** Semua `run_dir`/`result_dir`/`tokenized_dir` di JSON beralamat `/shared-docker/ACOS-IndoBERT/…` (mesin GPU ROCm), sedangkan jejak yang tersinkron ke repo ini ada di `D:\laragon\www\ACOS-ASLI\ACOS-IndoBERT\…`. Semua path di dalam JSON karena itu **rusak/putus** jika dibaca di mesin ini — tidak ada normalisasi atau manifest pemetaan.
2. **Penamaan run menyimpang dari runner.** `experiment_runner._unique_run_dir()` menghasilkan `appsid_<ddmmyyyy_hhmm>` (prefiks domain), tetapi folder aktual bernama `cv5fold_fold1_ep50_27092026_1413`. Selain itu `ts` dirender dengan format `%d%m%Y_%H%M` **tanpa padding nol** pada jam, sehingga `9` pagi dan `10` pagi berpotensi menghasilkan tabrakan nama yang ditangani oleh `_01/_02` — pola ini tidak terlihat dipakai di data.
3. **Kesenjangan fase data.** Fase **build TSV berhasil dan tersinkron**: `data/Apps-ACOS/` berisi `cv_5fold/fold_1..5`, `cv_10fold/`, `split_602020/701515/801010`, masing-masing dengan `appsid_quad_{train,dev,test}.tsv` + `id_to_split.json` + `_cv_report.json`. Fase **tokenisasi CV tidak tersinkron** — `tokenized_data/` hanya 6 berkas basis, dan `gates.csv` mencatat `tokenized_n = 6`.
4. **Rerun tanpa perubahan.** Dua gelombang CV10-fold (1339–1342 dan 1401–1404) dan dua gelombang CV5-fold (1336–1337, 1358–1359) gagal dengan bug identik dalam rentang 25 menit. Ini mengindikasikan siklus "restart kernel → jalankan ulang sel yang sama" tanpa perbaikan akar masalah.

---

## 6. Rekomendasi Bertingkat

### 6.1 Blocking — wajib sebelum eksperimen diulang

| # | Tindakan | Titik integrasi |
|---|---|---|
| 1 | Perbaiki bentuk `cfg` pada sel adapter `train_one_run()` menjadi `dict`; tambahkan assert dini `isinstance(cfg, dict)` di awal fungsi | Notebook V4 MI300X, sel adapter |
| 2 | Ganti seluruh pemanggilan `model.save_pretrained(...)` dengan API `acos_id/checkpoint.py`; aktifkan `gate_weights_loaded()` sebagai gerbang pasca-simpan agar key `bert.*` terverifikasi dengan `torch.equal` | Sel step1 & step2 training |
| 3 | Tambahkan guard anti-metrik-degenerat: jika `fp == 0 and fn == 0`, atau `f1 == 100.0` pada epoch pertama → **raise**, jangan tulis log. Metrik 100% harus menjadi alarm, bukan hasil | Loop evaluasi Step-1 |
| 4 | Isi `duration_sec`, `samples_per_sec`, `vram_pct` per epoch. Tanpa ini tujuan pengukuran GPU MI300X tidak tercapai | Pencatatan `training_log.csv` |
| 5 | Paksa `is_best=True` pada epoch pertama yang valid, atau set ambang minimum sebelum pencatatan "best" | State manajemen checkpoint |

### 6.2 Struktur & reproducibility

6. Bakukan lokasi run ke `results/experiments/<domain>_<ddmmyyyy_hhmm>/` sesuai `_unique_run_dir()`, lalu pindahkan 53 folder CV yang ada ke bawah `results/experiments/` (atau perbarui runner — pilih satu, jangan biarkan dua konvensi hidup).
7. Jalankan ulang `prepare_all_data()` sampai tuntas sehingga `tokenized_data/_experiment_manifest.json` dan `results/experiments/_experiment_progress.json` benar-benar ter-write; keduanya adalah satu-satunya jejak yang memungkinkan audit grid 54 run.
8. Sinkronkan `tokenized_data/cv_5fold/fold_*`, `cv_10fold/*`, `split_*/` dari mesin GPU — tanpa itu tidak ada run yang bisa dilanjutkan di repo ini.
9. Tambahkan normalisasi/manifest path (mis. `path_map.json`: `/shared-docker/ACOS-IndoBERT` → root repo lokal) sehingga JSON dari mesin GPU bisa dibaca lintas mesin.
10. Lengkapi `_gates/gates.csv` dengan gate `dataset`, `weights`, `tumpang_tindih_review_id` (sudah ada di `selftest.py`) — saat ini hanya 3 gate yang terekam.

### 6.3 Metodologi & pelaporan

11. Audit dan dokumentasikan definisi split CV (test 15.003 baris di skema "5-fold"); pertimbangkan rebuild sebagai K-fold murni dengan test-set global terpisah.
12. Arsipkan 47 run Bug #1 (tanpa isi epoch) ke `results/_archive_failed/` sebagai bukti, dan bersihkan 9 subfolder kosong pada run `1424`.
13. Satu-satunya klaim yang layak dikutip ke laporan saat ini: **`_eda/`, `_backbone/`, `_embedding/`, `_gates/`** — seluruh angka training di folder `cv*` tidak dapat digunakan.

---

## 7. Lampiran — Ringkasan Numerik Folder

| Metrik | Nilai |
|---|---|
| Total folder | 100 |
| Total berkas | 210 |
| Ukuran total | ±11,0 MB (10,4 MB di antaranya = `eda_all_samples_annotated.csv`) |
| Berkas `run_result.json` | 53 — status `ERROR` 53, status `OK` **0** |
| Berkas `run_config.json` | 54 (termasuk run `1424` tanpa result) |
| Berkas `training_log.csv` / `eval_per_epoch.csv` | 6 / 6, masing-masing hanya 1 baris epoch |
| Run dengan data epoch | 6 dari 53 (11,3%) |
| Direktori kosong | `checkpoints/step1_best`, `checkpoints/step2_best`, `csv/`, + 9 subfolder run `1424`, + `checkpoints/step{1,2}_best` internal run `1424` |
| Artefak valid (pra-pemrosesan) | 4 bagian: `_eda/`, `_backbone/`, `_embedding/`, `_gates/` |
| Gap grid eksperimen | 9 run split-ratio tidak berjejak; 53 folder run = hanya dimensi CV |

---

*Disusun dari inspeksi langsung terhadap `ACOS-IndoBERT/results`, `ACOS-IndoBERT/data/Apps-ACOS`, `ACOS-IndoBERT/tokenized_data`, dan modul `ACOS-IndoBERT/acos_id`.*
