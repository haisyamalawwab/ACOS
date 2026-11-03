# Indexing Hasil `ACOS-IndoBERT/results` → Perencanaan EDA & Ablasi

> **Tanggal:** 03112026
> **Sumber data:** `ACOS-IndoBERT/results/` (94 folder run), `ACOS-IndoBERT/data/Apps-ACOS/` (18 partisi), `ACOS-IndoBERT/tokenized_data/`, `ACOS-IndoBERT/acos_id/`
> **Artefak indeks yang dihasilkan:**
> `results/_index/run_index.csv` (94 baris), `results/_index/data_partition_index.csv` (19 baris), `results/_index/grid_coverage.csv` (89 baris)
> **Generator:** `python scripts/index_acos_results.py` (read-only terhadap hasil; dapat dijalankan ulang kapan saja)
> **Prasyarat baca:** `reports/038_analisis_kritis_hasil_folder_results_indobert_02112026.md`

---

## 1. Ringkasan Indeks — Apa yang Sebenarnya Ada

| Objek | Jumlah | Temuan kunci |
|---|---|---|
| Folder run CV | **94** (bukan 53 — lihat §6 koreksi) | cv10fold 60, cv5fold 34 |
| Status `ERROR` | 93 (98,9%) | Bug #1 `'list' object has no attribute 'items'` = **87**; Bug #2 `save_pretrained` = **6** |
| Status tanpa `run_result.json` | 1 | `cv5fold_fold3_ep75_…_1424`, 9 subfolder kosong |
| Status `OK` | **0** | Tidak ada satu pun hasil training yang sah |
| Sel grid CV yang **pernah dicoba** | 44 / 45 | Hanya `cv5fold` ep75 fold_5 yang tak pernah disentuh |
| Sel grid CV yang **selesai dengan metrik valid** | **0 / 45** | — |
| Sel grid split-ratio yang pernah dicoba | **0 / 9** | `run_idx` 1–9 tidak muncul sama sekali |
| Percobaan per sel grid | min 0, maks 3, modus 2 | Grid di-*rerun* 2–3× tanpa perubahan kode |
| Partisi TSV siap pakai di disk | 18 (5 + 10 + 3 + base) | Semua ada, semua konsisten dengan `_cv_report.json` |
| Partisi yang **sudah tertokenisasi & tersinkron lokal** | **1 / 19** (hanya `base`) | Ini adalah satu-satunya *root cause* operasional yang memblokir semuanya |
| Backend/AMP/seed di semua 94 run | identik: `rocm` / `bfloat16` / `42` | Tidak ada satu pun dimensi variasi hardware atau stokastik yang ter-manipulasi |

**Kesimpulan indexing:** eksperimen gagal bukan hanya karena bug kode, tapi karena **runtunan fase terputus di tokenisasi**. Build TSV selesai 18 partisi, tokenisasi hanya selesai untuk partisi basis. 94 run kemudian dijalankan terhadap direktori tokenisasi yang tidak ada.

---

## 2. Indeks Run (`run_index.csv`)

### 2.1 Skema kolom

`dir_name, family, n_folds, fold, epochs, wave_ts, run_id, run_idx, total_runs, status, error, duration_sec, backend, amp, amp_dtype, seed, has_config, has_result, training_log_count, eval_log_count, n_files, n_empty_subdirs, referenced_tokenized_dir`

### 2.2 Distribusi menurut `run_idx` (nomor sel grid, bukan nomor percobaan)

| Keluarga | `run_idx` teramati | Cakupan | Tafsir |
|---|---|---|---|
| split-ratio | — (kosong) | **1–9 tidak ada** | Grid mode `ratio` tidak pernah dieksekusi |
| cv5fold | 10–24, minus 19 | 14 dari 15 sel | `run_idx 19` = ep75 fold_5 → tidak pernah dijalankan |
| cv10fold | 25–54 (lengkap) | 30 dari 30 sel | Grid penuh dicoba, 2× tiap sel |

