# 📋 Detail Tahapan ACOS Pipeline Versi V5.1 (Universal Platform)

**Dokumen Penanda Versi V5.1**  
Tanggal: 26 September 2026  
Notebook: `01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_DriveSync.ipynb`

---

## 🎯 Ringkasan Eksekutif V5.1

### Evolusi Versi: V4 → V5 → V5.1

| Fitur | V4 | V5 | V5.1 (Ini) |
|-------|----|----|------------|
| **Platform GPU** | Manual config | MI300X only | **ROCm / CUDA / CPU auto-detect** |
| **Output** | Local only | Local `results/` | **Local + Drive mirror + manifest** |
| **EDA/Visualisasi** | Manual per-step | Tidak ada | **`acos_id.eda` + 4 PNG + tabel** |
| **Eksperimen** | Single run | Manual batch | **ExperimentGrid (54 kombinasi)** |
| **Batch Adaptif** | Fixed | Fixed | **SMALL/MEDIUM/LARGE tier preset** |
| **Per-run Tracking** | Basic CSV | `hardware_log.json` | **ResultSaver (csv/plots/md/checkpoints)** |
| **Drive Sync** | Manual | Tidak ada | **Auto sync + resume + share antar-server** |
| **Cross Validation** | Manual | Tidak ada | **5-fold & 10-fold built-in** |

---

## 🏗️ Arsitektur V5.1

### **Tiga Tier GPU Adaptif**

V5.1 memperkenalkan sistem **tier adaptif** yang secara otomatis menyesuaikan hyperparameter berdasarkan GPU yang terdeteksi:

| Tier | GPU Contoh | VRAM | Batch (S1/S2) | Accum | Efektif Batch | AMP | Worker | Cache | Resume |
|------|------------|------|---------------|-------|---------------|-----|--------|-------|--------|
| **SMALL** | T4, CPU | ≤20GB | 16/8 | 4 | 64/32 | fp16 | 2 | ✅ | ✅ |
| **MEDIUM** | L4 | ≤40GB | 32/24 | 2 | 64/48 | fp16 | 2 | ✅ | ✅ |
| **LARGE** | MI300X, A100, H100 | ≥40GB | 96/64 | 1 | 96/64 | bf16/fp16 | 4 | ❌ | ❌ |

**Filosofi Tier:**
- **SMALL/MEDIUM:** Maksimalkan cache & resume untuk GPU terbatas
- **LARGE:** Maksimalkan throughput, training from-scratch setiap run

---

### **ExperimentGrid: 54 Kombinasi Otomatis**

V5.1 menjalankan grid eksperimen **penuh** untuk riset:

```python
EXPERIMENT_EPOCHS = [50, 75, 100]           # 3 setting epoch
EXPERIMENT_RATIOS = [                        # 3 split ratio
    (0.8, 0.1),  # 80:10:10 train:dev:test
    (0.7, 0.15), # 70:15:15
    (0.6, 0.2)   # 60:20:20
]
EXPERIMENT_CV = [                            # 2 CV setting
    {'n_splits': 5},   # 5-fold
    {'n_splits': 10}   # 10-fold
]

# Total runs = 3 epoch × (3 ratio + 5 fold + 10 fold) = 54 run
```

**Keunggulan Grid:**
- ✅ Riset komprehensif tanpa manual script
- ✅ Setiap run isolated (tidak interfere)
- ✅ Resume-able (crash-resistant)
- ✅ Comparable results (JSON + CSV standardized)

---

## 📚 Struktur Sel V5.1 (11 Sel)

| Sel | Nama | Fungsi | Torch? | Waktu Est. |
|-----|------|--------|--------|------------|
| **1** | Diagnostik GPU & Hardware | Deteksi ROCm/CUDA/CPU, VRAM, tier adaptif | Tidak | 10s |
| **2** | Konfigurasi Dinamis | **Satu-satunya sel yang perlu diedit** | Tidak | 5s |
| **3** | Import & Path Setup | Dua-root validation, `acos_id` import, `sync_to_gdrive()` | Tidak | 30s |
| **4** | HardwareMonitor | Real-time VRAM tracking dual-backend | Ya | 10s |
| **5** | Backbone IndoBERT & Tokenizer | Cache checkpoint + vocab validation | Ya | 2-5 menit |
| **5b** | EDA + Visualisasi | Tabel + 4 PNG (ala V4) | Tidak | 1-3 menit |
| **6** | ExperimentGrid Preview | Preview 54 run **tanpa training** | Tidak | 10s |
| **7** | Persiapan Data | Build semua TSV + tokenisasi (1x, cached) | Ya | 30-60 menit |
| **8** | Training Adapter Function | Definisi `train_one_run()` | Tidak | 1s |
| **9** | Run Semua Eksperimen | **Eksekusi 54 run otomatis** | Ya | **5-8 hari** |
| **10** | Agregasi & Perbandingan | Plot comparison + tabel best models | Tidak | 5-10 menit |
| **11** | Hardware Summary | Tabel resource usage + REPORT_INDEX + Drive sync | Tidak | 2-5 menit |

---

## 🔄 Alur Eksekusi Lengkap V5.1

### **FASE 0: Setup Awal**

#### **Sel 1: Diagnostik GPU & Hardware** ⭐ DUAL-BACKEND

**Deteksi Platform:**
```python
HAS_CUDA = torch.cuda.is_available()
HAS_ROCM = HAS_CUDA and 'rocm' in torch.__version__.lower()
HAS_NVIDIA_SMI = shutil.which('nvidia-smi') is not None
HAS_ROCM_SMI = shutil.which('rocm-smi') is not None
BACKEND = 'rocm' if HAS_ROCM else ('cuda' if HAS_CUDA else 'cpu')
```

**Tier Adaptif:**
```python
if TOTAL_VRAM_GB <= 0:
    GPU_TIER = 'SMALL'
elif 't4' in GPU_NAME.lower() or TOTAL_VRAM_GB <= 20:
    GPU_TIER = 'SMALL'
elif 'l4' in GPU_NAME.lower() or TOTAL_VRAM_GB <= 40:
    GPU_TIER = 'MEDIUM'
else:
    GPU_TIER = 'LARGE'
```

