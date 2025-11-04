# Sprint 3 準備工作 - CRM MCP Server 開發前置調整

## 📋 總覽

根據 spec.md 的 MCP 架構設計，目前 Sprint 0-2 已完成的程式需要進行以下調整，才能順利開始 Sprint 3 的 CRM MCP Server 開發。

**調整目標**：
- 將現有的 `CRMService` (Mock 實作) 保留，並重新命名為 `MockCRMService`
- 建立 MCP 架構的基礎設施
- 為未來的 MCP 整合預留介面

---

## 🔍 現狀分析

### 已完成功能 (Sprint 0-2)

✅ **Sprint 0: 環境準備**
- Python 虛擬環境
- Quart 專案骨架
- Redis 連線設定

✅ **Sprint 1: 認證系統**
- 登入/登出功能
- Session 管理 (Redis)
- 前端認證 Middleware

✅ **Sprint 2: 續約流程 Step 1-4**
- WorkflowSessionManager (Redis)
- CRMService (Mock 實作)
- Step 1: 查詢客戶
- Step 2-3: 門號列表
- Step 4: 資格檢查
- 前端續約流程頁面

### 現有問題

❌ **問題 1: CRMService 名稱衝突**
- 目前的 `CRMService` 是 Mock 實作
- Sprint 3 需要建立真正的 CRM MCP Server 整合
- 需要重新命名以避免混淆

❌ **問題 2: 缺少 MCP 基礎設施**
- 沒有 MCP Client 管理
- 沒有 MCP Server 專案結構
- 缺少 MCP 相關套件

❌ **問題 3: 服務層耦合**
- renewal_workflow.py 直接依賴 CRMService
- 未來需要支援切換 Mock/MCP 兩種模式
- 缺少抽象層

---

## 🛠️ 必要調整清單

### 調整 1: 重新命名 Mock CRM Service

**優先級**: P0 (必須)

**檔案**:
- `backend/app/services/crm_service.py`

**調整內容**:
1. 將 `CRMService` 類別重新命名為 `MockCRMService`
2. 保留所有現有功能（Mock 資料實作）
3. 添加註解說明這是測試用的 Mock 實作

**程式碼變更**:
```python
# 修改前
class CRMService:
    """CRM 服務 (Mock 實作)"""
    
# 修改後
class MockCRMService:
    """
    CRM Mock 服務
    
    用於開發與測試階段的模擬資料服務
    Sprint 3 後將被 MCPClientService 取代
    """
```

**影響範圍**:
- `backend/app/routes/renewal_workflow.py` (需更新 import)

---

### 調整 2: 建立 MCP 專案結構

**優先級**: P0 (必須)

**新增目錄**:
```
backend/
├── mcp_servers/           # MCP Server 專案目錄
│   ├── __init__.py
│   ├── crm_server.py      # CRM MCP Server (Sprint 3)
│   ├── pos_server.py      # POS MCP Server (Sprint 4)
│   ├── promotion_server.py # Promotion MCP Server (Sprint 5)
│   └── common/            # 共用工具
│       ├── __init__.py
│       ├── base_server.py # MCP Server 基礎類別
│       └── utils.py       # 工具函數
```

**新增檔案**:
1. `backend/mcp_servers/__init__.py`
2. `backend/mcp_servers/common/__init__.py`
3. `backend/mcp_servers/common/base_server.py` (基礎框架)

---

### 調整 3: 安裝 MCP 相關套件

**優先級**: P0 (必須)

**檔案**: `backend/requirements.txt`

**新增內容**:
```pip-requirements
# MCP Integration
mcp>=0.9.0
```

**安裝指令**:
```bash
cd backend
pip install mcp>=0.9.0
```

---

### 調整 4: 建立 MCPClientService 骨架

**優先級**: P0 (必須)

**新增檔案**: `backend/app/services/mcp_client.py`

**功能**:
- 統一管理所有 MCP Server 連線
- 提供與 MockCRMService 相同的介面
- 支援開發模式切換（Mock/MCP）

