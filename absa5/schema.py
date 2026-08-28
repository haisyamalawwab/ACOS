"""Tuple schema: declares which elements a record carries and how it serialises.

The upstream ACOS repo hardcodes four elements in the field order
``aspect category sentiment opinion``.  Here the element list is data, so the
quadruple and the quintuple (and any future 6-element variant) are *the same
code* driven by a different :class:`TupleSchema`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .registry import Registry

IMPLICIT = (-1, -1)
SPAN = "span"
LABEL = "label"


class SchemaError(ValueError):
    pass


@dataclass(frozen=True)
class Element:
    """One slot of a tuple."""

    name: str
    kind: str
    default: Optional[str] = None

    def __post_init__(self):
        if self.kind not in (SPAN, LABEL):
            raise SchemaError(f"element '{self.name}': kind must be {SPAN!r} or {LABEL!r}")
        if self.kind == SPAN and self.default is not None:
            raise SchemaError(f"element '{self.name}': span elements cannot carry a default")


@dataclass(frozen=True)
class TupleSchema:
    """Ordered element list plus the serialised field order.

    ``order`` is the on-disk field order, which for historical reasons is not
    the logical order: ACOS writes ``aspect category sentiment opinion``.
    """

    name: str
    elements: Tuple[Element, ...]
    order: Tuple[str, ...]

    def __post_init__(self):
        names = [e.name for e in self.elements]
        if len(set(names)) != len(names):
            raise SchemaError(f"schema '{self.name}': duplicate element names")
        if sorted(self.order) != sorted(names):
            raise SchemaError(
                f"schema '{self.name}': order {self.order} does not cover elements {tuple(names)}"
            )
        if not self.spans:
            raise SchemaError(f"schema '{self.name}': needs at least one span element")

    # -- introspection -----------------------------------------------------
    @property
    def names(self) -> Tuple[str, ...]:
        return tuple(e.name for e in self.elements)

    @property
    def spans(self) -> Tuple[str, ...]:
        return tuple(e.name for e in self.elements if e.kind == SPAN)

    @property
    def labels(self) -> Tuple[str, ...]:
        return tuple(e.name for e in self.elements if e.kind == LABEL)

    @property
    def arity(self) -> int:
        return len(self.elements)

    def element(self, name: str) -> Element:
        for e in self.elements:
            if e.name == name:
                return e
        raise SchemaError(f"schema '{self.name}' has no element '{name}'")

    def extend(self, *elements: Element, name: Optional[str] = None) -> "TupleSchema":
        """Return a new schema with extra elements appended to logical and field order."""
        return TupleSchema(
            name=name or f"{self.name}+{'+'.join(e.name for e in elements)}",
            elements=self.elements + tuple(elements),
            order=self.order + tuple(e.name for e in elements),
        )

    # -- (de)serialisation -------------------------------------------------
    def parse(self, cell: str, *, repair: bool = True, repairs: Optional[List[str]] = None) -> "Tup":
        """Parse one whitespace-separated tuple cell, e.g. ``10,11 FOOD#QUALITY 2 13,16``."""
        fields = cell.split()
        expected = len(self.order)
        if len(fields) == expected:
            pass
        elif len(fields) < expected and self._defaultable_tail(len(fields)):
            fields = list(fields) + [
                self.element(n).default for n in self.order[len(fields):]
            ]
        else:
            raise SchemaError(
                f"schema '{self.name}' expects {expected} fields, got {len(fields)}: {cell!r}"
            )
        values: Dict[str, object] = {}
        for name, raw in zip(self.order, fields):
            elem = self.element(name)
            if elem.kind == SPAN:
                values[name] = parse_span(raw, name, repair=repair, repairs=repairs)
            else:
                values[name] = raw
        return Tup(self, values)

    def format(self, tup: "Tup") -> str:
        out = []
        for name in self.order:
            value = tup[name]
            elem = self.element(name)
            out.append(format_span(value) if elem.kind == SPAN else str(value))
        return " ".join(out)

    def make(self, **values) -> "Tup":
        filled: Dict[str, object] = {}
        for elem in self.elements:
            if elem.name in values:
                filled[elem.name] = values[elem.name]
            elif elem.default is not None:
                filled[elem.name] = elem.default
            else:
                raise SchemaError(f"schema '{self.name}': missing value for '{elem.name}'")
        unknown = set(values) - set(self.names)
        if unknown:
            raise SchemaError(f"schema '{self.name}': unknown elements {sorted(unknown)}")
        return Tup(self, filled)

    def _defaultable_tail(self, given: int) -> bool:
        """True when every field missing from the tail has a default."""
        return all(self.element(n).default is not None for n in self.order[given:])


