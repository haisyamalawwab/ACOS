# 039 — Survei, Analisis Mendalam, dan Peta Hasil Repo ACOS

> **Tanggal audit:** 2 November 2026
> **Objek:** checkout `/home/user/ACOS` (branch `arena/82da2da3-acos`, commit `8beb6cc`)
> **Sifat:** audit independen berbasis **rekalkulasi dan uji ulang**, bukan ringkasan dokumen.
> **Pelengkap:** `reports/038_...md` (pemetaan status) — laporan ini memverifikasi ulang klaimnya, mengoreksi yang perlu, dan menambah temuan kuantitatif yang belum ada.
> **Peta visual:** `reports/039_peta_hasil.html`
> **Data pendukung:** `reports/039_data/` (`inventaris_hasil.csv`, `matriks_klaim.csv`, `bukti_notebook.csv`, `audit_039_results.json`), skrip reproduksi `scripts/audit_039_repo.py`.

---

## 0. Ringkasan eksekutif

**Apa yang benar-benar sudah ada di folder ini (bukti terkuat):**

1. **Dataset Apps-ACOS lengkap dan dapat diverifikasi ulang.** 43.673 ulasan → 96.417 tuple label lemah → 76.077 baris ACOS (92.074 tuple) dengan split review-disjoint 60.159/8.027/7.891. Angka-angka ini **saya hitung ulang dari file, bukan mengutip laporan**.
2. **Konversi data reproducible.** Menjalankan `python -m acos_id.build_acos data` hari ini menghasilkan **file TSV yang byte-identik** dengan yang ada di repo (git hanya melaporkan perubahan pada JSON laporan karena path Windows).
3. **Tokenisasi bersih menurut data yang dikirim.** 0 `[UNK]`, 0 span invalid, dan **0 dari 92.074 quadruple hilang** dari file pair Step-2; file pair memuat 83.420 baris dengan multi-label 0,39%.
4. **Tiga belas gate `absa5` lulus lokal (13/13)** dan **enam gate `acos_en` lulus (3/3 rest16, 3/3 laptop)**. Ini kematangan *software/verifikasi*, bukan hasil model.
5. **Ada hasil training IndoBERT yang tersimpan sebagai output notebook, bukan sekadar klaim:** Step-1 Apps-ACOS 8 epoch dengan riwayat lengkap (97,94% pada epoch 8; TP 16.514 / FP 434 / FN 259), dan tiga run Step-2 (67,86% ep-1; 67,69% ep-3; 69,00% ep-3).
6. **Ada baseline Inggris yang “hilang dari peta”:** Step-1 rest16 **81,27%** (15 epoch penuh, BERT) di `notebooks/02`, dan Step-2 rest16 **48,24%** (15 epoch penuh, pair gold) di `notebooks/04`. Laporan 036 menyatakan hasil Step-2 rest16 “tidak tersedia”; klaim itu mengabaikan run legacy yang sah (48,24%), meski jalurnya bukan pipeline V4 yang sama.

**Apa yang belum ada atau tidak boleh diklaim:**

7. **Tidak ada checkpoint, history CSV, `master_metrics.json`, atau prediksi test** di checkout. Semua angka model hanya “terbukti oleh output notebook”, bukan reproducible penuh.
8. **Tidak ada satu pun hasil model yang konvergen.** Step-2 Apps-ACOS berhenti di epoch 1–3 dari rencana 15/50; tidak ada early stopping, tidak ada kurva penuh, dan angka yang dikutip (67,86%) bukan angka terbaik yang terlihat (69,00%).
9. **Tidak ada skor cross-validation**, walaupun manifest 5-fold/10-fold valid dan lengkap (36.821 review, 0 kebocoran antar-split).
10. **Emotion hampir merupakan fungsi dari sentimen.** `H(emotion | sentiment) = 0,498 bit` vs `H(emotion) = 1,869`; baseline “satu emosi mayoritas per sentimen” sudah mencapai **91,33% akurasi** tanpa melihat teks. Ini harus menjadi baseline wajib sebelum ACOSE dilatih.
11. **Kontaminasi cache lintas domain bukan insiden tunggal.** Run rest16 12-09 menyalin angka appsid 97,94/67,86; run rest16 24-09 **kembali** melaporkan 97,19/67,69 — identik dengan run appsid MI300X. Sistem cache/resume belum pernah benar.
12. **Klaim V5.2 “universal 8 platform” dan “54 run” tidak punya bukti eksekusi.** Notebook V5.2 berhenti pada `ModuleNotFoundError: bert_utils`; notebook V5.2.1/V5.3 berhenti pada assertion “Belum ada run OK”; notebook MI300X V5 bahkan `IndentationError`.

### Satu kalimat putusan

> Repo ini **sudah menghasilkan aset data + protokol verifikasi + hasil interim yang nyata (dan satu negative result yang berharga)**, tetapi **belum menghasilkan satu eksperimen end-to-end yang lengkap, bersih, dan dapat direproduksi dari clone** — dan beberapa klaim di dokumen lebih maju daripada buktinya.

---

## 1. Ruang lingkup, metode, dan tingkat bukti

### 1.1 Yang dijalankan ulang pada audit ini

| Uji | Perintah | Hasil |
|---|---|---|
| Gate ACOSE | `python -m absa5.selftest --repo .` | **13/13 lulus** (termasuk 18.862 span, 2.417 baris pair) |
| Gate Inggris rest16 | `python -m acos_en.selftest --domain rest16` | **3/3 lulus** (1.640 span) |
| Gate Inggris laptop | `python -m acos_en.selftest --domain laptop` | **3/3 lulus** (1.380 span) |
| Gate Indonesia | `python -m acos_id.selftest` | **3/5 lulus**; `tokenized` & `gate2_english` gagal karena vocab backbone tidak ada dan unduhan diblokir (exit 1) |
| Reproduksi konversi | `python -m acos_id.build_acos data` | **TSV byte-identik** dengan file repo |
| Rekalkulasi data | `python scripts/audit_039_repo.py` | Semua statistik di §5 dihasilkan ulang dari file |
| Verifikasi CV | pembacaan 5 + 10 manifest | 0 overlap, cakupan 36.821 review |
| Penambangan output | 45 notebook, 1.748 sel | 16 notebook tanpa output, 13 output error |

### 1.2 Tingkat bukti yang dipakai

| Kode | Arti | Contoh di repo |
|---|---|---|
| **E1** | Dapat dijalankan ulang sekarang dan hasilnya dibandingkan | gate selftest, build TSV, statistik data, manifest CV |
| **E2** | Output eksekusi tersimpan (bukan artefak run) | riwayat 8 epoch Step-1, 3 run Step-2, run BERT rest16 |
| **E3** | Angka hanya ada di dokumen; artefaknya tidak ada | 15-subtask, Gate-1 199/199, metrik Drive |
| **E4** | Rencana, klaim, atau scaffold tanpa eksekusi yang cocok | V5.2 universal, 54 run, model ACOSE, gold manusia, CV model |

**Aturan tafsir:** E2 tidak sama dengan reproducible. Output notebook bisa berasal dari kode/config yang berbeda, dijalankan sebagian, atau di-*edit* setelah eksekusi — dan repo ini memuat contoh nyata ketiganya (§6-K9).

---

## 2. Inventaris fisik repo

