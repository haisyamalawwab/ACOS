# Laporan 040 — Analisis Mendalam dan Kritis atas Folder Drive `results` (ACOS-IndoBERT)

> **Tanggal penyusunan:** 2 November 2026, 21.58 WIB
> **Objek:** Google Drive folder **`results`** — `1vKiRYlU2K9cNQWgXV4JBO5u-7DdtiAFq` (induk `1BdDhLujQHAHqJR5HqXN96lYA3drApgjN`, diubah 5 Sep 2026 12:27:40Z)
> **Sifat:** baca-saja. Tidak ada berkas yang diunggah, diubah, atau dihapus di Drive.
> **Pelengkap:** laporan 039 (peta repo) dan 038 (audit kritis). Laporan ini **tidak menimpa** keduanya; ia menguji ulang klaim 036/039 terhadap artefak Drive.
> **Lampiran data:** `reports/040_data/inventaris_drive.csv`, `rekonsiliasi_klaim_drive.csv`, `run_cv_27092026.csv`, `temuan_kritis.csv`
>
> **Tindak lanjut:** laporan **041** (`reports/041_analisis_mendalam_notebook_02112026_HM.md`) menambahkan jejak notebook untuk angka-angka di sini: 47,68 ↔ 48,24 (`04` sel 12), 78,72/81,93/69,56 ↔ 78,95/82,51/70,11 (`04` sel 12), dan menandai 66,28% serta 97,94% sebagai agregasi/cache-hit. Isi laporan ini tidak diubah.

---

## 1. Ringkasan eksekutif

Folder ini **bukan** folder kosong dan **bukan** duplikat repo. Isinya tiga hal yang selama ini hanya "terdokumentasi" di laporan: **checkpoint bobot terlatih**, **riwayat training per epoch**, dan **matriks 54 run cross-validation**. Karena itu laporan 040 mengubah peta bukti 039 secara material:

1. **Tiga artefak naik dari E3 ke E1.** Gate-1 (`199/199`, mean tensor identik) benar-benar ada sebagai berkas; lima gerbang data juga lulus di lingkungan Colab; dan tiga set checkpoint IndoBERT Apps-ACOS tersimpan lengkap (`step1_best`, `step2_best`, `step2_epoch_3`). Klaim "tidak ada checkpoint" di 039 **terbantah** — yang benar: checkpoint tidak ada **di repo**, tetapi ada di Drive.
2. **Empat angka 036 terkonfirmasi persis.** Step-1 appsid `97,94%` (epoch 8, TP 16.514/FP 434/FN 259); Gate-1 `199/199`; lima gerbang data; dan status CV "nol skor" (bahkan lebih tegas: `93` berkas `run_result.json` semuanya `ERROR`).
3. **Tiga klaim 036 harus dikoreksi.** (a) `67,86%` **bukan** angka sesi yang ada di folder ini — sesi ini mencatat `67,16 / 66,55 / 69,00`; (b) Step-2 sesi ini berhenti di **3/15 epoch**, bukan selesai; (c) klaim "baseline BERT tidak punya skor end-to-end" **salah** — ada sesi BERT-rest16 dengan **QUAD 47,68%** dan dekomposisi 15 subtask `47,03%`.
4. **Dua temuan baru yang serius.** (a) Metrik dua kepala Step-2 bernilai **0,0 secara permanen** di CSV dan `resume` (bukan sekadar tampilan), sehingga tidak ada bukti empiris kepala kategori/sentimen belajar; (b) **`master_08` yang ada di Drive adalah milik REST16**, bukan Apps-ACOS — laporan 036 mengutip `master_08` Apps-ACOS yang tidak ada di folder ini, dan menyatakan "TP/FP/FN lengkap di CSV", padahal CSV yang ada justru mengosongkan TP/FP/FN.
5. **Angka `66,28` vs `67,86` bukan soal "definisi TP" atau dedup.** Keduanya berasal dari **dua run berbeda** dengan volume kandidat berbeda: `66,28` dihitung atas `19.528` elemen gold + `24.066` prediksi; `67,86` atas `9.006` gold + `10.605` prediksi. Penjelasan di 035/036 dan dugaan di 039 tidak didukung artefak.
6. **`25.992` span bergeser** yang tercatat di `embedding_audit.csv` bukan cacat baru — saya reproduksi angkanya persis dari repo (`20.615 + 2.742 + 2.635 = 25.992`). Artinya klaim "0 span defect" di 039 benar secara harfiah, tetapi **menyesatkan** sebagai jaminan integritas label: `14,12%` span berubah offset dan `35,26%` baris berubah teks setelah retokenisasi.
7. **Narasi "+14 juta parameter karena vocab 30.521 vs 50.000" adalah salah tafsir.** Checkpoint menyimpan `vocab.txt` yang diawali `[PAD] [UNK] [CLS] [SEP] [MASK] ##an d ##er ...` — tokenizer IndoBERT asli. Embedding `50.000 × 768` adalah desain IndoBERT; baris di atas `30.520` tidak pernah diindeks. Tidak ada pemborosan 14 juta parameter yang perlu "diperbaiki".

**Putusan satu baris:** folder ini menaikkan kredibilitas *data, gerbang, checkpoint, dan Step-1*, tetapi **tidak** menyelamatkan *Step-2 Apps-ACOS* maupun *cross-validation*; justru memperlihatkan bahwa dua angka yang paling sering dikutip (`67,86` dan `66,28`) berasal dari sesi/run yang tidak berada di folder ini.

### 1.1 Matriks putusan ringkas

