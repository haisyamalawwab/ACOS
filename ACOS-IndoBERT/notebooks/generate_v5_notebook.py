"""Generator notebook V5 — AMD MI300X Full Experiment Pipeline.

Jalankan:
    python generate_v5_notebook.py

Output:
    ACOS-IndoBERT/notebooks/01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb
"""
import json
import os

# ─── Helpers ─────────────────────────────────────────────────────────────────

def md(source: str):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip("\n"),
    }


def code(source: str, tags=None):
    meta = {}
    if tags:
        meta["tags"] = tags
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": meta,
        "outputs": [],
        "source": source.strip("\n"),
    }


# ─── Cells ───────────────────────────────────────────────────────────────────

CELLS = []

# ── HEADER ──────────────────────────────────────────────────────────────────
CELLS.append(md(r"""# ACOS IndoBERT V5 — Full Experiment Pipeline (GPU AMD MI300X)

> **Notebook ini dirancang khusus untuk GPU enterprise (AMD MI300X 191 GB VRAM).**
> Tidak menggunakan early stopping. Menjalankan semua kombinasi eksperimen
> (multi-epoch × multi-split-ratio × K-Fold CV) secara otomatis.

| Item | Nilai |
|------|-------|
| **GPU Target** | AMD Instinct MI300X VF — 191.69 GB VRAM |
| **Akselerator** | AMD ROCm HIP |
| **Early Stopping** | ❌ DINONAKTIFKAN (`PATIENCE = 0`) |
| **Epoch** | 50 / 75 / 100 |
| **Split Ratio** | 80:10:10 / 70:15:15 / 60:20:20 |
| **Cross Validation** | 5-Fold & 10-Fold (berbasis review_id) |
| **Total Run** | 54 (serial, otomatis) |
| **Monitoring** | VRAM, waktu per epoch, ROCm stats, progress log |

---

## Alur Eksekusi

```
Sel 1  : Diagnostik GPU & Hardware (wajib)
Sel 2  : Konfigurasi (PATIENCE=0, batch besar)
Sel 3  : Import & path setup
Sel 4  : Hardware Monitor — kelas monitoring real-time
Sel 5  : Verifikasi backbone IndoBERT
Sel 6  : ExperimentGrid — preview 54 run
Sel 7  : Persiapan data (build TSV + tokenisasi semua)
Sel 8  : Training adapter function
Sel 9  : Run semua eksperimen (otomatis)
Sel 10 : Agregasi & perbandingan hasil
```
"""))

# ── SEL 1: GPU DIAGNOSTICS ──────────────────────────────────────────────────
CELLS.append(md("## Sel 1 — Diagnostik GPU & Hardware"))

CELLS.append(code(r"""# ============================================================
#  Sel 1: Diagnostik GPU & Hardware (AMD MI300X / ROCm)
#  Wajib dijalankan pertama. Mendeteksi platform dan memvalidasi
#  bahwa GPU enterprise tersedia dan VRAM mencukupi.
# ============================================================
import subprocess, sys, os, time, platform, json
from datetime import datetime

SESSION_START = datetime.now()
SESSION_START_TS = SESSION_START.strftime("%d%m%Y_%H%M%S")
print(f"Waktu mulai sesi : {SESSION_START.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Python           : {sys.version}")
print(f"Platform         : {platform.platform()}")
print()

# ── Deteksi GPU / akselerator ───────────────────────────────────────────────
import torch

HAS_CUDA  = torch.cuda.is_available()
HAS_ROCM  = HAS_CUDA and "rocm" in torch.__version__.lower()
DEVICE    = "cuda" if HAS_CUDA else "cpu"

print(f"PyTorch version  : {torch.__version__}")
print(f"CUDA available   : {HAS_CUDA}")
print(f"ROCm/HIP         : {HAS_ROCM}")
print(f"Device           : {DEVICE}")
print()

if HAS_CUDA:
    n_gpu = torch.cuda.device_count()
    print(f"GPU count        : {n_gpu}")
    for i in range(n_gpu):
        props = torch.cuda.get_device_properties(i)
        vram_gb = props.total_memory / 1024**3
        print(f"  GPU[{i}] : {props.name}")
        print(f"          VRAM  = {vram_gb:.2f} GB ({props.total_memory:,} bytes)")
        print(f"          SM    = {props.multi_processor_count} multiprocessors")
    print()

# ── ROCm-SMI diagnostik (jika tersedia) ─────────────────────────────────────
try:
    rocm_out = subprocess.check_output(
        ["rocm-smi", "--showmeminfo", "vram", "--json"],
        stderr=subprocess.DEVNULL, timeout=10, text=True,
    )
    rocm_data = json.loads(rocm_out)
    print("ROCm-SMI VRAM:")
    for card, info in rocm_data.items():
        used  = int(info.get("VRAM Total Used Memory (B)", 0)) / 1024**3
        total = int(info.get("VRAM Total Memory (B)", 0)) / 1024**3
        print(f"  {card}: {used:.2f} / {total:.2f} GB")
    ROCM_SMI_OK = True
except Exception:
    print("rocm-smi tidak tersedia — monitoring VRAM via torch.cuda")
    ROCM_SMI_OK = False

# ── Validasi GPU cukup besar ─────────────────────────────────────────────────
MIN_VRAM_GB = 16.0
if HAS_CUDA:
    props = torch.cuda.get_device_properties(0)
    TOTAL_VRAM_GB = props.total_memory / 1024**3
    IS_LARGE_GPU  = TOTAL_VRAM_GB >= MIN_VRAM_GB
    GPU_NAME      = props.name
else:
    TOTAL_VRAM_GB = 0.0
    IS_LARGE_GPU  = False
    GPU_NAME      = "CPU"

print()
print("=" * 60)
print(f"GPU Name         : {GPU_NAME}")
print(f"Total VRAM       : {TOTAL_VRAM_GB:.2f} GB")
print(f"IS_LARGE_GPU     : {IS_LARGE_GPU}")
if not IS_LARGE_GPU:
    print("PERINGATAN: VRAM < 16 GB — notebook ini dioptimalkan untuk GPU besar!")
print("=" * 60)
"""))

