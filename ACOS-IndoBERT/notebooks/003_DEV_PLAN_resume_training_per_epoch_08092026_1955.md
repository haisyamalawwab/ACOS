# Dev Plan: Resume Training Per Epoch — ACOS IndoBERT Notebook

**File:** `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb`
**Tanggal:** 2026-09-06
**Status:** Selesai — diimplementasikan di notebook (2026-09-06) dan di-port ke generator
`_build_v4_indobert.py` (2026-09-08) via `RESUME_SPECS` + langkah patch ke-14, sehingga
fitur ini kini reproducible dari build (sebelumnya hanya ada di .ipynb hasil patch manual
dan akan hilang saat generator dijalankan ulang). Portir: `ACOS-IndoBERT/build/_port_resume_to_v4.py`.

---

## 1. Latar Belakang & Masalah

Notebook saat ini sudah memiliki mekanisme **resume per-sesi**, yaitu:
- Jika folder sesi terdahulu ditemukan, checkpoint model terbaik (`pytorch_model.bin`) di-copy ke sesi aktif
- Training di-skip jika `step1_already_done == True`

**Masalah:** Jika Colab putus di tengah training (misalnya epoch ke-7 dari 15), sesi berikutnya akan:
1. Menemukan bahwa `step1_bin` BELUM ada → `step1_already_done = False`
2. Memulai training dari **epoch 1** lagi — membuang semua progres sebelumnya

---

## 2. Analisis Kode Saat Ini

### Cell 36 — `5b. Deteksi cache Step 1`
- Cek `os.path.exists(step1_bin) and os.path.exists(pred_file)` → `step1_already_done`
- Jika `step1_already_done = True` → `STEP1_SKIP_TRAINING = True` → training di-skip
- Tidak ada logika untuk "training setengah jalan"

### Cell 44 — `5e. Training Step 1`
```python
best_step1_f1 = 0.0     # di-reset setiap kali sel dijalankan
best1_epoch = 1          # di-reset
step1_history = []       # di-reset

for epoch in range(1, NUM_EPOCHS + 1):   # selalu mulai dari epoch 1
    ...
    torch.save(model_step1.state_dict(), step1_bin)  # hanya jika F1 meningkat
    # optimizer state TIDAK disimpan
```

### Cell 61 — `8b. Deteksi cache Step 2` & Cell 67 — `8e. Training Step 2`
- Masalah yang sama dengan Cell 36 dan 44

---

## 3. Desain Solusi

### Strategi: Rolling Epoch Checkpoint

Setiap akhir epoch, simpan:
1. **Model weights** → `checkpoints/step1_epoch_{N}/pytorch_model.bin`
2. **Optimizer state** → `checkpoints/step1_epoch_{N}/optimizer.pt`
3. **Resume metadata** → `logs/step1_resume.json`

File `step1_resume.json` berisi:
```json
{
  "last_completed_epoch": 7,
  "best_micro_f1": 0.4321,
  "best_epoch": 5,
  "history": [ ... ],
  "saved_at": "2026-09-06T20:00:00"
}
```

Saat sesi baru dimulai:
- Baca `step1_resume.json` → `last_completed_epoch = 7`
- Load model + optimizer dari `checkpoints/step1_epoch_7/`
- Lanjut dari `range(8, NUM_EPOCHS + 1)`
- Restore `step1_history`, `best_step1_f1`, `best1_epoch`

### Kebijakan Storage
- Hanya **1 rolling checkpoint** per step yang disimpan (checkpoint epoch `N-1` dihapus setelah epoch `N` selesai tersimpan)
- Checkpoint **best model** (`step1_best/`) tetap dipertahankan seperti sebelumnya
- Jika training selesai penuh (epoch = `NUM_EPOCHS`) → hapus rolling checkpoint (tidak diperlukan lagi)

---

## 4. Sel yang Dimodifikasi

### 4.1 Cell 36 — `5b. Deteksi cache Step 1`

Tambahkan SETELAH logika `STEP1_SKIP_TRAINING` yang ada:

```python
# Resume Epoch: cek apakah ada training yang terhenti di tengah jalan
step1_resume_json = os.path.join(session_dirs["logs"], "step1_resume.json")
STEP1_RESUME_EPOCH = 0  # epoch terakhir yang selesai (0 = belum ada)

if (not STEP1_SKIP_TRAINING) and (not FORCE_RETRAIN_STEP1):
    if os.path.exists(step1_resume_json):
        try:
            _rj = json.load(open(step1_resume_json, encoding="utf-8"))
            _last = int(_rj.get("last_completed_epoch", 0))
            _epoch_ckpt = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{_last}")
            _epoch_bin = os.path.join(_epoch_ckpt, "pytorch_model.bin")
            if _last > 0 and _last < NUM_EPOCHS and os.path.exists(_epoch_bin):
                STEP1_RESUME_EPOCH = _last
                print(f"♻️  [RESUME] Step 1 terhenti di epoch {_last}/{NUM_EPOCHS}. "
                      f"Akan dilanjutkan dari epoch {_last + 1}.")
            elif _last >= NUM_EPOCHS:
                print(f"✅ [RESUME] step1_resume.json menunjukkan training sudah "
                      f"selesai ({_last} epoch).")
        except Exception as _re:
            print(f"⚠️  Tidak bisa membaca step1_resume.json: {_re}")

if STEP1_RESUME_EPOCH > 0:
    STEP1_SKIP_TRAINING = False  # paksa jalankan training (lanjut dari epoch berikutnya)
```

---

### 4.2 Cell 44 — `5e. Training Step 1`

Ganti seluruh block `else:` (training) — tambah resume logic di awal loop dan
rolling checkpoint di akhir setiap epoch:

```python
else:
    require_vars("model_step1", "optimizer_1", "train_loader_1", "eval_loader_1")
    with step_stage(...) as st:

        # ── Resume State ──────────────────────────────────────────────
        step1_resume_json = os.path.join(session_dirs["logs"], "step1_resume.json")
        start_epoch = 1
        best_step1_f1 = 0.0
        best1_epoch = 1
        step1_history = []

        _resume_ep = globals().get("STEP1_RESUME_EPOCH", 0)
        if _resume_ep > 0 and not FORCE_RETRAIN_STEP1:
            _epoch_ckpt = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{_resume_ep}")
            _model_path = os.path.join(_epoch_ckpt, "pytorch_model.bin")
            _opt_path   = os.path.join(_epoch_ckpt, "optimizer.pt")
            try:
                model_step1.load_state_dict(
                    torch.load(_model_path, map_location=device))
                if os.path.exists(_opt_path):
                    optimizer_1.load_state_dict(
                        torch.load(_opt_path, map_location="cpu"))
                    st.note(f"✅ Optimizer state direstorasi dari epoch {_resume_ep}")
                _rj = json.load(open(step1_resume_json, encoding="utf-8"))
                step1_history  = _rj.get("history", [])
                best_step1_f1  = float(_rj.get("best_micro_f1", 0.0))
                best1_epoch    = int(_rj.get("best_epoch", 1))
                start_epoch    = _resume_ep + 1
                st.step(f"♻️  Resume dari epoch {_resume_ep} → mulai epoch {start_epoch}")
            except Exception as _load_err:
                st.note(f"❌ Gagal load resume: {_load_err}. Training dari awal.")
                start_epoch = 1
        # ─────────────────────────────────────────────────────────────

        epoch_bar = tqdm(range(start_epoch, NUM_EPOCHS + 1), ...)
        for epoch in epoch_bar:
            # ... training loop (SAMA seperti sebelumnya) ...

            # ── Rolling epoch checkpoint (BARU) ──────────────────────
            _epoch_ckpt_dir = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{epoch}")
            os.makedirs(_epoch_ckpt_dir, exist_ok=True)
            torch.save(model_step1.state_dict(),
                       os.path.join(_epoch_ckpt_dir, "pytorch_model.bin"))
            torch.save(optimizer_1.state_dict(),
                       os.path.join(_epoch_ckpt_dir, "optimizer.pt"))

            # Hapus rolling checkpoint epoch sebelumnya
            _prev = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{epoch - 1}")
            if epoch > start_epoch and os.path.isdir(_prev):
                shutil.rmtree(_prev, ignore_errors=True)

            # Update resume JSON
            with open(step1_resume_json, "w", encoding="utf-8") as _rjf:
                json.dump({
                    "last_completed_epoch": epoch,
                    "total_epochs": NUM_EPOCHS,
                    "best_micro_f1": best_step1_f1,
                    "best_epoch": best1_epoch,
                    "history": step1_history,
                    "saved_at": datetime.now().isoformat(),
                }, _rjf, indent=2)
            # ─────────────────────────────────────────────────────────
```

