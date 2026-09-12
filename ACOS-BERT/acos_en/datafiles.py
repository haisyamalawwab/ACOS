"""Verifikasi berkas data Inggris (torch-free).

Berbeda dari `acos_id.build_acos`/`tokenize_data`: berkas sumber
(`data/Restaurant-ACOS/`, `data/Laptop-ACOS/`) dan berkas token
(`Extract-Classify-ACOS/tokenized_data/`) sudah dikirim bersama repo, jadi
modul ini hanya memverifikasi — tidak membangun ulang:

- `required_tokenized(domain)`: daftar berkas token yang wajib ada per domain.
- `verify_tokenized()`: keberadaan + jumlah baris + 0-baris-kosong.
- `span_sanity()`: tiap span `a-b,c-d` pada sampel menunjuk token yang ada
  (lebar > 0, kecuali `-1,-1` implisit), pola `teks<TAB>span ...`.
- `verify_quad_source()`: berkas quad sumber ada + hitungan baris.
"""
from __future__ import annotations

import os
import re

SPAN_RE = re.compile(r"^(-?\d+),(-?\d+)$")

TOKENIZED_FILES = {
    "quad_bert": "{domain}_{split}_quad_bert.tsv",
    "pair": "{domain}_{split}_pair.tsv",
    "pair_1st": "{domain}_test_pair_1st.tsv",
}
SPLITS = ("train", "dev", "test")

QUAD_SOURCE = {
    "rest16": os.path.join("data", "Restaurant-ACOS"),
    "laptop": os.path.join("data", "Laptop-ACOS"),
}
QUAD_PREFIX = {"rest16": "rest16_quad_", "laptop": "laptop_quad_"}


def required_tokenized(domain: str) -> list:
    """Nama berkas token yang wajib ada untuk satu domain."""
    out = [TOKENIZED_FILES["quad_bert"].format(domain=domain, split=s) for s in SPLITS]
    out += [TOKENIZED_FILES["pair"].format(domain=domain, split=s) for s in ("train", "dev", "test")]
    out.append(TOKENIZED_FILES["pair_1st"].format(domain=domain))
    return out


def _tok(tokenized_base: str, name: str) -> str:
    """Path berkas token: `<base>/tokenized_data/<name>` (fallback `<base>/<name>`).

    Processor upstream menyusun path sebagai
    `data_dir + "tokenized_data/" + berkas`, jadi `tokenized_base` = `data_dir`
    (= folder `Extract-Classify-ACOS/`), bukan folder token itu sendiri.
    """
    p = os.path.join(tokenized_base, "tokenized_data", name)
    if os.path.isfile(p):
        return p
    return os.path.join(tokenized_base, name)


def _count_lines(path: str) -> dict:
    n, kosong = 0, 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            n += 1
            if not line.strip():
                kosong += 1
    return {"baris": n, "kosong": kosong}


def verify_tokenized(tokenized_dir: str, domain: str) -> dict:
    """Keberadaan + hitungan baris tiap berkas token satu domain."""
    hilang, info = [], {}
    for name in required_tokenized(domain):
        p = _tok(tokenized_dir, name)
        if not os.path.isfile(p):
            hilang.append(name)
            continue
        info[name] = _count_lines(p)
    return {"ok": not hilang, "hilang": hilang, "berkas": info}


def span_sanity(tokenized_dir: str, domain: str, split: str = "train",
                limit: int = 500) -> dict:
    """Cek span `*_quad_bert.tsv`: `a-b,c-d` valid, lebar > 0 / `-1,-1`.

    Format baris: `teks<TAB>asp_span cat senti opi_span ...` dengan teks yang
    sudah ter-WordPiece (spasi = batas token). Span aspek/opini adalah indeks
    token pada teks tersebut.
    """
    name = TOKENIZED_FILES["quad_bert"].format(domain=domain, split=split)
    path = _tok(tokenized_dir, name)
    rusak, jml_span, jml_baris = [], 0, 0
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= limit:
                break
            line = line.rstrip("\n")
            if not line.strip():
                continue
            jml_baris += 1
            parts = line.split("\t")
            n_tok = len(parts[0].split(" "))
            for quad in parts[1:]:
                ele = quad.split(" ")
                if len(ele) < 4:
                    rusak.append((i, "kolom<4"))
                    continue
                for span in (ele[0], ele[3]):
                    m = SPAN_RE.match(span)
                    if not m:
                        rusak.append((i, f"pola-span {span!r}"))
                        continue
                    jml_span += 1
                    a, b = int(m.group(1)), int(m.group(2))
                    if (a, b) == (-1, -1):
                        continue
                    if not (0 <= a < b <= n_tok):
                        rusak.append((i, f"span {span} di luar {n_tok} token"))
    return {"berkas": name, "baris_dicek": jml_baris, "span_dicek": jml_span,
            "rusak": rusak[:5], "n_rusak": len(rusak), "ok": not rusak}


def verify_quad_source(acos_root: str, domain: str) -> dict:
    """Berkas quad sumber (`data/...`) ada + hitungan baris."""
    d = os.path.join(acos_root, QUAD_SOURCE[domain])
    info, hilang = {}, []
    for split in SPLITS:
        name = f"{QUAD_PREFIX[domain]}{split}.tsv"
        p = os.path.join(d, name)
        if not os.path.isfile(p):
            hilang.append(name)
            continue
        info[name] = _count_lines(p)
    return {"ok": not hilang, "dir": d, "hilang": hilang, "berkas": info}
