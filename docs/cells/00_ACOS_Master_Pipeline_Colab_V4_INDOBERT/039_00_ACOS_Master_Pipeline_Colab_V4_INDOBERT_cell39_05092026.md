# Sel 39 — 5c. Bangun `eval_loader_1` & `eval_gold_1` dari Test Set

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 39 dari 80 (indeks JSON `cells[38]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyiapkan data evaluasi Step 1 (dilewati bila cache hit).

## Apa yang dilakukan

1. `eval_examples_1 = processor_step1.get_dev_examples(tokenized_base, DOMAIN)` — membaca `tokenized_data/{DOMAIN}_test_quad_bert.tsv`.
2. `eval_features_1 = features_step1(examples, label_list_step1, MAX_SEQ_LENGTH, tokenizer, output_modes['quad'], 'quad')`.
3. Tensor: `tokens_len, aspect_input_ids, aspect_input_mask, aspect_ids, aspect_segment_ids, exist_imp_aspect, exist_imp_opinion` → `TensorDataset` → `DataLoader(batch 16, SequentialSampler, pin_memory=cuda, num_workers=0 di Windows/2 lainnya)`.
4. Parse gold TSV: untuk setiap quad `a_st,a_ed ... o_st,o_ed` isi label BIO (`B-A/I-A`, `B-O/I-O`), tandai implicit bila `ed == -1`; kumpulkan `eval_gold_labels += [labels, imp_a, imp_o]`.
5. `eval_gold_1 = [ev_ids.numpy().tolist(), eval_gold_labels]`; `assert len(eval_gold_labels) == 3 * len(eval_features_1)`.

## Keluaran / variabel yang dihasilkan

- `eval_loader_1, eval_gold_1, eval_features_1, pin_mem, num_work`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 37 (5b) — `STEP1_SKIP_TRAINING`, `label_map_seq`, `tokenizer`.

---
← [Sel 38](038_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell38_05092026.md) | [Indeks](README.md) | [Sel 40](040_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell40_05092026.md) →
