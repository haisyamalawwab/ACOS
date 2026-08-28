"""Backbone adapters: prepare a checkpoint, then prove the weights actually loaded.

Two failure modes drove the design here, both verified against the repo:

1. The legacy loader at ``modeling.py:744-747`` only strips or adds the ``bert.``
   prefix when the target model has *no* ``self.bert`` attribute.  Every task
   model here does have one, so a checkpoint whose keys start at ``embeddings.*``
   (which is how ``indobenchmark/indobert-base-p1`` ships) lands entirely in
   ``missing_keys``.
2. The three logging blocks that would report ``missing_keys`` are commented out
   at ``modeling.py:748-753``.

Together those mean a mis-keyed checkpoint trains happily with a randomly
initialised encoder.  :func:`verify_encoder_weights` is the numeric gate that
makes that impossible to miss.
"""

from __future__ import annotations

import json
import os
import shutil
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .registry import Registry

WEIGHTS_NAME = "pytorch_model.bin"
SAFETENSORS_NAME = "model.safetensors"
CONFIG_NAME = "config.json"
VOCAB_NAME = "vocab.txt"

PROBE_KEYS = (
    "bert.embeddings.word_embeddings.weight",
    "bert.encoder.layer.0.attention.self.query.weight",
    "bert.encoder.layer.11.output.dense.weight",
)


class CheckpointError(RuntimeError):
    pass


@dataclass
class EncoderSpec:
    """Everything needed to fetch and normalise one backbone."""

    key: str
    model_name: str
    prefix: str = "bert."
    lowercase: bool = True
    files: Tuple[str, ...] = (CONFIG_NAME, WEIGHTS_NAME, VOCAB_NAME)
    notes: str = ""

    def describe(self) -> Dict[str, object]:
        return {
            "key": self.key,
            "model_name": self.model_name,
            "prefix": self.prefix,
            "lowercase": self.lowercase,
            "notes": self.notes,
        }


ENCODERS: Registry[EncoderSpec] = Registry("encoder")

ENCODERS.add(
    "indobert",
    EncoderSpec(
        key="indobert",
        model_name="indobenchmark/indobert-base-p1",
        notes=(
            "state_dict keys start at embeddings.*/encoder.*/pooler.* with no bert. prefix, "
            "and no cls.* MLM head; config.vocab_size 50000 while vocab.txt holds 30521 rows"
        ),
    ),
    "indobert_base",
    "indobert-base-p1",
)

ENCODERS.add(
    "indobert_large",
    EncoderSpec(key="indobert_large", model_name="indobenchmark/indobert-large-p1"),
    "indobert-large-p1",
)

ENCODERS.add(
    "bert",
    EncoderSpec(
        key="bert",
        model_name="bert-base-uncased",
        prefix="",
        notes="already carries the bert. prefix plus 14 cls.* keys",
    ),
    "bert_base",
    "bert-base-uncased",
)

ENCODERS.add(
    "nusabert",
    EncoderSpec(
        key="nusabert",
        model_name="LazarusNLP/NusaBERT-base",
        files=(CONFIG_NAME, SAFETENSORS_NAME, VOCAB_NAME),
        notes="safetensors only; needs conversion before the legacy torch.load path can read it",
    ),
    "nusabert_base",
)


@dataclass
class PrepareReport:
    """What :func:`prepare_checkpoint` did, kept for the run log."""

    model_name: str
    target_dir: str
    keys_before: int = 0
    keys_after: int = 0
    keys_reprefixed: int = 0
    dropped_keys: List[str] = field(default_factory=list)
    config_vocab_size: Optional[int] = None
    vocab_rows: Optional[int] = None
    hidden_size: Optional[int] = None
    num_layers: Optional[int] = None
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "model_name": self.model_name,
            "target_dir": self.target_dir,
            "keys_before": self.keys_before,
            "keys_after": self.keys_after,
            "keys_reprefixed": self.keys_reprefixed,
            "dropped_keys": self.dropped_keys,
            "config_vocab_size": self.config_vocab_size,
            "vocab_rows": self.vocab_rows,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "warnings": self.warnings,
        }


