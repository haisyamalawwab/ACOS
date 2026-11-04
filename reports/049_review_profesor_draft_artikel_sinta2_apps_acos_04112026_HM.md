# Review Profesor AI/NLP — Draf Artikel SINTA 2 "Apps-ACOS"

> **Tanggal review:** 4 November 2026
> **Target review:** `reports/048_draft_artikel_sinta2_apps_acos_03112026.md` (167 baris)
> **Peran penilai:** Profesor AI/NLP (20 th), reviewer Scopus Q3 & SINTA 2, Lead Senior Software Engineer, Lead Researcher, Mentor researcher
> **Kerangka penilaian:** `.agents/skills/persona-profesor-reviewer.md` (klasifikasi severity BLOCKER/MAYOR/MINOR/NIT + wajib solusi konkret)
> **Terkait:** `reports/042_kesiapan_publikasi_q2_s2_02112026_HM.md`, `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md`, `reports/038_analisis_kritis_hasil_folder_results_indobert_02112026.md`

---

## 0. Ringkasan penilaian

**Major revision — belum layak submit dalam kondisi sekarang.**

Naskah ini punya dua keutamaan yang jarang saya temukan di draf SINTA 2:

1. **Kejujuran status interim.** Draf secara eksplisit melabeli angka sebagai "batas bawah, belum konvergen", menolak klaim SOTA, dan menolak melaporkan angka 97,94% cache-hit sebagai kapabilitas.
2. **Audit reproduksibilitas (Tabel 5).** Enam ancaman validitas yang diidentifikasi, dikuantifikasi, lalu disertai remediasi — ini bahan publikasi yang layak, dan banyak naskah Q3 tidak seberani ini.

Namun tiga masalah kelas **BLOCKER** cukup untuk membuat reviewer menolak naskah *sebagai benchmark resource*, yang justru merupakan klaim utamanya:

- klaim "pertama" tanpa protokol pencarian sistematis;
- tidak adanya validasi manusia atas 92.074 label lemah;
- lisensi/izin rilis sumber daya yang tidak disebut sama sekali.

