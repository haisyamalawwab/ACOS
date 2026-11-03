# Analisis Mendalam Folder `screenshot/`: Rekonstruksi Alur Kerja Sesi Riset 24092026 dari 31 Gambar

> **Tanggal:** 03112026
> **Cakupan:** 31 PNG di `screenshot/` — 4 FireShot AMD DevCloud, 26 screenshot Windows (15:49–17:17), 1 screenshot aaPanel tanpa nama. Seluruhnya termodifikasi 24092026
> **Metode:** pembacaan visual penuh tiap gambar (31/31), ekstraksi teks/output yang terbaca, silang dengan artefak repo (`reports/038–041`, `v5_en/tokenized_data`, dokumen SETUP AAPANEL)
> **Prasyarat baca:** `reports/041` (kelengkapan notebook), `reports/038` (verdict results)

---

## 0. Ringkasan Eksekutif

Folder `screenshot/` adalah **dokumentasi visual satu hari kerja penuh (24092026)** saat infrastruktur GPU AMD Instinct MI300X di AMD Developer Cloud di-provisioning dan pipeline ACOS dijalankan di atasnya. Dari 31 gambar, lima hal besar dapat direkonstruksi:

1. **Infrastruktur lengkap dibangun dalam hari itu**: droplet MI300X 192 GB ($1,99/jam, Atlanta) + container ROCm + JupyterLab (port 8000 & 8888) + aaPanel + WSL Ubuntu-24.04 di laptop lokal + repo tersinkron ke `/shared-docker/ACOS`.
2. **Kontrol Inggris (REST16) terbukti berhasil dilatih di Step-1**: Micro-F1 test **53,20% → 80,76%** (15 epoch, 2m35s) — hasil sah paling lengkap yang terekam. **Tetapi Step-2-nya gagal total: Micro-F1 0,00% (TP=0, FP=165.728, FN=895)** — mode kegagalan Step-2 sudah muncul di domain kontrol sebelum CV appsid pernah jalan.
3. **Tokenisasi `v5_en/` (laptop & rest16) lahir pada hari itu di droplet** — gerbang 4e membangun ulang 6 berkas cache yang hilang; inilah yang kini tersinkron sebagai `ACOS-IndoBERT/v5_en/tokenized_data/`.
4. **Sesi APPSID 50-epoch (appsid_24092026_0901) disiapkan dan dijalankan** di droplet: 124,5 juta parameter, 65.423 contoh latih, 4.089 batch×16, BertAdam t_total=204.450 langkah — tapi artefak sesinya tidak tampak di `results/` lokal.
5. **GPU sangat tidak termanfaatkan**: utilization memori puncak hanya 9% dari 192 GB, VRAM terpakai 475 MB, daya 350 W (idle 140 W) — dengan biaya $1,99/jam.

---

## 1. Identitas Infrastruktur (FireShot 014/015/017/018 + Screenshot 155009/155052)

| Aspek | Nilai terbaca dari gambar |
|---|---|
| Droplet | `2.10.0-gpu-mi300x1-192gb-devcloud-atl1`, status Active, region **ATL1 (Atlanta)**, proyek "My AMD Home", powered by DigitalOcean |
| Spesifikasi (015) | 1 GPU / **192 GB VRAM** / 20 vCPU / 240 GB RAM; boot 720 GB NVMe + scratch 5 TB |
| Biaya | **$1,990 / jam** (Overview 155052) |
| Citra | marketplace "PyTorch 2.10.0 (ROCm 7.2.4)" — **tapi MOTD console (155009) melaporkan PyTorch 2.12.0+rocm7.14.0**, Python 3.12.3, ROCm host 7.14.1, JupyterLab 4.4.2, Docker 29.7.2, GPU terdeteksi `1 x AMD Instinct MI300X VF`, container `rocm` running |
| Akses | IP publik `165.245.133.11`; UFW hanya membuka 22/80/443; JupyterLab via tunnel `ssh -L 8000:localhost:8000` (155009) dan langsung via `:8000` (160130) serta `:8888` (171450–171757) |
| Perintah baku | `docker exec -it rocm /bin/bash`, `docker logs rocm`, `amd-smi monitor`, `rocminfo` (MOTD) |
| Manajemen server | **aaPanel PRO 8.0.6** di IP yang sama (Screenshot.png): Ubuntu 24, load 0.32/0.34/0.20, RAM 4,7/235,95 GB, disk 79,2/696,4 GB (12%), traffic masuk 645,65 MB — cocok dengan `PANDUAN_SERVER_JUPYTER_AAPANEL.md` dan `STEP_BY_STEP_AMD_GPU_JUPYTER_AAPANEL.md` di root repo |

