"""Label spaces for the label-valued elements (category, sentiment, emotion).

Two composition modes matter, and choosing between them is the central
modelling decision of the quintuple extension:

``joint``
    One classifier over the cross product of every label element, which is
    what upstream ACOS does (13 categories x 3 sentiments = 39 classes; Cai 2021,
    doi:10.18653/v1/2021.acl-long.29).
``factored``
    One classifier per label element, sharing the pair representation.

The cross product is what makes the quintuple expensive: 13 x 3 x 5 = 195
classes over ~2.4k training pairs, so most cells are never observed.  The
factored head keeps the parameter count at 13 + 3 + 5 = 21 outputs.
See :func:`LabelSpaceSet.report` for the numbers on a concrete dataset.

Every registered label set names its source; run
``python -m absa5 references --module taxonomy`` for the list with DOIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .registry import Registry
from .schema import TupleSchema, get_schema

JOINT = "joint"
FACTORED = "factored"


class TaxonomyError(ValueError):
    pass


@dataclass(frozen=True)
class LabelSpace:
    """Closed vocabulary for one label element."""

    element: str
    labels: Tuple[str, ...]
    description: str = ""

    def __post_init__(self):
        if not self.labels:
            raise TaxonomyError(f"label space '{self.element}' is empty")
        if len(set(self.labels)) != len(self.labels):
            dupes = sorted({x for x in self.labels if list(self.labels).count(x) > 1})
            raise TaxonomyError(f"label space '{self.element}': duplicates {dupes}")
        for lab in self.labels:
            if not lab or any(c.isspace() for c in lab):
                raise TaxonomyError(f"label space '{self.element}': bad label {lab!r}")

    def index(self) -> Dict[str, int]:
        return {lab: i for i, lab in enumerate(self.labels)}

    def __len__(self) -> int:
        return len(self.labels)

    def __contains__(self, label: object) -> bool:
        return label in self.labels


class LabelSpaceSet:
    """All label spaces of a schema, in schema order, plus joint/factored views."""

    def __init__(self, schema, spaces: Iterable[LabelSpace], *, sep: str = "#"):
        self.schema: TupleSchema = get_schema(schema)
        self.sep = sep
        by_name = {s.element: s for s in spaces}
        missing = [n for n in self.schema.labels if n not in by_name]
        if missing:
            raise TaxonomyError(f"no label space for {missing}")
        extra = [n for n in by_name if n not in self.schema.labels]
        if extra:
            raise TaxonomyError(f"label spaces for unknown elements {extra}")
        self.spaces: Tuple[LabelSpace, ...] = tuple(by_name[n] for n in self.schema.labels)

    @property
    def elements(self) -> Tuple[str, ...]:
        return tuple(s.element for s in self.spaces)

    def space(self, element: str) -> LabelSpace:
        for s in self.spaces:
            if s.element == element:
                return s
        raise TaxonomyError(f"no label space for '{element}'")

    def sizes(self) -> Dict[str, int]:
        return {s.element: len(s) for s in self.spaces}

    # -- head views --------------------------------------------------------
    def joint_labels(self) -> Tuple[str, ...]:
        """Cross product, joined by ``sep`` in schema label order."""
        return tuple(
            self.sep.join(combo) for combo in product(*(s.labels for s in self.spaces))
        )

    def factored_labels(self) -> Dict[str, Tuple[str, ...]]:
        return {s.element: s.labels for s in self.spaces}

    def head_sizes(self, mode: str) -> Dict[str, int]:
        if mode == JOINT:
            return {"joint": len(self.joint_labels())}
        if mode == FACTORED:
            return self.sizes()
        raise TaxonomyError(f"unknown label mode '{mode}'")

    def split_joint(self, key: str) -> Dict[str, str]:
        """Inverse of :meth:`join`, tolerant of separators inside category names."""
        parts = key.split(self.sep)
        n = len(self.spaces)
        if len(parts) < n:
            raise TaxonomyError(f"joint key {key!r} has fewer than {n} fields")
        # Only the first space may contain the separator (ENTITY#ATTRIBUTE).
        head = self.sep.join(parts[: len(parts) - n + 1])
        rest = parts[len(parts) - n + 1:]
        return dict(zip(self.elements, [head, *rest]))

    def join(self, values: Mapping[str, str]) -> str:
        return self.sep.join(str(values[n]) for n in self.elements)

    def report(self, observed: Optional[Sequence[Mapping[str, str]]] = None) -> Dict[str, object]:
        """Size report; with ``observed`` also the coverage of the joint space.

        ``observed`` is a sequence of label-value mappings (one per gold tuple).
        Sparse joint cells are the quantitative argument for ``factored``.
        """
        joint = self.joint_labels()
        out: Dict[str, object] = {
            "elements": list(self.elements),
            "sizes": self.sizes(),
            "joint_size": len(joint),
            "factored_size": sum(self.sizes().values()),
        }
        if observed is None:
            return out
        seen: Dict[str, int] = {}
        per_element: Dict[str, Dict[str, int]] = {n: {} for n in self.elements}
        for values in observed:
            seen[self.join(values)] = seen.get(self.join(values), 0) + 1
            for n in self.elements:
                bucket = per_element[n]
                bucket[str(values[n])] = bucket.get(str(values[n]), 0) + 1
        out["observed_tuples"] = sum(seen.values())
        out["joint_cells_seen"] = len(seen)
        out["joint_coverage"] = len(seen) / len(joint)
        out["joint_cells_below_10"] = sum(1 for v in seen.values() if v < 10)
        out["per_element_seen"] = {n: len(v) for n, v in per_element.items()}
        out["per_element_min_support"] = {
            n: (min(v.values()) if v else 0) for n, v in per_element.items()
        }
        return out


# -- registries ------------------------------------------------------------
CATEGORIES: Registry[Tuple[str, ...]] = Registry("category set")
SENTIMENTS: Registry[Tuple[str, ...]] = Registry("sentiment set")
EMOTIONS: Registry[Tuple[str, ...]] = Registry("emotion set")

# Which reference key each label set comes from.  Keys resolve through
# absa5.references; the gate `references` checks every one of them exists.
LABEL_SET_SOURCES: Dict[str, str] = {
    "rest16": "pontiki2016semeval",
    "resto_id": "pontiki2016semeval",
    "acos": "cai2021acos",
    "id": "cai2021acos",
    "emot": "saputri2018emotion",
    "emot_id": "saputri2018emotion",
    "emot_id_netral": "saputri2018emotion",
    "ekman": "ekman1992basic",
    "nusaparagraph": "cahyawijaya2023nusawrites",
    "plutchik": "plutchik1980theory",
    "goemotions": "demszky2020goemotions",
    "none": "",
}


def source_of(label_set: str):
    """The :class:`~absa5.references.Reference` a label set is taken from."""
    from .references import REFERENCES

    key = LABEL_SET_SOURCES.get(label_set.strip().lower().replace("-", "_"), "")
    return REFERENCES.get(key) if key else None


CATEGORIES.add(
    "rest16",
    (
        "RESTAURANT#GENERAL", "SERVICE#GENERAL", "FOOD#GENERAL", "FOOD#QUALITY",
        "FOOD#STYLE_OPTIONS", "DRINKS#STYLE_OPTIONS", "DRINKS#PRICES", "AMBIENCE#GENERAL",
        "RESTAURANT#PRICES", "FOOD#PRICES", "RESTAURANT#MISCELLANEOUS", "DRINKS#QUALITY",
        "LOCATION#GENERAL",
    ),
    "rest",
    "restaurant",
)
"""SemEval-2016 Task 5 restaurant categories (Pontiki 2016, doi:10.18653/v1/S16-1002)."""

CATEGORIES.add(
    "resto_id",
    (
        "RESTORAN#UMUM", "PELAYANAN#UMUM", "MAKANAN#UMUM", "MAKANAN#KUALITAS",
        "MAKANAN#PILIHAN", "MINUMAN#PILIHAN", "MINUMAN#HARGA", "SUASANA#UMUM",
        "RESTORAN#HARGA", "MAKANAN#HARGA", "RESTORAN#LAINNYA", "MINUMAN#KUALITAS",
        "LOKASI#UMUM",
    ),
    "resto",
    "restoran_id",
)
"""13 Indonesian restaurant categories, mapped 1:1 from rest16 for comparability.

