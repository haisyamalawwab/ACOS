"""Verification gates.  Every one of these runs without torch, numpy, or a GPU.

The gates exist because two of the failure modes in this pipeline are silent:
a mis-keyed checkpoint trains with a random encoder and reports no error, and a
wrong span remap only shows up as unexplained metric loss. Gate 2 in particular
is a regression test against ground truth that already ships in the repo:
``tokenized_data/*_quad_bert.tsv`` was produced by the original authors'
WordPiece pass, so reproducing it byte-for-byte proves the remapper.

Run: ``python -m absa5.selftest --repo .``
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .data import (
    PairExample,
    Record,
    parse_pair_line,
    parse_tag,
    pairs_from_prediction_line,
    read_records,
    records_to_pairs,
)
from .decode import assemble_tuples, decode_label_logits, decode_spans
from .emotion import LexiconEmotionTagger, agreement, extend_records
from .encoders import rekey_state_dict
from .features import BioTagging, ClassificationEncoder, ExtractionEncoder, build_encoders
from .metrics import (
    EXPLICIT_BOTH,
    IMPLICIT_ASPECT,
    IMPLICIT_BOTH,
    IMPLICIT_OPINION,
    evaluate,
    multiset_prf,
)
from .registry import Registry
from .schema import IMPLICIT, QUAD, QUINT, SchemaError, get_schema
from .spans import align_words, invert_alignment, remap_record, unmap_span
from .taxonomy import FACTORED, JOINT, build_label_spaces
from .tokenizers import WhitespaceTokenizer, WordPieceTokenizer

# One sentence in the upstream release is internally inconsistent, and the two
# gates below would otherwise report it forever.  In rest16_quad_train.tsv line
# 451 the opinion span is written 3,3 - zero width.  The authors' own derived
# files then disagree about what it should become: rest16_train_quad_bert.tsv
# records 3,4 while rest16_train_pair.tsv records 3,5, and the pair file also
# drops one of the sentence's three tuples.  There is no reconstruction that
# satisfies both, so the sentence is excused by name and everything else is held
# to exact equality.
KNOWN_UPSTREAM_DEFECTS = {
    "rest16_train:451": (
        "zero-width opinion span 3,3; quad_bert says 3,4 and pair says 3,5, "
        "and the pair file omits the 9,10/11,12 tuple"
    ),
}
DEFECT_SENTENCE_PREFIX = "this place is price ##y , and yes , the food is worth it"


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: Dict[str, object] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)

    def line(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        first = self.messages[0] if self.messages else ""
        return f"[{mark}] {self.name}: {first}"


GATES: Registry[Callable[..., GateResult]] = Registry("gate")


def gate(name: str):
    def deco(fn):
        GATES.add(name, fn)
        return fn

    return deco


# -- gate 1: schema and taxonomy invariants --------------------------------
@gate("schema")
def gate_schema(repo: str) -> GateResult:
    result = GateResult("schema", True)
    checks: Dict[str, object] = {}

    quad = get_schema("quad")
    quint = get_schema("quint")
    checks["quad_arity"] = quad.arity
    checks["quint_arity"] = quint.arity
    if quad.arity != 4 or quint.arity != 5:
        result.passed = False
        result.messages.append("arity is wrong")

    # A quad cell must parse under the quint schema, filling the emotion default.
    cell = "10,11 FOOD#QUALITY 2 13,16"
    as_quad = quad.parse(cell)
    as_quint = quint.parse(cell)
    checks["quad_roundtrip"] = quad.format(as_quad) == cell
    checks["quint_default_emotion"] = str(as_quint["emotion"])
    if quad.format(as_quad) != cell:
        result.passed = False
        result.messages.append("quad round-trip is not identity")
    if as_quint["aspect"] != (10, 11) or as_quint["opinion"] != (13, 16):
        result.passed = False
        result.messages.append("quint parse misplaced the spans")

    full = "10,11 FOOD#QUALITY 2 13,16 senang"
    parsed = quint.parse(full)
    checks["quint_roundtrip"] = quint.format(parsed) == full
    if quint.format(parsed) != full:
        result.passed = False
        result.messages.append("quint round-trip is not identity")

    # Implicit markers must survive parsing and never become half-implicit.
    imp = quint.parse("-1,-1 SERVICE#GENERAL 0 -1,-1 marah")
    checks["implicit_detected"] = imp.is_implicit("aspect") and imp.is_implicit("opinion")
    if not checks["implicit_detected"]:
        result.passed = False
        result.messages.append("implicit spans not recognised")

    quad = get_schema("quad")
    for bad in ("10,11 FOOD#QUALITY", "-1,3 FOOD#QUALITY 2 13,16", "5,2 FOOD#QUALITY 2 1,2"):
        try:
            quad.parse(bad)
        except SchemaError:
            continue
        result.passed = False
        result.messages.append(f"malformed cell accepted: {bad!r}")

    # A zero-width span is a real defect in rest16_quad_train.tsv line 451.  It is
    # repaired by default and rejected when repair is switched off; either way it
    # must never pass through unnoticed.
    repairs: List[str] = []
    widened = quad.parse("1,2 RESTAURANT#PRICES 0 3,3", repairs=repairs)
    checks["zero_width_repair"] = {"span": widened.span("opinion"), "log": repairs}
    if widened.span("opinion") != (3, 4) or not repairs:
        result.passed = False
        result.messages.append("zero-width span was not widened, or the repair went unlogged")
    try:
        quad.parse("1,2 RESTAURANT#PRICES 0 3,3", repair=False)
    except SchemaError:
        checks["zero_width_strict_rejects"] = True
    else:
        result.passed = False
        result.messages.append("repair=False still accepted a zero-width span")

    spaces = build_label_spaces(quint, category="resto_id", sentiment="acos", emotion="emot_id")
    checks["label_sizes"] = spaces.sizes()
    checks["joint_size"] = len(spaces.joint_labels())
    checks["factored_size"] = sum(spaces.sizes().values())
    if len(spaces.joint_labels()) != 13 * 3 * 5:
        result.passed = False
        result.messages.append("joint label space has the wrong size")

    # Splitting must survive the '#' inside ENTITY#ATTRIBUTE category names.
    key = spaces.join({"category": "MAKANAN#KUALITAS", "sentiment": "2", "emotion": "senang"})
    back = spaces.split_joint(key)
    checks["joint_split"] = back
    if back["category"] != "MAKANAN#KUALITAS" or back["emotion"] != "senang":
        result.passed = False
        result.messages.append("joint key split mangles categories containing '#'")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            f"quad/quint parse and round-trip cleanly; joint space "
            f"{checks['joint_size']} vs factored {checks['factored_size']}",
        )
    return result


# -- gate 2: span remap against the files already in the repo --------------
@gate("span_remap")
def gate_span_remap(repo: str) -> GateResult:
    """Reproduce ``tokenized_data`` from ``data`` using the repo's own vocab.

    Without a local BERT vocab the tokenizer cannot be rebuilt, so the gate
    instead inverts the shipped tokenised text into a word alignment and checks
    that remapping through it reproduces the shipped offsets exactly.
    """
    result = GateResult("span_remap", True)
    pairs = [
        (
            os.path.join(repo, "data", "Restaurant-ACOS", "rest16_quad_%s.tsv"),
            os.path.join(
                repo, "Extract-Classify-ACOS", "tokenized_data", "rest16_%s_quad_bert.tsv"
            ),
        ),
        (
            os.path.join(repo, "data", "Laptop-ACOS", "laptop_quad_%s.tsv"),
            os.path.join(
                repo, "Extract-Classify-ACOS", "tokenized_data", "laptop_%s_quad_bert.tsv"
            ),
        ),
    ]

    total_rows = 0
    total_spans = 0
    mismatched: List[str] = []
    text_mismatch = 0
    inverse_failures = 0
    repairs: List[str] = []
    excused = 0

    for raw_tpl, tok_tpl in pairs:
        for split in ("train", "dev", "test"):
            raw_path, tok_path = raw_tpl % split, tok_tpl % split
            if not (os.path.exists(raw_path) and os.path.exists(tok_path)):
                result.messages.append(f"skipped missing {os.path.basename(raw_path)}")
                continue
            raw = read_records(raw_path, QUAD, repairs=repairs)
            tok = read_records(tok_path, QUAD, repairs=repairs)
            if len(raw) != len(tok):
                result.passed = False
                mismatched.append(f"{split}: row count {len(raw)} vs {len(tok)}")
                continue

            for r, t in zip(raw, tok):
                total_rows += 1
                if t.text.startswith(DEFECT_SENTENCE_PREFIX):
                    excused += 1
                    continue
                alignment = invert_alignment(t.text.split())
                if alignment.words != _strip_for_compare(r.text.split()):
                    text_mismatch += 1
                for rt, tt in zip(r.tuples, t.tuples):
                    for element in QUAD.spans:
                        expected = tt.span(element)
                        try:
                            got = alignment.remap(rt.span(element))
                        except Exception as exc:  # noqa: BLE001
                            result.passed = False
                            mismatched.append(f"{split} line {r.line_no} {element}: {exc}")
                            continue
                        total_spans += 1
                        if got != expected:
                            result.passed = False
                            if len(mismatched) < 20:
                                mismatched.append(
                                    f"{split} line {r.line_no} {element}: "
                                    f"{rt.span(element)} -> {got}, file says {expected}"
                                )
                        if expected != IMPLICIT:
                            try:
                                if unmap_span(alignment, expected) != rt.span(element):
                                    inverse_failures += 1
                            except Exception:  # noqa: BLE001
                                inverse_failures += 1

    # Control: the identity tokenizer must be the identity transform.
    ws = WhitespaceTokenizer()
    rec = QUAD.parse("3,4 FOOD#QUALITY 2 1,2")
    text = "the food was really good ."
    _, remapped, _ = remap_record(ws, text, [rec], QUAD)
    identity_ok = remapped[0].span("aspect") == (3, 4) and remapped[0].span("opinion") == (1, 2)
    if not identity_ok:
        result.passed = False
        mismatched.append("whitespace tokenizer is not the identity transform")

    result.detail = {
        "rows_checked": total_rows,
        "spans_checked": total_spans,
        "span_mismatches": mismatched[:20],
        "span_mismatch_count": len(mismatched),
        "text_reconstruction_mismatches": text_mismatch,
        "inverse_mapping_failures": inverse_failures,
        "identity_control": identity_ok,
        "zero_width_repairs": repairs,
        "excused_rows": excused,
        "known_defects": KNOWN_UPSTREAM_DEFECTS,
    }
    if result.passed:
        result.messages.insert(
            0,
            f"{total_spans} spans across {total_rows - excused} rows remap exactly as the "
            f"repo's pre-tokenised files say they should "
            f"({excused} row excused, see known_defects)",
        )
    else:
        result.messages.insert(0, f"{len(mismatched)} discrepancies")
    return result


def _strip_for_compare(words: Sequence[str]) -> List[str]:
    """Lowercase-and-strip-accents comparison, matching the tokenizer's basic pass."""
    out = []
    for w in words:
        out.append(WordPieceTokenizer._strip_accents(w.lower()))
    return out


