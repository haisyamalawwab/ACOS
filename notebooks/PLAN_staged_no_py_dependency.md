# Rencana (revisi): Notebook ACOS STAGED tanpa dependensi `.py`

## 1. Temuan kunci (hasil inspeksi notebook sumber)
- Sumber (`00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`, 62 sel) **sudah** berisi blok helper INLINE (sel ~8–43) yang mendefinisikan: `session_dirs_from_root`, `session_cache_score`, `update_mcp_manifest`, `save_pipeline_state`, `auto_find_file`, `step_stage`, `require_step1_stage`, `ArgsH`, `auto_find_latest_state`, `ensure_objects`. Ini sudah di dalam `.ipynb` → tidak butuh `.py`.
- Satu-satunya pembacaan `.py` dari disk adalah **sel 7**: `importlib.import_module("colab_utils")` + pemilihan salinan (`_utils_missing_symbols`) + fallback unduh GitHub. Inilah yang harus dibuang.
- `notebooks/colab_utils.py` menyediakan simbol yang **tidak** ada di inline: `setup_timestamped_run_dir`, `download_bert_pretrained`, `analyze_and_plot_eda`, `plot_training_history`, `export_benchmark_tables_and_plots`, `display_quadruple_dataframe`, `df_to_markdown`, `export_step_table`, `MarkdownReport`, `SubtaskMetricCapture`, `plot_subtask_metrics`, `features_step1`, `features_step2`, `pair_examples_from_file`, `resolve_eval_pair_file`, `unpack_model_output`, `detect_acos_project_root`, `inspect_acos_drive_structure`, `verify_session_save_paths`, `find_resumable_session`. Hanya `auto_find_file` yang overlap.
- Modul riset yang diimpor dari clone repo (`from modeling import ...` dll., tidak ada inline): `modeling`, `bert_utils.*`, `file_utils`, `run_classifier_dataset_utils`, `eval_metrics`, `dataset_utils`.

## 2. Strategi (dua lapis, pertahankan perilaku)
- **Lapis A — helper utilitas:** pertahankan sel helper inline apa adanya (sudah aman). Ganti **hanya sel 7** (import disk) dengan sel yang mendaftarkan modul `colab_utils` TERTANAM (berisi simbol unik dari `colab_utils.py`) ke `sys.modules` + injeksi `REQUIRED_UTILS` persis seperti sebelumnya. `auto_find_file` tetap otoritas inline (didefinisikan setelah injeksi, menimpa).
- **Lapis B — modul riset:** sematkan sumber 6 modul riset ke dalam sel pustaka sebagai **base64**, daftarkan ke `sys.modules` via `exec` (tanpa tulis file ke disk). Urutan & penanganan paket/relative import di §4.

## 3. Mekanisme sematan (base64 + `types.ModuleType`)
- Generator membaca tiap `.py`, `base64`-encode, tulis sel dengan literal string (ASCII murni → bebas masalah escape; lebih aman daripada json).
- Fungsi `_reg(name, b64, package=None)`:
  - `src = base64.b64decode(b64).decode("utf-8")`
  - `mod = types.ModuleType(name)`; `mod.__file__ = "<embedded:name>"`
  - jika `package`: `mod.__package__ = package`; jika `name == package` (paket): `mod.__path__ = []`
  - modul top-level: `mod.__package__ = ""`
  - `sys.modules[name] = mod`
  - `exec(compile(src, mod.__file__, "exec"), mod.__dict__)`
- Validasi build-time: `ast.parse(src)` tiap sumber; assert simbol wajib ada (§6).

