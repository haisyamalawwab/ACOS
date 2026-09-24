# ⚠️ PENTING: Restart Jupyter Kernel

## Masalah ModuleNotFoundError Telah Diperbaiki!

Cell 3 telah diupdate dengan versi yang lebih robust. Namun, Jupyter kernel masih menyimpan cache modul yang lama.

## ✅ Langkah-Langkah (WAJIB):

### 1. Restart Kernel

Di Jupyter notebook, klik menu:

```
Kernel → Restart & Clear Output
```

Atau tekan: `0` + `0` (tekan angka 0 dua kali)

### 2. Jalankan Cell Secara Berurutan

```
Cell 1: Diagnostik GPU        → Run
Cell 2: Konfigurasi           → Run  
Cell 3: Import & Path Setup   → Run (versi baru!)
```

### 3. Lihat Output Cell 3

Jika berhasil, Anda akan melihat:

```
✓ Paths configured:
  base_project_dir : d:\laragon\www\ACOS-ASLI
  upstream_root    : d:\laragon\www\ACOS-ASLI\Extract-Classify-ACOS
  indo_root        : d:\laragon\www\ACOS-ASLI\ACOS-IndoBERT

✓ Verifying key files:
  All key files found!

============================================================
Importing modules...
============================================================
  ✓ BertTokenizer
  ✓ BertForQuadABSA, CategorySentiClassification
  ✓ acos_id (v0.2.1)
  ✓ taxonomy (13 aspects)
  ✓ checkpoint
  ✓ cross_val
  ✓ experiment_runner
  ✓ model_wrappers

✅ ALL IMPORTS SUCCESSFUL!
```

## 🐛 Jika Masih Error

### Error: "Root proyek tidak ditemukan"

Edit Cell 3, bagian `_ROOT_CANDIDATES`, tambahkan path Anda:

```python
_ROOT_CANDIDATES = [
    '/shared-docker/ACOS',
    'd:/laragon/www/ACOS-ASLI',
    'D:/laragon/www/ACOS-ASLI',          # Coba uppercase
    '/your/actual/path/ACOS-ASLI',        # Path Anda
    str(Path.cwd().parent.parent),
    str(Path.cwd().parent),
]
```

### Error: ModuleNotFoundError masih muncul

1. **Hapus Python cache:**

```bash
cd d:\laragon\www\ACOS-ASLI\ACOS-IndoBERT
rd /s /q acos_id\__pycache__
```

2. **Check Python environment di Jupyter:**

Buat cell baru dan jalankan:

```python
import sys
print("Python:", sys.executable)
print("Version:", sys.version)

# Check if torch installed
try:
    import torch
    print("✓ PyTorch installed:", torch.__version__)
except ImportError:
    print("❌ PyTorch NOT installed!")
```

3. **Pastikan Jupyter menggunakan environment yang benar:**

```bash
# Aktifkan environment Anda (conda/venv)
conda activate your_env
# atau
source your_venv/bin/activate

# Install ipykernel
pip install ipykernel

# Register kernel
python -m ipykernel install --user --name=your_env

# Restart Jupyter
jupyter notebook
```

Lalu di notebook: Kernel → Change kernel → pilih `your_env`

## 📋 Perubahan pada Cell 3

Cell 3 versi baru memiliki:

1. ✅ **Module cache clearing** - Hapus cache acos_id sebelum import
2. ✅ **Robust path detection** - Gunakan `.resolve()` untuk absolute path
3. ✅ **File verification** - Check semua file penting sebelum import
4. ✅ **Better error messages** - Error lebih informatif
5. ✅ **Import status** - Tampilkan progress import

## 🚀 Setelah Berhasil

Lanjutkan ke:
- Cell 4: HardwareMonitor
- Cell 5: Backbone IndoBERT
- Cell 6: ExperimentGrid
- Cell 7: Persiapan data
- Cell 8: Training adapter
- Cell 9: Run eksperimen

## 📞 Troubleshooting Lanjutan

Jika masih bermasalah setelah restart kernel, buka issue dengan info:

```python
# Jalankan ini di cell baru
import sys
from pathlib import Path

print("="*60)
print("DEBUG INFO")
print("="*60)
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
print(f"CWD: {Path.cwd()}")
print(f"\nsys.path (first 5):")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}] {p}")

acos_path = Path('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/acos_id')
print(f"\nacos_id dir exists: {acos_path.exists()}")
if acos_path.exists():
    print("Files in acos_id:")
    for f in sorted(acos_path.glob('*.py')):
        print(f"  - {f.name}")
```

Salin output debug info di atas saat melaporkan issue.

---

**Status:** ✅ Cell 3 Updated  
**Action Required:** **RESTART KERNEL** sebelum run Cell 3
