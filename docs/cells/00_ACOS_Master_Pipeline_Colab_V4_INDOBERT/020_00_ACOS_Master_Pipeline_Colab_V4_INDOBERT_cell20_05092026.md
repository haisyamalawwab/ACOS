# Sel 20 — Helper `save_pipeline_state()` (pipeline_state.pkl)

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 20 dari 80 (indeks JSON `cells[19]`) |
| Tipe sel | code |
| Bagian | 3. Konfigurasi |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Menyimpan konfigurasi, path, tahapan selesai, dan artefak runtime yang bisa di-pickle ke `pipeline_state.pkl` untuk pemulihan cepat.

## Apa yang dilakukan

1. Deteksi `completed_stages` dari keberadaan artefak: EDA, STEP1, PAIRS (`tokenized_data/{DOMAIN}_test_pair_1st.tsv` di `tokenized_base`), STEP2, EVAL.
2. Kumpulkan runtime serializable: `label_list_step1/2, label_map_seq, num_labels_step1/2, best_step1/2_f1, best_step1/2_epoch, pakai_1st, df_pairs, args_h(dict)`.
3. State V4 menyertakan `BACKBONE, indo_root, acos_root, tokenized_dir` di samping path & hyperparameter V2.
4. Tulis `pipeline_state.pkl` di root sesi + pointer `results_base/latest_pipeline_state_{DOMAIN}.pkl`.
5. Cadangan label ke `csv/labels_step1.json` dan `csv/labels_step2.json`.

## Keluaran / variabel yang dihasilkan

- Fungsi `save_pipeline_state(extra_runtime=None) -> state_file`.

---
← [Sel 19](019_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell19_05092026.md) | [Indeks](README.md) | [Sel 21](021_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell21_05092026.md) →
