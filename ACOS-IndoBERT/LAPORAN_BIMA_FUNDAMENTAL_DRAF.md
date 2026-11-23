# Draf substansi laporan akhir penelitian — BIMA penelitian fundamental

**Status: draf kerja, belum template resmi siap unggah.** Susunan A–H diadaptasi dari contoh laporan BIMA penelitian fundamental dan panduan pelaporan yang tersedia secara publik, bukan berkas template dari akun ketua. Tahun pendanaan, nomor kontrak, proposal disetujui, dan template yang diunduh dari BIMA masih diperlukan. Jangan menghapus atau mengubah instruksi dalam template resmi ketika memindahkan isi ini. Data dalam kurung siku harus dilengkapi, bukan dianggap fakta.

## Identitas penelitian (untuk dicocokkan dengan data BIMA)

| Isian | Keterangan |
|---|---|
| Judul penelitian sesuai kontrak | [Belum tersedia; judul kerja: ekstraksi ACOS pada ulasan aplikasi bank digital menggunakan IndoBERT] |
| Skema dan tahun pendanaan | [Penelitian fundamental — rincian skema dan tahun perlu dikonfirmasi] |
| Tahun pelaksanaan | [Tahun ke-… dari …] |
| Ketua, anggota, NIDN/NIM, institusi | [Belum tersedia] |
| Nomor kontrak dan sumber dana | [Belum tersedia] |
| Target dan capaian TKT | [Sesuai proposal dan bukti penilaian; belum tersedia] |
| Mitra | [Belum diketahui; isi bila ada] |

## A. Ringkasan

Penelitian ini mengadaptasi pipeline *Aspect–Category–Opinion–Sentiment* (ACOS) dua tahap untuk ulasan aplikasi bank digital berbahasa Indonesia menggunakan IndoBERT. Data ACOS dibentuk pada tingkat klausa dari anotasi lemah. Laporan pembangunan data mencatat 76.077 baris dan 92.074 quadruple pada split train, dev, dan test. Catatan tokenisasi menunjukkan tidak ada span invalid atau tuple yang hilang pada ketiga split. Ini adalah hasil persiapan data, bukan ukuran akurasi model. Laporan terdahulu juga mencatat hasil pelatihan sementara dan sejumlah masalah evaluasi; karena log dan prediksi aslinya tidak tersedia dalam checkout ini, angka tersebut belum dapat disahkan sebagai hasil akhir. Kesimpulan penelitian dibatasi pada pembangunan dan audit pipeline, bukan klaim keunggulan atau kinerja generalisasi IndoBERT.

Target luaran dan target/capaian TKT: [isi sesuai proposal dan bukti yang sah; belum tersedia].

## B. Kata kunci

ACOS; IndoBERT; analisis sentimen berbasis aspek; anotasi lemah; bank digital.

## C. Hasil pelaksanaan penelitian

### C.1 Konteks, pertanyaan dan tujuan

Ulasan aplikasi dapat memuat beberapa aspek dan opini dengan sentimen yang berbeda. Klasifikasi satu sentimen untuk seluruh ulasan tidak mempertahankan hubungan antara aspek, kategori, opini, dan sentimen. ACOS memodelkan hubungan tersebut sebagai quadruple `(aspek, kategori, opini, sentimen)`, termasuk slot aspek atau opini implisit. Penelitian ini mengadaptasi pendekatan ekstraksi–klasifikasi untuk data berbahasa Indonesia dan memeriksa kesiapan data serta evaluasinya.

**Pertanyaan penelitian:** (1) Bagaimana menyiapkan korpus klausa beranotasi lemah untuk ACOS? (2) Bagaimana pipeline IndoBERT dua tahap diimplementasikan dan diverifikasi? (3) Apa yang dapat disimpulkan dari bukti hasil yang tersedia? Pertanyaan ketiga belum dapat dijawab sebagai estimasi performa final tanpa artefak evaluasi yang valid.

**Kontribusi yang dapat ditelusuri:** konversi korpus ke format quadruple, adaptasi pipeline dan tokenisasi IndoBERT, serta identifikasi risiko evaluasi. Kebaruan ilmiah dan keunggulan atas metode lain belum dibuktikan.

### C.2 Metode dan tahapan

### 2.1 Data dan unit analisis

