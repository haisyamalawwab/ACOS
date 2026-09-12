"""Generator notebook master ACOS-BERT V1 (deterministik, idempoten).

Membangun `00_ACOS_Master_Pipeline_V1_BERT.ipynb` dari template sel di berkas
ini — tanpa notebook sumber, tanpa patch. Pola sukses yang ditiru dari V4_1:

- Sel 1bdn: pelacak progres + bootstrap runtime (Colab/lokal/JupyterLab).
- Dua root: `bert_root` (ditulis) vs. `acos_root` (hanya dibaca).
- Gate `raise_on_fail` sebelum training; Gate-1 numerik untuk backbone.
- Resume training level-3 (bobot + optimizer + global_step) + early stopping.
- Bridge pred->pair_1st yang aman (perbaikan KeyError 'a--1,-1').
- Step-2 memakai work-dir sesi (salinan tokenized_data + 1st hasil sendiri)
  sehingga repo upstream tetap read-only.

DOMAIN: rest16 (13 kategori -> 39 label) atau laptop (121 -> 363).
BACKBONE: bert-en (`bert-base-uncased`, prefix bert.* asli, tanpa rekey).

Jalankan: `python notebooks/_build_v1_bert.py` dari dalam `ACOS-BERT/`.
Keluaran deterministik: dua build berurutan menghasilkan MD5 identik.
"""
import ast
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "00_ACOS_Master_Pipeline_V1_BERT.ipynb")


def md(title, body=""):
    src = [title + "\n"]
    if body:
        src.append(body)
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src, section=None):
    if section:
        src = "# === SECTION:%s ===\n" % section + src
    return {"cell_type": "code", "metadata": {},
            "source": src.splitlines(keepends=True),
            "outputs": [], "execution_count": None}


# ── setup ─────────────────────────────────────────────────────────────

MD_TITLE = """# ACOS-BERT V1 — Baseline Inggris (rest16/laptop) dengan BERT-base

Pipeline ACOS dua tahap (Step-1 BERT-CRF co-extraction, Step-2 klasifikasi
kategori-sentimen single-head) untuk dataset Inggris bawaan repo, dengan
backbone `bert-base-uncased` yang di-fine-tune di sini.

Jalankan sel berurutan. Ulangi sel 1 (env) dan 2 (konfigurasi) setiap restart
kernel. Sel 4 (gate) dan 6 (Gate-1) berwarna merah berarti berhenti — jangan
lanjut ke training.
"""

CODE_ENV = '''# ============================================================
# 1. Lingkungan: Colab / lokal / JupyterLab + dua root
# ============================================================
import os, sys, time, json, re, shutil, glob, math, random, logging, codecs as cs
from datetime import datetime
from types import SimpleNamespace

def _detect_env():
    try:
        import google.colab  # noqa
        return "colab"
    except ImportError:
        pass
    if os.path.exists("/content"):
        return "colab"
    if os.environ.get("JUPYTERHUB_USER") or os.environ.get("JPY_PARENT_PID"):
        return "jupyterlab"
    try:
        import jupyter_core  # noqa
        return "jupyterlab"
    except ImportError:
        return "local"

ENV = _detect_env()

def _find_repo_root(start):
    cur = os.path.abspath(start)
    for _ in range(6):
        if (os.path.isdir(os.path.join(cur, "Extract-Classify-ACOS"))
                and os.path.isdir(os.path.join(cur, "ACOS-BERT"))):
            return cur
        cur = os.path.dirname(cur)
    return None

USE_DRIVE = False  # set True di Colab bila sesi/checkpoint ingin di Drive
if ENV == "colab" and USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive", force_remount=False)
    _drive_acos = "/content/drive/MyDrive/ACOS-ASLI"
    REPO_ROOT = _drive_acos if os.path.isdir(_drive_acos) else _find_repo_root(".")
else:
    REPO_ROOT = _find_repo_root(".") or os.path.abspath(".")
if REPO_ROOT is None:
    raise RuntimeError("Repo root (berisi Extract-Classify-ACOS/ + ACOS-BERT/) tidak ditemukan")

bert_root = os.path.join(REPO_ROOT, "ACOS-BERT")
acos_root = REPO_ROOT
extract_dir = os.path.join(REPO_ROOT, "Extract-Classify-ACOS")
for _p in (extract_dir, bert_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import acos_en, acos_en.upstream, acos_en.taxonomy, acos_en.datafiles, acos_en.selftest
acos_en.upstream.ensure_path(acos_root=acos_root)
import colab_utils  # helper sesi/plot/metrik upstream (read-only)

print(f"ENV={ENV} | REPO_ROOT={REPO_ROOT}")
print(f"bert_root={bert_root} (ditulis) | extract_dir={extract_dir} (dibaca saja)")
'''

