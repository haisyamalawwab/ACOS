# Sel 30 — Unduh, Rekey Prefiks `bert.` & Laporan Vocab IndoBERT

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 30 dari 80 (indeks JSON `cells[29]`) |
| Tipe sel | code |
| Bagian | 4c. Adapter IndoBERT (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan backbone IndoBERT yang benar-benar bisa dimuat oleh `BertForQuadABSA`/`CategorySentiClassification` legacy.

## Apa yang dilakukan

1. `require_vars('step_stage','acos_ckpt','bert_cache_dir','BACKBONE')`.
2. Domain bukan Indonesia → adapter dilewati (`backbone_report={'dilewati': True}`).
3. Domain Indonesia → `backbone_report = acos_ckpt.prepare_backbone(BACKBONE, bert_cache_dir)` (unduh dari HF `acos_ckpt.BACKBONES[BACKBONE]['hf_id']`, rekey, tulis penanda).
4. Laporkan rekey: `n_diberi_prefiks` dari `n_key`, contoh key sebelum/sesudah; atau alasan dilewati.
5. Laporkan vocab: `config_vocab_size`, jumlah baris `vocab.txt`, `hidden_size × num_hidden_layers`; peringatan bila tidak konsisten (normal).
6. `df_backbone` → `export_step_table('master_00_backbone_indobert')`, `rep.section('1b. Backbone & gerbang data')`.
7. Simpan `logs/backbone_report.json`.

## Keluaran / variabel yang dihasilkan

- `bert_cache_dir/{config.json, pytorch_model.bin, vocab.txt, _rekey.json}`, `backbone_report`, `df_backbone`, CSV/MD `master_00_backbone_indobert`, `logs/backbone_report.json`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 7, 12, 17.

## Catatan

- Gate 1 numerik (pembuktian bobot termuat) menyusul di sel 5d2.

---
← [Sel 29](029_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell29_05092026.md) | [Indeks](README.md) | [Sel 31](031_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell31_05092026.md) →
