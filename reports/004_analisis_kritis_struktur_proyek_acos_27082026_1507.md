# Analisis Kritis Struktur Proyek ACOS-ASLI

Tanggal analisis: 2026-08-27 15:07
Metode: pembacaan kode statis + inspeksi output tersimpan di notebook. Tidak ada
eksekusi pipeline (environment Windows tanpa `torch`/`pandas`/`seaborn`).

## TL;DR

Repo ini adalah fork dari kode resmi paper ACL 2021 (ACOS Quadruple Extraction)
yang dibungkus ulang menjadi 6 notebook Colab. **Temuan paling penting: notebook
master (00) ternyata SUDAH dieksekusi di Colab (GPU NVIDIA A100-40GB), dan
pipeline-nya GAGAL di tengah.** Step 1 training dan pair-generation berhasil,
tapi Step 2 (klasifikasi kategori-sentimen) crash dengan `KeyError: 'a--1,-1'`.
Akibatnya 3 cell terakhir (evaluasi final, inferensi, ringkasan artefak) tidak
pernah dijalankan. Dengan kata lain: **tidak ada satu metrik pun yang berhasil
dihasilkan dari repo ini**, bertentangan dengan kesan "pipeline end-to-end"
yang tersirat pada `docs/`.

## 1. Isi repo

Repo = dataset ACOS (Restaurant-ACOS & Laptop-ACOS) + implementasi **satu** dari
empat baseline (Extract-Classify-ACOS). Tiga baseline lain yang disebut di
`README.md` (Double-Propagation-ACOS, JET-ACOS, TAS-BERT-ACOS) tidak ada.

Struktur utama:
- `data/` — dataset mentah; tidak dipakai kode mana pun (versi terpakai ada di
  `Extract-Classify-ACOS/tokenized_data/`).
- `Extract-Classify-ACOS/` — kode paper (BERT+CRF step 1, BERT multi-label step 2)
  beserta `bert_utils/`, `eval_metrics.py`, `run_classifier_dataset_utils.py`,
  `tokenized_data/`, `get_1st_pairs.py`, `run.sh`.
- `notebooks/00..05` — suite Colab buatan kontributor.
- `docs/` — 3 rencana implementasi (0001-0003).
- `reports/` — laporan analisis (001-004, termasuk file ini).
- `backups/` — salinan lama notebook & utils.
- `img/` — gambar README.

## 2. Temuan utama: notebook 00 dieksekusi dan GAGAL

Laporan `reports/002` (2026-08-27 07:09) menyatakan seluruh notebook belum pernah
dieksekusi (`execution_count` semua `None`). **Kondisi itu sudah berubah.**
Notebook `00_ACOS_Master_Pipeline_Colab.ipynb` kini memuat 7 dari 10 cell kode
yang sudah dieksekusi, dan hasilnya sudah di-commit (`05fcf2a`).

Hasil eksekusi yang terekam (GPU `NVIDIA A100-SXM4-40GB`):
- Cell 2-6 : mount Drive, clone repo, unduh BERT — sukses.
- Cell 8   : EDA — sukses (rest16: train/dev/test = 1530/171/583; total 3661 quadruple).
- Cell 10  : **Step 1 training — sukses.** 15 epoch, Micro-F1 terbaik = 81.23% (epoch 6).
- Cell 12  : pair generation — sukses; **1451 pasangan kandidat** (74.16% explicit-explicit).
- Cell 14  : **Step 2 — GAGAL: `KeyError: 'a--1,-1'`.**
- Cell 16, 18, 20 (evaluasi final, inferensi dua tahap, ringkasan artefak):
  **`execution_count = None` → tidak pernah dieksekusi.**

Jadi klaim pada `docs/0001-0003` mengenai "15 subtask", "4 implicit subset",
"interactive inference", dan "checkpoint step2" **tidak pernah terwujud** dalam
eksekusi ini. Yang ada hanya: Step 1 terlatih dan dipersist ke
`checkpoints/step1_best/` (di `/content`, hilang begitu sesi Colab berakhir).
Tidak ada checkpoint Step 2, tidak ada laporan Markdown akhir, tidak ada angka
benchmark.

## 3. Akar bug Step 2 (`KeyError: 'a--1,-1'`)

Penyebab persisnya memerlukan `pred4pipeline.txt` hasil sesi Colab (hanya ada di
`/content`, tidak di repo), sehingga tidak bisa direproduksi penuh di sini.
Namun rantai sumbernya jelas dari stack trace:

- `eval_metrics.py:113-123` (`pred_eval`) menulis implicit aspect/opinion sebagai
  token literal `a--1,-1` / `o--1,-1` (prefix `a-`/`o-` + `-1,-1`).
