from typing import Any

import httpx

from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError, LLMRequestError
from app.llm.types import ChatCompletionRequest, ChatCompletionResult


class OpenAICompatibleClient(LLMClient):
    """Chat completions against an OpenAI-compatible HTTP API (OpenAI, Ollama, MLX servers, etc.)."""

    def __init__(
        self,
        *,
        provider: str,
        api_key: str | None,
        model: str,
        base_url: str,
        timeout_seconds: float = 60.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not model.strip():
            raise LLMConfigurationError("LLM_MODEL is required.")
        self._provider = provider
        self._api_key = api_key
        self._model = model.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._http = http_client or httpx.Client(timeout=timeout_seconds)

    @property
    def provider(self) -> str:
        return self._provider

    def complete(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        if not request.messages:
            raise LLMRequestError("At least one message is required.")

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [message.model_dump() for message in request.messages],
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        url = f"{self._base_url}/chat/completions"
        try:
            response = self._http.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise LLMRequestError(f"LLM request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip() or response.reason_phrase
            raise LLMRequestError(f"LLM returned {response.status_code}: {detail}")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMRequestError("LLM response was missing chat completion content.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMRequestError("LLM returned empty content.")

        return ChatCompletionResult(
            content=content,
            model=str(data.get("model", self._model)),
            provider=self._provider,
        )
