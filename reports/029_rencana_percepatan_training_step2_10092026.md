# 029 — Rencana Percepatan Training Step 2 IndoBERT pada T4

**Tanggal:** 10 September 2026
**Status:** rencana, menunggu implementasi di generator

---

## 1. Masalah

Training Step 2 (`CategorySentiClassification`) di notebook V4 IndoBERT pada Tesla T4:
- 4.089 batch × batch_size=16 = 65.424 pasangan per epoch
- ~5 menit per epoch
- 15 epoch = ~75 menit (mendekati batas Colab free tier)

Step 1 sudah cache hit — tidak berkontribusi pada masalah.

## 2. Akar Penyebab

| # | Penyebab | Dampak |
|---|---|---|
| 1 | Tidak ada Mixed Precision (AMP/FP16) | T4 punya tensor core untuk FP16; seluruh training di FP32. |
| 2 | `STEP2_BATCH_SIZE = 16` terlalu kecil | VRAM terpakai ~4-5 GB dari 14.56 GB. |
| 3 | `optimizer.zero_grad()` tanpa `set_to_none=True` | Overhead kecil tapi gratis diperbaiki. |

## 3. Rencana Perubahan

### 3.1 Config (`CODE_CONFIG`, baris ~1010 generator)

```python
STEP1_BATCH_SIZE = 32   # dari 24
STEP2_BATCH_SIZE = 32   # dari 16
MAX_EPOCHS_THIS_RUN = 1  # 0 = semua epoch, 1 = satu epoch per eksekusi
```

### 3.2 Training loop Step 1 & Step 2: AMP + set_to_none

```python
# Sebelum loop epoch
scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

# Di dalam loop batch
with torch.cuda.amp.autocast():
    out = model(...)
    loss, _ = unpack_model_output(out)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
optimizer.zero_grad(set_to_none=True)
```

### 3.3 Pembatasan epoch per eksekusi

```python
_run_until = (start_epoch + MAX_EPOCHS_THIS_RUN - 1) if MAX_EPOCHS_THIS_RUN else NUM_EPOCHS
_run_until = min(_run_until, NUM_EPOCHS)
epoch_bar = tqdm(range(start_epoch, _run_until + 1), ...)
```

## 4. Estimasi Dampak

| Skenario | Per Epoch | 15 Epoch | Dengan Early Stop (8 ep) |
|---|---|---|---|
| Sekarang (FP32, BS=16) | ~5 mnt | 75 mnt | 40 mnt |
| +AMP +BS=32 +set_to_none | **~1.8 mnt** | 27 mnt | 14 mnt |

Dengan `MAX_EPOCHS_THIS_RUN=1`, tiap sesi Colab hanya ~2 menit GPU time.
Resume otomatis dari `step2_resume.json` tetap berfungsi.

## 5. File yang Diedit

- `ACOS-IndoBERT/notebooks/_build_v4_indobert.py` (generator)
- Setelah edit, jalankan generator untuk meregenerasi notebook

**Tidak diedit:** notebook `.ipynb` langsung (dihasilkan oleh generator).