- Cell 12 notebook mem-parsing `pred4pipeline.txt` dan membangun kembali file
  `_test_pair_1st.tsv` dengan logika parsing sendiri yang rapuh (`ele[2:]`).
- Cell 14 membaca file itu lalu `convert_examples_to_features2nd`
  (`run_classifier_dataset_utils.py:444`) memanggil
  `tokenizer.convert_tokens_to_ids(aspect_tokens)`; salah satu token `a--1,-1`
  tidak ada di vocab → `KeyError`.

Ada ketidakselarasan format antara penulis `pred4pipeline.txt` (eval_metrics),
parser cell 12 (notebook), dan pembaca `_test_pair_1st.tsv`
(run_classifier_dataset_utils). Terbukti crash di lapisan paling akhir.

Catatan penting: parsing di cell 12 menduplikasi logika `get_1st_pairs.py` yang
sudah ada di repo. Bila cell 12 cukup memanggil `get_1st_pairs.py` (yang format
outputnya sudah benar: `text####aspan ospan`), duplikasi logika dan bug ini bisa
dihindari.

## 4. Masalah struktural lain

- **3 salinan `colab_utils.py` dengan 2 versi berbeda:**
  - `notebooks/colab_utils.py` = `Extract-Classify-ACOS/colab_utils.py`
    (md5 identik `d641548e...`, 752 baris; versi lengkap yang dipakai notebook).
  - `colab_utils.py` (root, 376 baris, md5 `eef45732...`) = versi **lama/outdated**,
    tidak dipakai siapa pun. Sumber kebingungan bila ada yang mengimpor dari root.
- **`data/raw` tidak dipakai kode mana pun**; tokenized_data yang terpakai.
- **Path absolut upstream** (`/mnt/nfs-storage-titan/...`) masih ada di `run.sh`.
- **Bug upstream yang belum disentuh** (dari laporan 001): `ae_loss` undefined di
  jalur gradient-accumulation/fp16 (`run_step1.py:420-428`); `pdb.set_trace()` di
  `except` yang menggantung non-interaktif (`run_classifier_dataset_utils.py:176-179`).
- **File `.pyc` ter-track di git**, termasuk artefak Python 3.7/3.8/3.9.
- **Tidak ada `requirements.txt`.** Dependensi terdeteksi dari import: torch,
  torchcrf, scikit-learn, tqdm, numpy, matplotlib/seaborn (notebook),
  boto3/requests (opsional).
- **Duplikasi `file_utils.py`** di `Extract-Classify-ACOS/` dan `bert_utils/`.

## 5. Perbedaan klaim vs realita

| Klaim di docs (0001-0003) | Realita |
|---|---|
| Full end-to-end, metrik 15 subtask & 4 implicit subset | Master pipeline crash di Step 2; 3 cell evaluasi tak pernah jalan. Tidak ada metrik. |
| Interactive custom review inference (cell 18) | Tak pernah dieksekusi; bergantung pada checkpoint Step 2 yang tak pernah dibuat. |
| Checkpoint persistence step1_best & step2_best | step1_best ada (di /content, hilang); step2_best tidak pernah dibuat. |
| Laporan Markdown & CSV per run | Sebagian CSV/plot Step 1 dibuat di /content; laporan akhir & tabel metrik final tidak ada. |

Laporan `reports/002` benar bahwa angka benchmark manual (0.784, 0.773, dll.)
sudah dihapus dan diganti jalur metrik nyata — **tetapi jalur itu belum pernah
menghasilkan angka**, karena pipeline berhenti di Step 2.

## 6. Batas verifikasi

- Environment analisis: Windows, Python untuk parsing statis. Tidak ada
  torch/pandas/seaborn → pipeline tidak bisa dijalankan.
- Bukti eksekusi berasal dari output yang tersimpan di notebook 00 (hasil sesi
  Colab). Tidak ada repo file `pred4pipeline.txt` dari sesi tersebut untuk
  reproduksi persis bentuk `a--1,-1`.

## 7. Rekomendasi (prioritas)

1. **Perbaiki bug Step 2** — ganti parsing manual cell 12 dengan pemanggilan
   `get_1st_pairs.py` (atau selaraskan format dengan `convert_examples_to_features2nd`).
2. **Konsolidasi `colab_utils.py`** — hapus versi root yang outdated.
3. Jalankan ulang pipeline sampai **selesai** (Step 2 + evaluasi + inferensi) dan
   commit hasilnya; baru klaim "end-to-end" valid.
4. Tambah `requirements.txt`; bersihkan `.pyc` dari git; tambah smoke-test
   parsing pair agar regresi format ketahuan sebelum training 15 epoch.