**Output:**
```
Waktu mulai sesi : 2026-09-26 13:43:31
PyTorch version  : 2.11.0+cu128
CUDA available   : True
Backend          : cuda
Device           : cuda

GPU count        : 1
  GPU[0] : Tesla T4
          VRAM = 14.56 GB
          SM   = 40 multiprocessors

=================================================================
GPU Name         : Tesla T4
Total VRAM       : 14.56 GB
BACKEND          : cuda
GPU_TIER         : SMALL
IS_LARGE_GPU     : False
=================================================================

Hardware info dicatat: 11 field
```

**Dictionary Global:**
```python
_hw_info = {
    'session_start': '2026-09-26T13:43:31',
    'session_ts': '26092026_134331',
    'gpu_name': 'Tesla T4',
    'total_vram_gb': 14.56,
    'backend': 'cuda',
    'gpu_tier': 'SMALL',
    'has_rocm': False,
    'smi_ok': True,
    'torch_version': '2.11.0+cu128',
    'python_version': '3.13.15',
    'platform': 'Linux-6.6.122+-x86_64'
}
```

---

#### **Sel 2: Konfigurasi Dinamis** ⭐ SATU-SATUNYA SEL YANG DIEDIT

**Dictionary Master:**
```python
CONFIG = {
    # Tier GPU
    'GPU_TIER_OVERRIDE': 'AUTO',  # AUTO/SMALL/MEDIUM/LARGE
    
    # Dataset & Model
    'DOMAIN': 'appsid',           # appsid (Indonesia)
    'BACKBONE': 'indobert',       # indobenchmark/indobert-base-p1
    
    # Grid Eksperimen
    'EXPERIMENT_EPOCHS': [50, 75, 100],
    'EXPERIMENT_RATIOS': [(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)],
    'EXPERIMENT_CV': [{'n_splits': 5}, {'n_splits': 10}],
    
    # Eksekusi
    'RUN_MODE': 'all',            # all/ratio/cv
    'DRY_RUN': True,              # True = preview; False = training sungguhan
    'RUN_EPOCHS': None,           # None = ikut EXPERIMENT_EPOCHS; [50] = test 1 epoch-set
    
    # Override Batch (None = preset tier)
    'STEP1_BATCH': None,          # mis. 16 untuk T4
    'STEP2_BATCH': None,          # mis. 8 untuk T4
    
    # Hyperparameter
    'STEP1_LR': 2e-5,
    'STEP2_LR': 5e-5,
    'MAX_SEQ_LENGTH': 128,
    'SEED': 42,
    'DO_LOWER_CASE': True,        # Wajib True untuk IndoBERT
    
    # Drive & Cache
    'DRIVE_SYNC': True,           # Auto mirror ke Drive
    'FORCE_REBUILD_DATA': None,   # None = adaptif tier
    'RESUME': None,               # None = adaptif tier
}
```

**Environment Override:**
Prioritas lebih tinggi dari `CONFIG`:
```bash
# Smoke test T4
export ACOS_TIER=SMALL
export ACOS_MODE=ratio
export ACOS_DRY=true
export ACOS_EPOCHS="[50]"
export ACOS_BATCH1=16
export ACOS_BATCH2=8

# Full MI300X
export ACOS_TIER=LARGE
export ACOS_MODE=all
export ACOS_DRY=false
```

**Preset Tier Efektif:**

**LARGE Tier (MI300X/A100):**
```python
STEP1_BATCH_SIZE, STEP2_BATCH_SIZE = 96, 64
GRAD_ACCUM_STEPS, NUM_WORKERS = 1, 4
USE_AMP, AMP_DTYPE = True, 'bfloat16' if BACKEND=='rocm' else 'float16'
TRAIN_FROM_SCRATCH = True
USE_MODEL_CACHE = False
FORCE_REBUILD_DATA = False
RESUME_LAST_SESSION = False
PATIENCE = 0  # No early stop
```

**MEDIUM Tier (L4):**
```python
STEP1_BATCH_SIZE, STEP2_BATCH_SIZE = 32, 24
GRAD_ACCUM_STEPS, NUM_WORKERS = 2, 2
USE_AMP, AMP_DTYPE = True, 'float16'
TRAIN_FROM_SCRATCH = False
USE_MODEL_CACHE = True
FORCE_REBUILD_DATA = False
RESUME_LAST_SESSION = True
PATIENCE = 0
```

**SMALL Tier (T4/CPU):**
```python
STEP1_BATCH_SIZE, STEP2_BATCH_SIZE = 16, 8
GRAD_ACCUM_STEPS, NUM_WORKERS = 4, 2
USE_AMP, AMP_DTYPE = True, 'float16'
TRAIN_FROM_SCRATCH = False
USE_MODEL_CACHE = True
FORCE_REBUILD_DATA = False
RESUME_LAST_SESSION = True
PATIENCE = 0
```

**Output Validasi:**
```
=================================================================
KONFIGURASI V5.1 DINAMIS — TIER=SMALL BACKEND=cuda
=================================================================
Domain              : appsid
Backbone            : indobert
Experiment epochs   : [50, 75, 100]
Experiment ratios   : [(80, 10), (70, 15), (60, 20)]
Experiment CV       : [5, 10]-fold
Total runs          : 54

STEP1_BATCH_SIZE    : 16
STEP2_BATCH_SIZE    : 8
GRAD_ACCUM_STEPS    : 4
NUM_WORKERS         : 2
PATIENCE            : 0 (0 = no early stop)
TRAIN_FROM_SCRATCH  : False
USE_MODEL_CACHE     : True
FORCE_REBUILD_DATA  : False
RESUME_LAST_SESSION : True
RUN_MODE/DRY_RUN    : all/True epochs=[50, 75, 100]
USE_AMP             : True (float16)
ROCM_BENCHMARK      : True
=================================================================
Mode cache: tokenized_data/backbone/checkpoint dipakai ulang, tidak rebuild.

DRIVE_SYNC=True BACKEND=cuda TIER=SMALL AMP_DTYPE=float16
Drive standar: /content/drive/MyDrive/ACOS/ACOS-IndoBERT
```

---

### **FASE 1: Import & Infrastructure**

#### **Sel 3: Import & Path Setup** ⭐ ROBUST DUA-ROOT

