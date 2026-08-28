# Rencana Implementasi: Sistem Multi-Tier Caching & Auto-Recovery untuk `00*PRO.ipynb`

Dokumen ini menjelaskan rancangan teknis dan panduan pembaruan menyeluruh untuk notebook **`00_ACOS_Master_Pipeline_Colab_PRO.ipynb`** (dan varian resume-nya) agar **setiap tahapan cell menyimpan hasilnya ke media persisten**, dan **cell berikutnya secara cerdas memanggil hasil yang ada** (baik dari memori runtime maupun auto-search ke penyimpanan sebelumnya).

---

## 1. Prinsip Utama (Core Architecture)

1. **Simpan Hasil Setiap Tahap (Checkpoint-on-Completion)**:
   - Setiap sel yang memproses data/melatih model/mengevaluasi wajib langsung menyimpan hasilnya ke disk (`pickle`, `CSV`, `JSON`, `model weights .bin`, atau `PNG`).
   - Objek status global diperbarui melalui fungsi tersentralisasi `save_pipeline_state()`.

2. **Panggil Hasil yang Ada / Auto-Restore (Smart Check & Fallback)**:
   - Setiap sel memeriksa ketersediaan objek di memori (`globals()`).
   - Jika variabel hilang (misal akibat *kernel restart*, *timeout*, atau *reconnect* Colab), sel otomatis mencari dan memuat file hasil dari:
     1. Direktori sesi aktif (`session_dirs`).
     2. File `pipeline_state.pkl` sesi aktif.
     3. Sesi terakhir yang tersimpan di Google Drive (`/content/drive/MyDrive/ACOS/Output/results`) atau direktori lokal `./results` / `./Output/results`.
   - Menghilangkan `NameError` dan mencegah pengulangan komputasi berulang.

3. **Toggle Force-Execution (`FORCE_RETRAIN` / `FORCE_REEVAL`)**:
   - Disediakan flag boolean di awal sel kritis:
     - `FORCE_RETRAIN_STEP1 = False` (default: jika model sudah ada, lewati training dan gunakan checkpoint terbaik).
     - `FORCE_RETRAIN_STEP2 = False` (default: jika model sudah ada, lewati training).
     - `FORCE_REEVAL = False` (default: jika metrik sudah dievaluasi, muat hasil JSON).
   - Pengguna tetap memiliki kontrol penuh untuk melatih ulang kapan saja hanya dengan mengubah flag menjadi `True`.

---

## 2. Peta Alur Caching & Auto-Recovery Tiap Sel

| Nomor Sel | Nama Tahapan | Output yang Disimpan | Mekanisme Pengecekan & Fallback Pemanggilan |
| :--- | :--- | :--- | :--- |
| **Sel 2** | Setup & GPU Diagnostics | Device, CUDA config | Deteksi lingkungan (Colab vs Lokal) otomatis |
| **Sel 4** | Path & Navigation | `base_project_dir`, `extract_dir`, `save_dir` | Mencari root direktori aktif & clone repo jika belum ada |
| **Sel 6** | Parameter & State Init | `session_dirs`, `bert_cache_dir`, `pipeline_state.pkl`, `session_manifest.json` | Membaca sesi aktif atau membuat direktori timestamp baru; inisialisasi helper `save_pipeline_state()` dan `ensure_objects()` |
| **Sel 8** | Exploratory Data Analysis (EDA) | `df_stats`, `df_records`, `eda_plots/*.png`, `master_01_statistik_dataset.csv` | **Cek Memori/Disk**: Jika CSV/Plot EDA sudah ada di sesi, muat langsung. Jika belum, jalankan `analyze_and_plot_eda()` dan simpan |
| **Sel 10**| Diagnostik Data | Log struktur folder data | Cek keberadaan `Restaurant-ACOS` dan `tokenized_data` |
| **Sel 12**| **Step 1: Aspect & Opinion Co-Extraction (BERT-CRF)** | `checkpoints/step1_best/pytorch_model.bin`, `config.json`, `vocab.txt`, `pred4pipeline.txt`, `step1_training_history.csv`, Plot loss/F1 curve | **Cek Status**: Jika checkpoint Step 1 dan `pred4pipeline.txt` sudah ada (dan `FORCE_RETRAIN_STEP1=False`), langsung muat riwayat F1 & lewati 15 epoch training. Jika belum ada, lakukan training dan simpan model terbaik per epoch |
| **Sel 14**| **Smart State Checkpoint Saver** | `pipeline_state.pkl` (berisi config, paths, runtime variables, status tahapan selesai) | Menyimpan snapshot lengkap ke file pickle & JSON label |
| **Sel 16**| **Smart State Recovery** | Memulihkan seluruh variabel global | Mencari file `.pkl` terbaru di Drive/Lokal dan memuat kembali semua konfigurasi dan objek |
| **Sel 18**| **Jaminan Objek Runtime (`ensure_objects`)** | Tokenizer, label lists, num_labels, args_h | Memastikan variabel esensial tidak pernah `None` atau `NameError` sebelum sel berikutnya dieksekusi |
| **Sel 20**| **Candidate Pair Generation Bridge** | `candidate_pairs_summary.csv`, `{DOMAIN}_test_pair_1st.tsv`, `04_candidate_pairs_distribution.png` | **Cek Status**: Jika file pasangan kandidat sudah terbentuk, muat `df_pairs`. Jika belum, baca `pred4pipeline.txt` (dari Step 1 aktif atau sesi lama) dan buat pasangannya |
| **Sel 22**| **Step 2: Category & Sentiment Classification** | `checkpoints/step2_best/pytorch_model.bin`, `config.json`, `step2_training_history.csv`, Plot loss/F1 curve | **Cek Status**: Jika checkpoint Step 2 sudah ada (dan `FORCE_RETRAIN_STEP2=False`), langsung muat riwayat F1 & lewati training. Jika belum ada, jalankan training |
| **Sel 24**| **Final Evaluation & 15 Sub-Tasks Dashboard** | `master_metrics.json`, `05_benchmark_subtasks_f1.png`, `master_07_metrik_quadruple_final.csv`, `master_08_metrik_subtask.csv` | **Cek Status**: Jika `master_metrics.json` sudah ada (dan `FORCE_REEVAL=False`), tampilkan tabel dan dashboard visual langsung dari file |
| **Sel 26**| **Live Interactive Inference** | Hasil prediksi ulasan bebas (`df_infer`), `master_10_contoh_inferensi.csv` | Otomatis memuat model Step 1 & Step 2 terbaik dari checkpoint folder jika belum ada di memori |
| **Sel 28**| **Ringkasan Artefak & Laporan Akhir** | `00_master_pipeline.md`, `master_11_daftar_artefak.csv`, `session_manifest.json` (FINISHED) | Mengompilasi seluruh file hasil sesi menjadi laporan Markdown komprehensif |

