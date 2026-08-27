# coding=utf-8
"""
Utility module for ACOS (Aspect-Category-Opinion-Sentiment) Quadruple Extraction.
Provides automated timestamped session directory management, model checkpoint persistence,
publication-quality visualizations (Matplotlib/Seaborn), CSV tabular exports, and live inference helper.
"""

import os
import re
import sys
import json
import shutil
import urllib.request
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch

# Configure Matplotlib styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300


def setup_timestamped_run_dir(base_dir="results", domain="rest16"):
    """
    Creates a unique timestamped session directory with isolated subfolders:
    results/<domain>_<DDMMYYYY_HMS>/
        ├── checkpoints/
        │   ├── step1_best/
        │   └── step2_best/
        ├── plots/
        ├── csv/
        ├── md/
        └── logs/
    """
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    run_dir = os.path.join(base_dir, f"{domain}_{timestamp}")
    
    dirs = {
        "root": run_dir,
        "checkpoints": os.path.join(run_dir, "checkpoints"),
        "step1_checkpoint": os.path.join(run_dir, "checkpoints", "step1_best"),
        "step2_checkpoint": os.path.join(run_dir, "checkpoints", "step2_best"),
        "plots": os.path.join(run_dir, "plots"),
        "csv": os.path.join(run_dir, "csv"),
        "md": os.path.join(run_dir, "md"),
        "logs": os.path.join(run_dir, "logs")
    }
    
    for path in dirs.values():
        os.makedirs(path, exist_ok=True)
        
    print(f"📁 Initialized timestamped session directory: {run_dir}")
    return dirs


def download_bert_pretrained(target_dir="./bert_base_uncased"):
    """
    Downloads and caches bert-base-uncased assets (config.json, pytorch_model.bin, vocab.txt)
    directly from HuggingFace Hub to guarantee offline reproducibility and avoid dead legacy S3 URLs.
    """
    os.makedirs(target_dir, exist_ok=True)
    base_hf_url = "https://huggingface.co/bert-base-uncased/resolve/main"
    files = {
        "config.json": f"{base_hf_url}/config.json",
        "pytorch_model.bin": f"{base_hf_url}/pytorch_model.bin",
        "vocab.txt": f"{base_hf_url}/vocab.txt"
    }
    
    for fname, url in files.items():
        dst = os.path.join(target_dir, fname)
        if not os.path.exists(dst) or os.path.getsize(dst) == 0:
            print(f"📥 Downloading {fname} to {dst} ...")
            urllib.request.urlretrieve(url, dst)
        else:
            print(f"✅ {fname} already cached at {dst} ({os.path.getsize(dst)/1024/1024:.2f} MB)")
            
    return target_dir


