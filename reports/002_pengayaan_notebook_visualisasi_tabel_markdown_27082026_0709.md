# Pengayaan Notebook: Visualisasi, Tabel, dan Ekspor Markdown

Tanggal: 2026-08-27
Ruang lingkup: 6 notebook di `notebooks/` + `colab_utils.py`
Metode verifikasi: parsing AST setiap cell kode, uji unit helper dengan stub.
Pipeline tidak dijalankan (environment ini Python 3.14 tanpa `torch`/`pandas`).

## 1. Permintaan

Memperkaya notebook agar setiap step punya visualisasi, tabel yang ditampilkan
sekaligus diekspor ke CSV, dan hasil teks yang tersimpan sebagai Markdown.

## 2. Temuan sebelum pengayaan

Saat membaca notebook untuk menambahkan visualisasi, ditemukan bahwa notebook
belum pernah dieksekusi sama sekali (`execution_count` semuanya `None`, tidak
ada satu pun `outputs`). Pemeriksaan silang terhadap kode di
`Extract-Classify-ACOS/` menemukan lima masalah yang membuat notebook tidak
mungkin berjalan sampai selesai. Semuanya diperbaiki dalam sesi ini.

### 2.1 Tiga nama fungsi yang tidak ada di repo

Notebook memanggil:

| Dipanggil notebook | Status di repo |
|---|---|
| `convert_examples_to_features_categorysenti` | tidak ada; yang ada `convert_examples_to_features2nd` |
| `processor.get_test_examples` | tidak ada di `CategorySentiProcessor` |
| `processor.get_test_1st_examples` | tidak ada di `CategorySentiProcessor` |

`CategorySentiProcessor` hanya punya `get_train_examples`, `get_valid_examples`,
`get_dev_examples`, `get_labels`, dan `_create_examples`.

### 2.2 Kwarg `domain_type=` yang tidak diterima

Notebook memanggil `convert_examples_to_features(..., domain_type=DOMAIN)`,
tetapi signature aslinya di `run_classifier_dataset_utils.py:264` adalah
`(examples, label_list, max_seq_length, tokenizer, output_mode, task_name)`
tanpa `domain_type`. Ini `TypeError` pada pemanggilan pertama.

### 2.3 `.backward()` dipanggil pada list

`BertForQuadABSA.forward` mengembalikan `[total_loss], [pred_tags, imp_a, imp_o]`
dan `CategorySentiClassification.forward` mengembalikan `[loss], [fused_feature]`.
Loop training di notebook menulis `loss, _ = model(...)` sehingga `loss` menjadi
list `[tensor]`, lalu `loss.backward()` gagal dengan `AttributeError`.

### 2.4 Angka benchmark ditulis manual

Cell dashboard di notebook 00 dan 05 berisi dictionary dengan 15 sub-task dan 5
subset yang seluruh nilainya ditulis tangan (`"Aspect": {"precision": 0.784, ...}`),
lalu diekspor sebagai "hasil benchmark". Angka-angka itu tidak pernah dihitung
oleh kode mana pun di sesi tersebut.

Akar masalahnya: `pair_eval` di `eval_metrics.py:344-363` memang menghitung
metrik untuk 15 kombinasi elemen, tetapi hanya menulisnya ke `logger.info` dan
`return res` hanya mengembalikan metrik keseluruhan. Tidak ada jalur untuk
mengambil angka per sub-task.

### 2.5 Inferensi memakai pencocokan kata kunci, bukan model

Fungsi `analyze_review_quadruples` bekerja dengan rangkaian
`if "food" in lower_text`, `if "service" in lower_text`, dan seterusnya, lalu
menetapkan kategori serta sentimen dari daftar kata. Model tidak pernah dipanggil,
padahal cell diberi judul "Live Inference".

Catatan tambahan: klaim "4 Implicit Subsets" pada heading notebook 05 tidak
didukung kode. `measureQuad_imp` dipanggil per sub-task, bukan per subset
implicit/explicit, dan pemisahan subset 0-4 tidak pernah dihitung.

## 3. Perubahan yang dilakukan

### 3.1 `colab_utils.py` — helper baru

Semua penambahan bersifat aditif; tidak ada fungsi lama yang dihapus.