# ── SEL 2: KONFIGURASI MI300X ───────────────────────────────────────────────
CELLS.append(md("""## Sel 2 — Konfigurasi (Dioptimalkan untuk AMD MI300X)

> **Perubahan kunci vs V4:**
> - `PATIENCE = 0` → no early stopping
> - `STEP1_BATCH_SIZE = 96` → 4x dari V4 (24)
> - `STEP2_BATCH_SIZE = 64` → 4x dari V4 (16)
> - `RESUME_LAST_SESSION = False` → folder baru
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 2: Konfigurasi Master — AMD MI300X Edition
# ============================================================

# ── Domain & backbone ────────────────────────────────────────
DOMAIN   = "appsid"
BACKBONE = "indobert"

# ── Dimensi eksperimen ───────────────────────────────────────
EXPERIMENT_EPOCHS  = [50, 75, 100]          # loop otomatis
EXPERIMENT_RATIOS  = [                       # train:dev:test
    (0.8, 0.1),   # 80:10:10
    (0.7, 0.15),  # 70:15:15
    (0.6, 0.2),   # 60:20:20
]
EXPERIMENT_CV      = [
    {"n_splits": 5},
    {"n_splits": 10},
]

# ── Hyperparameter training (MI300X — batch besar) ───────────
MAX_SEQ_LENGTH     = 128
STEP1_BATCH_SIZE   = 96    # V4: 24  → x4 untuk VRAM 191 GB
STEP2_BATCH_SIZE   = 64    # V4: 16  → x4
STEP1_LR           = 2e-5
STEP2_LR           = 5e-5
SEED               = 42
DO_LOWER_CASE      = True

# ── Early stopping: NONAKTIF untuk GPU besar ─────────────────
PATIENCE               = 0    # 0 = DINONAKTIFKAN
MIN_EPOCHS_BEFORE_STOP = 5    # tidak relevan bila PATIENCE=0

# ── Session control ──────────────────────────────────────────
RESUME_LAST_SESSION = False   # selalu buat folder baru

# ── ROCm optimizations ───────────────────────────────────────
ROCM_BENCHMARK     = True     # torch.backends.cudnn.benchmark
USE_AMP            = True     # Automatic Mixed Precision (fp16/bf16)
AMP_DTYPE          = "bfloat16"  # bf16 lebih stabil dari fp16 di MI300X
GRAD_ACCUM_STEPS   = 1        # gradient accumulation (1 = off)
NUM_WORKERS        = 4        # DataLoader workers

# ── Monitoring ───────────────────────────────────────────────
LOG_EVERY_N_STEPS  = 10       # cetak stats setiap N batch
MONITOR_VRAM       = True     # catat VRAM per epoch
SAVE_HARDWARE_LOG  = True     # simpan log hardware ke JSON

# ── Print ringkasan konfigurasi ───────────────────────────────
print("=" * 60)
print("KONFIGURASI AMD MI300X V5")
print("=" * 60)
print(f"Domain          : {DOMAIN}")
print(f"Backbone        : {BACKBONE}")
print()
print(f"Experiment epochs : {EXPERIMENT_EPOCHS}")
print(f"Experiment ratios : {EXPERIMENT_RATIOS}")
print(f"Experiment CV     : {EXPERIMENT_CV}")
print()
print(f"STEP1_BATCH_SIZE  : {STEP1_BATCH_SIZE} (V4: 24)")
print(f"STEP2_BATCH_SIZE  : {STEP2_BATCH_SIZE} (V4: 16)")
print(f"PATIENCE          : {PATIENCE} (0 = no early stop)")
print(f"RESUME_LAST_SESSION: {RESUME_LAST_SESSION}")
print()
print(f"USE_AMP           : {USE_AMP} ({AMP_DTYPE})")
print(f"GRAD_ACCUM_STEPS  : {GRAD_ACCUM_STEPS}")
print(f"ROCM_BENCHMARK    : {ROCM_BENCHMARK}")
print("=" * 60)
"""))

