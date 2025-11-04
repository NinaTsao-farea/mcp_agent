# Sprint 7 AI Chat - "Session 不存在" 錯誤排查指南

**錯誤訊息**: `Session 不存在`  
**API 端點**: `GET /api/renewal-workflow/chat/stream`  
**發生時間**: 2025-11-03

---

## 🔍 問題分析

### 錯誤位置
**檔案**: `backend/app/routes/renewal_workflow.py` (Line 2033)

```python
# 驗證 Session
workflow_manager = get_workflow_manager()
session = await workflow_manager.get_session(renewal_session_id)

if not session:
    logger.warning("Session 不存在", renewal_session_id=renewal_session_id)
    return jsonify({"success": False, "error": "Session 不存在"}), 404  # ← 這裡
```

### 參數說明

API 需要以下 Query Parameters：

| 參數 | 說明 | 範例 |
|------|------|------|
| `session_id` | **認證 Session ID**（用於驗證登入） | `session_S001_4a923b6ce9c05c7ad628d285c2c62b3a` |
| `renewal_session_id` | **續約流程 Session ID**（用於取得流程狀態） | `renewal_STAFF001_bd2aa232e14d7c1769a3758cc2c3efec` |
| `message` | 使用者訊息 | `目前有什麼促銷活動？` |

### 錯誤原因

根據錯誤訊息，問題出在 **`renewal_session_id`** 不存在於 Redis 中。

可能原因：
1. ❌ **續約 Session 已過期**（預設 8 小時）
2. ❌ **續約 Session ID 不正確**
3. ❌ **尚未開始續約流程**（未呼叫 `/start`）
4. ❌ **Redis 資料被清除**

---

## 🛠️ 排查步驟

### 步驟 1: 使用診斷工具

執行診斷腳本檢查 Session 狀態：

```bash
# 確保 Redis 已啟動
redis-cli ping
# 應該返回: PONG

# 執行診斷工具
python diagnose_session.py
```

診斷工具會檢查：
- ✓ 認證 Session 是否存在
- ✓ 續約 Session 是否存在
- ✓ 當前步驟是否允許使用 AI
- ✓ Staff ID 是否匹配

### 步驟 2: 手動檢查 Redis

#### 2.1 檢查認證 Session
```bash
redis-cli

# 檢查認證 Session
GET session:session_S001_4a923b6ce9c05c7ad628d285c2c62b3a

# 應該返回 JSON 格式的 Session 資料
# 如果返回 (nil)，表示 Session 不存在或已過期
```

#### 2.2 檢查續約 Session
```bash
# 檢查續約 Session
GET renewal_STAFF001_bd2aa232e14d7c1769a3758cc2c3efec

# 應該返回 JSON 格式的流程資料
# 如果返回 (nil)，表示續約 Session 不存在
```

#### 2.3 列出所有續約 Session
```bash
# 查看所有續約 Session
KEYS renewal_*

# 範例輸出:
# 1) "renewal_STAFF001_abc123"
# 2) "renewal_STAFF002_def456"
```

### 步驟 3: 檢查前端 Session ID

**前端檢查**（瀏覽器開發者工具 Console）：

```javascript
// 檢查認證 Session ID
console.log('Auth Session:', localStorage.getItem('session_id'))

// 檢查續約 Session ID
console.log('Renewal Session:', sessionStorage.getItem('renewal_session_id'))
// 或從 URL 取得
```

**確認事項**：
- ✓ 認證 Session 格式：`session_S001_xxxxx`
- ✓ 續約 Session 格式：`renewal_STAFF001_xxxxx`
- ✓ 兩個 ID 都不能是 `null` 或 `undefined`

### 步驟 4: 檢查續約流程步驟

AI Chat 功能需要續約流程至少到達 **Step 5**（選擇裝置類型）才能使用。

**允許的步驟**：
```python
allowed_steps = [
    'select_device_type',      # Step 5
    'select_device_os',        # Step 6
    'select_device',           # Step 7
    'list_plans',              # Step 8
    'compare_plans',           # Step 9
    'confirm'                  # Step 10
]
```

**檢查當前步驟**：
```bash
redis-cli GET renewal_STAFF001_bd2aa232e14d7c1769a3758cc2c3efec | jq '.current_step'
```

如果步驟是 `input_customer_id` 或 `select_phone` 等早期步驟，需要先完成前面的步驟。

---

## ✅ 解決方案

### 方案 1: 重新開始續約流程

如果續約 Session 已過期或不存在，需要重新開始：

```bash
# 使用 curl 或 Postman
POST http://localhost:8000/api/renewal-workflow/start
Headers:
  X-Session-ID: session_S001_4a923b6ce9c05c7ad628d285c2c62b3a
Body: {}

# 回應會包含新的 renewal_session_id
{
  "success": true,
  "session_id": "renewal_STAFF001_new_hash",
  "current_step": "input_customer_id",
  "message": "續約流程已開始"
}
```

