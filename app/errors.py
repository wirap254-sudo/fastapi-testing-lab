"""Error ของระบบ แต่ละคลาสกำหนด HTTP status ที่ต้องตอบกลับ"""

class AppError(Exception):
    status_code = 500

class ValidationError(AppError):
    status_code = 400
    def __init__(self, details: list[str]):
        super().__init__("Validation failed")
        self.details = details # รายการข้อความ error

class BadRequestError(AppError):
    status_code = 400

class UnauthorizedError(AppError):
    status_code = 401
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)

class NotFoundError(AppError):
    status_code = 404
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)

class ConflictError(AppError):
    status_code = 409
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)
