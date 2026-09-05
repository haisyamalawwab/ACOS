# Sel 52 — Pulihkan Konfigurasi & Artefak Runtime dari `pipeline_state.pkl`

| Field | Nilai |
|---|---|
| Notebook | `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` (versi Google Drive, 80 sel) |
| Nomor sel | 52 dari 80 (indeks JSON `cells[51]`) |
| Tipe sel | code |
| Bagian | 6. State & Recovery |
| Tanggal dokumentasi | 2026-09-05 |

## Ringkasan

Memuat state (dari `checkpoint_state_path` bila ada, atau pencarian di `candidate_state_roots`) dan menulis ulang variabel global.

## Apa yang dilakukan

1. `candidate_state_roots`: `results_base`, `<base>/Output/results`, `<base>/results`, path Drive ACOS/ACOS-ASLI.
2. Dipulihkan: `DOMAIN, BACKBONE, indo_root, tokenized_dir, base_project_dir, extract_dir, bert_cache_dir` (default `indo_root/backbones/<_backbone_dirname(BACKBONE)>`), `session_dirs, MAX_SEQ_LENGTH, NUM_EPOCHS, STEP2_BATCH_SIZE, STEP2_LR, SEED, device`.
3. Runtime: `label_list_step1/2, label_map_seq, num_labels_step1/2, best_step1/2_f1, best_step1/2_epoch, pakai_1st, df_pairs`; `args_h` dibangun ulang sebagai `SimpleNamespace`.
4. Cetak sesi, domain, device, `completed_stages`; set `_recovered_from_state`.

## Keluaran / variabel yang dihasilkan

- Variabel global terpulihkan; `pipe_state`, `_recovered_from_state`.

## Catatan

- `STEP1_BATCH_SIZE`/`STEP1_LR` tidak dipulihkan di sini (pemulihan diarahkan untuk melanjutkan ke Step 2).

---
← [Sel 51](051_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell51_05092026.md) | [Indeks](README.md) | [Sel 53](053_00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_cell53_05092026.md) →