# -- gate 3: pair files and label keys -------------------------------------
@gate("pair_format")
def gate_pair_format(repo: str) -> GateResult:
    result = GateResult("pair_format", True)
    tok_dir = os.path.join(repo, "Extract-Classify-ACOS", "tokenized_data")
    quad_path = os.path.join(tok_dir, "rest16_train_quad_bert.tsv")
    pair_path = os.path.join(tok_dir, "rest16_train_pair.tsv")
    checks: Dict[str, object] = {}

    if not (os.path.exists(quad_path) and os.path.exists(pair_path)):
        result.passed = False
        result.messages.append("reference rest16 files are missing")
        return result

    records = read_records(quad_path, QUAD)
    spaces = build_label_spaces(QUAD, category="rest16", sentiment="acos")
    rebuilt = records_to_pairs(records, QUAD, spaces)
    shipped = [
        parse_pair_line(line, 2, line_no=i)
        for i, line in enumerate(open(pair_path, encoding="utf-8"), 1)
    ]
    shipped = [p for p in shipped if p is not None]

    checks["rebuilt_pairs"] = len(rebuilt)
    checks["shipped_pairs"] = len(shipped)

    def excused(key: str) -> bool:
        return key.startswith(DEFECT_SENTENCE_PREFIX)

    rebuilt_index = {p.key(): sorted(p.label_keys) for p in rebuilt if not excused(p.key())}
    shipped_index = {p.key(): sorted(p.label_keys) for p in shipped if not excused(p.key())}
    only_rebuilt = sorted(set(rebuilt_index) - set(shipped_index))
    only_shipped = sorted(set(shipped_index) - set(rebuilt_index))
    label_diff = [
        k for k in set(rebuilt_index) & set(shipped_index)
        if rebuilt_index[k] != shipped_index[k]
    ]

    checks["keys_only_in_rebuilt"] = len(only_rebuilt)
    checks["keys_only_in_shipped"] = len(only_shipped)
    checks["label_disagreements"] = len(label_diff)
    checks["excused_keys"] = sum(1 for p in rebuilt if excused(p.key()))
    checks["known_defects"] = KNOWN_UPSTREAM_DEFECTS
    checks["examples"] = {
        "only_rebuilt": only_rebuilt[:3],
        "only_shipped": only_shipped[:3],
        "label_diff": [
            {"key": k, "rebuilt": rebuilt_index[k], "shipped": shipped_index[k]}
            for k in label_diff[:3]
        ],
    }
    if only_rebuilt or only_shipped or label_diff:
        result.passed = False
        result.messages.append(
            f"pair reconstruction differs: {len(only_rebuilt)} extra, "
            f"{len(only_shipped)} missing, {len(label_diff)} with different labels"
        )

    multi = sum(1 for p in rebuilt if len(p.label_keys) > 1)
    checks["multi_label_pairs"] = multi
    checks["multi_label_ratio"] = multi / max(len(rebuilt), 1)

    if result.passed:
        result.messages.insert(
            0,
            f"rebuilt {len(rebuilt_index)} pair rows identical to the shipped file "
            f"({multi} carry more than one label set, {multi / max(len(rebuilt), 1):.1%})",
        )
    result.detail = checks
    return result


