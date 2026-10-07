import json

def inspect_notebook(path):
    print("=" * 60)
    print("INSPECTING:", path)
    print("=" * 60)
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print(f"Total cells: {len(nb['cells'])}")
    for i, cell in enumerate(nb['cells']):
        lines = cell['source']
        if isinstance(lines, list):
            lines = [l.strip('\n') for l in lines]
            first_line = lines[0] if lines else ""
        else:
            first_line = lines.split('\n')[0] if lines else ""
        safe_line = first_line[:75].encode('ascii', errors='replace').decode()
        if cell['cell_type'] == 'markdown':
            print(f"Cell {i:2d} [MD]  : {safe_line}")
        else:
            print(f"Cell {i:2d} [CODE]: {safe_line}")

inspect_notebook('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/02_ACOS_V5_2_1_Embedding_Classification_Prediction.ipynb')
