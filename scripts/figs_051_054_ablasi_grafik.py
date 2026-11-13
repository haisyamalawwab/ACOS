#!/usr/bin/env python3
"""Grafik untuk draf artikel 051-054 (fig25-fig29).

PENGEUALIAN TERCATAT (V-04): memakai matplotlib (bukan stdlib). Output deterministik:
tanpa RNG, tanpa timestamp, gaya tetap. Jalankan sesudah eda_044, eda_053, eda_055
(angka dibaca dari CSV/definisi konstan yang provenance-nya dicatat di tiap draf).

fig25  051  Distribusi kategori x sentimen (stacked bar horizontal)
fig26  051  Slot implisit per split (grouped bar)
fig27  052  Kurva interim Step-2: loss + F1 per epoch (3/15)
fig28  053  Baseline determinisme: 3 bar + scatter akurasi uji vs pangsa mayoritas latih
fig29  054  Kontingensi 2x2 implisit + pola komplementer per kategori (diverging)

Jalankan: python3 scripts/figs_051_054_ablasi_grafik.py
"""
from __future__ import annotations

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D044 = os.path.join(ROOT, "reports", "044_data")
OUT = ROOT

# ---------- gaya standar: putih, tanpa spine atas/kanan, grid tipis ----------
plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200,
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "legend.frameon": False,
})
C_NEG, C_POS, C_NEU = "#C44E52", "#55A868", "#8C8C8C"
C_BLUE, C_ORANGE = "#4C72B0", "#DD8452"


def read_csv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ============================= fig25 (051) =============================
rows = read_csv(os.path.join(D044, "category_counts.csv"))
rows.sort(key=lambda r: int(r["total"]))
cats = [r["category"] for r in rows]
neg = [int(r["negative"]) for r in rows]
pos = [int(r["positive"]) for r in rows]
neu = [int(r["neutral"]) for r in rows]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.barh(cats, neg, color=C_NEG, label="Negatif")
ax.barh(cats, pos, left=neg, color=C_POS, label="Positif")
ax.barh(cats, neu, left=[a + b for a, b in zip(neg, pos)], color=C_NEU, label="Netral")
ax.set_xlabel("Jumlah kuadruplet")
ax.set_title("Distribusi kategori dan sentimen (92.074 kuadruplet, gabungan split)")
ax.legend(loc="lower right", ncols=3)
ax.set_xlim(0, 31500)
for i, r in enumerate(rows):
    ax.text(int(r["total"]) + 350, i, f"{int(r['total']):,}".replace(",", "."),
            va="center", fontsize=7.5, color="#444444")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "reports", "fig25_kategori_sentimen_appsacos.png"))
plt.close(fig)

# ============================= fig26 (051) =============================
ss = read_csv(os.path.join(D044, "split_stats.csv"))
splits = ["train", "dev", "test"]
ai = [float(r["rasio_aspek_implisit_pct"]) for r in ss if r["split"] in splits]
oi = [float(r["rasio_opini_implisit_pct"]) for r in ss if r["split"] in splits]
ai.append(30.11)
oi.append(40.48)
labels = ["Train", "Dev", "Test", "Gabungan"]
x = range(len(labels))
w = 0.36

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.bar([i - w / 2 for i in x], ai, w, color=C_BLUE, label="Aspek implisit")
ax.bar([i + w / 2 for i in x], oi, w, color=C_ORANGE, label="Opini implisit")
for i, v in enumerate(ai):
    ax.text(i - w / 2, v + 0.6, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8)
for i, v in enumerate(oi):
    ax.text(i + w / 2, v + 0.6, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8)
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_ylabel("Pangsa kuadruplet (%)")
ax.set_ylim(0, 50)
ax.set_title("Slot implisit per split (kuadruplet gold)")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "reports", "fig26_implisit_per_split.png"))
plt.close(fig)

# ============================= fig27 (052) =============================
ep = [1, 2, 3]
loss = [0.5511, 0.3792, 0.3052]
f1 = [67.16, 66.55, 69.00]

fig, ax = plt.subplots(figsize=(6.0, 3.6))
ax.plot(ep, loss, "o-", color=C_BLUE, label="Loss pelatihan")
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
ax.set_ylim(0.2, 0.65)
ax.set_xticks(ep)
ax2 = ax.twinx()
ax2.spines["right"].set_visible(True)
ax2.spines["right"].set_linewidth(0.6)
ax2.plot(ep, f1, "s--", color=C_ORANGE, label="F1 kuadruplet (%)")
ax2.set_ylabel("F1 kuadruplet (%)")
ax2.set_ylim(64, 71)
ax2.grid(False)
for e, v in zip(ep, f1):
    ax2.annotate(f"{v:.2f}", (e, v), textcoords="offset points", xytext=(0, 7),
                 ha="center", fontsize=8, color=C_ORANGE)
ax.set_title("Step-2 Apps-ACOS (IndoBERT): 3 epoch pertama dari 15 (interim)")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="center right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "reports", "fig27_epoch_interim_step2.png"))
plt.close(fig)

