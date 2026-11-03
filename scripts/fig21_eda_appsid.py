#!/usr/bin/env python3
"""Gambar 21 — EDA data sumber Apps-ACOS (4 panel).

Membaca ACOS-IndoBERT/data/Apps-ACOS/processed/reviews_clean.csv
dan reviews_labeled.csv. Keluaran: reports/fig21_eda_sumber_appsid.png / .svg

Jalankan: python3 scripts/fig21_eda_appsid.py
"""
from __future__ import annotations

import collections
import csv
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

csv.field_size_limit(2 ** 31 - 1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS", "processed")
BASE = os.path.join(ROOT, "reports", "fig21_eda_sumber_appsid")

INK, MUTED = "#1a202c", "#4a5568"
BLUE, RED, GREEN, AMBER = "#2b6cb0", "#c53030", "#2f855a", "#b7791f"
GRID = "#e2e8f0"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.edgecolor": "#cbd5e0", "svg.fonttype": "none"})

ratings = collections.Counter()
years = collections.Counter()
apps = collections.Counter()
n_words = []
pol = collections.Counter()

with open(os.path.join(SRC, "reviews_clean.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        ratings[r["rating"]] += 1
        years[r["review_year"]] += 1
        apps[r["app_slug"]] += 1
        pol[r["polarity_rating"]] += 1
        try:
            n_words.append(int(r["n_words"]))
        except ValueError:
            pass

total = sum(ratings.values())
fig = plt.figure(figsize=(16, 9))
gs = fig.add_gridspec(2, 2, left=0.065, right=0.975, top=0.815, bottom=0.10,
                      hspace=0.55, wspace=0.20)

fig.text(0.5, 0.945, "Gambar 21.  EDA Data Sumber Apps-ACOS (43.673 ulasan, 13 aplikasi)",
         ha="center", va="center", fontsize=17.5, fontweight="bold", color=INK)
fig.text(0.5, 0.916, "Distribusi rating, panjang ulasan, volume per tahun, dan sebaran per aplikasi",
         ha="center", va="center", fontsize=9.2, color=MUTED)


def rapikan(ax, judul, sub=""):
    ax.text(0, 1.15, judul, transform=ax.transAxes, fontsize=11.2, fontweight="bold",
            color=INK, va="bottom", ha="left")
    if sub:
        ax.text(0, 1.045, sub, transform=ax.transAxes, fontsize=8.2, color=MUTED,
                va="bottom", ha="left")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- (a) rating
ax = fig.add_subplot(gs[0, 0])
ks = ["1", "2", "3", "4", "5"]
vs = [ratings[k] for k in ks]
colors = [RED if k in "12" else (AMBER if k == "3" else GREEN) for k in ks]
bars = ax.bar(ks, vs, color=colors, width=0.62)
for b, v in zip(bars, vs):
    ax.text(b.get_x() + b.get_width() / 2, v + 150, f"{v:,}".replace(",", "."),
            ha="center", va="bottom", fontsize=8.6, fontweight="bold", color=INK)
    ax.text(b.get_x() + b.get_width() / 2, v / 2, f"{100*v/total:.1f}%".replace(".", ","),
            ha="center", va="center", fontsize=8.0, color="white", fontweight="bold")
rapikan(ax, "Distribusi rating bintang",
        f"43% ulasan bernada negatif (1–2 bintang: {(ratings['1']+ratings['2']):,})"
        .replace(",", "."))
ax.set_ylim(0, max(vs) * 1.18)
ax.set_xlabel("rating", fontsize=8.6, color=MUTED)
ax.set_ylabel("jumlah ulasan", fontsize=8.6, color=MUTED)

# ---------------------------------------------------------------- (b) panjang
ax = fig.add_subplot(gs[0, 1])
bins = [0, 5, 10, 15, 20, 30, 40, 60, 80, 120, 310]
counts = [0] * (len(bins) - 1)
for w in n_words:
    for i in range(len(bins) - 1):
        if bins[i] <= w < bins[i + 1] or (i == len(bins) - 2 and w >= bins[-1]):
            counts[i] += 1
            break
labels = [f"{bins[i]}–{bins[i+1]-1}" if i < len(bins) - 2 else f"≥{bins[-2]}"
          for i in range(len(bins) - 1)]
bars = ax.bar(range(len(counts)), counts, color=BLUE, width=0.68)
for i, (b, v) in enumerate(zip(bars, counts)):
    ax.text(b.get_x() + b.get_width() / 2, v * 1.06, f"{100*v/total:.1f}".replace(".", ","),
            ha="center", va="bottom", fontsize=7.4, color=MUTED, rotation=90)
rapikan(ax, "Panjang ulasan (kata)",
        f"median {int(statistics.median(n_words))} kata · p95 59 kata · maksimum {max(n_words)} kata")
ax.set_xticks(range(len(counts)))
ax.set_xticklabels(labels, fontsize=7.6, rotation=30, ha="right")
ax.set_xlabel("jumlah kata per ulasan", fontsize=8.6, color=MUTED)
ax.set_ylabel("jumlah ulasan", fontsize=8.6, color=MUTED)
ax.set_ylim(0, max(counts) * 1.22)

# ---------------------------------------------------------------- (c) tahun
ax = fig.add_subplot(gs[1, 0])
ys = sorted(years)
vs = [years[y] for y in ys]
ax.bar(ys, vs, color=[BLUE if y < "2026" else AMBER for y in ys], width=0.66)
for y, v in zip(ys, vs):
    if v >= 1500:
        ax.text(y, v + 350, f"{v:,}".replace(",", "."), ha="center", va="bottom",
                fontsize=7.6, color=MUTED, rotation=90)
rapikan(ax, "Volume ulasan per tahun",
        "61,9% ulasan berasal dari 2026 — risiko drift temporal, bukan sampel historis merata")
ax.set_ylim(0, max(vs) * 1.20)
ax.set_xlabel("tahun", fontsize=8.6, color=MUTED)
ax.set_ylabel("jumlah ulasan", fontsize=8.6, color=MUTED)

# ---------------------------------------------------------------- (d) aplikasi
ax = fig.add_subplot(gs[1, 1])
items = apps.most_common()
names = [k.replace("_", " ") for k, _ in items][::-1]
vals = [v for _, v in items][::-1]
ax.barh(names, vals, color=GREEN, height=0.66)
for i, v in enumerate(vals):
    ax.text(v + 40, i, f"{v:,}".replace(",", "."), va="center", fontsize=7.8, color=MUTED)
rapikan(ax, "Sebaran ulasan per aplikasi (13 bank digital)",
        "rentang 2.514–4.202 ulasan per aplikasi; sebaran relatif merata")
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.grid(axis="y", visible=False)
ax.set_xlim(0, max(vals) * 1.14)
ax.tick_params(axis="y", labelsize=8.0)
ax.set_xlabel("jumlah ulasan", fontsize=8.6, color=MUTED)

fig.text(0.5, 0.022,
         "Sumber: ACOS-IndoBERT/data/Apps-ACOS/processed/reviews_clean.csv (43.673 baris)  ·  "
         "dihitung oleh scripts/eda_044_appsid.py, digambar oleh scripts/fig21_eda_appsid.py",
         ha="center", va="center", fontsize=7.4, color=MUTED)

fig.savefig(BASE + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(BASE + ".svg", bbox_inches="tight", facecolor="white")
print("ditulis:", BASE + ".png")
print("ditulis:", BASE + ".svg")
