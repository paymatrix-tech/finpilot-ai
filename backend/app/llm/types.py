from typing import Any, Literal

from pydantic import BaseModel, Field

ChatRole = Literal["system", "user", "assistant", "tool"]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str
    # Gemini 3+ returns this on tool calls; must be echoed on subsequent requests.
    extra_content: dict[str, Any] | None = None


class ChatMessage(BaseModel):
    role: ChatRole
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class AssistantMessage(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ChatCompletionResponse(BaseModel):
    message: AssistantMessage
    model: str
    provider: str


class ChatCompletionResult(BaseModel):
    content: str
    model: str
    provider: str = Field(description="Configured LLM provider id")


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    tools: list[dict[str, Any]] | None = None
