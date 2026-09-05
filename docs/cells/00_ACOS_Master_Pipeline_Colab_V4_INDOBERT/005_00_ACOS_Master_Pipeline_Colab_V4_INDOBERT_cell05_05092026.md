# Sel 05 — Diagnostik & Optimasi GPU

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 5 dari 80 (indeks JSON `cells[4]`) |
| Tipe sel | code |
| Bagian | 1. Environment Setup |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menentukan perangkat komputasi (`cuda`/`cpu`) dan mencetak spesifikasi GPU, lalu mengaktifkan optimasi cuDNN.

## Apa yang dilakukan

1. `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')`.
2. Bila CUDA ada: cetak nama GPU, total VRAM (GB), compute capability, versi cuDNN.
3. `torch.backends.cudnn.benchmark = True` dan `torch.cuda.empty_cache()` untuk mempercepat operasi matriks berulang.
4. Bila tidak ada CUDA: cetak info mode CPU.

## Keluaran / variabel yang dihasilkan

- Variabel global `device` (dipakai semua sel training/inferensi).

## Prasyarat (sel yang harus sudah berjalan)

- Sel 4 (`torch` terimpor).

---
← [Sel 04](004_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell04_05092026.md) | [Indeks](README.md) | [Sel 06](006_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell06_05092026.md) →
