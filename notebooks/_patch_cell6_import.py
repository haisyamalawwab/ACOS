"""Ganti sel impor colab_utils di ketiga notebook master pipeline.

Sel lama membungkus ``from colab_utils import (...)`` dengan
``except ModuleNotFoundError``, yang tidak pernah bisa menangkap kegagalan yang
sebenarnya terjadi: modul yang ada tapi kekurangan nama melempar ``ImportError``.
Rinciannya ada di notebooks/_cell6_recommended.py, yang jadi sumber tunggal isi
sel pengganti di sini supaya keduanya tidak bisa berbeda.

Skrip ini idempoten: sel yang sudah memakai versi baru dilewati, bukan ditambal
dua kali.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNIPPET = os.path.join(HERE, "_cell6_recommended.py")

TARGETS = (
    "00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb",
    "00_ACOS_Master_Pipeline_Colab_PRO.ipynb",
    "00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb",
)

OLD_MARKER = "except ModuleNotFoundError:"
NEW_MARKER = "REQUIRED_UTILS = ("
# Sel dikenali lewat pola lama MAUPUN pola baru. Kalau hanya pola lama yang
# dipakai, replay setelah patch berhasil akan melaporkan "tidak ditemukan" —
# aman, tapi menyesatkan; yang benar adalah "sudah memakai versi baru".
CELL_MARKERS = ("Masukkan direktori penting ke sys.path", NEW_MARKER)


def cell_body() -> str:
    """Ambil isi sel dari snippet, buang blok komentar penjelas di kepalanya.

    Komentar itu ditujukan untuk pembaca diff, bukan untuk orang yang membuka
    notebook, jadi yang ikut masuk hanya kode plus komentar di dalamnya.
    """
    src = io.open(SNIPPET, encoding="utf-8").read()
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("import re"))
    header = (
        "# Impor colab_utils dengan pemilihan salinan yang lengkap.\n"
        "#\n"
        "# `except ModuleNotFoundError` tidak dipakai lagi: modul yang ADA tapi\n"
        "# kekurangan nama melempar ImportError, jadi guard lama tidak pernah aktif.\n"
        "# Salinan dipilih dengan memindai nama def/class (tanpa mengimpor, supaya\n"
        "# tetap benar sebelum pip install), lalu sys.modules dibersihkan agar\n"
        "# salinan usang tidak dipakai ulang dari cache.\n"
        "\n"
    )
    return header + "\n".join(lines[start:]).rstrip("\n") + "\n"


def source_lines(text: str) -> list:
    """Pecah jadi format ``source`` nbformat: setiap baris menyimpan \\n-nya."""
    return text.splitlines(keepends=True)


def patch(path: str, body: str) -> str:
    raw = io.open(path, encoding="utf-8").read()
    nb = json.loads(raw)
    hits = [
        i for i, c in enumerate(nb["cells"])
        if c["cell_type"] == "code"
        and any(m in "".join(c["source"]) for m in CELL_MARKERS)
    ]
    if not hits:
        return "sel target tidak ditemukan"
    if len(hits) > 1:
        return f"sel target ambigu di indeks {hits}"

    idx = hits[0]
    current = "".join(nb["cells"][idx]["source"])
    # Cek penanda BARU lebih dulu: kalau dibalik, patch yang diulang akan
    # menambal sel yang sudah benar.
    if NEW_MARKER in current:
        return f"sel {idx} sudah memakai versi baru — dilewati"
    if OLD_MARKER not in current:
        return f"sel {idx} tidak cocok pola lama; tidak diubah"

    nb["cells"][idx]["source"] = source_lines(body)
    nb["cells"][idx]["outputs"] = []
    nb["cells"][idx]["execution_count"] = None

    out = json.dumps(nb, ensure_ascii=False, indent=1)
    if raw.endswith("\n"):
        out += "\n"
    io.open(path, "w", encoding="utf-8", newline="\n").write(out)
    return f"sel {idx} diganti ({len(body.splitlines())} baris)"


def main() -> int:
    body = cell_body()
    compile(body, "<cell>", "exec")  # tolak menulis kode yang tidak bisa di-parse
    for name in TARGETS:
        path = os.path.join(HERE, name)
        if not os.path.isfile(path):
            print(f"  ?  {name}: tidak ada")
            continue
        print(f"  -> {name}: {patch(path, body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