@dataclass
class Tup:
    """One tuple instance bound to its schema."""

    schema: TupleSchema
    values: Dict[str, object] = field(default_factory=dict)

    def __getitem__(self, name: str):
        return self.values[name]

    def __setitem__(self, name: str, value) -> None:
        self.schema.element(name)
        self.values[name] = value

    def get(self, name: str, default=None):
        return self.values.get(name, default)

    def span(self, name: str) -> Tuple[int, int]:
        value = self.values[name]
        if self.schema.element(name).kind != SPAN:
            raise SchemaError(f"'{name}' is not a span element")
        return value  # type: ignore[return-value]

    def is_implicit(self, name: str) -> bool:
        return self.span(name) == IMPLICIT

    def label_key(self, names: Optional[Sequence[str]] = None, sep: str = "#") -> str:
        """Join label elements into the composite key used by the classifier head."""
        names = tuple(names) if names else self.schema.labels
        return sep.join(str(self.values[n]) for n in names)

    def as_tuple(self, names: Optional[Sequence[str]] = None) -> Tuple:
        names = tuple(names) if names else self.schema.names
        out = []
        for n in names:
            v = self.values[n]
            out.append(format_span(v) if self.schema.element(n).kind == SPAN else str(v))
        return tuple(out)

    def replace(self, **values) -> "Tup":
        merged = dict(self.values)
        for k, v in values.items():
            self.schema.element(k)
            merged[k] = v
        return Tup(self.schema, merged)

    def __str__(self) -> str:
        return self.schema.format(self)

    def __hash__(self) -> int:
        return hash(self.as_tuple())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tup):
            return NotImplemented
        return self.schema.names == other.schema.names and self.as_tuple() == other.as_tuple()


# -- span helpers ----------------------------------------------------------
def parse_span(
    raw: str,
    name: str = "span",
    *,
    repair: bool = True,
    repairs: Optional[List[str]] = None,
) -> Tuple[int, int]:
    """Parse ``start,end`` with ``end`` exclusive; ``-1,-1`` marks an implicit slot.

    ``repair`` handles one real defect in the upstream data: line 451 of
    ``rest16_quad_train.tsv`` carries the zero-width opinion span ``3,3``, which
    the authors' own pre-tokenised file records as ``3,4``.  A zero-width span
    would silently produce a tuple with no opinion tokens, so it is widened to one
    token and the change is recorded rather than hidden.
    """
    parts = raw.split(",")
    if len(parts) != 2:
        raise SchemaError(f"{name}: malformed span {raw!r}")
    try:
        start, end = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise SchemaError(f"{name}: non-integer span {raw!r}") from exc
    if (start == -1) != (end == -1):
        raise SchemaError(f"{name}: half-implicit span {raw!r}")
    if start != -1 and end == start:
        if not repair:
            raise SchemaError(f"{name}: zero-width span {raw!r}")
        end = start + 1
        if repairs is not None:
            repairs.append(f"{name}: widened zero-width span {raw!r} to {start},{end}")
    elif start != -1 and end < start:
        raise SchemaError(f"{name}: reversed span {raw!r}")
    return (start, end)


def format_span(span: Iterable[int]) -> str:
    start, end = span  # type: ignore[misc]
    return f"{start},{end}"


# -- built-in schemas ------------------------------------------------------
SCHEMAS: Registry[TupleSchema] = Registry("schema")

ASPECT = Element("aspect", SPAN)
OPINION = Element("opinion", SPAN)
CATEGORY = Element("category", LABEL)
SENTIMENT = Element("sentiment", LABEL)
EMOTION = Element("emotion", LABEL, default="netral")

QUAD = TupleSchema(
    name="quad",
    elements=(ASPECT, CATEGORY, SENTIMENT, OPINION),
    order=("aspect", "category", "sentiment", "opinion"),
)
"""Upstream ACOS: aspect, category, opinion, sentiment."""

QUINT = QUAD.extend(EMOTION, name="quint")
"""ACOSE: quad plus emotion, appended last so quad files parse unchanged."""

SCHEMAS.add("quad", QUAD, "acos", "quadruple")
SCHEMAS.add("quint", QUINT, "acose", "quintuple")


def get_schema(name: str | TupleSchema) -> TupleSchema:
    return name if isinstance(name, TupleSchema) else SCHEMAS.get(name)
