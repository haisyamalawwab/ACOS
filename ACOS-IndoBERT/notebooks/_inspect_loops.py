import json, sys

sys.stdout.reconfigure(encoding="utf-8")
nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell_idx in [44, 67]:
    src = "".join(nb['cells'][cell_idx]['source'])
    print(f"=== SEARCH IN CELL {cell_idx} ===")
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if "history.append" in line or "torch.save" in line or "val_f1 > best" in line:
            start = max(0, i - 4)
            end = min(len(lines), i + 10)
            print(f"--- Line {i} ---")
            print("\n".join(lines[start:end]))
            print()
