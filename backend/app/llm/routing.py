import logging

from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError, LLMRateLimitError, LLMRequestError
from app.llm.types import ChatCompletionRequest, ChatCompletionResponse

logger = logging.getLogger(__name__)

RETRYABLE_REQUEST_MARKERS = (
    "502",
    "503",
    "504",
    "404",
    "timeout",
    "timed out",
    "model_not_found",
    "does not exist or you do not have access",
)


class RoutingLLMClient(LLMClient):
    """Try providers in order; fall back on rate limits and transient upstream errors."""

    def __init__(self, clients: list[tuple[str, LLMClient]]) -> None:
        if not clients:
            raise LLMConfigurationError("Smart routing requires at least one LLM provider.")
        self._clients = clients
        self._last_provider = clients[0][0]
        self._preferred_index = 0

    @property
    def provider(self) -> str:
        return self._last_provider

    @property
    def route_order(self) -> list[str]:
        return [name for name, _ in self._clients]

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        failures: list[str] = []

        attempt_order = (
            list(range(self._preferred_index, len(self._clients)))
            + list(range(0, self._preferred_index))
        )

        for attempt, index in enumerate(attempt_order):
            name, client = self._clients[index]
            try:
                response = client.chat_completion(request)
            except LLMRateLimitError as exc:
                failures.append(f"{name}: rate limited")
                if attempt < len(attempt_order) - 1:
                    logger.warning("LLM provider %s rate limited; trying next route.", name)
                    continue
                raise
            except LLMRequestError as exc:
                if _is_retryable_request_error(exc) and attempt < len(attempt_order) - 1:
                    failures.append(f"{name}: {exc}")
                    logger.warning("LLM provider %s failed (%s); trying next route.", name, exc)
                    continue
                raise

            self._preferred_index = index
            self._last_provider = name
            if attempt > 0:
                logger.info("LLM smart routing selected provider %s.", name)
            return ChatCompletionResponse(
                message=response.message,
                model=response.model,
                provider=name,
            )

        detail = "; ".join(failures) if failures else "no providers succeeded"
        raise LLMRequestError(f"All LLM providers failed. {detail}")


def _is_retryable_request_error(exc: LLMRequestError) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in RETRYABLE_REQUEST_MARKERS)
