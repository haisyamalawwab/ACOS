# 038 — Survei, Pemetaan Hasil, dan Audit Kritis Repo ACOS

> **Tanggal audit:** 2 November 2026  
> **Cakupan:** seluruh checkout `/home/user/ACOS` (kode, data, notebook, dokumentasi, report, artefak build)  
> **Tujuan:** memisahkan hasil yang benar-benar tersedia dari rencana, demonstrasi, dan klaim yang belum terverifikasi; memetakan risiko ilmiah dan teknis.  
> **Metode:** inventaris file dan notebook, pembacaan dokumen utama dan laporan 023/028/034/036/037, inspeksi output notebook tersimpan, pemeriksaan artefak model lokal, serta menjalankan self-test yang memungkinkan.

---

## 1. Ringkasan eksekutif

Repo ini **bukan satu pipeline final yang homogen**. Ia merupakan arsip riset yang berkembang melalui beberapa cabang kerja: pipeline ACOS upstream berbahasa Inggris, adaptasi IndoBERT untuk Apps-ACOS, scaffold BERT baru, eksperimen ACOSE (emosi), eksperimen notebook V5.x, dan rangkaian dokumentasi/anotasi. Ada hasil nyata di beberapa lapisan, tetapi tingkat buktinya tidak sama.

### Putusan singkat

1. **Fondasi data dan persiapan dataset Indonesia paling matang.** Apps-ACOS memiliki data mentah, data olahan, label lemah, split per `review_id`, dan TSV train/dev/test; laporan konversi serta output notebook menunjukkan gate data/tokenisasi pernah lulus. Namun gate tokenisasi tidak sepenuhnya dapat direproduksi di checkout ini karena file vocab backbone tidak tersedia dan pengunduhan gagal dalam lingkungan audit.
2. **Ada hasil training IndoBERT yang terukur, tetapi hasil tersebut bersifat interim dan tidak lengkap di repo lokal.** Report 036 mengutip Step-1 F1 97,94% (epoch 8) dan Step-2 quadruple F1 67,86% (epoch 1/15). Hasil berasal dari artefak Google Drive yang dirujuk di laporan; checkpoint, CSV history, dan `master_metrics.json` training tidak ditemukan di checkout. Karena itu angka tersebut dapat dipakai sebagai **hasil terdokumentasi**, belum sebagai hasil yang dapat direproduksi hanya dari clone ini.
3. **Eksperimen Rest16 berstatus gagal/terkontaminasi, bukan skor model.** Report 036 dan output notebook mencatat cache Apps-ACOS dipakai ulang, riwayat identik, TP melampaui jumlah data train Rest16, serta evaluasi menghasilkan TP 0 dan FP sangat besar. Nilai F1 0% **tidak boleh ditafsirkan sebagai performa model**.
4. **V5.2 belum terbukti universal atau “100% berhasil”.** Output notebook V5.2 yang tersimpan justru berakhir dengan `ModuleNotFoundError: No module named 'bert_utils'`. Klaim README/dev report tentang keberhasilan penuh dan cakupan delapan platform lebih kuat daripada bukti eksekusi yang tersedia.
5. **`absa5/` memiliki cakupan unit/gate paling kuat, bukan hasil eksperimen ML.** Self-test lokal lulus 13/13, mencakup schema, remap span, format pair, parsing tag, metrik, persiapan demo, dan impor tanpa dependensi ML. Tidak ada bukti training atau evaluasi model ACOSE end-to-end.
6. **Cross-validation yang tersedia adalah hasil pembuatan split, bukan hasil CV model.** Ada manifest 5-fold dan 10-fold dengan pembagian review, tetapi tidak ditemukan hasil training/evaluasi per fold.
7. **Klaim ilmiah paling membatasi adalah kualitas label dan validasi.** Apps-ACOS adalah label lemah, belum ada hasil anotasi manusia/inter-annotator agreement di repo; Step-2 hanya satu epoch dalam hasil yang dilaporkan; hanya satu seed; tidak ada CV model; ada duplikasi teks lintas split pada level clause yang dicatat report 036.