### 1.1 Telemetri GPU (FireShot 014 & 017, jendela 14:55–17:23)

| Waktu | Peristiwa | Angka kunci |
|---|---|---|
| 14:55–15:43 | mesin baru nyala, hampir kosong | utilitas memori ~0–0,15%, daya naik ke 140 W (idle), suhu core 38°C |
| 15:45–15:50 (014) | boot/agent monitoring | PCIe 0,02 Gb/s, ECC error 0 |
| 16:23–16:28 (017) | **burst kerja #1** | utilitas memori **9%**, daya **350 W**, PCIe 1,3 Gb/s, **power throttling 0,2%**, core 45°C |
| 16:30–17:10 (017) | idle panjang | daya turun ke 145 W, PCIe 0 — fase setup/upload |
| 17:13–17:23 (017) | **burst kerja #2** | utilitas memori 3%, daya 350 W, PCIe puncak **2,2 Gb/s**, core naik 40→55°C |
| Droplet (018) | aktivitas CPU/IO | CPU 81,8% @16:24, load1 18,9; tulis vda 35 MB/s; baca 140 MB/s @17:08; disk 11,4→14,5%; bandwidth masuk ~110 Mb/s 17:05–17:15 (fase sinkron repo/data) |

**Interpretasi:** dua burst komputasi nyata (masing-masing ±5–10 menit) cocok dengan training Step-1 REST16 (2m35s) dan penyiapan sesi APPSID sore hari. Tidak ada satu pun jendela training panjang multi-jam pada hari itu — konsisten dengan temuan `reports/038` bahwa gelombang CV besar terjadi 27092026, tiga hari kemudian.

---

## 2. Alur Kerja per Screenshot (kronologis)

### 2.1 Fase IDE lokal (15:50–15:56, Antigravity IDE)

