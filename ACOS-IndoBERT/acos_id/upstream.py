"""Menemukan dan memasang repo pipeline Inggris `ACOS-ASLI/` ke `sys.path`.

Modul upstream (`modeling`, `bert_utils.tokenization`,
`run_classifier_dataset_utils`, `eval_metrics`) diimpor sebagai modul tingkat
atas, bukan sebagai paket — `bert_utils/tokenization.py` sendiri memakai
`from .file_utils import cached_path`, jadi folder `Extract-Classify-ACOS/`
harus ada di `sys.path`, bukan induknya.

Karena `ACOS-IndoBERT/` berada di luar repo itu, pemasangan path menjadi langkah
eksplisit. Tanpa modul ini setiap gate dan skrip harus mengulang penyisipan
`sys.path` sendiri, dan yang lupa gagal dengan `ModuleNotFoundError:
No module named 'bert_utils'` yang tidak menunjuk penyebabnya.
"""
from __future__ import annotations

import os
import sys

UPSTREAM_DIRNAME = "Extract-Classify-ACOS"

REQUIRED_FILES = ("modeling.py", "run_classifier_dataset_utils.py",
                  "eval_metrics.py", os.path.join("bert_utils", "tokenization.py"))


def indo_root() -> str:
    """Folder `ACOS-IndoBERT/`, dihitung dari lokasi paket ini."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_upstream(path: str) -> bool:
    """True bila `path` benar-benar folder `Extract-Classify-ACOS` yang lengkap."""
    return all(os.path.isfile(os.path.join(path, f)) for f in REQUIRED_FILES)


def find_upstream(acos_root: str = None, extract_dir: str = None) -> str:
    """Lokasi folder `Extract-Classify-ACOS` yang lengkap.

    Urutan pencarian: `extract_dir` eksplisit, lalu di bawah `acos_root`, lalu
    folder induk `ACOS-IndoBERT/` dan dua tingkat di atasnya. Melempar
    `FileNotFoundError` dengan daftar yang sudah dicoba — bukan mengembalikan
    None, karena pemanggil tidak punya jalan lain untuk melanjutkan.
    """
    kandidat = []
    if extract_dir:
        kandidat.append(extract_dir)
    if acos_root:
        kandidat.append(os.path.join(acos_root, UPSTREAM_DIRNAME))
    here = indo_root()
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
    """Pasang folder upstream ke posisi terdepan `sys.path`; kembalikan path-nya.

    Dipaksa ke posisi 0 walau sudah ada di urutan yang lebih rendah, supaya
    salinan `colab_utils.py`/`modeling.py` lain yang kebetulan lebih dulu di
    `sys.path` tidak membayangi yang ini.
    """
    path = find_upstream(acos_root, extract_dir)
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
    return path
