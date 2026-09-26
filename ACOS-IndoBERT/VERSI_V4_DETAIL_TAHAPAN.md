# 📋 Detail Tahapan ACOS Pipeline Versi V4 (IndoBERT)

**Dokumen Penanda Versi V4**  
Tanggal: 26 September 2026  
Notebook: `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`

---

## 🎯 Ringkasan Eksekutif V4

### Perbedaan V4 dari V2 (Baseline)

| Aspek | V2 (Baseline) | V4 (Ini) |
|-------|---------------|----------|
| **Backbone** | `bert-base-uncased` | `indobenchmark/indobert-base-p1` (fine-tuned) |
| **Domain** | `rest16` / `laptop` (Inggris) | `appsid` (ulasan aplikasi bank digital Indonesia) |
| **Kategori** | 13 (`ENTITAS#ATRIBUT`) | 13 (nama datar, mis. `AUTH_ACCESS`, `SECURITY_PRIVACY`) |
| **num_labels Step 2** | 39 | **39** (sengaja sama, dimensi head tidak berubah) |
| **Sumber Data** | `data/Restaurant-ACOS/` | `data/Apps-ACOS/processed/` |
| **Folder Sesi** | `results/rest16_<timestamp>/` | `results/appsid_<timestamp>/` |
| **Bahasa Review** | Inggris | **Indonesia** |

### Arsitektur Dua Root

V4 memperkenalkan **arsitektur dua root** untuk memisahkan kode Indonesia dari pipeline Inggris:

| Variabel | Isi | Ditulis? | Fungsi |
|----------|-----|----------|---------|
| `indo_root` | `ACOS-IndoBERT/` | **Ya** | Dataset Indonesia, tokenized_data, backbones, results |
| `acos_root` | `ACOS-ASLI/` | **Tidak** | Pipeline Inggris `Extract-Classify-ACOS/` + data rest16 (baca saja) |

**Prinsip Desain:**
- Seluruh perbedaan Indonesia ada di paket `acos_id/` di bawah `indo_root`
- **TIDAK** ada patch pada `Extract-Classify-ACOS/`
- Jalur Inggris tetap utuh, bisa dipakai sebagai kontrol

---

## 📚 Daftar Sel Baru V4

| Sel | Nama | Isi | Torch? | Prasyarat |
|-----|------|-----|--------|-----------|
| **1b** | Pelacak Progres Bertahap | Definisi `step_stage`, `require_vars`, `patch_eval_metrics_counts()` | Tidak | - |
| **1s** | Sinkronisasi `acos_id/` | Import paket `acos_id/`, setup `sys.path`, dua root | Tidak | Sel 2c |
| **2c** | Dua Root & Paket `acos_id/` | Validasi `indo_root` vs `acos_root`, kelengkapan modul | Tidak | - |
| **4c** | Adapter Checkpoint IndoBERT | Rekey prefiks `bert.`, validasi vocab, export laporan | **Ya** | Sel 4b |
| **4d** | Gerbang Data Indonesia | Taksonomi, split, konversi ACOS, generator `tokenized_data`, gate 2 Inggris | Tidak | Sel 4c |
| **5d2** | Gate 1: Validasi Bobot Encoder | Perbandingan numerik bobot encoder dengan checkpoint IndoBERT | **Ya** | Sel 5d |

---

## 🔄 Alur Eksekusi Lengkap V4

### **FASE 0: Setup Lingkungan & Hardware**

#### **Sel 1a: Instalasi Dependensi**
```bash
pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn \
            matplotlib pandas boto3 tqdm openpyxl tabulate
```

**Output:**
- Semua library ML/DL terinstall
- Dukungan ekspor Excel (`openpyxl`) & Markdown (`tabulate`)

---

#### **Sel 1b: Pelacak Progres Bertahap** ⭐ WAJIB

**Fungsi Utama:**

1. **`step_stage`** — Context manager untuk tracking progres per sel
   ```python
   with step_stage("Judul Tahap", total_steps=5) as stage:
       stage.step("Langkah 1 dimulai")
       # ... operasi ...
       stage.note("Info tambahan")
   ```
   - Cetak judul, langkah bernomor + waktu berjalan
   - Durasi total di akhir
   - Jejak tetap terbaca walau runtime Colab terputus

2. **`require_vars(*names)`** — Validasi prasyarat
   - Menghentikan sel dengan pesan jelas bila variabel belum ada
   - Contoh: `require_vars("model_step1", "pred4pipeline_path")`

