"""Adapter checkpoint IndoBERT + gate bobot — deliverable D1 & Gate 1 dari PRD.

Masalah yang diselesaikan modul ini adalah kegagalan **senyap**. `BertForQuadABSA`
punya atribut `self.bert` (`modeling.py:1536`), sehingga loader legacy menetapkan
`start_prefix = ''` (`modeling.py:745`) dan mencari key `bert.*` di state_dict.
Checkpoint `indobenchmark/indobert-base-p1` menyimpan key **tanpa** prefiks itu
(`embeddings.word_embeddings.weight`, bukan `bert.embeddings...`), jadi seluruh
bobot encoder masuk ke `missing_keys` dan encoder terlatih diganti inisialisasi
acak. Logging yang seharusnya melaporkannya di-comment out (`modeling.py:749-755`),
sehingga training berjalan mulus dengan encoder acak dan yang terlihat hanya
metrik yang rendah tanpa sebab.

Karena itu `prepare_backbone()` menulis ulang checkpoint dengan prefiks `bert.`,
dan `gate_weights_loaded()` membandingkan tensor **secara numerik** setelah model
dimuat. Gate itu tidak opsional: ia satu-satunya yang membedakan "encoder
terlatih" dari "encoder acak" dari luar.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request

BACKBONES = {
    "indobert": {
        "hf_id": "indobenchmark/indobert-base-p1",
        "needs_rekey": True,
        "do_lower_case": True,
        "catatan": "target utama; state_dict tanpa prefiks bert., wajib rekey",
    },
    "indobert-large": {
        "hf_id": "indobenchmark/indobert-large-p1",
        "needs_rekey": True,
        "do_lower_case": True,
        "catatan": "ditunda; 24 layer, VRAM Colab T4 mepet",
    },
    "bert-en": {
        "hf_id": "bert-base-uncased",
        "needs_rekey": False,
        "do_lower_case": True,
        "catatan": "kontrol Inggris; state_dict sudah memakai prefiks bert.",
    },
}
"""Registry backbone. `needs_rekey` diperiksa ulang saat unduh, bukan dipercaya."""

FILES = ("config.json", "pytorch_model.bin", "vocab.txt")

HF_TEMPLATE = "https://huggingface.co/{hf_id}/resolve/main/{fname}"


def _download(url: str, dst: str, *, force: bool = False):
    if os.path.exists(dst) and os.path.getsize(dst) > 0 and not force:
        return {"file": dst, "bytes": os.path.getsize(dst), "cached": True}
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    urllib.request.urlretrieve(url, dst)
    return {"file": dst, "bytes": os.path.getsize(dst), "cached": False}


def download_backbone(backbone: str, target_dir: str, *, force: bool = False) -> dict:
    """Unduh `config.json`, `pytorch_model.bin`, `vocab.txt` ke `target_dir`."""
    if backbone not in BACKBONES:
        raise KeyError(f"backbone '{backbone}' tidak dikenal; pilihan: {sorted(BACKBONES)}")
    spec = BACKBONES[backbone]
    out = {"backbone": backbone, "hf_id": spec["hf_id"], "dir": target_dir, "files": {}}
    for fname in FILES:
        url = HF_TEMPLATE.format(hf_id=spec["hf_id"], fname=fname)
        out["files"][fname] = _download(url, os.path.join(target_dir, fname), force=force)
    return out


def vocab_report(target_dir: str) -> dict:
    """Bandingkan `config.vocab_size` dengan jumlah baris `vocab.txt`.

    Untuk `indobert-base-p1` keduanya memang berbeda (50000 vs 30521): matriks
    embedding-nya benar-benar 50000 baris, id 30521+ tidak pernah terpakai. Yang
    berbahaya adalah memakai `config.vocab_size` sebagai acuan jumlah token —
    tokenizer hanya tahu 30521, jadi rujuk selalu `vocab.txt`.
    """
    cfg_path = os.path.join(target_dir, "config.json")
    vocab_path = os.path.join(target_dir, "vocab.txt")
    rep = {"config_json": cfg_path, "vocab_txt": vocab_path}
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        rep["config_vocab_size"] = cfg.get("vocab_size")
        rep["hidden_size"] = cfg.get("hidden_size")
        rep["num_hidden_layers"] = cfg.get("num_hidden_layers")
        rep["architectures"] = cfg.get("architectures")
    if os.path.exists(vocab_path):
        with open(vocab_path, "rb") as fh:
            raw = fh.read()
        rep["vocab_lines"] = len(raw.decode("utf-8").splitlines())
        rep["vocab_sha256"] = hashlib.sha256(raw).hexdigest()
        rep["vocab_bytes"] = len(raw)
    if "config_vocab_size" in rep and "vocab_lines" in rep:
        rep["konsisten"] = rep["config_vocab_size"] == rep["vocab_lines"]
        rep["selisih"] = (rep["config_vocab_size"] or 0) - rep["vocab_lines"]
    return rep


def rekey_state_dict(state_dict):
    """Tambahkan prefiks `bert.` pada key yang belum memilikinya.

    Key head (`cls.*`, `pooler` di luar `bert.`) tidak ikut; hanya key encoder.
    Checkpoint `indobert-base-p1` memang tidak punya `cls.*` sama sekali —
    `"architectures": ["BertModel"]`, bukan `BertForPreTraining` — jadi seluruh
    key masuk kategori encoder.
    """
    from collections import OrderedDict

    out = OrderedDict()
    n_prefixed = 0
    skipped = []
    for key, value in state_dict.items():
        if key.startswith("bert."):
            out[key] = value
        elif key.startswith("cls."):
            # Head MLM/NSP: biarkan apa adanya, memang tidak dipakai kelas target.
            out[key] = value
            skipped.append(key)
        else:
            out["bert." + key] = value
            n_prefixed += 1
    return out, {"n_key": len(state_dict), "n_diberi_prefiks": n_prefixed,
                 "n_key_cls_dilewati": len(skipped)}


def prepare_backbone(backbone: str, target_dir: str, *, force_download: bool = False,
                     force_rekey: bool = False) -> dict:
    """Unduh backbone lalu tulis ulang `pytorch_model.bin` dengan prefiks `bert.`.

    Idempoten: menulis penanda `_rekey.json`, dan melewati rekey bila penanda itu
    sudah ada untuk `hf_id` yang sama. Tanpa penanda ini, menjalankan sel dua
    kali akan menambahkan prefiks dua kali (`bert.bert.embeddings...`) dan
    hasilnya sama buruknya dengan tidak merekey sama sekali.
    """
    import torch

    spec = BACKBONES[backbone]
    dl = download_backbone(backbone, target_dir, force=force_download)
    rep = {"unduh": dl, "vocab": vocab_report(target_dir)}
    marker = os.path.join(target_dir, "_rekey.json")
    bin_path = os.path.join(target_dir, "pytorch_model.bin")

    if os.path.exists(marker) and not force_rekey:
        with open(marker, encoding="utf-8") as fh:
            done = json.load(fh)
        if done.get("hf_id") == spec["hf_id"]:
            rep["rekey"] = dict(done, dilewati="penanda _rekey.json sudah ada")
            rep["dir"] = target_dir
            return rep

    state_dict = torch.load(bin_path, map_location="cpu")
    sample_before = list(state_dict.keys())[:3]
    has_prefix = any(k.startswith("bert.") for k in state_dict)

    if has_prefix and not force_rekey:
        info = {"n_key": len(state_dict), "n_diberi_prefiks": 0,
                "catatan": "state_dict sudah memakai prefiks bert., tidak ditulis ulang"}
    else:
        new_sd, info = rekey_state_dict(state_dict)
        torch.save(new_sd, bin_path)
        state_dict = new_sd

    info.update({
        "hf_id": spec["hf_id"],
        "backbone": backbone,
        "needs_rekey_terduga": spec["needs_rekey"],
        "key_sebelum": sample_before,
        "key_sesudah": list(state_dict.keys())[:3],
        "n_key_berprefiks_bert": sum(1 for k in state_dict if k.startswith("bert.")),
    })
    with open(marker, "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=2, ensure_ascii=False)
    rep["rekey"] = info
    rep["dir"] = target_dir
    return rep


GATE_TENSORS = (
    "bert.embeddings.word_embeddings.weight",
    "bert.encoder.layer.0.attention.self.query.weight",
    "bert.encoder.layer.11.output.dense.weight",
)
"""Tiga tensor pemeriksa: embedding, layer pertama, layer terakhir.

