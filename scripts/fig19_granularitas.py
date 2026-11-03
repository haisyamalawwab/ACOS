#!/usr/bin/env python3
"""Gambar 19 — Diagram alir komparatif granularitas input ACOS.

Kiri  : Review-Level Processing  -> span truncation loss (cakupan aspek 61,5%, opini 48,0%)
Kanan : Clause-Level Segmentation -> retokenisasi WordPiece per klausa (0 [UNK], cakupan 100%)

Menghasilkan:
  reports/fig19_granularitas_input_ulasan_vs_klausa.png  (300 dpi)
  reports/fig19_granularitas_input_ulasan_vs_klausa.svg  (vektor)

Jalankan: python3 scripts/fig19_granularitas.py
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PNG = os.path.join(ROOT, "reports", "fig19_granularitas_input_ulasan_vs_klausa.png")
OUT_SVG = os.path.join(ROOT, "reports", "fig19_granularitas_input_ulasan_vs_klausa.svg")

INK = "#1a202c"
MUTED = "#4a5568"
RED = "#c53030"
RED_L = "#fff5f5"
GREEN = "#2f855a"
GREEN_L = "#f0fff4"
BLUE = "#2b6cb0"
GRAY = "#a0aec0"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.linewidth": 0, "svg.fonttype": "none"})


def box(ax, x, y, w, h, title, sub="", ec=BLUE, fc="white", tsize=9.6, ssize=7.6,
        lw=1.5, z=3, ls="-", sub_family="DejaVu Sans", sub_color=MUTED, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.30,rounding_size=1.1",
                                linewidth=lw, edgecolor=ec, facecolor=fc, zorder=z,
                                linestyle=ls, alpha=alpha))
    if sub:
        ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=ec, zorder=z + 1)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                fontsize=ssize, color=sub_color, zorder=z + 1,
                family=sub_family, linespacing=1.4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=ec, zorder=z + 1)


def arrow(ax, p1, p2, color=BLUE, lw=1.7, rad=0.0, ms=11, z=2, ls="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms,
                                 linewidth=lw, color=color, shrinkA=1, shrinkB=1,
                                 zorder=z, connectionstyle=f"arc3,rad={rad}", linestyle=ls))


def panel(ax, x, y, w, h, title, color, tint):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.4,rounding_size=1.6",
                                linewidth=1.2, edgecolor=color, facecolor=tint,
                                zorder=0, linestyle=(0, (6, 4))))
    ax.text(x + 2.0, y + h - 2.2, title, ha="left", va="center",
            fontsize=10.4, fontweight="bold", color=color, zorder=1)


fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 160)
ax.set_ylim(0, 90)
ax.axis("off")
fig.patch.set_facecolor("white")

# ------------------------------------------------------------------ judul
ax.text(80, 86.4, "Gambar 2.  Granularitas Input: Ulasan Utuh vs Segmentasi Klausa",
        ha="center", va="center", fontsize=18.5, fontweight="bold", color=INK)
ax.text(80, 83.0, "Dampak cara memotong input terhadap ketercakupan span dan token tak dikenal",
        ha="center", va="center", fontsize=9.0, color=MUTED)

# ------------------------------------------------------------------ sumber
box(ax, 26, 71.0, 108, 9.0, "Sumber yang sama: satu ulasan utuh",
    "“Aplikasi ini sangat membantu transfer antarbank, biayanya murah, tetapi antarmuka sering "
    "error saat login dan notifikasi transfer kadang terlambat.”",
    ec="#4a5568", fc="#f7fafc", tsize=9.4, ssize=7.2)

arrow(ax, (58, 71.0), (39.5, 66.4), RED, lw=2.0, rad=0.12, ms=13)
arrow(ax, (102, 71.0), (120.5, 66.4), GREEN, lw=2.0, rad=-0.12, ms=13)

# ------------------------------------------------------------------ panel
panel(ax, 2, 4, 75, 62, "A · REVIEW-LEVEL (baseline)", RED, RED_L)
panel(ax, 83, 4, 75, 62, "B · CLAUSE-LEVEL (diusulkan)", GREEN, GREEN_L)

arrow(ax, (39.5, 65.2), (39.5, 60.9), RED, lw=1.7, ms=10)
arrow(ax, (120.5, 65.2), (120.5, 60.9), GREEN, lw=1.7, ms=10)

# ================================================== KIRI
# tahap 1
box(ax, 6, 51.0, 67, 9.5, "Input: 1 ulasan utuh → 1 baris",
    "±40 kata · seluruh konteks dikirim sekaligus", ec=RED, tsize=9.2, ssize=7.2)
arrow(ax, (39.5, 51.0), (39.5, 48.4), RED)

# tahap 2
ax.add_patch(FancyBboxPatch((6, 36.0), 67, 12.4,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.5, edgecolor=RED, facecolor="white", zorder=3))
ax.text(39.5, 46.6, "WordPiece tokenizer · max_seq_length = 128", ha="center", va="center",
        fontsize=8.6, fontweight="bold", color=RED, zorder=4)

tx, ty, tw, th, n = 9.0, 40.4, 2.35, 3.0, 24
for i in range(n):
    cut = i >= 18
    ax.add_patch(Rectangle((tx + i * tw, ty), tw - 0.35, th,
                           facecolor=("#fed7d7" if cut else "#bee3f8"),
                           edgecolor=(RED if cut else BLUE), linewidth=0.6,
                           linestyle=("--" if cut else "-"), zorder=4))
ax.plot([tx + 18 * tw - 0.18, tx + 18 * tw - 0.18], [ty - 0.4, ty + th + 0.4],
        color=RED, linewidth=1.5, linestyle=(0, (3, 2)), zorder=5)
ax.text(tx + 18 * tw - 0.18, ty + th + 1.0, "batas 128 token", ha="center", va="center",
        fontsize=6.2, color=RED, fontweight="bold", zorder=5)
ax.text(tx + 21 * tw, ty - 1.2, "sisa ulasan hilang", ha="center", va="center",
        fontsize=6.8, color=RED, zorder=5)
ax.text(39.5, 37.6, "0 … 127 token  ·  token setelah batas tidak pernah di-encode",
        ha="center", va="center", fontsize=6.8, color=MUTED, zorder=5)

arrow(ax, (39.5, 36.0), (39.5, 33.4), RED)

# tahap 3
box(ax, 6, 21.0, 67, 12.0, "Span truncation loss",
    "tuple kuadrupel di ekor ulasan kehilangan span aspek/opini\n"
    "→ prediksi tidak dapat dibandingkan dengan gold",
    ec=RED, fc="white", tsize=9.6, ssize=7.4)
arrow(ax, (39.5, 21.0), (39.5, 18.4), RED)

# tahap 4 — bar
ax.add_patch(FancyBboxPatch((6, 4.8), 67, 13.2,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.5, edgecolor=RED, facecolor="white", zorder=3))
ax.text(12.0, 15.9, "Ketercakupan span", ha="left", va="center",
        fontsize=8.6, fontweight="bold", color=RED, zorder=4)

for label, val, y in (("Aspek", 0.615, 11.2), ("Opini", 0.480, 7.2)):
    ax.text(8.5, y + 0.7, label, ha="left", va="center", fontsize=7.6, color=INK, zorder=4)
    ax.add_patch(Rectangle((24.0, y), 46.0, 1.9, facecolor="#edf2f7",
                           edgecolor="none", zorder=4))
    ax.add_patch(Rectangle((24.0, y), 46.0 * val, 1.9, facecolor=RED,
                           edgecolor="none", alpha=0.85, zorder=5))
    ax.text(24.0 + 46.0 * val + 1.2, y + 0.95, f"{val*100:.1f}%".replace(".", ","),
            ha="left", va="center", fontsize=8.2, fontweight="bold", color=RED, zorder=5)

# ================================================== KANAN
# tahap 1 — klausa
ax.add_patch(FancyBboxPatch((87, 47.6), 67, 12.9,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.5, edgecolor=GREEN, facecolor="white", zorder=3))
ax.text(120.5, 58.4, "Input: dekomposisi menjadi klausa independen", ha="center", va="center",
        fontsize=8.8, fontweight="bold", color=GREEN, zorder=4)
clauses = [
    "aplikasi ini sangat membantu transfer antarbank",
    "biayanya murah",
    "antarmuka sering error saat login",
    "notifikasi transfer kadang terlambat",
]
for i, cl in enumerate(clauses):
    y = 55.0 - i * 2.35
    ax.add_patch(FancyBboxPatch((90, y), 61, 1.9,
                                boxstyle="round,pad=0.10,rounding_size=0.6",
                                linewidth=0.8, edgecolor=GREEN, facecolor=GREEN_L, zorder=4))
    ax.text(91.4, y + 0.95, f"k{i+1}", ha="left", va="center", fontsize=6.4,
            color=GREEN, fontweight="bold", zorder=5)
    ax.text(95.0, y + 0.95, f"“{cl}”", ha="left", va="center", fontsize=6.6,
            color=INK, zorder=5, style="italic")

arrow(ax, (120.5, 47.6), (120.5, 45.4), GREEN)

# tahap 2 — retokenisasi per klausa
ax.add_patch(FancyBboxPatch((87, 33.0), 67, 12.0,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.5, edgecolor=GREEN, facecolor="white", zorder=3))
ax.text(120.5, 42.8, "Retokenisasi WordPiece per klausa (≤ 128 token)", ha="center", va="center",
        fontsize=8.6, fontweight="bold", color=GREEN, zorder=4)
for j, cells in enumerate((9, 5, 6, 5)):
    y = 39.4 - j * 2.05
    ax.text(91.0, y + 0.75, f"k{j+1}", ha="left", va="center", fontsize=6.2,
            color=GREEN, fontweight="bold", zorder=5)
    for i in range(cells):
        ax.add_patch(Rectangle((96.0 + i * 2.1, y), 1.75, 1.5,
                               facecolor="#c6f6d5", edgecolor=GREEN, linewidth=0.5, zorder=5))
    ax.text(97.5 + cells * 2.1, y + 0.75, "…", ha="left", va="center",
            fontsize=7.0, color=MUTED, zorder=5)

arrow(ax, (120.5, 33.0), (120.5, 30.4), GREEN)

# tahap 3
box(ax, 87, 21.0, 67, 9.0, "Tidak ada pemotongan",
    "setiap span tetap berada di dalam jendela model",
    ec=GREEN, fc="white", tsize=9.6, ssize=7.4)
arrow(ax, (120.5, 21.0), (120.5, 18.4), GREEN)

# tahap 4 — hasil
ax.add_patch(FancyBboxPatch((87, 4.8), 67, 13.2,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.5, edgecolor=GREEN, facecolor="white", zorder=3))
ax.text(92.0, 14.6, "100%", ha="left", va="center", fontsize=21, fontweight="bold",
        color=GREEN, zorder=4)
ax.text(114.0, 15.4, "ketercakupan span", ha="left", va="center", fontsize=7.8,
        color=INK, zorder=4)
ax.text(114.0, 13.6, "aspek & opini, seluruh tuple", ha="left", va="center", fontsize=7.0,
        color=MUTED, zorder=4)
ax.add_patch(FancyBboxPatch((91.0, 6.4), 58.0, 4.4,
                            boxstyle="round,pad=0.20,rounding_size=0.9",
                            linewidth=1.0, edgecolor=GREEN, facecolor=GREEN_L, zorder=4))
ax.text(120.0, 8.6, "0 token [UNK]", ha="center", va="center", fontsize=9.2,
        fontweight="bold", color=GREEN, zorder=5)

# ------------------------------------------------------------------ pemisah
ax.plot([80, 80], [8, 64], color=GRAY, linewidth=1.0, linestyle=(0, (4, 4)), zorder=1)
ax.add_patch(plt.Circle((80, 34), 3.0, facecolor="white", edgecolor=GRAY, linewidth=1.0, zorder=6))
ax.text(80, 34, "vs", ha="center", va="center", fontsize=9.4, color=MUTED,
        fontweight="bold", zorder=7)

# ------------------------------------------------------------------ catatan
ax.text(80, 1.9,
        "Sumber: 023 §2.2 (pengukuran) & 035 §III-C — ulasan utuh 61,5% aspek / 48,0% opini, klausa 100%; "
        "0 [UNK] dari _build_report_appsid.json  ·  gambar skematik",
        ha="center", va="center", fontsize=7.2, color=MUTED)

fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_SVG, bbox_inches="tight", facecolor="white")
print("ditulis:", OUT_PNG)
print("ditulis:", OUT_SVG)
