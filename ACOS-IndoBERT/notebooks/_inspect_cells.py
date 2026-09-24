import json

nb = json.load(open('00_ACOS_Master_Pipeline_Colab.ipynb', encoding='utf-8'))
code_cells = [(i, c) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code']
for idx, (nb_idx, cell) in enumerate(code_cells):
    first_line = cell['source'][0][:100].strip() if cell['source'] else '(no source)'
    print(f"Code cell #{idx+1}: nb_idx={nb_idx}, first_line={first_line}")
