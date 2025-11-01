# src/agent_starter/core/llm.py
from __future__ import annotations

import os

import requests


class LLM:
    def __init__(self, provider: str | None = None, model: str | None = None, base_url: str | None = None):  # noqa: E501
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.model = model or os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q4_K_M")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "172.17.128.1:11434")

    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 512) -> str:
        if self.provider == "ollama":  # spell checker was whining here
            r = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                    "stream": False,
                },
                timeout=120,
            )
            r.raise_for_status()
            j = r.json()
            if "message" in j and isinstance(j["message"], dict):
                return j["message"].get("content", "")
            return j.get("content", "")

        raise ValueError(f"Unsupported provider: {self.provider}")
