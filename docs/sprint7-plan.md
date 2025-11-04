# Sprint 7 開發計畫：AI 自由對話與 MCP Tools 整合

**Sprint 時間**: 2025-11-01 開始  
**預計工期**: 2 週  
**狀態**: 🚧 進行中

---

## 📋 Sprint 目標

完成 AI 助理自由對話功能，整合所有 MCP Tools，讓門市人員在續約流程 Step 5 之後可以隨時向 AI 詢問方案比較、門號詳情等問題。

### 核心功能

1. ✅ **AI 對話管理器**：管理對話歷史、上下文
2. ✅ **Function Calling 整合**：將所有 MCP Tools 註冊為 Functions
3. ✅ **SSE 串流輸出**：即時顯示 AI 回答
4. ✅ **Token 使用追蹤**：記錄每次 AI 呼叫的成本
5. ✅ **錯誤處理**：優雅處理 AI 錯誤與超時

---

## 🎯 任務清單

### 後端任務 (P0 - 必須完成)

- [ ] **Task 1**: AIConversationManager 實作
  - [ ] 對話歷史管理
  - [ ] Function Calling 協調
  - [ ] Token 計算
  - [ ] 錯誤處理

- [ ] **Task 2**: MCP Tools 註冊為 Functions
  - [ ] CRM Tools (5 個)
    - `get_customer`
    - `list_customer_phones`
    - `get_phone_details`
    - `check_renewal_eligibility`
    - `check_promotion_eligibility`
  - [ ] POS Tools (5 個)
    - `query_device_stock`
    - `get_device_info`
    - `reserve_device`
    - `get_recommended_devices`
    - `get_device_pricing`
  - [ ] Promotion Tools (4 個)
    - `search_promotions`
    - `get_plan_details`
    - `compare_plans`
    - `calculate_upgrade_cost`

- [ ] **Task 3**: SSE 串流 API 實作
  - [ ] POST /renewal-workflow/chat/stream 端點
  - [ ] SSE 事件格式定義
  - [ ] 串流錯誤處理
  - [ ] 超時處理

- [ ] **Task 4**: Token 使用追蹤
  - [ ] 記錄到 AIUsageLogs 表
  - [ ] Token 數統計（Prompt + Completion）
  - [ ] 成本計算

### 前端任務 (P1 - 後續 Sprint)

- [ ] **Task 5**: 對話 UI 元件
  - [ ] 聊天框設計
  - [ ] 訊息顯示（User / AI）
  - [ ] Markdown 渲染
  - [ ] Loading 動畫

- [ ] **Task 6**: SSE 串流接收
  - [ ] EventSource 設定
  - [ ] 即時顯示 AI 回答
  - [ ] Function Calling 狀態顯示

### 測試任務 (P0)

- [ ] **Task 7**: 單元測試
  - [ ] AIConversationManager 測試
  - [ ] Function 註冊測試
  - [ ] Token 計算測試

- [ ] **Task 8**: 整合測試
  - [ ] AI 對話流程測試
  - [ ] Function Calling 測試（各種 Tool）
  - [ ] SSE 串流測試
  - [ ] 錯誤處理測試

---

## 📐 技術設計

### 1. AIConversationManager 架構

```python
class AIConversationManager:
    """AI 對話管理器"""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI(...)
        self.mcp_client = MCPClientService()
        
    async def chat_stream(
        self,
        session_id: str,
        user_message: str,
        max_iterations: int = 5
    ) -> AsyncGenerator[dict, None]:
        """
        串流對話，支援 Function Calling
        
        Args:
            session_id: 續約 Session ID
            user_message: 使用者訊息
            max_iterations: Function Calling 最大迭代次數
            
        Yields:
            dict: SSE 事件
                - type: "message" | "function_call" | "error" | "done"
                - content: 事件內容
                - tokens: Token 使用量（done 時）
        """
```

### 2. Function Definitions 範例

```python
FUNCTION_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "compare_plans",
            "description": "比較兩個或多個方案的差異，包含費用、流量、通話等",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要比較的方案 ID 列表"
                    },
                    "customer_usage": {
                        "type": "object",
                        "description": "客戶使用習慣（可選）"
                    }
                },
                "required": ["plan_ids"]
            }
        }
    },
    # ... 其他 13 個 Functions
]
```

