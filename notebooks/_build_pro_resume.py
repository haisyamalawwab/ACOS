# -*- coding: utf-8 -*-
"""
Builder: creates 00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb
from 00_ACOS_Master_Pipeline_Colab_PRO.ipynb by strengthening the
save/load continuity between stages:
  1) Cell 14 saves an EXPANDED pipeline_state.pkl: completed_stages +
     reloadable runtime artifacts (labels, num_labels, best epochs/F1,
     candidate source, args) plus JSON dumps of label lists.
  2) Cell 16 recovery restores all of the above into globals.
  3) New cell inserts a guaranteed-runtime-objects fallback (ensure_objects)
     that, if a global is missing, reloads it from saved state/checkpoint.
  4) Load-heavy cells (22, 24) are prefixed with ensure_objects() so they
     no longer depend on a prior kernel run.
"""
import json
import copy

SRC = r"D:\laragon\www\ACOS-ASLI\notebooks\00_ACOS_Master_Pipeline_Colab_PRO.ipynb"
DST = r"D:\laragon\www\ACOS-ASLI\notebooks\00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb"

with open(SRC, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]


def code(src):
    lines = src.rstrip("\n").split("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [l + "\n" for l in lines[:-1]] + [lines[-1] + "\n" if lines else ""],
    }


def replace_cell(idx, src):
    cells[idx] = code(src)


# ---------------------------------------------------------------------------
# CELL 14: EXPANDED STATE SAVER
# ---------------------------------------------------------------------------
cell14 = r'''# Simpan status variabel pipeline ke file pickle untuk pemulihan cepat.
# Sekarang menyimpan BUKAN hanya config, tapi juga artefak runtime yang bisa
# dimuat ulang + daftar tahapan yang sudah selesai (completed_stages).
checkpoint_state_path = os.path.join(session_dirs["root"], "pipeline_state.pkl")

# Tahapan yang sudah diselesaikan sejauh ini, dideteksi dari artefak di disk
# (robust: tidak bergantung pada flag variabel yang mungkin belum dibuat).
completed_stages = []
_sd = session_dirs
if os.path.exists(os.path.join(_sd["csv"], "master_01_statistik_dataset.csv")):
    completed_stages.append("EDA")
if os.path.exists(os.path.join(_sd["step1_checkpoint"], "pytorch_model.bin")) or os.path.exists(os.path.join(_sd["logs"], "pred4pipeline.txt")):
    completed_stages.append("STEP1")
if os.path.exists(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_pair_1st.tsv")):
    completed_stages.append("PAIRS")
if os.path.exists(os.path.join(_sd["step2_checkpoint"], "pytorch_model.bin")):
    completed_stages.append("STEP2")
if os.path.exists(os.path.join(_sd["logs"], "master_metrics.json")):
    completed_stages.append("EVAL")

# Artefak runtime yang bisa diserialisasi (aman dipickle & dimuat ulang).
_serializable = {}

def _snap(name):
    if name in globals():
        _serializable[name] = globals()[name]
    else:
        _serializable[name] = None

for _v in ["label_list_step1", "label_list_step2", "label_map_seq",
           "num_labels_step1", "num_labels_step2"]:
    _snap(_v)
_snap("best_step1_f1")
_snap("best_step1_epoch")
_snap("best_step2_f1")
_snap("best_step2_epoch")
_snap("pakai_1st")
_snap("df_pairs")
# args yang dipakai pair_eval (ArgsH / ArgsProxy)
if "args_h" in globals():
    _serializable["args_h"] = {
        "output_dir": getattr(globals()["args_h"], "output_dir", None),
        "max_seq_length": getattr(globals()["args_h"], "max_seq_length", None),
    }

pipeline_state = {
    "DOMAIN": DOMAIN,
    "base_project_dir": base_project_dir,
    "extract_dir": extract_dir,
    "data_root": data_root,
    "bert_cache_dir": bert_cache_dir,
    "session_dirs": session_dirs,
    "MAX_SEQ_LENGTH": MAX_SEQ_LENGTH,
    "NUM_EPOCHS": NUM_EPOCHS,
    "STEP2_BATCH_SIZE": STEP2_BATCH_SIZE,
    "STEP2_LR": STEP2_LR,
    "SEED": SEED,
    "device_str": str(device),
    # --- BARU: runtime yang bisa dimuat ulang ---
    "completed_stages": completed_stages,
    "runtime": _serializable,
}

with open(checkpoint_state_path, "wb") as f:
    pickle.dump(pipeline_state, f)

# Simpan juga label list sebagai JSON agar bisa dimuat tanpa pickle (debug/manual).
def _dump_labels(labels, name, path):
    try:
        with open(os.path.join(path, name + ".json"), "w", encoding="utf-8") as jf:
            json.dump(labels, jf, ensure_ascii=False, indent=2)
    except Exception as _e:
        print(f"   ⚠️ Gagal simpan {name}.json: {_e}")

_dump_labels(label_list_step1, "labels_step1", session_dirs["csv"])
_dump_labels(label_list_step2, "labels_step2", session_dirs["csv"])

print(f"✅ Pipeline State (expanded) berhasil disimpan ke: {checkpoint_state_path}")
print(f"   Tahapan selesai: {completed_stages}")
print(f"   Artefak runtime tersimpan: {list(_serializable.keys())}")
print("ℹ️ Jika runtime Colab terputus, jalankan sel pemulihan di bawah ini untuk melanjutkan.")'''

