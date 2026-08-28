"""Reading and writing the two on-disk formats, schema-driven.

Extraction format (``data/`` and ``tokenized_data/*_quad_bert.tsv``)::

    text <TAB> <tuple> <TAB> <tuple> ...
    tuple = aspect category sentiment opinion [emotion]

Pair format (``tokenized_data/*_pair.tsv``), input to the classification stage::

    text####aspect opinion <TAB> LABELKEY LABELKEY ...

Both readers accept the quintuple and the quadruple; a quad file read under the
quint schema gets the emotion default filled in, which is what keeps every
existing file usable while annotation is in progress.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from .schema import IMPLICIT, SchemaError, Tup, TupleSchema, format_span, get_schema
from .spans import RemapStats, remap_record
from .taxonomy import LabelSpaceSet

PAIR_SEP = "####"


@dataclass
class Record:
    """One sentence and its tuples."""

    text: str
    tuples: List[Tup] = field(default_factory=list)
    schema: Optional[TupleSchema] = None
    line_no: int = -1

    @property
    def words(self) -> List[str]:
        return self.text.strip().split()

    def label_values(self) -> List[Dict[str, str]]:
        out = []
        for tup in self.tuples:
            out.append({n: str(tup[n]) for n in (self.schema or tup.schema).labels})
        return out

    def pair_key(self, tup: Tup) -> str:
        schema = self.schema or tup.schema
        spans = " ".join(format_span(tup.span(n)) for n in schema.spans)
        return f"{self.text}{PAIR_SEP}{spans}"


@dataclass
class PairExample:
    """One (sentence, span-combination) candidate with its label keys."""

    text: str
    spans: Tuple[Tuple[int, int], ...]
    label_keys: List[str] = field(default_factory=list)
    line_no: int = -1

    def key(self) -> str:
        return f"{self.text}{PAIR_SEP}{' '.join(format_span(s) for s in self.spans)}"

    def to_line(self) -> str:
        labels = " ".join(self.label_keys)
        return f"{self.key()}\t{labels}" if labels else self.key()


# -- extraction format -----------------------------------------------------
def parse_record(
    line: str,
    schema,
    *,
    line_no: int = -1,
    strict: bool = True,
    repairs: Optional[List[str]] = None,
) -> Optional[Record]:
    schema = get_schema(schema)
    parts = line.rstrip("\n").rstrip("\r").split("\t")
    if len(parts) < 2 or not parts[0].strip():
        return None
    text = parts[0]
    tuples: List[Tup] = []
    for cell in parts[1:]:
        if not cell.strip():
            continue
        local: List[str] = []
        try:
            tuples.append(schema.parse(cell, repairs=local))
        except SchemaError as exc:
            if strict:
                raise SchemaError(f"line {line_no}: {exc}") from exc
            continue
        if repairs is not None:
            repairs.extend(f"line {line_no}: {r}" for r in local)
    if not tuples:
        return None
    return Record(text=text, tuples=tuples, schema=schema, line_no=line_no)


def read_records(
    path: str,
    schema,
    *,
    strict: bool = True,
    repairs: Optional[List[str]] = None,
) -> List[Record]:
    schema = get_schema(schema)
    out: List[Record] = []
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            rec = parse_record(line, schema, line_no=i, strict=strict, repairs=repairs)
            if rec is not None:
                out.append(rec)
    return out


def format_record(rec: Record, schema=None) -> str:
    schema = get_schema(schema or rec.schema)
    cells = [schema.format(t) for t in rec.tuples]
    return "\t".join([rec.text, *cells])


def write_records(path: str, records: Iterable[Record], schema=None) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for rec in records:
            fh.write(format_record(rec, schema) + "\n")
            n += 1
    return n


# -- pair format -----------------------------------------------------------
def parse_pair_line(line: str, n_spans: int = 2, *, line_no: int = -1) -> Optional[PairExample]:
    raw = line.rstrip("\n").rstrip("\r")
    if not raw.strip():
        return None
    parts = raw.split("\t")
    head = parts[0]
    if PAIR_SEP not in head:
        raise SchemaError(f"line {line_no}: pair line without {PAIR_SEP!r}: {head!r}")
    text, span_str = head.split(PAIR_SEP, 1)
    fields = span_str.split()
    if len(fields) != n_spans:
        raise SchemaError(
            f"line {line_no}: expected {n_spans} spans, got {len(fields)}: {span_str!r}"
        )
    spans = []
    for f in fields:
        a, b = f.split(",")
        spans.append((int(a), int(b)))
    keys: List[str] = []
    for cell in parts[1:]:
        for tok in cell.split():
            if tok not in keys:
                keys.append(tok)
    return PairExample(text=text, spans=tuple(spans), label_keys=keys, line_no=line_no)


def read_pairs(path: str, n_spans: int = 2) -> List[PairExample]:
    out: List[PairExample] = []
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            pe = parse_pair_line(line, n_spans, line_no=i)
            if pe is not None:
                out.append(pe)
    return out


def write_pairs(path: str, pairs: Iterable[PairExample]) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for pe in pairs:
            fh.write(pe.to_line() + "\n")
            n += 1
    return n


def records_to_pairs(
    records: Sequence[Record],
    schema,
    spaces: LabelSpaceSet,
    *,
    unknown_label: str = "raise",
    source: str = "",
) -> List[PairExample]:
    """Collapse tuples sharing the same spans into one multi-label pair example."""
    schema = get_schema(schema)
    index: Dict[str, PairExample] = {}
    order: List[str] = []
    where = f"{source}: " if source else ""
    for rec in records:
        for tup in rec.tuples:
            spans = tuple(tup.span(n) for n in schema.spans)
            values = {n: str(tup[n]) for n in spaces.elements}
            for element, value in values.items():
                if value not in spaces.space(element).labels:
                    msg = (
                        f"{where}line {rec.line_no}: '{value}' is not in the {element} "
                        f"label space {list(spaces.space(element).labels)}"
                    )
                    if unknown_label == "raise":
                        raise SchemaError(msg)
                    if unknown_label == "skip":
                        break
            else:
                key = f"{rec.text}{PAIR_SEP}{' '.join(format_span(s) for s in spans)}"
                pe = index.get(key)
                if pe is None:
                    pe = PairExample(text=rec.text, spans=spans, line_no=rec.line_no)
                    index[key] = pe
                    order.append(key)
                label_key = spaces.join(values)
                if label_key not in pe.label_keys:
                    pe.label_keys.append(label_key)
    return [index[k] for k in order]


# -- conversion pipeline ---------------------------------------------------
def convert_file(
    tokenizer,
    in_path: str,
    out_path: str,
    schema,
    *,
    subword_limit: Optional[int] = 126,
    report_path: Optional[str] = None,
    strict: bool = True,
    max_unk_ratio: Optional[float] = 0.05,
) -> Dict[str, object]:
    """Retokenize an extraction file and remap its spans, writing a build report."""
    schema = get_schema(schema)
    repairs: List[str] = []
    records = read_records(in_path, schema, strict=strict, repairs=repairs)
    stats = RemapStats()
    total_words = 0
    out_records: List[Record] = []
    for rec in records:
        stats.rows += 1
        total_words += len(rec.words)
        try:
            text, tuples, _ = remap_record(
                tokenizer, rec.text, rec.tuples, schema,
                stats=stats, subword_limit=subword_limit,
            )
        except Exception as exc:  # noqa: BLE001 - recorded, not swallowed
            stats.dropped_rows += 1
            stats.errors.append(f"line {rec.line_no}: {exc}")
            if strict:
                raise
            continue
        out_records.append(Record(text=text, tuples=tuples, schema=schema, line_no=rec.line_no))

    write_records(out_path, out_records, schema)
    report = {
        "input": in_path,
        "output": out_path,
        "schema": schema.name,
        "tokenizer": getattr(tokenizer, "describe", lambda: {})(),
        "subword_limit": subword_limit,
        "total_words": total_words,
        "unk_ratio": stats.unk_ratio(total_words),
        "span_repairs": repairs[:50],
        "span_repair_count": len(repairs),
        **stats.as_dict(),
    }
    if report_path:
        os.makedirs(os.path.dirname(os.path.abspath(report_path)) or ".", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
    if max_unk_ratio is not None and report["unk_ratio"] > max_unk_ratio:
        raise SchemaError(
            f"unknown-token ratio {report['unk_ratio']:.2%} exceeds the "
            f"{max_unk_ratio:.0%} budget - the tokenizer and the data disagree"
        )
    return report


def build_pair_files(
    records: Sequence[Record],
    schema,
    spaces: LabelSpaceSet,
    out_path: str,
    *,
    unknown_label: str = "raise",
    source: str = "",
) -> Dict[str, object]:
    pairs = records_to_pairs(
        records, schema, spaces, unknown_label=unknown_label, source=source
    )
    write_pairs(out_path, pairs)
    multi = sum(1 for p in pairs if len(p.label_keys) > 1)
    return {
        "output": out_path,
        "pairs": len(pairs),
        "multi_label_pairs": multi,
        "label_keys_used": len({k for p in pairs for k in p.label_keys}),
        "joint_space_size": len(spaces.joint_labels()),
    }


def cross_product_pairs(
    text: str,
    span_groups: Sequence[Sequence[Tuple[int, int]]],
) -> List[PairExample]:
    """Enumerate span combinations for the classification stage.

    Replaces ``tokenized_data/get_1st_pairs.py``, which mis-parsed tags whose
    prefix letter also starts a coordinate (see :func:`parse_tag`).
    """
    groups = [list(g) or [IMPLICIT] for g in span_groups]
    combos: List[Tuple[Tuple[int, int], ...]] = [()]
    for group in groups:
        combos = [prev + (s,) for prev in combos for s in group]
    return [PairExample(text=text, spans=c) for c in combos]


def parse_tag(tag: str) -> Tuple[str, Tuple[int, int]]:
    """Parse a ``a-3,4`` / ``o--1,-1`` prediction tag.

    ``tag[2:]`` happens to work for these two shapes but silently accepts
    anything else and files it under the wrong element, so the prefix and the
    coordinates are validated explicitly.
    """
    if len(tag) < 4 or tag[1] != "-":
        raise SchemaError(f"malformed tag {tag!r}")
    kind = tag[0]
    if kind not in ("a", "o"):
        raise SchemaError(f"unknown tag prefix {kind!r} in {tag!r}")
    body = tag[2:]
    fields = body.split(",")
    if len(fields) != 2:
        raise SchemaError(f"malformed tag body {body!r} in {tag!r}")
    try:
        start, end = int(fields[0]), int(fields[1])
    except ValueError as exc:
        raise SchemaError(f"non-integer coordinates in {tag!r}") from exc
    if (start == -1) != (end == -1):
        raise SchemaError(f"half-implicit tag {tag!r}")
    return kind, (start, end)


def pairs_from_prediction_line(line: str, *, strict: bool = False) -> List[PairExample]:
    """Turn one ``pred4pipeline.txt`` line into candidate pair examples."""
    parts = line.rstrip("\n").split("\t")
    if len(parts) <= 1:
        return []
    text = parts[0]
    aspects: List[Tuple[int, int]] = []
    opinions: List[Tuple[int, int]] = []
    for tag in parts[1:]:
        tag = tag.strip()
        if not tag:
            continue
        try:
            kind, span = parse_tag(tag)
        except SchemaError:
            if strict:
                raise
            continue
        bucket = aspects if kind == "a" else opinions
        if span not in bucket:
            bucket.append(span)
    return cross_product_pairs(text, [aspects, opinions])


def convert_predictions_to_pairs(
    pred_path: str,
    out_path: str,
    *,
    strict: bool = False,
) -> Dict[str, object]:
    pairs: List[PairExample] = []
    lines = 0
    with open(pred_path, "r", encoding="utf-8") as fh:
        for line in fh:
            lines += 1
            pairs.extend(pairs_from_prediction_line(line, strict=strict))
    write_pairs(out_path, pairs)
    return {"input": pred_path, "output": out_path, "lines": lines, "pairs": len(pairs)}


def iter_label_values(records: Iterable[Record]) -> Iterator[Dict[str, str]]:
    for rec in records:
        yield from rec.label_values()
