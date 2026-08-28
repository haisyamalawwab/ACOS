# -*- coding: utf-8 -*-
"""Menerapkan sisa IMPLEMENTATION_PLAN_00_PRO_CACHING.md ke notebook 00 PRO.

Rencana menuntut sel 6 "membaca sesi aktif atau membuat direktori timestamp
baru". Notebook selalu membuat direktori baru, sehingga seluruh pemeriksaan
cache di sel 8/12/20/22/24 (yang menunjuk ke session_dirs) selalu MISS pada
runtime baru. Empat perubahan di sini:

1. Sel 6  : resume sesi terakhir yang punya artefak + flag RESUME_LAST_SESSION.
2. Sel 8  : cache EDA hanya dianggap valid bila plot ikut ada, agar jalur cache
            tidak menampilkan laporan tanpa gambar.
3. Sel 24 : impor yang dipakai jalur non-cache diamankan supaya sel bisa
            dijalankan sesudah kernel restart.
4. Sel 26 : kelas model diimpor ulang bila hilang dari globals.
"""
import json
import sys

CELL_CONFIG, CELL_EDA, CELL_STEP2 = 6, 8, 22
CELL_EVAL, CELL_INFER = 24, 26

OLD_SESSION = '''active_save_dir = save_dir if 'save_dir' in locals() else base_project_dir

# 1. Inisialisasi direktori sesi berbasis timestamp (DDMMYYYY_HMS)
results_base = os.path.join(active_save_dir, "results")
session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)
'''

NEW_SESSION = '''active_save_dir = save_dir if 'save_dir' in locals() else base_project_dir

# Sesi dilanjutkan bila ada artefak tersimpan; set False untuk memaksa sesi baru.
RESUME_LAST_SESSION = True

# 1. Inisialisasi direktori sesi (lanjutkan sesi lama atau buat timestamp baru)
results_base = os.path.join(active_save_dir, "results")

_SESSION_KEYS = ("root", "checkpoints", "step1_checkpoint", "step2_checkpoint",
                 "plots", "csv", "md", "logs")

_SESSION_KEYS = ("root", "checkpoints", "step1_checkpoint", "step2_checkpoint",
                 "plots", "csv", "md", "logs")

def session_dirs_from_root(run_dir):
    """Menyusun ulang peta direktori sesi dengan kunci yang sama seperti
    setup_timestamped_run_dir(), tanpa membuat folder timestamp baru."""
    dirs = {
        "root": run_dir,
        "checkpoints": os.path.join(run_dir, "checkpoints"),
        "step1_checkpoint": os.path.join(run_dir, "checkpoints", "step1_best"),
        "step2_checkpoint": os.path.join(run_dir, "checkpoints", "step2_best"),
        "plots": os.path.join(run_dir, "plots"),
        "csv": os.path.join(run_dir, "csv"),
        "md": os.path.join(run_dir, "md"),
        "logs": os.path.join(run_dir, "logs"),
    }
    for _p in dirs.values():
        os.makedirs(_p, exist_ok=True)
    return dirs

def session_cache_score(run_dir):
    """Jumlah artefak kunci di sebuah direktori sesi (0 berarti sesi kosong)."""
    marks = [
        os.path.join(run_dir, "pipeline_state.pkl"),
        os.path.join(run_dir, "csv", "master_01_statistik_dataset.csv"),
        os.path.join(run_dir, "logs", "pred4pipeline.txt"),
        os.path.join(run_dir, "checkpoints", "step1_best", "pytorch_model.bin"),
        os.path.join(run_dir, "checkpoints", "step2_best", "pytorch_model.bin"),
        os.path.join(run_dir, "logs", "master_metrics.json"),
    ]
    return sum(1 for m in marks if os.path.exists(m))

def find_resumable_session(base_dir, domain):
    """Sesi domain ini dengan artefak terbanyak (penyeimbang: paling baru).
    Tanpa ini setiap eksekusi memakai folder timestamp baru sehingga cache
    per tahap di sel-sel berikutnya tidak pernah ditemukan."""
    if not os.path.isdir(base_dir):
        return None
    ranked = []
    for name in sorted(os.listdir(base_dir)):
        p = os.path.join(base_dir, name)
        if not os.path.isdir(p) or not name.startswith(domain + "_"):
            continue
        score = session_cache_score(p)
        if score:
            ranked.append((score, os.path.getmtime(p), p))
    if not ranked:
        return None
    ranked.sort(reverse=True)
    return ranked[0][2]

_resume_root = find_resumable_session(results_base, DOMAIN) if RESUME_LAST_SESSION else None
if _resume_root:
    session_dirs = session_dirs_from_root(_resume_root)
    print(f"\\u267b\\ufe0f Melanjutkan sesi tersimpan: {_resume_root}")
    print(f"   Artefak kunci terdeteksi: {session_cache_score(_resume_root)}/6")
else:
    session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)
'''

OLD_EDA_VAR = 'eda_ringkas_csv = os.path.join(csv_dir, "master_02_ringkasan_eda.csv")\n'
NEW_EDA_VAR = (
    'eda_ringkas_csv = os.path.join(csv_dir, "master_02_ringkasan_eda.csv")\n'
    '# Plot wajib ikut ada. Tanpa syarat ini jalur cache melewati pembuatan\n'
    '# gambar dan bagian laporan EDA berakhir tanpa visualisasi.\n'
    'eda_plot_utama = os.path.join(plots_dir, "01_eda_dataset_distribution.png")\n'
)