3. **`patch_eval_metrics_counts()`** — Patch metrik upstream
   - Membuat `measureQuad` & `measureQuad_imp` mengembalikan **TP/FP/FN**
   - Memperbaiki 2 bug upstream:
     - `measureQuad_imp` return di luar loop (hanya slot difficulty terakhir terbawa)
     - KeyError untuk teks prediksi tidak ada di `text_type`
   - Hitungan mentah disimpan ke CSV/JSON & ditampilkan di tabel hasil

4. **`ExecutionTracker`** — Pencatat waktu & checkpoint
   - Durasi per-epoch
   - Waktu penyimpanan checkpoint
   - Ekspor ke CSV/Excel/Markdown dengan profil GPU

**Catatan Penting:**
> ⚠️ **Sel ini WAJIB dijalankan ulang setiap kali kernel di-restart**, sebelum melompat ke Step 1/2 atau evaluasi.

---

#### **Sel 1c: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```

**Output:**
- `GDRIVE_MOUNTED = True` bila di Colab
- `GDRIVE_BACKUP_DIR = "/content/drive/MyDrive/ACOS_BACKUP"`
- Fungsi `sync_to_gdrive()` aktif untuk backup otomatis

---

#### **Sel 1d: Diagnostik Hardware GPU**

**Deteksi Platform:**
- ROCm (AMD Instinct MI300X/MI250)
- CUDA (NVIDIA A100/V100/H100)
- CPU fallback

**Output:**
```
⚡ Perangkat Komputasi Utama: cuda
============================================================
🖥️  SPESIFIKASI HARDWARE & AKSESIBILITAS GPU:
   Model GPU         : AMD Instinct MI300X VF
   Total VRAM        : 191.69 GB
   Akselerator       : AMD ROCm HIP
   ROCm HIP Build    : 7.14.60850
   Large GPU Class   : 🚀 YA (Enterprise / High-VRAM Accelerator)
   PyTorch Version   : 2.12.0+rocm7.14.0
============================================================
```

**Dictionary Global:**
```python
GPU_BENCHMARK_INFO = {
    "device": "cuda",
    "gpu_name": "AMD Instinct MI300X VF",
    "total_vram_gb": 191.69,
    "is_large_gpu": True,
    "platform_type": "AMD ROCm HIP",
    "rocm_hip_version": "7.14.60850",
    "pytorch_version": "2.12.0+rocm7.14.0",
    # ...
}
```

---

### **FASE 1: Navigasi Path & Import Modul**

#### **Sel 2a: Dynamic Directory Navigation**

**Prioritas Deteksi:**
1. Google Drive: `/content/drive/MyDrive/ACOS*`
2. Colab Ephemeral: `/content/ACOS`
3. Lokal: `./` atau `../`

**Output Variabel:**
- `base_project_dir` — root proyek
- `extract_dir` — `Extract-Classify-ACOS/`
- `data_root` — folder dataset
- `save_dir` — output hasil
- `notebooks_dir` — folder notebook

**Auto-clone Repo:**
```bash
git clone https://github.com/haisyamalawwab/ACOS.git /tmp/ACOS_clone
cp -r /tmp/ACOS_clone/* "${base_project_dir}/"
```

---

#### **Sel 2b: Import `colab_utils.py`** ⭐

**Validasi Kelengkapan:**
Memeriksa 21 simbol wajib:
```python
REQUIRED_UTILS = (
    "setup_timestamped_run_dir", "download_bert_pretrained", "analyze_and_plot_eda",
    "plot_training_history", "export_benchmark_tables_and_plots",
    "display_quadruple_dataframe", "df_to_markdown", "export_step_table",
    "MarkdownReport", "SubtaskMetricCapture", "plot_subtask_metrics",
    "features_step1", "features_step2", "pair_examples_from_file",
    "resolve_eval_pair_file", "unpack_model_output",
    "detect_acos_project_root", "inspect_acos_drive_structure",
    "verify_session_save_paths", "find_resumable_session", "auto_find_file",
)
```

**Strategi Fallback:**
1. Cek `notebooks_dir/colab_utils.py`
2. Cek `extract_dir/colab_utils.py`
3. Download dari GitHub bila semua tidak lengkap

