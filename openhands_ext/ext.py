from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, FastAPI
try:
    from . import test_multiuser, test_storage
except ImportError:
    # For direct testing without package structure
    import test_multiuser, test_storage

# Main extension router
router = APIRouter(prefix="/test-extension")

@router.get("/health")
async def health():
    return {"status": "ok", "component": "TestExtension"}

@router.get("/info")
async def extension_info():
    """Information about this test extension"""
    return {
        "name": "OpenHands Test Extension",
        "version": "0.1.0",
        "description": "Demonstrates enterprise-like functionality as clean extensions",
        "features": [
            "Multi-user authentication demo",
            "Multi-tenant storage demo", 
            "Extension composition patterns",
            "Clean separation from OpenHands core",
            "Lifespan management demo"
        ],
        "endpoints": {
            "health": "/test-extension/health",
            "info": "/test-extension/info",
            "multiuser": "/test-multiuser/*",
            "storage": "/test-storage/*"
        }
    }

def get_extension_state(app: FastAPI) -> Dict[str, Any]:
    """Get current extension state - useful for testing"""
    if not hasattr(app.state, 'extensions'):
        return {}
    return app.state.extensions.get('test_extension', {})

def set_extension_state(app: FastAPI, state: Dict[str, Any]) -> None:
    """Set extension state - useful for testing"""
    if not hasattr(app.state, 'extensions'):
        app.state.extensions = {}
    app.state.extensions['test_extension'] = state

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Extension lifespan manager for startup/shutdown tasks.
    
    This demonstrates how extensions can participate in the server lifecycle
    for tasks like:
    - Database connection setup/teardown
    - Background task management
    - Resource initialization/cleanup
    - Cache warming/clearing
    
    Args:
        app: FastAPI application instance
    """
    # Startup tasks
    startup_time = datetime.now(timezone.utc).isoformat()
    
    # Initialize extension state
    set_extension_state(app, {
        'status': 'starting',
        'features': ['multi_user_auth', 'multi_tenant_storage'],
        'startup_time': startup_time,
        'background_tasks': []
    })
    
    # Simulate background task setup (in real extension, this would be actual tasks)
    state = get_extension_state(app)
    state['background_tasks'].append('user_session_cleanup')
    state['background_tasks'].append('storage_maintenance')
    state['status'] = 'running'
    set_extension_state(app, state)
    
    try:
        yield
    finally:
        # Shutdown tasks
        state = get_extension_state(app)
        state['status'] = 'stopping'
        
        # Simulate cleanup of background tasks
        state['background_tasks'].clear()
        state['status'] = 'stopped'
        state['shutdown_time'] = datetime.now(timezone.utc).isoformat()
        
        set_extension_state(app, state)


def register(app: FastAPI) -> None:
    """Register all test extension components"""
    # Register main extension router
    app.include_router(router)
    
    # Register sub-extensions
    test_multiuser.register(app)
    test_storage.register(app)
    
    # Mark registration complete in state (testable)
    if not hasattr(app.state, 'extensions'):
        app.state.extensions = {}
    if 'test_extension' not in app.state.extensions:
        app.state.extensions['test_extension'] = {}
    app.state.extensions['test_extension']['registered'] = True