OLD_EDA_COND = 'elif os.path.exists(eda_stats_csv) and os.path.exists(eda_ringkas_csv):\n'
NEW_EDA_COND = (
    'elif (os.path.exists(eda_stats_csv) and os.path.exists(eda_ringkas_csv)\n'
    '      and os.path.exists(eda_plot_utama)):\n'
)

OLD_EVAL_HEAD = (
    'ensure_objects()\n'
    '# Evaluasi Final Memakai Checkpoint Model Step 2 Terbaik\n'
    'FORCE_REEVAL = False\n'
)
NEW_EVAL_HEAD = (
    'ensure_objects()\n'
    '# Evaluasi Final Memakai Checkpoint Model Step 2 Terbaik\n'
    'FORCE_REEVAL = False\n'
    '\n'
    '# Jalur non-cache memakai nama-nama dari sel 22; impor ulang agar sel ini\n'
    '# tetap bisa dijalankan setelah kernel restart.\n'
    'import logging\n'
    'from modeling import CategorySentiClassification\n'
    'from eval_metrics import pair_eval\n'
    'from colab_utils import SubtaskMetricCapture, plot_subtask_metrics\n'
)

OLD_EVAL_ELSE = (
    'else:\n'
    '    # Muat model Step 2 terbaik\n'
    '    step2_bin_path = os.path.join(session_dirs["step2_checkpoint"], "pytorch_model.bin")\n'
)
NEW_EVAL_ELSE = (
    'else:\n'
    '    if "eval_loader_2" not in globals() or "eval_gold_2" not in globals():\n'
    '        raise RuntimeError(\n'
    '            "Loader evaluasi step 2 belum ada di memori dan master_metrics.json "\n'
    '            "belum tersimpan. Jalankan sel Step 2 (sel 22) lebih dulu.")\n'
    '\n'
    '    # Muat model Step 2 terbaik\n'
    '    step2_bin_path = os.path.join(session_dirs["step2_checkpoint"], "pytorch_model.bin")\n'
)

OLD_EVAL_IMPORT = (
    '    subtask_metrics = cached_all.get("subtasks", {})\n'
    '    from colab_utils import SubtaskMetricCapture\n'
    '    df_subtasks = pd.DataFrame([\n'
)
NEW_EVAL_IMPORT = (
    '    subtask_metrics = cached_all.get("subtasks", {})\n'
    '    df_subtasks = pd.DataFrame([\n'
)

OLD_INFER = (
    'ensure_objects()\n'
    'import re as _re\n'
)
NEW_INFER = (
    'ensure_objects()\n'
    'import re as _re\n'
    '\n'
    '# Kelas model diimpor di sel 12 & 22; ambil ulang bila sel ini dijalankan\n'
    '# sendiri sesudah pemulihan state.\n'
    'from modeling import BertForQuadABSA, CategorySentiClassification\n'
)


OLD_STEP2_HEAD = (
    'ensure_objects()\n'
    'from modeling import CategorySentiClassification\n'
    'from dataset_utils import read_pair_gold\n'
    'from eval_metrics import pair_eval\n'
)
NEW_STEP2_HEAD = (
    'ensure_objects()\n'
    'from modeling import CategorySentiClassification\n'
    'from dataset_utils import read_pair_gold\n'
    'from eval_metrics import pair_eval\n'
    '# Nama-nama ini datang dari sel 12; diimpor ulang agar sel 22 tetap jalan\n'
    '# ketika Step 1 dilewati lewat pemulihan state.\n'
    'from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler\n'
    'from tqdm import tqdm\n'
)


def read_source(cell):
    return "".join(cell["source"])


def write_source(cell, text):
    lines = text.split("\n")
    cell["source"] = [l + "\n" for l in lines[:-1]] + ([lines[-1]] if lines[-1] else [])


def replace_once(cell, old, new, tag):
    text = read_source(cell)
    if old not in text:
        if new in text:
            print("  skip (sudah diterapkan):", tag)
            return
        raise SystemExit("  GAGAL: pola tidak ditemukan -> " + tag)
    write_source(cell, text.replace(old, new, 1))
    print("  ok:", tag)


def patch(path):
    print(path)
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    if len(cells) != 29:
        raise SystemExit("  GAGAL: jumlah sel tidak sesuai (%d)" % len(cells))

    replace_once(cells[CELL_CONFIG], OLD_SESSION, NEW_SESSION, "resume sesi di sel konfigurasi")
    replace_once(cells[CELL_EDA], OLD_EDA_VAR, NEW_EDA_VAR, "variabel plot EDA")
    replace_once(cells[CELL_EDA], OLD_EDA_COND, NEW_EDA_COND, "cache EDA wajib punya plot")
    replace_once(cells[CELL_STEP2], OLD_STEP2_HEAD, NEW_STEP2_HEAD, "impor loader di sel step 2")
    replace_once(cells[CELL_EVAL], OLD_EVAL_HEAD, NEW_EVAL_HEAD, "impor sel evaluasi")
    replace_once(cells[CELL_EVAL], OLD_EVAL_IMPORT, NEW_EVAL_IMPORT, "hapus impor ganda jalur cache")
    replace_once(cells[CELL_EVAL], OLD_EVAL_ELSE, NEW_EVAL_ELSE, "penjaga loader evaluasi")
    replace_once(cells[CELL_INFER], OLD_INFER, NEW_INFER, "impor kelas model di sel inferensi")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


for target in sys.argv[1:]:
    patch(target)
