"""Feature encoding: records -> integer arrays, with a pluggable tagging scheme.

Deliberately torch-free.  Everything returns plain Python lists so the encoding
can be tested, and its invariants checked, without a GPU or even numpy.  The
torch layer in :mod:`absa5.models` only stacks these into tensors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .data import PairExample, Record
from .registry import Registry
from .schema import IMPLICIT, Tup, TupleSchema, get_schema
from .taxonomy import LabelSpaceSet

CLS = "[CLS]"
SEP = "[SEP]"
PAD_ID = 0


class TaggingScheme:
    """Maps span elements onto per-token tags."""

    name = "base"
    tags: Tuple[str, ...] = ()

    def __init__(self, span_elements: Sequence[str]):
        self.span_elements = tuple(span_elements)

    def tag_list(self) -> List[str]:
        raise NotImplementedError

    def encode(self, n_tokens: int, tuples: Sequence[Tup], schema: TupleSchema) -> List[str]:
        raise NotImplementedError

    def decode(self, tags: Sequence[str]) -> Dict[str, List[Tuple[int, int]]]:
        raise NotImplementedError

    @property
    def num_tags(self) -> int:
        return len(self.tag_list())


class BioTagging(TaggingScheme):
    """B/I/O per span element, plus the ``[CLS]`` tag upstream keeps in the label set.

    For the quadruple this reproduces ``['[CLS]','O','I-A','B-A','I-O','B-O']``
    in that exact order, so CRF transition indices stay comparable with the
    published baseline.
    """

    name = "bio"

    def __init__(self, span_elements: Sequence[str], *, keep_cls_tag: bool = True):
        super().__init__(span_elements)
        self.keep_cls_tag = keep_cls_tag
        self.codes = {name: _short_code(name, self.span_elements) for name in self.span_elements}

    def tag_list(self) -> List[str]:
        tags: List[str] = []
        if self.keep_cls_tag:
            tags.append(CLS)
        tags.append("O")
        for name in self.span_elements:
            code = self.codes[name]
            tags.extend([f"I-{code}", f"B-{code}"])
        return tags

    def encode(self, n_tokens: int, tuples: Sequence[Tup], schema: TupleSchema) -> List[str]:
        tags = ["O"] * n_tokens
        for tup in tuples:
            for name in self.span_elements:
                start, end = tup.span(name)
                if (start, end) == IMPLICIT:
                    continue
                if start >= n_tokens:
                    continue
                code = self.codes[name]
                tags[start] = f"B-{code}"
                for i in range(start + 1, min(end, n_tokens)):
                    tags[i] = f"I-{code}"
        return tags

    def decode(self, tags: Sequence[str]) -> Dict[str, List[Tuple[int, int]]]:
        out: Dict[str, List[Tuple[int, int]]] = {n: [] for n in self.span_elements}
        by_code = {self.codes[n]: n for n in self.span_elements}
        i = 0
        while i < len(tags):
            tag = tags[i]
            if tag.startswith("B-") and tag[2:] in by_code:
                code = tag[2:]
                j = i + 1
                while j < len(tags) and tags[j] == f"I-{code}":
                    j += 1
                out[by_code[code]].append((i, j))
                i = j
            else:
                i += 1
        return out


def _short_code(name: str, all_names: Sequence[str]) -> str:
    """First letter, extended until unique: aspect -> A, opinion -> O."""
    for length in range(1, len(name) + 1):
        code = name[:length].upper()
        if sum(1 for other in all_names if other[:length].upper() == code) == 1:
            return code
    return name.upper()


TAGGING: Registry = Registry("tagging scheme")
TAGGING.add("bio", BioTagging, "bio_crf")


# -- extraction-stage features --------------------------------------------
@dataclass
class ExtractionFeature:
    """One sentence encoded for the span-extraction stage."""

    tokens_len: int
    input_ids: List[int]
    input_mask: List[int]
    segment_ids: List[int]
    tag_ids: List[int]
    implicit_flags: Dict[str, int] = field(default_factory=dict)
    tokens: List[str] = field(default_factory=list)
    guid: str = ""

    def implicit_vector(self, order: Sequence[str]) -> List[int]:
        return [self.implicit_flags.get(n, 0) for n in order]


@dataclass
class ExtractionEncoder:
    """Record -> :class:`ExtractionFeature`.

    ``max_seq_length`` counts the two boundary tokens upstream adds, so the text
    budget is ``max_seq_length - 2``.
    """

    tokenizer: object
    schema: TupleSchema
    tagging: TaggingScheme
    max_seq_length: int = 128
    boundary_token: str = CLS
    pad_tag: str = "O"

    def __post_init__(self):
        self.schema = get_schema(self.schema)
        self.tag_index = {t: i for i, t in enumerate(self.tagging.tag_list())}
        if self.boundary_token not in (CLS, SEP):
            raise ValueError("boundary_token must be [CLS] or [SEP]")

    @property
    def num_tags(self) -> int:
        return len(self.tag_index)

    def encode(self, rec: Record, *, guid: str = "") -> ExtractionFeature:
        tokens = rec.words
        limit = self.max_seq_length - 2
        tags = self.tagging.encode(len(tokens), rec.tuples, self.schema)
        tokens, tags = tokens[:limit], tags[:limit]

        boundary_tag = CLS if CLS in self.tag_index else self.pad_tag
        full_tokens = [self.boundary_token, *tokens, self.boundary_token]
        full_tags = [boundary_tag, *tags, boundary_tag]
        tokens_len = len(full_tokens)

        input_ids = _convert_tokens_to_ids(self.tokenizer, full_tokens)
        input_mask = [1] * len(input_ids)
        segment_ids = [0] * len(input_ids)
        tag_ids = [self.tag_index[t] for t in full_tags]

        pad = self.max_seq_length - len(input_ids)
        input_ids += [PAD_ID] * pad
        input_mask += [0] * pad
        segment_ids += [0] * pad
        tag_ids += [self.tag_index[self.pad_tag]] * pad

        flags = {}
        for name in self.schema.spans:
            flags[name] = int(any(t.span(name) == IMPLICIT for t in rec.tuples))

        for arr in (input_ids, input_mask, segment_ids, tag_ids):
            assert len(arr) == self.max_seq_length, "padding produced a wrong length"

        return ExtractionFeature(
            tokens_len=tokens_len,
            input_ids=input_ids,
            input_mask=input_mask,
            segment_ids=segment_ids,
            tag_ids=tag_ids,
            implicit_flags=flags,
            tokens=full_tokens,
            guid=guid,
        )

    def encode_all(self, records: Sequence[Record]) -> List[ExtractionFeature]:
        return [self.encode(r, guid=f"{i}") for i, r in enumerate(records)]

    def gold_tuples(self, records: Sequence[Record]) -> Dict[str, List[Tup]]:
        """Gold spans keyed the same way predictions will be, for scoring."""
        out: Dict[str, List[Tup]] = {}
        for i, rec in enumerate(records):
            out[f"{i}"] = list(rec.tuples)
        return out


# -- classification-stage features ----------------------------------------
@dataclass
class ClassificationFeature:
    """One (sentence, span-combination) candidate encoded for the label stage."""

    tokens_len: int
    input_ids: List[int]
    input_mask: List[int]
    segment_ids: List[int]
    span_masks: Dict[str, List[int]]
    joint_label: List[int]
    factored_labels: Dict[str, List[int]]
    tokens: List[str] = field(default_factory=list)
    guid: str = ""


@dataclass
class ClassificationEncoder:
    """PairExample -> :class:`ClassificationFeature`.

    Implicit spans are pooled from the trailing boundary token, matching upstream:
    an implicit aspect reads the leading ``[CLS]`` and an implicit opinion reads
    the final one.
    """

    tokenizer: object
    schema: TupleSchema
    spaces: LabelSpaceSet
    max_seq_length: int = 128
    boundary_token: str = CLS

    def __post_init__(self):
        self.schema = get_schema(self.schema)
        self.joint_index = {lab: i for i, lab in enumerate(self.spaces.joint_labels())}
        self.factored_index = {
            name: self.spaces.space(name).index() for name in self.spaces.elements
        }

    @property
    def joint_size(self) -> int:
        return len(self.joint_index)

    def factored_sizes(self) -> Dict[str, int]:
        return {n: len(v) for n, v in self.factored_index.items()}

    def encode(self, pair: PairExample, *, guid: str = "") -> ClassificationFeature:
        tokens = pair.text.strip().split()[: self.max_seq_length - 2]
        full_tokens = [self.boundary_token, *tokens, self.boundary_token]
        tokens_len = len(full_tokens)

        input_ids = _convert_tokens_to_ids(self.tokenizer, full_tokens)
        input_mask = [1] * len(input_ids)
        segment_ids = [0] * len(input_ids)
        pad = self.max_seq_length - len(input_ids)
        input_ids += [PAD_ID] * pad
        input_mask += [0] * pad
        segment_ids += [0] * pad

        span_masks: Dict[str, List[int]] = {}
        for name, span in zip(self.schema.spans, pair.spans):
            mask = [0] * self.max_seq_length
            start, end = span
            if (start, end) == IMPLICIT:
                # Implicit slots read a boundary token: the first for the leading
                # element, the last for every following one.
                pos = 0 if name == self.schema.spans[0] else tokens_len - 1
                mask[pos] = 1
            else:
                for i in range(start + 1, min(end + 1, self.max_seq_length)):
                    mask[i] = 1
                if not any(mask):
                    mask[0] = 1
            span_masks[name] = mask

        joint = [0] * len(self.joint_index)
        factored = {n: [0] * len(v) for n, v in self.factored_index.items()}
        for key in pair.label_keys:
            if key in self.joint_index:
                joint[self.joint_index[key]] = 1
            parts = self.spaces.split_joint(key)
            for name, value in parts.items():
                idx = self.factored_index[name].get(value)
                if idx is not None:
                    factored[name][idx] = 1

        return ClassificationFeature(
            tokens_len=tokens_len,
            input_ids=input_ids,
            input_mask=input_mask,
            segment_ids=segment_ids,
            span_masks=span_masks,
            joint_label=joint,
            factored_labels=factored,
            tokens=full_tokens,
            guid=guid,
        )

    def encode_all(self, pairs: Sequence[PairExample]) -> List[ClassificationFeature]:
        return [self.encode(p, guid=f"{i}") for i, p in enumerate(pairs)]


def _convert_tokens_to_ids(tokenizer, tokens: Sequence[str]) -> List[int]:
    fn = getattr(tokenizer, "convert_tokens_to_ids", None)
    if fn is None:
        raise AttributeError(
            f"{type(tokenizer).__name__} cannot map tokens to ids; "
            "feature encoding needs a vocab-backed tokenizer"
        )
    ids = list(fn(list(tokens)))
    if len(ids) != len(tokens):
        raise ValueError("tokenizer changed the token count during id conversion")
    return ids


def build_encoders(
    tokenizer,
    schema,
    spaces: LabelSpaceSet,
    *,
    max_seq_length: int = 128,
    tagging: str = "bio",
) -> Tuple[ExtractionEncoder, ClassificationEncoder]:
    schema = get_schema(schema)
    scheme = TAGGING.build(tagging, schema.spans)
    extraction = ExtractionEncoder(
        tokenizer=tokenizer, schema=schema, tagging=scheme, max_seq_length=max_seq_length
    )
    classification = ClassificationEncoder(
        tokenizer=tokenizer, schema=schema, spaces=spaces, max_seq_length=max_seq_length
    )
    return extraction, classification
