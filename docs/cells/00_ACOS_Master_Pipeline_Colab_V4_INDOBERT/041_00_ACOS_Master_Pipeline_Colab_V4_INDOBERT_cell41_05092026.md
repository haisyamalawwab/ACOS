# Sel 41 — 5d. Instansiasi `BertForQuadABSA`, Train Loader & `BertAdam`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 41 dari 80 (indeks JSON `cells[40]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memuat model Step 1 dari backbone IndoBERT dan menyiapkan data training + optimizer (dilewati bila cache hit).

## Apa yang dilakukan

1. `model_step1 = BertForQuadABSA.from_pretrained(bert_cache_dir, num_labels=num_labels_step1).to(device)`; laporkan jumlah parameter & VRAM terpakai.
2. `train_examples_1 = processor_step1.get_train_examples(tokenized_base, DOMAIN)` → `features_step1` → `TensorDataset` → `DataLoader(RandomSampler, batch=STEP1_BATCH_SIZE)`.
3. `num_train_steps_1 = len(train_loader_1) * NUM_EPOCHS`; grup parameter dengan `weight_decay=0.01` kecuali `bias`/`LayerNorm`.
4. `optimizer_1 = BertAdam(opt_grouped, lr=STEP1_LR, warmup=0.1, t_total=num_train_steps_1)`.
5. `class ArgsH` (`output_dir=logs`, `max_seq_length`) → `args_h`; `logger = logging.getLogger('Step1')`.

## Keluaran / variabel yang dihasilkan

- `model_step1, train_loader_1, optimizer_1, num_train_steps_1, args_h, logger`.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 39 (5c) — `eval_loader_1`, `eval_gold_1`.

---
← [Sel 40](040_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell40_05092026.md) | [Indeks](README.md) | [Sel 42](042_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell42_05092026.md) →