def analyze_and_plot_eda(data_dir, domain="rest16", output_plots_dir="./plots", output_csv_dir="./csv"):
    """
    Performs Exploratory Data Analysis (EDA) on ACOS datasets (Restaurant-ACOS or Laptop-ACOS):
    - Explicit vs Implicit Aspect/Opinion counts
    - Aspect Category distribution
    - Sentiment Polarity distribution
    - Token sequence length distribution
    Saves plots (PNG 300 DPI) and structured CSV tables.
    """
    os.makedirs(output_plots_dir, exist_ok=True)
    os.makedirs(output_csv_dir, exist_ok=True)
    
    # Mapping
    domain_map = {
        "rest16": ("Restaurant-ACOS", "rest16"),
        "laptop": ("Laptop-ACOS", "laptop")
    }
    folder_name, prefix = domain_map.get(domain, ("Restaurant-ACOS", "rest16"))
    
    # Find dataset path
    possible_paths = [
        os.path.join(data_dir, folder_name),
        os.path.join(data_dir, "data", folder_name),
        os.path.join(data_dir, "..", "data", folder_name)
    ]
    ds_path = None
    for p in possible_paths:
        if os.path.exists(p):
            ds_path = p
            break
            
    if not ds_path:
        print(f"⚠️ Dataset path for {domain} not found in {possible_paths}")
        return None, None
        
    splits = ["train", "dev", "test"]
    stats = []
    records = []
    
    for split in splits:
        fn = os.path.join(ds_path, f"{prefix}_quad_{split}.tsv")
        if not os.path.exists(fn):
            continue
        with open(fn, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        sentence_count = len(lines)
        total_quads = 0
        explicit_a = 0
        implicit_a = 0
        explicit_o = 0
        implicit_o = 0
        senti_counts = {0: 0, 1: 0, 2: 0} # 0: negative, 1: neutral, 2: positive
        categories = {}
        
        for line in lines:
            parts = line.strip().split("\t")
            if len(parts) <= 1:
                continue
            text = parts[0]
            quads = parts[1:]
            total_quads += len(quads)
            
            for q in quads:
                q_parts = q.split(" ")
                if len(q_parts) < 4:
                    continue
                asp = q_parts[0]
                cat = q_parts[1]
                senti = int(q_parts[2]) if q_parts[2].isdigit() else 1
                opi = q_parts[3]
                
                # Check implicit
                is_imp_a = (asp == "-1,-1" or asp == "NULL" or "-1" in asp)
                is_imp_o = (opi == "-1,-1" or opi == "NULL" or "-1" in opi)
                
                if is_imp_a:
                    implicit_a += 1
                else:
                    explicit_a += 1
                    
                if is_imp_o:
                    implicit_o += 1
                else:
                    explicit_o += 1
                    
                senti_counts[senti] = senti_counts.get(senti, 0) + 1
                categories[cat] = categories.get(cat, 0) + 1
                
                records.append({
                    "Domain": domain,
                    "Split": split,
                    "Text": text,
                    "Aspect": asp,
                    "Category": cat,
                    "Sentiment": senti,
                    "Opinion": opi,
                    "Is_Implicit_Aspect": is_imp_a,
                    "Is_Implicit_Opinion": is_imp_o,
                    "Text_Length": len(text.split())
                })
                
        stats.append({
            "Domain": domain,
            "Split": split,
            "Sentences": sentence_count,
            "Total_Quadruples": total_quads,
            "Explicit_Aspects": explicit_a,
            "Implicit_Aspects": implicit_a,
            "Explicit_Opinions": explicit_o,
            "Implicit_Opinions": implicit_o,
            "Negative_Count (0)": senti_counts.get(0, 0),
            "Neutral_Count (1)": senti_counts.get(1, 0),
            "Positive_Count (2)": senti_counts.get(2, 0)
        })
        
    df_stats = pd.DataFrame(stats)
    df_records = pd.DataFrame(records)
    
    # Save CSVs
    stats_csv_path = os.path.join(output_csv_dir, "eda_dataset_statistics.csv")
    records_csv_path = os.path.join(output_csv_dir, "eda_all_samples_annotated.csv")
    df_stats.to_csv(stats_csv_path, index=False, encoding="utf-8")
    df_records.to_csv(records_csv_path, index=False, encoding="utf-8")
    print(f"📊 Saved EDA Statistics CSV: {stats_csv_path}")
    
    # PLOT 1: Dataset Composition & Quadruple Counts
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_stats.plot(x="Split", y=["Sentences", "Total_Quadruples"], kind="bar", ax=axes[0], color=["#2b5c8f", "#d95f02"], rot=0)
    axes[0].set_title(f"[{domain.upper()}] Sentences & Quadruples per Split", fontsize=12, fontweight='bold')
    axes[0].set_ylabel("Count")
    axes[0].grid(axis="y", linestyle="--", alpha=0.7)
    
    # Explicit vs Implicit Aspects
    df_stats.plot(x="Split", y=["Explicit_Aspects", "Implicit_Aspects"], kind="bar", ax=axes[1], color=["#2ca02c", "#d62728"], rot=0)
    axes[1].set_title(f"[{domain.upper()}] Explicit vs Implicit Aspects", fontsize=12, fontweight='bold')
    axes[1].set_ylabel("Count")
    axes[1].grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plot1_path = os.path.join(output_plots_dir, "01_eda_dataset_distribution.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    
    # PLOT 2: Category & Sentiment Distribution
    if not df_records.empty:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        # Top 10 categories
        top_cats = df_records["Category"].value_counts().head(10)
        sns.barplot(y=top_cats.index, x=top_cats.values, ax=axes[0], palette="viridis")
        axes[0].set_title(f"[{domain.upper()}] Top Aspect Categories", fontsize=12, fontweight='bold')
        axes[0].set_xlabel("Frequency")
        
        # Sentiment distribution
        senti_map = {0: "Negative (0)", 1: "Neutral (1)", 2: "Positive (2)"}
        senti_series = df_records["Sentiment"].map(senti_map).value_counts()
        colors = ["#e74c3c", "#95a5a6", "#2ecc71"]
        axes[1].pie(senti_series.values, labels=senti_series.index, autopct='%1.1f%%', startangle=140, colors=colors,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        axes[1].set_title(f"[{domain.upper()}] Sentiment Polarity Breakdown", fontsize=12, fontweight='bold')
        plt.tight_layout()
        plot2_path = os.path.join(output_plots_dir, "02_eda_category_sentiment.png")
        plt.savefig(plot2_path, dpi=300)
        plt.close()

        # PLOT 3: distribusi panjang teks + kombinasi implicit/explicit
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        axes[0].hist(df_records["Text_Length"], bins=40, color="#2b5c8f",
                     edgecolor="white", alpha=0.9)
        med = df_records["Text_Length"].median()
        axes[0].axvline(med, color="#d95f02", linestyle="--", linewidth=2,
                        label=f"median = {med:.0f} kata")
        axes[0].set_title(f"[{domain.upper()}] Distribusi Panjang Kalimat", fontsize=12, fontweight="bold")
        axes[0].set_xlabel("Jumlah kata")
        axes[0].set_ylabel("Frekuensi quadruple")
        axes[0].legend()
        axes[0].grid(axis="y", linestyle="--", alpha=0.6)

        combo = (df_records["Is_Implicit_Aspect"].map({True: "Implicit", False: "Explicit"}) + " Aspect + "
                 + df_records["Is_Implicit_Opinion"].map({True: "Implicit", False: "Explicit"}) + " Opinion")
        combo_counts = combo.value_counts()
        bars = axes[1].bar(range(len(combo_counts)), combo_counts.values,
                           color=["#3498db", "#9b59b6", "#e67e22", "#e74c3c"][:len(combo_counts)],
                           edgecolor="black", alpha=0.88)
        total = combo_counts.sum()
        for b, v in zip(bars, combo_counts.values):
            axes[1].text(b.get_x() + b.get_width() / 2, v, f"{v:,}\n({v / total * 100:.1f}%)",
                         ha="center", va="bottom", fontsize=9, fontweight="bold")
        axes[1].set_xticks(range(len(combo_counts)))
        axes[1].set_xticklabels([c.replace(" + ", "\n+ ") for c in combo_counts.index], fontsize=8)
        axes[1].set_title(f"[{domain.upper()}] Kombinasi Implicit/Explicit", fontsize=12, fontweight="bold")
        axes[1].set_ylabel("Jumlah quadruple")
        axes[1].margins(y=0.15)
        axes[1].grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()
        plot3_path = os.path.join(output_plots_dir, "02b_eda_length_and_implicit_combo.png")
        plt.savefig(plot3_path, dpi=300)
        plt.close()

        # PLOT 4: heatmap kategori (top 12) x sentimen
        top12 = df_records["Category"].value_counts().head(12).index
        pivot = (df_records[df_records["Category"].isin(top12)]
                 .assign(Sent=lambda d: d["Sentiment"].map(senti_map))
                 .pivot_table(index="Category", columns="Sent", values="Text",
                              aggfunc="count", fill_value=0))
        if not pivot.empty:
            plt.figure(figsize=(9, max(4, 0.45 * len(pivot))))
            sns.heatmap(pivot, annot=True, fmt="d", cmap="YlGnBu", linewidths=0.5,
                        cbar_kws={"label": "Jumlah quadruple"})
            plt.title(f"[{domain.upper()}] Kategori (Top 12) x Sentimen", fontsize=12, fontweight="bold")
            plt.ylabel("")
            plt.tight_layout()
            plot4_path = os.path.join(output_plots_dir, "02c_eda_category_sentiment_heatmap.png")
            plt.savefig(plot4_path, dpi=300)
            plt.close()
        
    return df_stats, df_records


def plot_training_history(history_list, task_name="Step1", output_plot_path="training_curves.png", output_csv_path="training_history.csv"):
    """
    Plots training loss and validation Precision, Recall, F1 over epochs and exports history CSV.
    """
    if not history_list:
        return
    df = pd.DataFrame(history_list)
    df.to_csv(output_csv_path, index=False, encoding="utf-8")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # Loss curve
    if "loss" in df.columns or "train_loss" in df.columns:
        loss_col = "loss" if "loss" in df.columns else "train_loss"
        axes[0].plot(df["epoch"], df[loss_col], marker='o', color="#e74c3c", label="Training Loss", linewidth=2)
        axes[0].set_title(f"{task_name} Training Loss", fontsize=12, fontweight='bold')
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].legend()
        axes[0].grid(True, linestyle="--", alpha=0.6)
        
    # F1 / Precision / Recall
    metric_cols = [c for c in ["precision", "recall", "micro-F1", "f1"] if c in df.columns]
    if metric_cols:
        for col in metric_cols:
            axes[1].plot(df["epoch"], df[col], marker='s', label=col.capitalize(), linewidth=2)
        axes[1].set_title(f"{task_name} Validation Metrics Progression", fontsize=12, fontweight='bold')
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Score")
        axes[1].legend()
        axes[1].grid(True, linestyle="--", alpha=0.6)
        
    plt.tight_layout()
    plt.savefig(output_plot_path, dpi=300)
    plt.close()
    print(f"📈 Saved training plot: {output_plot_path}")
    return {"plot": output_plot_path, "csv": output_csv_path, "history": df}


def export_benchmark_tables_and_plots(subtask_metrics_dict, subset_metrics_dict, output_plots_dir="./plots", output_csv_dir="./csv"):
    """
    Exports comprehensive benchmark results:
    1. 15 Subtasks evaluation (Aspect, Opinion, Category, Sentiment, Pairs, Quadruple, etc.)
    2. 4 Implicit/Explicit subsets breakdown (Subset 0, 1, 2, 3, 4)
    Generates bar charts and CSV tables.
    """
    os.makedirs(output_plots_dir, exist_ok=True)
    os.makedirs(output_csv_dir, exist_ok=True)
    
    # 1. Subtasks Table & Plot
    if subtask_metrics_dict:
        subtasks_data = []
        for task, m in subtask_metrics_dict.items():
            subtasks_data.append({
                "Subtask": task,
                "Precision": m.get("precision", 0.0),
                "Recall": m.get("recall", 0.0),
                "Micro_F1": m.get("micro-F1", m.get("f1", 0.0))
            })
        df_subtasks = pd.DataFrame(subtasks_data)
        csv1 = os.path.join(output_csv_dir, "benchmark_15_subtasks_summary.csv")
        df_subtasks.to_csv(csv1, index=False, encoding="utf-8")
        
        # Plot Subtasks F1
        plt.figure(figsize=(12, 7))
        df_sorted = df_subtasks.sort_values(by="Micro_F1", ascending=True)
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_sorted)))
        bars = plt.barh(df_sorted["Subtask"], df_sorted["Micro_F1"] * 100, color=colors, edgecolor="black", alpha=0.85)
        for bar in bars:
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.2f}%", 
                     va='center', ha='left', fontsize=9, fontweight='bold')
        plt.title("ACOS Benchmark Performance across All 15 Sub-Tasks (Micro-F1 %)", fontsize=13, fontweight='bold')
        plt.xlabel("Micro-F1 (%)")
        plt.xlim(0, 105)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plot1 = os.path.join(output_plots_dir, "05_benchmark_15_subtasks_f1.png")
        plt.savefig(plot1, dpi=300)
        plt.close()
        
    # 2. Implicit Subsets Table & Plot
    if subset_metrics_dict:
        subset_names = {
            0: "Subset 0: Explicit Aspect + Explicit Opinion",
            1: "Subset 1: Implicit Aspect + Explicit Opinion",
            2: "Subset 2: Explicit Aspect + Implicit Opinion",
            3: "Subset 3: Implicit Aspect + Implicit Opinion",
            4: "Subset 4: Overall Total Quadruples"
        }
        subsets_data = []
        for s_idx, m in subset_metrics_dict.items():
            subsets_data.append({
                "Subset_ID": s_idx,
                "Subset_Description": subset_names.get(s_idx, f"Subset {s_idx}"),
                "Precision": m.get("precision", 0.0),
                "Recall": m.get("recall", 0.0),
                "Micro_F1": m.get("micro-F1", m.get("f1", 0.0))
            })
        df_subsets = pd.DataFrame(subsets_data)
        csv2 = os.path.join(output_csv_dir, "benchmark_implicit_subsets_summary.csv")
        df_subsets.to_csv(csv2, index=False, encoding="utf-8")
        
        # Plot Subsets
        plt.figure(figsize=(10, 5))
        x = np.arange(len(df_subsets))
        width = 0.25
        plt.bar(x - width, df_subsets["Precision"] * 100, width, label="Precision", color="#3498db")
        plt.bar(x, df_subsets["Recall"] * 100, width, label="Recall", color="#e67e22")
        plt.bar(x + width, df_subsets["Micro_F1"] * 100, width, label="Micro-F1", color="#2ecc71")
        plt.xticks(x, [f"Subset {row['Subset_ID']}" for _, row in df_subsets.iterrows()], rotation=0, fontweight='bold')
        plt.title("ACOS Quadruple Extraction Performance by Implicit/Explicit Subsets", fontsize=12, fontweight='bold')
        plt.ylabel("Score (%)")
        plt.ylim(0, 100)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plot2 = os.path.join(output_plots_dir, "06_implicit_subsets_breakdown_f1.png")
        plt.savefig(plot2, dpi=300)
        plt.close()
        
    print(f"📊 Saved Benchmark Visualizations & CSVs to {output_plots_dir} and {output_csv_dir}")


