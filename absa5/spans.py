"""Word -> subword span remapping, the step upstream ships as data but not as code.

The offsets in ``tokenized_data/*.tsv`` index whitespace tokens of *already
subword-split* text, not characters and not runtime subwords.  So converting raw
data into trainable data means retokenising each word and shifting every span.
That transformation is here, isolated and tested against the files already in the
repo (see :mod:`absa5.selftest`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .schema import IMPLICIT, SPAN, Tup, TupleSchema
from .tokenizers import BaseTokenizer, as_tokenizer


class SpanRemapError(ValueError):
    pass


@dataclass
class Alignment:
    """Word-to-subword index map for one sentence."""

    words: List[str]
    subwords: List[str]
    starts: List[int]
    ends: List[int]
    unk_count: int = 0

    def __post_init__(self):
        if not (len(self.words) == len(self.starts) == len(self.ends)):
            raise SpanRemapError("alignment arrays disagree in length")

    def remap(self, span: Tuple[int, int]) -> Tuple[int, int]:
        """Map a word-level ``[start, end)`` span onto subword indices."""
        start, end = span
        if (start, end) == IMPLICIT:
            return IMPLICIT
        if start < 0 or end <= start:
            raise SpanRemapError(f"malformed span {span}")
        if end > len(self.words):
            raise SpanRemapError(
                f"span {span} exceeds sentence length {len(self.words)}"
            )
        return (self.starts[start], self.ends[end - 1])

    @property
    def text(self) -> str:
        return " ".join(self.subwords)

    def expansion(self) -> float:
        return len(self.subwords) / max(len(self.words), 1)


def align_words(tokenizer, words: Sequence[str]) -> Alignment:
    """Tokenize each word separately and record where its subwords land."""
    tok = as_tokenizer(tokenizer)
    subwords: List[str] = []
    starts: List[int] = []
    ends: List[int] = []
    unk = 0
    for word in words:
        pieces = tok.tokenize_word(word)
        if len(pieces) == 1 and pieces[0] == tok.unk_token and word != tok.unk_token:
            unk += 1
        starts.append(len(subwords))
        subwords.extend(pieces)
        ends.append(len(subwords))
    return Alignment(list(words), subwords, starts, ends, unk_count=unk)


@dataclass
class RemapStats:
    """Accounting for one file conversion; the numbers that must not stay hidden."""

    rows: int = 0
    tuples: int = 0
    spans_remapped: int = 0
    implicit_spans: int = 0
    unk_words: int = 0
    rows_over_limit: int = 0
    dropped_rows: int = 0
    errors: List[str] = field(default_factory=list)
    length_histogram: Dict[str, int] = field(default_factory=dict)

    def note_length(self, n_subwords: int, *, limit: Optional[int]) -> None:
        bucket = f"{(n_subwords // 32) * 32}-{(n_subwords // 32) * 32 + 31}"
        self.length_histogram[bucket] = self.length_histogram.get(bucket, 0) + 1
        if limit is not None and n_subwords > limit:
            self.rows_over_limit += 1

    def unk_ratio(self, total_words: int) -> float:
        return self.unk_words / max(total_words, 1)

    def as_dict(self) -> Dict[str, object]:
        return {
            "rows": self.rows,
            "tuples": self.tuples,
            "spans_remapped": self.spans_remapped,
            "implicit_spans": self.implicit_spans,
            "unk_words": self.unk_words,
            "rows_over_limit": self.rows_over_limit,
            "dropped_rows": self.dropped_rows,
            "length_histogram": dict(sorted(self.length_histogram.items())),
            "errors": self.errors[:50],
            "error_count": len(self.errors),
        }


def remap_record(
    tokenizer,
    text: str,
    tuples: Sequence[Tup],
    schema: TupleSchema,
    *,
    stats: Optional[RemapStats] = None,
    subword_limit: Optional[int] = None,
) -> Tuple[str, List[Tup], Alignment]:
    """Retokenize ``text`` and shift every span element of every tuple."""
    words = text.strip().split()
    alignment = align_words(tokenizer, words)
    if stats is not None:
        stats.unk_words += alignment.unk_count
        stats.note_length(len(alignment.subwords), limit=subword_limit)

    out: List[Tup] = []
    for tup in tuples:
        values = dict(tup.values)
        for name in schema.spans:
            span = tup.span(name)
            new_span = alignment.remap(span)
            values[name] = new_span
            if stats is not None:
                if new_span == IMPLICIT:
                    stats.implicit_spans += 1
                else:
                    stats.spans_remapped += 1
        out.append(Tup(schema, values))
    if stats is not None:
        stats.tuples += len(out)
    return alignment.text, out, alignment


def infer_word_groups(subwords: Sequence[str], *, continuation: str = "##") -> List[List[int]]:
    """Group subwords back into words by continuation marker.

    Used only by the verification gate, to reconstruct which raw word each
    already-tokenised token came from without rerunning a tokenizer.
    """
    groups: List[List[int]] = []
    for i, tok in enumerate(subwords):
        if tok.startswith(continuation) and groups:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


def invert_alignment(subwords: Sequence[str], *, continuation: str = "##") -> Alignment:
    """Rebuild an :class:`Alignment` from pre-tokenised text."""
    groups = infer_word_groups(subwords, continuation=continuation)
    words = ["".join(subwords[i].removeprefix(continuation) for i in g) for g in groups]
    starts = [g[0] for g in groups]
    ends = [g[-1] + 1 for g in groups]
    return Alignment(words, list(subwords), starts, ends)


def unmap_span(alignment: Alignment, span: Tuple[int, int]) -> Tuple[int, int]:
    """Map a subword span back to word indices; inverse of :meth:`Alignment.remap`."""
    start, end = span
    if (start, end) == IMPLICIT:
        return IMPLICIT
    try:
        w_start = alignment.starts.index(start)
    except ValueError as exc:
        raise SpanRemapError(f"subword index {start} is not a word boundary") from exc
    try:
        w_end = alignment.ends.index(end) + 1
    except ValueError as exc:
        raise SpanRemapError(f"subword index {end} is not a word boundary") from exc
    return (w_start, w_end)


def spans_within(tup: Tup, schema: TupleSchema, limit: int) -> bool:
    """True when every explicit span of ``tup`` survives truncation at ``limit``."""
    for name in schema.spans:
        if schema.element(name).kind != SPAN:
            continue
        start, end = tup.span(name)
        if (start, end) == IMPLICIT:
            continue
        if end > limit:
            return False
    return True