**Kesimpulan keseluruhan:** repo memiliki bahan dan sebagian bukti yang cukup untuk melanjutkan riset, tetapi belum menyajikan satu eksperimen end-to-end yang bersih, lengkap, dan sepenuhnya dapat direproduksi dari checkout ini. Klaim yang paling aman sekarang adalah **hasil engineering/data preparation + hasil interim Apps-ACOS + dokumentasi kegagalan Rest16**, bukan klaim performa final atau perbandingan adil antar-backbone/dataset.

---

## 2. Cara membaca status hasil

| Status | Makna dalam audit ini |
|---|---|
| **Terverifikasi lokal** | Perintah dapat dijalankan ulang pada checkout ini dan hasilnya lulus. |
| **Hasil terdokumentasi** | Angka/output tercatat di report atau output notebook, tetapi sumber artefak eksperimen aslinya tidak tersedia di checkout untuk audit penuh. |
| **Scaffold/gate saja** | Kode, data, dan pemeriksaan awal tersedia; training/evaluasi belum dibuktikan. |
| **Rencana/klaim** | Ada desain, dokumentasi, atau klaim fitur, tetapi bukti eksekusi yang cocok tidak ditemukan atau bertentangan. |
| **Gagal/tidak sah** | Eksekusi menghasilkan kegagalan yang diketahui, atau datanya terkontaminasi sehingga metrik tidak dapat ditafsirkan sebagai performa model. |

Output tersimpan dalam `.ipynb` adalah jejak yang bermanfaat, tetapi tidak otomatis setara dengan reproduksi: output dapat berasal dari versi kode/config yang berbeda, kernel dapat dieksekusi sebagian, dan banyak notebook menunjukkan `execution_count=None` sekalipun output masih ada.

---

## 3. Peta struktur dan kematangan per subsistem

| Bagian | Isi utama | Hasil yang sudah ada | Status audit |
|---|---|---|---|
| `Extract-Classify-ACOS/` | Implementasi upstream Extract–Classify, tokenizer/model/evaluator, bridge pair | Source code; dataset tokenized Rest16/Laptop; beberapa notebook awal ber-output; analisis bug parser lama | **Kode tersedia; baseline end-to-end belum sah sebagai pembanding** |
| `data/` | Dataset upstream Restaurant-ACOS dan Laptop-ACOS, termasuk Demo-Resto-ID | TSV quadruple train/dev/test | **Data ada; sebagian diperiksa oleh gate lokal** |
| `ACOS-IndoBERT/data/Apps-ACOS/` | Raw Google Play/App Store, lexicon, processed weak labels, split, CV mappings | Data Indonesia skala besar; JSON build report; processed CSV/JSONL; manifest split 5/10 fold | **Persiapan data matang; provenance/kualitas weak labels tetap perlu diperkuat** |
| `ACOS-IndoBERT/acos_id/` | Build ACOS, taxonomy, checkpoint adapter, tokenizer, EDA, self-test | Gate dan modul persiapan; notebook lama mencatat gate hijau | **Terverifikasi sebagian; gate tokenisasi tidak dapat diulang penuh di lingkungan audit** |
| `ACOS-IndoBERT/notebooks/` | Notebook V4–V5.3, generator, fix dan walkthrough | Output eksekusi historis, termasuk hasil training interim dan kegagalan | **Sumber bukti historis, tetapi beberapa output stale/parsial** |
| `ACOS-BERT/` | Scaffold BERT baseline untuk Rest16/Laptop | Gate lokal domain Rest16 dan Laptop lulus; notebook split/master | **Scaffold terverifikasi, bukan model terlatih** |
| `absa5/` | Kerangka schema-pluggable quadruple→quintuple ACOSE | 13 self-test lulus; demo prepare dan validasi banyak kontrak | **Implementasi/engineering kuat; eksperimen ML belum ada** |
| `notebooks/` (root) | Pipeline ACOS awal, setup/EDA, Step 1/bridge/Step 2/eval, variasi staged | Output historis untuk sebagian notebook; laporan bug dan metode per-cell | **Legacy; ada hasil parsial, tetapi pipeline lama tidak menjadi baseline bersih** |
| `reports/`, `docs/`, root Markdown | Analisis, devlog, panduan anotasi, draft artikel, audit dan rencana | Banyak laporan terperinci; report 036 memetakan hasil interim dan validitasnya | **Dokumentasi kaya; ada risiko duplikasi, klaim berulang, dan status yang tidak konsisten** |
| `build/`, `dist/`, `img/`, `screenshot/` | EDA, gate data, grafik, panduan anotasi PDF, screenshot GPU | JSON gate/build, CSV/plot EDA, PDF panduan anotasi, bukti lingkungan | **Bukti pendukung; bukan pengganti artefak run/model** |

