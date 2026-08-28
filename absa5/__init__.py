"""absa5 - schema-driven ABSA tuple extraction.

The upstream ACOS pipeline hardcodes four elements.  Here the tuple shape is
data: :data:`~absa5.schema.QUAD` and :data:`~absa5.schema.QUINT` drive the same
code, so adding emotion is a schema change rather than a fork.

Layers, from bottom up.  Everything except :mod:`~absa5.heads`,
:mod:`~absa5.models`, and :mod:`~absa5.engine` works without torch:

``registry``      name -> factory lookup, used by every pluggable layer
``schema``        which elements a tuple has and how it serialises
``taxonomy``      label vocabularies, plus joint vs factored label spaces
``references``    every citation with a Crossref-verified DOI
``tokenizers``    adapters over one method, ``tokenize(word) -> list[str]``
``spans``         word to subword span remapping
``data``          reading and writing the two on-disk formats
``features``      records to integer arrays, pluggable tagging scheme
``metrics``       tuple scoring, per element subset and implicitness bucket
``decode``        model outputs back to tuples
``emotion``       quad to quint bootstrap and the annotation workflow
``encoders``      checkpoint preparation and the weight-loading gate
``heads``         span, implicit, and label heads
``models``        stage models assembled from a config
``engine``        training and inference loops
``pipeline``      end-to-end orchestration
``config``        one dataclass tree that determines a run
``selftest``      verification gates, runnable with no ML dependencies

Start with ``python -m absa5.selftest --repo .``, and
``python -m absa5 references`` for the bibliography.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .config import RunConfig, list_presets, preset
from .data import (
    PairExample,
    Record,
    build_pair_files,
    convert_file,
    read_pairs,
    read_records,
    records_to_pairs,
    write_pairs,
    write_records,
)
from .metrics import IMPLICITNESS_BUCKETS, PRF, EvalResult, evaluate
from .references import REFERENCES, Reference, bibliography, bibtex, cite
from .registry import Registry
from .schema import QUAD, QUINT, SCHEMAS, Element, Tup, TupleSchema, get_schema
from .spans import Alignment, align_words, remap_record
from .taxonomy import (
    CATEGORIES,
    EMOTIONS,
    FACTORED,
    JOINT,
    LABEL_SET_SOURCES,
    SENTIMENTS,
    LabelSpace,
    LabelSpaceSet,
    build_label_spaces,
    label_spaces_for_domain,
    source_of,
)
from .tokenizers import (
    WhitespaceTokenizer,
    WordPieceTokenizer,
    as_tokenizer,
    build_tokenizer,
)

__all__ = [
    "__version__",
    # schema
    "QUAD", "QUINT", "SCHEMAS", "Element", "Tup", "TupleSchema", "get_schema",
    # taxonomy
    "CATEGORIES", "SENTIMENTS", "EMOTIONS", "JOINT", "FACTORED", "LABEL_SET_SOURCES",
    "LabelSpace", "LabelSpaceSet", "build_label_spaces", "label_spaces_for_domain",
    "source_of",
    # references
    "REFERENCES", "Reference", "cite", "bibliography", "bibtex",
    # tokenizers and spans
    "WhitespaceTokenizer", "WordPieceTokenizer", "as_tokenizer", "build_tokenizer",
    "Alignment", "align_words", "remap_record",
    # data
    "Record", "PairExample", "read_records", "write_records", "read_pairs",
    "write_pairs", "records_to_pairs", "convert_file", "build_pair_files",
    # metrics
    "PRF", "EvalResult", "evaluate", "IMPLICITNESS_BUCKETS",
    # config
    "RunConfig", "preset", "list_presets",
    # infrastructure
    "Registry",
]


def gates(repo: str = "."):
    """Run the verification gates; returns ``(passed, results)``."""
    from .selftest import run_gates

    return run_gates(repo)
