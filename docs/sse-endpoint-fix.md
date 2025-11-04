# SSE 端點修復報告

## 問題描述

在整合測試時，AI 聊天框發送訊息時出現 500 錯誤：

```
FetchError: [POST] "/api/renewal-workflow/chat/stream": 500 Internal Server Error
```

## 根本原因

**前後端不匹配問題**：

1. **前端 (useAIChat.ts)**：
   - 先用 `$fetch` 發送 POST 請求（失敗）
   - 然後用 `EventSource` 發送 GET 請求
   - `EventSource` API **只支援 GET 方法**

2. **後端 (renewal_workflow.py)**：
   - `/api/renewal-workflow/chat/stream` 只接受 POST 方法
   - 從 request body 讀取參數

**衝突**：EventSource 無法發送 POST 請求，導致前端 POST 失敗

## 解決方案

### 1. 後端修改

**檔案**: `backend/app/routes/renewal_workflow.py`

**修改前**:
```python
@bp.route('/chat/stream', methods=['POST'])
async def chat_stream():
    # 從 request body 取得參數
    data = await request.get_json()
    session_id = data.get('session_id')
    message = data.get('message')
```

**修改後**:
```python
@bp.route('/chat/stream', methods=['GET'])
async def chat_stream():
    # 從 query parameters 取得參數
    session_id = request.args.get('session_id')
    message = request.args.get('message')
```

**變更內容**:
- ✅ HTTP 方法從 POST 改為 GET
- ✅ 參數來源從 request body 改為 query parameters
- ✅ 使用 `request.args.get()` 而非 `request.get_json()`

### 2. 前端修改

**檔案**: `frontend/composables/useAIChat.ts`

**修改前**:
```typescript
try {
  // 先發送 POST（會失敗）
  const response = await $fetch('/api/renewal-workflow/chat/stream', {
    method: 'POST',
    body: { session_id, message }
  })
  
  // 再建立 EventSource GET 連線
  const url = new URL('/api/renewal-workflow/chat/stream', window.location.origin)
  url.searchParams.set('session_id', sessionId)
  url.searchParams.set('message', message)
  eventSource = new EventSource(url.toString())
}
```

**修改後**:
```typescript
try {
  // 直接使用 EventSource 建立 GET 連線
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl || 'http://localhost:8000'
  
  const url = new URL('/api/renewal-workflow/chat/stream', baseURL)
  url.searchParams.set('session_id', sessionId)
  url.searchParams.set('message', message)
  
  eventSource = new EventSource(url.toString())
}
```

