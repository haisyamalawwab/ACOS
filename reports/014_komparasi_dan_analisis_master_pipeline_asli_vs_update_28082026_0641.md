# Komparasi & Analisis Mendalam Master Pipeline ACOS: Versi ASLI vs. UPDATE

**Tanggal:** 2026-08-28 06:41 WIB  
**Objek Perbandingan:**  
1. `notebooks/00_ACOS_Master_Pipeline_Colab_ASLI.ipynb` (24 sel, 1.25 MB)  
2. `notebooks/00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb` (25 sel, 1.81 MB)  

---

## 1. Ringkasan Eksekutif Komparasi

Telah dilakukan perbandingan komprehensif *cell-by-cell diff* antara berkas **`ASLI`** dan **`UPDATE`**. Versi **`UPDATE`** membawa peningkatan penting terkait ketahanan eksekusi terhadap *runtime disconnect*, perbaikan parameter pemanggilan EDA, serta penambahan sel diagnostik pelacakan direktori dataset dan *tokenized_data*.

---

## 2. Tabel Matriks Perubahan Antar Sel

| No | Tipe Sel | Versi ASLI | Versi UPDATE | Analisis Perubahan & Fungsi |
| :---: | :---: | :--- | :--- | :--- |
| **0** | Markdown | Badge "Open In Colab" terpisah. | Judul Utama + Ringkasan 9 Tahap terintegrasi. | Menggabungkan *header* agar lebih rapi dan bersih. |
| **1–2** | Code | Inisialisasi Drive & Dependensi. | Inisialisasi Drive & Dependensi. | **Identik:** Mount Drive via `try...except`, install packages, setup `torch.device`. |
| **3–4** | Code | Path resolution & import `colab_utils`. | Path resolution & import `colab_utils`. | **Identik:** Deteksi bertingkat direktori repo dan *fallback download*. |
| **5–6** | Code | Konfigurasi hyperparameter & BERT cache. | Konfigurasi hyperparameter & BERT cache. | **Identik:** `DOMAIN = "rest16"`, `EPOCHS = 15`, init timestamped folder. |
| **7–8** | Code | EDA dengan `data_dir=base_project_dir`. | EDA dengan `data_dir=data_root` (`os.path.join(base_project_dir, "data")`). | **Disesuaikan:** Parameter `data_dir` lebih presisi mengarah langsung ke folder `data/`. |
| **9** | Code | *(Belum ada)* | **BARU:** Diagnostik pencarian dataset di `/content/drive/MyDrive/ACOS`. | Melacak lokasi folder `Restaurant-ACOS`, `Laptop-ACOS`, dan `tokenized_data`. |
| **10** | Code | *(Belum ada)* | **BARU:** Multi-path search dataset di `/content` & `/content/drive/MyDrive`. | Memastikan file dataset terbaca sebelum proses training berjalan. |
| **11–12** | Code | Step 1 (BERT-CRF) Training & Checkpointing. | Step 1 (BERT-CRF) Training & Checkpointing. | **Identik:** Melatih model `BertForQuadABSA`, simpan checkpoint ke `checkpoints/step1_best/`. |
| **13** | Code | *(Belum ada)* | **BARU:** State Checkpoint Saver (`pipeline_state.pkl`). | Menyimpan variabel state (`DOMAIN`, `session_dirs`, `device`, dll.) ke berkas pickle. |
| **14** | Code | *(Belum ada)* | **BARU:** State Recovery Loader dari Pickle. | Memulihkan variabel state jika kernel Google Colab terputus / *restart*. |
| **15–16** | Code | Candidate Pair Generation Bridge. | Candidate Pair Generation Bridge. | **Identik:** Membaca `pred4pipeline.txt`, membangun pasangan kartesian $(a, o)$. |
| **17–18** | Code | Step 2 (Category-Sentiment Classification). | Step 2 (Category-Sentiment Classification). | **Identik:** Melatih model `CategorySentiClassification`, monkey-patch tokenizer debug. |
| **19–20** | Code | Benchmark 15 Sub-tasks & Metrik Akhir. | Benchmark 15 Sub-tasks & Metrik Akhir. | **Identik:** `SubtaskMetricCapture`, ekspor `master_metrics.json` & plot F1. |
| **21–22** | Code | Live Interactive Inference Demo. | Live Interactive Inference Demo. | **Identik:** Fungsi `analyze_review_quadruples()` ekstraksi teks bebas dua-tahap. |
| **23–24** | Code | Inventarisasi Artefak & Report Save. | Inventarisasi Artefak & Report Save. | **Identik:** Mengompilasi seluruh artefak ke tabel CSV dan Markdown report. |

---

## 3. Keunggulan & Temuan pada Versi UPDATE

1. **Fitur State Checkpointing (Sel 13 & 14):**
   - Penambahan penyimpanan `pipeline_state.pkl` merupakan perbaikan kritis untuk Google Colab gratisan yang sering mengalami *idle timeout* atau pemutusan sesi. Pengguna tidak perlu mengulang proses pelatihan Step 1 (~10–15 menit).
2. **Diagnostik Jalur Data (Sel 9 & 10):**
   - Memastikan pengguna Colab segera mengetahui jika folder dataset belum terunggah atau berada di luar folder induk `ACOS`.
3. **Penyimpanan Hasil ke Google Drive (`/content/drive/MyDrive/ACOS`):**
   - Baik versi ASLI maupun UPDATE secara konsisten mengarahkan penyimpanan output ke Google Drive bila `/content/drive/MyDrive` terdeteksi.

---

## 4. Catatan Teknis untuk Peningkatan Selanjutnya

1. **Penggantian Path Hardcoded pada Fallback:**
   - Di Sel 9 (`search_dir = "/content/drive/MyDrive/ACOS"`) dan Sel 14 (`checkpoint_state_path = '/content/ACOS/results/rest16_27082026_090134/pipeline_state.pkl'`), string statis tersebut perlu dijadikan dinamis agar bekerja mulus di komputer lokal dan pada sesi baru.
2. **Akselerasi GPU & VRAM Memory Management:**
   - Disarankan menyisipkan `torch.cuda.empty_cache()` serta `pin_memory=True` pada DataLoader untuk memaksimalkan performa GPU.
3. **Standarisasi MCP Manifest:**
   - Menambahkan berkas `session_manifest.json` agar siklus hidup training dapat dipantau oleh agent/tool MCP.
