#!/usr/bin/env python3
"""Gambar 22 & 23 — Wordcloud per komponen ACOS (Apps-ACOS).

Gambar 22: 2x2 — A (aspek), C (kategori), O (opini), S (sentimen).
Gambar 23: 1x3 — kosakata opini per polaritas (positif / netral / negatif).

Sumber frekuensi: reports/044_data/*.csv (dihasilkan scripts/eda_044_appsid.py).
Keluaran: reports/fig22_wordcloud_acos.png/.svg, reports/fig23_wordcloud_sentimen.png/.svg

Jalankan: python3 scripts/fig22_wordcloud_acos.py
"""
from __future__ import annotations

import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wordcloud import WordCloud

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "reports", "044_data")
REP = os.path.join(ROOT, "reports")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

INK, MUTED = "#1a202c", "#4a5568"
BLUE, AMBER, GREEN, PURPLE = "#2b6cb0", "#b7791f", "#2f855a", "#6b46c1"
RED = "#c53030"

SENT_NAME = {"negative": "negatif", "neutral": "netral", "positive": "positif"}
SENT_COLOR = {"positif": GREEN, "netral": "#718096", "negatif": RED}


def baca_frekuensi(path: str, col_term="term", col_count="count", limit=None,
                   satu_kata=False) -> dict:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            term = r[col_term].strip()
            if not term or len(term) < 2:
                continue
            if satu_kata and " " in term:
                continue
            out[term] = out.get(term, 0) + int(float(r[col_count]))
    items = sorted(out.items(), key=lambda kv: -kv[1])
    if limit:
        items = items[:limit]
    return dict(items)


def awan(freqs: dict, color: str, w=1400, h=760, max_words=150, max_font=150) -> WordCloud:
    wc = WordCloud(font_path=FONT, width=w, height=h, background_color="white",
                   prefer_horizontal=0.94, relative_scaling=0.42, max_words=max_words,
                   margin=5, random_state=42, min_font_size=9, max_font_size=max_font,
                   color_func=lambda *a, **k: color)
    wc.generate_from_frequencies(freqs)
    return wc


def panel(ax, wc: WordCloud, judul: str, sub: str, color: str) -> None:
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("", pad=0)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False,
                               edgecolor=color, linewidth=1.6, clip_on=False))
    ax.text(0.0, 1.105, judul, transform=ax.transAxes, fontsize=12.0, fontweight="bold",
            color=color, va="bottom", ha="left")
    ax.text(0.0, 1.058, sub, transform=ax.transAxes, fontsize=8.0, color=MUTED,
            va="bottom", ha="left")


