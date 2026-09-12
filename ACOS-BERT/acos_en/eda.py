"""EDA torch-free untuk data quad Inggris (rest16/laptop).

Membaca `*_quad_train/dev/test.tsv` sumber (`data/...`) — format
`teks<TAB>asp_span cat senti opi_span[TAB>...]` — dan menghasilkan ringkasan
per split: kalimat, tuple, eksplisit/implisit, sebaran sentimen/kategori.
`plot()` memakai matplotlib bila ada; tanpa itu tetap mengembalikan dict.
"""
from __future__ import annotations

import csv
import os
from collections import Counter

from .datafiles import QUAD_PREFIX, QUAD_SOURCE, SPLITS


def _iter_quads(path: str):
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if not row or not row[0].strip():
                continue
            yield row[0], row[1:]


def summarize_quad_file(path: str) -> dict:
    """Statistik satu berkas quad sumber."""
    n_baris, n_tuple = 0, 0
    asp_imp = opi_imp = 0
    senti, cats = Counter(), Counter()
    for _teks, quads in _iter_quads(path):
        n_baris += 1
        for q in quads:
            ele = q.split(" ")
            if len(ele) < 4:
                continue
            n_tuple += 1
            if ele[0] == "-1,-1":
                asp_imp += 1
            if ele[3] == "-1,-1":
                opi_imp += 1
            cats[ele[1]] += 1
            senti[ele[2]] += 1
    return {"baris": n_baris, "tuple": n_tuple,
            "aspek_implisit": asp_imp, "opini_implisit": opi_imp,
            "sentimen": dict(senti),
            "n_kategori_teramati": len(cats),
            "kategori_top5": cats.most_common(5)}


def summarize_domain(acos_root: str, domain: str) -> dict:
    """Ringkasan train/dev/test satu domain + total."""
    out = {}
    for split in SPLITS:
        p = os.path.join(acos_root, QUAD_SOURCE[domain],
                         f"{QUAD_PREFIX[domain]}{split}.tsv")
        out[split] = summarize_quad_file(p)
    tot = sum(v["tuple"] for v in out.values())
    out["total_tuple"] = tot
    return out


def plot(summary: dict, domain: str, out_dir: str) -> dict:
    """4 plot EDA (membutuhkan matplotlib; dilewati bila tak ada)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {"ok": False, "sebab": "matplotlib tidak tersedia"}
    os.makedirs(out_dir, exist_ok=True)
    hasil = {}
    # 1. tuple per split
    fig, ax = plt.subplots(figsize=(6, 3.2))
    xs = list(SPLITS)
    ax.bar(xs, [summary[s]["tuple"] for s in xs], color="#93C5FD", edgecolor="black")
    ax.set_title(f"{domain}: tuple per split")
    p = os.path.join(out_dir, "01_tuple_per_split.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    hasil["tuple_per_split"] = p
    # 2. sentimen train
    fig, ax = plt.subplots(figsize=(6, 3.2))
    s = summary["train"]["sentimen"]
    ax.bar(list(s), [s.get(k, 0) for k in s], color="#6EE7B7", edgecolor="black")
    ax.set_title(f"{domain} train: sebaran sentimen (0/1/2)")
    p = os.path.join(out_dir, "02_sentimen_train.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    hasil["sentimen_train"] = p
    return {"ok": True, **hasil}