**前端操作**：
1. 前往續約流程首頁
2. 點擊「開始續約」
3. 系統會自動建立新的續約 Session

### 方案 2: 繼續現有流程

如果續約 Session 存在但尚未到達 Step 5：

1. **輸入客戶身分證** (Step 1)
   ```
   POST /api/renewal-workflow/input-customer
   Body: {"id_number": "A123456789"}
   ```

2. **選擇門號** (Step 2)
   ```
   POST /api/renewal-workflow/select-phone
   Body: {"phone_number": "0912345678"}
   ```

3. **選擇合約期數** (Step 3)
   ```
   POST /api/renewal-workflow/select-contract-period
   Body: {"contract_period": 24}
   ```

4. **輸入機型偏好** (Step 4)
   ```
   POST /api/renewal-workflow/input-device-preference
   Body: {
     "brand_preference": "Apple",
     "min_price": 10000,
     "max_price": 40000
   }
   ```

5. **選擇裝置類型** (Step 5) ← **此步驟後可使用 AI**
   ```
   POST /api/renewal-workflow/select-device-type
   Body: {"device_type": "mobile"}
   ```

### 方案 3: 檢查並修復 Session 資料

如果 Session 資料不完整或損壞，可以手動修復：

```python
# 使用 Python 腳本修復
import asyncio
import json
from app.services.redis_manager import RedisManager

async def fix_session():
    redis = RedisManager("redis://localhost:6379")
    await redis.initialize()
    
    session_id = "renewal_STAFF001_bd2aa232e14d7c1769a3758cc2c3efec"
    session_data = await redis.get_json(session_id)
    
    if session_data:
        # 確保必要欄位存在
        if 'current_step' not in session_data:
            session_data['current_step'] = 'select_device_type'
        
        if 'staff_id' not in session_data:
            session_data['staff_id'] = 'STAFF001'
        
        # 更新 Session
        await redis.set_json(session_id, session_data, expire=28800)
        print(f"✓ Session 已修復")
    else:
        print(f"✗ Session 不存在")
    
    await redis.close()

asyncio.run(fix_session())
```

---

## 🔧 開發環境快速測試

### 完整測試流程

```bash
# 1. 啟動 Redis
redis-server

# 2. 啟動後端
cd backend
python run_app.py

# 3. 啟動前端
cd frontend
pnpm run dev

# 4. 登入系統
# 瀏覽器: http://localhost:3000/login
# 帳號: S001
# 密碼: Pass123

# 5. 開始續約流程
# 瀏覽器: http://localhost:3000/renewal

# 6. 完成前 5 個步驟後，測試 AI Chat
# URL: http://localhost:3000/renewal/select-device-type
# 側邊欄會出現 AI 聊天框
```

### 使用 curl 測試 API

```bash
# 假設已登入並取得 session_id 和 renewal_session_id

# 測試 AI Chat API
curl -X GET "http://localhost:8000/api/renewal-workflow/chat/stream?session_id=session_S001_xxx&renewal_session_id=renewal_STAFF001_xxx&message=目前有什麼促銷活動？" \
  -H "Accept: text/event-stream" \
  --no-buffer

# 預期輸出 (SSE 格式):
# event: message
# data: {"type":"message","content":"讓我為您查詢..."}
#
# event: function_call
# data: {"type":"function_call","name":"search_promotions","arguments":{}}
#
# event: function_result
# data: {"type":"function_result","name":"search_promotions","result":{...}}
#
# event: message
# data: {"type":"message","content":"目前有以下促銷活動..."}
#
# event: done
# data: {"type":"done","tokens":{"prompt":150,"completion":200,"total":350}}
```

---

## 📊 常見問題 FAQ

### Q1: 為什麼需要兩個 Session ID？

**A**: 系統使用雙 Session 機制：

1. **認證 Session (`session_id`)**
   - 用途：驗證使用者身份
   - 格式：`session_S001_xxx`
   - 儲存位置：Redis `session:xxx`
   - 生命週期：8 小時
   - 來源：登入 API (`/api/auth/login`)

2. **續約 Session (`renewal_session_id`)**
   - 用途：追蹤續約流程狀態
   - 格式：`renewal_STAFF001_xxx`
   - 儲存位置：Redis `renewal_STAFF001_xxx`
   - 生命週期：8 小時
   - 來源：開始續約 API (`/api/renewal-workflow/start`)

### Q2: Session 過期時間是多久？

**A**: 預設 **8 小時**（28800 秒）

可在 `.env` 中設定：
```env
SESSION_EXPIRE_HOURS=8
```

### Q3: 如何延長 Session 有效期？

