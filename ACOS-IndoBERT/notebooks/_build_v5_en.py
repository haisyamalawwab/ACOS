"""Membangun 00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP.ipynb dari V4_1.

V5 = V4_1 yang dikhususkan untuk dataset asli Inggris di folder root `data/`:
  - DOMAIN   : 'rest16' | 'laptop'  (default 'rest16')
  - BACKBONE : 'bert-en' (bert-base-uncased, selalu; dipaksa seperti kontrol V4)
  - Sumber data mentah : <repo>/data/Restaurant-ACOS/ & <repo>/data/Laptop-ACOS/
  - tokenized_data     : dibangun ulang dari data mentah itu ke
                         <indo_root>/v5_en/tokenized_data/ via
                         acos_id.tokenize_data.build + vocab bert_cache_dir
                         (terverifikasi: quad_bert identik 100% dengan berkas
                         Extract-Classify-ACOS/tokenized_data/ yang lama)

Yang berubah dibanding V4_1 (bedah sel, bukan rewrite):
  sel 0   : tambahan seksi changelog V5
  sel 11  : data_root menunjuk root data/ (V5_RAW_*), bukan indo_root/data
  sel 13  : konfigurasi V5 (DOMAIN/BACKBONE default, peta subfolder, validasi)
  sel 4e  : (BARU, setelah gate 4d) gerbang data Inggris V5 Root-data -> tokenized
  sel 16  : komentar resume disesuaikan (sesi V5 rest16_/laptop_ memang di indo_root)

Seluruh pola V4_1 dipertahankan: step_stage, require_vars, cache per tahap,
folder sesi bertimestamp, tabel master_*, plot 300 DPI, pred4pipeline.txt,
pipeline_state.pkl, session_manifest.json, live inference.

Skrip idempoten: berkas tujuan ditulis ulang dari nol setiap dijalankan.
"""

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb")
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V5_EN_REST16_LAPTOP.ipynb")