# ── SEL 3: IMPORT & PATH SETUP ──────────────────────────────────────────────
CELLS.append(md("## Sel 3 — Import & Path Setup"))

CELLS.append(code(r"""# ============================================================
#  Sel 3: Import semua modul & setup path dua-root
# ============================================================
import os, sys, time, json, pickle, re, math, random
import subprocess
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# ── Deteksi root (lokal vs Docker vs Colab) ──────────────────
_this_nb = Path(globals().get("__file__", __file__ if "__file__" in dir() else ".")).resolve()
_nb_dir  = _this_nb.parent if _this_nb.is_file() else Path.cwd()

# Root kandidat (sesuaikan jika berbeda)
_ROOT_CANDIDATES = [
    Path("/shared-docker/ACOS"),
    _nb_dir.parent,
    _nb_dir.parent.parent,
    Path("d:/laragon/www/ACOS-ASLI"),
]

base_project_dir = None
for _c in _ROOT_CANDIDATES:
    if (_c / "Extract-Classify-ACOS").exists() and (_c / "ACOS-IndoBERT").exists():
        base_project_dir = str(_c)
        break

if base_project_dir is None:
    raise RuntimeError(
        "Tidak dapat menemukan root proyek (yang berisi "
        "Extract-Classify-ACOS/ dan ACOS-IndoBERT/). "
        "Edit _ROOT_CANDIDATES di Sel 3."
    )

upstream_root = os.path.join(base_project_dir, "Extract-Classify-ACOS")
indo_root     = os.path.join(base_project_dir, "ACOS-IndoBERT")

for p in [base_project_dir, upstream_root, indo_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

print(f"base_project_dir : {base_project_dir}")
print(f"upstream_root    : {upstream_root}")
print(f"indo_root        : {indo_root}")

# ── Import modul upstream ────────────────────────────────────
from bert_utils.tokenization import BertTokenizer
import processor_utils as acos_proc
import model_utils as acos_model

# ── Import modul acos_id ─────────────────────────────────────
import acos_id
from acos_id import taxonomy as acos_taxonomy
from acos_id import checkpoint as acos_ckpt
from acos_id.cross_val import (
    build_with_ratio, build_kfold_splits,
    ExperimentGrid, tokenize_all_splits,
)
from acos_id.experiment_runner import (
    prepare_all_data, run_all_experiments, aggregate_cv_results,
)

# ── Seed global ──────────────────────────────────────────────
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    if ROCM_BENCHMARK:
        torch.backends.cudnn.benchmark = True

# ── Path data & hasil ────────────────────────────────────────
data_dir        = os.path.join(indo_root, "data", "Apps-ACOS")
processed_dir   = os.path.join(data_dir, "processed")
tokenized_base  = os.path.join(indo_root, "tokenized_data")
results_base    = os.path.join(indo_root, "results")
experiments_dir = os.path.join(results_base, "experiments")
bert_cache_dir  = os.path.join(indo_root, "backbones", "indobert_base_p1")

os.makedirs(experiments_dir, exist_ok=True)

print()
print(f"data_dir        : {data_dir}")
print(f"tokenized_base  : {tokenized_base}")
print(f"experiments_dir : {experiments_dir}")
print(f"bert_cache_dir  : {bert_cache_dir}")
print()
print("Import semua modul: OK")
"""))

