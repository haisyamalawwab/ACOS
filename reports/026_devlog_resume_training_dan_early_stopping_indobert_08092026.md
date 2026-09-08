# 026 — Dev Log: Resume Training Per-Epoch & Early Stopping untuk IndoBERT

**Tanggal:** 2026-09-08  
**File yang Diubah:**
- `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` (generator V4)
- `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (rebuilt)
- `ACOS-IndoBERT/build/_port_resume_to_v4.py` (baru, skrip portir)
- `ACOS-IndoBERT/notebooks/DEV_PLAN_resume_training_per_epoch.md` (status Draft → Selesai)

---

## 1. Latar Belakang & Masalah

### 1.1 Resume Training Per-Epoch

Fitur resume training per-epoch (rolling checkpoint + optimizer state) sudah ada di `.ipynb` V4 sejak 2026-09-06, tetapi **hanya di file .ipynb hasil patch manual**. Generator `_build_v4_indobert.py` tidak memuat fitur ini. Karena generator bersifat idempoten (menulis ulang dari nol), build berikutnya akan **menghapus fitur ini diam-diam**.

Konsekuensi: jika Colab putus di tengah training (misal epoch 7 dari 15), sesi berikutnya akan mulai dari epoch 1 lagi — membuang progres yang sudah ada.

### 1.2 Early Stopping

Training loop ACOS tidak memiliki mekanisme early stopping. Jika F1 sudah plateau (tidak membaik selama beberapa epoch berturut-turut), training tetap berjalan sampai `NUM_EPOCHS` habis. Ini memboroskan waktu Colab (terbatas 12 jam/session) tanpa manfaat konvergensi tambahan.

---

## 2. Brainstorming: Resume Training

### 2.1 Mengapa "Simpan Weight Saja" Tidak Cukup

Ada tiga level resume:

| Level | Yang Disimpan | Bisa Lanjut? | Akurasi LR Schedule? |
|---|---|---|---|
| **1. Weight saja** | `model.state_dict()` | ✅ model terlatih-sebagian | ❌ lr meloncat |
| **2. Weight + epoch** | weight + `epoch/global_step` | ✅ lanjut dari epoch berikutnya | ⚠️ hanya bila lr schedule juga diresume |
| **3. Weight + optimizer + scheduler + epoch** | semuanya | ✅ identik byte-per-byte | ✅ |

**Level 3 wajib** untuk resume "benar":
- `BertAdam` punya momentum (`state` per parameter) — tanpa optimizer state, Adam "kosong" membuat training melompat seolah di epoch 0
- LR schedule dihitung dari `t_total` (total step seluruh epoch) — resume harus tahu sudah di step ke berapa

### 2.2 Apa yang Perlu Disimpan Per Checkpoint

1. `model.state_dict()` — semua bobot (`bert.*` + head ACOS)
2. `optimizer.state_dict()` — momentum & variance Adam per-parameter
3. `global_step` / `epoch` — posisi dalam jadwal lr dan loop
4. `lr_scheduler` (implisit pada `BertAdam.get_lr`) — terikat pada `global_step`
5. `args` + `rng_state` (opsional) — reproducibility

### 2.3 Kendala pada Training Loop ACOS

Dari `run_step1.py`:
- `global_step` di-reset 0 setiap run (tidak diawetkan)
- Loop epoch tidak punya offset mulai
- `num_train_optimization_steps = ceil(len(dl)/grad_acc) * num_epochs` — dihitung saat awal; pada resume, `t_total` harus tetap = full 15 epoch (bukan sisa)
- Optimizer `BertAdam` — `state_dict()`/`load_state_dict()` berfungsi, `global_step = optimizer.state['step']` tersedia

### 2.4 Rekomendasi: Jalur 1 (Patch di Notebook Generator)

Karena training hanya jalan di Colab dan notebook V4 digenerate dari `_build_v4_indobert.py`, patch di dalam generator lebih aman daripada mengubah `run_step1.py` upstream (yang selama ini dijaga utuh).

**Struktur checkpoint:**
```
Output/results/{SESSION_ID}/
├── checkpoints/
│   ├── step1_best/                   # Model terbaik berdasarkan validasi Micro-F1
│   ├── step1_epoch_{N}/              # Rolling checkpoint epoch N (hanya 1 epoch terbaru)
│   │   ├── pytorch_model.bin
│   │   └── optimizer.pt
│   ├── step2_best/
│   └── step2_epoch_{N}/
└── logs/
    ├── step1_resume.json             # Metadata status resume Step 1
    └── step2_resume.json
