# 035 — Keunggulan V4_1_IndoBERT vs V2_PRO: Fleksibilitas, Storage, Resume, Output

Tanggal: 12-09-2026. Objek: `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` (29 cells, V2_PRO) vs `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb` (80 cells, V4_1). Metode: parse JSON notebook + hitung kemunculan string literal (bukan inferensi).

## 1. Kesimpulan (4 baris)

1. V4_1 adalah superset V2_PRO, bukan arsitektur baru: `drive.mount`, `IS_COLAB/HAS_DRIVE`, `pipeline_state.pkl`, `session_manifest.json` identik.
2. Keunggulan riil V4_1: eksekusi bertahap (80 vs 29 cells), dual-root storage, resume per-epoch.
3. Klaim yang TIDAK terbukti di kedua notebook: deteksi eksplisit JupyterLab/Kaggle, tombol download/zip.
4. Harga yang dibayar V4_1: kompleksitas +80 cells, ketergantungan `colab_utils` 21 nama, 2 root yang bisa tertukar bila salah konfigurasi.

## 2. Bukti hitungan (terverifikasi)

| String | V2_PRO | V4_1 |
|---|---|---|
| `drive.mount` | 1 | 1 |
| `IS_COLAB` / `HAS_DRIVE` | 1 / 2 | 1 / 3 |
| `get_ipython`, `JUPYTER`, `JupyterLab`, `KAGGLE`, `PLATFORM` | 0 semua | 0 semua |
| `step_stage` / `require_vars` | 0 / 0 | 43 / 30 |
| `indo_root` / `acos_root` | 0 / 0 | 35 / 11 |
| `candidate_result_roots` / `candidate_state_roots` | 0 / 0 | 2 / 2 |
| `step1_resume.json` / `step2_resume.json` / `optimizer.pt` | 0 / 0 / 0 | 6 / 6 / 6 |
| `MAX_EPOCHS_THIS_RUN` / `STEP1_RESUME_EPOCH` / `STEP2_RESUME_EPOCH` | 0 / 0 / 0 | 3 / 5 / 5 |
| `SKIP_TRAINING` | 0 | 31 |
| `files.download`, `zipfile`, `.zip`, `save_pretrained` | 0 semua | 0 semua |
| `progress.json` / `run_result.json` / `backbone_report.json` | 0 / 0 / 0 | 6 / 3 / 2 |
| `torch.save` / `json.dump` / `to_csv` / `dpi=300` | 2 / 4 / 1 / 1 | 8 / 12 / 3 / 1 |

## 3. Per aspek

### 3.1 Fleksibilitas Colab / Lokal / JupyterLab

* Sama: cell 02 keduanya `try: from google.colab import drive; drive.mount(...) except: lokal`. Deteksi `IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")`.
* Beda V4_1 cell 08: `drive_candidates=[MyDrive/ACOS, MyDrive/ACOS-ASLI]` + auto-scan `if "acos" in item.lower()`, plus validasi `Extract-Classify-ACOS/data`. V2 cell 04 hanya `MyDrive/ACOS` tunggal lalu fallback `/content/ACOS`, `./`, `../`, `abspath("ACOS")`.
* Beda V4_1 cell 05-06: `class step_stage` + `require_vars(*names)`. V2 tidak punya (0 hit). Dampak: V4_1 bisa skip per-sel (`STEP*_SKIP_TRAINING`, cell 36/61), V2 hanya skip per-blok besar (cell 12/22).
* Batas kritis: tidak ada string JupyterLab/Kaggle di keduanya. Klaim "support JupyterLab" hanya benar secara implisit (jalur lokal `abspath`), bukan deteksi khusus. Jangan dioverclaim.

### 3.2 Penyimpanan

