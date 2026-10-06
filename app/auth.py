"""ตรวจสอบ Bearer token จาก header: Authorization: Bearer <token>"""
from fastapi import Header
from app.errors import UnauthorizedError

# ผู้ใช้ตัวอย่างสำหรับแลป (ระบบจริงต้องเก็บรหัสผ่านแบบ hash ในฐานข้อมูล)
USERS = {"admin": "admin123"}

def create_auth_dependency(token_store: set[str]):
    def require_auth(authorization: str | None = Header(default=None)) -> None:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme != "Bearer" or not token or token not in token_store:
            raise UnauthorizedError()
    return require_auth
