# Analisis Mendalam Folder `ACOS-IndoBERT`: Yang Dikerjakan, Keterhubungan Berkas, dan Kelengkapan Notebook

> **Tanggal:** 03112026
> **Cakupan:** seluruh isi `ACOS-IndoBERT/` — 22 notebook ipynb, 14+4 modul `acos_id/`, 124 berkas `data/`, 93 berkas tokenisasi, 213 berkas `results/`, 3 dokumen VERSI, README, `build/`, `backbones/`, `REFERENSI/`
> **Metode:** inventaris penuh via `os.walk` (bukan listing terminal — pelajaran `reports/038` §8), parsing JSON tiap ipynb (sel, outputs, error, execution_count), grep silang referensi antar-berkas, pembacaan report build JSON
> **Prasyarat baca:** `reports/038` (verdict results), `reports/039` (indeks & ablasi), `reports/040` (korelasi plot↔CSV)

---

## 0. Ringkasan Eksekutif

1. **Yang dikerjakan:** proyek telah menyelesaikan **seluruh lapisan pra-pemrosesan** (scraping → weak-labeling → build quad → split CV/ratio → tokenisasi base → EDA → gerbang audit) dan **empat generasi notebook** (V4 → V4.1/4.2/4.3 → V5/V5.1/V5.2 → V5.2.1/V5.3) plus benih v6. Yang **belum selesai hanya satu**: training yang menghasilkan angka sah — kecuali satu jejak nyata: **Micro-F1 Step-2 67,69% (epoch 3)** yang tersimpan di output notebook `run08092026`.
2. **Hanya 2 dari 22 notebook berstatus dieksekusi penuh**: `00_..._V4_INDOBERT_run08092026.ipynb` (49/49 sel, 0 error) dan `V4_1_01_setup.ipynb` (22/22 sel, 0 error). Sisanya: 15 parsial, 3 mati di sel awal (`01_MI300X`, `01_V5.1`, `02_V5.2_Universal`), dan 2 belum pernah dijalankan (`Kaggle_V4`, `V4_1_02`).
3. **Rantai keterhubungan utuh dan dapat dilacak**: `raw → processed → appsid_quad_*.tsv → tokenized_data → results/_eda/_gates/_backbone/_embedding → run-folder CV`. Masing-masing artefak punya berkas report build JSON yang menyebut path sumbernya (semua dibangun di mesin Windows ini, kecuali 94 run-folder yang dibangun di `/shared-docker` GPU ROCm).
4. **Tiga celah artefak**: folder `results/checkpoints/` & `results/csv/` kosong; sesi Drive `appsid_08092026_150437` (pemilik angka 67,69%) tidak disinkron ke repo; tokenisasi baru 1 dari 19 partisi (konsisten `reports/039` G1).

---

## 1. Peta Struktur dan Apa yang Dikerjakan per Folder

| Folder | Isi | Peran dalam pipeline | Status |
|---|---|---|---|
| `data/Apps-ACOS/raw/` | `gplay/` (13) + `appstore/` (13) + 2 CSV agregat + 3 JSON registry (23,4 MB) | Hasil scraping ulasan 13+ aplikasi bank digital Indonesia | ✅ Lengkap |
| `data/Apps-ACOS/processed/` | `quintuples_weak.csv` (96.417 tuple, 39,7 MB), `reviews_clean/labeled.csv`, `stage1_{train,val,test}.jsonl`, `stage2_{train,val,test}.jsonl`, `label_maps.json` (123,9 MB) | Weak-labeling + format 2 tahap (stage1 ekstraksi, stage2 klasifikasi) | ✅ Lengkap |
| `data/Apps-ACOS/lexicon/` | 5 kamus (kamus_alay, KBBA, slang, singkatan/kateglo, colloquial 3 MB) | Normalisasi bahasa informal — **belum dipakai notebook mana pun** (lihat §4.3) | ⚠️ Terbuang |
| `data/Apps-ACOS/` (root) | `appsid_quad_{train,dev,test}.tsv` + `_build_acos_report.json` | Bangunan dasar 79:11:10 (60.159/8.027/7.891 kalimat) | ✅ Tervalidasi |
| `data/Apps-ACOS/cv_5fold/` + `cv_10fold/` | 5 + 10 fold × 4 berkas + `_cv_report.json` | Partisi CV level `review_id` — nol kebocoran terverifikasi (`reports/039`) | ✅ TSV siap, ❌ belum tokenized |
| `data/Apps-ACOS/split_{801010,701515,602020}/` | 3 × 4 berkas | Eksperimen rasio (run_idx 1–9) — **tidak pernah dijalankan** | ✅ TSV siap, ❌ belum tokenized |
| `tokenized_data/` | 6 berkas `appsid_*` + `_build_report_appsid.json` | Tokenisasi partisi **base saja** (path build: `D:\laragon…` = mesin ini) | ✅ Valid, 1/19 partisi |
| `v5_en/tokenized_data/` | 12 berkas `laptop_*`/`rest16_*` + 2 report | Kontrol bahasa Inggris (domain laptop & rest16) | ✅ Siap pakai |
| `backbones/` | 2 `vocab.txt` (indobert_base_p1, bert_base_uncased) | Cadangan vocab untuk verifikasi gerbang backbone | ✅ |
| `acos_id/` | 14 modul + subpaket `v6/` (config, drive, gpu) | Pustaka modular Inti — lihat §3 | ✅ |
| `notebooks/` | 22 ipynb + 7 md + 24 py builder/inspector | Antarmuka eksekusi Colab/Kaggle — lihat §4 | ⚠️ Campuran |
| `results/` | 94 run-folder + `_eda` `_gates` `_backbone` `_embedding` `_index` + `checkpoints/` `csv/` kosong | Output ekperimen CV — verdict di `reports/038`: 0 run OK | ❌ Training, ✅ pra-pemrosesan |
| `build/` | 3 skrip port/verifikasi + `_gate2_en/report.json` | Jembatan pemindahan fitur resume-training ke V4; gerbang tokenisasi EN | ✅ |
| `REFERENSI/` | 2 md analisis IndoBERT 13 bank digital | Catatan riset domain (bukan kode) | ℹ️ |
| Dokumen VERSI V4/V5.1/V5.2 (28–42 KB) | Detail tahapan per sel, 1.047–1.418 baris | Spesifikasi desain tiap generasi | ✅ |

