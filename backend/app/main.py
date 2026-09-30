import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api_errors import database_unavailable_exception
from app.db import check_database
from app.llm.factory import get_llm_client, reset_llm_client_cache
from app.llm.openai_compat import OpenAICompatibleClient
from app.llm.routing import RoutingLLMClient
from app.routers.investigation import router as investigation_router
from app.routers.llm import router as llm_router
from app.routers.payments import router as payments_router

logger = logging.getLogger(__name__)


def _log_llm_routes() -> None:
    reset_llm_client_cache()
    client = get_llm_client()
    if isinstance(client, RoutingLLMClient):
        for name, route_client in client._clients:
            model = getattr(route_client, "model", type(route_client).__name__)
            logger.info("LLM route %s -> model %s", name, model)
    elif isinstance(client, OpenAICompatibleClient):
        logger.info("LLM provider %s -> model %s", client.provider, client.model)
    else:
        logger.info("LLM client %s", type(client).__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _log_llm_routes()
    yield


app = FastAPI(title="FinPilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments_router)
app.include_router(llm_router)
app.include_router(investigation_router)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    _request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    http_exc = database_unavailable_exception(exc)
    return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})


@app.get("/health")
def health() -> dict[str, str]:
    database_up = check_database()
    return {
        "status": "ok" if database_up else "degraded",
        "service": "finpilot-api",
        "database": "up" if database_up else "down",
    }