**Output:**
```
🧩 colab_utils aktif       : /path/to/colab_utils.py
📂 Base Project Directory : /shared-docker/ACOS
📁 Extract & Model Dir     : /shared-docker/ACOS/Extract-Classify-ACOS
```

---

#### **Sel 2c: Dua Root & Paket `acos_id/`** ⭐ BARU V4

**Tujuan:**
Memisahkan kode Indonesia (`indo_root`) dari pipeline Inggris (`acos_root`)

**Validasi Modul:**
```python
ACOS_ID_MODULES = (
    "taxonomy",      # Kategori, sentiment, label sekuens
    "build_acos",    # Konversi raw → format ACOS
    "tokenize_data", # Generator tokenized
    "checkpoint",    # Adapter IndoBERT
    "selftest",      # Gerbang torch-free
    "eda",           # Plot EDA Indonesia
    "upstream"       # Finder Extract-Classify-ACOS
)
```

**Output:**
```
🇮🇩 acos_id v0.2.1
   indo_root  (tulis) : /shared-docker/ACOS/ACOS-IndoBERT
   acos_root  (baca)  : /shared-docker/ACOS
   extract_dir        : /shared-docker/ACOS/Extract-Classify-ACOS
   data / tokenized   : /shared-docker/ACOS/ACOS-IndoBERT/data | /shared-docker/ACOS/ACOS-IndoBERT/tokenized_data
   Domain Indonesia   : appsid
   Kategori           : 13 → num_labels Step 2 = 39
   Label sekuens S1   : ['[CLS]', 'O', 'I-A', 'B-A', 'I-O', 'B-O']
   Gerbang torch-free : taxonomy, dataset, acos_build, tokenized, gate2_english
```

**Folder Structure:**
```
ACOS-IndoBERT/          # indo_root (TULIS)
├── acos_id/            # Paket Python Indonesia
│   ├── taxonomy.py
│   ├── build_acos.py
│   ├── tokenize_data.py
│   ├── checkpoint.py
│   └── ...
├── data/
│   └── Apps-ACOS/      # Dataset Indonesia
├── tokenized_data/     # Output tokenisasi
├── backbones/
│   └── indobert/       # Checkpoint IndoBERT
└── results/
    └── appsid_*/       # Hasil eksperimen

ACOS-ASLI/              # acos_root (BACA SAJA)
└── Extract-Classify-ACOS/  # Pipeline asli Inggris
```

---

### **FASE 2: Konfigurasi Pipeline & Sesi**

#### **Sel 3: Master Pipeline Parameters**

**Konfigurasi V4:**
```python
# Domain Dataset
DOMAIN = "appsid"  # Indonesia
# DOMAIN = "rest16"  # Inggris (kontrol)

# Backbone Model
BACKBONE = "indobert"  # indobenchmark/indobert-base-p1
# BACKBONE = "bert-en"  # bert-base-uncased (untuk rest16)

# Hyperparameters
LR_STEP1 = 2e-5
LR_STEP2 = 2e-5
EPOCHS_STEP1 = 10
EPOCHS_STEP2 = 10
BATCH_SIZE = 16
MAX_SEQ_LEN = 128

# Optimasi Large GPU
GRAD_ACCUMULATION_STEPS = 1 if is_large_gpu else 2
AMP_ENABLED = True if is_large_gpu else False
```

**Setup Sesi Bertimestamp:**
```python
session_name = f"{DOMAIN}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
session_dir = os.path.join(save_dir, "results", session_name)
```

**Struktur Folder Sesi:**
```
results/appsid_20260926_143022/
├── csv/                    # Tabel hasil (CSV)
├── logs/                   # Progress JSON per tahap
├── model/                  # Checkpoint model
│   ├── step1_best_crf/
│   └── step2_best_classifier/
├── plots/                  # Visualisasi 300 DPI
├── pred4pipeline.txt       # Output Step 1
├── step2_input_candidates.txt
├── step2_predictions.txt
├── pipeline_state.pkl      # Checkpoint state
└── session_manifest.json   # MCP manifest
```

---

#### **Sel 4a: Cache Pretrained BERT**

**Untuk Domain Inggris (`rest16`):**
```python
download_bert_pretrained(
    model_name="bert-base-uncased",
    cache_dir=os.path.join(base_project_dir, "backbones", "bert_base_uncased")
)
```

**Untuk Domain Indonesia (`appsid`):**
```python
# Sel 4c menangani IndoBERT
```

---

#### **Sel 4b: EDA (Exploratory Data Analysis)**

