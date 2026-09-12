"""Verifikasi sesi hasil tanpa torch — reproduksi audit 12 Sep 2026.

Pakai: python scripts/verify_session.py <session_dir> [--domain appsid]
Fungsi: parse logs/result.txt, hitung TP/FP/FN + P/R/F1, bandingkan dengan
logs/master_metrics.json (bila ada), cek irisan gold-prediksi, plafon
kandidat, dan sidik jari checkpoint/bridge.

Contoh:
  python scripts/verify_session.py ACOS-IndoBERT/results/appsid_08092026_150437xxx
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ACOS-IndoBERT"))

from acos_id import guards  # noqa: E402


def load_master_metrics(session_dir: str) -> dict:
    for name in ("master_metrics.json", "logs/master_metrics.json"):
        path = os.path.join(session_dir, name)
        alt = os.path.join(session_dir, "logs", "master_metrics.json")
        for cand in (path, alt):
            if os.path.isfile(cand):
                with open(cand, encoding="utf-8") as fh:
                    return {"path": cand, "data": json.load(fh)}
    return {"path": None, "data": {}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_dir")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--bridge", default=None)
    ap.add_argument("--gold-pair", default=None)
    ap.add_argument("--quad-test", default=None)
    args = ap.parse_args()

    session = os.path.abspath(args.session_dir)
    if not os.path.isdir(session):
        print("sesi tidak ada: %s" % session)
        return 2
    domain = args.domain
    if domain is None:
        base = os.path.basename(session.rstrip(os.sep))
        domain = base.split("_")[0].lower() if "_" in base else "appsid"

    result_path = os.path.join(session, "logs", "result.txt")
    if not os.path.isfile(result_path):
        result_path = os.path.join(session, "result.txt")
    if not os.path.isfile(result_path):
        print("result.txt tidak ditemukan di %s" % session)
        return 2

    stat = guards.check_gold_pred_overlap(result_path)
    tp, fp, fn = stat["tp"], stat["fp"], stat["fn"]
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    print("result.txt: %s" % result_path)
    print("blok=%d gold_keys=%d pred_keys=%d irisan=%d" % (
        stat["n_blocks"], stat["n_gold_keys"], stat["n_pred_keys"],
        stat["n_overlap"]))
    print("TP=%d FP=%d FN=%d" % (tp, fp, fn))
    print("P=%.4f R=%.4f F1=%.4f" % (prec, rec, f1))
    if not stat["ok"]:
        print("GAGAL: %s" % stat.get("reason"))
    else:
        print("OK: irisan gold-prediksi > 0")

    master = load_master_metrics(session)
    if master["path"]:
        print("master_metrics: %s" % master["path"])
        print(json.dumps(master["data"], indent=2, ensure_ascii=False)[:2000])
    else:
        print("master_metrics.json tidak ditemukan (cache/re-eval belum jalan)")

    if args.bridge and args.gold_pair:
        ceil = guards.candidate_recall_ceiling(args.bridge, args.gold_pair)
        print("plafon kandidat: %.4f (%d/%d, mustahil=%d)" % (
            ceil["ceiling"], ceil["n_covered"], ceil["n_gold"],
            ceil["n_impossible"]))
    if args.bridge and args.quad_test:
        prov = guards.check_bridge_provenance(args.bridge, args.quad_test)
        print("provenance bridge: ok=%s alien=%d/%d" % (
            prov["ok"], prov.get("n_alien", -1), prov.get("n_bridge", -1)))
        if not prov["ok"]:
            print("GAGAL: %s" % prov.get("reason"))
            print("contoh alien: %s" % (prov.get("alien_sample"),))

    return 0 if stat["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