# -- gate 4: tag parsing (the Step 2 KeyError) -----------------------------
@gate("tag_parsing")
def gate_tag_parsing(repo: str) -> GateResult:
    result = GateResult("tag_parsing", True)
    checks: Dict[str, object] = {}

    good = {"a-3,4": ("a", (3, 4)), "o-0,1": ("o", (0, 1)), "a--1,-1": ("a", IMPLICIT)}
    for tag, expected in good.items():
        got = parse_tag(tag)
        if got != expected:
            result.passed = False
            result.messages.append(f"{tag} parsed as {got}")
    checks["accepted"] = list(good)

    rejected = []
    for bad in ("x-1,2", "a-1", "a-1,2,3", "aa-1,2", "a-1,-1", "", "a-", "o-x,y"):
        try:
            parse_tag(bad)
        except SchemaError:
            rejected.append(bad)
        else:
            result.passed = False
            result.messages.append(f"accepted malformed tag {bad!r}")
    checks["rejected"] = rejected

    # The upstream cross-product: two aspects and one opinion give two candidates.
    line = "the food was good .\ta-1,2\ta-0,1\to-3,4"
    pairs = pairs_from_prediction_line(line)
    checks["cross_product"] = [p.key() for p in pairs]
    if len(pairs) != 2:
        result.passed = False
        result.messages.append(f"cross product produced {len(pairs)} pairs, expected 2")

    # A line with only aspects must still yield a candidate, with implicit opinion.
    only_aspect = pairs_from_prediction_line("x y z\ta-0,1")
    checks["implicit_fill"] = [p.key() for p in only_aspect]
    if len(only_aspect) != 1 or only_aspect[0].spans[1] != IMPLICIT:
        result.passed = False
        result.messages.append("missing opinion was not filled with the implicit marker")

    # Garbage tags are dropped, not silently filed as opinions the way ele[2:] did.
    garbage = pairs_from_prediction_line("x y z\ta-0,1\tGARBAGE")
    checks["garbage_dropped"] = len(garbage) == 1
    if len(garbage) != 1:
        result.passed = False
        result.messages.append("a malformed tag leaked into the candidate set")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0, f"{len(good)} valid tag shapes parse, {len(rejected)} malformed shapes rejected"
        )
    return result


