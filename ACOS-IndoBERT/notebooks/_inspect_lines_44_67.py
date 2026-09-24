import json, sys

sys.stdout.reconfigure(encoding="utf-8")
with open("00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for c_idx in [44, 67]:
    src = "".join(nb['cells'][c_idx]['source'])
    lines = src.split("\n")
    print(f"=== CELL {c_idx} (Total lines: {len(lines)}) ===")
    for i, l in enumerate(lines):
        if any(k in l for k in ["for epoch in", "step1_history.append", "step2_history.append", "best_step", "torch.save", "st.step", "st.note"]):
            print(f"L{i:3d}: {l}")
    print()