replace_cell(14, cell14)

# ---------------------------------------------------------------------------
# CELL 16: RECOVERY (restores config + runtime reloadables)
# ---------------------------------------------------------------------------
cell16 = r'''# Sel Pemulihan Cerdas: Otomatis mendeteksi sesi aktif terakhir.
# Memulihkan BUKAN hanya config/path, tapi juga artefak runtime yang tersimpan.
def auto_find_latest_state(search_base):
    if not os.path.exists(search_base):
        return None
    candidates = []
    for root, dirs, files in os.walk(search_base):
        if "pipeline_state.pkl" in files:
            p = os.path.join(root, "pipeline_state.pkl")
            candidates.append((os.path.getmtime(p), p))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

# Prioritas path state
target_state_path = None
if 'checkpoint_state_path' in globals() and os.path.exists(checkpoint_state_path):
    target_state_path = checkpoint_state_path
else:
    target_state_path = auto_find_latest_state(
        results_base if 'results_base' in globals() else os.path.join(base_project_dir, "Output", "results"))
    if not target_state_path and os.path.exists("/content/drive/MyDrive/ACOS/Output/results"):
        target_state_path = auto_find_latest_state("/content/drive/MyDrive/ACOS/Output/results")

if target_state_path and os.path.exists(target_state_path):
    with open(target_state_path, "rb") as f:
        pipe_state = pickle.load(f)

    DOMAIN = pipe_state.get("DOMAIN", "rest16")
    base_project_dir = pipe_state.get("base_project_dir", base_project_dir if 'base_project_dir' in globals() else ".")
    extract_dir = pipe_state.get("extract_dir", os.path.join(base_project_dir, "Extract-Classify-ACOS"))
    bert_cache_dir = pipe_state.get("bert_cache_dir", os.path.join(base_project_dir, "bert_base_uncased"))
    session_dirs = pipe_state.get("session_dirs", session_dirs if 'session_dirs' in globals() else {})
    MAX_SEQ_LENGTH = pipe_state.get("MAX_SEQ_LENGTH", 128)
    NUM_EPOCHS = pipe_state.get("NUM_EPOCHS", 15)
    STEP2_BATCH_SIZE = pipe_state.get("STEP2_BATCH_SIZE", 16)
    STEP2_LR = pipe_state.get("STEP2_LR", 5e-5)
    SEED = pipe_state.get("SEED", 42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- BARU: pulihkan artefak runtime yang tersimpan ---
    rt = pipe_state.get("runtime", {}) or {}
    label_list_step1 = rt.get("label_list_step1")
    label_list_step2 = rt.get("label_list_step2")
    label_map_seq    = rt.get("label_map_seq")
    num_labels_step1 = rt.get("num_labels_step1")
    num_labels_step2 = rt.get("num_labels_step2")
    best_step1_f1    = rt.get("best_step1_f1")
    best_step1_epoch = rt.get("best_step1_epoch")
    best_step2_f1    = rt.get("best_step2_f1")
    best_step2_epoch = rt.get("best_step2_epoch")
    pakai_1st        = rt.get("pakai_1st")
    df_pairs         = rt.get("df_pairs")
    _args_h0         = rt.get("args_h")

    completed_stages = pipe_state.get("completed_stages", [])

    # Bangun ulang objek args_h agar sel evaluasi/inferensi tetap berfungsi.
    import types as _types
    if _args_h0 and _args_h0.get("output_dir"):
        _ah = _types.SimpleNamespace()
        _ah.output_dir = _args_h0.get("output_dir", session_dirs["logs"])
        _ah.max_seq_length = _args_h0.get("max_seq_length", MAX_SEQ_LENGTH)
        args_h = _ah
        if "args_h" in globals():
            globals()["args_h"] = args_h

    print(f"✅ Berhasil memulihkan state dari: {target_state_path}")
    print(f"📁 Session Dir : {session_dirs.get('root')}")
    print(f"📌 DOMAIN      : {DOMAIN} | Device: {device}")
    print(f"   Tahapan selesai : {completed_stages}")
    print(f"   Runtime dimuat  : {[k for k in ('label_list_step1','label_list_step2','num_labels_step1','num_labels_step2','df_pairs') if rt.get(k) is not None]}")
    _recovered_from_state = True
else:
    print(f"ℹ️ Berkas state belum ditemukan (Lanjutkan eksekusi normal dari sel atas).")
    _recovered_from_state = False'''