# -- gate 5: feature encoding -----------------------------------------------
@gate("features")
def gate_features(repo: str) -> GateResult:
    result = GateResult("features", True)
    checks: Dict[str, object] = {}

    tokenizer = _tiny_tokenizer()
    spaces = build_label_spaces(QUINT, category="resto_id", sentiment="acos", emotion="emot_id")
    extraction, classification = build_encoders(tokenizer, QUINT, spaces, max_seq_length=16)

    checks["tag_list"] = extraction.tagging.tag_list()
    expected_tags = ["[CLS]", "O", "I-A", "B-A", "I-O", "B-O"]
    if extraction.tagging.tag_list() != expected_tags:
        result.passed = False
        result.messages.append(
            f"tag list {extraction.tagging.tag_list()} differs from the upstream order "
            f"{expected_tags}, so CRF indices would not be comparable"
        )

    rec = Record(
        text="makanan nya enak sekali",
        tuples=[QUINT.parse("0,1 MAKANAN#KUALITAS 2 2,4 senang")],
        schema=QUINT,
    )
    feature = extraction.encode(rec)
    tags = [extraction.tagging.tag_list()[t] for t in feature.tag_ids[: feature.tokens_len]]
    checks["encoded_tags"] = tags
    # One boundary token is prepended, so the aspect at word 0 lands at index 1.
    if tags[1] != "B-A" or tags[3] != "B-O" or tags[4] != "I-O":
        result.passed = False
        result.messages.append(f"tag encoding is misaligned: {tags}")

    decoded = extraction.tagging.decode(tags)
    checks["decoded"] = {k: v for k, v in decoded.items()}
    if decoded["aspect"] != [(1, 2)] or decoded["opinion"] != [(3, 5)]:
        result.passed = False
        result.messages.append(f"tag decoding round-trip failed: {decoded}")

    shifted = decode_spans(
        feature.tag_ids[: feature.tokens_len], extraction.tagging, implicit_flags={}
    )
    checks["shifted"] = shifted
    if shifted["aspect"] != [(0, 1)] or shifted["opinion"] != [(2, 4)]:
        result.passed = False
        result.messages.append(f"offset correction is wrong: {shifted}")

    pair = PairExample(
        text="makanan nya enak sekali",
        spans=((0, 1), (2, 4)),
        label_keys=["MAKANAN#KUALITAS#2#senang"],
    )
    cfeature = classification.encode(pair)
    checks["joint_size"] = classification.joint_size
    checks["factored_sizes"] = classification.factored_sizes()
    checks["aspect_mask"] = cfeature.span_masks["aspect"][:8]
    checks["opinion_mask"] = cfeature.span_masks["opinion"][:8]
    if sum(cfeature.span_masks["aspect"]) != 1 or sum(cfeature.span_masks["opinion"]) != 2:
        result.passed = False
        result.messages.append("span masks cover the wrong number of tokens")
    if sum(cfeature.joint_label) != 1:
        result.passed = False
        result.messages.append("joint target is not one-hot for a single label set")
    for element, vector in cfeature.factored_labels.items():
        if sum(vector) != 1:
            result.passed = False
            result.messages.append(f"factored target for {element} is not one-hot")

    # An implicit pair must place its masks on the boundary tokens.
    imp_pair = PairExample(text="tidak akan kembali", spans=(IMPLICIT, IMPLICIT))
    imp_feature = classification.encode(imp_pair)
    checks["implicit_aspect_mask_at_0"] = imp_feature.span_masks["aspect"][0] == 1
    checks["implicit_opinion_mask_at_last"] = (
        imp_feature.span_masks["opinion"][imp_feature.tokens_len - 1] == 1
    )
    if not (checks["implicit_aspect_mask_at_0"] and checks["implicit_opinion_mask_at_last"]):
        result.passed = False
        result.messages.append("implicit spans are not pooled from the boundary tokens")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            f"encoding round-trips; joint head would need {classification.joint_size} "
            f"outputs, factored needs {sum(classification.factored_sizes().values())}",
        )
    return result


