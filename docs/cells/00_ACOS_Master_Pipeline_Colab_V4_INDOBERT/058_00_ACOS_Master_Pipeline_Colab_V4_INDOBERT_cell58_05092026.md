# Sel 58 — 7b. Tabel Tipe Pasangan, Plot Batang, Manifest & State

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 58 dari 80 (indeks JSON `cells[57]`) |
| Tipe sel | code |
| Bagian | 7. Jembatan Pasangan |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Melaporkan komposisi pasangan kandidat menurut kombinasi explicit/implicit.

## Apa yang dilakukan

1. `rep.section('4. Jembatan: pasangan kandidat')`; bila `df_pairs` kosong → catatan.
2. Kolom baru: `Is_Implicit_Aspect`, `Is_Implicit_Opinion`, `Pair_Type` (Explicit/Implicit-Explicit/Implicit).
3. `df_tipe` (Tipe_Pasangan, Jumlah, Persen) → `export_step_table('master_04_tipe_pasangan')`; `df_pairs.head(20)` → `master_05_preview_pasangan`.
4. Plot batang berwarna dengan label jumlah & persen → `plots/04_candidate_pairs_distribution.png` (300 DPI), `rep.image`.
5. `update_mcp_manifest('CANDIDATE_PAIRS_GENERATED', 4, {candidate_pairs_count})`; `save_pipeline_state({'df_pairs': df_pairs})`.

## Keluaran / variabel yang dihasilkan

- CSV/MD `master_04`, `master_05`; `plots/04_candidate_pairs_distribution.png`; manifest; state.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 56 (7a) — `df_pairs`.

---
← [Sel 57](057_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell57_05092026.md) | [Indeks](README.md) | [Sel 59](059_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell59_05092026.md) →
