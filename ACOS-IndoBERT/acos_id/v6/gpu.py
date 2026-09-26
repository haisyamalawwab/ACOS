"""Deteksi GPU dual-backend ROCm/CUDA/CPU + tier adaptif."""
from __future__ import annotations

import shutil
import subprocess


def _smi_ok() -> bool:
    for cmd in (["rocm-smi", "--showmeminfo", "vram", "--json"],
                ["nvidia-smi", "--query-gpu=memory.used,memory.total",
                 "--format=csv,noheader,nounits"]):
        if not shutil.which(cmd[0]):
            continue
        try:
            subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10, text=True)
            return True
        except Exception:
            continue
    return False


def detect() -> dict:
    """Kembalikan {backend, gpu_name, vram_gb, tier, has_cuda}."""
    try:
        import torch
        cuda = torch.cuda.is_available()
        rocm = cuda and "rocm" in torch.__version__.lower()
    except Exception:
        cuda, rocm = False, False
    name, vram = "CPU", 0.0
    if cuda:
        import torch as _t
        p = _t.cuda.get_device_properties(0)
        name, vram = p.name, p.total_memory / 1024 ** 3
    low = name.lower()
    if vram <= 0:
        tier = "SMALL"
    elif "t4" in low or vram <= 20:
        tier = "SMALL"
    elif "l4" in low or vram <= 40:
        tier = "MEDIUM"
    else:
        tier = "LARGE"
    backend = "rocm" if rocm else ("cuda" if cuda else "cpu")
    return {"backend": backend, "gpu_name": name, "vram_gb": round(vram, 2),
            "tier": tier, "has_cuda": cuda, "smi_ok": _smi_ok()}
