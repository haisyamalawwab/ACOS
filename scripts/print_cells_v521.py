import json

with open('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/02_ACOS_V5_2_1_Embedding_Classification_Prediction.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx in [12, 13, 34, 35, 36, 37, 38, 39]:
    cell = nb['cells'][idx]
    src = "".join(cell['source'])
    print("=" * 70)
    print(f"CELL {idx} [{cell['cell_type']}]")
    print(src)