# -- gate 6: metrics --------------------------------------------------------
@gate("metrics")
def gate_metrics(repo: str) -> GateResult:
    result = GateResult("metrics", True)
    checks: Dict[str, object] = {}

    # A duplicated prediction must not be credited twice against one gold tuple.
    dup = multiset_prf(["x", "x"], ["x"])
    checks["duplicate_prediction"] = dup.as_dict()
    if dup.tp != 1 or dup.fp != 1:
        result.passed = False
        result.messages.append(
            f"duplicate prediction scored tp={dup.tp} fp={dup.fp}, expected tp=1 fp=1"
        )

    gold = {
        "s1": [QUINT.parse("0,1 MAKANAN#KUALITAS 2 2,4 senang")],
        "s2": [QUINT.parse("-1,-1 PELAYANAN#UMUM 0 -1,-1 marah")],
    }
    pred = {
        "s1": [QUINT.parse("0,1 MAKANAN#KUALITAS 2 2,4 sedih")],
        "s2": [QUINT.parse("-1,-1 PELAYANAN#UMUM 0 -1,-1 marah")],
    }
    res = evaluate(pred, gold, QUINT, max_subset_size=None)
    checks["full_f1"] = res.overall.f1
    if abs(res.overall.f1 - 0.5) > 1e-9:
        result.passed = False
        result.messages.append(f"full-tuple F1 {res.overall.f1} should be 0.5")

    quad_only = res.subset("aspect", "category", "sentiment", "opinion")
    checks["quad_subset_f1"] = quad_only.f1
    if abs(quad_only.f1 - 1.0) > 1e-9:
        result.passed = False
        result.messages.append(
            f"dropping emotion should give F1 1.0, got {quad_only.f1}; "
            "the emotion element is where the only error is"
        )

    emotion_only = res.subset("emotion")
    checks["emotion_only_f1"] = emotion_only.f1
    if abs(emotion_only.f1 - 0.5) > 1e-9:
        result.passed = False
        result.messages.append(f"emotion-only F1 {emotion_only.f1} should be 0.5")

    buckets = {k: v.as_dict() for k, v in res.by_bucket.items()}
    checks["buckets"] = buckets
    if EXPLICIT_BOTH not in buckets or IMPLICIT_BOTH not in buckets:
        result.passed = False
        result.messages.append("implicitness breakdown is missing a bucket")
    else:
        if abs(buckets[EXPLICIT_BOTH]["f1"] - 0.0) > 1e-9:
            result.passed = False
            result.messages.append("explicit bucket should score 0 here")
        if abs(buckets[IMPLICIT_BOTH]["f1"] - 1.0) > 1e-9:
            result.passed = False
            result.messages.append("implicit bucket should score 1 here")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            "multiset scoring, element-subset projection, and the "
            "explicit/implicit breakdown all behave",
        )
    return result


# -- gate 7: checkpoint re-keying (no torch needed) ------------------------
@gate("rekey")
def gate_rekey(repo: str) -> GateResult:
    result = GateResult("rekey", True)
    checks: Dict[str, object] = {}

    # IndoBERT ships keys with no prefix; they must all gain 'bert.'.
    indobert_like = {
        "embeddings.word_embeddings.weight": 1,
        "encoder.layer.0.attention.self.query.weight": 2,
        "pooler.dense.weight": 3,
    }
    out, changed, dropped = rekey_state_dict(indobert_like)
    checks["indobert"] = {"keys": list(out), "changed": changed, "dropped": dropped}
    if changed != 3 or not all(k.startswith("bert.") for k in out):
        result.passed = False
        result.messages.append("unprefixed keys were not given the 'bert.' prefix")

    # bert-base-uncased already has the prefix and must be left alone, minus cls.*.
    bert_like = {
        "bert.embeddings.word_embeddings.weight": 1,
        "cls.predictions.bias": 2,
    }
    out2, changed2, dropped2 = rekey_state_dict(bert_like)
    checks["bert"] = {"keys": list(out2), "changed": changed2, "dropped": dropped2}
    if changed2 != 0 or dropped2 != ["cls.predictions.bias"]:
        result.passed = False
        result.messages.append("already-prefixed keys were altered, or cls.* was kept")

    # Re-keying twice must be a no-op.
    out3, changed3, _ = rekey_state_dict(dict(out))
    if changed3 != 0 or list(out3) != list(out):
        result.passed = False
        result.messages.append("re-keying is not idempotent")
    checks["idempotent"] = changed3 == 0

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            "state_dict re-keying handles both prefix conventions and is idempotent",
        )
    return result


# -- gate 8: decoding -------------------------------------------------------
@gate("decode")
def gate_decode(repo: str) -> GateResult:
    result = GateResult("decode", True)
    checks: Dict[str, object] = {}

    spaces = build_label_spaces(QUINT, category="resto_id", sentiment="acos", emotion="emot_id")

    factored = {
        "category": [0.0] * 13,
        "sentiment": [0.0, 0.0, 2.0],
        "emotion": [0.0, 0.0, 0.0, 0.0, 1.5],
    }
    factored["category"][3] = 3.0
    sets = decode_label_logits(factored, spaces, mode=FACTORED)
    checks["factored"] = sets
    if len(sets) != 1 or sets[0]["emotion"] != "senang" or sets[0]["sentiment"] != "2":
        result.passed = False
        result.messages.append(f"factored decoding produced {sets}")

    # Nothing above threshold: the fallback must still yield one assignment.
    empty = {"category": [-1.0] * 13, "sentiment": [-1.0, -2.0, -3.0], "emotion": [-1.0] * 5}
    fallback = decode_label_logits(empty, spaces, mode=FACTORED)
    checks["fallback"] = fallback
    if len(fallback) != 1:
        result.passed = False
        result.messages.append("threshold fallback dropped the pair")

    joint_scores = [0.0] * len(spaces.joint_labels())
    target = spaces.joint_labels().index("MAKANAN#KUALITAS#2#senang")
    joint_scores[target] = 5.0
    joint_sets = decode_label_logits({"joint": joint_scores}, spaces, mode=JOINT)
    checks["joint"] = joint_sets
    if len(joint_sets) != 1 or joint_sets[0]["category"] != "MAKANAN#KUALITAS":
        result.passed = False
        result.messages.append(f"joint decoding produced {joint_sets}")

    pair = PairExample(text="a b c d", spans=((0, 1), (2, 4)))
    tuples = assemble_tuples(pair, sets, QUINT)
    checks["assembled"] = [str(t) for t in tuples]
    if len(tuples) != 1 or tuples[0].span("opinion") != (2, 4):
        result.passed = False
        result.messages.append("tuple assembly lost the spans")

    result.detail = checks
    if result.passed:
        result.messages.insert(0, "label decoding and tuple assembly agree in both modes")
    return result