- **155325** — `00_ACOS_Master_Pipeline_Colab.ipynb` dibuka; sel dependensi (`pip install pytorch-crf transformers …`) jalan 19,2s; output: `PyTorch Device: cuda`, `GPU Model: AMD Instinct MI300X VF`. **Terminal menampilkan `wsl.exe --install -d Ubuntu-24.04` sedang download** — provisioning WSL lokal paralel. Panel Agent: Gemini 3.8 Flash Medium, status "MCP Error". Git graph memperlihatkan riwayat commit besar era ACOS-BERT/V4.
- **155408** — EDA REST16 (sesi `/shared-docker/ACOS/results/rest16_24092026_0849`): tabel statistik (train 1.530/2.484, dev 171/261, test 583/916), ringkasan EDA (**3.661 quadruple, 880 aspek implisit, 700 opini implisit, 350 keduanya-implisit, 13 kategori, median 15 kata**), dan 4 plot `[REST16]` (distribusi split, eksplisit-vs-implisit, top kategori FOOD#QUALITY/SERVICE#GENERAL, pie polaritas). **Catat penting: REST16 punya 350 klausa double-implicit, sedangkan appsid final = 0** (validasi silang `reports/040` §1.3).
- **155437** — **Training Step-1 BERT-CRF REST16 berhasil**: 15 epoch dalam **2m35s**, `tp/fp/fn` sehat tiap epoch (mis. ep6: tp=1328, fp=363, fn=287), Test Micro-F1 **53,20 → 75,26 → 80,00 → 80,34%**; checkpoint `step1_best` disimpan ke `rest16_24092026_0849/checkpoints/`. Warning dari `/shared-docker/ACOS/Extract-Classify-ACOS/bert_utils/optimization.py` (jejak asal-usul bug `bert_utils` yang muncul kemudian).
- **155514** — Tabel riwayat 15 epoch (`master_03_step1_riwayat.csv`): **terbaik epoch 14, micro-F1 80,76%**; dua plot kurva loss & metrik validasi (`03_step1_training_loss_f1_curve.png`).
- **155609** — **Training Step-2 REST16 gagal total**: 15 epoch loss turun 0,178→0,0035 tetapi **precision=recall=micro-F1=0,0 di semua epoch**; `tp=0, fp=0, fn=85…623` (model tidak pernah memprediksi positif). Tabel `master_06_step2_riwayat.csv`, plot `04_step2_training_loss_f1_curve.png`. Sel 11/23.

### 2.2 Fase JupyterLab di droplet (16:01)

- **160130** — Browser ke `165.245.133.11/lab/...00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb`; file browser `/ACOS/` menampilkan repo penuh tersinkron (absa5, ACOS-BERT, ACOS-IndoBERT, Extract-Classify-ACOS, results, dst). Sel diagnostik GPU: **VRAM 191,69 GB, Compute Capability 9.4, cuDNN 3005002**; markdown "1b. Pelacak Progres Bertahap (step_stage)" + `patch_eval_metrics_counts()` (TP/FP/FN ikut dikembalikan measureQuad) — mekanisme yang dipakai guards `reports/038`.

### 2.3 Fase notebook V5 EN PRO (16:03–16:15, 82 sel)

- **160338** — `00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP.ipynb` ("Production PRO Version") dibuka di IDE; Agent kanan mengerjakan **"Fixing Model Loading Error"** — traceback `AttributeError` di cell [10] notebook Colab, lalu `CommandNotFoundException` (pwsh tidak menemukan `python`), menjalankan `python _inspect_cells.py`; prompt izin "Allow running inspect script?" menunggu user.
- **160422** — Sel identitas: `acos_id v0.2.1`; **dua root terkonfirmasi**: `indo_root (tulis) = /shared-docker/ACOS/ACOS-IndoBERT`, `acos_root (baca) = /shared-docker/ACOS`; `extract_dir = /shared-docker/ACOS/Extract-Classify-ACOS`; domain `appsid`; 13 kategori → 39 label Step-2; gerbang torch-free (taxonomy, dataset, acos_build, tokenized, gate2_english); **rest16 & laptop terdeteksi ✅ di `/shared-docker/ACOS/data/`**.
- **160446** — Konfigurasi seed 42, `RESUME_LAST_SESSION=True`; `session_dirs_from_root()` — rekonstruksi peta direktori sesi tanpa membuat folder baru (checkpoint step1_best/step2_best, plots, csv, md, logs).
- **160507** — Sel 11: **sesi `rest16_24092026_0903` diinisialisasi**; verifikasi folder tulis ✅; unduh `bert_base_uncased` (config.json + pytorch_model.bin), vocab.txt sudah cache (0,22 MB).
- **160541** — Manifest MCP + tabel konfigurasi master pipeline REST16 (`master_00_konfigurasi.csv`): 15 epoch, batch 32/32, lr 2e-5/5e-5, max_seq 128, seed 42, device cuda.
- **160613** — EDA REST16 sesi 0903 diulang (angka identik dengan 155408 — deterministik) + plot dirender.
- **160713** — Laporan backbone (`master_00_backbone_indobert`): key rekeying, vocab vs config; **4c: DOMAIN='rest16' memakai bert-base-uncased apa adanya, adapter IndoBERT dilewati** ✅; `backbone_report.json` ke logs ("Gate 1 numerik menyusul di sel 5d2").
- **160740** — **Sel 4e "Gerbang data Inggris V5"**: cache v5_en belum lengkap (kurang 6 berkas) → **retokenisasi WordPiece + remap span dari mentah** (tokenizer 30.522 entri; train 1.530/2.484/2.420 pair, dev 171/261/251, test 583/916/895; 0,4s per split) → laporan `v5_en_gate.json`. **Inilah kelahiran `v5_en/tokenized_data/` yang ada di repo lokal sekarang.**
- **160844** — Sel 7a (sudah berpindah konteks ke **Colab `/content/drive`**): sumber prediksi Step-1 = sesi lama **`rest16_12092026_104518`**; 7.386 baris prediksi dibaca → **10.735 pasangan kandidat** ditulis ke `v5_en/tokenized_data/rest16_...`; widget progress gagal dirender (`Could not render content for widget-view+json`). Sel 34/82.
- **161017** — Sel 7b distribusi kandidat: **Explicit-Implicit 4.459 (41,54%), Explicit-Explicit 3.456 (32,19%), Implicit-Explicit 2.813 (26,20%), Implicit-Implicit 7 (0,07%)**; `master_04_type_pasangan.csv`. **Anomali penting:** tabel "Preview 20 Pasangan Kandidat (REST16)" berisi teks **Indonesia** ("saldo aku 100 ribu", "kok tidak bisa transfer", "chat ke customer service tidak membantu") — label domain REST16 di atas data yang tampak seperti appsid; indikasi kuat jalur cache/domain tercampur di sesi Colab ini.
- **161051** — Sel 8a inisialisasi Step-2: **[1/6] "GPU cache dibersihkan | Tesla T4"** — eksekusi kini di **Google Colab**, bukan MI300X; patch tokenizer (OOV→[UNK]), patch eval_metrics (tp/fp/fn), 39 label, Single-Head (`USE_DUAL_HEAD=False`); checkpoint dari `rest16_12092026_104518`; FORCE_RETRAIN_STEP2=False, target 15 epoch. Agent kanan berganti model ke **Claude Opus 4.6 (Thinking)**.
- **161112** — Sel 8b deteksi cache: checkpoint sesi **appsid_08092026** (474,9 MB) **ditandai/dilewati karena beda domain**; CACHE HIT ke checkpoint rest16_12092026_104518; **riwayat hanya 1/15 epoch — run terhenti** (⚠️ saran FORCE_RETRAIN_STEP2=True). Sel 60/82.
- **161138** — Sel 8c data evaluasi: 10.735 pasangan dari `rest16_test_pair_1st.tsv` (prediksi step-1 skor pipeline penuh) → 10.735 fitur (max_seq 128) → eval_loader 671 batch×16; **[5/5] "Gold quadruple dibaca dari rest16_test_pair.tsv (2 entri)"** — angka gold yang janggal (harusnya ratusan), kandidat bug pembacaan gold.
- **161430** — Sel 9a evaluasi final: **micro-F1 0,00%; TP=0, FP=165.728, FN=895**; 15 sub-task tertangkap dengan TP/FP/FN; `master_metrics.json` tersimpan; selesai 31,6s. Agent kanan mengalami **`UnicodeEncodeError` charmap cp1252** saat `_dump_cell.py` (posisi 3315, karakter `\u00f8`), lalu prompt "Allow dumping cell 9?".
- **161517** — **Audit artefak sesi REST16: 57 berkas tersimpan di Drive** (`rest16_12092026_104518`): 6 checkpoint (pytorch_model.bin 477,07 MB & 474,88 MB), 19 CSV (candidate_pairs_summary 851,2 KB, eda_all_samples_annotated 510,0 KB, master_00/00c/01 dst). Sel 80/82 — notebook PRO hampir tuntas.

### 2.4 Fase APPSID di droplet (17:14–17:17)

- **171450** — JupyterLab `:8888`, notebook **`00_..._V4_INDOBERT_run08092026.ipynb`** dijalankan di MI300X; manifest sesi **`appsid_24092026_0901`**; konfigurasi APPSID: **50 epoch, step1_batch 24, step2_batch 16**, lr 2e-5/5e-5, seed 42, cuda; sel EDA [16] menyiapkan `master_01_statistik_dataset.csv` + plot `01_eda_dataset_distribution.png`. File browser memperlihatkan eksperimen lain di droplet: `fine_tuning_lora_q…`, `train_ddim.ipynb`, `triton_kernel_devi…` (±1 jam), dan pengarsipan `results.tar.gz`/`output_results.tar` (37 menit) — **MI300X juga dipakai riset di luar ACOS**. Tab kedua terbuka: `04_step2_training_loss_f1_cu…`.
- **171623** — Sel 8d Step-2 APPSID: **model 124,5 juta parameter dimuat ke cuda, VRAM terpakai hanya 475 MB**; 65.423 contoh latih; **4.089 batch × 16**; BertAdam lr 5e-5, warmup 0,1, **t_total=204.450 langkah**; selesai 7,5s. Seksi 8e loop-training dengan ETA + step2_training_history.csv + step2_progress.json + session_manifest.json.
- **171757** — Plot `[APPSID] Pasangan Kandidat Step 1 -> Step 2`: **Explicit-Implicit 4.560 (41,5%), Explicit-Explicit 3.600 (32,8%), Implicit-Explicit 2.814 (25,6%), Implicit-Implicit 17 (0,2%)**; disimpan `appsid_24092026_0901/plots/04_candidate_pairs_distribution.png`. **Catatan:** 17 kandidat double-implicit di appsid — hilang (menjadi 0) di dataset final yang divalidasi `reports/040`; ada keputusan pembuangan eksplisit di pipeline.

---

## 3. Korelasi Screenshot ↔ Artefak Repo

| Bukti di gambar | Artefak fisik di repo | Status silang |
|---|---|---|
| 4e retokenisasi EN (160740), train 1.530/2.484/2.420 | `ACOS-IndoBERT/v5_en/tokenized_data/` (12 berkas + `_build_report_rest16.json`) | ✅ Angka cocok; berkas memang hasil sesi 24092026 |
| EDA REST16 (155408/160613): 3.661 quad, 350 double-implicit | `v5_en/tokenized_data/_build_report_laptop/rest16.json` | ✅ Konsisten |
| Step-1 REST16 80,76% + checkpoint `rest16_24092026_0849` | — (di `/shared-docker`, tidak tersinkron) | ❌ Tidak ada di repo lokal |
| Audit 57 berkas Drive `rest16_12092026_104518` | — (Drive) | ❌ Tidak tersinkron |
| Sesi APPSID `appsid_24092026_0901` (171450–171757) | — (droplet; `results/` lokal hanya punya run-folder 27092026) | ❌ Tidak tersinkron |
| Plot kandidat appsid 10.991 pair (171757) | `results/_eda/csv/eda_all_samples_annotated.csv` (92.074, I-I=0) | ⚠️ Tahap berbeda; 17 I-I dibuang |
| aaPanel + panduan (Screenshot.png) | `PANDUAN_SERVER_JUPYTER_AAPANEL.md`, `STEP_BY_STEP_AMD_GPU_JUPYTER_AAPANEL.md` | ✅ Dokumen sepadan |
| GPU telemetri (014/017) | `docs/0007_analisis_konfigurasi_gpu_mi300x…`, `GPU_Status.ipynb` | ✅ Konteks keputusan no-early-stopping |

---

## 4. Temuan Kritis

1. **Dua mode kegagalan Step-2 yang berbeda sudah terlihat hari itu**: (a) REST16 latih-langsung → semua epoch F1 0,0 dengan `tp=fp=0` (155609); (b) REST16 cache-hit sesi lama → `tp=0, fp=165.728` (161430). Keduanya mendahului gelombang CV appsid 27092026 yang menghasilkan F1 100% degenerat (`reports/038`). **Step-2 adalah titik lemah sistemik, bukan nasib buruk CV.**
2. **Kontrol Inggris berhasil di Step-1 (80,76%)** — membuktikan arsitektur BERT-CRF + pipeline pasangan berfungsi; kegagalan terisolasi di kepala Step-2/persiapan datanya (dan gold "2 entri" yang janggal, 161138).
3. **Pencampuran domain di sesi Colab** (preview "REST16" berisi teks Indonesia, 161017) + **pergantian lingkungan tiga kali** (droplet MI300X → Colab T4 → droplet) dalam satu notebook yang sama — sumber kebingungan path/state yang konsisten dengan bug lintas-mesin di `reports/038` §5.
4. **Pemanfaatan MI300X sangat rendah**: VRAM terpakai 475 MB dari 191,69 GB; utilitas memori puncak 9%; dua burst 350 W di antara idle 140 W. Untuk $1,99/jam, hari itu pada dasarnya membeli GPU supercepat untuk kerja yang muat di T4 — kecuali jika memang bertujuan uji-kinerja (docs 0007/0008).
5. **Risiko keamanan nyata**: JupyterLab & aaPanel terbuka di IP publik lewat HTTP ("Not secure" di address bar), dialog sim-sandi Chrome menampilkan akun, dan token Jupyter tertera di URL (160130). Tidak terlihat di gambar bahwa akses ini sudah ditutup.
6. **Versi citra tidak konsisten**: nama droplet "PyTorch 2.10.0 (ROCm 7.2.4)" vs MOTD "PyTorch 2.12.0+rocm7.14.0" — perlu dicatat agar jejak reproduksibilitas tidak salah label.
7. **17 kandidat double-implicit appsid dibuang** sebelum menjadi dataset final (I-I=0 di semua artefak) — keputusan pipeline yang belum terdokumentasi di VERSI manapun; screenshot ini adalah satu-satunya jejaknya.

---

## 5. Kesimpulan

Screenshot membuktikan bahwa pada 24092026 proyek mencapai: provisioning GPU penuh, validasi silang EDA dua domain, **keberhasilan Step-1 di kontrol Inggris**, pembangunan tokenisasi v5_en, dan kesiapan penuh Step-2 APPSID 50-epoch — sekaligus merekam **akar masalah Step-2 (F1 0 / FP meledak / gold 2 entri)** yang kemudian menjelma menjadi 94 run ERROR di hari 27092026. Artefak paling bernilai dari hari itu (checkpoint 80,76% dan 57 berkas Drive) hingga kini **tidak tersinkron ke repo lokal** — prioritas sinkronisasi utama bersama `appsid_08092026_150437` (laporan 041 §5.4).

---

*Seluruh angka dikutip langsung dari teks yang terbaca di 31 gambar; tidak ada gambar yang dilewati. Nomor gambar disebut dengan format `Screenshot 2026-09-24 HHMMSS.png` atau `FireShot Capture 0xx` sesuai isi folder `screenshot/`.*
