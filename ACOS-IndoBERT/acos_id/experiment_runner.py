"""Script runner untuk eksperimen multi-epoch, multi-ratio, dan cross-validation.

Jalankan sebagai sel di notebook ACOS atau langsung sebagai script Python:

    python -m acos_id.experiment_runner --help

Atau import fungsinya:

    from acos_id.experiment_runner import run_all_experiments
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Template konfigurasi eksperimen
# ──────────────────────────────────────────────────────────────────────────────

# Default grid: semua kombinasi yang ingin dijalankan
DEFAULT_EPOCHS = [50, 75, 100]
DEFAULT_RATIOS = [
    (0.8, 0.1),   # 80:10:10
    (0.7, 0.15),  # 70:15:15
    (0.6, 0.2),   # 60:20:20
]
DEFAULT_CV = [
    {"n_splits": 5},
    {"n_splits": 10},
]


# ──────────────────────────────────────────────────────────────────────────────
# Fungsi utama runner
# ──────────────────────────────────────────────────────────────────────────────

def prepare_all_data(
    indo_root: str,
    tokenizer,
    *,
    epochs_list: List[int] = None,
    ratio_list: List[tuple] = None,
    cv_configs: List[dict] = None,
    seed: int = 42,
    force_rebuild: bool = False,
) -> dict:
    """Bangun semua TSV mentah + tokenisasi untuk semua eksperimen sekaligus.

    Harus dijalankan SATU KALI sebelum training loop dimulai.
    Hasilnya di-cache — pemanggilan berikutnya akan skip jika sudah ada.

    Args:
        indo_root     : root folder ACOS-IndoBERT.
        tokenizer     : BertTokenizer sudah dimuat.
        epochs_list   : daftar epoch (tidak perlu diproses di sini, hanya dicatat).
        ratio_list    : daftar (train_ratio, dev_ratio).
        cv_configs    : daftar {"n_splits": 5} atau {"n_splits": 10}.
        seed          : random seed.
        force_rebuild : jika True, rebuild semua meski sudah ada.

    Returns:
        dict berisi path semua data yang sudah siap.
    """
    from .cross_val import (
        build_with_ratio, build_kfold_splits, tokenize_all_splits,
    )

    ratio_list = ratio_list or DEFAULT_RATIOS
    cv_configs = cv_configs or DEFAULT_CV

    processed_dir = os.path.join(indo_root, "data", "Apps-ACOS", "processed")
    data_base = os.path.join(indo_root, "data", "Apps-ACOS")
    tokenized_base = os.path.join(indo_root, "tokenized_data")

    prepared: dict = {"ratios": {}, "cv": {}}
    ratio_labels: List[str] = []

    # 1. Build TSV untuk setiap ratio
    print("=" * 60)
    print("📂 FASE 1: Membangun dataset untuk setiap split ratio")
    print("=" * 60)
    for train_r, dev_r in ratio_list:
        test_r = round(1.0 - train_r - dev_r, 4)
        label = f"split_{int(train_r*100)}{int(dev_r*100)}{int(test_r*100)}"
        out_dir = os.path.join(data_base, label)
        tsv_check = os.path.join(out_dir, "appsid_quad_train.tsv")

        if not force_rebuild and os.path.exists(tsv_check):
            print(f"  ⏩ {label}: TSV sudah ada — skip rebuild")
        else:
            print(f"  🔨 Membangun {label} ...")
            build_with_ratio(
                processed_dir, out_dir,
                train_ratio=train_r, dev_ratio=dev_r, seed=seed,
            )

        prepared["ratios"][label] = out_dir
        ratio_labels.append(label)

    # 2. Build TSV untuk setiap CV config
    print("\n" + "=" * 60)
    print("📂 FASE 2: Membangun dataset untuk Cross-Validation")
    print("=" * 60)
    for cv_cfg in cv_configs:
        n_splits = cv_cfg["n_splits"]
        cv_label = f"cv_{n_splits}fold"
        out_base = os.path.join(data_base, cv_label)
        report_check = os.path.join(out_base, "_cv_report.json")

        if not force_rebuild and os.path.exists(report_check):
            print(f"  ⏩ {cv_label}: splits sudah ada — skip rebuild")
        else:
            print(f"  🔨 Membangun {cv_label} ...")
            build_kfold_splits(
                processed_dir, out_base,
                n_splits=n_splits, seed=seed, build_tsv=True,
            )

        prepared["cv"][cv_label] = out_base

    # 3. Tokenisasi semua
    print("\n" + "=" * 60)
    print("🔤 FASE 3: Tokenisasi semua TSV")
    print("=" * 60)
    tokenize_all_splits(
        tokenizer,
        data_base=data_base,
        tokenized_base=tokenized_base,
        domain="appsid",
        ratio_labels=ratio_labels,
        cv_configs=cv_configs,
        force=force_rebuild,
    )

    # Simpan manifest
    manifest = {
        "prepared_at": datetime.now().isoformat(),
        "seed": seed,
        "ratio_labels": ratio_labels,
        "cv_configs": cv_configs,
        "paths": prepared,
    }
    manifest_path = os.path.join(tokenized_base, "_experiment_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print(f"\n✅ Semua data siap. Manifest: {manifest_path}")
    return prepared


def run_all_experiments(
    train_fn,
    indo_root: str,
    *,
    epochs_list: List[int] = None,
    ratio_list: List[tuple] = None,
    cv_configs: List[dict] = None,
    seed: int = 42,
    mode: str = "all",
    dry_run: bool = False,
) -> List[dict]:
    """Jalankan semua kombinasi eksperimen secara berurutan (1 per 1).

    Otomatis: setiap eksperimen selesai → lanjut ke berikutnya.
    Setiap hasil disimpan di folder bertimestamp terpisah.

    Args:
        train_fn    : fungsi training dengan signature:
                      ``train_fn(cfg) -> dict``
                      di mana cfg berisi:
                      ``{"type", "epochs", "tokenized_dir", "result_dir", ...}``
        indo_root   : root folder ACOS-IndoBERT.
        epochs_list : daftar epoch (default: [50, 75, 100]).
        ratio_list  : daftar (train_ratio, dev_ratio).
        cv_configs  : daftar {"n_splits": N}.
        seed        : random seed.
        mode        : "all"   → jalankan semua kombinasi,
                      "ratio" → hanya split-ratio,
                      "cv"    → hanya cross-validation.
        dry_run     : jika True, tampilkan rencana tanpa training.

    Returns:
        list dict hasil setiap eksperimen::

            [{"run_id": ..., "result_dir": ..., "metrics": {...}, ...}, ...]
    """
    from .cross_val import ExperimentGrid

    epochs_list = epochs_list or DEFAULT_EPOCHS
    ratio_list = ratio_list or DEFAULT_RATIOS
    cv_configs = cv_configs or DEFAULT_CV

    grid = ExperimentGrid()
    grid.add_epochs(epochs_list)

    if mode in ("all", "ratio"):
        grid.add_ratios(ratio_list)
    if mode in ("all", "cv"):
        for cv_cfg in cv_configs:
            grid.add_cv(n_splits=cv_cfg["n_splits"])

    grid.print_summary()

    if dry_run:
        print("\n⚠️  dry_run=True — tidak ada training yang dijalankan.")
        return []

    tokenized_base = os.path.join(indo_root, "tokenized_data")
    results_base = os.path.join(indo_root, "results", "experiments")
    os.makedirs(results_base, exist_ok=True)

    all_results: List[dict] = []
    total = len(grid)

    print(f"\n🚀 Memulai {total} eksperimen...\n")

    for run_idx, cfg in enumerate(grid, 1):
        run_id = cfg["run_id"]
        ts = datetime.now().strftime("%d%m%Y_%H%M")
        result_dir = os.path.join(results_base, f"{run_id}_{ts}")
        os.makedirs(result_dir, exist_ok=True)

        # Tentukan tokenized_dir berdasarkan tipe eksperimen
        if cfg["type"] == "ratio":
            train_r, dev_r, test_r = cfg["train_ratio"], cfg["dev_ratio"], cfg["test_ratio"]
            label = f"split_{int(train_r*100)}{int(dev_r*100)}{int(test_r*100)}"
            tokenized_dir = os.path.join(tokenized_base, label)
        else:  # cv
            n_splits = cfg["n_splits"]
            fold_idx = cfg["fold_idx"]
            tokenized_dir = os.path.join(
                tokenized_base, f"cv_{n_splits}fold", f"fold_{fold_idx}")

        full_cfg = {
            **cfg,
            "run_idx": run_idx,
            "total_runs": total,
            "tokenized_dir": tokenized_dir,
            "result_dir": result_dir,
            "seed": seed,
            "started_at": datetime.now().isoformat(),
        }

        print("=" * 70)
        print(f"  [{run_idx:3d}/{total}] {run_id}")
        print(f"           tokenized: {tokenized_dir}")
        print(f"           result   : {result_dir}")
        print("=" * 70)

        if not os.path.isdir(tokenized_dir):
            print(f"  ❌ tokenized_dir tidak ada: {tokenized_dir}")
            print(f"     Jalankan prepare_all_data() terlebih dahulu.")
            all_results.append({**full_cfg, "status": "SKIP_NO_DATA"})
            continue

        t0 = time.time()
        try:
            metrics = train_fn(full_cfg)
            duration = time.time() - t0
            result = {
                **full_cfg,
                "status": "OK",
                "duration_sec": round(duration, 1),
                "metrics": metrics or {},
                "finished_at": datetime.now().isoformat(),
            }
        except Exception as exc:
            duration = time.time() - t0
            result = {
                **full_cfg,
                "status": "ERROR",
                "error": str(exc),
                "duration_sec": round(duration, 1),
                "finished_at": datetime.now().isoformat(),
            }
            print(f"  ❌ Error: {exc}")

        all_results.append(result)

        # Simpan hasil per-run
        result_path = os.path.join(result_dir, "run_result.json")
        with open(result_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False, default=str)

        if result["status"] == "OK":
            m = result.get("metrics", {})
            print(f"  ✅ Selesai dalam {duration/60:.1f} menit | "
                  f"Step1 F1={m.get('step1_f1', '?')} "
                  f"Step2 F1={m.get('step2_f1', '?')}")

        # Simpan progress keseluruhan
        _save_experiment_log(results_base, all_results)

    # Ringkasan akhir
    print("\n" + "=" * 70)
    print("📊 RINGKASAN EKSPERIMEN")
    print("=" * 70)
    ok = [r for r in all_results if r["status"] == "OK"]
    err = [r for r in all_results if r["status"] == "ERROR"]
    skip = [r for r in all_results if r["status"] == "SKIP_NO_DATA"]
    print(f"  Total  : {total}")
    print(f"  ✅ OK   : {len(ok)}")
    print(f"  ❌ Error: {len(err)}")
    print(f"  ⏩ Skip : {len(skip)}")

    if ok:
        print("\n  Top 5 berdasarkan Step1 F1:")
        sorted_ok = sorted(
            ok, key=lambda r: r.get("metrics", {}).get("step1_f1", 0), reverse=True)
        for r in sorted_ok[:5]:
            m = r.get("metrics", {})
            print(f"    {r['run_id']:40s} → S1={m.get('step1_f1','?')} "
                  f"S2={m.get('step2_f1','?')}")

    return all_results


def _save_experiment_log(results_base: str, all_results: list):
    """Simpan progress log agar bisa dipantau saat training berjalan."""
    log_path = os.path.join(results_base, "_experiment_progress.json")
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "total": len(all_results),
            "ok": sum(1 for r in all_results if r["status"] == "OK"),
            "error": sum(1 for r in all_results if r["status"] == "ERROR"),
            "results": all_results,
        }, fh, indent=2, ensure_ascii=False, default=str)


# ──────────────────────────────────────────────────────────────────────────────
# Aggregator metrik CV
# ──────────────────────────────────────────────────────────────────────────────

def aggregate_cv_results(all_results: List[dict], n_splits: int) -> dict:
    """Agregasi hasil K-Fold CV: hitung mean ± std F1 per epoch.

    Args:
        all_results : output dari run_all_experiments().
        n_splits    : jumlah fold (5 atau 10).

    Returns:
        dict::

            {
                "cv_5fold": {
                    50: {"step1_f1_mean": ..., "step1_f1_std": ..., ...},
                    75: {...},
                    100: {...},
                }
            }
    """
    import statistics

    cv_key = f"cv_{n_splits}fold"
    cv_runs = [
        r for r in all_results
        if r.get("type") == "cv" and r.get("n_splits") == n_splits
        and r.get("status") == "OK"
    ]

    by_epoch: dict = {}
    for r in cv_runs:
        ep = r["epochs"]
        m = r.get("metrics", {})
        by_epoch.setdefault(ep, {"step1_f1": [], "step2_f1": []})
        if "step1_f1" in m:
            by_epoch[ep]["step1_f1"].append(m["step1_f1"])
        if "step2_f1" in m:
            by_epoch[ep]["step2_f1"].append(m["step2_f1"])

    agg: dict = {}
    for ep, vals in by_epoch.items():
        entry: dict = {"epoch": ep, "n_folds_completed": len(vals["step1_f1"])}
        for key in ("step1_f1", "step2_f1"):
            vs = vals[key]
            if vs:
                entry[f"{key}_mean"] = round(statistics.mean(vs), 4)
                entry[f"{key}_std"] = round(statistics.stdev(vs) if len(vs) > 1 else 0.0, 4)
                entry[f"{key}_min"] = round(min(vs), 4)
                entry[f"{key}_max"] = round(max(vs), 4)
        agg[ep] = entry

    return {cv_key: agg}


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main(argv=None):
    """CLI: tampilkan ringkasan grid default."""
    from .cross_val import ExperimentGrid

    grid = ExperimentGrid()
    grid.add_epochs(DEFAULT_EPOCHS)
    grid.add_ratios(DEFAULT_RATIOS)
    for cv_cfg in DEFAULT_CV:
        grid.add_cv(n_splits=cv_cfg["n_splits"])
    grid.print_summary()
    print(f"\n  Total: {len(grid)} run")
    print("\nGunakan run_all_experiments() di notebook untuk menjalankan semua.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
