#!/usr/bin/env python3
"""Gambar 20 — Grafik batang perbandingan ketercakupan span mapping.

Review-Level : Aspek 61,5%  · Opini 48,0%
Clause-Level : Aspek 100,0% · Opini 100,0%   (truncation loss dieliminasi)

Menghasilkan:
  reports/fig20_ketercakupan_span_mapping.png  (300 dpi)
  reports/fig20_ketercakupan_span_mapping.svg
  reports/fig20_ketercakupan_span_mapping.webp (lewat ImageMagick, opsional)

Jalankan: python3 scripts/fig20_ketercakupan_span.py
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "reports", "fig20_ketercakupan_span_mapping")

INK = "#1a202c"
MUTED = "#4a5568"
FAINT = "#a0aec0"
RED = "#c53030"
RED_F = "#e07a7a"
GREEN = "#2f855a"
GREEN_F = "#5aa97c"
GRID = "#e2e8f0"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.linewidth": 0, "svg.fonttype": "none"})

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 160)
ax.set_ylim(0, 90)
ax.axis("off")
fig.patch.set_facecolor("white")

Y0, H = 20.0, 42.0            # baseline & tinggi untuk 100%
def yv(v: float) -> float:
    return Y0 + H * v / 100.0

X0, X1 = 16.0, 104.0          # rentang sumbu

# ------------------------------------------------------------------ judul
ax.text(80, 86.6, "Gambar 3.  Ketercakupan Span Mapping: Ulasan Utuh vs Klausa",
        ha="center", va="center", fontsize=18.0, fontweight="bold", color=INK)
ax.text(80, 83.2, "Persentase span aspek dan opini yang berhasil dipetakan ke dalam jendela model",
        ha="center", va="center", fontsize=9.0, color=MUTED)

# ------------------------------------------------------------------ kisi & sumbu
for v in (0, 20, 40, 60, 80, 100):
    ax.plot([X0, X1], [yv(v), yv(v)], color=(FAINT if v in (0, 100) else GRID),
            linewidth=(1.1 if v in (0, 100) else 0.8), zorder=1,
            linestyle=((0, (5, 3)) if v == 100 else "-"))
    ax.text(X0 - 2.2, yv(v), f"{v}", ha="right", va="center", fontsize=8.4, color=MUTED)

ax.text(X0 - 2.2, yv(100) + 4.6, "%", ha="right", va="center", fontsize=8.4, color=MUTED)
ax.text(X0, yv(100) + 4.6, "ketercakupan span", ha="left", va="center",
        fontsize=8.6, color=MUTED, style="italic")
ax.text(X1, yv(100) + 4.6, "plafon teoretis 100%", ha="right", va="center",
        fontsize=8.0, color=FAINT, style="italic")

# ------------------------------------------------------------------ batang
BW, GAP = 11.0, 4.0
groups = [("Aspek", 36.0, 61.5), ("Opini", 76.0, 48.0)]

for label, c, red_v in groups:
    xr = c - GAP / 2 - BW
    xg = c + GAP / 2

    # defisit (span tidak terpetakan) di atas batang Review-Level
    ax.add_patch(Rectangle((xr, yv(red_v)), BW, yv(100) - yv(red_v),
                           facecolor="none", edgecolor=RED_F, hatch="///",
                           linewidth=0.9, zorder=2, alpha=0.75))
    # batang Review-Level
    ax.add_patch(Rectangle((xr, Y0), BW, yv(red_v) - Y0, facecolor=RED,
                           edgecolor="white", linewidth=0.8, zorder=3))
    ax.text(xr + BW / 2, yv(red_v) - 1.6, f"{red_v:.1f}%".replace(".", ","),
            ha="center", va="top", fontsize=11.2, fontweight="bold", color="white", zorder=5)

    # batang Clause-Level
    ax.add_patch(Rectangle((xg, Y0), BW, yv(100) - Y0, facecolor=GREEN,
                           edgecolor="white", linewidth=0.8, zorder=3))
    ax.text(xg + BW / 2, yv(100) + 2.0, "100,0%",
            ha="center", va="bottom", fontsize=11.0, fontweight="bold", color=GREEN, zorder=5)

    # angka di dalam batang
    ax.text(xr + BW / 2, Y0 + 2.4, "review", ha="center", va="bottom",
            fontsize=7.2, color="white", zorder=5, fontweight="bold")
    ax.text(xg + BW / 2, Y0 + 2.4, "klausa", ha="center", va="bottom",
            fontsize=7.2, color="white", zorder=5, fontweight="bold")

    # label kategori + selisih
    ax.text(c, Y0 - 4.0, label, ha="center", va="center", fontsize=11.5,
            fontweight="bold", color=INK)
    delta = 100.0 - red_v
    ax.text(c, Y0 - 7.6, f"Δ +{delta:.1f} poin".replace(".", ","), ha="center", va="center",
            fontsize=8.0, color=GREEN, fontweight="bold")

ax.plot([X0, X1], [Y0, Y0], color=MUTED, linewidth=1.3, zorder=4)

# ------------------------------------------------------------------ legenda
for lx, color, txt in ((X0, RED, "Review-Level  ·  satu ulasan utuh"),
                       (X0 + 36.0, GREEN, "Clause-Level  ·  segmentasi klausa")):
    ax.add_patch(Rectangle((lx, 75.4), 3.4, 3.0, facecolor=color, edgecolor="none", zorder=5))
    ax.text(lx + 4.8, 76.9, txt, ha="left", va="center", fontsize=8.8, color=INK)
ax.add_patch(Rectangle((X0, 70.8), 3.4, 3.0, facecolor="none", edgecolor=RED_F,
                       hatch="///", linewidth=0.9, zorder=5))
ax.text(X0 + 4.8, 72.3, "area bergaris = span tidak terpetakan (di luar jendela model)",
        ha="left", va="center", fontsize=8.0, color=MUTED)

# ================================================================== panel kanan
PX0, PX1, PY0, PY1 = 108.0, 158.0, 10.0, 79.0
ax.add_patch(FancyBboxPatch((PX0, PY0), PX1 - PX0, PY1 - PY0,
                            boxstyle="round,pad=0.4,rounding_size=1.6",
                            linewidth=1.2, edgecolor=GREEN, facecolor="#f0fff4",
                            zorder=1, linestyle=(0, (6, 4))))

ax.text(PX0 + 3.0, PY1 - 3.2, "PENANDA KHUSUS", ha="left", va="center",
        fontsize=7.6, fontweight="bold", color=GREEN)
ax.text(PX0 + 3.0, PY1 - 7.2, "Eliminasi truncation loss", ha="left", va="center",
        fontsize=11.4, fontweight="bold", color=INK)

ax.text(PX0 + 4.5, 62.0, "0", ha="left", va="center", fontsize=36, fontweight="bold",
        color=GREEN, zorder=5)
ax.text(PX0 + 12.5, 64.2, "span terpotong", ha="left", va="center", fontsize=9.6,
        fontweight="bold", color=GREEN, zorder=5)
ax.text(PX0 + 12.5, 60.0, "pada unit klausa,\nuntuk aspek maupun opini", ha="left", va="center",
        fontsize=7.4, color=MUTED, zorder=5, linespacing=1.5)

ax.plot([PX0 + 3.5, PX1 - 3.5], [53.0, 53.0], color="#c6f6d5", linewidth=1.4, zorder=3)

rows = [
    (RED, "Review-Level", "38,5% span aspek  ·  52,0% span opini\ntidak terpetakan (di luar jendela model)", 49.6),
    (GREEN, "Clause-Level", "0,0%  ·  0,0%\nseluruh span terpetakan", 39.0),
]
for color, name, desc, y in rows:
    ax.add_patch(Rectangle((PX0 + 3.5, y - 0.9), 1.8, 1.8, facecolor=color,
                           edgecolor="none", zorder=5))
    ax.text(PX0 + 7.0, y, name, ha="left", va="center", fontsize=9.0,
            fontweight="bold", color=color, zorder=5)
    ax.text(PX0 + 7.0, y - 4.4, desc, ha="left", va="center", fontsize=7.4,
            color=MUTED, zorder=5, linespacing=1.5)

ax.plot([PX0 + 3.5, PX1 - 3.5], [30.6, 30.6], color="#c6f6d5", linewidth=1.4, zorder=3)
ax.text(PX0 + 3.5, 27.0, "Selisih ketercakupan", ha="left", va="center", fontsize=8.0,
        fontweight="bold", color=INK, zorder=5)
ax.text(PX0 + 3.5, 23.4, "+38,5 poin (aspek)   ·   +52,0 poin (opini)", ha="left", va="center",
        fontsize=7.6, color=GREEN, zorder=5)
ax.text(PX0 + 3.5, 19.4, "Penanda dihitung sebagai 100% − ketercakupan.",
        ha="left", va="center", fontsize=6.8, color=MUTED, zorder=5, style="italic")
ax.text(PX0 + 3.5, 15.6, "Unit klausa: truncation loss = 0 pada kedua atribut.",
        ha="left", va="center", fontsize=6.8, color=GREEN, zorder=5, style="italic")

# ------------------------------------------------------------------ catatan kaki
ax.text(80, 3.2,
        "Sumber: 023 §2.2 (pengukuran) & 035 §III-C  ·  penanda = 100% − ketercakupan  ·  "
        "0 [UNK] dari _build_report_appsid.json  ·  grafik skematik",
        ha="center", va="center", fontsize=7.2, color=MUTED)

fig.savefig(BASE + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(BASE + ".svg", bbox_inches="tight", facecolor="white")
print("ditulis:", BASE + ".png")
print("ditulis:", BASE + ".svg")
