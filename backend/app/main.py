from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import check_database
from app.routers.payments import router as payments_router

app = FastAPI(title="FinPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments_router)


@app.get("/health")
def health() -> dict[str, str]:
    database_up = check_database()
    return {
        "status": "ok" if database_up else "degraded",
        "service": "finpilot-api",
        "database": "up" if database_up else "down",
    }
