#!/usr/bin/env python3
"""EDA 053/054: baseline majority-per-category dan implisit per kategori (gold TSV).

Stdlib murni. Deterministik. Tidak menjalankan sel notebook, tidak mengunduh apa pun.

Pertanyaan (menjawab temuan #5 review reports/049):
  Seberapa jauh sentimen dapat diprediksi dari kategori saja, tanpa membaca teks?

Metode:
  1. Fit pada train: sentimen mayoritas per kategori (tie-break: urutan leksikografis
     nama kelas, agar deterministik).
  2. Evaluasi pada test (dan dev, sebagai pemeriksaan): akurasi tuple-level.
  3. Pembanding: mayoritas global (satu kelas untuk semua).
  4. Tambahan untuk 054: rasio opini implisit dan aspek implisit per kategori (gold,
     gabungan train+dev+test).

Membaca : ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_{train,dev,test}.tsv
Keluaran: reports/053_data/majority_baseline.csv (stdin: tabel ringkas)

Jalankan: python3 scripts/eda_053_majority_baseline_implisit.py
"""
from __future__ import annotations

import csv
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUAD = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS")
OUT = os.path.join(ROOT, "reports", "053_data")
os.makedirs(OUT, exist_ok=True)

SENT = {"0": "negative", "1": "neutral", "2": "positive"}


def load(split: str) -> list[tuple[str, str, bool, bool]]:
    """Satu entri per quadruple gold: (kategori, sentimen, aspek_implisit, opini_implisit)."""
    rows: list[tuple[str, str, bool, bool]] = []
    path = os.path.join(QUAD, f"appsid_quad_{split}.tsv")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            for q in parts[1:]:
                f = q.split()
                if len(f) < 4:
                    continue
                a_st, _ = (int(x) for x in f[0].split(","))
                cat, s = f[1], SENT.get(f[2], f[2])
                o_st, _ = (int(x) for x in f[3].split(","))
                rows.append((cat, s, a_st < 0, o_st < 0))
    return rows


data = {sp: load(sp) for sp in ("train", "dev", "test")}

# 1. Fit mayoritas per kategori pada TRAIN
maj: dict[str, str] = {}
share_train: dict[str, float] = {}
for cat in sorted({r[0] for r in data["train"]}):
    c = Counter(r[1] for r in data["train"] if r[0] == cat)
    top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    maj[cat] = top[0]
    share_train[cat] = 100.0 * top[1] / sum(c.values())

# 2. Mayoritas global pada TRAIN
g = Counter(r[1] for r in data["train"])
g_top = sorted(g.items(), key=lambda kv: (-kv[1], kv[0]))[0]
glob_class, glob_share = g_top[0], 100.0 * g_top[1] / sum(g.values())


def acc(rows: list[tuple[str, str, bool, bool]], mapper) -> tuple[int, int, float]:
    ok = sum(1 for r in rows if mapper(r) == r[1])
    n = len(rows)
    return ok, n, (100.0 * ok / n if n else 0.0)


rows_out = []
print(f"{'kategori':<22} {'n_test':>6} {'benar':>6} {'akurasi%':>9} "
      f"{'maj_train':>10} {'share_maj_train%':>16} {'impl_opini%':>11}")
for cat in sorted(maj):
    sub = [r for r in data["test"] if r[0] == cat]
    ok, n, a = acc(sub, lambda r: maj[cat])
    pooled = [r for sp in ("train", "dev", "test") for r in data[sp] if r[0] == cat]
    imp_o = 100.0 * sum(1 for r in pooled if r[3]) / len(pooled)
    rows_out.append([cat, n, ok, round(a, 2), maj[cat],
                     round(share_train[cat], 2), round(imp_o, 2)])
    print(f"{cat:<22} {n:>6} {ok:>6} {a:>9.2f} {maj[cat]:>10} "
          f"{share_train[cat]:>16.2f} {imp_o:>11.2f}")

for sp in ("dev", "test"):
    ok, n, a = acc(data[sp], lambda r: maj[r[0]])
    okg, _, ag = acc(data[sp], lambda r: glob_class)
    print(f"[{sp}] majority-per-category: {ok}/{n} = {a:.2f}%  |  "
          f"mayoritas global ({glob_class}): {okg}/{n} = {ag:.2f}%")

okt, nt, at = acc(data["test"], lambda r: maj[r[0]])
row_tot = ["TOTAL", nt, okt, round(at, 2), glob_class, round(glob_share, 2), ""]
rows_out.append(row_tot)
print(f"[train] mayoritas global = {glob_class} ({glob_share:.2f}%); "
      f"gold gabungan = {sum(len(v) for v in data.values())} quadruple")

with open(os.path.join(OUT, "majority_baseline.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["kategori", "n_test", "benar_test", "akurasi_test_pct",
                "mayoritas_train", "share_mayoritas_train_pct", "opini_implisit_pct"])
    w.writerows(rows_out)
print("tulis: reports/053_data/majority_baseline.csv")

# 5. (untuk laporan 054) kontingensi 2x2 slot implisit gold + implisit per kategori
cont: Counter = Counter()
ai: Counter = Counter()
ao: Counter = Counter()
ncat: Counter = Counter()
for sp in ("train", "dev", "test"):
    for cat, _s, a_im, o_im in data[sp]:
        cont[("I" if a_im else "E") + "-" + ("I" if o_im else "E")] += 1
        ncat[cat] += 1
        if a_im:
            ai[cat] += 1
        if o_im:
            ao[cat] += 1
tot = sum(ncat.values())
print("kontingensi 2x2 gold (aspek x opini):")
for k in ("E-E", "E-I", "I-E", "I-I"):
    print(f"  {k}: {cont[k]} ({100.0 * cont[k] / tot:.2f}%)")
with open(os.path.join(OUT, "implisit_2x2_kategori.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["kategori", "n", "aspek_implisit_pct", "opini_implisit_pct"])
    for cat in sorted(ncat, key=lambda x: -ncat[x]):
        w.writerow([cat, ncat[cat], round(100.0 * ai[cat] / ncat[cat], 2),
                    round(100.0 * ao[cat] / ncat[cat], 2)])
    w.writerow(["TOTAL", tot, round(100.0 * sum(ai.values()) / tot, 2),
                round(100.0 * sum(ao.values()) / tot, 2)])
    w.writerow(["E-E", cont["E-E"], round(100.0 * cont["E-E"] / tot, 2), ""])
    w.writerow(["E-I", cont["E-I"], round(100.0 * cont["E-I"] / tot, 2), ""])
    w.writerow(["I-E", cont["I-E"], round(100.0 * cont["I-E"] / tot, 2), ""])
    w.writerow(["I-I", cont["I-I"], round(100.0 * cont["I-I"] / tot, 2), ""])
print("tulis: reports/053_data/implisit_2x2_kategori.csv")
