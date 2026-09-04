"""Gerbang verifikasi untuk lapisan Indonesia — dijalankan sebelum training.

Setiap gate mengembalikan `{"gate": nama, "ok": bool, "detail": {...}}`.
`run_gates()` menjalankan yang diminta dan gagal keras bila ada yang merah,
karena semua kegagalan yang ditangani di sini bersifat **senyap**: pipeline tetap
berjalan sampai selesai dan hanya menghasilkan angka yang salah.

Gate yang butuh torch dipisah (`weights`), sisanya torch-free sehingga bisa
dijalankan di laptop tanpa paket ML.
"""
from __future__ import annotations

import collections
import json
import os
import sys

from . import build_acos, taxonomy

TORCH_FREE_GATES = ("taxonomy", "dataset", "acos_build", "tokenized", "gate2_english")
ALL_GATES = TORCH_FREE_GATES + ("weights",)

RE_KNOWN_DEFECT = {
    "rest16_train_pair.tsv": 1,
}
"""Jumlah **kalimat** yang boleh berbeda pada gate 2, per berkas.

`data/Restaurant-ACOS/rest16_quad_train.tsv` baris 451 memuat span opini
lebar-nol `3,3`, dan berkas `tokenized_data` di repo memetakan baris itu secara
tidak konsisten: `*_quad_bert.tsv` memakai remap yang benar (`3,4`, `9,10`,
`16,17`) sementara `*_pair.tsv` memakai offset dari revisi lain (`3,5`, `10,11`)
dan kehilangan satu pasangan. Generator mengikuti berkas quad — yang dipakai
Step 1 — jadi selisih pada satu kalimat `rest16_train_pair.tsv` adalah cacat data
upstream, bukan cacat generator.

Toleransinya dinyatakan dalam satuan kalimat, bukan baris: satu baris ekstra
menggeser seluruh sisa berkas, sehingga hitungan per-baris melaporkan 1.684
"perbedaan" untuk satu kalimat yang cacat.
"""


def _group_pair_by_sentence(lines):
    """`{teks: [(span, label), ...]}` dari baris `*_pair.tsv`, urutan dijaga."""
    out = collections.OrderedDict()
    for line in lines:
        if not line.strip():
            continue
        left, _, labels = line.partition("\t")
        text, _, span = left.partition("####")
        out.setdefault(text, []).append((span, labels))
    return out


def _compare_files(gen_lines, repo_lines, *, per_sentence: bool):
    """Bandingkan dua berkas; kembalikan ringkasan selisih.

    Berkas quad sejajar satu-baris-per-kalimat dengan sumbernya, jadi
    perbandingan baris demi baris sudah tepat. Berkas pair punya jumlah baris
    variabel per kalimat, jadi dikelompokkan dulu supaya satu kalimat cacat tidak
    tampak seperti ribuan baris cacat.
    """
    if not per_sentence:
        beda = sum(1 for x, y in zip(gen_lines, repo_lines) if x != y)
        beda += abs(len(gen_lines) - len(repo_lines))
        return {"satuan": "baris", "n_generator": len(gen_lines),
                "n_repo": len(repo_lines), "n_beda": beda, "contoh": []}

    A = _group_pair_by_sentence(gen_lines)
    B = _group_pair_by_sentence(repo_lines)
    beda = []
    for text in A:
        if text not in B:
            beda.append({"teks": text[:70], "sebab": "hanya ada di generator"})
        elif A[text] != B[text]:
            beda.append({"teks": text[:70],
                         "generator": [s for s, _ in A[text]],
                         "repo": [s for s, _ in B[text]]})
    for text in B:
        if text not in A:
            beda.append({"teks": text[:70], "sebab": "hanya ada di repo"})
    return {"satuan": "kalimat", "n_generator": len(A), "n_repo": len(B),
            "n_beda": len(beda), "contoh": beda[:3],
            "baris_generator": len(gen_lines), "baris_repo": len(repo_lines)}


