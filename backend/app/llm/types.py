from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

ChatRole = Literal["system", "user", "assistant", "tool"]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str
    # Gemini 3+ returns this on tool calls; must be echoed on subsequent requests.
    extra_content: dict[str, Any] | None = None


class ChatMessage(BaseModel):
    role: ChatRole
    content: str | None = Field(default=None, max_length=16_000)
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = Field(default=None, max_length=256)
    name: str | None = Field(default=None, max_length=128)


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
    messages: list[ChatMessage] = Field(min_length=1, max_length=32)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    tools: list[dict[str, Any]] | None = Field(default=None, max_length=16)

    @model_validator(mode="after")
    def _bound_total_message_size(self) -> "ChatCompletionRequest":
        total_chars = sum(len(message.content or "") for message in self.messages)
        if total_chars > 64_000:
            raise ValueError("Total message content must be at most 64000 characters.")
        return self