Layer 0 dan 11 dipilih agar kegagalan sebagian (hanya sebagian layer termuat)
tetap tertangkap; memeriksa embedding saja tidak cukup.
"""


def gate_weights_loaded(model, checkpoint_dir: str, *, tensors=GATE_TENSORS) -> dict:
    """Gate 1: bandingkan bobot model terpasang dengan checkpoint di disk.

    `model` adalah hasil `BertForQuadABSA.from_pretrained(checkpoint_dir, ...)`.
    Perbandingan memakai `torch.equal` pada tensor CPU — bukan hanya cek nama key,
    karena key yang "ada" tidak menjamin nilainya ikut tersalin.
    """
    import torch

    raw = torch.load(os.path.join(checkpoint_dir, "pytorch_model.bin"),
                     map_location="cpu")
    live = model.state_dict()
    hasil = {}
    for name in tensors:
        ref = raw.get(name)
        got = live.get(name)
        if ref is None:
            hasil[name] = {"status": "GAGAL", "alasan": "tidak ada di checkpoint"}
            continue
        if got is None:
            hasil[name] = {"status": "GAGAL", "alasan": "tidak ada di model"}
            continue
        got = got.detach().to("cpu")
        if tuple(ref.shape) != tuple(got.shape):
            hasil[name] = {"status": "GAGAL", "alasan": f"bentuk {tuple(ref.shape)} vs {tuple(got.shape)}"}
            continue
        cocok = bool(torch.equal(ref.float(), got.float()))
        hasil[name] = {
            "status": "LULUS" if cocok else "GAGAL",
            "bentuk": list(ref.shape),
            "mean_checkpoint": float(ref.float().mean()),
            "mean_model": float(got.float().mean()),
        }
        if not cocok:
            hasil[name]["alasan"] = (
                "nilai berbeda — encoder kemungkinan terinisialisasi acak "
                "(lihat modeling.py:745, start_prefix='')")

    n_key_model_bert = sum(1 for k in live if k.startswith("bert."))
    n_key_ckpt_bert = sum(1 for k in raw if k.startswith("bert."))
    hilang = sorted(k for k in live if k.startswith("bert.") and k not in raw)

    return {
        "checkpoint_dir": checkpoint_dir,
        "tensor": hasil,
        "n_key_bert_model": n_key_model_bert,
        "n_key_bert_checkpoint": n_key_ckpt_bert,
        "key_model_tanpa_padanan_checkpoint": hilang[:10],
        "n_key_model_tanpa_padanan": len(hilang),
        "ok": all(v["status"] == "LULUS" for v in hasil.values()) and not hilang,
    }


def main(argv=None):
    """CLI: `python -m acos_id.checkpoint <backbone> <target_dir>`."""
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2:
        print("Pemakaian: python -m acos_id.checkpoint <backbone> <target_dir>")
        print("Backbone :", ", ".join(sorted(BACKBONES)))
        return 2
    rep = prepare_backbone(argv[0], argv[1])
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
