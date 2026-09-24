import json, sys

sys.stdout.reconfigure(encoding="utf-8")
nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [2, 4]:
    src = "".join(nb['cells'][idx]['source'])
    print(f"=== FULL CELL {idx} ===")
    print(src)
    print()