# ============================= fig28 (053) =============================
fig, (axa, axb) = plt.subplots(1, 2, figsize=(9.2, 3.9))

names = ["Mayoritas global\n(B1)", "Mayoritas per kategori\n(B2)", "B2 + istilah aspek\n(A3)"]
vals = [50.33, 59.93, 63.31]
bars = axa.bar(names, vals, color=[C_NEU, C_BLUE, C_ORANGE], width=0.55)
for b, v in zip(bars, vals):
    axa.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.2f}".replace(".", ","),
             ha="center", fontsize=9)
axa.set_ylabel("Akurasi pada uji (%)")
axa.set_ylim(0, 72)
axa.set_title("(a) Baseline trivial pada 9.514 kuadruplet uji")
axa.tick_params(axis="x", labelsize=8)

mb = read_csv(os.path.join(ROOT, "reports", "053_data", "majority_baseline.csv"))
pts = [r for r in mb if r["kategori"] not in ("TOTAL",)]
xs = [float(r["share_mayoritas_train_pct"]) for r in pts]
ys = [float(r["akurasi_test_pct"]) for r in pts]
axb.scatter(xs, ys, s=26, color=C_BLUE, zorder=3)
lims = [40, 90]
axb.plot(lims, lims, "-", color="#AAAAAA", linewidth=0.8, zorder=1)
axb.set_xlim(lims)
axb.set_ylim(lims)
axb.set_xlabel("Pangsa kelas mayoritas kategori di data latih (%)")
axb.set_ylabel("Akurasi uji kategori tersebut (%)")
axb.set_title("(b) Akurasi uji vs pangsa mayoritas latih (13 kategori)")
for r in pts:
    if r["kategori"] in ("AUTH_ACCESS", "APP_PERFORMANCE", "TRANSACTION_TRANSFER",
                         "FEATURES_PRODUCT", "UI_UX_DESIGN"):
        axb.annotate(r["kategori"].replace("_", "\n"),
                     (float(r["share_mayoritas_train_pct"]), float(r["akurasi_test_pct"])),
                     textcoords="offset points", xytext=(5, -3), fontsize=6.5, color="#333333")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "reports", "fig28_baseline_determinisme.png"))
plt.close(fig)

# ============================= fig29 (054) =============================
fig, (axa, axb) = plt.subplots(1, 2, figsize=(9.6, 4.2))

pair_labels = ["E–E", "E–I", "I–E", "I–I"]
pair_vals = [29.40, 40.48, 30.11, 0.00]
bars = axa.bar(pair_labels, pair_vals, color=[C_BLUE, C_ORANGE, "#8172B3", C_NEG], width=0.55)
for b, v in zip(bars, pair_vals):
    axa.text(b.get_x() + b.get_width() / 2, v + 0.7,
             (f"{v:.2f}".replace(".", ",") + "%" if v > 0 else "0"), ha="center", fontsize=9)
axa.set_ylabel("Pangsa kuadruplet gold (%)")
axa.set_ylim(0, 47)
axa.set_title("(a) Kontingensi slot implisit (92.074 kuadruplet)")

im = read_csv(os.path.join(ROOT, "reports", "053_data", "implisit_2x2_kategori.csv"))
cats2 = [r["kategori"] for r in im if r["kategori"] not in ("TOTAL", "E-E", "E-I", "I-E", "I-I")]
a_imp = [float(r["aspek_implisit_pct"]) for r in im if r["kategori"] not in ("TOTAL", "E-E", "E-I", "I-E", "I-I")]
o_imp = [-float(r["opini_implisit_pct"]) for r in im if r["kategori"] not in ("TOTAL", "E-E", "E-I", "I-E", "I-I")]
order = sorted(range(len(cats2)), key=lambda i: a_imp[i])
cats2 = [cats2[i] for i in order]
a_imp = [a_imp[i] for i in order]
o_imp = [o_imp[i] for i in order]
y = range(len(cats2))
axb.barh(list(y), a_imp, color=C_BLUE, label="Aspect-implicit (%)")
axb.barh(list(y), o_imp, color=C_ORANGE, label="Opinion-implicit (%)")
axb.set_yticks(list(y))
axb.set_yticklabels(cats2, fontsize=7.5)
axb.axvline(0, color="#555555", linewidth=0.8)
axb.set_xlim(-85, 85)
axb.set_xticks([-75, -50, -25, 0, 25, 50, 75])
axb.set_xticklabels(["75", "50", "25", "0", "25", "50", "75"])
axb.set_xlabel("Opinion-implicit  ←  (%)  →  Aspect-implicit")
axb.set_title("(b) Pola komplementer implisit per kategori")
axb.legend(loc="lower right", fontsize=8)
axb.grid(axis="y", visible=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "reports", "fig29_implisit_2x2_kategori.png"))
plt.close(fig)

print("tulis: reports/fig25..fig29 (5 berkas PNG, dpi 200)")