```

**`step1_resume.json`:**
```json
{
  "last_completed_epoch": 7,
  "total_epochs": 15,
  "best_micro_f1": 0.4321,
  "best_epoch": 5,
  "history": [ ... ],
  "early_stopped": false,
  "stopped_at_epoch": null,
  "saved_at": "2026-09-08T20:15:00.000000"
}
```

### 2.5 Trade-off: Praktis vs Bit-Identical

Jika tujuan hanya **praktis** ("jangan buang 5 epoch karena Colab disconnect"), menyimpan `weight + optimizer + global_step` per epoch dan resume dengan `t_total` penuh sudah cukup. Bit-identical reproducibility (menyimpan RNG state dan batch offset) menambah kerumitan tanpa manfaat praktis.

**Rekomendasi:** Targetkan checkpoint level 3 per-epoch ke Drive, dan nyatakan di laporan bahwa run "resume" adalah *statistically equivalent*, bukan bit-identical dengan run tak-terputus.

---

## 3. Implementasi: Port Resume-Per-Epoch ke Generator

### 3.1 Temuan Awal

Resume-per-epoch **sudah ada** di `.ipynb` V4 (baris 2802-2862 untuk deteksi, 3377-3527 untuk training Step 1; 4251-4573 untuk Step 2), tetapi **tidak di generator**. Build berikutnya akan menghapusnya diam-diam.

### 3.2 Solusi: Port ke Generator via `RESUME_SPECS`

Skrip `ACOS-IndoBERT/build/_port_resume_to_v4.py` mem-port keempat sel resume (5b/5e/8b/8e) ke generator:
- Setiap sel diganti **UTUH** dengan isi versi teruji dari `.ipynb`
- Disuntikkan sebagai `RESUME_SPECS` di `_build_v4_indobert.py` (baris ~896)
- Langkah patch ke-14 di `apply_patches()` (baris ~675) menerapkan `RESUME_SPECS`

### 3.3 Sel yang Dimodifikasi

| Sel | Isi | Perubahan Utama |
|---|---|---|
| **5b** | Deteksi cache Step 1 | Membaca `step1_resume.json` (sesi aktif lalu sesi lama via `auto_find_file`), menghitung `STEP1_RESUME_EPOCH`, menyalin rolling checkpoint dari sesi lama bila perlu, mengabaikan bila `total_epochs != NUM_EPOCHS`, override `STEP1_SKIP_TRAINING = False` bila resume valid |
| **5e** | Training Step 1 | Restore model+optimizer dari `step1_epoch_{N}/` (map_location device/cpu), restore `step1_history`/`best_step1_f1`/`best1_epoch`, `start_epoch = resume + 1`, `tqdm(..., initial=start_epoch-1, total=NUM_EPOCHS)`, simpan rolling checkpoint per epoch, hapus epoch sebelumnya, tulis `step1_resume.json`, hapus rolling final saat selesai |
| **8b** | Deteksi cache Step 2 | Pola identik untuk `step2_resume.json` / `STEP2_RESUME_EPOCH` |
| **8e** | Training Step 2 | Pola identik untuk `model_step2` / `optimizer_2` / `step2_epoch_{N}` |

### 3.4 Verifikasi

- Build ulang notebook: 4 sel resume **byte-identik** dengan versi teruji
- Keempatnya lulus `ast.parse`
- Rebuild deterministik: MD5 `fc75723c534bbc3b41dfefd175d6ebf2` stabil di dua run
- Skrip port idempoten: run kedua = no-op

---

## 4. Brainstorming: Early Stopping

### 4.1 Kesiapan Infrastruktur

| Komponen | Status |
|---|---|
| Variabel `best_step1_f1` / `best_step2_f1` | ✅ ADA |
| Variabel `best1_epoch` / `best2_epoch` | ✅ ADA |
| History per epoch (`step1_history` / `step2_history`) | ✅ ADA |
| Perbandingan `val_f1 > best_f1` | ✅ ADA |
| Counter "epoch tanpa improvement" | ❌ BELUM ADA |
| Variabel `PATIENCE` | ❌ BELUM ADA |
| Mekanisme `break` dari loop | ❌ BELUM ADA |

### 4.2 Mekanisme Kerja

1. Setiap epoch, cek apakah `val_f1 > best_step1_f1`
2. Jika ya: reset `epochs_since_best_1 = 0`
3. Jika tidak: increment `epochs_since_best_1 += 1`
4. Setelah rolling checkpoint, cek: `epoch >= MIN_EPOCHS_BEFORE_STOP and epochs_since_best_1 >= PATIENCE`
5. Jika kondisi terpenuhi: log pesan early stopping, set flag, `break` dari loop
6. Setelah break: hapus rolling checkpoint final, update resume JSON, print pesan final

### 4.3 Parameter

- **PATIENCE**: 5 epoch (berhenti jika F1 tidak membaik selama N epoch berturut-turut)
- **MIN_EPOCHS_BEFORE_STOP**: 5 epoch (training minimal jalan N epoch dulu sebelum early stopping aktif)

---

## 5. Implementasi: Early Stopping

### 5.1 Config Cell (baris ~710)

```python
NUM_EPOCHS = 15      # 15 epoch optimal untuk Colab GPU T4/A100 (Default paper: 30)
SEED = 42

