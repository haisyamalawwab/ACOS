"""Run configuration: one dataclass tree that fully determines a run.

Every pluggable choice is a *name* resolved through a registry at build time,
so a config round-trips through JSON and an experiment is reproducible from the
file alone.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any, Dict, List, Optional

from .schema import get_schema
from .taxonomy import FACTORED, JOINT, LabelSpaceSet, build_label_spaces


@dataclass
class TokenizerConfig:
    kind: str = "wordpiece"
    path: str = ""
    do_lower_case: bool = True
    options: Dict[str, Any] = field(default_factory=dict)

    def build(self):
        from .tokenizers import build_tokenizer

        kwargs = dict(self.options)
        kwargs.setdefault("do_lower_case", self.do_lower_case)
        if self.kind in ("whitespace", "identity"):
            return build_tokenizer(self.kind, **kwargs)
        if not self.path:
            raise ValueError(f"tokenizer '{self.kind}' needs a path or model name")
        return build_tokenizer(self.kind, self.path, **kwargs)


@dataclass
class EncoderConfig:
    """Backbone selection.  ``kind`` names an entry in :data:`absa5.models.ENCODERS`."""

    kind: str = "indobert"
    model_name_or_path: str = "indobenchmark/indobert-base-p1"
    local_dir: str = ""
    hidden_size: int = 768
    freeze: bool = False
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HeadConfig:
    """Head selection for both stages."""

    span_head: str = "crf"
    implicit_head: str = "linear"
    label_mode: str = FACTORED
    label_head: str = "span_pool"
    dropout: float = 0.1
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.label_mode not in (JOINT, FACTORED):
            raise ValueError(f"label_mode must be '{JOINT}' or '{FACTORED}'")


@dataclass
class DataConfig:
    raw_dir: str = "data"
    work_dir: str = "work"
    domain: str = "rest16"
    schema: str = "quint"
    category_set: str = "rest16"
    sentiment_set: str = "acos"
    emotion_set: str = "emot"
    max_seq_length: int = 128
    tagging: str = "bio"
    subword_limit: Optional[int] = 126
    max_unk_ratio: Optional[float] = 0.05

    def label_spaces(self) -> LabelSpaceSet:
        schema = get_schema(self.schema)
        kwargs: Dict[str, str] = {}
        if "category" in schema.labels:
            kwargs["category"] = self.category_set
        if "sentiment" in schema.labels:
            kwargs["sentiment"] = self.sentiment_set
        if "emotion" in schema.labels:
            kwargs["emotion"] = self.emotion_set
        return build_label_spaces(schema, **kwargs)


@dataclass
class TrainConfig:
    stage: str = "extraction"
    epochs: int = 30
    train_batch_size: int = 24
    eval_batch_size: int = 8
    learning_rate: float = 2e-5
    warmup_proportion: float = 0.1
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    seed: int = 13
    fp16: bool = False
    device: str = "auto"
    select_metric: str = "f1"
    loss_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class RunConfig:
    name: str = "indobert_quint_rest16"
    output_dir: str = "output/indobert_quint"
    data: DataConfig = field(default_factory=DataConfig)
    tokenizer: TokenizerConfig = field(default_factory=TokenizerConfig)
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    heads: HeadConfig = field(default_factory=HeadConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    notes: str = ""

    # -- (de)serialisation -------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)
        return path

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunConfig":
        return _from_dict(cls, data)

    @classmethod
    def from_json(cls, path: str) -> "RunConfig":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))

    def merged(self, **overrides: Any) -> "RunConfig":
        """Shallow-merge dotted overrides, e.g. ``merged(**{'train.epochs': 3})``."""
        data = self.to_dict()
        for dotted, value in overrides.items():
            node = data
            parts = dotted.split(".")
            for part in parts[:-1]:
                if part not in node:
                    raise KeyError(f"unknown config section '{part}' in '{dotted}'")
                node = node[part]
            if parts[-1] not in node:
                raise KeyError(f"unknown config key '{dotted}'")
            node[parts[-1]] = value
        return RunConfig.from_dict(data)

    # -- derived -----------------------------------------------------------
    def label_spaces(self) -> LabelSpaceSet:
        return self.data.label_spaces()

    def summary(self) -> Dict[str, Any]:
        schema = get_schema(self.data.schema)
        spaces = self.label_spaces()
        return {
            "name": self.name,
            "schema": schema.name,
            "arity": schema.arity,
            "elements": list(schema.names),
            "spans": list(schema.spans),
            "labels": list(schema.labels),
            "label_sizes": spaces.sizes(),
            "label_mode": self.heads.label_mode,
            "head_sizes": spaces.head_sizes(self.heads.label_mode),
            "encoder": self.encoder.model_name_or_path,
            "tokenizer": self.tokenizer.kind,
        }


def _from_dict(cls, data: Any):
    if not is_dataclass(cls):
        return data
    kwargs = {}
    for f in fields(cls):
        if f.name not in data:
            continue
        value = data[f.name]
        if is_dataclass(f.type) and isinstance(value, dict):
            kwargs[f.name] = _from_dict(f.type, value)
        elif isinstance(value, dict) and f.name in _SECTION_TYPES and isinstance(value, dict):
            kwargs[f.name] = _from_dict(_SECTION_TYPES[f.name], value)
        else:
            kwargs[f.name] = value
    return cls(**kwargs)


_SECTION_TYPES = {
    "data": DataConfig,
    "tokenizer": TokenizerConfig,
    "encoder": EncoderConfig,
    "heads": HeadConfig,
    "train": TrainConfig,
}


# -- presets ---------------------------------------------------------------
PRESETS: Dict[str, Dict[str, Any]] = {
    "quad_bert_en": {
        "name": "bert_quad_rest16",
        "data": {"schema": "quad", "domain": "rest16", "category_set": "rest16"},
        "encoder": {"kind": "bert", "model_name_or_path": "bert-base-uncased"},
        "heads": {"label_mode": JOINT},
    },
    "quint_indobert_id": {
        "name": "indobert_quint_resto",
        "data": {
            "schema": "quint",
            "domain": "resto_id",
            "category_set": "resto_id",
            "emotion_set": "emot_id",
        },
        "encoder": {"kind": "indobert", "model_name_or_path": "indobenchmark/indobert-base-p1"},
        "heads": {"label_mode": FACTORED},
    },
    "quint_dryrun_en": {
        "name": "dryrun_quint_rest16",
        "data": {"schema": "quint", "domain": "rest16", "category_set": "rest16"},
        "encoder": {"kind": "bert", "model_name_or_path": "bert-base-uncased"},
        "heads": {"label_mode": FACTORED},
        "train": {"epochs": 1, "train_batch_size": 8},
    },
}


def preset(preset_name: str, /, **overrides: Any) -> RunConfig:
    """Build a config from a preset, then apply dotted overrides.

    ``preset_name`` is positional-only so an override targeting the config's own
    ``name`` field does not collide with it.
    """
    if preset_name not in PRESETS:
        raise KeyError(
            f"unknown preset '{preset_name}'. available: {', '.join(sorted(PRESETS))}"
        )
    cfg = RunConfig.from_dict(_deep_merge(RunConfig().to_dict(), PRESETS[preset_name]))
    return cfg.merged(**overrides) if overrides else cfg


def _deep_merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def list_presets() -> List[str]:
    return sorted(PRESETS)
