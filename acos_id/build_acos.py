"""Konversi `data/Apps-ACOS/processed/*` → format ACOS mentah.

Keluaran: `data/Apps-ACOS/appsid_quad_{train,dev,test}.tsv` dengan format yang
sama persis seperti `data/Restaurant-ACOS/rest16_quad_*.tsv`:

    <teks>\\t<a_st,a_ed> <KATEGORI> <senti> <o_st,o_ed>\\t<quad ke-2> ...

`a_st,a_ed` adalah indeks **whitespace-token** pada `<teks>`, `a_ed` eksklusif,
dan `-1,-1` berarti implisit.

Keputusan penting: **satu baris = satu klausa**, bukan satu ulasan.
`quintuples_weak.csv` memberi kolom `clause` per tuple dan hanya 37,6% klausa
yang bisa dipetakan kembali ke token `text_norm` (sebagian klausa berasal dari
varian normalisasi yang berbeda), sedangkan aspek/opini terpetakan 100% di dalam
klausanya sendiri bila tokenisasi menyertakan tanda baca sebagai token
terpisah. Memakai ulasan utuh sebagai baris berarti membuang ~62% span menjadi
implisit palsu; memakai klausa mempertahankan seluruh anotasi.

Split diambil dari `stage2_{train,val,test}.jsonl` berdasarkan `review_id`
(`val` → `dev`), jadi tidak ada ulasan yang bocor antar split. Sudah diverifikasi
bahwa ketiga himpunan `review_id` saling lepas.
"""
from __future__ import annotations

import collections
import csv
import json
import os
import re
import sys

from .taxonomy import (
    CATEGORIES,
    DOMAIN,
    IMPLICIT_SPAN,
    NULL_TERM,
    SENTIMENT_FROM_NAME,
)

csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
"""Tokenisasi kata-atau-tanda-baca.

Dibutuhkan karena `text_norm` menyimpan `ribet,bebas` tanpa spasi di sekitar
koma. Dengan `str.split()` biasa, `bebas` tidak akan pernah cocok sebagai token
dan span-nya hilang. Pola ini memisahkan koma menjadi token sendiri, sehingga
seluruh aspek/opini eksplisit dapat dipetakan.
"""

SPLIT_FILES = {
    "train": "stage2_train.jsonl",
    "dev": "stage2_val.jsonl",
    "test": "stage2_test.jsonl",
}


def tokenize(text: str) -> list:
    """Token kata/tanda baca dalam huruf kecil."""
    return TOKEN_RE.findall(text.lower())


def _find_span(haystack: list, needle: list, prefer_from: int = 0):
    """Indeks awal kemunculan `needle` di `haystack`, mulai dari `prefer_from`.

    Kemunculan pertama pada atau setelah `prefer_from` dipilih lebih dulu supaya
    aspek dan opini dalam satu tuple tidak saling menimpa ketika kata yang sama
    muncul dua kali; bila tidak ada, kembali ke kemunculan pertama.
    """
    n = len(needle)
    if n == 0 or n > len(haystack):
        return None
    first = None
    for i in range(len(haystack) - n + 1):
        if haystack[i:i + n] == needle:
            if first is None:
                first = i
            if i >= prefer_from:
                return i
    return first


def read_split_ids(processed_dir: str) -> dict:
    """`{split: set(review_id)}` dari berkas stage2."""
    out = {}
    for split, fname in SPLIT_FILES.items():
        path = os.path.join(processed_dir, fname)
        ids = set()
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    ids.add(json.loads(line)["review_id"])
        out[split] = ids
    return out


def group_quintuples(processed_dir: str):
    """Kelompokkan `quintuples_weak.csv` menjadi `{(review_id, clause): [row]}`.

    Urutan kemunculan dipertahankan (dict biasa sudah terurut sejak Python 3.7)
    agar keluaran generator deterministik.
    """
    path = os.path.join(processed_dir, "quintuples_weak.csv")
    groups = collections.OrderedDict()
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            groups.setdefault((row["review_id"], row["clause"]), []).append(row)
    return groups