def rekey_state_dict(
    state_dict: Dict[str, object],
    *,
    prefix: str = "bert.",
    drop_prefixes: Sequence[str] = ("cls.", "mlm.", "predictions."),
) -> Tuple["OrderedDict[str, object]", int, List[str]]:
    """Give every encoder key the prefix the task model expects.

    Pure dict surgery, so it is testable without torch.
    """
    out: "OrderedDict[str, object]" = OrderedDict()
    changed = 0
    dropped: List[str] = []
    for key, value in state_dict.items():
        if any(key.startswith(p) for p in drop_prefixes):
            dropped.append(key)
            continue
        new_key = key if key.startswith(prefix) or not prefix else prefix + key
        if new_key != key:
            changed += 1
        out[new_key] = value
    return out, changed, dropped


def prepare_checkpoint(
    spec: str | EncoderSpec,
    target_dir: str,
    *,
    cache_dir: Optional[str] = None,
    force: bool = False,
    report_path: Optional[str] = None,
) -> PrepareReport:
    """Download a backbone and rewrite it into the layout the legacy loader wants."""
    import torch  # noqa: PLC0415 - optional dep

    spec = spec if isinstance(spec, EncoderSpec) else ENCODERS.get(spec)
    os.makedirs(target_dir, exist_ok=True)
    weights_out = os.path.join(target_dir, WEIGHTS_NAME)
    report = PrepareReport(model_name=spec.model_name, target_dir=target_dir)

    if os.path.exists(weights_out) and not force:
        report.warnings.append("target already prepared; pass force=True to rebuild")
        _fill_config_facts(report, target_dir)
        return report

    src = _resolve_source(spec, cache_dir=cache_dir)
    state_dict = _load_state_dict(src["weights"])
    report.keys_before = len(state_dict)

    remapped, changed, dropped = rekey_state_dict(state_dict, prefix=spec.prefix)
    report.keys_after = len(remapped)
    report.keys_reprefixed = changed
    report.dropped_keys = dropped

    torch.save(remapped, weights_out)
    shutil.copyfile(src["config"], os.path.join(target_dir, CONFIG_NAME))
    if src.get("vocab"):
        shutil.copyfile(src["vocab"], os.path.join(target_dir, VOCAB_NAME))

    _fill_config_facts(report, target_dir)
    if report.config_vocab_size and report.vocab_rows:
        if report.config_vocab_size != report.vocab_rows:
            report.warnings.append(
                f"config.vocab_size={report.config_vocab_size} but vocab.txt has "
                f"{report.vocab_rows} rows; the surplus embedding rows are unreachable"
            )
    if report.keys_after == 0:
        raise CheckpointError("re-keying produced an empty state_dict")

    if report_path:
        os.makedirs(os.path.dirname(os.path.abspath(report_path)) or ".", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report.as_dict(), fh, indent=2, ensure_ascii=False)
    return report


def _resolve_source(spec: EncoderSpec, *, cache_dir: Optional[str]) -> Dict[str, str]:
    """Locate config/weights/vocab, from a local dir or the HuggingFace hub."""
    if os.path.isdir(spec.model_name):
        base = spec.model_name
        weights = os.path.join(base, WEIGHTS_NAME)
        if not os.path.exists(weights):
            weights = os.path.join(base, SAFETENSORS_NAME)
        return {
            "config": os.path.join(base, CONFIG_NAME),
            "weights": weights,
            "vocab": os.path.join(base, VOCAB_NAME)
            if os.path.exists(os.path.join(base, VOCAB_NAME))
            else "",
        }

    from huggingface_hub import hf_hub_download  # noqa: PLC0415 - optional dep

    out: Dict[str, str] = {}
    out["config"] = hf_hub_download(spec.model_name, CONFIG_NAME, cache_dir=cache_dir)
    weight_file = next((f for f in spec.files if f in (WEIGHTS_NAME, SAFETENSORS_NAME)), WEIGHTS_NAME)
    try:
        out["weights"] = hf_hub_download(spec.model_name, weight_file, cache_dir=cache_dir)
    except Exception:  # noqa: BLE001 - fall back to the other serialisation
        other = SAFETENSORS_NAME if weight_file == WEIGHTS_NAME else WEIGHTS_NAME
        out["weights"] = hf_hub_download(spec.model_name, other, cache_dir=cache_dir)
    try:
        out["vocab"] = hf_hub_download(spec.model_name, VOCAB_NAME, cache_dir=cache_dir)
    except Exception:  # noqa: BLE001 - some checkpoints ship tokenizer.json only
        out["vocab"] = ""
    return out


