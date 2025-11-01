# src/agent_starter/core/agent.py
from __future__ import annotations

import json

from agent_starter.tools.web import FetchArgs, WebTools

from .llm import LLM
from .memory import ShortTermMemory
from .schemas import ActionResult, FinalAnswer, Plan


class ToolDenied(Exception):
    pass


class SingleAgent:
    """
    Minimal Sense → Plan → Act → Reflect agent.
    - plan(): ask the model for a JSON plan
    - act(): call a whitelisted tool (optional)
    - reflect(): synthesize a final JSON answer
    """

    def __init__(self, system_prompt: str, allowed_tools: list[str] | None = None):
        self.system_prompt = system_prompt
        self.allowed_tools = set(allowed_tools or [])
        self.llm = LLM()
        self.mem = ShortTermMemory()
        self.web = WebTools()

    # ----- internal helpers -----
    def _messages(self, user: str, scratch: str | None = None) -> list[dict]:
        msgs: list[dict] = [
            {"role": "system", "content": self.system_prompt},
            *self.mem.context(),
            {"role": "user", "content": user},
        ]
        if scratch:
            msgs.append({"role": "assistant", "content": scratch})
        return msgs

    # ----- sense/plan -----
    def plan(self, user_input: str) -> Plan:
        prompt = (
            "Decide a short plan. Respond ONLY with valid JSON in this exact format: "
            '{"steps":[], "requires_tool": true|false, "tool_name": null|"web.fetch", '
            '"tool_args": {}}'
        )
        raw = self.llm.chat(
            self._messages(user_input, scratch=prompt), temperature=0.1, max_tokens=300
        )
        try:
            obj = json.loads(raw)
        except Exception:
            # Try to extract JSON from the response if it's embedded in text
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                try:
                    obj = json.loads(json_match.group())
                except Exception:
                    obj = {
                        "steps": ["draft answer"],
                        "requires_tool": False,
                        "tool_name": None,
                        "tool_args": {},
                    }
            else:
                obj = {
                    "steps": ["draft answer"],
                    "requires_tool": False,
                    "tool_name": None,
                    "tool_args": {},
                }
        return Plan(**obj)

    # ----- act -----
    def act(self, plan: Plan) -> ActionResult:
        if not plan.requires_tool:
            return ActionResult(ok=True, data=None)

        if plan.tool_name not in self.allowed_tools:
            raise ToolDenied(f"Tool {plan.tool_name} not allowed")

        try:
            if plan.tool_name == "web.fetch":
                args = FetchArgs(**plan.tool_args)
                data = self.web.fetch(args)
                return ActionResult(ok=True, data=data)
            return ActionResult(ok=False, error=f"Unknown tool {plan.tool_name}")
        except Exception as e:
            return ActionResult(ok=False, error=str(e))

    # ----- reflect -----
    def reflect(self, user_input: str, plan: Plan, result: ActionResult) -> FinalAnswer:
        obs = result.data if result.ok and result.data else (result.error or "")
        critique = (
            "Reflect on the plan and observation. Respond ONLY with valid JSON in this exact format: "  # noqa: E501
            '{"summary": "your answer here", "citations": []}'
        )
        msgs = [
            {"role": "system", "content": self.system_prompt},
            *self.mem.context(),
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": f"PLAN: {plan.model_dump_json()}"},
            {"role": "tool", "content": obs[:4000]},
            {"role": "assistant", "content": critique},
        ]
        raw = self.llm.chat(msgs, temperature=0.2, max_tokens=500)
        # For now, just return the raw response as the summary
        # TODO: Improve JSON parsing or change to non-JSON response format
        return FinalAnswer(summary=raw.strip(), citations=[])

    # ----- entrypoint -----
    def run(self, user_input: str) -> FinalAnswer:
        # Temporarily simplify: just call LLM directly
        msgs = self._messages(user_input)
        raw = self.llm.chat(msgs, temperature=0.2, max_tokens=500)
        answer = FinalAnswer(summary=raw.strip(), citations=[])
        # short memory
        self.mem.add({"role": "user", "content": user_input})
        self.mem.add({"role": "assistant", "content": answer.summary})
        return answer
