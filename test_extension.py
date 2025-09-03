#!/usr/bin/env python3
"""
Simple test demonstration for TestExtension

This shows how the refactored extension is now testable without relying on print statements.
Run with: python test_extension.py
"""

import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import directly to avoid OpenHands dependencies in test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openhands_ext'))

from ext import register, lifespan, get_extension_state
from test_multiuser import create_test_token, verify_test_token


async def test_extension_lifecycle():
    """Test extension lifecycle management"""
    print("🧪 Testing Extension Lifecycle...")
    
    app = FastAPI()
    
    # Test registration
    register(app)
    state = get_extension_state(app)
    assert state.get('registered') is True, "Extension should be registered"
    print("✅ Registration: PASS")
    
    # Test lifespan
    async with lifespan(app):
        state = get_extension_state(app)
        assert state.get('status') == 'running', f"Expected 'running', got {state.get('status')}"
        assert 'startup_time' in state, "Should have startup_time"
        assert len(state.get('background_tasks', [])) == 2, "Should have 2 background tasks"
        print("✅ Startup: PASS")
    
    # Check shutdown
    state = get_extension_state(app)
    assert state.get('status') == 'stopped', f"Expected 'stopped', got {state.get('status')}"
    assert 'shutdown_time' in state, "Should have shutdown_time"
    assert len(state.get('background_tasks', [])) == 0, "Background tasks should be cleaned up"
    print("✅ Shutdown: PASS")


def test_jwt_functionality():
    """Test JWT token creation and validation"""
    print("🧪 Testing JWT Functionality...")
    
    # Test token creation
    token = create_test_token("user1")
    assert token is not None, "Token should be created"
    assert isinstance(token, str), "Token should be a string"
    print("✅ Token Creation: PASS")
    
    # Test token verification
    user_context = verify_test_token(token)
    assert user_context is not None, "Token should be valid"
    assert user_context.user_id == "user1", f"Expected user1, got {user_context.user_id}"
    assert user_context.email == "user1@example.com", "Email should match"
    assert user_context.plan == "free", "Plan should match"
    print("✅ Token Verification: PASS")
    
    # Test invalid token
    invalid_user = verify_test_token("invalid-token")
    assert invalid_user is None, "Invalid token should return None"
    print("✅ Invalid Token Handling: PASS")


def test_api_endpoints():
    """Test API endpoints work correctly"""
    print("🧪 Testing API Endpoints...")
    
    app = FastAPI(lifespan=lifespan)
    register(app)
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/test-extension/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", f"Health status should be ok, got {data['status']}"
    print("✅ Health Endpoint: PASS")
    
    # Test info endpoint
    response = client.get("/test-extension/info")
    assert response.status_code == 200, f"Info endpoint failed: {response.status_code}"
    data = response.json()
    assert data["name"] == "OpenHands Test Extension", "Name should match"
    assert "Multi-user authentication demo" in data["features"], f"Should have multi-user auth feature, got {data['features']}"
    print("✅ Info Endpoint: PASS")
    
    # Test multiuser login
    response = client.post("/test-multiuser/login", params={"user_id": "user1"})
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    data = response.json()
    assert "access_token" in data, f"Login should return access_token, got {data}"
    print("✅ Login Endpoint: PASS")


async def main():
    """Run all tests"""
    print("🚀 Starting TestExtension Tests\n")
    
    try:
        await test_extension_lifecycle()
        print()
        
        test_jwt_functionality()
        print()
        
        test_api_endpoints()
        print()
        
        print("🎉 All Tests Passed!")
        
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)