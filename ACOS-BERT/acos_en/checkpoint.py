"""Adapter checkpoint `bert-base-uncased` + Gate-1 numerik.

Berbeda dari `acos_id.checkpoint`: TIDAK ada rekey — checkpoint Inggris
sudah memakai prefix `bert.*` yang diharapkan loader legacy
(`modeling.py:744-747`, model tugas punya atribut `self.bert` sehingga
`start_prefix=''` dan key `bert.*` cocok langsung). Modul ini hanya:

- `ensure_vocab()`: pastikan `vocab.txt` ada di folder backbone
  (bekas unduhan ~230 KB; unduh bila hilang).
- `verify_weights()`: bandingkan 3 tensor probe (embedding, layer-0 query,
  layer-11 output) antara model hidup dan checkpoint dengan `torch.equal`.
  Merah = berhenti, karena training di atas encoder acak tak terlihat dari
  kurva loss (logging `missing_keys` di-comment di `modeling.py:749-755`).

Butuh torch — hanya diimpor di dalam fungsi agar paket tetap torch-free.
"""
from __future__ import annotations

import os
import urllib.request

VOCAB_FILE = "vocab.txt"
VOCAB_URL = ("https://huggingface.co/bert-base-uncased/resolve/main/vocab.txt")

PROBE_KEYS = (
    "bert.embeddings.word_embeddings.weight",
    "bert.encoder.layer.0.attention.self.query.weight",
    "bert.encoder.layer.11.output.dense.weight",
)


def backbone_dir(backbones_dir: str, backbone: str = "bert-en") -> str:
    """Folder cache per backbone (jangan berbagi antar backbone)."""
    nama = {"bert-en": "bert_base_uncased"}.get(backbone, backbone.replace("-", "_"))
    d = os.path.join(backbones_dir, nama)
    os.makedirs(d, exist_ok=True)
    return d


def ensure_vocab(backbones_dir: str, backbone: str = "bert-en") -> dict:
    """Pastikan `vocab.txt` ada; unduh bila hilang. Torch-free."""
    d = backbone_dir(backbones_dir, backbone)
    p = os.path.join(d, VOCAB_FILE)
    info = {"path": p, "ada": os.path.isfile(p)}
    if info["ada"]:
        with open(p, encoding="utf-8") as fh:
            info["baris"] = sum(1 for _ in fh)
        return info
    urllib.request.urlretrieve(VOCAB_URL, p)
    info["diunduh"] = True
    with open(p, encoding="utf-8") as fh:
        info["baris"] = sum(1 for _ in fh)
    return info


def verify_weights(model, checkpoint_path: str,
                   probe_keys=PROBE_KEYS) -> dict:
    """Bandingkan tensor hidup vs. checkpoint di disk (butuh torch).

    Mengembalikan `{"ok", "cocok", "hilang_encoder", "pesan"}`. `ok=True`
    hanya bila ketiga probe `torch.equal` dan tidak ada key `bert.*` model
    yang hilang dari checkpoint.
    """
    import torch
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    live = dict(model.state_dict())
    hilang = [k for k in live if k.startswith("bert.") and k not in state]
    cocok = {}
    for k in probe_keys:
        if k in state and k in live:
            cocok[k] = bool(torch.equal(live[k].cpu(), state[k].cpu()))
        else:
            cocok[k] = False
    ok = all(cocok.values()) and not hilang
    pesan = (f"{sum(cocok.values())}/{len(cocok)} probe cocok, "
             f"{len(hilang)} encoder-key hilang")
    return {"ok": ok, "cocok": cocok, "hilang_encoder": hilang[:5],
            "n_hilang": len(hilang), "pesan": pesan}
