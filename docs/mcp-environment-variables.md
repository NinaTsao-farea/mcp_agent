# MCP Server 環境變數設定指南

本文檔說明所有 MCP Server 的環境變數設定方式。

---

## 📋 快速參考

### MCP Server 端口分配

| Server | 預設端口 | 環境變數 | 用途 |
|--------|---------|----------|------|
| CRM MCP Server | 8001 | `CRM_MCP_PORT` | 客戶資料管理 |
| POS MCP Server | 8002 | `POS_MCP_PORT` | 設備庫存管理 |
| Promotion MCP Server | 8003 | `PROMOTION_MCP_PORT` | 促銷方案管理 |
| Backend API | 5000 | - | 主要 API Server |
| Frontend | 3000 | - | Nuxt.js 前端 |

---

## 🔧 環境變數詳細說明

### 1. 模式切換變數

#### USE_MCP_CRM / USE_MCP_POS / USE_MCP_PROMOTION
**用途**: 切換使用 Mock Service 或 MCP Client Service

**可選值**:
- `false` (預設): 使用 Mock Service，不需啟動 MCP Server
- `true`: 使用 MCP Client，需要先啟動對應的 MCP Server

**範例**:
```bash
# 開發模式 - 使用 Mock (快速開發測試)
USE_MCP_CRM=false
USE_MCP_POS=false
USE_MCP_PROMOTION=false

# 生產模式 - 使用 MCP Server
USE_MCP_CRM=true
USE_MCP_POS=true
USE_MCP_PROMOTION=true
```

**何時使用**:
- **開發/測試**: 設為 `false`，不需啟動 MCP Server
- **整合測試**: 設為 `true`，驗證 MCP 通訊
- **生產環境**: 設為 `true`，使用真實 MCP Server

---

#### USE_HTTP_TRANSPORT
**用途**: 切換 MCP 通訊協定

**可選值**:
- `true` (推薦): 使用 HTTP Transport
- `false`: 使用 stdio Transport (Windows 有相容性問題)

**範例**:
```bash
# 推薦：HTTP Transport
USE_HTTP_TRANSPORT=true

# 備用：stdio Transport (不推薦 Windows)
USE_HTTP_TRANSPORT=false
```

**為何推薦 HTTP**:
- ✅ Windows 完全相容
- ✅ 易於除錯 (可用瀏覽器/Postman 測試)
- ✅ 支援跨網路通訊
- ✅ 有 `/health` 端點可監控
- ❌ stdio 在 Windows 有編碼問題

---

### 2. HTTP Server 端點設定

#### CRM_MCP_HOST / POS_MCP_HOST / PROMOTION_MCP_HOST
**用途**: MCP Server 綁定的 IP 位址

**可選值**:
- `0.0.0.0` (預設): 監聽所有網路介面
- `127.0.0.1`: 只監聽本機
- `192.168.x.x`: 指定網路介面

**範例**:
```bash
# 允許外部存取
CRM_MCP_HOST=0.0.0.0
POS_MCP_HOST=0.0.0.0
PROMOTION_MCP_HOST=0.0.0.0

# 只允許本機存取
CRM_MCP_HOST=127.0.0.1
POS_MCP_HOST=127.0.0.1
PROMOTION_MCP_HOST=127.0.0.1
```

---

#### CRM_MCP_PORT / POS_MCP_PORT / PROMOTION_MCP_PORT
**用途**: MCP Server 監聽的端口號

**預設值**:
- `CRM_MCP_PORT=8001`
- `POS_MCP_PORT=8002`
- `PROMOTION_MCP_PORT=8003`

**範例**:
```bash
# 使用預設端口
CRM_MCP_PORT=8001
POS_MCP_PORT=8002
PROMOTION_MCP_PORT=8003

# 自訂端口（避免衝突）
CRM_MCP_PORT=9001
POS_MCP_PORT=9002
PROMOTION_MCP_PORT=9003
```

**注意事項**:
- 確保端口未被其他程式佔用
- 修改後需同步更新 `*_MCP_SERVER_URL`
- 防火牆需開放對應端口

---

#### CRM_MCP_SERVER_URL / POS_MCP_SERVER_URL / PROMOTION_MCP_SERVER_URL
**用途**: MCP Client 連接的 Server URL

**格式**: `http://{HOST}:{PORT}`

**範例**:
```bash
# 本機連接
CRM_MCP_SERVER_URL=http://localhost:8001
POS_MCP_SERVER_URL=http://localhost:8002
PROMOTION_MCP_SERVER_URL=http://localhost:8003

# 遠端連接
CRM_MCP_SERVER_URL=http://192.168.1.100:8001
POS_MCP_SERVER_URL=http://192.168.1.100:8002
PROMOTION_MCP_SERVER_URL=http://192.168.1.100:8003

# 使用域名
CRM_MCP_SERVER_URL=http://crm-mcp.company.com
POS_MCP_SERVER_URL=http://pos-mcp.company.com
PROMOTION_MCP_SERVER_URL=http://promotion-mcp.company.com
```

---

## 📝 使用場景範例

### 場景 1: 本機開發（推薦）

**目標**: 快速開發，不啟動 MCP Server

**設定**:
```bash
# .env
USE_MCP_CRM=false
USE_MCP_POS=false
USE_MCP_PROMOTION=false
```

**啟動**:
```bash
# 只需啟動 Backend
python backend/run_app.py
```

**優點**:
- ✅ 啟動快速
- ✅ 不需管理多個 Server
- ✅ Mock 資料可快速調整

---

### 場景 2: 整合測試

**目標**: 測試 MCP 通訊，驗證完整流程

