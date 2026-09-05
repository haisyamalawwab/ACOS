# Dokumentasi per Sel — `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`

Tanggal: 2026-09-05  
Sumber: notebook versi Google Drive (folder `12kRSVe-l88iZY1oix0CXSqTZ2308KzQx`, berkas `1J_ZzO0H5m_2Z6Nf1F6thTMIOU__iJ2l-`), dibaca statis, tidak dieksekusi.  
Jumlah sel: **80** (48 kode, 32 markdown).  
Pola nama berkas: `0xx_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cellNN_DDMMYYYY.md` — `0xx` nomor urut serial, `NN` nomor sel (1-based), tanggal `05092026`.

> Catatan: notebook di repo (`ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`) dan generator `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` **sudah 80 sel**, termasuk sel 2c (dua root + `acos_id.upstream`), 4c (adapter IndoBERT), 4d (gerbang data), dan 5d2 (Gate 1). Dokumentasi ini mengikuti versi itu. Ketujuh modul `acos_id` (`taxonomy`, `build_acos`, `tokenize_data`, `checkpoint`, `selftest`, `eda`, `upstream`) ada di paket.

## Peta alur

```
Sel 03-05  Env: Drive mount, pip, impor, GPU
Sel 07     1b  step_stage / require_vars / patch metrik  (wajib tiap restart kernel)
Sel 09-10  Path root + impor colab_utils
Sel 12     2c  indo_root (tulis) & acos_root (baca) + paket acos_id  (V4, wajib tiap restart)
Sel 14-21  Konfigurasi: DOMAIN=appsid, BACKBONE=indobert, sesi, manifest, state
Sel 23-26  EDA (acos_id.eda untuk domain Indonesia)
Sel 28     4b  audit folder
Sel 30     4c  unduh + rekey prefiks bert. checkpoint IndoBERT        (V4)
Sel 32     4d  5 gate torch-free: taxonomy/dataset/acos_build/tokenized/gate2_english (V4)
Sel 34-47  Step 1  5a init | 5b cache | 5c eval data | 5d model | 5d2 Gate 1 (V4) | 5e training | 5f laporan
Sel 49-54  State saver / recovery / ensure_objects
Sel 56-58  Jembatan 7a pasangan kandidat | 7b distribusi
Sel 60-70  Step 2  8a init | 8b cache | 8c eval data | 8d model | 8e training | 8f laporan
Sel 72-74  Evaluasi final 9a | 9b tabel & plot
Sel 76-78  Inferensi live
Sel 80     Audit artefak
```

## Daftar sel