| # | Pertanyaan | Jawaban 040 | Bukti utama |
|---|---|---|---|
| 1 | Apakah checkpoint benar-benar ada? | **Ya**, 3 set, 475–500 MB per model | `checkpoints/step1_best`, `step2_best`, `step2_epoch_3` |
| 2 | Apakah Gate-1 nyata? | **Ya**, 199/199, mean identik | `logs/gate1_weights.json` (`1IOp-tXL…`) |
| 3 | Apakah Step-1 97,94% nyata? | **Ya**, tetapi hanya 8/15 epoch | `logs/step1_run_result.json`, CSV 8 baris |
| 4 | Apakah Step-2 67,86% dari sesi ini? | **Tidak**, sesi ini 67,16 / 69,00 | `csv/step2_training_history.csv` |
| 5 | Apakah 15 subtask punya CSV? | **Tidak untuk appsid**; CSV yang ada = rest16 | `master_08_metrik_subtask.csv` (REST16) |
| 6 | Apakah CV menghasilkan skor? | **Tidak**, 93 `run_result.json` = ERROR | `experiments_27092026/*/run_result.json` |
| 7 | Apakah baseline BERT punya skor? | **Ya**, 47,68% (BERT-rest16) | `master_metrics.json`, `master_07`, `master_09` |
| 8 | Apakah metrik dual-head 0 hanya tampilan? | **Tidak**, tersimpan 0,0 | CSV + `step2_resume.json` |

---

## 2. Ruang lingkup, metode, dan batasan

### 2.1 Metode

1. **Enumerasi rekursif** seluruh folder dengan `files.list` (`q = '<id>' in parents`), termasuk subfolder `csv`, `logs`, `md`, `plots`, `checkpoints`, `reports`, `_gates`, `_eda`, `_embedding`, `_backbone`.
2. **Pembacaan isi** 24 berkas teks (JSON/CSV/MD/TXT) memakai ekstraksi teks Drive; berkas >1 MB dibaca pada 1.500–4.000 karakter pertama untuk identifikasi format, bukan untuk agregasi.
3. **Verifikasi silang** setiap angka Drive terhadap (a) berkas repo, (b) keluaran notebook yang tereksekusi, (c) hitung ulang mandiri dengan Python stdlib.
4. **Sampel run CV**: 4 dari 54 `run_idx` dibaca penuh; seluruh 93 `run_result.json` diperiksa ukurannya (569–591 byte) untuk memastikan tidak ada metrik di dalamnya.

### 2.2 Batasan yang harus dibaca sebelum mengutip

| Batasan | Konsekuensi |
|---|---|
| Bobot 475 MB tidak diunduh | Klaim tentang isi bobot (mis. kepala benar-benar terlatih) tetap **tidak** dapat dipastikan; yang terbukti hanya keberadaan + config + tokenizer |
| Lingkungan tanpa `torch` | Tidak ada inferensi ulang, tidak ada dump logits, tidak ada uji `save_pretrained` |
| Drive API memotong daftar pada 100 entri | Jumlah folder sesi dihitung lewat kueri nama (34 `cv5fold` + 60 `cv10fold` = 94), bukan dari satu daftar |
| Berkas >2 juta karakter tidak dibaca utuh | `logs/result.txt` (1,30 MB) dan `pred4pipeline.txt` (512 KB) hanya diidentifikasi formatnya |
| Folder yang dianalisis = yang diberikan user | Sesi `appsid_08092026_150437` dan `rest16_12092026_104518` yang dirujuk 036 **tidak** ada di folder ini |

---

## 3. Peta isi folder

### 3.1 Tingkat root

| Nama | ID | Jenis | Isi | Status |
|---|---|---|---|---|
| `appsid_05092026_122741` | `1IUh17tPAMwwr5SBOSVqJFTUY-eSR7VuZ` | sesi | 51 berkas (16 csv, 9 md, 9 log/json + 1 folder gerbang, 6 plot, 8 checkpoint) | **berhenti di Step-2 epoch 3/15** |
| `experiments_26092026` | `12YJUYK7y0ghJ8zblC8_qcrnEFSwsLL95` | eksperimen | kerangka kosong + 7 berkas | **gagal sebelum mulai** |
| `experiments_27092026` | `1J5t0O-uF2EBxYhVIkuKSj_c9qtqram5u` | eksperimen | 94 folder sesi + 4 folder tokenized | **54 run, semuanya ERROR** |
| `latest_pipeline_state_appsid.pkl` | `1EAYUj79mmk4BKvUJA8Ut4RTjbw0_TDY3` | state | 775.330 B | salinan `pipeline_state.pkl` sesi |

### 3.2 Sesi `appsid_05092026_122741`

| Kelompok | Jumlah | Catatan |
|---|---|---|
| `csv/` | 16 | `master_00`, `00b`, `00c`, `01`, `02`, `03`, `04`, `05`, `step1/step2_training_history`, `labels_*`, `candidate_pairs_summary`, `eda_*` |
| `logs/` | 9 + 1 folder gerbang | `step1_run_result`, `step1_progress`, `step2_progress`, `step2_resume`, `gate1_weights`, `id_gates`, `backbone_report`, `result.txt`, `pred4pipeline.txt`; `logs/gates/_gate2_en` |
| `md/` | 9 | hanya `master_00`–`master_05`; **tidak ada** `master_06`–`master_09` |
| `plots/` | 6 | EDA + kurva loss/F1 Step-1; **tidak ada** plot Step-2 final |
| `checkpoints/` | 3 folder, 8 berkas | `step1_best`, `step2_best`, `step2_epoch_3`, `optimizer.pt` 991 MB |
| Akar sesi | 2 | `session_manifest.json`, `pipeline_state.pkl` |

**Yang tidak ada di sesi ini (penting):** `master_06_step2_riwayat.csv`, `master_07_metrik_quadruple_final.csv`, `master_08_metrik_subtask.csv`, `master_09_agregasi_elemen.csv`, `logs/master_metrics.json`, `step2_run_result.json`. Artinya **evaluasi final Step-2 belum pernah dijalankan** pada sesi ini. Semua angka Step-2 di sesi ini berhenti pada riwayat training 3 baris.

### 3.3 `experiments_26092026` vs `experiments_27092026`

| Aspek | 26/09/2026 | 27/09/2026 |
|---|---|---|
| Folder sesi | 0 | 94 (34 `cv5fold` + 60 `cv10fold`) |
| Berkas hasil | 0 di `csv/plots/md/logs` (menurut `REPORT_INDEX`); 7 berkas tersebar di root/_gates/_backbone/reports | 93 `run_result.json`, semuanya ERROR |
| State | 483 B (kosong) | — |
| Gerbang | `taxonomy=True, vocab=True, tokenized_n=7` | `taxonomy=True, vocab=True, tokenized_n=6` |
| Audit embedding | — | `span_bergeser=25.992`, `unk=0` |
| Kesimpulan | kerangka yang tidak pernah diisi | percobaan besar yang gagal seragam |