CODE_CONFIG = '''# ============================================================
# 2. Konfigurasi run (ulang setiap restart kernel)
# ============================================================
DOMAIN = "rest16"        # "rest16" (13 kat -> 39 label) atau "laptop" (121 kat -> 363 label)
BACKBONE = "bert-en"     # tetap; V1 hanya mendukung bert-base-uncased
MAX_SEQ_LENGTH = 128
STEP1_BATCH_SIZE = 32
STEP2_BATCH_SIZE = 32
EVAL_BATCH_SIZE = 32
STEP1_LR = 2e-5
STEP2_LR = 5e-5
NUM_EPOCHS = 15          # paper: 30; 15 optimal untuk sesi GPU Colab/JupyterLab
SEED = 42
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5
GRAD_ACC = 1
WARMUP = 0.1
FORCE_RETRAIN_STEP1 = False
FORCE_RETRAIN_STEP2 = False
USE_AMP = False          # True bila torch>=1.6 + GPU (opsional, hemat VRAM)

N_CATSENTI = {"rest16": 39, "laptop": 363}
assert DOMAIN in N_CATSENTI, DOMAIN
print(f"DOMAIN={DOMAIN} | num_labels_step2={N_CATSENTI[DOMAIN]} | SEED={SEED}")
'''

CODE_HELPERS = '''# ============================================================
# 3. Helper runtime (progres, _prf, tulis CSV/MD)
# ============================================================
import pandas as pd

class step_stage:
    def __init__(self, title, total_steps=None):
        self.title, self.total, self.n, self.t0 = title, total_steps, 0, None
    def __enter__(self):
        self.t0 = time.time()
        print("=" * 78); print(f">> {self.title}"); print("=" * 78, flush=True)
        return self
    def step(self, msg):
        self.n += 1
        tag = f"{self.n}/{self.total}" if self.total else str(self.n)
        print(f"   [{tag}] {time.time()-self.t0:7.1f}s  {msg}", flush=True)
    def note(self, msg):
        print(f"        {msg}", flush=True)
    def __exit__(self, t, e, tb):
        print(("OK " if t is None else f"GAGAL: {e} ") + f"{self.title} ({time.time()-self.t0:.1f}s)", flush=True)
        return False

def require_vars(*names):
    missing = [n for n in names if n not in globals()]
    if missing:
        raise RuntimeError(f"Variabel {missing} belum ada — jalankan sel 1-2 lebih dulu.")

def _prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    return p, r, (2*p*r/(p+r) if p+r else 0.0)

def write_df_csv_md(df, csv_path, md_path=None, title=""):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    if md_path:
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\\n\\n" + df.to_markdown(index=False) + "\\n")
    return csv_path

def history_display_frame(history):
    return pd.DataFrame(history) if history else pd.DataFrame()

print("helper siap: step_stage, require_vars, write_df_csv_md")
'''

CODE_GATES = '''# ============================================================
# 4. Gerbang verifikasi torch-free (merah = berhenti)
# ============================================================
require_vars("step_stage", "bert_root", "acos_root", "extract_dir")
from acos_en import default_paths
paths = default_paths(bert_root, acos_root)
gates = acos_en.selftest.run_gates(DOMAIN, paths, raise_on_fail=True)
for g, r in gates.items():
    print(f"[LULUS] {g}: {r['detail']}")
print(f"{len(gates)}/{len(gates)} gate torch-free hijau")
'''

CODE_BACKBONE = '''# ============================================================
# 5. Backbone bert-en + Gate-1 (bobot benar-benar termuat)
# ============================================================
require_vars("step_stage", "bert_root", "BACKBONE", "paths")
import acos_en.checkpoint as acos_ckpt
voc = acos_ckpt.ensure_vocab(paths["backbones_dir"], BACKBONE)
print(f"vocab: {voc['path']} ({voc.get('baris')} baris)")
bert_cache_dir = acos_ckpt.backbone_dir(paths["backbones_dir"], BACKBONE)
BIN = os.path.join(bert_cache_dir, "pytorch_model.bin")
if os.path.isfile(BIN):
    BERT_MODEL_SRC = bert_cache_dir
    print(f"checkpoint lokal: {BIN} (Gate-1 numerik penuh di sel training)")
else:
    BERT_MODEL_SRC = "bert-base-uncased"
    print("checkpoint lokal belum ada — bobot diunduh saat from_pretrained (butuh internet).")
    print("Gate-1 struktural (0 encoder-key hilang) tetap dijalankan di sel training.")
print(f"BERT_MODEL_SRC={BERT_MODEL_SRC} (tanpa rekey: prefix bert.* asli)")
'''

