import json, sys

sys.stdout.reconfigure(encoding="utf-8")

nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb["cells"]):
    ctype = cell["cell_type"]
    first_lines = "".join(cell["source"][:3]).strip().replace("\n", " | ")
    first_lines = "".join(c if ord(c) < 128 else "?" for c in first_lines)
    print(f"Cell {i:2d} [{ctype}]: {first_lines[:100]}")