### 3. SSE 事件格式

```javascript
// 事件類型 1: AI 回答（串流）
event: message
data: {"type": "message", "content": "根據您的需求，我推薦..."}

// 事件類型 2: Function Calling
event: function_call
data: {"type": "function_call", "name": "compare_plans", "arguments": {...}}

// 事件類型 3: Function 結果
event: function_result
data: {"type": "function_result", "name": "compare_plans", "result": {...}}

// 事件類型 4: 完成
event: done
data: {"type": "done", "tokens": {"prompt": 150, "completion": 200, "total": 350}}

// 事件類型 5: 錯誤
event: error
data: {"type": "error", "error": "API 呼叫失敗"}
```

### 4. Function Calling 流程

```
使用者: "方案 A 和方案 B 有什麼差異？"
    ↓
AI 判斷需要呼叫 compare_plans
    ↓
後端呼叫 MCP Tool: compare_plans(["PLAN_A", "PLAN_B"])
    ↓
取得比較結果
    ↓
將結果回傳給 AI
    ↓
AI 生成自然語言回答（串流）
    ↓
前端即時顯示
```

### 5. Token 追蹤與成本計算

```python
# Azure OpenAI GPT-4o 定價 (範例)
PRICING = {
    "gpt-4o": {
        "prompt": 0.005 / 1000,      # $0.005 per 1K tokens
        "completion": 0.015 / 1000    # $0.015 per 1K tokens
    }
}

async def log_ai_usage(
    staff_id: str,
    session_id: str,
    usage_type: str,
    prompt_tokens: int,
    completion_tokens: int
):
    """記錄 AI 使用到資料庫"""
    total_tokens = prompt_tokens + completion_tokens
    cost = (
        prompt_tokens * PRICING["gpt-4o"]["prompt"] +
        completion_tokens * PRICING["gpt-4o"]["completion"]
    )
    
    await db.execute(
        """
        INSERT INTO ai_usage_logs (
            staff_id, session_id, usage_type,
            prompt_tokens, completion_tokens, total_tokens,
            cost_usd, created_at
        ) VALUES (
            :staff_id, :session_id, :usage_type,
            :prompt_tokens, :completion_tokens, :total_tokens,
            :cost_usd, SYSDATE
        )
        """,
        {
            "staff_id": staff_id,
            "session_id": session_id,
            "usage_type": usage_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost
        }
    )
```

---

## 🧪 測試場景

### 場景 1: 方案比較

**使用者**: "方案 A 和方案 B 有什麼差異？"

**預期行為**:
1. AI 呼叫 `compare_plans(["PLAN_A", "PLAN_B"])`
2. 取得比較結果
3. 生成自然語言回答（表格或列表）
4. 串流顯示

### 場景 2: 門號詳情查詢

**使用者**: "0912345678 目前的合約何時到期？"

**預期行為**:
1. AI 呼叫 `get_phone_details("0912345678")`
2. 取得合約資訊
3. 回答："您的合約將於 2025-12-31 到期"

### 場景 3: 多輪對話

**使用者**: "有哪些 5G 吃到飽方案？"  
**AI**: [呼叫 search_promotions] "有以下方案..."

**使用者**: "第一個和第二個哪個比較划算？"  
**AI**: [呼叫 compare_plans] "基於您的使用量..."

### 場景 4: 錯誤處理

**使用者**: "查詢不存在的門號"  
**AI**: [呼叫 Tool 失敗] "抱歉，查無此門號資訊"

---

## 📊 驗收標準

### 必須達成 (P0)

- [ ] AIConversationManager 可正常運作
- [ ] 所有 14 個 MCP Tools 都已註冊為 Functions
- [ ] SSE 串流可即時顯示 AI 回答
- [ ] Function Calling 正確執行
- [ ] Token 使用量正確記錄到資料庫
- [ ] 至少 3 個測試場景通過

### 建議達成 (P1)

- [ ] 對話歷史保存在 Redis
- [ ] 對話超時處理（30 秒）
- [ ] 併發對話限制（每個使用者同時 1 個）
- [ ] Markdown 格式回答支援
- [ ] Function Calling 狀態視覺化

---

## 🔧 環境配置

### Azure OpenAI 設定

