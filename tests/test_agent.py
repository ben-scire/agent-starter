"""Smoke tests for the agent loop without external services."""

from __future__ import annotations

from agent_starter.core.agent import SingleAgent
from agent_starter.core.schemas import FinalAnswer


class FakeLLM:
    """Return deterministic JSON so the agent loop can run without a model."""

    def __init__(self):
        self.calls = 0

    def chat(self, messages, temperature=0.0, max_tokens=0):
        # First LLM call is plan(), second is reflect()
        if self.calls == 0:
            self.calls += 1
            # No tool needed for the simple test
            return '{"steps":["draft"],"requires_tool":false,"tool_name":null,"tool_args":{}}'
        else:
            # reflect() result
            return '{"summary":"ok","citations":[]}'


def test_agent_basic_no_tool(monkeypatch):
    a = SingleAgent("You return JSON", allowed_tools=[])

    # Swap in fake LLM and a no-op web tool
    a.llm = FakeLLM()

    out: FinalAnswer = a.run("Explain what 2+2 is, briefly.")
    assert isinstance(out.summary, str)
    assert out.summary == "ok"


def test_agent_with_tool_stub(monkeypatch):
    a = SingleAgent("You return JSON", allowed_tools=["web.fetch"])

    # LLM plan requires the tool; reflect returns summary
    class ToolPlanLLM(FakeLLM):
        def chat(self, messages, temperature=0.0, max_tokens=0):
            if self.calls == 0:
                self.calls += 1
                return (
                    '{"steps":["fetch"],"requires_tool":true,'
                    '"tool_name":"web.fetch","tool_args":{"url":"https://example.com"}}'
                )
            else:
                return '{"summary":"fetched","citations":[]}'

    a.llm = ToolPlanLLM()

    # Stub network: don't actually call the internet
    a.web.fetch = lambda args: "Example Domain text"

    out: FinalAnswer = a.run("Summarize https://example.com")
    assert out.summary == "fetched"
