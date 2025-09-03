from dataclasses import dataclass

from openhands.server.config.server_config import ServerConfig


@dataclass
class TestServerConfig(ServerConfig):
    """Example ServerConfig for tests.

    Guidance: Prefer fine-grained settings or component providers over subclassing in production.
    This class exists only to validate the extension mechanism.
    """

    # Example: override a component class if needed for demo purposes only.
    # conversation_manager_class: str = (
    #     "openhands_ext.test_components:TestConversationManager"
    # )

    # Avoid redefining app_mode here; let OH control SU/None auth in core.
    pass
