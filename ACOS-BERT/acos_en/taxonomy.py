"""Taksonomi domain Inggris (rest16/laptop) untuk pipeline ACOS dua tahap.

Upstream `CategorySentiProcessor.get_labels()` sudah mengenal kedua domain
secara asli (13 kategori rest16, 121 kategori laptop), jadi modul ini TIDAK
mem-patch apa pun — ia hanya menuliskan ulang angkanya sebagai konstanta dan
menyediakan `verify_against_upstream()` yang mengekstrak daftar kategori
langsung dari sumber `run_classifier_dataset_utils.py` (regex, torch-free).
Kalau berkas upstream berubah, gate gagal — bukan training yang salah senyap.

Step-2 memakai label gabungan `KATEGORI#SENTIMEN`: rest16 13x3 = 39,
laptop 121x3 = 363. `QuadProcessor` (Step-1) mengabaikan domain: 6 tag
`[CLS],O,I-A,B-A,I-O,B-O` untuk kedua domain.
"""
from __future__ import annotations

import os
import re

DOMAINS = ("rest16", "laptop")

N_CATEGORY = {"rest16": 13, "laptop": 121}
N_SENTIMENT = 3
N_CATSENTI = {"rest16": 39, "laptop": 363}

SEQ_LABELS = ("[CLS]", "O", "I-A", "B-A", "I-O", "B-O")
SENTIMENTS = ("0", "1", "2")

# 13 kategori rest16, verbatim dari upstream (urutan menentukan indeks head).
REST16_CATEGORIES = (
    "RESTAURANT#GENERAL", "SERVICE#GENERAL", "FOOD#GENERAL", "FOOD#QUALITY",
    "FOOD#STYLE_OPTIONS", "DRINKS#STYLE_OPTIONS", "DRINKS#PRICES",
    "AMBIENCE#GENERAL", "RESTAURANT#PRICES", "FOOD#PRICES",
    "RESTAURANT#MISCELLANEOUS", "DRINKS#QUALITY", "LOCATION#GENERAL",
)

UPSTREAM_MODULE = "run_classifier_dataset_utils.py"


def num_labels_step1() -> int:
    return len(SEQ_LABELS)


def num_labels_step2(domain: str) -> int:
    """39 untuk rest16, 363 untuk laptop."""
    return N_CATSENTI[domain]


def _extract_upstream_categories(extract_dir: str) -> dict:
    """`{domain: [kategori]}` dari sumber upstream (tanpa import/torch)."""
    path = os.path.join(extract_dir, UPSTREAM_MODULE)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    body = re.search(
        r"class CategorySentiProcessor.*?def get_labels\(self, domain_type\):"
        r"(.*?)def _create_examples", src, re.S).group(1)
    rest = re.search(r"if domain_type\.startswith\('rest'\):(.*?)elif",
                     body, re.S).group(1)
    lap = re.search(r"elif domain_type == 'laptop':(.*?)sentiment = ",
                    body, re.S).group(1)
    return {
        "rest16": re.findall(r"'([^']*#[^']*)'", rest),
        "laptop": re.findall(r"'([^']*#[^']*)'", lap),
    }


def verify_against_upstream(extract_dir: str) -> dict:
    """Bandingkan konstanta modul ini dengan sumber upstream.

    Memeriksa jumlah kategori per domain (13/121) dan isi+urutan daftar
    rest16. Untuk laptop yang 121 entri, isi penuh tidak ditulis ulang di
    sini — yang dijaga adalah jumlah dan dua entri ujung (drift detector
    murah untuk berkas 121 baris).
    """
    found = _extract_upstream_categories(extract_dir)
    diff = []
    for dom in DOMAINS:
        if len(found[dom]) != N_CATEGORY[dom]:
            diff.append(f"{dom}: {len(found[dom])} kategori != {N_CATEGORY[dom]}")
    if list(found["rest16"]) != list(REST16_CATEGORIES):
        diff.append("rest16: isi/urutan kategori beda dari konstanta")
    lap = found["laptop"]
    if lap[:1] != ["MULTIMEDIA_DEVICES#PRICE"] or lap[-1:] != ["Out_Of_Scope#USABILITY"]:
        diff.append("laptop: entri ujung berubah — periksa daftar upstream")
    return {"ok": not diff, "diff": diff,
            "n_rest16": len(found["rest16"]), "n_laptop": len(found["laptop"]),
            "num_labels_step2": dict(N_CATSENTI)}