**Validasi Lengkap:**
```python
def _is_upstream(d):
    """Validasi Extract-Classify-ACOS lengkap."""
    return (os.path.isfile(os.path.join(d, 'modeling.py')) and 
            os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py')))

def _validate_acos_id_complete(indo_path):
    """Validasi semua modul acos_id ada dan tidak kosong."""
    ACOS_ID_MODULES = [
        "taxonomy", "checkpoint", "cross_val", "experiment_runner",
        "result_saver", "model_wrappers", "build_acos", 
        "tokenize_data", "selftest"
    ]
    acos_id_dir = os.path.join(indo_path, 'acos_id')
    missing = []
    for m in ACOS_ID_MODULES:
        fpath = os.path.join(acos_id_dir, f"{m}.py")
        if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
            missing.append(f"{m}.py")
    return len(missing) == 0, missing
```

**Kandidat Path:**
```python
kandidat = [
    "/shared-docker/ACOS",                    # Docker
    "d:/laragon/www/ACOS-ASLI",              # Windows local
    "/content/drive/MyDrive/ACOS",           # Colab Drive
    "/content/drive/MyDrive/ACOS-ASLI",
    str(Path.cwd().parent.parent),
    str(Path.cwd().parent),
    str(Path.cwd()),
]
```

**Fungsi `sync_to_gdrive()`:** ⭐ BARU V5.1
```python
def sync_to_gdrive(source_path, subdir=''):
    """Mirror file/folder ke Google Drive bila termount.
    
    Args:
        source_path: Path lokal file/folder
        subdir: Subfolder di Drive (relatif dari GDRIVE_ACOS_INDO)
    
    Returns:
        bool: True bila sukses sync
    """
    if not DRIVE_SYNC or not os.path.exists(GDRIVE_ACOS_INDO):
        return False
    
    try:
        dest_dir = os.path.join(GDRIVE_ACOS_INDO, GDRIVE_BACKUP_SUBDIR, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        
        if os.path.isdir(source_path):
            dest = os.path.join(dest_dir, os.path.basename(source_path))
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source_path, dest)
        else:
            shutil.copy2(source_path, dest_dir)
        
        print(f"  📤 Synced to Drive: {subdir}/{os.path.basename(source_path)}")
        return True
    except Exception as e:
        print(f"  ⚠️ Drive sync failed: {e}")
        return False
```

**Output:**
```
✓ Found valid upstream: /content/Extract-Classify-ACOS

=================================================================
✅ PATHS CONFIGURED SUCCESSFULLY
=================================================================
  base_project_dir : /content
  upstream_root    : /content/Extract-Classify-ACOS
  indo_root        : /content/ACOS-IndoBERT
  modeling.py      : True
  bert_utils/      : True

Importing modules...
  ✓ BertTokenizer
  ✓ BertForQuadABSA
  ✓ acos_id v0.3.1
  ✓ ExperimentGrid
  ✓ ResultSaver
```

---

#### **Sel 4: HardwareMonitor** ⭐ DUAL-BACKEND

**Kelas Monitor:**
```python
class HardwareMonitor:
    """Monitor real-time VRAM & utilization untuk ROCm dan CUDA.
    
    Features:
    - Dual-backend (ROCm/CUDA) detection
    - Per-epoch VRAM tracking
    - Per-run aggregation
    - JSON export (hardware_log.json)
    """
    
    def __init__(self, log_dir, device=0):
        self.log_dir = log_dir
        self.device = device
        self.backend = globals().get('BACKEND', 'cpu')
        self.run_logs = []
        
    def _get_vram(self):
        """Baca VRAM current via torch (universal)."""
        if not torch.cuda.is_available():
            return {'used_gb': 0.0, 'total_gb': 0.0}
        
        used = torch.cuda.memory_allocated(self.device) / (1024**3)
        total = torch.cuda.get_device_properties(self.device).total_memory / (1024**3)
        return {'used_gb': used, 'total_gb': total}
    
    def vram_str(self):
        """Format VRAM untuk progress print."""
        v = self._get_vram()
        return f"{v['used_gb']:.2f}/{v['total_gb']:.2f}GB"
    
    def start_run(self, run_id, config):
        self.current_run = {
            'run_id': run_id,
            'config': config,
            'epochs': [],
            'start_time': time.time()
        }
    
    def start_epoch(self, epoch, phase='step1'):
        self.current_epoch = {
            'epoch': epoch,
            'phase': phase,
            'start_time': time.time(),
            'vram_start': self._get_vram()
        }
    
    def end_epoch(self, loss, f1, n_batches, batch_size):
        dur = time.time() - self.current_epoch['start_time']
        vram_end = self._get_vram()
        
        self.current_epoch.update({
            'duration_sec': dur,
            'loss': float(loss),
            'f1': float(f1),
            'n_batches': n_batches,
            'batch_size': batch_size,
            'samples': n_batches * batch_size,
            'samples_per_sec': (n_batches * batch_size) / dur,
            'vram_end': vram_end,
            'vram_peak': vram_end['used_gb']  # approx
        })
        
        self.current_run['epochs'].append(self.current_epoch)
    
    def end_run(self):
        self.current_run['total_duration'] = time.time() - self.current_run['start_time']
        self.run_logs.append(self.current_run)
        
        # Save to JSON
        log_path = os.path.join(self.log_dir, 'hardware_log.json')
        with open(log_path, 'w') as f:
            json.dump(self.run_logs, f, indent=2)
        
        # Sync to Drive
        if globals().get('DRIVE_SYNC'):
            sync_to_gdrive(log_path, 'logs')
```

---

### **FASE 2: Data Preparation**

#### **Sel 5: Backbone IndoBERT & Tokenizer**

**Cache Checkpoint:**
```python
from acos_id.checkpoint import ensure_indobert_cached

bert_cache_dir = ensure_indobert_cached(
    indo_root=indo_root,
    pretrained_name='indobenchmark/indobert-base-p1',
    force_download=False
)

print(f"✅ Backbone cached: {bert_cache_dir}")
print(f"   - pytorch_model.bin: {os.path.getsize(os.path.join(bert_cache_dir, 'pytorch_model.bin')) / (1024**2):.1f} MB")
print(f"   - vocab.txt: {len(open(os.path.join(bert_cache_dir, 'vocab.txt')).readlines())} tokens")
```

**Tokenizer:**
```python
from bert_utils.tokenization import BertTokenizer

tokenizer = BertTokenizer.from_pretrained(
    bert_cache_dir,
    do_lower_case=DO_LOWER_CASE
)

print(f"✅ Tokenizer loaded")
print(f"   - vocab_size: {len(tokenizer.vocab)}")
print(f"   - do_lower_case: {tokenizer.do_lower_case}")
print(f"   - sample tokens: {list(tokenizer.vocab.keys())[:10]}")
```

