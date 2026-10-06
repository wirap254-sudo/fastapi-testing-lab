import secrets
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from app.auth import USERS

def create_auth_router(token_store: set[str]) -> APIRouter:
    router = APIRouter(prefix="/api/auth", tags=["auth"])

    @router.post("/login")
    def login(payload: dict | None = Body(default=None)):
        payload = payload or {}
        username = payload.get("username")
        password = payload.get("password")
        if not isinstance(username, str) or USERS.get(username) != password:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid username or password"},
            )
        token = secrets.token_hex(24)
        token_store.add(token)
        return {"token": token, "tokenType": "Bearer"}

    return router
