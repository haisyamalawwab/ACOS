#!/usr/bin/env python3
"""EDA 055: studi ablasi untuk draf artikel 053 (baseline determinisme) dan 054 (bridge).

Stdlib murni. Deterministik. Tidak menjalankan sel notebook, tidak mengunduh apa pun.

Ablasi A (untuk 053 — baseline majority-per-category):
  A1  Kebocoran teks: akurasi baseline pada baris uji yang teksnya muncul di train
      vs baris uji bersih.
  A2  Struktur slot: akurasi baseline dikelompokkan per tipe pasangan (E-E, E-I, I-E).
  A3  Menambah istilah aspek: baseline (kategori, istilah aspek) dengan fallback ke
      mayoritas kategori; dilaporkan terpisah untuk kuadrisplit yang memakai lookup.

Ablasi D (untuk 054 — struktur bridge pada gold test):
  D1  Kandidat oracle: span gold per klausa -> produk Kartesian; berapa kandidat,
      rasio terhadap gold, dan cakupan pasangan gold (diharapkan 100%).
  D2  Tabrakan label: pasangan (a,o) dengan >1 sentimen berbeda / >1 kategori
      berbeda -> batas atas recall struktural pipeline satu-label-per-pasangan.

Membaca : ACOS-IndoBERT/data/Apps-ACOS/appsid_quad_{train,dev,test}.tsv
Keluaran: reports/055_data/ablasi_053_baseline.csv, ablasi_054_bridge.csv (+ stdout)

Jalankan: python3 scripts/eda_055_ablasi_draf_artikel.py
"""
from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUAD = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS")
OUT = os.path.join(ROOT, "reports", "055_data")
os.makedirs(OUT, exist_ok=True)

SENT = {"0": "negative", "1": "neutral", "2": "positive"}


