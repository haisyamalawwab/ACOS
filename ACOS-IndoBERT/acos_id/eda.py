"""EDA untuk dataset Indonesia Apps-ACOS, kontrak keluaran sama dengan V2.

Notebook V2/V3 memanggil `colab_utils.analyze_and_plot_eda()`, yang memetakan
domain lewat tabel tertutup::

    domain_map = {"rest16": ("Restaurant-ACOS", "rest16"),
                  "laptop": ("Laptop-ACOS", "laptop")}
    folder_name, prefix = domain_map.get(domain, ("Restaurant-ACOS", "rest16"))

Perhatikan fallback-nya: domain `appsid` **tidak error**, ia diam-diam membaca
Restaurant-ACOS dan melaporkan statistik dataset Inggris sebagai statistik
dataset Indonesia. Itu sebabnya modul ini ada, bukan patch pada `colab_utils`:
tiga salinan `colab_utils.py` di repo harus tetap identik, dan jalur Inggris
harus tetap utuh sebagai kontrol.

Kontrak keluaran dijaga persis sama supaya sel laporan V2 (`export_step_table`,
`df_ringkas`, blok `display(Image(...))`) bekerja tanpa perubahan:

- mengembalikan `(df_stats, df_records)`
- `df_stats` berkolom `Domain, Split, Sentences, Total_Quadruples,
  Explicit_Aspects, Implicit_Aspects, Explicit_Opinions, Implicit_Opinions,
  Negative_Count (0), Neutral_Count (1), Positive_Count (2)`
- `df_records` berkolom `Domain, Split, Text, Aspect, Category, Sentiment,
  Opinion, Is_Implicit_Aspect, Is_Implicit_Opinion, Text_Length`
- menulis `eda_dataset_statistics.csv`, `eda_all_samples_annotated.csv`, dan
  empat PNG `01_eda_dataset_distribution.png`,
  `02_eda_category_sentiment.png`, `02b_eda_length_and_implicit_combo.png`,
  `02c_eda_category_sentiment_heatmap.png`
"""
from __future__ import annotations

import os

from .taxonomy import DATASET_DIRNAME, DOMAIN

SENTI_LABEL = {0: "Negative (0)", 1: "Neutral (1)", 2: "Positive (2)"}

SPLITS = ("train", "dev", "test")


def _heatmap(ax, pivot, plt):
    """Heatmap beranotasi tanpa seaborn.

    `colab_utils` memakai `sns.heatmap`; di sini seaborn dijadikan opsional agar
    modul bisa diuji di mesin tanpa paket itu, dan hasilnya tetap satu berkas PNG
    dengan nama yang sama.
    """
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    vmax = pivot.values.max() or 1
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = int(pivot.values[i, j])
            ax.text(j, i, f"{v:d}", ha="center", va="center", fontsize=8,
                    color="white" if v > vmax * 0.6 else "black")
    return im


