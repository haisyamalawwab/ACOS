import json
import ast
import os
import sys

def build_notebook():
    cells = []

    def add_md(source):
        if isinstance(source, str):
            lines = [l + "\n" for l in source.strip().split("\n")]
            if lines:
                lines[-1] = lines[-1].rstrip("\n")
        else:
            lines = source
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": lines
        })

    def add_code(source):
        if isinstance(source, str):
            lines = [l + "\n" for l in source.strip().split("\n")]
            if lines:
                lines[-1] = lines[-1].rstrip("\n")
        else:
            lines = source
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines
        })

    # CELL 0: Title Markdown
    add_md("""# 00. ACOS Master Pipeline: End-to-End Execution (Production PRO Version)

**Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction with Implicit Aspects and Opinions**

This production-grade master notebook executes the **entire ACOS benchmark pipeline with 1-Click** on **Google Colab** (with automatic Google Drive persistence at `/content/drive/MyDrive/ACOS`) or on a **Local Environment** (Windows / Linux):

1. **Environment Setup & GPU Diagnostics:** Automatic Google Drive mounting, dependency installation, and detailed GPU / VRAM inspection.
2. **Dynamic Path Architecture (Zero Hardcoded Paths):** Seamless switching between Google Drive `/content/drive/MyDrive/ACOS` and local project workspace.
3. **Pretrained BERT Offline Caching:** Directly caches `bert-base-uncased` from HuggingFace Hub to prevent legacy S3 URL deprecation errors.
4. **Exploratory Data Analysis (EDA):** High-resolution publication plots (300 DPI) and structured CSV exports with auto-caching.
5. **Step 1 (Aspect-Opinion Co-Extraction):** Trains and evaluates BERT-CRF, saves best model checkpoint, tracks peak VRAM, exports `pred4pipeline.txt`, and auto-skips if already trained.
6. **Smart State Checkpoint & Multi-Tier Recovery:** Persists complete runtime state (`pipeline_state.pkl`) and provides seamless fallback auto-loading across all cells.
7. **Candidate Pair Generation Bridge:** Forms Cartesian candidate pairs `(aspect, opinion)` with implicit entity handling `[-1, -1]`.
8. **Step 2 (Category-Sentiment Classification):** Trains multi-label classifier, saves best checkpoint, predicts full quadruples, and auto-skips if already trained.
9. **Benchmark Dashboard & 15 Subtask Metrics:** Evaluates complete quadruple extraction and exports `master_metrics.json`.
10. **MCP (Model Context Protocol) Ready:** Emits real-time `session_manifest.json` tracking pipeline lifecycle states.
11. **Live Interactive Inference:** Color-coded two-stage quadruple extraction on arbitrary customer review text with automatic model loading.""")

    # CELL 1: Section 1 Markdown
    add_md("""## 1. Environment Setup, Google Drive Mounting & GPU Diagnostics""")

    # CELL 2: Code Section 1
    add_code("""# 1. Mount Google Drive jika di Colab
try:
    from google.colab import drive
    drive.mount('/content/drive')
    print("✅ Google Drive berhasil di-mount pada /content/drive")
except Exception:
    print("💻 Berjalan pada lingkungan Lokal / Colab tanpa drive mount.")

# 2. Instalasi dependensi yang dibutuhkan
!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm

import os
import sys
import random
import json
import shutil
import pickle
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch

# 3. GPU Hardware Diagnostics & Optimization
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\\n⚡ Perangkat Komputasi Utama: {device}")

if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    vram_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    cuda_cap = torch.cuda.get_device_capability(0)
    print(f"   GPU Model         : {gpu_name}")
    print(f"   Total VRAM        : {vram_total_gb:.2f} GB")
    print(f"   Compute Capability: {cuda_cap[0]}.{cuda_cap[1]}")
    print(f"   cuDNN Version     : {torch.backends.cudnn.version()}")
    # Aktifkan optimasi benchmark cuDNN untuk matrix/convolution ops
    torch.backends.cudnn.benchmark = True
    torch.cuda.empty_cache()
    print("   ✅ CUDA Cache dibersihkan & cuDNN benchmark diaktifkan.")
else:
    print("   ℹ️ Berjalan dengan CPU mode.")""")

    # CELL 3: Section 2 Markdown
    add_md("""## 2. Dynamic Directory Navigation & Path Initialization (Zero Hardcoded Paths)""")

    # CELL 4: Code Section 2
    add_code("""# 1. Deteksi dinamis root direktori proyek (Colab vs Lokal)
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
HAS_DRIVE = os.path.exists("/content/drive/MyDrive")

if HAS_DRIVE:
    base_project_dir = "/content/drive/MyDrive/ACOS"
    os.makedirs(base_project_dir, exist_ok=True)
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Mode Google Drive Aktif: {base_project_dir}")
    print(f"📁 Output Sesi akan disimpan di: {save_dir}")
elif os.path.exists("/content/ACOS/Extract-Classify-ACOS"):
    base_project_dir = "/content/ACOS"
    save_dir = base_project_dir
    print(f"💾 Mode Colab Ephemeral Aktif: {base_project_dir}")
elif os.path.exists("Extract-Classify-ACOS"):
    base_project_dir = os.path.abspath(".")
    save_dir = base_project_dir
    print(f"💾 Mode Lokal Aktif (Current Dir): {base_project_dir}")
elif os.path.exists("../Extract-Classify-ACOS"):
    base_project_dir = os.path.abspath("..")
    save_dir = base_project_dir
    print(f"💾 Mode Lokal Aktif (Parent Dir): {base_project_dir}")
else:
    base_project_dir = os.path.abspath("ACOS")
    os.makedirs(base_project_dir, exist_ok=True)
    save_dir = base_project_dir
    print(f"💾 Inisialisasi folder ACOS lokal: {base_project_dir}")

# 2. Auto-clone repositori ACOS jika folder inti belum tersedia
extract_dir = os.path.join(base_project_dir, "Extract-Classify-ACOS")
if not os.path.exists(extract_dir):
    print(f"📥 Repositori belum ditemukan. Mengkloning ACOS ke {base_project_dir}...")
    !git clone https://github.com/haisyamalawwab/ACOS.git /tmp/ACOS_clone
    !cp -r /tmp/ACOS_clone/* "{base_project_dir}/"
    !rm -rf /tmp/ACOS_clone
    print("✅ Repositori berhasil disinkronkan.")

data_root = os.path.join(base_project_dir, "data")
notebooks_dir = os.path.join(base_project_dir, "notebooks")

# 3. Masukkan direktori penting ke sys.path
for p in [base_project_dir, extract_dir, notebooks_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# 4. Import colab_utils dengan mekanisme fallback unduh otomatis
try:
    from colab_utils import (
        setup_timestamped_run_dir, download_bert_pretrained, analyze_and_plot_eda,
        plot_training_history, export_benchmark_tables_and_plots,
        display_quadruple_dataframe, df_to_markdown, export_step_table,
        MarkdownReport, SubtaskMetricCapture, plot_subtask_metrics,
        features_step1, features_step2, pair_examples_from_file,
        resolve_eval_pair_file, unpack_model_output,
    )
except ModuleNotFoundError:
    import urllib.request
    print("⚠️ Mengunduh modul colab_utils.py langsung dari GitHub...")
    raw_url = "https://raw.githubusercontent.com/haisyamalawwab/ACOS/main/notebooks/colab_utils.py"
    target_utils = os.path.join(base_project_dir, "colab_utils.py")
    urllib.request.urlretrieve(raw_url, target_utils)
    if base_project_dir not in sys.path:
        sys.path.insert(0, base_project_dir)
    from colab_utils import (
        setup_timestamped_run_dir, download_bert_pretrained, analyze_and_plot_eda,
        plot_training_history, export_benchmark_tables_and_plots,
        display_quadruple_dataframe, df_to_markdown, export_step_table,
        MarkdownReport, SubtaskMetricCapture, plot_subtask_metrics,
        features_step1, features_step2, pair_examples_from_file,
        resolve_eval_pair_file, unpack_model_output,
    )

print(f"📂 Base Project Directory : {base_project_dir}")
print(f"📁 Extract & Model Dir     : {extract_dir}")
print(f"📁 Dataset Data Dir        : {data_root}")
print(f"📁 Output & Save Directory : {save_dir}")""")

    # CELL 5: Section 3 Markdown
    add_md("""## 3. Master Pipeline Parameters, BERT Caching & Session Manifest""")

    # CELL 6: Code Section 3
    add_code("""# Pilihan Domain Dataset: 'rest16' (Restaurant-ACOS) atau 'laptop' (Laptop-ACOS)
DOMAIN = "rest16"

# Hyperparameter Pelatihan
MAX_SEQ_LENGTH = 128
STEP1_BATCH_SIZE = 24
STEP2_BATCH_SIZE = 16
STEP1_LR = 2e-5
STEP2_LR = 5e-5
NUM_EPOCHS = 15      # 15 epoch optimal untuk Colab GPU T4/A100 (Default paper: 30)
SEED = 42

# Reproducibility seeding
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

active_save_dir = save_dir if 'save_dir' in locals() else base_project_dir

# 1. Inisialisasi direktori sesi berbasis timestamp (DDMMYYYY_HMS)
results_base = os.path.join(active_save_dir, "results")
session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)

# 2. Unduh dan cache model pretrained BERT (HuggingFace Hub)
bert_cache_dir = os.path.join(active_save_dir, "bert_base_uncased")
download_bert_pretrained(target_dir=bert_cache_dir)

print(f"\\n📁 Active Session Folder: {session_dirs['root']}")
plots_dir = session_dirs["plots"]
csv_dir = session_dirs["csv"]
md_dir = session_dirs["md"]
logs_dir = session_dirs["logs"]

# Inisialisasi Akumulator Laporan Markdown
rep = MarkdownReport(
    f"00 - Master Pipeline ACOS End-to-End [{DOMAIN.upper()}]",
    md_dir,
    filename="00_master_pipeline.md",
    meta={
        "domain": DOMAIN, "epochs": NUM_EPOCHS,
        "step1_batch": STEP1_BATCH_SIZE, "step2_batch": STEP2_BATCH_SIZE,
        "step1_lr": STEP1_LR, "step2_lr": STEP2_LR,
        "max_seq_length": MAX_SEQ_LENGTH, "seed": SEED,
        "device": str(device), "session_dir": session_dirs["root"],
    },
)

# Helper Manifest MCP (Model Context Protocol Status Logger)
def update_mcp_manifest(status_str, stage_num, extra_info=None):
    manifest_path = os.path.join(session_dirs["root"], "session_manifest.json")
    manifest_data = {
        "session_id": os.path.basename(session_dirs["root"]),
        "status": status_str,
        "stage": stage_num,
        "domain": DOMAIN,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "hyperparameters": {
            "epochs": NUM_EPOCHS,
            "max_seq_length": MAX_SEQ_LENGTH,
            "step1_batch_size": STEP1_BATCH_SIZE,
            "step2_batch_size": STEP2_BATCH_SIZE,
            "step1_lr": STEP1_LR,
            "step2_lr": STEP2_LR,
            "seed": SEED
        },
        "session_dirs": session_dirs,
        "last_updated": datetime.now().isoformat()
    }
    if extra_info:
        manifest_data.update(extra_info)
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)
    return manifest_path

# Helper Penyimpanan State Terpadu (Menyimpan seluruh variabel & artefak runtime ke pipeline_state.pkl)
def save_pipeline_state(extra_runtime=None):
    \"\"\"Menyimpan seluruh konfigurasi, path direktori, dan artefak runtime ke pipeline_state.pkl\"\"\"
    state_file = os.path.join(session_dirs["root"], "pipeline_state.pkl")
    completed_stages = []
    _sd = session_dirs
    if os.path.exists(os.path.join(_sd["csv"], "master_01_statistik_dataset.csv")):
        completed_stages.append("EDA")
    if os.path.exists(os.path.join(_sd["step1_checkpoint"], "pytorch_model.bin")) or os.path.exists(os.path.join(_sd["logs"], "pred4pipeline.txt")):
        completed_stages.append("STEP1")
    if os.path.exists(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")):
        completed_stages.append("PAIRS")
    if os.path.exists(os.path.join(_sd["step2_checkpoint"], "pytorch_model.bin")):
        completed_stages.append("STEP2")
    if os.path.exists(os.path.join(_sd["logs"], "master_metrics.json")):
        completed_stages.append("EVAL")

    _serializable = {}
    for _v in ["label_list_step1", "label_list_step2", "label_map_seq",
               "num_labels_step1", "num_labels_step2", "best_step1_f1",
               "best_step1_epoch", "best_step2_f1", "best_step2_epoch",
               "pakai_1st", "df_pairs"]:
        if _v in globals():
            _serializable[_v] = globals()[_v]
        else:
            _serializable[_v] = None

    if "args_h" in globals() and globals()["args_h"] is not None:
        _serializable["args_h"] = {
            "output_dir": getattr(globals()["args_h"], "output_dir", _sd["logs"]),
            "max_seq_length": getattr(globals()["args_h"], "max_seq_length", MAX_SEQ_LENGTH),
        }

    if extra_runtime:
        _serializable.update(extra_runtime)

    state_data = {
        "DOMAIN": DOMAIN,
        "base_project_dir": base_project_dir,
        "extract_dir": extract_dir,
        "data_root": data_root,
        "bert_cache_dir": bert_cache_dir,
        "session_dirs": session_dirs,
        "MAX_SEQ_LENGTH": MAX_SEQ_LENGTH,
        "NUM_EPOCHS": NUM_EPOCHS,
        "STEP1_BATCH_SIZE": STEP1_BATCH_SIZE,
        "STEP2_BATCH_SIZE": STEP2_BATCH_SIZE,
        "STEP1_LR": STEP1_LR,
        "STEP2_LR": STEP2_LR,
        "SEED": SEED,
        "device_str": str(device),
        "completed_stages": completed_stages,
        "runtime": _serializable,
    }

    with open(state_file, "wb") as sf:
        pickle.dump(state_data, sf)

    # Simpan JSON label terpisah untuk cadangan
    if globals().get("label_list_step1") is not None:
        with open(os.path.join(_sd["csv"], "labels_step1.json"), "w", encoding="utf-8") as jf:
            json.dump(globals()["label_list_step1"], jf, ensure_ascii=False, indent=2)
    if globals().get("label_list_step2") is not None:
        with open(os.path.join(_sd["csv"], "labels_step2.json"), "w", encoding="utf-8") as jf:
            json.dump(globals()["label_list_step2"], jf, ensure_ascii=False, indent=2)

    return state_file

# Helper Pencari File di Berbagai Lokasi Sesi (Fallback Search)
def auto_find_file(filename, search_roots=None):
    \"\"\"Mencari berkas di dalam direktori sesi aktif atau direktori sesi terdahulu.\"\"\"
    if search_roots is None:
        search_roots = [
            session_dirs.get("root", ""),
            results_base if 'results_base' in globals() else "",
            "/content/drive/MyDrive/ACOS/Output/results",
            os.path.join(base_project_dir, "Output", "results"),
            os.path.join(base_project_dir, "results"),
        ]
    for sr in search_roots:
        if not sr or not os.path.exists(sr):
            continue
        for root, dirs, files in os.walk(sr):
            if filename in files:
                return os.path.join(root, filename)
    return None

m_path = update_mcp_manifest("INITIALIZED", 1)
print(f"📡 MCP Session Manifest diinisialisasi: {m_path}")

# Konfigurasi Tabel
df_cfg = pd.DataFrame([
    {"Parameter": "domain", "Nilai": DOMAIN},
    {"Parameter": "num_epochs", "Nilai": NUM_EPOCHS},
    {"Parameter": "step1_batch_size", "Nilai": STEP1_BATCH_SIZE},
    {"Parameter": "step2_batch_size", "Nilai": STEP2_BATCH_SIZE},
    {"Parameter": "step1_learning_rate", "Nilai": STEP1_LR},
    {"Parameter": "step2_learning_rate", "Nilai": STEP2_LR},
    {"Parameter": "max_seq_length", "Nilai": MAX_SEQ_LENGTH},
    {"Parameter": "seed", "Nilai": SEED},
    {"Parameter": "device", "Nilai": str(device)},
])
rep.section("1. Konfigurasi pipeline")
export_step_table(df_cfg, name="master_00_konfigurasi", csv_dir=csv_dir, md_dir=md_dir,
                  title=f"Konfigurasi Master Pipeline ({DOMAIN.upper()})")
rep.table(df_cfg, caption="Hyperparameter")
save_pipeline_state()
print("💾 Inisialisasi state awal tersimpan.")""")

    # CELL 7: Section 4 Markdown
    add_md("""## 4. Exploratory Data Analysis (EDA) & Publication Visualizations""")

    # CELL 8: Code Section 4 (EDA with Auto-Cache)
    add_code("""# Eksekusi Analisis Data Eksploratif (dengan Pemeriksaan Cache Otomatis)
eda_stats_csv = os.path.join(csv_dir, "master_01_statistik_dataset.csv")
eda_ringkas_csv = os.path.join(csv_dir, "master_02_ringkasan_eda.csv")

if 'df_stats' in globals() and df_stats is not None and not df_stats.empty and 'df_records' in globals() and df_records is not None:
    print("⏩ [CACHE HIT] Menggunakan objek df_stats & df_records dari memori runtime.")
elif os.path.exists(eda_stats_csv) and os.path.exists(eda_ringkas_csv):
    print(f"⏩ [CACHE HIT] Memuat hasil EDA tersimpan dari: {eda_stats_csv}")
    df_stats = pd.read_csv(eda_stats_csv)
    df_ringkas = pd.read_csv(eda_ringkas_csv)
    df_records = pd.DataFrame()
else:
    print("📊 Menjalankan Analisis Data Eksploratif (EDA)...")
    df_stats, df_records = analyze_and_plot_eda(
        data_dir=base_project_dir,
        domain=DOMAIN,
        output_plots_dir=plots_dir,
        output_csv_dir=csv_dir,
    )

rep.section("2. Eksplorasi data")
if df_stats is None or df_stats.empty:
    print("⚠️ [Peringatan] Statistik EDA kosong: pastikan folder data/ tersedia.")
    rep.text("Statistik EDA kosong; folder `data/` tidak ditemukan.")
else:
    export_step_table(df_stats, name="master_01_statistik_dataset", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Statistik Dataset {DOMAIN.upper()} per Split")
    rep.table(df_stats, caption="Statistik per split")

    if 'df_records' in globals() and df_records is not None and not df_records.empty:
        n = len(df_records)
        df_ringkas = pd.DataFrame([{
            "Total_Quadruple": n,
            "Implicit_Aspect": int(df_records["Is_Implicit_Aspect"].sum()),
            "Implicit_Opinion": int(df_records["Is_Implicit_Opinion"].sum()),
            "Keduanya_Implicit": int((df_records["Is_Implicit_Aspect"] & df_records["Is_Implicit_Opinion"]).sum()),
            "Kategori_Unik": int(df_records["Category"].nunique()),
            "Panjang_Kalimat_Median": float(df_records["Text_Length"].median()),
        }])
        export_step_table(df_ringkas, name="master_02_ringkasan_eda", csv_dir=csv_dir, md_dir=md_dir,
                          title=f"Ringkasan EDA ({DOMAIN.upper()})")
        rep.table(df_ringkas, caption="Ringkasan EDA")

    from IPython.display import Image, display
    for fname, cap in [
        ("01_eda_dataset_distribution.png", "Komposisi dataset & explicit vs implicit"),
        ("02_eda_category_sentiment.png", "Kategori teratas & polaritas sentimen"),
        ("02b_eda_length_and_implicit_combo.png", "Panjang kalimat & kombinasi implicit"),
        ("02c_eda_category_sentiment_heatmap.png", "Heatmap kategori x sentimen"),
    ]:
        p = os.path.join(plots_dir, fname)
        if os.path.exists(p):
            display(Image(p))
            rep.image(p, cap)

tot_q = int(df_ringkas["Total_Quadruple"].values[0]) if ('df_ringkas' in globals() and not df_ringkas.empty) else 0
update_mcp_manifest("EDA_COMPLETED", 2, {"total_quadruples": tot_q})
save_pipeline_state()
print("✅ EDA selesai dan status disimpan ke pipeline_state.pkl.")""")

    # CELL 9: Section 4b Markdown
    add_md("""### 4b. Diagnostik Lokasi Dataset & Tokenized Data""")

    # CELL 10: Code Section 4b
    add_code("""# Diagnostik pelacakan data adaptif (Lokal & Colab)
print("--- Diagnostik Struktur Data Repositori ---")
search_locations = [base_project_dir, data_root, extract_dir, "/content", "/content/drive/MyDrive/ACOS"]
checked = set()

for s_dir in search_locations:
    if not os.path.exists(s_dir) or s_dir in checked:
        continue
    checked.add(s_dir)
    for root, dirs, files in os.walk(s_dir):
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        if 'Restaurant-ACOS' in dirs or 'Laptop-ACOS' in dirs:
            print(f"✅ Ditemukan dataset mentah di : {root}")
        if 'tokenized_data' in dirs:
            tok_path = os.path.join(root, 'tokenized_data')
            print(f"✅ Ditemukan tokenized_data di : {tok_path}")
            print(f"   Sampel file: {os.listdir(tok_path)[:4]}")""")

    # CELL 11: Section 5 Markdown
    add_md("""## 5. Step 1: Aspect & Opinion Co-Extraction (BERT-CRF Training & Checkpointing)
Melatih model `BertForQuadABSA` (BERT Encoder + Linear-Chain CRF + Dual Implicit Heads). Checkpoint model terbaik disimpan ke `checkpoints/step1_best/`.
Jika model terbaik dan `pred4pipeline.txt` sudah ada, sel ini otomatis memuat riwayat tanpa melatih ulang (hemat waktu & GPU). Ubah `FORCE_RETRAIN_STEP1 = True` jika ingin memaksa training ulang.""")

    # CELL 12: Code Section 5 (Step 1 with Smart Cache & Auto-Skip)
    add_code("""from modeling import BertForQuadABSA
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes
from eval_metrics import pred_eval
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm import tqdm

# Toggle Melatih Ulang (Set True jika ingin melatih ulang dari awal)
FORCE_RETRAIN_STEP1 = False

# Bersihkan memori GPU sebelum instansiasi model
if torch.cuda.is_available():
    torch.cuda.empty_cache()

tokenizer = BertTokenizer.from_pretrained(bert_cache_dir, do_lower_case=True)
processor_step1 = processors["quad"]()
label_list_step1 = processor_step1.get_labels(DOMAIN)
num_labels_step1 = len(label_list_step1[1])
label_map_seq = {label: i for i, label in enumerate(label_list_step1[1])}

# Path Checkpoint & Berkas Prediksi Step 1
step1_ckpt = session_dirs["step1_checkpoint"]
step1_bin = os.path.join(step1_ckpt, "pytorch_model.bin")
step1_csv = os.path.join(session_dirs["csv"], "step1_training_history.csv")
pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")

# Pemeriksaan apakah Step 1 sudah pernah selesai di sesi aktif atau sesi sebelumnya
step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)

if not step1_already_done:
    # Cari di penyimpanan sebelumnya (fallback)
    found_bin = auto_find_file("pytorch_model.bin", search_roots=[
        results_base if 'results_base' in globals() else "",
        "/content/drive/MyDrive/ACOS/Output/results",
        os.path.join(base_project_dir, "Output", "results"),
    ])
    if found_bin and "step1_best" in found_bin:
        src_dir = os.path.dirname(found_bin)
        print(f"🔍 Menemukan checkpoint Step 1 dari sesi sebelumnya: {src_dir}")
        for fn in ["pytorch_model.bin", "config.json", "vocab.txt"]:
            fp = os.path.join(src_dir, fn)
            if os.path.exists(fp):
                shutil.copy(fp, os.path.join(step1_ckpt, fn))
        found_pred = auto_find_file("pred4pipeline.txt")
        if found_pred:
            shutil.copy(found_pred, pred_file)
        found_csv = auto_find_file("step1_training_history.csv")
        if found_csv:
            shutil.copy(found_csv, step1_csv)
        step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)

if not FORCE_RETRAIN_STEP1 and step1_already_done:
    print(f"⏩ [CACHE HIT] Model Step 1 terbaik ditemukan di: {step1_ckpt}")
    print(f"⏩ [CACHE HIT] Berkas pred4pipeline.txt ditemukan di: {pred_file}")
    print(f"   Melewati 15 epoch training Step 1 dan langsung menggunakan hasil tersimpan.")
    if os.path.exists(step1_csv):
        df_s1_saved = pd.read_csv(step1_csv)
        step1_history = df_s1_saved.to_dict('records')
        best_step1_f1 = float(df_s1_saved["micro-F1"].max() / 100.0) if "micro-F1" in df_s1_saved else 0.0
        best1_epoch = int(df_s1_saved.loc[df_s1_saved["micro-F1"].idxmax()]["epoch"]) if "epoch" in df_s1_saved else NUM_EPOCHS
    else:
        step1_history = []
        best_step1_f1 = 0.0
        best1_epoch = NUM_EPOCHS
else:
    # 1. Muat Data Evaluasi (Dev/Test)
    eval_examples_1 = processor_step1.get_dev_examples(extract_dir, DOMAIN)
    eval_features_1 = features_step1(eval_examples_1, label_list_step1, MAX_SEQ_LENGTH, tokenizer, output_modes["quad"], "quad")

    ev_ids = torch.tensor([f.aspect_input_ids for f in eval_features_1], dtype=torch.long)
    ev_mask = torch.tensor([f.aspect_input_mask for f in eval_features_1], dtype=torch.long)
    ev_seg = torch.tensor([f.aspect_segment_ids for f in eval_features_1], dtype=torch.long)
    ev_lbl = torch.tensor([f.aspect_ids for f in eval_features_1], dtype=torch.long)
    ev_imp_a = torch.tensor([f.exist_imp_aspect for f in eval_features_1], dtype=torch.long)
    ev_imp_o = torch.tensor([f.exist_imp_opinion for f in eval_features_1], dtype=torch.long)
    ev_len = torch.tensor([f.tokens_len for f in eval_features_1], dtype=torch.long)
    eval_data_1 = TensorDataset(ev_len, ev_ids, ev_mask, ev_lbl, ev_seg, ev_imp_a, ev_imp_o)

    pin_mem = torch.cuda.is_available()
    num_work = 0 if sys.platform.startswith('win') else 2

    eval_loader_1 = DataLoader(
        eval_data_1, sampler=SequentialSampler(eval_data_1),
        batch_size=16, pin_memory=pin_mem, num_workers=num_work
    )

    # 2. Muat Ground Truth (Gold)
    eval_gold_1 = []
    with open(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_quad_bert.tsv"), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().split("\\t")
            cur_text = tokenizer.convert_tokens_to_ids(line[0].split(" "))
            aspect_labels = [label_map_seq['O'] for _ in range(MAX_SEQ_LENGTH)]
            cur_imp_a, cur_imp_o = 0, 0
            for quad in line[1:]:
                cur_aspect, cur_opinion = quad.split(' ')[0], quad.split(' ')[-1]
                a_st, a_ed = int(cur_aspect.split(',')[0]), int(cur_aspect.split(',')[1])
                if a_ed != -1:
                    aspect_labels[a_st] = label_map_seq['B-A']
                    for i in range(a_st+1, a_ed): aspect_labels[i] = label_map_seq['I-A']
                else: cur_imp_a = 1
                o_st, o_ed = int(cur_opinion.split(',')[0]), int(cur_opinion.split(',')[1])
                if o_ed != -1:
                    aspect_labels[o_st] = label_map_seq['B-O']
                    for i in range(o_st+1, o_ed): aspect_labels[i] = label_map_seq['I-O']
                else: cur_imp_o = 1
            eval_gold_1.append([cur_text, [aspect_labels, cur_imp_a, cur_imp_o]])
    eval_gold_1 = [[e[0] for e in eval_gold_1], [item for e in eval_gold_1 for item in e[1]]]

    # 3. Instansiasi Model Step 1
    model_step1 = BertForQuadABSA.from_pretrained(bert_cache_dir, num_labels=num_labels_step1).to(device)

    # 4. Muat Data Training
    train_examples_1 = processor_step1.get_train_examples(extract_dir, DOMAIN)
    train_features_1 = features_step1(train_examples_1, label_list_step1, MAX_SEQ_LENGTH, tokenizer, output_modes["quad"], "quad")
    tr_data_1 = TensorDataset(
        torch.tensor([f.tokens_len for f in train_features_1], dtype=torch.long),
        torch.tensor([f.aspect_input_ids for f in train_features_1], dtype=torch.long),
        torch.tensor([f.aspect_input_mask for f in train_features_1], dtype=torch.long),
        torch.tensor([f.aspect_ids for f in train_features_1], dtype=torch.long),
        torch.tensor([f.aspect_segment_ids for f in train_features_1], dtype=torch.long),
        torch.tensor([f.exist_imp_aspect for f in train_features_1], dtype=torch.long),
        torch.tensor([f.exist_imp_opinion for f in train_features_1], dtype=torch.long)
    )
    train_loader_1 = DataLoader(
        tr_data_1, sampler=RandomSampler(tr_data_1),
        batch_size=STEP1_BATCH_SIZE, pin_memory=pin_mem, num_workers=num_work
    )

    # 5. Optimizer Setup
    num_train_steps_1 = len(train_loader_1) * NUM_EPOCHS
    param_opt = list(model_step1.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    opt_grouped = [
        {'params': [p for n, p in param_opt if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_opt if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    optimizer_1 = BertAdam(opt_grouped, lr=STEP1_LR, warmup=0.1, t_total=num_train_steps_1)

    print(f"🚀 Memulai Training Step 1 BERT-CRF ({NUM_EPOCHS} Epochs pada {device})...")
    class ArgsH:
        def __init__(self):
            self.output_dir = session_dirs["logs"]
            self.max_seq_length = MAX_SEQ_LENGTH
    args_h = ArgsH()
    import logging
    logger = logging.getLogger("Step1")

    best_step1_f1 = 0.0
    best1_epoch = 1
    step1_history = []

    for epoch in range(1, NUM_EPOCHS + 1):
        model_step1.train()
        t_loss = 0.0
        for step, batch in enumerate(tqdm(train_loader_1, desc=f"Step 1 Epoch {epoch}/{NUM_EPOCHS}", leave=False)):
            batch = tuple(t.to(device) for t in batch)
            _len, _ids, _mask, _lbls, _seg, _imp_a, _imp_o = batch
            out1 = model_step1(aspect_input_ids=_ids, aspect_labels=_lbls, aspect_token_type_ids=_seg, aspect_attention_mask=_mask, exist_imp_aspect=_imp_a, exist_imp_opinion=_imp_o)
            loss, _ = unpack_model_output(out1)
            loss.backward()
            optimizer_1.step()
            optimizer_1.zero_grad()
            t_loss += loss.item()

        avg_loss = t_loss / len(train_loader_1)
        model_step1.eval()
        val_res = pred_eval(epoch, args_h, logger, tokenizer, model_step1, eval_loader_1, eval_gold_1, label_list_step1, device, "quad", eval_type='test')
        val_f1 = val_res.get('micro-F1', 0.0)
        
        # Track Peak VRAM
        peak_vram = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if torch.cuda.is_available() else 0.0
        print(f"Epoch {epoch:02d} | Loss: {avg_loss:.4f} | Test Micro-F1: {val_f1*100:.2f}% | Peak VRAM: {peak_vram:.1f} MB")
        
        step1_history.append({
            "epoch": epoch, "loss": avg_loss,
            "precision": val_res.get('precision', 0.0),
            "recall": val_res.get('recall', 0.0),
            "micro-F1": val_f1,
            "peak_vram_mb": round(peak_vram, 2)
        })

        # Simpan Checkpoint Model Terbaik
        if val_f1 > best_step1_f1:
            best_step1_f1 = val_f1
            best1_epoch = epoch
            print(f"🔥 Menyimpan model Step 1 terbaik ke {session_dirs['step1_checkpoint']}...")
            torch.save(model_step1.state_dict(), os.path.join(session_dirs["step1_checkpoint"], "pytorch_model.bin"))
            model_step1.config.to_json_file(os.path.join(session_dirs["step1_checkpoint"], "config.json"))
            tokenizer.save_vocabulary(session_dirs["step1_checkpoint"])

    # Ekspor Plot & CSV Riwayat Step 1
    plot_training_history(
        step1_history, task_name="Step 1 (BERT-CRF)",
        output_plot_path=os.path.join(session_dirs["plots"], "03_step1_training_loss_f1_curve.png"),
        output_csv_path=os.path.join(session_dirs["csv"], "step1_training_history.csv")
    )

# Laporan & Tabel Step 1
rep.section("3. Step 1: ekstraksi aspect & opinion")
df_s1 = pd.DataFrame(step1_history)
if not df_s1.empty:
    df_s1_pct = df_s1.copy()
    for c in ["precision", "recall", "micro-F1"]:
        if c in df_s1_pct.columns:
            if df_s1_pct[c].max() <= 1.0:
                df_s1_pct[c] = (df_s1_pct[c] * 100).round(2)
    export_step_table(df_s1_pct, name="master_03_step1_riwayat", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Riwayat Training Step 1 ({DOMAIN.upper()})",
                      notes="Metrik dihitung pada test set tiap epoch.",
                      max_rows_md=NUM_EPOCHS)
    rep.table(df_s1_pct, max_rows=NUM_EPOCHS, caption="Metrik step 1 per epoch")

    best1 = df_s1_pct.loc[df_s1_pct["micro-F1"].idxmax()]
    rep.kv({
        "epoch_terbaik": int(best1.get("epoch", best1_epoch)),
        "micro-F1_terbaik": f"{float(best1['micro-F1']):.2f}%",
        "checkpoint": session_dirs["step1_checkpoint"],
    })
    print(f"✅ Step 1 selesai. Micro-F1 terbaik: {float(best1['micro-F1']):.2f}% (Epoch {int(best1.get('epoch', best1_epoch))})")

_p1 = os.path.join(plots_dir, "03_step1_training_loss_f1_curve.png")
if os.path.exists(_p1):
    from IPython.display import Image, display
    display(Image(_p1))
    rep.image(_p1, "Kurva training step 1")

update_mcp_manifest("STEP1_COMPLETED", 3, {
    "step1_best_micro_f1": float(best_step1_f1 * 100 if best_step1_f1 <= 1.0 else best_step1_f1),
    "step1_checkpoint": session_dirs["step1_checkpoint"]
})
save_pipeline_state({"best_step1_f1": best_step1_f1, "best_step1_epoch": best1_epoch})""")

    # CELL 13: Section 6 Markdown
    add_md("""## 6. Smart State Checkpoint Saver (`pipeline_state.pkl`)""")

    # CELL 14: Code Section 6 (Smart State Checkpoint Saver)
    add_code("""# Simpan status variabel pipeline ke file pickle untuk pemulihan cepat.
# Menyimpan parameter konfigurasi, direktori, model status, dan artefak runtime.
checkpoint_state_path = save_pipeline_state()

print(f"✅ Pipeline State (expanded) berhasil disimpan ke: {checkpoint_state_path}")
print(f"   Checkpoint Step 1 : {session_dirs['step1_checkpoint']}")
print(f"   Prediksi File     : {os.path.join(session_dirs['logs'], 'pred4pipeline.txt')}")
print("ℹ️ Jika runtime Colab terputus, jalankan sel pemulihan (6b & 6c) di bawah ini untuk melanjutkan langsung ke Step 2.")""")

    # CELL 15: Section 6b Markdown
    add_md("""### 6b. Smart State Recovery (Gunakan Sel Ini Jika Kernel Reconnect / Restart)""")

    # CELL 16: Code Section 6b (Smart State Recovery)
    add_code("""# Sel Pemulihan Cerdas: Otomatis mendeteksi sesi aktif terakhir.
# Memulihkan BUKAN hanya config/path, tapi juga seluruh artefak runtime yang tersimpan.
def auto_find_latest_state(search_base):
    if not os.path.exists(search_base):
        return None
    candidates = []
    for root, dirs, files in os.walk(search_base):
        if "pipeline_state.pkl" in files:
            p = os.path.join(root, "pipeline_state.pkl")
            candidates.append((os.path.getmtime(p), p))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

# Prioritas path state
target_state_path = None
if 'checkpoint_state_path' in globals() and os.path.exists(checkpoint_state_path):
    target_state_path = checkpoint_state_path
else:
    target_state_path = auto_find_latest_state(
        results_base if 'results_base' in globals() else os.path.join(base_project_dir, "Output", "results"))
    if not target_state_path and os.path.exists("/content/drive/MyDrive/ACOS/Output/results"):
        target_state_path = auto_find_latest_state("/content/drive/MyDrive/ACOS/Output/results")

if target_state_path and os.path.exists(target_state_path):
    with open(target_state_path, "rb") as f:
        pipe_state = pickle.load(f)

    DOMAIN = pipe_state.get("DOMAIN", "rest16")
    base_project_dir = pipe_state.get("base_project_dir", base_project_dir if 'base_project_dir' in globals() else ".")
    extract_dir = pipe_state.get("extract_dir", os.path.join(base_project_dir, "Extract-Classify-ACOS"))
    bert_cache_dir = pipe_state.get("bert_cache_dir", os.path.join(base_project_dir, "bert_base_uncased"))
    session_dirs = pipe_state.get("session_dirs", session_dirs if 'session_dirs' in globals() else {})
    MAX_SEQ_LENGTH = pipe_state.get("MAX_SEQ_LENGTH", 128)
    NUM_EPOCHS = pipe_state.get("NUM_EPOCHS", 15)
    STEP2_BATCH_SIZE = pipe_state.get("STEP2_BATCH_SIZE", 16)
    STEP2_LR = pipe_state.get("STEP2_LR", 5e-5)
    SEED = pipe_state.get("SEED", 42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Pulihkan artefak runtime yang tersimpan
    rt = pipe_state.get("runtime", {}) or {}
    label_list_step1 = rt.get("label_list_step1")
    label_list_step2 = rt.get("label_list_step2")
    label_map_seq    = rt.get("label_map_seq")
    num_labels_step1 = rt.get("num_labels_step1")
    num_labels_step2 = rt.get("num_labels_step2")
    best_step1_f1    = rt.get("best_step1_f1")
    best_step1_epoch = rt.get("best_step1_epoch")
    best_step2_f1    = rt.get("best_step2_f1")
    best_step2_epoch = rt.get("best_step2_epoch")
    pakai_1st        = rt.get("pakai_1st")
    df_pairs         = rt.get("df_pairs")
    _args_h0         = rt.get("args_h")

    completed_stages = pipe_state.get("completed_stages", [])

    # Bangun ulang objek args_h agar sel evaluasi/inferensi tetap berfungsi
    import types as _types
    if _args_h0 and _args_h0.get("output_dir"):
        _ah = _types.SimpleNamespace()
        _ah.output_dir = _args_h0.get("output_dir", session_dirs.get("logs", ""))
        _ah.max_seq_length = _args_h0.get("max_seq_length", MAX_SEQ_LENGTH)
        args_h = _ah

    print(f"✅ Berhasil memulihkan state dari: {target_state_path}")
    print(f"📁 Session Dir : {session_dirs.get('root')}")
    print(f"📌 DOMAIN      : {DOMAIN} | Device: {device}")
    print(f"   Tahapan selesai : {completed_stages}")
    _recovered_from_state = True
else:
    print(f"ℹ️ Berkas state belum ditemukan (Lanjutkan eksekusi normal dari sel atas).")
    _recovered_from_state = False""")

    # CELL 17: Section 6c Markdown
    add_md("""### 6c. Jaminan Objek Runtime (Fallback Load Otomatis)

Sel ini menjalankan `ensure_objects()`: jika ada variabel runtime yang belum tersedia di memori (mis. kernel restart dan Anda hanya menjalankan sebagian sel), fungsi ini akan mencari hasilnya dari penyimpanan sebelumnya — yaitu *state* yang direstorasi (`pipeline_state.pkl`) atau file JSON label yang tersimpan — sehingga sel-sel lanjutan tidak pernah kehilangan variabel yang dibutuhkan di tengah jalan.""")

    # CELL 18: Code Section 6c (ensure_objects)
    add_code("""# Jaminan Objek Runtime (FALLBACK "cari hasil dari penyimpanan lama").
# Jika variabel runtime belum ada di memori (mis. kernel restart & hanya jalankan
# sebagian sel), fungsi ini memuatnya ulang dari: (a) state yang sudah direstorasi,
# (b) JSON label tersimpan, atau (c) inisialisasi ulang.
def ensure_objects():
    \"\"\"Pastikan tokenizer, label lists, num_labels, args_h tersedia di globals.
    Sumber: state yang direstorasi -> JSON label tersimpan -> fallback konstruksi.\"\"\"
    import types as _t
    g = globals()

    # 1) Tokenizer
    if "tokenizer" not in g or g["tokenizer"] is None:
        if "bert_cache_dir" not in g:
            g["bert_cache_dir"] = os.path.join(
                g.get("base_project_dir", "."), "bert_base_uncased")
        if os.path.exists(os.path.join(g["bert_cache_dir"], "vocab.txt")):
            from bert_utils.tokenization import BertTokenizer
            g["tokenizer"] = BertTokenizer.from_pretrained(
                g["bert_cache_dir"], do_lower_case=True)
            print("   🔁 Tokenizer dimuat ulang dari bert_cache_dir.")
        else:
            raise RuntimeError("Tokenizer belum ada & vocab.txt tidak ditemukan. "
                               "Jalankan sel konfigurasi (cell 6) dulu.")

    # 2) args_h
    if "args_h" not in g or g["args_h"] is None:
        _ah = _t.SimpleNamespace()
        _ah.output_dir = g.setdefault("session_dirs", {}).get("logs", "./logs")
        _ah.max_seq_length = g.get("MAX_SEQ_LENGTH", 128)
        g["args_h"] = _ah
        print("   🔁 args_h dibangun ulang dari state.")

    # 3) Label lists & num_labels (cari dari JSON tersimpan jika belum ada)
    csv_dir = g.setdefault("session_dirs", {}).get("csv")
    for _key, _jname in [("label_list_step1", "labels_step1"),
                         ("label_list_step2", "labels_step2")]:
        if (_key not in g or g[_key] is None) and csv_dir:
            _p = os.path.join(csv_dir, _jname + ".json")
            if os.path.exists(_p):
                with open(_p, "r", encoding="utf-8") as _jf:
                    g[_key] = json.load(_jf)
                print(f"   🔁 {_key} dimuat ulang dari {_jname}.json.")

    # Fallback dari processor jika masih None
    if g.get("label_list_step1") is None:
        from run_classifier_dataset_utils import processors
        processor_step1 = processors["quad"]()
        g["label_list_step1"] = processor_step1.get_labels(g.get("DOMAIN", "rest16"))
    if g.get("label_list_step2") is None:
        from run_classifier_dataset_utils import processors
        processor_step2 = processors["categorysenti"]()
        g["label_list_step2"] = processor_step2.get_labels(g.get("DOMAIN", "rest16"))

    if g.get("label_list_step1") is not None and "num_labels_step1" not in g:
        g["num_labels_step1"] = len(g["label_list_step1"][1])
    if g.get("label_list_step2") is not None and "num_labels_step2" not in g:
        g["num_labels_step2"] = len(g["label_list_step2"][0])

    # 4) Sumber kandidat pasangan (default: prediksi step 1 = pipeline penuh)
    if "pakai_1st" not in g:
        g["pakai_1st"] = True

    return g

ensure_objects()
print("🛡️ Objek runtime terverifikasi siap digunakan.")""")

    # CELL 19: Section 7 Markdown
    add_md("""## 7. Candidate Pair Generation Bridge
Membaca berkas `pred4pipeline.txt` dari Step 1 dan membentuk pasangan kartesian $(a, o)$ dengan penanganan entitas implisit `[-1, -1]`.
Jika berkas pasangan kandidat sudah dibuat sebelumnya, sel ini langsung memuatnya dari disk.""")

    # CELL 20: Code Section 7 (Candidate Pairs Bridge with Cache & Auto-Search)
    add_code("""ensure_objects()
import codecs as cs

pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")
target_tokenized_tsv = os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")
candidate_csv = os.path.join(session_dirs["csv"], "candidate_pairs_summary.csv")

if 'df_pairs' in globals() and df_pairs is not None and not df_pairs.empty and os.path.exists(target_tokenized_tsv):
    print(f"⏩ [CACHE HIT] Menggunakan {len(df_pairs)} pasangan kandidat dari memori runtime.")
elif os.path.exists(candidate_csv) and os.path.exists(target_tokenized_tsv):
    print(f"⏩ [CACHE HIT] Memuat pasangan kandidat tersimpan dari: {candidate_csv}")
    df_pairs = pd.read_csv(candidate_csv)
    print(f"   Total {len(df_pairs)} pasangan berhasil dimuat.")
else:
    # Jika pred4pipeline.txt belum ada di sesi ini, cari dari sesi sebelumnya
    if not os.path.exists(pred_file):
        found_pred = auto_find_file("pred4pipeline.txt")
        if found_pred:
            print(f"🔍 Menemukan pred4pipeline.txt dari penyimpanan sesi sebelumnya: {found_pred}")
            os.makedirs(session_dirs["logs"], exist_ok=True)
            shutil.copy(found_pred, pred_file)
        else:
            raise FileNotFoundError(f"Berkas pred4pipeline.txt tidak ditemukan di {pred_file} maupun sesi lainnya. Jalankan Step 1 terlebih dahulu.")

    with cs.open(pred_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pair_records = []
    os.makedirs(os.path.dirname(target_tokenized_tsv), exist_ok=True)
    with cs.open(target_tokenized_tsv, 'w', encoding='utf-8') as wf:
        for idx, line in enumerate(lines):
            asp, opi = [], []
            parts = line.strip().split('\\t')
            if len(parts) <= 1: continue
            text = parts[0]
            for ele in parts[1:]:
                if ele.startswith('a'): asp.append(ele[2:])
                else: opi.append(ele[2:])
            if not asp: asp.append('-1,-1')
            if not opi: opi.append('-1,-1')
            for pa in asp:
                for po in opi:
                    wf.write(f"{text}####{pa} {po}\\n")
                    pair_records.append({"Text": text, "Aspect_Span": pa, "Opinion_Span": po})

    df_pairs = pd.DataFrame(pair_records)
    df_pairs.to_csv(candidate_csv, index=False)
    print(f"✅ Terbentuk {len(df_pairs)} Pasangan Kandidat untuk Step 2. Tersimpan di {target_tokenized_tsv}.")

# Laporan & Distribusi Pasangan
rep.section("4. Jembatan: pasangan kandidat")
if df_pairs.empty:
    rep.text("Tidak ada pasangan kandidat yang terbentuk.")
else:
    df_pairs["Is_Implicit_Aspect"] = df_pairs["Aspect_Span"] == "-1,-1"
    df_pairs["Is_Implicit_Opinion"] = df_pairs["Opinion_Span"] == "-1,-1"
    df_pairs["Pair_Type"] = (
        df_pairs["Is_Implicit_Aspect"].map({True: "Implicit", False: "Explicit"}) + "-"
        + df_pairs["Is_Implicit_Opinion"].map({True: "Implicit", False: "Explicit"})
    )
    n_pair = len(df_pairs)
    df_tipe = df_pairs["Pair_Type"].value_counts().rename_axis("Tipe_Pasangan").reset_index(name="Jumlah")
    df_tipe["Persen"] = (df_tipe["Jumlah"] / n_pair * 100).round(2)

    export_step_table(df_tipe, name="master_04_tipe_pasangan", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Distribusi Tipe Pasangan Kandidat ({DOMAIN.upper()})",
                      notes=f"Total {n_pair} pasangan dari cross-product aspect x opinion.")
    rep.table(df_tipe, caption="Tipe pasangan")

    export_step_table(df_pairs.head(20), name="master_05_preview_pasangan",
                      csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Preview 20 Pasangan Kandidat ({DOMAIN.upper()})", max_rows_md=20)

    plt.figure(figsize=(9, 5))
    _w = ["#3498db", "#9b59b6", "#e67e22", "#e74c3c"][:len(df_tipe)]
    _b = plt.bar(df_tipe["Tipe_Pasangan"], df_tipe["Jumlah"], color=_w, edgecolor="black", alpha=0.88)
    for b, v in zip(_b, df_tipe["Jumlah"]):
        plt.text(b.get_x() + b.get_width() / 2, v, f"{v:,}\\n({v/n_pair*100:.1f}%)",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.title(f"[{DOMAIN.upper()}] Pasangan Kandidat Step 1 -> Step 2", fontsize=12, fontweight="bold")
    plt.ylabel("Jumlah pasangan")
    plt.margins(y=0.18)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    _pp = os.path.join(plots_dir, "04_candidate_pairs_distribution.png")
    plt.savefig(_pp, dpi=300)
    plt.show()
    plt.close()
    rep.image(_pp, "Distribusi tipe pasangan kandidat")

update_mcp_manifest("CANDIDATE_PAIRS_GENERATED", 4, {"candidate_pairs_count": len(df_pairs)})
save_pipeline_state({"df_pairs": df_pairs})""")

    # CELL 21: Section 8 Markdown
    add_md("""## 8. Step 2: Category & Sentiment Classification Training & Checkpointing
Melatih model `CategorySentiClassification` multi-label pada pasangan kandidat $(a, o)$. Model terbaik disimpan ke `checkpoints/step2_best/`.
Jika checkpoint Step 2 sudah tersedia, sel ini otomatis memuat riwayat tanpa melatih ulang. Ubah `FORCE_RETRAIN_STEP2 = True` jika ingin memaksa training ulang.""")

    # CELL 22: Code Section 8 (Step 2 with Smart Cache & Auto-Skip)
    add_code("""ensure_objects()
from modeling import CategorySentiClassification
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval

# Toggle Melatih Ulang Step 2 (Set True jika ingin memaksa melatih ulang)
FORCE_RETRAIN_STEP2 = False

# Bersihkan memori GPU sebelum instansiasi model Step 2
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Monkey-patch BertTokenizer untuk penanganan diagnostik KeyError
from bert_utils.tokenization import BertTokenizer
import logging

def patched_convert_tokens_to_ids(self, tokens):
    if tokens is None: return None
    if isinstance(tokens, str):
        try: return self.vocab[tokens]
        except KeyError:
            print(f"⚠️ Token di luar vocab: {ascii(tokens)}")
            return self.vocab.get('[UNK]', 100)
    ids = []
    for token in tokens:
        try: ids.append(self.vocab[token])
        except KeyError:
            ids.append(self.vocab.get('[UNK]', 100))
    if len(ids) > self.max_len:
        logging.getLogger(__name__).warning(f"Seq len ({len(ids)}) > max ({self.max_len})")
    return ids

BertTokenizer.convert_tokens_to_ids = patched_convert_tokens_to_ids

from run_classifier_dataset_utils import processors, output_modes
processor_step2 = processors["categorysenti"]()
label_list_step2 = processor_step2.get_labels(DOMAIN)
num_labels_step2 = len(label_list_step2[0])

# Checkpoint Path Step 2
step2_ckpt = session_dirs["step2_checkpoint"]
step2_bin = os.path.join(step2_ckpt, "pytorch_model.bin")
step2_csv = os.path.join(session_dirs["csv"], "step2_training_history.csv")

# 1. Muat Fitur Evaluasi Step 2 dari Pasangan Kandidat Step 1
tokenized_dir = os.path.join(extract_dir, "tokenized_data")
eval_pair_file, pakai_1st = resolve_eval_pair_file(tokenized_dir, DOMAIN, prefer_1st=True)
eval_examples_2 = pair_examples_from_file(processor_step2, eval_pair_file, set_type="test")
eval_features_2 = features_step2(eval_examples_2, label_list_step2, MAX_SEQ_LENGTH, tokenizer, output_modes["categorysenti"])

pin_mem = torch.cuda.is_available()
num_work = 0 if sys.platform.startswith('win') else 2

ev2_data = TensorDataset(
    torch.tensor([f.tokens_len for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.aspect_input_ids for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.aspect_input_mask for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.aspect_segment_ids for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.candidate_aspect for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.candidate_opinion for f in eval_features_2], dtype=torch.long),
    torch.tensor([f.label_id for f in eval_features_2], dtype=torch.float)
)
eval_loader_2 = DataLoader(ev2_data, sampler=SequentialSampler(ev2_data), batch_size=16, pin_memory=pin_mem, num_workers=num_work)

# 2. Muat Ground Truth (Gold) Step 2
class ArgsProxy:
    def __init__(self): self.bert_model = bert_cache_dir; self.do_lower_case = True
with open(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair.tsv"), "r", encoding="utf-8") as f:
    eval_gold_2 = read_pair_gold(f.readlines(), ArgsProxy())

# Cek apakah Step 2 sudah pernah selesai
step2_already_done = os.path.exists(step2_bin)

if not step2_already_done:
    # Cari di penyimpanan sebelumnya (fallback)
    found_bin2 = auto_find_file("pytorch_model.bin", search_roots=[
        results_base if 'results_base' in globals() else "",
        "/content/drive/MyDrive/ACOS/Output/results",
        os.path.join(base_project_dir, "Output", "results"),
    ])
    if found_bin2 and "step2_best" in found_bin2:
        src_dir2 = os.path.dirname(found_bin2)
        print(f"🔍 Menemukan checkpoint Step 2 dari sesi sebelumnya: {src_dir2}")
        for fn in ["pytorch_model.bin", "config.json", "vocab.txt"]:
            fp = os.path.join(src_dir2, fn)
            if os.path.exists(fp):
                shutil.copy(fp, os.path.join(step2_ckpt, fn))
        found_csv2 = auto_find_file("step2_training_history.csv")
        if found_csv2:
            shutil.copy(found_csv2, step2_csv)
        step2_already_done = os.path.exists(step2_bin)

if not FORCE_RETRAIN_STEP2 and step2_already_done:
    print(f"⏩ [CACHE HIT] Model Step 2 terbaik ditemukan di: {step2_ckpt}")
    print(f"   Melewati 15 epoch training Step 2 dan langsung menggunakan hasil tersimpan.")
    if os.path.exists(step2_csv):
        df_s2_saved = pd.read_csv(step2_csv)
        step2_history = df_s2_saved.to_dict('records')
        best_step2_f1 = float(df_s2_saved["micro-F1"].max() / 100.0) if "micro-F1" in df_s2_saved else 0.0
        best2_epoch = int(df_s2_saved.loc[df_s2_saved["micro-F1"].idxmax()]["epoch"]) if "epoch" in df_s2_saved else NUM_EPOCHS
    else:
        step2_history = []
        best_step2_f1 = 0.0
        best2_epoch = NUM_EPOCHS
else:
    # 3. Instansiasi Model Step 2
    model_step2 = CategorySentiClassification.from_pretrained(bert_cache_dir, num_labels=num_labels_step2).to(device)

    # 4. Muat Data Training Step 2
    train_examples_2 = processor_step2.get_train_examples(extract_dir, DOMAIN)
    train_features_2 = features_step2(train_examples_2, label_list_step2, MAX_SEQ_LENGTH, tokenizer, output_modes["categorysenti"])
    tr2_data = TensorDataset(
        torch.tensor([f.tokens_len for f in train_features_2], dtype=torch.long),
        torch.tensor([f.aspect_input_ids for f in train_features_2], dtype=torch.long),
        torch.tensor([f.aspect_input_mask for f in train_features_2], dtype=torch.long),
        torch.tensor([f.aspect_segment_ids for f in train_features_2], dtype=torch.long),
        torch.tensor([f.candidate_aspect for f in train_features_2], dtype=torch.long),
        torch.tensor([f.candidate_opinion for f in train_features_2], dtype=torch.long),
        torch.tensor([f.label_id for f in train_features_2], dtype=torch.float)
    )
    train_loader_2 = DataLoader(tr2_data, sampler=RandomSampler(tr2_data), batch_size=STEP2_BATCH_SIZE, pin_memory=pin_mem, num_workers=num_work)

    # 5. Optimizer Setup
    from bert_utils.optimization import BertAdam
    num_train_steps_2 = len(train_loader_2) * NUM_EPOCHS
    param_opt2 = list(model_step2.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    opt_grouped2 = [
        {'params': [p for n, p in param_opt2 if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_opt2 if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    optimizer_2 = BertAdam(opt_grouped2, lr=STEP2_LR, warmup=0.1, t_total=num_train_steps_2)

    print(f"🚀 Memulai Training Step 2 Klasifikasi Kategori & Sentimen ({NUM_EPOCHS} Epochs pada {device})...")
    logger2 = logging.getLogger("Step2")
    best_step2_f1 = 0.0
    best2_epoch = 1
    step2_history = []

    for epoch in range(1, NUM_EPOCHS + 1):
        model_step2.train()
        t_loss = 0.0
        for step, batch in enumerate(tqdm(train_loader_2, desc=f"Step 2 Epoch {epoch}/{NUM_EPOCHS}", leave=False)):
            batch = tuple(t.to(device) for t in batch)
            _len, _ids, _mask, _seg, _cand_a, _cand_o, _lbls = batch
            out2 = model_step2(tokenizer, epoch, aspect_input_ids=_ids, aspect_token_type_ids=_seg, aspect_attention_mask=_mask, candidate_aspect=_cand_a, candidate_opinion=_cand_o, label_id=_lbls)
            loss, _ = unpack_model_output(out2)
            loss.backward()
            optimizer_2.step()
            optimizer_2.zero_grad()
            t_loss += loss.item()

        avg_loss = t_loss / len(train_loader_2)
        model_step2.eval()
        val_res = pair_eval(epoch, args_h, logger2, tokenizer, model_step2, eval_loader_2, eval_gold_2, label_list_step2, device, "categorysenti", eval_type='test')
        val_f1 = val_res.get('micro-F1', 0.0)
        peak_vram2 = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if torch.cuda.is_available() else 0.0
        
        print(f"Epoch {epoch:02d} | Loss: {avg_loss:.4f} | Test Micro-F1: {val_f1*100:.2f}% | Peak VRAM: {peak_vram2:.1f} MB")
        step2_history.append({
            "epoch": epoch, "loss": avg_loss,
            "precision": val_res.get('precision', 0.0),
            "recall": val_res.get('recall', 0.0),
            "micro-F1": val_f1,
            "peak_vram_mb": round(peak_vram2, 2)
        })

        if val_f1 > best_step2_f1:
            best_step2_f1 = val_f1
            best2_epoch = epoch
            print(f"🔥 Menyimpan model Step 2 terbaik ke {session_dirs['step2_checkpoint']}...")
            torch.save(model_step2.state_dict(), os.path.join(session_dirs["step2_checkpoint"], "pytorch_model.bin"))
            model_step2.config.to_json_file(os.path.join(session_dirs["step2_checkpoint"], "config.json"))
            tokenizer.save_vocabulary(session_dirs["step2_checkpoint"])

    # Ekspor Plot & CSV Riwayat Step 2
    plot_training_history(
        step2_history, task_name="Step 2 (Category-Sentiment)",
        output_plot_path=os.path.join(session_dirs["plots"], "04_step2_training_loss_f1_curve.png"),
        output_csv_path=os.path.join(session_dirs["csv"], "step2_training_history.csv")
    )

# Laporan & Tabel Step 2
rep.section("5. Step 2: klasifikasi category & sentiment")
df_s2 = pd.DataFrame(step2_history)
if not df_s2.empty:
    df_s2_pct = df_s2.copy()
    for c in ["precision", "recall", "micro-F1"]:
        if c in df_s2_pct.columns:
            if df_s2_pct[c].max() <= 1.0:
                df_s2_pct[c] = (df_s2_pct[c] * 100).round(2)
    export_step_table(df_s2_pct, name="master_06_step2_riwayat", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Riwayat Training Step 2 ({DOMAIN.upper()})",
                      notes=("Metrik pada level quadruple lengkap. Sumber kandidat: "
                             f"{'prediksi step 1' if pakai_1st else 'gold pair'}."),
                      max_rows_md=NUM_EPOCHS)
    rep.table(df_s2_pct, max_rows=NUM_EPOCHS, caption="Metrik step 2 per epoch")

    best2 = df_s2_pct.loc[df_s2_pct["micro-F1"].idxmax()]
    rep.kv({
        "epoch_terbaik": int(best2.get("epoch", best2_epoch)),
        "micro-F1_terbaik": f"{float(best2['micro-F1']):.2f}%",
        "checkpoint": session_dirs["step2_checkpoint"],
    })
    print(f"✅ Step 2 selesai. Micro-F1 terbaik: {float(best2['micro-F1']):.2f}% (Epoch {int(best2.get('epoch', best2_epoch))})")

_p2 = os.path.join(plots_dir, "04_step2_training_loss_f1_curve.png")
if os.path.exists(_p2):
    from IPython.display import Image, display
    display(Image(_p2))
    rep.image(_p2, "Kurva training step 2")

update_mcp_manifest("STEP2_COMPLETED", 5, {
    "step2_best_micro_f1": float(best_step2_f1 * 100 if best_step2_f1 <= 1.0 else best_step2_f1),
    "step2_checkpoint": session_dirs["step2_checkpoint"]
})
save_pipeline_state({"best_step2_f1": best_step2_f1, "best_step2_epoch": best2_epoch})""")

    # CELL 23: Section 9 Markdown
    add_md("""## 9. Final Evaluation & 15 Sub-Tasks Benchmark Dashboard""")

    # CELL 24: Code Section 9 (Final Evaluation with Auto-Cache)
    add_code("""ensure_objects()
# Evaluasi Final Memakai Checkpoint Model Step 2 Terbaik
FORCE_REEVAL = False

metrics_json = os.path.join(session_dirs["logs"], "master_metrics.json")
cached_metrics_available = os.path.exists(metrics_json)

if not FORCE_REEVAL and cached_metrics_available:
    print(f"⏩ [CACHE HIT] Memuat hasil benchmark evaluasi lengkap dari: {metrics_json}")
    with open(metrics_json, "r", encoding="utf-8") as jf:
        cached_all = json.load(jf)
    final_res = cached_all.get("overall", {})
    subtask_metrics = cached_all.get("subtasks", {})
    from colab_utils import SubtaskMetricCapture
    df_subtasks = pd.DataFrame([
        {"Subtask": k, "Precision": v.get("precision", 0.0), "Recall": v.get("recall", 0.0), "Micro_F1": v.get("micro_f1", 0.0), "N_Elements": len(k.split('-'))}
        for k, v in subtask_metrics.items()
    ])
else:
    # Muat model Step 2 terbaik
    step2_bin_path = os.path.join(session_dirs["step2_checkpoint"], "pytorch_model.bin")
    if not os.path.exists(step2_bin_path):
        found_bin2 = auto_find_file("pytorch_model.bin")
        if found_bin2 and "step2_best" in found_bin2:
            shutil.copy(found_bin2, step2_bin_path)

    model_step2_best = CategorySentiClassification.from_pretrained(
        session_dirs["step2_checkpoint"], num_labels=num_labels_step2).to(device)
    model_step2_best.eval()

    logger_final = logging.getLogger("Final_Eval")
    with SubtaskMetricCapture(logger_final) as cap:
        final_res = pair_eval("final", args_h, logger_final, tokenizer, model_step2_best,
                              eval_loader_2, eval_gold_2, label_list_step2, device,
                              "categorysenti", eval_type="test")

    subtask_metrics = cap.to_dict()
    df_subtasks = cap.to_frame()

    with open(metrics_json, "w", encoding="utf-8") as jf:
        json.dump({"overall": final_res, "subtasks": subtask_metrics,
                   "step1_history": globals().get("step1_history", []),
                   "step2_history": globals().get("step2_history", []),
                   "sumber_kandidat": "step1" if globals().get("pakai_1st", True) else "gold"}, jf, indent=2)
    print(f"📊 JSON metrik pipeline lengkap tersimpan: {metrics_json}")

rep.section("6. Hasil akhir pipeline")
df_overall = pd.DataFrame([{
    "Metrik": k, "Nilai": v, "Persen": round(v * 100, 2),
} for k, v in final_res.items()])
export_step_table(df_overall, name="master_07_metrik_quadruple_final",
                  csv_dir=csv_dir, md_dir=md_dir,
                  title=f"Metrik Akhir Ekstraksi Quadruple ({DOMAIN.upper()})",
                  notes=("Sumber kandidat: "
                         f"{'prediksi step 1 (skor pipeline penuh)' if globals().get('pakai_1st', True) else 'gold pair (step 2 terisolasi)'}."))
rep.table(df_overall, caption="Metrik quadruple akhir")

print("\\n🏆 Metrik Quadruple Akhir:")
for k, v in final_res.items():
    print(f"   {k:15s}: {v*100:.2f}%")

if not df_subtasks.empty:
    df_sub_pct = df_subtasks.copy()
    for c in ["Precision", "Recall", "Micro_F1"]:
        if c in df_sub_pct.columns and df_sub_pct[c].max() <= 1.0:
            df_sub_pct[c] = (df_sub_pct[c] * 100).round(2)

    rep.section("7. Metrik per sub-task")
    export_step_table(df_sub_pct, name="master_08_metrik_subtask", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Metrik per Sub-Task ({DOMAIN.upper()}) - {len(df_sub_pct)} kombinasi",
                      notes="Diambil dari keluaran pair_eval sesi ini, bukan angka yang ditulis manual.",
                      max_rows_md=20)
    rep.table(df_sub_pct, max_rows=20, caption="Metrik per sub-task")

    _ps = os.path.join(plots_dir, "05_benchmark_subtasks_f1.png")
    plot_subtask_metrics(df_subtasks, _ps, title=f"[{DOMAIN.upper()}] Micro-F1 per Sub-Task")
    rep.image(_ps, "Micro-F1 per sub-task")

    df_agg = (df_subtasks.groupby("N_Elements")
              .agg(Jumlah_Subtask=("Subtask", "count"),
                   Micro_F1_Rata2=("Micro_F1", "mean"),
                   Micro_F1_Min=("Micro_F1", "min"),
                   Micro_F1_Maks=("Micro_F1", "max"))
              .reset_index())
    for c in ["Micro_F1_Rata2", "Micro_F1_Min", "Micro_F1_Maks"]:
        if df_agg[c].max() <= 1.0:
            df_agg[c] = (df_agg[c] * 100).round(2)
    export_step_table(df_agg, name="master_09_agregasi_elemen", csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Micro-F1 Menurut Jumlah Elemen ({DOMAIN.upper()})")
    rep.table(df_agg, caption="Agregasi per jumlah elemen")

update_mcp_manifest("FINAL_EVAL_COMPLETED", 6, {
    "final_metrics": final_res,
    "metrics_json_path": metrics_json
})
save_pipeline_state({"final_res": final_res})""")

    # CELL 25: Section 10 Markdown
    add_md("""## 10. Live Interactive Inference Demo pada Teks Ulasan Bebas""")

    # CELL 26: Code Section 10 (Live Interactive Inference with Auto-Load Models)
    add_code("""ensure_objects()
import re as _re

# Muat model Step 1 & Step 2 terbaik untuk inferensi live (dengan fallback auto-load)
step1_best_path = session_dirs["step1_checkpoint"]
if not os.path.exists(os.path.join(step1_best_path, "pytorch_model.bin")):
    found_b1 = auto_find_file("pytorch_model.bin")
    if found_b1 and "step1_best" in found_b1:
        step1_best_path = os.path.dirname(found_b1)

step2_best_path = session_dirs["step2_checkpoint"]
if not os.path.exists(os.path.join(step2_best_path, "pytorch_model.bin")):
    found_b2 = auto_find_file("pytorch_model.bin")
    if found_b2 and "step2_best" in found_b2:
        step2_best_path = os.path.dirname(found_b2)

model_step1_best = BertForQuadABSA.from_pretrained(
    step1_best_path, num_labels=num_labels_step1).to(device)
model_step1_best.eval()

model_step2_best = CategorySentiClassification.from_pretrained(
    step2_best_path, num_labels=num_labels_step2).to(device)
model_step2_best.eval()

_catsenti_labels = label_list_step2[0]

def _spans_dari_tag(tag_ids):
    s = "".join(str(t) for t in tag_ids)
    aspects = [(m.start() - 1, m.end() - 1) for m in _re.finditer(r"32*", s)]
    opinions = [(m.start() - 1, m.end() - 1) for m in _re.finditer(r"54*", s)]
    return aspects, opinions

def analyze_review_quadruples(review_text, domain=None, ambang=0.0, tampilkan_proses=True):
    \"\"\"Ekstraksi quadruple dua tahap untuk satu teks ulasan bebas.\"\"\"
    domain = domain or DOMAIN
    max_len = MAX_SEQ_LENGTH

    tokens = tokenizer.tokenize(review_text.lower())[: max_len - 2]
    input_tokens = ["[CLS]"] + tokens + ["[SEP]"]
    input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
    attn = [1] * len(input_ids)
    seg = [0] * len(input_ids)
    while len(input_ids) < max_len:
        input_ids.append(0)
        attn.append(0)
        seg.append(0)

    t_ids = torch.tensor([input_ids], dtype=torch.long).to(device)
    t_attn = torch.tensor([attn], dtype=torch.long).to(device)
    t_seg = torch.tensor([seg], dtype=torch.long).to(device)
    t_dummy = torch.zeros((1, max_len), dtype=torch.long).to(device)
    t_zero = torch.zeros(1, dtype=torch.long).to(device)

    with torch.no_grad():
        out1 = model_step1_best(
            aspect_input_ids=t_ids, aspect_labels=t_dummy,
            aspect_token_type_ids=t_seg, aspect_attention_mask=t_attn,
            exist_imp_aspect=t_zero, exist_imp_opinion=t_zero,
        )
    _, logits1 = unpack_model_output(out1)
    pred_tags, imp_a_logit, imp_o_logit = logits1
    imp_aspect = int(imp_a_logit.argmax(-1).item()) == 1
    imp_opinion = int(imp_o_logit.argmax(-1).item()) == 1

    aspects, opinions = _spans_dari_tag(pred_tags[0])
    if imp_aspect or not aspects:
        aspects = aspects + [(-1, -1)]
    if imp_opinion or not opinions:
        opinions = opinions + [(-1, -1)]

    if tampilkan_proses:
        print(f"\\nTeks Review : {review_text}")
        print(f"Tokens      : {tokens}")
        print(f"Aspect Spans: {aspects} (implicit={imp_aspect})")
        print(f"Opinion Span: {opinions} (implicit={imp_opinion})")

    hasil = []
    for (a_st, a_ed) in aspects:
        for (o_st, o_ed) in opinions:
            cand_a = [0] * max_len
            cand_o = [0] * max_len
            if a_st == -1:
                cand_a[0] = 1
            else:
                for i in range(a_st + 1, a_ed + 1):
                    if i < max_len: cand_a[i] = 1
            if o_st == -1:
                cand_o[len(tokens) + 1] = 1
            else:
                for i in range(o_st + 1, o_ed + 1):
                    if i < max_len: cand_o[i] = 1

            with torch.no_grad():
                out2 = model_step2_best(
                    tokenizer, 0,
                    aspect_input_ids=t_ids,
                    aspect_token_type_ids=t_seg,
                    aspect_attention_mask=t_attn,
                    candidate_aspect=torch.tensor([cand_a], dtype=torch.long).to(device),
                    candidate_opinion=torch.tensor([cand_o], dtype=torch.long).to(device),
                    label_id=torch.zeros((1, num_labels_step2), dtype=torch.float).to(device),
                )
            _, logits2 = unpack_model_output(out2)
            skor = logits2[0][0].detach().cpu().numpy()

            aktif = [i for i, v in enumerate(skor) if v > ambang] or [int(skor.argmax())]
            asp_txt = "[IMPLICIT]" if a_st == -1 else " ".join(tokens[a_st:a_ed])
            opi_txt = "[IMPLICIT]" if o_st == -1 else " ".join(tokens[o_st:o_ed])

            for idx in aktif:
                kategori, sentimen = _catsenti_labels[idx].rsplit("#", 1)
                hasil.append({
                    "Aspect": asp_txt,
                    "Aspect_Span": f"{a_st},{a_ed}",
                    "Category": kategori,
                    "Opinion": opi_txt,
                    "Opinion_Span": f"{o_st},{o_ed}",
                    "Sentiment": {"0": "negative", "1": "neutral", "2": "positive"}.get(sentimen, sentimen),
                    "Skor_Logit": round(float(skor[idx]), 4),
                    "Is_Implicit_Aspect": a_st == -1,
                    "Is_Implicit_Opinion": o_st == -1,
                })

    df = pd.DataFrame(hasil)
    if not df.empty:
        df = df.sort_values("Skor_Logit", ascending=False).reset_index(drop=True)
    return df

# Contoh Pengujian Live Review
sample_review = "The sushi was fresh and delicious, but the service was slow."
df_infer = analyze_review_quadruples(sample_review, domain=DOMAIN)

rep.section("8. Contoh inferensi")
rep.text(f"Teks: `{sample_review}`")
if not df_infer.empty:
    export_step_table(df_infer, name="master_10_contoh_inferensi", csv_dir=csv_dir, md_dir=md_dir,
                      title="Quadruple Hasil Inferensi Contoh",
                      notes="Skor_Logit adalah keluaran mentah sebelum sigmoid; ambang default 0.0.",
                      max_rows_md=20)
    rep.table(df_infer, max_rows=20, caption="Quadruple hasil inferensi")
    from IPython.display import display
    display(df_infer)

save_pipeline_state({"df_infer": df_infer})""")

    # CELL 27: Section 11 Markdown
    add_md("""## 11. Ringkasan Seluruh Artefak & Finalisasi Sesi""")

    # CELL 28: Code Section 11 (Summary of Artifacts & Finalization)
    add_code("""def _list_dir(label, path):
    rows = []
    if os.path.isdir(path):
        for f in sorted(os.listdir(path)):
            fp = os.path.join(path, f)
            if os.path.isfile(fp):
                rows.append({"Jenis": label, "Nama": f, "Ukuran_KB": round(os.path.getsize(fp) / 1024, 1)})
    return rows

ckpt_rows = []
for root, _dirs, files in os.walk(session_dirs["checkpoints"]):
    for f in files:
        fp = os.path.join(root, f)
        ckpt_rows.append({
            "Jenis": "Checkpoint",
            "Nama": os.path.relpath(fp, session_dirs["checkpoints"]),
            "Ukuran_KB": round(os.path.getsize(fp) / 1024, 1),
        })

df_art = pd.DataFrame(
    ckpt_rows + _list_dir("CSV", csv_dir) + _list_dir("Plot", plots_dir)
    + _list_dir("Markdown", md_dir) + _list_dir("Log", logs_dir)
)

rep.section("9. Artefak sesi")
if not df_art.empty:
    export_step_table(df_art, name="master_11_daftar_artefak", csv_dir=csv_dir, md_dir=md_dir,
                      title="Daftar Artefak Master Pipeline", max_rows_md=200)
    rep.table(df_art, max_rows=200, caption="Artefak sesi")

rep.section("10. Batasan").text(
    f"- Semua metrik berasal dari eksekusi sesi ini pada domain `{DOMAIN}`.\\n"
    f"- Sumber kandidat evaluasi step 2: {'prediksi step 1' if globals().get('pakai_1st', True) else 'gold pair'}.\\n"
    f"- Jumlah epoch: {NUM_EPOCHS} (paper memakai 30).\\n"
    "- Angka tidak dibandingkan langsung dengan paper karena konfigurasi berbeda."
)
rep.text(f"Sesi: `{session_dirs['root']}`")
report_path = rep.save()

# Update final MCP Manifest
update_mcp_manifest("SESSION_FINISHED", 8, {
    "total_artifacts": len(df_art),
    "report_markdown_path": report_path
})
save_pipeline_state()

print(f"\\n🎉 Pipeline Berhasil Selesai Sepenuhnya!")
print(f"📁 Direktori Sesi : {session_dirs['root']}")
print(f"📄 Laporan MD     : {report_path}")
print(f"📦 Total Artefak  : {len(df_art)} berkas tersimpan.")""")

    return {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }

if __name__ == "__main__":
    nb_dict = build_notebook()
    print(f"Generated notebook with {len(nb_dict['cells'])} cells.")
    
    # Syntax test for all code cells
    for i, cell in enumerate(nb_dict["cells"]):
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            # Remove ipython magics like !pip for ast testing
            clean_src = "\n".join([line if not line.strip().startswith("!") else "# " + line for line in src.split("\n")])
            try:
                ast.parse(clean_src)
                print(f"✅ Cell {i:02d} Python Syntax OK")
            except SyntaxError as e:
                print(f"❌ Cell {i:02d} Syntax Error: {e}")
                sys.exit(1)

    # Save to target files
    targets = [
        "notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb",
        "notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb"
    ]
    for target in targets:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(nb_dict, f, ensure_ascii=False, indent=1)
        print(f"💾 Successfully written to: {target}")
