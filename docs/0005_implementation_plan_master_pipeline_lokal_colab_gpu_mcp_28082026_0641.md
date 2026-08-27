# Implementation Plan: Peningkatan Master Pipeline ACOS (Lokal, Google Colab + Drive, GPU & MCP)

**Tanggal:** 2026-08-28 06:41 WIB  
**Dokumen Referensi:** `docs/0005_implementation_plan_master_pipeline_lokal_colab_gpu_mcp_28082026_0641.md`  
**Target Objek:** `notebooks/00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb` & `notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb`  

---

## 1. Latar Belakang & Tujuan

Dokumen ini merinci rancangan teknis peningkatan (*improvement*) menyeluruh pada notebook master pipeline ACOS agar memiliki karakteristik produksi (*production-grade*):
1. **Kompatibilitas Penuh Dual-Environment:** Bekerja otomatis di komputer lokal (Windows/Linux) maupun di Google Colab.
2. **Penyimpanan Terpusat di Google Drive:** Jika dijalankan di Google Colab, semua artefak (model checkpoint, grafik plot 300 DPI, tabel metrik CSV, laporan Markdown, dan session state) otomatis disimpan di Google Drive dalam folder `/content/drive/MyDrive/ACOS/Output/results/<domain>_<timestamp>/`.
3. **Akselerasi GPU & Manajemen Memori:** Memaksimalkan throughput komputasi GPU, mencegah error CUDA Out-Of-Memory (OOM), dan mengoptimalkan transfer tensor CPU ke GPU.
4. **Kesiapan Ekosistem MCP (Model Context Protocol):** Menyediakan mekanisme pelacakan status terstruktur (*structured lifecycle manifest*) sehingga dapat dimonitor dan dioperasikan secara terprogram oleh AI Agent / MCP Server.

---

## 2. Rincian Fitur & Peningkatan Teknis

### A. Resolusi Jalur Dinamis (*Zero Hardcoded Paths*)
- **Deteksi Lingkungan Otomatis:**
  ```python
  IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
  HAS_DRIVE = os.path.exists("/content/drive/MyDrive")
  
  if HAS_DRIVE:
      base_project_dir = "/content/drive/MyDrive/ACOS"
      save_dir = os.path.join(base_project_dir, "Output")
  elif IS_COLAB:
      base_project_dir = "/content/ACOS" if os.path.exists("/content/ACOS") else os.path.abspath(".")
      save_dir = base_project_dir
  else:
      base_project_dir = os.path.abspath("..") if os.path.exists("../Extract-Classify-ACOS") else os.path.abspath(".")
      save_dir = base_project_dir
  ```
- **Pembersihan String Statis:**
  - Seluruh sel pencarian dataset (Sel 9 & 10) menggunakan `base_project_dir` dan `data_root` dinamis.
  - Pemulihan state pickle di Sel 14 secara cerdas mencari file `pipeline_state.pkl` terbaru di dalam direktori `results/` jika kernel baru saja terhubung kembali (*auto-detect latest session*).

### B. Optimasi Akselerasi GPU (CUDA)
- **Inspeksi Hardware Mendalam:**
  - Menampilkan nama GPU, jumlah total VRAM, Compute Capability, status cuDNN, dan alokasi memori awal.
  - Mengaktifkan `torch.backends.cudnn.benchmark = True` saat GPU aktif untuk efisiensi komputasi konvolusi/matriks.
- **Pencegahan Error OOM (Out-Of-Memory):**
  - Menyisipkan `torch.cuda.empty_cache()` sebelum inisialisasi model, sebelum training loop, dan pasca evaluasi per epoch.
  - Mencatat penggunaan memori puncak (*Peak VRAM Usage in MB*) pada setiap epoch:
    `peak_vram_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)`.
- **Optimalisasi DataLoader:**
  - Mengaktifkan `pin_memory = True if torch.cuda.is_available() else False` pada `DataLoader` training dan evaluasi untuk mempercepat transfer data *page-locked* ke memori GPU.
  - Menyesuaikan `num_workers` adaptif (`0` untuk Windows, `2` untuk Colab Linux).

### C. Integrasi MCP (Model Context Protocol) & AI Agent
- **Automated Lifecycle Manifest (`session_manifest.json`):**
  - Membuat fungsi pelacak status yang menulis berkas JSON standar di setiap transisi fase:
    ```json
    {
      "session_id": "rest16_28082026_064500",
      "status": "STEP1_COMPLETED",
      "stage": 5,
      "domain": "rest16",
      "device": "cuda (NVIDIA A100-SXM4-40GB)",
      "step1_best_micro_f1": 81.23,
      "step1_best_epoch": 6,
      "checkpoint_path": ".../checkpoints/step1_best",
      "artifacts_count": 12,
      "updated_at": "2026-08-28T06:45:12"
    }
    ```
  - Memungkinkan agent MCP (seperti Google Colab Agent / Antigravity IDE) untuk membaca progres tanpa harus mem-parsing log terminal teks mentah.

---

## 3. Matriks Perubahan Berkas Kode

```
notebooks/
├── 00_ACOS_Master_Pipeline_Colab_PRO.ipynb   [NEW / PRODUCTION NOTEBOOK]
├── 00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb[UPDATED & SYNCHRONIZED]
└── colab_utils.py                            [ENHANCED HELPERS]
```

---

## 4. Rencana Verifikasi

1. **Uji Validitas Sintaks & Struktur Notebook:** Memvalidasi seluruh sel JSON notebook menggunakan skrip parser internal.
2. **Uji Kompatibilitas Lokal:** Memastikan inisialisasi path, alokasi memori CPU/GPU lokal, dan ekspor output berjalan mulus di OS Windows.
3. **Uji Jalur Simulasi Colab Drive:** Memastikan logika pencabangan mengarah tepat ke `/content/drive/MyDrive/ACOS/Output/results/...`.
4. **Uji Struktur JSON Manifest MCP:** Memastikan format berkas `session_manifest.json` valid dan siap dikonsumsi oleh tool eksternal.
