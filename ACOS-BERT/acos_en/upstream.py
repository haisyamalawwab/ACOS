"""Menemukan dan memasang repo pipeline `Extract-Classify-ACOS/` ke `sys.path`.

Cermin dari `acos_id.upstream`: modul upstream (`modeling`,
`bert_utils.tokenization`, `run_classifier_dataset_utils`, `eval_metrics`)
diimpor sebagai modul tingkat atas, jadi folder `Extract-Classify-ACOS/`
harus ada di `sys.path`, bukan induknya.
"""
from __future__ import annotations

import os
import sys

UPSTREAM_DIRNAME = "Extract-Classify-ACOS"

REQUIRED_FILES = ("modeling.py", "run_classifier_dataset_utils.py",
                  "eval_metrics.py", os.path.join("bert_utils", "tokenization.py"))


def bert_root() -> str:
    """Folder `ACOS-BERT/`, dihitung dari lokasi paket ini."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_upstream(path: str) -> bool:
    """True bila `path` benar-benar folder `Extract-Classify-ACOS` yang lengkap."""
    return all(os.path.isfile(os.path.join(path, f)) for f in REQUIRED_FILES)


def find_upstream(acos_root: str = None, extract_dir: str = None) -> str:
    """Lokasi folder `Extract-Classify-ACOS` yang lengkap (melempar bila tak ada)."""
    kandidat = []
    if extract_dir:
        kandidat.append(extract_dir)
    if acos_root:
        kandidat.append(os.path.join(acos_root, UPSTREAM_DIRNAME))
    here = bert_root()
    for up in (os.path.dirname(here), os.path.dirname(os.path.dirname(here)), here):
        kandidat.append(os.path.join(up, UPSTREAM_DIRNAME))

    dicoba = []
    for p in kandidat:
        p = os.path.abspath(p)
        if p in dicoba:
            continue
        dicoba.append(p)
        if is_upstream(p):
            return p
    raise FileNotFoundError(
        f"folder {UPSTREAM_DIRNAME} yang lengkap tidak ditemukan. Dicoba: {dicoba}. "
        f"Berkas yang dituntut: {list(REQUIRED_FILES)}")


def ensure_path(acos_root: str = None, extract_dir: str = None) -> str:
    """Pasang folder upstream ke posisi terdepan `sys.path`; kembalikan path-nya."""
    path = find_upstream(acos_root, extract_dir)
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
    return path
