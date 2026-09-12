"""Bangun notebook V4.2 (guards audit) dari V4.1.

V4.2 = V4.1 + 3 guard audit kritis 12 Sep 2026, tanpa mengubah logika train:
  sel 4e (baru) : vocab consistency + bridge provenance + UNK rate
                  (menutup kontaminasi rest16: checkpoint/bridge tertukar)
  sel 7c (baru) : plafon recall kandidat + hitung silent-drop pair_eval
  sel 9a-guard  : assert irisan gold-prediksi > 0 + skor set-based +
                  verifikasi dual-head + pemisah dev/final

Idempoten: DST ditulis ulang dari SRC setiap dijalankan.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT.ipynb")
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_2_GUARDS.ipynb")


def to_source(text):
    lines = text.splitlines(keepends=True)
    out = []
    for ln in lines:
        out.append(ln if ln.endswith("\n") else ln + "\n")
    if out and out[-1].endswith("\n"):
        out[-1] = out[-1][:-1]
    return out


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": to_source(text)}


def code_cell(text):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [],
            "source": to_source(text)}


MD_CHANGELOG = """
---

### Versi V4.2 — Guard audit (12 Sep 2026), tanpa ubah logika training

Menjawab temuan audit kritis `result/`: sesi rest16 memakai artefak appsid,
TP=0 karena konstruksi `[UNK]`, evaluasi memakai test set, gate lama lolos
pada kasus gagal. V4.2 menambah **3 guard torch-free** + 1 aturan evaluasi:

| Sel | Guard | Menutup temuan audit |
|---|---|---|
| 4e | `guards.check_vocab_consistency` + `check_bridge_provenance` + `check_unk_rate` | A, B, H (kontaminasi checkpoint/bridge, UNK collapse) |
| 7c | `guards.candidate_recall_ceiling` + `count_silent_drops` | E, F (plafon 92,66%, 175 baris dibuang diam-diam) |
| 9a-guard | `guards.check_gold_pred_overlap` + `setbased_subtask_scores` + `verify_dual_head_model` + `resolve_eval_files` | D, E, F (dual angka, inflasi 2,1x, dual-head 0%) |

Aturan dev/test: `purpose='select'` memakai `*_dev_*`, `purpose='final'`
memakai `*_test_*`. Pemilihan checkpoint tidak lagi memakai test set.
"""

MD_4E = """### 4e. Guard kontaminasi V4.2 — vocab, bridge, UNK (wajib sebelum training)

