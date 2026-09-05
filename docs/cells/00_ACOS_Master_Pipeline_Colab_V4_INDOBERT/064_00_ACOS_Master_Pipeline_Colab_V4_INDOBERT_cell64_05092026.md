# Sel 64 — 8c. Bangun `eval_loader_2` & `eval_gold_2`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 64 dari 80 (indeks JSON `cells[63]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan data evaluasi Step 2 dari pasangan kandidat (prediksi Step 1) dan gold quadruple.

## Apa yang dilakukan

1. Lewati bila `eval_loader_2` dan `eval_gold_2` sudah ada.
2. `tokenized_dir = tokenized_base/tokenized_data`; `eval_pair_file, pakai_1st = resolve_eval_pair_file(tokenized_dir, DOMAIN, prefer_1st=True)`.
3. `eval_examples_2 = pair_examples_from_file(processor_step2, eval_pair_file, set_type='test')` → `features_step2(..., output_modes['categorysenti'])`.
4. Tensor: `tokens_len, aspect_input_ids, aspect_input_mask, aspect_segment_ids, candidate_aspect, candidate_opinion, label_id(float)` → `DataLoader(batch 16, Sequential)`.
5. `class ArgsProxy(bert_model=bert_cache_dir, do_lower_case=True)`; `eval_gold_2 = read_pair_gold(open(tokenized_dir/{DOMAIN}_test_pair.tsv).readlines(), ArgsProxy())`.

## Keluaran / variabel yang dihasilkan

- `eval_loader_2, eval_gold_2, eval_features_2, pakai_1st, tokenized_dir`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 56 (7a) — `_test_pair_1st.tsv`; sel 60 (8a).

---
← [Sel 63](063_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell63_05092026.md) | [Indeks](README.md) | [Sel 65](065_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell65_05092026.md) →