---

### 4.3 Cell 61 — `8b. Deteksi cache Step 2`

Logika identik dengan Cell 36 tapi untuk variabel Step 2:
- `step2_resume_json`, `STEP2_RESUME_EPOCH`
- `step2_bin`, `FORCE_RETRAIN_STEP2`, `STEP2_SKIP_TRAINING`

---

### 4.4 Cell 67 — `8e. Training Step 2`

Logika identik dengan Cell 44 tapi untuk:
- `model_step2`, `optimizer_2`
- `step2_history`, `best_step2_f1`, `best2_epoch`
- `step2_resume_json`, folder `step2_epoch_{N}`

---

## 5. Artefak Baru yang Dihasilkan

| File | Lokasi | Isi |
|------|--------|-----|
| `step1_resume.json` | `logs/` | Metadata resume: epoch terakhir, best F1, history |
| `step2_resume.json` | `logs/` | Sama untuk Step 2 |
| `step1_epoch_{N}/pytorch_model.bin` | `checkpoints/` | Model weights epoch N (rolling) |
| `step1_epoch_{N}/optimizer.pt` | `checkpoints/` | Optimizer state epoch N (rolling) |
| `step2_epoch_{N}/pytorch_model.bin` | `checkpoints/` | Sama untuk Step 2 |
| `step2_epoch_{N}/optimizer.pt` | `checkpoints/` | Sama untuk Step 2 |

---

## 6. Alur Kerja Resume (User Flow)

```
Session 1: Epoch 1–7 selesai, Colab putus
├── step1_resume.json         → last_completed_epoch=7
├── checkpoints/step1_epoch_7/pytorch_model.bin ✅
├── checkpoints/step1_epoch_7/optimizer.pt ✅
└── checkpoints/step1_best/pytorch_model.bin ✅ (best dari epoch 1-7)

Session 2: Jalankan sel 1b, 2c, 3, 4c, 4d, 5a, 5b, 5c, 5d, 5d2, 5e
├── Cell 5b: Baca step1_resume.json → STEP1_RESUME_EPOCH=7
│           STEP1_SKIP_TRAINING=False (lanjut training)
└── Cell 5e: Load checkpoint epoch 7 + optimizer
            → Loop epoch 8–15 → Selesai ✅
```

---

## 7. Kompatibilitas Mundur

- Jika `step1_resume.json` TIDAK ada → training dari epoch 1 (perilaku lama)
- `FORCE_RETRAIN_STEP1 = True` → abaikan resume, mulai dari epoch 1
- Checkpoint best model (`step1_best/`) tidak berubah mekanismenya
- CSV history tetap tersimpan di `step1_training_history.csv`

---

## 8. Risiko & Mitigasi

| Risiko | Mitigasi |
|--------|----------|
| Optimizer state besar (ratusan MB) | Hapus otomatis setelah epoch berikutnya selesai |
| `step1_resume.json` korup | Try-except → fallback ke epoch 1 |
| User ubah `NUM_EPOCHS` di antara sesi | Cek `total_epochs` di resume JSON vs nilai saat ini → warning |
| Epoch checkpoint tidak cocok dengan model | Validasi `last_completed_epoch < NUM_EPOCHS` sebelum load |
