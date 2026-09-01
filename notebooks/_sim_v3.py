# Simulasi lokal torch-free sel 10a-10e V3 setelah pemindahan output ke folder
# ACOSE. Dihapus setelah verifikasi.
import json, os, sys, tempfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

nb = json.load(open(os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb"), encoding="utf-8"))
cells = nb["cells"]

def find_code(needle):
    for c in cells:
        if c["cell_type"] == "code" and needle in "".join(c["source"]):
            return "".join(c["source"])
    raise LookupError(needle)

tmp = tempfile.mkdtemp(prefix="acose_sim2_")
session_dirs = {k: os.path.join(tmp, "s", k) for k in
                ("checkpoints", "step1_checkpoint", "step2_checkpoint", "plots", "csv", "md", "logs")}
session_dirs["root"] = os.path.join(tmp, "s", "session_20260901_0000")
for d in session_dirs.values():
    os.makedirs(d, exist_ok=True)

manifest_calls, tables = [], []

def update_mcp_manifest(status, stage, extra=None):
    manifest_calls.append(status)

def save_pipeline_state(extra=None):
    pass

class RepStub:
    def section(self, t): print(f"[rep.section] {t}")
    def kv(self, d): print(f"[rep.kv] " + "; ".join(f"{k}={str(v)[:50]}" for k, v in d.items()))
    def text(self, t): pass
    def table(self, df, **kw): pass
    def image(self, p, cap): print(f"[rep.image] {os.path.basename(p)}")

def export_step_table(df, name=None, csv_dir=None, md_dir=None, **kw):
    tables.append((name, csv_dir))
    print(f"[export] {name} -> {csv_dir}")

vocab = set()
for split in ("train", "dev", "test"):
    p = os.path.join(REPO, "data", "Restaurant-ACOS", f"rest16_quad_{split}.tsv")
    for line in open(p, encoding="utf-8"):
        vocab.update(w.lower() for w in line.split("\t")[0].split())
bert_dir = os.path.join(tmp, "bert_fake")
os.makedirs(bert_dir, exist_ok=True)
with open(os.path.join(bert_dir, "vocab.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + sorted(vocab)) + "\n")

import _build_staged_v2 as V2
from datetime import datetime

env = {
    "__name__": "__main__",
    "os": os, "sys": sys, "json": json, "pd": pd, "plt": plt, "datetime": datetime,
    "session_dirs": session_dirs,
    "base_project_dir": REPO, "DOMAIN": "rest16",
    "bert_cache_dir": bert_dir,
    "MAX_SEQ_LENGTH": 128, "NUM_EPOCHS": 2, "SEED": 42, "device": "cpu",
    "update_mcp_manifest": update_mcp_manifest, "save_pipeline_state": save_pipeline_state,
    "rep": RepStub(), "export_step_table": export_step_table,
}
exec(compile(V2.CODE_TRACKER, "tracker", "exec"), env)

def run(needle, label):
    print(f"\n>>> {label}")
    exec(compile(find_code(needle), label, "exec"), env)

run("10a. Bootstrap quad", "cell_10a_run1")
run("10a. Bootstrap quad", "cell_10a_cachehit")
run("10b. Konfigurasi run ACOSE", "cell_10b_run1")
run("10b. Konfigurasi run ACOSE", "cell_10b_cachehit")

acose_root = os.path.join(REPO, "Output", "ACOSE", "rest16")
for d, best in (("extraction", 0.6123), ("classification", 0.4891)):
    os.makedirs(os.path.join(acose_root, d), exist_ok=True)
    json.dump({"stage": d, "best_metric": best, "best_epoch": 1, "history": [], "checkpoint": ""},
              open(os.path.join(acose_root, d, "train_log.json"), "w"))
run("10c. Training ACOSE", "cell_10c_cachehit")

json.dump({
    "overall": {"precision": 0.31, "recall": 0.22, "f1": 0.257, "tp": 90, "fp": 200, "fn": 320, "support": 410},
    "by_subset": {"aspect": {"precision": 0.55, "recall": 0.48, "f1": 0.513, "tp": 220, "fp": 180, "fn": 240, "support": 460},
                  "aspect+category+opinion+sentiment+emotion": {"precision": 0.31, "recall": 0.22, "f1": 0.257, "tp": 90, "fp": 200, "fn": 320, "support": 410}},
    "by_bucket": {"explicit-explicit": {"precision": 0.35, "recall": 0.26, "f1": 0.299, "tp": 70, "fp": 130, "fn": 200, "support": 270}},
    "table": "elements  P      R      F1\naspect   55.00% 48.00% 51.30%",
    "candidates": 3105, "redundancy_verdict": "deterministic renaming", "emotion_label_set": "emot_id_netral",
}, open(os.path.join(acose_root, "logs", "acose_metrics.json"), "w", encoding="utf-8"))
run("10d. Evaluasi end-to-end", "cell_10d_cachehit")

env["acose_bootstrap_reports"] = {}
run("10e. Tabel, plot & state ACOSE", "cell_10e")

print("\n=== VERIFIKASI LOKASI BARU ===")
for root, dirs, files in os.walk(acose_root):
    rel = os.path.relpath(root, os.path.join(REPO, "Output", "ACOSE"))
    for f in sorted(files):
        print("  ACOSE/" + os.path.normpath(os.path.join(rel, f)).replace("\\", "/"))
print("tabel -> folder:", sorted({t[1] for t in tables}))
print("manifest:", manifest_calls)
# folder sesi ACOS tidak boleh berisi artefak ACOSE
leak = [os.path.join(r, f) for r, _, fs in os.walk(session_dirs["root"]) for f in fs if "acose" in f.lower()]
print("kebocoran ke folder sesi:", leak or "TIDAK ADA")