def find_code(cells, *needles, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if all(n in src for n in needles):
            return i
    raise LookupError("Sel kode dengan penanda %r tidak ditemukan" % (needles,))


def as_lines(src):
    if isinstance(src, list):
        return src
    return src.splitlines(keepends=True)


def to_source(text):
    lines = text.splitlines(keepends=True)
    out = []
    for ln in lines:
        out.append(ln if ln.endswith("\n") else ln + "\n")
    # notebook JSON biasanya tanpa newline di baris terakhir
    if out and out[-1].endswith("\n"):
        out[-1] = out[-1][:-1]
    return out


MD_TITLE_V5 = """
---

### Versi V5 — Dataset asli Inggris Rest16 & Laptop dari folder root `data/`

Turunan langsung dari `00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb`
(referensi utama), dibangun oleh `_build_v5_en.py`. Seluruh pola V4_1
dipertahankan — sel bertahap `step_stage`, cache per tahap, folder sesi
bertimestamp, tabel `master_*`, plot 300 DPI, `pred4pipeline.txt`,
`pipeline_state.pkl`, `session_manifest.json`, live inference — hanya
**domain, backbone, dan sumber data** yang dikhususkan ke Inggris.

| Aspek | V4_1 (referensi) | V5 (ini) |
|---|---|---|
| Domain | `appsid` (target) + `rest16`/`laptop` (kontrol) | `rest16` / `laptop` saja |
| Backbone | IndoBERT (`appsid`) / `bert-en` (kontrol) | `bert-en` selalu (`bert-base-uncased`) |
| Sumber data mentah | `ACOS-IndoBERT/data/Apps-ACOS/` (ID) | folder root `data/Restaurant-ACOS/` & `data/Laptop-ACOS/` |
| `tokenized_data` | `ACOS-IndoBERT/tokenized_data/` (ID) / `Extract-Classify-ACOS/tokenized_data/` (kontrol, apa adanya) | dibangun ulang dari root `data/` ke `ACOS-IndoBERT/v5_en/tokenized_data/` (sel 4e) |
| Kategori Step 2 | 13 (ID, datar) | 13 (`rest16`, `ENTITAS#ATRIBUT`) / 121 (`laptop`) |
| `num_labels` Step 2 | 39 | 39 (`rest16`) / 363 (`laptop`) |
| Folder sesi | `results/appsid_<ts>/` (target) | `results/rest16_<ts>/` / `results/laptop_<ts>/` |

Sel baru dibanding V4_1:

| Sel | Isi | Torch? |
|---|---|---|
| 4e | Gerbang data Inggris: validasi root `data/`, build/verify `tokenized_data` V5 dari `bert_cache_dir`/vocab, `tokenized_base` diarahkan ke cache V5 | tidak |

Catatan verifikasi (lokal, `probe_v5.py`): rebuild `*_quad_bert.tsv` dari root
`data/` dengan vocab `bert-base-uncased` menghasilkan berkas **identik 100%**
dengan `Extract-Classify-ACOS/tokenized_data/` lama untuk semua split
`rest16` + `laptop` — root `data/` adalah sumber kebenaran, bukan salinan basi.

Sel 4c (adapter IndoBERT), 4d (gate Indonesia), dan 5d2 (Gate 1 numerik)
dipertahankan apa adanya: semuanya melewati dirinya sendiri untuk domain
Inggris, sehingga notebook tetap 1-klik tanpa cabang manual.
"""

# --- Pengganti sel 13 (konfigurasi V5) ---------------------------------------
CELL_13_V5 = '''# ============================================================
#  Konfigurasi V5 — Inggris asli Rest16 & Laptop dari folder root data/
# ============================================================
# Pilihan Domain Dataset (folder root data/):
#   'rest16'  -> data/Restaurant-ACOS (13 kategori, num_labels Step 2 = 39)
#   'laptop'  -> data/Laptop-ACOS     (121 kategori, num_labels Step 2 = 363)
DOMAIN = "rest16"

# Backbone V5 selalu Inggris. Nilai lain ditolak di bawah (bukan dipaksa
# diam-diam) supaya sesi V5 tidak pernah tercampur vocab IndoBERT.
#   'bert-en' -> bert-base-uncased (satu-satunya backbone V5)
BACKBONE = "bert-en"

# Subfolder dataset mentah di bawah folder root data/ (lihat sel 2c-V5:
# v5_data_root). Nama file di dalamnya: <prefix>_quad_<split>.tsv,
# dengan prefix 'rest16' / 'laptop'.
V5_RAW_SUBDIR = {
    "rest16": "Restaurant-ACOS",
    "laptop": "Laptop-ACOS",
}
V5_RAW_PREFIX = {
    "rest16": "rest16",
    "laptop": "laptop",
}

# Hyperparameter Pelatihan
MAX_SEQ_LENGTH = 128
STEP1_BATCH_SIZE = 32
STEP2_BATCH_SIZE = 32
STEP1_LR = 2e-5
STEP2_LR = 5e-5
NUM_EPOCHS = 15      # 15 epoch optimal untuk Colab GPU T4/A100 (Default paper: 30)
SEED = 42

# Mode per-epoch: jumlah epoch yang dilatih dalam satu kali eksekusi sel training.
# 0 = jalankan semua epoch sekaligus (perilaku lama).
# 1 = train 1 epoch, simpan state, berhenti — untuk lanjut di sesi Colab berikutnya.
MAX_EPOCHS_THIS_RUN = 1

# Mixed Precision (AMP): akselerasi FP16 pada T4/A100 via tensor core.
# Nonaktifkan (False) hanya jika GradScaler menyebabkan NaN pada optimizer lama.
USE_AMP = True

# Early Stopping: berhenti jika F1 tidak membaik selama N epoch berturut-turut
# (menghemat waktu Colab saat training sudah plateau). Set PATIENCE = 0 untuk
# menonaktifkan early stopping.
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5  # Training minimal jalan N epoch dulu sebelum early stopping aktif

# do_lower_case WAJIB True untuk bert-base-uncased.
DO_LOWER_CASE = True

_DOMAIN_NORM = str(DOMAIN).lower()
if _DOMAIN_NORM not in ("rest16", "laptop"):
    raise ValueError(
        "V5 hanya mendukung DOMAIN='rest16' atau 'laptop' "
        "(sumber: folder root data/Restaurant-ACOS & data/Laptop-ACOS). "
        "Diterima: %r. Untuk 'appsid' pakai notebook V4_1." % (DOMAIN,))
DOMAIN = _DOMAIN_NORM
if BACKBONE != "bert-en":
    raise ValueError(
        "V5 hanya mendukung BACKBONE='bert-en' (bert-base-uncased). "
        "Diterima: %r." % (BACKBONE,))

# Satu folder cache untuk backbone V5. Kunci dipertahankan sama seperti V4_1
# supaya sel pemulihan state (_backbone_dirname) tetap kompatibel.
BACKBONE_DIRNAME = {
    "indobert": "indobert_base_p1",
    "indobert-large": "indobert_large_p1",
    "bert-en": "bert_base_uncased",
}


def _backbone_dirname(backbone=None):
    """Nama folder cache untuk sebuah backbone; dipakai juga sel pemulihan state."""
    key = backbone or globals().get("BACKBONE") or "bert-en"
    return BACKBONE_DIRNAME.get(key, str(key).replace("-", "_"))


# `tokenized_base` adalah argumen `data_dir` yang diberikan ke processor upstream.
# Processor menyusun sendiri `<data_dir>/tokenized_data/<domain>_...`,
# Nilai awal di sini menunjuk repo upstream (yang berkasnya sudah identik
# dengan rebuild — lihat catatan verifikasi di sel judul); sel 4e (gerbang
# data V5) membangun cache dari root data/ dan MENGARAHKAN ULANG variabel
# global ini ke <indo_root>/v5_en. Jangan menimpa manual setelah sel 4e.
tokenized_base = extract_dir
print(f"📚 tokenized_base (awal, pra-gate 4e) : {tokenized_base}")

# Reproducibility seeding
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

active_save_dir = indo_root

# Sesi dilanjutkan bila ada artefak tersimpan; set False untuk memaksa sesi baru.
RESUME_LAST_SESSION = True

# 1. Direktori sesi. Seluruhnya di bawah indo_root — repo pipeline Inggris tidak
#    pernah menerima artefak run (sesi V5 rest16_/laptop_ tinggal berdampingan
#    dengan sesi V4 appsid_ dan tidak tertukar karena prefiks DOMAIN berbeda).
results_base = os.path.join(indo_root, "results")

print(f"🇬🇧 Domain   : {DOMAIN} ({V5_RAW_SUBDIR[DOMAIN]} | {V5_RAW_PREFIX[DOMAIN]}_quad_*.tsv)")
print(f"🧠 Backbone : {BACKBONE} (bert-base-uncased)")
print(f"📁 Sesi     : {results_base}/{DOMAIN}_<timestamp>/")
'''

# --- Tambahan sel 11: resolusi root data/ V5 ----------------------------------
CELL_11_V5_APPEND = '''
# --- V5: akar dataset Inggris di folder root data/ (bukan indo_root/data) ----
# V4_1 menaruh data Indonesia di <indo_root>/data; V5 membaca dataset asli
# Inggris dari folder root <acos_root>/data (Drive: .../ACOS/data atau
# .../ACOS-ASLI/data; lokal: ./data). Blok ini tidak mengubah indo_root,
# backbones_dir, atau results — hanya data_root + dua peta V5.
V5_RAW_SUBDIR = {
    "rest16": "Restaurant-ACOS",
    "laptop": "Laptop-ACOS",
}
V5_RAW_PREFIX = {
    "rest16": "rest16",
    "laptop": "laptop",
}


def _v5_resolve_data_root(acos_root=None, base_project_dir=None):
    """Folder root data/ yang memuat Restaurant-ACOS/ & Laptop-ACOS/."""
    kandidat = []
    for _base in (acos_root, base_project_dir):
        if _base:
            kandidat.append(os.path.join(_base, "data"))
    kandidat += [
        "/content/drive/MyDrive/ACOS/data",
        "/content/drive/MyDrive/ACOS-ASLI/data",
        os.path.abspath("data"),
        os.path.abspath(os.path.join("..", "data")),
        os.path.abspath(os.path.join("..", "..", "data")),
    ]
    for _d in kandidat:
        if _d and os.path.isdir(os.path.join(_d, "Restaurant-ACOS")):
            return os.path.abspath(_d)
    # fallback: data/ pertama yang ada walau Restaurant-ACOS belum lengkap
    for _d in kandidat:
        if _d and os.path.isdir(_d):
            return os.path.abspath(_d)
    return os.path.abspath(kandidat[2] if len(kandidat) > 2 else "data")


v5_data_root = _v5_resolve_data_root(
    acos_root=globals().get("acos_root"),
    base_project_dir=globals().get("base_project_dir"))
data_root = v5_data_root  # V5: EDA-ID (tak terpakai) & gate memakai path ini
print(f"🇬🇧 v5_data_root (root data/) : {v5_data_root}")
for _dom, _sub in V5_RAW_SUBDIR.items():
    _p = os.path.join(v5_data_root, _sub)
    print(f"   {_dom:6s} -> {_p} {'✅' if os.path.isdir(_p) else '❌ HILANG'}")
'''

MD_4E = """### 4e. Gerbang Data Inggris V5 — Root `data/` → `tokenized_data` (wajib sebelum training)

Membangun (atau memverifikasi) `tokenized_data/<domain>_{train,dev,test}_{quad_bert,pair}.tsv`
dari dataset **asli** di folder root `data/` memakai `vocab.txt` di `bert_cache_dir`,
lalu mengarahkan ulang global `tokenized_base` ke cache V5
(`<indo_root>/v5_en/`). Cache dipakai ulang antar sesi (CACHE HIT) kecuali berkas
mentah lebih baru atau `FORCE_REBUILD_EN_DATA=True`.

Sel ini torch-free dan aman diulang. Wajib dijalankan ulang setelah restart kernel
(seperti sel 1b/1s) sebelum melompat ke Step 1/2, karena `tokenized_base` adalah
variabel runtime.
"""

CELL_4E_V5 = '''require_vars("step_stage", "DOMAIN", "bert_cache_dir", "session_dirs")

# Set True untuk membangun ulang tokenized_data V5 dari nol.
FORCE_REBUILD_EN_DATA = False

with step_stage("4e. Gerbang data Inggris V5 (root data/ -> tokenized_data)", 7) as st:
    _dom = str(DOMAIN).lower()
    st.step(f"Domain: {_dom}")
    if _dom not in ("rest16", "laptop"):
        raise ValueError(
            "V5 hanya mendukung DOMAIN='rest16'/'laptop'. Diterima: %r" % (DOMAIN,))

    # 1. Lokasi dataset mentah (folder root data/)
    _v5_sub = {"rest16": "Restaurant-ACOS", "laptop": "Laptop-ACOS"}[_dom]
    _v5_pref = _dom
    _raw_candidates = [
        os.path.join(globals().get("v5_data_root", ""), _v5_sub),
        os.path.join(globals().get("acos_root", ""), "data", _v5_sub),
        os.path.join(globals().get("base_project_dir", ""), "data", _v5_sub),
        os.path.join("/content/drive/MyDrive/ACOS/data", _v5_sub),
        os.path.join("/content/drive/MyDrive/ACOS-ASLI/data", _v5_sub),
    ]
    raw_dir = next((d for d in _raw_candidates if d and os.path.isdir(d)), None)
    if raw_dir is None:
        raise FileNotFoundError(
            "Folder dataset mentah '%s' tidak ditemukan. Dicoba: %s. "
            "Pastikan folder root data/ (Restaurant-ACOS/, Laptop-ACOS/) ada di "
            "Drive (../ACOS/data) atau lokal (./data)." % (_v5_sub, _raw_candidates))
    st.step(f"Sumber mentah : {raw_dir}")
    for _sp in ("train", "dev", "test"):
        _rf = os.path.join(raw_dir, f"{_v5_pref}_quad_{_sp}.tsv")
        if not os.path.isfile(_rf):
            raise FileNotFoundError(f"Berkas mentah hilang: {_rf}")
        st.note(f"✔ {_v5_pref}_quad_{_sp}.tsv ({os.path.getsize(_rf) / 1024:.1f} KB)")

    # 2. Vocab tokenizer (bert-base-uncased hasil cache sel 3/16)
    _vocab = os.path.join(bert_cache_dir, "vocab.txt")
    if not os.path.isfile(_vocab):
        raise FileNotFoundError(
            f"vocab.txt belum ada di {bert_cache_dir}. Jalankan sel sesi (3) "
            f"lebih dulu — backbone bert-en diunduh di sana.")
    st.step(f"Vocab         : {_vocab}")

    # 3. Cache V5 (bersama untuk rest16+laptop; nama berkas sudah berprefiks domain)
    v5_base = os.path.join(globals().get("indo_root", os.path.abspath(".")),
                           "v5_en")
    v5_tok_dir = os.path.join(v5_base, "tokenized_data")
    os.makedirs(v5_tok_dir, exist_ok=True)
    st.step(f"Cache V5      : {v5_tok_dir}")

    _wants = [f"{_v5_pref}_{sp}_{kind}.tsv"
              for sp in ("train", "dev", "test")
              for kind in ("quad_bert", "pair")]
    _missing = [w for w in _wants if not os.path.isfile(os.path.join(v5_tok_dir, w))]
    _raw_mtime = max(os.path.getmtime(os.path.join(raw_dir, f"{_v5_pref}_quad_{sp}.tsv"))
                     for sp in ("train", "dev", "test"))
    _cache_mtime = (min(os.path.getmtime(os.path.join(v5_tok_dir, w))
                        for w in _wants) if not _missing else -1)
    _stale = (not _missing) and (_cache_mtime < _raw_mtime)

    if _missing:
        st.step(f"Cache belum lengkap — kurang {len(_missing)} berkas: {', '.join(_missing[:3])}...")
    elif _stale:
        st.step("Cache lebih lama dari data mentah — akan dibangun ulang.")
    else:
        st.step(f"Cache lengkap ({len(_wants)} berkas) dan lebih baru dari data mentah.")

    if (not _missing) and (not _stale) and (not FORCE_REBUILD_EN_DATA):
        st.step("CACHE HIT — build dilewati, cache V5 dipakai apa adanya.")
        v5_report = {"cache_hit": True, "domain": _dom,
                     "sumber": raw_dir, "keluaran": v5_tok_dir}
    else:
        st.step("Membangun tokenized_data dari data mentah (retokenisasi WordPiece + remap span)...")
        from bert_utils.tokenization import BertTokenizer as _V5BT
        try:
            from acos_id import tokenize_data as _v5td
            _tok = _V5BT.from_pretrained(bert_cache_dir, do_lower_case=True)
            st.note(f"Tokenizer: {len(_tok.vocab):,} entri vocab")
            v5_report = _v5td.build(_tok, raw_dir, v5_tok_dir, domain=_v5_pref)
        except ImportError:
            # Fallback tanpa acos_id: logika retokenisasi yang sama, mandiri.
            import collections as _coll

            def _retokenize(_tok, _text, _quads):
                _words = _text.strip().split()
                _pieces, _s0, _e0 = [], [], []
                for _w in _words:
                    _sub = _tok.tokenize(_w) or ["[UNK]"]
                    _s0.append(len(_pieces))
                    _pieces.extend(_sub)
                    _e0.append(len(_pieces))

                def _remap(_span):
                    _a, _b = _span.split(",")
                    _s, _e = int(_a), int(_b)
                    if _s < 0 or _e < 0:
                        return _span
                    if _s >= len(_words) or _e > len(_words):
                        return None
                    if _e <= _s:
                        return f"{_s0[_s]},{_s0[_s] + 1}"
                    return f"{_s0[_s]},{_e0[_e - 1]}"

                _nq = []
                for _q in _quads:
                    _p = _q.split(" ")
                    if len(_p) != 4:
                        continue
                    _na, _no = _remap(_p[0]), _remap(_p[3])
                    if _na is None or _no is None:
                        continue
                    _nq.append(f"{_na} {_p[1]} {_p[2]} {_no}")
                return " ".join(_pieces), _nq

            _tok = _V5BT.from_pretrained(bert_cache_dir, do_lower_case=True)
            v5_report = {"domain": _dom, "sumber": raw_dir,
                         "keluaran": v5_tok_dir, "split": {}}
            for _sp in ("train", "dev", "test"):
                _in = os.path.join(raw_dir, f"{_v5_pref}_quad_{_sp}.tsv")
                _qo = os.path.join(v5_tok_dir, f"{_v5_pref}_{_sp}_quad_bert.tsv")
                _po = os.path.join(v5_tok_dir, f"{_v5_pref}_{_sp}_pair.tsv")
                _n_bar = _n_quad = 0
                _pairs = _coll.OrderedDict()
                with open(_in, encoding="utf-8") as _fin, \\
                        open(_qo, "w", encoding="utf-8", newline="\\n") as _fq:
                    for _raw in _fin:
                        _raw = _raw.rstrip("\\n")
                        if not _raw.strip():
                            continue
                        _parts = _raw.split("\\t")
                        _nt, _nq = _retokenize(_tok, _parts[0], _parts[1:])
                        if not _nq:
                            continue
                        _n_bar += 1
                        _n_quad += len(_nq)
                        _fq.write(_nt + "\\t" + "\\t".join(_nq) + "\\n")
                        for _q in _nq:
                            _a, _c, _s, _o = _q.split(" ")
                            _k = (_nt, _a, _o)
                            _pairs.setdefault(_k, [])
                            _lbl = f"{_c}#{_s}"
                            if _lbl not in _pairs[_k]:
                                _pairs[_k].append(_lbl)
                with open(_po, "w", encoding="utf-8", newline="\\n") as _fp:
                    for (_t, _a, _o), _lbls in _pairs.items():
                        _fp.write(f"{_t}####{_a} {_o}\\t{' '.join(_lbls)}\\n")
                v5_report["split"][_sp] = {"baris": _n_bar, "quad": _n_quad,
                                           "pair": len(_pairs)}
        for _sp, _s in v5_report.get("split", {}).items():
            if isinstance(_s, dict):
                st.step(f"{_sp:5s}: {_s.get('baris', 0):,} baris | "
                        f"{_s.get('quad', 0):,} quad | {_s.get('pair', 0):,} pair")

    # 4. Verifikasi akhir + arahkan tokenized_base ke cache V5
    for _w in _wants:
        _fp = os.path.join(v5_tok_dir, _w)
        if not os.path.isfile(_fp) or os.path.getsize(_fp) == 0:
            raise RuntimeError(f"Hasil V5 tidak lengkap: {_fp}")
    globals()["tokenized_base"] = v5_base
    tokenized_base = v5_base
    st.step(f"tokenized_base → {tokenized_base} (global diperbarui)")

    _gate_json = os.path.join(session_dirs["logs"], "v5_en_gate.json")
    with open(_gate_json, "w", encoding="utf-8") as _jf:
        json.dump({"domain": _dom, "raw_dir": raw_dir, "v5_base": v5_base,
                   "report": v5_report}, _jf, indent=2, ensure_ascii=False, default=str)
    st.step(f"Laporan gate → {_gate_json}")

    try:
        _rows = [{"Split": sp,
                  "Baris": s.get("baris", 0), "Quad": s.get("quad", 0),
                  "Pair": s.get("pair", 0)}
                 for sp, s in v5_report.get("split", {}).items()
                 if isinstance(s, dict)]
        if _rows and "export_step_table" in globals():
            _df_gate = pd.DataFrame(_rows)
            export_step_table(_df_gate, name="master_00c_gerbang_data_en",
                              csv_dir=csv_dir, md_dir=md_dir,
                              title=f"Gerbang Data Inggris V5 ({_dom})")
            if "rep" in globals():
                rep.table(_df_gate, caption="Build/verify tokenized_data V5 per split")
            st.step("Tabel master_00c ditulis")
    except Exception as _e_tab:
        st.note(f"Tabel laporan dilewati: {_e_tab}")

    try:
        if "update_mcp_manifest" in globals():
            update_mcp_manifest("EN_DATA_GATE_PASSED", 1,
                                {"num_labels_step2": len(label_list_step2[0])
                                 if "label_list_step2" in globals()
                                 and globals()["label_list_step2"] else None})
    except Exception:
        pass
'''


def main():
    nb = json.load(open(SRC, encoding="utf-8"))
    cells = nb["cells"]
    print("Sel sumber (V4_1): %d" % len(cells))

    # 1. Judul: tambah changelog V5
    if not "".join(cells[0]["source"]).strip().startswith("# 00."):
        raise RuntimeError("Sel 0 bukan judul master pipeline; sumber berubah?")
    cells[0]["source"] = to_source("".join(cells[0]["source"]) + "\n" + MD_TITLE_V5)
    # sesuaikan baris versi di judul: PRO Version -> V5
    # (ringan: hanya header, isi 11 poin tetap karena pipeline-nya sama)
    print("  [ok] sel 0: changelog V5 ditambahkan")

    # 2. Sel 11 (dua root): append resolusi root data/ V5
    i11 = find_code(cells, "Dua root: indo_root (ditulis)", "acos_id")
    if 'v5_data_root' in "".join(cells[i11]["source"]):
        print("  [skip] sel 11 sudah memuat blok V5")
    else:
        cells[i11]["source"] = to_source(
            "".join(cells[i11]["source"]) + "\n" + CELL_11_V5_APPEND)
        print("  [ok] sel %d: blok v5_data_root ditambahkan" % i11)

    # 3. Sel 13 (konfigurasi): ganti penuh dengan konfigurasi V5
    i13 = find_code(cells, "Konfigurasi V4", "DOMAIN")
    old13 = "".join(cells[i13]["source"])
    assert 'DOMAIN = "appsid"' in old13, "Penanda DOMAIN appsid tidak ketemu di sel 13"
    cells[i13]["source"] = to_source(CELL_13_V5)
    print("  [ok] sel %d: konfigurasi diganti V5 (DOMAIN rest16/laptop, BACKBONE bert-en)" % i13)

    # 4. Sel 16 (resume+sesi): sesuaikan komentar sesi Inggris
    i16 = find_code(cells, "candidate_result_roots", "find_resumable_session")
    s16 = "".join(cells[i16]["source"])
    s16 = s16.replace(
        "# Kandidat lokasi pencarian sesi terdahulu. Hanya di bawah indo_root: sesi milik\n"
        "# pipeline Inggris memakai folder lain dan tidak boleh ikut dipilih, karena\n"
        "# checkpoint-nya memakai vocab yang berbeda.",
        "# Kandidat lokasi pencarian sesi terdahulu (V5: sesi Inggris rest16_/laptop_\n"
        "# tinggal di bawah indo_root/results berdampingan dengan sesi V4 appsid_;\n"
        "# prefiks DOMAIN membuat find_resumable_session() tidak pernah tertukar,\n"
        "# dan seluruh sesi V5 memakai vocab bert-base-uncased yang sama).")
    cells[i16]["source"] = to_source(s16)
    print("  [ok] sel %d: komentar resume disesuaikan V5" % i16)

    # 5. Sisipkan sel 4e setelah gate 4d
    i4d = find_code(cells, "4d. Gerbang data Indonesia (5 gate torch-free)")
    md_cell = {"cell_type": "markdown", "metadata": {},
               "source": to_source(MD_4E)}
    code_cell = {"cell_type": "code", "metadata": {},
                 "execution_count": None, "outputs": [],
                 "source": to_source(CELL_4E_V5)}
    # cegah duplikasi bila builder dijalankan dua kali (DST dibaca? tidak — SRC
    # selalu V4_1 murni, jadi cukup pastikan belum ada penanda di cells)
    if any("4e. Gerbang data Inggris V5" in "".join(c.get("source", []))
           for c in cells if c["cell_type"] == "code"):
        raise RuntimeError("Sel 4e V5 sudah ada di sumber — sumber bukan V4_1 murni?")
    cells.insert(i4d + 1, code_cell)
    cells.insert(i4d + 1, md_cell)
    print("  [ok] sel 4e (markdown+code) disisipkan setelah sel %d" % i4d)

    # 6. Metadata notebook: tandai V5
    nb.setdefault("metadata", {}).setdefault("acos", {})["pipeline_version"] = "V5_EN_REST16_LAPTOP"

    json.dump(nb, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Sel hasil (V5): %d" % len(cells))
    print("Ditulis: %s" % DST)


if __name__ == "__main__":
    main()
