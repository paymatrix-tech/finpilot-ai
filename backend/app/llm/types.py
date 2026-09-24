from typing import Literal

from pydantic import BaseModel, Field

ChatRole = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: ChatRole
    content: str


class ChatCompletionResult(BaseModel):
    content: str
    model: str
    provider: str = Field(description="Configured LLM provider id")


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
