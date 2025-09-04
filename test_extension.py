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

from ext import register, lifespan, get_extension_state, get_extension_calls, clear_extension_calls
from test_multiuser import create_test_token, verify_test_token, get_multiuser_calls, clear_multiuser_calls
from test_storage import get_storage_calls, clear_storage_calls


async def test_extension_lifecycle():
    """Test extension lifecycle management - REAL FUNCTION CALLS"""
    print("🧪 Testing Extension Lifecycle...")
    
    # Clear call history before testing
    clear_extension_calls()
    clear_multiuser_calls()
    clear_storage_calls()
    
    app = FastAPI()
    
    # Test registration - check that actual functions were called
    register(app)
    
    # Verify registration state
    state = get_extension_state(app)
    assert state.get('registered') is True, "Extension should be registered"
    
    # TEST REAL FUNCTION CALLS - this is the key difference!
    extension_calls = get_extension_calls()
    multiuser_calls = get_multiuser_calls()
    storage_calls = get_storage_calls()
    
    assert 'register_extension_components' in extension_calls, f"Should call register_extension_components, got {extension_calls}"
    assert 'initialize_user_auth_system' in multiuser_calls, f"Should call initialize_user_auth_system, got {multiuser_calls}"
    assert 'initialize_storage_system' in storage_calls, f"Should call initialize_storage_system, got {storage_calls}"
    print("✅ Registration Function Calls: PASS")
    
    # Test lifespan - check that actual startup/shutdown functions were called
    async with lifespan(app):
        state = get_extension_state(app)
        assert state.get('status') == 'running', f"Expected 'running', got {state.get('status')}"
        assert 'startup_time' in state, "Should have startup_time"
        
        # TEST REAL STARTUP FUNCTION CALLS
        extension_calls = get_extension_calls()
        assert 'initialize_extension_resources' in extension_calls, f"Should call initialize_extension_resources, got {extension_calls}"
        assert 'start_user_session_cleanup' in extension_calls, f"Should call start_user_session_cleanup, got {extension_calls}"
        assert 'start_storage_maintenance' in extension_calls, f"Should call start_storage_maintenance, got {extension_calls}"
        print("✅ Startup Function Calls: PASS")
    
    # Check shutdown - verify cleanup functions were actually called
    state = get_extension_state(app)
    assert state.get('status') == 'stopped', f"Expected 'stopped', got {state.get('status')}"
    assert 'shutdown_time' in state, "Should have shutdown_time"
    
    # TEST REAL CLEANUP FUNCTION CALLS
    extension_calls = get_extension_calls()
    assert 'stop_user_session_cleanup' in extension_calls, f"Should call stop_user_session_cleanup, got {extension_calls}"
    assert 'stop_storage_maintenance' in extension_calls, f"Should call stop_storage_maintenance, got {extension_calls}"
    assert 'cleanup_extension_resources' in extension_calls, f"Should call cleanup_extension_resources, got {extension_calls}"
    print("✅ Shutdown Function Calls: PASS")


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


def test_real_vs_fake_approach():
    """Demonstrate the difference between real testing and fake simulation"""
    print("🧪 Testing Real vs Fake Approach...")
    
    clear_extension_calls()
    
    # REAL APPROACH: Test actual function calls
    app = FastAPI()
    register(app)
    
    calls = get_extension_calls()
    assert 'register_extension_components' in calls, "Real approach: function actually called"
    print("✅ Real Approach: Actual function calls verified")
    
    # FAKE APPROACH (what I did wrong before): Just manipulating data
    fake_tasks = []
    fake_tasks.append('user_session_cleanup')  # This is just adding strings!
    fake_tasks.append('storage_maintenance')   # This proves nothing!
    
    assert len(fake_tasks) == 2, "Fake approach: just counting strings in a list"
    print("❌ Fake Approach: Only tests data manipulation, not real functionality")
    
    # The difference:
    # - Real approach: Tests that actual functions get called (extension plumbing works)
    # - Fake approach: Tests that we can add strings to lists (meaningless)
    print("✅ Real vs Fake Comparison: PASS")


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
        
        test_real_vs_fake_approach()
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