# ── SEL 4: HARDWARE MONITOR ─────────────────────────────────────────────────
CELLS.append(md("""## Sel 4 — Hardware Monitor

Kelas `HardwareMonitor` mencatat VRAM, waktu per epoch, GPU utilization,
dan menyimpan semua log ke JSON untuk analisis setelah training selesai.
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 4: HardwareMonitor — monitoring real-time GPU AMD MI300X
# ============================================================
import threading, time, subprocess, json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class EpochStats:
    epoch: int
    phase: str = ""                    # "step1" atau "step2"
    run_id: str = ""
    epoch_start: float = 0.0
    epoch_end: float = 0.0
    duration_sec: float = 0.0
    loss: float = 0.0
    f1: float = 0.0
    vram_used_gb: float = 0.0
    vram_total_gb: float = 0.0
    vram_pct: float = 0.0
    gpu_util_pct: Optional[float] = None
    batch_per_sec: float = 0.0
    samples_per_sec: float = 0.0


@dataclass
class RunStats:
    run_id: str
    started_at: str = ""
    finished_at: str = ""
    total_duration_sec: float = 0.0
    config: dict = field(default_factory=dict)
    epochs: List[EpochStats] = field(default_factory=list)
    hardware: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)


class HardwareMonitor:
    """Monitor real-time GPU VRAM, waktu per epoch, dan statistik hardware.

    Penggunaan:
        monitor = HardwareMonitor(log_dir="results/experiments/run_1")
        monitor.start_run("split_801010_ep50")

        # Per epoch:
        monitor.start_epoch(epoch=1, phase="step1")
        # ... training epoch ...
        stats = monitor.end_epoch(loss=0.42, f1=96.5,
                                  n_batches=2507, batch_size=96)
        print(stats)

        monitor.end_run(metrics={"step1_f1": 97.1})
    """

    def __init__(self, log_dir: str, device: int = 0):
        self.log_dir   = log_dir
        self.device    = device
        self._run: Optional[RunStats] = None
        self._epoch_start = 0.0
        self._current_epoch_idx = 0
        self._current_phase = ""
        os.makedirs(log_dir, exist_ok=True)

    # ── Public API ────────────────────────────────────────────

    def start_run(self, run_id: str, config: dict = None):
        hw = self._collect_hardware()
        self._run = RunStats(
            run_id=run_id,
            started_at=datetime.now().isoformat(),
            config=config or {},
            hardware=hw,
        )
        self._print_header(run_id, hw)

    def start_epoch(self, epoch: int, phase: str = "step1"):
        self._epoch_start = time.time()
        self._current_epoch_idx = epoch
        self._current_phase = phase

    def end_epoch(self, loss: float, f1: float,
                  n_batches: int = 0, batch_size: int = 96) -> EpochStats:
        t_end = time.time()
        dur   = t_end - self._epoch_start
        vram  = self._get_vram()
        gpu_u = self._get_gpu_util()
        bps   = n_batches / dur if dur > 0 else 0
        sps   = (n_batches * batch_size) / dur if dur > 0 else 0

        stats = EpochStats(
            epoch=self._current_epoch_idx,
            phase=self._current_phase,
            run_id=self._run.run_id if self._run else "",
            epoch_start=self._epoch_start,
            epoch_end=t_end,
            duration_sec=round(dur, 2),
            loss=round(loss, 6),
            f1=round(f1, 4),
            vram_used_gb=vram["used_gb"],
            vram_total_gb=vram["total_gb"],
            vram_pct=vram["pct"],
            gpu_util_pct=gpu_u,
            batch_per_sec=round(bps, 2),
            samples_per_sec=round(sps, 1),
        )

        if self._run:
            self._run.epochs.append(stats)

        self._print_epoch(stats)
        return stats

    def end_run(self, metrics: dict = None):
        if not self._run:
            return
        self._run.finished_at = datetime.now().isoformat()
        self._run.total_duration_sec = sum(
            e.duration_sec for e in self._run.epochs)
        self._run.metrics = metrics or {}
        self._save_log()
        self._print_footer()

    def get_current_vram_str(self) -> str:
        v = self._get_vram()
        return f"{v['used_gb']:.2f}/{v['total_gb']:.2f} GB ({v['pct']:.1f}%)"

    # ── Internal ──────────────────────────────────────────────

    def _get_vram(self) -> dict:
        if not torch.cuda.is_available():
            return {"used_gb": 0.0, "total_gb": 0.0, "pct": 0.0}
        used  = torch.cuda.memory_allocated(self.device)
        total = torch.cuda.get_device_properties(self.device).total_memory
        used_gb  = used / 1024**3
        total_gb = total / 1024**3
        return {
            "used_gb": round(used_gb, 3),
            "total_gb": round(total_gb, 3),
            "pct": round(used_gb / total_gb * 100, 2) if total_gb > 0 else 0.0,
        }

    def _get_gpu_util(self) -> Optional[float]:
        """Utilization via rocm-smi atau nvidia-smi."""
        try:
            if HAS_ROCM:
                out = subprocess.check_output(
                    ["rocm-smi", "--showuse", "--json"],
                    stderr=subprocess.DEVNULL, timeout=5, text=True)
                data = json.loads(out)
                for card, info in data.items():
                    util = info.get("GPU use (%)", None)
                    if util is not None:
                        return float(util)
            else:
                out = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu",
                     "--format=csv,noheader,nounits"],
                    stderr=subprocess.DEVNULL, timeout=5, text=True)
                return float(out.strip().split("\n")[0])
        except Exception:
            pass
        return None

    def _collect_hardware(self) -> dict:
        hw: dict = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform.platform(),
            "python": sys.version,
            "torch": torch.__version__,
            "cuda_available": HAS_CUDA,
            "rocm": HAS_ROCM,
        }
        if HAS_CUDA:
            props = torch.cuda.get_device_properties(0)
            hw["gpu_name"]    = props.name
            hw["vram_total_gb"] = round(props.total_memory / 1024**3, 3)
            hw["sm_count"]    = props.multi_processor_count
        return hw

    def _save_log(self):
        if not self._run:
            return
        path = os.path.join(self.log_dir, "hardware_log.json")
        data = asdict(self._run)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)

    def _print_header(self, run_id: str, hw: dict):
        print(f"\n{'='*70}")
        print(f"  RUN: {run_id}")
        print(f"  GPU: {hw.get('gpu_name', 'CPU')} | "
              f"VRAM: {hw.get('vram_total_gb', 0):.2f} GB | "
              f"ROCm: {hw.get('rocm', False)}")
        print(f"  Start: {self._run.started_at}")
        print(f"{'='*70}")
        print(f"  {'Epoch':>5} {'Phase':>6} {'Loss':>9} {'F1%':>7} "
              f"{'VRAM':>13} {'Util%':>6} {'Samp/s':>8} {'Dur':>8}")
        print(f"  {'-'*5} {'-'*6} {'-'*9} {'-'*7} "
              f"{'-'*13} {'-'*6} {'-'*8} {'-'*8}")

    def _print_epoch(self, s: EpochStats):
        vram_str = f"{s.vram_used_gb:.2f}/{s.vram_total_gb:.2f}G"
        util_str = f"{s.gpu_util_pct:.0f}%" if s.gpu_util_pct is not None else "  N/A"
        dur_str  = _fmt_dur(s.duration_sec)
        print(f"  {s.epoch:>5} {s.phase:>6} {s.loss:>9.4f} {s.f1:>7.2f} "
              f"{vram_str:>13} {util_str:>6} {s.samples_per_sec:>8.0f} {dur_str:>8}")

    def _print_footer(self):
        total = self._run.total_duration_sec if self._run else 0
        print(f"  {'─'*70}")
        print(f"  Selesai: {self._run.finished_at}")
        print(f"  Total duration: {_fmt_dur(total)}")
        m = self._run.metrics if self._run else {}
        print(f"  Metrics: Step1 F1={m.get('step1_f1','?')} | "
              f"Step2 F1={m.get('step2_f1','?')}")
        print(f"{'='*70}\n")


def _fmt_dur(sec: float) -> str:
    if sec < 60:
        return f"{sec:.1f}s"
    m, s = divmod(int(sec), 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m"


print("HardwareMonitor: OK")
"""))

