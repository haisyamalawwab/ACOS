"""Tokenizer adapters.

Everything downstream needs exactly one operation: ``tokenize(word) -> list[str]``,
splitting a single whitespace token into subwords.  Keeping the contract that
narrow is what lets the same span remapper serve legacy WordPiece, HuggingFace
fast tokenizers, and SentencePiece models later without a rewrite.

The pure-Python :class:`WordPieceTokenizer` exists so the span-remap gate can run
on a machine with no torch installed.
"""

from __future__ import annotations

import os
import unicodedata
from typing import Callable, Dict, List, Optional, Protocol, Sequence, runtime_checkable

from .registry import Registry

UNK = "[UNK]"


@runtime_checkable
class TokenizerLike(Protocol):
    def tokenize(self, text: str) -> List[str]:  # pragma: no cover - protocol
        ...


class BaseTokenizer:
    """Minimal shared surface; subclasses implement :meth:`tokenize`."""

    name = "base"
    unk_token = UNK

    def tokenize(self, text: str) -> List[str]:
        raise NotImplementedError

    def tokenize_word(self, word: str) -> List[str]:
        """Tokenize one word, never returning an empty list.

        An empty result would silently shift every following span index, so the
        unknown token is substituted instead.
        """
        pieces = self.tokenize(word)
        return list(pieces) if pieces else [self.unk_token]

    def describe(self) -> Dict[str, object]:
        return {"name": self.name, "class": type(self).__name__}


class WhitespaceTokenizer(BaseTokenizer):
    """Identity tokenizer: one word stays one token.

    Useful as a control - remapping with it must be the identity transform.
    """

    name = "whitespace"

    def __init__(self, *, do_lower_case: bool = False):
        self.do_lower_case = do_lower_case

    def tokenize(self, text: str) -> List[str]:
        text = text.lower() if self.do_lower_case else text
        return text.split()

    def describe(self) -> Dict[str, object]:
        return {**super().describe(), "do_lower_case": self.do_lower_case}


class WordPieceTokenizer(BaseTokenizer):
    """Pure-Python BERT tokenizer (basic + WordPiece), no torch required.

    Mirrors ``bert_utils/tokenization.py`` closely enough to reproduce the
    pre-tokenised files shipped in ``tokenized_data/``.
    """

    name = "wordpiece"

    def __init__(
        self,
        vocab: Sequence[str] | Dict[str, int],
        *,
        do_lower_case: bool = True,
        do_basic_tokenize: bool = True,
        max_input_chars_per_word: int = 100,
        unk_token: str = UNK,
    ):
        if isinstance(vocab, dict):
            self.vocab = dict(vocab)
        else:
            self.vocab = {tok: i for i, tok in enumerate(vocab)}
        if unk_token not in self.vocab:
            raise ValueError(f"vocab is missing the unknown token {unk_token!r}")
        self.unk_token = unk_token
        self.do_lower_case = do_lower_case
        self.do_basic_tokenize = do_basic_tokenize
        self.max_input_chars_per_word = max_input_chars_per_word

    @classmethod
    def from_vocab_file(cls, path: str, **kwargs) -> "WordPieceTokenizer":
        with open(path, "r", encoding="utf-8") as fh:
            vocab = [line.rstrip("\n") for line in fh]
        while vocab and vocab[-1] == "":
            vocab.pop()
        return cls(vocab, **kwargs)

    @classmethod
    def from_pretrained(cls, path: str, **kwargs) -> "WordPieceTokenizer":
        candidate = path if os.path.isfile(path) else os.path.join(path, "vocab.txt")
        if not os.path.isfile(candidate):
            raise FileNotFoundError(f"no vocab.txt under {path!r}")
        return cls.from_vocab_file(candidate, **kwargs)

    # -- basic tokenizer ---------------------------------------------------
    def _basic_tokenize(self, text: str) -> List[str]:
        text = self._clean_text(text)
        tokens = text.strip().split()
        out: List[str] = []
        for token in tokens:
            if self.do_lower_case:
                token = token.lower()
                token = self._strip_accents(token)
            out.extend(self._split_on_punc(token))
        return " ".join(out).strip().split()

    @staticmethod
    def _clean_text(text: str) -> str:
        out = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xFFFD or _is_control(char):
                continue
            out.append(" " if _is_whitespace(char) else char)
        return "".join(out)

    @staticmethod
    def _strip_accents(text: str) -> str:
        text = unicodedata.normalize("NFD", text)
        return "".join(c for c in text if unicodedata.category(c) != "Mn")

    @staticmethod
    def _split_on_punc(text: str) -> List[str]:
        chars = list(text)
        out: List[List[str]] = []
        start_new = True
        for char in chars:
            if _is_punctuation(char):
                out.append([char])
                start_new = True
            else:
                if start_new:
                    out.append([])
                start_new = False
                out[-1].append(char)
        return ["".join(x) for x in out]

    # -- wordpiece ---------------------------------------------------------
    def _wordpiece(self, token: str) -> List[str]:
        if len(token) > self.max_input_chars_per_word:
            return [self.unk_token]
        chars = list(token)
        start = 0
        sub_tokens: List[str] = []
        while start < len(chars):
            end = len(chars)
            cur = None
            while start < end:
                substr = "".join(chars[start:end])
                if start > 0:
                    substr = "##" + substr
                if substr in self.vocab:
                    cur = substr
                    break
                end -= 1
            if cur is None:
                return [self.unk_token]
            sub_tokens.append(cur)
            start = end
        return sub_tokens

    def tokenize(self, text: str) -> List[str]:
        pieces: List[str] = []
        if self.do_basic_tokenize:
            for token in self._basic_tokenize(text):
                pieces.extend(self._wordpiece(token))
        else:
            for token in text.strip().split():
                pieces.extend(self._wordpiece(token))
        return pieces

    def convert_tokens_to_ids(self, tokens: Sequence[str]) -> List[int]:
        unk_id = self.vocab[self.unk_token]
        return [self.vocab.get(tok, unk_id) for tok in tokens]

    def describe(self) -> Dict[str, object]:
        return {
            **super().describe(),
            "vocab_size": len(self.vocab),
            "do_lower_case": self.do_lower_case,
            "do_basic_tokenize": self.do_basic_tokenize,
        }


