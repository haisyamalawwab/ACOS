# Sel 34 — Impor Modul Upstream untuk Step 1

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 34 dari 80 (indeks JSON `cells[33]`) |
| Tipe sel | code |
| Bagian | 5. Step 1 |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Sel impor pendek (warisan V2) — memuat kelas/fungsi dari repo `Extract-Classify-ACOS` yang sudah ada di `sys.path`.

## Apa yang dilakukan

1. `from modeling import BertForQuadABSA`
2. `from bert_utils.tokenization import BertTokenizer`
3. `from bert_utils.optimization import BertAdam`
4. `from run_classifier_dataset_utils import processors, output_modes`
5. `from eval_metrics import pred_eval`
6. `from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler`
7. `from tqdm.auto import tqdm`, `import time`

## Catatan

- Impor yang sama diulang di sel 5a supaya 5a bisa dijalankan mandiri; sel ini bisa dianggap redundan tetapi tidak berbahaya.

---
← [Sel 33](033_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell33_05092026.md) | [Indeks](README.md) | [Sel 35](035_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell35_05092026.md) →