def load_rows(split: str) -> list[tuple[str, str, int, int, int, int]]:
    """Satu entri per quadruple gold: (kategori, sentimen, a_st, a_ed, o_st, o_ed)."""
    rows = []
    with open(os.path.join(QUAD, f"appsid_quad_{split}.tsv"), encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            for q in parts[1:]:
                f = q.split()
                if len(f) < 4:
                    continue
                a_st, a_ed = (int(x) for x in f[0].split(","))
                o_st, o_ed = (int(x) for x in f[3].split(","))
                rows.append((f[1], SENT.get(f[2], f[2]), a_st, a_ed, o_st, o_ed))
    return rows


def load_lines(split: str) -> list[tuple[str, list[tuple]]]:
    """(teks klausa, daftar quadruple) per baris."""
    out = []
    with open(os.path.join(QUAD, f"appsid_quad_{split}.tsv"), encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            quads = []
            for q in parts[1:]:
                f = q.split()
                if len(f) < 4:
                    continue
                a_st, a_ed = (int(x) for x in f[0].split(","))
                o_st, o_ed = (int(x) for x in f[3].split(","))
                quads.append((f[1], SENT.get(f[2], f[2]), a_st, a_ed, o_st, o_ed))
            out.append((parts[0], quads))
    return out


train_rows = load_rows("train")
test_rows = load_rows("test")

# ---------- fit baseline B2: mayoritas sentimen per kategori (train) ----------
maj: dict[str, str] = {}
for cat in sorted({r[0] for r in train_rows}):
    c = Counter(r[1] for r in train_rows if r[0] == cat)
    maj[cat] = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

# ---------- A3: mayoritas per (kategori, istilah aspek) train ----------
train_lines = load_lines("train")
test_lines = load_lines("test")

term_maj = {}
term_stats: Counter = Counter()
for text, quads in train_lines:
    toks = text.split()
    for cat, s, a_st, a_ed, _o_st, _o_ed in quads:
        if a_st >= 0:
            term = " ".join(toks[a_st:a_ed]).strip().lower()
            if term:
                term_stats[(cat, term, s)] += 1
for (cat, term, s), n in term_stats.items():
    key = (cat, term)
    if key not in term_maj or n > term_maj[key][1] or (n == term_maj[key][1] and s < term_maj[key][0]):
        term_maj[key] = (s, n)
term_lookup = {k: v[0] for k, v in term_maj.items()}

# ---------- status kebocoran teks uji ----------
train_texts = {t.strip().lower() for t, _q in train_lines}

# ---------- A1/A2/A3 ----------
groups = {"A1_bocor": [0, 0], "A1_bersih": [0, 0]}
strata = {"E-E": [0, 0], "E-I": [0, 0], "I-E": [0, 0]}
a3 = {"lookup": [0, 0], "fallback": [0, 0]}
for text, quads in test_lines:
    leaky = text.strip().lower() in train_texts
    toks = text.split()
    for cat, s, a_st, a_ed, o_st, o_ed in quads:
        pred = maj[cat]
        g = "A1_bocor" if leaky else "A1_bersih"
        groups[g][0] += pred == s
        groups[g][1] += 1
        st = ("I" if a_st < 0 else "E") + "-" + ("I" if o_st < 0 else "E")
        strata[st][0] += pred == s
        strata[st][1] += 1
        if a_st >= 0:
            term = " ".join(toks[a_st:a_ed]).strip().lower()
            key = (cat, term)
            if key in term_lookup:
                p3 = term_lookup[key]
                a3["lookup"][0] += p3 == s
                a3["lookup"][1] += 1
            else:
                a3["fallback"][0] += pred == s
                a3["fallback"][1] += 1
        else:
            a3["fallback"][0] += pred == s
            a3["fallback"][1] += 1

print("=== A1 (kebocoran teks) ===")
for k, (ok, n) in groups.items():
    print(f"  {k}: {ok}/{n} = {100.0 * ok / n:.2f}%")
print("=== A2 (tipe pasangan slot) ===")
for k, (ok, n) in strata.items():
    print(f"  {k}: {ok}/{n} = {100.0 * ok / n:.2f}%")
print("=== A3 (kategori + istilah aspek, fallback kategori) ===")
tot_ok = tot_n = 0
for k, (ok, n) in a3.items():
    print(f"  {k}: {ok}/{n} = {100.0 * ok / n:.2f}%")
    tot_ok += ok
    tot_n += n
print(f"  TOTAL A3: {tot_ok}/{tot_n} = {100.0 * tot_ok / tot_n:.2f}%")
b2 = sum(1 for cat, s, *_ in test_rows if maj[cat] == s)
print(f"  (pembanding B2 murni: {b2}/{len(test_rows)} = {100.0 * b2 / len(test_rows):.2f}%)")

with open(os.path.join(OUT, "ablasi_053_baseline.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["ablasi", "kelompok", "benar", "n", "akurasi_pct"])
    for k, (ok, n) in groups.items():
        w.writerow(["A1_kebocoran", k, ok, n, round(100.0 * ok / n, 2)])
    for k, (ok, n) in strata.items():
        w.writerow(["A2_slot", k, ok, n, round(100.0 * ok / n, 2)])
    for k, (ok, n) in a3.items():
        w.writerow(["A3_istilah", k, ok, n, round(100.0 * ok / n, 2)])
    w.writerow(["A3_istilah", "TOTAL", tot_ok, tot_n, round(100.0 * tot_ok / tot_n, 2)])
    w.writerow(["B2_pembanding", "test", b2, len(test_rows), round(100.0 * b2 / len(test_rows), 2)])

# ---------- D: struktur bridge pada gold test ----------
clauses = quads_total = pairs_unique = cart_total = 0
pairs_multi_sent = quads_on_multi_sent = pairs_multi_cat = quads_on_multi_cat = 0
covered = 0
for text, quads in test_lines:
    clauses += 1
    A = {(q[2], q[3]) for q in quads}
    O = {(q[4], q[5]) for q in quads}
    cart_total += len(A) * len(O)
    quads_total += len(quads)
    by_pair_s: dict[tuple, set] = defaultdict(set)
    by_pair_c: dict[tuple, set] = defaultdict(set)
    for cat, s, a_st, a_ed, o_st, o_ed in quads:
        by_pair_s[(a_st, a_ed, o_st, o_ed)].add(s)
        by_pair_c[(a_st, a_ed, o_st, o_ed)].add(cat)
        covered += (a_st, a_ed) in A and (o_st, o_ed) in O
    pairs_unique += len(by_pair_s)
    for p, ss in by_pair_s.items():
        if len(ss) > 1:
            pairs_multi_sent += 1
            quads_on_multi_sent += sum(1 for q in quads if (q[2], q[3], q[4], q[5]) == p)
    for p, cs in by_pair_c.items():
        if len(cs) > 1:
            pairs_multi_cat += 1
            quads_on_multi_cat += sum(1 for q in quads if (q[2], q[3], q[4], q[5]) == p)

print("=== D (bridge oracle pada gold test) ===")
print(f"  klausa={clauses}  kuadruplet gold={quads_total}  pasangan unik (a,o)={pairs_unique}")
print(f"  kandidat Kartesian oracle={cart_total}  rasio kandidat/gold={cart_total / quads_total:.2f}")
print(f"  cakupan pasangan gold oleh Kartesian: {covered}/{quads_total} = {100.0 * covered / quads_total:.2f}%")
print(f"  pasangan dengan >1 sentimen berbeda: {pairs_multi_sent} (menampung {quads_on_multi_sent} kuadruplet)")
print(f"  pasangan dengan >1 kategori berbeda: {pairs_multi_cat} (menampung {quads_on_multi_cat} kuadruplet)")
ceil_pair = pairs_unique
print(f"  batas atas recall (satu label per pasangan): {ceil_pair}/{quads_total} = {100.0 * ceil_pair / quads_total:.2f}%")

with open(os.path.join(OUT, "ablasi_054_bridge.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["ukuran", "nilai"])
    for k, v in [
        ("klausa_test", clauses), ("kuadruplet_gold_test", quads_total),
        ("pasangan_unik", pairs_unique), ("kandidat_kartesian_oracle", cart_total),
        ("rasio_kandidat_gold", round(cart_total / quads_total, 3)),
        ("cakupan_pasangan_gold_pct", round(100.0 * covered / quads_total, 2)),
        ("pasangan_multi_sentimen", pairs_multi_sent),
        ("kuadruplet_di_pasangan_multi_sentimen", quads_on_multi_sent),
        ("pasangan_multi_kategori", pairs_multi_cat),
        ("kuadruplet_di_pasangan_multi_kategori", quads_on_multi_cat),
        ("batas_atas_recall_satu_label_pct", round(100.0 * ceil_pair / quads_total, 2)),
    ]:
        w.writerow([k, v])
print("tulis: reports/055_data/ablasi_053_baseline.csv, ablasi_054_bridge.csv")
