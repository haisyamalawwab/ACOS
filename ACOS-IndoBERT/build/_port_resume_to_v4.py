"""Port resume-per-epoch dari patch manual .ipynb V4 ke generator V4.

Fitur resume-per-epoch (rolling checkpoint + optimizer state per epoch) semula
hanya ada di `00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb` karena di-patch
manual setelah notebook dibangkitkan. Generator `_build_v4_indobert.py` bersifat
idempoten (menulis ulang dari nol), jadi build berikutnya akan menghapus fitur
itu diam-diam.

Skrip ini mem-port fitur tersebut ke generator:
  1. Sel referensi (master) = isi empat sel .ipynb V4 saat ini (teruji kerja).
  2. Suntikkan ke `apply_patches()` sebagai RESUME_SPECS: setiap sel diganti
     UTUH dengan isi referensi (pola yang sama dengan `cells[i] = code(...)`
     yang sudah dipakai generator V4). Penggantian utuh dipilih karena jauh
     lebih andal daripada anchor difflib — diff karakter menghasilkan ratusan
     anchor kecil yang tidak stabil.
  3. Bangun ulang notebook V4 dan verifikasi 4 sel resume byte-identik dengan
     referensi + lulus ast.parse.

Idempoten: bila penanda `RESUME_SPECS = [` sudah ada di generator, suntikan
dilewati (cek string baru sebelum string lama).
"""
from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NB_DIR = os.path.join(os.path.dirname(HERE), "notebooks")

GEN_V4 = os.path.join(NB_DIR, "_build_v4_indobert.py")
NOTEBOOK = os.path.join(NB_DIR, "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb")

# Setiap needle harus unik di antara SEMUA sel kode notebook hasil V2 sehingga
# find_code(cells, *needles) menunjuk tepat satu sel.
NEEDLES = {
    "5b": ("step1_already_done = os.path.exists(step1_bin)",
           "STEP1_SKIP_TRAINING = (not FORCE_RETRAIN_STEP1)"),
    "5e": ("5e. Training Step 1 BERT-CRF", "optimizer_1.step()"),
    "8b": ("step2_already_done = os.path.exists(step2_bin)",
           "STEP2_SKIP_TRAINING = (not FORCE_RETRAIN_STEP2)"),
    "8e": ("8e. Training Step 2 Category-Sentiment", "optimizer_2.step()"),
}

MARKER_SPECS = "RESUME_SPECS = ["


def cell_src(nb_path, needles):
    nb = json.load(io.open(nb_path, encoding="utf-8"))
    hit = None
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if all(n in src for n in needles):
            if hit is not None:
                raise SystemExit(f"needles {needles} tidak unik di {nb_path}")
            hit = src
    if hit is None:
        raise SystemExit(f"sel dengan penanda {needles} tidak ada di {nb_path}")
    return hit


def py_lit(s: str) -> str:
    if '"""' not in s and "\\" not in s:
        return '"""' + s + '"""'
    return repr(s)


def emit_spec_block(ref_cells) -> str:
    lines = [
        "# ── Resume training per-epoch (port dari patch manual .ipynb V4) ───────────\n",
        "# Diport oleh ACOS-IndoBERT/build/_port_resume_to_v4.py. Keempat sel diganti\n",
        "# UTUH dengan isi versi teruji di .ipynb: sel deteksi 5b/8b membaca\n",
        "# step1/2_resume.json, sel training 5e/8e merestorasi bobot+optimizer lalu\n",
        "# melanjutkan dari epoch berikutnya (rolling checkpoint per epoch).\n",
        "RESUME_SPECS = [\n",
    ]
    for name in ("5b", "8b", "5e", "8e"):
        a, b = NEEDLES[name]
        lines.append("    ((%s, %s),\n" % (py_lit(a), py_lit(b)))
        lines.append("     %s),\n" % py_lit(ref_cells[name]))
    lines.append("]\n")
    return "".join(lines)


STEP_CODE = '''    # 14. Resume training per-epoch (rolling checkpoint + optimizer state): sel
    #      deteksi 5b/8b membaca step1/2_resume.json (+ menyalin checkpoint epoch
    #      terakhir dari sesi lama), sel training 5e/8e merestorasi bobot +
    #      optimizer lalu melanjutkan dari epoch berikutnya. Keempat sel diganti
    #      utuh dengan versi teruji di .ipynb V4 — pola yang sama dengan penulisan
    #      ulang sel lain di generator ini. Dibangkitkan/diperbarui oleh
    #      `ACOS-IndoBERT/build/_port_resume_to_v4.py`.
    for _needles, _full in RESUME_SPECS:
        cells[find_code(cells, *_needles)] = code(_full)

'''


def main():
    if not os.path.isfile(NOTEBOOK):
        return SystemExit(f"referensi tidak ada: {NOTEBOOK}")

    # Empat sel referensi dari .ipynb teruji — sebelum build ulang menimpanya.
    ref_cells = {k: cell_src(NOTEBOOK, v) for k, v in NEEDLES.items()}
    for k, v in ref_cells.items():
        print(f"   referensi sel {k}: {len(v)} karakter")

    gen = io.open(GEN_V4, encoding="utf-8").read()
    patched = False
    if MARKER_SPECS in gen:
        print("RESUME_SPECS sudah ada di generator — suntikan dilewati.")
    else:
        # 1. Konstanta: sisipkan sebelum def main().
        anchor_def = "\n\ndef main():"
        if gen.count(anchor_def) != 1:
            return SystemExit(f"anchor {anchor_def!r} tidak unik di generator")
        gen = gen.replace(anchor_def, "\n" + emit_spec_block(ref_cells) + anchor_def, 1)

        # 2. Langkah patch: sisipkan sebelum return apply_patches.
        anchor_ret = '    return cells, {"n_sel_tokenized_base": n_tb}'
        if gen.count(anchor_ret) != 1:
            return SystemExit(f"anchor return apply_patches tidak unik di generator")
        gen = gen.replace(anchor_ret, STEP_CODE + anchor_ret, 1)

        io.open(GEN_V4, "w", encoding="utf-8", newline="\n").write(gen)
        patched = True
        print("Generator dipatch: RESUME_SPECS + langkah 14 di apply_patches.")

    if not patched:
        print("Verifikasi dilewati (tidak ada perubahan).")
        return 0

    # 3. Verifikasi: bangun ulang notebook V4 (menjalankan generator V2 dulu).
    r = subprocess.run([sys.executable, GEN_V4], cwd=NB_DIR,
                       capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        return SystemExit("generator V4 gagal")
    new_cells = {k: cell_src(NOTEBOOK, v) for k, v in NEEDLES.items()}
    for k in NEEDLES:
        # code() menstrip newline akhir, jadi bandingkan hingga newline terakhir.
        if new_cells[k] != ref_cells[k].rstrip("\n"):
            return SystemExit(f"sel {k} hasil build berbeda dari referensi")
        ast.parse(new_cells[k])
        print(f"   sel {k}: byte-identik (s/d newline akhir) + ast.parse LULUS")
    print("PORT RESUME-PER-EPOCH OK — notebook V4 ter-reproduksi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())