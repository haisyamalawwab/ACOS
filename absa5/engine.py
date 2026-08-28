"""Training and inference loops for the two stages.

Torch-dependent, imported lazily.  The loops are thin on purpose: batching,
optimiser setup, and checkpoint selection live here, while every decision that
affects results (schema, label space, head type) comes in through the config.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .config import RunConfig
from .data import PairExample, Record
from .decode import (
    collect_predictions,
    decode_label_logits,
    decode_spans,
    gold_by_text,
)
from .features import (
    ClassificationEncoder,
    ClassificationFeature,
    ExtractionEncoder,
    ExtractionFeature,
)
from .metrics import EvalResult, evaluate, multiset_prf
from .schema import get_schema
from .taxonomy import FACTORED, LabelSpaceSet


def set_seed(seed: int) -> None:
    import torch  # noqa: PLC0415 - optional dep

    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    try:
        import numpy as np  # noqa: PLC0415 - optional dep

        np.random.seed(seed)
    except ImportError:
        pass


def resolve_device(spec: str = "auto"):
    import torch  # noqa: PLC0415 - optional dep

    if spec != "auto":
        return torch.device(spec)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_optimizer(model, cfg: RunConfig, total_steps: int):
    """AdamW with the upstream no-decay list; falls back to legacy BertAdam."""
    no_decay = ("bias", "LayerNorm.bias", "LayerNorm.weight")
    params = list(model.named_parameters())
    groups = [
        {
            "params": [p for n, p in params if not any(nd in n for nd in no_decay)],
            "weight_decay": cfg.train.weight_decay,
        },
        {
            "params": [p for n, p in params if any(nd in n for nd in no_decay)],
            "weight_decay": 0.0,
        },
    ]
    try:
        import torch  # noqa: PLC0415 - optional dep
        from torch.optim import AdamW  # noqa: PLC0415 - optional dep

        optimizer = AdamW(groups, lr=cfg.train.learning_rate)
        warmup = max(int(total_steps * cfg.train.warmup_proportion), 1)

        def lr_lambda(step: int) -> float:
            if step < warmup:
                return step / warmup
            remaining = max(total_steps - warmup, 1)
            return max(0.0, (total_steps - step) / remaining)

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
        return optimizer, scheduler
    except ImportError:
        from bert_utils.optimization import BertAdam  # noqa: PLC0415 - optional dep

        optimizer = BertAdam(
            groups,
            lr=cfg.train.learning_rate,
            warmup=cfg.train.warmup_proportion,
            t_total=total_steps,
        )
        return optimizer, None


# -- batching --------------------------------------------------------------
def extraction_batches(
    features: Sequence[ExtractionFeature],
    span_elements: Sequence[str],
    batch_size: int,
    *,
    shuffle: bool = False,
    device=None,
):
    import torch  # noqa: PLC0415 - optional dep

    order = list(range(len(features)))
    if shuffle:
        random.shuffle(order)
    for start in range(0, len(order), batch_size):
        chunk = [features[i] for i in order[start : start + batch_size]]
        batch = {
            "input_ids": torch.tensor([f.input_ids for f in chunk], dtype=torch.long),
            "attention_mask": torch.tensor([f.input_mask for f in chunk], dtype=torch.long),
            "token_type_ids": torch.tensor([f.segment_ids for f in chunk], dtype=torch.long),
            "tag_ids": torch.tensor([f.tag_ids for f in chunk], dtype=torch.long),
            "implicit_targets": {
                name: torch.tensor(
                    [f.implicit_flags.get(name, 0) for f in chunk], dtype=torch.long
                )
                for name in span_elements
            },
        }
        if device is not None:
            batch = _to_device(batch, device)
        yield batch, chunk


def classification_batches(
    features: Sequence[ClassificationFeature],
    span_elements: Sequence[str],
    label_elements: Sequence[str],
    batch_size: int,
    *,
    mode: str = FACTORED,
    shuffle: bool = False,
    device=None,
):
    import torch  # noqa: PLC0415 - optional dep

    order = list(range(len(features)))
    if shuffle:
        random.shuffle(order)
    for start in range(0, len(order), batch_size):
        chunk = [features[i] for i in order[start : start + batch_size]]
        targets: Dict[str, object] = {}
        if mode == FACTORED:
            for name in label_elements:
                targets[name] = torch.tensor(
                    [f.factored_labels[name] for f in chunk], dtype=torch.long
                )
        else:
            targets["joint"] = torch.tensor([f.joint_label for f in chunk], dtype=torch.long)
        batch = {
            "input_ids": torch.tensor([f.input_ids for f in chunk], dtype=torch.long),
            "attention_mask": torch.tensor([f.input_mask for f in chunk], dtype=torch.long),
            "token_type_ids": torch.tensor([f.segment_ids for f in chunk], dtype=torch.long),
            "span_masks": {
                name: torch.tensor([f.span_masks[name] for f in chunk], dtype=torch.long)
                for name in span_elements
            },
            "targets": targets,
        }
        if device is not None:
            batch = _to_device(batch, device)
        yield batch, chunk


def _to_device(obj, device):
    if isinstance(obj, dict):
        return {k: _to_device(v, device) for k, v in obj.items()}
    if hasattr(obj, "to"):
        return obj.to(device)
    return obj


# -- training --------------------------------------------------------------
@dataclass
class TrainOutcome:
    stage: str
    best_metric: float = -1.0
    best_epoch: int = -1
    history: List[Dict[str, object]] = field(default_factory=list)
    checkpoint: str = ""

    def as_dict(self) -> Dict[str, object]:
        return {
            "stage": self.stage,
            "best_metric": self.best_metric,
            "best_epoch": self.best_epoch,
            "checkpoint": self.checkpoint,
            "history": self.history,
        }


def train_extraction(
    model,
    cfg: RunConfig,
    train_features: Sequence[ExtractionFeature],
    dev_features: Sequence[ExtractionFeature],
    encoder: ExtractionEncoder,
    *,
    output_dir: Optional[str] = None,
    device=None,
) -> TrainOutcome:
    import torch  # noqa: PLC0415 - optional dep

    schema = get_schema(cfg.data.schema)
    device = device or resolve_device(cfg.train.device)
    out_dir = output_dir or os.path.join(cfg.output_dir, "extraction")
    os.makedirs(out_dir, exist_ok=True)
    set_seed(cfg.train.seed)
    model.to(device)

    steps_per_epoch = max(
        1,
        -(-len(train_features) // cfg.train.train_batch_size)
        // max(cfg.train.gradient_accumulation_steps, 1),
    )
    optimizer, scheduler = build_optimizer(model, cfg, steps_per_epoch * cfg.train.epochs)
    outcome = TrainOutcome(stage="extraction")

    for epoch in range(int(cfg.train.epochs)):
        model.train()
        total_loss = 0.0
        n_batches = 0
        optimizer.zero_grad()
        for step, (batch, _) in enumerate(
            extraction_batches(
                train_features,
                schema.spans,
                cfg.train.train_batch_size,
                shuffle=True,
                device=device,
            )
        ):
            out = model(**batch)
            loss = out["loss"] / max(cfg.train.gradient_accumulation_steps, 1)
            loss.backward()
            total_loss += float(out["loss"].detach())
            n_batches += 1
            if (step + 1) % max(cfg.train.gradient_accumulation_steps, 1) == 0:
                if cfg.train.max_grad_norm:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.train.max_grad_norm)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad()

        dev = evaluate_extraction(model, dev_features, encoder, cfg, device=device)
        record = {
            "epoch": epoch,
            "train_loss": total_loss / max(n_batches, 1),
            "dev_span_f1": dev["span_f1"],
            "dev_implicit": dev["implicit_accuracy"],
        }
        outcome.history.append(record)

        if dev["span_f1"] > outcome.best_metric:
            outcome.best_metric = dev["span_f1"]
            outcome.best_epoch = epoch
            outcome.checkpoint = os.path.join(out_dir, "pytorch_model.bin")
            torch.save(model.state_dict(), outcome.checkpoint)
            model.config.to_json_file(os.path.join(out_dir, "config.json"))

    with open(os.path.join(out_dir, "train_log.json"), "w", encoding="utf-8") as fh:
        json.dump(outcome.as_dict(), fh, indent=2)
    return outcome


def train_classification(
    model,
    cfg: RunConfig,
    train_features: Sequence[ClassificationFeature],
    dev_features: Sequence[ClassificationFeature],
    encoder: ClassificationEncoder,
    spaces: LabelSpaceSet,
    *,
    output_dir: Optional[str] = None,
    device=None,
) -> TrainOutcome:
    import torch  # noqa: PLC0415 - optional dep

    schema = get_schema(cfg.data.schema)
    device = device or resolve_device(cfg.train.device)
    out_dir = output_dir or os.path.join(cfg.output_dir, "classification")
    os.makedirs(out_dir, exist_ok=True)
    set_seed(cfg.train.seed)
    model.to(device)

    steps_per_epoch = max(
        1,
        -(-len(train_features) // cfg.train.train_batch_size)
        // max(cfg.train.gradient_accumulation_steps, 1),
    )
    optimizer, scheduler = build_optimizer(model, cfg, steps_per_epoch * cfg.train.epochs)
    outcome = TrainOutcome(stage="classification")

    for epoch in range(int(cfg.train.epochs)):
        model.train()
        total_loss = 0.0
        n_batches = 0
        optimizer.zero_grad()
        for step, (batch, _) in enumerate(
            classification_batches(
                train_features,
                schema.spans,
                spaces.elements,
                cfg.train.train_batch_size,
                mode=cfg.heads.label_mode,
                shuffle=True,
                device=device,
            )
        ):
            out = model(**batch)
            loss = out["loss"] / max(cfg.train.gradient_accumulation_steps, 1)
            loss.backward()
            total_loss += float(out["loss"].detach())
            n_batches += 1
            if (step + 1) % max(cfg.train.gradient_accumulation_steps, 1) == 0:
                if cfg.train.max_grad_norm:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.train.max_grad_norm)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad()

        dev = evaluate_classification_labels(
            model, dev_features, spaces, cfg, schema, device=device
        )
        record = {
            "epoch": epoch,
            "train_loss": total_loss / max(n_batches, 1),
            "dev_label_f1": dev["label_f1"],
            "dev_per_element_f1": dev["per_element_f1"],
        }
        outcome.history.append(record)

        if dev["label_f1"] > outcome.best_metric:
            outcome.best_metric = dev["label_f1"]
            outcome.best_epoch = epoch
            outcome.checkpoint = os.path.join(out_dir, "pytorch_model.bin")
            torch.save(model.state_dict(), outcome.checkpoint)
            model.config.to_json_file(os.path.join(out_dir, "config.json"))

    with open(os.path.join(out_dir, "train_log.json"), "w", encoding="utf-8") as fh:
        json.dump(outcome.as_dict(), fh, indent=2)
    return outcome


# -- inference -------------------------------------------------------------
def predict_spans(
    model,
    features: Sequence[ExtractionFeature],
    encoder: ExtractionEncoder,
    cfg: RunConfig,
    *,
    device=None,
) -> List[Dict[str, object]]:
    import torch  # noqa: PLC0415 - optional dep

    schema = get_schema(cfg.data.schema)
    device = device or resolve_device(cfg.train.device)
    model.to(device)
    model.eval()
    out: List[Dict[str, object]] = []

    with torch.no_grad():
        for batch, chunk in extraction_batches(
            features, schema.spans, cfg.train.eval_batch_size, device=device
        ):
            result = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                token_type_ids=batch["token_type_ids"],
            )
            implicit = {
                name: logits.argmax(-1).tolist()
                for name, logits in result["implicit_logits"].items()
            }
            for i, feature in enumerate(chunk):
                flags = {name: implicit[name][i] for name in schema.spans}
                spans = decode_spans(
                    result["tags"][i],
                    encoder.tagging,
                    implicit_flags=flags,
                    max_index=feature.tokens_len - 2,
                )
                out.append(
                    {
                        "guid": feature.guid,
                        "text": " ".join(feature.tokens[1:-1]),
                        "spans": spans,
                        "implicit": flags,
                    }
                )
    return out


def evaluate_extraction(
    model,
    features: Sequence[ExtractionFeature],
    encoder: ExtractionEncoder,
    cfg: RunConfig,
    *,
    device=None,
) -> Dict[str, object]:
    """Span-level micro F1 plus implicit-flag accuracy, per span element."""
    schema = get_schema(cfg.data.schema)
    preds = predict_spans(model, features, encoder, cfg, device=device)

    span_prf = {name: multiset_prf([], []) for name in schema.spans}
    implicit_correct = {name: 0 for name in schema.spans}
    for feature, pred in zip(features, preds):
        gold_tags = [
            encoder.tagging.tag_list()[t] for t in feature.tag_ids[: feature.tokens_len]
        ]
        gold_spans = encoder.tagging.decode(gold_tags)
        for name in schema.spans:
            g = [(s - 1, e - 1) for s, e in gold_spans.get(name, []) if e - 1 > s - 1]
            p = [x for x in pred["spans"].get(name, []) if x != (-1, -1)]
            span_prf[name] += multiset_prf(p, g)
            if pred["implicit"].get(name, 0) == feature.implicit_flags.get(name, 0):
                implicit_correct[name] += 1

    total = PRF_sum(span_prf.values())
    return {
        "span_f1": total.f1,
        "span_precision": total.precision,
        "span_recall": total.recall,
        "per_element": {n: v.as_dict() for n, v in span_prf.items()},
        "implicit_accuracy": {
            n: implicit_correct[n] / max(len(features), 1) for n in schema.spans
        },
    }


def PRF_sum(items):
    from .metrics import PRF

    total = PRF()
    for item in items:
        total += item
    return total


def predict_labels(
    model,
    features: Sequence[ClassificationFeature],
    spaces: LabelSpaceSet,
    cfg: RunConfig,
    *,
    device=None,
    threshold: float = 0.0,
) -> List[List[Dict[str, str]]]:
    import torch  # noqa: PLC0415 - optional dep

    schema = get_schema(cfg.data.schema)
    device = device or resolve_device(cfg.train.device)
    model.to(device)
    model.eval()
    out: List[List[Dict[str, str]]] = []

    with torch.no_grad():
        for batch, chunk in classification_batches(
            features,
            schema.spans,
            spaces.elements,
            cfg.train.eval_batch_size,
            mode=cfg.heads.label_mode,
            device=device,
        ):
            result = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                token_type_ids=batch["token_type_ids"],
                span_masks=batch["span_masks"],
            )
            logits = {k: v.detach().cpu().tolist() for k, v in result["logits"].items()}
            for i in range(len(chunk)):
                row = {k: v[i] for k, v in logits.items()}
                out.append(
                    decode_label_logits(
                        row, spaces, mode=cfg.heads.label_mode, threshold=threshold
                    )
                )
    return out


def evaluate_classification_labels(
    model,
    features: Sequence[ClassificationFeature],
    spaces: LabelSpaceSet,
    cfg: RunConfig,
    schema,
    *,
    device=None,
) -> Dict[str, object]:
    """Label-only score with gold spans: isolates classification from extraction."""
    from .metrics import PRF, multiset_prf

    preds = predict_labels(model, features, spaces, cfg, device=device)
    joint = PRF()
    per_element = {n: PRF() for n in spaces.elements}

    for feature, pred_sets in zip(features, preds):
        gold_sets: List[Dict[str, str]] = []
        for element in spaces.elements:
            labels = spaces.space(element).labels
            hot = [labels[i] for i, v in enumerate(feature.factored_labels[element]) if v]
            if not gold_sets:
                gold_sets = [{element: h} for h in hot] or [{}]
            else:
                gold_sets = [{**g, element: h} for g in gold_sets for h in hot] or gold_sets

        joint += multiset_prf(
            [spaces.join(p) for p in pred_sets if set(p) == set(spaces.elements)],
            [spaces.join(g) for g in gold_sets if set(g) == set(spaces.elements)],
        )
        for element in spaces.elements:
            per_element[element] += multiset_prf(
                sorted({p[element] for p in pred_sets if element in p}),
                sorted({g[element] for g in gold_sets if element in g}),
            )

    return {
        "label_f1": joint.f1,
        "label_precision": joint.precision,
        "label_recall": joint.recall,
        "per_element_f1": {n: v.f1 for n, v in per_element.items()},
        "per_element": {n: v.as_dict() for n, v in per_element.items()},
    }


def evaluate_end_to_end(
    pairs: Sequence[PairExample],
    label_sets: Sequence[Sequence[Dict[str, str]]],
    gold_records: Sequence[Record],
    schema,
    *,
    max_subset_size: Optional[int] = 2,
) -> EvalResult:
    """Score the assembled pipeline output against gold tuples."""
    schema = get_schema(schema)
    pred = collect_predictions(pairs, label_sets, schema)
    gold = gold_by_text(gold_records, schema)
    return evaluate(pred, gold, schema, max_subset_size=max_subset_size)
