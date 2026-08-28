import json

with open('notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb.get('cells', []))}")
for i, cell in enumerate(nb.get('cells', [])):
    cell_type = cell.get('cell_type')
    src = "".join(cell.get('source', []))
    first_few_lines = " | ".join([line.strip() for line in src.split("\n")[:3] if line.strip()])
    print(f"[{i:02d}] ({cell_type:4s}): {first_few_lines[:150]}")
