# =========================
# src/agent_starter/core/schemas.py
# =========================
from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    args: dict


class AgentMsg(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    tool_calls: list[ToolCall] | None = None


class Plan(BaseModel):
    steps: list[str] = Field(default_factory=list)
    requires_tool: bool = False
    tool_name: str | None = None
    tool_args: dict = Field(default_factory=dict)


class ActionResult(BaseModel):
    ok: bool = True
    data: Any = None
    error: str | None = None


class FinalAnswer(BaseModel):
    summary: str
    citations: list[str] = Field(default_factory=list)
