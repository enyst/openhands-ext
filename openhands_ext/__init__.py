from typing import Any

__all__ = [
    'register',
    'TestServerConfig',
]

# Lazy attribute access to avoid importing heavy dependencies at package import time.
# This allows using `openhands_ext.ext:register` without importing TestServerConfig
# (which may pull OpenHands and optional deps) unless explicitly accessed.

def __getattr__(name: str) -> Any:  # PEP 562
    if name == 'register':
        from .ext import register as _register
        return _register
    if name == 'TestServerConfig':
        from .config import TestServerConfig as _TestServerConfig
        return _TestServerConfig
    raise AttributeError(f"module {__name__} has no attribute {name!r}")
