# AI 對話不會影響 Workflow 狀態

## 問題

**詢問 AI 時，會不會造成原本 Workflow 狀態的錯誤？**

## 答案：不會 ✅

AI 對話功能是**完全獨立**的，不會修改續約流程的 Workflow 狀態。

## 設計原理

### 1. 只讀取，不修改

**AI 對話端點 (`/chat/stream`)** 只會：
- ✅ **讀取** Workflow Session 資料
- ✅ **驗證** 當前步驟是否允許使用 AI
- ❌ **不會修改** 任何 Workflow 狀態

```python
# 只讀取 Session
session = await workflow_manager.get_session(renewal_session_id)

# 只檢查當前步驟
current_step = session.get('current_step')
if current_step not in allowed_steps:
    return error

# 只讀取 Session 資料作為上下文
# 不會調用任何 update_session 或狀態轉換方法
```

### 2. Session 資料分離

系統使用**兩種不同的 Session**：

| Session 類型 | 用途 | 儲存位置 | 修改者 |
|-------------|------|---------|--------|
| **認證 Session** | 身份驗證 | Redis `session:{id}` | 登入/登出 API |
| **續約 Workflow Session** | 流程追蹤 | Redis `renewal_session:{id}` | Workflow API |

**AI 對話只讀取續約 Workflow Session，不修改它。**

### 3. AI 功能限制

**AI 助理的 Function Calling** 也是只讀的：

```python
# AI 可以調用的 13 個 MCP Tools
CRM Tools (只讀):
- get_customer           # 查詢客戶資料
- list_customer_phones   # 列出客戶門號
- get_phone_details      # 查詢門號詳情
- check_renewal_eligibility  # 檢查續約資格
- check_promotion_eligibility  # 檢查促銷資格

POS Tools (只讀):
- query_device_stock     # 查詢設備庫存
- get_device_info        # 查詢設備詳情
- get_recommended_devices  # 取得推薦設備
- get_device_pricing     # 查詢設備價格

Promotion Tools (只讀):
- search_promotions      # 搜尋促銷方案
- get_plan_details       # 查詢方案詳情
- compare_plans          # 比較方案
- calculate_upgrade_cost  # 計算升級費用
```

**所有 Tools 都是查詢功能，不會修改資料庫或 Session。**

## 實際流程

### 用戶操作流程

```
1. 進入續約流程 Step 5（選擇裝置類型）
   → Workflow 狀態: SELECT_DEVICE_TYPE
   
2. 點擊 AI 聊天框，詢問「目前有什麼促銷活動？」
   → AI 讀取 Workflow Session（只讀）
   → AI 調用 search_promotions (只讀)
   → AI 回答用戶
   → Workflow 狀態: 仍然是 SELECT_DEVICE_TYPE ✅
   
3. 用戶選擇「智慧型手機」
   → 調用 /step/select-device-type API
   → Workflow 狀態更新: SELECT_DEVICE_TYPE → SELECT_DEVICE_OS ✅
   
4. 繼續詢問 AI「iPhone 15 和 iPhone 16 有什麼差別？」
   → AI 讀取 Workflow Session（只讀）
   → AI 調用 get_device_info (只讀)
   → AI 回答用戶
   → Workflow 狀態: 仍然是 SELECT_DEVICE_OS ✅
```

### 狀態更新的唯一來源

**只有 Workflow API 會更新狀態**：

```python
# 這些 API 會更新 Workflow 狀態：
POST /api/renewal-workflow/start
POST /api/renewal-workflow/step/query-customer
POST /api/renewal-workflow/step/select-phone
POST /api/renewal-workflow/step/check-eligibility
POST /api/renewal-workflow/step/select-device-type
POST /api/renewal-workflow/step/select-device-os
POST /api/renewal-workflow/step/select-device
POST /api/renewal-workflow/step/select-plan
POST /api/renewal-workflow/step/confirm
POST /api/renewal-workflow/step/submit

# 這個 API 不會更新 Workflow 狀態：
GET /api/renewal-workflow/chat/stream  ← AI 對話（只讀）
```

## 代碼驗證

### AI 對話端點（只讀）

```python
@bp.route('/chat/stream', methods=['GET'])
async def chat_stream():
    # 1. 讀取 Session（只讀）
    session = await workflow_manager.get_session(renewal_session_id)
    
    # 2. 檢查當前步驟（只讀）
    current_step = session.get('current_step')
    
    # 3. 驗證步驟（只讀）
    if current_step not in allowed_steps:
        return error
    
    # 4. 啟動 AI 對話（只讀取 Session 作為上下文）
    async for event in ai_manager.chat_stream(
        session_id=renewal_session_id,  # 傳入 Session ID，但不修改
        user_message=message,
        staff_id=staff_id
    ):
        yield event
    
    # ❌ 沒有任何 update_session 或狀態轉換的調用
```

### AI Conversation Manager（只讀 Session）

```python
class AIConversationManager:
    async def chat_stream(self, session_id, user_message, staff_id):
        # 讀取 Session 資料作為上下文
        session_data = await self._get_session_data(session_id)
        
        # 生成 System Prompt（使用 Session 資料）
        system_prompt = self._get_system_prompt(session_data)
        
        # 調用 OpenAI（只讀取資料，不修改）
        async for event in self._stream_chat(
            system_prompt=system_prompt,
            user_message=user_message
        ):
            yield event
        
        # ❌ 不會修改 Session
```

## 安全保證

### 1. 權限檢查

```python
# 驗證 Session 屬於該員工
if session.get('staff_id') != staff_id:
    return error("Session 不屬於該員工"), 403
```

### 2. 步驟限制

```python
# 只有 Step 5 之後才能使用 AI
if current_step not in allowed_steps:
    return error("請先完成前面的步驟"), 400
```

### 3. 只讀 Tools

所有 MCP Tools 都設計為只讀查詢，不會修改資料。

## 總結

**AI 對話功能的設計原則**：

✅ **只讀取，不修改** - 不會改變 Workflow 狀態  
✅ **完全獨立** - 與流程步驟解耦  
✅ **輔助工具** - 幫助門市人員快速查詢資訊  
✅ **安全隔離** - 權限檢查 + 步驟驗證  

**結論：您可以放心使用 AI 對話功能，它不會影響續約流程的狀態！** 🎉

---

## 當前錯誤修復

**問題**：`WorkflowStep.SELECT_PLAN` 不存在

**修復**：移除 `SELECT_PLAN`，只保留實際存在的枚舉值：

```python
allowed_steps = [
    WorkflowStep.SELECT_DEVICE_TYPE.value,
    WorkflowStep.SELECT_DEVICE_OS.value,
    WorkflowStep.SELECT_DEVICE.value,
    WorkflowStep.LIST_PLANS.value,
    WorkflowStep.COMPARE_PLANS.value,
    WorkflowStep.CONFIRM.value
]
```

**需要重啟後端服務來應用修復。**