def _gate(name, ok, **detail):
    return {"gate": name, "ok": bool(ok), "detail": detail}


def gate_taxonomy(paths) -> dict:
    """13 kategori kode == 13 kategori `label_maps.json`, urutan sama."""
    rep = taxonomy.verify_against_label_maps(paths["data_root"])
    return _gate("taxonomy", rep["ok"],
                 label_maps=rep["path"],
                 n_kategori=rep.get("n_categories"),
                 num_labels_step2=rep.get("n_catsenti"),
                 num_labels_step1=taxonomy.num_labels_step1(),
                 selisih=rep["diff"])


def gate_dataset(paths) -> dict:
    """Berkas sumber ada, dan `review_id` antar split benar-benar terpisah."""
    processed = os.path.join(paths["data_root"], taxonomy.DATASET_DIRNAME, "processed")
    wajib = ["label_maps.json", "quintuples_weak.csv", "reviews_clean.csv"] + \
            list(build_acos.SPLIT_FILES.values())
    hilang = [f for f in wajib if not os.path.exists(os.path.join(processed, f))]
    detail = {"processed": processed, "berkas_hilang": hilang}
    if hilang:
        return _gate("dataset", False, **detail)

    ids = build_acos.read_split_ids(processed)
    detail["n_review_per_split"] = {k: len(v) for k, v in ids.items()}
    tumpang = {}
    names = list(ids)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            n = len(ids[a] & ids[b])
            if n:
                tumpang[f"{a}∩{b}"] = n
    detail["tumpang_tindih_review_id"] = tumpang
    return _gate("dataset", not tumpang, **detail)


def _span_roundtrip(path: str, limit: int = None) -> dict:
    """Cek tiap span di berkas quad benar-benar menunjuk token yang ada.

    Bukan sekadar memeriksa angkanya masuk rentang: span yang bergeser satu token
    tetap "valid" secara numerik, jadi yang diperiksa adalah `ed > st`,
    `ed <= len(tokens)`, dan span implisit tepat `-1,-1`.
    """
    rep = collections.Counter()
    contoh_gagal = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if limit and lineno > limit:
                break
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                rep["baris_tanpa_quad"] += 1
                continue
            toks = parts[0].split()
            rep["baris"] += 1
            for quad in parts[1:]:
                f = quad.split(" ")
                rep["quad"] += 1
                if len(f) != 4:
                    rep["quad_kolom_salah"] += 1
                    continue
                if f[1] not in taxonomy.CATEGORIES and "#" not in f[1]:
                    rep["kategori_asing"] += 1
                if f[2] not in taxonomy.SENTIMENTS:
                    rep["sentimen_asing"] += 1
                for kind, span in (("aspek", f[0]), ("opini", f[3])):
                    st_s, ed_s = span.split(",")
                    st, ed = int(st_s), int(ed_s)
                    if st == -1 and ed == -1:
                        rep[kind + "_implisit"] += 1
                        continue
                    if st < 0 or ed <= st or ed > len(toks):
                        rep[kind + "_span_rusak"] += 1
                        if len(contoh_gagal) < 5:
                            contoh_gagal.append(
                                {"baris": lineno, "jenis": kind, "span": span,
                                 "n_token": len(toks), "teks": parts[0][:70]})
                    else:
                        rep[kind + "_eksplisit"] += 1
    out = dict(rep)
    out["contoh_gagal"] = contoh_gagal
    out["ok"] = not (rep["aspek_span_rusak"] or rep["opini_span_rusak"]
                     or rep["quad_kolom_salah"] or rep["kategori_asing"]
                     or rep["sentimen_asing"])
    return out


