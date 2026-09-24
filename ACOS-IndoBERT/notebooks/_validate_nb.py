import json
import ast
import sys

sys.stdout.reconfigure(encoding="utf-8")

nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

tested_cells = [2, 4, 6, 44, 46, 67, 69, 79]
for idx in tested_cells:
    cell = nb['cells'][idx]
    src = "".join(cell['source'])
    # Skip lines starting with ! or % for ast.parse
    py_lines = [l for l in src.split("\n") if not l.strip().startswith("!") and not l.strip().startswith("%")]
    py_code = "\n".join(py_lines)
    try:
        ast.parse(py_code)
        print(f"Cell {idx:2d} ({cell['cell_type']}): Python Syntax OK ✅")
    except SyntaxError as e:
        print(f"Cell {idx:2d} SyntaxError ❌: {e}")