`total_runs` = 54 di semua berkas → grid yang direncanakan memang 9 + 15 + 30.

### 2.3 Gelombang eksekusi (19 stempel waktu berbeda)

| Gelombang | Rentang menit | Jumlah folder | Bug |
|---|---|---|---|
| W1 | `1336`–`1342` | 29 | Bug #1 (gagal 7,4–8,6 s) |
| W2 | `1358`–`1404` | 29 | Bug #1 (identik, tidak ada perbaikan di antara keduanya) |
| W3 | `1413`–`1424` | 7 (lengkap 6 + 1 terputus) | Bug #2 (89 s; `training_log.csv` + `eval_per_epoch.csv` tertulis) |
| Sisanya | tersebar | — | `1424` tidak punya `run_result.json` |

### 2.4 Satu-satunya data metrik yang ada (6 run W3)

| Run | `run_idx` | loss ep1 | P/R/F1 | tp | fp | fn | is_best | dur/sps/vram_pct |
|---|---|---|---|---|---|---|---|---|
| `cv5fold_fold1_ep50_…_1413` | 10 | 0,0816 | 100/100/100 | 71.955 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |
| `cv5fold_fold2_ep50_…_1415` | 11 | 0,0709 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |
| `cv5fold_fold3_ep50_…_1416` | 12 | 0,0922 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |
| `cv5fold_fold4_ep50_…_1418` | 13 | 0,0712 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |
| `cv5fold_fold1_ep75_…_1421` | 15 | 0,0850 | 100/100/100 | 71.955 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |
| `cv5fold_fold2_ep75_…_1422` | 16 | 0,1046 | 100/100/100 | 70.274 | 0 | 0 | False | 0,0 / 0,0 / 0,0 |

Nilai `tp` **tidak** cocok dengan jumlah quad train, train+dev, maupun dev fold mana pun, dan konstan antar-fold yang ukurannya berbeda → metrik degenerat (lihat `reports/038` §4). **Angka ini tidak dipakai sebagai input EDA maupun ablasi.**

---

## 3. Indeks Partisi Data (`data_partition_index.csv`)

### 3.1 Tabel lengkap (baris = klausa, quad = quadruple)

| Keluarga | Partisi | train b | train q | dev b | dev q | test b | test q | Σ quad | train/Σ | `id_to_split` | tokenized lokal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | `base_79_11_10` | 60.159 | 72.973 | 8.027 | 9.587 | 7.891 | 9.514 | 92.074 | 79,25% | ❌ | ✅ |
| ratio | `split_801010` (80/10/10) | 60.806 | 73.645 | 7.750 | 9.305 | 7.521 | 9.124 | 92.073 | 80,0% | ❌ | ❌ |
| ratio | `split_701515` (70/15/15) | 53.120 | 64.358 | 11.502 | 13.869 | 11.455 | 13.847 | 92.074 | 69,9% | ❌ | ❌ |
| ratio | `split_602020` (60/20/20) | 45.488 | 55.152 | 15.318 | 18.493 | 15.271 | 18.429 | 92.074 | 59,9% | ❌ | ❌ |
| cv5 | fold_1…fold_5 (train q) | 54.879→54.735 | 66.333→66.203 | 6.195/6.072 | 7.505/7.443 | 15.003→15.270 | 18.236→18.428 | 92.074 | 72,05% | ✅ | ❌ |
| cv10 | fold_1…fold_10 (train q) | 61.816→61.763 | 74.744→74.628 | 6.722/6.794 | 8.092/8.323 | 7.539→7.520 | 9.238→9.123 | 92.074 | 81,17% | ✅ | ❌ |

Seluruh 18 partisi **sah dan cocok 1:1** dengan `_cv_report.json` / `_build_report_*.json` (diverifikasi ulang baris-per-baris, 0 selisih).

### 3.2 Temuan struktural paling penting: cv5 vs cv10 bukan dua perlakuan berbeda