def gate_acos_build(paths, *, rebuild: bool = False) -> dict:
    """`appsid_quad_<split>.tsv` ada dan seluruh span-nya menunjuk token nyata."""
    out_dir = os.path.join(paths["data_root"], taxonomy.DATASET_DIRNAME)
    berkas = {s: os.path.join(out_dir, f"{taxonomy.DOMAIN}_quad_{s}.tsv")
              for s in ("train", "dev", "test")}
    detail = {"berkas": berkas}

    if rebuild or not all(os.path.exists(p) for p in berkas.values()):
        detail["konversi"] = build_acos.build(paths["data_root"], out_dir)

    per_split = {}
    ok = True
    for split, path in berkas.items():
        if not os.path.exists(path):
            per_split[split] = {"ok": False, "error": "tidak ada"}
            ok = False
            continue
        r = _span_roundtrip(path)
        per_split[split] = r
        ok &= r["ok"]
    detail["per_split"] = per_split
    return _gate("acos_build", ok, **detail)


def gate_tokenized(paths, *, vocab_dir: str = None, out_dir: str = None,
                   rebuild: bool = False) -> dict:
    """`tokenized_data` Indonesia: span tetap valid setelah retokenisasi WordPiece.

    Juga membandingkan jumlah quad sebelum/sesudah — retokenisasi tidak boleh
    membuang tuple. Ini yang menangkap span yang hilang karena pemecahan subword
    salah hitung.
    """
    from . import tokenize_data

    vocab_dir = vocab_dir or paths.get("bert_cache_dir")
    out_dir = out_dir or paths.get("tokenized_dir")
    detail = {"vocab_dir": vocab_dir, "out_dir": out_dir}
    if not vocab_dir or not os.path.exists(os.path.join(vocab_dir, "vocab.txt")):
        return _gate("tokenized", False,
                     error=f"vocab.txt tidak ada di {vocab_dir}", **detail)

    src_dir = os.path.join(paths["data_root"], taxonomy.DATASET_DIRNAME)
    berkas = {s: os.path.join(out_dir, f"{taxonomy.DOMAIN}_{s}_quad_bert.tsv")
              for s in ("train", "dev", "test")}
    if rebuild or not all(os.path.exists(p) for p in berkas.values()):
        tokenizer = tokenize_data.load_legacy_tokenizer(
            vocab_dir, acos_root=paths.get("acos_root"))
        detail["generator"] = {
            k: v for k, v in tokenize_data.build(
                tokenizer, src_dir, out_dir, domain=taxonomy.DOMAIN).items()
            if k != "split"}

    ok = True
    per_split = {}
    for split, path in berkas.items():
        if not os.path.exists(path):
            per_split[split] = {"ok": False, "error": "tidak ada"}
            ok = False
            continue
        r = _span_roundtrip(path)
        raw = os.path.join(src_dir, f"{taxonomy.DOMAIN}_quad_{split}.tsv")
        if os.path.exists(raw):
            n_raw = sum(len(l.rstrip("\n").split("\t")) - 1
                        for l in open(raw, encoding="utf-8") if l.strip())
            r["quad_sebelum_retokenisasi"] = n_raw
            r["quad_hilang"] = n_raw - r.get("quad", 0)
            if r["quad_hilang"]:
                r["ok"] = False
        pair = os.path.join(out_dir, f"{taxonomy.DOMAIN}_{split}_pair.tsv")
        r["pair_ada"] = os.path.exists(pair)
        if not r["pair_ada"]:
            r["ok"] = False
        per_split[split] = r
        ok &= r["ok"]
    detail["per_split"] = per_split
    return _gate("tokenized", ok, **detail)