---

## 4. Bukti yang berhasil dinaikkan (E3 → E1/E2)

### 4.1 Gate-1 (E1)

`logs/gate1_weights.json` (`1IOp-tXLqOIpg5ccY6Ldz-OC4zCxnUweg`, 949 B):

| Probe | Bentuk | Mean checkpoint | Mean model | Status |
|---|---|---|---|---|
| `bert.embeddings.word_embeddings.weight` | `[50000, 768]` | −0,0008125695749185979 | −0,0008125695749185979 | LULUS |
| `bert.encoder.layer.0.attention.self.query.weight` | `[768, 768]` | 7,764318979752716e−06 | 7,764318979752716e−06 | LULUS |
| `bert.encoder.layer.11.output.dense.weight` | `[768, 3072]` | 1,6511888816239662e−06 | 1,6511888816239662e−06 | LULUS |

`n_key_bert_model = 199`, `n_key_bert_checkpoint = 199`, `n_key_model_tanpa_padanan = 0`, `ok = true`. Ini **menutup** keraguan 036 §III dan 039 K-gate: klaim "199/199" bukan narasi, melainkan keluaran terukur.

### 4.2 Lima gerbang data (E1)

`logs/id_gates.json` (`18uB4X9ui7oorrcppJ-HFUDsEutyyuVSG`, 5.528 B):

| Gerbang | Status | Angka kunci |
|---|---|---|
| `taxonomy` | ok | 13 kategori, 39 label Step-2, 6 label Step-1, selisih `[]` |
| `dataset` | ok | 28.839 / 3.991 / 3.991 review; tumpang tindih `{}` |
| `acos_build` | ok | 60.159/8.027/7.891 baris; 72.973/9.587/9.514 quad |
| `tokenized` | ok | quad hilang 0 di tiga split; `pair_ada=true` |
| `gate2_english` | ok | rest16 quad 1.530/171/583 identik; pair beda 1 (toleransi 1) |

Catatan penting: **kegagalan `acos_id.selftest` di mesin lokal 039 adalah kegagalan lingkungan**, bukan kegagalan gerbang. Di Colab, kelima gerbang lulus dengan angka yang sama seperti yang dilaporkan 036.

### 4.3 Checkpoint (E1) — koreksi langsung atas 039

| Folder | Berkas | Ukuran | Tafsir |
|---|---|---|---|
| `checkpoints/step1_best` | `pytorch_model.bin`, `config.json`, `vocab.txt` | model 500.244.267 B (477,1 MB) | BERT-CRF + dua kepala implisit; +2,3 MB di atas backbone 497.831.231 B |
| `checkpoints/step2_best` | `pytorch_model.bin`, `config.json`, `vocab.txt` | model 497.946.703 B (474,9 MB) | Step-2 dengan dua kepala (≈29 ribu parameter tambahan) |
| `checkpoints/step2_epoch_3` | `pytorch_model.bin`, `optimizer.pt` | 497.946.703 B + optimizer 991.121.547 B (945,2 MB) | titik resum terakhir |

`config.json` di dalam checkpoint: `hidden_size 768`, `num_hidden_layers 12`, `num_attention_heads 12`, `vocab_size 50000`, `max_position_embeddings 512`. `vocab.txt` 229.167 B, 30.521 baris, diawali `[PAD] [UNK] [CLS] [SEP] [MASK] ##an d ##er m ##en s p ##ar ...` — **tokenizer IndoBERT**, bukan BERT-Inggris. (Bandingkan `build/_gate2/vocab.txt` di repo: 30.522 baris, diawali `[PAD] [unused0] …` — itu BERT-Inggris untuk gerbang 2.)

**Implikasi:** pertanyaan "apakah bobotnya ada?" selesai. Pertanyaan berikutnya berubah menjadi "apakah bobot itu benar-benar terlatih dan dapat direproduksi?" — dan itu hanya bisa dijawab dengan inferensi ulang, yang belum dilakukan di mana pun.

### 4.4 Riwayat training (E1)

Step-1 (`csv/step1_training_history.csv`, 900 B), 8 baris:

| Epoch | Loss | TP | FP | FN | Precision | Recall | Micro-F1 |
|---|---|---|---|---|---|---|---|
| 1 | 2,142225 | 16.084 | 993 | 689 | 94,19 | 95,89 | 95,03 |
| 4 | 0,290275 | 16.463 | 491 | 310 | 97,10 | 98,15 | 97,63 |
| 6 | 0,176273 | 16.445 | 450 | 328 | 97,34 | 98,04 | 97,69 |
| 8 | 0,099865 | 16.514 | 434 | 259 | 97,44 | 98,46 | **97,94** |

Step-2 (`csv/step2_training_history.csv`, 436 B), 3 baris:

| Epoch | Loss | TP | FP | FN | Precision | Recall | Micro-F1 | `category_micro_f1` | `sentiment_acc` |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0,551144 | 6.552 | 3.953 | 2.454 | 62,37 | 72,75 | 67,16 | **0,0** | **0,0** |
| 2 | 0,379151 | 6.542 | 4.111 | 2.464 | 61,41 | 72,64 | 66,55 | **0,0** | **0,0** |
| 3 | 0,305177 | 6.830 | 3.962 | 2.176 | 63,29 | 75,84 | 69,00 | **0,0** | **0,0** |

Perhatikan: `67,16` (bukan `67,86`) dan `69,00` — angka `67,86` sama sekali tidak muncul di sesi ini.

### 4.5 `master_metrics.json` yang selama ini dicari — ternyata milik REST16/BERT

`logs/master_metrics.json` (`1KtQHORqhCk9f0TPQ_XJ431_5-3JM90mg`, 10.905 B) berada di sesi **`rest16_27082026_070817`** (folder `1SeUEo0faB2Qf162S5nrkY0j-VQiTUT3H`), bukan Apps-ACOS.

| Tingkat | Nilai |
|---|---|
| Overall precision | 0,4306306 (43,06%) |
| Overall recall | 0,5340782 (53,41%) |
| Overall micro-F1 | 0,4768080 (**47,68%**) |
| Step-1 terbaik | 0,8122511 (81,23%) pada epoch 6 |
| Step-2 terbaik | 47,68% pada epoch 15 dari **30 baris** |
| Sumber kandidat | `step1` (pipeline penuh) |