---

## 3. Detail Implementasi Kode per Sel

### A. Fungsi State Manager & Jaminan Objek (Cell 6 & Cell 18)
```python
def save_pipeline_state(extra_runtime=None):
    """Menyimpan seluruh parameter, path direktori, dan artefak runtime ke pipeline_state.pkl"""
    state_file = os.path.join(session_dirs["root"], "pipeline_state.pkl")
    completed_stages = []
    if os.path.exists(os.path.join(session_dirs["csv"], "master_01_statistik_dataset.csv")):
        completed_stages.append("EDA")
    if os.path.exists(os.path.join(session_dirs["step1_checkpoint"], "pytorch_model.bin")):
        completed_stages.append("STEP1")
    if os.path.exists(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")):
        completed_stages.append("PAIRS")
    if os.path.exists(os.path.join(session_dirs["step2_checkpoint"], "pytorch_model.bin")):
        completed_stages.append("STEP2")
    if os.path.exists(os.path.join(session_dirs["logs"], "master_metrics.json")):
        completed_stages.append("FINAL_EVAL")
        
    state_data = {
        "DOMAIN": DOMAIN, "base_project_dir": base_project_dir,
        "extract_dir": extract_dir, "data_root": data_root,
        "bert_cache_dir": bert_cache_dir, "session_dirs": session_dirs,
        "MAX_SEQ_LENGTH": MAX_SEQ_LENGTH, "NUM_EPOCHS": NUM_EPOCHS,
        "STEP1_BATCH_SIZE": STEP1_BATCH_SIZE, "STEP2_BATCH_SIZE": STEP2_BATCH_SIZE,
        "STEP1_LR": STEP1_LR, "STEP2_LR": STEP2_LR, "SEED": SEED,
        "completed_stages": completed_stages,
        "runtime": {
            "best_step1_f1": globals().get("best_step1_f1"),
            "best_step2_f1": globals().get("best_step2_f1"),
            "pakai_1st": globals().get("pakai_1st", True),
        }
    }
    if extra_runtime:
        state_data["runtime"].update(extra_runtime)
    with open(state_file, "wb") as f:
        pickle.dump(state_data, f)
    return state_file
```

### B. Auto-Skip & Load pada Step 1 (Aspect & Opinion Extraction) (Cell 12)
```python
FORCE_RETRAIN_STEP1 = False  # Ubah ke True jika ingin melatih ulang dari awal

step1_ckpt = session_dirs["step1_checkpoint"]
step1_bin = os.path.join(step1_ckpt, "pytorch_model.bin")
step1_csv = os.path.join(session_dirs["csv"], "step1_training_history.csv")
pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")

if not FORCE_RETRAIN_STEP1 and os.path.exists(step1_bin) and os.path.exists(pred_file):
    print(f"⏩ [CACHE HIT] Checkpoint Step 1 ditemukan di: {step1_ckpt}")
    print(f"   Model terbaik dan pred4pipeline.txt sudah siap. Melewati proses training.")
    if os.path.exists(step1_csv):
        df_s1_saved = pd.read_csv(step1_csv)
        step1_history = df_s1_saved.to_dict('records')
        best_step1_f1 = df_s1_saved["micro-F1"].max() / 100.0 if "micro-F1" in df_s1_saved else 0.0
        print(f"   Micro-F1 Step 1 terbaik dari cache: {best_step1_f1*100:.2f}%")
else:
    print(f"🚀 Memulai Training Step 1 BERT-CRF ({NUM_EPOCHS} Epochs pada {device})...")
    # ... Training loop ...
    # Simpan checkpoint & history ...
```