def gate_gate2_english(paths, *, en_vocab_dir: str = None, work_dir: str = None) -> dict:
    """Gate 2 PRD: regenerasi data Inggris harus identik dengan berkas repo.

    Ini satu-satunya bukti bahwa generator memang mereproduksi konvensi offset
    upstream, bukan konvensi yang kita karang sendiri. Dijalankan dengan vocab
    `bert-base-uncased` pada `data/Restaurant-ACOS/`.
    """
    from . import tokenize_data

    en_vocab_dir = en_vocab_dir or paths.get("en_vocab_dir") or paths.get("bert_en_dir")
    work_dir = work_dir or os.path.join(paths.get("work_dir", "."), "_gate2_en")
    detail = {"en_vocab_dir": en_vocab_dir, "work_dir": work_dir}
    if not en_vocab_dir or not os.path.exists(os.path.join(en_vocab_dir, "vocab.txt")):
        return _gate("gate2_english", False,
                     error=f"vocab bert-base-uncased tidak ada di {en_vocab_dir}", **detail)

    repo_dir = os.path.join(paths["extract_dir"], "tokenized_data")
    src_dir = os.path.join(paths.get("en_data_root") or paths["data_root"],
                           "Restaurant-ACOS")
    if not os.path.exists(os.path.join(src_dir, "rest16_quad_train.tsv")):
        return _gate("gate2_english", False,
                     error=f"data Inggris tidak ada di {src_dir}", **detail)

    tokenizer = tokenize_data.load_legacy_tokenizer(
        en_vocab_dir, acos_root=paths.get("acos_root"))
    gen_dir = os.path.join(work_dir, "tokenized_data")
    tokenize_data.build(tokenizer, src_dir, gen_dir, domain="rest16",
                        report_path=os.path.join(work_dir, "report.json"))

    perbandingan = {}
    ok = True
    for split in ("train", "dev", "test"):
        for kind in ("quad_bert", "pair"):
            name = f"rest16_{split}_{kind}.tsv"
            a, b = os.path.join(gen_dir, name), os.path.join(repo_dir, name)
            if not os.path.exists(b):
                perbandingan[name] = {"ok": False, "error": "berkas repo tidak ada"}
                ok = False
                continue
            A = open(a, encoding="utf-8").read().splitlines()
            B = open(b, encoding="utf-8").read().splitlines()
            entry = _compare_files(A, B, per_sentence=(kind == "pair"))
            batas = RE_KNOWN_DEFECT.get(name, 0)
            entry["toleransi"] = batas
            entry["ok"] = entry["n_beda"] <= batas
            if entry["n_beda"] and entry["ok"]:
                entry["catatan"] = ("selisih sesuai cacat data upstream yang sudah "
                                    "dijelaskan: span lebar-nol 3,3 pada "
                                    "rest16_quad_train.tsv baris 451")
            perbandingan[name] = entry
            ok &= entry["ok"]
    detail["perbandingan"] = perbandingan
    return _gate("gate2_english", ok, **detail)


def gate_weights(paths, *, model=None, checkpoint_dir: str = None) -> dict:
    """Gate 1 PRD: bobot encoder di model == bobot di checkpoint (numerik).

    Butuh model yang sudah dimuat; dilewati (ok=False, `dilewati=True`) bila
    tidak diberikan, supaya pemanggil di notebook bisa menjalankannya tepat
    setelah `from_pretrained`.
    """
    from . import checkpoint as ckpt

    checkpoint_dir = checkpoint_dir or paths.get("bert_cache_dir")
    if model is None:
        return {"gate": "weights", "ok": False,
                "detail": {"dilewati": True,
                           "alasan": "model belum dimuat; jalankan dari sel setelah "
                                     "BertForQuadABSA.from_pretrained()"}}
    rep = ckpt.gate_weights_loaded(model, checkpoint_dir)
    return _gate("weights", rep["ok"], **rep)


GATE_FUNCS = {
    "taxonomy": gate_taxonomy,
    "dataset": gate_dataset,
    "acos_build": gate_acos_build,
    "tokenized": gate_tokenized,
    "gate2_english": gate_gate2_english,
    "weights": gate_weights,
}