def display_quadruple_dataframe(quadruples_list):
    """
    Nicely formats extracted quadruples into a styled pandas DataFrame for interactive display.
    """
    if not quadruples_list:
        return pd.DataFrame(columns=["Aspect", "Category", "Opinion", "Sentiment", "Is_Implicit_Aspect", "Is_Implicit_Opinion"])
    df = pd.DataFrame(quadruples_list)
    return df


# ---------------------------------------------------------------------------
# Tabel + ekspor Markdown per step
# ---------------------------------------------------------------------------

def df_to_markdown(df, max_rows=None, floatfmt="{:.4f}"):
    """
    Mengubah DataFrame ke tabel Markdown tanpa dependensi `tabulate`.
    """
    if df is None or len(df) == 0:
        return "_(tabel kosong)_\n"
    d = df.head(max_rows) if max_rows else df

    def fmt(v):
        if isinstance(v, float):
            return floatfmt.format(v)
        return str(v).replace("|", "\\|").replace("\n", " ")

    cols = list(d.columns)
    head = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = ["| " + " | ".join(fmt(r[c]) for c in cols) + " |" for _, r in d.iterrows()]
    out = "\n".join([head, sep] + body)
    if max_rows and len(df) > max_rows:
        out += f"\n\n_Menampilkan {max_rows} dari {len(df)} baris._"
    return out + "\n"


