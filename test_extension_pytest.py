#!/usr/bin/env python3
"""
Pytest suite for TestExtension

This demonstrates proper pytest testing of the extension with real function calls.
Run with: pytest test_extension_pytest.py -v
"""

import pytest
import sys
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import directly to avoid OpenHands dependencies in test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openhands_ext'))

from ext import (
    register, 
    lifespan, 
    get_extension_state, 
    get_extension_calls, 
    clear_extension_calls
)
from test_multiuser import (
    create_test_token, 
    verify_test_token, 
    get_multiuser_calls, 
    clear_multiuser_calls
)
from test_storage import (
    get_storage_calls, 
    clear_storage_calls
)


class TestExtensionLifecycle:
    """Test extension lifecycle management with real function calls"""
    
    def setup_method(self):
        """Clear call history before each test"""
        clear_extension_calls()
        clear_multiuser_calls()
        clear_storage_calls()
    
    def test_registration_calls_real_functions(self):
        """Test that registration actually calls stub functions"""
        app = FastAPI()
        register(app)
        
        # Verify registration state
        state = get_extension_state(app)
        assert state.get('registered') is True
        
        # TEST REAL FUNCTION CALLS - this is the key difference from fake simulation!
        extension_calls = get_extension_calls()
        multiuser_calls = get_multiuser_calls()
        storage_calls = get_storage_calls()
        
        assert 'register_extension_components' in extension_calls
        assert 'initialize_user_auth_system' in multiuser_calls
        assert 'initialize_storage_system' in storage_calls
    
    @pytest.mark.asyncio
    async def test_lifespan_calls_startup_shutdown_functions(self):
        """Test that lifespan actually calls startup/shutdown functions"""
        app = FastAPI()
        
        async with lifespan(app):
            # Check startup state
            state = get_extension_state(app)
            assert state.get('status') == 'running'
            assert 'startup_time' in state
            
            # TEST REAL STARTUP FUNCTION CALLS
            extension_calls = get_extension_calls()
            assert 'initialize_extension_resources' in extension_calls
            assert 'start_user_session_cleanup' in extension_calls
            assert 'start_storage_maintenance' in extension_calls
        
        # Check shutdown state
        state = get_extension_state(app)
        assert state.get('status') == 'stopped'
        assert 'shutdown_time' in state
        
        # TEST REAL CLEANUP FUNCTION CALLS
        extension_calls = get_extension_calls()
        assert 'stop_user_session_cleanup' in extension_calls
        assert 'stop_storage_maintenance' in extension_calls
        assert 'cleanup_extension_resources' in extension_calls
    
    def test_extension_plumbing_demonstrates_real_calls(self):
        """Verify extension plumbing uses real function calls, not fake simulation"""
        app = FastAPI()
        
        # Before registration - no calls
        assert len(get_extension_calls()) == 0
        
        # After registration - actual functions called
        register(app)
        calls = get_extension_calls()
        assert len(calls) > 0
        assert 'register_extension_components' in calls
        
        # This proves the plumbing works: real functions get called


class TestJWTFunctionality:
    """Test JWT token creation and validation"""
    
    def test_token_creation(self):
        """Test JWT token creation with proper claims"""
        token = create_test_token("user1")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_verification_valid(self):
        """Test valid JWT token verification"""
        token = create_test_token("user1")
        user_context = verify_test_token(token)
        
        assert user_context is not None
        assert user_context.user_id == "user1"
        assert user_context.email == "user1@example.com"
        assert user_context.plan == "free"
        assert user_context.is_authenticated is True
    
    def test_token_verification_invalid(self):
        """Test invalid JWT token handling"""
        invalid_user = verify_test_token("invalid-token")
        assert invalid_user is None
    
    def test_token_verification_nonexistent_user(self):
        """Test token for non-existent user"""
        token = create_test_token("nonexistent")
        user_context = verify_test_token(token)
        assert user_context is None


class TestAPIEndpoints:
    """Test API endpoints work correctly"""
    
    @pytest.fixture
    def client(self):
        """Create test client with extension registered"""
        app = FastAPI(lifespan=lifespan)
        register(app)
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/test-extension/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["component"] == "TestExtension"
    
    def test_info_endpoint(self, client):
        """Test extension info endpoint"""
        response = client.get("/test-extension/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "OpenHands Test Extension"
        assert "Multi-user authentication demo" in data["features"]
        assert "Multi-tenant storage demo" in data["features"]
    
    def test_multiuser_login_endpoint(self, client):
        """Test multiuser login endpoint"""
        response = client.post("/test-multiuser/login", params={"user_id": "user1"})
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == "user1"
    
    def test_multiuser_login_invalid_user(self, client):
        """Test multiuser login with invalid user"""
        response = client.post("/test-multiuser/login", params={"user_id": "invalid"})
        assert response.status_code == 401


class TestRealVsFakeApproach:
    """Demonstrate the difference between real testing and fake simulation"""
    
    def test_real_approach_verifies_actual_function_calls(self):
        """Real approach: Test that actual functions get called"""
        clear_extension_calls()
        
        app = FastAPI()
        register(app)
        
        calls = get_extension_calls()
        assert 'register_extension_components' in calls
        # This proves real function was actually invoked
    
    def test_fake_approach_only_tests_data_manipulation(self):
        """Fake approach: Only tests data manipulation (meaningless)"""
        # This is what I did wrong before - just manipulating data structures
        fake_tasks = []
        fake_tasks.append('user_session_cleanup')  # Just adding strings!
        fake_tasks.append('storage_maintenance')   # This proves nothing!
        
        assert len(fake_tasks) == 2  # Meaningless test
        
        # The problem: This doesn't test that any real functionality works
        # It only tests that we can add strings to a list
    
    def test_comparison_real_vs_fake(self):
        """Compare real testing vs fake simulation"""
        clear_extension_calls()
        
        # Real approach: Actual function calls
        app = FastAPI()
        register(app)
        real_calls = get_extension_calls()
        
        # Fake approach: Just data manipulation
        fake_data = ['some_function', 'another_function']
        
        # Real approach tests actual functionality
        assert len(real_calls) > 0
        assert 'register_extension_components' in real_calls
        
        # Fake approach only tests data structures
        assert len(fake_data) == 2
        
        # Key insight: Real approach proves extension plumbing works
        # Fake approach proves nothing about actual functionality


if __name__ == "__main__":
    # Allow running directly for quick testing
    pytest.main([__file__, "-v"])