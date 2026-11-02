# Laporan 042 — Kesiapan Publikasi: Scopus Q2 dan/atau SINTA S2

> **Tanggal penyusunan:** 2 November 2026, 23.55 WIB
> **Objek penilaian:** naskah `reports/035_Artikel_Revisi_ACOS_IndoBERT_12092026.md` (465 baris, 6 referensi, target awal "SCOPUS Q3") beserta seluruh bukti pendukungnya di `reports/036`–`reports/041`.
> **Sifat:** penilaian kelayakan (*readiness assessment*), bukan jaminan penerimaan. Kuartil jurnal berubah setiap tahun — verifikasi di Scimago (SJR) dan portal SINTA sebelum submit.
> **Pertanyaan yang dijawab:** apakah hasil-hasil ini cukup memiliki kontribusi dan potensi untuk artikel Scopus Q2 dan/atau SINTA S2?

---

## 1. Putusan

**Belum cukup untuk Scopus Q2 apa adanya. Untuk SINTA S2: belum sekarang, tetapi tercapai dalam 6–8 minggu kerja eksperimen — bukan kerja ide.**

Kekurangan utamanya bukan kebaruan dan bukan penulisan, melainkan **kelengkapan bukti**: belum ada satu pun sesi yang menyelesaikan Step-2 15 epoch pada data Indonesia, belum ada multi-seed/CV, belum ada anotasi manusia, dan belum ada baseline yang dijalankan pada split yang sama.

| Jalur | Status sekarang | Yang kurang | Estimasi kerja | Peluang setelah perbaikan |
|---|---|---|---|---|
| **Scopus Q2** | Belum layak | Bukti inti (training selesai, statistik, baseline, gold manusia) + referensi + bahasa Inggris | 4–5 bulan | Sedang (realistis bila opsi B+A) |
| **SINTA S2** | Berisiko tinggi ditolak / *major revision* | Dedupe, training selesai, 2 baseline, IAA, referensi ≥25 | 6–8 minggu | Tinggi |
| **Scopus Q3/Q4** (target awal naskah) | Hampir layak | Sama seperti S2, ambang lebih longgar | 6–8 minggu | Tinggi |

**Indeks kesiapan berbobot saat ini: 3,15 / 10.** Ambang kasar: Q2 ≈ 7,0; S2 ≈ 5,5. Proyeksi setelah paket minimum (Bagian 7): **7,4 / 10**.

---

## 2. Aset yang sudah dimiliki

| Aset | Angka kunci | Sumber | Status bukti |
|---|---|---|---|
| **Resource Apps-ACOS** | 43.673 ulasan → 80.260 klausa → 76.077 klausa pakai; 92.074 tuple label lemah; 13 kategori; split 60.159/8.027/7.891 by `review_id` | `035` §III; `037`; `_build_report_appsid.json` | Kuat (artefak + skrip) |
| **Baseline rest16 end-to-end** | Step-1 81,27% (ep8/15) → Step-2 **48,24%** (ep12/15); TP 486 / FP 634 / FN 409 | `02` sel 13 ec=8; `04` sel 10–12 ec=5–6 | **E2** (dihitung di selnya) |
| **Run pembanding rest16** | 47,68% (P 43,06 / R 53,41); 78,72 / 81,93 / 69,56 (15 sub-task) | Drive `master_metrics.json`, sesi 27/08 | E2 tanpa jejak notebook |
| **Pipeline IndoBERT appsid** | Step-1 **97,94%** (ep8); Step-2 67,86 (0809, 1 ep) · 67,69 (0901, 3 ep) · 67,16 (0509, 3 ep) | `V4_INDOBERT` sel 46/67; `V4_1_03` sel 19; MI300X sel 72 | E2/E3 (campur cache) |
| **Dekomposisi 15 sub-task dua domain** | rest16 78,95 → 48,24; appsid 94,21 → 66,08 | `04` sel 12 ec=6; MI300X sel 74 ec=163 | E2 (tetapi lihat B02) |
| **Temuan metodologis 041** | Rasio pasangan:gold **12,0×** → F1 0,00; *double-counting* gold **2,17×** (19.528 vs 9.006); kontaminasi cache lintas domain | `041` Tabel 7 & 9 | **E2, orisinal, belum masuk naskah** |
| **Audit repo & Drive** | 45 notebook/1.748 sel/575 tak pernah jalan/89 output yatim/13 error; 94 folder CV tanpa hasil | `039`, `040`, `041` | E2 |
| **Naskah 035** | 465 baris, 6 referensi, 5 ancaman validitas sudah dinyatakan jujur | `035` | Draf |

Catatan penting: naskah 035 **sudah** menyatakan bahwa klaim SOTA ditolak dan bahwa perbandingan BERT vs IndoBERT tidak valid. Sikap itu benar dan menaikkan kredibilitas — tetapi belum menutup celah bukti.

