# Sel 51 — Helper `auto_find_latest_state()`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 51 dari 80 (indeks JSON `cells[50]`) |
| Tipe sel | code |
| Bagian | 6. State & Recovery |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Mencari `pipeline_state.pkl` terbaru yang cocok domain.

## Apa yang dilakukan

1. (1) Cek pointer `latest_pipeline_state_{domain}.pkl` di setiap base.
2. (2) `os.walk` mencari `pipeline_state.pkl`; bila path tidak memuat nama domain, buka pickle dan cocokkan `DOMAIN`; pilih yang `mtime` terbaru.

## Keluaran / variabel yang dihasilkan

- Fungsi `auto_find_latest_state(search_bases, domain='rest16') -> path|None`.

---
← [Sel 50](050_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell50_05092026.md) | [Indeks](README.md) | [Sel 52](052_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell52_05092026.md) →
