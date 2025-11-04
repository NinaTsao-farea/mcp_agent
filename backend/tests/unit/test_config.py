"""
測試配置文件
統一管理所有測試腳本的配置，包括：
- API 基礎 URL
- 測試帳號密碼
- 測試用客戶資料
- 其他共用常量
"""

# API 配置
BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

# 測試帳號 - 統一使用這組帳密
TEST_STAFF = {
    "staff_code": "S001",
    "password": "password"
}

# 備用測試帳號
TEST_STAFF_ALT = {
    "staff_code": "STAFF001",
    "password": "password123"
}

# 測試客戶資料
TEST_CUSTOMER = {
    "id_number": "A123456789",
    "name": "張三",
    "phone": "0912345678"
}

# 測試設備資料
TEST_DEVICE = {
    "brand": "Apple",
    "model": "iPhone 15 Pro",
    "os": "iOS"
}

# API 超時設定（秒）
API_TIMEOUT = 30.0

# 測試用方案 ID
TEST_PLAN_ID = "PLAN001"
