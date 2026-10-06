"""Repository: ชั้นติดต่อกับแหล่งเก็บข้อมูล (แลปนี้ใช้ in-memory แทนฐานข้อมูลจริง)"""
from datetime import datetime, timezone

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class InMemoryProductRepository:
    def __init__(self, seed: list[dict] | None = None):
        self._products = [
            {"id": index + 1, **item} for index, item in enumerate(seed or [])
        ]
        self._next_id = len(self._products) + 1

    def find_all(self) -> list[dict]:
        return [dict(p) for p in self._products]

    def find_by_id(self, product_id: int) -> dict | None:
        for product in self._products:
            if product["id"] == product_id:
                return dict(product)
        return None

    def create(self, data: dict) -> dict:
        product = {"id": self._next_id, **data, "createdAt": _now()}
        self._next_id += 1
        self._products.append(product)
        return dict(product)

    def update(self, product_id: int, changes: dict) -> dict | None:
        for index, product in enumerate(self._products):
            if product["id"] == product_id:
                self._products[index] = {**product, **changes, "updatedAt": _now()}
                return dict(self._products[index])
        return None

    def remove(self, product_id: int) -> bool:
        before = len(self._products)
        self._products = [p for p in self._products if p["id"] != product_id]
        return len(self._products) < before