**Plot yang Dihasilkan:**
1. Distribusi panjang review (token)
2. Distribusi jumlah quadruple per review
3. Top-N kategori (bar chart)
4. Top-N sentiment (pie chart)
5. Statistik aspect/opinion implisit

**Output:**
```
plots/eda_distribution_review_length.png
plots/eda_distribution_quads_per_review.png
plots/eda_top_categories.png
plots/eda_sentiment_distribution.png
csv/eda_summary_appsid.csv
```

**Resolusi:** 300 DPI (publication quality)

---

#### **Sel 4c: Adapter Checkpoint IndoBERT** ⭐ BARU V4

**Masalah yang Diselesaikan:**

1. **Prefiks `bert.` hilang**
   - Checkpoint IndoBERT: `encoder.layer.0.weight`
   - `BertForQuadABSA` butuh: `bert.encoder.layer.0.weight`
   - Tanpa rekey → bobot encoder masuk `missing_keys` → training dengan encoder **acak**

2. **Vocab size mismatch**
   - IndoBERT: 30,522 tokens
   - BERT English: 30,522 tokens (sama, tapi mapping berbeda!)

**Proses:**
```python
from acos_id.checkpoint import adapt_indobert_checkpoint

ckpt_adapted = adapt_indobert_checkpoint(
    pretrained_name="indobenchmark/indobert-base-p1",
    output_dir=os.path.join(indo_root, "backbones", "indobert"),
    rekey_prefix=True,          # Tambah prefiks 'bert.'
    validate_vocab=True,        # Cek vocab size
    export_vocab_report=True    # Export vocab mapping
)
```

**Output:**
```
backbones/indobert/
├── pytorch_model.bin          # Bobot dengan prefiks 'bert.'
├── config.json
├── vocab.txt
└── vocab_report.json          # Laporan validasi
```

**Laporan Validasi:**
```json
{
  "vocab_size": 30522,
  "rekey_count": 199,
  "missing_keys": [],
  "unexpected_keys": [],
  "sample_tokens": ["[PAD]", "[UNK]", "[CLS]", "yang", "di", "..."],
  "validation": "PASSED"
}
```

---

#### **Sel 4d: Gerbang Data Indonesia** ⭐ BARU V4

**5 Gerbang Validasi:**

1. **Gate: Taksonomi**
   ```python
   assert len(acos_taxonomy.CATEGORIES) == 13
   assert acos_taxonomy.num_labels_step2() == 39
   assert list(acos_taxonomy.SEQ_LABELS) == ['[CLS]', 'O', 'I-A', 'B-A', 'I-O', 'B-O']
   ```

2. **Gate: Dataset Split**
   ```python
   split = acos_eda.count_split_sizes(data_root, DOMAIN)
   assert split["train"] > 0 and split["dev"] > 0 and split["test"] > 0
   ```

3. **Gate: Konversi ACOS**
   ```python
   from acos_id.build_acos import convert_raw_to_acos
   convert_raw_to_acos(
       raw_file="data/Apps-ACOS/raw/appsid_reviews.json",
       output_dir="data/Apps-ACOS/processed"
   )
   ```

4. **Gate: Tokenized Data Generator**
   ```python
   from acos_id.tokenize_data import tokenized_data_generator
   gen = tokenized_data_generator(
       domain=DOMAIN,
       data_root=data_root,
       tokenizer=tokenizer_indobert,
       max_len=MAX_SEQ_LEN
   )
   for split_name, features in gen:
       torch.save(features, f"tokenized_data/{DOMAIN}/{split_name}.pt")
   ```

5. **Gate 2: Blokir Domain Inggris Pakai Tokenizer Indonesia**
   ```python
   if DOMAIN in ("rest16", "laptop") and BACKBONE == "indobert":
       raise RuntimeError(
           "Domain Inggris tidak boleh pakai tokenizer IndoBERT. "
           "Set BACKBONE='bert-en' untuk domain Inggris."
       )
   ```

**Output:**
```
tokenized_data/appsid/
├── train.pt
├── dev.pt
└── test.pt
```

---

### **FASE 3: Step 1 — Aspect-Opinion Co-Extraction (BERT-CRF)**

#### **Sel 5a: Inisialisasi Step 1**

**Import Modul Upstream:**
```python
import sys
sys.path.insert(0, extract_dir)

import modeling
import train_step1
import pred_step1
import eval_step1
import eval_metrics
```

