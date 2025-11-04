# 電信門市銷售助理系統

## 系統概述

基於 AI 驅動的電信門市續約銷售輔助系統，透過智能推薦、自動化工作流程與即時統計，提升續約成功率與客戶滿意度。

## 技術架構

### 前端
- **框架**: Vue 3.4+ (Composition API)
- **路由**: Nuxt 3.11+
- **UI框架**: Nuxt UI v3 (Tailwind CSS)
- **狀態管理**: Composables + Pinia
- **HTTP客戶端**: $fetch (內建)
- **SSE**: EventSource API
- **認證**: Session ID + LocalStorage

### 後端
- **Web框架**: Quart 0.19+ (Async)
- **ASGI Server**: Hypercorn 0.17+
- **資料庫驅動**: python-oracledb 2.0+
- **Redis客戶端**: redis-py 5.0+ (async)
- **HTTP客戶端**: httpx 0.27+ (async)
- **AI整合**: openai 1.54+
- **搜尋整合**: azure-search-documents 11.6+
- **認證**: Session + bcrypt 4.1+

### 資料庫
- **主資料庫**: Oracle 19c+ (人員、統計、續約記錄)
- **快取/Session**: Redis 7.2+ (Standalone 或 Cluster)
- **向量搜尋**: Azure AI Search (Standard S1)

### AI/ML
- **LLM**: Azure OpenAI GPT-4o
- **Embedding**: text-embedding-3-large (1536維)
- **RAG**: Azure AI Search (HNSW + BM25 + RRF)
- **MCP**: FastMCP (可選，自由對話)

## 專案結構

```
├── backend/           # Python Quart 後端
│   ├── app/          # 應用程式主要程式碼
│   ├── config/       # 配置檔案
│   ├── tests/        # 測試程式碼
│   └── requirements.txt
├── frontend/         # Nuxt 3 前端
│   ├── components/   # Vue 組件
│   ├── pages/        # 頁面
│   ├── composables/  # 組合式函數
│   └── package.json
├── database/         # 資料庫腳本
│   ├── schema.sql    # Oracle Schema
│   └── test-data.sql # 測試資料
├── docs/            # 文件
│   ├── api.md       # API 文件
│   └── deployment.md # 部署文件
├── scripts/         # 工具腳本
└── README.md        # 專案說明
```

## 核心功能

### 🔐 認證與授權
- 門市人員登入/登出
- Session 管理（Redis 儲存）
- 登入狀態維護
- 登入記錄追蹤

### 📋 續約工作流程 (10 步驟)
1. **輸入身分證，查詢客戶**
2. **顯示客戶門號清單**
3. **門號詳情展示**
4. **選擇門號，檢查續約資格**
5. **選擇續約類型** 🔓 *從此步驟開始可自由提問*
6. **選擇手機作業系統**
7. **選擇手機與顏色**
8. **顯示可選方案（RAG 智能推薦）**
9. **方案比較（AI 生成）**
10. **確認申辦**

### 🤖 AI 智能推薦
- **RAG 檢索**: Azure AI Search + GPT-4o
- **資格預檢**: 自動過濾不符合條件的促銷
- **自由對話**: Function Calling + MCP Tools
- **即時回答**: SSE 串流顯示

### 📊 統計追蹤
- **個人統計**: 登入時長、服務客戶數、業績轉換率
- **AI 使用**: Token 數、使用成本、功能分布
- **門市排行**: 主管可查看門市比較（權限控制）

## 開發環境設定

### 後端環境
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 前端環境
```bash
cd frontend
pnpm install
pnpm run dev
```

### Redis 環境
```bash
# 本地安裝 Redis (推薦使用 Windows 版本)
# 下載並啟動 Redis 服務
# 或使用 WSL2 安裝 Redis
```

### 資料庫設定
```bash
# 執行 Oracle Schema 建立
sqlplus username/password@database @database/schema.sql

# 載入測試資料
sqlplus username/password@database @database/test-data.sql
```

## 環境變數

