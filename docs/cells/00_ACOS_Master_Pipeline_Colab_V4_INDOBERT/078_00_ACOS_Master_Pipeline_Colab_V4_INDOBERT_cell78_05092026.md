# Sel 78 — `analyze_review_quadruples()` + Contoh Inferensi & Ekspor `master_10`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 78 dari 80 (indeks JSON `cells[77]`) |
| Tipe sel | code |
| Bagian | 10. Inferensi Live |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Fungsi inferensi end-to-end untuk satu teks ulasan dan demonstrasinya pada contoh sesuai bahasa domain.

## Apa yang dilakukan

1. Tokenisasi `review_text.lower()` (maks `MAX_SEQ_LENGTH-2`), tambah `[CLS]`/`[SEP]`, padding ke `max_len`; tensor `t_ids, t_attn, t_seg, t_dummy, t_zero`.
2. Step 1: `model_step1_best(...)` → `pred_tags, imp_a_logit, imp_o_logit`; `imp_aspect/imp_opinion` dari argmax; span dari `_spans_dari_tag`; tambahkan `(-1,-1)` bila implicit atau kosong.
3. Untuk setiap pasangan (aspek × opini): bangun mask `cand_a`/`cand_o` (implicit aspek → posisi 0/[CLS]; implicit opini → posisi `[SEP]`), panggil `model_step2_best(tokenizer, 0, ...)` → `skor` logit 39 kelas.
4. `aktif` = indeks dengan skor > `ambang` (default 0.0) atau argmax; `kategori, sentimen = label.rsplit('#',1)`; peta sentimen `0→negative, 1→neutral, 2→positive`.
5. Kembalikan DataFrame (Aspect, Aspect_Span, Category, Opinion, Opinion_Span, Sentiment, Skor_Logit, Is_Implicit_*) terurut skor.
6. **V4**: `SAMPLE_REVIEWS` per domain — `appsid`: 'transfer nya cepat tapi aplikasi sering error saat buka menu'; `rest16`/`laptop` contoh Inggris.
7. `df_infer = analyze_review_quadruples(sample_review)`; `rep.section('8. Contoh inferensi')`; `export_step_table('master_10_contoh_inferensi')`; `display(df_infer)`; `save_pipeline_state({'df_infer': df_infer})`.

## Keluaran / variabel yang dihasilkan

- Fungsi `analyze_review_quadruples`; `df_infer`; CSV/MD `master_10_contoh_inferensi`; state.

## Prasyarat (sel yang harus sudah berjalan)

- Sel 77.

## Catatan

- Skor_Logit adalah keluaran mentah sebelum sigmoid.

---
← [Sel 77](077_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell77_05092026.md) | [Indeks](README.md) | [Sel 79](079_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell79_05092026.md) →
