from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

# The extension registers routers on import

def build_app(session_api_key: str | None = None) -> FastAPI:
    app = FastAPI()

    # Inject a minimal dependency to simulate core's get_dependencies behavior
    def _get_deps():
        if session_api_key:
            from fastapi import HTTPException, status
            from fastapi.security import APIKeyHeader

            header = APIKeyHeader(name="X-Session-API-Key", auto_error=False)

            def check_session_api_key(session_key = Depends(header)):
                if session_key != session_api_key:
                    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

            return [Depends(check_session_api_key)]
        return []

    # Patch extension to use our test dependencies
    from openhands_ext import ext as test_ext
    from fastapi import APIRouter
    test_ext.secure_router = APIRouter(prefix="/test-extension", dependencies=_get_deps())

    @test_ext.secure_router.get("/secure-health")
    async def secure_health():
        return {"status": "ok", "component": "TestExtension", "secure": True}

    test_ext.register(app)
    return app


def test_health_public():
    app = build_app()
    client = TestClient(app)
    r = client.get("/test-extension/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_secure_health_su_mode():
    app = build_app(session_api_key=None)
    client = TestClient(app)
    r = client.get("/test-extension/secure-health")
    assert r.status_code == 200
    assert r.json()["secure"] is True


def test_secure_health_api_key_required_and_ok():
    app = build_app(session_api_key="abc")
    client = TestClient(app)
    r = client.get("/test-extension/secure-health")
    assert r.status_code == 401
    r2 = client.get("/test-extension/secure-health", headers={"X-Session-API-Key": "abc"})
    assert r2.status_code == 200
    assert r2.json()["secure"] is True


def test_lifespan_flag_set_and_reset():
    from openhands_ext.ext import lifespan

    app = FastAPI()

    @asynccontextmanager
    async def combined(app):
        async with lifespan(app):
            yield

    app.router.lifespan_context = combined

    with TestClient(app):
        assert getattr(app.state, "test_extension_started", False) is True
    assert getattr(app.state, "test_extension_started", False) is False