# ── SEL 5: BACKBONE & TOKENIZER ─────────────────────────────────────────────
CELLS.append(md("## Sel 5 — Backbone IndoBERT & Tokenizer"))

CELLS.append(code(r"""# ============================================================
#  Sel 5: Siapkan backbone IndoBERT & tokenizer
# ============================================================
from acos_id.checkpoint import prepare_backbone, BACKBONES

print("Mempersiapkan backbone IndoBERT...")
backbone_report = prepare_backbone(BACKBONE, bert_cache_dir)
print(f"  Rekey: {backbone_report['rekey'].get('dilewati', False) and 'dilewati' or 'selesai'}")

tokenizer = BertTokenizer.from_pretrained(bert_cache_dir, do_lower_case=DO_LOWER_CASE)
print(f"  Tokenizer vocab: {len(tokenizer.vocab):,} token")

# ── Validasi dataset ─────────────────────────────────────────
for split in ("train", "dev", "test"):
    fpath = os.path.join(data_dir, f"appsid_quad_{split}.tsv")
    n = sum(1 for _ in open(fpath, encoding="utf-8")) if os.path.exists(fpath) else 0
    status = "OK" if n > 0 else "MISSING"
    print(f"  Dataset {split:5s}: {n:7,} baris  [{status}]")

print()
print("Backbone & tokenizer: OK")
"""))

# ── SEL 6: EXPERIMENT GRID ──────────────────────────────────────────────────
CELLS.append(md("""## Sel 6 — ExperimentGrid (Preview 54 Run)

Jalankan sel ini untuk **melihat semua rencana eksperimen tanpa training**.
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 6: Preview semua kombinasi eksperimen
# ============================================================
grid = ExperimentGrid()
grid.add_epochs(EXPERIMENT_EPOCHS)
grid.add_ratios(EXPERIMENT_RATIOS)
for cv_cfg in EXPERIMENT_CV:
    grid.add_cv(n_splits=cv_cfg["n_splits"])

grid.print_summary()
print(f"\nTotal: {len(grid)} run")
print(f"Estimasi waktu (50 epoch/run ~4 jam): {len(grid) * 4:.0f}+ jam total")
print("(gunakan EXPERIMENT_EPOCHS=[50] dan mode='ratio'|'cv' untuk subset)")
"""))