Keeping the count and the ENTITY#ATTRIBUTE shape of Pontiki 2016
(doi:10.18653/v1/S16-1002) is what lets the Indonesian numbers sit beside the
published English baseline.
"""

SENTIMENTS.add("acos", ("0", "1", "2"), "numeric", "rest16", "laptop")
"""Upstream encoding: 0 negative, 1 neutral, 2 positive (Cai 2021, doi:10.18653/v1/2021.acl-long.29)."""
SENTIMENTS.add("id", ("negatif", "netral", "positif"), "indonesian")

EMOTIONS.add(
    "emot",
    ("sadness", "anger", "love", "fear", "happy"),
    "indonlu",
    "indonlu_emot",
)
"""IndoNLU EmoT label set, verbatim (note: 'happy', not 'joy').

Task from Wilie 2020 (doi:10.18653/v1/2020.aacl-main.85), corpus from
Saputri 2018 (doi:10.1109/IALP.2018.8629262).  Note that ``love`` is not an Ekman
basic emotion and the set has neither disgust nor surprise, so it is not
interchangeable with :data:`EMOTIONS['ekman']`.
"""

EMOTIONS.add(
    "emot_id",
    ("sedih", "marah", "cinta", "takut", "senang"),
    "emot_indonesian",
)
"""EmoT translated; same 5 classes, Indonesian surface forms for annotators."""

EMOTIONS.add(
    "emot_id_netral",
    ("sedih", "marah", "cinta", "takut", "senang", "netral"),
    "emot_id_plus",
    "emot_id6",
)
"""EmoT plus an explicit neutral class.

