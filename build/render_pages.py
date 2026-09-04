"""Render every page of the final book to PNG for the visual acceptance pass."""
import os

import pymupdf

PDF = "dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf"
OUT = "dist/pages"
ZOOM = 1.7  # ~122 dpi: enough to judge layout, small enough to load fast

os.makedirs(OUT, exist_ok=True)
for stale in os.listdir(OUT):
    if stale.endswith(".png"):
        os.remove(os.path.join(OUT, stale))

doc = pymupdf.open(PDF)
matrix = pymupdf.Matrix(ZOOM, ZOOM)
for pno in range(len(doc)):
    pix = doc[pno].get_pixmap(matrix=matrix)
    path = os.path.join(OUT, "p%02d.png" % (pno + 1))
    pix.save(path)
doc.close()
print("rendered %d pages to %s" % (pno + 1, os.path.abspath(OUT)))
