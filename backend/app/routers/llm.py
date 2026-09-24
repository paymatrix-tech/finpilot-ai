from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError, LLMRequestError
from app.llm.factory import get_llm_client
from app.llm.types import ChatCompletionRequest, ChatCompletionResult

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.post("/chat", response_model=ChatCompletionResult)
def chat_completion(
    body: ChatCompletionRequest,
    llm: Annotated[LLMClient, Depends(get_llm_client)],
) -> ChatCompletionResult:
    try:
        return llm.complete(body)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
