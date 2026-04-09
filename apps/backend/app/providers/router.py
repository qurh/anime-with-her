from __future__ import annotations

from .contracts import Provider, ProviderError, ProviderResult
from .doubao_adapter import DoubaoAdapter
from .qwen_adapter import QwenAdapter


class ProviderRouter:
    def __init__(
        self,
        primary: Provider | None = None,
        secondary: Provider | None = None,
    ) -> None:
        self.primary = primary or QwenAdapter()
        self.secondary = secondary or DoubaoAdapter()

    def translate(self, text: str) -> ProviderResult:
        try:
            return self.primary.translate(text)
        except ProviderError:
            return self.secondary.translate(text)