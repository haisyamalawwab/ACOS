# Laporan Pengembangan: Sistem Inspeksi Folder Spesifik Google Drive & Pencegahan Salah Simpan/Load

**Nomor Dokumen:** `reports/019_sistem_inspeksi_folder_drive_dan_pencegahan_salah_simpan_load_29082026_1700.md`  
**Tanggal:** 2026-08-29 17:00 WIB  
**Status:** Selesai & Terverifikasi (Production Ready)  
**Objek Implementasi:**
- [`notebooks/colab_utils.py`](file:///d:/laragon/www/ACOS-ASLI/notebooks/colab_utils.py)
- [`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb)
- [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb)

---

## 1. Latar Belakang & Kebutuhan

Saat mengeksekusi pipeline deep learning ACOS pada Google Colab dengan integrasi Google Drive (`/content/drive/MyDrive`), terdapat potensi risiko operasional sebagai berikut:
1. **Risiko Salah Simpan (*Save Path Misplacement*)**: Output sesi, checkpoint, dan visualisasi tersimpan ke direktori sementara (*ephemeral storage* `/content`) alih-alih Google Drive persisten, sehingga seluruh hasil pelatihan hilang saat runtime Colab *timeout* atau terputus.
2. **Risiko Salah Muat (*Stale/Wrong Session Load*)**: Ketika pengguna memiliki beberapa sesi terdahulu dari domain berbeda (misalnya ulasan laptop `laptop` vs ulasan restoran `rest16`), mekanisme pemulihan otomatis (*auto-recovery*) yang tidak memiliki filter domain dapat memuat checkpoint atau pasangan kandidat dari domain yang salah.
3. **Kebutuhan Visibilitas & Audit Folder Drive**: Pengguna membutuhkan visibilitas menyeluruh terhadap folder-folder spesifik di Google Drive (Dataset mentah, Pretrained BERT Cache, Checkpoint Step 1/Step 2, Hasil Prediksi, dan Metrik 15 Sub-Tasks) sebelum dan sesudah eksekusi.

---

## 2. Arsitektur Solusi & Fitur Baru

Untuk menjamin keandalan penyimpanan dan pemuatan artefak, diimplementasikan 5 lapis pengamanan (*5 layers of path & storage resilience*):

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. DYNAMIC DRIVE ROOT DISCOVERY (detect_acos_project_root)             │
│ Memindai /content/drive/MyDrive/ACOS & variasinya secara otomatis       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. COMPREHENSIVE DRIVE INSPECTOR (inspect_acos_drive_structure)        │
│ Audit visual: Core Folders, Datasets, BERT Cache, Riwayat Sesi (0-6)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. MULTI-ROOT DOMAIN-SAFE RESUME (find_resumable_session)              │
│ Pencarian lintas Drive/Lokal dengan isolasi domain (rest16 != laptop)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. WRITE ACCESS PROBE & VALIDATION (verify_session_save_paths)         │
│ Uji izin tulis & konfirmasi banner persistensi Google Drive            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. RECOVERY POINTER & FINAL AUDIT (latest_pipeline_state_<domain>.pkl) │
│ Pointer 1-klik di results/ dan rekap detail seluruh file tersimpan     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detail Implementasi pada Modul `colab_utils.py`

### 3.1 `detect_acos_project_root()`
Secara cerdas mendeteksi root folder ACOS pada Google Drive (`/content/drive/MyDrive/ACOS`, `/content/drive/MyDrive/ACOS-ASLI`, atau folder lain yang memuat keyword `acos`), menguji izin tulis (*write probe*), dan mengembalikan path absolut yang valid.

### 3.2 `inspect_acos_drive_structure(base_project_dir, domain, verbose=True)`
Melakukan audit menyeluruh terhadap:
- **Folder Inti Proyek**: `Extract-Classify-ACOS`, `tokenized_data`, `data`, `bert_base_uncased`, `Output`, `results`.
- **Dataset Mentah**: Memeriksa file TSV split `train`, `dev`, dan `test` beserta ukuran file.
- **Pretrained BERT Cache**: Memastikan 3 file utama (`config.json`, `pytorch_model.bin`, `vocab.txt`) lengkap dan tidak 0-byte.
- **Riwayat Sesi Hasil (*Session History*)**: Memindai seluruh folder `<domain>_<timestamp>` di `results/` dan `Output/results/`, menghitung skor kelengkapan (*Health Score* 0–6), memverifikasi model Step 1 (>1MB), prediksi `pred4pipeline.txt`, model Step 2 (>1MB), dan metrik `master_metrics.json`.

### 3.3 `verify_session_save_paths(session_dirs, domain)`
Menguji izin tulis pada subfolder `logs`, `checkpoints`, `csv`, dan `plots`, serta menampilkan banner konfirmasi apakah output disimpan secara **PERSISTEN (Google Drive)** atau **EPHEMERAL (Lokal)**.

### 3.4 `find_resumable_session(search_dirs, domain)` & `auto_find_file(...)`
- **Domain Isolation**: Menolak folder yang bukan milik domain aktif (misal `laptop_*` tidak akan pernah dimuat saat `DOMAIN = 'rest16'`).
- **Integrity Check**: Memastikan file model memiliki ukuran valid (>1MB) agar file rusak/kosong tidak dimuat.

---

## 4. Pembaruan pada Notebook Pipeline

### 4.1 Sel Inisialisasi & Path (Section 2 - Sel 8 & 9)
- Mendeteksi ketersediaan Google Drive dan memprioritaskan penyimpanan permanen di `/content/drive/MyDrive/ACOS/Output/results`.
- Mengimpor seluruh utilitas diagnostik dan verifikasi.

### 4.2 Sel Diagnostik Folder (Section 4b - Sel 25)
- Menjalankan `inspect_acos_drive_structure(...)` yang mencetak tabel status seluruh folder inti, dataset, pretrained cache, dan daftar sesi terdahulu secara visual.

### 4.3 Sel Pemulihan Cerdas (Section 6b - Sel 42 & 43)
- Menyimpan pointer pemulihan cepat `latest_pipeline_state_<domain>.pkl` di root `results/`.
- Memulihkan state dengan prioritas path dan verifikasi kesesuaian domain.

### 4.4 Sel Audit Akhir (Section 11 - Sel 71)
- Melakukan audit akhir dan rekapitulasi seluruh file yang berhasil dibuat di dalam Google Drive lengkap dengan kategori subfolder dan ukuran filenya.

---

## 5. Ringkasan File yang Diperbarui

| File | Peran | Status |
|---|---|---|
| [`notebooks/colab_utils.py`](file:///d:/laragon/www/ACOS-ASLI/notebooks/colab_utils.py) | Modul utilitas inti inspeksi & manajemen sesi | Diperbarui & Disinkronkan |
| [`Extract-Classify-ACOS/colab_utils.py`](file:///d:/laragon/www/ACOS-ASLI/Extract-Classify-ACOS/colab_utils.py) | Salinan utilitas di folder engine model | Sinkron |
| [`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb) | Notebook produksi bertahap (72 sel bersih) | Diperbarui |
| [`notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb) | Notebook induk versi resume | Diperbarui |