### Statistik inventaris cepat

- Ditemukan **45 notebook** dengan kira-kira **1.748 cell**. Sebagian memiliki output lama; tidak seluruhnya dieksekusi sampai akhir.
- Tidak ditemukan file checkpoint lokal (`.bin`, `.pt`, `.ckpt`, `.safetensors`), `pipeline_state.pkl`, atau CSV history training pada checkout. Model/hasil Apps-ACOS yang dibahas dalam report 036 dirujuk ke Google Drive.
- Data lokal cukup besar (checkout sekitar 473 MB; `ACOS-IndoBERT/data` sekitar 308 MB). Ini membuat repo berfungsi sebagai gabungan kode, dataset, dan arsip kerja—bukan sekadar source package.
- Folder hasil training `ACOS-IndoBERT/results/` tidak tersedia di checkout ini.

---

## 4. Peta hasil yang telah tersedia

### A. Dataset Apps-ACOS dan konstruksi data

**Artefak:** `ACOS-IndoBERT/data/Apps-ACOS/processed/`, `split_*`, `cv_5fold/`, `cv_10fold/`, `ACOS-IndoBERT/data/Apps-ACOS/_build_acos_report.json`, `ACOS-IndoBERT/tokenized_data/_build_report_appsid.json`, `build/_indobert_tokenized/_build_report_appsid.json`, report 023 dan 037.

**Hasil yang tercatat:**

- 43.673 review sumber dan `quintuples_weak.csv` yang dilaporkan berisi 96.417 tuple weak-label.
- Split utama hasil konversi: 60.159 / 8.027 / 7.891 baris klausa dan 72.973 / 9.587 / 9.514 tuple train/dev/test; 4.183 klausa tidak masuk split. Total tuple yang dipakai pada split adalah 92.074; selisih dari jumlah raw harus dibaca sebagai hasil filtering/split, bukan sebagai jumlah baris yang hilang satu-per-satu.
- `label_maps.json` mengatur 13 kategori, 3 sentimen, dan 7 emosi; tuple weak-label juga memuat `aspect_implicit`, `pairing`, `lex_score`, `evidence`, dan `margin`.
- Laporan tokenisasi mencatat 0 `[UNK]`, 0 span invalid, dan tidak ada tuple hilang setelah retokenisasi pada hasil yang pernah dijalankan.
- Pembagian 5-fold dan 10-fold memiliki `seed=42`, pemetaan per review, serta report jumlah review/tuple per fold.

**Audit kritis:**

- Struktur split per `review_id` membantu mencegah satu review bocor lintas split, tetapi tidak otomatis mencegah teks klausa identik/repetitif dari review berbeda masuk ke train dan test. Report 036 sendiri mencatat 14,7% baris test berupa klausa berulang terhadap train (9,0% teks unik disebut berulang); perlu evaluasi unique-only atau grouping/dedup sebelum angka dianggap generalisasi.
- Label dari lexicon/heuristic bukan gold human. F1 terhadap label tersebut terutama menunjukkan seberapa baik model mereplikasi anotator otomatis, bukan akurasi semantik terhadap penilaian manusia.
- `emotion` ada di skema weak-label, tetapi belum menjadi target tervalidasi manusia; jangan menyimpulkan kemampuan emosi dari keberadaan kolom.
- Path absolut Windows tersimpan di beberapa report JSON. Itu mempersulit reproduksi dan tidak berfungsi sebagai provenance portable.

**Putusan:** hasil data preparation nyata dan bermanfaat. Validasi kualitas label, audit duplikasi, dan reproduksi pipeline tokenizer masih menjadi pekerjaan ilmiah/data, bukan detail kosmetik.

### B. Tokenisasi dan validasi upstream Rest16/Laptop

