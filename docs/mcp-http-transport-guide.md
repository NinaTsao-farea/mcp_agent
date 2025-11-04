# MCP HTTP Transport 使用指南

## 🎯 概述

HTTP Transport 是 MCP 的替代通訊方式，使用標準 HTTP/REST API 取代 stdio，解決 Windows 相容性問題。

## ✅ 優勢

| 特性 | stdio 模式 | HTTP 模式 |
|------|-----------|----------|
| Windows 相容性 | ❌ 有問題 | ✅ 完美支援 |
| Linux/macOS | ✅ 正常 | ✅ 正常 |
| 除錯難度 | 🔴 困難 | 🟢 容易 |
| 監控 | 🔴 困難 | 🟢 容易 (HTTP logs) |
| 負載平衡 | ❌ 不支援 | ✅ 支援 |
| 部署彈性 | 🟡 中等 | 🟢 高 |
| 開發體驗 | 🟡 中等 | 🟢 優秀 |

## 📦 安裝依賴

```bash
cd backend

# 安裝 FastAPI 和 uvicorn
pip install fastapi uvicorn[standard] httpx
```

或更新 requirements.txt:
```bash
pip install -r requirements.txt
```

## 🚀 啟動 HTTP Server

### 方式 1: 使用 uvicorn (推薦)

```bash
cd backend

# 開發模式 (自動重載)
uvicorn mcp_servers.crm_server_http:app --port 8001 --reload

# 生產模式
uvicorn mcp_servers.crm_server_http:app --host 0.0.0.0 --port 8001 --workers 4
```

### 方式 2: 直接執行

```bash
cd backend
python mcp_servers/crm_server_http.py
```

### 驗證啟動

瀏覽器開啟: http://localhost:8001

預期看到:
```json
{
  "service": "CRM MCP Server (HTTP)",
  "version": "1.0.0",
  "status": "running",
  "transport": "HTTP"
}
```

## 🧪 測試 HTTP 模式

### 1. 健康檢查

```bash
curl http://localhost:8001/health
```

回應:
```json
{
  "status": "healthy",
  "service": "CRM MCP Server",
  "mode": "Mock"
}
```

### 2. 列出所有 Tools

```bash
curl http://localhost:8001/mcp/tools
```

### 3. 調用 Tool

```bash
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_customer",
    "arguments": {"id_number": "A123456789"}
  }'
```

### 4. 執行完整測試

```bash
# 終端 1: 啟動 Server
uvicorn mcp_servers.crm_server_http:app --port 8001

# 終端 2: 執行測試
python test_mcp_http.py
```

預期結果:
```
✅✅✅ 所有測試通過！MCP HTTP Transport 工作正常 ✅✅✅

HTTP 模式優勢：
  ✓ 跨平台相容 (Windows/Linux/macOS)
  ✓ 易於除錯和監控
  ✓ 支援負載平衡
  ✓ 標準 HTTP/REST API
```

## 🔧 整合到應用程式

### 更新 Factory

修改 `backend/app/services/crm_factory.py`:

```python
import os
from typing import Union
import structlog

from .crm_service import MockCRMService
from .mcp_client_http import MCPClientServiceHTTP

logger = structlog.get_logger()

USE_MCP = os.getenv('USE_MCP_CRM', 'false').lower() == 'true'
USE_HTTP_TRANSPORT = os.getenv('USE_HTTP_TRANSPORT', 'true').lower() == 'true'

async def get_crm_service():
    """取得 CRM 服務實例"""
    if USE_MCP:
        if USE_HTTP_TRANSPORT:
            logger.info("使用 MCP CRM Service (HTTP)")
            from .mcp_client_http import mcp_client_http
            await mcp_client_http.initialize()
            return mcp_client_http
        else:
            logger.info("使用 MCP CRM Service (stdio)")
            from .mcp_client import mcp_client
            await mcp_client.initialize()
            return mcp_client
    else:
        logger.debug("使用 Mock CRM Service")
        return MockCRMService()
```

### 更新 .env

```env
# MCP 模式切換
USE_MCP_CRM=true                    # 啟用 MCP 模式
USE_HTTP_TRANSPORT=true             # 使用 HTTP Transport

# HTTP Transport 配置
MCP_CRM_HTTP_URL=http://localhost:8001

# 舊的 stdio 配置 (HTTP 模式不需要)
# MCP_CRM_COMMAND=python
# MCP_CRM_ARGS=mcp_servers/crm_server.py
```

## 📊 API 端點文件

### GET /

取得 API 資訊

