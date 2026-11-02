#!/usr/bin/env python3
"""Audit 039 — rekalkulasi & verifikasi hasil repo ACOS (stdlib saja).

Menjalankan ulang pemeriksaan yang dipakai di
`reports/039_survey_analisis_mendalam_dan_peta_hasil_02112026_2148.md` dan menulis
ringkasan JSON ke `reports/039_data/audit_039_results.json`.

Pemakaian:
    python3 scripts/audit_039_repo.py            # dari root repo
"""
from __future__ import annotations

import collections
import csv
import glob
import hashlib
import json
import math
import os
import re
import statistics
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS")
TOK = os.path.join(ROOT, "ACOS-IndoBERT", "tokenized_data")
OUT = os.path.join(ROOT, "reports", "039_data", "audit_039_results.json")

SENT = {0: "negative", 1: "neutral", 2: "positive"}


def entropy(counter):
    n = sum(counter.values())
    return -sum((v / n) * math.log2(v / n) for v in counter.values() if v)


def read_quad(path):
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line:
            parts = line.split("\t")
            yield parts[0], parts[1:]


def audit_quad_files():
    out = {}
    clauses = {}
    for split in ("train", "dev", "test"):
        rows = list(read_quad(f"{APPS}/appsid_quad_{split}.tsv"))
        nt = imp_a = imp_o = bad = 0
        cats = collections.Counter()
        sents = collections.Counter()
        lengths = []
        short_tuples = 0
        clause = collections.Counter()
        for text, quads in rows:
            clause[text] += 1
            lengths.append(len(text.split()))
            for q in quads:
                f = q.split(" ")
                if len(f) != 4:
                    bad += 1
                    continue
                nt += 1
                cats[f[1]] += 1
                try:
                    sents[SENT.get(int(f[2]), f[2])] += 1
                except ValueError:
                    sents[f[2]] += 1
                a = list(map(int, f[0].split(",")))
                o = list(map(int, f[3].split(",")))
                if a == [-1, -1]:
                    imp_a += 1
                if o == [-1, -1]:
                    imp_o += 1
                if len(text.split()) <= 3:
                    short_tuples += 1
        out[split] = {
            "rows": len(rows),
            "tuples": nt,
            "unique_clauses": len(clause),
            "duplicate_clause_rows": sum(v - 1 for v in clause.values()),
            "implicit_aspect": imp_a,
            "implicit_opinion": imp_o,
            "categories": dict(cats.most_common()),
            "sentiment": dict(sents),
            "bad_quad_fields": bad,
            "tokens_mean": round(statistics.mean(lengths), 2),
            "tokens_median": statistics.median(lengths),
            "rows_le3_tokens": sum(1 for x in lengths if x <= 3),
            "tuples_in_le3_token_rows": short_tuples,
        }
        clauses[split] = clause
    out["total_tuples"] = sum(out[s]["tuples"] for s in ("train", "dev", "test"))
    out["total_rows"] = sum(out[s]["rows"] for s in ("train", "dev", "test"))
    for a, b in (("train", "test"), ("train", "dev"), ("val", "test")):
        if a == "val":
            continue
        common = set(clauses[a]) & set(clauses[b])
        rows = sum(clauses[b][c] for c in common)
        out[f"overlap_{a}_{b}"] = {
            "common_texts": len(common),
            "rows": rows,
            "pct_rows": round(100 * rows / out[b]["rows"], 2),
            "pct_unique": round(100 * len(common) / out[b]["unique_clauses"], 2),
        }
    return out