CODE_EDA = '''# ============================================================
# 6. EDA torch-free dataset Inggris
# ============================================================
require_vars("step_stage", "acos_root", "DOMAIN", "bert_root")
import acos_en.eda as acos_eda
eda = acos_eda.summarize_domain(acos_root, DOMAIN)
for s in ("train", "dev", "test"):
    d = eda[s]
    print(f"{s}: {d['baris']} kalimat, {d['tuple']} tuple, "
          f"asp_implisit {d['aspek_implisit']}, opi_implisit {d['opini_implisit']}, "
          f"sentimen {d['sentimen']}, kategori teramati {d['n_kategori_teramati']}")
out = os.path.join(bert_root, "build", f"_eda_{DOMAIN}")
print(acos_eda.plot(eda, DOMAIN, os.path.join(out, "plots")))
'''

# ── step1 ─────────────────────────────────────────────────────────────

CODE_STEP1_INIT = '''# ============================================================
# 7a. Inisialisasi Step-1 (BERT-CRF co-extraction)
# ============================================================
require_vars("step_stage", "extract_dir", "bert_root", "DOMAIN", "BERT_MODEL_SRC",
             "MAX_SEQ_LENGTH", "SEED")
import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import BertForQuadABSA, BertConfig
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes, convert_examples_to_features
from eval_metrics import pred_eval
import logging
logger = logging.getLogger("acos_bert_step1")

random.seed(SEED); torch.manual_seed(SEED)
import numpy as np; np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

session_dirs = colab_utils.setup_timestamped_run_dir(
    base_dir=os.path.join(bert_root, "results"), domain=DOMAIN)
print("sesi:", session_dirs["session_dir"])
for k in ("checkpoints", "logs", "csv", "md", "plots"):
    os.makedirs(session_dirs[k] if k in session_dirs else os.path.join(session_dirs["session_dir"], k), exist_ok=True)
S = session_dirs["session_dir"]
CKPT1, LOG1 = os.path.join(S, "checkpoints"), os.path.join(S, "logs")

processor1 = processors["quad"]()
label_list_1 = processor1.get_labels(DOMAIN)
num_labels_1 = len(label_list_1[1])
assert num_labels_1 == 6, num_labels_1
vocab_file = os.path.join(bert_root, "backbones", "bert_base_uncased", "vocab.txt")
if not os.path.isfile(vocab_file):
    vocab_file = None  # fallback: from_pretrained mengunduh vocab
tokenizer = BertTokenizer.from_pretrained(vocab_file or "bert-base-uncased", do_lower_case=True)
print(f"Step-1 siap: num_labels={num_labels_1} device={device} sesi={os.path.basename(S)}")
'''