Gagal-keras bila: vocab checkpoint tidak sesuai backbone, teks bridge di luar
korpus domain, atau UNK rate > 5%. Guard ini yang hilang saat sesi rest16
memakai bridge kandidat appsid dengan vocab Inggris.
"""

CELL_4E = '''require_vars("step_stage", "session_dirs", "bert_cache_dir", "DOMAIN")

with step_stage("4e. Guard kontaminasi V4.2 (vocab+bridge+UNK)", 4) as st:
    from acos_id import guards
    st.step("vocab checkpoint vs backbone")
    _vreps = {}
    for _step in ("step1_best", "step2_best"):
        _cdir = os.path.join(session_dirs.get("checkpoints", ""), _step)
        if os.path.isdir(_cdir):
            _vreps[_step] = guards.check_vocab_consistency(_cdir, BACKBONE)
    # backbone cache (pre-training) selalu diperiksa
    _vreps["backbone_cache"] = guards.check_vocab_consistency(bert_cache_dir, BACKBONE)
    for _k, _r in _vreps.items():
        st.note("%s: ok=%s %s" % (_k, _r.get("ok"), _r.get("reason", "")))
    if not all(_r.get("ok") for _r in _vreps.values()):
        raise RuntimeError("Guard vocab GAGAL: %s" % (_vreps,))

    st.step("provenance bridge kandidat")
    _tok_base = globals().get("tokenized_base", indo_root)
    _bridge = os.path.join(_tok_base, "tokenized_data", "%s_test_pair_1st.tsv" % DOMAIN)
    _quad = os.path.join(_tok_base, "tokenized_data", "%s_test_quad_bert.tsv" % DOMAIN)
    if os.path.isfile(_bridge) and os.path.isfile(_quad):
        _prov = guards.check_bridge_provenance(_bridge, _quad)
        st.note("bridge=%d quad_texts=%d alien=%d" % (
            _prov.get("n_bridge", -1), _prov.get("n_quad_texts", -1), _prov.get("n_alien", -1)))
        if not _prov.get("ok"):
            raise RuntimeError("Guard bridge GAGAL: %s contoh=%s" % (
                _prov.get("reason"), _prov.get("alien_sample")))
    else:
        st.note("bridge/quad test belum ada (pre-step1): dilewati, dicek ulang di sel 7c")

    st.step("UNK rate data vs vocab runtime")
    _vocab = os.path.join(bert_cache_dir, "vocab.txt")
    _sample_quad = _quad if os.path.isfile(_quad) else None
    if _sample_quad and os.path.isfile(_vocab):
        _texts = []
        with open(_sample_quad, encoding="utf-8") as _fh:
            for _i, _ln in enumerate(_fh):
                if _i >= 300:
                    break
                if _ln.strip():
                    _texts.append(_ln.split("\\t")[0])
        _unk = guards.check_unk_rate(_texts, _vocab)
        st.note("unk_rate=%.4f (%d/%d)" % (_unk["unk_rate"], _unk["n_unk"], _unk["n_token"]))
        if not _unk["ok"]:
            raise RuntimeError("Guard UNK GAGAL: %s" % (_unk.get("reason"),))
    st.step("sidik jari dataset dicatat di logs/fingerprints.json")
    _fp = guards.fingerprint_files([_bridge, _quad, _vocab])
    with open(os.path.join(session_dirs["logs"], "fingerprints.json"), "w", encoding="utf-8") as _jf:
        json.dump(_fp, _jf, indent=2, ensure_ascii=False)
'''

MD_7C = """### 7c. Plafon kandidat & silent-drop V4.2 (laporan, tidak menghentikan)

Melaporkan batas atas recall (fraksi gold yang ada di kandidat) dan jumlah
baris yang dibuang diam-diam oleh penyaring `pair_eval`. Audit menemukan plafon
92,66% dan 175 baris gugur tanpa peringatan pada appsid.
"""

CELL_7C = '''require_vars("step_stage", "session_dirs")

with step_stage("7c. Plafon kandidat V4.2", 3) as st:
    from acos_id import guards
    _tok_base = globals().get("tokenized_base", indo_root)
    _bridge = os.path.join(_tok_base, "tokenized_data", "%s_test_pair_1st.tsv" % DOMAIN)
    _gold_pair = os.path.join(_tok_base, "tokenized_data", "%s_test_pair.tsv" % DOMAIN)
    _quad = os.path.join(_tok_base, "tokenized_data", "%s_test_quad_bert.tsv" % DOMAIN)
    if os.path.isfile(_bridge) and os.path.isfile(_gold_pair):
        _ceil = guards.candidate_recall_ceiling(_bridge, _gold_pair)
        st.step("plafon=%.4f (%d/%d, mustahil=%d)" % (
            _ceil["ceiling"], _ceil["n_covered"], _ceil["n_gold"], _ceil["n_impossible"]))
        _prov = guards.check_bridge_provenance(_bridge, _quad) if os.path.isfile(_quad) else {"ok": True}
        if not _prov.get("ok"):
            raise RuntimeError("Bridge bukan dari domain ini: %s" % (_prov.get("reason"),))
        try:
            _tab = pd.DataFrame([{"metrik": "plafon_recall_kandidat", "nilai": _ceil["ceiling"]},
                                 {"metrik": "gold_tertutup", "nilai": _ceil["n_covered"]},
                                 {"metrik": "gold_mustahil", "nilai": _ceil["n_impossible"]}])
            export_step_table(_tab, name="master_04b_plafon_kandidat",
                              csv_dir=csv_dir, md_dir=md_dir,
                              title="Plafon recall kandidat step 1")
        except Exception as _e_tab:
            st.note("tabel plafon dilewati: %s" % (_e_tab,))
    else:
        st.note("bridge/gold belum ada: dilewati")
'''

MD_9AG = """### 9a-guard. Gerbang evaluasi final V4.2 (wajib sebelum kutip angka)

