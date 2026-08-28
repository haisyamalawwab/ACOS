"""Stage models: encoder plus heads, assembled from a :class:`~absa5.config.RunConfig`.

Torch is imported lazily, so importing this module on a machine without torch is
fine as long as you only inspect it.  Call :func:`build_extraction_model` or
:func:`build_classification_model` to get a live module.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from .config import RunConfig
from .encoders import CONFIG_NAME, verify_encoder_weights
from .features import ClassificationEncoder, ExtractionEncoder
from .heads import build_implicit_head, build_label_head, build_span_head, head_classes
from .registry import Registry
from .schema import TupleSchema, get_schema
from .taxonomy import FACTORED, JOINT, LabelSpaceSet

MODELS: Registry = Registry("model")


def _make_classes():
    import torch  # noqa: PLC0415 - optional dep
    import torch.nn as nn  # noqa: PLC0415 - optional dep

    from modeling import BertConfig, BertModel  # noqa: PLC0415 - optional dep

    head_classes()  # populate the head registries

    class SequenceEncoder(nn.Module):
        """Adapter that hides the backbone behind a fixed output contract.

        Returns ``(sequence_output, pooled_output)``.  Any replacement encoder
        (BiLSTM, XLM-R) only has to honour that.
        """

        def __init__(self, backbone, hidden_size: int, *, uses_token_type: bool = True):
            super().__init__()
            self.backbone = backbone
            self.hidden_size = hidden_size
            self.uses_token_type = uses_token_type

        def forward(self, input_ids, token_type_ids=None, attention_mask=None):
            if self.uses_token_type:
                return self.backbone(
                    input_ids,
                    token_type_ids,
                    attention_mask,
                    output_all_encoded_layers=False,
                    head_mask=None,
                )
            return self.backbone(
                input_ids,
                None,
                attention_mask,
                output_all_encoded_layers=False,
                head_mask=None,
            )

    class ExtractionModel(nn.Module):
        """Stage 1: span extraction with implicit-slot detection."""

        def __init__(
            self,
            config,
            *,
            num_tags: int,
            span_elements: Sequence[str],
            span_head: str = "crf",
            implicit_head: str = "linear",
            dropout: Optional[float] = None,
            loss_weights: Optional[Dict[str, float]] = None,
        ):
            super().__init__()
            self.config = config
            hidden = config.hidden_size
            drop = config.hidden_dropout_prob if dropout is None else dropout
            self.span_elements = tuple(span_elements)
            self.loss_weights = dict(loss_weights or {})

            self.bert = BertModel(config)
            self.encoder = SequenceEncoder(self.bert, hidden)
            self.span_head = build_span_head(span_head, hidden, num_tags, dropout=drop)
            self.implicit_head = build_implicit_head(
                implicit_head, hidden, self.span_elements, dropout=drop
            )
            self._init_new_weights()

        def _init_new_weights(self):
            def init(module):
                if isinstance(module, (nn.Linear, nn.Embedding)):
                    module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
                if isinstance(module, nn.Linear) and module.bias is not None:
                    module.bias.data.zero_()

            self.span_head.apply(init)
            self.implicit_head.apply(init)

        def forward(
            self,
            input_ids,
            attention_mask,
            token_type_ids=None,
            tag_ids=None,
            implicit_targets=None,
        ):
            sequence_output, pooled_output = self.encoder(
                input_ids, token_type_ids, attention_mask
            )
            span_out = self.span_head(sequence_output, attention_mask, tag_ids)
            imp_out = self.implicit_head(
                sequence_output, pooled_output, attention_mask, implicit_targets
            )

            losses: Dict[str, object] = {}
            if "loss" in span_out:
                losses["span"] = self.loss_weights.get("span", 1.0) * span_out["loss"]
            for name, loss in imp_out.get("losses", {}).items():
                key = f"implicit_{name}"
                losses[key] = self.loss_weights.get(key, 1.0) * loss

            out: Dict[str, object] = {
                "tags": span_out["tags"],
                "implicit_logits": imp_out["logits"],
                "losses": losses,
            }
            if losses:
                out["loss"] = sum(losses.values())
            return out

    class ClassificationModel(nn.Module):
        """Stage 2: label the span combinations produced by stage 1."""

        def __init__(
            self,
            config,
            *,
            span_elements: Sequence[str],
            label_mode: str = FACTORED,
            joint_size: int = 0,
            factored_sizes: Optional[Dict[str, int]] = None,
            label_head: str = "span_pool",
            dropout: Optional[float] = None,
            loss_weights: Optional[Dict[str, float]] = None,
        ):
            super().__init__()
            self.config = config
            hidden = config.hidden_size
            drop = config.hidden_dropout_prob if dropout is None else dropout
            self.span_elements = tuple(span_elements)
            self.label_mode = label_mode

            self.bert = BertModel(config)
            self.encoder = SequenceEncoder(self.bert, hidden)
            self.label_head = build_label_head(
                label_head,
                hidden,
                self.span_elements,
                mode=label_mode,
                joint_size=joint_size,
                factored_sizes=factored_sizes,
                dropout=drop,
                loss_weights=loss_weights,
            )
            self._init_new_weights()

        def _init_new_weights(self):
            def init(module):
                if isinstance(module, (nn.Linear, nn.Embedding)):
                    module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
                if isinstance(module, nn.Linear) and module.bias is not None:
                    module.bias.data.zero_()

            self.label_head.apply(init)

        def forward(self, input_ids, attention_mask, span_masks, token_type_ids=None, targets=None):
            sequence_output, _ = self.encoder(input_ids, token_type_ids, attention_mask)
            out = self.label_head(sequence_output, span_masks, targets)
            if "loss" not in out and "losses" in out and out["losses"]:
                out["loss"] = sum(out["losses"].values())
            return out

    return {
        "SequenceEncoder": SequenceEncoder,
        "ExtractionModel": ExtractionModel,
        "ClassificationModel": ClassificationModel,
        "BertConfig": BertConfig,
    }


_CLASSES: Optional[Dict[str, type]] = None

_MODEL_CLASS_NAMES = frozenset(
    {"SequenceEncoder", "ExtractionModel", "ClassificationModel", "BertConfig"}
)


def model_classes() -> Dict[str, type]:
    global _CLASSES
    if _CLASSES is None:
        _CLASSES = _make_classes()
        MODELS.add("extraction", _CLASSES["ExtractionModel"], "step1", "span")
        MODELS.add("classification", _CLASSES["ClassificationModel"], "step2", "label")
    return _CLASSES


def __getattr__(name: str):
    """Same lazy exposure as :mod:`absa5.heads`; only real class names build torch."""
    if name not in _MODEL_CLASS_NAMES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return model_classes()[name]


def __dir__():
    return sorted(set(globals()) | _MODEL_CLASS_NAMES)


# -- builders --------------------------------------------------------------
def _load_config(checkpoint_dir: str):
    import os  # noqa: PLC0415

    classes = model_classes()
    return classes["BertConfig"].from_json_file(os.path.join(checkpoint_dir, CONFIG_NAME))


def _load_weights(model, checkpoint_dir: str, *, strict: bool = False) -> Dict[str, object]:
    """Load a prepared checkpoint and report exactly what was and was not filled.

    Unlike the legacy loader this never silently swallows ``missing_keys``.
    """
    import os  # noqa: PLC0415

    import torch  # noqa: PLC0415 - optional dep

    path = os.path.join(checkpoint_dir, "pytorch_model.bin")
    state = torch.load(path, map_location="cpu", weights_only=True)
    result = model.load_state_dict(state, strict=False)
    missing_encoder = [k for k in result.missing_keys if k.startswith("bert.")]
    report = {
        "checkpoint": path,
        "missing_keys": list(result.missing_keys),
        "unexpected_keys": list(result.unexpected_keys),
        "missing_encoder_keys": missing_encoder,
    }
    if missing_encoder and strict:
        raise RuntimeError(
            f"{len(missing_encoder)} encoder parameters were not found in {path}; "
            "the checkpoint needs re-keying (absa5.encoders.prepare_checkpoint)"
        )
    return report


def build_extraction_model(
    cfg: RunConfig,
    extraction_encoder: ExtractionEncoder,
    *,
    checkpoint_dir: Optional[str] = None,
    verify: bool = True,
) -> Tuple[object, Dict[str, object]]:
    """Assemble stage 1 and, unless told otherwise, prove the backbone loaded."""
    classes = model_classes()
    schema = get_schema(cfg.data.schema)
    ckpt = checkpoint_dir or cfg.encoder.local_dir or cfg.encoder.model_name_or_path
    config = _load_config(ckpt)

    model = classes["ExtractionModel"](
        config,
        num_tags=extraction_encoder.num_tags,
        span_elements=schema.spans,
        span_head=cfg.heads.span_head,
        implicit_head=cfg.heads.implicit_head,
        dropout=cfg.heads.dropout,
        loss_weights=cfg.train.loss_weights,
    )
    info = _load_weights(model, ckpt)
    if verify:
        info["weight_check"] = (
            verify_encoder_weights(model, ckpt).raise_for_status().as_dict()
        )
    return model, info


def build_classification_model(
    cfg: RunConfig,
    classification_encoder: ClassificationEncoder,
    *,
    checkpoint_dir: Optional[str] = None,
    verify: bool = True,
) -> Tuple[object, Dict[str, object]]:
    """Assemble stage 2.  Starts from the same pre-trained checkpoint as stage 1."""
    classes = model_classes()
    schema = get_schema(cfg.data.schema)
    ckpt = checkpoint_dir or cfg.encoder.local_dir or cfg.encoder.model_name_or_path
    config = _load_config(ckpt)

    model = classes["ClassificationModel"](
        config,
        span_elements=schema.spans,
        label_mode=cfg.heads.label_mode,
        joint_size=classification_encoder.joint_size,
        factored_sizes=classification_encoder.factored_sizes(),
        label_head=cfg.heads.label_head,
        dropout=cfg.heads.dropout,
        loss_weights=cfg.train.loss_weights,
    )
    info = _load_weights(model, ckpt)
    if verify:
        info["weight_check"] = (
            verify_encoder_weights(model, ckpt).raise_for_status().as_dict()
        )
    return model, info


def head_size_report(cfg: RunConfig, spaces: Optional[LabelSpaceSet] = None) -> Dict[str, object]:
    """Parameter counts for the two label-head modes, without building anything."""
    spaces = spaces or cfg.label_spaces()
    hidden = cfg.encoder.hidden_size
    n_spans = len(get_schema(cfg.data.schema).spans)
    fused = hidden * n_spans
    joint = len(spaces.joint_labels())
    factored = spaces.sizes()
    return {
        "fused_size": fused,
        "joint": {"outputs": joint, "params": fused * joint + joint},
        "factored": {
            "outputs": sum(factored.values()),
            "params": sum(fused * k + k for k in factored.values()),
            "per_element": factored,
        },
        "mode_in_use": cfg.heads.label_mode,
    }