Berkas pendampingnya: `master_07_metrik_quadruple_final.csv` (F1 47,68%), `master_08_metrik_subtask.csv` (15 subtask; QUAD **47,03%**), `master_09_agregasi_elemen.csv` (1 el 79,31; 2 el 66,41; 3 el 55,59; 4 el 47,03), `master_10_contoh_inferensi.csv` (9 baris contoh), `step2_run_result.json` (6.860 B, 30 epoch).

Checkpoint sesi ini: `vocab.txt` 231.508 B (30.522 baris, BERT-Inggris), model 440.407.851 B yang di `step2_best` menjadi 438.251.079 B — **bukan IndoBERT**. Jadi `81,23` dan `47,68` adalah **hasil BERT-base-uncased pada rest16**, bukan IndoBERT.

### 4.6 Audit embedding (E2, direproduksi E1)

`_embedding/embedding_audit.csv` (`1Eq532S8DY1qjK5fB-wy30TKldRTapEz9`, 162 B):

| Metrik | Nilai |
|---|---|
| `vocab_txt_bariss` | 30.521 |
| `config_vocab_size` | 50.000 |
| `hidden_size` | 768 |
| `emb_params_jt` | 38,4 |
| `unk_disisipkan` | 0 |
| `span_bergeser` | **25.992** |
| `baris_lebih_126` | 0 |

Saya menghitung ulang dari repo dengan membandingkan `data/Apps-ACOS/appsid_quad_<split>.tsv` terhadap `tokenized_data/appsid_<split>_quad_bert.tsv`:

| Split | Baris | Baris berubah teks | Quad | Span bergeser | `[UNK]` |
|---|---|---|---|---|---|
| train | 60.159 | 21.122 | 72.973 | 20.615 | 0 |
| dev | 8.027 | 2.887 | 9.587 | 2.742 | 0 |
| test | 7.891 | 2.813 | 9.514 | 2.635 | 0 |
| **total** | **76.077** | **26.822 (35,26%)** | **92.074** | **25.992 (14,12% dari 184.148 span)** | **0** |

Angka `25.992` di Drive **identik** dengan hitung ulang. Artinya metrik ini nyata, tetapi tidak pernah dilaporkan di 036/039 sebagai risiko.

---

## 5. Rekonsiliasi angka: repo vs Drive

| # | Klaim | Angka di repo | Artefak Drive (ID) | Angka di Drive | Status |
|---|---|---|---|---|---|
| K01 | Step-1 appsid 97,94% | 97,94 | `1LrhdlbB…` | 97,94 (ep8; TP 16.514/434/259) | **TERKONFIRMASI** |
| K02 | Step-1 15 epoch | 15/15 | `1LrhdlbB…` | 8/15; `early_stopped=false`; `stopped_at=null` | **TERBANTAH** |
| K03 | Step-2 67,86% | 67,86 | `11ocx1pn…` | 67,16 / 66,55 / 69,00 | **TIDAK COCOK** |
| K04 | Step-2 15 epoch | 15/15 | `1LyTrf-2…` | 3/15; best 69,00 ep3 | **TERBANTAH** |
| K05 | Dual-head 0 = bug logging | 0,00 | `11ocx1pn…`, `1LyTrf-2…` | 0,0 tersimpan di 3 epoch | **TIDAK TERBUKTI** |
| K06 | 15 subtask: opini 96,29 … QUAD 66,28 | 96,29 / 66,28 | notebook `V4_1_04` cell 10 (exec 52) | tabel lengkap + TP/FP/FN | **TERVERIFIKASI SEBAGIAN** |
| K07 | TP/FP/FN lengkap di `master_08` appsid | "ada" | `1TXLapXB…` | `master_08` = REST16; TP/FP/FN kosong | **TIDAK TERBUKTI** |
| K08 | rest16 81,27 / 48,24 | 81,27 / 48,24 | `1KtQHORq…` | 81,23 (ep6) / 47,68 (ep15) | **BERBEDA TIPIS** |
| K09 | Baseline BERT tanpa skor end-to-end | crash | `1KtQHORq…` | QUAD 47,68; 15 subtask 47,03 | **TERBANTAH** |
| K10 | Gate-1 199/199 | 199/199 | `1IOp-tXL…` | 199/199, mean identik | **TERKONFIRMASI** |
| K11 | Enam gerbang lulus | 5/5 / 3/3 | `18uB4X9u…` | 5 gerbang `ok` | **TERKONFIRMASI** |
| K12 | Checkpoint tidak ada | nol | `1GtREyFG…` dll. | 3 set, 475–500 MB | **TERBANTAH** |
| K13 | CV tanpa skor | 0 skor | `1J5t0O-u…` | 93 `run_result.json` ERROR | **TERKONFIRMASI** |
| K14 | `master_metrics` appsid ada | "ada" | `1KtQHORq…` | hanya ada untuk REST16 | **TIDAK TERBUKTI** |
| K15 | Vocab 30.521 vs 50.000 = +14M parameter | +14M | `1eBX8pzd…` | tokenizer IndoBERT; 50.000 = desain | **SALAH TAFSIR** |
| K16 | 0 span defect | 0 | `1Eq532S8…` | 25.992 span bergeser | **MENYESATKAN** |
| K17 | Kontaminasi rest16 (0,00; FP 165.728) | 0,00 | tidak ada di folder ini | sesi 12/09 tidak disertakan | **TIDAK DAPAT DIPERIKSA** |

---

## 6. Temuan kritis

### F01 — Folder ini bukan sumber sesi yang dikutip 036

**Bukti.** 036 §Data merujuk `appsid_08092026_150437xxx` dan `rest16_12092026_104518` (folder Drive `15cRYLPh18GBEj95OvM1S6ID9zZlCs8BL`). Folder yang dianalisis berisi `appsid_05092026_122741`, `experiments_26092026`, `experiments_27092026`, dan satu state pkl. Tidak ada satu pun sesi 08/09 atau 12/09.