Inspeksi `id_to_split.json` (36.821 review, **0% tumpang tindih train∩dev∩test**, union = 100% review → klaim anti-leakage di `docs/0010` **tervalidasi**):

| | CV-5 per fold | CV-10 per fold |
|---|---|---|
| train | 26.511 review (72,0%) | 29.825 review (81,0%) |
| dev | 2.945 review (8,0%) | 3.313 review (9,0%) |
| **test** | **7.365 review (20,0%)** | **3.683 review (10,0%)** |

Artinya:

1. Keduanya adalah **satu skema yang sama** (satu hold-out besar + irisan dev) dengan **jumlah rotasi lipatan berbeda** — bukan "5-fold vs 10-fold" yang komparabel secara statistik.
2. **Volume data latih berbeda ~9 poin persentase (72% vs 81%)**, jadi perbandingan apa pun antara cv5 dan cv10 **terconfound oleh ukuran data latih**. Ini harus dinetaskan sebelum ablasi apa pun (lihat §5.2).
3. Lipatan-lipatan dalam satu keluarga **saling lepas** — gabungan test tiap keluarga = seluruh korpus. Jadi cv10 adalah desain yang lebih efisien (test coverage penuh), cv5 hanya menguji 20% korpus ×5.

### 3.3 Kesenjangan yang harus ditutup sebelum eksperimen

| Partisi | Berkas yang dibutuhkan per partisi | Status lokal |
|---|---|---|
| 15 partisi CV (5 + 10) | `appsid_{train,dev,test}_{quad_bert,pair}.tsv` = 6 berkas | ❌ 0 dari 15 |
| 3 partisi ratio | 6 berkas | ❌ 0 dari 3 |
| base | 6 berkas | ✅ |
| Manifest | `tokenized_data/_experiment_manifest.json` | ❌ |
| Progres | `results/experiments/_experiment_progress.json` | ❌ |

Total tokenisasi yang tertunda: **18 partisi × 3 split × 2 format**.

---

## 4. Perencanaan EDA

EDA saat ini hanya **satu tingkat** (korpus global, 4 CSV + 4 PNG di `results/_eda/`). Indeks di atas memungkinkan naik ke empat tingkat. Setiap item di bawah punya *input file* konkret dan bisa dikerjakan **sekarang, tanpa menunggu training**.

### Tingkat 1 — Validasi global (sudah ada, perlu ditindaklanjuti)

| ID | Item | Input | Tindakan |
|---|---|---|---|
| E1.1 | Distribusi kategori × sentimen (13×3) | `_eda/csv/eda_category_sentiment_counts.csv` | Identifikasi sel kelas minoritas: `PROMO_MARKETING` net=124, `SECURITY_FRAUD` net=125, `NOTIFICATION_INFO` net=490 → kandidat re-weighting atau penggabungan kelas |
| E1.2 | Statistik panjang teks | `eda_length_describe.csv` (mean 8,92; p75 11; max 79) | Verifikasi `MAX_LEN` pipeline vs e95; teks pendek → risiko span collapse |
| E1.3 | Rasio eksplisit/implisit | `eda_dataset_statistics.csv` (aspek 71/29, opini 60/40) | Opini implisit 40% = beban besar Step-1; wajib jadi dimensi ablasi (A6) |
| E1.4 | **Tindak lanjut `embedding_audit.csv`** | `results/_embedding/` | `span_bergeser = 25.992` (28% quad) dan `vocab.txt` 30.521 vs `config` 50.000 **belum pernah dijelaskan atau diperbaiki**. Blokir: jangan jalankan ablasi sampai penyebab (vocab BERT-uncased vs IndoBERT) tuntas |

### Tingkat 2 — EDA per partisi (baru, dimungkinkan oleh indeks)

