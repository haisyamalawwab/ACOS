"""Turning quadruple data into quintuple data.

No published dataset carries (aspect, category, opinion, sentiment, emotion), so
the emotion column has to be created.  The five-element ABSA tasks that do exist
mean something else by "quintuple": ACOSI's fifth element is an implicitness
marker (Peper 2024, doi:10.18653/v1/2024.findings-emnlp.907), and COQE's are
comparative-opinion slots.  The nearest work joining emotion to structured
extraction is emotion-cause pair extraction, which operates on clauses rather
than aspects (Xia 2019, doi:10.18653/v1/P19-1096).

This module supports the only defensible route: produce *candidate* labels
cheaply, then have people check them.

What is here:

* :func:`export_annotation_tasks` - writes one row per tuple for human labelling,
  which is the path that yields data you can publish;
* :class:`LexiconEmotionTagger` - a transparent keyword baseline used to
  pre-fill candidates and to measure how much work annotation actually saves;
* :func:`agreement` - Cohen's kappa (Cohen 1960, doi:10.1177/001316446002000104)
  with the Landis & Koch bands (doi:10.2307/2529310), so the pre-fill is never
  trusted blindly;
* :func:`sentiment_redundancy` - whether the emotion column adds anything over
  sentiment at all.

That last one is the scientific crux.  Sentiment polarity and emotion are
distinct axes in affect theory - valence is one dimension of Russell's circumplex,
not the whole space (Russell 1980, doi:10.1037/h0077714) - but *in a given
annotated dataset* they can still collapse into each other.  Theory says the fifth
element can carry information; only measurement says whether it does.

The lexicon is a starting point, not a resource: it is small, it is not
validated, and anything it produces is marked ``suggested`` until a human
confirms it.  Training on unchecked output measures the lexicon, not the model.
"""

from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .data import Record, read_records, write_records
from .registry import Registry
from .schema import Tup, get_schema
from .taxonomy import EMOTIONS

SUGGESTED = "suggested"
CONFIRMED = "confirmed"

# Indonesian cue words per EmoT class.  Deliberately short and readable; extend
# it from annotated data rather than from intuition.
LEXICON_ID: Dict[str, Tuple[str, ...]] = {
    "marah": (
        "marah", "kesal", "jengkel", "geram", "sebal", "murka", "kecewa berat",
        "parah", "buruk sekali", "tidak sopan", "kasar", "lambat sekali", "menyebalkan",
    ),
    "sedih": (
        "sedih", "kecewa", "menyesal", "sayang sekali", "kurang", "hampa",
        "mengecewakan", "gagal", "sepi", "muram",
    ),
    "takut": (
        "takut", "khawatir", "cemas", "ragu", "was-was", "ngeri", "trauma",
        "tidak aman", "curiga",
    ),
    "senang": (
        "senang", "enak", "mantap", "lezat", "puas", "bagus", "keren", "nyaman",
        "ramah", "cepat", "murah", "bersih", "rekomendasi", "terbaik", "gurih",
    ),
    "cinta": (
        "cinta", "suka banget", "favorit", "kangen", "rindu", "jatuh cinta",
        "selalu kembali", "langganan", "sayang",
    ),
}

# Fallback when no cue word fires: sentiment alone is weak evidence for emotion,
# so the mapping is coarse on purpose and the result stays "suggested".
SENTIMENT_FALLBACK: Dict[str, str] = {"0": "marah", "1": "netral", "2": "senang"}


@dataclass
class EmotionSuggestion:
    label: str
    status: str = SUGGESTED
    evidence: List[str] = field(default_factory=list)
    scores: Dict[str, int] = field(default_factory=dict)

    @property
    def confident(self) -> bool:
        """One class fired and nothing else did."""
        hits = [k for k, v in self.scores.items() if v > 0]
        return len(hits) == 1 and bool(self.evidence)


class EmotionTagger:
    name = "base"

    def suggest(self, text: str, tup: Tup) -> EmotionSuggestion:
        raise NotImplementedError


