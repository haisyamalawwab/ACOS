"""acos_en — lapisan Inggris (rest16/laptop) untuk pipeline ACOS dua tahap.

Cermin dari `acos_id/` (ACOS-IndoBERT) dengan tiga penyederhanaan yang
disengaja, semuanya karena data Inggris sudah jadi di repo upstream:

1. Tanpa `build_acos`/`tokenize_data` — berkas `tokenized_data/rest16_*` dan
   `laptop_*` sudah dikirim bersama `Extract-Classify-ACOS/`; modul
   `datafiles` hanya memverifikasi, bukan membangun ulang.
2. Tanpa patch `get_labels` — `CategorySentiProcessor` upstream sudah mengenal
   `rest*` (13 kategori) dan `laptop` (121 kategori) secara asli.
3. Tanpa rekey prefix — checkpoint `bert-base-uncased` sudah memakai prefix
   `bert.*`; Gate-1 tetap memverifikasi secara numerik.

Torch-free kecuali `checkpoint.py` (butuh torch untuk `torch.load`).
"""
from __future__ import annotations

import os


def bert_root() -> str:
    """Folder `ACOS-BERT/`, dihitung dari lokasi paket ini."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_paths(bert_root_dir: str = None, acos_root: str = None) -> dict:
    """Dua root ala V4: `bert_root` ditulis, `acos_root` hanya dibaca."""
    here = bert_root_dir or bert_root()
    if acos_root is None:
        acos_root = os.path.dirname(os.path.abspath(here))
    from .upstream import find_upstream
    return {
        "bert_root": os.path.abspath(here),
        "acos_root": os.path.abspath(acos_root),
        "extract_dir": find_upstream(acos_root=acos_root),
        "tokenized_base": find_upstream(acos_root=acos_root),
        "backbones_dir": os.path.join(os.path.abspath(here), "backbones"),
        "results_base": os.path.join(os.path.abspath(here), "results"),
    }
