import sys, json
sys.stdout.reconfigure(encoding='utf-8')
nb = json.load(open('notebooks/05_ACOS_Evaluation_and_Interactive_Inference.ipynb', encoding='utf-8'))
print(f"Total cells: {len(nb['cells'])}")
for i, c in enumerate(nb['cells']):
    src = "".join(c['source'])
    print(f"Cell {i} [{c['cell_type']}] len={len(src)}: {src[:60].strip()}")