**Patch Metrik Counts:**
```python
eval_metrics = patch_eval_metrics_counts()
```

**Inisialisasi Variabel:**
```python
bert_config_step1 = modeling.BertConfig.from_pretrained(BERT_CACHE_DIR)
bert_config_step1.num_labels = 6  # CLS, O, I-A, B-A, I-O, B-O

model_step1 = modeling.BertForABSA.from_pretrained(
    BERT_CACHE_DIR,
    config=bert_config_step1
)
model_step1.to(device)
```

---

#### **Sel 5b: Cache Data Step 1**

**Load Tokenized Data:**
```python
train_features_s1 = torch.load(f"tokenized_data/{DOMAIN}/train.pt")
dev_features_s1 = torch.load(f"tokenized_data/{DOMAIN}/dev.pt")
test_features_s1 = torch.load(f"tokenized_data/{DOMAIN}/test.pt")
```

**Output:**
```
✅ Data Step 1 loaded:
   Train: 1,234 samples
   Dev:     156 samples
   Test:    195 samples
```

---

#### **Sel 5c: Validasi Data Step 1**

**Cek Tensor Shape:**
```python
assert train_features_s1[0].input_ids.shape[0] == MAX_SEQ_LEN
assert train_features_s1[0].label_ids.shape[0] == MAX_SEQ_LEN
```

**Inspeksi Sample:**
```python
sample = train_features_s1[0]
print(f"Input IDs: {sample.input_ids[:10]}")
print(f"Label IDs: {sample.label_ids[:10]}")
print(f"Text: {tokenizer.decode(sample.input_ids)}")
```

---

#### **Sel 5d: Load Model Step 1**

**Auto-skip bila Checkpoint Ada:**
```python
step1_best_path = os.path.join(session_dir, "model", "step1_best_crf")
if os.path.exists(os.path.join(step1_best_path, "pytorch_model.bin")):
    print("⏭️ Step 1 checkpoint sudah ada. Loading...")
    model_step1 = modeling.BertForABSA.from_pretrained(step1_best_path)
    model_step1.to(device)
    # Skip training
else:
    # Lanjut ke Sel 5e (training)
```

---

#### **Sel 5d2: Gate 1 — Validasi Bobot Encoder** ⭐ BARU V4

**Tujuan:**
Memastikan bobot encoder benar-benar ter-load dari checkpoint IndoBERT, bukan acak.

**Proses:**
```python
from acos_id.checkpoint import validate_encoder_weights

report = validate_encoder_weights(
    model=model_step1,
    checkpoint_path=ckpt_adapted,
    tolerance=1e-5
)

if not report["passed"]:
    raise RuntimeError(
        f"Bobot encoder tidak cocok dengan checkpoint IndoBERT!\n"
        f"Missing keys: {report['missing_keys']}\n"
        f"Weight diff: {report['max_diff']}"
    )
```

**Output:**
```
✅ Gate 1 PASSED:
   Encoder layers matched: 12/12
   Max weight difference: 8.34e-8
   Missing keys: []
   Unexpected keys: []
```

---

#### **Sel 5e: Training Step 1**

