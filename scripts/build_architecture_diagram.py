"""Render diagram arsitektur dua tahap ACOS-IndoBERT menjadi PNG/WEBP high-res.

Hasil: img/acos_indobert_architecture.png (+ .webp)
Metode: Pillow, tema dark navy / cyan / white, isometric flow boxes.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 3800, 1900

# ---------- palette ----------
BG_TOP = (6, 13, 26)
BG_BOT = (11, 27, 51)
NAVY_PANEL = (15, 34, 56)
NAVY_PANEL_DK = (10, 24, 42)
BORDER = (30, 58, 95)
CYAN = (34, 211, 238)
CYAN_SOFT = (125, 211, 252)
WHITE = (248, 250, 252)
DIM = (148, 163, 184)
GREEN = (34, 197, 94)
GRAY = (148, 163, 184)
RED = (239, 68, 68)
AMBER = (251, 191, 36)

FDIR = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


F_TITLE = font("arialbd.ttf", 84)
F_SUB = font("arial.ttf", 34)
F_ZONE = font("arialbd.ttf", 40)
F_BOX = font("arialbd.ttf", 30)
F_BOXSM = font("arial.ttf", 24)
F_MONO = font("consola.ttf", 24)
F_MONOS = font("consola.ttf", 21)
F_CHIP = font("consola.ttf", 18)
F_TINY = font("arial.ttf", 21)
F_LEG = font("arial.ttf", 24)

img = Image.new("RGBA", (W, H), (0, 0, 0, 255))


# ---------- background gradient + dot grid ----------
def gradient():
    base = Image.new("RGBA", (W, H))
    bd = ImageDraw.Draw(base)
    for y in range(H):
        t = y / H
        col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)) + (255,)
        bd.line([(0, y), (W, y)], fill=col)
    return base


img = gradient()
main = ImageDraw.Draw(img)
for gx in range(60, W, 90):
    for gy in range(60, H, 90):
        main.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(56, 92, 140, 46))

# ---------- helpers ----------
def overlay_copy():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def stamp(layer, blur=0):
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    global img
    img = Image.alpha_composite(img, layer)
    main = ImageDraw.Draw(img)
    globals()["main"] = main
    return main


def rbox(layer, xy, fill, outline=None, width=3, radius=18, alpha=255):
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    if alpha != 255:  # not used; keep signature simple
        pass


def text(layer, xy, s, f, fill, anchor="mm"):
    d = ImageDraw.Draw(layer)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def arrow(layer, pts, color=CYAN, width=6, head=22):
    d = ImageDraw.Draw(layer)
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=color, width=width)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    for off in (0.5, -0.5):
        hx = x2 - head * math.cos(ang + off * 0.9)
        hy = y2 - head * math.sin(ang + off * 0.9)
        d.line([(x2, y2), (hx, hy)], fill=color, width=width)
    d.ellipse([x2 - 5, y2 - 5, x2 + 5, y2 + 5], fill=color)


def iso_stack(layer, cx, cy, label_lines, n=5, w_=380, pitch=76):
    """Isometric encoder: tumpukan layer paralelogram."""
    d = ImageDraw.Draw(layer)
    top_off, dh = 66, 30
    y0 = cy + (n - 1) * pitch / 2
    for i in range(n):
        y = y0 - i * pitch
        t = i / max(1, n - 1)
        front = tuple(int(NAVY_PANEL[k] + (CYAN[k] - NAVY_PANEL[k]) * (0.10 + 0.28 * (1 - t))) for k in range(3)) + (255,)
        topc = tuple(int(front[k] * 1.25) for k in range(3)) + (255,)
        sidec = tuple(int(front[k] * 0.7) for k in range(3)) + (255,)
        x0, x1 = cx - w_ / 2, cx + w_ / 2
        # front face
        d.rounded_rectangle([x0, y, x1, y + dh], radius=6, fill=front,
                            outline=(70, 160, 200, 220), width=2)
        # top face
        d.polygon([(x0, y), (x0 + top_off, y - 34), (x1 + top_off, y - 34), (x1, y)],
                  fill=topc, outline=(90, 190, 230, 200))
        # right side
        d.polygon([(x1, y), (x1 + top_off, y - 34), (x1 + top_off, y - 34 + dh), (x1, y + dh)],
                  fill=sidec, outline=(70, 160, 200, 180))
    for j, ln in enumerate(label_lines):
        text(layer, (cx, y0 + dh + 34 + j * 30), ln, F_BOXSM, CYAN_SOFT, "mm")


# ---------- title ----------
L = overlay_copy()
text(L, (W / 2, 92), "ACOS-IndoBERT  ·  Two-Stage ABSA Pipeline Architecture", F_TITLE, WHITE, "mm")
text(L, (W / 2, 168), "Step 1 Co-Extraction (BERT-CRF quadruples)   →   Candidate Pair Bridge   →   Step 2 Joint Classification (13 Kategori × 3 Sentimen = 39 label)", F_SUB, DIM, "mm")
stamp(L)

# ---------- zone frames (dashed, glow) ----------
zones = [
    (80, 250, 1380, 1810, "STEP 1 · CO-EXTRACTION"),
    (1420, 250, 2260, 1810, "CANDIDATE PAIR BRIDGE"),
    (2300, 250, 3720, 1810, "STEP 2 · JOINT CLASSIFICATION"),
]
gl = overlay_copy()
gd = ImageDraw.Draw(gl)
for x0, y0, x1, y1, _ in zones:
    gd.rounded_rectangle([x0, y0, x1, y1], radius=26, outline=CYAN + (70,), width=3)
stamp(gl, blur=2)

L = overlay_copy()
d = ImageDraw.Draw(L)
for x0, y0, x1, y1, name in zones:
    d.rounded_rectangle([x0 + 24, y0 - 34, x0 + 24 + 30 * len(name) + 60, y0 + 34], radius=16,
                        fill=NAVY_PANEL_DK + (255,), outline=CYAN + (200,), width=3)
    text(L, (x0 + 54 + 15 * len(name), y0), name, F_ZONE, CYAN, "mm")
stamp(L)

# ================= STEP 1 =================
L = overlay_copy()
# input clause box
rbox(L, (150, 890, 470, 1060), NAVY_PANEL + (255,), CYAN + (230,), 4, 20)
text(L, (310, 935), "Input Clause", F_BOX, WHITE, "mm")
text(L, (310, 985), "“pelayanannya ramah", F_MONOS, CYAN_SOFT, "mm")
text(L, (310, 1015), "tapi lambat”", F_MONOS, CYAN_SOFT, "mm")

# encoder 1
iso_stack(L, 760, 940, ["IndoBERT-base Encoder", "indobenchmark/indobert-base-p1"])

# upper branch: BIO-CRF
rbox(L, (560, 380, 1180, 610), NAVY_PANEL + (255,), GREEN + (220,), 4, 20)
text(L, (870, 420), "BIO-CRF Sequence Tagger", F_BOX, WHITE, "mm")
text(L, (870, 458), "6 label · span aspek/opini eksplisit", F_BOXSM, GREEN, "mm")
chips = [("makanan", "B-ASP", GREEN), ("enak", "I-ASP", GREEN), ("harga", "B-OPN", AMBER), ("mahal", "I-OPN", AMBER), ("dan", "O", DIM)]
cx0 = 585
for tok, tag_, col in chips:
    wch = 13 * len(tok) + 26
    rbox(L, (cx0, 495, cx0 + wch, 538), NAVY_PANEL_DK + (255,), BORDER + (255,), 2, 10)
    text(L, (cx0 + wch / 2, 516), tok, F_CHIP, WHITE, "mm")
    rbox(L, (cx0 + 6, 548, cx0 + wch - 6, 588), col + (60,), col + (230,), 2, 10)
    text(L, (cx0 + wch / 2, 568), tag_, F_CHIP, col, "mm")
    cx0 += wch + 12

# lower branch: CLS heads
rbox(L, (560, 1290, 1180, 1520), NAVY_PANEL + (255,), RED + (180,), 4, 20)
text(L, (870, 1332), "CLS Classification Heads", F_BOX, WHITE, "mm")
text(L, (870, 1372), "aspek & opini implisit (implicit)", F_BOXSM, RED, "mm")
rbox(L, (640, 1410, 760, 1470), NAVY_PANEL_DK + (255,), CYAN + (200,), 3, 10)
text(L, (700, 1440), "[CLS]", F_MONO, CYAN, "mm")
arrow(L, [(768, 1440), (838, 1420)], DIM, 4, 14)
arrow(L, [(768, 1440), (838, 1462)], DIM, 4, 14)
for yy, lab in ((1418, "σ  implicit aspect"), (1462, "σ  implicit opinion")):
    d = ImageDraw.Draw(L)
    d.ellipse([846, yy - 14, 874, yy + 14], outline=CYAN_SOFT + (230,), width=3)
    text(L, (860, yy), "σ", F_MONOS, CYAN_SOFT, "mm")
    text(L, (1035, yy), lab, F_MONOS, WHITE, "mm")

# quadruples output node
rbox(L, (1090, 880, 1340, 1060), NAVY_PANEL_DK + (255,), CYAN + (255,), 5, 20)
text(L, (1215, 930), "Quadruples", F_BOX, CYAN, "mm")
text(L, (1215, 975), "(a, c, o, s)", F_MONO, WHITE, "mm")
text(L, (1215, 1015), "aspect·category", F_TINY, DIM, "mm")
text(L, (1215, 1040), "opinion·sentiment", F_TINY, DIM, "mm")

# arrows step1
arrow(L, [(478, 975), (552, 950)], CYAN, 7, 24)
arrow(L, [(915, 830), (960, 780), (935, 700), (880, 622)], GREEN, 7, 24)
arrow(L, [(940, 1120), (1010, 1200), (950, 1262), (885, 1286)], RED, 7, 24)
arrow(L, [(1160, 620), (1195, 750), (1208, 868)], GREEN, 7, 24)
arrow(L, [(1160, 1288), (1200, 1180), (1212, 1072)], RED, 7, 24)
stamp(L)

# ================= BRIDGE =================
L = overlay_copy()
a_nodes = [(1560, 620, "a₁"), (1560, 940, "a₂"), (1560, 1260, "a₃")]
o_nodes = [(2120, 620, "o₁"), (2120, 940, "o₂"), (2120, 1260, "o₃")]
d = ImageDraw.Draw(L)
for (ax, ay, _), (ox, oy, _) in [(A, O) for A in a_nodes for O in o_nodes]:
    col = CYAN + (90,)
    mx1 = ax + (ox - ax) * 0.35
    mx2 = ax + (ox - ax) * 0.65
    my = (ay + oy) / 2 + (0 if ay == oy else (30 if oy > ay else -30))
    d.line([(ax, ay), (mx1, my * 0.5 + ay * 0.5), (mx2, my * 0.5 + oy * 0.5), (ox, oy)],
           fill=col, width=4)
for x, y, lab in a_nodes:
    d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=NAVY_PANEL_DK + (255,), outline=GREEN + (240,), width=4)
    text(L, (x, y), lab, F_MONO, GREEN, "mm")
for x, y, lab in o_nodes:
    d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=NAVY_PANEL_DK + (255,), outline=AMBER + (240,), width=4)
    text(L, (x, y), lab, F_MONO, AMBER, "mm")
for mmx, mmy in [(1560, 470), (2120, 470)]:
    text(L, (mmx, mmy), "aspects" if mmx < 1800 else "opinions", F_BOXSM, DIM, "mm")
rbox(L, (1660, 860, 2020, 1020), NAVY_PANEL_DK + (255,), CYAN + (240,), 4, 20)
text(L, (1840, 905), "Cartesian Pairs", F_BOX, CYAN, "mm")
text(L, (1840, 950), "(aᵢ , oⱼ)", F_MONO, WHITE, "mm")
text(L, (1840, 990), "|A| × |O| candidates", F_TINY, DIM, "mm")
text(L, (1840, 1420), "setiap pasangan menjadi satu contoh latih/inferensi Step 2", F_BOXSM, DIM, "mm")
arrow(L, [(1348, 970), (1500, 950), (1614, 944)], CYAN, 7, 24)
stamp(L)

# ================= STEP 2 =================
L = overlay_copy()
# input pair+clause
rbox(L, (2360, 860, 2640, 1040), NAVY_PANEL + (255,), CYAN + (230,), 4, 20)
text(L, (2500, 915), "Candidate Pair", F_BOX, WHITE, "mm")
text(L, (2500, 955), "+ Clause", F_BOX, WHITE, "mm")
text(L, (2500, 1000), "[CLS] aᵢ sep oⱼ [SEP]", F_MONOS, CYAN_SOFT, "mm")
arrow(L, [(2210, 940), (2352, 940)], CYAN, 7, 24)

# encoder 2
iso_stack(L, 2860, 940, ["IndoBERT Encoder", "(fine-tuned, Step 2)"])
arrow(L, [(2648, 945), (2668, 942), (2676, 941)], CYAN, 7, 24)

# 39-class head box
rbox(L, (3120, 700, 3560, 1200), NAVY_PANEL + (255,), CYAN + (255,), 5, 22)
text(L, (3340, 745), "39-class Classifier Head", F_BOX, WHITE, "mm")
text(L, (3340, 785), "Single-Head · softmax", F_BOXSM, CYAN_SOFT, "mm")
arrow(L, [(3048, 928), (3112, 928)], CYAN, 7, 24)
gx0, gy0 = 3160, 830
for gi in range(13):
    x = gx0 + gi * 29
    for k, col in enumerate((GREEN, GRAY, RED)):
        y = gy0 + 90 + k * 22
        d = ImageDraw.Draw(L)
        d.rounded_rectangle([x, y, x + 22, y + 16], radius=4, fill=col + (230,))
text(L, (3340, 1080), "13 Kategori × 3 Sentimen", F_BOXSM, WHITE, "mm")
lg = [("positive", GREEN), ("neutral", GRAY), ("negative", RED)]
for i, (lab, col) in enumerate(lg):
    x = 3185 + i * 125
    d = ImageDraw.Draw(L)
    d.ellipse([x, 1120, x + 18, 1138], fill=col + (255,))
    text(L, (x + 66, 1129), lab, F_TINY, DIM, "mm")

# final output banner
rbox(L, (3080, 1330, 3620, 1530), NAVY_PANEL_DK + (255,), GREEN + (230,), 5, 22)
text(L, (3350, 1385), "Final 4-Tuples", F_BOX, GREEN, "mm")
text(L, (3350, 1428), "(Aspect, Category, Opinion, Sentiment)", F_BOXSM, WHITE, "mm")
d = ImageDraw.Draw(L)
d.line([(3112, 1470), (3124, 1484), (3146, 1452)], fill=GREEN, width=5)
text(L, (3168, 1475), "(pelayanannya, SERVICE, lambat, negative)", F_MONOS, CYAN_SOFT, "lm")
arrow(L, [(3350, 1210), (3350, 1320)], GREEN, 8, 26)
stamp(L)

# ---------- footer legend ----------
L = overlay_copy()
d = ImageDraw.Draw(L)
d.line([(150, 1862), (230, 1862)], fill=CYAN, width=6)
text(L, (246, 1862), "aliran data", F_LEG, DIM, "lm")
d.rounded_rectangle([420, 1848, 500, 1876], radius=8, outline=CYAN + (120,), width=3)
text(L, (516, 1862), "tahap / stage", F_LEG, DIM, "lm")
text(L, (760, 1862), "ACOS-IndoBERT · BERT-CRF + Single-Head 39 label · seed 42", F_LEG, (72, 96, 128, 255), "lm")
stamp(L)

# ---------- save ----------
out_dir = os.path.join(os.path.dirname(__file__), "..", "img")
os.makedirs(out_dir, exist_ok=True)
png = os.path.abspath(os.path.join(out_dir, "acos_indobert_architecture.png"))
webp = os.path.abspath(os.path.join(out_dir, "acos_indobert_architecture.webp"))
final = img.convert("RGB")
final.save(png, "PNG")
final.save(webp, "WEBP", quality=92)
print("saved:", png, final.size)
print("saved:", webp)
