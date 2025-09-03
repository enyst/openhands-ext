# OpenHands Extensions with FastAPI DI (TestExtension)

This document explains how the TestExtension demonstrates an extension architecture using FastAPI dependency injection plus a tiny application-level registry.

Key ideas
- Global, non-enforcing request context via FastAPI Depends: resolves principal/tenant into request.state.ctx (never 401s).
- Per-router enforcement: enterprise routes add an `auth_required` dependency; core routes remain SU-friendly.
- Service registry (app.state.services): singleton providers (first-wins) and additive contributions.
- Entry points: `openhands_server_extensions`, `openhands_server_lifespans`, and `openhands_components` for contributions.

Files in this repo
- openhands_ext/ext.py: defines register(app) and lifespan(app)
- openhands_ext/contrib.py: returns a ComponentContribution for future loader usage
- openhands_ext/test_components.py: a stub TestConversationManager (demo only)

How to run (with playground demo loader)
- Install both `playground` and `openhands-ext` into the same Python environment.
- Run: `uvicorn openhands.server.app_ext_demo:app --host 0.0.0.0 --port 3000`
- Test endpoints: `/test-extension/health`, `/test-extension/secure-health` (with X-Session-API-Key if configured).

Versioning
- Extensions should declare a compatibility string in code (not env): e.g., `EXTENSION_COMPAT = ">=1.0,<2.0"`.
- Core defines `OPENHANDS_EXTENSION_API_VERSION` and validates.