### C. Auto-Skip & Load pada Candidate Pairs Bridge (Cell 20)
```python
candidate_csv = os.path.join(session_dirs["csv"], "candidate_pairs_summary.csv")
target_tokenized_tsv = os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")

if os.path.exists(candidate_csv) and os.path.exists(target_tokenized_tsv):
    print(f"⏩ [CACHE HIT] Pasangan kandidat sudah ada di: {target_tokenized_tsv}")
    df_pairs = pd.read_csv(candidate_csv)
    print(f"   Total {len(df_pairs)} pasangan berhasil dimuat dari cache.")
else:
    # Cek lokasi pred4pipeline.txt jika belum ada di sesi aktif
    if not os.path.exists(pred_file):
        # Fallback cari ke sesi sebelumnya
        found_pred = auto_find_file("pred4pipeline.txt", search_roots=[results_base, "/content/drive/MyDrive/ACOS/Output/results"])
        if found_pred:
            shutil.copy(found_pred, pred_file)
    # Generate pasangan kartesian dan simpan TSV + CSV
```

### D. Auto-Skip & Load pada Step 2 (Category & Sentiment Classification) (Cell 22)
```python
FORCE_RETRAIN_STEP2 = False

step2_ckpt = session_dirs["step2_checkpoint"]
step2_bin = os.path.join(step2_ckpt, "pytorch_model.bin")
step2_csv = os.path.join(session_dirs["csv"], "step2_training_history.csv")

if not FORCE_RETRAIN_STEP2 and os.path.exists(step2_bin) and os.path.exists(step2_csv):
    print(f"⏩ [CACHE HIT] Checkpoint Step 2 ditemukan di: {step2_ckpt}")
    print(f"   Model terbaik sudah siap. Melewati proses training Step 2.")
    df_s2_saved = pd.read_csv(step2_csv)
    step2_history = df_s2_saved.to_dict('records')
    best_step2_f1 = df_s2_saved["micro-F1"].max() / 100.0 if "micro-F1" in df_s2_saved else 0.0
    print(f"   Micro-F1 Step 2 terbaik dari cache: {best_step2_f1*100:.2f}%")
else:
    print(f"🚀 Memulai Training Step 2 Klasifikasi Kategori & Sentimen ({NUM_EPOCHS} Epochs pada {device})...")
    # ... Training loop & simpan model terbaik ...
```

### E. Auto-Load pada Final Evaluation (Cell 24)
```python
FORCE_REEVAL = False
metrics_json = os.path.join(session_dirs["logs"], "master_metrics.json")

if not FORCE_REEVAL and os.path.exists(metrics_json):
    print(f"⏩ [CACHE HIT] Memuat hasil evaluasi lengkap dari: {metrics_json}")
    with open(metrics_json, "r", encoding="utf-8") as jf:
        cached_eval = json.load(jf)
    final_res = cached_eval.get("overall", {})
    subtask_metrics = cached_eval.get("subtasks", {})
else:
    # Muat model_step2_best dari checkpoint dan jalankan pair_eval
```

---

## 4. Keuntungan & Manfaat

1. **Tahan Gangguan (Crash/Disconnect Resilient)**:
   Jika Google Colab terputus setelah melatih Step 1, pengguna cukup menghubungkan kembali runtime, menjalankan sel Recovery (Cell 16 & 18), dan langsung melanjutkan ke Step 2 tanpa harus menunggu Step 1 dilatih ulang.
2. **Efisiensi Waktu & Kuota GPU**:
   Tidak ada lagi komputasi yang terbuang sia-sia karena setiap model bobot, metrik, dan file perantara selalu tersimpan di Google Drive / disk lokal.
3. **Fleksibilitas Tinggi**:
   Jika ingin melakukan eksperimen baru dari awal, cukup ubah flag `FORCE_RETRAIN_STEP1 = True` atau `FORCE_RETRAIN_STEP2 = True`.
4. **Reproduksibilitas & Transparansi**:
   File `pipeline_state.pkl` dan `session_manifest.json` menyimpan riwayat eksekusi lengkap yang dapat dibaca oleh skrip otomatisasi maupun evaluasi manusia.

---

## 5. Rencana Eksekusi Pembaruan File

- Target Berkas:
  - [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb)
  - [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb)
- Uji Validitas Sintaks Python & Struktur JSON Notebook dengan skrip verifikasi otomatis.
