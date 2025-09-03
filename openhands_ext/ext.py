from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/test-extension")

@router.get("/health")
async def health():
    return {"status": "ok", "component": "TestExtension"}


def register(app: FastAPI) -> None:
    app.include_router(router)
