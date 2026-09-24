import json, sys

sys.stdout.reconfigure(encoding="utf-8")
nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells_to_inspect = [2, 4, 44, 46, 67, 69, 79]
for idx in cells_to_inspect:
    src = "".join(nb['cells'][idx]['source'])
    print(f"=== CELL {idx} ===")
    lines = src.split("\n")
    print("\n".join(lines[:35]))
    if len(lines) > 35:
        print(f"... ({len(lines) - 35} more lines)")
    print()
