from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, FastAPI
try:
    from . import test_multiuser, test_storage
except ImportError:
    # For direct testing without package structure
    import test_multiuser, test_storage

# Track actual function calls for testing
_extension_calls: List[str] = []

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

# Actual stub functions that get called - this is real plumbing!
def start_user_session_cleanup() -> None:
    """Stub: Start user session cleanup background task"""
    _extension_calls.append('start_user_session_cleanup')

def stop_user_session_cleanup() -> None:
    """Stub: Stop user session cleanup background task"""
    _extension_calls.append('stop_user_session_cleanup')

def start_storage_maintenance() -> None:
    """Stub: Start storage maintenance background task"""
    _extension_calls.append('start_storage_maintenance')

def stop_storage_maintenance() -> None:
    """Stub: Stop storage maintenance background task"""
    _extension_calls.append('stop_storage_maintenance')

def initialize_extension_resources() -> None:
    """Stub: Initialize extension resources (DB connections, etc.)"""
    _extension_calls.append('initialize_extension_resources')

def cleanup_extension_resources() -> None:
    """Stub: Cleanup extension resources"""
    _extension_calls.append('cleanup_extension_resources')

# Testing utilities
def get_extension_calls() -> List[str]:
    """Get list of actual function calls made - for testing"""
    return _extension_calls.copy()

def clear_extension_calls() -> None:
    """Clear call history - for testing"""
    _extension_calls.clear()

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
    # Startup tasks - ACTUALLY CALL STUB FUNCTIONS
    startup_time = datetime.now(timezone.utc).isoformat()
    
    # Initialize extension state
    set_extension_state(app, {
        'status': 'starting',
        'features': ['multi_user_auth', 'multi_tenant_storage'],
        'startup_time': startup_time,
    })
    
    # Actually call startup functions - this is real plumbing!
    initialize_extension_resources()
    start_user_session_cleanup()
    start_storage_maintenance()
    
    # Mark as running after startup functions complete
    state = get_extension_state(app)
    state['status'] = 'running'
    set_extension_state(app, state)
    
    try:
        yield
    finally:
        # Shutdown tasks - ACTUALLY CALL CLEANUP FUNCTIONS
        state = get_extension_state(app)
        state['status'] = 'stopping'
        set_extension_state(app, state)
        
        # Actually call cleanup functions - this is real plumbing!
        stop_user_session_cleanup()
        stop_storage_maintenance()
        cleanup_extension_resources()
        
        # Mark as stopped after cleanup functions complete
        state = get_extension_state(app)
        state['status'] = 'stopped'
        state['shutdown_time'] = datetime.now(timezone.utc).isoformat()
        set_extension_state(app, state)


def register_extension_components() -> None:
    """Stub: Register extension components with OpenHands core"""
    _extension_calls.append('register_extension_components')

def register(app: FastAPI) -> None:
    """Register all test extension components"""
    # Actually call registration stub - this is real plumbing!
    register_extension_components()
    
    # Register main extension router
    app.include_router(router)
    
    # Register sub-extensions - these are real function calls
    test_multiuser.register(app)
    test_storage.register(app)
    
    # Mark registration complete in state (testable)
    if not hasattr(app.state, 'extensions'):
        app.state.extensions = {}
    if 'test_extension' not in app.state.extensions:
        app.state.extensions['test_extension'] = {}
    app.state.extensions['test_extension']['registered'] = True
