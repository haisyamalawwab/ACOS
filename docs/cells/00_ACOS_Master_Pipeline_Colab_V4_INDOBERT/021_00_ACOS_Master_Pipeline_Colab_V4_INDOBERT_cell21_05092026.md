# Sel 21 — Helper `auto_find_file()`, Manifest INITIALIZED & Tabel Konfigurasi

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 21 dari 80 (indeks JSON `cells[20]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Mendefinisikan pencari berkas lintas sesi (menimpa versi `colab_utils`), lalu mencatat status awal dan tabel hyperparameter.

## Apa yang dilakukan

1. `auto_find_file(filename, search_roots=None, must_contain=None, domain=None, min_size_bytes=0)` — `os.walk` pada root sesi aktif, `results_base`, dan path Drive lama; filter substring path (`step1_best`), filter domain (tolak path `laptop_`/`rest16_` milik domain lain), dan ukuran minimum.
2. `update_mcp_manifest('INITIALIZED', 1)`.
3. `df_cfg` (domain, epoch, batch, lr, max_seq_length, seed, device) → `export_step_table(name='master_00_konfigurasi')` + `rep.section('1. Konfigurasi pipeline')`.
4. `save_pipeline_state()` — state awal.

## Keluaran / variabel yang dihasilkan

- `csv/master_00_konfigurasi.csv`, `md/master_00_konfigurasi.md`, `session_manifest.json`, `pipeline_state.pkl`.

---
← [Sel 20](020_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell20_05092026.md) | [Indeks](README.md) | [Sel 22](022_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell22_05092026.md) →
