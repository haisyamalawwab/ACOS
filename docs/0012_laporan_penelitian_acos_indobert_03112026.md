# Laporan Penelitian — Survey, Pemetaan Hasil, dan Analisis Kritis ACOS-IndoBERT (Apps-ACOS)

| Item | Keterangan |
|---|---|
| Judul kerja | Apps-ACOS: Ekstraksi Quadruple Aspect–Category–Opinion–Sentiment untuk Ulasan Aplikasi Bank Digital Berbahasa Indonesia |
| Bidang | Pemrosesan Bahasa Alami (NLP) — Aspect-Based Sentiment Analysis (ABSA) |
| Tanggal laporan | 3 November 2026 |
| Versi / Status | 1.0 — Draf internal (konsolidasi survey + audit) |
| Objek survey | Repositori `rozanhaisyam/ACOS` + folder Drive `results` (ID `1vKiRYlU2K9cNQWgXV4JBO5u-7DdtiAFq`) |
| Metode | Enumerasi rekursif Drive API, pembacaan artefak primer (JSON/CSV/MD/TXT), verifikasi silang terhadap repo & laporan terdahulu (038–044), hitung ulang mandiri |
| Dokumen terkait | `docs/0011` (laporan 02/11), `reports/045` (artikel SINTA2 02/11), `reports/048` (artikel SINTA2 03/11) |

> **Catatan metode.** Laporan ini disusun dari verifikasi artefak primer Drive + repositori GitHub. Analisis gambar memakai verifikasi angka pada CSV sumber + kode pembangkit plot + audit visual terdahulu (`reports/042` untuk 31 screenshot; `reports/040`-korelasi untuk 4 plot EDA).

---

## Ringkasan Eksekutif

Proyek ini membangun **Apps-ACOS**, sumber daya ACOS berbahasa Indonesia pertama pada domain bank digital, beserta adaptasi pipeline *Extract-Classify* ke IndoBERT. Survey menemukan bahwa **lapisan data, gerbang verifikasi, checkpoint, dan Step-1 sudah memiliki artefak nyata**, tetapi **Step-2 belum selesai, cross-validation gagal total, dan sejumlah angka yang beredar tidak dapat dipertahankan**.

| Klaim | Nilai | Status bukti | Putusan |
|---|---|---|---|
| Ukuran dataset | 43.673 ulasan → 76.077 klausa → 92.074 tuple | Kuat (artefak + hitung ulang) | Dipakai |
| Step-1 appsid (IndoBERT) | 97,94% micro-F1 (ep8) | Cache-hit, 8/15 epoch | **Ditolak sebagai kapabilitas**; laporkan sebagai interim |
| Step-1 rest16 (BERT) | 81,27% micro-F1 (ep8/15) | Kuat (notebook tereksekusi) | Dipakai sebagai kontrol |
| Step-2 appsid (sesi Drive 05/09) | 67,16 / 66,55 / 69,00% (3/15 epoch) | Interim, belum selesai | Lower bound, bukan hasil final |
| Step-2 rest16 (BERT) | 48,24% F1 (ep12/15) | Kuat | Dipakai sebagai kontrol |
| Cross-validation (54 run rencana) | 0 valid; 93/94 ERROR | Kuat (run_result.json) | Tidak ada skor CV yang sah |
| Gate-1 bobot encoder | 199/199 key, mean identik | Kuat | Lulus |
| Kesiapan publikasi | 3,15/10 (S2 ≈ 5,5; Q2 ≈ 7,0) | Penilaian 042 | Belum siap submit; 6–8 minggu kerja |

> **Putusan satu baris:** dataset dan pipeline berjalan serta terdokumentasi baik, tetapi tiga masalah harus dibereskan sebelum naskah diajukan — seleksi checkpoint pada test set, kebocoran teks 14,66% baris test, dan angka 97,94% (cache-hit) yang masih beredar.

---

## BAB I — Pendahuluan

