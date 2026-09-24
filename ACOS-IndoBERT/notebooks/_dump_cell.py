import json, sys

nb = json.load(open('00_ACOS_Master_Pipeline_Colab.ipynb', encoding='utf-8'))
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

cell_num = int(sys.argv[1]) if len(sys.argv) > 1 else 9
src = ''.join(code_cells[cell_num - 1]['source'])

with open(f'_cell_{cell_num}_dump.txt', 'w', encoding='utf-8') as f:
    f.write(src)
print(f"Cell #{cell_num} written to _cell_{cell_num}_dump.txt")
