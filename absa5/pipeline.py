"""End-to-end orchestration: prepare data, train both stages, score, report.

Data preparation is torch-free and runs anywhere; the training steps import torch
lazily.  Both halves are separately callable so the data gates can be cleared on
a laptop before anything is scheduled on a GPU.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .config import RunConfig
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
from .features import build_encoders
from .schema import get_schema
from .taxonomy import LabelSpaceSet

SPLITS = ("train", "dev", "test")


@dataclass
class DataArtifacts:
    """Where prepared files landed, plus the numbers worth reading before training."""

    work_dir: str
    tokenized: Dict[str, str] = field(default_factory=dict)
    pairs: Dict[str, str] = field(default_factory=dict)
    reports: Dict[str, object] = field(default_factory=dict)
    label_report: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "work_dir": self.work_dir,
            "tokenized": self.tokenized,
            "pairs": self.pairs,
            "reports": self.reports,
            "label_report": self.label_report,
        }


def raw_path(cfg: RunConfig, split: str) -> str:
    """Locate the raw file for a split, tolerating the upstream naming variants."""
    schema = get_schema(cfg.data.schema)
    domain = cfg.data.domain
    candidates = [
        os.path.join(cfg.data.raw_dir, f"{domain}_{schema.name}_{split}.tsv"),
        os.path.join(cfg.data.raw_dir, f"{domain}_quad_{split}.tsv"),
        os.path.join(cfg.data.raw_dir, "Restaurant-ACOS", f"{domain}_quad_{split}.tsv"),
        os.path.join(cfg.data.raw_dir, "Laptop-ACOS", f"{domain}_quad_{split}.tsv"),
        os.path.join(cfg.data.raw_dir, domain, f"{domain}_{schema.name}_{split}.tsv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"no raw file for split '{split}'; looked for:\n  " + "\n  ".join(candidates)
    )


def prepare_data(
    cfg: RunConfig,
    *,
    splits: Sequence[str] = SPLITS,
    tokenizer=None,
    strict: bool = True,
) -> DataArtifacts:
    """Retokenize, remap spans, and build pair files for each split."""
    schema = get_schema(cfg.data.schema)
    spaces = cfg.label_spaces()
    tokenizer = tokenizer or cfg.tokenizer.build()
    work = os.path.join(cfg.data.work_dir, cfg.name)
    os.makedirs(work, exist_ok=True)
    artifacts = DataArtifacts(work_dir=work)

    all_label_values: List[Dict[str, str]] = []
    for split in splits:
        src = raw_path(cfg, split)
        tokenized = os.path.join(work, f"{cfg.data.domain}_{split}_{schema.name}.tsv")
        report = convert_file(
            tokenizer,
            src,
            tokenized,
            schema,
            subword_limit=cfg.data.subword_limit,
            report_path=os.path.join(work, f"_build_{split}.json"),
            strict=strict,
            max_unk_ratio=cfg.data.max_unk_ratio,
        )
        artifacts.tokenized[split] = tokenized
        artifacts.reports[split] = report

        records = read_records(tokenized, schema)
        all_label_values.extend(v for r in records for v in r.label_values())
        pair_path = os.path.join(work, f"{cfg.data.domain}_{split}_pair.tsv")
        artifacts.pairs[split] = pair_path
        artifacts.reports[f"{split}_pairs"] = build_pair_files(
            records, schema, spaces, pair_path, source=tokenized
        )

    artifacts.label_report = spaces.report(all_label_values)
    with open(os.path.join(work, "_prepare.json"), "w", encoding="utf-8") as fh:
        json.dump(artifacts.as_dict(), fh, indent=2, ensure_ascii=False)
    return artifacts


def load_prepared(
    cfg: RunConfig, artifacts: DataArtifacts, split: str
) -> Tuple[List[Record], List[PairExample]]:
    schema = get_schema(cfg.data.schema)
    records = read_records(artifacts.tokenized[split], schema)
    pairs = read_pairs(artifacts.pairs[split], n_spans=len(schema.spans))
    return records, pairs


@dataclass
class RunResult:
    config: Dict[str, object]
    data: Dict[str, object]
    extraction: Dict[str, object] = field(default_factory=dict)
    classification: Dict[str, object] = field(default_factory=dict)
    end_to_end: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "config": self.config,
            "data": self.data,
            "extraction": self.extraction,
            "classification": self.classification,
            "end_to_end": self.end_to_end,
        }

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.as_dict(), fh, indent=2, ensure_ascii=False)
        return path


def run(
    cfg: RunConfig,
    *,
    checkpoint_dir: Optional[str] = None,
    prepare: bool = True,
    artifacts: Optional[DataArtifacts] = None,
    stages: Sequence[str] = ("extraction", "classification", "end_to_end"),
    verify_weights: bool = True,
) -> RunResult:
    """Full pipeline.  Requires torch; call :func:`prepare_data` alone if you lack it."""
    from .encoders import prepare_checkpoint  # noqa: PLC0415
    from .engine import (  # noqa: PLC0415
        evaluate_end_to_end,
        predict_labels,
        predict_spans,
        train_classification,
        train_extraction,
    )
    from .models import (  # noqa: PLC0415
        build_classification_model,
        build_extraction_model,
        head_size_report,
    )

    schema = get_schema(cfg.data.schema)
    spaces = cfg.label_spaces()
    tokenizer = cfg.tokenizer.build()

    if artifacts is None:
        artifacts = prepare_data(cfg, tokenizer=tokenizer) if prepare else DataArtifacts(
            work_dir=os.path.join(cfg.data.work_dir, cfg.name)
        )

    ckpt = checkpoint_dir or cfg.encoder.local_dir
    if not ckpt:
        ckpt = os.path.join(cfg.output_dir, "backbone")
        prepare_checkpoint(cfg.encoder.kind, ckpt, report_path=os.path.join(ckpt, "_prepare.json"))

    extraction_encoder, classification_encoder = build_encoders(
        tokenizer, schema, spaces, max_seq_length=cfg.data.max_seq_length,
        tagging=cfg.data.tagging,
    )

    result = RunResult(
        config=cfg.summary(),
        data=artifacts.as_dict(),
    )
    result.config["head_sizes"] = head_size_report(cfg, spaces)

    train_records, _ = load_prepared(cfg, artifacts, "train")
    dev_records, dev_pairs = load_prepared(cfg, artifacts, "dev")
    test_records, test_pairs = load_prepared(cfg, artifacts, "test")

    extraction_model = None
    if "extraction" in stages:
        extraction_model, info = build_extraction_model(
            cfg, extraction_encoder, checkpoint_dir=ckpt, verify=verify_weights
        )
        outcome = train_extraction(
            extraction_model,
            cfg,
            extraction_encoder.encode_all(train_records),
            extraction_encoder.encode_all(dev_records),
            extraction_encoder,
        )
        result.extraction = {"load": info, "train": outcome.as_dict()}

    classification_model = None
    if "classification" in stages:
        _, train_pairs = load_prepared(cfg, artifacts, "train")
        classification_model, info = build_classification_model(
            cfg, classification_encoder, checkpoint_dir=ckpt, verify=verify_weights
        )
        outcome = train_classification(
            classification_model,
            cfg,
            classification_encoder.encode_all(train_pairs),
            classification_encoder.encode_all(dev_pairs),
            classification_encoder,
            spaces,
        )
        result.classification = {"load": info, "train": outcome.as_dict()}

    if "end_to_end" in stages and extraction_model and classification_model:
        span_preds = predict_spans(
            extraction_model, extraction_encoder.encode_all(test_records), extraction_encoder, cfg
        )
        candidates = _pairs_from_span_predictions(span_preds, schema.spans)
        label_sets = predict_labels(
            classification_model, classification_encoder.encode_all(candidates), spaces, cfg
        )
        evaluation = evaluate_end_to_end(candidates, label_sets, test_records, schema)
        result.end_to_end = {
            "candidate_pairs": len(candidates),
            "metrics": evaluation.as_dict(),
            "table": evaluation.table(),
        }
        pipeline_path = os.path.join(cfg.output_dir, "test_candidates.tsv")
        write_pairs(pipeline_path, candidates)
        result.end_to_end["candidates_file"] = pipeline_path

    result.save(os.path.join(cfg.output_dir, "run_result.json"))
    return result


def _pairs_from_span_predictions(
    span_preds: Sequence[Dict[str, object]],
    span_elements: Sequence[str],
) -> List[PairExample]:
    from .data import cross_product_pairs  # noqa: PLC0415

    out: List[PairExample] = []
    for pred in span_preds:
        spans = pred["spans"]  # type: ignore[index]
        groups = [list(spans.get(name) or [(-1, -1)]) for name in span_elements]
        out.extend(cross_product_pairs(str(pred["text"]), groups))
    return out


def summarize_run(result: RunResult) -> str:
    """Human-readable digest of one run, for pasting into a report."""
    lines = [f"run: {result.config.get('name')}", f"schema: {result.config.get('schema')}"]
    sizes = result.config.get("label_sizes") or {}
    if sizes:
        lines.append(
            "label spaces: "
            + ", ".join(f"{k}={v}" for k, v in sizes.items())
            + f" (mode {result.config.get('label_mode')})"
        )
    label_report = (result.data.get("label_report") or {}) if result.data else {}
    if label_report.get("joint_coverage") is not None:
        lines.append(
            f"joint space: {label_report['joint_cells_seen']}/{label_report['joint_size']} cells "
            f"observed ({label_report['joint_coverage']:.1%}), "
            f"{label_report.get('joint_cells_below_10', 0)} with fewer than 10 examples"
        )
    if result.extraction.get("train"):
        lines.append(
            f"extraction: best span F1 {result.extraction['train']['best_metric']:.2%} "
            f"at epoch {result.extraction['train']['best_epoch']}"
        )
    if result.classification.get("train"):
        lines.append(
            f"classification: best label F1 {result.classification['train']['best_metric']:.2%} "
            f"at epoch {result.classification['train']['best_epoch']}"
        )
    if result.end_to_end.get("table"):
        lines.append("end-to-end:")
        lines.append(str(result.end_to_end["table"]))
    return "\n".join(lines)
