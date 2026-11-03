"""Render infografik bar chart: Review-Level vs Clause-Level segmentation coverage.

Hasil: img/acos_review_vs_clause_coverage.png/.webp/.jpg (background putih,
biru = Review-Level, emerald = Clause-Level, gaya publikasi riset).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 2400, 1500
WHITE = (255, 255, 255)
INK = (15, 23, 42)
SUB = (100, 116, 139)
GRID = (226, 232, 240)
BLUE = (37, 99, 235)
BLUE_LT = (96, 165, 250)
EMERALD = (5, 150, 105)
EMERALD_LT = (52, 211, 153)
RED = (220, 38, 38)

FDIR = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


F_TITLE = font("arialbd.ttf", 58)
F_SUB = font("arial.ttf", 28)
F_PANEL = font("arialbd.ttf", 36)
F_VAL = font("arialbd.ttf", 44)
F_LBL = font("arialbd.ttf", 26)
F_NOTE = font("arial.ttf", 23)
F_BADGE = font("arialbd.ttf", 25)
F_AXIS = font("arial.ttf", 21)

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

# ---------- header ----------
d.text((W / 2, 78), "ACOS Extraction: Review-Level vs Clause-Level Segmentation",
       font=F_TITLE, fill=INK, anchor="mm")
d.text((W / 2, 138), "Cakupan aspek & opini yang berhasil diekstrak — kehilangan akibat truncasi urutan pada level review vs segmentasi klausa",
       font=F_SUB, fill=SUB, anchor="mm")

# ---------- chart geometry ----------
BASE_Y = 1180          # garis 0%
TOP_Y = 420            # garis 100%
SCALE = (BASE_Y - TOP_Y) / 100.0
panels = [
    dict(x0=170, x1=1130, name="REVIEW-LEVEL", col=BLUE, col_lt=BLUE_LT,
         vals=[61.5, 48.0], note="loss akibat sequence truncation"),
    dict(x0=1270, x1=2230, name="CLAUSE-LEVEL", col=EMERALD, col_lt=EMERALD_LT,
         vals=[100.0, 100.0], note="setiap klausa utuh · konteks penuh"),
]

# gridlines + axis labels
for pct in (0, 25, 50, 75, 100):
    y = BASE_Y - pct * SCALE
    for p in panels:
        d.line([(p["x0"], y), (p["x1"], y)],
               fill=GRID if pct else (148, 163, 184), width=2 if pct == 0 else 1)
    d.text((128, y), f"{pct}%", font=F_AXIS, fill=SUB, anchor="rm")

# dashed 100% reference across both panels
y100 = BASE_Y - 100 * SCALE
x = 170
while x < 2230:
    d.line([(x, y100), (min(x + 22, 2230), y100)], fill=(148, 163, 184), width=2)
    x += 40

# ---------- panels ----------
labels = ["Aspect Coverage", "Opinion Coverage"]
for p in panels:
    cx = (p["x0"] + p["x1"]) / 2
    # panel header chip
    hw = 34 * len(p["name"]) + 60
    d.rounded_rectangle([cx - hw / 2, 200, cx + hw / 2, 262], radius=14,
                        fill=p["col"], outline=p["col"], width=2)
    d.text((cx, 230), p["name"], font=F_PANEL, fill=WHITE, anchor="mm")

    bw = 210
    gap = (p["x1"] - p["x0"] - 2 * bw) / 3
    for i, v in enumerate(p["vals"]):
        bx0 = p["x0"] + gap + i * (bw + gap)
        bx1 = bx0 + bw
        h_ = v * SCALE
        # bar with vertical gradient (emerald/blue)
        steps = int(h_)
        for sy in range(steps):
            t = sy / max(1, steps - 1)
            col = tuple(int(p["col_lt"][k] + (p["col"][k] - p["col_lt"][k]) * t) for k in range(3))
            d.line([(bx0, BASE_Y - sy), (bx1, BASE_Y - sy)], fill=col, width=1)
        d.rounded_rectangle([bx0, BASE_Y - h_, bx1, BASE_Y], radius=12, outline=None)
        # rounded top cap
        d.rounded_rectangle([bx0, BASE_Y - h_, bx1, BASE_Y - h_ + 34], radius=12, fill=p["col"])
        d.rectangle([bx0, BASE_Y - h_ + 20, bx1, BASE_Y - h_ + 34], fill=p["col"])
        # value label
        d.text(((bx0 + bx1) / 2, BASE_Y - h_ - 42), f"{v:.1f}%", font=F_VAL,
               fill=p["col"], anchor="mm")
        # x label
        d.text(((bx0 + bx1) / 2, BASE_Y + 42), labels[i], font=F_LBL, fill=INK, anchor="mm")

    # note under x labels
    d.text((cx, BASE_Y + 96), p["note"], font=F_NOTE, fill=SUB, anchor="mm")

# ---------- delta annotations (left panel: losses) ----------
p = panels[0]
for i, (v, lab) in enumerate(zip(p["vals"], ["−38,5 pp", "−52,0 pp"])):
    bw = 210
    gap = (p["x1"] - p["x0"] - 2 * bw) / 3
    bx0 = p["x0"] + gap + i * (bw + gap)
    yv = BASE_Y - v * SCALE
    d.line([(bx0 + bw / 2, yv + 8), (bx0 + bw / 2, y100 - 6)], fill=RED, width=3)
    d.polygon([(bx0 + bw / 2 - 9, yv + 14), (bx0 + bw / 2 + 9, yv + 14),
               (bx0 + bw / 2, yv + 2)], fill=RED)
    d.text((bx0 + bw / 2 + 16, (yv + y100) / 2), lab, font=F_BADGE, fill=RED, anchor="lm")

# ---------- badge 0 UNK (right panel) ----------
d.rounded_rectangle([1600, 276, 1900, 334], radius=16,
                    outline=EMERALD, width=4, fill=(236, 253, 245))
d.line([(1638, 305), (1648, 316), (1666, 292)], fill=EMERALD, width=5)
d.text((1782, 305), "0 UNK tokens", font=F_BADGE, fill=EMERALD, anchor="mm")

# ---------- footer legend ----------
lx = 700
for col, lab in ((BLUE, "Review-Level (review utuh dipotong max_seq)"),
                 (EMERALD, "Clause-Level (satu klausa = satu unit)")):
    d.rounded_rectangle([lx, 1330, lx + 34, 1364], radius=7, fill=col)
    d.text((lx + 50, 1347), lab, font=F_NOTE, fill=INK, anchor="lm")
    lx += 640
d.text((W / 2, 1425), "ACOS-IndoBERT · evaluasi cakupan segmentasi Step 1 (co-extraction aspek & opini)",
       font=F_AXIS, fill=SUB, anchor="mm")

# ---------- save ----------
out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img"))
os.makedirs(out_dir, exist_ok=True)
base = os.path.join(out_dir, "acos_review_vs_clause_coverage")
img.save(base + ".png", "PNG")
img.save(base + ".webp", "WEBP", quality=92)
img.save(base + ".jpg", "JPEG", quality=92)
print("saved:", base + ".png / .webp / .jpg", img.size)