**Posisi keputusan:** naskah bisa bergerak cepat ke arah *metodological-audit paper* (kerjakan #7, #5, polish), atau menunggu menjadi *benchmark resource* yang kuat (kerjakan #2, #4, #3 terlebih dahulu). Kondisi sekarang berada di tengah-tengah, dan di situlah reviewer menangkap kontradiksi.

---

## 1. Temuan Review

| # | Severity | Temuan | Akar masalah | Solusi konkret | Effort |
|---|---|---|---|---|---|
| 1 | **BLOCKER** | Klaim "belum memiliki benchmark" / "sumber daya ACOS Indonesia **pertama**" (Abstrak L21, §1 L35) dinyatakan sebagai fakta tanpa bukti pencarian | Negasi eksistensial adalah klaim terkuat di naskah, tetapi tidak ada metode pencariannya | Tambah subbagian *Related Work* dengan protokol eksplisit: database yang dibaca (Scopus, Google Scholar, ACL Anthology, Garfika), string query, tahun cakupan, kriteria inklusi, dan berapa kandidat yang diperiksa lalu dieksklusi. Jika tidak sanggup, turunkan menjadi "sejauh penelusuran kami, belum ditemukan…" | 1–2 hari |
| 2 | **BLOCKER** | 92.074 quadruple berlabel lemah, **nol** verifikasi manusia. §3.7 mengakui "κ belum diukur" | Untuk *resource paper*, mutu label = produk yang dijual. Reviewer akan minta bukti label dapat dipercaya | Anotasi manual acak 500 klausa oleh 2 annotator → laporkan Cohen's κ + akurasi weak-label terhadap gold manusia. Sertakan di Tabel 1 sebagai kolom `agreement`. Ini sekaligus menjawab R4 ("batas klaim yang valid pada hasil label lemah") yang kini **tidak terjawab** di §3 | 3–5 hari (butuh anotator) |
| 3 | **BLOCKER** | Tidak ada pernyataan lisensi/izin redistribusi ulasan Google Play & App Store | ToS kedua toko umumnya membatasi redistribusi konten ulasan. Jurnal resource wajib mencantumkan lisensi | Tulis eksplisit di §2.1: apakah data mentah dirilis, atau hanya anotasi/split ID + tautan ke sumber (fair-use). Pilih lisensi (CC BY 4.0 / MIT) dan tautkan repo. Jika data tidak bisa dirilis → ubah framing dari "resource" menjadi "metode konstruksi resource" | 2–4 jam |
| 4 | **MAYOR** | Selisih 48,24 vs 44,52 (§3.1 L88) diklaim "+3,7 poin" dari **1 seed** pada 895 quadruple gold. SE binomial ≈ √(0,5·0,5/895) ≈ **1,66 poin** → 95% CI ≈ ±3,3 poin. Besarnya gains ≈ 2,2 SE, dan selisih dua run independen dari sumber berbeda tidak bisa dibandingkan tanpa varians upstream | Klaim improvement butuh distribusi, bukan satu titik | Jalankan ≥3 seed pada kontrol. Lapor mean ± std + paired bootstrap/t-test pada test set identik. **Alternatif murah:** ganti kalimat menjadi "setara dengan baseline upstream (48,24 vs 44,52)", hapus kata "di atas" | 3 seed ≈ 3–6 jam GPU |
| 5 | **MAYOR** | §3.4 menemukan sentimen hampir deterministik dari kategori (APP_PERFORMANCE 79,4% negatif, AUTH_ACCESS 78,5%, UI_UX 71,1% positif) — naskah sendiri menyimpulkan "membatasi validitas metrik sentimen". Tetapi angka utama 69,00% (Tabel 4) tetap disajikan tanpa pembanding trivial | Jika head kategori BCE sudah memprediksi sentimen, F1 quadruple mengukur kemampuan menyalin korelasi kategori→sentimen, bukan pemahaman bahasa | **Eksperimen penutup wajib, sangat murah:** baseline *majority-per-category* (prediksi sentimen = mayoritas kelas untuk kategori itu). Laporkan di tabel baru. Jika baseline ini tembus ~60%, itu bottleneck sesungguhnya dan justru memperkuat narasi §3.3 | 2–4 jam, tanpa GPU |
| 6 | **MAYOR** | "(Implisit,Implisit)=0" (§3.4 L105) kontradiktif dengan klaim Abstrak L21 "termasuk slot implisit" | Kombinasi nol hampir pasti artefak pipeline bridge (produk Kartesian aspek×opini tidak pernah menghasilkan (-1,-1) bersamaan), bukan fenomena data | Jelaskan mekanismenya di §2.2 atau akui sebagai limitation di §3.7. Jangan biarkan pembaca menemukan kontradiksi sendiri — ini sinyal "tidak paham data sendiri" bagi reviewer | 1–2 jam |
| 7 | **MAYOR** | Temuan kebocoran 14,66% (Tabel 5) sudah diketahui, namun Tabel 4, §3.3, dan Abstrak melaporkan angka **sebelum dedupe** sebagai headline | Angka yang diketahui terkontaminasi tidak boleh muncul di Abstrak tanpa kualifikasi kuantitatif | Laporkan dua kolom: `F1 (test bocor)` dan `F1 (test unik 85,34%)`; atau pindah seluruh Tabel 4 ke subbagian *prak-sanksi/diagnostik* dengan judul eksplisit. Hitung metrik pada subset bersih — tidak perlu latih ulang, hanya evaluasi ulang | 3–5 jam |
| 8 | **MAYOR** | Sitasi backbone salah (L66): `indobenchmark/indobert-base-p1` diberi rujukan [5],[6]. [5] = IndoNLU, [6] = IndoLEM/IndoBERT (kumpulan benchmark). Model base-p1 berasal dari **Yulius et al., "IndoBERT and IndoBERTa: Sentiment Analysis Models for Indonesian", arXiv:2104.08191** | Kelalaian atribusi primer; mudah diverifikasi reviewer dan merusak kredibilitas | Tambah referensi khusus model base-p1, sitasi itu di §2.2; biarkan [5],[6] hanya untuk benchmark IndoNLU/IndoLEM | 30 menit |
| 9 | **MAYOR** | R1–R4 (§1 L41) tidak dipetakan eksplisit ke §3. R4 sama sekali tidak terjawab; R2 hanya terjawab implisit lewat enam gerbang | Struktur IMRaD melonggar: pertanyaan yang diajukan harus dijawab | Tambah paragraf penutup §3 berisi tabel pemetaan `RQ → subbagian → bukti`. Untuk R4, jawab memakai hasil anotasi manusia (#2) + interval dari #4 | 2–3 jam |
| 10 | **MINOR** | Format angka **campur dalam satu paragraf**: Abstrak Indonesia L21 memakai "43.673 / 76.077", Abstract Inggris L27 memakai "43,673 / 76,077". Daftar Pustaka juga campur ("hlm." vs "pp.") | Tidak ada *house style* yang ditetapkan | Kunci satu konvensi (pedoman Indonesia: titik sebagai pemisah ribuan) di seluruh naskah; Abstract Inggris mengikuti konvensi jurnal target. Sesuaikan gaya sitasi ke satu format (IEEE atau APA) sesuai author guideline | 2–3 jam |
| 11 | **MINOR** | Referensi didominasi survei & karya lama (2001–2022: [10]–[27]); 19 dari 28 entri adalah survei/sumber generik. Tidak ada ACOS/quadruple pasca-2022 selain [9] | Survei tidak menggantikan posisi penelitian terkini; kemutakhiran referensi dan self-citation ratio diperiksa di SINTA 2 maupun Scopus Q3 | Pakai `ACOS-IndoBERT/REFERENCES/` (24 tinjauan + ±20 PDF, disebut di L5) untuk menambah 6–8 paper quadruple/implicit-slot 2022–2025. Batasi survei maksimal 5 entri | 1 hari |
| 12 | **MINOR** | [9] MEMD-ABSA (pra-cetak arXiv) dipakai sebagai pembanding numerik "T5 67,15" (§3.1 L88, §3.6 L122) | Membandingkan angka dari pra-cetak tanpa peer-review, pada split yang tidak dipastikan identik | Verifikasi apakah 67,15 dihitung pada split Restaurant-ACOS yang sama. Jika tidak, hapus perbandingan atau pindah ke kalimat kualifikasi. Gunakan versi publikasi jika tersedia | 1–2 jam |
| 13 | **NIT** | Tabel 4 tidak punya kolom dev — padahal akar masalah T03 adalah tidak adanya seleksi pada dev | Presentasi mengulang kesalahan yang dikritik sendiri | Tambah kolom `dev F1` dan tandai checkpoint yang terpilih lewat dev | 15 menit |
| 14 | **NIT** | "67,16–69,00%" (Abstrak) adalah min–maks dari 3 baris epoch, bukan interval. "CATATAN EDITORIAL (hapus sebelum submit)" L9 rawan tertinggal | Bahasa kuantitatif longgar | Tulis "F1 tertinggi 69,00% pada epoch ke-3 dari 15". Buat checklist penghapusan L3–L9 saat submit | 15 menit |

---

## 2. Rekomendasi Urutan Perbaikan

1. **#3 → #2** (lisensi & validasi manusia) — menentukan apakah naskah ini *boleh* berdiri sebagai resource paper. Jika keduanya gagal, reframing total (#1) mengikuti.
2. **#7** (evaluasi ulang pada test bersih) — murah, mengubah seluruh angka yang ada. Kerjakan sebelum yang lain supaya tidak menghitung dua kali.
3. **#5** (baseline majority-per-category) — murah, dan hasilnya berpotensi menjadi temuan terkuat naskah.
4. **#4, #9** — eksperimen multi-seed + pemetaan RQ.
5. **#8, #1, #11, #12** — koreksi atribusi, protokol klaim "first", kemutakhiran referensi.
6. **#10, #13, #14** — polish house style dan presentasi.

---

## 3. Catatan Mentor

Yang membedakan draf ini dari rata-rata kiriman SINTA 2 yang saya review adalah **Tabel 5**. Enam ancaman validitas diidentifikasi, dikuantifikasi (14,66%; 2,17×; 97,94% cache-hit), lalu disertai remediasi. Sayang sekali naskah kemudian *tetap melaporkan* angka yang dihasilkan oleh kondisi terkontaminasi tersebut — itulah jurang antara "jujur" dan "konsisten".

Pilihan yang harus Anda ambil, bukan saya:

- **Jalur A — audit metodologis + resource label lemah.** Jadikan Tabel 5 tulang punggung kontribusi. Bisa submit lebih cepat, tetap jujur, dan punya pembeda yang tidak bisa diklaim ulang oleh grup lain.
- **Jalur B — benchmark final yang bersih.** Lebih kuat dan potensi sitasinya lebih tinggi, tetapi wajib menyelesaikan #2 (IAA) dan #4 (multi-seed) lebih dulu.

Jangan berada di tengah-tengah seperti sekarang.

---

## 4. Artefak Peran yang Dibuat Sesi Ini

| Berkas | Fungsi |
|---|---|
| `.agents/skills/persona-profesor-reviewer.md` | Sumber kebenaran peran (93 baris): aturan skeptisisme, klasifikasi severity, standar penulisan jurnal, format output review, dan Bagian 7 titik masuk per agen |
| `AGENTS.md` (root) | Pointer untuk agen yang membaca root: ChatGPT Codex, Openclaw, Hermes, Opencode, ARENA AI, Zcode. Tidak menyalin isi, hanya menunjuk sumber kebenaran |
| Memori `Persistent Expert Persona Requirement` | Diperbarui: roster agen kini mencakup ChatGPT Codex, Claude Code, Kiro + jalur persistensi repo |

**Titik masuk per agen (masih terbuka):**

| Agen | Berkas yang dibacanya | Status |
|---|---|---|
| ChatGPT Codex, Openclaw, Hermes, Opencode, ARENA AI, Zcode | `AGENTS.md` (root) | ✅ dibuat |
| Qoder | `.agents/skills/*.md` | ✅ dibuat |
| Claude Code | `CLAUDE.md` (root) | ⬜ belum dibuat |
| Kiro | `.kiro/steering/*.md` | ⬜ belum dibuat (folder steering tidak ada; repo hanya punya `.kiro/specs/`) |
| Cursor | `.cursor/rules/*.mdc` | ⬜ belum dibuat |

---

## 5. Batas Keyakinan Review Ini

Agar tidak terjadi salah baca tentang apa yang sudah dan belum saya verifikasi:

- Yang saya baca pada review pertama **hanya** draf `reports/048`. Saya **belum** membuka artefak primer (CSV hasil epoch, log training, file split, kode evaluator) sehingga temuan #4, #5, #7 dihitung dari angka yang **tertulis di draf**, bukan dari data mentah. SE 1,66 poin pada #4 adalah estimasi binomial sederhana, bukan selisih dengan varians antar-seed terukur. *(Catatan: setelah bagian ini ditulis, saya membuka `reports/033` untuk cek silang — hasilnya dilaporkan di Bagian 6.1; artefak primer tetap belum dibuka.)*
- Verifikasi struktur repo: `AGENTS.md`, `CLAUDE.md`, `.kiro/steering/**`, `.cursor/rules/**` saya cek dengan glob dan **tidak ada** pada saat review (kecuali `AGENTS.md` yang kemudian saya buat).
- Temuan #8 (atribusi `indobert-base-p1`) berasal dari pengetahuan domain saya atas lanskap model IndoBERT dan perlu dikonfirmasi ke kartu model HF resmi sebelum diubah menjadi teks naskah — jangan menyalin nomor arXiv dari dokumen ini tanpa pengecekan.
- Review ini **tidak** menyatakan hasil eksperimen salah; review ini menyatakan klaim belum terdukung pada tingkat yang diminta SINTA 2.

---

## 6. Tindak Lanjut — Perluasan Peran (4 November 2026)

Peran diperluas dengan dua kapasitas baru: **penulis utama artikel** dan **copy editor**; ditambah daftar **kelengkapan isi standar Scopus Q3** (Poin 4.1 pada berkas peran). Temuan di Bagian 1 di atas **tidak berubah**; yang berikut adalah konsekuensi baru dari kriteria 4.1 terhadap draf `reports/048`, yang belum sempat dinilai saat review pertama karena kriterianya belum ada:

| Artefak Q3 | Status di draf 048 | Tindakan |
|---|---|---|
| Gambar konsep/arsitektur | ⬜ **nol gambar** di seluruh naskah (167 baris, hanya 5 tabel) | Tambah diagram alur 2-tahap (Step-1 BERT-CRF → bridge Kartesian → Step-2 dual-head) dari `img/acos_indobert_architecture.png` yang sudah ada di repo, plus diagram task dengan contoh klausa→quadruple |
| Grafik plot hasil | ⬜ tidak ada | Kurva loss & dev/test F1 per epoch untuk Tabel 4; bar 15 sub-task untuk §3.3 (sudah ada precedens di `reports/fig24/`) |
| Tabel EDA | ⚠️ ada sebagai paragraf naratif di §3.4 | Pindahkan ke tabel eksplisit: distribusi kategori, sentimen per kategori, top-10 term, rasio kosakata tertutup |
| Confusion matrix + per-class P/R/F1 | ⬜ tidak ada | Wajib untuk mendukung klaim §3.4 bahwa sentimen dapat diprediksi dari kategori (temuan #5) |
| Rumus formal | ⬜ tidak ada (hanya notasi inline "ℝ¹⁵³⁶" dan "13×3") | Tulis definisi quadruple, skema BIO, micro-F1, loss BCE+CE dual-head, dan bridge Kartesian sebagai persamaan bernomor |
| Tabel ablasi | ⬜ tidak ada | **Koreksi setelah cek silang:** `reports/030` dan `reports/033` **bukan** ablasi terukur — 033 secara eksplisit menyebut kontribusi backbone "~0 — estimasi analitis (rep. 030 §5.2), bukan ablasi terukur" dan **menolak** klaim "IndoBERT lebih baik dari BERT". Jadi baris backbone pada tabel ablasi wajib dijalankan sebagai eksperimen baru, bukan diambil dari laporan tersebut. Ablasi yang bisa memakai bahan existing: tanpa head IA/IO, mean-pool vs [CLS], tanpa bridge |
| Analisis error bercontoh | ⬜ tidak ada | 5 kasus sulit: singkatan non-standar, campur kode, klausa <3 kata, opini implisit |
| Angka gambar = angka tabel = angka Abstrak | belum dapat diverifikasi (belum ada gambar) | Jadikan langkah terakhir sebelum submit |

**Konsekuensi penilaian:** dengan kriteria 4.1, draf 048 bergeser dari *major revision* menjadi **mayor + pekerjaan presentasi substantif**. Naskah berisi 5 tabel dan 0 gambar adalah bentuk yang oleh reviewer Q3 dibaca sebagai *technical report*, bukan *article*. Urutan perbaikan di Bagian 2 tetap berlaku; sisipkan satu langkah baru **di antara langkah 3 dan langkah 4** (setelah angka bersih dari #7 dan #5 tersedia, sebelum multi-seed #4 ditutup) untuk pembuatan gambar, plot, rumus, dan tabel ablasi — **jangan membuat visual dari angka interim yang nanti berubah**, itu sumber revisi ganda.

### 6.1 Temuan Baru dari Cek Silang (setelah review pertama)

Review pertama hanya membaca draf 048. Setelah saya membuka artefak sumbernya, muncul dua temuan yang **tidak bisa** terdeteksi dari draf saja:

| # | Severity | Temuan | Bukti | Solusi |
|---|---|---|---|---|
| 15 | **MAYOR** | Jumlah quadruple gold kontrol **tidak konsisten**: draf 048 §3.1 menyebut "583 kalimat test, **895 quadruple**", sedangkan `reports/033` Tabel 1 mencatat split rest16 `583 / 916` (kalimat / quadruple) | 895 (048 L81) vs 916 (033 L24) | Tentukan satu angka dari **artefak primer** (file test gold), bukan dari laporan turunan. Koreksi juga di semua tempat yang memakainya (denominator metrik, klaim +3,7 poin). Ini persis jenis kegagalan "angka tabel ≠ angka metode" yang dilarang Poin 4.1 | 30–60 menit |
| 16 | **MINOR** | Estimasi SE pada temuan #4 saya hitung dengan denominator 895. Dengan 916: SE ≈ √(0,25/916) ≈ **1,65 poin** (95% CI ≈ ±3,2) | — | Kesimpulan #4 **tidak berubah**: gains 3,72 poin masih setara ~2,3 SE pada satu seed, sehingga belum layak disebut improvement tanpa multi-seed. Angka final menunggu #15 tuntas | — |

**Pelajaran proses** (untuk agen lain yang melanjutkan): draf 048 menyatakan sendiri di L3 bahwa angka-angkanya diambil dari "verifikasi artefak primer Drive + repositori", namun dua laporan turunan di repo ini sudah saling berbeda angka. Sebelum submit, **setiap angka di naskah harus ditelusuri ke artefak primer**, bukan ke laporan lain.

---
*Akhir dokumen review.*
