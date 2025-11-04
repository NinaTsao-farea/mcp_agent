"""
自定義異常類別
"""

class APIException(Exception):
    """API 異常基類"""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(APIException):
    """認證錯誤"""
    
    def __init__(self, message: str = "認證失敗"):
        super().__init__(message, 401)

class AuthorizationError(APIException):
    """授權錯誤"""
    
    def __init__(self, message: str = "權限不足"):
        super().__init__(message, 403)

class ValidationError(APIException):
    """驗證錯誤"""
    
    def __init__(self, message: str = "資料驗證失敗"):
        super().__init__(message, 422)

class NotFoundError(APIException):
    """找不到資源錯誤"""
    
    def __init__(self, message: str = "找不到指定資源"):
        super().__init__(message, 404)

class BusinessLogicError(APIException):
    """業務邏輯錯誤"""
    
    def __init__(self, message: str = "業務邏輯錯誤"):
        super().__init__(message, 400)

class ExternalServiceError(APIException):
    """外部服務錯誤"""
    
    def __init__(self, message: str = "外部服務異常"):
        super().__init__(message, 502)