**Artefak:** `ACOS-BERT/acos_en/selftest.py`, `absa5/selftest.py`, `build/_gate2/report.json`, `build/_gate2_en/report.json`, `Extract-Classify-ACOS/tokenized_data/`.

**Verifikasi yang dijalankan saat audit:**

- `python -m acos_en.selftest --domain rest16` → **3/3 gate lulus**.
- `python -m acos_en.selftest --domain laptop` → **3/3 gate lulus**.
- `absa5` gate remap membandingkan 18.862 span pada 6.359 baris dengan file tokenized yang ada; satu defect upstream dikecualikan secara eksplisit.

**Interpretasi:** taxonomy, ketersediaan data, dan konsistensi tokenized data upstream cukup baik untuk digunakan sebagai input. Ini belum membuktikan weights termuat benar atau model Rest16/Laptop berhasil dilatih.

**Cacat upstream yang terdokumentasi:** baris `rest16_train` 451 memiliki span opini zero-width (`3,3`) dan file turunan `quad_bert` vs. `pair` tidak sependapat; pair file juga kehilangan tuple tertentu. Repo `absa5` mencatat exception ini secara eksplisit. Ini adalah transparansi yang baik, tetapi sebelum benchmark harus ada keputusan kanonik: perbaiki data sumber atau keluarkan baris dengan alasan dan analisis sensitivitas yang dibakukan.

### C. Hasil training IndoBERT pada Apps-ACOS

**Sumber utama:** `reports/036_final_report_ACOS_IndoBERT_appsid_vs_rest16_12092026.md`; output notebook V4/MI300X; hasil asli dirujuk ke folder Drive, tidak ada di checkout lokal.

| Tahap | Hasil terdokumentasi | Penilaian |
|---|---:|---|
| Step-1 aspect/opinion co-extraction | Micro-F1 terbaik **97,94%** di epoch 8/15, report 036 | Hasil interim yang masuk akal sebagai skor terhadap weak label; hanya satu seed dan bukan human gold. Artefak lokal untuk hitung ulang tidak ditemukan. |
| Step-2 quadruple | **67,86%** di epoch 1/15; 6.654 TP, 3.951 FP, 2.352 FN menurut report 036 | Lower bound/interim, bukan performa final setelah konvergensi. Jangan presentasikan sebagai hasil akhir model. |
| Subtask tunggal | Opinion 96,29; aspect 93,88; category 92,41; sentiment 84,97 menurut report 036 | Menunjukkan sentimen sebagai kandidat bottleneck, tetapi angka masih terhadap data weak-label dan hanya satu epoch Step-2. |
| Gate bobot IndoBERT | Report 036 menyatakan Gate-1 199/199, 0 missing | Klaim positif yang tercatat, tetapi tidak dapat diulang pada checkout ini tanpa checkpoint/backbone. Perlu simpan log, hash checkpoint, dan versi tokenizer lokal. |

**Peringatan tambahan:** output notebook run bertanggal 24 September memperlihatkan konfigurasi sumber menyebut 50 epoch, tetapi cache membawa riwayat hanya 3 epoch (F1 97,19% pada epoch 3); Gate-1 dilewati karena model berasal dari cache. Ini membuktikan risiko utama bukan hanya kualitas model, tetapi **identitas run, cache, dan konfigurasi yang tidak melekat secara kriptografis pada output**. Jangan menyatukan angka epoch-3 dari output itu dengan epoch-8 pada report 036 tanpa menyatakan bahwa keduanya run/artefak berbeda.

### D. Rest16 bahasa Inggris: hasil negatif yang tidak boleh dianggap skor

**Sumber:** report 036 bagian VI-D dan output notebook `00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP.ipynb`.

Bukti yang dicatat:

- Riwayat Step-1/Step-2 Rest16 byte-identik dengan Apps-ACOS dan mencatat hitungan TP yang tidak mungkin untuk data Rest16.
- Run melaporkan cache hit; kandidat result root dan `SKIP_TRAINING` mengambil artefak domain yang salah.
- Evaluasi Rest16 berakhir TP=0, FP=165.728, FN=895, F1=0; metrik run dan status manifest juga kontradiktif.
- Gate weights untuk backbone Inggris tidak tersedia dalam sesi itu.