### 1.1 Latar Belakang
Ulasan aplikasi bank digital memuat keluhan dan pujian yang terikat pada objek tertentu (kegagalan transfer, biaya admin, kecepatan verifikasi, kualitas antarmuka). Analisis sentimen tingkat dokumen tidak dapat memisahkan objek-objek tersebut; yang dibutuhkan adalah ekstraksi **quadruple** (aspek, kategori, opini, sentimen) beserta penanganan **slot implisit**. Untuk bahasa Indonesia, kapasitas ini belum tersedia sebagai benchmark — IndoNLU hanya menyediakan CASA (aspek mobil) dan HoASA (hotel), keduanya berhenti pada pasangan aspek–sentimen.

### 1.2 Tujuan Survey
1. Memetakan bagian repositori dan folder Drive yang **sudah memiliki hasil** versus yang masih kosong/gagal.
2. Memverifikasi angka-angka yang dilaporkan terhadap artefak primer.
3. Menganalisis gambar (screenshot alur kerja dan plot hasil) secara kritis.
4. Menyusun dasar faktual bagi laporan penelitian dan draft artikel SINTA 2.

### 1.3 Ruang Lingkup & Metode
Survey mencakup: (a) struktur repositori GitHub (folder ACOS-IndoBERT, ACOS-BERT, Extract-Classify-ACOS, absa5, notebooks, reports, docs, screenshot, img); (b) folder Drive `results` berisi tiga sesi; (c) 31 screenshot; (d) plot EDA dan figure laporan. Metode: enumerasi rekursif, pembacaan isi artefak, verifikasi silang tiga sumber (Drive, repo, laporan terdahulu), dan hitung ulang mandiri. Tingkat bukti: **E2** (dihitung ulang/dieksekusi), **E1** (artefak tanpa eksekusi ulang), **E3** (klaim tanpa artefak).

---

## BAB II — Peta Artefak dan Hasil

### 2.1 Peta Repositori (GitHub)
| Folder | Isi | Status hasil |
|---|---|---|
| ACOS-IndoBERT/ | Pipeline utama: acos_id/, notebooks/, data/Apps-ACOS/, tokenized_data/, REFERENSI/, REFERENCES/, build/ | Berisi kode + data + audit; hasil training tidak disimpan di repo |
| ACOS-BERT/ | Pipeline kontrol Inggris (acos_en) | Berisi kode + notebook |
| Extract-Classify-ACOS/ | Kode upstream ACL 2021 (tidak dimodifikasi) | Referensi baseline |
| absa5/ | Arsitektur modular ABSA | Eksperimental |
| notebooks/ | 45 notebook, 1.748 sel (audit 041) | 575 sel tak pernah jalan; 13 error |
| reports/ | 47+ laporan audit (001–047) + figure fig1–fig24 | Kaya; menjadi tulang punggung bukti |
| docs/ | PRD, rencana, laporan penelitian 0011/0012 | Laporan 0011 sudah menolak 97,94% |
| screenshot/ | 31 PNG sesi MI300X (24/09) | Dianalisis penuh di laporan 042 |
| img/ | Infografis arsitektur & cakupan review-vs-klausa | Perlu koreksi angka |

### 2.2 Peta Folder Drive `results`
| Objek | Jenis | Isi | Status |
|---|---|---|---|
| appsid_05092026_122741 | Sesi utama (T4) | 16 CSV, 9 MD, 9 log/JSON, 6 plot, 3 set checkpoint | **Berhenti di Step-2 epoch 3/15** |
| experiments_26092026 | Eksperimen | Kerangka + _backbone/_eda/_gates + _pair_bridge + _grid_composition | Gagal sebelum mulai; EDA parsial ada |
| experiments_27092026 | Eksperimen CV | 94 folder run (cv5fold 34, cv10fold 60) + _embedding/_eda/_gates | **54 run, semuanya ERROR** |
| latest_pipeline_state_appsid.pkl | State | 775 KB | Salinan state sesi |