---

## 2. Alur Data yang Terbukti dari Report JSON

```
raw (gplay+appstore scraping)
  → processed/ (weak-label: quintuples_weak.csv 96.417 tuple; stage1/stage2 jsonl)
    → build_acos.py  ⇒  appsid_quad_{train,dev,test}.tsv   [_build_acos_report.json:
      64.348 aspek eksplisit / 27.726 implisit; 54.800 opini eksplisit / 37.274 implisit —
      IDENTIK dengan joint count yang memvalidasi plot 02b di reports/040]
      → cross_val.py  ⇒  cv_5fold/fold_1..5, cv_10fold/fold_1..10, split_*  [_cv_report.json]
        → tokenize_data.py  ⇒  tokenized_data/ (BASE SAJA) + v5_en/ (EN)   [_build_report_*.json]
          → experiment_runner.py + notebook V5  ⇒  results/cv*fold_* (94 folder, /shared-docker)
          → eda.py + guards.py + checkpoint.py  ⇒  results/_eda, _gates, _backbone, _embedding
```

Angka `_build_acos_report.json` (64.348/27.726/54.800/37.274) **cocok persis** dengan marginal di `eda_dataset_statistics.csv` dan joint di `eda_all_samples_annotated.csv` — tiga lapisan (builder → EDA → plot) saling mengunci. Ini bukti integritas rantai data terkuat di repo.

---

## 3. Modul `acos_id/` — Siapa Memanggil Siapa

| Modul | Baris | Fungsi | Dipakai oleh |
|---|---|---|---|
| `build_acos.py` | ~230 | quad TSV dari processed/ | notebook V4 setup, `reports/023` |
| `cross_val.py` | 29,5 KB | partisi CV & rasio | notebook V5 (prepare_all_data) |
| `tokenize_data.py` | 11,4 KB | tokenisasi → pair/quad_bert TSV | semua pipeline |
| `experiment_runner.py` | 15,9 KB | grid 54 run | **5 notebook V5** (01_MI300X, 01_V5.1, 02_V5.2, 02_V5.2.1, 03_V5.3) |
| `guards.py` | 12,6 KB | gerbang verifikasi + parse TP/FP/FN | V4_2_GUARDS dst → `results/_gates/gates.csv` |
| `checkpoint.py` | 11,6 KB | rekey `bert.*` + `gate_weights_loaded` | penyebab GATE 1 GAGAL di 2 notebook (lihat §4.4) |
| `eda.py` | 11,9 KB | statistik + 4 plot PNG | → `results/_eda/` (tervalidasi `reports/040`) |
| `result_saver.py` | 31,1 KB | penulisan artefak run | runner |
| `selftest.py` | 20 KB | audit wajib berkas processed (baris 104) | sel selftest di 21 notebook |
| `session.py`, `taxonomy.py`, `model_wrappers.py`, `upstream.py`, `__init__.py` | — | state resume, kategori, wrapper, unduhan | V4_3_SESSION dll |
| `v6/{config,drive,gpu}.py` | kecil | **benih generasi berikutnya** — baru 4 berkas, belum ada notebook v6 | ⚠️ work-in-progress |