class ConstantEmotionTagger(EmotionTagger):
    """Fills a single placeholder; makes a quad file structurally valid as quint."""

    name = "constant"

    def __init__(self, label: str = "netral"):
        self.label = label

    def suggest(self, text: str, tup: Tup) -> EmotionSuggestion:
        return EmotionSuggestion(label=self.label, status=SUGGESTED)


class LexiconEmotionTagger(EmotionTagger):
    """Keyword scoring over the opinion span first, then the whole sentence.

    Scoring the opinion span before the sentence matters: a review can carry
    several tuples with different emotions, and a sentence-level cue would give
    them all the same label.

    ``label_set`` names the emotion registry entry this tagger must stay inside.
    It defaults to ``emot_id_netral`` because the sentiment fallback needs a
    neutral class to fall back *to*; pointing it at plain ``emot_id`` (no neutral)
    raises rather than emitting a label the pair builder would later reject.
    """

    name = "lexicon"

    def __init__(
        self,
        lexicon: Optional[Mapping[str, Sequence[str]]] = None,
        *,
        fallback: Optional[Mapping[str, str]] = None,
        label_set: str = "emot_id_netral",
        opinion_element: str = "opinion",
        sentiment_element: str = "sentiment",
        window: int = 4,
    ):
        self.lexicon = {k: tuple(v) for k, v in (lexicon or LEXICON_ID).items()}
        self.fallback = dict(fallback or SENTIMENT_FALLBACK)
        self.label_set = label_set
        self.labels = set(EMOTIONS.get(label_set))
        self.opinion_element = opinion_element
        self.sentiment_element = sentiment_element
        self.window = window

        stray = (set(self.lexicon) | set(self.fallback.values())) - self.labels
        if stray:
            raise ValueError(
                f"tagger would emit {sorted(stray)}, which is outside the "
                f"'{label_set}' label set {sorted(self.labels)}; pick a label set that "
                f"covers them or supply a matching lexicon and fallback"
            )

        self._patterns = {
            label: [re.compile(rf"(?<!\w){re.escape(cue)}(?!\w)", re.IGNORECASE) for cue in cues]
            for label, cues in self.lexicon.items()
        }

    def _score(self, text: str) -> Tuple[Dict[str, int], List[str]]:
        scores: Dict[str, int] = {label: 0 for label in self.lexicon}
        evidence: List[str] = []
        for label, patterns in self._patterns.items():
            for pattern, cue in zip(patterns, self.lexicon[label]):
                if pattern.search(text):
                    scores[label] += 1
                    evidence.append(f"{label}:{cue}")
        return scores, evidence

    def suggest(self, text: str, tup: Tup) -> EmotionSuggestion:
        words = text.split()
        focus = text
        if self.opinion_element in tup.schema.spans:
            start, end = tup.span(self.opinion_element)
            if (start, end) != (-1, -1):
                lo = max(0, start - self.window)
                hi = min(len(words), end + self.window)
                focus = " ".join(words[lo:hi])

        scores, evidence = self._score(focus)
        if not any(scores.values()) and focus != text:
            scores, evidence = self._score(text)

        if any(scores.values()):
            best = max(scores, key=lambda k: scores[k])
            return EmotionSuggestion(
                label=best, status=SUGGESTED, evidence=evidence, scores=scores
            )

        sentiment = str(tup.get(self.sentiment_element, "1"))
        return EmotionSuggestion(
            label=self.fallback.get(sentiment, "netral"),
            status=SUGGESTED,
            evidence=[f"fallback:sentiment={sentiment}"],
            scores=scores,
        )


TAGGERS: Registry = Registry("emotion tagger")
TAGGERS.add("lexicon", LexiconEmotionTagger, "keyword")
TAGGERS.add("constant", ConstantEmotionTagger, "placeholder")