---

#### **Sel 5b: EDA + Visualisasi** ⭐ BARU V5.1

**Import:**
```python
from acos_id.eda import (
    count_split_sizes,
    analyze_categories_sentiments,
    analyze_implicit_stats,
    plot_distribution_bars,
    plot_category_sentiment_heatmap,
    export_eda_summary
)
```

**Analisis:**
```python
# 1. Statistik split
split_stats = count_split_sizes(data_root, DOMAIN)
print(f"Train: {split_stats['train']} samples")
print(f"Dev:   {split_stats['dev']} samples")
print(f"Test:  {split_stats['test']} samples")

# 2. Kategori & sentiment
cat_sent_stats = analyze_categories_sentiments(data_root, DOMAIN)
print(f"Top-5 categories:")
for cat, cnt in cat_sent_stats['top_categories'][:5]:
    print(f"  {cat}: {cnt}")

# 3. Implisit
implicit_stats = analyze_implicit_stats(data_root, DOMAIN)
print(f"Implicit aspects: {implicit_stats['implicit_aspect_pct']:.1f}%")
print(f"Implicit opinions: {implicit_stats['implicit_opinion_pct']:.1f}%")
```

**Visualisasi (4 PNG):**
```python
plots_dir = os.path.join(session_dir, 'plots')
os.makedirs(plots_dir, exist_ok=True)

# Plot 1: Distribusi split
plot_distribution_bars(
    split_stats,
    save_path=os.path.join(plots_dir, 'eda_split_distribution.png'),
    dpi=300
)

# Plot 2: Top-10 kategori
plot_distribution_bars(
    {'categories': cat_sent_stats['top_categories'][:10]},
    save_path=os.path.join(plots_dir, 'eda_top_categories.png'),
    dpi=300
)

# Plot 3: Sentiment pie chart
plot_sentiment_pie(
    cat_sent_stats['sentiment_counts'],
    save_path=os.path.join(plots_dir, 'eda_sentiment_distribution.png'),
    dpi=300
)

# Plot 4: Heatmap kategori × sentiment
plot_category_sentiment_heatmap(
    cat_sent_stats['category_sentiment_matrix'],
    save_path=os.path.join(plots_dir, 'eda_category_sentiment_heatmap.png'),
    dpi=300
)
```

**Export Tabel:**
```python
csv_dir = os.path.join(session_dir, 'csv')
os.makedirs(csv_dir, exist_ok=True)

export_eda_summary(
    split_stats=split_stats,
    cat_sent_stats=cat_sent_stats,
    implicit_stats=implicit_stats,
    output_path=os.path.join(csv_dir, f'eda_summary_{DOMAIN}.csv')
)
```

**Sync ke Drive:**
```python
if DRIVE_SYNC:
    sync_to_gdrive(plots_dir, 'plots')
    sync_to_gdrive(csv_dir, 'csv')
```

---

#### **Sel 6: ExperimentGrid Preview** ⭐

**Generator Grid:**
```python
from acos_id.experiment_runner import ExperimentGrid

grid = ExperimentGrid(
    domain=DOMAIN,
    indo_root=indo_root,
    epoch_list=EXPERIMENT_EPOCHS,
    ratio_list=EXPERIMENT_RATIOS,
    cv_configs=EXPERIMENT_CV,
    seed=SEED,
    mode=RUN_MODE  # 'all' / 'ratio' / 'cv'
)

# Preview tanpa training
configs = grid.generate_configs()
print(f"Total configurations: {len(configs)}")
print(f"\nFirst 3 configs:")
for i, cfg in enumerate(configs[:3]):
    print(f"\n  [{i+1}] {cfg['run_id']}")
    print(f"      epochs: {cfg['epochs']}")
    print(f"      split:  {cfg.get('split_type', 'N/A')}")
    print(f"      result: {cfg['result_dir']}")
```

**Tabel Grid:**
```python
df_grid = pd.DataFrame([
    {
        'Run ID': cfg['run_id'],
        'Epochs': cfg['epochs'],
        'Split Type': cfg.get('split_type', 'cv'),
        'Train%': f"{cfg.get('train_ratio', 0)*100:.0f}" if 'train_ratio' in cfg else f"fold_{cfg.get('fold', '?')}",
        'Result Dir': os.path.basename(cfg['result_dir'])
    }
    for cfg in configs
])

print(df_grid.to_string(index=False))
```

**Output:**
```
Total configurations: 54

First 3 configs:

  [1] appsid_50ep_ratio80_10
      epochs: 50
      split:  ratio
      result: results/appsid_50ep_ratio80_10_26092026_143022

  [2] appsid_50ep_ratio70_15
      epochs: 50
      split:  ratio
      result: results/appsid_50ep_ratio70_15_26092026_143022

  [3] appsid_50ep_ratio60_20
      epochs: 50
      split:  ratio
      result: results/appsid_50ep_ratio60_20_26092026_143022
```

---

#### **Sel 7: Persiapan Data** ⭐ CACHED 1X

**Fungsi Persiapan:**
```python
from acos_id.experiment_runner import prepare_all_data

prepared = prepare_all_data(
    indo_root=indo_root,
    tokenizer=tokenizer,
    ratio_list=EXPERIMENT_RATIOS,
    cv_configs=EXPERIMENT_CV,
    seed=SEED,
    force_rebuild=FORCE_REBUILD_DATA
)
```

**Proses Internal:**
```
1. Build TSV mentah (dari JSON raw)
   - appsid_quad_train.tsv
   - appsid_quad_dev.tsv
   - appsid_quad_test.tsv

2. Split custom ratio (80:10:10, 70:15:15, 60:20:20)
   - Level review_id (anti-bocor)
   - Output: tokenized_data/appsid_ratio<train>_<dev>/

3. Cross-validation fold (5-fold, 10-fold)
   - StratifiedKFold per review_id
   - Output: tokenized_data/appsid_cv<n>_fold<k>/

4. Tokenisasi semua split
   - features_step1: input_ids, attention_mask, label_ids
   - features_step2: pair features + category/sentiment labels
   - Disimpan: *.pt (torch.save)
```

