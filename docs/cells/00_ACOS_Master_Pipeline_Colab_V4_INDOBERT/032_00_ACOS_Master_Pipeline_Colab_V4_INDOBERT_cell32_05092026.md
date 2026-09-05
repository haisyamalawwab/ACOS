# Sel 32 — Jalankan 5 Gate Torch-Free & Ekspor Tabel Gerbang

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 32 dari 80 (indeks JSON `cells[31]`) |
| Tipe sel | code |
| Bagian | 4d. Gerbang Data (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memvalidasi taksonomi, dataset, konversi ACOS, retokenisasi, dan konvensi offset generator sebelum satu pun epoch dilatih.

## Apa yang dilakukan

1. `FORCE_REBUILD_ID_DATA = False` — set True untuk membangun ulang berkas ACOS & tokenized_data dari nol.
2. Domain bukan Indonesia → semua gate dilewati (`id_gate_results = {}`).
3. Cek `bert_cache_dir/vocab.txt` ada, kalau tidak → `RuntimeError` minta jalankan 4c.
4. `_paths = acos_selftest.default_paths(indo_root, acos_root)`; timpa `bert_cache_dir` dan `work_dir = logs/gates`.
5. Gate 2 butuh vocab bert-base-uncased: unduh `vocab.txt` (232 KB) dari HF ke `_paths['en_vocab_dir']` bila belum ada.
6. `id_gate_results = acos_selftest.run_gates(paths=_paths, only=TORCH_FREE_GATES, rebuild=FORCE_REBUILD_ID_DATA, raise_on_fail=True, verbose=True)`.
7. Bangun `df_id_gates` per split (Baris_ACOS, Quad_ACOS, Quad_Tokenized, Quad_Hilang, Aspek/Opini Eksplisit/Implisit) → `export_step_table('master_00b_gerbang_data_id')`.
8. Simpan `logs/id_gates.json`; `update_mcp_manifest('ID_DATA_GATES_PASSED', 1, {n_gate, num_labels_step2})`.

## Keluaran / variabel yang dihasilkan

- `tokenized_data/appsid_*_quad_bert.tsv`, `appsid_*_pair.tsv` di `indo_root`; `id_gate_results`, `df_id_gates`; CSV/MD `master_00b`; `logs/id_gates.json`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 30 (4c) selesai — vocab IndoBERT.

---
← [Sel 31](031_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell31_05092026.md) | [Indeks](README.md) | [Sel 33](033_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell33_05092026.md) →