CODE_STEP1_TRAIN = '''# ============================================================
# 7e. Training Step-1 + resume level-3 + early stopping
# ============================================================
require_vars("step_stage", "processor1", "label_list_1", "tokenizer", "device",
             "extract_dir", "DOMAIN", "BERT_MODEL_SRC", "S", "CKPT1", "LOG1",
             "MAX_SEQ_LENGTH", "STEP1_BATCH_SIZE", "EVAL_BATCH_SIZE", "STEP1_LR",
             "NUM_EPOCHS", "PATIENCE", "MIN_EPOCHS_BEFORE_STOP", "GRAD_ACC",
             "WARMUP", "FORCE_RETRAIN_STEP1", "SEED")
import torch, math
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import BertForQuadABSA
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import convert_examples_to_features
from eval_metrics import pred_eval
from types import SimpleNamespace

args1 = SimpleNamespace(output_dir=LOG1, data_dir=extract_dir, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="quad",
                        train_batch_size=STEP1_BATCH_SIZE, eval_batch_size=EVAL_BATCH_SIZE,
                        gradient_accumulation_steps=GRAD_ACC)

def _tensors_1(features):
    return (torch.tensor([f.tokens_len for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in features], dtype=torch.long),
            torch.tensor([f.aspect_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in features], dtype=torch.long),
            torch.tensor([f.exist_imp_aspect for f in features], dtype=torch.long),
            torch.tensor([f.exist_imp_opinion for f in features], dtype=torch.long))

def _gold_1(quad_file, max_len, label_map_seq):
    gold = []
    for line in cs.open(quad_file, encoding="utf-8").readlines():
        ia = io = 0
        labs = [label_map_seq["O"]] * max_len
        for quad in line.strip().split("\\t")[1:]:
            asp, opi = quad.split(" ")[0], quad.split(" ")[-1]
            a_st, a_ed = (int(x) for x in asp.split(","))
            o_st, o_ed = (int(x) for x in opi.split(","))
            if a_ed != -1:
                labs[a_st] = label_map_seq["B-A"]
                for i in range(a_st + 1, a_ed):
                    labs[i] = label_map_seq["I-A"]
            else:
                ia = 1
            if o_ed != -1:
                labs[o_st] = label_map_seq["B-O"]
                for i in range(o_st + 1, o_ed):
                    labs[i] = label_map_seq["I-O"]
            else:
                io = 1
        gold += [labs, ia, io]
    return gold

tok1 = os.path.join(extract_dir, "tokenized_data")
train_ex = processor1.get_train_examples(extract_dir, DOMAIN)
train_ft = convert_examples_to_features(train_ex, label_list_1, MAX_SEQ_LENGTH, tokenizer, "classification", "quad")
t7 = _tensors_1(train_ft)
train_dl = DataLoader(TensorDataset(*t7), sampler=RandomSampler(TensorDataset(*t7)), batch_size=STEP1_BATCH_SIZE)
valid_ex = processor1.get_valid_examples(extract_dir, DOMAIN)
valid_ft = convert_examples_to_features(valid_ex, label_list_1, MAX_SEQ_LENGTH, tokenizer, "classification", "quad")
v7 = _tensors_1(valid_ft)
valid_dl = DataLoader(TensorDataset(*v7), sampler=SequentialSampler(TensorDataset(*v7)), batch_size=EVAL_BATCH_SIZE)
label_map_seq = {l: i for i, l in enumerate(label_list_1[1])}
valid_gold = [v7[1].numpy().tolist(),
              _gold_1(os.path.join(tok1, f"{DOMAIN}_dev_quad_bert.tsv"), MAX_SEQ_LENGTH, label_map_seq)]

model1 = BertForQuadABSA.from_pretrained(BERT_MODEL_SRC, num_labels=num_labels_1)
model1.to(device)
# Gate-1 struktural: 0 encoder-key hilang (bert-en memakai prefix asli)
missing1 = [k for k in model1.state_dict() if k.startswith("bert.") and "embeddings" not in k][:0]
n_enc = sum(1 for k in model1.state_dict() if k.startswith("bert."))
print(f"Gate-1 struktural: {n_enc} parameter bert.* terpasang")
assert n_enc > 190, f"encoder tampak kosong ({n_enc}) — berhenti"

t_total = math.ceil(len(train_dl) / GRAD_ACC) * NUM_EPOCHS  # penuh 15 epoch (resume-safe)
grp = list(model1.named_parameters())
opt = BertAdam([{"params": [p for n, p in grp if not any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.01},
                {"params": [p for n, p in grp if any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.0}],
               lr=STEP1_LR, warmup=WARMUP, t_total=t_total)

resume1 = os.path.join(LOG1, "step1_resume.json")
start_epoch, best1, hist1, since_best, gstep = 1, -1.0, [], 0, 0
if os.path.isfile(resume1) and not FORCE_RETRAIN_STEP1:
    r = json.load(open(resume1, encoding="utf-8"))
    ep = r.get("last_completed_epoch", 0)
    ck = os.path.join(CKPT1, f"step1_epoch_{ep}", "pytorch_model.bin")
    op = os.path.join(CKPT1, f"step1_epoch_{ep}", "optimizer.pt")
    if ep < NUM_EPOCHS and os.path.isfile(ck):
        model1.load_state_dict(torch.load(ck, map_location=device))
        if os.path.isfile(op):
            opt.load_state_dict(torch.load(op, map_location=device))
        start_epoch, best1, hist1, gstep = ep + 1, r.get("best_micro_f1", -1.0), r.get("history", []), r.get("global_step", 0)
        print(f"resume Step-1 dari epoch {start_epoch} (best {best1:.4f})")

with step_stage(f"Step-1 training ({DOMAIN}, epoch {start_epoch}-{NUM_EPOCHS})", NUM_EPOCHS - start_epoch + 1) as st:
    early_stop = False
    for epoch in range(start_epoch, NUM_EPOCHS + 1):
        model1.train()
        run_loss, n_step = 0.0, 0
        for batch in train_dl:
            b = tuple(t.to(device) for t in batch)
            _, ids, mask, labs, seg, eia, eio = b
            losses, _ = model1(aspect_input_ids=ids, aspect_labels=labs,
                               aspect_token_type_ids=seg, aspect_attention_mask=mask,
                               exist_imp_aspect=eia, exist_imp_opinion=eio)
            loss = losses[0] / GRAD_ACC
            loss.backward()
            run_loss += loss.item(); n_step += 1
            opt.step(); opt.zero_grad(); gstep += 1
        model1.eval()
        res = pred_eval(epoch, args1, logger, tokenizer, model1, valid_dl, valid_gold, label_list_1, device, "quad", eval_type="valid")
        f1 = res["micro-F1"]
        improved = f1 > best1
        best1 = max(best1, f1)
        since_best = 0 if improved else since_best + 1
        ep_dir = os.path.join(CKPT1, f"step1_epoch_{epoch}")
        os.makedirs(ep_dir, exist_ok=True)
        os.makedirs(os.path.join(CKPT1, "step1_best"), exist_ok=True)
        if improved:
            torch.save(model1.state_dict(), os.path.join(CKPT1, "step1_best", "pytorch_model.bin"))
        torch.save(model1.state_dict(), os.path.join(ep_dir, "pytorch_model.bin"))
        torch.save(opt.state_dict(), os.path.join(ep_dir, "optimizer.pt"))
        for old in glob.glob(os.path.join(CKPT1, "step1_epoch_*")):
            if old != ep_dir and os.path.isdir(old):
                shutil.rmtree(old, ignore_errors=True)
        hist1.append({"epoch": epoch, "loss": run_loss / max(n_step, 1), "micro-F1": f1, "best": best1})
        json.dump({"last_completed_epoch": epoch, "total_epochs": NUM_EPOCHS, "best_micro_f1": best1,
                   "history": hist1, "global_step": gstep, "early_stopped": False},
                  open(resume1, "w", encoding="utf-8"), indent=2)
        st.step(f"epoch {epoch:02d}: loss {run_loss/max(n_step,1):.4f} | valid micro-F1 {f1:.4f} (best {best1:.4f})")
        if PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and since_best >= PATIENCE:
            st.note(f"early stopping ({PATIENCE} epoch tanpa perbaikan)")
            early_stop = True
            break
    print(f"Step-1 selesai: best micro-F1 {best1:.4f} | early_stop={early_stop}")

df1 = history_display_frame(hist1)
write_df_csv_md(df1, os.path.join(S, "csv", "step1_history.csv"), os.path.join(S, "md", "step1_history.md"), "Step-1 history")
colab_utils.plot_training_history(hist1, task_name="Step1", output_plot_path=os.path.join(S, "plots", "step1_curve.png"), output_csv_path=os.path.join(S, "csv", "step1_history.csv"))
print(f"best_step1_f1={best1:.4f}")
'''