| Serial | Sel | Tipe | Bagian | Judul | Berkas |
|---|---|---|---|---|---|
| 001 | 01 | markdown | 0. Pembuka | Judul & Gambaran Umum Notebook (V2 → V4 IndoBERT) | [001_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell01_05092026.md](001_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell01_05092026.md) |
| 002 | 02 | markdown | 1. Environment Setup | Heading: 1. Environment Setup, Google Drive Mounting & GPU Diagnostics | [002_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell02_05092026.md](002_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell02_05092026.md) |
| 003 | 03 | code | 1. Environment Setup | Mount Google Drive & Instalasi Dependensi | [003_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell03_05092026.md](003_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell03_05092026.md) |
| 004 | 04 | code | 1. Environment Setup | Impor Pustaka Standar & Ilmiah | [004_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell04_05092026.md](004_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell04_05092026.md) |
| 005 | 05 | code | 1. Environment Setup | Diagnostik & Optimasi GPU | [005_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell05_05092026.md](005_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell05_05092026.md) |
| 006 | 06 | markdown | 1b. Pelacak Progres | Heading: 1b. Pelacak Progres Bertahap (`step_stage`) | [006_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell06_05092026.md](006_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell06_05092026.md) |
| 007 | 07 | code | 1b. Pelacak Progres | Definisi `step_stage`, `require_vars`, Patch Metrik & Helper Tabel | [007_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell07_05092026.md](007_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell07_05092026.md) |
| 008 | 08 | markdown | 2. Path Dinamis | Heading: 2. Dynamic Directory Navigation & Path Initialization | [008_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell08_05092026.md](008_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell08_05092026.md) |
| 009 | 09 | code | 2. Path Dinamis | Deteksi Root Proyek (Drive / Colab / Lokal) & Auto-Clone Repo | [009_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell09_05092026.md](009_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell09_05092026.md) |
| 010 | 10 | code | 2. Path Dinamis | Impor `colab_utils` yang Lengkap & Robust | [010_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell10_05092026.md](010_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell10_05092026.md) |
| 011 | 11 | markdown | 2c. Dua Root (baru di V4) | Heading: 2c. Dua Root & Paket `acos_id/` | [011_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell11_05092026.md](011_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell11_05092026.md) |
| 012 | 12 | code | 2c. Dua Root (baru di V4) | Resolusi `indo_root`/`acos_root` & Impor Paket `acos_id` | [012_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell12_05092026.md](012_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell12_05092026.md) |
| 013 | 13 | markdown | 3. Konfigurasi | Heading: 3. Master Pipeline Parameters, BERT Caching & Session Manifest | [013_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell13_05092026.md](013_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell13_05092026.md) |
| 014 | 14 | code | 3. Konfigurasi | Konfigurasi V4: DOMAIN, BACKBONE, Hyperparameter & Seeding | [014_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell14_05092026.md](014_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell14_05092026.md) |
| 015 | 15 | code | 3. Konfigurasi | Helper `session_dirs_from_root()` | [015_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell15_05092026.md](015_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell15_05092026.md) |
| 016 | 16 | code | 3. Konfigurasi | Helper `session_cache_score()` | [016_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell16_05092026.md](016_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell16_05092026.md) |
| 017 | 17 | code | 3. Konfigurasi | Resume/Buat Sesi, Verifikasi Izin Simpan & Path Backbone | [017_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell17_05092026.md](017_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell17_05092026.md) |
| 018 | 18 | code | 3. Konfigurasi | Inisialisasi `MarkdownReport` | [018_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell18_05092026.md](018_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell18_05092026.md) |
| 019 | 19 | code | 3. Konfigurasi | Helper `update_mcp_manifest()` (MCP Session Manifest) | [019_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell19_05092026.md](019_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell19_05092026.md) |
| 020 | 20 | code | 3. Konfigurasi | Helper `save_pipeline_state()` (pipeline_state.pkl) | [020_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell20_05092026.md](020_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell20_05092026.md) |
| 021 | 21 | code | 3. Konfigurasi | Helper `auto_find_file()`, Manifest INITIALIZED & Tabel Konfigurasi | [021_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell21_05092026.md](021_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell21_05092026.md) |
| 022 | 22 | markdown | 4. EDA | Heading: 4. Exploratory Data Analysis (EDA) & Publication Visualizations | [022_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell22_05092026.md](022_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell22_05092026.md) |
| 023 | 23 | code | 4. EDA | Path Artefak EDA | [023_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell23_05092026.md](023_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell23_05092026.md) |
| 024 | 24 | code | 4. EDA | Eksekusi EDA (Cache Memori → Cache Disk → acos_id.eda / colab_utils) | [024_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell24_05092026.md](024_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell24_05092026.md) |
| 025 | 25 | code | 4. EDA | Tabel Statistik, Ringkasan EDA & Tampilan Plot | [025_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell25_05092026.md](025_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell25_05092026.md) |
| 026 | 26 | code | 4. EDA | Manifest `EDA_COMPLETED` & Simpan State | [026_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell26_05092026.md](026_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell26_05092026.md) |
| 027 | 27 | markdown | 4b. Diagnostik Drive | Heading: 4b. Diagnostik Lokasi Dataset & Tokenized Data | [027_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell27_05092026.md](027_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell27_05092026.md) |
| 028 | 28 | code | 4b. Diagnostik Drive | Audit Struktur Folder Drive/Dataset/Cache/Sesi | [028_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell28_05092026.md](028_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell28_05092026.md) |
| 029 | 29 | markdown | 4c. Adapter IndoBERT (baru di V4) | Heading: 4c. Adapter Checkpoint IndoBERT | [029_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell29_05092026.md](029_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell29_05092026.md) |
| 030 | 30 | code | 4c. Adapter IndoBERT (baru di V4) | Unduh, Rekey Prefiks `bert.` & Laporan Vocab IndoBERT | [030_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell30_05092026.md](030_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell30_05092026.md) |
| 031 | 31 | markdown | 4d. Gerbang Data (baru di V4) | Heading: 4d. Gerbang Data Indonesia (wajib sebelum training) | [031_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell31_05092026.md](031_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell31_05092026.md) |
| 032 | 32 | code | 4d. Gerbang Data (baru di V4) | Jalankan 5 Gate Torch-Free & Ekspor Tabel Gerbang | [032_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell32_05092026.md](032_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell32_05092026.md) |
| 033 | 33 | markdown | 5. Step 1 | Heading: 5. Step 1 — Aspect & Opinion Co-Extraction (BERT-CRF) | [033_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell33_05092026.md](033_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell33_05092026.md) |
| 034 | 34 | code | 5. Step 1 | Impor Modul Upstream untuk Step 1 | [034_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell34_05092026.md](034_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell34_05092026.md) |
| 035 | 35 | code | 5. Step 1 | 5a. Inisialisasi Step 1: Tokenizer, Patch Metrik, Taksonomi ID, Label & Path | [035_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell35_05092026.md](035_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell35_05092026.md) |
| 036 | 36 | markdown | 5. Step 1 | Heading: 5b. Deteksi Cache Step 1 | [036_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell36_05092026.md](036_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell36_05092026.md) |
| 037 | 37 | code | 5. Step 1 | 5b. Deteksi Cache Step 1 (Sesi Aktif → Sesi Lama) | [037_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell37_05092026.md](037_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell37_05092026.md) |
| 038 | 38 | markdown | 5. Step 1 | Heading: 5c. Data Evaluasi & Ground Truth | [038_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell38_05092026.md](038_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell38_05092026.md) |
| 039 | 39 | code | 5. Step 1 | 5c. Bangun `eval_loader_1` & `eval_gold_1` dari Test Set | [039_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell39_05092026.md](039_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell39_05092026.md) |
| 040 | 40 | markdown | 5. Step 1 | Heading: 5d. Model, Data Training & Optimizer | [040_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell40_05092026.md](040_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell40_05092026.md) |
| 041 | 41 | code | 5. Step 1 | 5d. Instansiasi `BertForQuadABSA`, Train Loader & `BertAdam` | [041_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell41_05092026.md](041_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell41_05092026.md) |
| 042 | 42 | markdown | 5d2. Gate 1 (baru di V4) | Heading: 5d2. Gate 1 — Bobot Encoder Benar-Benar Termuat | [042_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell42_05092026.md](042_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell42_05092026.md) |
| 043 | 43 | code | 5d2. Gate 1 (baru di V4) | 5d2. Verifikasi Numerik Bobot IndoBERT vs Checkpoint | [043_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell43_05092026.md](043_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell43_05092026.md) |
| 044 | 44 | markdown | 5. Step 1 | Heading: 5e. Loop Training Step 1 | [044_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell44_05092026.md](044_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell44_05092026.md) |
| 045 | 45 | code | 5. Step 1 | 5e. Training BERT-CRF per Epoch + Checkpoint Terbaik + Ringkasan Run | [045_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell45_05092026.md](045_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell45_05092026.md) |
| 046 | 46 | markdown | 5. Step 1 | Heading: 5f. Plot, Tabel & Penyimpanan State Step 1 | [046_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell46_05092026.md](046_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell46_05092026.md) |
| 047 | 47 | code | 5. Step 1 | 5f. Plot Kurva, Tabel `master_03`, Manifest & State Step 1 | [047_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell47_05092026.md](047_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell47_05092026.md) |
| 048 | 48 | markdown | 6. State & Recovery | Heading: 6. Smart State Checkpoint Saver (`pipeline_state.pkl`) | [048_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell48_05092026.md](048_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell48_05092026.md) |
| 049 | 49 | code | 6. State & Recovery | Simpan State Pipeline Eksplisit | [049_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell49_05092026.md](049_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell49_05092026.md) |
| 050 | 50 | markdown | 6. State & Recovery | Heading: 6b. Smart State Recovery (Gunakan Jika Kernel Reconnect / Restart) | [050_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell50_05092026.md](050_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell50_05092026.md) |
| 051 | 51 | code | 6. State & Recovery | Helper `auto_find_latest_state()` | [051_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell51_05092026.md](051_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell51_05092026.md) |
| 052 | 52 | code | 6. State & Recovery | Pulihkan Konfigurasi & Artefak Runtime dari `pipeline_state.pkl` | [052_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell52_05092026.md](052_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell52_05092026.md) |
| 053 | 53 | markdown | 6. State & Recovery | Heading: 6c. Jaminan Objek Runtime (Fallback Load Otomatis) | [053_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell53_05092026.md](053_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell53_05092026.md) |
| 054 | 54 | code | 6. State & Recovery | Definisi & Eksekusi `ensure_objects()` | [054_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell54_05092026.md](054_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell54_05092026.md) |
| 055 | 55 | markdown | 7. Jembatan Pasangan | Heading: 7. Jembatan Pasangan Kandidat (Step 1 → Step 2) / 7a | [055_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell55_05092026.md](055_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell55_05092026.md) |
| 056 | 56 | code | 7. Jembatan Pasangan | 7a. Pembentukan / Pemuatan Pasangan Kandidat | [056_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell56_05092026.md](056_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell56_05092026.md) |
| 057 | 57 | markdown | 7. Jembatan Pasangan | Heading: 7b. Distribusi Tipe Pasangan | [057_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell57_05092026.md](057_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell57_05092026.md) |
| 058 | 58 | code | 7. Jembatan Pasangan | 7b. Tabel Tipe Pasangan, Plot Batang, Manifest & State | [058_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell58_05092026.md](058_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell58_05092026.md) |
| 059 | 59 | markdown | 8. Step 2 | Heading: 8. Step 2 — Klasifikasi Category & Sentiment (Bertahap) / 8a | [059_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell59_05092026.md](059_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell59_05092026.md) |
| 060 | 60 | code | 8. Step 2 | 8a. Inisialisasi Step 2: Patch Tokenizer OOV, Patch Metrik, Label & Path | [060_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell60_05092026.md](060_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell60_05092026.md) |
| 061 | 61 | markdown | 8. Step 2 | Heading: 8b. Deteksi Cache Step 2 | [061_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell61_05092026.md](061_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell61_05092026.md) |
| 062 | 62 | code | 8. Step 2 | 8b. Deteksi Cache Step 2 (Sesi Aktif → Sesi Lama) | [062_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell62_05092026.md](062_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell62_05092026.md) |
| 063 | 63 | markdown | 8. Step 2 | Heading: 8c. Data Evaluasi Pasangan & Gold Step 2 | [063_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell63_05092026.md](063_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell63_05092026.md) |
| 064 | 64 | code | 8. Step 2 | 8c. Bangun `eval_loader_2` & `eval_gold_2` | [064_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell64_05092026.md](064_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell64_05092026.md) |
| 065 | 65 | markdown | 8. Step 2 | Heading: 8d. Model, Data Training & Optimizer Step 2 | [065_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell65_05092026.md](065_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell65_05092026.md) |
| 066 | 66 | code | 8. Step 2 | 8d. Instansiasi `CategorySentiClassification`, Train Loader & `BertAdam` | [066_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell66_05092026.md](066_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell66_05092026.md) |
| 067 | 67 | markdown | 8. Step 2 | Heading: 8e. Loop Training Step 2 | [067_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell67_05092026.md](067_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell67_05092026.md) |
| 068 | 68 | code | 8. Step 2 | 8e. Training Category-Sentiment per Epoch + Checkpoint + Ringkasan Run | [068_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell68_05092026.md](068_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell68_05092026.md) |
| 069 | 69 | markdown | 8. Step 2 | Heading: 8f. Plot, Tabel & State Step 2 | [069_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell69_05092026.md](069_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell69_05092026.md) |
| 070 | 70 | code | 8. Step 2 | 8f. Plot Kurva, Tabel `master_06`, Manifest & State Step 2 | [070_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell70_05092026.md](070_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell70_05092026.md) |
| 071 | 71 | markdown | 9. Evaluasi Final | Heading: 9. Evaluasi Final & Benchmark Sub-Task / 9a | [071_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell71_05092026.md](071_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell71_05092026.md) |
| 072 | 72 | code | 9. Evaluasi Final | 9a. Evaluasi Quadruple Final dengan Checkpoint Terbaik + 15 Sub-Task | [072_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell72_05092026.md](072_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell72_05092026.md) |
| 073 | 73 | markdown | 9. Evaluasi Final | Heading: 9b. Tabel & Plot Benchmark | [073_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell73_05092026.md](073_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell73_05092026.md) |
| 074 | 74 | code | 9. Evaluasi Final | 9b. Tabel `master_07/08/09`, Plot Sub-Task, Manifest & State | [074_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell74_05092026.md](074_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell74_05092026.md) |
| 075 | 75 | markdown | 10. Inferensi Live | Heading: 10. Live Interactive Inference Demo pada Teks Ulasan Bebas | [075_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell75_05092026.md](075_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell75_05092026.md) |
| 076 | 76 | code | 10. Inferensi Live | Persiapan Inferensi: `ensure_objects()` & Impor Kelas Model | [076_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell76_05092026.md](076_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell76_05092026.md) |
| 077 | 77 | code | 10. Inferensi Live | Muat Model Step 1 & Step 2 Terbaik + Helper `_spans_dari_tag()` | [077_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell77_05092026.md](077_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell77_05092026.md) |
| 078 | 78 | code | 10. Inferensi Live | `analyze_review_quadruples()` + Contoh Inferensi & Ekspor `master_10` | [078_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell78_05092026.md](078_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell78_05092026.md) |
| 079 | 79 | markdown | 11. Audit Artefak | Heading: 11. Ringkasan Seluruh Artefak & Finalisasi Sesi | [079_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell79_05092026.md](079_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell79_05092026.md) |
| 080 | 80 | code | 11. Audit Artefak | Audit Akhir Artefak Sesi (Drive/Lokal) | [080_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell80_05092026.md](080_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell80_05092026.md) |
