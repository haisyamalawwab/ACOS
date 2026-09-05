# Sel 54 — Definisi & Eksekusi `ensure_objects()`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 54 dari 80 (indeks JSON `cells[53]`) |
| Tipe sel | code |
| Bagian | 6. State & Recovery |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Fungsi penjamin ketersediaan `tokenizer, args_h, label_list_step1/2, num_labels_step1/2, pakai_1st` yang dipanggil di awal sel 7a, 8a, 8c, 9a, dan 10.

## Apa yang dilakukan

1. (1) Tokenizer: bila belum ada, muat dari `bert_cache_dir` (default `indo_root/backbones/<dirname>`); tanpa `vocab.txt` → `RuntimeError`.
2. (2) `args_h` SimpleNamespace dari `session_dirs['logs']` & `MAX_SEQ_LENGTH`.
3. **V4**: bila `DOMAIN` diawali 'apps' → `acos_id.taxonomy.patch_processor_labels(processors)` di sini juga (karena `CategorySentiProcessor.get_labels('appsid')` tanpa patch mengembalikan `None` dan meledak di `for cate in l`).
4. (3) Label list: dari `csv/labels_step1.json`/`labels_step2.json`, fallback ke processor upstream; turunkan `num_labels_step1 = len(l[1])`, `num_labels_step2 = len(l[0])`.
5. (4) `pakai_1st` default `True` (kandidat dari prediksi Step 1 = pipeline penuh).
6. Langsung dipanggil sekali: `ensure_objects()`.

## Keluaran / variabel yang dihasilkan

- Fungsi global `ensure_objects()`; objek runtime terjamin.

---
← [Sel 53](053_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell53_05092026.md) | [Indeks](README.md) | [Sel 55](055_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell55_05092026.md) →
