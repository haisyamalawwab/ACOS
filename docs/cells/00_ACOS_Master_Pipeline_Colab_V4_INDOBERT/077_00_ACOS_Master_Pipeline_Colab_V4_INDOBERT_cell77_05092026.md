# Sel 77 — Muat Model Step 1 & Step 2 Terbaik + Helper `_spans_dari_tag()`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 77 dari 80 (indeks JSON `cells[76]`) |
| Tipe sel | code |
| Bagian | 10. Inferensi Live |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memuat kedua checkpoint terbaik (dengan fallback pencarian lintas sesi) ke mode eval dan menyiapkan dekoder span dari tag CRF.

## Apa yang dilakukan

1. `step1_best_path = session_dirs['step1_checkpoint']`; bila bin tidak ada → `auto_find_file('pytorch_model.bin', must_contain='step1_best')`. Sama untuk Step 2.
2. `model_step1_best = BertForQuadABSA.from_pretrained(step1_best_path, num_labels=num_labels_step1).to(device).eval()`.
3. `model_step2_best = CategorySentiClassification.from_pretrained(step2_best_path, num_labels=num_labels_step2).to(device).eval()`.
4. `_catsenti_labels = label_list_step2[0]`.
5. `_spans_dari_tag(tag_ids)` — gabungkan id tag jadi string; regex `32*` → span aspek (B-A=3, I-A=2), `54*` → span opini (B-O=5, I-O=4); offset −1 untuk membuang `[CLS]`.

## Keluaran / variabel yang dihasilkan

- `model_step1_best, model_step2_best, _catsenti_labels, _spans_dari_tag`.

## Prasyarat (sel yang harus sudah berjalan)

- Checkpoint Step 1 & 2; `num_labels_step1/2`, `label_list_step2`, `device`.

---
← [Sel 76](076_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell76_05092026.md) | [Indeks](README.md) | [Sel 78](078_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell78_05092026.md) →