def read_quad_records(data_dir: str, domain: str = DOMAIN, splits=SPLITS):
    """Baca `<domain>_quad_<split>.tsv` menjadi `(stats, records)` list-of-dict."""
    stats, records = [], []
    for split in splits:
        path = os.path.join(data_dir, f"{domain}_quad_{split}.tsv")
        if not os.path.exists(path):
            continue
        n_sent = n_quad = 0
        exp_a = imp_a = exp_o = imp_o = 0
        senti_counts = {0: 0, 1: 0, 2: 0}
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) <= 1:
                    continue
                text, quads = parts[0], parts[1:]
                n_sent += 1
                n_quad += len(quads)
                n_words = len(text.split())
                for quad in quads:
                    f = quad.split(" ")
                    if len(f) < 4:
                        continue
                    asp, cat, senti_raw, opi = f[0], f[1], f[2], f[3]
                    senti = int(senti_raw) if senti_raw.isdigit() else 1
                    is_imp_a = asp.startswith("-1")
                    is_imp_o = opi.startswith("-1")
                    exp_a += not is_imp_a
                    imp_a += is_imp_a
                    exp_o += not is_imp_o
                    imp_o += is_imp_o
                    senti_counts[senti] = senti_counts.get(senti, 0) + 1
                    records.append({
                        "Domain": domain, "Split": split, "Text": text,
                        "Aspect": asp, "Category": cat, "Sentiment": senti,
                        "Opinion": opi,
                        "Is_Implicit_Aspect": is_imp_a,
                        "Is_Implicit_Opinion": is_imp_o,
                        "Text_Length": n_words,
                    })
        stats.append({
            "Domain": domain, "Split": split, "Sentences": n_sent,
            "Total_Quadruples": n_quad,
            "Explicit_Aspects": exp_a, "Implicit_Aspects": imp_a,
            "Explicit_Opinions": exp_o, "Implicit_Opinions": imp_o,
            "Negative_Count (0)": senti_counts.get(0, 0),
            "Neutral_Count (1)": senti_counts.get(1, 0),
            "Positive_Count (2)": senti_counts.get(2, 0),
        })
    return stats, records