replace_cell(16, cell16)

# ---------------------------------------------------------------------------
# NEW CELL 16b: ensure_objects() fallback — "cari hasil dari penyimpanan lama"
# ---------------------------------------------------------------------------
cell16b = r'''# 16b. Jaminan Objek Runtime (FALLBACK "cari hasil dari penyimpanan lama").
# Jika variabel runtime belum ada di memori (mis. kernel restart & hanya jalankan
# sebagian sel), fungsi ini memuatnya ulang dari: (a) state yang sudah direstorasi,
# (b) JSON label tersimpan, atau (c) ekspor manual. Dipanggil di awal tiap sel
# lanjutan yang butuh tokenizer / labels / model agar tidak pernah NameError.
def ensure_objects():
    """Pastikan tokenizer, label lists, num_labels, args_h tersedia di globals.
    Sumber: state yang direstorasi -> JSON label tersimpan -> fallback konstruksi."""
    import types as _t
    g = globals()

    # 1) Tokenizer
    if "tokenizer" not in g or g["tokenizer"] is None:
        if "bert_cache_dir" not in g:
            g["bert_cache_dir"] = os.path.join(
                g.get("base_project_dir", "."), "bert_base_uncased")
        if os.path.exists(os.path.join(g["bert_cache_dir"], "vocab.txt")):
            from bert_utils.tokenization import BertTokenizer
            g["tokenizer"] = BertTokenizer.from_pretrained(
                g["bert_cache_dir"], do_lower_case=True)
            print("   🔁 Tokenizer dimuat ulang dari bert_cache_dir.")
        else:
            raise RuntimeError("Tokenizer belum ada & vocab.txt tidak ditemukan. "
                               "Jalankan sel konfigurasi (cell 6) dulu.")

    # 2) args_h
    if "args_h" not in g or g["args_h"] is None:
        _ah = _t.SimpleNamespace()
        _ah.output_dir = g.setdefault("session_dirs", {}).get("logs")
        _ah.max_seq_length = g.get("MAX_SEQ_LENGTH", 128)
        g["args_h"] = _ah
        print("   🔁 args_h dibangun ulang dari state.")

    # 3) Label lists & num_labels (cari dari JSON tersimpan jika belum ada)
    csv_dir = g.setdefault("session_dirs", {}).get("csv")
    for _key, _jname in [("label_list_step1", "labels_step1"),
                         ("label_list_step2", "labels_step2")]:
        if (_key not in g or g[_key] is None) and csv_dir:
            _p = os.path.join(csv_dir, _jname + ".json")
            if os.path.exists(_p):
                with open(_p, "r", encoding="utf-8") as _jf:
                    g[_key] = json.load(_jf)
                print(f"   🔁 {_key} dimuat ulang dari {_jname}.json.")

    if g.get("label_list_step1") is not None and "num_labels_step1" not in g:
        g["num_labels_step1"] = len(g["label_list_step1"][1])
    if g.get("label_list_step2") is not None and "num_labels_step2" not in g:
        g["num_labels_step2"] = len(g["label_list_step2"][0])

    # 4) Sumber kandidat pasangan (default: prediksi step 1 = pipeline penuh)
    if "pakai_1st" not in g:
        g["pakai_1st"] = True

    return g


ensure_objects()'''
cell16b_meta = code(cell16b)
cell16b_mark = {
    "cell_type": "markdown",
    "metadata": {},
    "source": ["### 6c. Jaminan Objek Runtime (Fallback Load Otomatis)\n",
               "\n",
               "Sel ini menjalankan `ensure_objects()`: jika ada variabel runtime yang belum tersedia "
               "di memori (mis. kernel restart dan Anda hanya menjalankan sebagian sel), fungsi ini "
               "akan mencari hasilnya dari penyimpanan sebelumnya — yaitu *state* yang direstorasi "
               "(`pipeline_state.pkl`) atau file JSON label yang tersimpan — sehingga sel-sel lanjutan "
               "tidak pernah kehilangan variabel yang dibutuhkan di tengah jalan."]
}

