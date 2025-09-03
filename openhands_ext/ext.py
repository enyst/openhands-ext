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
            "Clean separation from OSS core"
        ],
        "endpoints": {
            "health": "/test-extension/health",
            "info": "/test-extension/info",
            "multiuser": "/test-multiuser/*",
            "storage": "/test-storage/*"
        }
    }

def register(app: FastAPI) -> None:
    """Register all test extension components"""
    # Register main extension router
    app.include_router(router)
    
    # Register sub-extensions
    test_multiuser.register(app)
    test_storage.register(app)
    
    print("TestExtension: All components registered successfully")