**Output:**
```
Waktu estimasi: 30-60 menit (1x saja)

🔧 Preparing data...
  ✓ Base split (train/dev/test): 3 files
  ✓ Ratio 80:10:10 → 3 files tokenized
  ✓ Ratio 70:15:15 → 3 files tokenized
  ✓ Ratio 60:20:20 → 3 files tokenized
  ✓ CV 5-fold → 15 files tokenized (5 folds × 3 splits)
  ✓ CV 10-fold → 30 files tokenized (10 folds × 3 splits)

Total: 54 tokenized file sets
Total waktu persiapan data: 42m 18s
Semua data siap untuk training.
```

**Caching:**
- Pemanggilan kedua: skip file yang sudah ada (deteksi via `os.path.exists`)
- Force rebuild: set `FORCE_REBUILD_DATA=True` di Sel 2

---

### **FASE 3: Training Loop**

#### **Sel 8: Training Adapter Function**

**Signature:**
```python
def train_one_run(cfg: dict) -> dict:
    """Jalankan 1 run lengkap (Step 1 + Step 2).
    
    Args:
        cfg: Dictionary dari ExperimentGrid
            - cfg['run_id']: Nama unik run
            - cfg['epochs']: Jumlah epoch
            - cfg['tokenized_dir']: Folder tokenized data
            - cfg['result_dir']: Folder output
            - cfg['seed']: Random seed
    
    Returns:
        Dictionary hasil:
            - 'run_id': str
            - 'step1_best_f1': float
            - 'step2_best_f1': float
            - 'full_quad_f1': float
            - 'duration_sec': float
            - 'vram_peak_gb': float
    """
```

**Step 1: Co-Extraction (BERT-CRF):**
```python
# Load data
train_loader = load_loader('train', STEP1_BATCH_SIZE, shuffle=True)
dev_loader = load_loader('dev', STEP1_BATCH_SIZE, shuffle=False)

# Model
model = BertForQuadABSA.from_pretrained(
    bert_cache_dir,
    num_labels=acos_taxonomy.num_labels_step1()
).to(DEVICE)

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=STEP1_LR)

# AMP Scaler
scaler = torch.cuda.amp.GradScaler() if USE_AMP and HAS_CUDA else None

# Training loop
for epoch in range(1, num_epochs + 1):
    monitor.start_epoch(epoch, phase='step1')
    model.train()
    total_loss = 0.0
    
    for step, batch in enumerate(train_loader):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}
        optimizer.zero_grad()
        
        if USE_AMP and scaler:
            dtype = torch.bfloat16 if AMP_DTYPE=='bfloat16' else torch.float16
            with torch.cuda.amp.autocast(dtype=dtype):
                outputs = model(**batch)
                loss = outputs['loss'] / GRAD_ACCUM_STEPS
            
            scaler.scale(loss).backward()
            
            if (step + 1) % GRAD_ACCUM_STEPS == 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
        else:
            outputs = model(**batch)
            loss = outputs['loss'] / GRAD_ACCUM_STEPS
            loss.backward()
            
            if (step + 1) % GRAD_ACCUM_STEPS == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
        
        total_loss += loss.item() * GRAD_ACCUM_STEPS
        
        # Progress print
        if LOG_EVERY_N_STEPS > 0 and (step + 1) % LOG_EVERY_N_STEPS == 0:
            elapsed = time.time() - epoch_start
            sps = (step * STEP1_BATCH_SIZE) / elapsed
            print(f"    ep{epoch:3d} step{step+1:4d} "
                  f"loss={loss.item():.4f} "
                  f"VRAM={monitor.vram_str()} "
                  f"samp/s={sps:.0f}", end='\r')
    
    # Evaluasi
    eval_results = model_wrappers.compute_extraction_metrics(model, dev_loader, DEVICE)
    f1 = eval_results['f1']
    
    avg_loss = total_loss / len(train_loader)
    monitor.end_epoch(avg_loss, f1, len(train_loader), STEP1_BATCH_SIZE)
    
    # Save best
    if f1 > best_f1_s1:
        best_f1_s1 = f1
        ckpt_path = os.path.join(sess['checkpoints'], 'step1_best')
        model.save_pretrained(ckpt_path)
        print(f"    >> Best checkpoint: ep{epoch} F1={f1:.2f}%")
    
    # VRAM flush (penting untuk T4/L4)
    if VRAM_FLUSH_EPOCH:
        torch.cuda.empty_cache()
```

**Step 2: Category-Sentiment Classification:**
```python
# Implementasi serupa Step 1, tapi:
# - Load pair.tsv (bukan quad.tsv)
# - Model: CategorySentiClassification (bukan BertForQuadABSA)
# - num_labels: 39 (13 categories × 3 sentiments)
# - Evaluasi: multi-label F1
```

**ResultSaver Integration:**
```python
from acos_id.result_saver import ResultSaver

saver = ResultSaver(run_dir=cfg['result_dir'])
saver.init(config=cfg)

# Per-epoch logging
saver.log_epoch_step1(
    epoch=epoch,
    loss=avg_loss,
    f1=f1,
    tp=eval_results.get('tp', 0),
    fp=eval_results.get('fp', 0),
    fn=eval_results.get('fn', 0),
    vram_gb=monitor._get_vram()['used_gb'],
    duration_sec=epoch_duration,
    samples_per_sec=samples_per_sec
)

# Final save
saver.save_training_history_step1()
saver.save_training_plots()
saver.save_markdown_report()
saver.save_final_metrics()

# Sync to Drive
if DRIVE_SYNC:
    sync_to_gdrive(cfg['result_dir'], 'results')
```

---

#### **Sel 9: Run Semua Eksperimen** ⭐ OTOMATIS

