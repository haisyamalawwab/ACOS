"""Render the book cover (template 02 Corporate Editorial) and merge it into the body PDF."""
from __future__ import annotations

import os
import sys

SD = os.environ["SD"]
sys.path.insert(0, os.path.join(SD, "scripts"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

from cover_render import detect_fonts, render_cover  # noqa: E402

from build_book import BOOK_TITLE, merge_cover, register_fonts  # noqa: E402

OUT_DIR = os.path.join(ROOT, "dist")
COVER = os.path.join(OUT_DIR, "_cover.pdf")
BODY = os.path.join(OUT_DIR, "_body.pdf")
FINAL = os.path.join(OUT_DIR, "Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf")

# Same cascade palette the body uses (minimal / monochrome / seed 42).
PALETTE = {
    "primary": "#475b66",
    "text": "#151617",
    "muted": "#80878a",
    "bg": "#ffffff",
}

CONTENT = {
    "kicker": "PANDUAN TEKNOLOGI TEPAT GUNA · SERI 022",
    "hero": BOOK_TITLE,
    # The hero is a three-word triad, so the summary has to decode it: this is the
    # only place a reader learns what the book actually teaches.
    "summary": (
        "Kata menjadi data, supaya komputer bisa membaca rasa — keluhan dan pujian "
        "di balik setiap ulasan. Buku ini mengajarkan cara menandai lima elemen "
        "ACOSE: aspek, kategori, opini, sentimen, dan emosi. Ditulis untuk pembaca "
        "umum tanpa latar belakang ilmu komputer."
    ),
    # cover_render.para() feeds a ReportLab Paragraph, which collapses "\n" into a
    # space; only <br/> breaks a line. Without this the subtitle runs into the
    # project line and reads as one run-on sentence.
    "meta": (
        "Panduan Anotasi ACOSE untuk Ulasan Berbahasa Indonesia<br/>"
        "Proyek ACOS-ASLI · Taksonomi resto_id<br/>"
        "Edisi pertama · September 2026"
    ),
    "footer": "PROYEK ACOS-ASLI · PANDUAN ANOTASI ACOSE",
    "year": "2026",
    "word": "PANDUAN",
}

FONT_OVERRIDES = {
    # Indonesian text is Latin-only; Segoe UI reads far more corporate than a CJK face.
    "sans": ("CoverSans", "C:/Windows/Fonts/segoeui.ttf", 0),
    "latin": ("CoverSans", "C:/Windows/Fonts/segoeui.ttf", 0),
}

# Template 03 "Monolith" is the selection-matrix default for Authority/Corporate and is
# best-for white papers, proposals and technical standards. Template 02 was ruled out:
# _t02_corporate() measures the year watermark at 180pt but never calls setFont, so it
# renders as 12pt Helvetica instead of a large tint.
TEMPLATE = "03"


def main() -> None:
    register_fonts()
    os.makedirs(OUT_DIR, exist_ok=True)
    fonts = detect_fonts(overrides=FONT_OVERRIDES)
    print("cover fonts:", fonts)
    render_cover(TEMPLATE, CONTENT, COVER, palette=PALETTE, fonts=fonts)
    print("cover:", COVER, "template:", TEMPLATE)
    pages = merge_cover(COVER, BODY, FINAL)
    print("final:", FINAL, "pages:", pages)


if __name__ == "__main__":
    main()
