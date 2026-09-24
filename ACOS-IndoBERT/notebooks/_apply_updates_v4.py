import json
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Loaded notebook with {len(nb['cells'])} cells.")

# ==============================================================================
# 1. UPDATE CELL 2: Google Drive Mounting & Dependency Installation
# ==============================================================================
cell2_code = '''# 1. Mount Google Drive jika di Colab & siapkan mekanisme backup otomatis
GDRIVE_MOUNTED = False
GDRIVE_BACKUP_DIR = None

try:
    from google.colab import drive
    drive.mount('/content/drive')
    GDRIVE_MOUNTED = True
    GDRIVE_BACKUP_DIR = "/content/drive/MyDrive/ACOS_BACKUP"
    os.makedirs(GDRIVE_BACKUP_DIR, exist_ok=True)
    print(f"✅ Google Drive berhasil di-mount pada /content/drive (Backup dir: {GDRIVE_BACKUP_DIR})")
except Exception:
    print("💻 Berjalan pada lingkungan Lokal / Colab tanpa drive mount.")

def sync_to_gdrive(source_path, target_subpath=""):
    """Menyalin file atau direktori artefak ke Google Drive secara otomatis."""
    if not GDRIVE_MOUNTED or not GDRIVE_BACKUP_DIR:
        return False
    try:
        import shutil
        dest_dir = os.path.join(GDRIVE_BACKUP_DIR, target_subpath) if target_subpath else GDRIVE_BACKUP_DIR
        os.makedirs(dest_dir, exist_ok=True)
        if os.path.isdir(source_path):
            dest_path = os.path.join(dest_dir, os.path.basename(source_path))
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path, ignore_errors=True)
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_dir)
        return True
    except Exception as _e_sync:
        print(f"⚠️ Gagal sync ke Google Drive: {_e_sync}")
        return False

# 2. Instalasi dependensi yang dibutuhkan (termasuk openpyxl & tabulate untuk ekspor Excel & Markdown)
!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm openpyxl tabulate
'''

nb['cells'][2]['source'] = [l + "\n" for l in cell2_code.strip().split("\n")]
print("[OK] Cell 2 updated with Google Drive mount, sync_to_gdrive, and openpyxl/tabulate install.")

# ==============================================================================
# 2. UPDATE CELL 4: GPU Hardware Diagnostics & Optimization + Benchmark Info
# ==============================================================================
cell4_code = '''# 3. GPU Hardware Diagnostics, ROCm/CUDA Detection & Profiling
import platform

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\\n⚡ Perangkat Komputasi Utama: {device}")

# Deteksi platform ROCm (AMD Instinct) vs CUDA (NVIDIA)
is_rocm = hasattr(torch.version, 'hip') and torch.version.hip is not None
is_cuda = torch.cuda.is_available() and not is_rocm

gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
total_vram_gb = 0.0
cuda_cap_str = "N/A"
cudnn_version_str = "N/A"

if torch.cuda.is_available():
    total_vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
    try:
        cuda_cap = torch.cuda.get_device_capability(0)
        cuda_cap_str = f"{cuda_cap[0]}.{cuda_cap[1]}"
    except Exception:
        cuda_cap_str = "ROCm/HIP Target"
    try:
        cudnn_ver = torch.backends.cudnn.version()
        cudnn_version_str = str(cudnn_ver) if cudnn_ver is not None else "MIOpen (ROCm)"
    except Exception:
        cudnn_version_str = "MIOpen (ROCm)"

# Kriteria Large GPU: VRAM >= 16 GB atau GPU kelas enterprise/akselerator besar
is_large_gpu = total_vram_gb >= 16.0 or any(
    k in gpu_name.upper() for k in ["MI300", "MI250", "A100", "H100", "V100", "L40", "RTX 4090", "RTX 3090", "A6000"]
)

# Aktifkan optimasi benchmark cuDNN jika NVIDIA CUDA
if is_cuda:
    try:
        torch.backends.cudnn.benchmark = True
    except Exception:
        pass
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Simpan metadata profil hardware ke global dictionary
GPU_BENCHMARK_INFO = {
    "device": str(device),
    "gpu_name": gpu_name,
    "total_vram_gb": total_vram_gb,
    "is_large_gpu": is_large_gpu,
    "platform_type": "AMD ROCm HIP" if is_rocm else ("NVIDIA CUDA" if is_cuda else "CPU"),
    "rocm_hip_version": str(torch.version.hip) if is_rocm else None,
    "cuda_version": str(torch.version.cuda) if hasattr(torch.version, 'cuda') and torch.version.cuda else None,
    "compute_capability": cuda_cap_str,
    "cudnn_miopen_version": cudnn_version_str,
    "pytorch_version": torch.__version__,
    "os_platform": f"{platform.system()} {platform.release()}",
    "python_version": platform.python_version()
}

print("=" * 60)
print("🖥️  SPESIFIKASI HARDWARE & AKSESIBILITAS GPU:")
print(f"   Model GPU         : {gpu_name}")
print(f"   Total VRAM        : {total_vram_gb:.2f} GB")
print(f"   Akselerator       : {GPU_BENCHMARK_INFO['platform_type']}")
if is_rocm:
    print(f"   ROCm HIP Build    : {torch.version.hip}")
elif is_cuda:
    print(f"   CUDA Version      : {torch.version.cuda}")
    print(f"   Compute Cap       : {cuda_cap_str}")
print(f"   Large GPU Class   : {'🚀 YA (Enterprise / High-VRAM Accelerator)' if is_large_gpu else 'Standard GPU / CPU'}")
print(f"   PyTorch Version   : {torch.__version__}")
print("=" * 60)
'''

