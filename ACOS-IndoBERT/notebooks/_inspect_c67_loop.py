import json, sys

sys.stdout.reconfigure(encoding="utf-8")
with open("00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src67 = "".join(nb['cells'][67]['source'])
lines = src67.split("\n")

for i in range(50, 140):
    if i < len(lines):
        print(f"L{i:3d}: {lines[i]}")
