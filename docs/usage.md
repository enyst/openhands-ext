# TestExtension Usage and Design Notes

Sources: See code in this repo (`openhands_ext/ext.py`, `openhands_ext/contrib.py`, tests in `tests/test_extension.py`) and the loader demo in `enyst/playground` (`openhands/server/extensions.py`, `openhands/server/app_ext_demo.py`, `docs/extension-loader.md`).

## What this extension provides
- `register(app)`: mounts two routers
  - `/test-extension/health` (public)
  - `/test-extension/secure-health` (enforced only when core config enables `X-Session-API-Key`)
- `lifespan(app)`: marks `app.state.test_extension_started` True on startup, False on shutdown
- `ComponentContribution` (entry point `openhands_components`): contributes an additional demo router and a sample singleton name

## Router behavior and prefix rules
- Routers are additive. The loader sanitizes prefixes: it strips trailing `/` and ensures a single leading `/` if non-empty.
- This extension uses `APIRouter(prefix="/test-extension")` for both public and secure routes.

## Auth model: SU in core; MU only in extensions
- Core OpenHands runs in SU mode (no multiuser). Our secure route demonstrates per-router enforcement tied to a session API key header when configured.
- The extension never overrides global app auth.

## Optional dependencies
- The extension has no heavy/optional deps by default.
- The core demo loader supports lazy optional deps; see `docs/extension-loader.md` in the demo.

## Tests
- `tests/test_extension.py` validates:
  - `/test-extension/health` returns 200
  - `/test-extension/secure-health` behavior in SU vs API-key modes
  - lifespan flag toggling
- Tests avoid importing heavy OpenHands components; they patch the secure router dependency to simulate core behavior.

## Version compatibility
- The loader will define `OPENHANDS_EXTENSION_API_VERSION` in core and check the extension's `EXTENSION_COMPAT` (to be added) during discovery.

