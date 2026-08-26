# coding=utf-8
"""
Utility module for ACOS (Aspect-Category-Opinion-Sentiment) Quadruple Extraction.
Provides automated timestamped session directory management, model checkpoint persistence,
publication-quality visualizations (Matplotlib/Seaborn), CSV tabular exports, and live inference helper.
"""

import os
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