def _load_state_dict(path: str) -> Dict[str, object]:
    if path.endswith(".safetensors"):
        from safetensors.torch import load_file  # noqa: PLC0415 - optional dep

        return dict(load_file(path))
    import torch  # noqa: PLC0415 - optional dep

    obj = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(obj, dict):
        raise CheckpointError(f"{path} does not contain a state_dict")
    return obj


def _fill_config_facts(report: PrepareReport, target_dir: str) -> None:
    cfg_path = os.path.join(target_dir, CONFIG_NAME)
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        report.config_vocab_size = cfg.get("vocab_size")
        report.hidden_size = cfg.get("hidden_size")
        report.num_layers = cfg.get("num_hidden_layers")
    vocab_path = os.path.join(target_dir, VOCAB_NAME)
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as fh:
            report.vocab_rows = sum(1 for line in fh if line.strip() != "" or True)


# -- the gate --------------------------------------------------------------
@dataclass
class WeightCheck:
    passed: bool
    checked: Dict[str, bool] = field(default_factory=dict)
    missing_encoder_keys: List[str] = field(default_factory=list)
    unexpected_keys: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "passed": self.passed,
            "checked": self.checked,
            "missing_encoder_keys": self.missing_encoder_keys[:20],
            "missing_encoder_key_count": len(self.missing_encoder_keys),
            "unexpected_keys": self.unexpected_keys[:20],
            "messages": self.messages,
        }

    def raise_for_status(self) -> "WeightCheck":
        if not self.passed:
            raise CheckpointError(
                "encoder weights did not load: " + "; ".join(self.messages)
            )
        return self


def verify_encoder_weights(
    model,
    checkpoint_dir: str,
    *,
    probe_keys: Sequence[str] = PROBE_KEYS,
    prefix: str = "bert.",
) -> WeightCheck:
    """Compare live parameters against the checkpoint on disk, element-wise.

    A structural key check is not enough: the legacy loader reports no error when
    it matches nothing, so the values themselves are compared.
    """
    import torch  # noqa: PLC0415 - optional dep

    check = WeightCheck(passed=True)
    disk = _load_state_dict(os.path.join(checkpoint_dir, WEIGHTS_NAME))
    live = dict(model.state_dict())

    encoder_keys = [k for k in disk if k.startswith(prefix)]
    if not encoder_keys:
        check.passed = False
        check.messages.append(
            f"checkpoint has no '{prefix}*' keys; it was never re-keyed "
            "(see absa5.encoders.rekey_state_dict)"
        )
        return check

    for key in encoder_keys:
        if key not in live:
            check.unexpected_keys.append(key)
    for key in live:
        if key.startswith(prefix) and key not in disk:
            check.missing_encoder_keys.append(key)
    if check.missing_encoder_keys:
        check.passed = False
        check.messages.append(
            f"{len(check.missing_encoder_keys)} encoder parameters are absent from the "
            f"checkpoint, so they stayed randomly initialised "
            f"(first: {check.missing_encoder_keys[0]})"
        )

    probes = [k for k in probe_keys if k in disk and k in live]
    if not probes:
        check.passed = False
        check.messages.append(
            f"none of the probe keys {list(probe_keys)} exist in both checkpoint and model"
        )
    for key in probes:
        same = bool(torch.allclose(live[key].float().cpu(), disk[key].float().cpu()))
        check.checked[key] = same
        if not same:
            check.passed = False
            check.messages.append(f"{key} differs from the checkpoint")
    if check.passed:
        check.messages.append(
            f"{len(probes)} probe tensors match and every '{prefix}*' parameter was found"
        )
    return check


def load_backbone(config_or_dir, **kwargs):
    """Instantiate a ``BertModel`` from a prepared directory (used by the models layer)."""
    from modeling import BertConfig, BertModel  # noqa: PLC0415 - optional dep

    if isinstance(config_or_dir, str):
        cfg = BertConfig.from_json_file(os.path.join(config_or_dir, CONFIG_NAME))
    else:
        cfg = config_or_dir
    return BertModel(cfg, **kwargs)


BACKBONE_LOADERS: Registry[Callable] = Registry("backbone loader")
BACKBONE_LOADERS.add("legacy_bert", load_backbone, "bert", "indobert")
