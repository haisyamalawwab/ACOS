# Laporan Penelitian — Kondisi Terkini Proyek Apps-ACOS: Konsolidasi Artefak, Kontradiksi Angka, dan Kesiapan Klaim

**Tanggal penyusunan:** 10/11/2026
**Dasar penyusunan:** commit `cee6893` pada `main` (merge PR #13) dan berkas yang ada di repositori pada commit tersebut.
**Sifat dokumen:** laporan *status*, bukan laporan hasil akhir. Tujuannya menjawab satu pertanyaan: **apa yang sekarang benar-benar dimiliki proyek ini, dan apa yang belum boleh diklaim.**

**Legenda tingkat bukti.** **E2** = terverifikasi di repositori lewat kode, keluaran tersimpan, atau hitung ulang. **E1** = dokumen repositori yang belum diverifikasi ulang ke artefak primer. **E0** = penilaian dan rekomendasi.

> **Putusan satu baris:** data dan infrastruktur berada pada kondisi terkuatnya — 92.074 kuadruplet dengan jejak audit — sementara **klaim kinerja berada pada kondisi terlemahnya**: Step-1 appsid ditarik karena *cache-hit*, Step-2 appsid baru 3 dari 15 epoch dengan metrik dua kepala bernilai nol, *cross-validation* 0 dari 94 run yang sah, dan naskah berstatus **major revision dengan tiga blocker**.

---

## 1. Sumber dan cara membaca laporan ini

| Berkas | Peran | Tingkat |
|---|---|---|
| `docs/0011_laporan_penelitian_acos_indobert_02112026.md` | Laporan penelitian 02/11; memuat dua catatan hasil Step-2 appsid | E1 |
| `docs/0012_laporan_penelitian_acos_indobert_03112026.md` | Survey artefak Drive 03/11; sumber klaim status per komponen | E1 |
| `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md` | Draf artikel SINTA 2 versi 02/11 | E1 |
| `reports/048_draft_artikel_sinta2_apps_acos_03112026.md` | Draf artikel versi 03/11, memakai angka interim | E1 |
| `reports/049_review_profesor_draft_artikel_sinta2_apps_acos_04112026_HM.md` | Review 16 temuan atas draf 048 | E0 untuk penilaian, E1 untuk temuannya |
| `docs/0013` | Sintesis literatur ACOS/ACOSE | E1 |
| `docs/0014` | Laporan kemajuan format LPPM UWG | E1 |
| Kode `Extract-Classify-ACOS/`, `notebooks/` | Bukti perilaku dan keluaran model | E2 |

**Aturan yang dipakai laporan ini:** bila dua dokumen saling bertentangan, keduanya dicatat dan **tidak ada yang dipilih diam-diam**. Penyelesaian hanya boleh dilakukan terhadap artefak primer (berkas keluaran, CSV, atau bobot), bukan terhadap laporan turunan. Aturan ini muncul karena review 049 temuan #15 menemukan dua laporan repositori memuat angka quadruple gold yang berbeda.

---

## 2. Kondisi data

| Butir | Nilai | Tingkat | Sumber |
|---|---:|---|---|
| Ulasan bersih | 43.673 (13 aplikasi bank digital) | E2 | `eda_044_appsid.py` |
| Klausa | 76.077 | E2 | sama |
| Kuadruplet | 92.074 | E2 | sama |
| Split latih / dev / uji (klausa) | 60.159 / 8.027 / 7.891 | E2 | `docs/0011` §3.2 |
| Split latih / dev / uji (tuple) | 72.973 / 9.587 / 9.514 | E2 | sama |
| Kategori / kelas sentimen | 13 / 3 | E2 | sama |

**Jembatan pasangan kandidat** (tahap 2) sudah terhitung dan terdokumentasi:

| Tipe pasangan | Jumlah | Persentase |
|---|---:|---:|
| Eksplisit–Implisit | 4.459 | 41,54% |
| Eksplisit–Eksplisit | 3.456 | 32,19% |
| Implisit–Eksplisit | 2.813 | 26,20% |
| Implisit–Implisit | 7 | 0,07% |
| **Total** | **10.735** | **100%** |

Angka 0,07% untuk implisit–implisit **bukan temuan linguistik**. Ia artefak mekanisme: pasangan dibentuk dari perkalian Cartesian span aspek dan span opini, sehingga kombinasi ketika keduanya tidak ber-span hampir tidak pernah terbentuk. Review 049 temuan #6 menandai kontradiksi ini dengan klaim abstrak "termasuk slot implisit"; sampai laporan ini disusun, penjelasan mekanismenya belum ditulis di naskah.

**Cacat data yang masih terbuka:**

| Cacat | Nilai | Status |
|---|---:|---|
| Baris uji berbagi teks dengan latih | 14,66% | Belum dideduplikasi |
| Istilah aspek unik | 362 | Kosakata tertutup |
| Istilah opini unik | 202 | Kosakata tertutup |
| Klausa opini memuat negasi | 16,68% | Belum dianalisis dampaknya |
| Verifikasi manusia atas label lemah | 0 dari 92.074 | Belum ada; κ belum diukur |

---

## 3. Kondisi hasil per komponen

| Komponen | Angka terkini | Tingkat | Kelayakan klaim |
|---|---:|---|---|
| Step-1 rest16 (BERT) | 81,27% micro-F1, epoch 8 dari 15 | E2 (`notebooks/02` sel 13) | **Dipakai** sebagai kontrol |
| Step-1 appsid (IndoBERT) | 97,94% micro-F1, 8 dari 15 epoch | E2 | **Ditolak sebagai kapabilitas** — *cache-hit* |
| Step-2 rest16 (BERT) | 48,24% F1, epoch 12 dari 15 | E2 (`notebooks/04` sel 12) | Dipakai sebagai kontrol, dengan catatan selisih tidak signifikan |
| Step-2 appsid sesi 05/09 | 3 epoch: 67,16 / 66,55 / **69,00** | E2 | **Batas bawah interim**, bukan hasil konvergen |
| Step-2 appsid sesi 09/01 | 67,69% (TP/FP/FN 6.681/4.052/2.325) | E1 | **Belum dapat dipakai** — lihat §4.1 |
| 15 sub-tugas | 91,08% → 66,08% (rest16, bukan appsid) | E2 | Berlaku hanya untuk rest16 |
| *Cross-validation* | 94 run, 93 ERROR, **0 skor sah** | E2 (`run_result.json`) | **Tidak boleh dikutip** |
| Gerbang bobot (Gate-1) | 199 dari 199 key, rerata identik | E2 | Lulus |
| Audit embedding | vocab 30.521 vs config 50.000; 25.992 span bergeser (14,12%) | E2 | Catatan teknis, bukan cacat baru |

**Dua catatan yang menentukan cara membaca tabel di atas.**

Pertama, **metrik dua kepala Step-2 bernilai nol permanen**. Pada sesi 05/09, kolom `category_micro_f1` dan `sentiment_acc` tercatat 0,0 di seluruh epoch maupun di berkas *resume*. Menurut survey 0012 ini bukan sekadar cacat tampilan, melainkan bug persistensi, sehingga **tidak ada bukti empiris bahwa kepala kategori dan sentimen belajar**. Konsekuensinya, angka F1 kuadruplet 69,00% hanya mengukur kepala pasangan.

Kedua, **angka 97,94% adalah *cache-hit*.** Angka ini muncul karena evaluasi memakai hasil yang sudah tersimpan, bukan inferensi baru; ia tetap beredar di abstrak `reports/035` dan belum disinkronkan meskipun sudah ditolak di `docs/0012`.

---

## 4. Kontradiksi yang belum diselesaikan

### 4.1 Dua catatan untuk satu hasil: Step-2 appsid

| Sumber | Angka | Dasar |
|---|---:|---|
| `docs/0011` baris 35 dan 187 (sesi `appsid_24092026_0901`) | **67,69** | TP/FP/FN 6.681/4.052/2.325 |
| `docs/0011` baris 185 (sesi 05/09) | **67,16** | TP 6.552 |
| `docs/0012` §4.2 dan `reports/048` Tabel 4 (sesi 05/09) | 67,16 / 66,55 / **69,00** | 3 epoch, epoch-3 TP/FP/FN 6.830/3.962/2.176 |

Tiga pembacaan yang mungkin, dan tidak satu pun dapat dipilih tanpa artefak primer:

1. Sesi 05/09 dan 09/01 adalah dua sesi berbeda; maka 67,69% masih berdiri sebagai hasil sesi lain, tetapi jumlah epoch dan status konvergensinya tidak diketahui.
2. Angka 67,69 adalah salah tulis dari 67,16; maka satu-satunya hasil Step-2 appsid adalah deret 3 epoch.
3. Angka 67,69 berasal dari artefak terpisah yang belum tercatat lengkap di repositori.

**Tindakan yang benar:** buka artefak `appsid_24092026_0901` di Drive, cocokkan amount TP/FP/FN, dan tetapkan satu angka. Sampai itu dilakukan, artikel **tidak boleh** memakai 67,69% sebagai hasil.

### 4.2 Jumlah quadruple gold kontrol

Review 049 temuan #15 mencatat `reports/048` menyebut **895** kuadruplet gold rest16, sementara `reports/033` mencatat **916**. Selisih 21 kuadruplet ini mengubah denominator metrik dan perhitungan galat baku pada klaim "+3,7 poin". Belum diselesaikan.

### 4.3 Angka baseline yang dikutip dua versi

| Sumber | Restaurant | Laptop |
|---|---:|---:|
| `docs/0013` mengutip catatan Drive | 44,61% | 35,80% |
| `docs/0013` mengutip sumber kedua | 44,52% | 35,48% |

Selisih 0,09 dan 0,32 poin belum dijelaskan. Karena klaim keunggulan rest16 dihitung terhadap angka ini (48,24 berbanding 44,52 atau 44,61), ketidakpastian kecil ini tetap harus ditutup sebelum submit.

### 4.4 Angka yang ditarik tetapi masih beredar

| Angka | Status | Masih muncul di |
|---|---|---|
| 97,94% (Step-1 appsid) | Ditolak — *cache-hit* | `reports/035` baris 21, 248, 304, 327, 360 |
| 67,86% (abstrak lama) | Digantikan 67,69 / 69,00 | `reports/035` baris 21, 258, 260, 368 |
| "1–3 poin" (dampak seleksi *checkpoint*) | Dikoreksi menjadi 0,07–0,56 poin | Sudah bersih di `045`, `042`, `046` |

---

## 5. Kesiapan publikasi

Penilaian `reports/042` menempatkan kesiapan pada **3,15 dari 10**, dengan perkiraan 5,5 untuk jurnal SINTA 2 dan 7,0 untuk Q2. Review 049 atas draf 048 memberi vonis **major revision — belum layak submit dalam kondisi sekarang**, dengan tiga blocker:

| # | Blocker | Akar masalah | Perbaikan |
|---|---|---|---|
| 1 | Klaim "sumber daya ACOS Indonesia pertama" | Negasi eksistensial tanpa protokol pencarian | Tambah subbagian dengan basis data, string kueri, tahun, kriteria inklusi; atau turunkan menjadi "sejauh penelusuran kami" |
| 2 | Nol verifikasi manusia atas 92.074 label lemah | Untuk *resource paper*, mutu label adalah produk utama | Anotasi acak 500 klausa oleh dua anotator; laporkan κ dan akurasi label lemah |
| 3 | Tidak ada pernyataan lisensi/izin redistribusi ulasan | ToS Google Play dan App Store membatasi redistribusi | Tulis kebijakan rilis: data mentah, atau hanya anotasi dan ID, atau ubah kerangka menjadi "metode konstruksi" |

Selain tiga blocker, review mencatat 13 temuan lain (mayor dan minor). Empat di antaranya berbiaya rendah dan berdampak besar:

| Temuan | Inti | Biaya |
|---|---|---|
| #5 | Sentimen hampir deterministik dari kategori (APP_PERFORMANCE 79,4% negatif, AUTH_ACCESS 78,5%, UI_UX 71,1% positif); belum ada baseline *majority-per-category* | 2–4 jam tanpa GPU |
| #7 | Angka utama dilaporkan sebelum deduplikasi 14,66%; perlu kolom F1 pada subset bersih | 3–5 jam, tanpa latih ulang |
| #4 | Klaim "+3,7 poin" dari satu seed; galat baku ≈ 1,66 poin sehingga belum layak disebut peningkatan | 3 seed, 3–6 jam GPU |
| #8 | Sitasi model *base-p1* salah; seharusnya Yulius et al., arXiv:2104.08191 | 30 menit |

---

## 6. Yang boleh dan tidak boleh diklaim sekarang

| Klaim | Status |
|---|---|
| Dataset 92.074 kuadruplet berbahasa Indonesia pada domain bank digital | **Boleh**, dengan kata "label lemah" |
| Pipeline dua tahap berjalan dan dapat direproduksi dari kode | **Boleh** |
| Step-1 rest16 81,27% sebagai kontrol internal | **Boleh**, dengan catatan seleksi *checkpoint* pada uji |
| Step-2 appsid 69,00% | **Sebatas batas bawah interim** 3 dari 15 epoch |
| Step-2 appsid 67,69% | **Tidak boleh** sampai artefak sesi 09/01 diverifikasi |
| Step-1 appsid 97,94% | **Tidak boleh**, *cache-hit* |
| Skor *cross-validation* | **Tidak boleh**, 0 dari 94 run sah |
| State of the art, atau mengungguli baseline secara signifikan | **Tidak boleh**, selisih berada dalam galat baku |
| "Sumber daya pertama" sebagai fakta | **Tidak boleh** tanpa protokol pencarian |

---

## 7. Rencana kerja berdasarkan kondisi ini

| Prioritas | Tindakan | Prasyarat | Alasan |
|---|---|---|---|
| P0 | Verifikasi artefak sesi `appsid_24092026_0901` dan tetapkan satu angka Step-2 | Akses Drive | Menutup kontradiksi §4.1 |
| P0 | Perbaiki seleksi *checkpoint*: dev di dalam siklus, uji sekali di akhir | GPU | Pelanggaran protokol, apa pun besarnya dampak |
| P0 | Hitung metrik pada subset uji bersih setelah deduplikasi | Tanpa GPU | Menjawab temuan #7 |
| P0 | Anotasi 500 klausa oleh dua anotator, laporkan κ | Anotator | Blocker #2 |
| P1 | Baseline *majority-per-category* | Tanpa GPU | Menjawab temuan #5, menentukan apakah 69,00% bermakna |
| P1 | Tiga seed pada Step-1 rest16 dan Step-2 rest16 | GPU | Menjawab temuan #4 |
| P1 | Perbaiki bug persistensi metrik dua kepala Step-2 | GPU | Tanpa itu, klaim kepala kategori dan sentimen tidak punya dasar |
| P2 | Protokol pencarian literatur dan pernyataan lisensi | Tanpa GPU | Blocker #1 dan #3 |
| P2 | Sinkronkan abstrak `reports/035` | Tanpa GPU | Menghapus angka yang sudah ditolak |

---

## 8. Batasan laporan ini

1. **Laporan ini disusun dari dokumen, bukan dari artefak primer Drive.** Angka Step-2 appsid, *cross-validation*, dan audit embedding dikutip dari `docs/0012` yang menyatakan telah memverifikasi artefak tersebut; verifikasi ulang belum dilakukan dalam penyusunan laporan ini.
2. **Tidak ada pelatihan ulang atau inferensi baru.** Seluruh angka berasal dari keluaran tersimpan.
3. **Belum ada pemeriksaan independen** atas klaim bahwa 97,94% adalah *cache-hit*; laporan ini meneruskannya dari 0012 dan 040 tanpa menguji ulang mekanismenya.
4. **Kontradiksi di §4 sengaja dibiarkan terbuka.** Menutupnya dengan memilih salah satu angka akan mengulang kesalahan yang justru dikritik review 049.
5. **Tanggal dokumen** mengikuti commit terakhir `main` (`cee6893`) dan berkas terbaru di repositori, bukan tanggal penyusunan di luar repositori.

---

## 9. Rujukan internal

1. `docs/0011_laporan_penelitian_acos_indobert_02112026.md`
2. `docs/0012_laporan_penelitian_acos_indobert_03112026.md`
3. `docs/0013_laporan_penelitian_literatur_acos_acose_indobert_03112026.md`
4. `docs/0014_laporan_kemajuan_penelitian_lppm_uwg_03112026.md`
5. `reports/042_kesiapan_publikasi_q2_s2_02112026_HM.md`
6. `reports/044_eda_appsid_dan_hasil_02112026_HM.md`
7. `reports/045_artikel_ilmiah_sinta2_acos_indobert_02112026_HM.md`
8. `reports/046_verifikasi_jalur_a_02112026_HM.md`
9. `reports/048_draft_artikel_sinta2_apps_acos_03112026.md`
10. `reports/049_review_profesor_draft_artikel_sinta2_apps_acos_04112026_HM.md`