# -- gate 9: emotion bootstrap ---------------------------------------------
@gate("emotion")
def gate_emotion(repo: str) -> GateResult:
    result = GateResult("emotion", True)
    checks: Dict[str, object] = {}

    tagger = LexiconEmotionTagger()
    records = [
        Record(
            text="makanan nya enak sekali dan pelayanan nya lambat sekali",
            tuples=[
                QUAD.parse("0,1 MAKANAN#KUALITAS 2 2,4"),
                QUAD.parse("6,7 PELAYANAN#UMUM 0 8,10"),
            ],
            schema=QUAD,
        )
    ]
    extended, report = extend_records(records, QUINT, tagger)
    labels = [str(t["emotion"]) for t in extended[0].tuples]
    checks["labels"] = labels
    checks["report"] = report
    # Two tuples in one sentence must be able to get different emotions.
    if labels[0] == labels[1]:
        result.passed = False
        result.messages.append(
            f"both tuples got '{labels[0]}'; the tagger is reading the sentence "
            "instead of the opinion span"
        )
    if labels[0] != "senang":
        result.passed = False
        result.messages.append(f"'enak sekali' produced '{labels[0]}'")

    kappa = agreement(["senang", "marah", "sedih", "senang"], ["senang", "marah", "senang", "senang"])
    checks["kappa"] = kappa
    if not 0.0 < kappa["kappa"] < 1.0:
        result.passed = False
        result.messages.append(f"kappa out of range: {kappa}")

    perfect = agreement(["a", "b"], ["a", "b"])
    if abs(perfect["kappa"] - 1.0) > 1e-9:
        result.passed = False
        result.messages.append("identical annotations did not give kappa 1.0")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            f"span-local tagging distinguishes tuples in one sentence "
            f"({report['unambiguous_ratio']:.0%} of tuples had exactly one cue hit)",
        )
    return result


# -- gate 10: config round-trip --------------------------------------------
@gate("config")
def gate_config(repo: str) -> GateResult:
    from .config import RunConfig, list_presets, preset

    result = GateResult("config", True)
    checks: Dict[str, object] = {}

    cfg = preset("quint_indobert_id")
    checks["presets"] = list_presets()
    checks["summary"] = cfg.summary()

    restored = RunConfig.from_dict(cfg.to_dict())
    checks["roundtrip"] = restored.to_dict() == cfg.to_dict()
    if not checks["roundtrip"]:
        result.passed = False
        result.messages.append("config does not survive a dict round-trip")

    tweaked = cfg.merged(**{"train.epochs": 3, "heads.label_mode": JOINT})
    checks["override"] = {
        "epochs": tweaked.train.epochs,
        "label_mode": tweaked.heads.label_mode,
    }
    if tweaked.train.epochs != 3 or tweaked.heads.label_mode != JOINT:
        result.passed = False
        result.messages.append("dotted overrides did not apply")
    if cfg.train.epochs == 3:
        result.passed = False
        result.messages.append("merged() mutated the original config")

    try:
        cfg.merged(**{"train.nonexistent": 1})
    except KeyError:
        checks["rejects_unknown_key"] = True
    else:
        result.passed = False
        result.messages.append("an unknown config key was accepted silently")

    quad_cfg = preset("quad_bert_en")
    checks["quad_summary"] = quad_cfg.summary()
    if quad_cfg.summary()["head_sizes"]["joint"] != 39:
        result.passed = False
        result.messages.append(
            f"quad joint head should be 39 outputs, got {quad_cfg.summary()['head_sizes']}"
        )

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0, f"{len(checks['presets'])} presets resolve and configs round-trip"
        )
    return result


def _tiny_tokenizer() -> WordPieceTokenizer:
    vocab = [
        "[PAD]", "[UNK]", "[CLS]", "[SEP]",
        "makanan", "nya", "enak", "sekali", "pelayanan", "lambat",
        "tidak", "akan", "kembali", "a", "b", "c", "d",
        "the", "food", "was", "really", "good", ".",
    ]
    return WordPieceTokenizer(vocab, do_lower_case=True)