**Training Loop:**
```python
from train_step1 import train

history_step1 = []
best_f1_step1 = 0.0
best_epoch_step1 = 0

for epoch in range(1, EPOCHS_STEP1 + 1):
    t0_epoch = time.time()
    
    # Training
    train_loss = train_one_epoch(
        model=model_step1,
        train_features=train_features_s1,
        optimizer=optimizer_step1,
        device=device,
        batch_size=BATCH_SIZE,
        grad_accumulation_steps=GRAD_ACCUMULATION_STEPS,
        amp_enabled=AMP_ENABLED
    )
    
    # Evaluation
    dev_metrics = evaluate_step1(
        model=model_step1,
        dev_features=dev_features_s1,
        device=device
    )
    
    # Track
    history_step1.append({
        "epoch": epoch,
        "loss": train_loss,
        "precision": dev_metrics["precision"],
        "recall": dev_metrics["recall"],
        "micro-F1": dev_metrics["micro-F1"],
        "tp": dev_metrics["tp"],
        "fp": dev_metrics["fp"],
        "fn": dev_metrics["fn"]
    })
    
    # Save best
    if dev_metrics["micro-F1"] > best_f1_step1:
        best_f1_step1 = dev_metrics["micro-F1"]
        best_epoch_step1 = epoch
        
        t0_save = time.time()
        model_step1.save_pretrained(step1_best_path)
        save_duration = time.time() - t0_save
        
        print(f"💾 Best model saved (F1={best_f1_step1:.4f}) in {save_duration:.2f}s")
    
    # Track execution time
    epoch_duration = time.time() - t0_epoch
    execution_tracker.record_epoch(
        step_name="Step1_BERT_CRF",
        epoch=epoch,
        duration_sec=epoch_duration,
        train_loss=train_loss,
        precision=dev_metrics["precision"],
        recall=dev_metrics["recall"],
        f1=dev_metrics["micro-F1"],
        peak_vram_mb=torch.cuda.max_memory_allocated() / (1024**2),
        checkpoint_saved=(dev_metrics["micro-F1"] == best_f1_step1),
        save_duration_sec=save_duration if dev_metrics["micro-F1"] == best_f1_step1 else 0,
        save_path=step1_best_path if dev_metrics["micro-F1"] == best_f1_step1 else None
    )
    
    # Progress JSON (persistent across Colab crashes)
    write_stage_progress(
        os.path.join(session_dir, "logs", "step1_progress.json"),
        step="Step1_BERT_CRF",
        epoch=epoch,
        total_epochs=EPOCHS_STEP1,
        train_loss=float(train_loss),
        dev_f1=float(dev_metrics["micro-F1"]),
        best_f1=float(best_f1_step1),
        best_epoch=int(best_epoch_step1)
    )
```

**Output:**
```
Epoch 1/10 — Loss: 0.4521, Dev F1: 65.32%, VRAM: 8.2GB [1m 23s]
💾 Best model saved (F1=0.6532) in 2.34s
Epoch 2/10 — Loss: 0.3012, Dev F1: 71.08%, VRAM: 8.2GB [1m 19s]
💾 Best model saved (F1=0.7108) in 2.28s
...
Epoch 10/10 — Loss: 0.1203, Dev F1: 78.94%, VRAM: 8.2GB [1m 15s]

✅ Step 1 Training Complete:
   Best F1: 78.94% (Epoch 9)
   Total Time: 13m 48s
```

---

#### **Sel 5f: Evaluasi & Export Step 1**

**Prediksi Test Set:**
```python
pred4pipeline_path = os.path.join(session_dir, "pred4pipeline.txt")
pred_step1.main(
    model_path=step1_best_path,
    test_features=test_features_s1,
    output_file=pred4pipeline_path,
    device=device
)
```

**Evaluasi Test:**
```python
test_metrics_step1 = eval_step1.main(
    pred_file=pred4pipeline_path,
    gold_file=f"data/Apps-ACOS/processed/appsid_quint_test.tsv"
)
```

**Export Tabel:**
```python
export_step_table(
    history=history_step1,
    test_metrics=test_metrics_step1,
    output_dir=os.path.join(session_dir, "csv"),
    step_name="step1"
)
```

**Output Files:**
```
csv/step1_training_history.csv
csv/step1_test_results.csv
logs/step1_run_result.json
```

---

### **FASE 4: Bridge — Candidate Pair Generation**

#### **Sel 7a: Generate Candidate Pairs**

**Proses:**
```python
from Extract-Classify-ACOS.pair_generation import generate_candidates

candidates_path = os.path.join(session_dir, "step2_input_candidates.txt")
generate_candidates(
    pred4pipeline_path=pred4pipeline_path,
    output_file=candidates_path,
    handle_implicit=True  # [-1, -1] untuk aspect/opinion implisit
)
```

**Format:**
```
review_id####aspect_span####opinion_span
0####[2, 3]####[5, 5]
0####[-1, -1]####[5, 5]    # implicit aspect
1####[1, 2]####[-1, -1]    # implicit opinion
```

---

### **FASE 5: Step 2 — Category-Sentiment Classification**

#### **Sel 8a: Inisialisasi Step 2**

**Model Config:**
```python
bert_config_step2 = modeling.BertConfig.from_pretrained(BERT_CACHE_DIR)
bert_config_step2.num_labels = 39  # 13 categories × 3 sentiments

model_step2 = modeling.BertForQuadABSA_S2.from_pretrained(
    BERT_CACHE_DIR,
    config=bert_config_step2
)
model_step2.to(device)
```

---

#### **Sel 8b-8f: Training Step 2**

