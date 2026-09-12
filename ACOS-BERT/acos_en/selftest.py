"""Gerbang verifikasi lapisan Inggris — dijalankan sebelum training.

Cermin `acos_id.selftest` dengan 4 gate (semua torch-free kecuali `weights`):

- `taxonomy` — jumlah kategori 13/121 + isi/urutan rest16 vs. sumber upstream.
- `datafiles` — berkas quad sumber ada + hitungan baris.
- `tokenized` — berkas token ada + 0 baris kosong + span sanity 500 baris.
- `weights` (Gate-1, butuh torch/Colab) — probe numerik encoder vs. checkpoint.

CLI: `python -m acos_en.selftest` dari dalam `ACOS-BERT/`.
"""
from __future__ import annotations

import os
import sys

from . import datafiles, taxonomy
from .upstream import find_upstream

TORCH_FREE_GATES = ("taxonomy", "datafiles", "tokenized")
ALL_GATES = TORCH_FREE_GATES + ("weights",)


def _gate(name, ok, **detail):
    return {"gate": name, "ok": bool(ok), "detail": detail}


def gate_taxonomy(paths) -> dict:
    rep = taxonomy.verify_against_upstream(paths["extract_dir"])
    return _gate("taxonomy", rep["ok"], **{k: v for k, v in rep.items() if k != "ok"})


def gate_datafiles(paths, domain: str) -> dict:
    rep = datafiles.verify_quad_source(paths["acos_root"], domain)
    return _gate("datafiles", rep["ok"],
                 dir=rep["dir"], hilang=rep["hilang"],
                 berkas={k: v["baris"] for k, v in rep["berkas"].items()})


def gate_tokenized(paths, domain: str) -> dict:
    rep = datafiles.verify_tokenized(paths["tokenized_base"], domain)
    if not rep["ok"]:
        detail = {k: v for k, v in rep.items() if k != "ok"}
        return _gate("tokenized", False, **detail)
    sanity = datafiles.span_sanity(paths["tokenized_base"], domain)
    ok = rep["ok"] and sanity["ok"]
    return _gate("tokenized", ok, berkas={k: v["baris"] for k, v in rep["berkas"].items()},
                 span_dicek=sanity["span_dicek"], n_rusak=sanity["n_rusak"],
                 contoh_rusak=sanity["rusak"])


def run_gates(domain: str, paths: dict, gates=TORCH_FREE_GATES,
              raise_on_fail: bool = True) -> dict:
    """Jalankan gate yang diminta; gagal keras bila ada yang merah."""
    hasil = {}
    for g in gates:
        if g == "taxonomy":
            hasil[g] = gate_taxonomy(paths)
        elif g == "datafiles":
            hasil[g] = gate_datafiles(paths, domain)
        elif g == "tokenized":
            hasil[g] = gate_tokenized(paths, domain)
        elif g == "weights":
            hasil[g] = _gate("weights", None, pesan="butuh torch/Colab (sel Gate-1)")
    gagal = [g for g, r in hasil.items() if r["ok"] is False]
    if gagal and raise_on_fail:
        raise RuntimeError(f"gate merah: {gagal} — berhenti sebelum training")
    return hasil


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Gate torch-free ACOS-BERT")
    ap.add_argument("--domain", default="rest16", choices=["rest16", "laptop"])
    ap.add_argument("--bert-root", default=None)
    ap.add_argument("--acos-root", default=None)
    ns = ap.parse_args(argv)
    from . import default_paths
    paths = default_paths(ns.bert_root, ns.acos_root)
    hasil = run_gates(ns.domain, paths)
    for g, r in hasil.items():
        print(f"[{'LULUS' if r['ok'] else 'GAGAL'}] {g}: {r['detail']}")
    print(f"{sum(1 for r in hasil.values() if r['ok'])}/{len(hasil)} gate lulus")
    return 0 if all(r["ok"] for r in hasil.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