---

## 3. Skor kesiapan per dimensi

| Dimensi | Bobot | Skor sekarang | Ambang Q2 | Ambang S2 | Gap utama |
|---|---:|---:|:---:|:---:|---|
| Kebaruan (*novelty*) | 20% | 5 | 7 | 6 | Resource + analisis, belum ada metode baru yang terbukti |
| Kelengkapan bukti (training selesai) | 25% | **3** | 8 | 6 | Step-2 IndoBERT 1–3 dari 15 epoch |
| Rigor statistik (seed/CI/uji) | 20% | **2** | 7 | 5 | 1 seed; 0 CV; tanpa interval kepercayaan |
| Baseline pembanding | 15% | **2** | 8 | 6 | Tidak ada baseline dijalankan pada split yang sama |
| Konsistensi evaluasi | 10% | **3** | 8 | 6 | Dua evaluator, dua definisi gold |
| Reproduksibilitas/artefak | 5% | 6 | 7 | 6 | Audit bagus; pipeline sendiri rapuh (cache, gate) |
| Kualitas naskah & referensi | 5% | **2** | 8 | 6 | 6 referensi; bahasa Indonesia untuk target Q2 |
| **Total berbobot** | 100% | **3,15** | **≈7,0** | **≈5,5** | — |

---

## 4. Blocker yang akan langsung ditembak reviewer

| ID | Masalah | Bukti angka | Dampak | Perbaikan | Usaha |
|---|---|---|---|---|---|
| **B01** | Kebocoran teks antar split | 9,0% klausa unik test ada di train; **14,7% baris test** (1.157 baris / 14,66%) | F1 terinflasi; temuan bisa dibantah | Split ulang *group-wise* (normalisasi teks + `review_id`), laporkan F1 subset unik vs seluruh | 3–5 hari |
| **B02** | Dua evaluator, dua gold | `pair_eval` gold **9.006** vs `SubtaskMetricCapture` gold **19.528** (2,17×) | Seluruh klaim "peluruhan linier 8–9 poin" jadi artefak pengukuran | Satukan evaluator; semua angka quadruple pakai gold 9.006; ulangi dekomposisi | 5–7 hari |
| **B03** | Training belum selesai | Step-2 IndoBERT 1 epoch (0809), 3 epoch (0509/0901) dari 15 | 67,86% hanya *lower bound*, bukan hasil | 15 epoch × minimal 3 seed | 2–3 minggu GPU |
| **B04** | Tanpa statistik | 1 seed (42); CV **0 dari 54 run** yang direncanakan | Selisih 67,16/67,86/67,69 tidak bermakna | 5 seed + median/IQR + Wilcoxon; atau 5-fold CV | 1–2 minggu GPU |
| **B05** | Tanpa gold manusia | κ tidak ada; 100% label lemah | Tidak bisa mengklaim performa linguistik | IAA 300 klausa, 2 anotator, Cohen κ (target ≥0,6) + gold subset | 2–3 minggu |
| **B06** | Tanpa baseline di split sama | Publikasi: 44,52 (Extract-Classify asli); Anda 48,24; SOTA generatif 67,15 | Tidak ada tolok ukur yang sah | Jalankan ≥2 baseline pada split identik (single-head + satu generatif) | 2–3 minggu |
| **B07** | Klaim gate tidak teruji | Gate-1 gagal di `V4_BERT_rest16` sel 43 dan `V5_EN` sel 44, tetapi pipeline lanjut dan mencetak metrik | Bertentangan dengan klaim "bersifat memblokir"; risiko integritas | Perbaiki kode agar benar-benar menghentikan, atau lunakkan klaim | 2–3 hari |
| **B08** | Dual-head tanpa bukti | `category_micro_f1`, `sentiment_accuracy` = **0,00%** di semua notebook | Kontribusi metode tidak terbukti | Persistensi logit per-head + ablasi dual vs single | 1–2 minggu |
| **B09** | Referensi & bahasa | 6 referensi (Q2 umumnya 40–60; S2 20–25); naskah Indonesia | Ditolak di tahap editor | Tambah related work; versi Inggris untuk Q2 | 1–2 minggu |
| **B10** | Ketersediaan data & etika | Data ulasan App/Play Store; belum ada pernyataan ToS/anonimisasi/DOI | Reviewer Q2 hampir selalu menanyakan | Anonimisasi, pernyataan etika, rilis split + kode + DOI Zenodo | 3–5 hari |

---

## 5. Posisi terhadap literatur

Pada Restaurant-ACOS, split dan ukuran test identik dengan yang dipakai repo ini (583 kalimat, 895 quadruple):