def export_step_table(df, name, csv_dir, md_dir=None, title=None, notes=None,
                      max_rows_md=50, show=True):
    """
    Satu pintu untuk setiap step: simpan CSV, simpan/kembalikan potongan Markdown,
    dan tampilkan tabel di notebook.

    Mengembalikan dict {'csv': path, 'md': path|None, 'markdown': str}.
    """
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{name}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")

    md_block = f"### {title or name}\n\n{df_to_markdown(df, max_rows=max_rows_md)}"
    if notes:
        md_block += f"\n{notes}\n"

    md_path = None
    if md_dir:
        os.makedirs(md_dir, exist_ok=True)
        md_path = os.path.join(md_dir, f"{name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title or name}\n\n")
            f.write(f"_Dihasilkan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
            f.write(df_to_markdown(df, max_rows=max_rows_md))
            if notes:
                f.write(f"\n{notes}\n")

    if show:
        try:
            from IPython.display import display as _display
            print(f"=== {title or name} ({len(df)} baris) ===")
            _display(df.head(max_rows_md))
        except Exception:
            print(df.head(max_rows_md).to_string())
    print(f"[tabel] CSV: {csv_path}" + (f" | MD: {md_path}" if md_path else ""))
    return {"csv": csv_path, "md": md_path, "markdown": md_block}


class MarkdownReport:
    """
    Akumulator hasil teks per step, lalu ditulis sebagai satu file Markdown.

    rep = MarkdownReport("Step 1", md_dir)
    rep.section("Konfigurasi").kv({"domain": "rest16"}).table(df).text("catatan").save()
    """

    def __init__(self, title, md_dir, filename=None, meta=None):
        os.makedirs(md_dir, exist_ok=True)
        self.title = title
        self.path = os.path.join(md_dir, filename or f"{_slug(title)}.md")
        self.parts = []
        self.parts.append(f"# {title}\n")
        self.parts.append(f"_Dihasilkan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")
        if meta:
            self.parts.append(_kv_block(meta))

    def section(self, heading, level=2):
        self.parts.append(f"\n{'#' * level} {heading}\n")
        return self

    def text(self, body):
        self.parts.append(f"{body}\n")
        return self

    def kv(self, mapping):
        self.parts.append(_kv_block(mapping))
        return self

    def table(self, df, max_rows=50, caption=None):
        if caption:
            self.parts.append(f"**{caption}**\n")
        self.parts.append(df_to_markdown(df, max_rows=max_rows))
        return self

    def code(self, body, lang="text"):
        self.parts.append(f"```{lang}\n{body}\n```\n")
        return self

    def image(self, plot_path, caption=None):
        """Sisipkan gambar sebagai path relatif terhadap lokasi file Markdown."""
        try:
            rel = os.path.relpath(plot_path, os.path.dirname(self.path))
        except ValueError:
            rel = plot_path
        self.parts.append(f"![{caption or os.path.basename(plot_path)}]({rel.replace(os.sep, '/')})\n")
        if caption:
            self.parts.append(f"_{caption}_\n")
        return self

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.parts))
        print(f"[markdown] Laporan disimpan: {self.path}")
        return self.path