EmoT was built for tweets, which are selected for emotional content
(Saputri 2018, doi:10.1109/IALP.2018.8629262).  ABSA tuples are not: a review
saying "harganya wajar" has neutral sentiment and no emotional charge, and forcing
it into one of the five would inject label noise into the class it is forced into.
GoEmotions keeps a neutral class for the same reason
(Demszky 2020, doi:10.18653/v1/2020.acl-main.372).  The trade-off is that
`netral` becomes the majority class on factual reviews, which is why it is a
separate registry entry rather than the default - measure both before choosing.
"""

EMOTIONS.add(
    "ekman",
    ("anger", "disgust", "fear", "happiness", "sadness", "surprise"),
    "ekman6",
)
"""Ekman's six basic emotions (Ekman 1992, doi:10.1080/02699939208411068)."""

EMOTIONS.add(
    "nusaparagraph",
    ("angry", "disgusted", "fear", "happy", "sad", "shame", "surprise"),
    "nusawrites",
)
"""NusaParagraph's 7 labels (Cahyawijaya 2023, doi:10.18653/v1/2023.ijcnlp-main.60).

The only Indonesian resource carrying both disgust and surprise, which makes it
the closest local set to Ekman-6; it substitutes ``shame`` for a neutral class.
"""

EMOTIONS.add(
    "plutchik",
    ("joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"),
    "plutchik8",
)
"""Plutchik's eight primary emotions in four bipolar pairs.

Plutchik 1980 (doi:10.1016/B978-0-12-558701-3.50007-7); the wheel presentation is
Plutchik 2001 (doi:10.1511/2001.4.344).
"""

EMOTIONS.add(
    "goemotions",
    (
        "admiration", "amusement", "anger", "annoyance", "approval", "caring",
        "confusion", "curiosity", "desire", "disappointment", "disapproval",
        "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
        "joy", "love", "nervousness", "optimism", "pride", "realization",
        "relief", "remorse", "sadness", "surprise", "neutral",
    ),
    "goemotions27",
)
"""GoEmotions 27 + neutral (Demszky 2020, doi:10.18653/v1/2020.acl-main.372).

Registered for completeness and for its published mapping down to Ekman-6.  Not a
serious candidate here: 28 x 13 x 3 = 1,092 joint cells, and even factored it
would need far more annotated tuples per class than this project will have.
"""

EMOTIONS.add("none", ("netral",), "neutral_only", "off")
"""Degenerate single-class emotion space: makes a quint run reduce to a quad run."""

_SPACE_REGISTRIES: Dict[str, Registry[Tuple[str, ...]]] = {
    "category": CATEGORIES,
    "sentiment": SENTIMENTS,
    "emotion": EMOTIONS,
}


def build_label_spaces(
    schema,
    *,
    category: str = "rest16",
    sentiment: str = "acos",
    emotion: str = "emot",
    sep: str = "#",
    **extra: str,
) -> LabelSpaceSet:
    """Assemble the label spaces a schema needs from the registries by name."""
    schema = get_schema(schema)
    chosen = {"category": category, "sentiment": sentiment, "emotion": emotion, **extra}
    spaces: List[LabelSpace] = []
    for element in schema.labels:
        if element not in chosen:
            raise TaxonomyError(f"no label set name given for element '{element}'")
        registry = _SPACE_REGISTRIES.get(element)
        if registry is None:
            raise TaxonomyError(
                f"element '{element}' has no registry; register one in _SPACE_REGISTRIES"
            )
        spaces.append(LabelSpace(element, tuple(registry.get(chosen[element]))))
    return LabelSpaceSet(schema, spaces, sep=sep)


def label_spaces_for_domain(schema, domain_type: str, *, emotion: str = "emot") -> LabelSpaceSet:
    """Resolve label spaces from an upstream ``--domain_type`` string."""
    schema = get_schema(schema)
    d = domain_type.lower()
    if d.startswith("resto"):
        category = "resto_id"
    elif d.startswith("rest"):
        category = "rest16"
    elif d.startswith("laptop"):
        raise TaxonomyError(
            "the laptop taxonomy (121 categories) is not registered for quintuple runs; "
            "13 x 3 x 5 is already sparse, 121 x 3 x 5 = 1815 is not trainable"
        )
    else:
        raise TaxonomyError(f"unknown domain_type '{domain_type}'")
    kwargs = {"category": category, "sentiment": "acos"}
    if "emotion" in schema.labels:
        kwargs["emotion"] = emotion
    return build_label_spaces(schema, **kwargs)