def audit_funnel():
    clean = set()
    with open(f"{APPS}/processed/reviews_clean.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            clean.add(r["review_id"])
    weak_reviews = set()
    weak_rows = 0
    weak_clauses = set()
    with open(f"{APPS}/processed/quintuples_weak.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            weak_rows += 1
            weak_reviews.add(r["review_id"])
            weak_clauses.add(r["clause"])
    ids = {}
    for split, fn in (("train", "train"), ("dev", "val"), ("test", "test")):
        ids[split] = set()
        for line in open(f"{APPS}/processed/stage2_{fn}.jsonl", encoding="utf-8"):
            ids[split].add(json.loads(line)["review_id"])
    stage = set().union(*ids.values())
    tsv_rows = 0
    tsv_clauses = set()
    for split in ("train", "dev", "test"):
        for text, _ in read_quad(f"{APPS}/appsid_quad_{split}.tsv"):
            tsv_rows += 1
            tsv_clauses.add(text)
    return {
        "reviews_clean": len(clean),
        "weak_rows": weak_rows,
        "weak_reviews": len(weak_reviews),
        "weak_clauses": len(weak_clauses),
        "reviews_without_tuple": len(clean - weak_reviews),
        "stage2_reviews": len(stage),
        "labels_but_no_split": len(weak_reviews - stage),
        "split_but_no_labels": len(stage - weak_reviews),
        "tsv_rows": tsv_rows,
        "tsv_unique_clauses": len(tsv_clauses),
        "tuples_dropped_in_conversion": weak_rows - 92074,
        "review_retention_pct": round(100 * len(stage) / len(clean), 2),
    }


def audit_split_snapshot():
    """Apakah review yang punya label tetapi tidak masuk split tersebar merata?"""
    ids = set()
    for sp in ("train", "val", "test"):
        for line in open(f"{APPS}/processed/stage2_{sp}.jsonl", encoding="utf-8"):
            ids.add(json.loads(line)["review_id"])
    first = {}
    nrow = 0
    with open(f"{APPS}/processed/quintuples_weak.csv", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            nrow = i
            first.setdefault(r["review_id"], i)
    dropped = [p for rid, p in first.items() if rid not in ids]
    kept = [p for rid, p in first.items() if rid in ids]
    deciles = collections.Counter(min(9, int(10 * p / max(nrow, 1))) for p in dropped)
    return {
        "file_rows": nrow + 1,
        "dropped_reviews": len(dropped),
        "kept_reviews": len(kept),
        "dropped_first_row_mean": round(statistics.mean(dropped), 1),
        "kept_first_row_mean": round(statistics.mean(kept), 1),
        "dropped_by_decile": {str(k + 1): deciles[k] for k in range(10)},
    }


def audit_stage_build():
    out = {}
    for st in ("stage1", "stage2"):
        for sp in ("train", "val", "test"):
            path = f"{APPS}/processed/{st}_{sp}.jsonl"
            if not os.path.exists(path):
                continue
            recs = 0
            keys = collections.Counter()
            reviews = set()
            for line in open(path, encoding="utf-8"):
                d = json.loads(line)
                recs += 1
                reviews.add(d["review_id"])
                if st == "stage1":
                    keys[tuple(d["tokens"])] += 1
                else:
                    keys[(d["review_id"], d["clause"], d["aspect"], d["category"], d["sentiment"])] += 1
            out[f"{st}_{sp}"] = {
                "records": recs,
                "unique_keys": len(keys),
                "duplicate_records": sum(v - 1 for v in keys.values()),
                "reviews": len(reviews),
            }
    # irisan klausa stage1 vs stage2
    s1 = set()
    for sp in ("train", "val", "test"):
        for line in open(f"{APPS}/processed/stage1_{sp}.jsonl", encoding="utf-8"):
            s1.add(" ".join(json.loads(line)["tokens"]))
    s2 = set()
    for sp in ("train", "val", "test"):
        for line in open(f"{APPS}/processed/stage2_{sp}.jsonl", encoding="utf-8"):
            s2.add(json.loads(line)["clause"])
    out["stage1_clauses"] = len(s1)
    out["stage2_clauses"] = len(s2)
    out["stage2_clauses_missing_in_stage1"] = len(s2 - s1)
    out["stage1_clauses_missing_in_stage2"] = len(s1 - s2)
    return out


def audit_emotion():
    pairs = collections.Counter()
    sentiment = collections.Counter()
    emotion = collections.Counter()
    with open(f"{APPS}/processed/quintuples_weak.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pairs[(r["sentiment"], r["emotion"])] += 1
            sentiment[r["sentiment"]] += 1
            emotion[r["emotion"]] += 1
    n = sum(pairs.values())
    h_s = entropy(sentiment)
    h_e = entropy(emotion)
    h_cond = 0.0
    top_share = {}
    for sent in sentiment:
        sub = collections.Counter({e: v for (s, e), v in pairs.items() if s == sent})
        tot = sum(sub.values())
        h_cond += (tot / n) * entropy(sub)
        top_share[sent] = round(100 * max(sub.values()) / tot, 2)
    return {
        "n": n,
        "H_sentiment": round(h_s, 3),
        "H_emotion": round(h_e, 3),
        "H_emotion_given_sentiment": round(h_cond, 3),
        "mutual_information": round(h_e - h_cond, 3),
        "top_emotion_share_per_sentiment_pct": top_share,
        "sentiment_emotion_pairs": {f"{k[0]}|{k[1]}": v for k, v in sorted(pairs.items())},
    }


def audit_tokenized():
    out = {}
    for split in ("train", "dev", "test"):
        pair = {}
        rows = 0
        for line in open(f"{TOK}/appsid_{split}_pair.tsv", encoding="utf-8"):
            rows += 1
            f = line.rstrip("\n").split("\t")
            labs = []
            for x in f[1:]:
                labs += x.split()
            pair[f[0]] = labs
        quads = missing = 0
        unk = 0
        for text, fields in read_quad(f"{TOK}/appsid_{split}_quad_bert.tsv"):
            unk += text.split().count("[UNK]")
            for q in fields:
                f = q.split(" ")
                if len(f) != 4:
                    missing += 1
                    continue
                quads += 1
                key = f"{text}####{f[0]} {f[3]}"
                if key not in pair or f"{f[1]}#{f[2]}" not in pair[key]:
                    missing += 1
        multilabel = sum(1 for v in pair.values() if len(set(v)) > 1)
        out[split] = {
            "quad_rows": sum(1 for _ in read_quad(f"{TOK}/appsid_{split}_quad_bert.tsv")),
            "quads": quads,
            "quads_missing_in_pair": missing,
            "unk_tokens": unk,
            "pair_rows": rows,
            "multilabel_pair_rows": multilabel,
            "multilabel_pct": round(100 * multilabel / rows, 2),
        }
    return out


def audit_cv():
    out = {}
    for cv in ("cv_5fold", "cv_10fold"):
        folds = sorted(glob.glob(f"{APPS}/{cv}/fold_*"))
        universe = set()
        tests = []
        overlap = 0
        for fdir in folds:
            mapping = json.load(open(f"{fdir}/id_to_split.json", encoding="utf-8"))
            by = collections.defaultdict(set)
            for rid, sp in mapping.items():
                by[sp].add(rid)
            universe |= set(mapping)
            tests.append(len(by["test"]))
            if (by["train"] & by["dev"]) or (by["train"] & by["test"]) or (by["dev"] & by["test"]):
                overlap += 1
        out[cv] = {
            "folds": len(folds),
            "unique_reviews": len(universe),
            "test_reviews_per_fold": tests,
            "sum_test_reviews": sum(tests),
            "folds_with_overlap": overlap,
            "has_fold_scores": any(
                os.path.exists(os.path.join(ROOT, "ACOS-IndoBERT", "results")) for _ in [0]
            ),
        }
    return out


def audit_inventory():
    files = [p for p in glob.glob(f"{ROOT}/**/*", recursive=True) if os.path.isfile(p) and "/.git/" not in p]
    ext = collections.Counter(os.path.splitext(p)[1].lower().lstrip(".") or "noext" for p in files)
    by_dir = collections.Counter(os.path.relpath(p, ROOT).split(os.sep)[0] for p in files)
    size = sum(os.path.getsize(p) for p in files)
    nb = glob.glob(f"{ROOT}/**/*.ipynb", recursive=True)
    cells = 0
    no_out = 0
    errors = 0
    for p in nb:
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        cs = data.get("cells", [])
        cells += len(cs)
        code = [c for c in cs if c.get("cell_type") == "code"]
        if not any(c.get("outputs") for c in code):
            no_out += 1
        for c in code:
            for o in c.get("outputs", []):
                if o.get("output_type") == "error":
                    errors += 1
    py = [p for p in files if p.endswith(".py")]
    loc = 0
    for p in py:
        loc += sum(1 for _ in open(p, encoding="utf-8", errors="ignore"))
    try:
        commits = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "HEAD"],
                                 capture_output=True, text=True, check=False).stdout.strip()
    except Exception:
        commits = "?"
    return {
        "files": len(files),
        "size_mb": round(size / 1e6, 1),
        "by_extension_top": dict(ext.most_common(12)),
        "files_by_top_dir": dict(by_dir.most_common()),
        "notebooks": len(nb),
        "notebook_cells": cells,
        "notebooks_without_output": no_out,
        "notebook_error_outputs": errors,
        "python_files": len(py),
        "python_loc": loc,
        "git_commits": commits,
    }


def audit_notebook_metrics():
    """Ambil angka hasil yang tercetak di output notebook (bukti tersimpan)."""
    patterns = [
        r"Micro-F1 terbaik tersimpan: ([0-9.]+)% \(epoch (\d+)\)",
        r"quadruple micro-F1 ([0-9.]+)%",
        r"Epoch (\d+) \| loss ([0-9.]+) \| P ([0-9.]+)% \| R ([0-9.]+)% \| micro-F1 ([0-9.]+)%",
        r"Hasil Akhir Step 1 .*micro-F1 ([0-9.]+)",
    ]
    out = []
    for p in sorted(glob.glob(f"{ROOT}/**/*.ipynb", recursive=True)):
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        texts = []
        for c in data.get("cells", []):
            for o in c.get("outputs", []):
                if o.get("output_type") == "stream":
                    texts.append("".join(o.get("text", [])))
                elif o.get("output_type") == "execute_result":
                    texts.append("".join((o.get("data") or {}).get("text/plain", [])))
        blob = "\n".join(texts)
        found = {}
        for pat in patterns:
            hits = re.findall(pat, blob)
            if hits:
                found[pat] = hits[:8]
        if found:
            out.append({"notebook": os.path.relpath(p, ROOT), "metrics": found})
    return out


def main():
    result = {
        "apps_quad": audit_quad_files(),
        "funnel": audit_funnel(),
        "split_snapshot": audit_split_snapshot(),
        "stage_build": audit_stage_build(),
        "emotion": audit_emotion(),
        "tokenized": audit_tokenized(),
        "cross_validation": audit_cv(),
        "inventory": audit_inventory(),
        "notebook_metrics": audit_notebook_metrics(),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    print(f"ditulis: {os.path.relpath(OUT, ROOT)}")
    for key in ("inventory", "funnel", "apps_quad", "emotion", "cross_validation"):
        print(f"\n[{key}]")
        print(json.dumps(result[key], indent=1, ensure_ascii=False)[:1200])


if __name__ == "__main__":
    main()
