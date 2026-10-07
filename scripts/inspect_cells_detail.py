import json

def inspect_cell_content(nb_path, cell_indices):
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print("=" * 80)
    print(f"FILE: {nb_path}")
    print("=" * 80)
    for idx in cell_indices:
        if idx < len(nb['cells']):
            cell = nb['cells'][idx]
            src = "".join(cell['source'])
            print(f"--- CELL {idx} ({cell['cell_type']}) ---")
            print(src[:1000])
            print("...\n")

inspect_cell_content('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/02_ACOS_V5_2_Universal_FullExperiment_AllPlatforms.ipynb', [12, 13, 34, 35])
inspect_cell_content('d:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/03_ACOS_V5_3_Classification_Prediction_IndoBERT.ipynb', [12, 13, 34, 35, 36, 37, 38, 39])
