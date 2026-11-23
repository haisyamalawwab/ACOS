# Survei dan analisis proyeksi statistik AppsID pada tabel ACOS

**Tanggal:** 22 November 2026. **Status:** analisis deskriptif yang dapat direproduksi, bukan hasil ablasi pelatihan model. Sumber tabel pengguna: [`img/stat.PNG`](../img/stat.PNG), salinan dalam repositori dari [gambar yang ditautkan](https://raw.githubusercontent.com/rozanhaisyam/ACOS/main/img/stat.PNG). Tabel aslinya juga muncul pada [Cai dkk., ACL 2021](https://aclanthology.org/2021.acl-long.29/). Hitungan AppsID dihitung dari TSV yang ada di checkout; bukan dikutip dari gambar.

## 1. Tabel yang ditambah AppsID

Angka dataset selain AppsID ditranskripsi dari gambar dan **tidak dihitung ulang seluruhnya**. Nilai AppsID memakai himpunan proyeksi unik **per baris** untuk train + dev + test, termasuk representasi `-1,-1` sebagai satu nilai NULL. Kolom Sentence untuk AppsID adalah jumlah **baris klausa**, bukan jumlah kalimat atau ulasan; diberi tanda † agar perbedaannya tidak tersembunyi. Kolom Sentiment ditandai `?` karena konvensi pada tabel asli belum dapat direkonstruksi secara meyakinkan. Angka 76.606 adalah alternatif jumlah label sentimen unik per baris, **bukan** angka yang terbukti sebanding dengan kolom tersebut.

| Dataset | Sentence | Aspect | Category | Opinion | Sentiment | AS Pair | AO Pair | AOS Triple | ACS Triple | ACOS Quadruple | Sumber dataset |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Restaurant-2014 | 3.841 | 4.827 | 4.738 | – | 4.534 | 4.827 | – | – | – | –  [Pontiki dkk., 2014](https://aclanthology.org/S14-2004/) |
| Laptop-2014 | 1.910 | 3.012 | – | – | 3.012 | 3.012 | – | – | – | –  [Pontiki dkk., 2014](https://aclanthology.org/S14-2004/) |
| Restaurant-2016 | 2.295 | 3.122 | 3.001 | – | 3.122 | 3.182 | – | – | 3.364 | –  [Pontiki dkk., 2016](https://aclanthology.org/S16-1002/) |
| Laptop-2016 | 2.612 | – | 3.705 | – | 3.705 | – | – | – | – | –  [Pontiki dkk., 2016](https://aclanthology.org/S16-1002/) |
| Restaurant-2014-AO | 2.125 | 3.503 | – | 3.610 | – | – | 4.092 | – | – | –  [Fan dkk., 2019](https://aclanthology.org/N19-1259/) |
| Restaurant-2016-AO | 1.407 | 1.968 | – | 2.146 | – | – | 2.294 | – | – | –  [Fan dkk., 2019](https://aclanthology.org/N19-1259/) |
| Restaurant-2014-AOS | 2.068 | 3.399 | – | 3.443 | 3.399 | 3.399 | 3.908 | 3.908 | – | –  [Xu dkk., 2020](https://aclanthology.org/2020.emnlp-main.183/) |
| Restaurant-2016-AOS | 1.393 | 1.946 | – | 2.101 | 1.946 | 1.946 | 2.247 | 2.247 | – | –  [Xu dkk., 2020](https://aclanthology.org/2020.emnlp-main.183/) |
| Restaurant-ACOS | 2.286 | 3.110 | 2.967 | 3.335 | 3.110 | 3.155 | 3.571 | 3.575 | 3.335 | 3.658  [Cai dkk., 2021](https://aclanthology.org/2021.acl-long.29/) |
| Laptop-ACOS | 4.076 | 4.958 | 4.992 | 5.378 | 4.958 | 5.035 | 5.726 | 5.731 | 5.227 | 5.758  [Cai dkk., 2021](https://aclanthology.org/2021.acl-long.29/) |
| **AppsID / Apps-ACOS** | **76.077†** | **91.995** | **86.512** | **84.071** | **?** | **92.074** | **92.070** | **92.074** | **92.074** | **92.074**  [TSV repositori](../ACOS-IndoBERT/data/Apps-ACOS/) |

Sumber angka semua baris selain AppsID adalah gambar/tabel Cai dkk. yang ditranskripsi; kolom sumber dataset menunjukkan referensi asal dataset, bukan klaim bahwa statistik ini diperiksa ulang di setiap sumber primer. Angka AppsID dihitung dari TSV dengan [skrip](../scripts/statistik_acos_projection.py).

† Unit AppsID adalah baris klausa berlabel lemah hasil konversi, bukan review. Hitungan aspect/opinion di atas mencakup NULL per baris, bukan semata jumlah span eksplisit. Nama AppsID adalah domain pipeline dari dataset Apps-ACOS; ini bukan klaim bahwa dataset lain di gambar mempunyai anotasi atau unit setara. `?` berarti belum diverifikasi, sedangkan `–` mempertahankan tanda tak tersedia pada gambar.

## 2. Definisi dan reproduksi

Input: [`appsid_quad_train.tsv`](../ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_train.tsv), [`dev`](../ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_dev.tsv), [`test`](../ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_test.tsv). Masing-masing kolom setelah teks berisi `(rentang aspek, kategori, sentimen, rentang opini)`; urutan struktur dalam laporan ditulis A, C, O, S. Untuk setiap baris, proyeksikan tuple ke subset kolom yang dipilih, hapus duplikat dalam baris, lalu jumlahkan antarb​aris dan split. Baris yang teksnya sama tetapi muncul sebagai rekaman terpisah tetap dihitung terpisah; span berupa indeks token, bukan kata unik global. Jumlah raw quadruple juga ditampilkan terpisah. Skrip tidak memuat data eksternal dan tidak melatih model:

```bash
python scripts/statistik_acos_projection.py
```

Hasil semua split, kontrol dan subset: [`055_estadistik_acos_projection.csv`](055_estadistik_acos_projection.csv). Perbandingan dengan [`_build_acos_report.json`](../ACOS-IndoBERT/data/Apps-ACOS/_build_acos_report.json) cocok pada 60.159/8.027/7.891 baris, 72.973/9.587/9.514 quadruple, serta total aspek eksplisit 64.348 dan opini eksplisit 54.800. Laporan build dan TSV merupakan artefak pipeline yang berkaitan, sehingga kecocokan ini **bukan validasi anotasi independen**.

## 3. Kontrol terhadap tabel asli

Skrip juga memproses `data/Restaurant-ACOS/rest16_quad_{train,dev,test}.tsv` dan `data/Laptop-ACOS/laptop_quad_{train,dev,test}.tsv`. Pada Restaurant, proyeksi A, C, O, AS, AO, AOS, ACS dan ACOS seluruhnya mereproduksi delapan angka gambar. Pada Laptop, tujuh kolom selain C cocok; category yang dihitung 4.991 sementara gambar menyebut 4.992. Penyebab selisih belum diidentifikasi; bisa berkaitan dengan definisi, sumber atau versi, tetapi belum boleh disimpulkan. Restaurant mempunyai 2.284 baris TSV sementara gambar menyebut 2.286 kalimat; penyebab juga belum diverifikasi. Laptop memiliki 4.076 baris, cocok.

Kolom sentiment tabel asli adalah 3.110/4.958 untuk Restaurant/Laptop; jumlah label sentimen unik per baris dalam TSV adalah 2.462/4.283. Karena tidak cocok, angka 76.606 pada AppsID tidak dimasukkan seolah-olah identik definisinya. Sentimen per quadruple mentah AppsID berjumlah 92.074, namun ini juga **bukan** pembuktian konvensi tabel asli. Perlu sumber kode/metode penghitungan penulis, atau konfirmasi eksplisit konvensi, sebelum mengisi sel tersebut.

TSV Restaurant memiliki 3.661 quadruple mentah tetapi 3.658 unik per baris; Laptop memiliki 5.773 mentah dan 5.758 unik. Ini mendukung penggunaan deduplikasi per baris untuk kolom struktur, tetapi kesesuaian sebagian kolom tidak membuktikan kesetaraan penuh definisi.

## 4. Ablasi deskriptif: sensitivitas statistik terhadap slot implisit

Ini adalah **analisis subset dan proyeksi**, bukan ablasi model: tidak ada model yang dilatih ulang, tidak ada dampak F1 atau hubungan sebab-akibat yang dapat disimpulkan. Pada AppsID tidak ada quadruple mentah duplikat per baris, sehingga jumlah mentah dan unik sama. IA/IO berarti aspek/opini direpresentasikan sebagai NULL.

| Subset AppsID | Train | Dev | Test | Total | Pangsa total quadruple |
|---|---:|---:|---:|---:|---:|
| Aspek eksplisit, opini eksplisit | 21.482 | 2.837 | 2.755 | 27.074 | 29,4% |
| Aspek eksplisit, opini implisit | 29.702 | 3.751 | 3.821 | 37.274 | 40,5% |
| Aspek implisit, opini eksplisit | 21.789 | 2.999 | 2.938 | 27.726 | 30,1% |
| Keduanya implisit | 0 | 0 | 0 | 0 | 0,0% |
| **Seluruhnya** | **72.973** | **9.587** | **9.514** | **92.074** | **100,0%** |

Menonaktifkan slot implisit **sebagai filter data**, bukan melatih ulang sistem, menyisakan 27.074 quadruple (29,4%) dan 27.070 pasangan AO unik per baris; dibandingkan 92.074 quadruple dan 92.070 AO pada data penuh. Ini menunjukkan besarnya perubahan cakupan evaluasi jika NULL dikeluarkan. Nol ganda-implisit merupakan properti representasi berkas hasil konversi, bukan bukti bahwa teks aslinya tidak mengandung kasus tersebut.

Menjatuhkan kategori dan/atau opini juga menghasilkan AS = ACS = AOS = ACOS = 92.074. Dengan definisi per baris ini, proyeksi tersebut tidak menggabungkan quadruple AppsID yang berbeda; hal tersebut adalah **struktur korpus dan hasil prapemrosesan**, bukan bukti bahwa salah satu komponen tidak diperlukan untuk prediksi. AO = 92.070, empat lebih sedikit, karena empat proyeksi AO per baris bergabung. Selisih dan kesetaraan tersebut tidak bisa dipakai sebagai ablasi performa.

## 5. Interpretasi, keterbatasan dan langkah berikutnya

- [README AppsID](../ACOS-IndoBERT/001_README_04092026_1413.md) menyebut anotasi lemah, pemisahan berdasarkan `review_id`, serta duplikasi teks klausa pendek lintas split. Ukuran besar AppsID tidak membuktikan kualitas label setara benchmark beranotasi manusia; ukuran klausa dan review tidak dapat dibandingkan langsung dengan kalimat benchmark.
- [Audit hasil 038](038_analisis_kritis_hasil_folder_results_indobert_02112026.md) melaporkan kegagalan run CV pada artefak historis; [draf 052](052_draft_artikel_ijacsa_pipeline_dua_tahap_acos_12112026_HM.md) mencatat hasil sementara dan masalah evaluator. Hitungan tabel di atas tidak memvalidasi kinerja model.
- [Studi baseline dan ablasi terdahulu](053_draft_artikel_khazanah_determinisme_sentimen_12112026_HM.md) membahas prediksi mayoritas kategori dan subset overlap; itu analisis berbeda dan tetap menggunakan label lemah. Tidak ada angka F1 atau keunggulan model yang disimpulkan dari tabel ini.
- Sebelum publikasi: verifikasi sumber metode tabel dan dua selisih kontrol; tambahkan audit anotasi manusia; pertahankan penanda unit dan definisi NULL. Untuk **ablasi model** yang sesungguhnya, tetapkan split, evaluator, konfigurasi dan seeds; latih ulang varian dengan/ tanpa komponen yang diuji, bandingkan pada test yang sama, lalu laporkan F1, variabilitas dan batasan. Jangan mengisi hasil yang belum dijalankan.
