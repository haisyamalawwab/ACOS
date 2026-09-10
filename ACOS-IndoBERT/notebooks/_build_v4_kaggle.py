"""Membangun notebook 00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb untuk Kaggle.

Skrip ini mengambil notebook V4 Colab (yang sudah memiliki fitur Dual-Head Step 2,
IndoBERT fine-tuning, dan resume per-epoch), lalu mengadaptasikannya untuk
lingkungan Kaggle:
  1. Deteksi platform Kaggle (`/kaggle/working`, `/kaggle/input`)
  2. Nonaktifkan drive.mount Colab saat di Kaggle
  3. Auto-clone repositori GitHub jika folder proyek belum ada di Kaggle working dir
  4. Penambahan path search roots untuk checkpoint dan artefak di Kaggle
  5. Pengemasan otomatis zip artefak di akhir sesi agar mudah di-download dari tab Output Kaggle

Hasil disimpan di dua lokasi:
  - kaggle/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb (workspace kaggle)
  - ACOS-IndoBERT/notebooks/00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb
"""

import copy
import hashlib
import io
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
INDO_ROOT = os.path.dirname(HERE)
ACOS_ROOT = os.path.dirname(INDO_ROOT)
KAGGLE_DIR = os.path.join(ACOS_ROOT, "kaggle")
os.makedirs(KAGGLE_DIR, exist_ok=True)

SRC_NB = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb")
DST_KAGGLE_DIR = os.path.join(KAGGLE_DIR, "00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb")
DST_NOTEBOOKS_DIR = os.path.join(HERE, "00_ACOS_Master_Pipeline_Kaggle_V4_INDOBERT.ipynb")


MD_TITLE_KAGGLE = """# 00. ACOS Master Pipeline: End-to-End Execution (Kaggle V4 INDOBERT Dual-Head Version)

**Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction with Implicit Aspects and Opinions on Kaggle**

This production-grade master notebook executes the **entire ACOS benchmark pipeline with 1-Click** on **Kaggle Notebooks** (with automatic GPU T4 x2 / P100 acceleration and output persistence at `/kaggle/working/`):

1. **Environment Setup & GPU Diagnostics:** Automatic Kaggle environment detection, dependency installation, and detailed GPU / VRAM inspection.
2. **Dynamic Path Architecture (Zero Hardcoded Paths):** Seamless execution on Kaggle `/kaggle/working/`, Google Colab `/content/`, or Local environments.
3. **Reproducible Seeding & Logging:** Centralized hyperparameter configuration with full determinism.
4. **Step 1: BERT+CRF Sequence Labeling:** Joint Extraction of Aspect & Opinion terms (with implicit `-1,-1` support).
5. **Step 2: Dual-Head Classifier:** Independent Aspect Category (13 classes, multi-label BCE) and Sentiment (3 classes, multi-class CE) classification with fused aspect-opinion span candidate representations.
6. **Unified Metric Benchmark & Audit:** Automated quadruple metric calculation (`pair_eval`), per-head metrics, publication-ready table exports, and loss curves.

> **Petunjuk Eksekusi di Kaggle:**  
> 1. Aktifkan **Accelerator**: Pilih **GPU T4 x2** atau **GPU P100** di panel kanan (*Settings* -> *Accelerator*).  
> 2. Aktifkan **Internet**: Pastikan status **Internet ON** di panel kanan (*Settings* -> *Internet*) untuk download dependensi & model pretrained IndoBERT.  
> 3. Pasang **Dataset Input**: Pastikan dataset Indonesia terpasang di panel input Kaggle (*Input* -> *Add Input*):  
>    - `/kaggle/input/datasets/rozanhaisyam/appsid-gplay`  
>    - `/kaggle/input/datasets/rozanhaisyam/appsid`  
>    (Pipeline akan otomatis mendeteksi dan menyinkronkan data ke `/kaggle/working/`).  
> 4. Seluruh output (model checkpoint, tabel CSV metrik, kurva loss PNG) akan otomatis tersimpan di `/kaggle/working/` dan dapat langsung di-download dari tab *Output*.
"""