Sumber data yang didokumentasikan adalah ulasan aplikasi bank digital Indonesia. `processed/quintuples_weak.csv` memuat anotasi lemah; label bukan gold standard anotasi manusia. Satu baris data ACOS merupakan **klausa**, bukan ulasan. Split didokumentasikan berdasarkan `review_id` untuk mencegah satu ulasan yang sama masuk ke beberapa split ([README](001_README_04092026_1413.md); [laporan konversi](../reports/023_pipeline_acos_indobert_dataset_indonesia_04092026.md)). Laporan konversi mencatat 4.183 klausa dibuang karena ID ulasan tidak ditemukan pada split yang digunakan; mekanisme dan dampak eksklusinya perlu diaudit sebelum generalisasi.

Terdapat 13 kategori dan tiga sentimen sehingga konfigurasi kategori–sentimen mempunyai 39 kombinasi. Rincian taksonomi tersedia di [`label_maps.json`](data/Apps-ACOS/processed/label_maps.json). Hasil terhadap label lemah mengukur kesesuaian dengan proses anotasi tersebut, bukan otomatis ketepatan terhadap penilaian manusia.

### 2.2 Pipeline

```text
Ulasan → normalisasi / anotasi lemah → klausa dan quadruple
       → pemisahan berdasarkan review_id → tokenisasi IndoBERT
       → Step 1: ekstraksi kandidat aspek dan opini
       → Step 2: klasifikasi kategori dan sentimen → quadruple prediksi
```

Implementasi dan versi notebook tersedia di [`acos_id/`](acos_id/) dan [`notebooks/`](notebooks/). Desain dua tahap beserta alternatif *dual-head* dijelaskan dalam [laporan arsitektur](../reports/027_analisis_arsitektur_pipeline_acos_dualhead_step2_09092026.md). Versi, konfigurasi, pembentukan kandidat, penanganan slot implisit, dan checkpoint harus diambil dari manifest run yang benar-benar dievaluasi; jangan menganggap seluruh notebook memakai konfigurasi identik.

### 2.3 Evaluasi yang diperlukan

Untuk pencocokan quadruple eksak, hitung precision = TP/(TP+FP), recall = TP/(TP+FN), dan F1 = 2PR/(P+R), dengan definisi kecocokan dan agregasi ditentukan sebelum pengujian. Gunakan dev untuk pemilihan checkpoint dan hyperparameter; test hanya untuk evaluasi akhir. Simpan prediksi, gold, skrip evaluator, konfigurasi, seed, versi kode dan data, serta checkpoint. Laporkan juga per kategori/sentimen, eksplisit–implisit dan subset tanpa duplikasi teks. CV dan ablasi perlu menyertakan hasil setiap fold/run dan variasinya; adanya berkas split saja bukan bukti eksperimen selesai.

### C.3 Hasil persiapan data

### 3.1 Komposisi split

| Split | Klausa/baris | Quadruple | Aspek eksplisit | Opini eksplisit |
|---|---:|---:|---:|---:|
| Train | 60.159 | 72.973 | 51.184 | 43.271 |
| Dev | 8.027 | 9.587 | 6.588 | 5.836 |
| Test | 7.891 | 9.514 | 6.576 | 5.693 |
| **Total** | **76.077** | **92.074** | **64.348** | **54.800** |

Sumber: [`_build_acos_report.json`](data/Apps-ACOS/_build_acos_report.json) dan [README](001_README_04092026_1413.md). Dari total quadruple, laporan build mencatat 27.726 aspek dan 37.274 opini implisit. Denominator adalah quadruple, bukan jumlah ulasan unik. Baris dev disebut `val` pada sebagian berkas sumber.

**Gambar 1. Komposisi quadruple per split** (panjang batang dibulatkan; sumber laporan build).

```text
Train  72.973  ████████████████████████████████
Dev     9.587  ████
Test    9.514  ████
```

### 3.2 Tokenisasi dan verifikasi

[`_build_report_appsid.json`](tokenized_data/_build_report_appsid.json) mencatat 72.973/9.587/9.514 quadruple train/dev/test setelah tokenisasi, `span_invalid = 0` dan `unk_disisipkan = 0` pada masing-masing split. Ini adalah keluaran proses yang direkam, bukan verifikasi independen bahwa seluruh label benar. README melaporkan lima gate *torch-free* berhasil pada saat terdokumentasi; gate bobot encoder memerlukan pembuktian pada run aktual. Audit lama atas hasil eksperimen melaporkan bukti gate yang tersimpan belum lengkap. Oleh karena itu kedua catatan tersebut tidak membuktikan gate bobot lulus pada run yang akan dilaporkan.

