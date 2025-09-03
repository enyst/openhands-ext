from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import socketio

from openhands.core.config.openhands_config import OpenHandsConfig
from openhands.core.config.llm_config import LLMConfig
from openhands.events.action import MessageAction
from openhands.server.config.server_config import ServerConfig
from openhands.server.conversation_manager.conversation_manager import (
    ConversationManager,
)
from openhands.server.data_models.agent_loop_info import AgentLoopInfo
from openhands.server.monitoring import MonitoringListener
from openhands.server.session.agent_session import AgentSession
from openhands.server.session.conversation import ServerConversation
from openhands.storage.conversation.conversation_store import ConversationStore
from openhands.storage.data_models.settings import Settings
from openhands.storage.files import FileStore


class TestConversationManager(ConversationManager):
    """A tiny ConversationManager stub for demonstrating component substitution.

    DO NOT use in production. This is only to prove that extensions can provide
    custom managers without copying enterprise logic.
    """

    def __init__(
        self,
        sio: socketio.AsyncServer,
        config: OpenHandsConfig,
        file_store: FileStore,
        server_config: ServerConfig,
        monitoring_listener: MonitoringListener,
    ) -> None:
        self.sio = sio
        self.config = config
        self.file_store = file_store
        self.server_config = server_config
        self.monitoring_listener = monitoring_listener
        self._sessions: dict[str, AgentSession] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._sessions.clear()

    async def attach_to_conversation(self, sid: str, user_id: str | None = None) -> ServerConversation | None:  # noqa: E501
        # For demo: always create a minimal ServerConversation that does nothing.
        # NOTE: We must initialize ServerConversation with OpenHandsConfig and user_id per OH API.
        # This stub intentionally does not start an agent loop.
        return ServerConversation(sid=sid, file_store=self.file_store, config=self.config, user_id=user_id)

    async def detach_from_conversation(self, conversation: ServerConversation):
        return None

    async def join_conversation(
        self,
        sid: str,
        connection_id: str,
        settings: Settings,
        user_id: str | None,
    ) -> AgentLoopInfo | None:
        # Demo: return an empty loop info
        return AgentLoopInfo(session_id=sid, connection_id=connection_id, is_running=False)

    async def is_agent_loop_running(self, sid: str) -> bool:
        return False

    async def get_running_agent_loops(
        self, user_id: str | None = None, filter_to_sids: set[str] | None = None
    ) -> set[str]:
        return set()

    async def get_connections(
        self, user_id: str | None = None, filter_to_sids: set[str] | None = None
    ) -> dict[str, str]:
        return {}

    async def maybe_start_agent_loop(
        self,
        sid: str,
        settings: Settings,
        user_id: str | None,
        initial_user_msg: MessageAction | None = None,
        replay_json: str | None = None,
    ) -> AgentLoopInfo:
        return AgentLoopInfo(session_id=sid, connection_id="demo", is_running=False)

    async def send_to_event_stream(self, connection_id: str, data: dict):
        return None

    async def send_event_to_conversation(self, sid: str, data: dict):
        return None

    async def disconnect_from_session(self, connection_id: str):
        return None

    async def close_session(self, sid: str):
        return None

    def get_agent_session(self, sid: str) -> AgentSession | None:
        return None

    async def get_agent_loop_info(
        self, user_id: str | None = None, filter_to_sids: set[str] | None = None
    ) -> list[AgentLoopInfo]:
        return []

    async def request_llm_completion(
        self,
        sid: str,
        service_id: str,
        llm_config: LLMConfig,
        messages: list[dict[str, str]],
    ) -> str:
        return ""

    @classmethod
    def get_instance(
        cls,
        sio: socketio.AsyncServer,
        config: OpenHandsConfig,
        file_store: FileStore,
        server_config: ServerConfig,
        monitoring_listener: MonitoringListener,
    ) -> ConversationManager:
        return cls(sio, config, file_store, server_config, monitoring_listener)
