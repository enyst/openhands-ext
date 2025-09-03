"""
TestExtension: Multi-Tenant Storage Demo

This demonstrates how enterprise storage functionality could be 
implemented as a clean extension with proper tenant isolation.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path

router = APIRouter(prefix="/test-storage")

@dataclass
class TestSettings:
    """Test settings model"""
    user_id: str
    theme: str = "dark"
    language: str = "en"
    notifications: bool = True
    api_keys: Dict[str, str] = None
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = {}

class TestStorageManager:
    """
    Test storage manager that demonstrates multi-tenant storage patterns
    In enterprise, this would be a database with proper encryption
    """
    
    def __init__(self, base_path: str = "/tmp/openhands-test-storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def _get_user_path(self, user_id: str) -> Path:
        """Get user-specific storage path (tenant isolation)"""
        user_path = self.base_path / f"user_{user_id}"
        user_path.mkdir(exist_ok=True)
        return user_path
    
    def _get_settings_file(self, user_id: str) -> Path:
        """Get user settings file path"""
        return self._get_user_path(user_id) / "settings.json"
    
    def _get_secrets_file(self, user_id: str) -> Path:
        """Get user secrets file path"""
        return self._get_user_path(user_id) / "secrets.json"
    
    def save_settings(self, user_id: str, settings: TestSettings) -> None:
        """Save user settings with tenant isolation"""
        settings_file = self._get_settings_file(user_id)
        settings_data = asdict(settings)
        # Remove sensitive data from settings
        settings_data.pop('api_keys', None)
        
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f, indent=2)
    
    def load_settings(self, user_id: str) -> TestSettings:
        """Load user settings with tenant isolation"""
        settings_file = self._get_settings_file(user_id)
        
        if not settings_file.exists():
            return TestSettings(user_id=user_id)
        
        with open(settings_file, 'r') as f:
            data = json.load(f)
        
        return TestSettings(**data)
    
    def save_secrets(self, user_id: str, secrets: Dict[str, str]) -> None:
        """Save user secrets (encrypted in enterprise)"""
        secrets_file = self._get_secrets_file(user_id)
        
        # In enterprise, this would be encrypted
        with open(secrets_file, 'w') as f:
            json.dump(secrets, f, indent=2)
    
    def load_secrets(self, user_id: str) -> Dict[str, str]:
        """Load user secrets (decrypted in enterprise)"""
        secrets_file = self._get_secrets_file(user_id)
        
        if not secrets_file.exists():
            return {}
        
        with open(secrets_file, 'r') as f:
            return json.load(f)
    
    def list_user_data(self, user_id: str) -> Dict[str, Any]:
        """List all user data (for admin/debugging)"""
        user_path = self._get_user_path(user_id)
        
        data = {
            "user_id": user_id,
            "storage_path": str(user_path),
            "files": []
        }
        
        for file_path in user_path.iterdir():
            if file_path.is_file():
                data["files"].append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return data

# Global storage manager instance
storage_manager = TestStorageManager()

# Mock user dependency (in real extension, would integrate with auth)
async def get_test_user_id() -> str:
    """Mock user ID for testing - in real extension would come from auth"""
    return "test_user_123"

@router.get("/settings")
async def get_settings(user_id: str = Depends(get_test_user_id)):
    """Get user settings with tenant isolation"""
    settings = storage_manager.load_settings(user_id)
    return asdict(settings)

@router.put("/settings")
async def update_settings(
    settings_data: dict,
    user_id: str = Depends(get_test_user_id)
):
    """Update user settings with tenant isolation"""
    try:
        # Load current settings
        current_settings = storage_manager.load_settings(user_id)
        
        # Update with new data
        for key, value in settings_data.items():
            if hasattr(current_settings, key) and key != 'user_id':
                setattr(current_settings, key, value)
        
        # Save updated settings
        storage_manager.save_settings(user_id, current_settings)
        
        return {"message": "Settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/secrets")
async def get_secrets(user_id: str = Depends(get_test_user_id)):
    """Get user secrets (keys only, not values)"""
    secrets = storage_manager.load_secrets(user_id)
    # Return only keys for security
    return {"keys": list(secrets.keys())}

@router.put("/secrets/{key}")
async def set_secret(
    key: str,
    value: dict,  # {"value": "secret_value"}
    user_id: str = Depends(get_test_user_id)
):
    """Set a user secret with tenant isolation"""
    secrets = storage_manager.load_secrets(user_id)
    secrets[key] = value.get("value", "")
    storage_manager.save_secrets(user_id, secrets)
    
    return {"message": f"Secret '{key}' saved successfully"}

@router.delete("/secrets/{key}")
async def delete_secret(
    key: str,
    user_id: str = Depends(get_test_user_id)
):
    """Delete a user secret"""
    secrets = storage_manager.load_secrets(user_id)
    
    if key not in secrets:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    del secrets[key]
    storage_manager.save_secrets(user_id, secrets)
    
    return {"message": f"Secret '{key}' deleted successfully"}

@router.get("/admin/user-data")
async def get_user_data(user_id: str = Depends(get_test_user_id)):
    """Get user data summary (admin endpoint)"""
    return storage_manager.list_user_data(user_id)

@router.get("/health")
async def storage_health():
    """Storage health check"""
    return {
        "status": "healthy",
        "storage_path": str(storage_manager.base_path),
        "writable": os.access(storage_manager.base_path, os.W_OK)
    }

def register(app):
    """Register the test storage extension"""
    app.include_router(router)
    print("TestExtension: Multi-tenant storage demo registered")