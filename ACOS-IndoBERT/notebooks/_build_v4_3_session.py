"""Bangun notebook V4.3 (kebijakan sesi HM + 60 mnt) dari V4.2 GUARDS.

Perubahan V4.3 (menjawab "result output DDMMYYYY_HM, rentang 1 jam"):
  sel 9  : REQUIRED_UTILS + 2 simbol baru (ensure_session_dir_hm,
           find_nearest_session_hm) — kontrak lama 21 simbol tetap lolos.
  sel 16 : session_dirs_from_root + kunci "reports".
  sel 18 : kebijakan sesi V4.3 — pakai ulang sesi HM terdekat <= 60 mnt,
           selain itu buat baru <domain>_DDMMYYYY_HHMM (+ suffix _01 bila
           tabrakan menit); tulis session_manifest.json + REPORT_INDEX.md.
           Fallback ke fungsi lama bila salinan colab_utils belum diperbarui.

Idempoten: DST ditulis ulang dari SRC setiap dijalankan.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipynb")
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_3_SESSION.ipynb")


def to_source(text):
    lines = text.splitlines(keepends=True)
    out = []
    for ln in lines:
        out.append(ln if ln.endswith("\n") else ln + "\n")
    if out and out[-1].endswith("\n"):
        out[-1] = out[-1][:-1]
    return out


def find_code(cells, *needles, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "code":
            continue
        if all(n in "".join(c["source"]) for n in needles):
            return i
    raise LookupError("sel %r tidak ketemu" % (needles,))


MD_CHANGELOG = """
---

### Versi V4.3 — Kebijakan sesi DDMMYYYY_HM + jendela 60 menit

Menjawab permintaan folder hasil: nama sesi kini `<domain>_DDMMYYYY_HHMM`
(presisi menit, cth `appsid_12092026_1045`; format lama `..._HHMMSS` tetap
dibaca). Saat startup, sesi domain yang sama dengan cap waktu **<= 60 menit**
yang terbaru dipakai ulang (lanjutkan run Colab yang terputus; tabel/csv,
grafik, pickle, json tetap satu paket laporan). Di luar jendela itu dibuat
folder baru (tabrakan menit -> suffix `_01`, `_02`).

| Kontrol | Default | Arti |
|---|---|---|
| `RESUME_LAST_SESSION` | True | False = selalu sesi baru |
| `SESSION_REUSE_WINDOW_MIN` | 60 | 0 = selalu sesi baru (mode arsip per-run) |
| `FORCE_NEW_SESSION` | False | True = selalu sesi baru walau ada yang <= 60 mnt |

