"""Pasang sel bootstrap fallback ke notebook master pipeline UPDATE.

Mengganti sel navigasi direktori (sel 4) dengan versi yang memanggil
``acos_bootstrap.ensure_project()``, dan menyisipkan satu sel markdown penjelas
di depannya. Idempoten: dijalankan ulang tidak menumpuk sel.

Jalankan: ``python notebooks/_patch_update_bootstrap.py``
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional

NOTEBOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "00_ACOS_Master_Pipeline_Colab_UPDATE.ipynb")
MARKER = "acos_bootstrap"
ANCHOR = "## 2. Directory Navigation & Path Initialization"

MARKDOWN_SOURCE = """### 2a. Bootstrap & fallback ke repo induk

Sel di bawah menyatakan seluruh prasyarat pipeline, memeriksanya satu per satu,
lalu mengunduh dari repo induk GitHub apa pun yang hilang. Yang diperiksa:

1. **Folder proyek** — kalau `MyDrive/ACOS` belum ada, dibuat; kalau folder
   `Extract-Classify-ACOS`/`data` telanjur tersimpan di root Drive, dipindahkan
   ke dalamnya.
2. **34 file wajib** — modul pipeline, `bert_utils/`, data latih, dan
   `tokenized_data/`. File **nol byte** diperlakukan sebagai tidak ada, karena
   unduhan Drive yang terputus meninggalkan file kosong yang lolos
   `os.path.exists` lalu gagal jauh di dalam training.
3. **16 simbol `colab_utils`** — bukan cuma "modulnya bisa diimpor". Repo ini
   punya tiga salinan `colab_utils.py` dengan isi berbeda, dan salinan di root
   repo kehilangan 10 dari 16 simbol yang dipakai notebook. Salinan yang tidak
   lengkap di-rename menjadi `.incomplete` agar tidak membayangi yang benar.

Strateginya berjenjang dari yang termurah: pindahkan folder salah tempat → kalau
yang hilang ≥ 6 file, satu `git clone --depth 1` → sisanya ditambal per-file via
HTTP dengan 3 kali percobaan → verifikasi simbol. Unduhan ditulis ke file
sementara lalu di-rename, jadi file separuh terunduh tidak pernah terlihat utuh.

Kalau ada prasyarat yang tetap tidak terpenuhi, sel ini **gagal di sini** dengan
daftar file yang bermasalah. Itu disengaja: lebih baik berhenti sekarang daripada
crash di tengah training dua jam kemudian."""

CODE_SOURCE = '''import os
import sys
import urllib.request

# Ambil modul bootstrap itu sendiri kalau belum ada. Ini satu-satunya unduhan
# yang tidak bisa di-bootstrap oleh bootstrap.
BOOTSTRAP_URL = "https://raw.githubusercontent.com/haisyamalawwab/ACOS/main/notebooks/acos_bootstrap.py"

def _locate_bootstrap():
    for candidate in ("acos_bootstrap.py",
                      os.path.join("notebooks", "acos_bootstrap.py"),
                      "/content/drive/MyDrive/ACOS/notebooks/acos_bootstrap.py",
                      "/content/ACOS/notebooks/acos_bootstrap.py"):
        if os.path.isfile(candidate) and os.path.getsize(candidate) > 0:
            return os.path.dirname(os.path.abspath(candidate)) or os.getcwd()
    urllib.request.urlretrieve(BOOTSTRAP_URL, "acos_bootstrap.py")
    print("acos_bootstrap.py diunduh dari repo induk.")
    return os.getcwd()

_bootstrap_dir = _locate_bootstrap()
if _bootstrap_dir not in sys.path:
    sys.path.insert(0, _bootstrap_dir)

from acos_bootstrap import BootstrapError, ensure_project, import_colab_utils

# Periksa semua prasyarat; unduh dari induk yang hilang. strict=True menghentikan
# notebook di sini kalau ada yang wajib tidak terpenuhi.
bootstrap = ensure_project(
    repo="haisyamalawwab/ACOS",
    branch="main",
    prefer_drive=True,
    include_tokenized=True,
    strict=True,
)

base_project_dir = bootstrap.base
extract_dir = bootstrap.extract_dir
notebooks_dir = bootstrap.notebooks_dir
save_dir = bootstrap.save_dir

# Ambil simbol colab_utils lewat pemeriksa yang membedakan "paket belum
# ter-install" dari "salinan colab_utils salah". Pesannya menyebut penyebabnya,
# bukan sekadar satu nama pertama yang gagal seperti ImportError biasa.
try:
    _utils = import_colab_utils()
except BootstrapError as exc:
    print(f"Gagal menyiapkan colab_utils: {exc}")
    raise

globals().update(_utils)

print()
print(f"Base project directory : {base_project_dir}")
print(f"Extract & model dir    : {extract_dir}")
print(f"Save directory         : {save_dir}")
print(f"colab_utils            : {len(_utils)} simbol siap dipakai")
'''


def load(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(path: str, nb: Dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def as_source(text: str) -> List[str]:
    """nbformat menyimpan source sebagai list baris ber-newline, kecuali baris akhir."""
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])


def find_anchor(cells: List[Dict]) -> int:
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "markdown" and ANCHOR in "".join(cell["source"]):
            return i
    raise SystemExit(f"tidak menemukan sel markdown berisi {ANCHOR!r}")


def patch(path: str = NOTEBOOK) -> int:
    nb = load(path)
    cells = nb["cells"]
    anchor = find_anchor(cells)

    # Sel kode yang mau diganti adalah sel kode pertama setelah anchor.
    target = next(
        (i for i in range(anchor + 1, len(cells)) if cells[i]["cell_type"] == "code"), None
    )
    if target is None:
        raise SystemExit("tidak menemukan sel kode setelah anchor")

    already = MARKER in "".join(cells[target]["source"])
    old_lines = len("".join(cells[target]["source"]).splitlines())

    new_code = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": dict(cells[target].get("metadata", {})),
        "outputs": [],
        "source": as_source(CODE_SOURCE),
    }
    cells[target] = new_code

    # Sisipkan penjelas hanya kalau belum ada.
    have_md = any(
        c["cell_type"] == "markdown" and "2a. Bootstrap" in "".join(c["source"])
        for c in cells
    )
    if not have_md:
        cells.insert(target, {
            "cell_type": "markdown",
            "metadata": {},
            "source": as_source(MARKDOWN_SOURCE),
        })

    save(path, nb)
    print(f"{'diperbarui' if already else 'dipatch'}: {path}")
    print(f"  sel kode #{target}: {old_lines} baris -> {len(CODE_SOURCE.splitlines())} baris")
    print(f"  sel markdown penjelas: {'sudah ada' if have_md else 'disisipkan'}")
    print(f"  total sel: {len(cells)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(patch(sys.argv[1] if len(sys.argv) > 1 else NOTEBOOK))