**Arti.** Angka-angka 036 yang paling penting tidak dapat ditutup dari folder ini. Yang dapat ditutup hanya angka yang kebetulan identik (Step-1 97,94; Gate-1; gerbang data).

**Dampak.** Tinggi. Pembaca yang diberi folder ini akan mengira `67,86` dan `66,28` berasal dari sini, padahal tidak.

**Tindakan.** Satukan sesi yang dikutip ke satu folder `results`; cantumkan `session_id` pada setiap tabel metrik.

### F02 — `67,86%` bukan angka sesi ini; Step-2 sesi ini berhenti di 3/15

**Bukti.** `csv/step2_training_history.csv` hanya memuat epoch 1–3 dengan F1 `67,16 / 66,55 / 69,00`. `session_manifest.json`: `status = STEP2_TRAINING`, `step2_epoch_progress = 3/15`, `step2_best_micro_f1 = 68,99686837054249`, `step2_best_epoch = 3`. `step2_progress.json` dan `step2_resume.json` konsisten (`early_stopped=false`, `stopped_at_epoch=null`).

**Arti.** Angka `67,86` di 036 berasal dari sesi `appsid_08092026_150437` (jejaknya terlihat di notebook `V4_1_04_eval_inference.ipynb` cell 6: `master_06` 1 baris, TP 6.654/FP 3.951/FN 2.352, `category_micro_f1=0`, `sentiment_acc=0`). Sesi di folder ini adalah **run yang berbeda dan lebih pendek**. Bukti bahwa keduanya bukan run yang sama:

| | Sesi 0509 (folder ini) epoch 1 | Sesi 0809 (dikutip 036) epoch 1 |
|---|---|---|
| Loss | 0,551144 | 0,5544 |
| TP / FP / FN | 6.552 / 3.953 / 2.454 | 6.654 / 3.951 / 2.352 |
| Gold (TP+FN) | 9.006 | 9.006 |
| Prediksi (TP+FP) | 10.505 | 10.605 |
| Micro-F1 | 67,16 | 67,86 |
| Epoch tercatat | 3 | 1 |

Himpunan gold identik (9.006 pasangan uji), tetapi prediksi berbeda 100 pasangan dan loss berbeda — dua model/epoch yang berbeda, bukan dua cara menghitung run yang sama.

**Dampak.** Tinggi. `67,86` dan `69,00` sama-sama "interim", tetapi hanya `67,86` yang dikutip. Tidak ada alasan metodologis memilih run yang lebih buruk kecuali kebetulan run itu yang mengekspor `master_06`.

**Tindakan.** Kutip `69,00` (epoch 3, sesi 0509) **dan** `67,86` (epoch 1, sesi 0809) sebagai dua titik dari dua sesi; atau selesaikan sesi 0509 sampai 15 epoch lalu kutip satu angka.

### F03 — Metrik dua kepala Step-2 nol secara permanen

**Bukti.** `step2_training_history.csv` memuat kolom `category_micro_f1` dan `sentiment_acc` bernilai `0.0` untuk **ketiga** epoch. `step2_resume.json` juga menyimpan `"category_micro_f1": 0.0, "sentiment_acc": 0.0` per epoch. Sesi 0809 (notebook `V4_1_04` cell 6) menunjukkan pola yang sama pada `master_06`.

**Arti.** 036 §V menyebut ini "logging bug ... proven because the fused-39 path that depends on the same heads still scores 67.86%". Argumen itu **tidak valid sebagai bukti**: fused-39 dihitung dari kepala yang sama, sehingga F1 67,86 hanya membuktikan kepala menghasilkan *sesuatu*, bukan bahwa metrik per-kepala dihitung benar. Yang pasti: tidak ada artefak yang memisahkan `z_cat` dan `z_senti`; keduanya lenyap sebelum ditulis.

**Dampak.** Tinggi. Naskah tidak dapat mengklaim "kategori 92,41 / sentimen 84,97" sebagai pengukuran kepala; angka itu berasal dari dekomposisi 15 subtask (pencocokan fused), bukan dari kepala terpisah.

**Tindakan.** Dari `step2_epoch_3` (model + config tersedia), jalankan inferensi 500–1.000 pasangan, simpan `z_cat`, `z_senti`, `argmax`, lalu hitung micro-F1 kategori dan akurasi sentimen. Tanpa itu, klaim "dual-head dapat diaudit" harus dicabut.

### F04 — `master_08` yang ada adalah REST16; `master_08` Apps-ACOS tidak ada

**Bukti.** `master_08_metrik_subtask.csv` (`1TXLapXB…`, 666 B) berjudul **"Metrik per Sub-Task (REST16) - 15 kombinasi"**; QUAD = `47,03`; kolom TP/FP/FN **kosong**; catatan MD-nya: *"Diambil dari keluaran pair_eval sesi ini, bukan angka manual. TP/FP/FN kosong — sub-task ini ditangkap sebelum patch metrik aktif."* Di sesi Apps-ACOS, `md/` hanya memuat `master_00`–`master_05`; tidak ada `master_06`–`master_09`.

**Arti.** 036 Tabel VI memberi keterangan `(csv/master_08_metrik_subtask.csv)` untuk Apps-ACOS dan menulis *"Full TP/FP/FN in the CSV"*. Dua pernyataan itu tidak dapat dipenuhi oleh berkas yang ada: CSV itu domain lain, dan CSV itu justru mengosongkan TP/FP/FN.

**Dampak.** Tinggi. Ini persis jenis kesalahan yang paling sulit dideteksi pembaca: nama berkas sama, domain berbeda.

**Tindakan.** Ganti nama menjadi `master_08_metrik_subtask_<domain>_<session>.csv`; untuk klaim Apps-ACOS, ekspor ulang dari sesi 0809 dan unggah ke folder yang sama.

### F05 — `66,28` vs `67,86`: dua run, dua volume kandidat — bukan "definisi TP" atau dedup

**Bukti.** Notebook `V4_1_04_eval_inference.ipynb` cell 10 (execution 52) menampilkan agregasi:

| Jumlah elemen | Subtask | Micro-F1 rata-rata | TP total | FP total | FN total |
|---|---|---|---|---|---|
| 1 | 4 | 91,89 | 64.529 | 4.759 | 6.245 |
| 2 | 6 | 82,82 | 96.220 | 22.896 | 16.996 |
| 3 | 4 | 73,81 | 61.353 | 27.489 | 16.103 |
| 4 | 1 | **66,28** | **14.448** | **9.618** | **5.080** |