### 2.3 Matriks Status Hasil per Komponen
| Komponen | Ada hasil? | Bukti | Kelayakan pakai |
|---|---|---|---|
| Dataset Apps-ACOS (TSV + stats) | Ya | eda_dataset_statistics.csv, _build_report | Layak (label lemah) |
| EDA + 4 plot | Ya | 4 PNG + 4 CSV, terverifikasi 1:1 | Layak |
| Gerbang verifikasi (Gate-1 + 5 gerbang data) | Ya | gate1_weights.json, id_gates.json | Layak |
| Checkpoint Step-1/Step-2 | Ya | step1_best, step2_best, step2_epoch_3 (475–500 MB) | Ada; isi bobot belum diinferensi ulang |
| Step-1 training history | Ya (8 epoch) | step1_training_history.csv | Interim; mode cache-hit |
| Step-2 training history | Ya (3 epoch) | step2_training_history.csv | Interim; dual-head = 0 |
| Candidate pairs (bridge) | Ya | candidate_pairs_summary.csv (10.735) | Layak |
| Cross-validation | **Tidak valid** | 93 run_result.json = ERROR | Tidak boleh dikutip |
| 15 sub-task appsid | Tidak di Drive ini | master_08 di Drive = milik REST16 | Perlu sesi lain / hitung ulang |
| Screenshot alur kerja | Ya | 31 PNG | Layak sebagai dokumentasi proses |

---

## BAB III — Data dan Metode

### 3.1 Konstruksi Apps-ACOS
| Tahap | Keluaran | Jumlah |
|---|---|---|
| Ulasan terkumpul & dibersihkan | reviews_clean.csv | 43.673 ulasan (13 aplikasi) |
| Pelabelan lemah | quintuples_weak.csv | 96.417 baris (pra-pemecahan) |
| Pemecahan klausa | appsid_quad_*.tsv | 80.260 klausa |
| Dibuang (tanpa split) | _build_acos_report.json | 4.183 klausa |
| Dataset final | train/dev/test | 60.159 / 8.027 / 7.891 = 76.077 |
| Tuple | total | 72.973 / 9.587 / 9.514 = 92.074 |

### 3.2 Statistik per Split (terverifikasi dari CSV Drive)
| Split | Klausa | Quad | Asp-Ekspl | Asp-Impl | Opi-Ekspl | Opi-Impl | Neg | Neu | Pos |
|---|---|---|---|---|---|---|---|---|---|
| train | 60.159 | 72.973 | 51.184 | 21.789 | 43.271 | 29.702 | 36.217 | 8.274 | 28.482 |
| dev | 8.027 | 9.587 | 6.588 | 2.999 | 5.836 | 3.751 | 4.819 | 1.030 | 3.738 |
| test | 7.891 | 9.514 | 6.576 | 2.938 | 5.693 | 3.821 | 4.788 | 1.100 | 3.626 |
| **Total** | **76.077** | **92.074** | **64.348** | **27.726** | **54.800** | **37.274** | **45.824** | **10.404** | **35.846** |

Proporsi: aspek implisit 30,11%; opini implisit 40,48%; sentimen negatif 49,77% / netral 11,30% / positif 38,93%. Panjang klausa: mean 8,92 kata, median 7, p25=4, p75=11, maks 79 (jauh di bawah `max_seq_length` 128).

### 3.3 Arsitektur Dua Tahap
| Komponen | Spesifikasi |
|---|---|
| Backbone | `indobenchmark/indobert-base-p1`, 12 layer, 768 hidden, 12 head, vocab 50.000 |
| Step-1 | BERT-CRF, tag BIO (O, B/I-A, B/I-O) + dua head biner implisit (IA, IO) |
| Bridge | Produk Kartesian A × O, termasuk pasangan implisit (-1,-1) |
| Step-2 | Fitur [mean-pool(aspect); mean-pool(opinion)] ∈ ℝ¹⁵³⁶ → head 39 dimensi (13 kategori BCE + 3 sentimen CE) |
| max_seq_length | 128 |
| Hiperparameter (manifest) | epoch 15, batch 24/16, lr 2e-5/5e-5, seed 42, device Tesla T4 |