| ID | Item | Input | Output |
|---|---|---|---|
| E2.1 | Heatmap 13 kategori × 3 sentimen **per partisi** (18 partisi × 3 split) | `data/Apps-ACOS/**/appsid_quad_*.tsv` | Matriks 54 sel; deteksi partisi yang rusak stratifikasinya |
| E2.2 | **Tes χ² kesetaraan** antar partisi | hasil E2.1 | Bukti formal bahwa `split_*` dan `cv_*` punya distribusi sama; jika tidak, ablasi rasio tidak valid |
| E2.3 | Kurva konvergensi komposisi vs ukuran partisi | `train_share_of_fold` (59,9%→81,2%) | Menentukan berapa besar efek ukuran data yang harus dipisahkan dari efek epoch |
| E2.4 | Proporsi klausa ter-buang | `_build_report_*.json`: `klausa_dibuang_tanpa_split = 4.183` (4,5% korpus) konsisten di 3 rasio | Audit: review mana yang hilang, apakah bias kategori |
| E2.5 | Disjointness antar lipatan | `id_to_split.json` tiap fold | Sudah terverifikasi 0 tumpang tindih — jadikan gate otomatis, bukan pengecekan manual |

### Tingkat 3 — EDA kesetaraan CV-5 vs CV-10 (kunci sebelum ablasi)

| ID | Item | Pertanyaan yang dijawab |
|---|---|---|
| E3.1 | Overlay graf review: berapa pasangan review yang berpindah peran train→test di antara keluarga | Seberapa besar cv5 & cv10 bisa dianggap replikasi vs perlakuan berbeda |
| E3.2 | Normalisasi test-size: bandingkan cv10 (test 10%) dengan sub-sampling cv5 menjadi test 10% | Memisahkan efek "jumlah lipatan" dari efek "ukuran data latih" |
| E3.3 | Varians antar-lipatan dalam satu keluarga (dev 2.945 vs 3.313 review, hampir konstan) | Estimasi ceiling noise; batas bawah signifikansi untuk semua ablasi |

### Tingkat 4 — EDA leksikon & normalisasi (mendukung ablasi A7)

| ID | Item | Input |
|---|---|---|
| E4.1 | Cakupan kamus slang/alay terhadap korpus | `data/Apps-ACOS/lexicon/` — 5 berkas: `colloquial_indonesian_lexicon.csv` (3,1 MB), `kamus_alay.csv` (181 KB), `kbba.txt` (19 KB), `singkatan_akronim_kateglo.json` (123 KB), `slang_adeariniputri.csv` (21 KB) |
| E4.2 | Kata tak-tervocab dengan & tanpa normalisasi | gabungan leksikon + `vocab.txt` |
| E4.3 | Contoh kasus sulit (implisit + multi-klausa + slang) untuk set inspeksi manual | `eda_all_samples_annotated.csv` (10,4 MB, 92.074 baris) |

**Prioritas eksekusi:** E1.4 (blokir) → E2.1 + E2.2 (validasi partisi) → E3.2 (netaskan desain ablasi) → sisanya.

---

## 5. Perencanaan Ablasi

### 5.1 Status dimensi ablasi berdasarkan indeks

| Dimensi | Nilai yang ada di hasil | Status |
|---|---|---|
| Epochs | 50 / 75 / 100 | **Direncanakan, 0 hasil** |
| Split ratio | 80/10/10, 70/15/15, 60/20/20 | **Data siap, 0 run pernah dijalankan** |
| Jumlah lipatan CV | 5 / 10 | 44/45 sel dicoba, 0 valid |
| Seed | hanya 42 | **Tidak pernah dimanipulasi** |
| Backend | hanya `rocm` | Tidak ada perbandingan CUDA/ROCm/CPU |
| AMP dtype | hanya `bfloat16` | Tidak ada perbandingan fp16/fp32 |
| Arsitektur (IndoBERT vs BERT vs dual-head) | — | Tidak ada dalam grid ini (lihat `reports/030`, `033`, `036`) |

