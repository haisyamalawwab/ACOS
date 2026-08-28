"""Decoding: model outputs -> tuples.

Stage 1 emits tag sequences plus implicit flags; stage 2 emits label logits.
This module turns both back into :class:`~absa5.schema.Tup` objects so the same
:mod:`absa5.metrics` code scores predictions and gold identically.

Kept free of torch: it takes plain lists, so decoding is unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .data import PairExample, cross_product_pairs
from .features import ClassificationEncoder, TaggingScheme
from .schema import IMPLICIT, Tup, TupleSchema, get_schema
from .taxonomy import FACTORED, JOINT, LabelSpaceSet


@dataclass
class SpanPrediction:
    """Stage 1 output for one sentence."""

    key: str
    text: str
    spans: Dict[str, List[Tuple[int, int]]]

    def groups(self, order: Sequence[str]) -> List[List[Tuple[int, int]]]:
        return [self.spans.get(name) or [IMPLICIT] for name in order]

    def to_pairs(self) -> List[PairExample]:
        order = list(self.spans)
        return cross_product_pairs(self.text, self.groups(order))


def decode_spans(
    tags: Sequence[int],
    tagging: TaggingScheme,
    *,
    offset: int = -1,
    implicit_flags: Optional[Mapping[str, int]] = None,
    max_index: Optional[int] = None,
) -> Dict[str, List[Tuple[int, int]]]:
    """Turn one tag-id sequence into spans per span element.

    ``offset`` shifts indices from the padded encoding (which prepends a boundary
    token) back to text coordinates; the default -1 undoes that single token.
    """
    tag_names = tagging.tag_list()
    labels = [tag_names[t] if 0 <= t < len(tag_names) else "O" for t in tags]
    raw = tagging.decode(labels)

    out: Dict[str, List[Tuple[int, int]]] = {}
    for name, spans in raw.items():
        shifted: List[Tuple[int, int]] = []
        for start, end in spans:
            s, e = start + offset, end + offset
            if s < 0:
                s = 0
            if max_index is not None:
                e = min(e, max_index)
            if e > s:
                shifted.append((s, e))
        out[name] = shifted

    if implicit_flags:
        for name, flag in implicit_flags.items():
            if flag and name in out and IMPLICIT not in out[name]:
                out[name].append(IMPLICIT)
            elif flag and name not in out:
                out[name] = [IMPLICIT]
    return out


def decode_label_logits(
    logits: Mapping[str, Sequence[float]] | Mapping[str, Sequence[Sequence[float]]],
    spaces: LabelSpaceSet,
    *,
    mode: str = FACTORED,
    threshold: float = 0.0,
    top_k_fallback: bool = True,
) -> List[Dict[str, str]]:
    """Turn one example's label logits into label-value assignments.

    Multi-label by design: 2.3% of rest16 pairs carry more than one label set, so
    thresholding is kept rather than forcing a single argmax.  ``top_k_fallback``
    keeps the highest-scoring option when nothing crosses the threshold, which
    avoids silently dropping the pair.
    """
    if mode == JOINT:
        scores = list(logits["joint"])  # type: ignore[index]
        labels = spaces.joint_labels()
        chosen = [i for i, s in enumerate(scores) if s > threshold]
        if not chosen and top_k_fallback and scores:
            chosen = [max(range(len(scores)), key=lambda i: scores[i])]
        return [spaces.split_joint(labels[i]) for i in chosen]

    if mode != FACTORED:
        raise ValueError(f"unknown label mode '{mode}'")

    per_element: Dict[str, List[str]] = {}
    for element in spaces.elements:
        scores = list(logits[element])  # type: ignore[index]
        labels = spaces.space(element).labels
        picked = [labels[i] for i, s in enumerate(scores) if s > threshold]
        if not picked and top_k_fallback and scores:
            picked = [labels[max(range(len(scores)), key=lambda i: scores[i])]]
        per_element[element] = picked

    combos: List[Dict[str, str]] = [{}]
    for element in spaces.elements:
        combos = [
            {**prev, element: value} for prev in combos for value in per_element[element]
        ]
    return combos


def assemble_tuples(
    pair: PairExample,
    label_sets: Sequence[Mapping[str, str]],
    schema,
) -> List[Tup]:
    """Combine one span combination with its predicted label values."""
    schema = get_schema(schema)
    out: List[Tup] = []
    for values in label_sets:
        kwargs: Dict[str, object] = dict(zip(schema.spans, pair.spans))
        kwargs.update({k: v for k, v in values.items()})
        tup = schema.make(**kwargs)
        if tup not in out:
            out.append(tup)
    return out


def collect_predictions(
    pairs: Sequence[PairExample],
    label_sets_per_pair: Sequence[Sequence[Mapping[str, str]]],
    schema,
    *,
    key_fn=None,
) -> Dict[str, List[Tup]]:
    """Group predicted tuples by sentence, ready for :func:`absa5.metrics.evaluate`."""
    schema = get_schema(schema)
    if len(pairs) != len(label_sets_per_pair):
        raise ValueError("pairs and label sets differ in length")
    key_fn = key_fn or (lambda p: p.text)
    out: Dict[str, List[Tup]] = {}
    for pair, label_sets in zip(pairs, label_sets_per_pair):
        bucket = out.setdefault(key_fn(pair), [])
        for tup in assemble_tuples(pair, label_sets, schema):
            if tup not in bucket:
                bucket.append(tup)
    return out


def gold_by_text(records: Iterable, schema) -> Dict[str, List[Tup]]:
    schema = get_schema(schema)
    out: Dict[str, List[Tup]] = {}
    for rec in records:
        bucket = out.setdefault(rec.text, [])
        for tup in rec.tuples:
            if tup not in bucket:
                bucket.append(tup)
    return out


def spans_to_tag_string(
    spans: Mapping[str, Sequence[Tuple[int, int]]],
    *,
    codes: Optional[Mapping[str, str]] = None,
) -> str:
    """Serialise decoded spans as the ``a-3,4 o-0,1`` tags the pair builder reads."""
    codes = codes or {"aspect": "a", "opinion": "o"}
    parts: List[str] = []
    for name, group in spans.items():
        code = codes.get(name, name[0])
        for start, end in group:
            parts.append(f"{code}-{start},{end}")
    return "\t".join(parts)