**設定**:
```bash
# .env
USE_MCP_CRM=true
USE_MCP_POS=true
USE_MCP_PROMOTION=true
USE_HTTP_TRANSPORT=true

CRM_MCP_PORT=8001
POS_MCP_PORT=8002
PROMOTION_MCP_PORT=8003

CRM_MCP_SERVER_URL=http://localhost:8001
POS_MCP_SERVER_URL=http://localhost:8002
PROMOTION_MCP_SERVER_URL=http://localhost:8003
```

**啟動**:
```bash
# Terminal 1: CRM MCP Server
.\scripts\start-crm-http.bat

# Terminal 2: POS MCP Server
.\scripts\start-pos-http.bat

# Terminal 3: Promotion MCP Server
.\scripts\start-promotion-http.bat

# Terminal 4: Backend
python backend/run_app.py
```

**優點**:
- ✅ 完整驗證 MCP 通訊
- ✅ 測試跨 Server 協作
- ✅ 模擬生產環境

---

### 場景 3: 部分使用 MCP

**目標**: CRM 使用 Mock，POS/Promotion 使用 MCP

**設定**:
```bash
# .env
USE_MCP_CRM=false          # Mock
USE_MCP_POS=true           # MCP
USE_MCP_PROMOTION=true     # MCP
USE_HTTP_TRANSPORT=true

POS_MCP_PORT=8002
PROMOTION_MCP_PORT=8003
POS_MCP_SERVER_URL=http://localhost:8002
PROMOTION_MCP_SERVER_URL=http://localhost:8003
```

**啟動**:
```bash
# Terminal 1: POS MCP Server
.\scripts\start-pos-http.bat

# Terminal 2: Promotion MCP Server
.\scripts\start-promotion-http.bat

# Terminal 3: Backend (CRM 使用 Mock)
python backend/run_app.py
```

---

### 場景 4: 生產環境

**目標**: 所有 Server 分散部署

**設定**:
```bash
# Backend .env
USE_MCP_CRM=true
USE_MCP_POS=true
USE_MCP_PROMOTION=true
USE_HTTP_TRANSPORT=true

# 遠端 MCP Servers
CRM_MCP_SERVER_URL=http://crm-mcp.internal.company.com:8001
POS_MCP_SERVER_URL=http://pos-mcp.internal.company.com:8002
PROMOTION_MCP_SERVER_URL=http://promotion-mcp.internal.company.com:8003
```

**部署架構**:
```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Backend │ (Port 5000)
    └────┬────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼───┐  ┌────▼────┐  ┌────▼────┐
│  CRM  │  │   POS   │  │Promotion│
│  MCP  │  │   MCP   │  │   MCP   │
│ :8001 │  │  :8002  │  │  :8003  │
└───────┘  └─────────┘  └─────────┘
```

---

## 🧪 測試環境變數

### 測試 MCP Server 是否正常

```bash
# 測試 CRM MCP Server
curl http://localhost:8001/health

# 測試 POS MCP Server
curl http://localhost:8002/health

# 測試 Promotion MCP Server
curl http://localhost:8003/health
```

**預期回應**:
```json
{
  "status": "healthy",
  "service": "xxx-mcp-server",
  "mode": "Mock"
}
```

---

### 測試 MCP Tools

```bash
# 列出 CRM Tools
curl http://localhost:8001/mcp/tools

# 呼叫 CRM Tool
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"get_customer","arguments":{"id_number":"A123456789"}}'
```

---

## 🔍 故障排除

### 問題 1: 端口被佔用

**錯誤訊息**:
```
Error: Address already in use
```

**解決方法**:
```bash
# Windows: 查看端口佔用
netstat -ano | findstr :8001

# 修改端口
CRM_MCP_PORT=9001
```

---

### 問題 2: 連線被拒絕

**錯誤訊息**:
```
Connection refused
```

**檢查清單**:
1. ✅ MCP Server 是否已啟動？
2. ✅ 端口號是否正確？
3. ✅ `USE_MCP_*` 是否設為 `true`？
4. ✅ `*_MCP_SERVER_URL` 是否正確？
5. ✅ 防火牆是否阻擋？

---

### 問題 3: stdio 編碼錯誤 (Windows)

**錯誤訊息**:
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**解決方法**:
```bash
# 改用 HTTP Transport
USE_HTTP_TRANSPORT=true
```

---

## 📚 相關文檔

- [Sprint 3 完成報告](./sprint3-completion-report.md) - CRM MCP Server
- [Sprint 4 完成報告](./sprint4-completion-report.md) - POS MCP Server
- [Sprint 5 完成報告](./sprint5-completion-report.md) - Promotion MCP Server
- [MCP HTTP Transport Guide](./mcp-http-transport-guide.md)
- [MCP stdio Windows Issue](./mcp-stdio-windows-issue.md)

---

## ✅ 檢查清單

開發前檢查：
- [ ] 複製 `.env.example` 為 `.env`
- [ ] 設定 `USE_MCP_*` 變數
- [ ] 設定 `USE_HTTP_TRANSPORT=true`
- [ ] 確認端口未被佔用
- [ ] 測試 MCP Server 健康檢查

整合測試前檢查：
- [ ] 所有 MCP Server 已啟動
- [ ] Health 端點回應正常
- [ ] Tools 列表可取得
- [ ] Tool 呼叫測試通過

生產部署前檢查：
- [ ] 所有 `*_MCP_SERVER_URL` 指向正確位址
- [ ] 防火牆規則已設定
- [ ] Load balancer 已配置
- [ ] 監控與日誌已設定

---

**最後更新**: 2025-10-29  
**版本**: 1.0