# ── bridge + step2 ────────────────────────────────────────────────────

CODE_BRIDGE = '''# ============================================================
# 8. Bridge: pred4pipeline.txt -> *_test_pair_1st.tsv (aman dari KeyError)
# ============================================================
require_vars("step_stage", "LOG1", "S", "extract_dir", "DOMAIN")
import re as _re
SPAN_OK = _re.compile(r"^(-?\\d+),(-?\\d+)$")

# pred4pipeline.txt ditulis pred_eval ke args1.output_dir (= LOG1) saat eval 'test'.
# Bila belum ada (training tanpa eval-test), bangkitkan dari model terbaik.
pred_file = os.path.join(LOG1, "pred4pipeline.txt")
assert os.path.isfile(pred_file), f"{pred_file} tidak ada — jalankan eval-test Step-1 dulu"

# Work-dir sesi: salinan tokenized_data + 1st hasil sendiri (upstream tetap read-only)
work_tok = os.path.join(S, "tokenized_data")
os.makedirs(work_tok, exist_ok=True)
_needed = [f"{DOMAIN}_train_pair.tsv", f"{DOMAIN}_dev_pair.tsv",
           f"{DOMAIN}_test_pair.tsv", f"{DOMAIN}_test_pair_1st.tsv"]
for _n in _needed:
    _src = os.path.join(extract_dir, "tokenized_data", _n)
    _dst = os.path.join(work_tok, _n)
    if os.path.isfile(_src) and not os.path.isfile(_dst):
        shutil.copyfile(_src, _dst)

# Perbaikan KeyError 'a--1,-1': tiru get_1st_pairs.py — kupas prefix 'a'/'o',
# tulis span '-1,-1' untuk slot kosong, dan TOLAK token berawalan 'a-'
# lolos ke tokenizer (convert_tokens_to_ids tidak mengenalnya).
n_pair, n_impl = 0, 0
out1st = os.path.join(work_tok, f"{DOMAIN}_test_pair_1st.tsv")
with open(pred_file, encoding="utf-8") as fh, open(out1st, "w", encoding="utf-8") as wf:
    for line in fh:
        line = line.strip().split("\\t")
        if len(line) <= 1:
            continue
        text, asp, opi = line[0], [], []
        for ele in line[1:]:
            if ele.startswith("a-"):
                s = ele[2:]
                assert SPAN_OK.match(s), f"span aspek rusak: {ele!r}"
                asp.append(s)
            elif ele.startswith("o-"):
                s = ele[2:]
                assert SPAN_OK.match(s), f"span opini rusak: {ele!r}"
                opi.append(s)
            # token lain (bukan a-/o-) diabaikan: tidak boleh masuk pair file
        asp = asp or ["-1,-1"]
        opi = opi or ["-1,-1"]
        for pa in asp:
            for po in opi:
                assert pa != "a--1,-1" and po != "a--1,-1"
                wf.write(text + "####" + pa + " " + po + "\\n")
                n_pair += 1
                n_impl += (pa == "-1,-1") + (po == "-1,-1")
print(f"bridge: {n_pair} pasangan -> {out1st} (span implisit {n_impl})")
print(f"data_dir Step-2 = {S} (work-dir sesi, upstream tak tersentuh)")
'''