class DelegatingTokenizer(BaseTokenizer):
    """Wraps any object exposing ``tokenize``; the escape hatch for new backends."""

    name = "delegating"

    def __init__(self, inner, *, unk_token: str = UNK, name: Optional[str] = None):
        if not hasattr(inner, "tokenize"):
            raise TypeError(f"{type(inner).__name__} has no .tokenize()")
        self.inner = inner
        self.unk_token = getattr(inner, "unk_token", None) or unk_token
        if name:
            self.name = name

    def tokenize(self, text: str) -> List[str]:
        return list(self.inner.tokenize(text))

    def convert_tokens_to_ids(self, tokens: Sequence[str]) -> List[int]:
        fn = getattr(self.inner, "convert_tokens_to_ids", None)
        if fn is None:
            raise AttributeError(f"{type(self.inner).__name__} cannot map tokens to ids")
        return list(fn(list(tokens)))

    def describe(self) -> Dict[str, object]:
        return {**super().describe(), "inner": type(self.inner).__name__}


def legacy_bert_tokenizer(model_path: str, *, do_lower_case: bool = True) -> DelegatingTokenizer:
    """Adapter over ``bert_utils.tokenization.BertTokenizer`` (the training path)."""
    from bert_utils.tokenization import BertTokenizer  # noqa: PLC0415 - optional dep

    inner = BertTokenizer.from_pretrained(model_path, do_lower_case=do_lower_case)
    return DelegatingTokenizer(inner, name="legacy_bert")


def hf_tokenizer(model_name: str, *, do_lower_case: bool = True, **kwargs) -> DelegatingTokenizer:
    """Adapter over ``transformers.AutoTokenizer``."""
    from transformers import AutoTokenizer  # noqa: PLC0415 - optional dep

    inner = AutoTokenizer.from_pretrained(model_name, do_lower_case=do_lower_case, **kwargs)
    return DelegatingTokenizer(inner, name="hf")


TOKENIZERS: Registry[Callable[..., BaseTokenizer]] = Registry("tokenizer")
TOKENIZERS.add("whitespace", WhitespaceTokenizer, "identity")
TOKENIZERS.add("wordpiece", WordPieceTokenizer.from_pretrained, "bert", "indobert")
TOKENIZERS.add("legacy_bert", legacy_bert_tokenizer, "legacy")
TOKENIZERS.add("hf", hf_tokenizer, "transformers", "auto")


def build_tokenizer(spec: str, *args, **kwargs) -> BaseTokenizer:
    return TOKENIZERS.build(spec, *args, **kwargs)


def as_tokenizer(obj) -> BaseTokenizer:
    """Coerce any tokenizer-ish object into the adapter surface."""
    if isinstance(obj, BaseTokenizer):
        return obj
    return DelegatingTokenizer(obj)


# -- character class helpers (copied semantics from BERT) -------------------
def _is_whitespace(char: str) -> bool:
    if char in (" ", "\t", "\n", "\r"):
        return True
    return unicodedata.category(char) == "Zs"


def _is_control(char: str) -> bool:
    if char in ("\t", "\n", "\r"):
        return False
    return unicodedata.category(char).startswith("C")


def _is_punctuation(char: str) -> bool:
    cp = ord(char)
    if (33 <= cp <= 47) or (58 <= cp <= 64) or (91 <= cp <= 96) or (123 <= cp <= 126):
        return True
    return unicodedata.category(char).startswith("P")
