import json

def compare_cells(path1, path2, indices):
    with open(path1, 'r', encoding='utf-8') as f:
        nb1 = json.load(f)
    with open(path2, 'r', encoding='utf-8') as f:
        nb2 = json.load(f)
    for idx in indices:
        print("="*60)
        print(f"INDEX {idx}")
        s1 = "".join(nb1['cells'][idx]['source'])[:300].encode('ascii', errors='replace').decode()
        s2 = "".join(nb2['cells'][idx]['source'])[:300].encode('ascii', errors='replace').decode()
        print(f"--- {path1.split('/')[-1]} ---\n{s1}\n")
        print(f"--- {path2.split('/')[-1]} ---\n{s2}\n")

compare_cells(
    'd:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/02_ACOS_V5_2_Universal_FullExperiment_AllPlatforms.ipynb',
    'd:/laragon/www/ACOS-ASLI/ACOS-IndoBERT/notebooks/02_ACOS_V5_2_1_Embedding_Classification_Prediction.ipynb',
    [0, 1, 6, 7, 12, 13, 34, 35, 36, 37]
)