**回應**:
```json
{
  "service": "CRM MCP Server (HTTP)",
  "version": "1.0.0",
  "status": "running",
  "transport": "HTTP",
  "endpoints": {
    "tools": "/mcp/tools",
    "call": "/mcp/call",
    "health": "/health"
  }
}
```

### GET /health

健康檢查

**回應**:
```json
{
  "status": "healthy",
  "service": "CRM MCP Server",
  "mode": "Mock"
}
```

### GET /mcp/tools

列出所有可用的 Tools

**回應**:
```json
[
  {
    "name": "get_customer",
    "description": "查詢客戶基本資料",
    "parameters": {
      "type": "object",
      "properties": {
        "id_number": {
          "type": "string",
          "description": "客戶身分證號（10位）"
        }
      },
      "required": ["id_number"]
    }
  }
]
```

### POST /mcp/call

調用指定的 Tool

**請求**:
```json
{
  "tool": "get_customer",
  "arguments": {
    "id_number": "A123456789"
  }
}
```

**回應 (成功)**:
```json
{
  "success": true,
  "data": {
    "customer_id": "C123456",
    "name": "張三",
    "phone": "0912345678",
    "email": "zhang@example.com"
  }
}
```

**回應 (失敗)**:
```json
{
  "success": false,
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "找不到客戶"
  }
}
```

## 🔒 安全性考量

### 1. 認證

在生產環境中加入 API Key 認證:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/mcp/call", dependencies=[Depends(verify_api_key)])
async def call_tool(request: ToolCallRequest):
    # ...
```

### 2. CORS

如果需要從瀏覽器調用:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

使用 slowapi 限制請求頻率:

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/mcp/call")
@limiter.limit("10/minute")
async def call_tool(request: Request, tool_request: ToolCallRequest):
    # ...
```

## 🚀 部署

### Docker 部署

`Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "mcp_servers.crm_server_http:app", "--host", "0.0.0.0", "--port", "8001"]
```

啟動:
```bash
docker build -t crm-mcp-server .
docker run -p 8001:8001 -e MCP_CRM_API_URL="" crm-mcp-server
```

### Kubernetes 部署

`deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crm-mcp-server
  template:
    metadata:
      labels:
        app: crm-mcp-server
    spec:
      containers:
      - name: server
        image: crm-mcp-server:latest
        ports:
        - containerPort: 8001
        env:
        - name: MCP_CRM_API_URL
          value: ""
---
apiVersion: v1
kind: Service
metadata:
  name: crm-mcp-server
spec:
  selector:
    app: crm-mcp-server
  ports:
  - port: 80
    targetPort: 8001
  type: LoadBalancer
```

## 📈 監控

### 1. 日誌監控

使用 structlog 的結構化日誌:
```python
logger.info("Tool called", tool="get_customer", duration_ms=45)
```

### 2. Metrics

整合 Prometheus:
```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 3. Health Check

定期檢查 `/health` 端點:
```bash
curl http://localhost:8001/health
```

## 💡 最佳實踐

1. **使用環境變數** - 不要硬編碼 URL 和密鑰
2. **加入超時設定** - 防止長時間阻塞
3. **實作重試機制** - 處理暫時性網路錯誤
4. **記錄所有請求** - 方便除錯和審計
5. **使用 HTTPS** - 生產環境必須加密
6. **實作健康檢查** - 支援負載平衡器監控
7. **版本管理** - API 路徑包含版本號 (/v1/mcp/call)

## 🔄 從 stdio 遷移到 HTTP

### 1. 保持向後相容

同時支援兩種模式:
```python
if USE_HTTP_TRANSPORT:
    client = MCPClientServiceHTTP()
else:
    client = MCPClientService()  # stdio 版本
```

### 2. 漸進式遷移

1. 先在開發環境測試 HTTP 模式
2. 在測試環境並行運行兩種模式
3. 驗證功能一致性
4. 逐步切換生產流量
5. 最後移除 stdio 模式

### 3. 性能測試

使用 `locust` 或 `k6` 進行壓力測試:
```python
from locust import HttpUser, task

class MCPUser(HttpUser):
    @task
    def call_get_customer(self):
        self.client.post("/mcp/call", json={
            "tool": "get_customer",
            "arguments": {"id_number": "A123456789"}
        })
```

## 📚 相關文件

- FastAPI 文檔: https://fastapi.tiangolo.com/
- uvicorn 文檔: https://www.uvicorn.org/
- httpx 文檔: https://www.python-httpx.org/

---

**更新日期**: 2025-10-29  
**狀態**: HTTP Transport 實作完成，可替代 stdio 模式