Jadi `66,28` dihitung atas `19.528` elemen gold dan `24.066` prediksi. Sebaliknya, notebook `V4_1_03_step2_train.ipynb` cell 19 (execution 41) mencatat `Quad num: 10605`, `tp=6654`, `fp=3951`, `fn=2352` — yaitu `9.006` gold dan `10.605` prediksi. Keduanya berlabel "prediksi step 1 (skor pipeline penuh)".

**Arti.** `66,28` dan `67,86` tidak mungkin berasal dari run yang sama dengan set evaluasi yang sama: jumlah gold berbeda 2,17×. Penjelasan 035 ("perbedaan definisi TP yang sedikit berbeda") dan 039 ("deduplikasi per teks, label berulang") **tidak didukung artefak**. Yang paling mungkin: evaluator 0809 dijalankan pada himpunan kandidat yang jauh lebih besar, sehingga precision turun (60,03 vs 62,74) dan recall naik (73,99 vs 73,88).

**Dampak.** Tinggi. Dua angka "QUAD" untuk entitas yang disebut "run yang sama" membuat pembaca tidak punya sumber kebenaran; 039 sudah menandai ini sebagai K6, tetapi penjelasannya perlu dikoreksi.

**Tindakan.** Laporkan setiap F1 bersama `(session_id, jumlah gold, jumlah prediksi, sumber kandidat)`. Jangan menyebut dua angka itu "run yang sama" tanpa bukti.

### F06 — Baseline BERT-rest16 punya hasil end-to-end: 47,68%

**Bukti.** Sesi `rest16_27082026_070817` (`1SeUEo0faB2Qf162S5nrkY0j-VQiTUT3H`): `session_manifest.json` status `FINAL_EVAL_COMPLETED`, `final_metrics.micro-F1 = 0,4768080`; `step2_run_result.json` 30 baris, terbaik `47,68` pada epoch 15; checkpoint `vocab.txt` 231.508 B (BERT-Inggris) dan model 440.407.851 B (420,0 MB, BERT-base + kepala); `master_07` = 47,68%; `master_08` = 47,03%; `master_09` = 79,31/66,41/55,59/47,03.

**Arti.** 036 §VII menulis *"Earlier baseline has no end-to-end score (crash) and was never retrained post-fix."* Itu tidak akurat: ada sesi BERT-rest16 dengan evaluasi selesai dan 30 baris riwayat. Yang benar: baseline BERT **pernah** gagal (KeyError `a--1,-1`) pada satu run, tetapi run 27/08 menghasilkan skor lengkap.

**Dampak.** Tinggi untuk posisi naskah: baseline yang tadinya "tidak ada" sebenarnya ada di kisaran 47,68% — hanya 0,56 poin di bawah `48,24` yang dikutip dari notebook lain. Ini justru memperkuat argumen bahwa Step-2 adalah bottleneck, bukan melemahkannya.

**Tindakan.** Sitir `47,68` sebagai baseline BERT-rest16 (pipeline penuh), jelaskan perbedaan dengan `48,24` (gold pair vs pipeline), dan hapus klaim "tanpa skor end-to-end".

### F07 — Matriks CV: 54 run, 94 folder, 93 ERROR, 0 skor

**Bukti.** `experiments_27092026` memuat 34 folder `cv5fold` + 60 folder `cv10fold` = 94 folder sesi. `run_result.json` berjumlah 93 dengan ukuran **569–591 byte** — terlalu kecil untuk memuat metrik; empat sampel yang dibaca semuanya `"status": "ERROR"`:

| Folder | `run_idx` | Fold | Epoch | Error | Durasi |
|---|---|---|---|---|---|
| `cv5fold_fold4_ep75_…1337` | 18 | 4/5 | 75 | `'list' object has no attribute 'items'` | 7,6 s |
| `cv5fold_fold1_ep100_…1359` | 20 | 1/5 | 100 | `'list' object has no attribute 'items'` | 7,5 s |
| `cv5fold_fold1_ep75_…1421` | 15 | 1/5 | 75 | `'BertForQuadABSA' object has no attribute 'save_pretrained'` | 89,9 s |
| `cv10fold_fold9_ep100_…1403` | 53 | 9/10 | 100 | `'list' object has no attribute 'items'` | 8,3 s |

`checkpoints/step1_best` di sesi yang diperiksa **kosong** (0 berkas).

**Arti.** "54 run" adalah **rencana**, bukan hasil: `run_idx` berjalan 0–53, tetapi tidak satu pun menghasilkan metrik. Kegagalan terjadi 7–90 detik setelah mulai — jauh sebelum satu epoch selesai — sehingga tidak ada model yang tersimpan.

**Dampak.** Tinggi. Klaim "universal/8 platform/54 run" yang sudah ditolak 039 kini punya penjelasan formal: runner gagal pada serialisasi konfigurasi (`list.items`) dan penyimpanan model (`save_pretrained`).

**Tindakan.** Perbaiki dua titik itu, jalankan satu fold sebagai uji asap, dan laporkan `54 percobaan / 0 hasil` sampai ada metrik.

### F08 — `25.992` span bergeser: bukan cacat, tetapi bukan "nol"

**Bukti.** `embedding_audit.csv` mencatat `span_bergeser = 25.992`; reproduksi repo menghasilkan angka identik. `tokenize_data.py:190` menambahkan `info["n_shift"]` untuk setiap span yang offset numeriknya berubah setelah retokenisasi (`build_split`), dan `:281` mencetaknya. `26.822` dari `76.077` baris (35,26%) memiliki teks yang berbeda antara `data/Apps-ACOS/*.tsv` dan `tokenized_data/*.tsv`.

**Arti.** `span_invalid = 0` dan `quad_hilang = 0` mengukur **kegagalan**, bukan **pergeseran**. Yang terjadi adalah normalisasi: teks direkonstruksi dari subword (`login ##nya`), sehingga offset bergeser dan teks berubah. Selama training dan evaluasi memakai berkas hasil tokenisasi yang sama, hasilnya konsisten; yang menjadi masalah adalah bila ada evaluator yang mencocokkan prediksi terhadap offset di `data/` mentah.

