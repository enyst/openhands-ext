from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import APIRouter


@dataclass
class ComponentContribution:
    # Additive
    routers: list[tuple[str, APIRouter]]

    # Singletons (first-wins). Simple demo: name strings.
    conversation_manager_name: Optional[str] = None


def get_test_contribution() -> ComponentContribution:
    # Demo contribution that could be discovered later by OH loader
    router = APIRouter(prefix="/ext/test-di")

    @router.get("/ctx")
    def _ctx_probe():
        return {"ok": True}

    return ComponentContribution(routers=[("/", router)], conversation_manager_name="TestConversationManager")