**Putusan:** ini **bukti kegagalan orkestrasi/cache/evaluasi**, bukan bukti IndoBERT buruk pada bahasa Inggris atau Rest16 sulit. Pertahankan sebagai negative engineering result, karantina run, dan jangan pakai 0% di tabel model.

### E. V5.1/V5.2 universal notebooks

**Artefak:** root `DEV_REPORT_V52_26092026.md`, `V5_2_README.md`, `V5_2_CHANGELOG.md`, `cell_0_universal_dynamic.py`, `cell_3_dynamic_adaptive.py`, `dynamic_environment_detector.py`, notebook V5.2.

**Klaim dokumentasi:** multi-platform, zero-config, import berhasil, diagnostics, setup lebih cepat.

**Bukti yang berlawanan:** output notebook `ACOS-IndoBERT/notebooks/02_ACOS_V5_2_Universal_FullExperiment_AllPlatforms.ipynb` pada cell import menampilkan `ModuleNotFoundError: No module named 'bert_utils'`. Konfigurasi notebook juga menampilkan `DRY_RUN=True`, sehingga output konfigurasi/diagnostik bukan bukti 54 training run telah berlangsung. Tidak ditemukan 54 hasil run atau CV training.

**Putusan:** V5.2 berstatus **implementasi dan eksperimen perbaikan belum lulus verifikasi eksekusi final**, bukan “ready for production” berdasarkan bukti repo. Klaim keberhasilan 100% dan delapan platform perlu diturunkan menjadi target sampai matrix test per environment disertai hasil.

### F. Scaffold ACOS-BERT

**Artefak:** `ACOS-BERT/`, report 034, selftest di atas.

- Taxonomy/data/tokenized gate Rest16 dan Laptop berhasil pada checkout lokal.
- README/report secara eksplisit mengatakan training, Gate-1 numerik dengan weights lokal, dan hasil metrik akhir masih membutuhkan runtime ML/GPU.
- Notebook master dan split notebook tersedia, tetapi notebook BERT V1.1 tidak memiliki output tersimpan pada file utama; sebagian notebook memiliki output setup/gate saja.

**Putusan:** scaffold rapi dan lebih auditabel daripada eksperimen yang cache-nya tercampur, namun **belum merupakan baseline BERT terlatih**. Jangan membandingkannya dengan hasil Apps-ACOS IndoBERT sebagai head-to-head.

### G. `absa5/`: ACOSE quadruple → quintuple

**Verifikasi lokal aktual:** `python -m absa5.selftest --repo .` → **13/13 gate passed**.

Yang terbukti: schema quad/quint dan round-trip, parsing tag, remap span, format pair, decoding, metrik multiset/subset, registries/config, prepare demo, reference format, rekey, serta impor modul tanpa ML dependencies. Repo juga mencatat secara tepat risiko bahwa emosi bisa menjadi deterministik dari sentimen dan bahwa demonstrasi lexicon fallback menghasilkan redundansi.

Yang belum terbukti: training model ACOSE, penilaian manusia terhadap label emosi, validitas konstruk emosi, generalisasi, atau peningkatan performa dari elemen kelima.

**Putusan:** **kematangan software/gates tinggi; kematangan hasil eksperimen rendah/belum ada.** Hindari menyebutnya model ACOSE yang sudah tervalidasi.

### H. Panduan anotasi dan dokumentasi

`reports/021` dan seri `022a–022h` serta `dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf` merupakan deliverable dokumentasi. Ini membuktikan pedoman anotasi dan bahan pelatihan telah disusun, bukan bahwa anotator sudah menjalankan anotasi, mencapai agreement, atau menghasilkan gold set. Perlu tambahkan versi pedoman, contoh gold adjudication, jumlah anotator, sampel pilot, dan statistik agreement ketika tersedia.

---

## 5. Audit validitas dan konsistensi klaim

### 5.1 Tidak ada eksperimen komparatif yang terkendali

Perbandingan Apps-ACOS vs Rest16 mengubah bahasa, domain, skala data, granularitas unit (klausa vs kalimat), dan kualitas label. Sesi Rest16 pula tercemar cache. Maka angka tidak dapat digunakan untuk menyimpulkan IndoBERT vs BERT, bahasa Indonesia vs Inggris, atau kualitas domain.