---

## 4. Audit Kelengkapan 22 Notebook

### 4.1 Tabel status (hasil parsing JSON, bukan tebakan)

Legenda: **L** = dieksekusi penuh tanpa error tersimpan; **S** = sebagian; **R** = rusak di sel awal; **B** = bersih tapi belum pernah dijalankan.

| Notebook | Sel kode | Output | Error tersimpan | Eksekusi | Kelas |
|---|---|---|---|---|---|
| `00_..._V4_INDOBERT_run08092026.ipynb` | 49/49 | 38 | 0 | exec 1–56 penuh | **L ✅** |
| `V4_1_01_setup.ipynb` | 22/22 | 15 | 0 | exec 1–22 penuh | **L ✅** |
| `00_..._V4_INDOBERT.ipynb` | 48 | 32 | 0 | lastExec 79 (heavily rerun) | S |
| `00_..._V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb` | 49 | 38 | 0 | lastExec 167 | S |
| `00_..._V4_1_INDOBERT.ipynb` / `_V4_2_GUARDS.ipynb` / `_V4_3_SESSION.ipynb` | 48–51 | 37 | 0 | lastExec 48 | S |
| `02_ACOS_V5_2_1_Embedding_Classification_Prediction.ipynb` | 20 | 18 | 1 (assert "Belum ada run OK") | s/d exec 17 | S* |
| `03_ACOS_V5_3_Classification_Prediction_IndoBERT.ipynb` | 20 | 18 | 1 (assert sama) | s/d exec 13 | S* |
| `V4_1_03_step2_train.ipynb` / `V4_2_05_acos_classification_indobert.ipynb` | 9 | 7 | 0 | parsial | S |
| `V4_1_04_eval_inference.ipynb` / `V4_2_06_prediction_indobert.ipynb` | 9 | 5 | 0 | parsial | S |
| `00_ACOS_Master_Pipeline_Colab.ipynb` (V2-era) | 12 | 10 | 1 (`NoneType.to`) | berhenti sel 18 | S |
| `00_..._V4_INDOBERT copy.ipynb` | 48 | 21 | 2 (KeyboardInterrupt, `require_vars`) | lastExec 2 | S |
| `00_..._V4_BERT_rest16_run24092026_GPU…` | 49 | 38 | 1 (**GATE 1 GAGAL**) | lastExec 29 | S |
| `00_..._V5_EN_REST16_LAPTOP.ipynb` | 49 | 38 | 1 (**GATE 1 GAGAL**) | lastExec 30 | S |
| `01_ACOS_MI300X_V5_FullExperiment…` | 12 | 4 | 1 (**IndentationError sel 7**) | mati dini | **R** |
| `01_ACOS_V5_1_FullExperiment…DriveSync.ipynb` | 14 | 3 | 1 (**`bert_utils` hilang**) | mati dini | **R** |
| `02_ACOS_V5_2_Universal_FullExperiment…` | 18 | 3 | 1 (**`bert_utils` hilang**) | mati dini | **R** |
| `00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb` | 48 | 0 | 0 | belum pernah jalan | **B** |
| `V4_1_02_step1_train.ipynb` | 11 | 1 | 1 (kosong) | belum jalan | **B/R** |

### 4.2 Mana yang "sudah lengkap"

- **Lengkap dan berisi hasil nyata — hanya `00_..._run08092026.ipynb`.** Satu-satunya yang menuntaskan seluruh 49 sel (0 error) dengan artefak: ringkasan Step-2 "**Micro-F1 terbaik tersimpan: 67,69% (epoch 3)**", tabel TP/FP/FN per epoch, benchmark sub-task (sel 9a/9b), inferensi contoh (`transfer nya cepat tapi aplikasi sering error…`), dan **sel 80 "AUDIT ARTEFAK SESI AKTIF"**. Ini angka sah *tertinggi* yang ada di seluruh repo — sayangnya artefak sesinya (`appsid_08092026_150437` di Google Drive) tidak ikut tersinkron ke `results/` lokal.
- **Lengkap untuk tahapannya — `V4_1_01_setup.ipynb`**: setup + mount + diagnostik folder + EDA (cache-hit dari `master_01_statistik_dataset.csv`) + adapter checkpoint + 5 gerbang torch-free. Inilah notebook sumber artefak `_eda`/`_gates`/`_backbone` (diperkuat grep §4.4).
- **Lengkap secara struktur, nol eksekusi — `00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb`**: 48 sel utuh, 0 output; siap jalan, belum pernah dipakai.
- **Rangka V5 (01/02/03) tidak ada yang tuntas**: dua mati di `bert_utils` (bug yang diklaim sudah diperbaiki `VERSI_V5_2_DETAIL_TAHAPAN.md` §"1. bert_utils FIXED" — output tersimpan membuktikan perbaikan belum pernah berhasil dieksekusi di notebook ini), satu IndentationError, dan V5.2.1/V5.3 berhenti di gerbang_assert yang *benar perilakunya* ("Belum ada run OK").

