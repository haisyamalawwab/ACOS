"""Tuple-level metrics, generalised over arity.

Two things upstream's ``eval_metrics.py`` does that must be preserved:

* micro-averaged precision/recall/F1 over exact tuple matches;
* a breakdown by implicitness type, since implicit aspects and opinions are the
  hard cases and a single headline number hides them.

Two things it does that are bugs, not preserved here:

* ``measureQuad`` counts a prediction as correct by membership, so a duplicated
  prediction is counted twice against a single gold tuple;
* ``measureQuad_imp`` returns only the *last* bucket's numbers from its loop,
  so four of the five reported breakdowns are discarded by the caller.

Everything is pure Python: the metrics run in the verification gate on a machine
with no numpy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple

from .schema import IMPLICIT, Tup, TupleSchema, get_schema

EXPLICIT_BOTH = "explicit_aspect_explicit_opinion"
IMPLICIT_ASPECT = "implicit_aspect_explicit_opinion"
IMPLICIT_OPINION = "explicit_aspect_implicit_opinion"
IMPLICIT_BOTH = "implicit_aspect_implicit_opinion"
OVERALL = "overall"

IMPLICITNESS_BUCKETS = (
    EXPLICIT_BOTH,
    IMPLICIT_ASPECT,
    IMPLICIT_OPINION,
    IMPLICIT_BOTH,
    OVERALL,
)


@dataclass
class PRF:
    tp: float = 0.0
    fp: float = 0.0
    fn: float = 0.0

    @property
    def precision(self) -> float:
        return 0.0 if self.tp + self.fp == 0 else self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        return 0.0 if self.tp + self.fn == 0 else self.tp / (self.tp + self.fn)

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 0.0 if p + r == 0 else 2 * p * r / (p + r)

    @property
    def support(self) -> float:
        return self.tp + self.fn

    def as_dict(self) -> Dict[str, float]:
        return {
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "support": self.support,
        }

    def __iadd__(self, other: "PRF") -> "PRF":
        self.tp += other.tp
        self.fp += other.fp
        self.fn += other.fn
        return self


def multiset_prf(pred: Sequence[Hashable], gold: Sequence[Hashable]) -> PRF:
    """Multiset intersection, so duplicate predictions cannot be double-credited."""
    remaining: Dict[Hashable, int] = {}
    for g in gold:
        remaining[g] = remaining.get(g, 0) + 1
    tp = 0
    for p in pred:
        if remaining.get(p, 0) > 0:
            remaining[p] -= 1
            tp += 1
    return PRF(tp=tp, fp=len(pred) - tp, fn=len(gold) - tp)


def score_sets(
    pred: Mapping[str, Sequence[Hashable]],
    gold: Mapping[str, Sequence[Hashable]],
) -> PRF:
    """Micro-average over every key in either side."""
    total = PRF()
    for key in set(pred) | set(gold):
        total += multiset_prf(list(pred.get(key, ())), list(gold.get(key, ())))
    return total


# -- implicitness ----------------------------------------------------------
def implicitness_bucket(
    tup: Tup,
    schema: TupleSchema,
    *,
    aspect: str = "aspect",
    opinion: str = "opinion",
) -> str:
    imp_a = tup.span(aspect) == IMPLICIT if aspect in schema.spans else False
    imp_o = tup.span(opinion) == IMPLICIT if opinion in schema.spans else False
    if not imp_a and not imp_o:
        return EXPLICIT_BOTH
    if imp_a and not imp_o:
        return IMPLICIT_ASPECT
    if not imp_a and imp_o:
        return IMPLICIT_OPINION
    return IMPLICIT_BOTH


def bucket_of_key(key: Sequence[str], span_positions: Sequence[int]) -> str:
    """Bucket a serialised tuple key by which of its span fields are ``-1,-1``."""
    flags = [key[i] == "-1,-1" for i in span_positions]
    imp_a = flags[0] if flags else False
    imp_o = flags[1] if len(flags) > 1 else False
    if not imp_a and not imp_o:
        return EXPLICIT_BOTH
    if imp_a and not imp_o:
        return IMPLICIT_ASPECT
    if not imp_a and imp_o:
        return IMPLICIT_OPINION
    return IMPLICIT_BOTH


# -- element subsets -------------------------------------------------------
def element_subsets(
    schema: TupleSchema,
    *,
    max_size: Optional[int] = None,
    include: Optional[Sequence[Sequence[str]]] = None,
) -> List[Tuple[str, ...]]:
    """Which element combinations to report.

    Upstream enumerates all ``2**4 - 1 = 15`` subsets of the quadruple.  For the
    quintuple that becomes 31, which is more table than anyone reads, so the
    default caps subset size and always keeps the full tuple.
    """
    if include:
        return [tuple(x) for x in include]
    names = schema.names
    cap = max_size or len(names)
    out: List[Tuple[str, ...]] = []
    for size in range(1, min(cap, len(names)) + 1):
        out.extend(combinations(names, size))
    full = tuple(names)
    if full not in out:
        out.append(full)
    return out


@dataclass
class EvalResult:
    overall: PRF
    by_subset: Dict[Tuple[str, ...], PRF] = field(default_factory=dict)
    by_bucket: Dict[str, PRF] = field(default_factory=dict)
    by_subset_bucket: Dict[Tuple[Tuple[str, ...], str], PRF] = field(default_factory=dict)

    def subset(self, *names: str) -> PRF:
        return self.by_subset[tuple(names)]

    def as_dict(self) -> Dict[str, object]:
        return {
            "overall": self.overall.as_dict(),
            "by_subset": {"+".join(k): v.as_dict() for k, v in self.by_subset.items()},
            "by_bucket": {k: v.as_dict() for k, v in self.by_bucket.items()},
            "by_subset_bucket": {
                f"{'+'.join(s)}|{b}": v.as_dict()
                for (s, b), v in self.by_subset_bucket.items()
            },
        }

    def table(self, *, subsets: Optional[Sequence[Tuple[str, ...]]] = None) -> str:
        keys = list(subsets or self.by_subset.keys())
        rows = [("elements", "P", "R", "F1", "support")]
        for k in keys:
            prf = self.by_subset[k]
            rows.append(
                (
                    "+".join(k),
                    f"{prf.precision:.2%}",
                    f"{prf.recall:.2%}",
                    f"{prf.f1:.2%}",
                    f"{prf.support:.0f}",
                )
            )
        widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
        lines = []
        for i, row in enumerate(rows):
            lines.append("  ".join(cell.ljust(widths[j]) for j, cell in enumerate(row)))
            if i == 0:
                lines.append("  ".join("-" * w for w in widths))
        return "\n".join(lines)


def evaluate(
    pred: Mapping[str, Sequence[Tup]],
    gold: Mapping[str, Sequence[Tup]],
    schema,
    *,
    subsets: Optional[Sequence[Sequence[str]]] = None,
    max_subset_size: Optional[int] = None,
    breakdown: bool = True,
) -> EvalResult:
    """Score predicted tuples against gold, per element subset and implicitness."""
    schema = get_schema(schema)
    chosen = element_subsets(schema, max_size=max_subset_size, include=subsets)
    result = EvalResult(overall=PRF())

    for names in chosen:
        span_positions = [i for i, n in enumerate(names) if n in schema.spans]
        agg = PRF()
        buckets: Dict[str, PRF] = {}
        for key in set(pred) | set(gold):
            p_items = _project(pred.get(key, ()), names)
            g_items = _project(gold.get(key, ()), names)
            agg += multiset_prf(p_items, g_items)
            if not breakdown:
                continue
            bucket_names = set()
            for item in list(p_items) + list(g_items):
                bucket_names.add(bucket_of_key(item, span_positions))
            for bucket in bucket_names | {OVERALL}:
                sub_p = [
                    i for i in p_items
                    if bucket == OVERALL or bucket_of_key(i, span_positions) == bucket
                ]
                sub_g = [
                    i for i in g_items
                    if bucket == OVERALL or bucket_of_key(i, span_positions) == bucket
                ]
                buckets.setdefault(bucket, PRF())
                buckets[bucket] += multiset_prf(sub_p, sub_g)
        result.by_subset[tuple(names)] = agg
        for bucket, prf in buckets.items():
            result.by_subset_bucket[(tuple(names), bucket)] = prf
        if tuple(names) == tuple(schema.names):
            result.overall = agg
            result.by_bucket = buckets
    return result


def _project(tuples: Iterable[Tup], names: Sequence[str]) -> List[Tuple[str, ...]]:
    """Deduplicate on projection: two tuples differing only in a dropped element merge."""
    out: List[Tuple[str, ...]] = []
    seen = set()
    for tup in tuples:
        key = tup.as_tuple(names)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def compare_results(
    results: Mapping[str, EvalResult],
    *,
    subset: Optional[Sequence[str]] = None,
) -> str:
    """Side-by-side F1 table across runs, for the ablation report."""
    names = list(results)
    if not names:
        return "(no results)"
    schema_subset = tuple(subset) if subset else next(iter(results.values())).by_subset
    key = tuple(subset) if subset else max(schema_subset, key=len)
    rows = [("run", "P", "R", "F1")]
    for name in names:
        prf = results[name].by_subset[key]
        rows.append((name, f"{prf.precision:.2%}", f"{prf.recall:.2%}", f"{prf.f1:.2%}"))
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    lines = []
    for i, row in enumerate(rows):
        lines.append("  ".join(c.ljust(widths[j]) for j, c in enumerate(row)))
        if i == 0:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines)