**A**: 每次 API 請求會自動更新認證 Session 的過期時間，但續約 Session 不會自動延長。

如需手動延長：
```python
# 在後端程式碼中
await redis_manager.expire(renewal_session_id, 28800)  # 延長 8 小時
```

### Q4: AI Chat 可以在任何步驟使用嗎？

**A**: 否，必須至少到達 **Step 5**（選擇裝置類型）才能使用。

**原因**: 
- Step 1-4 主要是資料收集（客戶、門號、合約期數、偏好）
- Step 5+ 才開始選擇方案和設備，此時 AI 才能提供有意義的建議

### Q5: 如果在 AI 對話時 Session 過期怎麼辦？

**A**: 
1. SSE 連線會收到 `error` 事件
2. 前端顯示錯誤訊息
3. 使用者需要重新登入或重新開始續約流程

**建議**: 在重要操作前檢查 Session 是否即將過期。

---

## 🐛 已知問題

### Issue 1: Redis 連線失敗
**症狀**: `Connection refused` 或 `Session 不存在`  
**原因**: Redis Server 未啟動  
**解決**: `redis-server` 或 `sudo service redis-server start`

### Issue 2: Session ID 格式錯誤
**症狀**: 傳入的 Session ID 格式不正確  
**檢查**:
- 認證 Session: 必須是 `session_S001_xxx` 格式
- 續約 Session: 必須是 `renewal_STAFF001_xxx` 格式

### Issue 3: 步驟檢查失敗
**症狀**: 雖然 Session 存在但仍無法使用 AI  
**原因**: 當前步驟不在允許清單中  
**解決**: 完成前面步驟至少到 Step 5

---

## 📝 日誌分析

### 後端日誌關鍵字

查看後端日誌找出問題：

```bash
# 查看最近的錯誤
tail -f backend/logs/app.log | grep -i "session 不存在"

# 查看認證相關日誌
tail -f backend/logs/app.log | grep -i "authenticate"

# 查看 AI Chat 相關日誌
tail -f backend/logs/app.log | grep -i "chat/stream"
```

### 關鍵日誌訊息

```
[warning] Session 不存在 renewal_session_id=renewal_STAFF001_xxx
→ 續約 Session 不存在於 Redis

[warning] 未登入或 Session 無效
→ 認證 Session 問題

[warning] 目前步驟不允許使用 AI 對話 current_step=input_customer_id
→ 步驟檢查失敗

[debug] Session 驗證成功 staff_code=S001
→ 認證成功
```

---

## 🎯 最佳實踐

### 1. 前端 Session 管理

```typescript
// composables/useSession.ts
export function useSession() {
  // 檢查 Session 是否有效
  const checkSession = async () => {
    const authSessionId = localStorage.getItem('session_id')
    const renewalSessionId = sessionStorage.getItem('renewal_session_id')
    
    if (!authSessionId) {
      // 導向登入頁
      navigateTo('/login')
      return false
    }
    
    if (!renewalSessionId) {
      // 導向續約首頁
      navigateTo('/renewal')
      return false
    }
    
    return true
  }
  
  return {
    checkSession
  }
}
```

### 2. API 錯誤處理

```typescript
// composables/useAIChat.ts
async function sendMessage(sessionId: string, message: string) {
  try {
    // ... 建立 EventSource
    
    eventSource.addEventListener('error', (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      
      if (data.error === 'Session 不存在') {
        // 提示使用者重新開始
        error.value = 'Session 已過期，請重新開始續約流程'
        navigateTo('/renewal')
      }
    })
  } catch (e) {
    // ...
  }
}
```

### 3. 後端 Session 驗證增強

```python
# backend/app/routes/renewal_workflow.py
async def validate_renewal_session(renewal_session_id: str, staff_id: str):
    """驗證續約 Session"""
    workflow_manager = get_workflow_manager()
    session = await workflow_manager.get_session(renewal_session_id)
    
    if not session:
        raise APIException("續約 Session 不存在或已過期", 404)
    
    if session.get('staff_id') != staff_id:
        raise APIException("Session 不屬於該員工", 403)
    
    current_step = session.get('current_step')
    allowed_steps = [...]
    
    if current_step not in allowed_steps:
        raise APIException(
            f"目前步驟 '{current_step}' 不允許使用 AI，請先完成前面步驟",
            400
        )
    
    return session
```

---

## 📚 相關文件

- [Sprint 7 計畫](./sprint7-plan.md)
- [Sprint 7 完成報告](./sprint7-completion-report.md)
- [AI ChatBox 整合指南](./ai-chatbox-integration-guide.md)
- [Session ID 修復指南](./session-id-fix.md)

---

**建立時間**: 2025-11-03  
**最後更新**: 2025-11-03  
**維護者**: GitHub Copilot