### 3.4 Gerbang Verifikasi
Gate-1 (bobot encoder): 199/199 key cocok, mean tensor identik → LULUS. Lima gerbang data (taxonomy, dataset, acos_build, tokenized, gate2_english) semuanya ok=true; 0 quad hilang saat retokenisasi; tidak ada tumpang tindih review_id antar split. Gate-2 English memverifikasi paritas rest16 dengan upstream (selisih 1 baris pair sesuai cacat data upstream yang terdokumentasi).

---

## BAB IV — Hasil Terverifikasi

### 4.1 Step-1 (Ekstraksi Span) — sesi Drive, T4
| Epoch | Loss | TP | FP | FN | P% | R% | F1% |
|---|---|---|---|---|---|---|---|
| 1 | 2,1422 | 16.084 | 993 | 689 | 94,19 | 95,89 | 95,03 |
| 2 | 0,5881 | 16.311 | 630 | 462 | 96,28 | 97,25 | 96,76 |
| 3 | 0,3933 | 16.487 | 633 | 286 | 96,30 | 98,29 | 97,29 |
| 4 | 0,2903 | 16.463 | 491 | 310 | 97,10 | 98,15 | 97,63 |
| 5 | 0,2213 | 16.462 | 518 | 311 | 96,95 | 98,15 | 97,54 |
| 6 | 0,1763 | 16.445 | 450 | 328 | 97,34 | 98,04 | 97,69 |
| 7 | 0,1330 | 16.485 | 485 | 288 | 97,14 | 98,28 | 97,71 |
| 8 | 0,0999 | 16.514 | 434 | 259 | 97,44 | 98,46 | **97,94** |

**Catatan kritis:** `step1_run_result.json` mencatat `mode=cache_hit`, `epochs_recorded=8` dari target 15. Angka 97,94% berasal dari pemuatan cache, bukan eksekusi penuh; tidak boleh dikutip sebagai kapabilitas model. VRAM puncak 5.174 MB.

### 4.2 Step-2 (Klasifikasi Quadruple) — sesi Drive, T4
| Epoch | Loss | TP | FP | FN | P% | R% | F1% | Cat-F1 | Sent-Acc |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0,5511 | 6.552 | 3.953 | 2.454 | 62,37 | 72,75 | 67,16 | 0,0 | 0,0 |
| 2 | 0,3792 | 6.542 | 4.111 | 2.464 | 61,41 | 72,64 | 66,55 | 0,0 | 0,0 |
| 3 | 0,3052 | 6.830 | 3.962 | 2.176 | 63,29 | 75,84 | **69,00** | 0,0 | 0,0 |

**Catatan kritis:** hanya 3/15 epoch (status STEP2_TRAINING). Metrik dua kepala (`category_micro_f1`, `sentiment_acc`) = 0,0 permanen di CSV dan resume → bug persistensi, bukan sekadar tampilan; tidak ada bukti empiris kepala kategori/sentimen belajar. TP+FN = 9.006 (gold test). Angka 69,00% adalah lower bound interim.

### 4.3 Distribusi Tipe Pasangan Kandidat (Bridge)
| Tipe | Jumlah | % |
|---|---|---|
| Explicit-Implicit | 4.459 | 41,54 |
| Explicit-Explicit | 3.456 | 32,19 |
| Implicit-Explicit | 2.813 | 26,20 |
| Implicit-Implicit | 7 | 0,07 |
| **Total** | **10.735** | 100 |

