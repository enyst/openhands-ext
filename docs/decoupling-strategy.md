# OpenHands Enterprise Decoupling Strategy

## Executive Summary

This document outlines a comprehensive strategy for decoupling the OpenHands enterprise functionality (`/enterprise`) into clean, maintainable extensions while preserving both the open-source core's simplicity and the enterprise platform's capabilities.

## Current Architecture Problems

### 1. Tight Coupling Issues
- **Dynamic Override Pattern**: Enterprise uses `OPENHANDS_CONFIG_CLS` to completely replace core components
- **Import Dependencies**: Enterprise code directly imports and extends OSS internals
- **Shared State**: Both OSS and enterprise share database models and storage systems
- **Configuration Complexity**: 50+ environment variables with complex conditional loading

### 2. Architectural Brittleness
- **API Dependencies**: Enterprise relies on specific OSS internal APIs that could change
- **Middleware Conflicts**: Stacking enterprise middleware on OSS can cause conflicts
- **Monolithic Structure**: Single enterprise directory contains everything from auth to billing
- **Testing Complexity**: Difficult to test enterprise features in isolation

### 3. Development Workflow Issues
- **Deployment Coupling**: Enterprise deployment requires OSS codebase
- **Version Synchronization**: Enterprise and OSS versions must be kept in sync
- **Development Environment**: Complex setup with multiple interdependent components

## Proposed Solution: Graduated Extension Architecture

### Phase 1: Extension Foundation (Immediate - 2-4 weeks)

#### 1.1 Implement Extension Discovery in OpenHands OSS

```python
# openhands/server/extensions.py
import os
import pkg_resources
from typing import List, Callable
from fastapi import FastAPI

def load_extensions(app: FastAPI) -> List[str]:
    """Load and register all available extensions"""
    loaded_extensions = []
    
    # Environment variable discovery (for development)
    extensions_env = os.getenv('OPENHANDS_EXTENSIONS', '')
    for ext in extensions_env.split(','):
        if ext.strip():
            try:
                register_func = import_from(ext.strip())
                register_func(app)
                loaded_extensions.append(ext.strip())
            except Exception as e:
                logger.warning(f"Failed to load extension {ext}: {e}")
    
    # Entry point discovery (for production)
    for entry_point in pkg_resources.iter_entry_points('openhands_server_extensions'):
        try:
            register_func = entry_point.load()
            register_func(app)
            loaded_extensions.append(entry_point.name)
        except Exception as e:
            logger.warning(f"Failed to load extension {entry_point.name}: {e}")
    
    return loaded_extensions
```

#### 1.2 Integrate Extension Loading into Server Startup

```python
# openhands/server/app.py (modify existing)
from openhands.server.extensions import load_extensions

# Add after existing route registrations
loaded_extensions = load_extensions(app)
logger.info(f"Loaded extensions: {loaded_extensions}")
```

#### 1.3 Create Extension Interface Standards

```python
# openhands/server/extension_interface.py
from abc import ABC, abstractmethod
from fastapi import FastAPI
from typing import Dict, Any, Optional

class ExtensionInterface(ABC):
    """Base interface for OpenHands extensions"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Extension name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Extension version"""
        pass
    
    @abstractmethod
    def register(self, app: FastAPI) -> None:
        """Register extension with the FastAPI app"""
        pass
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return configuration schema for this extension"""
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status of this extension"""
        return {"status": "ok"}
```

### Phase 2: Core Interface Abstraction (Short-term - 4-8 weeks)

#### 2.1 User Context Interface

```python
# openhands/server/user_context.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum

class UserMode(Enum):
    SINGLE_USER = "single_user"
    MULTI_USER = "multi_user"

class UserContext(ABC):
    """Abstract user context - can be single-user or multi-user"""
    
    @property
    @abstractmethod
    def user_id(self) -> str:
        """Unique user identifier"""
        pass
    
    @property
    @abstractmethod
    def mode(self) -> UserMode:
        """User mode (single or multi-user)"""
        pass
    
    @property
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Whether user is authenticated"""
        pass

class SingleUserContext(UserContext):
    """Single-user context for OSS mode"""
    
    def __init__(self):
        self._user_id = "default_user"
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def mode(self) -> UserMode:
        return UserMode.SINGLE_USER
    
    @property
    def is_authenticated(self) -> bool:
        return True  # Always authenticated in single-user mode

class MultiUserContext(UserContext):
    """Multi-user context for enterprise extensions"""
    
    def __init__(self, user_id: str, email: Optional[str] = None, 
                 plan: Optional[str] = None, **kwargs):
        self._user_id = user_id
        self.email = email
        self.plan = plan
        self.metadata = kwargs
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def mode(self) -> UserMode:
        return UserMode.MULTI_USER
    
    @property
    def is_authenticated(self) -> bool:
        return bool(self._user_id)
```

