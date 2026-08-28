"""Citations, machine-readable.

Every design decision in this package that rests on published work names its
source here rather than in prose, so a claim can be traced without grepping
docstrings.  Each DOI was checked against the Crossref REST API
(``https://api.crossref.org/works/<doi>``) on 2026-08-28; the ``title`` field
below is what Crossref returns, not a paraphrase.

Three works genuinely have no DOI, and they are recorded as such instead of
being given a plausible-looking one:

* Lafferty et al. 2001 - the ICML 2001 proceedings were never DOI-registered;
* Loshchilov & Hutter 2019 - ICLR/OpenReview papers have no DOI (arXiv only);
* Ekman 1971 - a book chapter in the Nebraska Symposium series.

The gate :func:`absa5.selftest.gate_references` checks the shape of every entry
and that every ``cited_by`` module actually exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .registry import Registry

CROSSREF_CHECKED = "2026-08-28"


@dataclass(frozen=True)
class Reference:
    """One citation.  ``doi`` is None only when the work has none."""

    key: str
    authors: Tuple[str, ...]
    year: str
    title: str
    venue: str
    doi: Optional[str] = None
    arxiv: Optional[str] = None
    url: Optional[str] = None
    note: str = ""
    cited_by: Tuple[str, ...] = ()

    def __post_init__(self):
        if not self.doi and not self.arxiv and not self.url:
            raise ValueError(f"{self.key}: needs a doi, an arxiv id, or a url")
        if self.doi and not self.doi.startswith("10."):
            raise ValueError(f"{self.key}: {self.doi!r} is not a DOI")

    @property
    def identifier(self) -> str:
        if self.doi:
            return f"doi:{self.doi}"
        if self.arxiv:
            return f"arXiv:{self.arxiv}"
        return self.url or ""

    @property
    def link(self) -> str:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        if self.arxiv:
            return f"https://arxiv.org/abs/{self.arxiv}"
        return self.url or ""

    @property
    def family(self) -> str:
        """Surname of the first author, for inline citations."""
        return self.authors[0].split()[-1]

    def author_string(self, *, max_authors: int = 3) -> str:
        if len(self.authors) > max_authors:
            return f"{self.authors[0]} et al."
        return ", ".join(self.authors)

    def cite(self) -> str:
        """Short inline form: ``Ekman 1992, doi:10.1080/02699939208411068``."""
        return f"{self.family} {self.year}, {self.identifier}"

    def full(self) -> str:
        parts = [f"{self.author_string()} ({self.year}). {self.title}. {self.venue}."]
        if self.identifier:
            parts.append(self.identifier)
        if self.note:
            parts.append(f"[{self.note}]")
        return " ".join(parts)

    def bibtex(self) -> str:
        kind = "inproceedings" if "Proceedings" in self.venue or "ACL" in self.venue else "article"
        lines = [
            f"@{kind}{{{self.key},",
            f"  author    = {{{' and '.join(self.authors)}}},",
            f"  title     = {{{self.title}}},",
            f"  year      = {{{self.year}}},",
            f"  booktitle = {{{self.venue}}}," if kind == "inproceedings"
            else f"  journal   = {{{self.venue}}},",
        ]
        if self.doi:
            lines.append(f"  doi       = {{{self.doi}}},")
        if self.arxiv:
            lines.append(f"  eprint    = {{{self.arxiv}}},")
            lines.append("  archivePrefix = {arXiv},")
        if self.url and not self.doi:
            lines.append(f"  url       = {{{self.url}}},")
        lines.append("}")
        return "\n".join(lines)


REFERENCES: Registry[Reference] = Registry("reference")


def _add(ref: Reference) -> Reference:
    REFERENCES.add(ref.key, ref)
    return ref


# -- the task this package extends -----------------------------------------
_add(Reference(
    key="cai2021acos",
    authors=("Hongjie Cai", "Rui Xia", "Jianfei Yu"),
    year="2021",
    title=(
        "Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit "
        "Aspects and Opinions"
    ),
    venue="Proceedings of the 59th Annual Meeting of the ACL (ACL 2021)",
    doi="10.18653/v1/2021.acl-long.29",
    note="the ACOS task and the Extract-Classify baseline this repo forks",
    cited_by=("schema", "metrics", "features"),
))

_add(Reference(
    key="zhang2021asqp",
    authors=("Wenxuan Zhang", "Yang Deng", "Xin Li", "Yifei Yuan", "Lidong Bing", "Wai Lam"),
    year="2021",
    title="Aspect Sentiment Quad Prediction as Paraphrase Generation",
    venue="Proceedings of EMNLP 2021",
    doi="10.18653/v1/2021.emnlp-main.726",
    note="generative alternative to pipeline quad extraction",
    cited_by=("schema",),
))

_add(Reference(
    key="pontiki2016semeval",
    authors=("Maria Pontiki", "Dimitris Galanis", "Haris Papageorgiou"),
    year="2016",
    title="SemEval-2016 Task 5: Aspect Based Sentiment Analysis",
    venue="Proceedings of SemEval-2016",
    doi="10.18653/v1/S16-1002",
    note="source of the ENTITY#ATTRIBUTE category convention and the rest16 data",
    cited_by=("taxonomy",),
))

_add(Reference(
    key="peper2024acosi",
    authors=("Joseph J. Peper", "Wenzhao Qiu", "Ryan Bruggeman"),
    year="2024",
    title=(
        "Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit "
        "Opinion Extraction"
    ),
    venue="Findings of EMNLP 2024",
    doi="10.18653/v1/2024.findings-emnlp.907",
    note=(
        "the existing five-element ABSA task; its fifth element is an implicitness "
        "marker, not emotion, so 'quintuple' is already taken in this literature"
    ),
    cited_by=("schema",),
))

_add(Reference(
    key="xia2019ecpe",
    authors=("Rui Xia", "Zixiang Ding"),
    year="2019",
    title="Emotion-Cause Pair Extraction: A New Task to Emotion Analysis in Texts",
    venue="Proceedings of ACL 2019",
    doi="10.18653/v1/P19-1096",
    note="closest prior art joining emotion to structured extraction, at clause level",
    cited_by=("emotion",),
))

# -- emotion taxonomies ----------------------------------------------------
_add(Reference(
    key="ekman1992basic",
    authors=("Paul Ekman",),
    year="1992",
    title="An argument for basic emotions",
    venue="Cognition and Emotion 6(3-4), 169-200",
    doi="10.1080/02699939208411068",
    note="the six basic emotions behind the EMOTIONS['ekman'] label set",
    cited_by=("taxonomy",),
))

_add(Reference(
    key="ekman1971universals",
    authors=("Paul Ekman",),
    year="1971",
    title="Universals and cultural differences in facial expressions of emotion",
    venue=(
        "Nebraska Symposium on Motivation 1971, Vol. 19, 207-283, "
        "University of Nebraska Press"
    ),
    url="https://psycnet.apa.org/record/1973-01880-001",
    note=(
        "no DOI: book chapter, imprint year 1972. Do not substitute the distinct "
        "1987 JPSP paper (10.1037/0022-3514.53.4.712) for it"
    ),
    cited_by=("taxonomy",),
))

_add(Reference(
    key="plutchik1980theory",
    authors=("Robert Plutchik",),
    year="1980",
    title="A general psychoevolutionary theory of emotion",
    venue="Emotion: Theory, Research, and Experience, Vol. 1, 3-33, Academic Press",
    doi="10.1016/B978-0-12-558701-3.50007-7",
    note="the eight primary emotions behind EMOTIONS['plutchik']",
    cited_by=("taxonomy",),
))

_add(Reference(
    key="plutchik2001nature",
    authors=("Robert Plutchik",),
    year="2001",
    title="The Nature of Emotions",
    venue="American Scientist 89(4), 344",
    doi="10.1511/2001.4.344",
    note=(
        "the wheel-of-emotions presentation. Crossref carries a duplicate record "
        "10.1511/2001.28.344; this is the original registration"
    ),
    cited_by=("taxonomy",),
))

_add(Reference(
    key="russell1980circumplex",
    authors=("James A. Russell",),
    year="1980",
    title="A circumplex model of affect",
    venue="Journal of Personality and Social Psychology 39(6), 1161-1178",
    doi="10.1037/h0077714",
    note=(
        "the valence-arousal argument for why sentiment polarity and emotion are "
        "different axes, which is what makes the fifth element non-redundant in "
        "principle - see absa5.emotion.sentiment_redundancy for the empirical test"
    ),
    cited_by=("emotion", "taxonomy"),
))

_add(Reference(
    key="demszky2020goemotions",
    authors=("Dorottya Demszky", "Dana Movshovitz-Attias", "Jeongwoo Ko"),
    year="2020",
    title="GoEmotions: A Dataset of Fine-Grained Emotions",
    venue="Proceedings of ACL 2020",
    doi="10.18653/v1/2020.acl-main.372",
    note="27 emotions plus neutral, and the hierarchical mapping down to Ekman-6",
    cited_by=("taxonomy",),
))

# -- Indonesian resources --------------------------------------------------
_add(Reference(
    key="wilie2020indonlu",
    authors=("Bryan Wilie", "Karissa Vincentio", "Genta Indra Winata"),
    year="2020",
    title=(
        "IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural "
        "Language Understanding"
    ),
    venue="Proceedings of AACL-IJCNLP 2020",
    doi="10.18653/v1/2020.aacl-main.85",
    note=(
        "source of IndoBERT and of the EmoT task whose five labels became "
        "EMOTIONS['emot']"
    ),
    cited_by=("taxonomy", "encoders"),
))

_add(Reference(
    key="saputri2018emotion",
    authors=("Mei Silviana Saputri", "Rahmad Mahendra", "Mirna Adriani"),
    year="2018",
    title="Emotion Classification on Indonesian Twitter Dataset",
    venue="2018 International Conference on Asian Language Processing (IALP)",
    doi="10.1109/IALP.2018.8629262",
    note=(
        "the corpus behind EmoT: 4,403 tweets, labels anger/happy/sadness/fear/love. "
        "Tweets are selected for emotional content, which is the reason "
        "EMOTIONS['emot_id_netral'] adds a neutral class for ABSA text"
    ),
    cited_by=("taxonomy", "emotion"),
))

_add(Reference(
    key="cahyawijaya2023nusawrites",
    authors=("Samuel Cahyawijaya", "Holy Lovenia", "Fajri Koto"),
    year="2023",
    title=(
        "NusaWrites: Constructing High-Quality Corpora for Underrepresented and "
        "Extremely Low-Resource Languages"
    ),
    venue="Proceedings of AACL-IJCNLP 2023",
    doi="10.18653/v1/2023.ijcnlp-main.60",
    note=(
        "NusaParagraph's 7 emotion labels are the only Indonesian set carrying both "
        "disgust and surprise; registered as EMOTIONS['nusaparagraph']"
    ),
    cited_by=("taxonomy",),
))

_add(Reference(
    key="winata2023nusax",
    authors=("Genta Indra Winata", "Alham Fikri Aji", "Samuel Cahyawijaya"),
    year="2023",
    title="NusaX: Multilingual Parallel Sentiment Dataset for 10 Indonesian Local Languages",
    venue="Proceedings of EACL 2023",
    doi="10.18653/v1/2023.eacl-main.57",
    note="sentiment only, no emotion; relevant to later local-language extension",
    cited_by=("taxonomy",),
))

_add(Reference(
    key="koto2020indolem",
    authors=("Fajri Koto", "Afshin Rahimi", "Jey Han Lau", "Timothy Baldwin"),
    year="2020",
    title=(
        "IndoLEM and IndoBERT: A Benchmark Dataset and Pre-trained Language Model "
        "for Indonesian NLP"
    ),
    venue="Proceedings of COLING 2020",
    doi="10.18653/v1/2020.coling-main.66",
    note="a second, distinct IndoBERT; no emotion task among its seven",
    cited_by=("encoders",),
))

# -- architecture and method ----------------------------------------------
_add(Reference(
    key="devlin2019bert",
    authors=("Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"),
    year="2019",
    title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    venue="Proceedings of NAACL-HLT 2019",
    doi="10.18653/v1/N19-1423",
    note=(
        "the DOI resolves but Crossref's deposited title field is empty; title taken "
        "from the ACL Anthology"
    ),
    cited_by=("encoders", "models"),
))

_add(Reference(
    key="conneau2020xlmr",
    authors=("Alexis Conneau", "Kartikay Khandelwal", "Naman Goyal"),
    year="2020",
    title="Unsupervised Cross-lingual Representation Learning at Scale",
    venue="Proceedings of ACL 2020",
    doi="10.18653/v1/2020.acl-main.747",
    note=(
        "the multilingual comparison a reviewer will ask for. Needs its own "
        "tokenised data, which is why tokenizers enter as a parameter"
    ),
    cited_by=("tokenizers", "encoders"),
))

_add(Reference(
    key="schuster2012wordpiece",
    authors=("Mike Schuster", "Kaisuke Nakajima"),
    year="2012",
    title="Japanese and Korean voice search",
    venue="2012 IEEE International Conference on Acoustics, Speech and Signal Processing",
    doi="10.1109/ICASSP.2012.6289079",
    note="WordPiece, the subword scheme whose splits force the span remapping",
    cited_by=("tokenizers", "spans"),
))

_add(Reference(
    key="lafferty2001crf",
    authors=("John Lafferty", "Andrew McCallum", "Fernando C. N. Pereira"),
    year="2001",
    title=(
        "Conditional Random Fields: Probabilistic Models for Segmenting and "
        "Labeling Sequence Data"
    ),
    venue="Proceedings of the 18th International Conference on Machine Learning (ICML 2001), 282-289",
    url="https://repository.upenn.edu/cis_papers/159/",
    note="no DOI: the ICML 2001 proceedings were never DOI-registered",
    cited_by=("heads",),
))

_add(Reference(
    key="lample2016ner",
    authors=("Guillaume Lample", "Miguel Ballesteros", "Sandeep Subramanian"),
    year="2016",
    title="Neural Architectures for Named Entity Recognition",
    venue="Proceedings of NAACL-HLT 2016",
    doi="10.18653/v1/N16-1030",
    note=(
        "the BiLSTM-CRF span-tagging architecture; the deferred pre-Transformer "
        "baseline, and the reason the CRF head is encoder-agnostic"
    ),
    cited_by=("heads", "features"),
))

_add(Reference(
    key="loshchilov2019adamw",
    authors=("Ilya Loshchilov", "Frank Hutter"),
    year="2019",
    title="Decoupled Weight Decay Regularization",
    venue="International Conference on Learning Representations (ICLR 2019)",
    arxiv="1711.05101",
    note=(
        "no DOI: ICLR/OpenReview papers are not DOI-registered. The optimiser "
        "absa5.engine.build_optimizer uses, with the no-decay group split"
    ),
    cited_by=("engine",),
))

# -- annotation quality ----------------------------------------------------
_add(Reference(
    key="cohen1960kappa",
    authors=("Jacob Cohen",),
    year="1960",
    title="A Coefficient of Agreement for Nominal Scales",
    venue="Educational and Psychological Measurement 20(1), 37-46",
    doi="10.1177/001316446002000104",
    note="the statistic absa5.emotion.agreement computes",
    cited_by=("emotion",),
))

_add(Reference(
    key="landis1977agreement",
    authors=("J. Richard Landis", "Gary G. Koch"),
    year="1977",
    title="The Measurement of Observer Agreement for Categorical Data",
    venue="Biometrics 33(1), 159-174",
    doi="10.2307/2529310",
    note=(
        "source of the slight/fair/moderate/substantial/almost-perfect bands in "
        "absa5.emotion._kappa_band. The bands are a convention, not a threshold "
        "derived from theory"
    ),
    cited_by=("emotion",),
))


# -- access ----------------------------------------------------------------
def cite(*keys: str) -> str:
    """Inline citation string for one or more keys."""
    return "; ".join(REFERENCES.get(k).cite() for k in keys)


def get(key: str) -> Reference:
    return REFERENCES.get(key)


def for_module(module: str) -> List[Reference]:
    """Every reference that names ``module`` in its ``cited_by``."""
    return [
        REFERENCES.get(k) for k in REFERENCES.names()
        if module in REFERENCES.get(k).cited_by
    ]


def all_references() -> List[Reference]:
    return [REFERENCES.get(k) for k in REFERENCES.names()]


def without_doi() -> List[Reference]:
    """The works that genuinely have no DOI, so the gap is explicit."""
    return [r for r in all_references() if not r.doi]


def bibliography(*, group_by_module: bool = False) -> str:
    if not group_by_module:
        return "\n".join(f"- {r.full()}" for r in all_references())
    modules: Dict[str, List[Reference]] = {}
    for ref in all_references():
        for module in ref.cited_by or ("(uncited)",):
            modules.setdefault(module, []).append(ref)
    blocks = []
    for module in sorted(modules):
        blocks.append(f"{module}:")
        blocks.extend(f"  - {r.full()}" for r in modules[module])
    return "\n".join(blocks)


def bibtex(*keys: str) -> str:
    refs = [REFERENCES.get(k) for k in keys] if keys else all_references()
    return "\n\n".join(r.bibtex() for r in refs)


def markdown_table() -> str:
    rows = [("key", "work", "identifier")]
    for ref in all_references():
        rows.append(
            (ref.key, f"{ref.family} et al. ({ref.year})"
             if len(ref.authors) > 1 else f"{ref.family} ({ref.year})", ref.identifier)
        )
    widths = [max(len(r[i]) for r in rows) for i in range(3)]
    lines = []
    for i, row in enumerate(rows):
        lines.append("| " + " | ".join(c.ljust(widths[j]) for j, c in enumerate(row)) + " |")
        if i == 0:
            lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    return "\n".join(lines)