```bash
# backend/.env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # 或 gpt-4o-mini

# Function Calling 設定
AI_MAX_FUNCTION_ITERATIONS=5
AI_TIMEOUT_SECONDS=30
AI_MAX_TOKENS=1000
```

---

## 📁 檔案結構

```
backend/
├── app/
│   ├── services/
│   │   ├── ai_conversation_manager.py  # 新增：AI 對話管理器
│   │   ├── mcp_function_registry.py    # 新增：Function 註冊表
│   │   └── token_tracker.py            # 新增：Token 追蹤
│   └── routes/
│       └── renewal_workflow.py         # 更新：新增 /chat/stream 端點
├── tests/
│   ├── test_ai_conversation.py         # 新增：AI 對話測試
│   ├── test_function_calling.py        # 新增：Function Calling 測試
│   └── test_sprint7_apis.py            # 新增：Sprint 7 整合測試
└── docs/
    └── sprint7-completion-report.md    # 完成後撰寫
```

---

## 📝 API 文件

### POST /renewal-workflow/chat/stream

**描述**: AI 自由對話（SSE 串流）

**請求**:
```json
{
  "session_id": "renewal_STAFF001_xxx",
  "message": "方案 A 和方案 B 有什麼差異？"
}
```

**回應**: Server-Sent Events (SSE)

```
event: message
data: {"type": "message", "content": "讓我"}

event: message
data: {"type": "message", "content": "為您"}

event: message
data: {"type": "message", "content": "比較"}

event: function_call
data: {"type": "function_call", "name": "compare_plans", "arguments": {"plan_ids": ["PLAN_A", "PLAN_B"]}}

event: function_result
data: {"type": "function_result", "result": {...}}

event: message
data: {"type": "message", "content": "方案 A 和方案 B 的主要差異：\n\n1. 月租費..."}

event: done
data: {"type": "done", "tokens": {"prompt": 150, "completion": 250, "total": 400}}
```

---

## 🚀 開發流程

### Week 1: 核心功能

**Day 1-2**: AIConversationManager 實作
- [ ] 基本對話功能
- [ ] Function Calling 協調
- [ ] 錯誤處理

**Day 3-4**: Function 註冊與 SSE
- [ ] 註冊 14 個 MCP Tools
- [ ] SSE 串流實作
- [ ] Token 追蹤

**Day 5**: 測試與修正
- [ ] 單元測試
- [ ] 整合測試
- [ ] Bug 修正

### Week 2: 優化與前端整合

**Day 6-7**: 前端 UI
- [ ] 對話框元件
- [ ] SSE 接收
- [ ] Markdown 渲染

**Day 8-9**: 整合測試
- [ ] 端對端測試
- [ ] 效能優化
- [ ] 錯誤場景測試

**Day 10**: 文件與交付
- [ ] 完成報告
- [ ] API 文件
- [ ] Demo 準備

---

## 📈 成功指標

| 指標 | 目標 | 測量方式 |
|------|------|----------|
| API 回應時間 | < 3秒 | 壓力測試 |
| Function Calling 成功率 | > 95% | 單元測試 |
| Token 追蹤準確度 | 100% | 資料庫驗證 |
| SSE 連線穩定性 | > 99% | 整合測試 |
| 測試覆蓋率 | > 80% | pytest coverage |

---

## 🔗 相關資源

- [Azure OpenAI Function Calling 文件](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling)
- [Server-Sent Events (SSE) 規範](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Sprint 6 完成報告](./sprint6-completion-report.md)
- [MCP Tools 規格](../spec.md#75-mcp-server-tools-總覽)

---

## 📋 檢查清單

### 開發前

- [x] 閱讀 Sprint 7 計畫
- [ ] 檢查 Azure OpenAI 配置
- [ ] 檢查 MCP Servers 運作正常
- [ ] 確認 AIUsageLogs 表結構

### 開發中

- [ ] 遵循程式碼風格
- [ ] 撰寫單元測試
- [ ] 記錄重要決策
- [ ] 定期提交程式碼

### 開發後

- [ ] 所有測試通過
- [ ] 撰寫完成報告
- [ ] 更新 API 文件
- [ ] Demo 準備

---

**計畫建立日期**: 2025-11-01  
**計畫撰寫人**: GitHub Copilot  
**Sprint 狀態**: 🚧 進行中
