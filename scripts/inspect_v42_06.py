import json

with open('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/V4_2_06_prediction_indobert.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i in [11, 12, 13, 14]:
    if i < len(nb['cells']):
        print(f"=== CELL {i} ({nb['cells'][i]['cell_type']}) ===")
        print("".join(nb['cells'][i]['source'])[:1500])