* V2: single-root. `base_project_dir=/content/drive/MyDrive/ACOS`, `save_dir=base/Output`, `results_base=save_dir/results`, `bert_cache_dir=bert_base_uncased`.
* V4_1 cell 11: dual-root. `indo_root` (ditulis: dataset, tokenized, backbones, results) vs `acos_root` (baca saja, upstream Inggris). Penanda `acos_id/` via `_cari_indo_root()` (Drive 3 kandidat + lokal 4 kandidat).
* V4_1 cell 13: cache per-backbone `_backbone_dirname()` (`indobert_base_p1` vs `bert_base_uncased`). V2 hanya satu folder Inggris. Ini keunggulan anti-tabrakan vocab, tapi juga risiko: salah `BACKBONE/DOMAIN` = salah cache.
* V4_1 cell 16: `candidate_result_roots` 5 path (vs V2 `find_resumable_session(results_base)` tunggal). Cell 79 audit eksplisit `is_drive_saved="/content/drive/MyDrive" in path` (TERSIMPAN DI DRIVE vs LOKAL/EPHEMERAL); V2 cell 28 hanya list file tanpa flag Drive.

### 3.3 Lanjut session terputus

* V2 (cell 06/14/16/18): `save_pipeline_state()->pipeline_state.pkl`, `auto_find_latest_state(search_base:str)` tunggal, `ensure_objects()` fallback, cache-hit `step*_already_done = exists(bin) and exists(pred)`. Granularitas: level best-checkpoint saja.
* V4_1 (cell 19/36/44/48/50/51/53/61/67): sama + (a) `step*_resume.json{last_completed_epoch,history,best_f1}`, (b) `checkpoints/step*_epoch_N/pytorch_model.bin+optimizer.pt`, (c) `start_epoch=_resume_ep+1`, (d) `MAX_EPOCHS_THIS_RUN=1` cicilan anti-timeout, (e) pointer `latest_pipeline_state_{DOMAIN}.pkl` + cek `pickle["DOMAIN"]`, (f) `candidate_state_roots` 7 path.
* Batas kritis: resume per-epoch V4_1 hanya berguna bila `optimizer.pt` + epoch ckpt selamat di Drive. Putus sebelum epoch-1 selesai = tetap ulang dari awal. `MAX_EPOCHS_THIS_RUN=1` mengurangi risiko timeout tapi menambah jumlah eksekusi manual.

### 3.4 Simpan output result

* Sama: `torch.save(state_dict->pytorch_model.bin)`, `config.to_json_file`, `tokenizer.save_vocabulary`, `master_metrics.json`, `pred4pipeline.txt`, `*.csv via to_csv`, `plt.savefig(dpi=300)`.
* Tambahan V4_1 saja: `logs/step*_progress.json` (terbaca dari Drive walau tab tertutup), `step*_run_result.json`, `logs/backbone_report.json`, `gate1_weights.json`, `id_gates.json`, `candidate_pairs_summary.csv`.
* Batas kritis: tidak ada `files.download/zip` di keduanya. Persistensi = path Drive, bukan tombol unduh. Backup manual tetap tanggung jawab pengguna.

## 4. Yang bukan keunggulan (anti-overclaim)

1. Bukan "support JupyterLab/Kaggle native" — tidak ada kode deteksinya.
2. Bukan "auto-download hasil" — tidak ada kodenya.
3. Bukan "resume sempurna" — V2 resume best-model, V4_1 resume epoch; keduanya gagal bila Drive tidak ter-mount atau sesi kosong (`session_cache_score 0/6`).
4. V4_1 menambah 51 cells + kontrak `colab_utils` 21 nama (cell 09): satu nama hilang = salinan ditolak. Fleksibilitas dibayar dengan kerapuhan impor.

## 5. Rekomendasi pakai

* Colab gratisan, sering idle-timeout: pakai V4_1, set `MAX_EPOCHS_THIS_RUN=1`, pastikan Drive ter-mount sebelum cell 08.
* Lokal/JupyterLab stabil, dataset Inggris rest16: V2_PRO cukup, lebih sederhana.
* Sebelum klaim "lanjut otomatis", cek `session_cache_score`, `latest_pipeline_state_{DOMAIN}.pkl`, dan `step*_resume.json` di Drive.
