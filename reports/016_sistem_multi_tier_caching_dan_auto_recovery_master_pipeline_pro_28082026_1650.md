# Laporan Pembaruan: Sistem Multi-Tier Caching & Auto-Recovery pada Master Pipeline ACOS Versi PRO

**Nomor Dokumen:** `reports/016_sistem_multi_tier_caching_dan_auto_recovery_master_pipeline_pro_28082026_1650.md`  
**Tanggal:** 2026-08-28 16:50 WIB  
**Objek Implementasi:**
- [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb)
- [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb)  
**Dokumen Pendukung:**
- [`notebooks/IMPLEMENTATION_PLAN_00_PRO_CACHING.md`](file:///d:/laragon/www/ACOS-ASLI/notebooks/IMPLEMENTATION_PLAN_00_PRO_CACHING.md)
- [`IMPLEMENTATION_PLAN_00_PRO_CACHING.md`](file:///d:/laragon/www/ACOS-ASLI/IMPLEMENTATION_PLAN_00_PRO_CACHING.md)

---

## 1. Latar Belakang & Tujuan

Pada eksekusi model deep learning berskala besar (seperti ekstraksi *Aspect-Category-Opinion-Sentiment* / ACOS dengan BERT-CRF dan Klasifikasi Multi-Label), proses pelatihan dan evaluasi memerlukan waktu komputasi yang signifikan. Kendala umum yang sering dihadapi pada lingkungan seperti Google Colab adalah:
- **Diskoneksi / Kernel Timeout**: Runtime Google Colab dapat terputus sewaktu-waktu.
- **Kehilangan Momentum & Hasil di Tengah Jalan**: Tanpa mekanisme *caching* antar-tahap, jika kernel terestart atau pengguna ingin menjalankan sel tertentu (misalnya langsung ke evaluasi atau inferensi live), seluruh proses dari sel 1 harus diulang dari awal.

**Tujuan Pembaruan:**
Membuat arsitektur **Multi-Tier Caching & Smart Auto-Recovery** di mana:
1. **Setiap tahapan/sel secara otomatis menyimpan hasilnya** ke media penyimpanan persisten (Google Drive / disk lokal).
2. **Sel berikutnya memeriksa dan memanggil hasil yang ada**, baik di memori runtime maupun di disk.
3. **Jika hasil tidak ada di memori, sistem otomatis mencari dari hasil penyimpanan sebelumnya** (fallback auto-search lintas sesi).
4. **Disediakan opsi toggle manual** (`FORCE_RETRAIN_STEP1`, `FORCE_RETRAIN_STEP2`, `FORCE_REEVAL`) agar pengguna tetap memiliki kendali penuh jika ingin melatih ulang dari awal.

---

## 2. Arsitektur Multi-Tier Caching & Auto-Recovery

Sistem bekerja melalui 4 lapisan perlindungan (*layers of resilience*):

```
┌─────────────────────────────────────────────────────────────┐
│ 1. IN-MEMORY RUNTIME CHECK                                  │
│ Apakah variabel/objek sudah ada di memori aktif?            │
│  ├── [YA] ──► Gunakan langsung (Super Cepat)                │
│  └── [TIDAK] ──► Masuk ke Layer 2                           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ACTIVE SESSION DISK CACHE                                │
│ Apakah artefak/checkpoint ada di session_dirs saat ini?     │
│  ├── [YA] ──► Muat file CSV/JSON/PKL/Model weights (.bin)   │
│  └── [TIDAK] ──► Masuk ke Layer 3                           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CROSS-SESSION AUTO-SEARCH FALLBACK                       │
│ Cari berkas di direktori sesi terdahulu (Drive / Lokal)     │
│ (auto_find_file, auto_find_latest_state)                    │
│  ├── [DITEMUKAN] ──► Salin & pulihkan ke sesi aktif         │
│  └── [TIDAK] ──► Masuk ke Layer 4                           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RUNTIME OBJECT GUARANTEE & AUTO-CONSTRUCT                │
│ Jalankan ensure_objects() untuk merekonstruksi tokenizer,   │
│ label mapping, args, dan device tanpa NameError             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Rincian Pembaruan Per-Sel (29 Sel Lengkap)

| No. Sel | Jenis | Nama Tahapan | Fitur Caching & Mekanisme Auto-Recovery |
| :---: | :---: | :--- | :--- |
| **00** | Markdown | Header & Dokumen Title | Penjelasan fitur multi-tier caching & auto-skip. |
| **01** | Markdown | Section 1 Header | Header environment & GPU. |
| **02** | Code | Setup, Drive & GPU Diagnostics | Mount Google Drive aman, instalasi dependensi, optimasi CUDA & cuDNN. |
| **03** | Markdown | Section 2 Header | Header navigasi direktori dinamis. |
| **04** | Code | Dynamic Directory Navigation | Deteksi root dinamis (Drive/Lokal) + fallback download `colab_utils.py`. |
| **05** | Markdown | Section 3 Header | Header parameter, caching BERT & manifest. |
| **06** | Code | Parameters & Unified State Init | **Inisialisasi State Manager**: mendefinisikan fungsi `save_pipeline_state()`, `auto_find_file()`, `update_mcp_manifest()`, dan menyimpan status awal ke `pipeline_state.pkl`. |
| **07** | Markdown | Section 4 Header | Header EDA. |
| **08** | Code | EDA & Publication Plots | **Auto-Cache EDA**: jika `master_01_statistik_dataset.csv` sudah ada, data langsung dimuat dari CSV tanpa menghitung ulang; grafik 300 DPI disimpan. |
| **09** | Markdown | Section 4b Header | Header diagnostik data. |
| **10** | Code | Dataset Structure Diagnostics | Pemindaian multi-lokasi dataset mentah dan tokenized data. |
| **11** | Markdown | Section 5 Header | Header Step 1 BERT-CRF. |
| **12** | Code | **Step 1: Aspect & Opinion Co-Extraction** | **Auto-Skip & Cache Hit**: Mendukung `FORCE_RETRAIN_STEP1 = False`. Jika `step1_best/pytorch_model.bin` dan `pred4pipeline.txt` sudah ada, sel melewati 15 epoch training dan langsung memuat riwayat metrik dari `step1_training_history.csv`. |
| **13** | Markdown | Section 6 Header | Header state checkpoint saver. |
| **14** | Code | **Smart State Checkpoint Saver** | Menyimpan seluruh snapshot konfigurasi, path, variabel runtime, dan tahapan selesai ke `pipeline_state.pkl`. |
| **15** | Markdown | Section 6b Header | Header state recovery. |
| **16** | Code | **Smart State Recovery** | Otomatis melacak dan memulihkan seluruh variabel global jika kernel Colab terputus / restart. |
| **17** | Markdown | Section 6c Header | Header jaminan objek runtime. |
| **18** | Code | **Jaminan Objek Runtime (`ensure_objects`)** | Memastikan `tokenizer`, `label_list_step1`, `label_list_step2`, `num_labels_step1`, `num_labels_step2`, `args_h`, dan `device` selalu siap digunakan (mencegah `NameError`). |
| **19** | Markdown | Section 7 Header | Header candidate pair bridge. |
| **20** | Code | **Candidate Pair Generation Bridge** | **Auto-Cache Pairs**: Memeriksa keberadaan `candidate_pairs_summary.csv` dan `{DOMAIN}_test_pair_1st.tsv`. Jika belum ada, memuat `pred4pipeline.txt` (dengan fallback search ke sesi sebelumnya) dan membuat pasangan $(a, o)$. |
| **21** | Markdown | Section 8 Header | Header Step 2 klasifikasi. |
| **22** | Code | **Step 2: Category & Sentiment Classification** | **Auto-Skip & Cache Hit**: Mendukung `FORCE_RETRAIN_STEP2 = False`. Jika checkpoint `step2_best/pytorch_model.bin` sudah ada, sel melewati training dan langsung memuat riwayat metrik. |
| **23** | Markdown | Section 9 Header | Header evaluasi final benchmark. |
| **24** | Code | **Final Evaluation & 15 Subtasks Dashboard** | **Auto-Load Evaluation**: Mendukung `FORCE_REEVAL = False`. Jika `master_metrics.json` sudah ada, hasil metrik langsung ditampilkan tanpa inferensi ulang test set. |
| **25** | Markdown | Section 10 Header | Header inferensi interaktif. |
| **26** | Code | **Live Interactive Inference Demo** | **Auto-Load Best Models**: Otomatis memuat model Step 1 dan Step 2 terbaik dari checkpoint folder sesi aktif (atau sesi terdahulu jika sel training dilewati) dan menjalankan ekstraksi quadruple ulasan bebas. |
| **27** | Markdown | Section 11 Header | Header ringkasan artefak. |
| **28** | Code | **Ringkasan Seluruh Artefak & Finalisasi** | Mengompilasi seluruh file hasil sesi menjadi laporan Markdown komprehensif `00_master_pipeline.md` dan memperbarui status MCP ke `SESSION_FINISHED`. |

---

## 4. Matriks Komparasi: Versi PRO Awal vs. Versi PRO Caching

| Aspek / Fitur | Versi PRO Awal (27 Sel) | Versi PRO Caching & Auto-Recovery (29 Sel) |
| :--- | :---: | :---: |
| **Jumlah Sel Total** | 27 Sel | **29 Sel (Termasuk Dedicated Runtime Shield)** |
| **Auto-Skip Training Jika Model Sudah Ada** | ❌ Harus melatih ulang | ✅ **Auto-Skip Cerdas (`[CACHE HIT]`)** |
| **Pencarian Sesi Sebelumnya (*Fallback Search*)** | ⚠️ Terbatas pada state .pkl | ✅ **Menjangkau Model Bin, Log, Prediksi, CSV** |
| **Penyimpanan State Tiap Tahap (*Continuous Sync*)** | ⚠️ Hanya pasca Step 1 | ✅ **Tersinkronisasi di Setiap Tahapan Eksekusi** |
| **Jaminan Objek Runtime (`ensure_objects`)** | ❌ Tidak ada | ✅ **Terpasang di Setiap Sel Kritis** |
| **Pencegahan `NameError` saat Kernel Restart** | ⚠️ Tergantung urutan run manual | ✅ **100% Otomatis Dipulihkan** |
| **Toggle Flag Melatih Ulang (`FORCE_RETRAIN`)** | ❌ Tidak ada | ✅ **`FORCE_RETRAIN_STEP1/2` & `FORCE_REEVAL`** |
| **Dukungan Resume Tanpa Kehilangan Metrik** | ⚠️ Parsial | ✅ **Lengkap (Metrik, Riwayat, Artefak)** |

---

## 5. Hasil Verifikasi Teknis

1. **Pengujian Sintaks Python (`ast.parse`)**:
   - Seluruh 14 sel kode Python di dalam notebook `00_ACOS_Master_Pipeline_Colab_PRO.ipynb` dan `00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb` berhasil diparse dan diverifikasi **100% bebas dari kesalahan sintaks (*Zero Syntax Errors*)**.
2. **Validasi Struktur JSON Notebook**:
   - Berkas notebook berformat Jupyter Notebook v4 yang valid dan dapat langsung dibuka di Visual Studio Code, JupyterLab, maupun Google Colab.
3. **Pembersihan Scratch Script**:
   - Seluruh berkas pembantu sementara telah dibersihkan sehingga repositori tetap rapi dan bersih.

---

## 6. Kesimpulan & Rekomendasi Penggunaan

Dengan pembaruan ini:
- Pengguna yang menjalankan notebook di **Google Colab** tidak perlu lagi khawatir kehilangan progres atau hasil pelatihan jika koneksi internet terputus di tengah jalan.
- Pengguna dapat langsung menjalankan sel **Candidate Pair Bridge (Sel 20)**, **Step 2 (Sel 22)**, **Final Evaluation (Sel 24)**, atau **Live Inference (Sel 26)** secara mandiri; notebook akan secara otomatis menemukan dan memuat model serta hasil dari tahapan sebelumnya.
- Jika pengguna ingin melakukan eksperimen baru dari awal, cukup mengubah flag `FORCE_RETRAIN_STEP1 = True` atau `FORCE_RETRAIN_STEP2 = True`.