**骨架程式碼**:
```python
"""
MCP Client Service - 統一管理 MCP Server 連線
"""
from typing import Optional, Dict, List, Any
import structlog

logger = structlog.get_logger()


class MCPClientService:
    """
    MCP Client 服務
    
    統一管理所有 MCP Server (CRM, POS, Promotion) 的連線
    """
    
    def __init__(self):
        self._crm_session: Optional[Any] = None
        self._pos_session: Optional[Any] = None
        self._promotion_session: Optional[Any] = None
        self._initialized = False
        
    async def initialize(self):
        """初始化所有 MCP Server 連線"""
        if self._initialized:
            logger.warning("MCP Client 已初始化")
            return
            
        logger.info("初始化 MCP Client Service")
        
        # Sprint 3: 連接 CRM MCP Server
        await self._connect_crm()
        
        # Sprint 4: 連接 POS MCP Server
        # await self._connect_pos()
        
        # Sprint 5: 連接 Promotion MCP Server
        # await self._connect_promotion()
        
        self._initialized = True
        logger.info("MCP Client Service 初始化完成")
    
    async def _connect_crm(self):
        """連接 CRM MCP Server"""
        # Sprint 3 實作
        logger.info("連接 CRM MCP Server (待實作)")
        pass
    
    async def close(self):
        """關閉所有連線"""
        logger.info("關閉 MCP Client Service")
        # 實作清理邏輯
        pass
    
    # CRM Tools (與 MockCRMService 保持相同介面)
    async def query_customer_by_id(self, id_number: str) -> Optional[Dict[str, Any]]:
        """查詢客戶資料"""
        raise NotImplementedError("Sprint 3 實作")
    
    async def get_customer_phones(self, customer_id: str) -> List[Dict[str, Any]]:
        """取得客戶門號"""
        raise NotImplementedError("Sprint 3 實作")
    
    async def get_phone_contract(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """取得門號合約"""
        raise NotImplementedError("Sprint 3 實作")
    
    async def get_phone_usage(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """取得門號使用量"""
        raise NotImplementedError("Sprint 3 實作")
    
    async def get_phone_billing(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """取得門號帳單"""
        raise NotImplementedError("Sprint 3 實作")
    
    async def check_eligibility(
        self,
        phone_number: str,
        customer_id: str
    ) -> Dict[str, Any]:
        """檢查續約資格"""
        raise NotImplementedError("Sprint 3 實作")


# 全域實例 (應用程式啟動時初始化)
mcp_client = MCPClientService()
```

---

### 調整 5: 建立 CRM 服務工廠函數

**優先級**: P0 (必須)

**檔案**: `backend/app/services/crm_factory.py` (新增)

**功能**:
- 根據配置決定使用 Mock 或 MCP
- 統一介面，方便切換
- 降低路由層的耦合

**程式碼**:
```python
"""
CRM 服務工廠
根據環境配置返回適當的 CRM 服務實例
"""
import os
from typing import Union
import structlog

from .crm_service import MockCRMService
from .mcp_client import mcp_client

logger = structlog.get_logger()

# 從環境變數讀取配置
USE_MCP = os.getenv('USE_MCP_CRM', 'false').lower() == 'true'


def get_crm_service() -> Union[MockCRMService, 'MCPClientService']:
    """
    取得 CRM 服務實例
    
    開發階段: 返回 MockCRMService
    Sprint 3 後: 可切換為 MCPClientService
    
    Returns:
        CRM 服務實例 (Mock 或 MCP)
    """
    if USE_MCP:
        logger.info("使用 MCP CRM Service")
        return mcp_client
    else:
        logger.info("使用 Mock CRM Service")
        return MockCRMService()
```

---

### 調整 6: 更新路由層引用

**優先級**: P0 (必須)

**檔案**: `backend/app/routes/renewal_workflow.py`

**變更內容**:
```python
# 修改前
from ..services.crm_service import CRMService

def get_crm_service() -> CRMService:
    """取得 CRM 服務"""
    return CRMService()

# 修改後
from ..services.crm_factory import get_crm_service

# 移除 get_crm_service() 函數定義
# 直接使用 from crm_factory import get_crm_service
```

---

### 調整 7: 更新環境變數配置

**優先級**: P1 (建議)

**檔案**: `backend/.env.example` (新增)

**新增內容**:
```bash
# MCP Configuration
USE_MCP_CRM=false  # 開發階段使用 Mock，Sprint 3 後改為 true

# CRM MCP Server (Sprint 3)
MCP_CRM_COMMAND=python
MCP_CRM_ARGS=mcp_servers/crm_server.py
MCP_CRM_API_URL=https://crm.company.com/api
MCP_CRM_API_KEY=your_crm_api_key

# POS MCP Server (Sprint 4)
# MCP_POS_COMMAND=python
# MCP_POS_ARGS=mcp_servers/pos_server.py

# Promotion MCP Server (Sprint 5)
# MCP_PROMOTION_COMMAND=python
# MCP_PROMOTION_ARGS=mcp_servers/promotion_server.py
```

---

### 調整 8: 建立 MCP Server 基礎框架

**優先級**: P1 (建議)

**檔案**: `backend/mcp_servers/common/base_server.py`

**功能**:
- 提供 MCP Server 的基礎類別
- 統一錯誤處理
- 日誌記錄

**骨架程式碼**:
```python
"""
MCP Server 基礎類別
"""
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()


class BaseMCPServer:
    """
    MCP Server 基礎類別
    
    提供共用的功能：
    - 錯誤處理
    - 日誌記錄
    - 回傳格式標準化
    """
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        logger.info(f"初始化 {server_name}")
    
    def success_response(self, data: Any) -> Dict[str, Any]:
        """成功回應格式"""
        return {
            "success": True,
            "data": data
        }
    
    def error_response(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """錯誤回應格式"""
        response = {
            "success": False,
            "error_code": error_code,
            "message": message
        }
        if details:
            response["details"] = details
        return response
    
    async def handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """統一錯誤處理"""
        logger.error(
            f"{self.server_name} 錯誤",
            context=context,
            error=str(error),
            exc_info=True
        )
        return self.error_response(
            "INTERNAL_ERROR",
            f"{context}時發生錯誤"
        )
```

