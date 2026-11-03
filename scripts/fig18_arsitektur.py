#!/usr/bin/env python3
"""Gambar 18 — Diagram arsitektur dua tahap ACOS-IndoBERT.

Menghasilkan:
  reports/fig18_arsitektur_dua_tahap_acos_indobert.png  (300 dpi)
  reports/fig18_arsitektur_dua_tahap_acos_indobert.svg  (vektor, untuk penyuntingan)

Jalankan: python3 scripts/fig18_arsitektur.py
Dependensi: matplotlib.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PNG = os.path.join(ROOT, "reports", "fig18_arsitektur_dua_tahap_acos_indobert.png")
OUT_SVG = os.path.join(ROOT, "reports", "fig18_arsitektur_dua_tahap_acos_indobert.svg")

# ---------------------------------------------------------------- palet
INK = "#1a202c"
MUTED = "#4a5568"
C1 = "#2b6cb0"   # Tahap 1
C1_L = "#ebf4ff"
C2 = "#b7791f"   # Bridge
C2_L = "#fdf6e3"
C3 = "#2f855a"   # Tahap 2
C3_L = "#eaf7ef"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0,
    "svg.fonttype": "none",
})


def box(ax, x, y, w, h, title, sub="", ec=C1, fc="white", tsize=10.0, ssize=8.0,
        tcolor=None, lw=1.6, z=3, sub_color=MUTED, sub_linespace=1.4):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.30,rounding_size=1.1",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=z,
    ))
    tc = tcolor or ec
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=tc, zorder=z + 1)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                fontsize=ssize, color=sub_color, zorder=z + 1,
                linespacing=sub_linespace)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=tc, zorder=z + 1)


def arrow(ax, p1, p2, color=C1, lw=1.7, rad=0.0, z=2, ms=11, ls="-"):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=ms, linewidth=lw,
        color=color, shrinkA=1, shrinkB=1, zorder=z,
        connectionstyle=f"arc3,rad={rad}", linestyle=ls,
    ))


def panel(ax, x, y, w, h, title, color, tint):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.4,rounding_size=1.6",
        linewidth=1.2, edgecolor=color, facecolor=tint, zorder=0,
        linestyle=(0, (6, 4)),
    ))
    ax.text(x + 1.8, y + h - 1.9, title, ha="left", va="center",
            fontsize=10.5, fontweight="bold", color=color, zorder=1)


fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 160)
ax.set_ylim(0, 90)
ax.axis("off")
fig.patch.set_facecolor("white")

# ---------------------------------------------------------------- judul
ax.text(80, 86.6, "Gambar 1.  Arsitektur Dua Tahap ACOS-IndoBERT",
        ha="center", va="center", fontsize=19, fontweight="bold", color=INK)
ax.text(80, 83.0,
        "Pipeline Extract–Classify yang diadaptasi ke IndoBERT  ·  satu baris masukan = satu klausa",
        ha="center", va="center", fontsize=9.2, color=MUTED)

# ---------------------------------------------------------------- panel
panel(ax, 2.0, 6.0, 59.0, 73.5, "TAHAP 1 · Ekstraksi Span", C1, C1_L)
panel(ax, 63.5, 6.0, 30.0, 73.5, "BRIDGE", C2, C2_L)
panel(ax, 96.0, 6.0, 62.0, 73.5, "TAHAP 2 · Klasifikasi Quadruple", C3, C3_L)

# ================================================== TAHAP 1
box(ax, 8.0, 66.0, 47.0, 8.2, "Klausa masukan",
    "“pelayanan cepat tapi aplikasi sering error”", ec=C1, tsize=10.0, ssize=8.4)
arrow(ax, (31.5, 66.0), (31.5, 62.6), C1)

box(ax, 8.0, 53.6, 47.0, 8.8, "IndoBERT  ·  indobert-base-p1",
    "12 layer · 768 hidden · 12 head · vocab 50.000", ec=C1, fc=C1_L, tsize=10.6)

arrow(ax, (24.0, 53.6), (18.5, 51.2), C1)
arrow(ax, (39.0, 53.6), (45.5, 51.2), C1)

box(ax, 5.5, 42.6, 26.0, 8.2, "6-label BIO-CRF",
    "B/I-A · B/I-O · penanda implisit", ec=C1, tsize=9.8, ssize=7.6)

box(ax, 34.5, 45.6, 25.0, 5.0, "Head IA · biner", ec=C1, tsize=8.8)
box(ax, 34.5, 39.6, 25.0, 5.0, "Head IO · biner", ec=C1, tsize=8.8)
arrow(ax, (18.5, 42.6), (18.5, 39.2), C1)
arrow(ax, (47.0, 39.6), (47.0, 38.4), C1)

box(ax, 5.5, 27.0, 54.0, 11.2,
    "Kandidat entitas",
    "Aspek  :  a₁ … aₙ  (eksplisit)   +   IA\nOpini  :  o₁ … oₘ  (eksplisit)   +   IO",
    ec=C1, fc=C1_L, tsize=9.8, ssize=8.2)

# contoh keluaran tahap 1
ax.add_patch(FancyBboxPatch((5.5, 11.0), 54.0, 12.6,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.2, edgecolor=C1, facecolor="white",
                            linestyle=(0, (3, 2)), zorder=3))
ax.text(32.5, 21.4, "Contoh keluaran Tahap 1", ha="center", va="center",
        fontsize=8.8, fontweight="bold", color=C1, zorder=4)
ax.text(8.0, 18.3, '“pelayanan”            → aspek eksplisit,  IA = 0', ha="left", va="center",
        fontsize=7.4, family="DejaVu Sans Mono", color=INK, zorder=4)
ax.text(8.0, 15.5, '“cepat”, “sering error” → opini eksplisit,  IO = 0', ha="left", va="center",
        fontsize=7.4, family="DejaVu Sans Mono", color=INK, zorder=4)
ax.text(8.0, 12.7, 'aspek implisit          → IA = 1', ha="left", va="center",
        fontsize=7.4, family="DejaVu Sans Mono", color=MUTED, zorder=4)

# ================================================== BRIDGE
ax.text(78.5, 69.0, "Candidate Pair Bridge", ha="center", va="center",
        fontsize=9.6, fontweight="bold", color=C2)

gx0, gy0, cw, ch = 68.6, 50.4, 7.0, 5.0
cols = ["o₁", "o₂", "IO"]
rows = ["a₁", "a₂", "IA"]
for j, c in enumerate(cols):
    ax.text(gx0 + j * cw + cw / 2, gy0 + 3 * ch + 1.6, c, ha="center", va="center",
            fontsize=8.6, color=MUTED, fontweight="bold")
for i, r in enumerate(rows):
    ax.text(gx0 - 1.6, gy0 + (2 - i) * ch + ch / 2, r, ha="center", va="center",
            fontsize=8.6, color=MUTED, fontweight="bold")
for i in range(3):
    for j in range(3):
        implicit = (i == 2 and j == 2)
        ax.add_patch(Rectangle((gx0 + j * cw, gy0 + (2 - i) * ch), cw, ch,
                               facecolor=C2 if implicit else "white",
                               edgecolor=C2, linewidth=1.1, zorder=3))
        if implicit:
            ax.text(gx0 + j * cw + cw / 2, gy0 + (2 - i) * ch + ch / 2, "−1,−1",
                    ha="center", va="center", fontsize=7.6, fontweight="bold",
                    color="white", zorder=4)

ax.text(78.5, 48.2, "setiap sel = satu pasangan kandidat", ha="center", va="center",
        fontsize=7.4, color=MUTED, style="italic")
ax.text(78.5, 44.8, "P = A × O = { (aᵢ , oⱼ) }", ha="center", va="center",
        fontsize=8.8, color=INK, family="DejaVu Sans Mono")
ax.text(78.5, 41.6, "termasuk pasangan implisit (−1, −1)", ha="center", va="center",
        fontsize=7.8, color=MUTED, style="italic")

box(ax, 65.5, 18.5, 26.0, 13.0, "Skala kandidat",
    "rest16: 10.735 untuk 895 gold\nappsid: 10.991 untuk 9.006",
    ec=C2, fc=C2_L, tsize=8.8, ssize=7.2)
ax.text(78.5, 16.7, "rasio menentukan presisi", ha="center", va="center",
        fontsize=7.2, color=MUTED, style="italic")

# panah bridge -> tahap 2 (masuk ke kotak masukan Tahap 2)
arrow(ax, (90.8, 67.4), (99.2, 70.4), C3, lw=2.0, ms=13, rad=-0.18)

# ================================================== TAHAP 2
box(ax, 99.5, 66.0, 55.0, 8.2, "Klausa + pasangan kandidat (aᵢ , oⱼ)",
    "pasangan yang sama dipakai untuk semua kategori", ec=C3, tsize=9.6, ssize=7.8)
arrow(ax, (127.0, 66.0), (127.0, 62.6), C3)

box(ax, 99.5, 53.6, 55.0, 8.8, "IndoBERT  ·  encoder tahap 2",
    "mean-pool span → h_pair ∈ ℝ¹⁵³⁶", ec=C3, fc=C3_L, tsize=10.2)
arrow(ax, (127.0, 53.6), (127.0, 50.4), C3)

box(ax, 99.5, 40.2, 55.0, 10.0, "Multi-Label Classifier Head · 39 dimensi",
    "13 kategori × 3 sentimen   ·   Linear(1536, 39) + BCEWithLogits",
    ec=C3, tsize=10.0, ssize=7.8)
arrow(ax, (127.0, 40.2), (127.0, 38.7), C3)

# strip 39 logit (13 kategori x 3 sentimen)
sx, sy, sw, sh = 101.2, 37.2, 4.35, 1.65
for c in range(13):
    for s in range(3):
        ax.add_patch(Rectangle((sx + c * sw, sy - s * sh), sw - 0.4, sh - 0.32,
                               facecolor=["#2f855a", "#68d391", "#c6f6d5"][s],
                               edgecolor="white", linewidth=0.6, zorder=3))
ax.text(127.0, 31.8, "39 logit  →  ambang > 0  →  satu sentimen per kategori aktif",
        ha="center", va="center", fontsize=7.6, color=MUTED)

# keluaran
ax.add_patch(FancyBboxPatch((99.5, 15.5), 55.0, 13.6,
                            boxstyle="round,pad=0.30,rounding_size=1.1",
                            linewidth=1.6, edgecolor=C3, facecolor=C3_L, zorder=3))
ax.text(127.0, 26.6, "Tuple kuadrupel akhir  (a , c , s , o)", ha="center", va="center",
        fontsize=9.6, fontweight="bold", color=C3, zorder=4)
ax.text(102.0, 23.2, '( "pelayanan" , SERVICE_GENERAL , positif , "cepat" )',
        ha="left", va="center", fontsize=7.4, family="DejaVu Sans Mono", color=INK, zorder=4)
ax.text(102.0, 20.6, '( "−1" , APP_PERFORMANCE , negatif , "sering error" )',
        ha="left", va="center", fontsize=7.4, family="DejaVu Sans Mono", color=INK, zorder=4)
ax.text(102.0, 17.6, "aspek implisit ditandai a = −1", ha="left", va="center",
        fontsize=7.0, color=MUTED, style="italic", zorder=4)

# ---------------------------------------------------------------- catatan kaki
ax.text(80, 3.4,
        "Sumber: repo ACOS-IndoBERT (pipeline Extract–Classify yang diadaptasi)  ·  "
        "gambar skematik, bukan hasil pengukuran",
        ha="center", va="center", fontsize=7.6, color=MUTED)

fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_SVG, bbox_inches="tight", facecolor="white")
print("ditulis:", OUT_PNG)
print("ditulis:", OUT_SVG)