#### 2.2 Storage Interface Abstraction

```python
# openhands/storage/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from openhands.server.user_context import UserContext
from openhands.core.config import OpenHandsConfig

class SettingsStoreInterface(ABC):
    """Abstract interface for settings storage"""
    
    @abstractmethod
    async def load(self, user_context: UserContext) -> Optional[OpenHandsConfig]:
        """Load user settings"""
        pass
    
    @abstractmethod
    async def save(self, user_context: UserContext, config: OpenHandsConfig) -> None:
        """Save user settings"""
        pass

class SecretsStoreInterface(ABC):
    """Abstract interface for secrets storage"""
    
    @abstractmethod
    async def get_secret(self, user_context: UserContext, key: str) -> Optional[str]:
        """Get a secret value"""
        pass
    
    @abstractmethod
    async def set_secret(self, user_context: UserContext, key: str, value: str) -> None:
        """Set a secret value"""
        pass
    
    @abstractmethod
    async def delete_secret(self, user_context: UserContext, key: str) -> None:
        """Delete a secret"""
        pass

class ConversationStoreInterface(ABC):
    """Abstract interface for conversation storage"""
    
    @abstractmethod
    async def save_conversation(self, user_context: UserContext, 
                              conversation_id: str, data: Dict[str, Any]) -> None:
        """Save conversation data"""
        pass
    
    @abstractmethod
    async def load_conversation(self, user_context: UserContext, 
                              conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data"""
        pass
    
    @abstractmethod
    async def list_conversations(self, user_context: UserContext) -> List[str]:
        """List user's conversations"""
        pass
```

#### 2.3 Authentication Interface

```python
# openhands/server/auth/interface.py
from abc import ABC, abstractmethod
from fastapi import Request
from openhands.server.user_context import UserContext

class AuthenticationInterface(ABC):
    """Abstract authentication interface"""
    
    @abstractmethod
    async def authenticate(self, request: Request) -> UserContext:
        """Authenticate request and return user context"""
        pass
    
    @abstractmethod
    async def get_auth_routes(self) -> Optional[APIRouter]:
        """Return authentication routes (login, logout, etc.)"""
        pass

class SingleUserAuth(AuthenticationInterface):
    """Single-user authentication for OSS"""
    
    async def authenticate(self, request: Request) -> UserContext:
        return SingleUserContext()
    
    async def get_auth_routes(self) -> Optional[APIRouter]:
        return None  # No auth routes needed for single-user
```

### Phase 3: Enterprise Extension Implementation (Medium-term - 8-12 weeks)

#### 3.1 Create Enterprise Extension Package

```
openhands-enterprise/
├── pyproject.toml
├── openhands_enterprise/
│   ├── __init__.py
│   ├── extension.py          # Main extension registration
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth.py          # OAuth providers
│   │   ├── sso.py            # Enterprise SSO
│   │   └── jwt_auth.py       # JWT authentication
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py       # Database connection
│   │   ├── settings_store.py # Multi-tenant settings
│   │   ├── secrets_store.py  # Encrypted secrets
│   │   └── conversation_store.py # Conversation storage
│   ├── billing/
│   │   ├── __init__.py
│   │   ├── stripe_integration.py
│   │   └── usage_tracking.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── github.py
│   │   ├── gitlab.py
│   │   ├── jira.py
│   │   └── slack.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── billing.py
│       ├── admin.py
│       └── webhooks.py
```

#### 3.2 Enterprise Extension Registration

