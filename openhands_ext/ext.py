from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI

from openhands.server.dependencies import get_dependencies

router = APIRouter(prefix="/test-extension")
secure_router = APIRouter(prefix="/test-extension", dependencies=get_dependencies())


@router.get("/health")
async def health():
    return {"status": "ok", "component": "TestExtension"}


@secure_router.get("/secure-health")
async def secure_health():
    return {"status": "ok", "component": "TestExtension", "secure": True}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Demo: mark extension as started in app.state
    setattr(app.state, "test_extension_started", True)
    try:
        yield
    finally:
        setattr(app.state, "test_extension_started", False)


def register(app: FastAPI) -> None:
    app.include_router(router)
    app.include_router(secure_router)