**Dampak.** Sedang. Tidak membatalkan hasil, tetapi dua laporan (036, 039) menyatakan "0 span defect" tanpa menyebut 25.992 pergeseran.

**Tindakan.** Simpan peta offset lama→baru per baris; sebut angka 25.992/14,12% di bagian keterbatasan.

### F09 — "Vocab 30.521 vs 50.000 = +14 juta parameter" adalah salah tafsir

**Bukti.** `vocab.txt` di `step1_best`/`step2_best` 30.521 baris dan diawali `[PAD] [UNK] [CLS] [SEP] [MASK]` diikuti subkata Indonesia. `config.json` `vocab_size = 50000`; bobot embedding `[50000, 768]`. Gate-1 memverifikasi bentuk itu dan mean-nya identik dengan checkpoint.

**Arti.** Ini adalah desain IndoBERT: tabel embedding 50.000 baris, tokenizer memakai 30.521 token pertama. Baris 30.521–49.999 tidak pernah diindeks, jadi tidak ada "14 juta parameter tambahan" yang dibayar per forward pass. Klaim 030/035/036 bahwa ada "dampak ~15M parameter" karena ketidakcocokan vocab **menyesatkan** — yang benar: model 124–125 juta parameter, sebagian embedding tidak terpakai.

**Dampak.** Sedang. Bukan kesalahan eksperimen, tetapi kesalahan narasi yang masuk ke artikel.

**Tindakan.** Ganti kalimat di 030 §4/035/036 dengan: *"IndoBERT menyimpan embedding 50.000×768; tokenizer hanya memakai 30.521 token. Tidak ada ketidakcocokan runtime."*

### F10 — Semua `run_result` bermode `cache_hit`; rest16 mencatat 30 epoch untuk target 15

**Bukti.** `step1_run_result.json` appsid: `"mode": "cache_hit"`, 8 epoch dari target 15, `early_stopped=false`. `step2_run_result.json` rest16: `"mode": "cache_hit"`, `total_epochs_target: 15`, `epochs_recorded: 30`, `best_epoch: 15`. `session_manifest.json` appsid: `status STEP2_TRAINING`, bukan final.

**Arti.** Riwayat yang tersimpan bisa berasal dari state lama, bukan dari run yang sedang dijalankan. Pada rest16, 30 baris untuk target 15 menunjukkan dua siklus ditempel (epoch 16–30 adalah pass kedua, bukan epoch baru). Status `FINAL_EVAL_COMPLETED` juga tidak menjamin run bersih — 036 sudah membuktikannya untuk sesi 12/09.

**Dampak.** Sedang–tinggi. Semua angka "epoch terbaik" bergantung pada pemahaman ini.

**Tindakan.** Saat cache hit, catat hash `step*_training_history.csv` + `session_id` sumber; tolak cache bila domain/backbone/konfigurasi berbeda. Untuk rest16, potong history pada 15 baris pertama dan laporkan.

### F11 — `experiments_26092026` kosong total

**Bukti.** `REPORT_INDEX.md` menyatakan `csv 0, plots 0, md 0, logs 0`, state `pipeline_state.pkl` 483 B, dan `_gates/gates.csv` hanya memuat tiga baris. Folder `checkpoints/`, `csv/`, `logs/`, `md/`, `plots/` semuanya tanpa berkas.

**Arti.** Ini artefak "kerangka sesi" yang tidak pernah diisi. Kehadirannya menambah kesan volume eksperimen tanpa isi.

**Dampak.** Rendah, tetapi relevan untuk audit aset.

**Tindakan.** Tandai `ARSIP_KOSONG` atau hapus dari folder hasil.

---

## 7. Peta bukti yang diperbarui (menggantikan baris terkait di 039)

| # | Artefak/klaim | 039 | 040 | Dasar |
|---|---|---|---|---|
| A21 | Metrik 15 subtask appsid | E3 | **E2** | Output notebook `V4_1_04` cell 10 (exec 52) dengan TP/FP/FN; CSV tidak ada |
| A22 | Checkpoint/bobot | 🔴 tidak ada | **E1** | 3 set checkpoint di Drive |
| A23 | `master_metrics.json` appsid | tidak ada | **tetap tidak ada** | Hanya versi REST16 yang ditemukan |
| A24 | Skor CV | 🔴 0 | **🔴 0 (terkonfirmasi)** | 93 `run_result` ERROR, checkpoint kosong |
| A25 | Baseline BERT-rest16 | "crash, tanpa skor" | **47,68% (E1)** | `master_metrics`, `master_07/08/09`, checkpoint BERT |
| K13 | 15 subtask: sentimen 84,97 | tidak dapat diverifikasi | **terverifikasi di notebook, CSV hilang** | Cell 10 output |
| K18 | Gate-1 199/199 | E3 | **E1** | `gate1_weights.json` |
| K20 | Provenance | merah | **tetap merah, lebih spesifik** | Sesi yang dikutip ≠ folder yang diberikan |

---

## 8. Kalimat di laporan lama yang perlu diubah

| Lokasi | Kutipan | Masalah | Usulan |
|---|---|---|---|
| 036 §V | *"Step-2 ... reaches 67.86% quadruple F1 at epoch 1/15"* | Benar untuk sesi 0809, tetapi bukan sesi 0509 yang ada di folder ini | Tambah `(session appsid_08092026_150437)`; sebut juga `69,00%` sesi 0509 |
| 036 §V | *"... in every file is a logging bug ... proven because the fused-39 path ... still scores 67.86%"* | Nol tersimpan di CSV/resume; argumen fused bukan bukti | Ganti dengan: *"tidak ada artefak per-kepala; perlu dump logits"* |
| 036 Tabel VI | *"Appsid subtasks, epoch-1 Step-2 (csv/master_08_metrik_subtask.csv)"* + *"Full TP/FP/FN in the CSV"* | CSV Apps-ACOS tidak ada; CSV yang ada = REST16 dan TP/FP/FN kosong | Tunjuk ke output notebook; unggah CSV Apps-ACOS |
| 035 §IV | *"perbedaan bersumber dari cakupan evaluasi yang berbeda"* | Tidak menjelaskan volume kandidat 24.066 vs 10.605 | Sebut jumlah gold/prediksi per angka |
| 036 §VII | *"Earlier baseline has no end-to-end score (crash)"* | Ada sesi BERT-rest16 dengan 47,68 | Sitir 47,68 sebagai baseline |
| 030 §4 / 035 / 036 | *"Vocab 30.522 vs 50.000, dampak ~15M parameter"* | Salah tafsir desain embedding | Ganti dengan penjelasan embedding 50k/30.521 |
| 039 K6 | *"Kontrak evaluasi: deduplikasi per teks, label berulang"* | Tidak didukung; penyebabnya run/volume kandidat berbeda | Perbaiki ke F05 laporan ini |
| 039 §Bukti | *"checkpoint/artefak run 🔴"* | Checkpoint ada di Drive | Ubah menjadi "tidak ada di repo, ada di Drive" |