```python
# openhands_enterprise/extension.py
from fastapi import FastAPI
from openhands.server.extension_interface import ExtensionInterface
from .auth.jwt_auth import EnterpriseAuth
from .storage import EnterpriseStorageFactory
from .routes import auth_router, billing_router, admin_router

class EnterpriseExtension(ExtensionInterface):
    """OpenHands Enterprise Extension"""
    
    @property
    def name(self) -> str:
        return "openhands-enterprise"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def register(self, app: FastAPI) -> None:
        """Register enterprise functionality"""
        
        # Register authentication
        auth = EnterpriseAuth()
        app.dependency_overrides[get_user_context] = auth.authenticate
        
        # Register storage implementations
        storage_factory = EnterpriseStorageFactory()
        app.dependency_overrides[get_settings_store] = storage_factory.get_settings_store
        app.dependency_overrides[get_secrets_store] = storage_factory.get_secrets_store
        
        # Register routes
        app.include_router(auth_router)
        app.include_router(billing_router)
        app.include_router(admin_router)
        
        # Add middleware
        app.add_middleware(EnterpriseAuthMiddleware)
        app.add_middleware(RateLimitMiddleware)
        
        print("Enterprise extension registered successfully")

# Entry point for extension discovery
def register(app: FastAPI) -> None:
    extension = EnterpriseExtension()
    extension.register(app)
```

### Phase 4: Migration Strategy (Long-term - 12-16 weeks)

#### 4.1 Gradual Migration Plan

1. **Week 1-2**: Implement extension discovery in OSS
2. **Week 3-4**: Create basic interfaces and TestExtension
3. **Week 5-8**: Migrate authentication system to interface
4. **Week 9-12**: Migrate storage systems to interface
5. **Week 13-16**: Extract enterprise functionality to separate package

#### 4.2 Backward Compatibility

```python
# Maintain backward compatibility during migration
class LegacyConfigSupport:
    """Support for legacy OPENHANDS_CONFIG_CLS during migration"""
    
    def __init__(self):
        self.legacy_config_cls = os.getenv('OPENHANDS_CONFIG_CLS')
        if self.legacy_config_cls:
            warnings.warn(
                "OPENHANDS_CONFIG_CLS is deprecated. Use extension entry points instead.",
                DeprecationWarning
            )
    
    def load_legacy_config(self, app: FastAPI):
        if self.legacy_config_cls:
            # Load legacy configuration
            config_cls = import_from(self.legacy_config_cls)
            # Convert to new extension format
            self.convert_legacy_to_extension(app, config_cls)
```

## Benefits of This Approach

### 1. Clean Separation of Concerns
- **OSS Core**: Remains simple, single-user focused
- **Extensions**: Handle complex multi-user, enterprise features
- **Interfaces**: Provide clean contracts between components

### 2. Independent Development
- **Separate Repositories**: Enterprise can be developed independently
- **Version Independence**: Extensions can have their own release cycles
- **Testing Isolation**: Each component can be tested independently

### 3. Deployment Flexibility
- **Modular Deployment**: Deploy only needed extensions
- **Configuration Simplicity**: Extensions manage their own configuration
- **Scaling Options**: Different scaling strategies for different components

### 4. Maintainability
- **Clear Boundaries**: Well-defined interfaces prevent coupling
- **Extensibility**: New extensions can be added without core changes
- **Backward Compatibility**: Gradual migration path preserves existing functionality

## Implementation Priorities

### High Priority (Phase 1)
1. Extension discovery mechanism
2. Basic extension interface
3. TestExtension proof of concept

### Medium Priority (Phase 2)
1. User context abstraction
2. Storage interface abstraction
3. Authentication interface

### Lower Priority (Phase 3-4)
1. Full enterprise extension implementation
2. Migration of existing enterprise code
3. Deprecation of legacy systems

## Success Metrics

1. **Decoupling**: Enterprise functionality runs as independent extension
2. **Maintainability**: OSS core remains simple and focused
3. **Extensibility**: New extensions can be added easily
4. **Performance**: No significant performance degradation
5. **Developer Experience**: Improved development workflow for both OSS and enterprise

## Conclusion

This graduated approach allows for a smooth transition from the current tightly-coupled architecture to a clean, extensible system. The TestExtension demonstrates the feasibility of the approach, while the phased implementation plan ensures minimal disruption to existing functionality.

The key insight is that OpenHands can maintain its simplicity for single-user scenarios while supporting complex enterprise features through well-designed extensions. This approach benefits both the open-source community and enterprise customers.