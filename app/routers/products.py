import re
from fastapi import APIRouter, Body, Depends, Response
from app.errors import BadRequestError
from app.services.product_service import ProductService

def parse_id(value: str) -> int:
    """แปลง id จาก path เป็นจำนวนเต็มบวก ถ้าไม่ใช่ให้ตอบ 400"""
    if not re.fullmatch(r"[0-9]+", value) or int(value) <= 0:
        raise BadRequestError("id must be a positive integer")
    return int(value)

def create_product_router(service: ProductService, require_auth) -> APIRouter:
    router = APIRouter(prefix="/api/products", tags=["products"])

    @router.get("")
    def list_products():
        return service.list_products()

    @router.get("/{product_id}")
    def get_product(product_id: str):
        return service.get_product(parse_id(product_id))

    @router.post("", status_code=201, dependencies=[Depends(require_auth)])
    def create_product(payload: dict | None = Body(default=None)):
        return service.create_product(payload or {})

    @router.put("/{product_id}", dependencies=[Depends(require_auth)])
    def update_product(product_id: str, payload: dict | None = Body(default=None)):
        return service.update_product(parse_id(product_id), payload or {})

    @router.delete(
        "/{product_id}", status_code=204, dependencies=[Depends(require_auth)]
    )
    def delete_product(product_id: str):
        service.delete_product(parse_id(product_id))
        return Response(status_code=204)

    @router.patch("/{product_id}/stock", dependencies=[Depends(require_auth)])
    def patch_stock(product_id: str, payload: dict | None = Body(default=None)):
        payload = payload or {}
        quantity = payload.get("quantity", 0)
        return service.update_stock(parse_id(product_id), quantity)

    return router
