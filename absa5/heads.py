"""Pluggable heads.  Torch is imported lazily so the rest of absa5 stays importable.

Every head takes the same two things from whatever encoder sits underneath:
a token-level tensor ``(batch, seq, hidden)`` and a sentence vector
``(batch, hidden)``.  Nothing here mentions BERT, which is what lets a BiLSTM or
XLM-R encoder drop in later without touching the heads.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from .registry import Registry

SPAN_HEADS: Registry = Registry("span head")
IMPLICIT_HEADS: Registry = Registry("implicit head")
LABEL_HEADS: Registry = Registry("label head")


def _torch():
    import torch  # noqa: PLC0415 - optional dep

    return torch


def _nn():
    import torch.nn as nn  # noqa: PLC0415 - optional dep

    return nn


def _base():
    """``nn.Module`` fetched lazily so module import does not require torch."""
    return _nn().Module


def build_span_head(kind: str, *args, **kwargs):
    return SPAN_HEADS.build(kind, *args, **kwargs)


def build_implicit_head(kind: str, *args, **kwargs):
    return IMPLICIT_HEADS.build(kind, *args, **kwargs)


def build_label_head(kind: str, *args, **kwargs):
    return LABEL_HEADS.build(kind, *args, **kwargs)


def _make_classes():
    """Define the torch-dependent classes once, on first use."""
    nn = _nn()
    torch = _torch()

    class CrfSpanHead(nn.Module):
        """Token classifier plus CRF; the upstream arrangement, kept comparable.

        ``num_tags`` comes from the tagging scheme, so adding a span element
        widens this head automatically.
        """

        def __init__(self, hidden_size: int, num_tags: int, *, dropout: float = 0.1):
            super().__init__()
            from torchcrf import CRF  # noqa: PLC0415 - optional dep

            self.num_tags = num_tags
            self.projection = nn.Sequential(
                nn.Dropout(dropout), nn.Linear(hidden_size, num_tags)
            )
            self.crf = CRF(num_tags, batch_first=True)

        def forward(self, sequence_output, attention_mask, tag_ids=None):
            emissions = self.projection(sequence_output)
            mask = attention_mask.bool()
            out: Dict[str, object] = {"emissions": emissions}
            if tag_ids is not None:
                out["loss"] = -self.crf(emissions, tag_ids, mask=mask, reduction="mean")
            out["tags"] = self.crf.decode(emissions, mask=mask)
            return out

    class SoftmaxSpanHead(nn.Module):
        """CRF-free ablation: independent per-token softmax."""

        def __init__(self, hidden_size: int, num_tags: int, *, dropout: float = 0.1):
            super().__init__()
            self.num_tags = num_tags
            self.projection = nn.Sequential(
                nn.Dropout(dropout), nn.Linear(hidden_size, num_tags)
            )
            self.loss_fct = nn.CrossEntropyLoss(ignore_index=-100)

        def forward(self, sequence_output, attention_mask, tag_ids=None):
            emissions = self.projection(sequence_output)
            out: Dict[str, object] = {"emissions": emissions}
            if tag_ids is not None:
                target = tag_ids.masked_fill(attention_mask == 0, -100)
                out["loss"] = self.loss_fct(
                    emissions.view(-1, self.num_tags), target.view(-1)
                )
            preds = emissions.argmax(-1)
            lengths = attention_mask.sum(-1).tolist()
            out["tags"] = [
                preds[i, : int(lengths[i])].tolist() for i in range(preds.size(0))
            ]
            return out

    class ImplicitHead(nn.Module):
        """One binary classifier per span element, reading a designated position.

        The leading element reads the first boundary token and the rest read the
        last, which is where upstream put the implicit-opinion signal.
        """

        def __init__(
            self,
            hidden_size: int,
            span_elements: Sequence[str],
            *,
            dropout: float = 0.1,
            num_classes: int = 2,
        ):
            super().__init__()
            self.span_elements = tuple(span_elements)
            self.classifiers = nn.ModuleDict(
                {
                    name: nn.Sequential(
                        nn.Dropout(dropout), nn.Linear(hidden_size, num_classes)
                    )
                    for name in self.span_elements
                }
            )
            self.loss_fct = nn.CrossEntropyLoss()

        def forward(self, sequence_output, pooled_output, attention_mask, targets=None):
            last_index = attention_mask.sum(-1) - 1
            batch = torch.arange(sequence_output.size(0), device=sequence_output.device)
            last_token = sequence_output[batch, last_index]

            logits: Dict[str, object] = {}
            losses: Dict[str, object] = {}
            for i, name in enumerate(self.span_elements):
                source = pooled_output if i == 0 else last_token
                logit = self.classifiers[name](source)
                logits[name] = logit
                if targets is not None and name in targets:
                    losses[name] = self.loss_fct(logit, targets[name].view(-1))
            out: Dict[str, object] = {"logits": logits, "losses": losses}
            if losses:
                out["loss"] = sum(losses.values())
            return out

    class SpanPoolLabelHead(nn.Module):
        """Mean-pool each span, concatenate, then classify.

        ``joint`` keeps one output over the label cross product (upstream);
        ``factored`` keeps one output per label element.  With 13 categories,
        3 sentiments and 5 emotions the joint space is 195 cells against ~2.4k
        training pairs, so factored is the default for the quintuple.
        """

        def __init__(
            self,
            hidden_size: int,
            span_elements: Sequence[str],
            *,
            mode: str = "factored",
            joint_size: int = 0,
            factored_sizes: Optional[Dict[str, int]] = None,
            dropout: float = 0.1,
            loss_weights: Optional[Dict[str, float]] = None,
        ):
            super().__init__()
            self.span_elements = tuple(span_elements)
            self.mode = mode
            self.fused_size = hidden_size * len(self.span_elements)
            self.dropout = nn.Dropout(dropout)
            self.loss_fct = nn.BCEWithLogitsLoss()
            self.loss_weights = dict(loss_weights or {})

            if mode == "joint":
                if joint_size <= 0:
                    raise ValueError("joint mode needs joint_size > 0")
                self.classifier = nn.Linear(self.fused_size, joint_size)
                self.joint_size = joint_size
                self.factored_sizes: Dict[str, int] = {}
            elif mode == "factored":
                if not factored_sizes:
                    raise ValueError("factored mode needs factored_sizes")
                self.classifiers = nn.ModuleDict(
                    {n: nn.Linear(self.fused_size, k) for n, k in factored_sizes.items()}
                )
                self.factored_sizes = dict(factored_sizes)
                self.joint_size = 0
            else:
                raise ValueError(f"unknown label head mode '{mode}'")

        def pool(self, sequence_output, span_masks: Dict[str, object]):
            parts = []
            for name in self.span_elements:
                mask = span_masks[name].to(sequence_output.dtype)
                denom = mask.sum(-1, keepdim=True).clamp(min=1.0)
                pooled = (mask.unsqueeze(-1) * sequence_output).sum(1) / denom
                parts.append(pooled)
            return torch.cat(parts, dim=-1)

        def forward(self, sequence_output, span_masks, targets=None):
            fused = self.dropout(self.pool(sequence_output, span_masks))
            if self.mode == "joint":
                logits = self.classifier(fused)
                out: Dict[str, object] = {"logits": {"joint": logits}}
                if targets is not None and "joint" in targets:
                    out["loss"] = self.loss_fct(logits, targets["joint"].float())
                    out["losses"] = {"joint": out["loss"]}
                return out

            logits = {n: head(fused) for n, head in self.classifiers.items()}
            out = {"logits": logits}
            if targets is not None:
                losses = {}
                for name, logit in logits.items():
                    if name not in targets:
                        continue
                    weight = self.loss_weights.get(name, 1.0)
                    losses[name] = weight * self.loss_fct(logit, targets[name].float())
                if losses:
                    out["losses"] = losses
                    out["loss"] = sum(losses.values())
            return out

    return {
        "CrfSpanHead": CrfSpanHead,
        "SoftmaxSpanHead": SoftmaxSpanHead,
        "ImplicitHead": ImplicitHead,
        "SpanPoolLabelHead": SpanPoolLabelHead,
    }


_CLASSES: Optional[Dict[str, type]] = None

_HEAD_CLASS_NAMES = frozenset(
    {"CrfSpanHead", "SoftmaxSpanHead", "ImplicitHead", "SpanPoolLabelHead"}
)


def head_classes() -> Dict[str, type]:
    """Build and register the torch head classes on first call."""
    global _CLASSES
    if _CLASSES is None:
        _CLASSES = _make_classes()
        SPAN_HEADS.add("crf", _CLASSES["CrfSpanHead"], "bio_crf")
        SPAN_HEADS.add("softmax", _CLASSES["SoftmaxSpanHead"], "linear")
        IMPLICIT_HEADS.add("linear", _CLASSES["ImplicitHead"], "binary")
        LABEL_HEADS.add("span_pool", _CLASSES["SpanPoolLabelHead"], "mean_pool")
    return _CLASSES


def __getattr__(name: str):
    """Expose the head classes as module attributes without importing torch eagerly.

    Only the four class names are answered here.  The import machinery probes
    modules for names like ``__path__``, and answering those by building the
    classes would drag torch in on every plain ``import absa5.heads``.
    """
    if name not in _HEAD_CLASS_NAMES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return head_classes()[name]


def __dir__():
    return sorted(set(globals()) | _HEAD_CLASS_NAMES)
