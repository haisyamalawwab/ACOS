"""ACOS v6 modular library — thin, reusable, upgradeable.

Pakai dari notebook tipis atau dari GitHub langsung:

    %pip install -q git+https://github.com/haisyamalawwab/ACOS.git#subdirectory=ACOS-IndoBERT
    from acos_id.v6 import boot, run_eda, run_grid, train_factory

    cfg = boot.build_config({"DRY_RUN": True, "RUN_MODE": "ratio"})
    ctx = boot.setup(cfg)
"""
from __future__ import annotations

__version__ = "6.0.0"
__all__ = ["config", "gpu", "drive", "paths", "loader", "monitor", "eda_runner", "viz", "train", "runner", "boot"]
