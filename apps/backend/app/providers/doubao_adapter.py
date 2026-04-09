from __future__ import annotations

from .contracts import ProviderResult


class DoubaoAdapter:
    provider_name = "doubao"

    def translate(self, text: str) -> ProviderResult:
        return ProviderResult(text=text, provider=self.provider_name)