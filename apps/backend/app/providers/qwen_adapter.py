from __future__ import annotations

from .contracts import ProviderResult


class QwenAdapter:
    provider_name = "qwen"

    def translate(self, text: str) -> ProviderResult:
        return ProviderResult(text=text, provider=self.provider_name)