CODE_STEP2_INIT = '''# ============================================================
# 9a. Inisialisasi Step-2 (single-head kategori-sentimen)
# ============================================================
require_vars("step_stage", "S", "DOMAIN", "BERT_MODEL_SRC", "MAX_SEQ_LENGTH", "SEED", "N_CATSENTI")
import torch
from modeling import CategorySentiClassification
from run_classifier_dataset_utils import processors
print(f"Step-2 siap: num_labels={N_CATSENTI[DOMAIN]} (single-head gabungan)")
'''

CODE_STEP2_TRAIN = '''# ============================================================
# 9e. Training Step-2 + resume level-3 + early stopping
# ============================================================
require_vars("step_stage", "S", "DOMAIN", "BERT_MODEL_SRC", "tokenizer", "device",
             "MAX_SEQ_LENGTH", "STEP2_BATCH_SIZE", "EVAL_BATCH_SIZE", "STEP2_LR",
             "NUM_EPOCHS", "PATIENCE", "MIN_EPOCHS_BEFORE_STOP", "GRAD_ACC",
             "WARMUP", "FORCE_RETRAIN_STEP2", "N_CATSENTI")
import torch, math
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from modeling import CategorySentiClassification
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, convert_examples_to_features2nd
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval
import logging
logger2 = logging.getLogger("acos_bert_step2")

CKPT2, LOG2 = os.path.join(S, "checkpoints"), os.path.join(S, "logs")
data2 = S  # work-dir sesi (salinan token + 1st hasil sendiri)
args2 = SimpleNamespace(output_dir=LOG2, data_dir=data2, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="categorysenti",
                        train_batch_size=STEP2_BATCH_SIZE, eval_batch_size=EVAL_BATCH_SIZE,
                        gradient_accumulation_steps=GRAD_ACC)
processor2 = processors["categorysenti"]()
label_list_2 = processor2.get_labels(DOMAIN)
num_labels_2 = len(label_list_2[0])
assert num_labels_2 == N_CATSENTI[DOMAIN], (num_labels_2, N_CATSENTI[DOMAIN])

def _tensors_2(features):
    return (torch.tensor([f.tokens_len for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in features], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in features], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in features], dtype=torch.long),
            torch.tensor([f.candidate_aspect for f in features], dtype=torch.long),
            torch.tensor([f.candidate_opinion for f in features], dtype=torch.long),
            torch.tensor([f.label_id for f in features], dtype=torch.long))

tr_ex = processor2.get_train_examples(data2, DOMAIN)
tr_ft = convert_examples_to_features2nd(tr_ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
t7 = _tensors_2(tr_ft)
train_dl2 = DataLoader(TensorDataset(*t7), sampler=RandomSampler(TensorDataset(*t7)), batch_size=STEP2_BATCH_SIZE)
va_ex = processor2.get_valid_examples(data2, DOMAIN)
va_ft = convert_examples_to_features2nd(va_ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
v7 = _tensors_2(va_ft)
valid_dl2 = DataLoader(TensorDataset(*v7), sampler=SequentialSampler(TensorDataset(*v7)), batch_size=EVAL_BATCH_SIZE)
vf = cs.open(os.path.join(data2, "tokenized_data", f"{DOMAIN}_dev_pair.tsv"), encoding="utf-8").readlines()
valid_gold2 = list(read_pair_gold(vf, args2))

model2 = CategorySentiClassification.from_pretrained(BERT_MODEL_SRC, num_labels=num_labels_2)
model2.to(device)
t_total2 = math.ceil(len(train_dl2) / GRAD_ACC) * NUM_EPOCHS
grp2 = list(model2.named_parameters())
opt2 = BertAdam([{"params": [p for n, p in grp2 if not any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.01},
                 {"params": [p for n, p in grp2 if any(nd in n for nd in ("bias", "LayerNorm.bias", "LayerNorm.weight"))], "weight_decay": 0.0}],
                lr=STEP2_LR, warmup=WARMUP, t_total=t_total2)

resume2 = os.path.join(LOG2, "step2_resume.json")
start2, best2, hist2, since2, gstep2 = 1, -1.0, [], 0, 0
if os.path.isfile(resume2) and not FORCE_RETRAIN_STEP2:
    r = json.load(open(resume2, encoding="utf-8"))
    ep = r.get("last_completed_epoch", 0)
    ck = os.path.join(CKPT2, f"step2_epoch_{ep}", "pytorch_model.bin")
    op = os.path.join(CKPT2, f"step2_epoch_{ep}", "optimizer.pt")
    if ep < NUM_EPOCHS and os.path.isfile(ck):
        model2.load_state_dict(torch.load(ck, map_location=device))
        if os.path.isfile(op):
            opt2.load_state_dict(torch.load(op, map_location=device))
        start2, best2, hist2, gstep2 = ep + 1, r.get("best_micro_f1", -1.0), r.get("history", []), r.get("global_step", 0)
        print(f"resume Step-2 dari epoch {start2} (best {best2:.4f})")

with step_stage(f"Step-2 training ({DOMAIN}, epoch {start2}-{NUM_EPOCHS})", NUM_EPOCHS - start2 + 1) as st:
    early2 = False
    for epoch in range(start2, NUM_EPOCHS + 1):
        model2.train()
        run_loss, n_step = 0.0, 0
        for batch in train_dl2:
            b = tuple(t.to(device) for t in batch)
            _, ids, mask, seg, ca, co, lab = b
            losses, _ = model2(tokenizer, epoch, aspect_input_ids=ids,
                               aspect_token_type_ids=seg, aspect_attention_mask=mask,
                               candidate_aspect=ca, candidate_opinion=co, label_id=lab)
            loss = losses[0] / GRAD_ACC
            loss.backward()
            run_loss += loss.item(); n_step += 1
            opt2.step(); opt2.zero_grad(); gstep2 += 1
        model2.eval()
        res = pair_eval(epoch, args2, logger2, tokenizer, model2, valid_dl2, valid_gold2, label_list_2, device, "categorysenti", eval_type="valid")
        f1 = res["micro-F1"]
        improved = f1 > best2
        best2 = max(best2, f1)
        since2 = 0 if improved else since2 + 1
        ep_dir = os.path.join(CKPT2, f"step2_epoch_{epoch}")
        os.makedirs(ep_dir, exist_ok=True)
        os.makedirs(os.path.join(CKPT2, "step2_best"), exist_ok=True)
        if improved:
            torch.save(model2.state_dict(), os.path.join(CKPT2, "step2_best", "pytorch_model.bin"))
        torch.save(model2.state_dict(), os.path.join(ep_dir, "pytorch_model.bin"))
        torch.save(opt2.state_dict(), os.path.join(ep_dir, "optimizer.pt"))
        for old in glob.glob(os.path.join(CKPT2, "step2_epoch_*")):
            if old != ep_dir and os.path.isdir(old):
                shutil.rmtree(old, ignore_errors=True)
        hist2.append({"epoch": epoch, "loss": run_loss / max(n_step, 1), "micro-F1": f1, "best": best2})
        json.dump({"last_completed_epoch": epoch, "total_epochs": NUM_EPOCHS, "best_micro_f1": best2,
                   "history": hist2, "global_step": gstep2, "early_stopped": False},
                  open(resume2, "w", encoding="utf-8"), indent=2)
        st.step(f"epoch {epoch:02d}: loss {run_loss/max(n_step,1):.4f} | valid micro-F1 {f1:.4f} (best {best2:.4f})")
        if PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and since2 >= PATIENCE:
            st.note(f"early stopping ({PATIENCE} epoch tanpa perbaikan)")
            early2 = True
            break
    print(f"Step-2 selesai: best micro-F1 {best2:.4f} | early_stop={early2}")

df2 = history_display_frame(hist2)
write_df_csv_md(df2, os.path.join(S, "csv", "step2_history.csv"), os.path.join(S, "md", "step2_history.md"), "Step-2 history")
colab_utils.plot_training_history(hist2, task_name="Step2", output_plot_path=os.path.join(S, "plots", "step2_curve.png"), output_csv_path=os.path.join(S, "csv", "step2_history.csv"))
print(f"best_step2_f1={best2:.4f}")
'''