| Helper | Fungsi |
|---|---|
| `df_to_markdown(df, max_rows, floatfmt)` | DataFrame ke tabel Markdown tanpa dependensi `tabulate`, dengan escape karakter pipe |
| `export_step_table(df, name, csv_dir, md_dir, ...)` | Satu pintu: simpan CSV, tulis file MD, tampilkan tabel di notebook |
| `MarkdownReport` | Akumulator laporan per notebook; mendukung `section`, `text`, `kv`, `table`, `code`, `image`, `save` |
| `SubtaskMetricCapture` | Menangkap metrik 15 sub-task dari log `pair_eval` lewat logging handler |
| `plot_subtask_metrics(df, path)` | Bar chart horizontal Micro-F1 per sub-task |
| `features_step1`, `features_step2` | Wrapper ke `convert_examples_to_features` dan `convert_examples_to_features2nd`, menyerap kwarg berlebih |
| `pair_examples_from_file(processor, file)` | Membangun `InputExample2nd` dari file pair mana pun |
| `resolve_eval_pair_file(dir, domain)` | Memilih `_test_pair_1st.tsv` bila ada, jika tidak `_test_pair.tsv`, sambil melaporkan pilihannya |
| `unpack_model_output(out)` | Mengambil skalar loss dari `([loss], [logits])` |

Perubahan pada fungsi yang sudah ada:

- `setup_timestamped_run_dir`: menambah subfolder `md/`.
- `analyze_and_plot_eda`: menambah dua plot baru (`02b` distribusi panjang
  kalimat + kombinasi implicit/explicit, `02c` heatmap kategori x sentimen).
- `plot_training_history`: kini mengembalikan dict berisi path plot, path CSV,
  dan DataFrame riwayat.

Pendekatan wrapper dipilih agar `Extract-Classify-ACOS/run_classifier_dataset_utils.py`
tidak perlu diubah. Kode paper tetap utuh, notebook menyesuaikan diri ke API asli.

### 3.2 Ekspor per notebook

Jumlah tabel, plot, dan bagian laporan setelah pengayaan:

| Notebook | `export_step_table` | `plt.savefig` | Bagian laporan MD |
|---|---|---|---|
| 00 master pipeline | 12 | 1 | 10 |
| 01 setup & EDA | 7 | 0 (4 plot dari `colab_utils`) | 7 |
| 02 step 1 | 8 | 2 | 8 |
| 03 jembatan pasangan | 5 | 2 | 5 |
| 04 step 2 | 8 | 0 (1 plot dari helper) | 9 |
| 05 evaluasi & inferensi | 7 | 1 | 9 |

Setiap notebook menulis satu file Markdown ke `results/<domain>_<timestamp>/md/`
melalui `rep.save()`, dan setiap tabel juga tersimpan sebagai CSV di
`results/<domain>_<timestamp>/csv/`.

### 3.3 Tabel yang ditambahkan per step

**Notebook 01 (EDA):** statistik per split, preview 25 quadruple beranotasi,
rekap implicit aspect/opinion, distribusi kategori lengkap, distribusi sentimen,
statistik panjang kalimat, daftar artefak.

**Notebook 02 (step 1):** konfigurasi hyperparameter, ringkasan fitur test,
distribusi tag sekuens gold, riwayat metrik per epoch, statistik loss per epoch,
epoch terbaik, hasil akhir test, ringkasan prediksi, detail prediksi per kalimat.

**Notebook 03 (jembatan):** sumber dan jumlah pasangan, distribusi tipe pasangan,
statistik pasangan per kalimat, preview pasangan, 10 kalimat dengan pasangan
terbanyak.

**Notebook 04 (step 2):** konfigurasi, daftar kelas `CATEGORY#SENTIMENT`, sumber
data evaluasi, distribusi label aktif, riwayat per epoch, statistik loss, epoch
terbaik, hasil quadruple final, metrik 15 sub-task.

**Notebook 05 (evaluasi):** konteks evaluasi, metrik quadruple, metrik per
sub-task, agregasi menurut jumlah elemen, dua tabel hasil inferensi, daftar
artefak.

### 3.4 Visualisasi baru

- `02b_eda_length_and_implicit_combo.png` — histogram panjang kalimat dengan
  garis median, plus bar kombinasi implicit/explicit.
- `02c_eda_category_sentiment_heatmap.png` — heatmap 12 kategori teratas x sentimen.
- `02a_step1_data_profile.png` — panjang token WordPiece dan distribusi tag entitas.
- `03b_step1_prediksi_distribusi.png` — sebaran jumlah aspect dan opinion
  terprediksi per kalimat.