---

## 9. Rekomendasi

### P0 — sebelum angka apa pun dikutip ulang

1. **Ekspor `master_08` Apps-ACOS dari sesi 0809 dan unggah ke folder yang sama.** Tanpa CSV, Tabel VI 036 tetap E2 dan keterangan "TP/FP/FN lengkap di CSV" harus dicabut.
2. **Hitung ulang metrik dua kepala dari `step2_epoch_3`.** Dump `z_cat`/`z_senti` untuk ≥500 pasangan; simpan CSV; ganti klaim "logging bug" dengan hasil pengukuran.
3. **Perbaiki runner CV** (`'list' object has no attribute 'items'` dan `save_pretrained`), jalankan **satu** fold sebagai uji asap, dan publikasikan `0/54` sampai ada angka.
4. **Satukan sesi yang dikutip** (0509, 0809, 1209, 2708) dalam satu folder `results` dengan `session_id` di setiap nama berkas.

### P1 — memperbaiki naskah

5. Ganti narasi "67,86" menjadi dua angka bertanggal sesi; tambahkan kolom `n_gold`, `n_pred`, `sumber_kandidat` di setiap tabel F1.
6. Sitir baseline BERT-rest16 `47,68%` dan dekomposisi `47,03%`, serta jelaskan hubungannya dengan `48,24%`.
7. Perbaiki klaim vocab (F09) dan tambahkan angka 25.992 span bergeser di bagian keterbatasan.
8. Potong `step2_run_result.json` rest16 pada 15 epoch pertama sebelum menghitung "best epoch"; tandai 16–30 sebagai pass kedua.

### P2 — kerapian aset

9. Beri nama berdomain pada semua `master_0x` (`<domain>_<session>`); hapus/tandai `experiments_26092026` sebagai kosong.
10. Simpan `sha256` bobot checkpoint pada manifest agar integritas 475 MB dapat diverifikasi tanpa mengunduh ulang.
11. Tambahkan `span_bergeser` dan `baris_teks_berubah` ke `master_00b_gerbang_data_id.csv` supaya gerbang data tidak lagi terlihat "100% bersih".

---

## 10. Yang tidak dapat disimpulkan dari folder ini

1. **Kualitas model final.** Tidak ada Step-2 yang selesai 15 epoch pada folder ini; `69,00%` adalah epoch 3.
2. **Kontribusi dua kepala.** Metriknya nol dan tidak ada logits tersimpan.
3. **Generalisasi.** Tidak ada CV, tidak ada multi-seed, tidak ada uji signifikansi — 54 run semuanya gagal.
4. **Kualitas label.** Tidak ada gold manusia; semua angka adalah replikasi label lemah.
5. **Validitas lintas dataset.** Sesi rest16 IndoBERT yang dikutip 036 (0,00; FP 165.728) tidak ada di folder ini; yang ada adalah rest16 **BERT** 47,68.
6. **Reproduksibilitas penuh.** Bobot ada, tetapi tanpa `torch` di lingkungan ini dan tanpa skrip inferensi yang dipin, klaim "dapat direproduksi" belum diuji.

---

## Lampiran A — Inventaris berkas Drive

Lihat `reports/040_data/inventaris_drive.csv` (40 baris): path, `id_folder`, `id_file`, jenis, ukuran, waktu modifikasi, kategori, catatan.

## Lampiran B — Rekonsiliasi klaim

Lihat `reports/040_data/rekonsiliasi_klaim_drive.csv` (17 baris K01–K17): klaim, angka repo, sumber repo, artefak Drive, angka Drive, status, catatan.

## Lampiran C — Sampel run CV 27/09/2026

Lihat `reports/040_data/run_cv_27092026.csv` (4 baris): folder, `run_idx`, `fold_idx`, `epochs`, status, error, durasi.

## Lampiran D — Temuan kritis

Lihat `reports/040_data/temuan_kritis.csv` (12 baris F01–F12): temuan, bukti, tingkat, dampak, tindakan.

## Lampiran E — Cara memverifikasi ulang

1. **Gate-1:** buka `logs/gate1_weights.json`; pastikan `n_key_bert_model = n_key_bert_checkpoint = 199`, `mean_checkpoint = mean_model` pada tiga probe, `ok = true`.
2. **Step-1:** bandingkan `csv/step1_training_history.csv` dengan `logs/step1_run_result.json`; baris ke-8 harus `97,9449` dan `best_epoch = 8`, `epochs_recorded = 8`.
3. **Step-2:** `csv/step2_training_history.csv` harus 3 baris; kolom `category_micro_f1`/`sentiment_acc` harus `0.0`; `session_manifest.json` harus `3/15`.
4. **15 subtask:** buka `V4_1_04_eval_inference.ipynb` cell 10; cari tabel agregasi `66.28` dengan `TP_Total 14448`, `FP_Total 9618`, `FN_Total 5080`.
5. **CV:** buka salah satu `run_result.json` di `experiments_27092026`; `status` harus `ERROR`; `checkpoints/step1_best` harus kosong.
6. **Span bergeser:** jalankan perbandingan baris-per-baris `data/Apps-ACOS/appsid_quad_<split>.tsv` vs `tokenized_data/appsid_<split>_quad_bert.tsv`; jumlah offset berubah harus `20.615 + 2.742 + 2.635 = 25.992`.