### 5.2 Temuan penentu desain: cv5 vs cv10 tidak boleh jadi baris ablasi

Karena §3.2, memperlakukan "cv5fold vs cv10fold" sebagai efek eksperimental akan mencampur tiga hal: (a) jumlah rotasi lipatan, (b) ukuran data latih 72% vs 81%, (c) ukuran test 20% vs 10%. **Rekomendasi:** ganti dengan ablasi A2 yang men-etapkan ukuran data latih.

### 5.3 Grid ablasi yang diusulkan

| ID | Hipotesis | Perlakuan | Data partisi | Anggaran run | Prioritas |
|---|---|---|---|---|---|
| **A1** | Konvergensi epoch — apakah 50 cukup, atau 75/100 menambah F1 nyata | ep 25 / 50 / 100 (bukan 50/75/100; 25 memotong biaya 1/3) | cv10 fold_1..3 | 9 | P0 |
| **A2** | Efek jumlah lipatan **setelah data latih dineraskan** — cv10 vs cv5-subsampel (train disamakan ke 81%) | 2 kondisi | cv10 semua fold + cv5 subsampel | 15 | P0 |
| **A3** | Learning-curve / efek ukuran data — rasio split sebagai dimensi utama | 80/10/10, 70/15/15, 60/20/20 | `split_*` (sudah ada di disk!) | 9 | **P0 — biaya terendah, hasil paling baru** |
| **A4** | Varians seed → ceiling noise dan signifikansi semua ablasi lain | seed 42 / 1337 / 2024 pada 1 sel tetap | cv10 fold_1 ep50 | 3 | P0 (syarat interpretasi A1–A3) |
| **A5** | Amplop numerik: `bfloat16` vs `fp32` (dan `fp16` bila ROCm stabil) | 2–3 kondisi | cv10 fold_1 ep50 | 3 | P1 |
| **A6** | Kontribusi opini/aspek implisit terhadap Step-1 — latih dengan vs tanpa klausa implisit (40% opini implisit, lihat E1.3) | 3 kondisi: penuh / hapus opini-implisit / hapus aspek-implisit | base atau `split_801010` | 9 | P1 |
| **A7** | Normalisasi leksikon (5 kamus slang/alay/KBBI/akronim) vs mentah | 2 kondisi | `split_801010` | 3 | P1 |
| **A8** | Ukuran hold-out test — 10% vs 20% vs 25% dengan train tetap | 3 kondisi | cv5 (20%) vs cv10 (10%) vs partisi baru (25%) | 9 | P2 |
| **A9** | Backbone: IndoBERT-base vs BERT-uncased vs IndoBERT-large | 3 kondisi | `split_801010` | 9 | P2 (sudah sebagian tercakup `reports/030`) |

**Grid minimum yang layak dijalankan = A1+A2+A3+A4 = 36 run**, bukan 54. Grid lama 54 run membuang 15 sel untuk cv5/cv10 yang terconfound dan 30 sel duplikat.

### 5.4 Anggaran waktu berdasarkan angka yang terukur

Satu-satunya durasi epoch yang terekam adalah **89 s/run untuk 1 epoch Step-1** (6 run W3, konsisten 88,7–89,9 s). Dengan asumsi linear:

| Skenario | Estimasi serial |
|---|---|
| 1 run ep50 (Step-1 saja) | ≈ 74 menit |
| 1 run ep50 (Step-1 + Step-2) | ≈ 2,5–3 jam |
| Grid usulan 36 run ep50 | ≈ 3,5–4,5 hari komputasi |
| Grid lama 54 run | ≈ 6–7 hari |

**Peringatan:** angka 89 s/epoch itu sendiri berasal dari run yang metriknya degenerat — pakai hanya sebagai ordo besaran, bukan sebagai tolok ukur throughput. Kolom `duration_sec`, `samples_per_sec`, `vram_pct` kosong di semua log (0,0), sehingga tidak ada baseline throughput yang valid; memperbaiki pencatatan kolom ini adalah prasyarat A5.