**Proses Identik dengan Step 1:**
- Cache data
- Validasi
- Training loop
- Best checkpoint saving
- Execution tracking

**Output:**
```
step2_best_classifier/
├── pytorch_model.bin
├── config.json
└── training_args.bin

csv/step2_training_history.csv
logs/step2_progress.json
```

---

### **FASE 6: Evaluasi Benchmark Akhir**

#### **Sel 9a: Evaluasi 15 Subtask**

**Subtask List:**
1. Aspect Extraction
2. Opinion Extraction
3. Category Identification
4. Sentiment Classification
5. Aspect-Opinion Pair
6. Aspect-Category Pair
7. Opinion-Category Pair
8. Aspect-Sentiment Pair
9. Opinion-Sentiment Pair
10. Category-Sentiment Pair
11. Aspect-Opinion-Category Triple
12. Aspect-Opinion-Sentiment Triple
13. Aspect-Category-Sentiment Triple
14. Opinion-Category-Sentiment Triple
15. **Full Quadruple (ACOS)**

**Evaluasi:**
```python
from eval_metrics import evaluate_all_subtasks

final_metrics = evaluate_all_subtasks(
    pred_file=os.path.join(session_dir, "step2_predictions.txt"),
    gold_file=f"data/Apps-ACOS/processed/appsid_quint_test.tsv"
)
```

**Export:**
```json
{
  "full_quadruple": {
    "precision": 0.7234,
    "recall": 0.6891,
    "micro-F1": 0.7058,
    "tp": 456.0,
    "fp": 174.0,
    "fn": 205.0
  },
  "aspect_extraction": {...},
  "category_identification": {...},
  // ... 15 subtasks
}
```

---

#### **Sel 9b: Visualisasi & Export**

**Plot:**
1. Training history Step 1 & 2
2. Subtask metrics radar chart
3. Confusion matrix kategori
4. Confusion matrix sentiment

**Export Formats:**
- CSV: `master_metrics.csv`
- Excel: `master_report.xlsx` (3 sheets)
- Markdown: `master_report.md`
- JSON: `master_metrics.json`

---

### **FASE 7: Live Interactive Inference**

#### **Sel 10: Two-Stage Inference**

**Input:**
```python
sample_review = "Aplikasi BCA Mobile sangat lambat saat login. Tapi fitur transfer mudah digunakan."
```

**Proses:**
```python
# Stage 1: Extract aspects & opinions
aspects, opinions = model_step1.extract(sample_review)

# Stage 2: Classify categories & sentiments
quadruples = model_step2.classify(
    review=sample_review,
    aspect_opinion_pairs=zip(aspects, opinions)
)
```

**Output:**
```
┌─────────────┬──────────────┬────────────────────┬───────────┐
│ Aspect      │ Opinion      │ Category           │ Sentiment │
├─────────────┼──────────────┼────────────────────┼───────────┤
│ login       │ lambat       │ PERFORMANCE_SPEED  │ negative  │
│ transfer    │ mudah        │ UI_UX_EASE         │ positive  │
│ [implicit]  │ [implicit]   │ APP_GENERAL        │ neutral   │
└─────────────┴──────────────┴────────────────────┴───────────┘
```

---

## 🔧 Dua Kegagalan Senyap yang Dijaga V4

### **1. Prefix `bert.` Hilang**

**Masalah:**
- Checkpoint IndoBERT: `encoder.layer.0.weight`
- `BertForQuadABSA` butuh: `bert.encoder.layer.0.weight`
- Loader legacy (`modeling.py:745`) set `start_prefix=''`
- Tanpa rekey → seluruh bobot encoder masuk `missing_keys`
- Logging yang melaporkan ini di-comment out (`modeling.py:749-755`)
- **Training berjalan mulus dengan encoder acak!**

**Solusi V4:**
```python
# Sel 4c: adapt_indobert_checkpoint(..., rekey_prefix=True)
# Sel 5d2: validate_encoder_weights() dengan toleransi 1e-5
```

---

### **2. `get_labels()` Hanya Kenal `rest16` & `laptop`**

**Masalah:**
```python
def get_labels(data_dir):
    if "rest" in data_dir.lower():
        return RESTAURANT_CATEGORIES
    elif "laptop" in data_dir.lower():
        return LAPTOP_CATEGORIES
    else:
        return None  # Kategori hilang!
```