### 4.3 Yang tidak terhubung ke apa pun (dead assets)

| Berkas | Bukti |
|---|---|
| `data/Apps-ACOS/lexicon/` (5 kamus, 3,4 MB) | 0 notebook mereferensikan `lexicon`/`kamus_alay` — ablasi A7 (`reports/039`) masih menunggu implementasi |
| `results/checkpoints/`, `results/csv/` | direktori kosong tanpa satu berkas pun |
| `notebooks/test_v51.tmp` (2 B), `.bak` × 2, 24 skrip `_inspect_*`/`_apply_*`/`fix_*` | perkakas sekali-pakai era perbaikan V5.1 — arsip, bukan pipeline |
| `acos_id/v6/` | 4 modul tanpa pemanggil (notebook v6 belum ada) |

### 4.4 Matriks keterhubungan notebook → artefak hasil (grep string unik)

| Artefak di `results/` | Notebook yang memuat kode pembuatnya |
|---|---|
| `_eda/` (4 CSV + 4 PNG) | semua `00_…V4*` + `V4_1_01_setup` + `V4_1_04` + `V4_2_06` (string `01_eda_dataset_distribution`, `eda_all_samples_annotated`) |
| `_gates/gates.csv` | `02_ACOS_V5_2_1`, `02_ACOS_V5_2_Universal`, `03_ACOS_V5_3` (+ sel gerbang V4) |
| `_backbone/backbone_check.csv` | `02_ACOS_V5_2_1`, `03_ACOS_V5_3` |
| `_embedding/embedding_audit.csv` | `02_ACOS_V5_2_1`, `03_ACOS_V5_3` (konsisten `reports/038`: temuan `span_bergeser=25.992` lahir dari sini) |
| 94 run-folder `cv*fold_*` | 5 notebook V5 yang memanggil `run_all_experiments`/`prepare_all_data` — dieksekusi di `/shared-docker` (sesi 27092026 tercatat di output `02_V5_2_1` dan `03_V5_3`) |
| Sesi `appsid_08092026_*` (Drive, tidak lokal) | `run08092026`, `V4_1_01_setup`, varian V4_1/V4_2 |

---

## 5. Konklusi

1. **Pekerjaan yang sudah benar-benar selesai**: pengumpulan & pembersihan data (43.673 ulasan → 96.417 weak-quintuple), pembangunan partisi (base + 15 CV + 3 rasio, nol kebocoran), tokenisasi base + EN, EDA tervalidasi silang, sistem gerbang (gates/backbone/embedding), pustaka modular `acos_id`, dan satu pelatihan Step-2 nyata (Micro-F1 67,69%) di sesi 08092026 yang artefaknya tertinggal di Drive.
2. **Yang berhenti tepat sebelum garis finis**: training Step-1 CV — 94 run folder semuanya ERROR (`reports/038`), dan tiga notebook peluncurnya mati di sel 7 (`bert_utils`/indentasi). Perbaikan yang didokumentasikan V5.2 **belum pernah dibuktikan berjalan**.
3. **Notebook yang layak dipakai ulang apa adanya**: `run08092026` (referensi hasil), `V4_1_01_setup` (referensi pra-pemrosesan), `Kaggle_V4` (basis bersih belum jalan). Sisanya perlu dirangkai ulang mengikuti gerbang G1–G8 di `reports/039` §5.5 — dimulai dari tokenisasi 18 partisi, bukan dari menambah notebook baru.
4. **Rekomendasi sinkronisasi**: unduh `appsid_08092026_150437/` dari Drive ke `results/` lokal — satu-satunya cara repo ini menyimpan bukti numerik sah 67,69% selain screenshot di output notebook.

---

*Angka eksekusi per notebook berasal dari parsing `execution_count`/`outputs` JSON ipynb; daftar referensi dari grep string unik di seluruh sel. Skrip audit tersimpan di `ACOS-IndoBERT/build/_audit_notebooks.py` (read-only, dapat dijalankan ulang).*