**Loop Eksekusi:**
```python
# Sel 9: Run 54 kombinasi otomatis (5-8 hari)
from acos_id.experiment_runner import ExperimentGrid

grid = ExperimentGrid(
    domain=DOMAIN,
    indo_root=indo_root,
    epoch_list=RUN_EPOCHS,  # [50, 75, 100] atau [50] untuk test
    ratio_list=EXPERIMENT_RATIOS,
    cv_configs=EXPERIMENT_CV,
    seed=SEED,
    mode=RUN_MODE
)

configs = grid.generate_configs()
total = len(configs)

print(f"========================================")
print(f"🚀 STARTING {total} EXPERIMENT RUNS")
print(f"========================================")
print(f"DRY_RUN: {DRY_RUN}")
print(f"Estimasi: {'Preview only' if DRY_RUN else f'{total * 2} - {total * 4} jam'}")
print()

if DRY_RUN:
    print("⚠️ DRY_RUN aktif — tidak ada training sungguhan.")
    print("   Set DRY_RUN=False di Sel 2 untuk eksekusi penuh.")
    print()
    for i, cfg in enumerate(configs, 1):
        print(f"  [{i:2d}/{total}] {cfg['run_id']:40s} | "
              f"ep={cfg['epochs']:3d} | {cfg.get('split_type', 'cv'):5s}")
else:
    results = []
    for i, cfg in enumerate(configs, 1):
        print(f"\n{'='*70}")
        print(f"RUN {i}/{total}: {cfg['run_id']}")
        print(f"{'='*70}")
        
        t0_run = time.time()
        try:
            result = train_one_run(cfg)
            result['status'] = 'success'
        except Exception as e:
            print(f"❌ Run failed: {e}")
            result = {'run_id': cfg['run_id'], 'status': 'failed', 'error': str(e)}
        
        result['duration_total'] = time.time() - t0_run
        results.append(result)
        
        # Save intermediate results
        results_json = os.path.join(indo_root, 'results', 'all_runs_results.json')
        with open(results_json, 'w') as f:
            json.dump(results, f, indent=2)
        
        if DRIVE_SYNC:
            sync_to_gdrive(results_json, 'results')
        
        print(f"\n✅ Run {i}/{total} selesai dalam {_fmt_dur(result['duration_total'])}")
        print(f"   Step1 F1: {result.get('step1_best_f1', 0):.2f}%")
        print(f"   Step2 F1: {result.get('step2_best_f1', 0):.2f}%")
        print(f"   Full Quad F1: {result.get('full_quad_f1', 0):.2f}%")
    
    print(f"\n{'='*70}")
    print(f"🎉 SEMUA {total} RUN SELESAI!")
    print(f"{'='*70}")
```

**Output:**
```
========================================
🚀 STARTING 54 EXPERIMENT RUNS
========================================
DRY_RUN: False
Estimasi: 108 - 216 jam (4.5 - 9 hari)

======================================================================
RUN 1/54: appsid_50ep_ratio80_10_26092026_143022
======================================================================
  [Step 1] 50 epoch | batch=16 | AMP=True(float16) | PATIENCE=0
    ep  1 step  10 loss=0.4521 VRAM=8.23/14.56GB samp/s=124
    ep  1 step  20 loss=0.3892 VRAM=8.23/14.56GB samp/s=126
    ...
    ep 50 step 120 loss=0.0892 VRAM=8.23/14.56GB samp/s=128
    >> Best checkpoint: ep47 F1=78.94%
  
  [Step 1] SELESAI | Best F1=78.94% di ep47
  
  [Step 2] 50 epoch | batch=8 | AMP=True(float16)
    ...
  
  [Step 2] SELESAI | Best F1=71.23% di ep49

✅ Run 1/54 selesai dalam 2j 14m 32s
   Step1 F1: 78.94%
   Step2 F1: 71.23%
   Full Quad F1: 68.45%

======================================================================
RUN 2/54: appsid_50ep_ratio70_15_26092026_143022
======================================================================
...
```

---

### **FASE 4: Analisis & Pelaporan**

#### **Sel 10: Agregasi & Perbandingan**

**Load Semua Hasil:**
```python
results_json = os.path.join(indo_root, 'results', 'all_runs_results.json')
with open(results_json) as f:
    all_results = json.load(f)

df_results = pd.DataFrame(all_results)
df_results = df_results[df_results['status'] == 'success']

print(f"Total successful runs: {len(df_results)}")
```

**Tabel Best Models:**
```python
# Best per epoch setting
best_per_epoch = df_results.groupby('epochs').apply(
    lambda g: g.loc[g['full_quad_f1'].idxmax()]
).reset_index(drop=True)

print("\n📊 Best Model Per Epoch Setting:")
print(best_per_epoch[['run_id', 'epochs', 'full_quad_f1', 'step1_best_f1', 'step2_best_f1']].to_string(index=False))
```

**Plot Comparison:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Plot 1: F1 vs Epochs
fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
for split_type in df_results['split_type'].unique():
    subset = df_results[df_results['split_type'] == split_type]
    ax.plot(subset['epochs'], subset['full_quad_f1'], 
            marker='o', label=split_type)

ax.set_xlabel('Epochs')
ax.set_ylabel('Full Quadruple F1 (%)')
ax.set_title('ACOS Performance vs Epochs')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'comparison_f1_vs_epochs.png'), dpi=300)
plt.close()

# Plot 2: Box plot per split ratio
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ratio_df = df_results[df_results['split_type'] == 'ratio']
sns.boxplot(data=ratio_df, x='train_ratio', y='full_quad_f1', ax=ax)
ax.set_xlabel('Train Ratio')
ax.set_ylabel('Full Quadruple F1 (%)')
ax.set_title('Performance Distribution Across Split Ratios')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'comparison_boxplot_ratios.png'), dpi=300)
plt.close()

# Plot 3: Heatmap CV performance
cv_df = df_results[df_results['split_type'] == 'cv']
pivot = cv_df.pivot_table(values='full_quad_f1', 
                           index='n_splits', 
                           columns='epochs', 
                           aggfunc='mean')
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlGnBu', ax=ax)
ax.set_title('CV Performance: F1 (%) Heatmap')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'comparison_cv_heatmap.png'), dpi=300)
plt.close()

print(f"\n✅ Saved 3 comparison plots to {plots_dir}")
```

**Export Tabel:**
```python
# CSV lengkap
df_results.to_csv(os.path.join(csv_dir, 'all_runs_results.csv'), index=False)

# Excel dengan multiple sheets
with pd.ExcelWriter(os.path.join(csv_dir, 'all_runs_report.xlsx'), engine='openpyxl') as writer:
    df_results.to_excel(writer, sheet_name='All_Runs', index=False)
    best_per_epoch.to_excel(writer, sheet_name='Best_Per_Epoch', index=False)
    ratio_df.to_excel(writer, sheet_name='Ratio_Splits', index=False)
    cv_df.to_excel(writer, sheet_name='CV_Folds', index=False)