| Sistem | P | R | F1 | Sumber |
|---|---:|---:|---:|---|
| Extract-Classify-ACOS (baseline asli) | 38,68 | 52,45 | **44,52** | [1](https://www.itc.ktu.lt/index.php/ITC/article/view/32903/15952) |
| **Pipeline repo ini (BERT-rest16, 15 epoch)** | 43,4 | 54,3 | **48,24** | `04` sel 12 ec=6 |
| Pipeline repo ini (rest16, sesi lain) | 43,06 | 53,41 | 47,68 | Drive 27/08 |
| PyABSA T5-large | — | — | 40,9 | [4](https://ceur-ws.org/Vol-3551/paper13.pdf) |
| Model generatif T5-index | — | — | **67,15** | [2](https://arxiv.org/html/2306.16956) |

Implikasi:

1. **Reproduksi baseline layak diklaim** (+3,7 poin di atas angka asli 44,52) asalkan protokol dan split dijelaskan.
2. **Tidak bisa diklaim SOTA** — tertinggal 15–19 poin dari model generatif. Naskah 035 sudah menolak klaim SOTA; itu harus dipertahankan.
3. **Angka appsid 67,69% tidak boleh disandingkan** dengan angka rest16 mana pun: dataset, bahasa, unit input, dan sifat label berbeda. Perbandingan semacam itu akan langsung gugur.
4. **97,94% bukan kapabilitas model** — itu F1 tingkat klausa (5–10 token) atas label lemah, dengan gold 16.773 span. Menyebutnya sebagai "performa IndoBERT" tanpa kualifikasi berisiko dianggap *overclaim*.

---

## 6. Tiga opsi repositioning

| Opsi | Inti klaim | Kerja tambahan | Estimasi | Peluang Q2 | Peluang S2 |
|---|---|---|---|---|---|
| **A. Resource + benchmark Indonesia** | Apps-ACOS (92.074 tuple) + protokol dua tahap + dekomposisi 15 sub-task | Dedupe & split ulang, 15 epoch × 3–5 seed, 2 baseline, IAA 300 klausa | 6–8 minggu | Sedang | **Tinggi** |
| **B. Studi empiris: jebakan evaluasi pipeline dua tahap** | Rasio pasangan kandidat vs gold (12,0× → F1 0), *double-counting* gold (2,17×), kontaminasi cache | Eksperimen terkontrol *pair-inflation sweep*, perbandingan dua evaluator, protokol audit | 4–6 minggu | Sedang–tinggi | **Tinggi** |
| **C. Metode: dual-head + gates + ablasi** | Dual-head lebih akurat dan 2,4× lebih kecil | 15 epoch × 5 seed, ablasi single vs dual, 2 domain, uji signifikansi | 3–5 bulan | Tinggi (bila berhasil) | Tinggi |

**Rekomendasi: B + A digabung.** Opsi B memakai aset paling orisinal yang sudah 100% terbukti di repo ini (temuan 041), tidak menuntut 15 epoch IndoBERT untuk bisa terbit, dan memberi sudut pandang yang jarang diambil peneliti lain: **evaluasi pipeline ACOS sendiri sebagai objek penelitian**. Opsi A menyediakan *resource* yang membuat artikel punya nilai jangka panjang.

Jika target utama adalah Q2 dan waktu tersedia, urutan terbaik: **B dulu (cepat, klaim tajam) → perluas ke A dengan gold manusia → C sebagai pekerjaan lanjutan (artikel berikutnya).**

---

## 7. Paket minimum sebelum submit

| ID | Item | Kriteria lulus | Keluaran | Usaha |
|---|---|---|---|---|
| P1 | Dedupe *group-wise* | 0 klausa identik lintas split; F1 dilaporkan untuk subset unik dan seluruh test | Tabel + split baru | 3–5 hari |
| P2 | Satu evaluator | Semua angka quadruple memakai gold 9.006; selisih dua evaluator dijelaskan | Skrip evaluasi tunggal + tabel rekonsiliasi | 5–7 hari |
| P3 | Training selesai | Step-1 & Step-2 15 epoch, tanpa cache-hit, `missing_keys=0` | 3–5 run lengkap + kurva | 2–3 minggu |
| P4 | Statistik | ≥5 seed atau 5-fold CV; median, IQR, uji Wilcoxon vs baseline | Tabel mean±std + nilai p | 1–2 minggu |
| P5 | Baseline eksternal | ≥2 baseline dijalankan pada split identik | Tabel perbandingan | 2–3 minggu |
| P6 | Gold manusia | 300 klausa, 2 anotator, Cohen κ ≥0,6; F1 weak→human dilaporkan | Tabel IAA + gold subset | 2–3 minggu |
| P7 | Ablasi dual-head | Dual-head vs single-head, 3 seed, uji signifikansi | Tabel ablasi | 1–2 minggu |
| P8 | Kontrol *backbone* | IndoBERT pada rest16 (Inggris) dan/atau BERT pada appsid | Tabel kontrol | 1 minggu |
| P9 | Artefak & etika | Dataset + split + kode + seed + hash; DOI Zenodo; pernyataan anonimisasi & ToS | Repositori + lampiran | 3–5 hari |
| P10 | Naskah | ≥30 referensi (Q2: 40+); Inggris untuk Q2; 300 DPI; *similarity* <20% | Draf final | 1–2 minggu |

Total: **6–8 minggu** bila P3–P7 dijalankan paralel di 1–2 GPU (T4/A100 cukup; 15 epoch appsid ±3–5 jam/run untuk Step-2).

---

## 8. Peta venue, biaya, dan aturan penting

| Target | Contoh venue | Waktu terbit | Biaya | Catatan |
|---|---|---|---|---|
| **SINTA S2** | Jurnal RESTI, ILKOM, JEPIN, Register, MATRIK, Techno.COM, Khazanah Informatika, IJCCS | 2–5 bulan | Rp0–2 juta | Bahasa Indonesia diterima; wajib kebaruan eksplisit + 20–25 referensi |
| **Scopus Q2** | PeerJ Computer Science, J. Intelligent Information Systems, Applied Intelligence, Expert Systems, IEEE Access, Knowledge and Information Systems | 6–12 bulan | USD 1.000–2.500 (APC) | Bahasa Inggris; 40–60 referensi; *reproducibility statement* |
| **Scopus Q3/Q4** | IAES IJ-AI, TELKOMNIKA, IJECE, IJPCC | 3–6 bulan | USD 300–1.200 | Paling dekat dengan kondisi naskah saat ini |

Aturan yang harus dipatuhi:

1. **Jangan terbitkan isi yang sama dua kali.** Jika S2 dulu, versi Q2 harus ≥50% konten baru (gold manusia, ablasi metode, uji statistik, dataset kedua) dan mengutip versi S2.
2. **Kuartil berubah tiap tahun.** Cek SJR terkini; jangan mengandalkan klaim kuartil di dokumen lama.
3. **APC Q2 bukan biaya kecil.** Jika ada pilihan Q2 tanpa APC (mis. beberapa jurnal Elsevier/Springer berbasis langganan), tempuh jalur itu.

---

## 9. Risiko dan etika publikasi

| Risiko | Uraian | Mitigasi |
|---|---|---|
| Klaim "dataset ACOS Indonesia pertama" | Pencarian awal tidak menemukan dataset ACOS quadruple Indonesia, tetapi klaim "pertama" mudah dibantah bila ada satu saja | Tulis "to the best of our knowledge"; lakukan tinjauan sistematis singkat dan kutip ABSA Indonesia yang ada (CASA, HoASA, SmSA) |
| Overclaim 97,94% | Angka tingkat klausa, label lemah, gold 16.773 span | Selalu sertakan unit, gold, dan sifat label |
| Kontaminasi cache | 97,94 dan 67,86 muncul di berkas domain lain | Laporkan sebagai temuan (041), jangan sebagai hasil |
| Gate yang tidak memblokir | Klaim "memblokir" bertentangan dengan eksekusi | Perbaiki kode atau ubah klaim |
| Duplikasi angka | 67,16/67,86/67,69 untuk model yang sama | Laporkan ketiganya dengan protokol berbeda, atau pilih satu dengan justifikasi |
| Data toko aplikasi | ToS, privasi pengulas | Anonimisasi, hapus nama pengguna, pernyataan etika |
| *Self-plagiarism* dari repo | Laporan internal bukan publikasi, tetapi teks harus ditulis ulang | Parafrase penuh; jangan salin tabel laporan apa adanya tanpa konteks ilmiah |

---

## 10. Rencana kerja 8 minggu (jalur S2, sambil menyiapkan Q2)

| Minggu | Aktivitas | Milestone |
|---|---|---|
| 1 | P1 + P2: dedupe, split ulang, satukan evaluator | Split final + tabel rekonsiliasi gold 9.006 |
| 2 | P3 mulai: Step-1 & Step-2 15 epoch (seed 42) | Kurva lengkap, `missing_keys=0` |
| 3 | P3 lanjut: seed 43, 44; P7 ablasi single-head | 3 run + tabel ablasi awal |
| 4 | P5: jalankan 2 baseline pada split sama | Tabel perbandingan 4 sistem |
| 5 | P6: anotasi 300 klausa (2 anotator) | κ + gold subset |
| 6 | P4: statistik (IQR, Wilcoxon); P8 kontrol backbone | Tabel mean±std, nilai p |
| 7 | P9: rilis artefak, DOI, etika; tulis ulang §IV–§VI | Draf v1 lengkap |
| 8 | P10: referensi 30+, gambar 300 DPI, *proofread*, format venue | Submit S2 (atau Q3) |

Jika Q2 menjadi prioritas tunggal: tambahkan 6–10 minggu untuk versi Inggris, perluasan literatur, dan satu dataset/domain kedua.

---

## 11. Draf ulang kontribusi dan judul alternatif

**Kontribusi (versi B+A, untuk S2/Q2):**

1. **Resource**: Apps-ACOS — 92.074 quadruple berlabel lemah dari 43.673 ulasan bank digital Indonesia, dengan split bersih dan protokol konstruksi yang diaudit.
2. **Temuan empiris**: rasio pasangan kandidat terhadap gold adalah faktor penentu presisi pada pipeline dua tahap — 12,0× menghasilkan F1 0,00, sedangkan 1,2–1,6× menghasilkan 48–68%.
3. **Temuan evaluasi**: dua implementasi evaluasi yang tampak setara dapat menghasilkan gold berbeda 2,17× dan F1 berbeda 1,6 poin; kami menyediakan protokol rekonsiliasi.
4. **Benchmark**: 15 sub-task berjenjang pada dua domain, dengan penurunan konsisten seiring jumlah elemen (91,08 → 66,08 pada appsid; 79,66 → 48,24 pada rest16).
5. **Reproducibility**: audit 45 notebook yang mengungkap 575 sel tak pernah dijalankan, 89 output yatim, dan kontaminasi cache lintas domain.

**Judul alternatif:**

- **B (paling tajam):** *"When Candidate Pairs Explode: Evaluation Pitfalls in Two-Stage Aspect-Category-Opinion-Sentiment Quadruple Extraction"*
- **A (resource):** *"Apps-ACOS: An Indonesian Aspect-Category-Opinion-Sentiment Quadruple Dataset and a Reproducible Two-Stage Benchmark"*
- **A+B (gabungan, rekomendasi):** *"Apps-ACOS and the Evaluation Gap: A Reproducible Benchmark for Indonesian ACOS Quadruple Extraction"*

---

## 12. Lampiran — provenance angka yang dipakai

| Angka | Nilai | Sumber | Status |
|---|---|---|---|
| Ulasan/klausa/tuple appsid | 43.673 / 76.077 / 92.074 | `035` §III; `037` | E2 |
| Split appsid | 60.159 / 8.027 / 7.891 | `035` Tabel I | E2 |
| Kebocoran teks | 9,0% klausa unik; 14,7% baris test | `035` §III-E; `039` (1.157 baris) | E2 |
| Step-1 appsid | 97,94% (ep8, gold 16.773 span) | `V4_INDOBERT` sel 46 ec=69 | E2 |
| Step-2 appsid | 67,86 / 67,69 / 67,16 | `V4_1_03` sel 19 ec=41; MI300X sel 72 ec=162; `V4_INDOBERT` sel 67 | E2/E3 |
| Step-1 rest16 | 81,27% (ep8/15) | `02` sel 13 ec=8 | E2 |
| Step-2 rest16 | 48,24% (ep12/15) | `04` sel 10–12 ec=5–6 | E2 |
| Step-2 rest16 (Drive) | 47,68% | `master_metrics.json` sesi 27/08 | E2 (tanpa notebook) |
| 15 sub-task rest16 | 78,95 → 48,24 | `04` sel 12 ec=6 | E2 |
| 15 sub-task appsid | 94,21 → 66,08 | MI300X sel 74 ec=163 | E2 |
| Gold ganda | 9.006 vs 19.528 (2,17×) | `041` Tabel 7 | E2 |
| Rasio pasangan | 12,0× → F1 0,00; 1,62× → 48,24 | `041` Tabel 7 | E2 |
| CV | 54 direncanakan, 0 selesai | `040`; `V5.2.1`/`V5.3` sel 35 | E0 |
| Audit notebook | 45 nb; 575 tak jalan; 89 yatim; 13 error | `041` Tabel 1–3 | E2 |
| Baseline publik | 44,52 (Extract-Classify); 67,15 (T5-index) | [1](https://www.itc.ktu.lt/index.php/ITC/article/view/32903/15952); [2](https://arxiv.org/html/2306.16956) | literatur |

---

## 13. Daftar periksa pra-submit

- [ ] Split bersih (0 klausa identik lintas split) dan F1 subset unik dilaporkan
- [ ] Satu evaluator, gold 9.006, tabel rekonsiliasi dua evaluator
- [ ] Step-1 & Step-2 15 epoch tanpa cache-hit, `missing_keys=0`
- [ ] ≥5 seed atau 5-fold CV + uji signifikansi
- [ ] ≥2 baseline eksternal pada split identik
- [ ] 300 klausa beranotasi manusia + Cohen κ
- [ ] Ablasi dual-head vs single-head
- [ ] Kontrol backbone lintas bahasa
- [ ] Dataset + kode + seed + hash + DOI
- [ ] Pernyataan etika data & anonimisasi
- [ ] ≥30 referensi (Q2: 40+), 80% terbit ≤10 tahun
- [ ] *Similarity check* <20%; naskah Inggris untuk Q2
- [ ] Gate-1 diperbaiki atau klaim dilunakkan
- [ ] Seluruh angka 97,94% diberi kualifikasi (klausa, label lemah, gold 16.773)

---

**Kesimpulan satu paragraf.** Bahan mentahnya cukup untuk artikel yang layak: satu resource Indonesia yang belum ada padanannya, satu baseline rest16 yang tereproduksi, satu dekomposisi 15 sub-task lintas domain, dan satu temuan metodologis yang benar-benar baru (ledakan pasangan kandidat dan inflasi gold). Yang belum ada adalah **bukti bahwa pipeline-nya sendiri bekerja pada kapasitas penuh** — dan itu yang pertama dicari reviewer Q2, serta yang paling sering menggagalkan artikel di S2. Enam sampai delapan minggu kerja eksperimen yang terarah (P1–P10) cukup untuk mengubah skor kesiapan dari 3,15 menjadi ±7,4 dan memindahkan artikel dari "berisiko" ke "layak submit".

---

## 14. Rekomendasi teknis untuk perbaikan

### 14.1 Urutan pengerjaan: validitas dulu, eksperimen kemudian

Kesalahan yang paling sering terjadi adalah menambah eksperimen (seed, dataset, model) di atas protokol yang masih cacat. Urutan yang benar:

1. **Data** (dedupe & split ulang) — T01
2. **Evaluator** (satu definisi gold) — T02
3. **Protokol pemilihan model** (dev, bukan test) — T03
4. **Statistik** (seed, CI) — T04
5. **Pembanding** (baseline eksternal) — T05
6. **Validasi manusia** (κ, gold subset) — T06
7. **Kebaruan** (eksperimen *pair-ratio sweep*) — T12

Empat langkah pertama tidak menambah klaim baru; keempatnya hanya membuat klaim yang sudah ada menjadi sah. Tanpa itu, seluruh angka di Bagian 5 tetap rapuh.

**Catatan penting untuk T03.** Ini bukan sekadar preferensi metodologis. Kode `02` dan `04` mengevaluasi **test set pada setiap epoch** dan menyimpan checkpoint ketika F1 test naik (`best_val_f1`), sehingga angka yang dilaporkan (81,27% dan 48,24%) adalah **maksimum atas 15 evaluasi test** — estimasi yang optimistis secara sistematis. Split dev sebenarnya tersedia (rest16: 171 kalimat; appsid: 8.027 klausa) tetapi tidak dipakai untuk seleksi. Memperbaiki ini adalah perubahan satu baris per notebook (`eval_type="dev"` + loader dev), dan hampir pasti menurunkan angka final 1–3 poin.

### 14.2 Peta kelemahan teknis (T01–T12)

| ID | Akar masalah | Bukti | Perbaikan teknis | Usaha | Dampak |
|---|---|---|---|---|---|
| **T01** | Split hanya by `review_id`; klausa pendek berulang lintas split | 9,0% klausa unik test ada di train; 14,7% baris test (1.157 baris) | *Union-find* atas (`review_id`, hash teks ternormalisasi) + deteksi near-dup (Jaccard 5-gram ≥0,8); laporkan F1 subset unik | 3–5 hari | Sangat tinggi |
| **T02** | Dua evaluator: `pair_eval` vs `SubtaskMetricCapture` | Gold 9.006 vs 19.528 (2,17×) | Satu evaluator kanonik; 15 sub-task dihitung sebagai **proyeksi** dari himpunan gold yang sama | 5–7 hari | Sangat tinggi |
| **T03** | **Seleksi checkpoint di test set**, bukan dev | `02` sel 11 dan `04` sel 10 memanggil `pred_eval(..., eval_type="test")` di dalam loop epoch lalu menyimpan bila `val_f1` naik; "Epoch terbaik: 8 (81,27%)" / "12 (48,24%)"; `UPDATE` mencetak "Test Micro-F1" 15 kali | Pilih checkpoint di **dev**, evaluasi test sekali di akhir; bila dev terlalu kecil (rest16: 171 kalimat), pakai 5-fold pada train+dev | 1–2 hari kode + re-run | Sangat tinggi |
| **T04** | 1 seed; tanpa interval kepercayaan | SEED 42; CV 0/54 | 5 seed + median/IQR; bootstrap 1.000× untuk CI; McNemar untuk perbandingan sistem | 1–2 minggu GPU | Tinggi |
| **T05** | Tanpa baseline pada split sama | Publikasi 44,52; SOTA 67,15 | Jalankan single-head + satu generatif (T5/PyABSA) pada split identik | 2–3 minggu | Tinggi |
| **T06** | Tanpa gold manusia | κ tidak ada | 300 klausa stratified (jumlah elemen × sentimen × implisit), 2 anotator, adjudikasi | 2–3 minggu | Tinggi |
| **T07** | Dual-head tidak terukur | `category_micro_f1` = `sentiment_accuracy` = 0,00% | Persistensi logit per-head ke JSONL saat evaluasi; ablasi dual vs single, 3 seed | 1–2 minggu | Sedang |
| **T08** | Gate gagal tetapi eksekusi lanjut | `V4_BERT_rest16` sel 43, `V5_EN` sel 44 | Gate menghentikan sel (`raise`), tulis `missing_keys=0` ke JSON, tambah gate ukuran gold (9.006/895) dan hash kode evaluator | 2–3 hari | Sedang (kredibilitas) |
| **T09** | Cache tidak dikunci konfigurasi/domain | 97,94 & 67,86 muncul di sesi rest16 | Kunci cache = SHA-1(`domain`, `backbone`, `data_sha1`, `cfg`, `seed`, `git_sha`); tolak hit bila metadata berbeda | 3–4 hari | Sedang–tinggi |
| **T10** | Pipeline hidup di notebook, bukan skrip | 45 notebook, 575 sel tak pernah jalan, 89 output yatim | Satu entrypoint `run_pipeline.py` + konfigurasi YAML; notebook jadi dokumentasi | 1 minggu | Sedang |
| **T11** | Pelaporan tidak seragam | Tabel tanpa CI/CI lebar tidak dilaporkan | Template tabel wajib: mean±std, CI95, n gold, protokol seleksi | 1 minggu | Tinggi |
| **T12** | Kebaruan belum diuji terkontrol | Rasio 12,0× → F1 0,00 hanya 1 titik data | *Pair-ratio sweep*: evaluasi model Step-2 tetap pada kandidat 1,5× / 3× / 6× / 12× / 25× gold → kurva F1 vs rasio | 1–2 minggu | **Sangat tinggi (Q2)** |

### 14.3 Empat perubahan kode inti

**(a) Split bebas kebocoran — gabungkan `review_id` dan teks identik**

```python
import hashlib, re

def norm(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def text_key(t: str) -> str:
    return hashlib.sha1(norm(t).encode()).hexdigest()[:16]

# union-find: review_id dan hash teks adalah simpul; teks yang muncul di
# beberapa review akan menyatukan review-review tersebut ke satu grup.
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

for r in rows:                      # r.review_id, r.text
    union(f"rev:{r.review_id}", f"txt:{text_key(r.text)}")
# split dilakukan atas grup (bukan baris) -> 0 teks identik lintas split
```

Setelah itu: laporkan F1 pada **seluruh test** dan pada **test unik** (satu baris per teks). Selisih keduanya adalah ukuran inflasi akibat pengulangan.

**(b) Evaluator kanonik + proyeksi 15 sub-task**

```python
# q = (category, sentiment, asp_start, asp_end, opi_start, opi_end)
def proj(q, keep):
    c, s, a0, a1, o0, o1 = q
    out = []
    if "category"  in keep: out.append(c)
    if "sentiment" in keep: out.append(s)
    if "aspect"    in keep: out.append((a0, a1))
    if "opinion"   in keep: out.append((o0, o1))
    return tuple(out)

def prf(gold, pred, keep):
    G = {proj(q, keep) for q in gold}
    P = {proj(q, keep) for q in pred}
    tp = len(G & P)
    if not P or not G:
        return 0.0, 0.0, 0.0, tp, len(P) - tp, len(G) - tp
    p, r = tp / len(P), tp / len(G)
    f1 = 0.0 if p + r == 0 else 2 * p * r / (p + r)
    return p, r, f1, tp, len(P) - tp, len(G) - tp
```

Uji wajib: `len(gold(appsid_test)) == 9006`, `len(gold(rest16_test)) == 895`, dan `TP + FN == len(gold)` pada setiap baris. Ketiga asersi ini mencegah T02 terulang.

**(c) Pemilihan model di dev + bootstrap CI**

```python
# 1) pilih epoch terbaik HANYA dari dev
best_epoch = max(range(len(dev_hist)), key=lambda e: dev_hist[e]["f1"])
# 2) evaluasi test sekali, dengan checkpoint dev-terbaik
test_metrics = evaluate(test, ckpt[best_epoch])

# 3) CI bootstrap atas contoh test (bukan atas epoch)
import random
def bootstrap_ci(pairs, n=1000, seed=42):
    rng, out = random.Random(seed), []
    for _ in range(n):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        out.append(f1_of(s))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n)]
```

Dengan 895 gold, lebar CI95 pada F1 biasanya **±2–3 poin**. Konsekuensinya: selisih 47,68 vs 48,24 (0,56) dan 67,16 vs 67,86 (0,70) **tidak boleh** diklaim sebagai perbedaan.

**(d) Cache berprovenans**

```python
meta = {"domain": cfg.domain, "backbone": cfg.backbone,
        "data_sha1": sha1_file(cfg.data_path), "cfg": cfg.hash(),
        "seed": cfg.seed, "git_sha": git_sha(), "eval_version": "v2"}
key = hashlib.sha1(json.dumps(meta, sort_keys=True).encode()).hexdigest()

if cache_hit(key):
    cached = json.load(open(cache_path(key) / "provenance.json"))
    assert cached == meta, "cache metadata mismatch -> recompute"
else:
    run_and_write(key, meta)
```

Dengan ini, kejadian 041 (angka appsid 97,94/67,86 muncul di folder rest16) tidak mungkin terulang tanpa error.

### 14.4 Tambahan analisis yang menaikkan nilai terbit (murah)

| Analisis | Alasan | Biaya |
|---|---|---|
| **Eksplisit vs implisit** | Aspek implisit 30,1%, opini implisit 40,5%; paper asli ACOS juga menganalisis ini → langsung sebanding dengan literatur | 2–3 hari |
| **Per-kelas kategori & sentimen** | Netral hanya 11,3%; recall netral hampir pasti terburuk dan perlu dilaporkan | 1–2 hari |
| **Kurva F1 vs jumlah elemen pada satu evaluator** | Menggantikan klaim "peluruhan 8–9 poin" dengan angka yang sah | sudah tercakup T02 |
| **Analisis error 200 sampel** (batas span, kategori tertukar, sentimen terbalik, pasangan salah) | Reviewer menyukai bukti kedalaman; murah | 3–4 hari |
| **Efisiensi**: parameter, waktu latih, latensi inferensi | Nilai tambah untuk jurnal terapan (S2) | 1 hari |
| **Generalisasi domain**: split bank vs e-wallet dalam appsid | Menambah klaim generalisasi tanpa data baru | 3–5 hari |

### 14.5 Matriks dampak vs usaha

| Kuadran | Item | Tindakan |
|---|---|---|
| **Dampak tinggi, usaha kecil** | T03 (dev selection), T01 (dedupe), T02 (satu evaluator), T08 (gate), T09 (cache key) | Kerjakan **minggu 1–2**; ini yang paling sering menggagalkan review |
| **Dampak tinggi, usaha sedang** | T04 (seed + CI), T05 (baseline), T06 (gold manusia), T11 (pelaporan) | Minggu 2–6 |
| **Dampak tinggi, usaha besar** | T12 (*pair-ratio sweep*), T07 (ablasi dual-head) | Minggu 4–8 |
| **Dampak sedang** | T10 (paket reproduksi), analisis tambahan §14.4 | Minggu 6–8 |

### 14.6 Ekspektasi angka setelah perbaikan

Perbaikan validitas **akan menurunkan** angka, dan itu normal serta harus diantisipasi:

| Skenario | Angka sekarang | Perkiraan setelah perbaikan | Alasan |
|---|---|---|---|
| Step-2 rest16 | 48,24% | 45–48% | Seleksi di dev (bukan test) + dedupe test |
| Step-2 appsid | 67,69% | 64–67% | Idem, ditambah evaluator tunggal |
| Step-1 appsid | 97,94% | 96–98% | Relatif stabil (span pendek), tetapi tidak lagi dipilih di test |
| 15 sub-task | 66,08% (gold 19.528) | 66–68% (gold 9.006) | Definisi gold berubah; angka tidak lagi sebanding dengan tabel lama |

Naskah harus menulis transisi ini secara eksplisit ("angka revisi menggantikan angka pra-registrasi protokol"), bukan menyembunyikannya. Reviewer Q2 menghargai protokol yang diperbaiki; reviewer akan menghukum angka yang tidak dapat direproduksi.

### 14.7 Definition of done sebelum submit

- [ ] `python -m acos_eval --self-test` lulus: `|gold|=9006/895`, `TP+FN=|gold|`, `TP+FP=|pred|`
- [ ] Split final 0 teks identik lintas split; F1 penuh vs unik dilaporkan
- [ ] Semua checkpoint dipilih di dev; test dievaluasi sekali
- [ ] ≥5 seed; setiap angka punya CI95
- [ ] ≥2 baseline pada split identik, dijalankan dengan skrip yang sama
- [ ] κ dan gold subset dilaporkan; F1 weak→human diukur
- [ ] `provenance.json` ada di setiap folder sesi; tidak ada cache lintas domain
- [ ] Satu perintah mereproduksi seluruh tabel: `make paper-tables`
- [ ] 40+ referensi (Q2) / 25+ (S2); seluruh gambar 300 DPI