# ── SEL 7: PREPARE ALL DATA ─────────────────────────────────────────────────
CELLS.append(md("""## Sel 7 — Persiapan Data (Semua Split + Fold)

**Jalankan 1x saja.** Hasilnya di-cache — pemanggilan berikutnya skip file yang sudah ada.

Menghasilkan:
- `data/Apps-ACOS/split_801010/`, `split_701515/`, `split_602020/`
- `data/Apps-ACOS/cv_5fold/fold_1/` ... `fold_5/`
- `data/Apps-ACOS/cv_10fold/fold_1/` ... `fold_10/`
- `tokenized_data/` untuk semua di atas
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 7: Build semua TSV mentah + tokenisasi (1x, dicache)
# ============================================================
t0 = time.time()

prepared = prepare_all_data(
    indo_root=indo_root,
    tokenizer=tokenizer,
    ratio_list=EXPERIMENT_RATIOS,
    cv_configs=EXPERIMENT_CV,
    seed=SEED,
    force_rebuild=False,   # True untuk rebuild paksa
)

dur = time.time() - t0
print(f"\nTotal waktu persiapan data: {_fmt_dur(dur)}")
print("Data siap untuk training.")
"""))

# ── SEL 8: TRAINING ADAPTER ─────────────────────────────────────────────────
CELLS.append(md("""## Sel 8 — Training Adapter Function

Fungsi `train_one_run(cfg)` adalah jembatan antara `ExperimentGrid`
dan training loop V4 yang sudah ada. Setiap panggilan menjalankan
1 kombinasi (epoch × split) dari awal.
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 8: Adapter — satu run eksperimen
# ============================================================
from acos_id.session import session_dirs_from_root

# Import fungsi training dari V4 (sesuaikan nama jika beda)
# Jika pipeline V4 sudah modular, import langsung:
# from pipeline_v4 import run_step1_training, run_step2_training

def train_one_run(cfg: dict) -> dict:
    """Jalankan 1 run lengkap (Step 1 + Step 2) dengan konfigurasi dari grid.

    cfg berisi:
      cfg["epochs"]         = NUM_EPOCHS run ini
      cfg["tokenized_dir"]  = folder tokenized_data yang akan dipakai
      cfg["result_dir"]     = folder output checkpoint, CSV, log
      cfg["run_id"]         = nama unik run ini
      cfg["seed"]           = random seed
    """
    global PATIENCE, MIN_EPOCHS_BEFORE_STOP

    run_id    = cfg["run_id"]
    num_ep    = cfg["epochs"]
    tok_dir   = cfg["tokenized_dir"]
    res_dir   = cfg["result_dir"]
    seed      = cfg.get("seed", SEED)

    # Pastikan tokenized_dir ada
    if not os.path.isdir(tok_dir):
        raise FileNotFoundError(f"tokenized_dir tidak ada: {tok_dir}")

    # Setup session dirs
    sess = session_dirs_from_root(res_dir)

    # Monitor hardware
    monitor = HardwareMonitor(log_dir=res_dir, device=0)
    monitor.start_run(run_id, config=cfg)

    # ── AMP scaler ───────────────────────────────────────────
    scaler = None
    if USE_AMP and HAS_CUDA:
        scaler = torch.cuda.amp.GradScaler()

    # ── Load dataset ─────────────────────────────────────────
    def load_dataset(split):
        path = os.path.join(tok_dir, f"appsid_{split}_quad_bert.tsv")
        return acos_proc.load_and_cache_examples(
            task="acos_extraction",
            data_file=path,
            tokenizer=tokenizer,
            max_seq_length=MAX_SEQ_LENGTH,
        )

    train_data = load_dataset("train")
    dev_data   = load_dataset("dev")

    train_loader = DataLoader(train_data, batch_size=STEP1_BATCH_SIZE,
                              shuffle=True, num_workers=NUM_WORKERS)
    dev_loader   = DataLoader(dev_data, batch_size=STEP1_BATCH_SIZE,
                              shuffle=False, num_workers=NUM_WORKERS)

    # ── Model Step 1 ─────────────────────────────────────────
    model = acos_model.BertForQuadABSA.from_pretrained(
        bert_cache_dir,
        num_aspect_labels=len(acos_taxonomy.ASPECT_LABELS),
        num_opinion_labels=len(acos_taxonomy.OPINION_LABELS),
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=STEP1_LR)

    best_f1 = 0.0
    best_epoch = 0

    # ── Training loop Step 1 ─────────────────────────────────
    print(f"\n  [Step 1] Training {num_ep} epoch | batch={STEP1_BATCH_SIZE} | "
          f"PATIENCE={PATIENCE} | AMP={USE_AMP}")

    for epoch in range(1, num_ep + 1):
        monitor.start_epoch(epoch, phase="step1")
        model.train()
        total_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            optimizer.zero_grad()

            if USE_AMP and scaler:
                with torch.cuda.amp.autocast(dtype=torch.bfloat16
                                             if AMP_DTYPE == "bfloat16"
                                             else torch.float16):
                    outputs = model(**batch)
                    loss = outputs["loss"]
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(**batch)
                loss = outputs["loss"]
                loss.backward()
                optimizer.step()

            total_loss += loss.item()
            n_batches  += 1

            if LOG_EVERY_N_STEPS > 0 and n_batches % LOG_EVERY_N_STEPS == 0:
                print(f"    ep{epoch} batch{n_batches} loss={loss.item():.4f} "
                      f"VRAM={monitor.get_current_vram_str()}", end="\r")

        # ── Evaluasi dev ──────────────────────────────────────
        model.eval()
        tp = fp = fn = 0
        with torch.no_grad():
            for batch in dev_loader:
                batch = {k: v.to(DEVICE) for k, v in batch.items()}
                preds = model.predict(**batch)
                _tp, _fp, _fn = acos_proc.compute_tp_fp_fn(preds, batch)
                tp += _tp; fp += _fp; fn += _fn

        prec = tp / (tp + fp + 1e-9)
        rec  = tp / (tp + fn + 1e-9)
        f1   = 2 * prec * rec / (prec + rec + 1e-9) * 100

        avg_loss = total_loss / max(n_batches, 1)
        stats = monitor.end_epoch(avg_loss, f1, n_batches, STEP1_BATCH_SIZE)

        # Simpan checkpoint jika f1 meningkat
        if f1 > best_f1:
            best_f1   = f1
            best_epoch = epoch
            ckpt_path = os.path.join(sess["checkpoints"], "step1_best")
            model.save_pretrained(ckpt_path)
            print(f"    >> Checkpoint disimpan: ep{epoch} F1={f1:.2f}%")

        # Flush VRAM setiap epoch
        if MONITOR_VRAM:
            torch.cuda.empty_cache()

    print(f"\n  [Step 1] SELESAI | Best F1={best_f1:.2f}% di epoch {best_epoch}")

    # ── Step 2 (Category-Sentiment Classification) ────────────
    # ... (implementasi Step 2 serupa dengan Step 1) ...
    # Untuk sementara return placeholder
    step2_f1 = 0.0  # TODO: implementasi Step 2

    monitor.end_run(metrics={
        "step1_f1": round(best_f1, 4),
        "step1_best_epoch": best_epoch,
        "step2_f1": round(step2_f1, 4),
    })

    torch.cuda.empty_cache()
    return {"step1_f1": best_f1, "step2_f1": step2_f1}


print("train_one_run: terdefinisi.")
print()
print("Catatan: Step 2 masih perlu diimplementasi (mirip Step 1 tapi")
print("         pakai DataLoader pair.tsv dan model klasifikasi).")
"""))