---

### 調整 9: 更新專案文檔

**優先級**: P2 (可選)

**檔案**: 
- `README.md` (更新架構說明)
- `docs/sprint2-completion-report.md` (補充調整說明)

**新增內容**:
- MCP 架構說明
- 開發模式切換方法
- Sprint 3 準備工作清單

---

## 🎯 調整執行順序

### Phase 1: 基礎重構 (1-2 小時)

1. ✅ 重新命名 `CRMService` → `MockCRMService`
2. ✅ 更新 `renewal_workflow.py` 的 import
3. ✅ 測試現有功能是否正常運作

### Phase 2: MCP 架構準備 (2-3 小時)

4. ✅ 安裝 `mcp` 套件
5. ✅ 建立 `mcp_servers/` 目錄結構
6. ✅ 建立 `MCPClientService` 骨架
7. ✅ 建立 `crm_factory.py`
8. ✅ 建立 `base_server.py`

### Phase 3: 整合與測試 (1-2 小時)

9. ✅ 更新 `renewal_workflow.py` 使用工廠函數
10. ✅ 設定環境變數 (`USE_MCP_CRM=false`)
11. ✅ 完整測試 Step 1-4 功能
12. ✅ 更新文檔

---

## ✅ 驗收標準

完成以下檢查後，即可開始 Sprint 3：

### 功能驗收

- [ ] 前端可正常啟動 (`pnpm run dev`)
- [ ] 後端可正常啟動 (`python app.py`)
- [ ] 登入功能正常
- [ ] Step 1: 查詢客戶正常（使用 Mock 資料）
- [ ] Step 2-3: 門號列表正常顯示
- [ ] Step 4: 資格檢查正常運作
- [ ] 返回重新查詢功能正常

### 架構驗收

- [ ] `MockCRMService` 重新命名完成
- [ ] `mcp_servers/` 目錄結構建立
- [ ] `MCPClientService` 骨架建立
- [ ] `crm_factory.py` 工廠函數建立
- [ ] `USE_MCP_CRM=false` 環境變數設定
- [ ] 路由層使用工廠函數

### 測試驗收

- [ ] 執行 `pytest` 所有測試通過
- [ ] 前端 E2E 測試通過
- [ ] 無 Python import 錯誤
- [ ] 無 TypeScript 錯誤

---

## 📦 調整後的專案結構

```
test_mcp_agent2/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── renewal_workflow.py      ✏️ 已調整
│   │   └── services/
│   │       ├── crm_service.py           ✏️ MockCRMService
│   │       ├── crm_factory.py           ⭐ 新增
│   │       ├── mcp_client.py            ⭐ 新增
│   │       ├── database.py
│   │       ├── redis_manager.py
│   │       └── workflow_session.py
│   ├── mcp_servers/                     ⭐ 新增
│   │   ├── __init__.py
│   │   ├── crm_server.py                🔜 Sprint 3
│   │   ├── pos_server.py                🔜 Sprint 4
│   │   ├── promotion_server.py          🔜 Sprint 5
│   │   └── common/
│   │       ├── __init__.py
│   │       ├── base_server.py           ⭐ 新增
│   │       └── utils.py
│   ├── requirements.txt                 ✏️ 已調整 (新增 mcp)
│   └── .env.example                     ⭐ 新增
├── frontend/
│   └── (無需調整)
└── docs/
    └── sprint3-preparation.md           ⭐ 本文件
```

---

## 🚀 開始 Sprint 3 的條件

完成以上所有 P0 調整後：

✅ **可以開始 Sprint 3: CRM MCP Server 開發**

Sprint 3 的主要任務：
1. 實作 `crm_server.py` (CRM MCP Server)
2. 實作 5 個 MCP Tools
3. 在 `MCPClientService` 中整合 CRM MCP Server
4. 設定 `USE_MCP_CRM=true` 切換到 MCP 模式
5. 測試 MCP 整合

---

## 📝 備註

### 為什麼要保留 MockCRMService？

1. **開發便利性**: 不依賴外部系統，可快速開發
2. **測試隔離**: 單元測試不需要啟動 MCP Server
3. **環境切換**: 開發/測試環境可使用 Mock，正式環境使用 MCP
4. **回退方案**: 如果 MCP 整合有問題，可快速切回 Mock

### 工廠模式的優勢

- **低耦合**: 路由層不需要知道使用哪種實作
- **易測試**: 可以輕鬆 mock 工廠函數
- **易維護**: 切換邏輯集中在一處
- **易擴展**: 未來可支援更多 CRM 系統

---

## 📞 聯絡資訊

如有問題，請參考：
- `spec.md` - 完整架構說明
- `docs/renewal-pages-structure.md` - 前端結構
- `docs/sprint2-completion-report.md` - Sprint 2 完成報告