CODE_SETUP_KAGGLE = """# 1. Deteksi Lingkungan (Kaggle vs Google Colab vs Lokal)
import os
import sys

IS_KAGGLE = os.path.exists("/kaggle")
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

if IS_KAGGLE:
    print("🦅 Berjalan pada lingkungan Kaggle (Working dir: /kaggle/working)")
elif IS_COLAB:
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Google Drive berhasil di-mount pada /content/drive")
    except Exception:
        print("💻 Berjalan pada Google Colab tanpa drive mount.")
else:
    print("💻 Berjalan pada lingkungan Lokal / Server Mandiri.")

# 2. Instalasi dependensi yang dibutuhkan
!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm
"""

CODE_PATH_KAGGLE = """# 1. Deteksi dinamis root direktori proyek (Kaggle vs Google Drive vs Colab vs Lokal)
IS_KAGGLE = os.path.exists("/kaggle")
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
HAS_DRIVE = os.path.exists("/content/drive/MyDrive")

# Prioritas pencarian folder ACOS
drive_candidates = []
if IS_KAGGLE:
    drive_candidates += [
        "/kaggle/working/ACOS",
        "/kaggle/working/ACOS-ASLI",
        "/kaggle/working",
        "/kaggle/input/acos-asli",
        "/kaggle/input/acos-indobert",
        "/kaggle/input/datasets/rozanhaisyam/appsid-gplay",
        "/kaggle/input/datasets/rozanhaisyam/appsid",
        "/kaggle/input/appsid-gplay",
        "/kaggle/input/appsid",
        "/kaggle/input/rozanhaisyam/appsid-gplay",
        "/kaggle/input/rozanhaisyam/appsid",
    ]
if HAS_DRIVE:
    drive_candidates += [
        "/content/drive/MyDrive/ACOS",
        "/content/drive/MyDrive/ACOS-ASLI",
    ]
    try:
        for _item in sorted(os.listdir("/content/drive/MyDrive")):
            if "acos" in _item.lower():
                _p = os.path.join("/content/drive/MyDrive", _item)
                if os.path.isdir(_p) and _p not in drive_candidates:
                    drive_candidates.append(_p)
    except Exception:
        pass

base_project_dir = None
if IS_KAGGLE:
    for dc in drive_candidates:
        if os.path.isdir(dc) and (os.path.exists(os.path.join(dc, "Extract-Classify-ACOS")) or os.path.exists(os.path.join(dc, "data"))):
            base_project_dir = dc
            break
    if not base_project_dir:
        base_project_dir = "/kaggle/working/ACOS"
        os.makedirs(base_project_dir, exist_ok=True)
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"🦅 Mode Kaggle Aktif: {base_project_dir}")
    print(f"📁 Output Sesi akan disimpan di: {save_dir}")
elif HAS_DRIVE:
    for dc in drive_candidates:
        if os.path.isdir(dc) and (os.path.exists(os.path.join(dc, "Extract-Classify-ACOS")) or os.path.exists(os.path.join(dc, "data"))):
            base_project_dir = dc
            break
    if not base_project_dir:
        base_project_dir = "/content/drive/MyDrive/ACOS"
        os.makedirs(base_project_dir, exist_ok=True)
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Mode Google Drive Terdeteksi: {base_project_dir}")
    print(f"📁 Output Sesi akan disimpan persisten di: {save_dir}")
elif os.path.exists("/content/ACOS/Extract-Classify-ACOS"):
    base_project_dir = "/content/ACOS"
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Mode Colab Ephemeral Aktif: {base_project_dir}")
elif os.path.exists("Extract-Classify-ACOS"):
    base_project_dir = os.path.abspath(".")
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Mode Lokal Aktif (Current Dir): {base_project_dir}")
elif os.path.exists("../Extract-Classify-ACOS"):
    base_project_dir = os.path.abspath("..")
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Mode Lokal Aktif (Parent Dir): {base_project_dir}")
else:
    base_project_dir = os.path.abspath("ACOS")
    os.makedirs(base_project_dir, exist_ok=True)
    save_dir = os.path.join(base_project_dir, "Output")
    os.makedirs(save_dir, exist_ok=True)
    print(f"💾 Inisialisasi folder ACOS: {base_project_dir}")

# 2. Auto-clone repositori ACOS jika folder inti belum tersedia
extract_dir = os.path.join(base_project_dir, "Extract-Classify-ACOS")
absa5_dir = os.path.join(base_project_dir, "absa5")
if not os.path.exists(extract_dir) or not os.path.exists(absa5_dir):
    print(f"📥 Repositori atau modul absa5 belum lengkap di {base_project_dir}. Menyinkronkan dari GitHub...")
    _tmp_clone = "/tmp/ACOS_clone" if not IS_KAGGLE else "/kaggle/temp/ACOS_clone"
    os.system(f'rm -rf {_tmp_clone}')
    os.system(f'git clone https://github.com/haisyamalawwab/ACOS.git {_tmp_clone}')
    os.system(f'cp -r {_tmp_clone}/* "{base_project_dir}/"')
    os.system(f'rm -rf {_tmp_clone}')
    print("✅ Repositori dan modul absa5 berhasil disinkronkan.")

data_root = os.path.join(base_project_dir, "data")
notebooks_dir = os.path.join(base_project_dir, "notebooks")
"""