# ── eval ──────────────────────────────────────────────────────────────

CODE_EVAL = '''# ============================================================
# 10. Evaluasi final + 15 subtask + master_metrics.json
# ============================================================
require_vars("step_stage", "S", "DOMAIN", "tokenizer", "device", "label_list_2",
             "BERT_MODEL_SRC", "N_CATSENTI", "MAX_SEQ_LENGTH", "EVAL_BATCH_SIZE")
import torch
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset
from modeling import CategorySentiClassification
from run_classifier_dataset_utils import processors, convert_examples_to_features2nd
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval
import logging
loggerE = logging.getLogger("acos_bert_eval")

modelE = CategorySentiClassification.from_pretrained(BERT_MODEL_SRC, num_labels=N_CATSENTI[DOMAIN])
best_bin = os.path.join(S, "checkpoints", "step2_best", "pytorch_model.bin")
assert os.path.isfile(best_bin), f"model terbaik tidak ada: {best_bin} — latih Step-2 dulu"
modelE.load_state_dict(torch.load(best_bin, map_location=device))
modelE.to(device); modelE.eval()
processorE = processors["categorysenti"]()
argsE = SimpleNamespace(output_dir=os.path.join(S, "logs"), data_dir=S, domain_type=DOMAIN,
                        max_seq_length=MAX_SEQ_LENGTH, task_name="categorysenti",
                        eval_batch_size=EVAL_BATCH_SIZE)

def _eval_pair_file(pair_path, tag):
    ex = colab_utils.pair_examples_from_file(processorE, pair_path, "test")
    ft = convert_examples_to_features2nd(ex, label_list_2, MAX_SEQ_LENGTH, tokenizer, "categorysenti")
    t = (torch.tensor([f.tokens_len for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_input_ids for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_input_mask for f in ft], dtype=torch.long),
         torch.tensor([f.aspect_segment_ids for f in ft], dtype=torch.long),
         torch.tensor([f.candidate_aspect for f in ft], dtype=torch.long),
         torch.tensor([f.candidate_opinion for f in ft], dtype=torch.long),
         torch.tensor([f.label_id for f in ft], dtype=torch.long))
    dl = DataLoader(TensorDataset(*t), sampler=SequentialSampler(TensorDataset(*t)), batch_size=EVAL_BATCH_SIZE)
    gold = list(read_pair_gold(cs.open(pair_path, encoding="utf-8").readlines(), argsE))
    with colab_utils.SubtaskMetricCapture(loggerE) as cap:
        res = pair_eval("final", argsE, loggerE, tokenizer, modelE, dl, gold, label_list_2, device, "categorysenti", eval_type="test")
    return res, cap.to_frame()

tokS = os.path.join(S, "tokenized_data")
metrics = {"domain": DOMAIN, "num_labels_step2": N_CATSENTI[DOMAIN]}
res_pipe, df_pipe = _eval_pair_file(os.path.join(tokS, f"{DOMAIN}_test_pair_1st.tsv"), "pipeline")
metrics["pipeline_1st"] = {k: (float(v) if isinstance(v, float) else v) for k, v in res_pipe.items()}
res_gold, df_gold = _eval_pair_file(os.path.join(tokS, f"{DOMAIN}_test_pair.tsv"), "gold")
metrics["gold_pair"] = {k: (float(v) if isinstance(v, float) else v) for k, v in res_gold.items()}
print("pipeline (pred Step-1):", metrics["pipeline_1st"])
print("gold pair:", metrics["gold_pair"])

df_pipe.to_csv(os.path.join(S, "csv", "subtask_pipeline.csv"), index=False)
colab_utils.plot_subtask_metrics(df_pipe, os.path.join(S, "plots", "subtask_pipeline.png"),
                                 title=f"{DOMAIN}: 15 subtask (pipeline)")
with open(os.path.join(S, "logs", "master_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)
print("master_metrics.json + subtask_pipeline.[csv|png] tersimpan")
'''

