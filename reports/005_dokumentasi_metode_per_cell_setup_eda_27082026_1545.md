# Dokumentasi Metode & Teknik per Cell — 01. Setup, Pretrained Caching & EDA

Tanggal: 2026-08-27
Objek: `notebooks/01_ACOS_Setup_and_Data_Exploration.ipynb`
Metode: pembacaan statis seluruh cell (7 code + 10 markdown). Tidak dieksekusi.

---

## 0. Ringkasan Eksekutif

Notebook 01 adalah **tahap persiapan + analisis data**. Tidak ada training model. Ia memastikan environment siap (GPU/deps), cache pretrained BERT lokal, dan melakukan EDA menyeluruh atas dataset ACOS. Output: 7 tabel CSV + 4 plot PNG 300dpi + 1 laporan Markdown.

Tujuh cell kode:
1. Deteksi Colab/local + install deps + cek GPU
2. Resolusi path + import `colab_utils`
3. Init direktori timestamped + akumulator Markdown
4. Download & verifikasi cache BERT
5. EDA — statistik per split
6. EDA — preview, implicit, kategori, sentimen, panjang kalimat
7. Tampilkan plot + ringkasan artefak

---

## 1. Diagram Alur Konseptual

```
┌─────────────────────────────────────────────────────────────┐
│              NOTEBOOK 01: SETUP + EDA                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Cell 2]  Env: deteksi Colab/local → pip install            │
│            → cek GPU (VRAM, device cuda/cpu)                 │
│      │                                                       │
│  [Cell 4]  Path: deteksi repo (auto-clone bila kosong)       │
│            → sys.path → import colab_utils (+fallback URL)   │
│      │                                                       │
│  [Cell 6]  Session: DOMAIN → setup_timestamped_run_dir()     │
│            → subfolder plots/csv/md/logs/checkpoints         │
│            → MarkdownReport(title, filename, meta)           │
│      │                                                       │
│  [Cell 8]  BERT cache: download_bert_pretrained()            │
│            → config.json + pytorch_model.bin + vocab.txt     │
│            → assert keberadaan + ukuran MB                   │
│      │                                                       │
│  [Cell 10] EDA: analyze_and_plot_eda(data/)                  │
│            → df_stats + df_records → CSV + plot              │
│      │                                                       │
│  [Cell 12] Analisis lanjut: preview 25 quad, implicit,       │
│            kategori, sentimen, panjang kalimat               │
│      │                                                       │
│  [Cell 14] Render 4 plot inline + daftarkan ke report        │
│      │                                                       │
│  [Cell 16] Walk dirs → daftar artefak → rep.save()           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Detail Metode/Teknik per Cell

### Cell 2 — Environment Setup
- **Teknik**: `try/import google.colab` → flag `IN_COLAB` (bukan hardcode).
- Instalasi: `pytorch-crf`, `transformers`, `huggingface_hub`, `seaborn`, `scikit-learn`, `matplotlib`, `pandas`, `boto3`.
- Deteksi GPU: `torch.cuda.is_available()` → nama GPU + total VRAM (GB); fallback CPU.
- **Perbedaan vs notebook 00**: di sini `IN_COLAB` dipertahankan sebagai variabel (di 00 langsung mount Drive).

### Cell 4 — Path Resolution & Import
- Identik dengan notebook 00 cell 4: deteksi lokasi repo berlapis, auto-clone `haisyamalawwab/ACOS`, `sys.path.insert` tiga jalur, import `colab_utils` dengan fallback download dari raw GitHub.
- Mengimpor **18 helper** sekaligus (termasuk yang tidak dipakai notebook ini — `plot_training_history`, `export_benchmark_tables_and_plots`, dsb.). Ini pola "import semua sekali" untuk keseragaman antar notebook.

### Cell 6 — Session Init
- `DOMAIN = "rest16"` (bisa `laptop`).
- `setup_timestamped_run_dir()` → `results/<domain>_<DDMMYYYY_HMS>/`.
- Ambil alias `md_dir`, `plots_dir`, `csv_dir`, `logs_dir`.
- `MarkdownReport(...)` dengan `filename="01_setup_dan_eda.md"` + meta (domain, session_dir, device).

### Cell 8 — BERT Caching
- `download_bert_pretrained(target_dir=bert_cache_dir)` — unduh 3 file (`config.json`, `pytorch_model.bin`, `vocab.txt`) dari HuggingFace Hub, skip bila sudah ada.
- Verifikasi ketat: `assert os.path.exists` per file + cetak ukuran MB.
- **Tujuan**: menggantikan URL S3 legacy yang mati (lihat laporan 001/002).

### Cell 10 — EDA (Statistik per Split)
- `analyze_and_plot_eda(data_dir, domain, plots_dir, csv_dir)` → mengembalikan `(df_stats, df_records)`.
- `df_stats`: per split (train/dev/test) → jumlah kalimat, total quadruple, explicit/implicit aspect & opinion, count sentimen 0/1/2.
- `export_step_table()` → simpan CSV + Markdown + tampilkan.
- Penanganan kosong: `if df_stats is None or df_stats.empty` → peringatan, bukan crash.

### Cell 12 — Analisis Lanjut (5 sub-analisis)
1. **Preview 25 quadruple** beranotasi (`df_records.head(25)`).
2. **Rekap implicit vs explicit** — hitung jumlah & persen implicit aspect, implicit opinion, dan kombinasi keduanya (`&` boolean).
3. **Distribusi kategori** — `value_counts()` kategori aspek + persen.
4. **Distribusi sentimen** — map `0/1/2` → nama, lalu `value_counts()`.
5. **Statistik panjang kalimat** — `df_records["Text_Length"].describe()` (count/mean/std/min/quartile/max).

### Cell 14 — Render Plot Inline
- Daftar 4 plot: distribusi dataset, kategori×sentimen, panjang kalimat+kombinasi implicit, heatmap kategori×sentimen.
- Loop `os.path.exists` → `display(Image(path))` + `rep.image()`; plot hilang dilewati dengan pesan.
- Hitung `shown/total` plot yang tampil.

### Cell 16 — Ringkasan Artefak
- `_list_dir()` → walk CSV/Plot/Markdown/Log, kumpulkan nama + ukuran KB.
- `rep.save()` → tulis file Markdown final `01_setup_dan_eda.md`.
- Print path laporan + hint lanjut ke notebook 02.

---

## 3. Pola Teknis Menonjol

| Pola | Penerapan |
|------|-----------|
| **Defensive EDA** | Setiap `df_*.empty` dicek sebelum diproses; tidak crash bila data kosong |
| **Dual output konsisten** | `export_step_table` = CSV + MD + tampil; `rep.table` = laporan |
| **Verifikasi keras di titik kritis** | `assert os.path.exists` untuk 3 file BERT |
| **Fallback import** | `colab_utils` diunduh dari raw GitHub bila import gagal |
| **Render selektif** | Plot hanya ditampilkan bila file benar-benar ada |

---

## 4. Artefak yang Dihasilkan

| Jenis | File |
|-------|------|
| CSV | `eda_dataset_statistics.csv`, `eda_all_samples_annotated.csv` (dari helper) + `eda_01`–`eda_07` (dari `export_step_table`) |
| Plot | `01_eda_dataset_distribution.png`, `02_eda_category_sentiment.png`, `02b_eda_length_and_implicit_combo.png`, `02c_eda_category_sentiment_heatmap.png` |
| Markdown | `01_setup_dan_eda.md` |

---

## 5. Catatan Kritis

1. **Notebook 01 tidak menghasilkan model** — murni setup + EDA; lanjutan ada di notebook 02.
2. **Import berlebih**: 18 helper diimpor, hanya sebagian dipakai (mis. `plot_training_history`, `SubtaskMetricCapture`, `features_step1/2` tidak terpakai di sini). Tidak berbahaya, tapi tidak ramping.
3. **EDA bergantung folder `data/` mentah** (bukan `tokenized_data/`). Bila folder `data/` tidak ada (seperti saat clone fresh tanpa LFS), seluruh EDA kosong dan hanya cetak peringatan.
4. **`Text_Length` dihitung per quadruple, bukan per kalimat unik** — baris kalimat dengan banyak quadruple akan terhitung berulang di statistik panjang kalimat (bias ringan).
5. **Sentimen `int(q_parts[2]) if isdigit() else 1`** (di `colab_utils`) — fallback ke neutral bila token sentimen non-digit, menutupi potensi data korup secara diam-diam.
6. **VRAM tampil tapi tidak dipakai untuk keputusan** — murni informatif; tidak ada branch ukuran batch berdasar VRAM.
