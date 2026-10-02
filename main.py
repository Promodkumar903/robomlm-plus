from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.discovery_api import router as discovery_router
from app.api.v1.memory_api import router as memory_router
from app.api.v1.terminal_api import router as terminal_router
from app.api.v1.automation_api import automation_router, live_router


app = FastAPI(
    title="ROBOMLM_PLUS",
    description="Market Intelligence Operating System",
    version="1.0.0",
)

# AutoROBOMLM router
from app.api.v1.autorobomlm_api import router as autorobomlm_router
from app.api.account_routes import (
    router as account_router,
    bot_router as bot_router,
)
app.include_router(autorobomlm_router)
app.include_router(account_router)
app.include_router(bot_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def root():
    return {
        "service": "ROBOMLM_PLUS",
        "status": "running",
        "health": "/health",
    }


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "ROBOMLM_PLUS",
        "version": "1.0.0",
    }


app.include_router(discovery_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(terminal_router, prefix="/api")
app.include_router(automation_router, prefix="/api")
app.include_router(live_router, prefix="/api")