# Sel 43 — 5d2. Verifikasi Numerik Bobot IndoBERT vs Checkpoint

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 43 dari 80 (indeks JSON `cells[42]`) |
| Tipe sel | code |
| Bagian | 5d2. Gate 1 (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Membuktikan secara numerik bahwa fine-tuning berjalan di atas bobot IndoBERT terlatih, bukan inisialisasi acak.

## Apa yang dilakukan

1. `STEP1_SKIP_TRAINING` → gate dilewati (model tidak dimuat).
2. Domain Inggris → gate tetap dijalankan sebagai kontrol; domain Indonesia → `require_vars('model_step1')`.
3. `gate1_report = acos_ckpt.gate_weights_loaded(model_step1, bert_cache_dir)`.
4. Cetak per tensor: `✅ identik (mean ...)` atau `❌ alasan`; ringkas jumlah key `bert.*` di model vs checkpoint dan yang tanpa padanan.
5. `df_gate1` → `export_step_table('master_00c_gate1_bobot_encoder')`, `rep.table`; simpan `logs/gate1_weights.json`.
6. Bila `not gate1_report['ok']` → `RuntimeError` dengan instruksi `acos_ckpt.prepare_backbone(BACKBONE, bert_cache_dir, force_rekey=True)`.

## Keluaran / variabel yang dihasilkan

- `gate1_report, df_gate1`; CSV/MD `master_00c`; `logs/gate1_weights.json`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 41 (5d) — `model_step1`.

---
← [Sel 42](042_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell42_05092026.md) | [Indeks](README.md) | [Sel 44](044_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell44_05092026.md) →
