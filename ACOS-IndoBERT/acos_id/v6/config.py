"""Satu-satunya titik konfigurasi dinamis V6."""
from __future__ import annotations

import ast
import os

DEFAULTS = {
    "GPU_TIER_OVERRIDE": "AUTO",
    "DOMAIN": "appsid", "BACKBONE": "indobert",
    "EXPERIMENT_EPOCHS": [50, 75, 100],
    "EXPERIMENT_RATIOS": [(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)],
    "EXPERIMENT_CV": [{"n_splits": 5}, {"n_splits": 10}],
    "RUN_MODE": "all", "DRY_RUN": True, "RUN_EPOCHS": None,
    "STEP1_BATCH": None, "STEP2_BATCH": None,
    "STEP1_LR": 2e-5, "STEP2_LR": 5e-5,
    "MAX_SEQ_LENGTH": 128, "SEED": 42, "DO_LOWER_CASE": True,
    "DRIVE_SYNC": True, "FORCE_REBUILD_DATA": None, "RESUME": None,
}

TIER_PRESETS = {
    "LARGE": {"b1": 96, "b2": 64, "accum": 1, "workers": 4, "cache": False, "resume": False},
    "MEDIUM": {"b1": 32, "b2": 24, "accum": 2, "workers": 2, "cache": True, "resume": True},
    "SMALL": {"b1": 16, "b2": 8, "accum": 4, "workers": 2, "cache": True, "resume": True},
}


def _env(name, default=None):
    v = os.environ.get(name)
    return default if v is None or v == "" else v


def build_config(overrides: dict | None = None) -> dict:
    """Gabung DEFAULTS + overrides dict + env ACOS_*; validasi ringan."""
    cfg = dict(DEFAULTS)
    cfg.update(overrides or {})
    if _env("ACOS_TIER") is not None:
        cfg["GPU_TIER_OVERRIDE"] = _env("ACOS_TIER")
    if _env("ACOS_MODE") is not None:
        cfg["RUN_MODE"] = _env("ACOS_MODE")
    if _env("ACOS_DRY") is not None:
        cfg["DRY_RUN"] = str(_env("ACOS_DRY")).lower() in ("1", "true", "ya")
    for k, env in (("RUN_EPOCHS", "ACOS_EPOCHS"), ("STEP1_BATCH", "ACOS_BATCH1"), ("STEP2_BATCH", "ACOS_BATCH2")):
        if _env(env) is not None:
            try:
                cfg[k] = list(ast.literal_eval(_env(env))) if k == "RUN_EPOCHS" else int(_env(env))
            except Exception:
                pass
    assert all(e > 0 for e in cfg["EXPERIMENT_EPOCHS"])
    assert all(0 < a < 1 and 0 < b < 1 and a + b < 1 for a, b in cfg["EXPERIMENT_RATIOS"])
    assert cfg["RUN_MODE"] in ("all", "ratio", "cv")
    return cfg


def resolve(cfg: dict, detected_tier: str, backend: str) -> dict:
    """Terapkan preset tier + override eksplisit -> dict efektif datar."""
    tier = cfg["GPU_TIER_OVERRIDE"] if cfg["GPU_TIER_OVERRIDE"] != "AUTO" else detected_tier
    p = TIER_PRESETS.get(tier, TIER_PRESETS["SMALL"])
    amp = "bfloat16" if backend == "rocm" and tier == "LARGE" else "float16"
    eff = dict(cfg)
    eff.update({
        "TIER": tier,
        "STEP1_BATCH_SIZE": int(cfg["STEP1_BATCH"] or p["b1"]),
        "STEP2_BATCH_SIZE": int(cfg["STEP2_BATCH"] or p["b2"]),
        "GRAD_ACCUM_STEPS": p["accum"], "NUM_WORKERS": p["workers"],
        "USE_AMP": True, "AMP_DTYPE": amp,
        "TRAIN_FROM_SCRATCH": tier == "LARGE",
        "USE_MODEL_CACHE": p["cache"] if cfg["FORCE_REBUILD_DATA"] is None else not cfg["FORCE_REBUILD_DATA"],
        "FORCE_REBUILD_DATA": False if cfg["FORCE_REBUILD_DATA"] is None else bool(cfg["FORCE_REBUILD_DATA"]),
        "RESUME_LAST_SESSION": p["resume"] if cfg["RESUME"] is None else bool(cfg["RESUME"]),
        "PATIENCE": 0, "ROCM_BENCHMARK": True,
        "RUN_EPOCHS": list(cfg["RUN_EPOCHS"]) if cfg["RUN_EPOCHS"] else list(cfg["EXPERIMENT_EPOCHS"]),
    })
    return eff