### 5.2 Hasil model tidak dapat direproduksi penuh dari clone

Tidak ada checkpoint model maupun hasil training mentah lokal. Report merujuk artefak eksternal Drive; beberapa notebook menyimpan output, tetapi bukan satu paket provenance yang memuat hash data/config/model, log lengkap, dan bobot. Ini menghalangi audit independen serta verifikasi angka.

### 5.3 Status eksperimen pada manifest/notebook belum cukup dipercaya

Kasus Rest16 menunjukkan manifest dapat menyatakan `FINAL_EVAL_COMPLETED` ketika hasil tidak sah. Status seharusnya dipisahkan: `TRAIN_COMPLETED`, `EVAL_COMPLETED`, `EVAL_VALIDATED`, `EVAL_FAILED`; gate konsistensi perlu menolak TP>gold count, ketidakcocokan run_result-vs-metrics, domain/backbone/hash mismatch, dan cache provenance yang hilang.

### 5.4 Metrik perlu kontrak tunggal

Report 036 mencatat mismatch metrik dual-head: Step-2 `category_micro_f1` dan `sentiment_acc` 0,00 akibat logging/cache bug, sementara fused quadruple menghasilkan 67,86%. Ini menunjukkan hasil utama dan diagnostik head belum dijamin satu sumber kebenaran. Selain itu, upstream `measureQuad` memiliki masalah duplicate counting yang disebut di `absa5`; semua skor harus dikonfirmasi dengan evaluator multiset yang teruji.

### 5.5 Cross-validation belum menghasilkan estimasi generalisasi

`cv_5fold`/`cv_10fold` berisi split dan report, bukan skor per fold. Tanpa training fold, mean/std/CI, atau repeated seeds, tidak tepat menulis “hasil cross-validation” untuk model.

### 5.6 Klaim “final” dan “universal” perlu disiplin status

Repo memuat draft artikel “final”, laporan “ready”, dan changelog yang menarasikan solusi, berdampingan dengan notebook output error dan cache contamination. Status harus didasarkan pada bukti eksekusi otomatis terkini, bukan status dokumen atau nama file.

---

## 6. Peta kematangan (merah–kuning–hijau)

| Area | Status | Dasar |
|---|---|---|
| Inventaris dataset upstream Rest16/Laptop | 🟢 | File data tersedia; selftest domain keduanya lulus. |
| Schema, span, parser, prepare di `absa5` | 🟢 | 13/13 gate berjalan lokal; bukan training ML. |
| Apps-ACOS raw/processed/split dan dokumentasi komposisi | 🟢/🟡 | Artefak data ada; komposisi tercatat, tetapi anotasi lemah dan audit provenance/duplikasi belum selesai. |
| Apps-ACOS tokenize/gate | 🟡 | Output/report historis menyatakan lulus; selftest hari ini berhenti karena vocab tak tersedia dan koneksi unduhan gagal. |
| IndoBERT Step-1 | 🟡 | F1 97,94% terdokumentasi, artefak model lokal tidak ada. |
| IndoBERT Step-2 | 🟡/🔴 | 67,86% hanya epoch 1/15; diagnosa head metrik 0 akibat logging; perlu rerun. |
| Rest16 IndoBERT/English control | 🔴 | Cache contamination dan evaluasi tidak valid; rerun wajib. |
| ACOS-BERT baseline training | 🔴 | Scaffold/gate saja, tiada training result. |
| CV model (5/10-fold) | 🔴 | Split tersedia, fold model tidak. |
| ACOSE model/validasi emosi | 🔴 | Software gate lulus; tiada gold emosi atau training. |
| V5.2 universal multi-platform | 🔴/🟡 | Source/dokumen tersedia, tetapi notebook output mencatat `bert_utils` import error; klaim universal belum dibuktikan. |
| Panduan anotasi | 🟢 sebagai dokumen / 🔴 sebagai gold dataset | PDF dan materi tersedia; tidak ada bukti pilot agreement dalam repo. |

---

## 7. Rekomendasi berurutan

### P0 — Pulihkan satu run yang dapat dipercaya

