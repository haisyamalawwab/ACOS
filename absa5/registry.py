"""Generic name -> factory registry used by every pluggable layer in absa5."""

from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, kind: str):
        self.kind = kind
        self._items: Dict[str, T] = {}
        self._aliases: Dict[str, str] = {}

    def register(self, name: str, *aliases: str) -> Callable[[T], T]:
        def deco(obj: T) -> T:
            self.add(name, obj, *aliases)
            return obj

        return deco

    def add(self, name: str, obj: T, *aliases: str) -> T:
        key = self._norm(name)
        if key in self._items:
            raise KeyError(f"{self.kind} '{name}' already registered")
        self._items[key] = obj
        for alias in aliases:
            akey = self._norm(alias)
            if akey in self._aliases or akey in self._items:
                raise KeyError(f"{self.kind} alias '{alias}' already taken")
            self._aliases[akey] = key
        return obj

    def get(self, name: str) -> T:
        key = self._norm(name)
        key = self._aliases.get(key, key)
        if key not in self._items:
            raise KeyError(
                f"unknown {self.kind} '{name}'. available: {', '.join(self.names())}"
            )
        return self._items[key]

    def build(self, name: str, *args, **kwargs):
        return self.get(name)(*args, **kwargs)

    def names(self) -> list[str]:
        return sorted(self._items)

    def aliases(self) -> Dict[str, str]:
        return dict(self._aliases)

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        key = self._norm(name)
        return self._aliases.get(key, key) in self._items

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())

    def __len__(self) -> int:
        return len(self._items)

    @staticmethod
    def _norm(name: str) -> str:
        return name.strip().lower().replace("-", "_")