# -- extension -------------------------------------------------------------
def extend_records(
    records: Sequence[Record],
    quint_schema,
    tagger: EmotionTagger,
    *,
    emotion_element: str = "emotion",
    sentiment_element: str = "sentiment",
) -> Tuple[List[Record], Dict[str, object]]:
    """Add an emotion value to every tuple, reporting how it was obtained."""
    quint = get_schema(quint_schema)
    out: List[Record] = []
    counts: Dict[str, int] = {}
    confident = 0
    total = 0
    joint: Dict[Tuple[str, str], int] = {}

    for rec in records:
        tuples: List[Tup] = []
        for tup in rec.tuples:
            suggestion = tagger.suggest(rec.text, tup)
            values = dict(tup.values)
            values[emotion_element] = suggestion.label
            tuples.append(Tup(quint, values))
            counts[suggestion.label] = counts.get(suggestion.label, 0) + 1
            confident += int(suggestion.confident)
            total += 1
            key = (str(tup.get(sentiment_element, "?")), suggestion.label)
            joint[key] = joint.get(key, 0) + 1
        out.append(Record(text=rec.text, tuples=tuples, schema=quint, line_no=rec.line_no))

    report = {
        "tuples": total,
        "distribution": dict(sorted(counts.items())),
        "unambiguous_cue_hits": confident,
        "unambiguous_ratio": confident / max(total, 1),
        "tagger": tagger.name,
        "status": SUGGESTED,
        "warning": (
            "every emotion value here is a suggestion; training on it without human "
            "validation measures the tagger, not the model"
        ),
    }
    report.update(sentiment_redundancy(joint))
    return out, report


def sentiment_redundancy(joint: Mapping[Tuple[str, str], int]) -> Dict[str, object]:
    """Measure how much the emotion column adds beyond sentiment.

    If every sentiment value maps to exactly one emotion, the fifth element is a
    renaming of the fourth and the quintuple is not a real extension.  This is the
    number that decides whether an emotion column is worth training on, so it is
    computed rather than assumed.

    Affect theory supports the distinction - valence is one axis of Russell's
    circumplex, and arousal is another (Russell 1980, doi:10.1037/h0077714), so
    "senang" and "cinta" can share a polarity while differing in emotion.  But
    theory only says the distinction *can* exist; whether a particular annotated
    file preserves it is an empirical question, and H(emotion | sentiment) is the
    answer.  Zero bits means the column is decorative.
    """
    by_sentiment: Dict[str, Dict[str, int]] = {}
    total = 0
    for (sentiment, emotion), count in joint.items():
        by_sentiment.setdefault(sentiment, {})[emotion] = count
        total += count

    deterministic = all(len(v) == 1 for v in by_sentiment.values()) if by_sentiment else False
    # Conditional entropy H(emotion | sentiment) in bits: 0 means fully redundant.
    conditional_entropy = 0.0
    for sentiment, emotions in by_sentiment.items():
        n = sum(emotions.values())
        for count in emotions.values():
            p = count / n
            if p > 0:
                conditional_entropy -= (n / total) * p * _log2(p)

    return {
        "emotion_given_sentiment": {k: dict(sorted(v.items())) for k, v in sorted(by_sentiment.items())},
        "emotion_is_function_of_sentiment": deterministic,
        "conditional_entropy_bits": conditional_entropy,
        "redundancy_verdict": (
            "the emotion column is a deterministic renaming of sentiment and adds no "
            "information; a model trained on it cannot learn anything sentiment does not "
            "already say"
            if deterministic
            else f"emotion carries {conditional_entropy:.3f} bits beyond sentiment"
        ),
    }


def _log2(x: float) -> float:
    import math

    return math.log2(x)