# -- gate 11: the data path must not need torch ----------------------------
@gate("torch_free")
def gate_torch_free(repo: str) -> GateResult:
    """Importing any module must not pull in torch.

    This is a real constraint, not tidiness: the data preparation and every gate
    have to run on a machine with no ML stack, so the GPU-only work can be
    scheduled after the cheap checks already passed.
    """
    import importlib
    import subprocess

    result = GateResult("torch_free", True)
    modules = [
        "registry", "schema", "taxonomy", "tokenizers", "spans", "data",
        "features", "metrics", "decode", "config", "encoders", "emotion",
        "heads", "models", "engine", "pipeline", "cli", "selftest",
    ]
    failed: Dict[str, str] = {}
    for name in modules:
        try:
            importlib.import_module(f"absa5.{name}")
        except Exception as exc:  # noqa: BLE001
            failed[name] = f"{type(exc).__name__}: {exc}"

    if failed:
        result.passed = False
        result.messages.append(
            f"{len(failed)} modules cannot be imported without torch: {sorted(failed)}"
        )

    # Check in a clean interpreter too: a module already in sys.modules from an
    # earlier gate would mask a top-level torch import.
    probe = subprocess.run(
        [sys.executable, "-c", "import absa5.pipeline, absa5.models, sys; "
         "print('torch' in sys.modules)"],
        capture_output=True, text=True, cwd=repo,
    )
    leaked = probe.stdout.strip()
    result.detail = {
        "modules_checked": len(modules),
        "import_failures": failed,
        "torch_in_sys_modules_after_import": leaked,
        "probe_stderr": probe.stderr.strip()[-400:],
    }
    if probe.returncode != 0:
        result.passed = False
        result.messages.append(f"clean-interpreter probe failed: {probe.stderr.strip()[-200:]}")
    elif leaked != "False":
        result.passed = False
        result.messages.append(f"torch was imported eagerly (probe said {leaked!r})")

    if result.passed:
        result.messages.insert(
            0, f"all {len(modules)} modules import with no ML dependencies present"
        )
    return result


# -- gate 12: data preparation end to end ----------------------------------
@gate("prepare")
def gate_prepare(repo: str) -> GateResult:
    """Run the real preparation path on the bundled Indonesian demo data."""
    import shutil
    import tempfile

    from .config import preset
    from .data import read_pairs
    from .pipeline import prepare_data

    result = GateResult("prepare", True)
    demo = os.path.join(repo, "data", "Demo-Resto-ID")
    if not os.path.isdir(demo):
        result.passed = False
        result.messages.append("data/Demo-Resto-ID is missing")
        return result

    work = tempfile.mkdtemp(prefix="absa5_gate_")
    try:
        cfg = preset(
            "quint_indobert_id",
            **{
                "name": "gate_demo",
                "data.raw_dir": demo,
                "data.work_dir": work,
                "data.domain": "resto_id",
                "data.emotion_set": "emot_id_netral",
                "data.max_seq_length": 32,
                "data.subword_limit": 30,
                "tokenizer.kind": "whitespace",
            },
        )
        artifacts = prepare_data(cfg)
        checks: Dict[str, object] = {
            "splits": sorted(artifacts.tokenized),
            "label_report": artifacts.label_report,
        }

        for split in ("train", "dev", "test"):
            if split not in artifacts.tokenized:
                result.passed = False
                result.messages.append(f"split '{split}' was not prepared")
                continue
            report = artifacts.reports[split]
            if report["rows"] == 0:
                result.passed = False
                result.messages.append(f"split '{split}' produced no rows")
            if report["error_count"]:
                result.passed = False
                result.messages.append(f"split '{split}' logged {report['error_count']} errors")

        # The whitespace tokenizer changes nothing, so prepared text must equal input.
        original = read_records(
            os.path.join(demo, "resto_id_quint_train.tsv"), QUINT
        )
        prepared = read_records(artifacts.tokenized["train"], QUINT)
        checks["identity_preserved"] = [r.text for r in original] == [r.text for r in prepared]
        if not checks["identity_preserved"]:
            result.passed = False
            result.messages.append(
                "the identity tokenizer altered the text during preparation"
            )
        for a, b in zip(original, prepared):
            if [str(t) for t in a.tuples] != [str(t) for t in b.tuples]:
                result.passed = False
                result.messages.append(f"tuples changed on line {a.line_no}")
                break

        pairs = read_pairs(artifacts.pairs["train"], n_spans=2)
        checks["train_pairs"] = len(pairs)
        checks["all_pairs_labelled"] = all(p.label_keys for p in pairs)
        if not pairs or not checks["all_pairs_labelled"]:
            result.passed = False
            result.messages.append("pair file is empty or has unlabelled rows")

        # Every label key must split back into exactly the three label elements.
        spaces = cfg.label_spaces()
        for pair in pairs:
            for key in pair.label_keys:
                parts = spaces.split_joint(key)
                if set(parts) != set(spaces.elements):
                    result.passed = False
                    result.messages.append(f"label key {key!r} does not split cleanly")
                    break

        checks["joint_coverage"] = artifacts.label_report["joint_coverage"]
        result.detail = checks
        if result.passed:
            result.messages.insert(
                0,
                f"prepared {len(prepared)} train rows and {len(pairs)} pair rows; "
                f"only {artifacts.label_report['joint_coverage']:.1%} of the "
                f"{artifacts.label_report['joint_size']}-cell joint space is populated, "
                f"which is why factored is the default",
            )
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return result


