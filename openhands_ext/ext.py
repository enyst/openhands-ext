from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import APIRouter, FastAPI
from . import test_multiuser, test_storage

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
    print("🚀 TestExtension: Starting up...")
    
    # Mark extension as started in app state (for demonstration)
    if not hasattr(app.state, 'extensions'):
        app.state.extensions = {}
    app.state.extensions['test_extension'] = {
        'status': 'running',
        'features': ['multi_user_auth', 'multi_tenant_storage'],
        'startup_time': '2025-09-03T20:30:00Z'
    }
    
    # Simulate background task setup
    print("📊 TestExtension: Background services initialized")
    
    try:
        yield
    finally:
        # Shutdown tasks
        print("🛑 TestExtension: Shutting down...")
        
        # Clean up app state
        if hasattr(app.state, 'extensions') and 'test_extension' in app.state.extensions:
            app.state.extensions['test_extension']['status'] = 'stopped'
        
        print("✅ TestExtension: Cleanup completed")


def register(app: FastAPI) -> None:
    """Register all test extension components"""
    # Register main extension router
    app.include_router(router)
    
    # Register sub-extensions
    test_multiuser.register(app)
    test_storage.register(app)
    
    print("TestExtension: All components registered successfully")