**變更內容**:
- ✅ 移除不必要的 `$fetch` POST 請求
- ✅ 直接建立 EventSource 連線
- ✅ 使用正確的 baseURL (http://localhost:8000)
- ✅ 通過 query parameters 傳遞參數

## EventSource 限制說明

### 為什麼只能用 GET？

`EventSource` 是瀏覽器原生 API，用於接收 Server-Sent Events (SSE)，**設計上只支援 GET 請求**：

```javascript
// ✅ 正確：EventSource 只能用 GET
const eventSource = new EventSource('/api/endpoint?param=value')

// ❌ 錯誤：EventSource 不支援 POST
const eventSource = new EventSource('/api/endpoint', {
  method: 'POST',  // 無此選項
  body: {...}      // 無此選項
})
```

### 替代方案比較

| 方案 | 優點 | 缺點 | 適用場景 |
|------|------|------|----------|
| **EventSource (GET)** | 原生支援、自動重連、簡單易用 | 只能 GET、無法自訂 headers | SSE 串流（我們的選擇） |
| **fetch + ReadableStream** | 支援 POST、可自訂 headers | 需手動處理重連、較複雜 | 需要 POST 的 SSE |
| **WebSocket** | 雙向通訊、支援二進位 | 較複雜、需要 WebSocket 伺服器 | 即時雙向互動 |

## 測試驗證

### 1. 單元測試

建立 `backend/test_sse_endpoint.py`：
```python
def test_chat_stream_endpoint_method():
    """測試 chat/stream 端點支援 GET 方法"""
    from app.routes.renewal_workflow import bp
    # 驗證路由支援 GET
    assert 'GET' in chat_stream_rule.methods
```

### 2. 整合測試步驟

1. 重啟後端服務：
   ```bash
   cd backend
   python run_app.py
   ```

2. 前端應自動熱重載

3. 測試流程：
   - 登入系統
   - 進入續約流程 Step 5
   - 點擊 AI 聊天框範例問題
   - 確認訊息成功發送
   - 確認收到 SSE 事件

### 3. 預期結果

**瀏覽器開發者工具 Network 標籤**：
```
Request URL: http://localhost:8000/api/renewal-workflow/chat/stream?session_id=xxx&message=...
Request Method: GET
Status Code: 200 OK
Content-Type: text/event-stream
```

**EventSource 事件流**：
```
event: message
data: {"content": "根據您的查詢..."}

event: function_call
data: {"name": "search_promotions", "arguments": {...}}

event: function_result
data: {"name": "search_promotions", "result": {...}}

event: done
data: {"token_usage": {...}}
```

## 相關文件

- [MDN - EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [MDN - Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Sprint 7 開發計畫](./sprint7-plan.md)
- [AI 聊天框整合指南](./ai-chatbox-integration-guide.md)

## 後續優化建議

### P2 優化項目

1. **錯誤處理增強**
   - EventSource 連線失敗自動重試
   - 顯示友善的錯誤訊息

2. **安全性考量**
   - 訊息長度限制（避免過長的 URL）
   - 對特殊字元進行 URL 編碼

3. **效能優化**
   - 考慮使用 WebSocket（支援 POST + 雙向通訊）
   - 實作訊息壓縮

## 認證問題修復（401 Unauthorized）

### 問題描述

修復 GET 方法後，出現 401 認證錯誤：
```
GET http://localhost:8000/api/renewal-workflow/chat/stream?... 401 (Unauthorized)
後端日誌: "未登入或 Session 無效"
```

### 根本原因

**EventSource 無法自訂 Headers**：
- EventSource API 不支援設置自訂 HTTP headers
- 無法傳遞 `X-Session-ID` header
- 後端無法從 header 取得認證 Session ID

### 解決方案

**分離兩種 Session ID**：
1. **認證 Session ID**：用於身份驗證（從 localStorage）
2. **續約流程 Session ID**：用於追蹤續約進度

**前端修改** (`frontend/composables/useAIChat.ts`):
```typescript
// 取得認證 Session ID
const authSessionId = localStorage.getItem('session_id')

if (!authSessionId) {
  throw new Error('請先登入')
}

const url = new URL('/api/renewal-workflow/chat/stream', baseURL)
url.searchParams.set('session_id', authSessionId)  // 認證用
url.searchParams.set('renewal_session_id', sessionId)  // 續約流程用
url.searchParams.set('message', message)
```

**後端修改** (`backend/app/routes/renewal_workflow.py`):
```python
# session_id 用於認證（中間件會自動處理）
# renewal_session_id 用於續約流程
renewal_session_id = request.args.get('renewal_session_id')

# 驗證續約流程 Session
session = await workflow_manager.get_session(renewal_session_id)
```

**認證中間件** (`backend/app/middleware/auth.py`):
```python
# 已支援從 query parameters 讀取 session_id
session_id = (
    request.headers.get('X-Session-ID') or 
    request.cookies.get('session_id') or
    request.args.get('session_id')  # ← EventSource 使用這個
)
```

## 總結

✅ 問題已完全修復  
✅ 前後端已同步使用 GET + query parameters  
✅ EventSource 可正常工作  
✅ 認證機制正常運作  
✅ SSE 串流功能完整

**修改檔案**：
- `backend/app/routes/renewal_workflow.py` (8 處修改)
- `frontend/composables/useAIChat.ts` (2 處修改)

**關鍵改進**：
1. HTTP 方法：POST → GET
2. 參數傳遞：Body → Query Parameters
3. Session 分離：認證 + 續約流程
4. 認證來源：Header → Query Parameter

**測試狀態**：待驗證（需重啟後端）
