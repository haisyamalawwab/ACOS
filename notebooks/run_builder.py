import json
import ast
import os
import sys

# Configure UTF-8 for stdout if possible
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Import the builder function
from build_pro_notebooks import build_notebook

nb_dict = build_notebook()
print(f"Generated notebook with {len(nb_dict['cells'])} cells.")

# Syntax test for all code cells
for i, cell in enumerate(nb_dict["cells"]):
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        # Remove ipython magics like !pip for ast testing
        clean_src = "\n".join([line if not line.strip().startswith("!") else "# " + line for line in src.split("\n")])
        try:
            ast.parse(clean_src)
            print(f"[OK] Cell {i:02d} Python Syntax OK")
        except SyntaxError as e:
            print(f"[ERROR] Cell {i:02d} Syntax Error: {e}")
            sys.exit(1)

# Save to target files
targets = [
    "notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb",
    "notebooks/00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb"
]
for target in targets:
    with open(target, "w", encoding="utf-8") as f:
        json.dump(nb_dict, f, ensure_ascii=False, indent=1)
    print(f"[SAVED] Successfully written to: {target}")
