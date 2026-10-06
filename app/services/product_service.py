from decimal import ROUND_HALF_UP, Decimal
from app.errors import ConflictError, NotFoundError, ValidationError

ALLOWED_FIELDS = ("name", "price", "stock", "discountPercent")

# ---------- Pure functions: เหมาะกับ Unit Test ที่สุด ----------
def _is_number(value) -> bool:
    # bool เป็น subclass ของ int ใน Python จึงต้องตัดออก และ value == value ใช้ตัดค่า NaN
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value == value
    )

def calculate_final_price(price, discount_percent=0):
    """คำนวณราคาหลังหักส่วนลด ปัดเศษ 2 ตำแหน่งแบบปัดครึ่งขึ้น"""
    value = Decimal(str(price)) * (100 - Decimal(str(discount_percent))) / 100
    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(value) if value == value.to_integral_value() else float(value)

def validate_product(data: dict, partial: bool = False) -> list[str]:
    """ตรวจสอบข้อมูลสินค้า คืนค่าเป็นรายการข้อความ error (list ว่าง = ผ่าน)"""
    errors = []
    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append("name is required")
        elif len(name) > 100:
            errors.append("name must be at most 100 characters")
    if not partial or "price" in data:
        price = data.get("price")
        if not _is_number(price) or price <= 0:
            errors.append("price must be a number greater than 0")
    if not partial or "stock" in data:
        stock = data.get("stock")
        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            errors.append("stock must be an integer >= 0")
    if "discountPercent" in data:
        discount = data["discountPercent"]
        if not _is_number(discount) or discount < 0 or discount > 100:
            errors.append("discountPercent must be between 0 and 100")
    return errors

# ---------- Service: รับ repository ผ่าน constructor (Dependency Injection) ----------
class ProductService:
    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _to_product(record: dict) -> dict:
        discount = record.get("discountPercent", 0)
        final_price = calculate_final_price(record["price"], discount)
        return {**record, "finalPrice": final_price}

    def list_products(self) -> list[dict]:
        return [self._to_product(r) for r in self.repository.find_all()]

    def get_product(self, product_id: int) -> dict:
        record = self.repository.find_by_id(product_id)
        if record is None:
            raise NotFoundError(f"Product {product_id} not found")
        return self._to_product(record)

    def create_product(self, data: dict) -> dict:
        errors = validate_product(data)
        if errors:
            raise ValidationError(errors)
        record = self.repository.create({
            "name": data["name"].strip(),
            "price": data["price"],
            "stock": data["stock"],
            "discountPercent": data.get("discountPercent", 0),
        })
        return self._to_product(record)

    def update_product(self, product_id: int, data: dict) -> dict:
        errors = validate_product(data, partial=True)
        if errors:
            raise ValidationError(errors)
        changes = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        record = self.repository.update(product_id, changes)
        if record is None:
            raise NotFoundError(f"Product {product_id} not found")
        return self._to_product(record)

    def delete_product(self, product_id: int) -> None:
        if not self.repository.remove(product_id):
            raise NotFoundError(f"Product {product_id} not found")

    def update_stock(self, product_id: int, quantity: int) -> dict:
        record = self.repository.find_by_id(product_id)
        if record is None:
            raise NotFoundError(f"Product {product_id} not found")
        current_stock = record.get("stock", 0)
        new_stock = current_stock + quantity
        if new_stock < 0:
            raise ConflictError("Stock cannot be negative")
        record = self.repository.update(product_id, {"stock": new_stock})
        return self._to_product(record)
