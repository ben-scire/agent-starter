"""Minimal HTTP fetch helper used by the agent tool interface."""

from __future__ import annotations

import re
from dataclasses import dataclass

import requests


@dataclass
class FetchArgs:
    url: str


class WebTools:
    """Tiny web helper used by the agent. No JS, no crawling, just fetch + trim."""

    name = "web"

    def fetch(self, args: FetchArgs) -> str:
        if not args.url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        r = requests.get(
            args.url,
            timeout=15,
            headers={"User-Agent": "agent-starter/0.1 (+https://example.invalid)"},
        )
        r.raise_for_status()
        text = r.text

        # Dependency-free scrub: strip script/style blocks and collapse spaces
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Keep it small for the model
        return text[:8000]
