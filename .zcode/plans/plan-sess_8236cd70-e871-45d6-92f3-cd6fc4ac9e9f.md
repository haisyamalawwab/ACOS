## Rencana: Laporan `030_analisis_komparatif_bert_vs_indobert.md`

### Output
Satu file Markdown baru: `reports/030_analisis_komparatif_bert_vs_indobert_10092026.md`

### Prasyarat
- Read-only: tidak ada kode, notebook, atau konfigurasi yang dimodifikasi
- Semua metrik diambil dari output cell notebook yang sudah dieksekusi + laporan yang ada
- Mesin lokal tanpa torch/transformers — tidak ada training yang dijalankan

### Struktur Laporan (9 bagian)

**§1 — Ringkasan Eksekutif (TL;DR)**
Tiga paragraf padat: dataset berbeda (apples-to-oranges), metrik yang ada, dan kesimpulan paling penting — bahwa 97.94% Step 1 di appsid adalah artefak dataset, bukan keunggulan IndoBERT.

**§2 — Matriks Perbandingan Penuh**
Tabel master 12 dimensi: dataset, ukuran, domain, unit input, labeling, arsitektur, parameter, GPU, metrik Step 1, metrik Step 2, status bug, status eksekusi.

**§3 — Analisis Dataset: rest16 vs appsid**
- Skala: 2.284 kalimat/3.661 quad (rest16) vs 76.077 klausa/92.074 quad (appsid) — 25× lebih besar
- Domain: restoran (aspek kompleks multi-kata) vs bank digital (aspek teknis singkat)
- Granularitas unit: kalimat penuh vs klausa — klausa lebih pendek → span extraction lebih mudah
- Kualitas label: manual gold vs weak labeling otomatis (floor=0.3, saturation=2.0)
- Distribusi sentimen dan implisit/eksplisit
- **Insight**: F1 Step 1 yang tinggi di appsid bukan berarti IndoBERT lebih unggul

**§4 — Analisis Arsitektur Model**
- Embedding: 30.522 vs 50.000 vocab, dampak ~15M parameter tambahan
- Identitas arsitektur encoder (12 layer, 768 hidden, 12 head)
- Single-head (39 fused label) vs Dual-head (13 cat + 3 sent)
- Bug prefix `bert.` di IndoBERT checkpoint dan risiko silent random encoder

**§5 — Dinamika Training: Step 1**
- BERT: 81.23% F1 (epoch 6/15, A100) pada rest16
- IndoBERT: 97.94% F1 (epoch 8/15, T4) pada appsid — baru 8 dari 15 epoch
- Analisis loss curve IndoBERT: 2.14 → 0.10 dalam 8 epoch (konvergensi sangat cepat)
- Mengapa gap 16.7 poin: klausa pendek + data 25×, bukan keunggulan model

**§6 — Dinamika Training: Step 2**
- BERT: crash `KeyError: 'a--1,-1'` — tidak ada hasil
- IndoBERT: 67.86% quadruple F1 (baru 1 epoch dari 15, AMP+BS32+T4)
- Analisis per-difficulty-slot: slot mudah 90-95%, slot sulit 92% — distribusi aneh
- Bug dual-head: category_micro_f1 = sentiment_accuracy = 0.00%
- Prediksi: F1 akan naik signifikan di epoch berikutnya

**§7 — Dekomposisi 15 Subtask & Agregasi**
- Tabel 15 subtask dari termudah (opinion: 96.29%) ke tersulit (full quad: 66.28%)
- Agregasi per jumlah elemen: 1 → 91.89%, 2 → 82.82%, 3 → 73.81%, 4 → 66.28%
- Pola error propagation: setiap tambahan elemen menurunkan F1 ~8-9 poin
- Analisis di mana kategori vs sentimen masing-masing lemah (terbatas dual-head bug)

**§8 — Empat Critical Insight Sintesis**
1. Perbandingan langsung tidak valid tanpa kontrol dataset yang sama
2. Ukuran dataset (25×) mendominasi performa, bukan pilihan backbone
3. Cross-lingual (IndoBERT pada rest16) adalah satu-satunya eksperimen kontrol yang valid — belum dijalankan
4. Tiga bug harus diselesaikan sebelum kesimpulan apapun bisa ditarik (dual-head metrics, prefix bert., Step 2 baru 1 epoch)

**§9 — Rekomendasi & Next Steps**
Prioritas berurut:
1. Jalankan Step 2 sampai selesai (15 epoch atau early stop)
2. Perbaiki dual-head metrics bug (`latest_cat_logits`/`latest_senti_logits`)
3. Verifikasi Gate 1 (prefix `bert.`) dengan torch di Colab
4. Bangun dan jalankan cross-lingual notebook (IndoBERT + rest16)
5. Jangka panjang: pertimbangkan freeze-encoder atau LoRA

### Yang TIDAK dilakukan
- Tidak menjalankan training
- Tidak memodifikasi kode/notebook
- Tidak membuat visualisasi/chart
- Tidak berspekulasi tanpa data