def apply_kaggle_patches(cells):
    """Adaptasikan sel notebook V4 untuk lingkungan Kaggle."""
    # 1. Judul (Sel 0)
    cells[0]["source"] = [line + "\n" for line in MD_TITLE_KAGGLE.splitlines()]

    # 2. Setup & Environment (Sel 2)
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "from google.colab import drive" in src and "!pip install" in src:
            cells[idx]["source"] = [line + "\n" for line in CODE_SETUP_KAGGLE.splitlines()]
            break

    # 3. Path Initialization (Sel 8)
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "drive_candidates = [" in src and "Extract-Classify-ACOS" in src:
            cells[idx]["source"] = [line + "\n" for line in CODE_PATH_KAGGLE.splitlines()]
            break

    # 4. Dua Root & Dataset Kaggle: Deteksi indo_root & sinkronisasi data di Kaggle (Sel 11)
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "def _cari_indo_root():" in src and "ACOS-IndoBERT" in src:
            _old_anchor = '    if os.path.exists("/content/drive/MyDrive"):'
            _kaggle_branch = (
                '    if os.path.exists("/kaggle"):\n'
                '        kandidat += [\n'
                '            "/kaggle/working/ACOS/ACOS-IndoBERT",\n'
                '            "/kaggle/working/ACOS-IndoBERT",\n'
                '            "/kaggle/working",\n'
                '            "/kaggle/input/acos-indobert/ACOS-IndoBERT",\n'
                '            "/kaggle/input/acos-indobert",\n'
                '            "/kaggle/input/acos-asli/ACOS-IndoBERT",\n'
                '            "/kaggle/input/datasets/rozanhaisyam/appsid-gplay/ACOS-IndoBERT",\n'
                '            "/kaggle/input/datasets/rozanhaisyam/appsid-gplay",\n'
                '            "/kaggle/input/datasets/rozanhaisyam/appsid/ACOS-IndoBERT",\n'
                '            "/kaggle/input/datasets/rozanhaisyam/appsid",\n'
                '            "/kaggle/input/appsid-gplay/ACOS-IndoBERT",\n'
                '            "/kaggle/input/appsid-gplay",\n'
                '            "/kaggle/input/appsid/ACOS-IndoBERT",\n'
                '            "/kaggle/input/appsid",\n'
                '        ]\n'
                '    if os.path.exists("/content/drive/MyDrive"):'
            )
            if _old_anchor in src and "/kaggle" not in src:
                src = src.replace(_old_anchor, _kaggle_branch)

            _old_init_dirs = (
                'for _d in (data_root, tokenized_dir, backbones_dir,\n'
                '           os.path.join(indo_root, "results"), os.path.join(indo_root, "build")):\n'
                '    os.makedirs(_d, exist_ok=True)'
            )
            _kaggle_dataset_sync = (
                'for _d in (data_root, tokenized_dir, backbones_dir,\n'
                '           os.path.join(indo_root, "results"), os.path.join(indo_root, "build")):\n'
                '    os.makedirs(_d, exist_ok=True)\n'
                '\n'
                '# ============================================================\n'
                '#  Deteksi & Sinkronisasi Dataset Kaggle (appsid-gplay / appsid)\n'
                '# ============================================================\n'
                'KAGGLE_DATASET_CANDIDATES = [\n'
                '    "/kaggle/input/datasets/rozanhaisyam/appsid-gplay",\n'
                '    "/kaggle/input/datasets/rozanhaisyam/appsid",\n'
                '    "/kaggle/input/appsid-gplay",\n'
                '    "/kaggle/input/appsid",\n'
                '    "/kaggle/input/rozanhaisyam/appsid-gplay",\n'
                '    "/kaggle/input/rozanhaisyam/appsid",\n'
                ']\n'
                '\n'
                '_target_apps = os.path.join(data_root, "Apps-ACOS")\n'
                'os.makedirs(_target_apps, exist_ok=True)\n'
                '_synced_datasets = []\n'
                '\n'
                'for _kd in KAGGLE_DATASET_CANDIDATES:\n'
                '    if os.path.isdir(_kd):\n'
                '        _synced_datasets.append(_kd)\n'
                '        print(f"📊 Dataset Kaggle terdeteksi: {_kd}")\n'
                '        # 1. Sinkronisasi folder Apps-ACOS / processed / tsv dataset\n'
                '        _cand_apps = [\n'
                '            os.path.join(_kd, "Apps-ACOS"),\n'
                '            os.path.join(_kd, "data", "Apps-ACOS"),\n'
                '            _kd,\n'
                '        ]\n'
                '        _apps_src = next((p for p in _cand_apps if os.path.exists(os.path.join(p, "processed")) or os.path.exists(os.path.join(p, "appsid_quad_train.tsv"))), None)\n'
                '        if _apps_src:\n'
                '            print(f"   📥 Menyinkronkan data {_apps_src} -> {_target_apps}...")\n'
                '            os.system(f\'cp -rn "{_apps_src}/"* "{_target_apps}/" 2>/dev/null || cp -r "{_apps_src}/"* "{_target_apps}/"\')\n'
                '        # 2. Sinkronisasi tokenized_data jika ada\n'
                '        _sub_tok = os.path.join(_kd, "tokenized_data")\n'
                '        if os.path.isdir(_sub_tok):\n'
                '            print(f"   📥 Menyinkronkan tokenized_data {_sub_tok} -> {tokenized_dir}...")\n'
                '            os.system(f\'cp -rn "{_sub_tok}/"* "{tokenized_dir}/" 2>/dev/null || cp -r "{_sub_tok}/"* "{tokenized_dir}/"\')\n'
                '        else:\n'
                '            try:\n'
                '                if any("quad_bert.tsv" in f for f in os.listdir(_kd)):\n'
                '                    print(f"   📥 Menyinkronkan tokenized_data langsung dari {_kd} -> {tokenized_dir}...")\n'
                '                    os.system(f\'cp -rn "{_kd}"/*_quad_bert.tsv "{tokenized_dir}/" 2>/dev/null || true\')\n'
                '                    os.system(f\'cp -rn "{_kd}"/*_pair.tsv "{tokenized_dir}/" 2>/dev/null || true\')\n'
                '            except Exception:\n'
                '                pass\n'
                '        # 3. Sinkronisasi pretrained backbones jika ada\n'
                '        _sub_bb = os.path.join(_kd, "backbones")\n'
                '        if os.path.isdir(_sub_bb):\n'
                '            print(f"   📥 Menyinkronkan pretrained backbone {_sub_bb} -> {backbones_dir}...")\n'
                '            os.system(f\'cp -rn "{_sub_bb}/"* "{backbones_dir}/" 2>/dev/null || cp -r "{_sub_bb}/"* "{backbones_dir}/"\')\n'
                '\n'
                'if _synced_datasets:\n'
                '    print(f"✅ Selesai konfigurasi {len(_synced_datasets)} sumber dataset Kaggle ke {data_root}.")'
            )
            if _old_init_dirs in src and "KAGGLE_DATASET_CANDIDATES" not in src:
                src = src.replace(_old_init_dirs, _kaggle_dataset_sync)

            cells[idx]["source"] = [line + "\n" for line in src.splitlines()]
            break

    # 5. Tambahkan search roots Kaggle pada pencarian checkpoint
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "_search_roots = [" in src:
            _anchor_sr = '                session_dirs.get("root", ""),'
            _kaggle_sr = (
                '                session_dirs.get("root", ""),\n'
                '                "/kaggle/working/results",\n'
                '                "/kaggle/working/ACOS/results",\n'
                '                "/kaggle/working/ACOS-IndoBERT/results",'
            )
            if _anchor_sr in src and "/kaggle/working/results" not in src:
                src = src.replace(_anchor_sr, _kaggle_sr)
                cells[idx]["source"] = [line + "\n" for line in src.splitlines()]

    # 6. Audit artefak & packaging zip di akhir sesi (Sel 79)
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "🏁 AUDIT ARTEFAK SESI AKTIF" in src:
            _anchor_audit = 'is_drive_saved = "/content/drive/MyDrive" in session_dirs.get("root", "")'
            _kaggle_audit = (
                'is_kaggle = os.path.exists("/kaggle")\n'
                'is_drive_saved = "/content/drive/MyDrive" in session_dirs.get("root", "")\n'
                'if is_kaggle:\n'
                '    print(f"🛡️  Lingkungan Kaggle: ✅ Output tersimpan di {session_dirs.get(\'root\')} (Tersedia di tab Output)\\n")\n'
                '    _zip_out = "/kaggle/working/acos_run_results.zip"\n'
                '    os.system(f"zip -rq {_zip_out} {session_dirs.get(\'root\')} 2>/dev/null || true")\n'
                '    if os.path.exists(_zip_out):\n'
                '        print(f"📦 Arsip zip otomatis dibuat: {_zip_out} ({os.path.getsize(_zip_out)/1024**2:.1f} MB)\\n")'
            )
            if _anchor_audit in src and "is_kaggle" not in src:
                src = src.replace(_anchor_audit, _kaggle_audit)
                cells[idx]["source"] = [line + "\n" for line in src.splitlines()]
            break

    return cells


def main():
    if not os.path.isfile(SRC_NB):
        raise FileNotFoundError(f"Notebook sumber {SRC_NB} tidak ditemukan.")

    nb = json.load(io.open(SRC_NB, encoding="utf-8"))
    cells = nb["cells"]
    print(f"Membaca {SRC_NB}: {len(cells)} sel...")

    cells = apply_kaggle_patches(cells)
    nb["cells"] = cells

    # Simpan ke target Kaggle
    for dst_path in [DST_KAGGLE_DIR, DST_NOTEBOOKS_DIR]:
        with io.open(dst_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
            f.write("\n")
        n_code = sum(1 for c in cells if c["cell_type"] == "code")
        digest = hashlib.md5(open(dst_path, "rb").read()).hexdigest()
        print(f"✅ {os.path.basename(dst_path)} ditulis ke {os.path.dirname(dst_path)}: "
              f"{len(cells)} sel ({n_code} kode). MD5 {digest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