**Solusi V4:**
```python
# acos_id/taxonomy.py
def get_labels_appsid():
    return [
        "AUTH_ACCESS", "SECURITY_PRIVACY", "PERFORMANCE_SPEED",
        "UI_UX_EASE", "FEATURE_FUNCTIONALITY", "CUSTOMER_SERVICE",
        # ... 13 kategori
    ]

# Sel 4d: Gate validasi taksonomi
assert acos_taxonomy.CATEGORIES is not None
assert len(acos_taxonomy.CATEGORIES) == 13
```

---

## 📊 Output Lengkap V4

### **Struktur Folder Sesi:**
```
results/appsid_20260926_143022/
├── csv/
│   ├── eda_summary_appsid.csv
│   ├── step1_training_history.csv
│   ├── step1_test_results.csv
│   ├── step2_training_history.csv
│   ├── step2_test_results.csv
│   └── master_metrics.csv
├── logs/
│   ├── step1_progress.json
│   ├── step1_run_result.json
│   ├── step2_progress.json
│   ├── step2_run_result.json
│   └── master_metrics.json
├── model/
│   ├── step1_best_crf/
│   │   ├── pytorch_model.bin
│   │   └── config.json
│   └── step2_best_classifier/
│       ├── pytorch_model.bin
│       └── config.json
├── plots/
│   ├── eda_distribution_review_length.png
│   ├── eda_top_categories.png
│   ├── step1_training_curve.png
│   ├── step2_training_curve.png
│   ├── subtask_metrics_radar.png
│   └── confusion_matrix_category.png
├── pred4pipeline.txt
├── step2_input_candidates.txt
├── step2_predictions.txt
├── pipeline_state.pkl
├── session_manifest.json
├── master_report.xlsx
└── master_report.md
```

---

## 🎓 Cara Menjalankan V4

### **Colab (Recommended):**
```python
# 1. Upload notebook ke Drive: /content/drive/MyDrive/ACOS/notebooks/
# 2. Mount Drive
# 3. Run All (Runtime → Run all)
# 4. Hasil tersimpan otomatis di Drive: /content/drive/MyDrive/ACOS/results/
```

### **Local (Windows/Linux):**
```bash
# 1. Clone repo
git clone https://github.com/haisyamalawwab/ACOS.git
cd ACOS/ACOS-IndoBERT/notebooks

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run notebook
jupyter notebook 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb
```

---

## 📝 Catatan Penting

1. **Sel 1b & 1s WAJIB dijalankan ulang setiap restart kernel**
2. **Domain `appsid` hanya bisa pakai backbone `indobert`**
3. **Domain `rest16/laptop` harus pakai backbone `bert-en`**
4. **Gate 1 (Sel 5d2) akan gagal bila checkpoint IndoBERT tidak valid**
5. **Progress JSON (`logs/`) tetap terbaca walau tab Colab tertutup**
6. **Checkpoint auto-skip: sel training akan dilewati bila model sudah ada**

---

## 🔄 Perbedaan Sel V4 vs V2

| Sel | V2 | V4 | Perubahan |
|-----|----|----|-----------|
| 1b | ✅ | ✅ | + `patch_eval_metrics_counts()` |
| 1s | ❌ | ✅ | **BARU** — Import `acos_id/` |
| 2c | ❌ | ✅ | **BARU** — Dua root validation |
| 4c | ❌ | ✅ | **BARU** — IndoBERT adapter |
| 4d | ❌ | ✅ | **BARU** — Gerbang data Indonesia |
| 5d2 | ❌ | ✅ | **BARU** — Gate 1 encoder weights |
| 3 | `DOMAIN = "rest16"` | `DOMAIN = "appsid"` | Domain switch |
| 3 | `BACKBONE = "bert-en"` | `BACKBONE = "indobert"` | Backbone switch |

---

## 📚 Referensi

- **Notebook V4:** `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run24092026_GPU_AMD_MI300X.ipynb`
- **Builder Script:** `_build_v4_indobert.py`
- **Paket Indonesia:** `acos_id/` (v0.2.1)
- **Dataset:** Apps-ACOS (13 kategori, 1,585 reviews)
- **Backbone:** IndoBERT Base (Phase 1) — `indobenchmark/indobert-base-p1`

---

**Dokumen ini adalah penanda resmi Versi V4.**  
Semua tahapan, sel baru, gerbang validasi, dan output telah didokumentasikan.

---

*Generated: 26 September 2026*  
*Author: ACOS Pipeline V4 Documentation System*