| Ukuran | Nilai |
|---|---:|
| File terlacak git / di disk | **662 / 685** |
| Ukuran checkout | **±427 MB** |
| Commit git | **1** (“Merge pull request #11”, 2 Nov 2026) |
| Notebook / sel | **45 / 1.748** |
| Notebook tanpa output / dengan output error | **16 / 13** |
| File Python / baris | **143 / ±42.700** |
| Dokumen Markdown | **181** |
| File TSV / CSV / JSONL | **113 / 36 / 6** |
| Duplikasi byte-identik | **28 grup, ±22,9 MB** (mis. `colab_utils.py` 3 salinan) |

**Implikasi:** ini bukan *source package*, melainkan **arsip kerja + dataset + dokumentasi**. Satu commit berarti **tidak ada sejarah perubahan** yang bisa dipakai untuk melacak kapan/kenapa angka berubah — provenance harus dibangun ulang secara manual.

---

## 3. Peta subsistem — satu layar

| # | Bagian | Isi | Sudah ada hasil? | Tingkat | Putusan |
|---|---|---|---|---|---|
| 1 | `data/` (Restaurant-ACOS, Laptop-ACOS, Demo) | Data upstream + tokenized upstream | **Ya** — 2.284 kalimat/3.661 tuple rest16; 4.076/5.773 laptop | E1 | Siap dipakai sebagai kontrol |
| 2 | `ACOS-IndoBERT/data/Apps-ACOS/` | Raw, lexicon, label lemah, split, CV | **Ya** — 43.673 ulasan; 96.417 tuple; 92.074 tuple terpakai | E1 | Aset terkuat repo |
| 3 | `ACOS-IndoBERT/acos_id/` | Build, tokenize, gate, checkpoint, CV, runner | **Ya (parsial)** — 3/5 gate lokal; build reproducible | E1/E4 | Modul jalan; gate tokenizer tergantung vocab |
| 4 | `ACOS-IndoBERT/notebooks/` | V4/V5, run T4 & MI300X | **Ya (interim)** — 3 run Step-2, 1 run Step-1 | E2 | Bukti utama, tetapi terfragmentasi |
| 5 | `notebooks/` (root, legacy) | Pipeline awal rest16 | **Ya** — Step-1 81,27%; Step-2 48,24% | E2 | Baseline Inggris nyata, tetapi tidak dipetakan |
| 6 | `Extract-Classify-ACOS/` | Kode upstream Cai et al. | Kode + data tokenized; **tidak ada skor** | — | Fondasi, bukan hasil |
| 7 | `ACOS-BERT/` | Scaffold BERT EN | Gate 6/6 lulus; **training tidak** | E1/E4 | Scaffold, bukan model |
| 8 | `absa5/` | Quad → quint (ACOSE) | **13/13 gate**; **tanpa model** | E1/E4 | Software matang, hasil ML kosong |
| 9 | `reports/`, `docs/` | 181 md: analisis, devlog, draft artikel, panduan | Dokumen ada; status bercampur | E1–E4 | Perlu satu sumber status kanonik |
| 10 | `build/`, `dist/`, `screenshot/`, `img/` | EDA, gate, PDF panduan, bukti GPU | **Ya** — CSV EDA, PDF, 31 screenshot | E1/E2 | Bukti pendukung, bukan pengganti artefak run |

---

## 4. Katalog hasil yang sudah ada (dipetakan per tingkat bukti)

### 4.1 E1 — Dapat dijalankan ulang sekarang

| Hasil | Angka terverifikasi | Bukti |
|---|---|---|
| Dataset bersih | 43.673 ulasan; 13 aplikasi; 37.825 Google Play + 5.848 App Store; 62,0% berasal dari 2026 | `processed/reviews_clean.csv` |
| Label lemah | 96.417 tuple; 40.537 ulasan; 69.724 klausa unik; median 2 tuple/ulasan; maksimum 23 | `processed/quintuples_weak.csv` |
| Data ACOS | 76.077 baris; 92.074 tuple; 66.198 teks klausa unik; 20,0% baris ≤3 token | `appsid_quad_*.tsv` |
| Split utama | 60.159/8.027/7.891 baris; 28.839/3.991/3.991 ulasan; **0 overlap** | `processed/stage2_*.jsonl` |
| CV 5-fold | 5 fold; test 7.365/7.364×4; total 36.821; **0 overlap** | `cv_5fold/fold_*/id_to_split.json` |
| CV 10-fold | 10 fold; 3.683/3.682×9; total 36.821; **0 overlap** | `cv_10fold/` |
| Tokenisasi | 0 `[UNK]`; 0 span invalid; 92.074/92.074 quad hadir di pair file | `tokenized_data/` |
| Pair Step-2 | 83.420 baris (65.423/8.991/9.006); multi-label 0,39% train, 0,18% dev/test | `tokenized_data/*_pair.tsv` |
| Gate software | `absa5` 13/13; `acos_en` 3/3 per domain; `acos_id` 3/5 | dijalankan 2 Nov 2026 |
| Reproduksi build | TSV hasil build ulang **identik byte** | `build_acos` hari ini |

### 4.2 E2 — Output eksekusi tersimpan (hasil model)

| Run | Data | Epoch tercatat | Skor terbaik | Bukti |
|---|---|---:|---|---|
| Step-1 IndoBERT (T4) | Apps-ACOS | **8** dari 15 | **97,94%** (ep8); TP 16.514 / FP 434 / FN 259 | `00_..._V4_INDOBERT.ipynb` sel 46 |
| Step-2 IndoBERT run A | Apps-ACOS | **1** dari 15 | **67,86%** (ep1); TP 6.654 / FP 3.951 / FN 2.352 | `V4_1_03_step2_train.ipynb` |
| Step-2 IndoBERT run B | Apps-ACOS | **3** | 67,16 → 66,55 → **69,00%** (ep3) | `00_..._V4_INDOBERT.ipynb` sel 67 |
| Step-2 IndoBERT run C | Apps-ACOS (MI300X) | **3** | 67,69% (ep3); Step-1 97,19% (ep3) | `..._V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb` |
| Step-1 BERT (EN) | rest16 | **15** penuh | **81,27%** (ep8); P 78,16 / R 84,64 | `notebooks/02_ACOS_Step1...ipynb` |
| Step-2 BERT (EN, pair gold) | rest16 | **15** penuh | **48,24%** (ep12); P 43,39 / R 54,30 | `notebooks/04_ACOS_Step2...ipynb` |

**Catatan penting:** tiga run Step-2 Apps-ACOS adalah **tiga run berbeda**, bukan tiga epoch dari satu run. Menggabungkannya menjadi satu kurva adalah kesalahan provenance.

### 4.3 E2 (negatif) — Hasil yang valid justru sebagai *kegagalan*

| Sesi | Gejala | Angka | Tafsir |
|---|---|---|---|
| rest16 12-09 | Riwayat identik dengan appsid; evaluasi label space salah | 97,94/67,86 (salinan), final TP 0 / FP 165.728 / F1 0 | Kegagalan cache + evaluasi, **bukan** performa model |
| rest16 24-09 | **Kontaminasi kedua** | 97,19/67,69 — identik dengan appsid MI300X | Bug sistemik; belum pernah diperbaiki sampai akar |

### 4.4 E3 — Hanya terdokumentasi (artefak tidak ada di repo)

- **15-subtask Apps-ACOS**: opinion 96,29; aspect 93,88; category 92,41; sentiment 84,97; QUAD 66,28. CSV `master_08` tidak ada.
- **Gate-1 199/199** bobot IndoBERT termuat: tidak ada checkpoint/backbone lokal; tidak bisa diuji.
- **Artefak Drive** (`results/appsid_08092026_150437xxx/`, `results/rest16_12092026_104518/`): checkpoint, CSV, `pipeline_state.pkl`, `master_metrics.json` — semuanya eksternal.
- **Klaim MI300X**: 191,69 GB VRAM, ROCm 7.14 — didukung 31 screenshot, bukan artefak run.

### 4.5 E4 — Rencana/klaim tanpa bukti eksekusi

| Klaim | Kenyataan di repo |
|---|---|
| V5.2 universal, 8 platform, “fix bert_utils” | Notebook berhenti `ModuleNotFoundError: bert_utils`; `DRY_RUN=True` |
| 54 run (3 epoch × 3 rasio × 3 CV + …) | V5.2.1/V5.3: assertion “Belum ada run OK”; MI300X V5: `IndentationError` |
| Model ACOSE/quintuple | Hanya 13 gate software; tanpa checkpoint, logit, atau evaluasi emosi |
| Cross-validation model | Hanya split; tanpa skor per fold |
| Model laptop | Hanya data + gate; nol output metrik laptop |
| Gold manusia + IAA | Panduan anotasi (PDF/DOCX) ada; pilot/κ/gold set tidak ada |
| ACOS-BERT terlatih | Notebook berhenti `ModuleNotFoundError: torchcrf` |

---

## 5. Rekalkulasi angka kunci (klaim vs hasil hitung ulang)

| # | Klaim | Sumber | Hasil hitung ulang | Putusan |
|---|---|---|---|---|
| 1 | 43.673 ulasan | 036/032 | **43.673** | ✅ |
| 2 | 76.077 klausa | 036/032 | 76.077 **baris**; **66.198 teks unik** (13% baris duplikat) | ⚠️ istilah |
| 3 | 92.074 tuple | 036/032 | **92.074** | ✅ |
| 4 | Split 60.159/8.027/7.891 | 036 | **cocok** | ✅ |
| 5 | 28.839/3.991/3.991 review disjoint | 036 | **cocok, 0 irisan** | ✅ |
| 6 | 0 UNK / 0 span invalid / 0 tuple hilang | 036 | **cocok** (dicek langsung di file) | ✅ |
| 7 | Multi-label 0,4% (255/65.423) | 036 | **255 (0,39%)** | ✅ |
| 8 | 14,7% baris test berulang; 9,0% teks unik | 036 | **14,66% / 8,98%** | ✅ |
| 9 | Step-1 97,94% (ep8) | 036/030 | **cocok** dengan riwayat 8 epoch | ✅ E2 |
| 10 | Step-2 67,86% ep-1 “lower bound” | 036 | **cocok untuk run A**, yang berhenti di ep-1; run B mencapai **69,00%** (ep3) | ⚠️ bukan hasil terbaik |
| 11 | Step-2 rest16 tidak tersedia | 036 | **Ada run legacy**: 48,24% (15 epoch, pair gold, BERT) di `notebooks/04`; sesi V4 IndoBERT tetap tidak sah | ⚠️ menyesatkan |
| 12 | BERT rest16 Step-1 81,23% (ep6) | 030/033/035 | Run tersimpan: **81,14% ep6**, **81,27% ep8** | ❌ tidak cocok |
| 13 | category/sentiment head 0,00% = bug logging | 036 | **Pasti artefak**, karena exact-match quad 67,86% mengimplikasikan akurasi sentimen ≥ 67,86% | ✅ inferensi, mekanisme belum dibuktikan |
| 14 | Gate-1 199/199 | 036 | Tidak ada artefak | ⬜ tidak dapat diverifikasi |
| 15 | 15-subtask (sentimen 84,97%) | 036 | Tabel ada; CSV tidak | ⬜ tidak dapat diverifikasi |
| 16 | V5.2 universal | README/DEV_REPORT | Gagal import; dry-run | ❌ |
| 17 | CV tersedia | 036/038 | Split valid; **skor model tidak ada** | ⚠️ split ≠ hasil |

### 5.1 Rantai penyusutan data (funnel) yang tidak didokumentasikan

| Tahap | Jumlah | Selisih | Status |
|---|---:|---:|---|
| Ulasan bersih | 43.673 | — | ✅ |
| Ulasan dengan ≥1 tuple | 40.537 | −3.136 (7,2%) | tidak ada tuple |
| Ulasan masuk split | 36.821 | −3.766 (9,3%) | **tidak dijelaskan** |
| Ulasan berlabel **dan** masuk split | 36.771 | −50 arah sebaliknya | 50 review di split tanpa label |

- **Tuple:** 96.417 → 92.074 (**−4.343, 4,5%**) karena review tanpa split.
- **Klausa:** 69.724 → 66.198 teks unik (−5,1%); 4.183 klausa tercatat dibuang karena review-nya tidak masuk split.
- **Sebaran 3.766 review yang hilang merata di 10 desil file** (259–454 per desil), jadi **bukan** efek pemotongan di akhir file, melainkan perbedaan snapshot label vs snapshot split (didukung 50 review “hantu” di split).
- **Konsekuensi:** seleksi ini **tidak dapat direproduksi**, karena skrip pembuat `stage1/stage2_*.jsonl` tidak ada di repo (hanya pembacanya).

### 5.2 Dua jalur data Step-1 dan Step-2 tidak sinkron

| Berkas | Baris | Ulasan | Klausa unik | Catatan |
|---|---:|---:|---:|---|
| `stage1_train.jsonl` | **40.000** | 24.822 | 35.589 | angka bulat → tampak di-cap |
| `stage1_val/test` | 7.880 / 7.765 | 3.991 | 7.309 / 7.277 | tidak di-cap |
| `stage2_train.jsonl` | **60.000** | 28.839 | 45.794 | angka bulat → tampak di-cap |
| `stage2_val/test` | 9.429 / 9.386 | 3.991 | 7.324 / 7.293 | tidak di-cap |

- **15.991 klausa** yang ada di stage2 **tidak ada** di stage1; **5.859** sebaliknya. Artinya Step-1 dan Step-2 tidak pernah melihat populasi data yang sama.
- `stage1_train` juga memuat **4.411 baris duplikat** (35.589 unik dari 40.000).
- Tidak ada penjelasan di dokumen mana pun tentang batas 40.000/60.000 ini.

### 5.3 Emosi sebagai elemen kelima: hampir deterministik dari sentimen

| Ukuran | Nilai |
|---|---:|
| `H(sentiment)` | 1,386 bit |
| `H(emotion)` | 1,869 bit |
| `H(emotion │ sentiment)` | **0,498 bit** (26,6% dari entropi emosi) |
| Mutual information | 1,372 bit |
| Emosi mayoritas per sentimen | positif→joy 94,0%; negatif→anger 87,8%; netral→neutral 97,4% |
| Akurasi baseline “1 emosi mayoritas per sentimen” | **91,33%** |

**Implikasi:** elemen kelima **tidak otomatis menambah informasi**. Setiap klaim ACOSE harus mengalahkan baseline 91,33% dan melaporkan akurasi emosi bersyarat sentimen; tanpa itu, “quintuple” hanya mengganti nama sentimen dengan tiga label emosi.

### 5.4 Panjang klausa menjelaskan (sebagian) skor Step-1 yang tinggi

| Ukuran | Train | Test |
|---|---:|---:|
| Panjang token rata-rata / median / p90 | 7,8 / 6 / 15 | 7,8 / 6 / 15 |
| Baris ≤3 token | 20,0% | 20,2% |
| Tuple di baris ≤3 token | 16,7% | 17,0% |

Satu dari lima baris uji adalah frasa seperti “mantap”, “bagus”, “aplikasi banyak bug”. Ini membuat F1 span 97,94% **masuk akal tanpa** menyimpulkan model luar biasa — dan menuntut pelaporan **terpisah per panjang klausa**.

### 5.5 Kebocoran teks antar-split

| Pasangan | Teks sama | Baris test terdampak | % baris | % teks unik |
|---|---:|---:|---:|---:|
| train → test | 663 | 1.157 | **14,66%** | **8,98%** |
| train → dev | 669 | 1.245 | 15,51% | 9,00% |
| dev → test | 270 | 710 | 9,00% | 3,66% |

Split per `review_id` memang bersih di level ulasan, tetapi **tidak** di level teks klausa. Angka ini konsisten dengan 036, dan tetap menjadi ancaman validitas yang belum ditangani (tidak ada evaluasi *unique-only*).

---

## 6. Temuan kritis

### K1 — Angka “76.077 klausa” adalah jumlah baris, bukan klausa unik
76.077 baris memuat **66.198 teks klausa unik**; 8.518 baris adalah duplikat di dalam split, ditambah 663+669 teks yang muncul lintas split. Abstrak artikel memakai “76.077 clauses”, yang secara teknis keliru dan memperbesar kesan ukuran korpus ~15%.
**Tindakan:** ganti menjadi “76.077 baris klausa (66.198 teks unik)”.

### K2 — Rantai penyusutan 43.673 → 36.821 tidak terdokumentasi dan tidak reproducible
3.136 ulasan tanpa tuple dapat diterima; tetapi **3.766 ulasan berlabel dibuang tanpa alasan tertulis**, dan 50 ulasan di split tidak punya label. Skrip pembuat `stage1/stage2` **tidak ada**, sehingga split tidak dapat diregenerasi. Ini lebih serius daripada sekadar “tidak ada checkpoint”: **identitas dataset final tidak dapat direkonstruksi**.
**Tindakan:** simpan skrip builder + filter log per `review_id`, atau terbitkan split sebagai artefak beku dengan hash.

### K3 — Step-1 dan Step-2 dilatih pada populasi berbeda, dengan cap 40k/60k
Angka bulat 40.000 dan 60.000 plus divergensi 15.991 klausa menunjukkan sampling/cap yang tidak didokumentasikan. Jika Step-1 hanya melihat 49.006 klausa (67% dari 76.077 baris) dan Stage-2 59.138 klausa, maka “satu pipeline dua tahap” secara data **bukan satu pipeline**.
**Tindakan:** satukan populasi; laporkan cap sebagai hyperparameter eksplisit atau hapus cap.

### K4 — 67,86% bukan hasil terbaik; ia berasal dari run yang berhenti di epoch 1
Tiga run Step-2 yang terdokumentasi: 67,86% (ep1), 67,69% (ep3), **69,00% (ep3)**. Tidak ada yang mencapai konvergensi; tidak ada kurva penuh. Mengutip 67,86% sebagai “lower bound” jujur, tetapi memilih run terlemah sebagai headline **mengundang pertanyaan seleksi**.
**Tindakan:** laporkan ketiga run, pilih protokol (mis. median atau best-of-N dengan biaya komputasi), atau selesaikan 15 epoch.

### K5 — Diagnostik head 0,00% pasti artefak, dan itu bisa dibuktikan tanpa logit
`pair_eval` mencocokkan quadruple lengkap termasuk sentimen. Jika 67,86% quadruple cocok persis, maka akurasi sentimen pada pasangan yang sama **tidak mungkin** di bawah 67,86%. Jadi `sentiment_acc = 0.00%` adalah kegagalan instrumentasi — bukan properti model. Namun laporan 036 menyebutnya “terbukti” hanya dengan inferensi; mekanismenya (`latest_*_logits` tidak dipersist) tidak diuji.
**Tindakan:** tulis unit test yang menghitung ulang akurasi dari logit tersimpan; gate harus menolak `acc=0` bila F1>0.

### K6 — Dua angka “quad” untuk run yang sama: 67,86% vs 66,28%
Headline `pair_eval` dan tabel 15-subtask menghasilkan angka berbeda (66,28% untuk QUAD). Penyebabnya bukan data, tetapi **kontrak evaluasi**: deduplikasi per teks, perlakuan label berulang, dan agregasi per tingkat kesulitan. Ini membuat pembaca tidak punya satu sumber kebenaran.
**Tindakan:** satu evaluator multiset, satu definisi TP, satu skrip yang menghasilkan kedua tabel dari prediksi yang sama.

### K7 — Kontaminasi cache lintas domain terulang, dan notebook-nya saling bertentangan
Bukti baru: `..._V4_BERT_rest16_run24092026_...ipynb` menampilkan output **DOMAIN=rest16, backbone bert-en, sesi `rest16_24092026_1446`**, tetapi metriknya **97,19%/67,69%** — sama persis dengan sesi appsid `appsid_24092026_1426`. Sementara *source code* notebook tersebut kini berisi `DOMAIN="appsid"`. Artinya: (a) kontaminasi terjadi dua kali di dua tanggal, (b) file notebook menyimpan output dari konfigurasi yang berbeda dari source-nya.
**Tindakan:** karantina seluruh sesi rest16, hapus cache lintas domain, dan ikat output ke hash konfigurasi (config + data + backbone) sebelum disimpan.

### K8 — Hasil Inggris yang sah ada, tetapi “yatim”
`notebooks/02` memuat Step-1 rest16 **15 epoch penuh** (81,27% ep8; P 78,16/R 84,64) dan `notebooks/04` memuat Step-2 rest16 **15 epoch penuh** (48,24% ep12; P 43,39/R 54,30, pair gold). Keduanya dari pipeline lama (BERT-base), bukan IndoBERT. 036 menyatakan Step-2 rest16 tidak tersedia dan hanya mengutip 81,23% (ep6), yang tidak cocok dengan run tersimpan (81,14% ep6 / 81,27% ep8). Klaim 036 benar untuk sesi V4 IndoBERT, tetapi mengabaikan baseline legacy yang sah.
**Tindakan:** masukkan sebagai baseline kondisional: rest16 **Step-1 81,27% + Step-2-gold-pair 48,24%**, dengan label tegas “bukan end-to-end”.

### K9 — Klaim V5.2/V5.3 berlawanan langsung dengan output yang disimpan
- V5.2: `ModuleNotFoundError: bert_utils` setelah path berhasil dikonfigurasi; `DRY_RUN=True`.
- V5.2.1 & V5.3: `AssertionError: Belum ada run OK — jalankan Sel 9 DRY_RUN=False dulu`; “Hardware logs ditemukan: 0”.
- MI300X V5: `IndentationError` di sel 7, padahal notebook ini yang mendeklarasikan **54 run**.
Kombinasi ini membuktikan matriks 54 run **belum pernah dieksekusi**, apa pun isi README/changelog.

### K10 — Tidak ada satu pun artefak model di clone
Tidak ditemukan `.bin`, `.pt`, `.ckpt`, `.safetensors`, `.pkl`, `history*.csv`, `master_metrics.json`, atau folder `results/`. Semua angka E2 berasal dari output notebook. Konsekuensinya: **tidak ada evaluasi independen, tidak ada bootstrap CI, tidak ada audit prediksi per kelas** tanpa mengunduh Drive.
**Tindakan:** simpan minimal: prediksi test (teks + quadruple), logit, history, hash checkpoint, dan config per run.

### K11 — Repo tidak punya sejarah, dan banyak path absolut Windows
Satu commit hasil squash, 3,2 juta baris masuk sekaligus. Laporan JSON menyimpan path `D:\laragon\www\ACOS-ASLI\...` dan `/shared-docker/...`. Tidak ada CI, tidak ada `requirements.txt`/lock ML, dan `colab_utils.py` ada **3 salinan identik**.
**Tindakan:** requirements/lock + CI untuk gate torch-free + path relatif; hapus duplikat (±22,9 MB).

### K12 — Kualitas label belum diuji terhadap manusia, dan baseline lemah pun belum diukur
Tidak ada gold set, tidak ada κ, tidak ada pilot. Yang bisa diukur sekarang: konsistensi label dengan rating (rating 5 → 91,2% positif; rating 1 → 88,7% negatif; rating 4 → 26,9% negatif), `margin` median 0,925, dan 3.136 ulasan tanpa tuple. Semua skor F1 saat ini mengukur **sejauh mana model mereplikasi heuristic**, bukan kebenaran semantik.
**Tindakan:** sampel bertingkat ≥300 klausa, double annotation, adjudication, κ per elemen; laporkan F1 terhadap gold dan terhadap weak label secara terpisah.

---

## 7. Matriks klaim vs bukti (ringkas)

| Klaim | Putusan | Dasar |
|---|---|---|
| Dataset Apps-ACOS 43.673/92.074 | ✅ terverifikasi | hitung ulang |
| 76.077 “klausa” | ⚠️ baris, bukan unik | 66.198 teks unik |
| Tokenisasi lossless | ✅ terverifikasi | 0 UNK, 0 hilang |
| Step-1 97,94% | ✅ E2 | riwayat 8 epoch |
| Step-2 67,86% | ✅ E2, ⚠️ bukan terbaik | run B 69,00% |
| Head 0,00% = bug | ✅ inferensi kuat | batas bawah 67,86% |
| 15-subtask | ⬜ tidak dapat diverifikasi | CSV tidak ada |
| Gate-1 199/199 | ⬜ tidak dapat diverifikasi | artefak tidak ada |
| rest16 end-to-end 0% | ✅ (negatif) | TP 0, FP 165.728 |
| Kontaminasi sekali | ❌ | terjadi 12-09 dan 24-09 |
| Step-2 rest16 tidak ada | ❌ | 48,24% di `notebooks/04` |
| BERT 81,23% ep6 | ❌ | 81,14% ep6 / 81,27% ep8 |
| CV tersedia | ⚠️ split saja | skor fold tidak ada |
| V5.2 universal | ❌ | import error |
| 54 run | ❌ | assertion/IndentationError |
| ACOSE siap | ❌ | gate saja; H(E│S)=0,50 |
| Gold manusia | ❌ | tidak ada |

Detail lengkap: `reports/039_data/matriks_klaim.csv` (20 klaim).

---

## 8. Peta kematangan

| Area | Status | Dasar |
|---|---|---|
| Data mentah & pembersihan Apps-ACOS | 🟢 | 43.673 ulasan; funnel terukur |
| Konversi klausa → ACOS TSV | 🟢 | build ulang byte-identik |
| Split review-disjoint | 🟢 | 0 overlap; 3 split |
| Manifest CV 5/10-fold | 🟢 | 36.821 review; 0 overlap |
| Tokenisasi & pair Step-2 | 🟢 | 0 UNK; 0 tuple hilang |
| Gate software (`absa5`, `acos_en`) | 🟢 | 13/13; 3/3; 3/3 |
| Gate `acos_id` (tokenized, EN) | 🟡 | gagal karena vocab/unduhan, bukan logika |
| Step-1 Apps-ACOS | 🟡 | 8/15 epoch; E2 |
| Step-2 Apps-ACOS | 🟡/🔴 | 1–3 epoch; 3 run; metrik diagnostik rusak |
| Baseline BERT rest16 | 🟡 | 81,27% + 48,24% (pair gold), tetapi yatim |
| rest16 end-to-end | 🔴 | kontaminasi 2× |
| Model laptop | 🔴 | tidak ada |
| Cross-validation model | 🔴 | split saja |
| ACOSE/quintuple | 🔴 | software saja; emosi ≈ sentimen |
| V5.2/V5.3 universal | 🔴 | error eksekusi |
| Gold manusia & IAA | 🔴 | panduan ada, eksekusi tidak |
| Provenance & artefak run | 🔴 | tanpa checkpoint/CSV; 1 commit |
| Dokumentasi | 🟡 | kaya, tetapi status bercampur |

---

## 9. Batas klaim ilmiah

**Yang boleh diklaim sekarang:**

- “Kami membangun **Apps-ACOS**: 43.673 ulasan, 92.074 tuple berlabel lemah, 76.077 baris klausa (66.198 unik), split review-disjoint dan 5/10-fold yang tervalidasi.”
- “Pipeline konversi dan tokenisasi **lossless dan reproducible** (0 UNK, 0 tuple hilang, build byte-identik).”
- “Kami melaporkan **hasil interim** Step-1 97,94% (8 epoch) dan Step-2 67,86–69,00% (1–3 epoch) pada label lemah, **bukan** hasil konvergen.”
- “Kami mendokumentasikan **kegagalan orkestrasi** rest16 (cache lintas domain, TP 0, FP 165.728) sebagai negative engineering result.”
- “Kami menyediakan baseline kondisional BERT rest16: Step-1 81,27% dan Step-2 48,24% dengan **pasangan gold**.”

**Yang tidak boleh diklaim:**

- Perbandingan BERT vs IndoBERT (dataset, bahasa, domain, granularitas, dan kualitas label berbeda).
- “67,86% adalah performa akhir” (1 epoch; ada run 69,00%).
- “Cross-validation” (baru split).
- “Universal/multi-platform” (gagal eksekusi).
- “Model ACOSE” (belum ada model; emosi hampir deterministik).
- “F1 0% menunjukkan rest16 sulit” (itu kegagalan pipeline).
- “Gate-1 lulus” sebagai fakta yang dapat diaudit (artefaknya tidak ada).

---

## 10. Rekomendasi berurutan

### P0 — Kembalikan satu run yang dapat dipercaya (1–2 minggu)

1. **Bekukan dataset:** terbitkan split final + hash SHA-256 per file; sertakan skrip pembuat `stage1/stage2` (atau ganti dengan split dari TSV langsung).
2. **Hapus cap 40k/60k** atau jadikan parameter eksplisit; sinkronkan populasi Step-1 dan Step-2.
3. **Matikan cache lintas domain.** Nama run = hash(config + data + backbone + commit). Gate harus menolak hasil jika hash tidak cocok.
4. **Selesaikan 15 epoch Step-2** dan simpan: prediksi test, logit, history, checkpoint, config, environment lock.
5. **Perbaiki instrumentasi head** dan tambahkan gate: `sentiment_acc < F1_quad` → gagal.
6. **Satukan evaluator** (multiset, satu definisi TP) dan hasilkan ulang headline + 15-subtask dari prediksi yang sama.

**Kriteria lulus:** satu run Apps-ACOS yang dapat dihitung ulang dari artefak lokal, dengan F1, CI bootstrap, dan evaluasi unique-only.

### P1 — Perbaiki validitas (2–4 minggu)

7. **Evaluasi unique-clause** dan stratifikasi panjang klausa (≤3 / 4–10 / 11–20 / >20 token).
8. **Dedup/grouping** untuk mengukur dampak 14,7% kebocoran teks.
9. **Gold manusia:** ≥300 klausa, double annotation, adjudication, κ per elemen; pisahkan skor vs weak label dan vs gold.
10. **Jalankan 5-fold CV** setelah pipeline stabil; laporkan mean/std/CI per fold.
11. **Selesaikan defect rest16 baris 451** dengan aturan resmi + sensitivity run.
12. **Sitasi baseline Inggris yang sudah ada** (81,27% / 48,24%) sebagai pembanding kondisional, bukan disembunyikan.

### P2 — Rapikan produk & klaim (paralel)

13. **Turunkan klaim V5.2** menjadi “target”; tambahkan matriks uji per platform dengan hasil nyata, atau hapus klaim 8 platform/54 run.
14. **ACOSE:** uji dulu apakah emosi menambah informasi di luar sentimen (H(E│S), akurasi bersyarat, baseline 91,33%); baru latih model.
15. **Satu `EXPERIMENT_STATUS.md`** sebagai sumber status kanonik (`plan`/`interim`/`validated`/`failed`); semua laporan lain merujuk ke sana.
16. **Higiene repo:** requirements/lock, CI gate torch-free, path relatif, hapus duplikat `colab_utils.py`, arsipkan notebook tanpa output ke `archive/`.
17. **Artefak model:** gunakan Git LFS/release untuk checkpoint & prediksi; jangan bergantung pada link Drive yang dapat hilang.

---

## 11. Kesimpulan

Repo ACOS ini **sudah menghasilkan sesuatu yang nyata dan bernilai**: dataset Indonesia yang besar dengan konstruksi klausa yang dirancang hati-hati, konversi yang reproducible, tokenisasi lossless, split yang bersih di level ulasan, gate verifikasi yang benar-benar lulus, serta **tiga hasil interim dan dua negative result** yang mendokumentasikan kegagalan orkestrasi secara jujur.

Namun repo ini **belum menghasilkan satu hasil akhir yang lengkap**: tidak ada model konvergen, tidak ada artefak yang dapat diaudit ulang, tidak ada CV model, tidak ada gold manusia, dan tidak ada model ACOSE. Yang paling menyesatkan bukan angka-angkanya, melainkan **statusnya**: dokumen “final”, “universal”, dan “100% berhasil” hidup berdampingan dengan notebook yang error, cache yang menyalin hasil lintas domain, dan split yang tidak dapat diregenerasi.

Garis pemisah yang paling jujur:

> **Sudah ada:** data + label lemah + split/CV + tokenisasi + gate + hasil interim Apps-ACOS + baseline BERT rest16 (kondisional) + diagnosis kegagalan cache.
>
> **Belum ada:** eksperimen end-to-end yang konvergen dan reproducible, skor CV, gold manusia, model ACOSE, model laptop, dan provenance artefak yang memadai.

---

## Lampiran A — Perintah verifikasi yang dijalankan

```bash
# 1. Gate software
python -m absa5.selftest --repo .                       # 13/13
cd ACOS-BERT && python -m acos_en.selftest --domain rest16   # 3/3
cd ACOS-BERT && python -m acos_en.selftest --domain laptop   # 3/3
cd ACOS-IndoBERT && python -m acos_id.selftest          # 3/5 (exit 1)

# 2. Reproduksi konversi (TSV byte-identik)
cd ACOS-IndoBERT && python -m acos_id.build_acos data

# 3. Rekalkulasi seluruh statistik
python scripts/audit_039_repo.py                        # → reports/039_data/audit_039_results.json
```

Catatan lingkungan: sandbox audit tidak memuat `numpy`, `pandas`, `torch`, `requests`, dan tidak dapat mengunduh vocab backbone. Karena itu `acos_id` gate `tokenized`/`gate2_english` gagal, dan `build/_verify_id_features.py` serta `build/_sim_v4_cells.py` tidak dapat dijalankan. Kegagalan ini **lingkungan**, bukan bukti cacat logika — tetapi juga berarti gate tersebut **belum pernah diverifikasi ulang di clone ini**.

## Lampiran B — Berkas kunci

| Kebutuhan | Berkas |
|---|---|
| Data siap latih | `ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_{train,dev,test}.tsv` |
| Tokenized | `ACOS-IndoBERT/tokenized_data/` |
| Split & CV | `ACOS-IndoBERT/data/Apps-ACOS/processed/stage2_*.jsonl`, `cv_5fold/`, `cv_10fold/` |
| Riwayat Step-1 | `ACOS-IndoBERT/notebooks/00_..._V4_INDOBERT.ipynb` sel 46 |
| Run Step-2 | `V4_1_03_step2_train.ipynb`, `00_..._V4_INDOBERT.ipynb` sel 67 |
| Baseline Inggris | `notebooks/02_...` (Step-1), `notebooks/04_...` (Step-2) |
| Bukti kontaminasi | `00_..._V5_EN_REST16_LAPTOP.ipynb`, `00_..._V4_BERT_rest16_run24092026_...ipynb` |
| Gate software | `absa5/selftest.py`, `ACOS-BERT/acos_en/selftest.py`, `ACOS-IndoBERT/acos_id/selftest.py` |
| Data pendukung audit | `reports/039_data/*.csv`, `reports/039_data/audit_039_results.json` |

## Lampiran C — Keterbatasan audit

1. Semua angka E2 berasal dari output notebook; tanpa Drive, tidak ada verifikasi prediksi mentah.
2. Gate `acos_id` tokenizer dan gate-2 Inggris tidak dapat dijalankan karena vocab dan jaringan.
3. Tabel 15-subtask dan Gate-1 tidak dapat direkonstruksi tanpa CSV/logit.
4. Analisis duplikasi teks memakai kesamaan string persis, bukan normalisasi semantik.
5. Audit ini tidak mengubah kode atau data eksperimen; satu-satunya perubahan adalah penambahan `scripts/audit_039_repo.py`, `reports/039_*`, dan `reports/039_data/*`.

---

*Laporan ini adalah audit, bukan validasi. Angka yang tidak dapat dihitung ulang dari repo ditandai eksplisit sebagai E3/E4.*

---


---

## Lampiran D — Inventaris hasil (35 artefak)

Sumber tabel: `reports/039_data/inventaris_hasil.csv`. Kolom **tingkat** memakai kode E1–E4 (§1.2).

| ID | Subsistem | Artefak | Angka kunci | Tingkat | Status |
|---|---|---|---|---|---|
| A01 | Dataset Apps-ACOS | `processed/reviews_clean.csv` | 43.673 ulasan; 13 app; 37.825 Google Play + 5.848 App Store | E1 | terverifikasi |
| A02 | Dataset Apps-ACOS | `processed/quintuples_weak.csv` | 96.417 tuple; 40.537 ulasan; 69.724 klausa unik | E1 | terverifikasi |
| A03 | Dataset Apps-ACOS | `appsid_quad_{train,dev,test}.tsv` | 76.077 baris; 92.074 tuple; 66.198 teks klausa unik | E1 | terverifikasi + dapat dibangun ulang |
| A04 | Dataset Apps-ACOS | `Split utama per review_id` | 60.159/8.027/7.891 baris; 28.839/3.991/3.991 ulasan; 0 overlap | E1 | terverifikasi (split), tidak dapat diregenerasi |
| A05 | Dataset Apps-ACOS | `cv_5fold/` | 5 fold; 36.821 ulasan; test 7.365/7.364x4; 0 overlap | E1 | terverifikasi sebagai split |
| A06 | Dataset Apps-ACOS | `cv_10fold/` | 10 fold; 36.821 ulasan; 0 overlap | E1 | terverifikasi sebagai split |
| A07 | Tokenisasi | `tokenized_data/appsid_*_quad_bert.tsv` | 92.074 quad; 0 [UNK]; 0 span invalid | E1 | terverifikasi |
| A08 | Tokenisasi | `tokenized_data/appsid_*_pair.tsv` | 83.420 baris; 0 quad hilang; multi-label 0,39% train | E1 | terverifikasi |
| A09 | Konversi data | `acos_id/build_acos.py` | 3 split; 92.074 tuple; 4.183 klausa tanpa split | E1 | terverifikasi hari ini |
| A10 | Gate Indonesia | `acos_id/selftest.py` | 3 lulus (taxonomy, dataset, acos_build); 2 gagal (tokenized, gate2_english) | E1 | terverifikasi sebagian |
| A11 | Gate Inggris | `ACOS-BERT/acos_en/selftest.py` | rest16 3/3; laptop 3/3 | E1 | terverifikasi |
| A12 | Gate ACOSE | `absa5/selftest.py` | 13/13 lulus; 18.862 span; 2.417 baris pair | E1 | terverifikasi |
| A13 | Model IndoBERT Step-1 | `Notebook V4_INDOBERT sel 46` | Best 97.94% (ep8); TP 16.514 FP 434 FN 259 | E2 | bukti tersimpan |
| A14 | Model IndoBERT Step-2 (run A) | `V4_1_03_step2_train.ipynb` | F1 67,86%; TP 6.654 FP 3.951 FN 2.352 | E2 | bukti tersimpan |
| A15 | Model IndoBERT Step-2 (run B) | `00_..._V4_INDOBERT.ipynb sel 67` | 67,16 / 66,55 / 69,00%; best ep3 | E2 | bukti tersimpan |
| A16 | Model IndoBERT Step-2 (run C) | `V4_INDOBERT_run24092026 (MI300X)` | Step-1 97,19% ep3; Step-2 67,69% ep3 | E2 | bukti tersimpan |
| A17 | Model BERT rest16 Step-1 | `notebooks/02_ACOS_Step1...` | Best 81,27% (ep8); P 78,16 R 84,64 | E2 | bukti tersimpan |
| A18 | Model BERT rest16 Step-2 | `notebooks/04_ACOS_Step2...` | Best 48,24% (ep12); P 43,39 R 54,30 | E2 | bukti tersimpan |
| A19 | Model BERT rest16 end-to-end | `V5_EN_REST16_LAPTOP.ipynb` | 0,00%; TP 0; FP 165.728; FN 895 | E2 | hasil negatif (terkontaminasi) |
| A20 | Kontaminasi rest16 (baru) | `V4_BERT_rest16_run24092026` | Step-1 97,19% & Step-2 67,69% identik dengan run appsid MI300X | E2 | hasil negatif (terkontaminasi) |
| A21 | Metrik 15 subtask | `reports/036 Tabel VI` | Opinion 96,29; aspect 93,88; category 92,41; sentiment 84,97; QUAD 66,28 | E3 | terdokumentasi saja |
| A22 | Gate-1 bobot IndoBERT | `reports/036 Tabel III` | 199/199 key, 0 missing | E3 | terdokumentasi saja |
| A23 | EDA Apps-ACOS | `build/_eda_id/` | 10,6 MB CSV; 3 plot | E2 | artefak ada |
| A24 | EDA rest16 | `notebooks/01_ACOS_Setup...` | 1.530/171/583; 3.661 quad | E2 | bukti tersimpan |
| A25 | Inferensi demo | `V4_INDOBERT sel 78` | 4 baris quadruple pada 1 kalimat | E2 | bukti tersimpan |
| A26 | Cross-validation model | `-` | Tidak ada | E4 | belum ada |
| A27 | Model laptop | `-` | Tidak ada | E4 | belum ada |
| A28 | Scaffold ACOS-BERT | `ACOS-BERT/` | Gate lokal lulus; training tidak | E4 | scaffold |
| A29 | Model ACOSE (absa5) | `absa5/` | 13/13 gate; tanpa training | E4 | belum ada model |
| A30 | Gold manusia / IAA | `reports/021, 022a-h` | PDF + DOCX | E4 | belum ada anotasi |
| A31 | V5.2 universal | `Notebook V5.2` | Import gagal: bert_utils | E4 | klaim tidak terbukti |
| A32 | Matriks 54 run MI300X | `01_ACOS_MI300X_V5...` | 54 run (3 epoch x 3 rasio x 3 CV + ...) | E4 | belum ada |
| A33 | Dokumentasi | `181 file .md` | 2 duplikat persis; 8 laporan memuat angka F1 | E1 | artefak ada |
| A34 | Panduan anotasi | `dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf` | PDF 364 KB + DOCX 79 KB | E1 | artefak ada |
| A35 | Bukti lingkungan GPU | `screenshot/` | 31 PNG (MI300X, 24-09) | E2 | artefak ada |

**Cara membaca:** E1 = dapat dijalankan ulang di clone; E2 = output eksekusi tersimpan tetapi artefak run tidak ada; E3 = angka hanya di dokumen; E4 = rencana/klaim. Detail bukti per baris ada di CSV (`bukti_path`, `catatan`).

---

## Lampiran E — Matriks klaim vs bukti (20 klaim)

Sumber tabel: `reports/039_data/matriks_klaim.csv`.

| ID | Klaim | Sumber | Hasil verifikasi independen | Putusan |
|---|---|---|---|---|
| K01 | 43.673 ulasan, 76.077 klausa, 92.074 tuple | 036/032/035 | 43.673 ✓; 92.074 ✓; 76.077 adalah baris, bukan klausa unik (66.198 teks unik) | **TERVERIFIKASI SEBAGIAN** |
| K02 | Split 60.159/8.027/7.891 & 28.839/3.991/3.991 review disjoint | 036 | Sama persis; 0 irisan review | **TERVERIFIKASI** |
| K03 | 0 [UNK], 0 span invalid, 0 tuple hilang setelah retokenisasi | 036 | 0 [UNK], 0 span invalid, 0 dari 92.074 quad hilang dari pair file | **TERVERIFIKASI** |
| K04 | Multi-label 0,4% (255/65.423 pair row) | 036 | 255/65.423 = 0,39% ✓ (dev/test masing-masing 16) | **TERVERIFIKASI** |
| K05 | 14,7% baris test = klausa berulang dari train; 9,0% teks unik | 036 | 14,66% baris; 8,98% teks unik | **TERVERIFIKASI** |
| K06 | Step-1 appsid 97,94% (ep8/15, TP 16.514) | 036/030 | Riwayat 8 epoch lengkap di output notebook; cocok | **TERVERIFIKASI (output tersimpan)** |
| K07 | Step-2 appsid 67,86% pada epoch 1/15 | 036 | Cocok untuk run A; run A memang berhenti setelah 1 epoch | **TERVERIFIKASI, TAPI BUKAN TERBAIK** |
| K08 | Tidak ada hasil Step-2 rest16 yang sah | 036 | Notebook 04 memuat run rest16 Step-2 15 epoch: 48,24% (pair gold, BERT legacy); sesi V4 IndoBERT tetap tidak sah | **TERBANTAH SEBAGIAN** |
| K09 | BERT rest16 Step-1 = 81,23% (epoch 6) | 030/033/035 | Run yang tersimpan: 81,14% (ep6) dan 81,27% (ep8) | **TIDAK COCOK** |
| K10 | rest16 end-to-end 0,00% = kegagalan pipeline | 036 | TP 0; FP 165.728; FN 895; cache appsid dipakai ulang | **TERVERIFIKASI** |
| K11 | Cache lintas domain hanya terjadi sekali (12-09) | 036/038 | Terjadi lagi 24-09: run rest16 melaporkan 97,19/67,69 identik dengan run appsid | **TEMUAN BARU** |
| K12 | category_micro_f1 = sentiment_acc = 0,00% adalah bug logging | 036 | Logis mustahil: exact-match quadruple 67,86% mensyaratkan akurasi sentimen ≥ 67,86% | **INFERENSI KUAT, MEKANISME BELUM DIBUKTIKAN** |
| K13 | 15 subtask: sentimen bottleneck 84,97% vs opini 96,29% | 036 | Tabel ada, CSV master_08 tidak ada di repo | **TIDAK DAPAT DIVERIFIKASI** |
| K14 | Gate-1 199/199 bobot IndoBERT termuat | 036 | Tidak ada checkpoint/backbone lokal; tidak dapat diuji | **TIDAK DAPAT DIVERIFIKASI** |
| K15 | Cross-validation 5/10-fold tersedia | 036/038 | Manifest split lengkap & valid; skor model tidak ada | **SPLIT TERVERIFIKASI, HASIL TIDAK ADA** |
| K16 | V5.2 universal 8 platform, import fix | V5_2_README/DEV_REPORT | Notebook V5.2 berhenti di ModuleNotFoundError bert_utils | **TERBANTAH** |
| K17 | 54 run eksperimen & hasil agregasi | notebook V5.3/V5.2.1/MI300X | Tidak ada run OK; assertion & IndentationError; DRY_RUN=True | **TERBANTAH** |
| K18 | Model ACOSE (quintuple) siap | RENCANA_QUINTUPLE/absa5 | Hanya 13 gate software; tidak ada training/evaluasi emosi | **BELUM ADA MODEL** |
| K19 | Weak label = gold? | 036 | Tidak ada anotasi manusia/IAA; panduan ada, eksekusi tidak | **BELUM ADA GOLD** |
| K20 | Repo reproducible dari clone | 036/038 | Tidak ada checkpoint/CSV/history; stage builder tidak ada; 1 commit squashed | **TIDAK REPRODUCIBLE END-TO-END** |

---

## Lampiran F — Bukti per notebook (45 notebook)

Sumber tabel: `reports/039_data/bukti_notebook.csv`. Kolom **sel** = jumlah sel, **output** = sel kode yang memiliki output, **error** = jumlah output bertipe error.

| Notebook | Sel | Output | Error | Domain | Putusan |
|---|---:|---:|---:|---|---|
| `ACOS-BERT/notebooks/00_ACOS_Master_Pipeline_V1_1_BERT.ipynb` | 24 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/00_ACOS_Master_Pipeline_V1_BERT.ipynb` | 18 | 7 | 1 | rest16 | 🔴 ERROR: ModuleNotFoundError: No module named 'torchcrf' |
| `ACOS-BERT/notebooks/V1_01_setup.ipynb` | 8 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_02_step1_train.ipynb` | 11 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_03_step2_train.ipynb` | 12 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_04_eval_inference.ipynb` | 11 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_1_01_setup.ipynb` | 12 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_1_02_step1_train.ipynb` | 16 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_1_03_step2_train.ipynb` | 17 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-BERT/notebooks/V1_1_04_eval_inference.ipynb` | 16 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab.ipynb` | 23 | 10 | 1 | rest16 | 🔴 ERROR: AttributeError: 'NoneType' object has no attribute 'to' |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb` | 80 | 37 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipynb` | 86 | 37 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ipynb` | 86 | 37 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_BERT_rest16_run24092026_GPU_AMD_MI300X.ipynb` | 81 | 38 | 1 | appsid | 🔴 ERROR: RuntimeError: GATE 1 GAGAL: bobot encoder di model tidak sama dengan checkpoint. Encoder kemungkinan terinisialisasi acak (modeling.py |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT copy.ipynb` | 80 | 21 | 2 | appsid | 🔴 ERROR: KeyboardInterrupt:  |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` | 80 | 32 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb` | 81 | 38 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb` | 81 | 38 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP.ipynb` | 82 | 38 | 1 | appsid | 🔴 ERROR: RuntimeError: GATE 1 GAGAL: bobot encoder di model tidak sama dengan checkpoint. Encoder kemungkinan terinisialisasi acak (modeling.py |
| `ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb` | 80 | 0 | 0 | — | 🟡 tanpa output |
| `ACOS-IndoBERT/notebooks/01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb` | 24 | 4 | 1 | appsid | 🔴 ERROR: IndentationError: unexpected indent (890569663.py, line 25) |
| `ACOS-IndoBERT/notebooks/01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_DriveSync.ipynb` | 27 | 3 | 1 | appsid | 🔴 ERROR: ModuleNotFoundError: No module named 'bert_utils' |
| `ACOS-IndoBERT/notebooks/02_ACOS_V5_2_1_Embedding_Classification_Prediction.ipynb` | 40 | 18 | 1 | appsid | 🔴 ERROR: AssertionError: Belum ada run OK — jalankan Sel 9 DRY_RUN=False dulu. |
| `ACOS-IndoBERT/notebooks/02_ACOS_V5_2_Universal_FullExperiment_AllPlatforms.ipynb` | 35 | 3 | 1 | appsid | 🔴 ERROR: ModuleNotFoundError: No module named 'bert_utils' |
| `ACOS-IndoBERT/notebooks/03_ACOS_V5_3_Classification_Prediction_IndoBERT.ipynb` | 40 | 18 | 1 | appsid | 🔴 ERROR: AssertionError: Belum ada run OK — jalankan Sel 9 DRY_RUN=False dulu. |
| `ACOS-IndoBERT/notebooks/V4_1_01_setup.ipynb` | 33 | 15 | 0 | appsid | 🟢 output setup/diagnostik |
| `ACOS-IndoBERT/notebooks/V4_1_02_step1_train.ipynb` | 23 | 1 | 1 | — | 🔴 ERROR: :  |
| `ACOS-IndoBERT/notebooks/V4_1_03_step2_train.ipynb` | 21 | 7 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/V4_1_04_eval_inference.ipynb` | 17 | 5 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/V4_2_05_acos_classification_indobert.ipynb` | 21 | 7 | 0 | appsid | 🟢 output berisi metrik |
| `ACOS-IndoBERT/notebooks/V4_2_06_prediction_indobert.ipynb` | 17 | 5 | 0 | appsid | 🟢 output berisi metrik |
| `GPU_Status.ipynb` | 7 | 0 | 0 | — | 🟡 tanpa output |
| `kaggle/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb` | 80 | 0 | 0 | — | 🟡 tanpa output |
| `notebooks/00_ACOS_Master_Pipeline_Colab_ASLI.ipynb` | 24 | 7 | 0 | rest16 | 🟢 output setup/diagnostik |
| `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb` | 29 | 0 | 0 | — | 🟡 tanpa output |
| `notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb` | 62 | 0 | 0 | — | 🟡 tanpa output |
| `notebooks/00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb` | 26 | 10 | 1 | rest16 | 🔴 ERROR: KeyError: 'a--1,-1' |
| `notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb` | 72 | 0 | 0 | — | 🟡 tanpa output |
| `notebooks/00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb` | 82 | 0 | 0 | — | 🟡 tanpa output |
| `notebooks/01_ACOS_Setup_and_Data_Exploration.ipynb` | 17 | 8 | 0 | rest16 | 🟢 output setup/diagnostik |
| `notebooks/02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb` | 16 | 8 | 0 | rest16 | 🟢 output berisi metrik |
| `notebooks/03_ACOS_Step1_to_Step2_Pair_Generation.ipynb` | 11 | 5 | 0 | rest16 | 🟢 output setup/diagnostik |
| `notebooks/04_ACOS_Step2_Category_Sentiment_Classification.ipynb` | 15 | 7 | 0 | rest16 | 🟢 output berisi metrik |
| `notebooks/05_ACOS_Evaluation_and_Interactive_Inference.ipynb` | 24 | 5 | 0 | rest16 | 🟢 output setup/diagnostik |

**Rekap:** 45 notebook; 16 tanpa output; 13 output error. Notebook dengan hasil metrik: Step-1/Step-2 Apps-ACOS (V4_1_03, V4_INDOBERT), baseline rest16 (`notebooks/02`, `notebooks/04`), dan dua sesi rest16 yang terkontaminasi.

---

## Lampiran G — Cara memperbarui laporan ini

```bash
# 1. rekalkulasi seluruh angka (stdlib, ±5 detik)
python3 scripts/audit_039_repo.py

# 2. gate software
python3 -m absa5.selftest --repo .
cd ACOS-BERT && python3 -m acos_en.selftest --domain rest16
cd ../ACOS-IndoBERT && python3 -m acos_id.selftest

# 3. reproduksi konversi data (bandingkan dengan git diff)
python3 -m acos_id.build_acos data
```

Jika ada run baru, tambahkan baris ke `inventaris_hasil.csv` dengan tingkat bukti yang sesuai, lalu perbarui tabel di Lampiran D dan ringkasan §4.