def default_paths(indo_root: str, acos_root: str = None) -> dict:
    """Peta path standar dari dua root.

    `indo_root` adalah folder `ACOS-IndoBERT/` — seluruh berkas Indonesia
    (dataset, `tokenized_data`, backbone, hasil sesi) ada di bawahnya.
    `acos_root` adalah repo pipeline Inggris `ACOS-ASLI/`, dipakai **hanya
    untuk dibaca**: modul `Extract-Classify-ACOS/` dan data rest16 untuk gate 2.
    Default-nya folder induk `indo_root`.
    """
    indo_root = os.path.abspath(indo_root)
    acos_root = os.path.abspath(acos_root or os.path.dirname(indo_root))
    return {
        "indo_root": indo_root,
        "acos_root": acos_root,
        # Berkas Indonesia
        "data_root": os.path.join(indo_root, "data"),
        "tokenized_dir": os.path.join(indo_root, "tokenized_data"),
        "backbones_dir": os.path.join(indo_root, "backbones"),
        "bert_cache_dir": os.path.join(indo_root, "backbones", "indobert_base_p1"),
        "work_dir": os.path.join(indo_root, "build"),
        "results_dir": os.path.join(indo_root, "results"),
        # Upstream, baca saja
        "extract_dir": os.path.join(acos_root, "Extract-Classify-ACOS"),
        "en_data_root": os.path.join(acos_root, "data"),
        "en_vocab_dir": os.path.join(indo_root, "backbones", "bert_base_uncased"),
    }


def run_gates(indo_root: str = None, *, only=None, paths: dict = None,
              acos_root: str = None, raise_on_fail: bool = True,
              verbose: bool = True, **kwargs) -> dict:
    """Jalankan gate yang diminta; kembalikan `{nama: hasil}`.

    `only` default ke gate torch-free. `raise_on_fail=True` melempar
    `RuntimeError` bila ada gate merah — itu perilaku yang diinginkan di
    notebook, agar sel berikutnya tidak menyembunyikan masalah.
    """
    paths = paths or default_paths(indo_root, acos_root)
    names = list(only or TORCH_FREE_GATES)
    hasil = {}
    for name in names:
        fn = GATE_FUNCS.get(name)
        if fn is None:
            hasil[name] = _gate(name, False, error="gate tidak dikenal")
            continue
        kw = {k: v for k, v in kwargs.items()
              if k in fn.__code__.co_varnames}
        try:
            hasil[name] = fn(paths, **kw)
        except Exception as exc:  # gate tidak boleh menyembunyikan exception
            hasil[name] = _gate(name, False, error=f"{type(exc).__name__}: {exc}")
        if verbose:
            r = hasil[name]
            tanda = "✅" if r["ok"] else ("⏭️" if r["detail"].get("dilewati") else "❌")
            print(f"{tanda} gate {name}")
            if not r["ok"]:
                for k in ("error", "selisih", "berkas_hilang",
                          "tumpang_tindih_review_id", "alasan"):
                    if r["detail"].get(k):
                        print(f"     {k}: {r['detail'][k]}")

    gagal = [n for n, r in hasil.items()
             if not r["ok"] and not r["detail"].get("dilewati")]
    if gagal and raise_on_fail:
        raise RuntimeError(
            f"gate gagal: {', '.join(gagal)} — perbaiki sebelum training, karena "
            f"seluruh kegagalan ini tidak terlihat dari metrik training.")
    return hasil


def indo_root_default() -> str:
    """Folder `ACOS-IndoBERT/`, dihitung dari lokasi paket ini."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv=None):
    """CLI: `python -m acos_id.selftest [gate ...]`.

    Root dihitung dari lokasi paket, jadi perintahnya sama dari mana pun ia
    dijalankan. Tanpa argumen, kelima gate torch-free dijalankan.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    only = argv or None
    indo = indo_root_default()
    print(f"indo_root : {indo}")
    print(f"acos_root : {os.path.dirname(indo)} (baca saja)\n")
    try:
        hasil = run_gates(indo, only=only, raise_on_fail=False)
    except Exception as exc:
        print(f"❌ {type(exc).__name__}: {exc}")
        return 1
    print()
    print(json.dumps({k: {"ok": v["ok"]} for k, v in hasil.items()},
                     indent=2, ensure_ascii=False))
    return 0 if all(v["ok"] or v["detail"].get("dilewati") for v in hasil.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