### 後端 (.env)
```env
# 資料庫
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
ORACLE_USER=your_user
ORACLE_PASSWORD=your_password

# Redis
REDIS_URL=redis://localhost:6379

# Session
SESSION_SECRET_KEY=your-session-secret-key
SESSION_EXPIRE_HOURS=8

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
AZURE_SEARCH_INDEX_NAME=promotions-index

# CRM 整合
CRM_API_BASE_URL=https://your-crm-api.com
CRM_API_KEY=your-crm-key
```

### 前端 (.env)
```env
# API Base URL
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## API 端點

### 認證
- `POST /api/auth/login` - 登入
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 取得當前使用者

### 續約流程
- `POST /api/renewal-workflow/start` - 開始流程
- `POST /api/renewal-workflow/step/query-customer` - 查詢客戶
- `POST /api/renewal-workflow/step/list-phones` - 列出門號
- `POST /api/renewal-workflow/step/select-phone` - 選擇門號
- `POST /api/renewal-workflow/step/select-device-type` - 選擇續約類型
- `POST /api/renewal-workflow/step/list-plans` - 列出方案
- `POST /api/renewal-workflow/chat/stream` - AI 對話 (SSE)
- `POST /api/renewal-workflow/submit` - 提交申辦

### 統計
- `GET /api/statistics/daily-stats` - 當日統計
- `GET /api/statistics/my-dashboard` - 個人儀表板
- `GET /api/statistics/store-rankings` - 門市排行榜

## 開發進度

- ✅ **Sprint 1**: 認證系統 (已完成 - 95%)
  - 後端認證 API (登入/登出/Session 管理)
  - 前端登入頁面與認證狀態管理
  - bcrypt 密碼安全
  - Redis Session 儲存
  - 詳見: `docs/sprint1-summary.md`

- ✅ **Sprint 2**: 續約工作流程基礎 (已完成 - 100%)
  - WorkflowSessionManager (狀態機管理)
  - CRMService Mock 資料服務
  - 續約流程 API (Step 1-4)
  - 前端續約頁面 UI
  - 資格檢查邏輯
  - 詳見: `docs/sprint2-completion-report.md`

- 🔜 **Sprint 3**: 手機與方案選擇 (Step 5-10)
- 📋 **Sprint 4**: AI 對話整合 (RAG + SSE)
- 📋 **Sprint 5**: 統計報表與儀表板

## 快速開始 (Sprint 1 可用)

### 測試帳號
```
員工編號: S001
密碼: password
```

### Windows 使用者
```bash
# 1. 確保 Redis 正在執行 (Docker)
docker run -d -p 6379:6379 redis:7.2-alpine

# 2. 執行啟動腳本
scripts\start-dev.bat

# 3. 開啟瀏覽器訪問 http://localhost:3000
```

### macOS/Linux 使用者
```bash
# 1. 啟動 Redis
redis-server

# 2. 執行啟動腳本
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh

# 3. 開啟瀏覽器訪問 http://localhost:3000
```

### 手動啟動
```bash
# 1. 確保 Redis 正在執行
redis-cli ping  # 應返回 PONG

# 2. 後端（終端機 1）
cd backend
pip install -r requirements-dev.txt
python run_app.py

# 3. 前端（終端機 2）
cd frontend
pnpm install
pnpm run dev

# 4. 開啟瀏覽器訪問 http://localhost:3000
```

### 開發模式特色
- ✅ **Mock 資料庫**: 無需 Oracle，使用模擬資料
- ✅ **熱重載**: 程式碼修改即時生效
- ✅ **詳細日誌**: 結構化日誌輸出
- ✅ **完整測試**: 8/13 測試通過，核心功能已驗證

### 生產環境
```bash
# 後端
cd backend
hypercorn app:app --bind 0.0.0.0:8000

# 前端
cd frontend
pnpm run build
pnpm run preview
```

## 測試

### 後端測試
```bash
cd backend
pytest tests/
```

### 前端測試
```bash
cd frontend
pnpm run test
```

## 授權

Copyright © 2025 電信門市銷售助理系統
