#!/usr/bin/env python3
"""Audit 041 — analisis mendalam 45 berkas .ipynb (stdlib murni).

Menghasilkan:
  reports/041_data/notebooks_inventaris.csv   satu baris per notebook
  reports/041_data/notebooks_metrik.csv       metrik yang benar-benar tercetak di output
  reports/041_data/notebooks_galat.csv        sel yang berakhir dengan traceback
  reports/041_data/notebooks_jejak.csv        jejak path/sesi/flag per notebook
  reports/041_data/audit_041_results.json     agregat + sidik jari kode

Jalankan:  python3 scripts/audit_041_notebooks.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "041_data")

METRIC_RE = re.compile(
    r"(micro[-_ ]?F1|Micro_F1|quad(?:ruple)?[-_ ]?F1|Quad[-_ ]?F1|"
    r"sentiment_acc|category_micro_f1|accuracy|Accuracy|Acc)\s*[:=]?\s*"
    r"([0-9]{1,3}[.,][0-9]{1,6})\s*(%?)"
)
NUM_PCT = re.compile(r"\b([0-9]{2}[.,][0-9]{2})\s*%")
SESSION_RE = re.compile(r"\b(appsid|rest16|laptop)_\d{8}_\d{6}(?:xxx)?\b")
DRIVE_RE = re.compile(r"/content/drive/MyDrive/[^\s\"'\\]+,?")
ERROR_RE = re.compile(r"Traceback \(most recent call last\)")


def text_of(src) -> str:
    return "".join(src) if isinstance(src, list) else str(src or "")


def out_text(cell) -> str:
    parts = []
    for o in cell.get("outputs", []):
        t = o.get("text")
        if t:
            parts.append(text_of(t))
        for key in ("data",):
            d = o.get(key) or {}
            for mime in ("text/plain", "text/markdown", "text/html"):
                if mime in d:
                    parts.append(text_of(d[mime]))
    return "".join(parts)


def has_image(cell) -> int:
    n = 0
    for o in cell.get("outputs", []):
        d = o.get("data") or {}
        if any(k.startswith("image/") for k in d):
            n += 1
    return n


def code_hash(cells) -> str:
    h = hashlib.sha256()
    for c in cells:
        if c.get("cell_type") == "code":
            h.update(text_of(c.get("source")).encode("utf-8"))
            h.update(b"\x00")
    return h.hexdigest()[:16]


def family(path: str) -> str:
    b = os.path.basename(path)
    d = os.path.dirname(path)
    if path.startswith("ACOS-BERT/") or "/ACOS-BERT/" in path:
        return "ACOS-BERT V1"
    if "Kaggle" in b:
        return "Kaggle (2 salinan)"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_ASLI"):
        return "ASLI"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_PRO_Resume"):
        return "PRO Resume"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_PRO"):
        return "PRO"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_UPDATE"):
        return "UPDATE"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_V2"):
        return "V2 STAGED"
    if b.startswith("00_ACOS_Master_Pipeline_Colab_V3"):
        return "V3 ACOSE"
    if "V4_1" in b:
        return "V4.1"
    if "V4_2" in b:
        return "V4.2"
    if "V4_3" in b:
        return "V4.3"
    if "V4_BERT_rest16" in b:
        return "V4 BERT MI300X"
    if "V4_INDOBERT_run24092026" in b:
        return "V4 IndoBERT MI300X"
    if "V4_INDOBERT_run08092026" in b:
        return "V4 IndoBERT 0809"
    if "V4_INDOBERT copy" in b:
        return "V4 IndoBERT (copy)"
    if "V4_INDOBERT" in b and b.startswith("00_"):
        return "V4 IndoBERT"
    if b.startswith("01_ACOS_MI300X_V5"):
        return "V5 MI300X"
    if b.startswith("01_ACOS_V5_1"):
        return "V5.1"
    if b.startswith("02_ACOS_V5_2_1"):
        return "V5.2.1"
    if b.startswith("02_ACOS_V5_2"):
        return "V5.2"
    if b.startswith("03_ACOS_V5_3"):
        return "V5.3"
    if "V5_EN_REST16_LAPTOP" in b:
        return "V5 EN rest16"
    if b == "00_ACOS_Master_Pipeline_Colab.ipynb":
        return "Colab dasar"
    if re.match(r"0[1-5]_ACOS_", b) and d == "notebooks":
        return "Lokal 01-05"
    if b == "GPU_Status.ipynb":
        return "Utilitas"
    return "lain"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for base, _dirs, files in os.walk(ROOT):
        if "/.git" in base or "/.arena" in base:
            continue
        for f in files:
            if f.endswith(".ipynb"):
                paths.append(os.path.join(base, f))
    paths.sort()

    inv_rows, met_rows, err_rows, trace_rows = [], [], [], []
    agg = {"n": len(paths), "cells": 0, "code": 0, "md": 0, "outputs": 0,
           "errors": 0, "never_run": 0, "images": 0, "metrics": 0,
           "families": {}, "hashes": {}}

    for p in paths:
        rel = os.path.relpath(p, ROOT)
        try:
            nb = json.load(open(p, encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            inv_rows.append([rel, os.path.getsize(p), 0, 0, 0, 0, 0, 0, 0, 0,
                             "RUSAK", family(rel), str(exc)[:120]])
            continue
        cells = nb.get("cells", [])
        code = [c for c in cells if c.get("cell_type") == "code"]
        md = [c for c in cells if c.get("cell_type") == "markdown"]
        meta = nb.get("metadata", {})
        kern = (meta.get("kernelspec") or {}).get("name", "") or meta.get("language_info", {}).get("name", "")
        n_out = sum(1 for c in code if c.get("outputs"))
        n_err = 0
        n_img = sum(has_image(c) for c in code)
        never = [c for c in code if c.get("execution_count") is None]
        execs = [c.get("execution_count") for c in code if isinstance(c.get("execution_count"), int)]
        src_all = "\n".join(text_of(c.get("source")) for c in cells)
        out_all_len = sum(len(out_text(c)) for c in code)

        nb_metrics = []
        for ci, c in enumerate(cells):
            txt = out_text(c)
            for o in c.get("outputs", []):
                if o.get("output_type") == "error":
                    n_err += 1
                    err_rows.append([rel, ci, c.get("execution_count"), o.get("ename", ""),
                                     (o.get("evalue") or "")[:160]])
            if not txt:
                continue
            for m in METRIC_RE.finditer(txt):
                val = m.group(2).replace(",", ".")
                try:
                    fval = float(val)
                except ValueError:
                    continue
                if fval > 100.5 and not m.group(3):
                    continue
                ctx = txt[max(0, m.start() - 90): m.end() + 60].replace("\n", " ").strip()
                nb_metrics.append((ci, c.get("execution_count"), m.group(1), fval, bool(m.group(3)), ctx))

        seen = set()
        for ci, ec, name, val, pct, ctx in nb_metrics:
            key = (ci, name, round(val, 3))
            if key in seen:
                continue
            seen.add(key)
            met_rows.append([rel, ci, ec, name, f"{val:.4f}", "ya" if pct else "tidak", ctx[:220]])
            agg["metrics"] += 1

        sessions = sorted(set(SESSION_RE.findall(src_all + "\n" + "\n".join(out_text(c) for c in code))))
        sess_full = sorted(set(re.findall(r"\b(?:appsid|rest16|laptop)_\d{8}_\d{6}(?:xxx)?\b", src_all)))
        drive_roots = sorted(set(re.findall(r"/content/drive/MyDrive/([A-Za-z0-9_.\-]+)", src_all)))
        flags = []
        for flag in ("DRY_RUN", "SKIP_TRAINING", "USE_DUAL_HEAD", "use_dual_head", "CACHE"):
            vals = sorted(set(re.findall(rf"(?m)^\s*{flag}\s*=\s*(True|False)", src_all)))
            envs = sorted(set(re.findall(rf"['\"]{flag}['\"]\s*:\s*(True|False)", src_all)))
            if vals or envs:
                flags.append(f"{flag}={'/'.join(vals + envs)}")
        datasets = sorted({d for d in ("appsid", "rest16", "laptop") if re.search(rf"\b{d}\b", src_all, re.I)})
        gpus = sorted({g for g in ("T4", "A100", "MI300X", "ROCm", "rocm", "cuda", "mps") if g in src_all})

        trace_rows.append([rel, family(rel), kern, ";".join(sess_full)[:300], ";".join(drive_roots),
                           ";".join(flags), ";".join(datasets), ";".join(gpus),
                           "ya" if "save_pretrained" in src_all else "tidak",
                           "ya" if "SubtaskMetricCapture" in src_all else "tidak"])

        fam = family(rel)
        n_orphan = sum(1 for c in code if c.get("outputs") and c.get("execution_count") is None)
        inv_rows.append([rel, os.path.getsize(p), len(cells), len(code), len(md), n_out, n_orphan,
                         n_err, len(never), n_img, len(execs),
                         f"{min(execs)}..{max(execs)}" if execs else "—",
                         "ya" if execs and execs != sorted(execs) else "tidak",
                         len(nb_metrics), fam, code_hash(code)])
        agg["cells"] += len(cells)
        agg["code"] += len(code)
        agg["md"] += len(md)
        agg["outputs"] += n_out
        agg["errors"] += n_err
        agg["never_run"] += len(never)
        agg["images"] += n_img
        agg["families"][fam] = agg["families"].get(fam, 0) + 1
        agg["hashes"].setdefault(code_hash(code), []).append(rel)

    with open(os.path.join(OUT, "notebooks_inventaris.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["notebook", "ukuran_byte", "sel", "sel_kode", "sel_md", "sel_beroutput",
                    "sel_output_yatim", "sel_error", "sel_kode_tanpa_eksekusi", "sel_bergambar", "sel_tereksekusi",
                    "rentang_exec", "exec_tidak_monoton", "jumlah_metrik", "keluarga", "hash_kode"])
        w.writerows(inv_rows)

    with open(os.path.join(OUT, "notebooks_metrik.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["notebook", "sel", "exec_count", "metrik", "nilai", "persen", "konteks"])
        w.writerows(met_rows)

    with open(os.path.join(OUT, "notebooks_galat.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["notebook", "sel", "exec_count", "error", "pesan"])
        w.writerows(err_rows)

    with open(os.path.join(OUT, "notebooks_jejak.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["notebook", "keluarga", "kernel", "sesi_drive", "root_drive",
                    "flag", "dataset", "gpu", "pakai_save_pretrained", "pakai_subtask_capture"])
        w.writerows(trace_rows)

    # kemiripan kode antar notebook (Jaccard 8-gram atas seluruh sel kode)
    grams = {}
    for p in paths:
        rel = os.path.relpath(p, ROOT)
        try:
            nb = json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        txt = " ".join(re.sub(r"\s+", " ", text_of(c.get("source"))) for c in nb.get("cells", []) if c.get("cell_type") == "code")
        toks = txt.split()
        grams[rel] = {" ".join(toks[i:i + 8]) for i in range(max(0, len(toks) - 7))}
    pairs = []
    names = sorted(grams)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = grams[a], grams[b]
            if not A or not B:
                continue
            inter = len(A & B)
            if not inter:
                continue
            j = inter / len(A | B)
            if j >= 0.40:
                pairs.append([a, b, f"{j:.3f}", len(A), len(B), inter])
    pairs.sort(key=lambda r: -float(r[2]))
    with open(os.path.join(OUT, "notebooks_kemiripan.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["notebook_a", "notebook_b", "jaccard_8gram", "shingle_a", "shingle_b", "irisan"])
        w.writerows(pairs)
    agg["pasangan_mirip"] = len(pairs)

    dups = {h: v for h, v in agg["hashes"].items() if len(v) > 1}
    agg["duplikat_kode"] = dups
    agg["total_metrik_baris"] = len(met_rows)
    agg["total_error_sel"] = len(err_rows)
    with open(os.path.join(OUT, "audit_041_results.json"), "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2, ensure_ascii=False)

    print(json.dumps({k: v for k, v in agg.items() if k != "hashes"}, indent=2, ensure_ascii=False)[:4000])


if __name__ == "__main__":
    main()