# ── SEL 9: RUN ALL EXPERIMENTS ──────────────────────────────────────────────
CELLS.append(md("""## Sel 9 — Run Semua Eksperimen (Otomatis)

> **Estimasi: 5–8 hari untuk semua 54 run.**
>
> Gunakan parameter `mode` untuk subset:
> - `mode="ratio"` → hanya 9 run split-ratio
> - `mode="cv"` → hanya 45 run CV
> - `mode="all"` → semua 54 run
>
> Set `dry_run=True` untuk preview tanpa training.
"""))

CELLS.append(code(r"""# ============================================================
#  Sel 9: Jalankan semua eksperimen secara otomatis (1-per-1)
# ============================================================

# Preview dulu (dry_run=True) — ganti False untuk training sungguhan
DRY_RUN = True   # <─ GANTI False untuk training

all_results = run_all_experiments(
    train_fn=train_one_run,
    indo_root=indo_root,
    epochs_list=EXPERIMENT_EPOCHS,
    ratio_list=EXPERIMENT_RATIOS,
    cv_configs=EXPERIMENT_CV,
    seed=SEED,
    mode="all",        # "all", "ratio", atau "cv"
    dry_run=DRY_RUN,
)

print(f"\nStatus: {'DRY RUN selesai' if DRY_RUN else f'{len(all_results)} run selesai'}")
"""))

# ── SEL 10: AGREGASI HASIL ──────────────────────────────────────────────────
CELLS.append(md("## Sel 10 — Agregasi & Perbandingan Hasil"))

