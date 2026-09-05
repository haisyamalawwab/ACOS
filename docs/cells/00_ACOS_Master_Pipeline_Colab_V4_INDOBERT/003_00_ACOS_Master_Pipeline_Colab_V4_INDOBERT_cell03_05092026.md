# Sel 03 — Mount Google Drive & Instalasi Dependensi

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 3 dari 80 (indeks JSON `cells[2]`) |
| Tipe sel | code |
| Bagian | 1. Environment Setup |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan lingkungan: mount Google Drive bila berjalan di Colab, lalu memasang paket Python yang dibutuhkan pipeline.

## Apa yang dilakukan

1. `try: from google.colab import drive; drive.mount('/content/drive')` — jika gagal (lokal), cetak pesan mode lokal tanpa error.
2. `!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm` — `pytorch-crf` untuk lapisan CRF Step 1, `huggingface_hub` untuk mengunduh checkpoint IndoBERT, `boto3` dibutuhkan loader legacy.

## Cuplikan kode kunci

```python
try:
    from google.colab import drive
    drive.mount('/content/drive')
except Exception:
    print("💻 Berjalan pada lingkungan Lokal / Colab tanpa drive mount.")
!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm
```

## Keluaran / variabel yang dihasilkan

- Drive ter-mount di `/content/drive` (Colab).
- Paket terpasang di runtime.

## Catatan

- Shell magic `!pip` hanya berfungsi di Jupyter/Colab; di skrip biasa harus diganti `os.system`.

---
← [Sel 02](002_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell02_05092026.md) | [Indeks](README.md) | [Sel 04](004_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell04_05092026.md) →
