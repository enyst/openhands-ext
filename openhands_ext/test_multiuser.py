"""
TestExtension: Multi-User Authentication Demo

This demonstrates how enterprise multi-user functionality could be 
implemented as a clean extension without modifying OpenHands core.
"""
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends, FastAPI
from fastapi.security import HTTPBearer
import jwt
import os
from datetime import datetime, timedelta

# Test extension router
router = APIRouter(prefix="/test-multiuser")
security = HTTPBearer()

# Simple in-memory user store (enterprise would use database)
USERS = {
    "user1": {"id": "user1", "email": "user1@example.com", "plan": "free"},
    "user2": {"id": "user2", "email": "user2@example.com", "plan": "pro"},
}

# JWT secret (demo/test only - not for production)
JWT_SECRET = "test-secret-key-for-demo-only"

# Track actual function calls for testing
_multiuser_calls = []

def initialize_user_auth_system() -> None:
    """Stub: Initialize user authentication system"""
    _multiuser_calls.append('initialize_user_auth_system')

def get_multiuser_calls() -> list:
    """Get list of actual function calls made - for testing"""
    return _multiuser_calls.copy()

def clear_multiuser_calls() -> None:
    """Clear call history - for testing"""
    _multiuser_calls.clear()

class TestUserContext:
    """Simple user context for testing multi-user scenarios"""
    def __init__(self, user_id: str, email: str, plan: str):
        self.user_id = user_id
        self.email = email
        self.plan = plan
        self.is_authenticated = True

def create_test_token(user_id: str) -> str:
    """Create a test JWT token with proper claims"""
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "exp": now + timedelta(hours=24),
        "iat": now,
        "iss": "test-extension",
        "aud": "test-multiuser",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_test_token(token: str) -> Optional[TestUserContext]:
    """Verify and decode test JWT token"""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="test-multiuser",
            issuer="test-extension",
        )
        user_id = payload.get("user_id")
        if user_id and user_id in USERS:
            user_data = USERS[user_id]
            return TestUserContext(
                user_id=user_id,
                email=user_data["email"],
                plan=user_data["plan"]
            )
    except jwt.InvalidTokenError:
        pass
    return None

async def get_current_user(request: Request) -> TestUserContext:
    """Dependency to get current authenticated user"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    user = verify_test_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

@router.post("/login")
async def login(user_id: str):
    """Test login endpoint - returns JWT token"""
    if user_id not in USERS:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    token = create_test_token(user_id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": USERS[user_id]
    }

@router.get("/profile")
async def get_profile(user: TestUserContext = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "plan": user.plan,
        "authenticated": user.is_authenticated
    }

@router.get("/conversations")
async def list_conversations(user: TestUserContext = Depends(get_current_user)):
    """List user's conversations (demo of user-scoped data)"""
    # In enterprise, this would query database with user_id filter
    return {
        "user_id": user.user_id,
        "conversations": [
            {"id": f"conv_{user.user_id}_1", "title": "Test Conversation 1"},
            {"id": f"conv_{user.user_id}_2", "title": "Test Conversation 2"},
        ]
    }

@router.get("/billing")
async def get_billing_info(user: TestUserContext = Depends(get_current_user)):
    """Get user billing information (demo of enterprise feature)"""
    if user.plan == "free":
        return {
            "plan": "free",
            "usage": {"conversations": 5, "limit": 10},
            "upgrade_available": True
        }
    else:
        return {
            "plan": "pro", 
            "usage": {"conversations": 25, "limit": 100},
            "billing_cycle": "monthly"
        }

def register(app: FastAPI):
    """Register the test multi-user extension"""
    # Actually call initialization stub - this is real plumbing!
    initialize_user_auth_system()
    
    app.include_router(router)
    # Registration is tracked in main extension state