def extend_file(
    in_path: str,
    out_path: str,
    *,
    quad_schema="quad",
    quint_schema="quint",
    tagger: Optional[EmotionTagger] = None,
    report_path: Optional[str] = None,
) -> Dict[str, object]:
    quad = get_schema(quad_schema)
    quint = get_schema(quint_schema)
    records = read_records(in_path, quad)
    extended, report = extend_records(records, quint, tagger or LexiconEmotionTagger())
    write_records(out_path, extended, quint)
    report.update({"input": in_path, "output": out_path, "rows": len(extended)})
    if report_path:
        os.makedirs(os.path.dirname(os.path.abspath(report_path)) or ".", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
    return report


# -- annotation workflow ---------------------------------------------------
ANNOTATION_COLUMNS = (
    "row_id",
    "text",
    "aspect_span",
    "aspect_text",
    "opinion_span",
    "opinion_text",
    "category",
    "sentiment",
    "emotion_suggested",
    "emotion_final",
    "evidence",
    "annotator",
    "notes",
)


def export_annotation_tasks(
    records: Sequence[Record],
    out_path: str,
    *,
    tagger: Optional[EmotionTagger] = None,
    emotion_set: str = "emot_id",
) -> Dict[str, object]:
    """Write one CSV row per tuple, with ``emotion_final`` left blank for a human.

    The suggestion is included so annotators accept or correct rather than start
    cold, and ``evidence`` shows why it was suggested so a wrong cue is visible.
    """
    tagger = tagger or LexiconEmotionTagger()
    labels = EMOTIONS.get(emotion_set)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    rows = 0
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(ANNOTATION_COLUMNS)
        for rec_i, rec in enumerate(records):
            words = rec.text.split()
            for tup_i, tup in enumerate(rec.tuples):
                suggestion = tagger.suggest(rec.text, tup)
                writer.writerow(
                    [
                        f"{rec_i}-{tup_i}",
                        rec.text,
                        _span_str(tup, "aspect"),
                        _span_text(words, tup, "aspect"),
                        _span_str(tup, "opinion"),
                        _span_text(words, tup, "opinion"),
                        tup.get("category", ""),
                        tup.get("sentiment", ""),
                        suggestion.label,
                        "",
                        "; ".join(suggestion.evidence),
                        "",
                        "",
                    ]
                )
                rows += 1

    guide = os.path.splitext(out_path)[0] + "_guideline.md"
    with open(guide, "w", encoding="utf-8") as fh:
        fh.write(_guideline(labels, emotion_set=emotion_set))
    return {
        "output": out_path,
        "guideline": guide,
        "rows": rows,
        "label_set": emotion_set,
        "labels": list(labels),
    }


def import_annotations(
    tasks_path: str,
    records: Sequence[Record],
    quint_schema,
    *,
    emotion_set: str = "emot_id",
    require_complete: bool = True,
) -> Tuple[List[Record], Dict[str, object]]:
    """Read back ``emotion_final`` and attach it to the matching tuples."""
    quint = get_schema(quint_schema)
    labels = set(EMOTIONS.get(emotion_set))
    filled: Dict[str, str] = {}
    unknown: List[str] = []

    with open(tasks_path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            value = (row.get("emotion_final") or "").strip()
            if not value:
                continue
            if value not in labels:
                unknown.append(f"{row.get('row_id')}: {value!r}")
                continue
            filled[str(row.get("row_id"))] = value

    out: List[Record] = []
    missing: List[str] = []
    for rec_i, rec in enumerate(records):
        tuples: List[Tup] = []
        for tup_i, tup in enumerate(rec.tuples):
            row_id = f"{rec_i}-{tup_i}"
            if row_id not in filled:
                missing.append(row_id)
                if require_complete:
                    continue
                value = str(tup.get("emotion", "netral"))
            else:
                value = filled[row_id]
            values = dict(tup.values)
            values["emotion"] = value
            tuples.append(Tup(quint, values))
        if tuples:
            out.append(Record(text=rec.text, tuples=tuples, schema=quint, line_no=rec.line_no))

    report = {
        "annotated": len(filled),
        "missing": len(missing),
        "missing_examples": missing[:20],
        "invalid_labels": unknown[:20],
        "status": CONFIRMED if not missing and not unknown else "incomplete",
    }
    if require_complete and (missing or unknown):
        raise ValueError(
            f"annotation incomplete: {len(missing)} rows blank, "
            f"{len(unknown)} invalid labels (first: {(missing + unknown)[:3]})"
        )
    return out, report


def agreement(a: Sequence[str], b: Sequence[str]) -> Dict[str, object]:
    """Cohen's kappa plus raw agreement, for the annotator-reliability check."""
    if len(a) != len(b):
        raise ValueError("annotation sequences differ in length")
    n = len(a)
    if n == 0:
        return {"n": 0, "observed": 0.0, "kappa": 0.0}
    observed = sum(1 for x, y in zip(a, b) if x == y) / n
    labels = set(a) | set(b)
    expected = sum(
        (sum(1 for x in a if x == lab) / n) * (sum(1 for y in b if y == lab) / n)
        for lab in labels
    )
    kappa = 0.0 if expected >= 1.0 else (observed - expected) / (1 - expected)
    return {
        "n": n,
        "observed": observed,
        "expected": expected,
        "kappa": kappa,
        "interpretation": _kappa_band(kappa),
    }


def _kappa_band(kappa: float) -> str:
    """Landis & Koch bands (doi:10.2307/2529310).

    These are a widely reused convention, not a threshold derived from theory;
    the original authors called them arbitrary.  Treat 0.4 as a prompt to revisit
    the guideline, not as a pass mark.
    """
    if kappa < 0.2:
        return "slight - the label set or the guideline needs rework"
    if kappa < 0.4:
        return "fair - not yet publishable"
    if kappa < 0.6:
        return "moderate"
    if kappa < 0.8:
        return "substantial"
    return "almost perfect"


def _span_str(tup: Tup, name: str) -> str:
    if name not in tup.schema.spans:
        return ""
    start, end = tup.span(name)
    return f"{start},{end}"


def _span_text(words: Sequence[str], tup: Tup, name: str) -> str:
    if name not in tup.schema.spans:
        return ""
    start, end = tup.span(name)
    if (start, end) == (-1, -1):
        return "[IMPLISIT]"
    return " ".join(words[start:end])


def _guideline(labels: Sequence[str], *, emotion_set: str = "emot_id") -> str:
    from .references import get
    from .taxonomy import source_of

    source = source_of(emotion_set)
    provenance = (
        f"Label set `{emotion_set}` berasal dari {source.full()}"
        if source
        else f"Label set `{emotion_set}` tidak punya sumber terdaftar."
    )
    kappa = get("cohen1960kappa")
    bands = get("landis1977agreement")
    russell = get("russell1980circumplex")

    return f"""# Pedoman anotasi emosi (kolom `emotion_final`)

Label yang boleh dipakai: {', '.join(labels)}.

{provenance}

Aturan:

1. Beri label emosi **penulis terhadap aspek pada baris itu**, bukan emosi
   keseluruhan ulasan. Satu ulasan dengan dua aspek boleh punya dua emosi berbeda.
2. Gunakan `opinion_text` sebagai bukti utama. Jika opini implisit
   (`[IMPLISIT]`), pakai kalimat penuh, dan jika tetap tidak ada bukti emosi,
   pilih label yang paling dekat, jangan mengosongkan.
3. Sentimen dan emosi tidak boleh disamakan begitu saja. "harganya wajar"
   sentimennya positif tetapi emosinya bukan `senang` yang kuat; jangan
   memetakan positif -> senang secara mekanis. Dasar teoretisnya: valensi hanya
   satu sumbu dari ruang afek, bukan seluruh ruangnya
   ({russell.family} {russell.year}, {russell.identifier}).
4. Kolom `emotion_suggested` adalah keluaran leksikon dan sering salah. Perlakukan
   sebagai tebakan; `evidence` menunjukkan kata pemicunya sehingga kesalahan
   mudah terlihat.
5. Isi `annotator` dengan inisial Anda. Isi `notes` bila ragu; baris ber-notes
   dipakai untuk mengukur kesepakatan antar-anotator.

Prosedur mutu: minimal 200 baris dianotasi oleh dua orang secara independen,
lalu hitung Cohen's kappa ({kappa.family} {kappa.year}, {kappa.identifier}) lewat
`absa5.emotion.agreement`. Pembacaan nilainya memakai pita
{bands.family} & Koch ({bands.year}, {bands.identifier}) — pita itu konvensi,
bukan ambang teoretis. Di bawah 0.4, perbaiki pedoman atau kurangi jumlah label
sebelum melanjutkan.

Referensi lengkap dengan DOI: `python -m absa5 references --module emotion`
"""