print(f"✅ Exported Excel report: all_runs_report.xlsx")
```

---

#### **Sel 11: Hardware Summary** ⭐ FINAL REPORT

**Aggregate Hardware Logs:**
```python
hardware_logs = []
for result in all_results:
    if result['status'] != 'success':
        continue
    
    log_path = os.path.join(result['result_dir'], 'hardware_log.json')
    if os.path.exists(log_path):
        with open(log_path) as f:
            log = json.load(f)
            hardware_logs.append({
                'run_id': result['run_id'],
                'total_duration_hr': log['total_duration'] / 3600,
                'avg_vram_gb': np.mean([e['vram_peak'] for e in log['epochs']]),
                'peak_vram_gb': np.max([e['vram_peak'] for e in log['epochs']]),
                'avg_samples_per_sec': np.mean([e['samples_per_sec'] for e in log['epochs']]),
                'backend': log['config']['backend']
            })

df_hw = pd.DataFrame(hardware_logs)

print("\n🖥️ Hardware Usage Summary:")
print(f"Total runtime: {df_hw['total_duration_hr'].sum():.1f} hours")
print(f"Avg VRAM: {df_hw['avg_vram_gb'].mean():.2f} GB")
print(f"Peak VRAM: {df_hw['peak_vram_gb'].max():.2f} GB")
print(f"Avg throughput: {df_hw['avg_samples_per_sec'].mean():.0f} samples/sec")
```

**REPORT_INDEX.md:** ⭐
```python
report_index = f"""# ACOS V5.1 Experiment Report

**Session:** {SESSION_START_TS}  
**Domain:** {DOMAIN}  
**Backbone:** {BACKBONE}  
**GPU:** {GPU_NAME} ({TOTAL_VRAM_GB:.2f} GB)  
**Backend:** {BACKEND}  
**Tier:** {TIER}

---

## Executive Summary

- **Total Runs:** {len(all_results)}
- **Successful:** {len(df_results)}
- **Failed:** {len(all_results) - len(df_results)}
- **Total Runtime:** {df_hw['total_duration_hr'].sum():.1f} hours
- **Best F1:** {df_results['full_quad_f1'].max():.2f}% (Run: {df_results.loc[df_results['full_quad_f1'].idxmax(), 'run_id']})

---

## Best Models

{best_per_epoch[['run_id', 'epochs', 'full_quad_f1', 'step1_best_f1', 'step2_best_f1']].to_markdown(index=False)}

---

## Files

### Results
- `all_runs_results.json` — Raw results
- `all_runs_results.csv` — Tabel lengkap
- `all_runs_report.xlsx` — Excel multi-sheet

### Plots
- `comparison_f1_vs_epochs.png` — Performance curve
- `comparison_boxplot_ratios.png` — Ratio distribution
- `comparison_cv_heatmap.png` — CV performance heatmap

### Hardware
- `hardware_summary.csv` — Resource usage
- Individual `results/*/hardware_log.json`

---

## Drive Location

All files synced to: `{GDRIVE_ACOS_INDO}/{GDRIVE_BACKUP_SUBDIR}/`

Direct link: {GDRIVE_URL}

---

*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

report_path = os.path.join(indo_root, 'results', 'REPORT_INDEX.md')
with open(report_path, 'w') as f:
    f.write(report_index)

print(f"\n✅ Final report saved: {report_path}")
```

**Final Drive Sync:**
```python
if DRIVE_SYNC:
    print("\n📤 Final sync to Google Drive...")
    sync_to_gdrive(os.path.join(indo_root, 'results'), '')
    print("✅ All files synced to Drive!")
    print(f"   📂 {GDRIVE_ACOS_INDO}/{GDRIVE_BACKUP_SUBDIR}/")
    print(f"   🔗 {GDRIVE_URL}")
```

---

## 📊 Output Struktur Lengkap V5.1

```
ACOS-IndoBERT/
├── results/
│   ├── REPORT_INDEX.md                           # 📄 Master report
│   ├── all_runs_results.json                     # Raw results
│   ├── all_runs_results.csv
│   ├── all_runs_report.xlsx
│   ├── hardware_summary.csv
│   │
│   ├── appsid_50ep_ratio80_10_26092026_143022/   # Run 1
│   │   ├── csv/
│   │   │   ├── step1_training_history.csv
│   │   │   ├── step2_training_history.csv
│   │   │   └── final_metrics.csv
│   │   ├── plots/
│   │   │   ├── step1_training_curve.png
│   │   │   ├── step2_training_curve.png
│   │   │   └── confusion_matrix.png
│   │   ├── checkpoints/
│   │   │   ├── step1_best/
│   │   │   │   ├── pytorch_model.bin
│   │   │   │   └── config.json
│   │   │   └── step2_best/
│   │   │       ├── pytorch_model.bin
│   │   │       └── config.json
│   │   ├── logs/
│   │   │   ├── step1_progress.json
│   │   │   └── step2_progress.json
│   │   ├── hardware_log.json
│   │   ├── run_summary.md
│   │   └── session_manifest.json
│   │
│   ├── appsid_50ep_ratio70_15_26092026_143022/   # Run 2
│   ├── appsid_50ep_ratio60_20_26092026_143022/   # Run 3
│   ├── ... (51 more runs)
│   │
│   └── comparison_plots/
│       ├── comparison_f1_vs_epochs.png
│       ├── comparison_boxplot_ratios.png
│       └── comparison_cv_heatmap.png
│
├── tokenized_data/
│   ├── appsid_base/                              # Base split
│   ├── appsid_ratio80_10/                        # Ratio splits
│   ├── appsid_ratio70_15/
│   ├── appsid_ratio60_20/
│   ├── appsid_cv5_fold0/                         # CV folds
│   ├── appsid_cv5_fold1/
│   ├── ... (5-fold × 5 = 25 folders)
│   └── appsid_cv10_fold0/                        # 10-fold × 10 = 100 folders
│
├── backbones/
│   └── indobert/
│       ├── pytorch_model.bin
│       ├── config.json
│       └── vocab.txt
│
└── data/
    └── Apps-ACOS/
        ├── raw/
        └── processed/
            ├── appsid_quad_train.tsv
            ├── appsid_quad_dev.tsv
            └── appsid_quad_test.tsv
```

---

## 🚀 Cara Menjalankan V5.1

### **Mode 1: Preview (Dry Run)**
```python
# Sel 2: Edit CONFIG
CONFIG['DRY_RUN'] = True
CONFIG['RUN_EPOCHS'] = [50]  # Test 1 epoch-set saja

# Run Sel 1-9
# Output: Preview 9 kombinasi (3 ratio × 3 epoch) tanpa training
```

### **Mode 2: Smoke Test (T4, 1 Ratio)**
```python
# Sel 2
CONFIG['GPU_TIER_OVERRIDE'] = 'SMALL'
CONFIG['RUN_MODE'] = 'ratio'
CONFIG['RUN_EPOCHS'] = [50]
CONFIG['EXPERIMENT_RATIOS'] = [(0.8, 0.1)]  # 1 ratio saja
CONFIG['EXPERIMENT_CV'] = []  # Skip CV
CONFIG['DRY_RUN'] = False

# Total runs: 1 epoch × 1 ratio = 1 run (~2-3 jam)
```

### **Mode 3: Full Experiment (MI300X, 54 Run)**
```python
# Sel 2
CONFIG['GPU_TIER_OVERRIDE'] = 'LARGE'
CONFIG['RUN_MODE'] = 'all'
CONFIG['RUN_EPOCHS'] = None  # Use EXPERIMENT_EPOCHS [50, 75, 100]
CONFIG['DRY_RUN'] = False
CONFIG['DRIVE_SYNC'] = True

# Total runs: 54 (~5-8 hari)
# Resume-able: bila crash, set RESUME=True
```

### **Mode 4: Environment Override (Tanpa Edit File)**
```bash
# Terminal / Colab
export ACOS_TIER=SMALL
export ACOS_MODE=ratio
export ACOS_DRY=false
export ACOS_EPOCHS="[50]"
export ACOS_BATCH1=16
export ACOS_BATCH2=8

# Lalu run notebook tanpa edit Sel 2
```

---

## 🔧 Fitur Unggulan V5.1

### **1. Dual-Backend Detection** ⭐
```python
HAS_ROCM = 'rocm' in torch.__version__.lower()
HAS_CUDA = torch.cuda.is_available() and not HAS_ROCM
BACKEND = 'rocm' if HAS_ROCM else ('cuda' if HAS_CUDA else 'cpu')

# AMP dtype adaptif
AMP_DTYPE = 'bfloat16' if BACKEND == 'rocm' else 'float16'
```

### **2. Tier Adaptif Otomatis** ⭐
- **Deteksi:** `GPU_TIER = 'SMALL/MEDIUM/LARGE'`
- **Preset:** Batch, accum, worker, AMP, cache, resume
- **Override:** Via `CONFIG['GPU_TIER_OVERRIDE']` atau `ACOS_TIER` env

### **3. ExperimentGrid Generator** ⭐
- 54 kombinasi: 3 epoch × (3 ratio + 5 + 10 fold)
- Isolated runs (tidak interfere)
- Resume-able setiap run

### **4. Drive Sync Built-in** ⭐
```python
sync_to_gdrive(source_path, subdir)
# Mirror otomatis: checkpoints, plots, CSV, JSON, MD
```

### **5. ResultSaver Komprehensif** ⭐
- Per-epoch CSV
- Training plots (300 DPI)
- Markdown report per-run
- Hardware log JSON
- Session manifest

### **6. Cross-Validation Native** ⭐
- 5-fold & 10-fold
- StratifiedKFold per review_id
- Anti-bocor guarantee

### **7. EDA + Visualisasi (ala V4)** ⭐
- 4 PNG: split, kategori, sentiment, heatmap
- Tabel CSV summary
- Sync ke Drive

### **8. HardwareMonitor Dual-Backend** ⭐
- Real-time VRAM tracking
- Per-epoch aggregation
- ROCm & CUDA support
- JSON export

### **9. Crash-Resistant** ⭐
- Per-run isolated
- Resume dari run terakhir
- Intermediate results saved
- Drive backup otomatis

### **10. One-Cell Config** ⭐
- Hanya edit Sel 2
- Environment override available
- Preset adaptif
- Validation built-in

---

## 📝 Catatan Penting

1. **Sel 2 adalah satu-satunya sel yang perlu diedit**
2. **PATIENCE=0 di semua tier** (no early stop, warisan V5)
3. **Sel 7 hanya perlu dijalankan 1x** (data cached)
4. **DRY_RUN=True untuk preview** sebelum training sungguhan
5. **Drive sync otomatis** bila `DRIVE_SYNC=True`
6. **Resume-able:** Set `RESUME=True` bila crash di tengah
7. **Tier override:** `GPU_TIER_OVERRIDE` atau env `ACOS_TIER`
8. **Estimasi total:** 5-8 hari untuk 54 run (MI300X)

---

## 🆚 Perbandingan V4 vs V5.1

| Aspek | V4 | V5.1 |
|-------|----|----|
| **Platform** | Manual config | Auto-detect ROCm/CUDA/CPU |
| **Eksperimen** | Single run | 54 run grid |
| **Batch** | Fixed | Tier adaptif |
| **CV** | Manual | 5/10-fold built-in |
| **Drive Sync** | Manual | Auto + resume |
| **EDA** | Manual per-step | 1-click (Sel 5b) |
| **Monitoring** | Basic | HardwareMonitor dual-backend |
| **Config** | Multi-cell edit | One-cell (Sel 2) |
| **Resume** | Manual | Auto (crash-resistant) |
| **Output** | Local only | Local + Drive mirror |

---

## 📚 Referensi

- **Notebook V5.1:** `01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_DriveSync.ipynb`
- **Paket Indonesia:** `acos_id/` (v0.3.1)
  - `experiment_runner.py` — ExperimentGrid
  - `result_saver.py` — ResultSaver
  - `cross_val.py` — StratifiedKFold
  - `model_wrappers.py` — Training adapters
- **Dataset:** Apps-ACOS (13 kategori, 1,585 reviews)
- **Backbone:** IndoBERT Base (Phase 1)
- **Drive:** https://drive.google.com/drive/folders/1AEzC-dncJAweHPHUPdnFfPHxbsCa83_K

---

**Dokumen ini adalah penanda resmi Versi V5.1.**  
Semua tahapan, tier adaptif, grid eksperimen, dan output telah didokumentasikan.

---

*Generated: 26 September 2026*  
*Author: ACOS Pipeline V5.1 Documentation System*
