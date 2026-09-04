"""Geometry audit: substitute for the visual gate when image review is unavailable.

Checks what a reviewer would otherwise catch by eye: content escaping the margins,
overlapping text, missing furniture, and panels/tables wider than the text column.
"""
import re

import pymupdf

PDF = "dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf"
BOOK_TITLE = "Kata, Data, Rasa"
SERIES = "Panduan Teknologi Tepat Guna"

# Frame in PDF points: margins 2.2cm x, 2.5cm top, 1.85cm bottom.
# Running head sits at y~45 and the footer at y~805, both intentionally outside the frame.
L, R = 62.4, 532.9
FURNITURE_TOP, FURNITURE_BOTTOM = 40.0, 815.0
TOL = 1.0

doc = pymupdf.open(PDF)
problems = []

for pno in range(1, len(doc)):          # page 0 is the cover, its own template
    page = doc[pno]
    text = page.get_text()

    if BOOK_TITLE not in text:
        problems.append((pno + 1, "running header missing"))
    if SERIES not in text:
        problems.append((pno + 1, "footer series line missing"))
    if not re.search(r"Seri 022\s*\n?\s*%d\b" % (pno + 1), text.replace("\u00a0", " ")):
        nums = re.findall(r"(?m)^\s*(\d+)\s*$", text)
        if str(pno + 1) not in nums:
            problems.append((pno + 1, "footer page number not %d" % (pno + 1)))

    spans = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"].strip():
                    spans.append(span)

    # Horizontal check uses word boxes: span boxes include trailing spaces, which
    # would report a 2-3pt overflow that has no visible ink.
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        if not word.strip():
            continue
        if x0 < L - TOL or x1 > R + TOL:
            problems.append((pno + 1, "word outside column: %.1f..%.1f %r"
                             % (x0, x1, word[:40])))

    for span in spans:
        _, y0, _, y1 = span["bbox"]
        if y0 < FURNITURE_TOP or y1 > FURNITURE_BOTTOM:
            problems.append((pno + 1, "text outside page body: y=%.1f..%.1f %r"
                             % (y0, y1, span["text"][:40])))

    for drawing in page.get_drawings():
        rect = drawing["rect"]
        if rect.width < 1 or rect.height < 1:
            continue
        if rect.x0 < L - TOL or rect.x1 > R + TOL:
            problems.append((pno + 1, "panel/rule outside column: %.1f..%.1f"
                             % (rect.x0, rect.x1)))

    # Overlapping text rows: same y band, horizontally intersecting, different content.
    rows: dict[int, list] = {}
    for span in spans:
        rows.setdefault(int(span["bbox"][1] // 4), []).append(span)
    for band in rows.values():
        for i, a in enumerate(band):
            for b in band[i + 1:]:
                ax0, _, ax1, _ = a["bbox"]
                bx0, _, bx1, _ = b["bbox"]
                overlap = min(ax1, bx1) - max(ax0, bx0)
                if overlap > 3:
                    problems.append((pno + 1, "overlapping text %r / %r"
                                     % (a["text"][:24], b["text"][:24])))

print("pages audited: %d (cover excluded)" % (len(doc) - 1))
print("problems:", len(problems))
for pno, why in problems[:25]:
    print("   p%-3d %s" % (pno, why))
doc.close()
