# MCP HTTP Transport - 快速開始

## 🎯 為什麼選擇 HTTP Transport？

✅ **解決 Windows stdio 問題** - 完美相容 Windows/Linux/macOS  
✅ **易於除錯** - 標準 HTTP/REST API  
✅ **生產就緒** - 支援負載平衡、監控、部署  
✅ **開發友善** - 可用瀏覽器、curl、Postman 測試  

## 🚀 5 分鐘快速啟動

### 步驟 1: 安裝依賴

```bash
cd backend
pip install fastapi uvicorn httpx
```

### 步驟 2: 啟動 Server

**Windows**:
```cmd
scripts\start-mcp-http.bat
```

**Linux/macOS**:
```bash
cd backend
uvicorn mcp_servers.crm_server_http:app --port 8001 --reload
```

### 步驟 3: 驗證

瀏覽器開啟: http://localhost:8001

看到這個就成功了：
```json
{
  "service": "CRM MCP Server (HTTP)",
  "status": "running"
}
```

### 步驟 4: 測試

**Windows**:
```cmd
scripts\test-mcp-http.bat
```

**手動測試**:
```bash
# 健康檢查
curl http://localhost:8001/health

# 查詢客戶
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"get_customer","arguments":{"id_number":"A123456789"}}'
```

## 📁 檔案結構

```
backend/
├── mcp_servers/
│   ├── crm_server.py           # 原始 stdio 版本
│   └── crm_server_http.py      # ✨ HTTP 版本
├── app/services/
│   ├── mcp_client.py           # stdio Client
│   └── mcp_client_http.py      # ✨ HTTP Client
└── test_mcp_http.py            # ✨ HTTP 測試

scripts/
├── start-mcp-http.bat          # ✨ 啟動 Server
└── test-mcp-http.bat           # ✨ 測試腳本

docs/
└── mcp-http-transport-guide.md # ✨ 完整文檔
```

## 🔧 整合到應用程式

### 更新 .env

```env
# 啟用 MCP 模式 + HTTP Transport
USE_MCP_CRM=true
USE_HTTP_TRANSPORT=true
MCP_CRM_HTTP_URL=http://localhost:8001
```

### 更新 Factory (可選)

如果想支援自動切換 stdio/HTTP:

```python
# backend/app/services/crm_factory.py
async def get_crm_service():
    if USE_MCP:
        if USE_HTTP_TRANSPORT:
            from .mcp_client_http import mcp_client_http
            await mcp_client_http.initialize()
            return mcp_client_http
        else:
            from .mcp_client import mcp_client
            await mcp_client.initialize()
            return mcp_client
    else:
        return MockCRMService()
```

## 📊 對比三種模式

| 特性 | Mock 模式 | stdio 模式 | HTTP 模式 |
|------|----------|-----------|----------|
| Windows 相容 | ✅ 完美 | ❌ 有問題 | ✅ 完美 |
| Linux 相容 | ✅ 完美 | ✅ 完美 | ✅ 完美 |
| 開發速度 | 🚀 最快 | 🟡 中等 | 🟢 快 |
| 除錯難度 | 🟢 容易 | 🔴 困難 | 🟢 容易 |
| 生產部署 | ❌ 不適合 | 🟡 可以 | ✅ 最佳 |
| 負載平衡 | ❌ 不支援 | ❌ 不支援 | ✅ 支援 |
| 監控 | 🟡 基本 | 🟡 中等 | 🟢 完整 |

## 🎯 建議使用場景

### Mock 模式
- ✅ 本地開發
- ✅ 單元測試
- ✅ 快速原型

### HTTP 模式 (推薦)
- ✅ 整合測試
- ✅ 生產環境
- ✅ 微服務架構
- ✅ Windows 開發環境

### stdio 模式
- ⚠️ Linux 命令列工具
- ⚠️ 容器化環境 (如果不需要網路隔離)

## 🔄 遷移步驟

### 從 Mock 模式遷移

1. 啟動 HTTP Server: `scripts\start-mcp-http.bat`
2. 更新 `.env`: `USE_MCP_CRM=true` + `USE_HTTP_TRANSPORT=true`
3. 測試應用程式
4. 驗證所有功能正常

### 從 stdio 模式遷移

1. 保持 `.env` 中 `USE_MCP_CRM=true`
2. 新增 `USE_HTTP_TRANSPORT=true`
3. 新增 `MCP_CRM_HTTP_URL=http://localhost:8001`
4. 啟動 HTTP Server
5. 測試並驗證

## 📚 API 端點快速參考

| 端點 | 方法 | 用途 |
|------|------|------|
| `/` | GET | API 資訊 |
| `/health` | GET | 健康檢查 |
| `/mcp/tools` | GET | 列出所有 Tools |
| `/mcp/call` | POST | 調用 Tool |

### 範例: 調用 get_customer

```bash
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_customer",
    "arguments": {
      "id_number": "A123456789"
    }
  }'
```

回應:
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

## ⚡ 常見問題

### Q: HTTP 模式會比 Mock 模式慢嗎？
A: 會有輕微延遲（網路往返），但可忽略。如果擔心效能，可以：
- 使用本地 Server (localhost)
- 啟用 HTTP/2
- 實作連線池

### Q: 需要修改現有程式碼嗎？
A: 不需要！`MCPClientServiceHTTP` 介面與 `MockCRMService` 完全相同。

### Q: 可以在生產環境使用嗎？
A: 可以！HTTP 模式就是為生產環境設計的。記得：
- 加入認證 (API Key/JWT)
- 使用 HTTPS
- 設定 Rate Limiting
- 實作監控和日誌

### Q: Server 可以獨立部署嗎？
A: 可以！這正是 HTTP 模式的優勢：
```bash
# Docker
docker run -p 8001:8001 crm-mcp-server

# Kubernetes
kubectl apply -f deployment.yaml
```

## 📖 延伸閱讀

- 📘 [完整使用指南](./mcp-http-transport-guide.md)
- 📙 [stdio 問題分析](./mcp-stdio-windows-issue.md)
- 📕 [Sprint 3 完成報告](./sprint3-completion-report.md)

## 🎉 下一步

**HTTP Transport 已就緒！** 您現在可以：

1. ✅ 在 Windows 上正常使用 MCP 模式
2. ✅ 開始 Sprint 4-9 開發
3. ✅ 準備生產環境部署

---

**狀態**: ✅ HTTP Transport 實作完成並測試通過  
**更新日期**: 2025-10-29  
**建議**: 使用 HTTP 模式取代 stdio 模式