## 4. Urutan pendaftaran (krusial untuk relative import)
1. `file_utils` (top-level)
2. `bert_utils` (paket, `__path__=[]`)
3. `bert_utils.file_utils` (`__package__="bert_utils"`)
4. `bert_utils.tokenization` (`__package__="bert_utils"`) — butuh #3 untuk `from .file_utils import cached_path`
5. `bert_utils.optimization`
6. `run_classifier_dataset_utils`
7. `eval_metrics` — butuh #6 (`from run_classifier_dataset_utils import compute_metrics`)
8. `dataset_utils` — butuh #4 (`from bert_utils.tokenization import BertTokenizer`)
9. `modeling` — butuh #1 (`from file_utils import cached_path, WEIGHTS_NAME, CONFIG_NAME`)
10. `colab_utils` (simbol unik) — daftarkan + inject `REQUIRED_UTILS`

## 5. Perubahan generator (`_build_staged_v2.py`)
- Tambah manifes: daftar `(nama, path_relatif, package)` untuk 9 modul di §4 (baca dari `Extract-Classify-ACOS/` dan `notebooks/`).
- Saat build: baca & base64-encode tiap file (sumber kebenaran tetap `.py` di disk dev).
- Sisipkan sel Markdown `## 1c. Pustaka tertanam (tanpa .py)` + sel kode berisi `_reg` + pemanggilan berurutan.
- **Ganti isi sel 7**: buang `_utils_missing_symbols`, `_prepend_sys_path` dance, `importlib.import_module`, fallback GitHub; ganti dengan registrasi modul `colab_utils` tertanam + `globals().update({n: getattr(_cu, n) for n in REQUIRED_UTILS})` + assert tiap simbol ada.
- Pertahankan sel helper inline (8–43) dan clone repo di sel 2 (data-only). (Opsional: clone bisa dipersempit ke `data/` saja — catatan, bukan wajib.)

## 6. Rekonsiliasi & assert
- `REQUIRED_UTILS` (21 simbol) tetap; diinject dari modul `colab_utils` tertanam.
- Build-time: untuk `colab_utils` tertanam, assert semua `REQUIRED_UTILS` ada; untuk tiap modul riset, assert simbol yang diimpor sel tahap ada: `BertForQuadABSA`, `CategorySentiClassification` (modeling); `BertTokenizer`, `BertAdam` (bert_utils); `processors`, `output_modes`, `compute_metrics` (run_classifier_dataset_utils); `pred_eval`, `pair_eval` (eval_metrics); `read_pair_gold` (dataset_utils); `cached_path`, `WEIGHTS_NAME`, `CONFIG_NAME` (file_utils).
- Pastikan tidak ada penimpaan tak terduga: `auto_find_file` inline tetap menang (didefinisikan setelah injeksi).

## 7. Validasi (lokal, tanpa torch/Colab)
- `json.load` notebook terurai.
- tiap sel kode `ast.parse` valid.
- tiap sumber tertanam: decode base64 → `ast.parse` valid.
- grep: tidak ada lagi `importlib.import_module("colab_utils")`, tidak ada `open(...)` terhadap `colab_utils.py`/`.py` lain dari disk saat runtime, tidak ada `_utils_missing_symbols`.
- Catatan: import nyata butuh `torch`/Colab → verifikasi runtime dilakukan di Colab.

## 8. Risiko & catatan
- Ukuran notebook +~5000 baris (Colab OK).
- Dua `file_utils` (top-level vs `bert_utils.file_utils`) — keduanya didaftarkan di nama masing-masing.
- Perilaku dipertahankan: helper inline tidak diubah; hanya kontrak sel 7 yang diganti (inject dari modul tertanam, bukan file disk).
- Opsi penyempitan (jika terlalu berat): bisa hanya menghilangkan dependensi `colab_utils.py` (Lapis A) dan biarkan modul riset tetap diimpor dari clone. Itu BELUM sepenuhnya bebas `.py`. **Default: embed semua (A+B).**

## 9. Hasil
- `_build_staged_v2.py` diperbarui (membaca `.py` saat build, menyematkan ke sel).
- `00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb` dihasilkan ulang dengan **nol dependensi `.py` saat runtime**.
- Catatan singkat cara menjalankan & memverifikasi di Colab.
