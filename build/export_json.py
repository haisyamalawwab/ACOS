"""Export the parsed book to JSON so the DOCX renderer shares the PDF's parser.

Running both outputs off one parser keeps them identical in content: the same
cross-reference rewriting (022x -> Bab n), the same dropped per-file metadata
lines, and the same chapter titles.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from build_book import (  # noqa: E402
    BOOK_SERIES,
    BOOK_SUBTITLE,
    BOOK_TITLE,
    CHAPTERS,
    REPORTS,
    parse_markdown,
)

OUT = os.path.join(HERE, "book.json")


def block_to_dict(block) -> dict:
    if block.kind == "heading":
        return {"kind": "heading", "level": block.level,
                "text": block.text, "flag": block.flag}
    if block.kind == "para":
        return {"kind": "para", "text": block.text}
    if block.kind == "list":
        return {"kind": "list", "ordered": block.flag == "ol", "items": list(block.items)}
    if block.kind == "quote":
        return {"kind": "quote",
                "items": [{"kind": k, "text": t} for k, t in block.items]}
    if block.kind == "code":
        return {"kind": "code", "text": block.text}
    if block.kind == "table":
        return {"kind": "table", "rows": [list(r) for r in block.rows]}
    raise ValueError("unknown block kind %r" % block.kind)


def main() -> None:
    chapters = []
    for stem, kicker, running, title in CHAPTERS:
        with open(os.path.join(REPORTS, stem + ".md"), encoding="utf-8") as fh:
            blocks = parse_markdown(fh.read())

        # The file's own H1 is replaced by the book-style chapter title.
        dropped_h1 = False
        kept = []
        for b in blocks:
            if not dropped_h1 and b.kind == "heading" and b.level == 1:
                dropped_h1 = True
                continue
            kept.append(block_to_dict(b))

        chapters.append({
            "stem": stem, "kicker": kicker, "running": running,
            "title": title, "blocks": kept,
        })

    payload = {
        "title": BOOK_TITLE,
        "subtitle": BOOK_SUBTITLE,
        "series": BOOK_SERIES,
        "chapters": chapters,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    counts: dict[str, int] = {}
    for ch in chapters:
        for b in ch["blocks"]:
            counts[b["kind"]] = counts.get(b["kind"], 0) + 1
    print("wrote", OUT)
    print("chapters:", len(chapters), "| blocks:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