# Insert markdown header + guard code cell right after recovery cell (index 16).
cells.insert(17, cell16b_mark)
cells.insert(18, cell16b_meta)
# NOTE: inserting shifts indices. We recompute the new index of the inserted cell
# so we can later place c22/c24 correctly. The insertion is at position 17
# (0-based), pushing old 17..26 to 18..27.

# ---------------------------------------------------------------------------
# redefine cell 22 & 24 (now at new indices) to call ensure_objects() at top
# ---------------------------------------------------------------------------
# Original cell 22 (evaluasi) was index 22; after inserting 1 cell at idx17,
# it is now at index 23. Original cell 24 is now at index 25.
# We prepend ensure_objects() to their source.
# Helper: prepend a guard line to a code cell source.

def prepend_guard(idx, guard_line):
    src = "".join(cells[idx]["source"])
    # avoid double-insert
    if guard_line.lstrip() in [l.lstrip() for l in src.split("\n") if l.strip()]:
        return
    cells[idx] = code(guard_line + "\n" + src)
    # remove execution_count reset concerns; code() sets execution_count None


# Cell 22 (evaluasi final) -> after inserting 2 cells at idx17/18, now at index 24
prepend_guard(24, 'ensure_objects()  # pastikan tokenizer/labels/args tersedia (fallback restore)')

# Cell 24 (inferensi live) -> now at index 26
prepend_guard(26, 'ensure_objects()  # pastikan tokenizer/labels/args tersedia (fallback restore)')

# ---------------------------------------------------------------------------
# markdown heading for the inserted resume cell
# ---------------------------------------------------------------------------
# Find the markdown cell that preceded original cell 16 to also insert a note.
# We'll pre-pend a note into the markdown cell right before the new 16b cell.
# The markdown cell that was originally index 15 ("## 6b. Smart State Recovery")
# is now at index 16, right before our inserted cell at 17. Leave it as-is.

# Re-number markdown headers? Not required; keep original numbering.

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
out = copy.deepcopy(nb)
out["cells"] = cells
out["metadata"]["colab"] = out["metadata"].get("colab", {})
out["metadata"]["colab"]["name"] = "00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb"

with open(DST, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("✅ Ditulis:", DST)
print("   Total cells:", len(out["cells"]))