### 4.4 Cross-Validation (experiments_27092026)
| Metrik | Nilai |
|---|---|
| Folder run | 94 (cv5fold 34, cv10fold 60) |
| Status ERROR | 93 (98,9%) |
| Bug #1 `'list' object has no attribute 'items'` | 87 run (gagal 7–9 detik) |
| Bug #2 `'BertForQuadABSA' object has no attribute 'save_pretrained'` | 6 run (89 detik; sempat menulis log) |
| Status OK / skor valid | **0** |
| Run dengan metrik degenerat | 6 (F1 100%, fp=fn=0, tp konstan antar-fold) |

**Akar masalah:** tokenisasi hanya selesai untuk partisi basis; 18 partisi CV/ratio belum tertokenisasi. Run dijalankan terhadap direktori tokenisasi yang tidak ada. Enam run gelombang-3 menghasilkan F1 100% dengan fp=fn=0 dan tp tidak cocok jumlah quad fold mana pun → metrik degenerat (evaluasi pada data latih / bug), tidak boleh dipakai.

### 4.5 Audit Embedding
`embedding_audit.csv`: vocab_txt 30.521 baris vs config_vocab_size 50.000 (selisih 19.479); hidden 768; emb_params 38,4 jt; span_bergeser 25.992; baris_lebih_126 = 0. Angka 25.992 span bergeser dapat direproduksi dari repo (20.615+2.742+2.635); ini bukan cacat baru tetapi menegaskan 14,12% span berubah offset setelah retokenisasi. Narasi "+14 juta parameter karena vocab" adalah salah tafsir — embedding 50.000×768 adalah desain IndoBERT; baris di atas 30.520 tidak pernah diindeks.

---

## BAB V — Analisis Gambar (Screenshot & Plot)

### 5.1 Analisis Screenshot (31 gambar, sesi MI300X 24/09)
Folder `screenshot/` merekam satu hari kerja penuh provisioning GPU AMD Instinct MI300X (AMD Developer Cloud) dan eksekusi pipeline. Rekonstruksi (laporan 042, pembacaan visual 31/31):
- **Infrastruktur:** droplet `2.10.0-gpu-mi300x1-192gb-devcloud-atl1` (Atlanta), 192 GB VRAM, 20 vCPU, 240 GB RAM, $1,99/jam; container ROCm + JupyterLab (port 8000/8888) + aaPanel PRO 8.0.6; WSL Ubuntu-24.04 lokal.
- **Kontrol REST16 berhasil di Step-1:** Micro-F1 test 53,20% → 80,76% (15 epoch, 2m35s) — hasil sah paling lengkap yang terekam.
- **Step-2 REST16 gagal total:** Micro-F1 0,00% (TP=0, FP=165.728, FN=895) — model tidak pernah memprediksi positif; mode kegagalan Step-2 sudah muncul di domain kontrol sebelum CV appsid.
- **Sesi APPSID 50-epoch disiapkan** (124,5 jt parameter, 65.423 contoh latih) tetapi artefak sesinya tidak tampak di `results/` lokal.
- **GPU sangat tidak termanfaatkan:** utilitas memori puncak 9% dari 192 GB, VRAM terpakai 475 MB, daya 350 W (idle 140 W).
- **Risiko keamanan:** JupyterLab & aaPanel terbuka publik pada IP yang sama; versi PyTorch tidak konsisten (marketplace 2.10.0 vs MOTD 2.12.0+rocm7.14).

**Implikasi:** screenshot adalah bukti proses yang kuat, tetapi juga mengungkap inefisiensi biaya, kegagalan Step-2 yang berulang, dan risiko keamanan yang harus ditutup.