CELLS.append(code(r"""# ============================================================
#  Sel 10: Ringkasan & perbandingan semua hasil
# ============================================================

if not all_results:
    print("Belum ada hasil. Jalankan Sel 9 dengan dry_run=False.")
else:
    ok_results = [r for r in all_results if r.get("status") == "OK"]
    print(f"Total run selesai : {len(ok_results)} / {len(all_results)}")

    if ok_results:
        # ── Tabel ringkasan ───────────────────────────────────
        rows = []
        for r in ok_results:
            m = r.get("metrics", {})
            rows.append({
                "run_id"     : r["run_id"],
                "type"       : r["type"],
                "epochs"     : r["epochs"],
                "split"      : (f"{int(r.get('train_ratio',0)*100)}:"
                                f"{int(r.get('dev_ratio',0)*100)}"
                                if r["type"] == "ratio"
                                else f"cv{r.get('n_splits','?')}-fold{r.get('fold_idx','?')}"),
                "step1_f1"   : m.get("step1_f1", 0),
                "step2_f1"   : m.get("step2_f1", 0),
                "duration_m" : round(r.get("duration_sec", 0) / 60, 1),
            })

        df = pd.DataFrame(rows).sort_values("step1_f1", ascending=False)
        print("\nTop 10 berdasarkan Step1 F1:")
        print(df.head(10).to_string(index=False))

        # ── Agregasi CV ───────────────────────────────────────
        for n_splits in [5, 10]:
            agg = aggregate_cv_results(all_results, n_splits=n_splits)
            cv_key = f"cv_{n_splits}fold"
            if agg.get(cv_key):
                print(f"\nCV {n_splits}-Fold Aggregated:")
                df_cv = pd.DataFrame(agg[cv_key].values())
                cols  = ["epoch", "step1_f1_mean", "step1_f1_std",
                         "step2_f1_mean", "step2_f1_std", "n_folds_completed"]
                print(df_cv[[c for c in cols if c in df_cv.columns]].to_string(index=False))

        # ── Simpan tabel lengkap ──────────────────────────────
        summary_path = os.path.join(experiments_dir, "final_results_summary.csv")
        df.to_csv(summary_path, index=False)
        print(f"\nRingkasan disimpan: {summary_path}")
"""))

# ── SEL 11: HARDWARE SUMMARY ────────────────────────────────────────────────
CELLS.append(md("## Sel 11 — Ringkasan Penggunaan Hardware per Run"))

CELLS.append(code(r"""# ============================================================
#  Sel 11: Baca semua hardware_log.json dan buat ringkasan
# ============================================================
import glob

hw_logs = sorted(glob.glob(os.path.join(experiments_dir, "*", "hardware_log.json")))
print(f"Hardware logs ditemukan: {len(hw_logs)}")

hw_rows = []
for log_path in hw_logs:
    try:
        with open(log_path, encoding="utf-8") as fh:
            data = json.load(fh)
        epochs = data.get("epochs", [])
        if epochs:
            vram_vals = [e["vram_used_gb"] for e in epochs if e.get("vram_used_gb")]
            util_vals = [e["gpu_util_pct"] for e in epochs
                         if e.get("gpu_util_pct") is not None]
            hw_rows.append({
                "run_id"          : data.get("run_id", "?"),
                "total_dur_min"   : round(data.get("total_duration_sec", 0) / 60, 1),
                "epochs_logged"   : len(epochs),
                "vram_max_gb"     : max(vram_vals, default=0),
                "vram_avg_gb"     : round(sum(vram_vals) / len(vram_vals), 3) if vram_vals else 0,
                "gpu_util_avg_pct": round(sum(util_vals) / len(util_vals), 1) if util_vals else None,
                "step1_f1"        : data.get("metrics", {}).get("step1_f1", None),
            })
    except Exception as e:
        print(f"  Gagal baca {log_path}: {e}")

if hw_rows:
    df_hw = pd.DataFrame(hw_rows).sort_values("total_dur_min")
    print("\nRingkasan Hardware per Run:")
    print(df_hw.to_string(index=False))

    hw_summary_path = os.path.join(experiments_dir, "hardware_summary.csv")
    df_hw.to_csv(hw_summary_path, index=False)
    print(f"\nHardware summary disimpan: {hw_summary_path}")
else:
    print("Belum ada hardware log (jalankan training terlebih dahulu).")
"""))

# ── NOTEBOOK JSON ─────────────────────────────────────────────────────────────

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0",
        },
        "accelerator": "GPU",
        "notebook_version": "V5-MI300X",
        "created": "2026-09-24",
        "description": (
            "ACOS IndoBERT V5 — Full Experiment Pipeline khusus GPU AMD MI300X. "
            "No early stopping. Multi-epoch (50/75/100) x multi-split-ratio x K-Fold CV. "
            "Dengan hardware monitoring lengkap (VRAM, waktu, GPU util)."
        ),
    },
    "cells": CELLS,
}

# ── Tulis ke file ─────────────────────────────────────────────────────────────

out_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "ACOS-IndoBERT", "notebooks",
    "01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb",
)
out_path = os.path.normpath(out_path)

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(notebook, fh, indent=1, ensure_ascii=False)

print(f"Notebook berhasil dibuat:")
print(f"  {out_path}")
print(f"  Cells  : {len(CELLS)}")
print(f"  Size   : {os.path.getsize(out_path):,} bytes")
