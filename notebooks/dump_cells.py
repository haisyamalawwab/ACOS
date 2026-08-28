import json

with open('notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb.get('cells', [])):
    print(f"=== CELL {i} ({cell.get('cell_type')}) ===")
    print("".join(cell.get('source', [])))
    print("\n" + "="*50 + "\n")
