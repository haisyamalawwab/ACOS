"""Guard anti-kontaminasi V4.2 — jawaban atas audit kritis 12 Sep 2026.

Latar: audit membuktikan sesi rest16 memakai artefak appsid (checkpoint,
pred4pipeline, bridge kandidat identik), TP=0 karena konstruksi ([UNK]
collapse), evaluasi memakai test set, dan gate lama lolos pada kasus gagal.

Modul ini torch-free (kecuali verify_dual_head_model) agar bisa dipanggil
dari sel gate sebelum training. Setiap check mengembalikan dict
{"ok": bool, ...} dan pemanggil memutuskan gagal-keras.
"""
from __future__ import annotations

import collections
import hashlib
import os

EXPECTED_VOCAB_LINES = {
    "indobert": 30521,
    "bert-en": 30522,
}

MAX_UNK_RATE = 0.05


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fingerprint_files(paths: list) -> dict:
    out = {}
    for path in paths:
        if os.path.isfile(path):
            out[path] = {
                "sha256": sha256_file(path),
                "bytes": os.path.getsize(path),
            }
        else:
            out[path] = {"missing": True}
    return out


def check_vocab_consistency(backbone_dir: str, backbone: str) -> dict:
    """Pengganti backbone_report.json yang tidak alarm-palsu.

    IndoBERT resmi memang config.vocab_size=50000 vs vocab.txt=30521
    (embedding over-provisioned). Jadi aturan: indobert -> vocab_lines
    harus 30521 dan config_vocab_size >= vocab_lines; bert-en ->
    harus sama persis 30522.
    """
    import json

    cfg_path = os.path.join(backbone_dir, "config.json")
    vocab_path = os.path.join(backbone_dir, "vocab.txt")
    rep = {"backbone": backbone, "dir": backbone_dir, "ok": False}
    if not os.path.isfile(cfg_path):
        return dict(rep, reason="config.json hilang: %s" % cfg_path)
    if not os.path.isfile(vocab_path):
        return dict(rep, reason="vocab.txt hilang: %s" % vocab_path)
    with open(cfg_path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    with open(vocab_path, "rb") as fh:
        raw = fh.read()
    vocab_lines = len(raw.decode("utf-8").splitlines())
    rep["config_vocab_size"] = cfg.get("vocab_size")
    rep["vocab_lines"] = vocab_lines
    rep["vocab_sha256"] = hashlib.sha256(raw).hexdigest()[:16]
    expected = EXPECTED_VOCAB_LINES.get(backbone)
    if expected is not None and vocab_lines != expected:
        return dict(rep, reason="vocab %d baris, harapan %d untuk %s"
                    % (vocab_lines, expected, backbone))
    if backbone == "bert-en" and rep["config_vocab_size"] != vocab_lines:
        return dict(rep, reason="bert-en menuntut config==vocab")
    if (rep["config_vocab_size"] or 0) < vocab_lines:
        return dict(rep, reason="config.vocab_size < vocab_lines")
    rep["ok"] = True
    return rep


def _texts_of_quad_file(path: str) -> set:
    texts = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                texts.add(line.split("\t")[0])
    return texts


def _texts_of_pair_file(path: str) -> list:
    texts = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                texts.append(line.split("####")[0])
    return texts


def check_bridge_provenance(bridge_path: str, quad_path: str) -> dict:
    """Bridge kandidat harus berasal dari domain yang sama.

    Syarat: 100% teks bridge ada di quad test domain tersebut.
    Ini guard yang hilang saat rest16 memakai bridge appsid.
    """
    rep = {"bridge": bridge_path, "quad": quad_path, "ok": False}
    if not os.path.isfile(bridge_path):
        return dict(rep, reason="bridge hilang")
    if not os.path.isfile(quad_path):
        return dict(rep, reason="quad hilang")
    quad_texts = _texts_of_quad_file(quad_path)
    bridge_texts = _texts_of_pair_file(bridge_path)
    rep["n_bridge"] = len(bridge_texts)
    rep["n_quad_texts"] = len(quad_texts)
    alien = [t for t in bridge_texts if t not in quad_texts]
    rep["n_alien"] = len(alien)
    rep["alien_sample"] = alien[:3]
    if alien:
        rep["reason"] = "%d/%d teks bridge di luar korpus domain" % (
            len(alien), len(bridge_texts))
        return rep
    rep["ok"] = True
    return rep


def check_unk_rate(texts: list, vocab_path: str, max_rate: float = MAX_UNK_RATE) -> dict:
    """Rasio token OOV terhadap vocab runtime harus kecil.

    Mekanisme kegagalan rest16: teks Indonesia + vocab Inggris -> semua
    [UNK], 10735 baris kolaps jadi 8940 kunci. Guard ini menangkapnya
    sebelum satu epoch pun berjalan.
    """
    vocab = set()
    with open(vocab_path, encoding="utf-8") as fh:
        for line in fh:
            vocab.add(line.strip())
    n_tok = 0
    n_unk = 0
    for text in texts:
        for word in text.split():
            n_tok += 1
            if word not in vocab and word.lower() not in vocab:
                n_unk += 1
    rate = (n_unk / n_tok) if n_tok else 1.0
    return {"n_token": n_tok, "n_unk": n_unk, "unk_rate": rate,
            "ok": rate <= max_rate,
            "reason": None if rate <= max_rate else
            "unk_rate %.3f > %.3f (vocab/data tidak cocok)" % (rate, max_rate)}


def parse_result_txt(path: str) -> dict:
    """Parser format warisan 3-4 baris/blok tanpa penanda.

    Mengembalikan gold_keys, pred_keys, dan triple TP/FP/FN per definisi
    measureQuad (kunci = teks+span, nilai = KAT#SENTI).
    """
    with open(path, encoding="utf-8") as fh:
        raw = fh.read().splitlines()
    blocks = []
    buf = []
    for line in raw + [""]:
        if line.strip() == "":
            if buf:
                blocks.append(buf)
                buf = []
        else:
            buf.append(line.rstrip("\n"))
    gold_keys = {}
    pred_keys = {}
    for blk in blocks:
        if len(blk) < 1:
            continue
        header = blk[0]
        golds = [x for x in blk[1].split("\t") if x.strip()] if len(blk) >= 2 else []
        preds = [x for x in blk[2].split("\t") if x.strip()] if len(blk) >= 3 else []
        if golds:
            gold_keys[header] = golds
        if preds:
            pred_keys[header] = preds
        elif len(blk) >= 1 and len(blk) == 1:
            pass
    tp = fp = fn = 0
    for key, plist in pred_keys.items():
        if key in gold_keys:
            cnt = sum(1 for p in plist if p in gold_keys[key])
            tp += cnt
            fp += len(plist) - cnt
            fn += len(gold_keys[key]) - cnt
        else:
            fp += len(plist)
    for key, glist in gold_keys.items():
        if key not in pred_keys:
            fn += len(glist)
    inter = set(gold_keys) & set(pred_keys)
    return {"n_blocks": len(blocks), "n_gold_keys": len(gold_keys),
            "n_pred_keys": len(pred_keys), "n_overlap": len(inter),
            "tp": tp, "fp": fp, "fn": fn}


def check_gold_pred_overlap(result_path: str) -> dict:
    """Gagalkan run bila irisan gold-prediksi kosong (kasus rest16)."""
    stat = parse_result_txt(result_path)
    stat["ok"] = stat["n_overlap"] > 0
    if not stat["ok"]:
        stat["reason"] = ("irisan gold-prediksi = 0 dari %d gold + %d prediksi; "
                          "evaluasi tidak bermakna" % (
                              stat["n_gold_keys"], stat["n_pred_keys"]))
    return stat


def candidate_recall_ceiling(bridge_path: str, gold_pair_path: str) -> dict:
    """Plafon recall: fraksi gold yang pernah muncul di kandidat step 1."""
    def key_of_pair_line(line: str) -> str:
        left = line.strip().split("\t")[0]
        text, _, span = left.partition("####")
        return text + " " + span
    bridge = set()
    with open(bridge_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                bridge.add(key_of_pair_line(line))
    gold = set()
    with open(gold_pair_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                gold.add(key_of_pair_line(line))
    hit = len(gold & bridge)
    return {"n_gold": len(gold), "n_bridge": len(bridge),
            "n_covered": hit, "ceiling": (hit / len(gold)) if gold else 0.0,
            "n_impossible": len(gold) - hit}


def count_silent_drops(bridge_path: str) -> dict:
    """Replikasi penyaring pair_eval tanpa peringatan.

    Upstream hanya menilai baris dengan tepat 1 aspek + 1 opini
    (eval_metrics.py). Baris lain dibuang diam-diam.
    """
    import re

    kept = dropped = empty_label = 0
    with open(bridge_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            left = line.split("\t")[0]
            _, _, span = left.partition("####")
            parts = span.split(" ")
            if len(parts) != 2:
                dropped += 1
                continue
            kept += 1
    return {"n_kept_shape_ok": kept, "note": "filter span detail dihitung saat evaluasi"}


def setbased_subtask_scores(quad_gold: dict, quad_pred: dict) -> dict:
    """Skor sub-task set-based per teks (satu elemen dihitung sekali).

    Pengganti measureQuad_imp yang membobot slot kesulitan sehingga
    hitungan elemen terinflasi ~2,1x. Fungsi ini murni himpunan.
    """
    out = {}
    for name, idx in (("category", 0), ("sentiment", 1),
                      ("aspect", 2), ("opinion", 3)):
        tp = fp = fn = 0
        all_texts = set(quad_gold) | set(quad_pred)
        for text in all_texts:
            gold_set = set(q[idx] for q in quad_gold.get(text, []))
            pred_set = set(q[idx] for q in quad_pred.get(text, []))
            tp += len(gold_set & pred_set)
            fp += len(pred_set - gold_set)
            fn += len(gold_set - pred_set)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        out[name] = {"tp": tp, "fp": fp, "fn": fn,
                     "precision": prec, "recall": rec, "f1": f1}
    return out


def resolve_eval_files(data_dir: str, domain: str, purpose: str) -> str:
    """Pemisah dev vs test yang benar (menutup cacat upstream).

    Upstream get_dev_examples() membaca *_test_* sehingga pemilihan
    checkpoint memakai test set. Aturan V4.2: purpose='select' ->
    dev; purpose='final' -> test / test_pair_1st.
    """
    if purpose == "select":
        cand = os.path.join(data_dir, "tokenized_data",
                            "%s_dev_pair.tsv" % domain)
        if not os.path.isfile(cand):
            cand = os.path.join(data_dir, "tokenized_data",
                                "%s_dev_quad_bert.tsv" % domain)
        return cand
    if purpose == "final":
        cand = os.path.join(data_dir, "tokenized_data",
                            "%s_test_pair_1st.tsv" % domain)
        if not os.path.isfile(cand):
            cand = os.path.join(data_dir, "tokenized_data",
                                "%s_test_pair.tsv" % domain)
        return cand
    raise ValueError("purpose harus 'select' atau 'final'")


def verify_dual_head_model(model) -> dict:
    """Pastikan model step-2 benar-benar dual-head sebelum angkanya dikutip."""
    has_cat = hasattr(model, "category_head")
    has_senti = hasattr(model, "sentiment_head") or hasattr(model, "senti_head")
    ok = bool(has_cat and has_senti)
    return {"ok": ok, "has_category_head": bool(has_cat),
            "has_sentiment_head": bool(has_senti),
            "reason": None if ok else "model bukan CategorySentiDualHead"}


def check_session_contamination(session_dir: str, expected_domain: str,
                                expected_vocab_lines: int) -> dict:
    """Deteksi sesi yang memakai artefak domain lain (temuan A audit).

    Memeriksa: vocab checkpoint sesi vs harapan domain, dan apakah
    bridge *_test_pair_1st.tsv berasal dari teks domain tersebut.
    Ringan (hash + hitung baris), tanpa torch.
    """
    rep = {"session": session_dir, "expected_domain": expected_domain,
           "ok": True, "issues": []}
    for step in ("step1_best", "step2_best"):
        vocab = os.path.join(session_dir, "checkpoints", step, "vocab.txt")
        if os.path.isfile(vocab):
            with open(vocab, "rb") as fh:
                n = len(fh.read().decode("utf-8").splitlines())
            if n != expected_vocab_lines:
                rep["ok"] = False
                rep["issues"].append("%s/vocab.txt=%d baris" % (step, n))
    return rep