### 5.5 Prasyarat keras sebelum satu run pun diulang

| # | Prasyarat | Bukti dari indeks |
|---|---|---|
| G1 | Tokenisasi 18 partisi CV/ratio dibuat & tersinkron (atau dibangun ulang) | hanya 1/19 partisi yang punya folder tokenisasi |
| G2 | `train_one_run(cfg)` menerima `dict`, dengan assert | 87 run mati karena `list.items` |
| G3 | Simpan bobot lewat `acos_id/checkpoint.py`, bukan `model.save_pretrained()` | 6 run mati di tahap simpan |
| G4 | Guard metrik: `f1 == 100.0` di ep1 **atau** `fp == 0 and fn == 0` → raise, jangan tulis log | 6/6 log tersimpan melanggar ini |
| G5 | Isi `duration_sec` / `samples_per_sec` / `vram_pct` per epoch | semua bernilai 0,0 |
| G6 | Tuliskan `_experiment_manifest.json` + `_experiment_progress.json` | keduanya tidak ada di repo |
| G7 | Satukan konvensi nama folder (`appsid_<ts>` vs `cv5fold_…`) dan letak (`results/` vs `results/experiments/`) | path JSON `/shared-docker/…/results/experiments/` ≠ struktur lokal |
| G8 | Selesaikan E1.4 (25.992 span bergeser) | tanpa ini semua F1 tidak bisa ditafsirkan |

---

## 6. Koreksi terhadap `reports/038`

Proses indexing menemukan bahwa analisis sebelumnya **meremehkan jumlah run**, karena daftar direktori pertama terpotong di tengah keluaran terminal dan angka 53 dipakai apa adanya:

| Butir | `reports/038` (keliru) | Nilai terverifikasi |
|---|---|---|
| Folder run CV | 53 (30 cv10 + 23 cv5) | **94** (60 cv10 + 34 cv5) |
| Run berstatus ERROR karena Bug #1 | 47 | **87** |
| Berkas `run_result.json` | 53 | **93**, + 1 folder tanpa result |
| Total folder | 100 | 101 (sebelum `_index/` dibuat) |
| Total run berstatus `OK` | 0 | 0 (tetap) |
| Disjointness train/dev/test | "perlu diaudit ulang" | **Terverifikasi 0 tumpang tindih** pada 36.821 review |
| Dugaan "test 15.003 tidak proporsional" | dianggap anomaly | Bukan anomaly: cv5 memang hold-out 20%; temuan sebenarnya adalah **cv5 ≠ cv10 dalam ukuran data latih (72% vs 81%)** |

Koreksi ini telah ditulis sebagai bagian koreksi pada `reports/038`.

---

## 7. Cara Pakai & Perbarui Indeks

```powershell
cd D:\laragon\www\ACOS-ASLI
python scripts/index_acos_results.py
```

Skrip bersifat *idempotent* dan *read-only* terhadap folder hasil; output tiga CSV ke `results/_index/` dan ringkasan ke stdout. Jalankan ulang setiap kali gelombang eksperimen baru selesai, lalu bandingkan `grid_coverage.csv` untuk melihat sel mana yang berubah dari `ERROR` → `OK`.

| Berkas indeks | Baris | Kegunaan utama |
|---|---|---|
| `run_index.csv` | 94 | Join `family`×`epochs`×`fold`×`status` — dasar semua pivot ablasi |
| `data_partition_index.csv` | 19 | Ketersediaan & ukuran tiap partisi + flag tokenisasi — penentu kelayakan tiap run |
| `grid_coverage.csv` | 89 | Matriks 45 sel CV + 1 sel hilang + daftar sel tak pernah dijalankan — checklist eksekusi |

---

*Semua angka di dokumen ini berasal dari pembacaan langsung berkas di disk, dapat direproduksi dengan menjalankan ulang skrip pada §7.*
