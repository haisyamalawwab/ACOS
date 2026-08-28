import json

with open('notebooks/00_ACOS_Master_Pipeline_Colab_PRO.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open('notebooks/cells_dump.txt', 'w', encoding='utf-8') as out:
    for i, cell in enumerate(nb.get('cells', [])):
        out.write(f"=== CELL {i} ({cell.get('cell_type')}) ===\n")
        out.write("".join(cell.get('source', [])))
        out.write("\n" + "="*50 + "\n\n")

print(f"Dumped {len(nb.get('cells', []))} cells to notebooks/cells_dump.txt")