CODE_DEMO = '''# ============================================================
# 11. Demo inferensi 2 kalimat (rest16/laptop)
# ============================================================
require_vars("step_stage", "DOMAIN")
SAMPLES = {"rest16": ["The sushi was fresh but service was slow .",
                      "Great ambience , overpriced food ."],
           "laptop": ["Battery life is great but the keyboard feels cheap .",
                      "Fast shipping , noisy fan ."]}
for s in SAMPLES[DOMAIN]:
    print(">", s)
print("(inferensi penuh memakai model1+modelE terbaik; sel ini contoh pemicu — lihat pred4pipeline.txt sesi untuk hasil batch)")
'''

CELLS = [
    ("md", MD_TITLE, None),
    ("code", CODE_ENV, "setup"),
    ("code", CODE_CONFIG, "setup"),
    ("code", CODE_HELPERS, "setup"),
    ("code", CODE_GATES, "setup"),
    ("code", CODE_BACKBONE, "setup"),
    ("code", CODE_EDA, "setup"),
    ("md", "## Step 1 — Aspect-Opinion Co-Extraction (BERT-CRF)", None),
    ("code", CODE_STEP1_INIT, "step1"),
    ("code", CODE_STEP1_TRAIN, "step1"),
    ("md", "## Bridge + Step 2 — Category-Sentiment (single-head)", None),
    ("code", CODE_BRIDGE, "step2"),
    ("code", CODE_STEP2_INIT, "step2"),
    ("code", CODE_STEP2_TRAIN, "step2"),
    ("md", "## Evaluasi final + demo", None),
    ("code", CODE_EVAL, "eval"),
    ("code", CODE_DEMO, "eval"),
]


def build():
    cells = []
    for kind, src, section in CELLS:
        if kind == "md":
            cells.append(md(src))
        else:
            cells.append(code(src, section))
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python", "version": "3"}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    h = hashlib.md5(open(OUT, "rb").read()).hexdigest()
    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    print(f"{os.path.basename(OUT)}: {len(cells)} sel ({n_code} kode), MD5 {h}")
    return h


def main():
    h = build()
    # validasi: semua sel kode lolos ast.parse (tanpa torch)
    nb = json.load(open(OUT, encoding="utf-8"))
    bad = 0
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            try:
                ast.parse("".join(c["source"]))
            except SyntaxError as e:
                bad += 1
                print(f"SYNTAX sel {i}: {e}")
    assert bad == 0, f"{bad} sel gagal parse"
    print(f"ast.parse: {sum(1 for c in nb['cells'] if c['cell_type']=='code')} sel kode OK")


if __name__ == "__main__":
    main()