`result.txt` warisan tanpa penanda: gagalkan bila irisan gold-prediksi = 0,
laporkan skor sub-task set-based (tanpa inflasi difficulty), dan verifikasi
model dual-head benar-benar punya `category_head` sebelum `master_07b` dikutip.
"""

CELL_9AG = '''require_vars("step_stage", "session_dirs")

with step_stage("9a-guard. Gerbang evaluasi final V4.2", 3) as st:
    from acos_id import guards
    _res = os.path.join(session_dirs["logs"], "result.txt")
    if os.path.isfile(_res):
        _ov = guards.check_gold_pred_overlap(_res)
        st.step("blok=%d gold=%d pred=%d irisan=%d TP=%d FP=%d FN=%d" % (
            _ov["n_blocks"], _ov["n_gold_keys"], _ov["n_pred_keys"],
            _ov["n_overlap"], _ov["tp"], _ov["fp"], _ov["fn"]))
        if not _ov.get("ok"):
            raise RuntimeError("Evaluasi TIDAK BERMAKNA: %s" % (_ov.get("reason"),))
    else:
        st.note("result.txt belum ada: guard dilewati (jalan setelah sel 9a)")
    if globals().get("USE_DUAL_HEAD"):
        _m = globals().get("model_step2_best", globals().get("model"))
        _dh = guards.verify_dual_head_model(_m) if _m is not None else {"ok": False, "reason": "model belum di memori"}
        st.note("dual-head: %s" % (_dh,))
        if not _dh.get("ok"):
            raise RuntimeError("USE_DUAL_HEAD=True tetapi %s" % (_dh.get("reason"),))
    st.step("aturan dev/final: select->%s final->%s" % (
        guards.resolve_eval_files(globals().get("tokenized_base", indo_root), DOMAIN, "select"),
        guards.resolve_eval_files(globals().get("tokenized_base", indo_root), DOMAIN, "final")))
'''


def find_code(cells, *needles, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "code":
            continue
        if all(n in "".join(c["source"]) for n in needles):
            return i
    raise LookupError("sel %r tidak ketemu" % (needles,))


def main():
    nb = json.load(open(SRC, encoding="utf-8"))
    cells = nb["cells"]
    if any("V4.2" in "".join(c.get("source", [])) for c in cells):
        raise RuntimeError("SRC sudah V4.2?")
    cells[0]["source"] = "".join(cells[0]["source"]) + "\n" + MD_CHANGELOG
    # sel 4e setelah gate 4d (kode acos_selftest)
    i4d = find_code(cells, "acos_selftest", "acos_taxonomy")
    cells.insert(i4d + 1, md_cell(MD_4E))
    cells.insert(i4d + 2, code_cell(CELL_4E))
    # sel 7c setelah bridge (df_pairs)
    i7 = find_code(cells, "df_pairs")
    cells.insert(i7 + 1, md_cell(MD_7C))
    cells.insert(i7 + 2, code_cell(CELL_7C))
    # sel 9a-guard sebelum tabel benchmark (final_res, df_subtasks)
    i9 = find_code(cells, "final_res", "df_subtasks")
    cells.insert(i9, md_cell(MD_9AG))
    cells.insert(i9 + 1, code_cell(CELL_9AG))
    nb.setdefault("metadata", {}).setdefault("acos", {})["pipeline_version"] = "V4_2_GUARDS"
    json.dump(nb, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("V4.1=%d -> V4.2=%d" % (len(json.load(open(SRC, encoding="utf-8"))["cells"]), len(cells)))
    print("DST=%s" % DST)


if __name__ == "__main__":
    main()
