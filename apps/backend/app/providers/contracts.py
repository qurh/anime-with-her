from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    pass


@dataclass(slots=True)
class ProviderResult:
    text: str
    provider: str


class Provider(Protocol):
    def translate(self, text: str) -> ProviderResult: ...