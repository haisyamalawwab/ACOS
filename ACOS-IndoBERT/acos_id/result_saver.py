"""ResultSaver — Menyimpan semua output setiap step secara terorganisasi.

Struktur folder yang dihasilkan per run:

    <run_dir>/
    ├── run_config.json             konfigurasi eksperimen ini
    ├── run_result.json             ringkasan akhir metrik
    ├── hardware_log.json           log hardware per epoch
    ├── session_manifest.json       manifest sesi (dari acos_id.session)
    │
    ├── step1/                      hasil Step 1 (co-extraction)
    │   ├── training_log.csv        log per epoch: loss, F1, VRAM, waktu
    │   ├── eval_per_epoch.csv      TP, FP, FN, Precision, Recall, F1 per epoch
    │   ├── best_metrics.json       metrik terbaik & epoch
    │   ├── classification_report.txt  laporan evaluasi teks
    │   ├── plots/
    │   │   ├── 01_loss_curve.png       kurva loss per epoch
    │   │   ├── 02_f1_curve.png         kurva F1 per epoch
    │   │   ├── 03_vram_usage.png       VRAM per epoch
    │   │   ├── 04_speed_curve.png      samples/sec per epoch
    │   │   └── 05_combined_dashboard.png  dashboard 2x2
    │   └── checkpoints/
    │       └── step1_best/         checkpoint model terbaik
    │
    ├── step2/                      hasil Step 2 (category-sentiment)
    │   ├── training_log.csv
    │   ├── eval_per_epoch.csv
    │   ├── best_metrics.json
    │   ├── confusion_matrix.png    confusion matrix kategori
    │   ├── plots/
    │   └── checkpoints/
    │
    ├── inference/                  hasil inferensi test set
    │   ├── predictions.tsv         prediksi lengkap test set
    │   ├── sample_predictions.json  10 contoh prediksi
    │   └── inference_summary.json  ringkasan akurasi inferensi
    │
    └── reports/                    laporan akhir
        ├── REPORT_INDEX.md         indeks semua artefak
        ├── full_report.md          laporan narasi lengkap
        └── final_comparison.csv    perbandingan antar run (jika ada)
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Matplotlib diimpor lazy agar modul tetap bisa diimpor tanpa GUI
_PLT_AVAILABLE = None


def _get_plt():
    global _PLT_AVAILABLE
    if _PLT_AVAILABLE is None:
        try:
            import matplotlib
            matplotlib.use("Agg")          # non-interactive backend
            import matplotlib.pyplot as plt
            _PLT_AVAILABLE = plt
        except ImportError:
            _PLT_AVAILABLE = False
    return _PLT_AVAILABLE if _PLT_AVAILABLE is not False else None


# ─── Konstanta subfolder ──────────────────────────────────────────────────────

STEP_DIRS = {
    "step1": ("training_log.csv", "eval_per_epoch.csv",
               "best_metrics.json", "classification_report.txt",
               "plots", "checkpoints"),
    "step2": ("training_log.csv", "eval_per_epoch.csv",
               "best_metrics.json", "confusion_matrix.png",
               "plots", "checkpoints"),
}

TOP_DIRS = ("step1", "step2", "inference", "reports")


# ─── Kelas utama ──────────────────────────────────────────────────────────────

class ResultSaver:
    """Menyimpan semua hasil per-step secara terstruktur dan otomatis.

    Penggunaan minimal::

        saver = ResultSaver(run_dir="results/experiments/run_1")
        saver.init(config={"epochs": 50, "batch_size": 96})

        # Per epoch Step 1:
        saver.log_epoch_step1(
            epoch=1, loss=2.14, f1=94.86,
            tp=16106, fp=1079, fn=667,
            vram_gb=5.3, duration_sec=142.0, samples_per_sec=422.0,
        )

        # Setelah Step 1 selesai:
        saver.finalize_step1(best_epoch=3, best_f1=97.19)
        saver.save_step1_plots()

        # Simpan prediksi test set:
        saver.save_predictions(predictions, split="test")

        # Laporan akhir:
        saver.write_final_report()
    """

    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self._dirs: Dict[str, str] = {}
        self._step1_log: List[dict] = []
        self._step2_log: List[dict] = []
        self._config: dict = {}
        self._step1_best: dict = {}
        self._step2_best: dict = {}
        self._inference_summary: dict = {}
        self._init_time = datetime.now()

    # ─── Inisialisasi ─────────────────────────────────────────────────────────

    def init(self, config: dict = None) -> Dict[str, str]:
        """Buat semua subfolder dan simpan konfigurasi."""
        self._config = config or {}
        self._dirs = self._make_dirs()
        self._save_json("run_config.json", {
            "run_dir": self.run_dir,
            "initialized_at": self._init_time.isoformat(),
            "config": self._config,
        })
        print(f"  [ResultSaver] Folder output: {self.run_dir}")
        return self._dirs

    def _make_dirs(self) -> Dict[str, str]:
        dirs = {"root": self.run_dir}
        for top in TOP_DIRS:
            top_path = os.path.join(self.run_dir, top)
            os.makedirs(top_path, exist_ok=True)
            dirs[top] = top_path
        # Plot subfolder per step
        for step in ("step1", "step2"):
            plots_path = os.path.join(self.run_dir, step, "plots")
            ckpt_path  = os.path.join(self.run_dir, step, "checkpoints")
            os.makedirs(plots_path, exist_ok=True)
            os.makedirs(ckpt_path, exist_ok=True)
            dirs[f"{step}_plots"]       = plots_path
            dirs[f"{step}_checkpoints"] = ckpt_path
        os.makedirs(os.path.join(self.run_dir, "reports"), exist_ok=True)
        return dirs

    # ─── Step 1 — per epoch ───────────────────────────────────────────────────

    def log_epoch_step1(
        self, *,
        epoch: int,
        loss: float,
        f1: float,
        tp: int = 0, fp: int = 0, fn: int = 0,
        vram_gb: float = 0.0,
        vram_pct: float = 0.0,
        duration_sec: float = 0.0,
        samples_per_sec: float = 0.0,
        is_best: bool = False,
        extra: dict = None,
    ):
        """Catat 1 epoch Step 1. Langsung append ke CSV dan list memori."""
        prec = tp / (tp + fp + 1e-9) * 100
        rec  = tp / (tp + fn + 1e-9) * 100
        row = {
            "epoch": epoch,
            "loss": round(loss, 6),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn,
            "vram_gb": round(vram_gb, 3),
            "vram_pct": round(vram_pct, 2),
            "duration_sec": round(duration_sec, 2),
            "samples_per_sec": round(samples_per_sec, 1),
            "is_best": is_best,
            "timestamp": datetime.now().isoformat(),
            **(extra or {}),
        }
        self._step1_log.append(row)
        self._append_csv("step1/training_log.csv", row)
        self._append_csv("step1/eval_per_epoch.csv", {
            k: row[k] for k in
            ("epoch", "tp", "fp", "fn", "precision", "recall", "f1", "is_best")
        })

    def finalize_step1(self, best_epoch: int, best_f1: float,
                       classification_report_text: str = ""):
        """Simpan ringkasan terbaik Step 1."""
        self._step1_best = {
            "best_epoch": best_epoch,
            "best_f1": round(best_f1, 4),
            "total_epochs": len(self._step1_log),
            "finalized_at": datetime.now().isoformat(),
        }
        self._save_json("step1/best_metrics.json", self._step1_best)
        if classification_report_text:
            self._save_text("step1/classification_report.txt",
                            classification_report_text)
        print(f"  [Step 1] Best F1={best_f1:.2f}% ep{best_epoch} "
              f"| {len(self._step1_log)} epoch tercatat")

    # ─── Step 2 — per epoch ───────────────────────────────────────────────────

    def log_epoch_step2(
        self, *,
        epoch: int,
        loss: float,
        f1: float,
        accuracy: float = 0.0,
        vram_gb: float = 0.0,
        vram_pct: float = 0.0,
        duration_sec: float = 0.0,
        samples_per_sec: float = 0.0,
        is_best: bool = False,
        per_label: dict = None,
        extra: dict = None,
    ):
        """Catat 1 epoch Step 2."""
        row = {
            "epoch": epoch,
            "loss": round(loss, 6),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
            "vram_gb": round(vram_gb, 3),
            "vram_pct": round(vram_pct, 2),
            "duration_sec": round(duration_sec, 2),
            "samples_per_sec": round(samples_per_sec, 1),
            "is_best": is_best,
            "timestamp": datetime.now().isoformat(),
            **(extra or {}),
        }
        self._step2_log.append(row)
        self._append_csv("step2/training_log.csv", row)

        if per_label:
            label_row = {"epoch": epoch, **per_label}
            self._append_csv("step2/eval_per_label.csv", label_row)

    def finalize_step2(self, best_epoch: int, best_f1: float,
                       classification_report_text: str = ""):
        self._step2_best = {
            "best_epoch": best_epoch,
            "best_f1": round(best_f1, 4),
            "total_epochs": len(self._step2_log),
            "finalized_at": datetime.now().isoformat(),
        }
        self._save_json("step2/best_metrics.json", self._step2_best)
        if classification_report_text:
            self._save_text("step2/classification_report.txt",
                            classification_report_text)
        print(f"  [Step 2] Best F1={best_f1:.2f}% ep{best_epoch} "
              f"| {len(self._step2_log)} epoch tercatat")

    # ─── Plots ────────────────────────────────────────────────────────────────

    def save_step1_plots(self) -> List[str]:
        """Buat dan simpan semua plot Step 1. Return list path file."""
        if not self._step1_log:
            return []
        plt = _get_plt()
        if plt is None:
            print("  [ResultSaver] matplotlib tidak tersedia — plot dilewati")
            return []

        paths = []
        log = self._step1_log
        epochs   = [r["epoch"] for r in log]
        losses   = [r["loss"] for r in log]
        f1s      = [r["f1"] for r in log]
        vrams    = [r["vram_gb"] for r in log]
        sps      = [r["samples_per_sec"] for r in log]
        best_ep  = self._step1_best.get("best_epoch", None)

        # 1. Loss curve
        p = self._plot_single(
            epochs, losses, "Epoch", "Loss",
            title=f"Step 1 — Training Loss\n{self._run_label()}",
            color="#e74c3c", marker="o",
            vline=best_ep, vline_label="Best epoch",
            save_path=os.path.join(self._dirs.get("step1_plots", ""), "01_loss_curve.png"),
        )
        paths.append(p)

        # 2. F1 curve
        p = self._plot_single(
            epochs, f1s, "Epoch", "Micro-F1 (%)",
            title=f"Step 1 — Micro-F1 Score\n{self._run_label()}",
            color="#27ae60", marker="s",
            vline=best_ep, vline_label=f"Best F1={self._step1_best.get('best_f1', 0):.2f}%",
            save_path=os.path.join(self._dirs.get("step1_plots", ""), "02_f1_curve.png"),
        )
        paths.append(p)

        # 3. VRAM usage
        p = self._plot_single(
            epochs, vrams, "Epoch", "VRAM Used (GB)",
            title=f"Step 1 — VRAM Usage\n{self._run_label()}",
            color="#8e44ad", marker="^",
            save_path=os.path.join(self._dirs.get("step1_plots", ""), "03_vram_usage.png"),
        )
        paths.append(p)

        # 4. Speed (samples/sec)
        p = self._plot_single(
            epochs, sps, "Epoch", "Samples / sec",
            title=f"Step 1 — Training Speed\n{self._run_label()}",
            color="#2980b9", marker="D",
            save_path=os.path.join(self._dirs.get("step1_plots", ""), "04_speed_curve.png"),
        )
        paths.append(p)

        # 5. Dashboard 2x2
        p = self._plot_dashboard_step1(
            epochs, losses, f1s, vrams, sps, best_ep,
            save_path=os.path.join(self._dirs.get("step1_plots", ""), "05_combined_dashboard.png"),
        )
        paths.append(p)

        print(f"  [Step 1 Plots] {len(paths)} gambar disimpan di: "
              f"{self._dirs.get('step1_plots', '')}")
        return [p for p in paths if p]

    def save_step2_plots(self) -> List[str]:
        """Buat dan simpan semua plot Step 2."""
        if not self._step2_log:
            return []
        plt = _get_plt()
        if plt is None:
            return []

        paths = []
        log = self._step2_log
        epochs = [r["epoch"] for r in log]
        losses = [r["loss"] for r in log]
        f1s    = [r["f1"] for r in log]
        vrams  = [r["vram_gb"] for r in log]
        best_ep = self._step2_best.get("best_epoch", None)

        p = self._plot_single(
            epochs, losses, "Epoch", "Loss",
            title=f"Step 2 — Training Loss\n{self._run_label()}",
            color="#e67e22", marker="o",
            vline=best_ep,
            save_path=os.path.join(self._dirs.get("step2_plots", ""), "01_loss_curve.png"),
        )
        paths.append(p)

        p = self._plot_single(
            epochs, f1s, "Epoch", "F1 (%)",
            title=f"Step 2 — F1 Score\n{self._run_label()}",
            color="#16a085", marker="s",
            vline=best_ep,
            vline_label=f"Best F1={self._step2_best.get('best_f1', 0):.2f}%",
            save_path=os.path.join(self._dirs.get("step2_plots", ""), "02_f1_curve.png"),
        )
        paths.append(p)

        p = self._plot_single(
            epochs, vrams, "Epoch", "VRAM Used (GB)",
            title=f"Step 2 — VRAM Usage\n{self._run_label()}",
            color="#8e44ad", marker="^",
            save_path=os.path.join(self._dirs.get("step2_plots", ""), "03_vram_usage.png"),
        )
        paths.append(p)

        print(f"  [Step 2 Plots] {len(paths)} gambar disimpan di: "
              f"{self._dirs.get('step2_plots', '')}")
        return [p for p in paths if p]

    # ─── Inferensi ────────────────────────────────────────────────────────────

    def save_predictions(
        self,
        predictions: list,
        split: str = "test",
        sample_n: int = 10,
    ):
        """Simpan prediksi model ke inference/."""
        inf_dir = self._dirs.get("inference", os.path.join(self.run_dir, "inference"))
        os.makedirs(inf_dir, exist_ok=True)

        # Full TSV
        tsv_path = os.path.join(inf_dir, f"{split}_predictions.tsv")
        with open(tsv_path, "w", encoding="utf-8", newline="\n") as fh:
            for pred in predictions:
                fh.write(str(pred) + "\n")

        # Sample JSON
        samples = predictions[:sample_n] if len(predictions) >= sample_n else predictions
        sample_path = os.path.join(inf_dir, f"{split}_sample_{sample_n}.json")
        with open(sample_path, "w", encoding="utf-8") as fh:
            json.dump({"split": split, "n_total": len(predictions),
                       "samples": [str(s) for s in samples]},
                      fh, indent=2, ensure_ascii=False, default=str)

        print(f"  [Inference] {len(predictions)} prediksi disimpan: {tsv_path}")

    def save_inference_summary(self, metrics: dict, split: str = "test"):
        """Simpan ringkasan metrik inferensi."""
        inf_dir = self._dirs.get("inference", os.path.join(self.run_dir, "inference"))
        path = os.path.join(inf_dir, f"{split}_inference_summary.json")
        data = {"split": split, "saved_at": datetime.now().isoformat(), **metrics}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        self._inference_summary = data

    # ─── Laporan akhir ────────────────────────────────────────────────────────

    def write_final_report(self, extra_info: dict = None) -> str:
        """Tulis laporan narasi lengkap dalam Markdown."""
        s1 = self._step1_best
        s2 = self._step2_best
        cfg = self._config
        now = datetime.now()
        dur_sec = (now - self._init_time).total_seconds()

        lines = [
            f"# Laporan Run: {cfg.get('run_id', os.path.basename(self.run_dir))}",
            f"",
            f"> **Selesai:** {now.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> **Durasi:** {_fmt_dur(dur_sec)}  ",
            f"> **Folder:** `{self.run_dir}`",
            f"",
            f"---",
            f"",
            f"## Konfigurasi",
            f"",
            f"| Parameter | Nilai |",
            f"|-----------|-------|",
        ]
        for k, v in cfg.items():
            lines.append(f"| `{k}` | {v} |")

        lines += [
            f"",
            f"---",
            f"",
            f"## Hasil Step 1 — Aspect & Opinion Co-Extraction (BERT-CRF)",
            f"",
            f"| Metrik | Nilai |",
            f"|--------|-------|",
            f"| Best Epoch | {s1.get('best_epoch', '?')} dari {s1.get('total_epochs', '?')} |",
            f"| Best Micro-F1 | **{s1.get('best_f1', 0):.4f}%** |",
            f"",
        ]

        # Tabel training Step 1
        if self._step1_log:
            lines += [
                f"### Log Training per Epoch",
                f"",
                f"| Epoch | Loss | F1% | Precision% | Recall% | VRAM (GB) | Dur | Best |",
                f"|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
            ]
            for r in self._step1_log:
                best_mark = "**BEST**" if r.get("is_best") else ""
                lines.append(
                    f"| {r['epoch']} | {r['loss']:.4f} | {r['f1']:.2f} "
                    f"| {r['precision']:.2f} | {r['recall']:.2f} "
                    f"| {r['vram_gb']:.2f} | {_fmt_dur(r['duration_sec'])} "
                    f"| {best_mark} |"
                )

        lines += [
            f"",
            f"---",
            f"",
            f"## Hasil Step 2 — Klasifikasi Category & Sentiment",
            f"",
            f"| Metrik | Nilai |",
            f"|--------|-------|",
            f"| Best Epoch | {s2.get('best_epoch', '?')} dari {s2.get('total_epochs', '?')} |",
            f"| Best F1 | **{s2.get('best_f1', 0):.4f}%** |",
            f"",
        ]

        if self._step2_log:
            lines += [
                f"### Log Training per Epoch",
                f"",
                f"| Epoch | Loss | F1% | Accuracy% | VRAM (GB) | Dur | Best |",
                f"|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
            ]
            for r in self._step2_log:
                best_mark = "**BEST**" if r.get("is_best") else ""
                lines.append(
                    f"| {r['epoch']} | {r['loss']:.4f} | {r['f1']:.2f} "
                    f"| {r.get('accuracy', 0):.2f} | {r['vram_gb']:.2f} "
                    f"| {_fmt_dur(r['duration_sec'])} | {best_mark} |"
                )

        if extra_info:
            lines += ["", "---", "", "## Info Tambahan", ""]
            for k, v in extra_info.items():
                lines.append(f"- **{k}**: {v}")

        # File artefak
        lines += [
            f"",
            f"---",
            f"",
            f"## Artefak yang Disimpan",
            f"",
            f"| Jenis | Path |",
            f"|-------|------|",
        ]
        for root, dirs, files in os.walk(self.run_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, self.run_dir)
                sz = os.path.getsize(fpath)
                if sz > 0:
                    ext = fname.split(".")[-1].lower()
                    ftype = {"png": "Gambar", "csv": "Tabel CSV",
                             "json": "JSON", "txt": "Teks",
                             "md": "Markdown", "bin": "Model Checkpoint",
                             "pkl": "State Pickle"}.get(ext, "File")
                    lines.append(f"| {ftype} | `{rel}` ({sz/1024:.1f} KB) |")

        report_text = "\n".join(lines)
        report_path = os.path.join(self._dirs.get("reports", self.run_dir), "full_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(report_text)

        # Update run_result.json
        result = {
            "run_id": cfg.get("run_id", ""),
            "completed_at": now.isoformat(),
            "duration_sec": round(dur_sec, 1),
            "step1": s1,
            "step2": s2,
            "inference": self._inference_summary,
            "config": cfg,
            "report_path": report_path,
        }
        self._save_json("run_result.json", result)

        # Index
        self._write_report_index()

        print(f"  [Report] Laporan disimpan: {report_path}")
        return report_path

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _save_json(self, rel_path: str, data: dict):
        path = os.path.join(self.run_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)

    def _save_text(self, rel_path: str, text: str):
        path = os.path.join(self.run_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def _append_csv(self, rel_path: str, row: dict):
        path = os.path.join(self.run_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_header = not os.path.exists(path)
        with open(path, "a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def _run_label(self) -> str:
        return self._config.get("run_id", os.path.basename(self.run_dir))

    def _write_report_index(self):
        """Tulis indeks semua file output ke reports/REPORT_INDEX.md."""
        lines = [
            f"# Indeks Artefak — {self._run_label()}",
            f"",
            f"> Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> Root  : `{self.run_dir}`",
            f"",
            f"| # | Jenis | File | Ukuran |",
            f"|---|-------|------|--------|",
        ]
        idx = 1
        for root, dirs, files in os.walk(self.run_dir):
            dirs.sort()
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, self.run_dir)
                sz = os.path.getsize(fpath)
                ext = fname.split(".")[-1].lower()
                ftype = {"png": "Gambar", "csv": "Tabel CSV",
                         "json": "JSON", "txt": "Teks",
                         "md": "Markdown", "bin": "Model",
                         "pkl": "State"}.get(ext, "File")
                lines.append(f"| {idx} | {ftype} | `{rel}` | {sz/1024:.1f} KB |")
                idx += 1

        rpt_dir = self._dirs.get("reports", os.path.join(self.run_dir, "reports"))
        os.makedirs(rpt_dir, exist_ok=True)
        idx_path = os.path.join(rpt_dir, "REPORT_INDEX.md")
        with open(idx_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    # ─── Plot helpers ─────────────────────────────────────────────────────────

    def _plot_single(
        self,
        x, y,
        xlabel: str, ylabel: str,
        title: str = "",
        color: str = "#2980b9",
        marker: str = "o",
        vline: Optional[int] = None,
        vline_label: str = "",
        save_path: str = "",
    ) -> str:
        plt = _get_plt()
        if plt is None or not save_path:
            return ""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x, y, color=color, marker=marker, linewidth=2, markersize=5)
        if vline is not None and vline in x:
            ax.axvline(x=vline, color="gray", linestyle="--", linewidth=1.2,
                       label=vline_label or f"ep {vline}")
            ax.legend(fontsize=9)
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=9)
        fig.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def _plot_dashboard_step1(
        self,
        epochs, losses, f1s, vrams, sps,
        best_ep: Optional[int],
        save_path: str,
    ) -> str:
        plt = _get_plt()
        if plt is None:
            return ""
        fig, axes = plt.subplots(2, 2, figsize=(14, 8))
        fig.suptitle(f"Dashboard Step 1 — {self._run_label()}", fontsize=13)

        def _vline(ax):
            if best_ep and best_ep in epochs:
                ax.axvline(x=best_ep, color="gray", linestyle="--", lw=1.2,
                           label=f"Best ep={best_ep}")
                ax.legend(fontsize=8)

        ax = axes[0, 0]
        ax.plot(epochs, losses, color="#e74c3c", marker="o", ms=4, lw=2)
        _vline(ax)
        ax.set_title("Training Loss"); ax.set_xlabel("Epoch"); ax.set_ylabel("Loss")
        ax.grid(True, alpha=0.3)

        ax = axes[0, 1]
        ax.plot(epochs, f1s, color="#27ae60", marker="s", ms=4, lw=2)
        _vline(ax)
        best_f1 = self._step1_best.get("best_f1", 0)
        ax.set_title(f"Micro-F1 (best={best_f1:.2f}%)")
        ax.set_xlabel("Epoch"); ax.set_ylabel("F1 (%)")
        ax.grid(True, alpha=0.3)

        ax = axes[1, 0]
        ax.plot(epochs, vrams, color="#8e44ad", marker="^", ms=4, lw=2)
        ax.set_title("VRAM Usage"); ax.set_xlabel("Epoch"); ax.set_ylabel("GB")
        ax.grid(True, alpha=0.3)

        ax = axes[1, 1]
        ax.plot(epochs, sps, color="#2980b9", marker="D", ms=4, lw=2)
        ax.set_title("Training Speed"); ax.set_xlabel("Epoch"); ax.set_ylabel("Samples/sec")
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path


# ─── Utilitas ─────────────────────────────────────────────────────────────────

def _fmt_dur(sec: float) -> str:
    if sec < 60:
        return f"{sec:.1f}s"
    m, s = divmod(int(sec), 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m"


def merge_experiment_results(experiments_dir: str) -> str:
    """Baca semua run_result.json dan buat tabel perbandingan CSV + MD.

    Harus dipanggil setelah semua run selesai untuk membuat perbandingan
    lintas run.
    """
    import glob
    result_files = sorted(
        glob.glob(os.path.join(experiments_dir, "*", "run_result.json")))

    rows = []
    for path in result_files:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            cfg = data.get("config", {})
            s1  = data.get("step1", {})
            s2  = data.get("step2", {})
            rows.append({
                "run_id"       : data.get("run_id", "?"),
                "type"         : cfg.get("type", "?"),
                "epochs"       : cfg.get("epochs", "?"),
                "train_ratio"  : cfg.get("train_ratio", "?"),
                "n_splits"     : cfg.get("n_splits", "?"),
                "fold_idx"     : cfg.get("fold_idx", "?"),
                "step1_best_ep": s1.get("best_epoch", "?"),
                "step1_best_f1": s1.get("best_f1", 0),
                "step2_best_ep": s2.get("best_epoch", "?"),
                "step2_best_f1": s2.get("best_f1", 0),
                "duration_sec" : data.get("duration_sec", 0),
            })
        except Exception as e:
            print(f"  Gagal baca {path}: {e}")

    if not rows:
        print("Tidak ada run_result.json ditemukan.")
        return ""

    # CSV
    csv_path = os.path.join(experiments_dir, "final_comparison.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Markdown
    rows_sorted = sorted(rows, key=lambda r: r.get("step1_best_f1", 0), reverse=True)
    md_lines = [
        "# Perbandingan Semua Run Eksperimen",
        "",
        f"> Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Total run: {len(rows)}",
        "",
        "| # | Run ID | Type | Epochs | Split | S1 Best Ep | **S1 F1%** | S2 F1% | Dur |",
        "|---|--------|------|--------|-------|-----------|-----------|--------|-----|",
    ]
    for rank, r in enumerate(rows_sorted, 1):
        split_str = (f"{int(float(r['train_ratio'])*100)}%" if r['train_ratio'] not in ('?', None, '')
                     else f"cv{r['n_splits']}-f{r['fold_idx']}")
        md_lines.append(
            f"| {rank} | {r['run_id']} | {r['type']} | {r['epochs']} "
            f"| {split_str} | {r['step1_best_ep']} | **{r['step1_best_f1']:.2f}** "
            f"| {r['step2_best_f1']:.2f} | {_fmt_dur(r['duration_sec'])} |"
        )

    md_path = os.path.join(experiments_dir, "final_comparison.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines) + "\n")

    print(f"Perbandingan disimpan:")
    print(f"  CSV: {csv_path}")
    print(f"  MD : {md_path}")
    return md_path
