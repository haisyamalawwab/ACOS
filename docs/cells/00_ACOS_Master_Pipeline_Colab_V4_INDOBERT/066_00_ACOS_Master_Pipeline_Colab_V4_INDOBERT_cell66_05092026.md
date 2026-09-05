# Sel 66 — 8d. Instansiasi `CategorySentiClassification`, Train Loader & `BertAdam`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 66 dari 80 (indeks JSON `cells[65]`) |
| Tipe sel | code |
| Bagian | 8. Step 2 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memuat model Step 2 dari backbone IndoBERT dan menyiapkan data training + optimizer (dilewati bila cache hit).

## Apa yang dilakukan

1. `model_step2 = CategorySentiClassification.from_pretrained(bert_cache_dir, num_labels=num_labels_step2).to(device)`; laporkan parameter & VRAM.
2. `train_examples_2 = processor_step2.get_train_examples(tokenized_base, DOMAIN)` (membaca `{DOMAIN}_train_pair.tsv`) → `features_step2` → `DataLoader(RandomSampler, batch=STEP2_BATCH_SIZE)`.
3. `optimizer_2 = BertAdam(grup weight_decay 0.01/0.0, lr=STEP2_LR, warmup=0.1, t_total=len(train_loader_2)*NUM_EPOCHS)`.
4. Memakai ulang `logger2` & `args_h` dari 8a.

## Keluaran / variabel yang dihasilkan

- `model_step2, train_loader_2, optimizer_2, num_train_steps_2`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 64 (8c) — `eval_loader_2, eval_gold_2, num_labels_step2`.

---
← [Sel 65](065_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell65_05092026.md) | [Indeks](README.md) | [Sel 67](067_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell67_05092026.md) →