### 5.2 Analisis Plot EDA (4 PNG, terverifikasi 1:1 dengan CSV)
| Plot | CSV sumber | Korelasi | Temuan |
|---|---|---|---|
| 01_eda_dataset_distribution | eda_dataset_statistics.csv | Identik (12/12 bar) | Split & eksplisit-implisit konsisten; satuan 'Sentences' ≠ baris CSV anotasi (per-quad) |
| 02_eda_category_sentiment | category_sentiment_counts + dataset_statistics | Identik (bar+pie) | Pie polaritas 49,8/38,9/11,3 dikonfirmasi 3 sumber independen |
| 02b_eda_length_and_implicit_combo | length_describe + all_samples_annotated | Identik + info joint | Mengungkap (Impl,Impl)=0 → hanya 3 kombinasi; tidak terlihat di CSV marginal |
| 02c_eda_category_sentiment_heatmap | category_sentiment_counts.csv | Identik (39/39 sel) | Sel tergelap FEATURES_PRODUCT/Positif (14.212); terterang PROMO_MARKETING/Netral (124) |

**Putusan:** keempat plot EDA dapat dipertanggungjawabkan (angka gambar = angka CSV). Namun korelasi ini sepenuhnya di lapisan EDA — tidak ada plot yang mewakili hasil training, karena 94 run CV tidak menghasilkan plot maupun metrik sah. Mengutip plot sebagai "hasil eksperimen" adalah kesalahan kategori.

### 5.3 Analisis Figure Laporan & Infografis
| Figure | Isi | Catatan integritas |
|---|---|---|
| fig18 / img acos_indobert_architecture | Diagram dua tahap (BIO-CRF → bridge → head 39) | Representasi arsitektur benar; label nomor internal perlu diselaraskan |
| fig24_arsitektur_acos_indobert_detail | Diagram arsitektur detail (baru, 03/11) | Perlu verifikasi terhadap kode aktual |
| fig3_step1_curve | Kurva loss & F1 Step-1 | Perjelas run/domain (rest16 vs appsid) dan status cache |
| fig4_15subtask | Dekomposisi 15 sub-task | Terkena temuan dua evaluator (gold 9.006 vs 19.528); perlu hitung ulang |
| fig21_eda_sumber_appsid | EDA 43.673 ulasan (rating, panjang, tahun, aplikasi) | Valid; distribusi bimodal, 61,96% ulasan 2026 |
| fig22/fig23 wordcloud | Wordcloud A/C/O/S & per polaritas | Panel netral memuat kata negatif → kelas sisa, bukan tanpa polaritas |
| img acos_review_vs_clause_coverage | Infografis cakupan review vs klausa | Memakai angka 61,5/48,0 yang tidak lolos uji replikasi — harus dikoreksi |

---

## BAB VI — Temuan Kritis dan Ancaman Validitas
| ID | Temuan | Bukti | Dampak |
|---|---|---|---|
| T01 | 97,94% adalah cache-hit | step1_run_result.json mode=cache_hit | Bukan kapabilitas; jangan dikutip |
| T02 | Step-2 belum selesai (3/15) | step2_progress.json | 69,00% hanya lower bound |
| T03 | Seleksi checkpoint pada test set | metrik dihitung pada test tiap epoch | Angka optimistis 1–3 poin |
| T04 | Kebocoran teks 14,66% baris test | 1.157 baris test identik train | F1 terinflasi |
| T05 | Dual-head metric = 0,0 permanen | CSV + resume | Kontribusi dual-head tidak terbukti |
| T06 | CV 0 valid (93 ERROR) | run_result.json | Tidak ada rigor statistik |
| T07 | Metrik CV degenerat (F1 100%) | 6 training_log.csv | Evaluasi bocor/bug |
| T08 | Dua evaluator, dua gold (9.006 vs 19.528) | pair_eval vs SubtaskMetricCapture | Dekomposisi 15 sub-task perlu ulang |
| T09 | Vocab mismatch & 25.992 span bergeser | embedding_audit.csv | Integritas label perlu dijaga |
| T10 | Label lemah, tanpa IAA manusia | quintuples_weak.csv | Klaim linguistik terbatas |
| T11 | 61,5/48,0 tidak tereplikasi | uji 10 kombinasi tokenisasi (044) | Justifikasi klausa harus ditulis ulang |
| T12 | Kosakata tertutup (362 aspek, 202 opini) | hitung ulang 044 | F1 tinggi ≠ generalisasi |

