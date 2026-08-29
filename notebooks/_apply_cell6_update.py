import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PRO = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb")
DST_STAGED = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb")
REC_PY = os.path.join(HERE, "_cell6_recommended.py")

with open(REC_PY, "r", encoding="utf-8") as f:
    rec_code = f.read()

code_lines = rec_code.splitlines(keepends=True)
start_idx = 0
for idx, line in enumerate(code_lines):
    if line.startswith("import re"):
        start_idx = idx
        break

clean_code_lines = ["\n", "# Impor colab_utils dengan pemilihan salinan yang lengkap & robust\n"] + code_lines[start_idx:]

# 1. Update PRO_Resume
with open(SRC_PRO, "r", encoding="utf-8") as f:
    nb_pro = json.load(f)

pro_target_cell = None
for idx, cell in enumerate(nb_pro["cells"]):
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        if "colab_utils" in src and ("REQUIRED_UTILS" in src or "Import colab_utils" in src):
            pro_target_cell = idx
            break

if pro_target_cell is not None:
    nb_pro["cells"][pro_target_cell]["source"] = clean_code_lines
    with open(SRC_PRO, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb_pro, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[OK] PRO_Resume cell {pro_target_cell} updated successfully.")
else:
    print("[ERROR] Could not find colab_utils cell in PRO_Resume.")

# 2. Update V2_STAGED directly
with open(DST_STAGED, "r", encoding="utf-8") as f:
    nb_staged = json.load(f)

staged_target_cell = None
for idx, cell in enumerate(nb_staged["cells"]):
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        if "colab_utils" in src and ("REQUIRED_UTILS" in src or "Import colab_utils" in src):
            staged_target_cell = idx
            break

if staged_target_cell is not None:
    nb_staged["cells"][staged_target_cell]["source"] = clean_code_lines
    with open(DST_STAGED, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb_staged, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[OK] V2_STAGED cell {staged_target_cell} updated successfully.")
else:
    print("[ERROR] Could not find colab_utils cell in V2_STAGED.")