- `04b_candidate_pairs_implicit_matrix.png` — matriks implicit vs explicit pada
  pasangan kandidat.
- `05_benchmark_subtasks_f1.png` — Micro-F1 per sub-task dari evaluasi nyata.
- `06_subtask_difficulty_by_element_count.png` — Micro-F1 rata-rata/min/maks
  menurut jumlah elemen yang dievaluasi bersamaan.

### 3.5 Metrik nyata menggantikan angka manual

Dictionary hardcoded dihapus dari notebook 00 dan 05. Penggantinya:

```python
with SubtaskMetricCapture(logger) as cap:
    final_res = pair_eval(..., eval_type="test")
df_subtasks = cap.to_frame()
```

Bila tidak ada metrik yang tertangkap, notebook mencetak catatan bahwa metrik
sub-task tidak tersedia dan melewati tabel serta plotnya, alih-alih menampilkan
angka pengganti.

Notebook juga sekarang melaporkan secara eksplisit apakah kandidat evaluasi
berasal dari prediksi step 1 (skor pipeline penuh) atau dari gold pair (step 2
terisolasi), serta memperingatkan bila checkpoint yang dimuat ternyata bobot BERT
mentah, bukan hasil training.

### 3.6 Inferensi dua tahap yang sebenarnya

`analyze_review_quadruples` di notebook 00 dan 05 ditulis ulang: tokenisasi teks,
jalankan `BertForQuadABSA` untuk mendapat tag CRF, ubah tag menjadi span dengan
pola yang sama seperti `eval_metrics.pred_eval` (`32*` untuk aspect, `54*` untuk
opinion, offset dikurangi 1 karena `[CLS]`), deteksi implicit dari dua classifier
biner, lalu untuk setiap pasangan kandidat jalankan `CategorySentiClassification`
dan ambil label di atas ambang. Keluaran menyertakan `Skor_Logit` supaya terlihat
seberapa yakin model.

## 4. Verifikasi yang dilakukan

- Parsing AST setiap cell kode di 6 notebook: semua lolos (46 cell kode total).
- Pemeriksaan urutan definisi: tidak ada nama yang dipakai sebelum terdefinisi
  bila cell dijalankan berurutan dari atas.
- Pencarian residu: tidak ada lagi `convert_examples_to_features_categorysenti`,
  `get_test_1st_examples`, `get_test_examples`, `domain_type=DOMAIN`, maupun
  angka `0.784`/`0.773`/`0.535` dan dictionary `subtasks_results`.
- `SubtaskMetricCapture` diuji terhadap format log persis dari `eval_metrics.py`
  (`"***** %s results *****"` dan `"  {} = {:.2%}"`): 3 sub-task uji tertangkap
  dengan nilai benar, dan blok `"***** Test results *****"` diabaikan agar tidak
  masuk tabel sub-task.
- `df_to_markdown` diuji: header, format float 4 desimal, escape pipe, tabel
  kosong, catatan pemotongan baris.
- `MarkdownReport` diuji end-to-end: heading, tabel key-value, tabel DataFrame,
  blok kode, path gambar relatif.
- `unpack_model_output` diuji untuk input list maupun skalar.

## 5. Backup

Sesuai `.agents/skills/karpathy-guidelines.md` bagian 5:

```
backups/notebooks/*.ipynb.bak_20260826   (6 notebook)
backups/py/colab_utils.py.bak_20260826
```

## 6. Yang belum terverifikasi

- Pipeline belum dijalankan. Environment ini Python 3.14 tanpa `torch`, `pandas`,
  `matplotlib`, atau `seaborn`, jadi tidak ada eksekusi end-to-end.
- Angka metrik apa pun belum pernah dihasilkan repo ini; notebook sekarang
  menyediakan jalurnya, bukan hasilnya.
- Bentuk tepat `candidate_aspect`/`candidate_opinion` untuk kasus implicit pada
  fungsi inferensi disusun mengikuti pola di `convert_examples_to_features2nd`
  dan `pair_eval`, tetapi belum dibandingkan dengan keluaran nyata karena butuh
  checkpoint terlatih.
- Lima file porting yang dianalisis di laporan 001 tidak diubah dalam sesi ini.