def _slug(s):
    keep = [c.lower() if c.isalnum() else "_" for c in str(s)]
    out = "".join(keep)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_") or "report"


def _kv_block(mapping):
    rows = ["| Kunci | Nilai |", "| --- | --- |"]
    for k, v in mapping.items():
        rows.append(f"| {k} | {v} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------------------
# Penangkap metrik sub-task dari log pair_eval
# ---------------------------------------------------------------------------

class SubtaskMetricCapture:
    """
    `pair_eval` di eval_metrics.py menghitung metrik 15 sub-task tetapi hanya
    menulisnya ke logger tanpa mengembalikannya. Handler ini menangkap baris log
    tersebut dan mengubahnya menjadi DataFrame, sehingga notebook memakai angka
    hasil evaluasi nyata alih-alih angka yang ditulis manual.

    with SubtaskMetricCapture(logger) as cap:
        res = pair_eval(..., eval_type='test')
    df = cap.to_frame()
    """

    _HEAD = re.compile(r"\*{5}\s*(.+?)\s*results\s*\*{5}")
    _METRIC = re.compile(r"^\s*(precision|recall|micro-F1)\s*=\s*([0-9.]+)%?\s*$")
    # pair_eval juga me-log blok "***** Test results *****" / "***** Eval results *****"
    # untuk metrik quadruple keseluruhan. Blok itu bukan sub-task, jadi diabaikan
    # agar tidak muncul sebagai baris tambahan di tabel sub-task.
    _BUKAN_SUBTASK = {"test", "eval"}

    def __init__(self, logger, level=None):
        import logging as _logging
        self._logging = _logging
        self.logger = logger
        self.level = level if level is not None else _logging.INFO
        self.records = {}
        self._current = None
        self._handler = None
        self._prev_level = None

    def __enter__(self):
        outer = self

        class _H(self._logging.Handler):
            def emit(self, record):
                try:
                    outer._consume(record.getMessage())
                except Exception:
                    pass

        self._handler = _H()
        self._handler.setLevel(self.level)
        self._prev_level = self.logger.level
        self.logger.setLevel(self.level)
        self.logger.addHandler(self._handler)
        return self

    def __exit__(self, *exc):
        if self._handler is not None:
            self.logger.removeHandler(self._handler)
        if self._prev_level is not None:
            self.logger.setLevel(self._prev_level)
        return False

    def _consume(self, msg):
        head = self._HEAD.search(msg)
        if head:
            name = head.group(1).strip()
            if name.lower() in self._BUKAN_SUBTASK:
                self._current = None
            else:
                self._current = name
                self.records.setdefault(name, {})
            return
        m = self._METRIC.match(msg)
        if m and self._current:
            key, raw = m.group(1), float(m.group(2))
            # pair_eval memakai format {:.2%} sehingga nilainya sudah dalam persen.
            self.records[self._current][key] = raw / 100.0 if "%" in msg else raw

    def to_dict(self):
        return {k: v for k, v in self.records.items() if v}

    def to_frame(self):
        rows = []
        for name, m in self.to_dict().items():
            rows.append({
                "Subtask": name,
                "N_Elements": len(name.split()),
                "Precision": m.get("precision", float("nan")),
                "Recall": m.get("recall", float("nan")),
                "Micro_F1": m.get("micro-F1", float("nan")),
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(["N_Elements", "Micro_F1"], ascending=[True, False]).reset_index(drop=True)
        return df


def plot_subtask_metrics(df_subtasks, output_plot_path, title="Metrik per Sub-Task (Micro-F1 %)"):
    """
    Bar chart horizontal Micro-F1 untuk DataFrame keluaran SubtaskMetricCapture.to_frame().
    """
    if df_subtasks is None or df_subtasks.empty:
        print("[plot] DataFrame sub-task kosong, plot dilewati.")
        return None
    d = df_subtasks.dropna(subset=["Micro_F1"]).sort_values("Micro_F1")
    plt.figure(figsize=(11, max(4, 0.42 * len(d))))
    colors = plt.cm.viridis(np.linspace(0.15, 0.9, len(d)))
    bars = plt.barh(d["Subtask"], d["Micro_F1"] * 100, color=colors, edgecolor="black", alpha=0.88)
    for bar in bars:
        plt.text(bar.get_width() + 0.6, bar.get_y() + bar.get_height() / 2,
                 f"{bar.get_width():.2f}%", va="center", ha="left", fontsize=8, fontweight="bold")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.xlabel("Micro-F1 (%)")
    plt.xlim(0, 105)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_plot_path) or ".", exist_ok=True)
    plt.savefig(output_plot_path, dpi=300)
    plt.show()
    print(f"[plot] Disimpan: {output_plot_path}")
    return output_plot_path


# ---------------------------------------------------------------------------
# Lapis kompatibilitas ke run_classifier_dataset_utils.py
#
# Notebook sebelumnya memanggil nama fungsi/metode yang tidak ada di repo
# (get_test_examples, get_test_1st_examples, convert_examples_to_features_categorysenti)
# dan mengirim kwarg `domain_type=` yang tidak diterima signature aslinya.
# Wrapper di bawah memetakan pemanggilan itu ke API asli tanpa mengubah
# Extract-Classify-ACOS/run_classifier_dataset_utils.py.
# ---------------------------------------------------------------------------

def features_step1(examples, label_list, max_seq_length, tokenizer, output_mode="classification",
                   task_name="quad", **ignored):
    """Wrapper untuk convert_examples_to_features (step 1). Kwarg tambahan diabaikan."""
    from run_classifier_dataset_utils import convert_examples_to_features
    return convert_examples_to_features(examples, label_list, max_seq_length,
                                        tokenizer, output_mode, task_name)


def features_step2(examples, label_list, max_seq_length, tokenizer, output_mode="classification",
                   *ignored_args, **ignored_kwargs):
    """Wrapper untuk convert_examples_to_features2nd (step 2). Kwarg tambahan diabaikan."""
    from run_classifier_dataset_utils import convert_examples_to_features2nd
    return convert_examples_to_features2nd(examples, label_list, max_seq_length,
                                           tokenizer, output_mode)


def pair_examples_from_file(processor, pair_file, set_type="test"):
    """
    Membuat InputExample2nd dari file pair apa pun (`*_test_pair.tsv` atau
    `*_test_pair_1st.tsv`). CategorySentiProcessor hanya punya jalur tetap
    train_pair / dev_pair / test_pair_1st, sehingga pembacaan file eksplisit
    diperlukan agar notebook bisa memilih sumber evaluasi.
    """
    lines = processor._read_tsv(pair_file)
    return processor._create_examples(lines, set_type)


def resolve_eval_pair_file(tokenized_dir, domain, prefer_1st=True):
    """
    Menentukan file pair untuk evaluasi step 2 dan melaporkan pilihannya.
    Mengembalikan (path, is_1st).
    """
    p1 = os.path.join(tokenized_dir, f"{domain}_test_pair_1st.tsv")
    p0 = os.path.join(tokenized_dir, f"{domain}_test_pair.tsv")
    if prefer_1st and os.path.exists(p1):
        print(f"[data] Evaluasi memakai pasangan prediksi step 1: {p1}")
        return p1, True
    if os.path.exists(p0):
        print(f"[data] Pasangan prediksi step 1 tidak dipakai. Memakai pasangan gold: {p0}")
        print("       Catatan: angka yang dihasilkan BUKAN skor pipeline penuh.")
        return p0, False
    raise FileNotFoundError(f"Tidak menemukan {p1} maupun {p0}")


def unpack_model_output(out):
    """
    BertForQuadABSA dan CategorySentiClassification sama-sama mengembalikan
    ([loss], [logits...]). Helper ini mengambil skalar loss dan daftar logits
    supaya loop training tidak memanggil .backward() pada sebuah list.
    """
    losses, logits = out
    loss = losses[0] if isinstance(losses, (list, tuple)) else losses
    return loss, logits