aspek = baca_frekuensi(os.path.join(DATA, "top_aspect_terms.csv"), limit=160, satu_kata=True)
opini = baca_frekuensi(os.path.join(DATA, "top_opinion_terms.csv"), limit=160, satu_kata=True)
kategori = baca_frekuensi(os.path.join(DATA, "category_counts.csv"), "category", "total")
sentimen = {}
with open(os.path.join(DATA, "sentiment_counts.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r["sentiment"] in SENT_NAME:
            sentimen[SENT_NAME[r["sentiment"]]] = int(r["count"])

with open(os.path.join(DATA, "eda_summary.json"), encoding="utf-8") as fh:
    _sum = json.load(fh)["hasil"]
n_a = _sum["istilah_aspek_unik"]
n_o = _sum["istilah_opini_unik"]
n_tup = _sum["total_tuple"]

# ============================================================ GAMBAR 22
fig = plt.figure(figsize=(16, 9.6))
gs = fig.add_gridspec(2, 2, left=0.03, right=0.97, top=0.825, bottom=0.07,
                      hspace=0.50, wspace=0.10)

fig.text(0.5, 0.945, "Gambar 22.  Wordcloud per Komponen ACOS — Apps-ACOS",
         ha="center", va="center", fontsize=18, fontweight="bold", color=INK)
fig.text(0.5, 0.905, "A (aspek) dan O (opini) diambil dari span eksplisit; C (kategori) dan S (sentimen) adalah label",
         ha="center", va="center", fontsize=9.2, color=MUTED)

ax = fig.add_subplot(gs[0, 0])
panel(ax, awan(aspek, BLUE, max_words=120, max_font=140), "A · ASPEK (span eksplisit)",
      f"{n_a} istilah unik · 64.348 span eksplisit · digambar 150 teratas, satu kata", BLUE)

ax = fig.add_subplot(gs[0, 1])
panel(ax, awan(dict(sorted(kategori.items(), key=lambda kv: -kv[1])), AMBER),
      "C · KATEGORI (13 label)",
      "ukuran ∝ jumlah tuple · FEATURES_PRODUCT 27.694 = 30,1%", AMBER)

ax = fig.add_subplot(gs[1, 0])
panel(ax, awan(opini, GREEN, max_words=120, max_font=140), "O · OPINI (span eksplisit)",
      f"{n_o} istilah unik · 54.800 span eksplisit · digambar 150 teratas; frasa «tidak bisa» 6.763 kali", GREEN)

ax = fig.add_subplot(gs[1, 1])
panel(ax, awan(sentimen, PURPLE), "S · SENTIMEN (3 kelas)",
      "variabel kategorikal: ukuran ∝ jumlah tuple, bukan kosakata "
      "(negatif 45.824 · positif 35.846 · netral 10.404)", PURPLE)

fig.text(0.5, 0.022,
         f"Sumber: reports/044_data/*.csv  ·  {n_tup:,} tuple hasil build Apps-ACOS  ·  "
         "wordcloud 1.9.6, font DejaVu Sans".replace(",", "."),
         ha="center", va="center", fontsize=7.4, color=MUTED)

# wordcloud adalah raster di dalam matplotlib -> SVG hanya membungkus bitmap,
# sehingga hanya PNG/WebP yang dihasilkan untuk gambar 22 dan 23.
fig.savefig(os.path.join(REP, "fig22_wordcloud_acos.png"), dpi=300,
            bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============================================================ GAMBAR 23
per_sent = {"positif": {}, "netral": {}, "negatif": {}}
with open(os.path.join(DATA, "opinion_terms_by_sentiment.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        name = SENT_NAME.get(r["sentiment"], r["sentiment"])
        if name in per_sent and " " not in r["term"]:
            per_sent[name][r["term"]] = int(r["count"])

fig = plt.figure(figsize=(16, 6.4))
gs = fig.add_gridspec(1, 3, left=0.03, right=0.97, top=0.76, bottom=0.09, wspace=0.08)

fig.text(0.5, 0.935, "Gambar 23.  Kosakata Opini per Polaritas — Apps-ACOS",
         ha="center", va="center", fontsize=17, fontweight="bold", color=INK)
fig.text(0.5, 0.888, "Span opini eksplisit yang paling sering muncul pada tiap kelas sentimen",
         ha="center", va="center", fontsize=9.0, color=MUTED)

for i, (name, freqs) in enumerate(per_sent.items()):
    ax = fig.add_subplot(gs[0, i])
    ranked = sorted(freqs.items(), key=lambda kv: -kv[1])[:45]
    freqs = dict(ranked)
    tot = sum(freqs.values())
    top3 = ", ".join([t for t, _ in ranked[:3]])
    panel(ax, awan(freqs, SENT_COLOR[name], w=1300, h=1000, max_words=45, max_font=150),
          name.upper(),
          f"{len(freqs)} istilah satu kata · {tot:,} kemunculan · teratas: {top3}".replace(",", "."),
          SENT_COLOR[name])

fig.text(0.5, 0.028,
         "Sumber: reports/044_data/opinion_terms_by_sentiment.csv  ·  "
         "60 istilah teratas per kelas, frasa multi-kata tidak digambar  ·  wordcloud 1.9.6",
         ha="center", va="center", fontsize=7.4, color=MUTED)

fig.savefig(os.path.join(REP, "fig23_wordcloud_sentimen.png"), dpi=300,
            bbox_inches="tight", facecolor="white")
plt.close(fig)

print("ditulis:", os.path.join(REP, "fig22_wordcloud_acos.png"))
print("ditulis:", os.path.join(REP, "fig23_wordcloud_sentimen.png"))