Artefak laporan per sesi: `csv/` (tabel), `plots/` (grafik 300 DPI),
`md/` (laporan), `logs/` (json: `master_metrics.json`, `step*_run_result.json`,
`result.txt`), `pipeline_state.pkl` + `session_manifest.json` (root),
`reports/REPORT_INDEX.md` (indeks hitung berkas per jenis).
"""

CELL_18_V43 = '''# Kandidat lokasi pencarian sesi terdahulu. Hanya di bawah indo_root: sesi milik
# pipeline Inggris memakai folder lain dan tidak boleh ikut dipilih, karena
# checkpoint-nya memakai vocab yang berbeda.
candidate_result_roots = [
    results_base,
    os.path.join(indo_root, "Output", "results"),
    "/content/drive/MyDrive/ACOS-IndoBERT/results",
    "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results",
    "/content/drive/MyDrive/ACOS-ASLI/ACOS-IndoBERT/results",
]

# --- V4.3: kebijakan sesi DDMMYYYY_HM + jendela 60 menit --------------------
# Dalam jendela -> PAKAI ULANG (run terputus lanjut; artefak laporan satu paket).
# Di luar jendela -> BUAT BARU <domain>_DDMMYYYY_HHMM. Set 0/True untuk arsip.
SESSION_REUSE_WINDOW_MIN = 60
FORCE_NEW_SESSION = False

_session_meta = {"domain": DOMAIN, "policy": "V4_3_HM_60MIN"}
session_dirs = None
if RESUME_LAST_SESSION and not FORCE_NEW_SESSION and SESSION_REUSE_WINDOW_MIN > 0:
    _roots = [r for r in candidate_result_roots if r and os.path.isdir(r)]
    _best = None
    for _base in _roots:
        try:
            if hasattr(colab_utils, "find_nearest_session_hm"):
                _hit = colab_utils.find_nearest_session_hm(
                    _base, DOMAIN, SESSION_REUSE_WINDOW_MIN)
            else:
                _root = find_resumable_session([_base], DOMAIN)
                _hit = {"path": _root, "name": os.path.basename(_root),
                        "delta_min": 0.0} if _root else None
            if _hit and (_best is None or _hit["delta_min"] < _best["delta_min"]):
                _best = _hit
        except Exception:
            continue
    if _best is not None:
        session_dirs = session_dirs_from_root(_best["path"])
        _session_meta.update({"reused": True, "nearest": _best["name"],
                              "delta_min": round(_best.get("delta_min", 0.0), 1)})
        print("Reuse sesi HM terdekat: %s (Δ %.1f mnt)" % (
            _best["path"], _best.get("delta_min", 0.0)))
        print("   Artefak kunci terdeteksi: %d/6" % session_cache_score(_best["path"]))
if session_dirs is None:
    if hasattr(colab_utils, "ensure_session_dir_hm") and not FORCE_NEW_SESSION:
        try:
            session_dirs = colab_utils.ensure_session_dir_hm(
                results_base, DOMAIN, SESSION_REUSE_WINDOW_MIN,
                RESUME_LAST_SESSION, FORCE_NEW_SESSION)
            _session_meta.update({"reused": False, "root": session_dirs["root"]})
        except Exception:
            session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)
    else:
        session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)
    print("Sesi baru: %s" % session_dirs["root"])

# Verifikasi integritas dan izin simpan sesi
verify_session_save_paths(session_dirs, domain=DOMAIN)

# 2. Backbone cache di bawah indo_root/backbones, satu folder per backbone
#    (nama dari _backbone_dirname() di sel 3). Isinya diunduh & direkey di sel 4c
#    — di sini hanya path-nya yang ditetapkan.
bert_cache_dir = os.path.join(backbones_dir, _backbone_dirname(BACKBONE))
os.makedirs(bert_cache_dir, exist_ok=True)

if BACKBONE == "bert-en":
    # Jalur kontrol: fungsi V2 apa adanya, tanpa rekey.
    download_bert_pretrained(target_dir=bert_cache_dir)
else:
    _n_ada = sum(1 for _f in ("config.json", "pytorch_model.bin", "vocab.txt")
                 if os.path.exists(os.path.join(bert_cache_dir, _f)))
    print("Backbone dir : %s (%d/3 berkas ada)" % (bert_cache_dir, _n_ada))
    print("   Unduh & rekey dilakukan di sel 4c (jangan pakai download_bert_pretrained "
          "untuk IndoBERT — fungsi itu selalu mengunduh bert-base-uncased).")

print("\\nActive Session Folder: %s" % session_dirs["root"])
plots_dir = session_dirs["plots"]
csv_dir = session_dirs["csv"]
md_dir = session_dirs["md"]
logs_dir = session_dirs["logs"]
reports_dir = session_dirs.get("reports", os.path.join(session_dirs["root"], "reports"))
os.makedirs(reports_dir, exist_ok=True)

# Manifest + indeks laporan (dipakai penyusun laporan penelitian)
try:
    _session_meta.update({"session_root": session_dirs["root"]})
    with open(os.path.join(session_dirs["root"], "session_manifest.json"),
              "w", encoding="utf-8") as _mf:
        json.dump(_session_meta, _mf, indent=2, ensure_ascii=False, default=str)
    _idx = ["# Indeks Artefak Laporan", "",
            "Root sesi: `%s`" % session_dirs["root"], ""]
    for _label, _key, _ext in (("tabel/csv", "csv", ".csv"),
                               ("grafik", "plots", ".png"),
                               ("laporan md", "md", ".md"),
                               ("log/json", "logs", ".json")):
        _d = session_dirs.get(_key, "")
        _n = sum(1 for _f in os.listdir(_d) if _f.lower().endswith(_ext)) \\
            if _d and os.path.isdir(_d) else 0
        _idx.append("| %s | `%s` | %d |" % (_label, _key, _n))
    with open(os.path.join(reports_dir, "REPORT_INDEX.md"),
              "w", encoding="utf-8") as _rf:
        _rf.write("\\n".join(_idx) + "\\n")
except Exception as _e_manifest:
    print("manifest/indeks dilewati: %s" % (_e_manifest,))
'''


def main():
    nb = json.load(open(SRC, encoding="utf-8"))
    cells = nb["cells"]
    if any("V4.3" in "".join(c.get("source", [])) for c in cells):
        raise RuntimeError("SRC sudah V4.3?")
    cells[0]["source"] = to_source("".join(cells[0]["source"]) + "\n" + MD_CHANGELOG)

    i9 = find_code(cells, "REQUIRED_UTILS")
    s9 = "".join(cells[i9]["source"])
    if "ensure_session_dir_hm" not in s9:
        s9 = s9.replace(
            '"verify_session_save_paths", "find_resumable_session", "auto_find_file",',
            '"verify_session_save_paths", "find_resumable_session", "auto_find_file",\n'
            '    "ensure_session_dir_hm", "find_nearest_session_hm",')
        cells[i9]["source"] = to_source(s9)

    i16 = find_code(cells, "def session_dirs_from_root")
    s16 = "".join(cells[i16]["source"])
    if '"reports"' not in s16:
        s16 = s16.replace(
            '"logs": os.path.join(run_dir, "logs"),',
            '"logs": os.path.join(run_dir, "logs"),\n'
            '        "reports": os.path.join(run_dir, "reports"),')
        cells[i16]["source"] = to_source(s16)

    i18 = find_code(cells, "candidate_result_roots", "find_resumable_session")
    cells[i18]["source"] = to_source(CELL_18_V43)

    nb.setdefault("metadata", {}).setdefault("acos", {})["pipeline_version"] = "V4_3_SESSION"
    json.dump(nb, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("V4.2=%d -> V4.3=%d" % (
        len(json.load(open(SRC, encoding="utf-8"))["cells"]), len(cells)))
    print("DST=%s" % DST)


if __name__ == "__main__":
    main()
