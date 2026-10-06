from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth import create_auth_dependency
from app.errors import AppError, ValidationError
from app.repositories.product_repository import InMemoryProductRepository
from app.routers.auth import create_auth_router
from app.routers.products import create_product_router
from app.services.product_service import ProductService

SEED_PRODUCTS = [
    {"name": "Mechanical Keyboard", "price": 2490, "stock": 12, "discountPercent": 0},
    {"name": "Wireless Mouse", "price": 890, "stock": 30, "discountPercent": 10},
]

def create_app(repository=None, token_store: set[str] | None = None) -> FastAPI:
    """App factory: สร้างแอปใหม่ได้ทุกครั้ง ทำให้แต่ละเทสต์มีข้อมูลแยกกัน"""
    if repository is None:
        repository = InMemoryProductRepository(SEED_PRODUCTS)
    if token_store is None:
        token_store = set()

    app = FastAPI(title="Product API", version="1.0.0")
    service = ProductService(repository)
    require_auth = create_auth_dependency(token_store)

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    app.include_router(create_auth_router(token_store))
    app.include_router(create_product_router(service, require_auth))

    # ---------- Exception handlers: แปลง error เป็น JSON รูปแบบเดียวกันทั้งระบบ ----------
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        content = {"error": str(exc)}
        if isinstance(exc, ValidationError):
            content["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        request: Request, exc: RequestValidationError
    ):
        # FastAPI ปกติตอบ 422 แต่ API นี้กำหนดให้ตอบ 400 เพื่อให้สอดคล้องกับ error อื่น
        errors = exc.errors()
        is_json_error = any(e.get("type") == "json_invalid" for e in errors)
        message = "Invalid JSON body" if is_json_error else "Invalid request body"
        return JSONResponse(status_code=400, content={"error": message})

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        message = "Route not found" if exc.status_code == 404 else exc.detail
        return JSONResponse(status_code=exc.status_code, content={"error": message})

    return app

app = create_app()