def analyze_and_plot_eda_id(data_dir, domain=DOMAIN, output_plots_dir="./plots",
                            output_csv_dir="./csv"):
    """Padanan `colab_utils.analyze_and_plot_eda()` untuk dataset Indonesia.

    `data_dir` boleh berupa root proyek, folder `data/`, atau langsung folder
    dataset — ketiganya dicoba, seperti fungsi aslinya.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    os.makedirs(output_plots_dir, exist_ok=True)
    os.makedirs(output_csv_dir, exist_ok=True)

    kandidat = [
        os.path.join(data_dir, DATASET_DIRNAME),
        os.path.join(data_dir, "data", DATASET_DIRNAME),
        os.path.join(data_dir, "..", "data", DATASET_DIRNAME),
        data_dir,
    ]
    ds_path = next((p for p in kandidat
                    if os.path.exists(os.path.join(p, f"{domain}_quad_train.tsv"))), None)
    if ds_path is None:
        print(f"⚠️ Dataset {domain} tidak ditemukan di {kandidat}")
        return None, None

    stats, records = read_quad_records(ds_path, domain)
    df_stats = pd.DataFrame(stats)
    df_records = pd.DataFrame(records)
    if df_stats.empty:
        print(f"⚠️ Tidak ada split terbaca di {ds_path}")
        return df_stats, df_records

    stats_csv = os.path.join(output_csv_dir, "eda_dataset_statistics.csv")
    records_csv = os.path.join(output_csv_dir, "eda_all_samples_annotated.csv")
    df_stats.to_csv(stats_csv, index=False, encoding="utf-8")
    df_records.to_csv(records_csv, index=False, encoding="utf-8")
    print(f"📊 Statistik EDA disimpan: {stats_csv}")

    # PLOT 1 — komposisi split & explicit vs implicit aspect
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_stats.plot(x="Split", y=["Sentences", "Total_Quadruples"], kind="bar",
                  ax=axes[0], color=["#2b5c8f", "#d95f02"], rot=0)
    axes[0].set_title(f"[{domain.upper()}] Kalimat & Quadruple per Split",
                      fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Jumlah")
    axes[0].grid(axis="y", linestyle="--", alpha=0.7)
    df_stats.plot(x="Split", y=["Explicit_Aspects", "Implicit_Aspects"], kind="bar",
                  ax=axes[1], color=["#2ca02c", "#d62728"], rot=0)
    axes[1].set_title(f"[{domain.upper()}] Aspek Eksplisit vs Implisit",
                      fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Jumlah")
    axes[1].grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_plots_dir, "01_eda_dataset_distribution.png"), dpi=300)
    plt.close()

    # PLOT 2 — kategori teratas & polaritas
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    top_cats = df_records["Category"].value_counts().head(13)
    axes[0].barh(list(top_cats.index)[::-1], list(top_cats.values)[::-1],
                 color="#2b5c8f", edgecolor="white")
    axes[0].set_title(f"[{domain.upper()}] Kategori Aspek", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Frekuensi")
    axes[0].tick_params(axis="y", labelsize=8)
    senti_series = df_records["Sentiment"].map(SENTI_LABEL).value_counts()
    axes[1].pie(senti_series.values, labels=senti_series.index, autopct="%1.1f%%",
                startangle=140, colors=["#e74c3c", "#95a5a6", "#2ecc71"],
                wedgeprops={"edgecolor": "white", "linewidth": 2})
    axes[1].set_title(f"[{domain.upper()}] Sebaran Polaritas Sentimen",
                      fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_plots_dir, "02_eda_category_sentiment.png"), dpi=300)
    plt.close()

    # PLOT 3 — panjang teks & kombinasi implisit
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    axes[0].hist(df_records["Text_Length"], bins=40, color="#2b5c8f",
                 edgecolor="white", alpha=0.9)
    med = df_records["Text_Length"].median()
    axes[0].axvline(med, color="#d95f02", linestyle="--", linewidth=2,
                    label=f"median = {med:.0f} kata")
    axes[0].set_title(f"[{domain.upper()}] Distribusi Panjang Klausa",
                      fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Jumlah kata")
    axes[0].set_ylabel("Frekuensi quadruple")
    axes[0].legend()
    axes[0].grid(axis="y", linestyle="--", alpha=0.6)

    combo = (df_records["Is_Implicit_Aspect"].map({True: "Implisit", False: "Eksplisit"})
             + " Aspek + "
             + df_records["Is_Implicit_Opinion"].map({True: "Implisit", False: "Eksplisit"})
             + " Opini")
    counts = combo.value_counts()
    bars = axes[1].bar(range(len(counts)), counts.values,
                       color=["#3498db", "#9b59b6", "#e67e22", "#e74c3c"][:len(counts)],
                       edgecolor="black", alpha=0.88)
    total = counts.sum()
    for b, v in zip(bars, counts.values):
        axes[1].text(b.get_x() + b.get_width() / 2, v,
                     f"{v:,}\n({v / total * 100:.1f}%)", ha="center", va="bottom",
                     fontsize=9, fontweight="bold")
    axes[1].set_xticks(range(len(counts)))
    axes[1].set_xticklabels([c.replace(" + ", "\n+ ") for c in counts.index], fontsize=8)
    axes[1].set_title(f"[{domain.upper()}] Kombinasi Implisit/Eksplisit",
                      fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Jumlah quadruple")
    axes[1].margins(y=0.15)
    axes[1].grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_plots_dir, "02b_eda_length_and_implicit_combo.png"),
                dpi=300)
    plt.close()

    # PLOT 4 — heatmap kategori x sentimen
    pivot = (df_records.assign(Sent=lambda d: d["Sentiment"].map(SENTI_LABEL))
             .pivot_table(index="Category", columns="Sent", values="Text",
                          aggfunc="count", fill_value=0))
    if not pivot.empty:
        fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(pivot))))
        im = _heatmap(ax, pivot, plt)
        fig.colorbar(im, ax=ax, label="Jumlah quadruple")
        ax.set_title(f"[{domain.upper()}] Kategori x Sentimen", fontsize=12,
                     fontweight="bold")
        plt.tight_layout()
        plt.savefig(os.path.join(output_plots_dir,
                                 "02c_eda_category_sentiment_heatmap.png"), dpi=300)
        plt.close()

    return df_stats, df_records


def main(argv=None):
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    base = argv[0] if argv else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    out = argv[1] if len(argv) > 1 else os.path.join(base, "build", "_eda_id")
    df_stats, _ = analyze_and_plot_eda_id(
        os.path.join(base, "data"), output_plots_dir=os.path.join(out, "plots"),
        output_csv_dir=os.path.join(out, "csv"))
    if df_stats is None:
        return 1
    print(df_stats.to_string(index=False))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