### C.4 Hasil model dan pembahasan

**Hasil final: belum dapat ditetapkan.** Folder `results/` tidak terdapat dalam checkout ini dan memang dikecualikan dari Git oleh [`.gitignore`](.gitignore). Ketiadaan lokal tidak membuktikan hasil tersebut tidak ada di penyimpanan lain.

Sebagai petunjuk historis, [draft artikel 052](../reports/052_draft_artikel_ijacsa_pipeline_dua_tahap_acos_12112026_HM.md) melaporkan F1 Step 2 sebesar 69,00 pada epoch 3 dari 15 untuk satu sesi Indonesia; laporan yang sama menandai ketidaksesuaian evaluator dan persoalan pemilihan checkpoint menggunakan test. Angka ini **sementara, bersumber sekunder, belum diverifikasi dari prediksi dan log asli, serta bukan hasil final atau batas bawah kinerja final**. Laporan itu juga mencabut angka Step 1 97,94 karena *cache hit*. [Audit 038](../reports/038_analisis_kritis_hasil_folder_results_indobert_02112026.md) melaporkan 94 folder run CV yang diperiksa pada lokasi asal tanpa run selesai berstatus OK; ini temuan audit historis pada lokasi dan waktu tersebut, bukan hasil pemeriksaan langsung atas run saat ini.

Perbandingan IndoBERT pada Apps-ACOS dengan BERT pada Rest16 tidak mengisolasi pengaruh backbone karena bahasa dan dataset berbeda. Tidak ada dasar dari bukti yang tersedia untuk menyatakan IndoBERT lebih unggul, atau bahwa CV/ablasi telah membuktikan peningkatan.

### C.5 Kesimpulan sementara

Artefak yang tersedia mendukung bahwa korpus quadruple dan pipeline Indonesia telah disiapkan serta sejumlah pemeriksaan integritas data telah didokumentasikan. Bukti saat ini belum memadai untuk menetapkan performa akhir model, efektivitas metode, maupun keunggulan IndoBERT. Laporan akhir substantif memerlukan validasi anotasi dan eksekusi ulang atau audit lengkap terhadap artefak eksperimen yang sah.

**Kesesuaian dengan tahapan proposal:** [Bandingkan setiap capaian di atas dengan proposal dan jadwal yang disetujui setelah dokumen tersedia.]

## D. Status luaran

| Jenis | Target sesuai proposal | Status aktual | Bukti/tautan |
|---|---|---|---|
| Luaran wajib | [Belum tersedia] | [Belum terverifikasi] | [Belum tersedia] |
| Luaran tambahan, jika ada | [Belum tersedia] | [Belum terverifikasi] | [Belum tersedia] |

Naskah di repositori merupakan draf; keberadaannya saja tidak membuktikan status submit, accepted, atau published. Isi tabel dan unggah bukti sesuai ketentuan akun BIMA.

## E. Peran mitra

[Belum diketahui apakah ada mitra. Jika ada, isi nama, peran, kontribusi dan bukti pelaksanaan sesuai proposal; jika tidak ada, nyatakan setelah dikonfirmasi. Kewajiban bagian ini mengikuti template skema dan tahun yang berlaku.]

## F. Kendala pelaksanaan penelitian

| Prioritas | Masalah dan akar | Tindakan konkret |
|---|---|---|
| BLOCKER | Log, checkpoint, prediksi dan evaluator run final tidak tersedia di checkout; angka historis tidak dapat direproduksi. | Kumpulkan artefak sesi asli, cocokkan hash/konfigurasi dan hitung ulang metrik dari prediksi serta gold. |
| BLOCKER | Audit sebelumnya mencatat evaluasi tidak konsisten, cache dan pemilihan checkpoint dengan test. | Pisahkan cache per run, gunakan satu evaluator terdokumentasi, pilih checkpoint dengan dev dan evaluasi test sekali setelah konfigurasi dibekukan. |
| MAYOR | Anotasi lemah berisiko mewariskan pola pelabel otomatis. | Buat sampel anotasi manusia independen, ukur kesepakatan dan kualitas label, lalu evaluasi pada gold manusia. |
| MAYOR | README melaporkan teks klausa pendek berulang lintas split meskipun review ID terpisah: 14,7% baris test berbagi teks dengan train. | Audit overlap pada data versi final dan laporkan metrik pada test penuh dan subset tanpa overlap. |
| MAYOR | Belum ada bukti lokal hasil CV, beberapa seed, baseline sebanding atau ablasi valid. | Jalankan baseline sederhana dan baseline kuat pada split/evaluator sama; laporkan tiap fold/seed serta mean dan simpangan baku; ablasikan komponen relevan. |
| MAYOR | 4.183 klausa tidak ikut split pada konversi. | Telusuri penyebab ID tidak cocok dan distribusi kategori/sentimennya; laporkan dampak eksklusi. |
| MINOR | Metadata penelitian dan konfigurasi eksperimen final belum tersedia. | Lengkapi identitas, sumber dan periode data, izin/etika, versi perangkat lunak, perangkat keras, hyperparameter, dan template institusi. |

