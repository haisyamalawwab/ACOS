"""Pecah 00_ACOS_Master_Pipeline_V1_1_BERT.ipynb menjadi 4 notebook serial.

Berbasis penanda `# === SECTION:<nama> ===` (bukan indeks sel kaku), sehingga
selamat dari penambahan sel di generator:

  V1_1_01_setup.ipynb          SECTION:setup (env, config, sesi, gate, backbone,
                               EDA, state-saver, recovery, ensure)
  V1_1_02_step1_train.ipynb    bootstrap + SECTION:step1 (init, cache, train)
  V1_1_03_step2_train.ipynb    bootstrap + SECTION:step2 (bridge, init, cache, train)
  V1_1_04_eval_inference.ipynb bootstrap + SECTION:eval (eval, audit, demo)

Notebook 02-04 diawali sel bootstrap: penanda bahwa sel env+config+helpers+sesi
master harus dijalankan (atau notebook 01) sebelum recovery — state training
sendiri tersimpan di disk sesi (pipeline_state.pkl + resume JSON + rolling
checkpoint + pointer latest_pipeline_state_{DOMAIN}.pkl).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_V1_1_BERT.ipynb")

BOOTSTRAP_MD = ("Jalankan `V1_1_01_setup.ipynb` (atau sel env+config+helpers+sesi master) "
                "lebih dulu — state sesi dibaca dari disk, bukan dari memori.")


def md(title, body=""):
    src = [title + "\n"]
    if body:
        src.append(body)
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def section_of(cell):
    if cell.get("cell_type") != "code":
        return None
    for line in cell.get("source", [])[:3]:
        line = line.strip()
        if line.startswith("# === SECTION:"):
            return line.split(":", 2)[1].split("=")[0].strip()
    return None


def main():
    with open(SRC, encoding="utf-8") as f:
        nb_src = json.load(f)
    groups = {"setup": [], "step1": [], "step2": [], "eval": []}
    pending_md = []
    for c in nb_src["cells"]:
        if c.get("cell_type") == "markdown":
            pending_md.append(c)
            continue
        sec = section_of(c) or "setup"
        groups.setdefault(sec, []).append((pending_md, c))
        pending_md = []
    # markdown tanpa kode pengikut (judul akhir) -> eval
    tail = pending_md

    plans = [
        ("V1_1_01_setup.ipynb", "V1.1 — 01: Setup, Sesi, Gate, Backbone, EDA, Recovery",
         [("setup", False)]),
        ("V1_1_02_step1_train.ipynb", "V1.1 — 02: Step-1 Training (BERT-CRF, cache-aware)",
         [("step1", True)]),
        ("V1_1_03_step2_train.ipynb", "V1.1 — 03: Bridge + Step-2 Training (single-head, cache-aware)",
         [("step2", True)]),
        ("V1_1_04_eval_inference.ipynb", "V1.1 — 04: Evaluasi Final + Audit + Demo",
         [("eval", True)]),
    ]
    setup_code = [c for _, c in groups.get("setup", [])
                  if c.get("cell_type") == "code"]
    for fname, title, parts in plans:
        cells = [md("# " + title)]
        for sec, boot in parts:
            if boot:
                cells.append(md("## Bootstrap",
                                "Sel env+config+helpers disalin dari `01_setup` agar "
                                "notebook ini mandiri pasca-restart kernel. Jalankan "
                                "semua sel Bootstrap sebelum sel tahap."))
                cells.extend(setup_code)
            for mds, c in groups.get(sec, []):
                cells.extend(mds)
                cells.append(c)
        if "_04" in fname:
            cells.extend(tail)
        nb_out = {"cells": cells,
                  "metadata": dict(nb_src.get("metadata", {})),
                  "nbformat": 4, "nbformat_minor": 5}
        dst = os.path.join(HERE, fname)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(nb_out, f, ensure_ascii=False, indent=1)
        n_code = sum(1 for c in cells if c.get("cell_type") == "code")
        print(f"{fname}: {len(cells)} sel ({n_code} kode)")


if __name__ == "__main__":
    main()
