# Sel 29 — Heading: 4c. Adapter Checkpoint IndoBERT

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 29 dari 80 (indeks JSON `cells[28]`) |
| Tipe sel | markdown |
| Bagian | 4c. Adapter IndoBERT (baru di V4) |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menjelaskan tujuan sel berikutnya: menyiapkan `bert_cache_dir` berisi `config.json`, `pytorch_model.bin`, `vocab.txt` IndoBERT dengan state_dict yang **direkey** (setiap key diberi prefiks `bert.`) agar cocok dengan `start_prefix=''` loader legacy. Harus berjalan **sebelum** 4d karena generator `tokenized_data` memakai vocab IndoBERT. Idempoten lewat penanda `_rekey.json` (rekey dua kali → `bert.bert.embeddings...`). Menjelaskan bahwa `config.vocab_size = 50000` sementara `vocab.txt` berisi 30.521 token adalah normal untuk indobert-base-p1.

---
← [Sel 28](028_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell28_05092026.md) | [Indeks](README.md) | [Sel 30](030_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell30_05092026.md) →