# Early Stopping: berhenti jika F1 tidak membaik selama N epoch berturut-turut
# (menghemat waktu Colab saat training sudah plateau). Set PATIENCE = 0 untuk
# menonaktifkan early stopping.
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5
```

### 5.2 Step 1 Training (sel 5e)

**Inisialisasi counter** (setelah `step1_history = []`):
```python
epochs_since_best_1 = 0
early_stopped_step1 = False
```

**Update counter** (modifikasi blok `if val_f1 > best_step1_f1`):
```python
if val_f1 > best_step1_f1:
    best_step1_f1 = val_f1
    best1_epoch = epoch
    epochs_since_best_1 = 0  # Reset
    # ... save checkpoint ...
else:
    epochs_since_best_1 += 1  # Increment
```

**Early stopping check** (setelah rolling checkpoint):
```python
if (PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and 
    epochs_since_best_1 >= PATIENCE):
    st.note(f"⏹️ Early stopping: F1 tidak membaik selama {PATIENCE} epoch "
            f"(terbaik di epoch {best1_epoch}, F1 {best_step1_f1 * 100:.2f}%)")
    early_stopped_step1 = True
    break
```

**Resume JSON** (tambahkan 2 field):
```python
"early_stopped": early_stopped_step1,
"stopped_at_epoch": epoch if early_stopped_step1 else None,
```

**Pesan final** (conditional):
```python
if early_stopped_step1:
    print(f"⏹️ Training berhenti (early stopping) di epoch {epoch}. "
          f"Micro-F1 terbaik {best_step1_f1 * 100:.2f}% pada epoch {best1_epoch}.", flush=True)
else:
    print(f"🏁 Training selesai. Micro-F1 terbaik {best_step1_f1 * 100:.2f}% "
          f"pada epoch {best1_epoch}.", flush=True)
```

### 5.3 Step 2 Training (sel 8e)

Perubahan identik dengan Step 1:
- Inisialisasi `epochs_since_best_2` dan `early_stopped_step2`
- Update counter setelah blok `if val_f1 > best_step2_f1`
- Early stopping check setelah rolling checkpoint
- Update resume JSON
- Pesan final conditional

### 5.4 Run Summary

Tambahkan field ke `step1_run_result.json` dan `step2_run_result.json`:
```python
"early_stopped": globals().get("early_stopped_step1", False),
"stopped_at_epoch": epoch if globals().get("early_stopped_step1", False) else None,
```

### 5.5 Verifikasi

- Build deterministik: MD5 `caf80401773704505f0e7de69af8d481` stabil
- AST valid untuk config, 5e, dan 8e
- Keyword count sesuai (PATIENCE > 0 di 2 sel, MIN_EPOCHS_BEFORE_STOP di 3 sel)
- 116 baris disisipkan, 8 dihapus

---

## 6. Cara Pakai

### 6.1 Resume Training

- **Default**: otomatis aktif. Jika training terhenti di epoch N, sesi berikutnya akan resume dari epoch N+1
- **Paksa ulang dari awal**: set `FORCE_RETRAIN_STEP1 = True` (atau `FORCE_RETRAIN_STEP2 = True`)
- **Kompatibilitas mundur**: jika `step1_resume.json` tidak ada, training dari epoch 1 (perilaku lama)

### 6.2 Early Stopping

- **Default**: aktif dengan patience 5 epoch
- **Nonaktifkan**: set `PATIENCE = 0` di config cell
- **Ubah sensitivity**: sesuaikan `PATIENCE` dan/atau `MIN_EPOCHS_BEFORE_STOP`

---

## 7. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Optimizer state besar (ratusan MB) | Hapus otomatis setelah epoch berikutnya selesai |
| `step1_resume.json` korup | Try-except → fallback ke epoch 1 |
| User ubah `NUM_EPOCHS` di antara sesi | Cek `total_epochs` di resume JSON vs nilai saat ini → warning + abaikan resume |
| Epoch checkpoint tidak cocok dengan model | Validasi `last_completed_epoch < NUM_EPOCHS` sebelum load |
| Early stopping terlalu agresif | `MIN_EPOCHS_BEFORE_STOP = 5` memastikan training minimal jalan dulu |
| Resume dari epoch setelah early stopping | Rolling checkpoint tetap ada, resume tetap bekerja |

---

## 8. Kesimpulan

Dua fitur training yang saling melengkapi telah diimplementasikan dan diverifikasi:

1. **Resume training per-epoch**: jika Colab putus di tengah training, sesi berikutnya dapat melanjutkan dari epoch terakhir (bukan dari nol), dengan bobot model + optimizer state yang utuh
2. **Early stopping**: training berhenti otomatis jika F1 tidak membaik selama 5 epoch berturut-turut, menghemat waktu Colab tanpa mengorbankan kualitas model

Kedua fitur ini diimplementasikan di generator (`_build_v4_indobert.py`), bukan patch manual di `.ipynb`, sehingga reproducible dan tidak hilang saat build ulang.

**Status:** Siap digunakan di Colab. Tidak ada training yang dijalankan di sesi ini — implementasi hanya di generator, training tetap di Colab.
