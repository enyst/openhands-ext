# OpenHands Enterprise Integration Patterns - Deep Dive

This document provides a comprehensive analysis of how the OpenHands enterprise system integrates with, overrides, and extends the core OpenHands OSS codebase.

## Table of Contents

1. [Core Integration Mechanism](#core-integration-mechanism)
2. [Configuration Override System](#configuration-override-system)
3. [Class Override Patterns](#class-override-patterns)
4. [Environment Variables Mapping](#environment-variables-mapping)
5. [Server Integration Architecture](#server-integration-architecture)
6. [Storage Layer Overrides](#storage-layer-overrides)
7. [Authentication System Override](#authentication-system-override)
8. [Middleware Integration](#middleware-integration)
9. [Route Extensions](#route-extensions)
10. [Monitoring and Experiments](#monitoring-and-experiments)

## Core Integration Mechanism

### Dynamic Import System (`get_impl`)

The enterprise system leverages OpenHands' built-in extensibility mechanism through the `get_impl` function in `openhands/utils/import_utils.py`:

```python
@lru_cache()
def get_impl(cls: type[T], impl_name: str | None) -> type[T]:
    """Import and validate a named implementation of a base class."""
    if impl_name is None:
        return cls
    impl_class = import_from(impl_name)
    assert cls == impl_class or issubclass(impl_class, cls)
    return impl_class
```

**Key Integration Points:**
- **Server Configuration**: `OPENHANDS_CONFIG_CLS` environment variable
- **User Authentication**: `user_auth_class` in server config
- **Conversation Management**: `conversation_manager_class` in server config
- **Storage Stores**: `settings_store_class`, `secret_store_class`, `conversation_store_class`
- **Monitoring**: `monitoring_listener_class` in server config

### Entry Point Override

The enterprise system completely replaces the main server entry point:
- **OSS**: Uses `openhands/server/app.py` directly
- **Enterprise**: Uses `enterprise/saas_server.py` which imports and extends the OSS app

## Configuration Override System

### Server Configuration Hierarchy

#### OSS Base Configuration (`openhands/server/config/server_config.py`)
```python
class ServerConfig(ServerConfigInterface):
    config_cls = os.environ.get('OPENHANDS_CONFIG_CLS', None)
    app_mode = AppMode.OSS
    posthog_client_key = 'phc_3ESMmY9SgqEAGBB6sMGK5ayYHkeUuknH2vP6FmWH9RA'
    github_client_id = os.environ.get('GITHUB_APP_CLIENT_ID', '')
    enable_billing = os.environ.get('ENABLE_BILLING', 'false') == 'true'
    hide_llm_settings = os.environ.get('HIDE_LLM_SETTINGS', 'false') == 'true'
    
    # Default OSS implementations
    settings_store_class: str = 'openhands.storage.settings.file_settings_store.FileSettingsStore'
    secret_store_class: str = 'openhands.storage.secrets.file_secrets_store.FileSecretsStore'
    conversation_store_class: str = 'openhands.storage.conversation.file_conversation_store.FileConversationStore'
    conversation_manager_class: str = 'openhands.server.conversation_manager.standalone_conversation_manager.StandaloneConversationManager'
    monitoring_listener_class: str = 'openhands.server.monitoring.MonitoringListener'
    user_auth_class: str = 'openhands.server.user_auth.default_user_auth.DefaultUserAuth'
```

#### Enterprise Configuration Override (`enterprise/server/config.py`)
```python
class SaaSServerConfig(ServerConfig):
    config_cls: str = os.environ.get('OPENHANDS_CONFIG_CLS', '')
    app_mode: AppMode = AppMode.SAAS
    posthog_client_key: str = os.environ.get('POSTHOG_CLIENT_KEY', '')
    
    # Enterprise-specific overrides
    settings_store_class: str = 'storage.saas_settings_store.SaasSettingsStore'
    secret_store_class: str = 'storage.saas_secrets_store.SaasSecretsStore'
    conversation_store_class: str = 'storage.saas_conversation_store.SaasConversationStore'
    conversation_manager_class: str = 'server.clustered_conversation_manager.ClusteredConversationManager'
    monitoring_listener_class: str = 'server.saas_monitoring_listener.SaaSMonitoringListener'
    user_auth_class: str = 'server.auth.saas_user_auth.SaasUserAuth'
    
    # Enterprise-specific features
    stripe_publishable_key: str = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    auth_url: str | None = os.environ.get('AUTH_URL')
    maintenance_start_time: str = os.environ.get('MAINTENANCE_START_TIME', '')
    enable_jira = ENABLE_JIRA
    enable_jira_dc = ENABLE_JIRA_DC
    enable_linear = ENABLE_LINEAR
```

### Configuration Loading Process

1. **Environment Variable Check**: `OPENHANDS_CONFIG_CLS` determines which config class to use
2. **Dynamic Loading**: `load_server_config()` uses `get_impl()` to instantiate the correct config class
3. **Validation**: Each config class validates its required environment variables
4. **Shared State**: The config is loaded once in `openhands/server/shared.py` and used throughout

## Class Override Patterns

### 1. User Authentication Override

**OSS Implementation** (`openhands/server/user_auth/default_user_auth.py`):
- Simple file-based authentication
- No external identity providers
- Basic session management

**Enterprise Implementation** (`enterprise/server/auth/saas_user_auth.py`):
- Keycloak integration for SSO
- OAuth providers (GitHub, GitLab, Bitbucket)
- JWT token management
- Rate limiting
- Multi-tenant user isolation

### 2. Storage Layer Overrides

**OSS Storage** (File-based):
- `FileSettingsStore`: Local JSON files
- `FileSecretsStore`: Local encrypted files
- `FileConversationStore`: Local file storage

**Enterprise Storage** (Database-based):
- `SaasSettingsStore`: PostgreSQL with user isolation
- `SaasSecretsStore`: Encrypted database storage
- `SaasConversationStore`: Multi-tenant database storage

### 3. Conversation Manager Override

**OSS**: `StandaloneConversationManager`
- Single-server deployment
- In-memory conversation state
- Direct file system access

**Enterprise**: `ClusteredConversationManager`
- Multi-server deployment support
- Redis-backed session management
- Distributed conversation state
- Background task processing

### 4. Monitoring Override

**OSS**: Basic `MonitoringListener`
- Simple logging
- No external analytics

**Enterprise**: `SaaSMonitoringListener`
- PostHog integration
- A/B testing support
- Advanced metrics collection
- User behavior tracking

## Environment Variables Mapping

### Core Configuration Variables

| Variable | OSS Default | Enterprise Usage | Purpose |
|----------|-------------|------------------|---------|
| `OPENHANDS_CONFIG_CLS` | `None` | `enterprise.server.config.SaaSServerConfig` | Determines which config class to load |
| `APP_MODE` | `OSS` | `SAAS` | Controls feature availability |
| `ENABLE_BILLING` | `false` | `true` | Enables Stripe integration |
| `HIDE_LLM_SETTINGS` | `false` | `true` | Hides LLM config from users |

### Authentication & Identity

| Variable | Purpose | Required |
|----------|---------|----------|
| `GITHUB_APP_CLIENT_ID` | GitHub OAuth integration | Optional |
| `GITHUB_APP_CLIENT_SECRET` | GitHub OAuth secret | If GitHub enabled |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App private key | If GitHub enabled |
| `GITHUB_APP_WEBHOOK_SECRET` | GitHub webhook validation | If GitHub enabled |
| `GITLAB_APP_CLIENT_ID` | GitLab OAuth integration | Optional |
| `GITLAB_APP_CLIENT_SECRET` | GitLab OAuth secret | If GitLab enabled |
| `BITBUCKET_APP_CLIENT_ID` | Bitbucket OAuth integration | Optional |
| `BITBUCKET_APP_CLIENT_SECRET` | Bitbucket OAuth secret | If Bitbucket enabled |
| `KEYCLOAK_SERVER_URL` | Keycloak server endpoint | If SSO enabled |
| `KEYCLOAK_REALM_NAME` | Keycloak realm | If SSO enabled |
| `KEYCLOAK_CLIENT_ID` | Keycloak client ID | If SSO enabled |
| `KEYCLOAK_CLIENT_SECRET` | Keycloak client secret | If SSO enabled |
| `ENABLE_ENTERPRISE_SSO` | Enable Keycloak SSO | Optional |
| `AUTH_URL` | External auth service URL | Optional |

### Database Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `openhands` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASS` | Database password | Required |
| `DB_POOL_SIZE` | Connection pool size | `10` |
| `DB_MAX_OVERFLOW` | Max overflow connections | `20` |

### Redis Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `REDIS_HOST` | Redis server host | None (disables clustering) |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_PASSWORD` | Redis password | None |
| `REDIS_DB` | Redis database number | `0` |

### External Integrations

| Variable | Purpose | Required |
|----------|---------|----------|
| `STRIPE_API_KEY` | Stripe payment processing | If billing enabled |
| `STRIPE_PUBLISHABLE_KEY` | Stripe frontend key | If billing enabled |
| `POSTHOG_CLIENT_KEY` | PostHog analytics | Yes |
| `POSTHOG_HOST` | PostHog server URL | Optional |
| `SLACK_CLIENT_ID` | Slack integration | If Slack enabled |
| `SLACK_CLIENT_SECRET` | Slack OAuth secret | If Slack enabled |
| `SLACK_SIGNING_SECRET` | Slack webhook validation | If Slack enabled |
| `JIRA_CLIENT_ID` | Jira Cloud integration | If Jira enabled |
| `JIRA_CLIENT_SECRET` | Jira Cloud secret | If Jira enabled |
| `JIRA_DC_CLIENT_ID` | Jira Data Center integration | If Jira DC enabled |
| `JIRA_DC_CLIENT_SECRET` | Jira DC secret | If Jira DC enabled |
| `JIRA_DC_BASE_URL` | Jira DC server URL | If Jira DC enabled |
| `LINEAR_CLIENT_ID` | Linear integration | If Linear enabled |
| `LINEAR_CLIENT_SECRET` | Linear secret | If Linear enabled |

### LiteLLM Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `LITE_LLM_API_URL` | LiteLLM proxy URL | `https://llm-proxy.app.all-hands.dev` |
| `LITE_LLM_API_KEY` | LiteLLM API key | Required |
| `LITE_LLM_TEAM_ID` | LiteLLM team identifier | Optional |
| `LITELLM_DEFAULT_MODEL` | Default model override | Calculated from version |

### Feature Flags

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENABLE_JIRA` | Enable Jira integration | `false` |
| `ENABLE_JIRA_DC` | Enable Jira Data Center | `false` |
| `ENABLE_LINEAR` | Enable Linear integration | `false` |
| `ENABLE_EXPERIMENT_MANAGER` | Enable A/B testing | `false` |
| `SLACK_WEBHOOKS_ENABLED` | Enable Slack webhooks | `false` |
| `GITHUB_WEBHOOKS_ENABLED` | Enable GitHub webhooks | `false` |
| `GITLAB_WEBHOOKS_ENABLED` | Enable GitLab webhooks | `false` |
| `JIRA_WEBHOOKS_ENABLED` | Enable Jira webhooks | `false` |
| `LINEAR_WEBHOOKS_ENABLED` | Enable Linear webhooks | `false` |

### Deployment Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `WEB_HOST` | Primary web hostname | `app.all-hands.dev` |
| `AUTH_WEB_HOST` | Auth service hostname | Same as WEB_HOST |
| `PERMITTED_CORS_ORIGINS` | Allowed CORS origins | `https://{WEB_HOST}` |
| `FRONTEND_DIRECTORY` | Frontend build directory | `./frontend/build` |
| `MAINTENANCE_START_TIME` | Maintenance window start | None |

### Experiments & A/B Testing

| Variable | Purpose | Default |
|----------|---------|---------|
| `EXPERIMENT_LITELLM_DEFAULT_MODEL_EXPERIMENT` | Model A/B test | None |
| `EXPERIMENT_SYSTEM_PROMPT_EXPERIMENT` | Prompt A/B test | None |
| `EXPERIMENT_CLAUDE4_VS_GPT5` | Model comparison test | None |

## Server Integration Architecture

### Application Composition

The enterprise system uses a composition pattern to extend the OSS application:

```python
# enterprise/saas_server.py
from openhands.server.app import app as base_app

# Add enterprise-specific routes
base_app.include_router(api_router)  # Auth routes
base_app.include_router(oauth_router)  # OAuth callbacks
base_app.include_router(billing_router)  # Stripe integration
base_app.include_router(github_integration_router)  # GitHub webhooks
# ... more enterprise routes

# Add enterprise middleware
base_app.add_middleware(CORSMiddleware, ...)
base_app.middleware('http')(SetAuthCookieMiddleware())

# Final ASGI app with SocketIO
app = socketio.ASGIApp(sio, other_asgi_app=base_app)
```

### Route Conditional Loading

Enterprise routes are conditionally loaded based on environment variables:

```python
# GitHub integration only if configured
if GITHUB_APP_CLIENT_ID:
    from server.routes.integration.github import github_integration_router
    base_app.include_router(github_integration_router)

# GitLab integration only if configured
if GITLAB_APP_CLIENT_ID:
    from server.routes.integration.gitlab import gitlab_integration_router
    base_app.include_router(gitlab_integration_router)

# Feature-specific integrations
if ENABLE_JIRA:
    base_app.include_router(jira_integration_router)
if ENABLE_JIRA_DC:
    base_app.include_router(jira_dc_integration_router)
if ENABLE_LINEAR:
    base_app.include_router(linear_integration_router)
```

### OSS Route Filtering

Some OSS routes are conditionally excluded in enterprise mode:

```python
# openhands/server/app.py
if server_config.app_mode == AppMode.OSS:
    app.include_router(git_api_router)  # Git routes only in OSS
```

## Storage Layer Overrides

### Database Models

Enterprise uses SQLAlchemy models with a unified base:

```python
# enterprise/storage/base.py
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# All enterprise models inherit from this base
class UserSettings(Base):
    __tablename__ = 'user_settings'
    # ... model definition

class StoredConversationMetadata(Base):
    __tablename__ = 'conversation_metadata'
    # ... model definition
```

### Store Implementation Pattern

Each store follows the same override pattern:

```python
@dataclass
class SaasSettingsStore(SettingsStore):
    user_id: str
    session_maker: sessionmaker
    config: OpenHandsConfig

    async def load(self) -> Settings | None:
        # Database-specific implementation
        with self.session_maker() as session:
            # Query user-specific settings
            # Apply encryption/decryption
            # Return Settings object
```

### Multi-tenancy Implementation

All enterprise stores implement user isolation:

1. **User ID Filtering**: All queries filter by `keycloak_user_id`
2. **Encryption**: Sensitive data is encrypted per-user
3. **Connection Pooling**: Shared database connections with user context
4. **Transaction Management**: Proper rollback on errors

## Authentication System Override

### Token Management

Enterprise authentication uses a sophisticated token management system:

```python
class SaasUserAuth(UserAuth):
    refresh_token: SecretStr
    user_id: str
    email: str | None = None
    email_verified: bool | None = None
    access_token: SecretStr | None = None
    provider_tokens: PROVIDER_TOKEN_TYPE | None = None
    refreshed: bool = False
```

### Authentication Flow

1. **Initial Authentication**: OAuth flow with external providers
2. **Token Exchange**: Exchange provider tokens for internal JWT
3. **Token Refresh**: Automatic refresh using refresh tokens
4. **Session Management**: Redis-backed session storage
5. **Rate Limiting**: Per-user rate limiting

### Provider Integration

Each OAuth provider has its own integration:

- **GitHub**: App installation flow, repository access
- **GitLab**: OAuth with repository sync
- **Bitbucket**: OAuth integration
- **Keycloak**: Enterprise SSO with SAML/OIDC

## Middleware Integration

### Authentication Middleware

The `SetAuthCookieMiddleware` handles:

1. **Cookie Validation**: JWT signature verification
2. **Token Refresh**: Automatic token renewal
3. **TOS Enforcement**: Terms of service acceptance
4. **Email Verification**: Email verification enforcement
5. **Error Handling**: Proper error responses and cookie cleanup

### Request Flow

```
Request → CORS Middleware → Cache Control → Auth Middleware → Route Handler
```

### Error Handling

Enterprise middleware provides comprehensive error handling:

- `NoCredentialsError`: 401 Unauthorized
- `ExpiredError`: 401 with token refresh
- `EmailNotVerifiedError`: 403 Forbidden
- `TosNotAcceptedError`: 403 with TOS prompt
- `AuthError`: 401 with cookie cleanup

## Route Extensions

### Enterprise-Specific Routes

| Route Prefix | Purpose | Module |
|--------------|---------|---------|
| `/api/auth` | Authentication endpoints | `server.routes.auth` |
| `/api/oauth` | OAuth callbacks | `server.routes.auth` |
| `/api/billing` | Stripe integration | `server.routes.billing` |
| `/api/user` | User management | `server.routes.user` |
| `/api/keys` | API key management | `server.routes.api_keys` |
| `/api/email` | Email management | `server.routes.email` |
| `/api/integration/github` | GitHub webhooks | `server.routes.integration.github` |
| `/api/integration/gitlab` | GitLab webhooks | `server.routes.integration.gitlab` |
| `/api/integration/jira` | Jira integration | `server.routes.integration.jira` |
| `/api/integration/slack` | Slack integration | `server.routes.integration.slack` |
| `/internal/metrics` | Prometheus metrics | `server.metrics` |

### Webhook Handling

Enterprise implements comprehensive webhook handling:

1. **Signature Verification**: HMAC signature validation
2. **Event Processing**: Async event processing
3. **Rate Limiting**: Per-source rate limiting
4. **Error Handling**: Retry logic and dead letter queues
5. **Audit Logging**: Complete audit trail

## Monitoring and Experiments

### PostHog Integration

Enterprise integrates PostHog for analytics:

```python
# experiments/constants.py
posthog.api_key = os.environ.get('POSTHOG_CLIENT_KEY', 'phc_placeholder')
posthog.host = os.environ.get('POSTHOG_HOST', 'https://us.i.posthog.com')
```

### A/B Testing Framework

The experiment manager supports:

1. **Model Experiments**: Different LLM models for different users
2. **Prompt Experiments**: System prompt variations
3. **Feature Experiments**: Feature flag-based experiments
4. **Cohort Management**: User segmentation for experiments

### Metrics Collection

Enterprise collects comprehensive metrics:

- **User Behavior**: Page views, feature usage, conversion funnels
- **System Performance**: Response times, error rates, resource usage
- **Business Metrics**: Billing events, subscription changes, churn
- **Integration Health**: Webhook success rates, API call volumes

## Key Integration Insights

### 1. Minimal OSS Modification

The enterprise system achieves complete functionality override without modifying OSS code by:
- Using the built-in `get_impl()` extensibility mechanism
- Leveraging environment variable-based configuration
- Composing rather than modifying the base application

### 2. Configuration-Driven Architecture

All integration points are controlled through:
- Environment variables for feature flags
- Class name strings for implementation selection
- Runtime configuration validation

### 3. Graceful Degradation

Enterprise features gracefully degrade when not configured:
- OAuth providers are optional
- Integrations are conditionally loaded
- Default implementations are always available

### 4. Multi-tenancy by Design

Every enterprise component is designed for multi-tenancy:
- User isolation at the database level
- Per-user encryption and secrets management
- Tenant-aware rate limiting and monitoring

### 5. Scalability Considerations

The architecture supports horizontal scaling:
- Redis-backed session management
- Database connection pooling
- Async webhook processing
- Distributed conversation management

This integration pattern allows OpenHands to maintain a clean separation between OSS and enterprise functionality while providing a seamless user experience and comprehensive enterprise features.