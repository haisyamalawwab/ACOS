"""Final verification: xrefs, code fences, running heads, page fill, sparse-page content."""
import re

import pymupdf

PDF = "dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf"
BOOK_TITLE = "Kata, Data, Rasa"
LABELS = {
    "PEMBUKA": "Kata Pengantar", "BAB 1": "Apa Itu ACOSE", "BAB 2": "Aspek & Opini",
    "BAB 3": "Kategori", "BAB 4": "Sentimen", "BAB 5": "Emosi",
    "BAB 6": "Format Data", "BAB 7": "Kasus Sulit & FAQ", "BAB 8": "Di Balik Layar",
}
FRAME_TOP, FRAME_BOTTOM = 70.9, 796.0

doc = pymupdf.open(PDF)
pages = [doc[i].get_text() for i in range(len(doc))]
print("pages:", len(pages))

print("=== text hygiene ===")
for label, pattern in (
    ("leftover file codes 022x", r"\b022(aa|[a-h])\b"),
    ("literal double backticks", r"``"),
    ("stray heading marks", r"(?m)^#{1,4}\s"),
    ("stray bold marks", r"\*\*"),
    ("typo bagaimanakerja", r"bagaimanakerja"),
    ("English leak Verdict-nya", r"Verdict-nya"),
):
    hits = [i + 1 for i, t in enumerate(pages) if re.search(pattern, t)]
    print(f"    {label:26} {'CLEAN' if not hits else 'FOUND on ' + str(hits[:8])}")

print("=== running head on chapter-opening pages ===")
bad = 0
for i, text in enumerate(pages):
    m = re.search(r"(?m)^(PEMBUKA|BAB \d)$", text)
    if not m:
        continue
    want = LABELS[m.group(1)]
    ok = want in text and BOOK_TITLE in text
    bad += 0 if ok else 1
    print(f"    p{i + 1:>3} {m.group(1):8} -> header {want!r:20} {'OK' if ok else 'MISSING'}")
print("    mismatches:", bad)

print("=== page fill ===")
low = []
for i in range(len(pages)):
    page = doc[i]
    ys = [y for b in page.get_text("blocks") if b[4].strip() for y in (b[1], b[3])]
    ys += [y for d in page.get_drawings() if d["rect"].height < 400
           for y in (d["rect"].y0, d["rect"].y1)]
    inner = [y for y in ys if FRAME_TOP < y < FRAME_BOTTOM]
    pct = (max(inner) - FRAME_TOP) / (FRAME_BOTTOM - FRAME_TOP) if inner else 0.0
    if pct < 0.45:
        low.append((i + 1, round(pct * 100)))
print("    under 45%:", low if low else "NONE")
for pno, pct in low:
    body = " / ".join(ln for ln in pages[pno - 1].split("\n") if ln.strip())
    body = body.replace(BOOK_TITLE, "").replace("Panduan Teknologi Tepat Guna", "")
    print(f"    p{pno} ({pct}%): {body[:180]!r}")
doc.close()