nb['cells'][4]['source'] = [l + "\n" for l in cell4_code.strip().split("\n")]
print("[OK] Cell 4 updated with ROCm/CUDA detection and GPU_BENCHMARK_INFO.")

# ==============================================================================
# 3. UPDATE CELL 6: Add ExecutionTracker Class
# ==============================================================================
# Append ExecutionTracker to cell 6
src6 = "".join(nb['cells'][6]['source'])
tracker_code = '''

# ==============================================================================
# Pelacak Waktu Eksekusi, Penanda Waktu Penyimpanan & Ekspor CSV/Excel/Markdown
# ==============================================================================
class ExecutionTracker:
    """Melacak durasi eksekusi per epoch, penanda waktu penyimpanan checkpoint,
    serta mengekspor rekap performa ke CSV, Excel (.xlsx), dan Markdown (.md).
    """

    def __init__(self, gpu_info=None):
        self.gpu_info = gpu_info or globals().get("GPU_BENCHMARK_INFO", {})
        self.epoch_records = []
        self.checkpoint_records = []

    def record_epoch(self, step_name, epoch, duration_sec, train_loss,
                     precision=None, recall=None, f1=None,
                     peak_vram_mb=None, checkpoint_saved=False,
                     save_duration_sec=0.0, save_path=None):
        from datetime import datetime
        now_ts = datetime.now()
        rec = {
            "Step": step_name,
            "Epoch": int(epoch),
            "Timestamp": now_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration_Sec": round(float(duration_sec), 2),
            "Duration_Formatted": f"{int(duration_sec // 60)}m {duration_sec % 60:04.1f}s",
            "Train_Loss": round(float(train_loss), 4) if train_loss is not None else None,
            "Precision_%": round(float(precision) * 100, 2) if precision is not None else None,
            "Recall_%": round(float(recall) * 100, 2) if recall is not None else None,
            "Micro_F1_%": round(float(f1) * 100, 2) if f1 is not None else None,
            "Peak_VRAM_MB": round(float(peak_vram_mb), 2) if peak_vram_mb is not None else None,
            "Checkpoint_Saved": bool(checkpoint_saved),
            "Save_Duration_Sec": round(float(save_duration_sec), 3) if checkpoint_saved else 0.0,
            "Save_Path": str(save_path) if checkpoint_saved and save_path else "-",
            "GPU_Name": self.gpu_info.get("gpu_name", "Unknown"),
            "Total_VRAM_GB": self.gpu_info.get("total_vram_gb", 0.0),
            "Is_Large_GPU": self.gpu_info.get("is_large_gpu", False)
        }
        self.epoch_records.append(rec)
        if checkpoint_saved:
            self.checkpoint_records.append({
                "Step": step_name,
                "Epoch": int(epoch),
                "Timestamp": now_ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Micro_F1_%": round(float(f1) * 100, 2) if f1 is not None else None,
                "Save_Duration_Sec": round(float(save_duration_sec), 3),
                "Save_Path": str(save_path),
                "GPU_Name": self.gpu_info.get("gpu_name", "Unknown"),
                "Total_VRAM_GB": self.gpu_info.get("total_vram_gb", 0.0)
            })
        return rec

    def to_dataframe(self):
        return pd.DataFrame(self.epoch_records)

    def export_summary(self, output_dir, session_name="ACOS_Session", gdrive_sync=True):
        os.makedirs(output_dir, exist_ok=True)
        df_records = self.to_dataframe()
        df_saves = pd.DataFrame(self.checkpoint_records)
        df_gpu = pd.DataFrame([self.gpu_info])

        csv_file = os.path.join(output_dir, f"{session_name}_execution_time.csv")
        excel_file = os.path.join(output_dir, f"{session_name}_execution_report.xlsx")
        md_file = os.path.join(output_dir, f"{session_name}_execution_report.md")

        # 1. Ekspor CSV
        df_records.to_csv(csv_file, index=False, encoding="utf-8")

        # 2. Ekspor Excel (.xlsx) dengan tab terpisah
        try:
            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                df_records.to_excel(writer, sheet_name="Epoch_Execution_Time", index=False)
                df_gpu.to_excel(writer, sheet_name="GPU_Hardware_Profile", index=False)
                if not df_saves.empty:
                    df_saves.to_excel(writer, sheet_name="Checkpoint_Saves", index=False)
        except Exception as _e_xl:
            print(f"⚠️ Gagal export file Excel: {_e_xl}")

        # 3. Ekspor Markdown (.md)
        md_content = self.generate_markdown(session_name)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 4. Sinkronisasi otomatis ke Google Drive
        if gdrive_sync and "sync_to_gdrive" in globals():
            sync_to_gdrive(csv_file, "reports")
            sync_to_gdrive(excel_file, "reports")
            sync_to_gdrive(md_file, "reports")

        return {"csv": csv_file, "excel": excel_file, "md": md_file}

    def generate_markdown(self, session_name="ACOS_Session"):
        lines = []
        lines.append(f"# ⏱️ Ringkasan Waktu Eksekusi & Profil GPU: {session_name}")
        lines.append(f"\\n> Diekspor otomatis pada: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\\n")

        # Profil Hardware
        lines.append("## 🖥️ 1. Detail Hardware & Akselerator GPU")
        lines.append("| Parameter | Nilai |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **GPU Model** | {self.gpu_info.get('gpu_name', 'N/A')} |")
        lines.append(f"| **Total VRAM** | {self.gpu_info.get('total_vram_gb', '0')} GB |")
        lines.append(f"| **Tipe Akselerator** | {self.gpu_info.get('platform_type', 'N/A')} |")
        lines.append(f"| **Kategori Akselerator** | {'🚀 High-End / Large GPU' if self.gpu_info.get('is_large_gpu') else 'Standard GPU / CPU'} |")
        lines.append(f"| **Compute Cap / HIP** | {self.gpu_info.get('rocm_hip_version') or self.gpu_info.get('compute_capability', 'N/A')} |")
        lines.append(f"| **PyTorch Version** | {self.gpu_info.get('pytorch_version', 'N/A')} |")
        lines.append(f"| **Sistem Operasi** | {self.gpu_info.get('os_platform', 'N/A')} |\\n")

        # Rincian Epoch
        df = self.to_dataframe()
        if not df.empty:
            lines.append("## 📈 2. Detail Waktu Eksekusi Per-Epoch")
            cols_show = ["Step", "Epoch", "Duration_Formatted", "Train_Loss", "Precision_%", "Recall_%", "Micro_F1_%", "Peak_VRAM_MB", "Checkpoint_Saved", "Save_Duration_Sec"]
            cols_avail = [c for c in cols_show if c in df.columns]
            lines.append("| " + " | ".join(cols_avail) + " |")
            lines.append("| " + " | ".join([":---:" if c in ["Epoch", "Checkpoint_Saved"] else (":---" if c == "Step" else "---:") for c in cols_avail]) + " |")
            for _, r in df[cols_avail].iterrows():
                row_vals = []
                for c in cols_avail:
                    v = r[c]
                    if pd.isna(v):
                        row_vals.append("-")
                    elif c == "Checkpoint_Saved":
                        row_vals.append("✅ YA" if v else "-")
                    elif c == "Save_Duration_Sec":
                        row_vals.append(f"{v:.3f}s" if v > 0 else "-")
                    else:
                        row_vals.append(str(v))
                lines.append("| " + " | ".join(row_vals) + " |")
            lines.append("")

            # Total Durasi
            tot_sec = df["Duration_Sec"].sum()
            tot_min = tot_sec / 60.0
            lines.append(f"**Total Durasi Eksekusi Training:** `{int(tot_sec // 3600)}j {int((tot_sec % 3600) // 60)}m {tot_sec % 60:.1f}s` ({tot_min:.2f} menit)\\n")

        # Riwayat Checkpoint Saves
        if self.checkpoint_records:
            lines.append("## 💾 3. Penanda Waktu & Durasi Penyimpanan Checkpoint")
            lines.append("| Step | Epoch | Waktu Tersimpan | Micro-F1 (%) | Durasi Simpan (s) | Path Simpan |")
            lines.append("| :--- | :---: | :---: | ---: | ---: | :--- |")
            for cs in self.checkpoint_records:
                lines.append(f"| {cs['Step']} | {cs['Epoch']} | `{cs['Timestamp']}` | {cs['Micro_F1_%']}% | {cs['Save_Duration_Sec']:.3f}s | `{cs['Save_Path']}` |")
            lines.append("")

        return "\\n".join(lines)


# Inisialisasi instance global ExecutionTracker
execution_tracker = ExecutionTracker(gpu_info=globals().get("GPU_BENCHMARK_INFO", {}))
print("⏱️  ExecutionTracker siap mencatat durasi eksekusi per-epoch & waktu penyimpanan checkpoint.")
'''

if "class ExecutionTracker" not in src6:
    nb['cells'][6]['source'] = [l + "\n" for l in (src6 + tracker_code).strip().split("\n")]
    print("[OK] Cell 6 updated with ExecutionTracker class and global instance.")
else:
    print("[SKIP] ExecutionTracker already present in Cell 6.")

# Save intermediate notebook
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Saved notebook checkpoint 1.")
