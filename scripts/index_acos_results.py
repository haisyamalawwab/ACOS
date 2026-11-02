"""Bangun indeks run eksperimen di ACOS-IndoBERT/results untuk perencanaan EDA & ablas.

Hanya membaca berkas (read-only): run_config.json, run_result.json, training_log.csv.
Menulis dua CSV ke results/_index/. Jalankan: python scripts/index_acos_results.py
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re

RESULTS = os.path.join("ACOS-IndoBERT", "results")
DATA = os.path.join("ACOS-IndoBERT", "data", "Apps-ACOS")
TOK = os.path.join("ACOS-IndoBERT", "tokenized_data")
OUT = os.path.join(RESULTS, "_index")

RUN_RE = re.compile(r"^(cv(?P<nf>\d+)fold)_fold(?P<fold>\d+)_ep(?P<ep>\d+)_(?P<ts>\d{8}_\d{4})")


def count_quads(path: str) -> tuple[int, int]:
    """(baris, quadruple) berkas appsid_quad_*.tsv — kolom 2..n adalah quad."""
    lines = quads = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            lines += 1
            quads += max(len(line.rstrip("\n").split("\t")) - 1, 0)
    return lines, quads


def index_runs() -> list[dict]:
    rows = []
    for d in sorted(os.listdir(RESULTS)):
        m = RUN_RE.match(d)
        if not m:
            continue
        cfg_p = os.path.join(RESULTS, d, "run_config.json")
        res_p = os.path.join(RESULTS, d, "run_result.json")
        cfg = json.load(open(cfg_p, encoding="utf-8")) if os.path.exists(cfg_p) else {}
        res = json.load(open(res_p, encoding="utf-8")) if os.path.exists(res_p) else {}
        logs = glob.glob(os.path.join(RESULTS, d, "**", "training_log.csv"), recursive=True)
        evals = glob.glob(os.path.join(RESULTS, d, "**", "eval_per_epoch.csv"), recursive=True)
        files = [f for _, _, fs in os.walk(os.path.join(RESULTS, d)) for f in fs]
        dirs = [p for p, _, _ in os.walk(os.path.join(RESULTS, d))][1:]
        inner = cfg.get("config", {})
        rows.append({
            "dir_name": d,
            "family": "cv5" if m.group("nf") == "5" else "cv10",
            "n_folds": m.group("nf"),
            "fold": m.group("fold"),
            "epochs": m.group("ep"),
            "wave_ts": m.group("ts"),
            "run_id": res.get("run_id", ""),
            "run_idx": res.get("run_idx", ""),
            "total_runs": res.get("total_runs", ""),
            "status": res.get("status", "NO_RESULT_FILE"),
            "error": res.get("error", ""),
            "duration_sec": res.get("duration_sec", ""),
            "backend": inner.get("backend", ""),
            "amp": inner.get("amp", ""),
            "amp_dtype": inner.get("amp_dtype", ""),
            "seed": res.get("seed", inner.get("seed", "")),
            "has_config": os.path.exists(cfg_p),
            "has_result": os.path.exists(res_p),
            "training_log_count": len(logs),
            "eval_log_count": len(evals),
            "n_files": len(files),
            "n_empty_subdirs": sum(
                1 for p in dirs if not glob.glob(os.path.join(p, "**", "*"), recursive=True)),
            "referenced_tokenized_dir": res.get("tokenized_dir", ""),
        })
    return rows


def index_partitions() -> list[dict]:
    rows = []
    parts = []
    for fold in sorted(glob.glob(os.path.join(DATA, "cv_5fold", "fold_*"))):
        parts.append(("cv5", os.path.basename(fold), fold))
    for fold in sorted(glob.glob(os.path.join(DATA, "cv_10fold", "fold_*")),
                       key=lambda p: int(re.search(r"\d+", os.path.basename(p)).group())):
        parts.append(("cv10", os.path.basename(fold), fold))
    for split in sorted(glob.glob(os.path.join(DATA, "split_*"))):
        parts.append(("ratio", os.path.basename(split), split))
    parts.append(("base", "base_79_11_10", DATA))

    for family, label, path in parts:
        rec = {"family": family, "partition": label, "path": os.path.relpath(path, ".")}
        for s in ("train", "dev", "test"):
            p = os.path.join(path, f"appsid_quad_{s}.tsv")
            if os.path.exists(p):
                lines, quads = count_quads(p)
                rec[f"{s}_lines"] = lines
                rec[f"{s}_quads"] = quads
            else:
                rec[f"{s}_lines"] = rec[f"{s}_quads"] = ""
        if family == "cv5":
            tok = os.path.join(TOK, "cv_5fold", label)
        elif family == "cv10":
            tok = os.path.join(TOK, "cv_10fold", label)
        elif family == "ratio":
            tok = os.path.join(TOK, label)
        else:
            tok = TOK
        rec["tokenized_dir_expected"] = os.path.relpath(tok, ".")
        rec["tokenized_dir_present"] = os.path.isdir(tok)
        rec["tokenized_files_present"] = len(
            glob.glob(os.path.join(tok, "appsid_*_quad_bert.tsv"))) if os.path.isdir(tok) else 0
        rec["id_to_split_present"] = os.path.exists(os.path.join(path, "id_to_split.json"))
        rec["report_present"] = bool(glob.glob(os.path.join(path, "_*.json")))
        # Deteksi apakah dev adalah irisan dari train (bukan bagian hold-out terpisah),
        # dengan membandingkan jumlah baris/quad terhadap laporan partition aslinya.
        rec["sum_lines"] = sum(int(rec[f"{s}_lines"] or 0) for s in ("train", "dev", "test"))
        rec["sum_quads"] = sum(int(rec[f"{s}_quads"] or 0) for s in ("train", "dev", "test"))
        rec["exceeds_dataset"] = rec["sum_lines"] > 76077 or rec["sum_quads"] > 92074
        rec["quad_share_of_total"] = round(100 * rec["sum_quads"] / 92074, 2)
        rec["train_share_of_fold"] = (
            round(100 * int(rec["train_quads"] or 0) / rec["sum_quads"], 2)
            if rec["sum_quads"] else "")
        rows.append(rec)
    return rows


def write(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def index_grid(rows: list[dict]) -> list[dict]:
    """Matriks sel grid (family x epochs x fold) beserta jumlah percobaannya."""
    per_cell: dict[tuple, list[dict]] = {}
    for r in rows:
        per_cell.setdefault((r["family"], r["n_folds"], r["epochs"], int(r["fold"])), []).append(r)
    out = []
    for (fam, nf, ep, fold), runs in sorted(
            per_cell.items(), key=lambda x: (x[0][0], -int(x[0][1]), int(x[0][2]), x[0][3])):
        waves = sorted(r["wave_ts"] for r in runs)
        statuses = {r["status"] for r in runs}
        out.append({
            "family": fam, "n_folds": nf, "epochs": ep, "fold": fold,
            "n_attempts": len(runs), "attempt_waves": ";".join(waves),
            "run_idx": runs[0]["run_idx"],
            "statuses": ";".join(sorted(statuses)),
            "max_duration_sec": max((float(r["duration_sec"]) for r in runs if r["duration_sec"]),
                                    default=""),
            "has_training_log": any(int(r["training_log_count"]) > 0 for r in runs),
            "grid_cell_exists": True,
        })
    # Sel yang seharusnya ada di grid tapi tidak punya folder sama sekali
    missing = []
    for fam, nf in (("cv5", 5), ("cv10", 10)):
        for ep in ("50", "75", "100"):
            for fold in range(1, nf + 1):
                if (fam, nf, ep, fold) not in per_cell:
                    missing.append({"family": fam, "n_folds": nf, "epochs": ep,
                                    "fold": fold, "n_attempts": 0, "attempt_waves": "",
                                    "run_idx": "", "statuses": "TIDAK_PERNAH_DIJALANKAN",
                                    "max_duration_sec": "", "has_training_log": False,
                                    "grid_cell_exists": False})
    return out + missing


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    runs = index_runs()
    parts = index_partitions()
    grid = index_grid(runs)
    write(os.path.join(OUT, "run_index.csv"), runs)
    write(os.path.join(OUT, "data_partition_index.csv"), parts)
    write(os.path.join(OUT, "grid_coverage.csv"), grid)
    print(f"run_index.csv            : {len(runs)} baris")
    print(f"data_partition_index.csv : {len(parts)} baris")
    print(f"grid_coverage.csv        : {len(grid)} baris")
    from collections import Counter
    print("per family  :", dict(Counter(r["family"] for r in runs)))
    print("per status  :", dict(Counter(r["status"] for r in runs)))
    print("per error   :", dict(Counter((r["error"] or "n/a")[:32] for r in runs)))
    print("sel grid    :", sum(1 for g in grid if g["grid_cell_exists"]), "ada,",
          sum(1 for g in grid if not g["grid_cell_exists"]), "tidak pernah dijalankan")
    print("percobaan per sel (min/max):",
          min(g["n_attempts"] for g in grid), "/", max(g["n_attempts"] for g in grid))
    print("tokenized dir tersinkron :",
          sum(1 for p in parts if p["tokenized_dir_present"]), "/", len(parts))
    print("partition yang dev-nya tumpang tindih train:",
          [p["partition"] for p in parts if p["exceeds_dataset"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
