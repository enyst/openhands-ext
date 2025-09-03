# openhands-ext

TestExtension for OpenHands: a minimal external extension to validate the OpenHands extension mechanism.

Features:
- Registers routers at `/test-extension` with endpoints:
  - `/health` (public)
  - `/secure-health` (requires X-Session-API-Key if configured in OH)
- Provides an optional `lifespan(app)` to demonstrate startup/shutdown composition
- Discoverable via either:
  - Env var: `OPENHANDS_EXTENSIONS="openhands_ext.ext:register"`
  - Entry point: `openhands_server_extensions` (see `pyproject.toml`)
- Optional custom `ServerConfig` via `openhands_server_config` entry point (demo/stub only)

Usage
1) Install into the same Python environment as OpenHands:

```
pip install -e .
```

2) Use env var discovery (no packaging metadata required):

```
export OPENHANDS_EXTENSIONS="openhands_ext.ext:register"
```

3) Or use entry points (recommended):

- Ensure this package is installed (`pip install -e .`)
- Unset any legacy env overrides if present: `unset OPENHANDS_CONFIG_CLS` and `unset OPENHANDS_EXTENSIONS`

4) Run OpenHands (example):

```
poetry run uvicorn openhands.server.app:app --host 0.0.0.0 --port 3000
```

Then verify:

```
curl http://localhost:3000/test-extension/health
# {"status": "ok", "component": "TestExtension"}
```

Notes
- This repo purposely avoids any multi-user/auth specifics. It is a simple, external extension that can be developed and run independently of OpenHands.
- The legacy env var `OPENHANDS_CONFIG_CLS` is still honored by OpenHands for backward compatibility but may be removed later.