1. Jalankan ulang Apps-ACOS dari data dan config yang dikunci, matikan cache lintas domain/backbone; nama run harus mengandung hash data, config, backbone, dan commit.
2. Simpan di artefak terstruktur: `config.json`, split manifest, tokenizer/backbone revision, per-epoch raw metrics, prediksi test, gate logs, model checkpoint, environment lock, serta checksums.
3. Paksa Gate-1 selalu berjalan pada bobot yang akan dievaluasi; jangan melewati gate hanya karena model dari cache.
4. Latih Step-2 sampai protokol yang ditetapkan, benahi penyimpanan metrik dual-head, dan hitung ulang seluruh skor dengan evaluator yang menangani duplikasi sebagai multiset.
5. Jadikan pipeline berhenti keras jika domain/backbone/split hash/cache manifest tidak cocok atau jika hitungan TP/FP/FN melanggar batas.

### P1 — Perbaiki validitas evaluasi

6. Tambah evaluasi unique-clause / dedup-grouped split, bootstrap confidence interval, dan minimal beberapa seed.
7. Audit 4.183 klausa yang tidak masuk split serta selisih jumlah tuple raw-vs-kept melalui laporan filter row-level yang dapat ditelusuri.
8. Buat pilot gold Apps-ACOS (mis. sampel bertingkat per kategori/sentimen/implicitness), double annotation, adjudication, dan agreement per elemen; pisahkan score terhadap weak label dari score terhadap gold.
9. Selesaikan defect Rest16 line 451 dengan aturan resmi dan sensitivity run; jangan biarkan exception tersembunyi hanya di gate ACOSE.

### P2 — Tutup status proyek dan kurangi kebingungan

10. Jalankan smoke-test V5.2 dengan versi notebook yang sama; jika `bert_utils` masih gagal, perbaiki path/import dan buat regression test di CI. Revisi klaim platform support menjadi yang benar-benar dites.
11. Lakukan 5-fold CV setelah pipeline/cache stabil; laporkan fold score, mean/std/CI. Manifest CV saat ini hanya membuktikan split.
12. Untuk ACOSE, jangan melatih/quintuple claim sebelum anotasi manusia membuktikan emosi menambah informasi di luar sentimen (`H(emotion|sentiment)` dan agreement antarkonstruk).
13. Susun satu `EXPERIMENT_STATUS.md` sebagai sumber status kanonik dan tandai semua laporan sebagai `historical`, `plan`, `interim`, atau `validated`; hindari kata “final” sampai gate final aktual lulus.

---

## 8. Kesimpulan akhir

Folder ini kaya dalam data, iterasi engineering, analisis kegagalan, dan dokumentasi. Ia sudah menghasilkan **produk pengetahuan yang sah**: konstruksi Apps-ACOS berbasis klausa, tokenisasi yang dirancang untuk mempertahankan span, self-test ACOSE yang komprehensif, serta diagnosis konkret atas kontaminasi cache. Ia juga menyimpan **angka training interim yang menarik**, khususnya Step-1 97,94% dan Step-2 67,86% pada Apps-ACOS.

Tetapi hasil training utama tidak hadir sebagai artefak lokal lengkap; Step-2 masih satu epoch; dataset target utama lemah-label; Rest16 control tidak valid; CV model, baseline BERT terlatih, dan validasi ACOSE belum ada; dan klaim V5.2 berkonflik dengan output notebook. Maka garis pemisah yang paling jujur adalah:

> **Sudah ada:** dataset/konversi dan sebagian gates; hasil interim Apps-ACOS yang terdokumentasi; negative result Rest16 yang menjelaskan bug pipeline; 13/13 gates `absa5`; 3/3 gates ACOS-BERT per domain.  
> **Belum ada:** eksperimen akhir end-to-end yang dapat direproduksi lokal, pembandingan BERT–IndoBERT yang terkendali, skor cross-validation, gold human Apps-ACOS, dan model ACOSE tervalidasi.

Audit ini tidak mengubah kode atau data eksperimen. Self-test `absa5` dan self-test `acos_en` dijalankan pada 2 November 2026; self-test `acos_id` berhasil menjalankan taxonomy/build checks, tetapi gagal pada gate tokenizer dan gate Inggris karena vocab lokal tidak ada dan unduhan ditutup oleh koneksi TLS di lingkungan audit.