# -- gate 13: references ----------------------------------------------------
@gate("references")
def gate_references(repo: str) -> GateResult:
    """Every citation must be well-formed and point at a module that exists.

    A DOI is only worth carrying if it is checkable, so this gate verifies the
    shape offline: prefix, non-empty fields, no duplicate identifiers, and that
    each ``cited_by`` names a real module.  It does *not* call Crossref - the
    gates must run without network.  The DOIs were checked against the Crossref
    REST API once, on the date recorded in ``references.CROSSREF_CHECKED``.
    """
    import importlib

    from .references import (
        CROSSREF_CHECKED,
        REFERENCES,
        all_references,
        bibliography,
        bibtex,
        without_doi,
    )
    from .taxonomy import CATEGORIES, EMOTIONS, LABEL_SET_SOURCES, SENTIMENTS, source_of

    result = GateResult("references", True)
    refs = all_references()
    checks: Dict[str, object] = {
        "count": len(refs),
        "crossref_checked": CROSSREF_CHECKED,
        "without_doi": [r.key for r in without_doi()],
    }

    if len(refs) < 20:
        result.passed = False
        result.messages.append(f"only {len(refs)} references registered")

    seen_ids: Dict[str, str] = {}
    for ref in refs:
        if not ref.authors or not all(ref.authors):
            result.passed = False
            result.messages.append(f"{ref.key}: empty author")
        if not ref.year.isdigit():
            result.passed = False
            result.messages.append(f"{ref.key}: year {ref.year!r} is not numeric")
        if not ref.title or not ref.venue:
            result.passed = False
            result.messages.append(f"{ref.key}: missing title or venue")
        if ref.doi and " " in ref.doi:
            result.passed = False
            result.messages.append(f"{ref.key}: DOI contains whitespace")
        if ref.identifier in seen_ids:
            result.passed = False
            result.messages.append(
                f"{ref.key} and {seen_ids[ref.identifier]} share identifier {ref.identifier}"
            )
        seen_ids[ref.identifier] = ref.key
        if not ref.link.startswith("http"):
            result.passed = False
            result.messages.append(f"{ref.key}: link {ref.link!r} is not a URL")

        for module in ref.cited_by:
            try:
                importlib.import_module(f"absa5.{module}")
            except Exception:  # noqa: BLE001
                result.passed = False
                result.messages.append(f"{ref.key} cites absa5.{module}, which fails to import")

    # A work without a DOI must say why, so the gap is a decision not an omission.
    for ref in without_doi():
        if "no DOI" not in ref.note:
            result.passed = False
            result.messages.append(
                f"{ref.key} has no DOI and does not explain why in its note"
            )

    # Every registered label set must name a source, or explicitly name none.
    registered = set(CATEGORIES.names()) | set(SENTIMENTS.names()) | set(EMOTIONS.names())
    unmapped = sorted(registered - set(LABEL_SET_SOURCES))
    checks["label_sets"] = len(registered)
    checks["unmapped_label_sets"] = unmapped
    if unmapped:
        result.passed = False
        result.messages.append(f"label sets with no source entry: {unmapped}")

    bad_source = []
    for name, key in LABEL_SET_SOURCES.items():
        if not key:
            continue
        try:
            REFERENCES.get(key)
        except KeyError:
            bad_source.append(f"{name} -> {key}")
    if bad_source:
        result.passed = False
        result.messages.append(f"label sets pointing at unknown references: {bad_source}")

    # Spot-check the resolution path used by the annotation guideline.
    emot_source = source_of("emot_id_netral")
    checks["emot_id_netral_source"] = emot_source.cite() if emot_source else None
    if emot_source is None or emot_source.doi != "10.1109/IALP.2018.8629262":
        result.passed = False
        result.messages.append("emot_id_netral does not resolve to the Saputri 2018 DOI")

    # Rendering must not raise on any entry.
    try:
        checks["bibliography_lines"] = len(bibliography().splitlines())
        checks["bibtex_entries"] = bibtex().count("@")
        checks["grouped_lines"] = len(bibliography(group_by_module=True).splitlines())
    except Exception as exc:  # noqa: BLE001
        result.passed = False
        result.messages.append(f"rendering failed: {type(exc).__name__}: {exc}")

    result.detail = checks
    if result.passed:
        result.messages.insert(
            0,
            f"{len(refs)} references well-formed, {len(refs) - len(without_doi())} with DOIs "
            f"(checked against Crossref {CROSSREF_CHECKED}), "
            f"{len(without_doi())} documented as having none",
        )
    return result


# -- runner ----------------------------------------------------------------
def run_gates(repo: str, *, only: Optional[Sequence[str]] = None) -> Tuple[bool, List[GateResult]]:
    names = list(only) if only else GATES.names()
    results = [GATES.get(name)(repo) for name in names]
    return all(r.passed for r in results), results


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="absa5 verification gates")
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--only", nargs="*", help="run only these gates")
    parser.add_argument("--json", dest="json_path", help="write full results here")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    repo = os.path.abspath(args.repo)
    sys.path.insert(0, os.path.join(repo, "Extract-Classify-ACOS"))

    passed, results = run_gates(repo, only=args.only)
    for r in results:
        print(r.line())
        for extra in r.messages[1:]:
            print(f"       {extra}")
        if args.verbose:
            print("       " + json.dumps(r.detail, ensure_ascii=False, default=str)[:2000])

    print()
    print(f"{sum(1 for r in results if r.passed)}/{len(results)} gates passed")
    if args.json_path:
        payload = {
            "passed": passed,
            "gates": [
                {"name": r.name, "passed": r.passed, "messages": r.messages, "detail": r.detail}
                for r in results
            ],
        }
        os.makedirs(os.path.dirname(os.path.abspath(args.json_path)) or ".", exist_ok=True)
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
        print(f"wrote {args.json_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
