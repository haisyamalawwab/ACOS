# Walkthrough: Resume Training Per-Epoch pada Notebook ACOS-IndoBERT

**File Target:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`  
**Tanggal:** 2026-09-06  
**Status:** Selesai Diimplementasikan ✅  

---

## 1. Ringkasan Fitur

Notebook kini mendukung mekanisme **Resume Training Per-Epoch**. Jika koneksi Google Colab terputus, sesi timeout, atau runtime restart saat training berlangsung, training dapat dilanjutkan dari epoch terakhir yang selesai tanpa mengulang dari epoch 1.

---

## 2. Rincian Sel yang Dimodifikasi

| Sel | Tahap Pipeline | Perubahan Utama |
|---|---|---|
| **Cell 36** | `5b. Deteksi cache Step 1` | Memeriksa `step1_resume.json` (pada folder log sesi aktif maupun sesi sebelumnya via `auto_find_file`). Jika ditemukan proses terhenti di epoch $N < \text{NUM\_EPOCHS}$, variabel `STEP1_RESUME_EPOCH` diset ke $N$ dan `STEP1_SKIP_TRAINING` di-override menjadi `False`. |
| **Cell 44** | `5e. Training Step 1` | • Memulihkan bobot model (`pytorch_model.bin`) dan momentum optimizer (`optimizer.pt`) dari epoch terakhir.<br>• Melanjutkan loop training dari `epoch + 1` hingga `NUM_EPOCHS`.<br>• Menyimpan **rolling checkpoint** per epoch dan mengupdate `step1_resume.json`.<br>• Otomatis menghapus checkpoint epoch sebelumnya (`epoch - 1`) untuk menghemat storage.<br>• Menghapus rolling checkpoint final saat training selesai 100%. |
| **Cell 61** | `8b. Deteksi cache Step 2` | Logika deteksi resume identik dengan Step 1, khusus untuk Step 2 Category-Sentiment Extraction (`step2_resume.json` dan `step2_epoch_{N}`). |
| **Cell 67** | `8e. Training Step 2` | Rolling checkpoint, restore bobot model + optimizer, update riwayat, dan auto-cleanup untuk Step 2. |

---

## 3. Struktur Berkas Checkpoint & Log Baru

Ketika training berjalan, direktori output sesi menghasilkan struktur berikut:

```
Output/results/{SESSION_ID}/
├── checkpoints/
│   ├── step1_best/                   # Model terbaik berdasarkan validasi Micro-F1 (tetap dipertahankan)
│   │   ├── pytorch_model.bin
│   │   ├── config.json
│   │   └── vocab.txt
│   ├── step1_epoch_{N}/              # Rolling checkpoint epoch N (hanya 1 epoch terbaru yang disimpan)
│   │   ├── pytorch_model.bin
│   │   └── optimizer.pt
│   ├── step2_best/                   # Model Step 2 terbaik
│   └── step2_epoch_{N}/              # Rolling checkpoint Step 2 epoch N
└── logs/
    ├── step1_resume.json             # Metadata status resume Step 1
    └── step2_resume.json             # Metadata status resume Step 2
```

### Struktur `step1_resume.json` / `step2_resume.json`:

```json
{
  "last_completed_epoch": 7,
  "total_epochs": 15,
  "best_micro_f1": 0.4321,
  "best_epoch": 5,
  "history": [ ... ],
  "saved_at": "2026-09-06T20:15:00.000000"
}
```

---

## 4. Alur Penggunaan (Workflow)

```
[Sesi 1: Training Berjalan]
       │
       ▼
 Epoch 1 → 2 → ... → 7 selesai
 (Tersimpan: checkpoints/step1_epoch_7/ & logs/step1_resume.json)
       │
       ▼
 [Koneksi Colab Putus / Runtime Disconnect]
       │
       ▼
[Sesi 2: Reconnect & Buka Notebook]
 1. Jalankan sel persiapan (1b, 2c, 3, 4c, 4d, 5a, 5b)
 2. Cell 5b mendeteksi:
    "♻️ [RESUME] Step 1 terhenti di epoch 7/15. Akan dilanjutkan dari epoch 8."
 3. Cell 5e otomatis memuat:
    - Model weights dari epoch 7
    - Optimizer state dari epoch 7
    - Melanjutkan range(8, 16)
 4. Setelah epoch 15 selesai:
    - Checkpoint rolling dibersihkan
    - step1_best/ siap digunakan untuk Step 2 & evaluasi
```

---

## 5. Kompatibilitas & Pengendalian Manual

- **Training Normal / Awal**: Jika file `step1_resume.json` belum ada, training dimulai normal dari epoch 1.
- **Paksa Ulang dari Awal**: Jika ingin mengabaikan checkpoint resume dan melatih ulang dari epoch 1, cukup set flag:
  ```python
  FORCE_RETRAIN_STEP1 = True
  # atau
  FORCE_RETRAIN_STEP2 = True
  ```
- **Proteksi Perubahan Epoch**: Jika konfigurasi `NUM_EPOCHS` diubah di tengah jalan (misal dari 15 ke 20), script akan memberi peringatan dan melatih dari awal untuk mencegah inkonsistensi scheduler.

---

## 6. Verifikasi & Pengujian

- **Validasi Sintaks AST**: Sel 36, 44, 61, dan 67 telah divalidasi dengan `ast.parse` tanpa ada error sintaks.
- **Status Berkas**: Notebook `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` telah tersimpan dengan rapi.