---

## BAB VII — Rekomendasi dan Peta Jalan

### 7.1 Prioritas Perbaikan (blocker publikasi)
1. **B01 Dedupe & split ulang group-wise** (normalisasi teks + review_id); laporkan F1 subset unik vs seluruh. (3–5 hari)
2. **B02 Satukan evaluator**; semua angka quadruple pakai gold 9.006; ulangi dekomposisi 15 sub-task. (5–7 hari)
3. **B03 Selesaikan Step-2** 15 epoch × minimal 3 seed. (2–3 minggu GPU)
4. **B04 Statistik**: 5 seed + median/IQR + Wilcoxon, atau 5-fold CV yang benar. (1–2 minggu GPU)
5. **B05 Gold manusia**: IAA 300 klausa, 2 anotator, Cohen κ ≥ 0,6. (2–3 minggu)
6. **B06 Baseline pada split sama**: ≥2 baseline (single-head + generatif). (2–3 minggu)
7. **B07 Gate benar-benar memblokir**; perbaiki kode atau lunakkan klaim. (2–3 hari)
8. **B08 Dual-head terbukti**: persistensi logit per-head + ablasi dual vs single. (1–2 minggu)
9. **B09 Referensi ≥25** + related work; versi Inggris untuk Q2. (1–2 minggu)
10. **B10 Etika & ketersediaan**: anonimisasi, pernyataan ToS, rilis split+kode+DOI Zenodo. (3–5 hari)

### 7.2 Perbaikan Kode Segera
- Perbaiki Bug #1 (`'list' object has no attribute 'items'`) pada pemuatan data CV.
- Tambahkan `save_pretrained` pada `BertForQuadABSA` (Bug #2).
- Selesaikan tokenisasi 18 partisi CV/ratio sebelum menjalankan grid.
- Perbaiki persistensi metrik dual-head (`category_micro_f1`, `sentiment_acc`).
- Pisahkan seleksi checkpoint (dev) dari evaluasi akhir (test).

### 7.3 Posisi Publikasi
Repositioning dari klaim performa ke **reproducible benchmark + audit metodologis**. Kontribusi yang dapat dipertahankan: (K1) dataset Apps-ACOS; (K2) adaptasi pipeline Extract-Classify ke IndoBERT dengan gerbang verifikasi; (K3) dekomposisi 15 sub-task (setelah evaluator disatukan); (K4) audit metodologis yang jujur. Target SINTA 2 realistis setelah paket minimum 6–8 minggu; Scopus Q2 butuh 4–5 bulan.

---

## Lampiran A — Inventaris Artefak Kunci (Drive)
| Artefak | Lokasi | Isi |
|---|---|---|
| session_manifest.json | appsid_05092026_122741/ | Status STEP2_TRAINING, T4, hiperparameter |
| step1/step2_training_history.csv | csv/ | Riwayat per epoch |
| gate1_weights.json, id_gates.json | logs/ | Verifikasi bobot & data |
| backbone_report.json | logs/ | Unduhan & re-key IndoBERT |
| candidate_pairs_summary.csv | csv/ | 10.735 pasangan kandidat |
| embedding_audit.csv | experiments_27092026/_embedding/ | Audit vocab & span |
| run_result.json (×94) | experiments_27092026/*/ | Status ERROR semua |

## Lampiran B — Tingkat Bukti
**E2**: dihitung ulang/dieksekusi di sesi audit (mis. statistik dataset, korelasi plot-CSV). **E1**: artefak ada tanpa eksekusi ulang (mis. checkpoint, riwayat training Drive). **E3**: klaim tanpa artefak pendukung (mis. 67,86% yang tidak ada di folder ini). Semua angka dalam laporan ini diberi label tingkat bukti di tabel terkait.

---
*Disusun oleh Arena Agent dari verifikasi artefak primer Drive + repositori GitHub, 3 November 2026.*