def build_quad_lines(processed_dir: str):
    """Bentuk baris ACOS per klausa beserta laporan.

    Mengembalikan `(lines_by_split, report)`; `lines_by_split[split]` adalah
    daftar string baris tanpa newline.
    """
    split_ids = read_split_ids(processed_dir)
    id_to_split = {}
    for split, ids in split_ids.items():
        for rid in ids:
            id_to_split[rid] = split

    groups = group_quintuples(processed_dir)
    categories = set(CATEGORIES)

    lines = {"train": [], "dev": [], "test": []}
    rep = collections.Counter()
    unknown_cat = collections.Counter()

    for (rid, clause), rows in groups.items():
        split = id_to_split.get(rid)
        if split is None:
            rep["klausa_dibuang_tanpa_split"] += 1
            continue

        tokens = tokenize(clause)
        if not tokens:
            rep["klausa_dibuang_kosong"] += 1
            continue

        quads = []
        for row in rows:
            cat = row["category"]
            if cat not in categories:
                unknown_cat[cat] += 1
                rep["tuple_dibuang_kategori_asing"] += 1
                continue
            senti = SENTIMENT_FROM_NAME.get(row["sentiment"])
            if senti is None:
                rep["tuple_dibuang_sentimen_asing"] += 1
                continue

            asp_raw, opi_raw = row["aspect"], row["opinion"]
            if asp_raw == NULL_TERM:
                asp_span = IMPLICIT_SPAN
                rep["aspek_implisit"] += 1
                asp_end = 0
            else:
                at = tokenize(asp_raw)
                st = _find_span(tokens, at)
                if st is None:
                    rep["tuple_dibuang_aspek_tak_ditemukan"] += 1
                    continue
                asp_span = f"{st},{st + len(at)}"
                asp_end = st + len(at)
                rep["aspek_eksplisit"] += 1

            if opi_raw == NULL_TERM:
                opi_span = IMPLICIT_SPAN
                rep["opini_implisit"] += 1
            else:
                ot = tokenize(opi_raw)
                st = _find_span(tokens, ot, prefer_from=asp_end)
                if st is None:
                    rep["tuple_dibuang_opini_tak_ditemukan"] += 1
                    continue
                opi_span = f"{st},{st + len(ot)}"
                rep["opini_eksplisit"] += 1

            quad = f"{asp_span} {cat} {senti} {opi_span}"
            if quad not in quads:
                quads.append(quad)
            else:
                rep["tuple_duplikat_digabung"] += 1

        if not quads:
            rep["klausa_dibuang_tanpa_tuple_valid"] += 1
            continue

        text = " ".join(tokens)
        lines[split].append(text + "\t" + "\t".join(quads))
        rep[f"baris_{split}"] += 1
        rep[f"tuple_{split}"] += len(quads)
        if len(tokens) > 126:
            rep["baris_lebih_126_token"] += 1

    report = dict(rep)
    report["kategori_asing"] = dict(unknown_cat)
    return lines, report


def write_quad_files(lines_by_split: dict, out_dir: str) -> dict:
    """Tulis `appsid_quad_<split>.tsv` dan kembalikan `{split: path}`."""
    os.makedirs(out_dir, exist_ok=True)
    written = {}
    for split, lines in lines_by_split.items():
        path = os.path.join(out_dir, f"{DOMAIN}_quad_{split}.tsv")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for line in lines:
                fh.write(line + "\n")
        written[split] = path
    return written


def build(data_root: str, out_dir: str = None, *, report_path: str = None) -> dict:
    """Jalankan konversi penuh.

    `data_root` adalah folder `data/`; keluaran default ke
    `data/Apps-ACOS/` agar berdampingan dengan `Restaurant-ACOS/`.
    """
    processed = os.path.join(data_root, "Apps-ACOS", "processed")
    if out_dir is None:
        out_dir = os.path.join(data_root, "Apps-ACOS")

    lines, report = build_quad_lines(processed)
    written = write_quad_files(lines, out_dir)
    report["berkas"] = written
    report["sumber"] = processed

    if report_path is None:
        report_path = os.path.join(out_dir, "_build_acos_report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, sort_keys=True)
    report["laporan"] = report_path
    return report


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    data_root = argv[0] if argv else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    rep = build(data_root)
    print(f"Sumber : {rep['sumber']}")
    for split in ("train", "dev", "test"):
        print(f"  {split:5s} {rep.get(f'baris_{split}', 0):6d} baris, "
              f"{rep.get(f'tuple_{split}', 0):6d} tuple → {rep['berkas'][split]}")
    print(f"  aspek  : {rep.get('aspek_eksplisit', 0)} eksplisit, "
          f"{rep.get('aspek_implisit', 0)} implisit")
    print(f"  opini  : {rep.get('opini_eksplisit', 0)} eksplisit, "
          f"{rep.get('opini_implisit', 0)} implisit")
    dibuang = {k: v for k, v in rep.items() if k.startswith(("tuple_dibuang", "klausa_dibuang"))}
    print(f"  dibuang: {dibuang or 'tidak ada'}")
    print(f"  laporan: {rep['laporan']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