Hubungan kendala dengan target dan jadwal kontrak [belum dapat dinilai tanpa proposal serta logbook]. Tabel di atas mencatat kendala verifikasi berbasis bukti yang tersedia, bukan pernyataan tentang penggunaan dana atau keseluruhan pelaksanaan hibah.

## G. Rencana tahapan selanjutnya

1. Cocokkan dokumen proposal, tahun pelaksanaan, target luaran dan kontrak dengan data BIMA.
2. Kumpulkan artefak primer dan verifikasi gate bobot, konfigurasi, split, evaluator serta prediksi; lakukan evaluasi ulang sesuai protokol dev/test.
3. Lakukan audit anotasi manusia, overlap dan perbandingan baseline/ablasi yang layak.
4. Susun luaran sesuai target yang disetujui, dokumentasikan status dan unggah bukti.
5. Lengkapi jadwal, penanggung jawab dan roadmap berdasarkan proposal: [belum tersedia].

## H. Daftar pustaka

[Belum lengkap. Masukkan hanya pustaka primer yang benar-benar disitasi dalam teks, dengan penomoran sesuai urutan sitasi dan metadata yang diverifikasi. Sumber internal berikut adalah jejak audit, bukan pengganti daftar pustaka ilmiah.]

### Jejak sumber internal (catatan kerja; pindahkan atau hapus sesuai template resmi)

1. [README ACOS-IndoBERT](001_README_04092026_1413.md) — desain, statistik dan keterbatasan data.
2. [Laporan build dataset](data/Apps-ACOS/_build_acos_report.json) dan [laporan tokenisasi](tokenized_data/_build_report_appsid.json) — angka persiapan data.
3. [Laporan pipeline 023](../reports/023_pipeline_acos_indobert_dataset_indonesia_04092026.md) — konteks konversi dan gate pada saat penulisan.
4. [Audit hasil 038](../reports/038_analisis_kritis_hasil_folder_results_indobert_02112026.md) — audit historis run, termasuk koreksi jumlah folder.
5. [Draf artikel 052](../reports/052_draft_artikel_ijacsa_pipeline_dua_tahap_acos_12112026_HM.md) — angka sementara dan ancaman evaluasi; bukan pengganti artefak primer.
6. [Indeks referensi](REFERENCES/INDEX_REFERENCES.md) — kandidat literatur; metadata dan isi sumber primer harus diverifikasi sebelum menyusun daftar pustaka final.

### Acuan format yang digunakan (catatan kerja)

- Contoh laporan BIMA skema Fundamental Reguler 2025: https://repo-dosen.ulm.ac.id/bitstream/handle/123456789/37036/Laporan_Pengembangan%20Model%20Konseptual%20Pengintegrasian%20Teknologi%20pada%20Platform%20Tech4TPD%20untuk%20Mendukung%20Pengembangan%20Keprofesian%20Guru%20secara%20Berkelanjutan.pdf?sequence=1&isAllowed=y
- Panduan unggah laporan BIMA 2023: https://lldikti6.id/wp-content/uploads/2023/09/20230908_Revisi-Lampiran-I-Panduan-Mengunggah-Laporan-Kemajuan-dan-SPTB-Penelitian-PTV-Melalui-BIMA.pdf
- Contoh cover 2025 dari perguruan tinggi menyatakan isi laporan akhir diunduh dari akun BIMA ketua: https://konten.usu.ac.id/storage/year/2025-12/posts/51/announcement/Cover%20Laporan%20Akhir%20DPPM%202025.pdf

Ketiga sumber di atas merupakan rujukan kontekstual, bukan jaminan kesesuaian tahun pendanaan pengguna. Ikuti template yang dihasilkan sistem dan arahan LPPM untuk format, sampul, pengesahan, lampiran dan unggahan.
