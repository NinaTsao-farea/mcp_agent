# 前端 "Session 不存在" 問題排查指南

## 🔍 問題現象

前端使用 AI Chat 功能時，一直收到 "Session 不存在" 錯誤。

## ✅ 排查步驟

### 步驟 1: 使用前端檢查工具

1. 用瀏覽器打開 `debug_frontend_session.html`
   ```
   file:///d:/ai_project/test_mcp_agent2/debug_frontend_session.html
   ```

2. 檢查顯示的資訊：
   - ✅ 認證 Session ID 格式應為：`session_S001_xxx`
   - ✅ 續約 Session ID 格式應為：`renewal_STAFF001_xxx`
   - ✅ 兩個 Session 都應該存在

3. 點擊「測試連線」按鈕，確認 API 是否可以連線

### 步驟 2: 檢查瀏覽器 Console

1. 打開前端頁面：`http://localhost:3000/renewal/select-device-type`
2. 按 F12 打開開發者工具
3. 切換到 Console 頁籤
4. 發送一條 AI 訊息
5. 查看 Console 中的日誌：

**正常日誌應該顯示**：
```javascript
[AI Chat] 發送請求: {
  authSessionId: "session_S001_xxx",
  renewalSessionId: "renewal_STAFF001_xxx",
  message: "目前有什麼促銷活動？",
  url: "http://localhost:8000/api/renewal-workflow/chat/stream?session_id=...&renewal_session_id=...&message=..."
}
```

**錯誤日誌**：
```javascript
[AI Chat] SSE 錯誤事件: ...
[AI Chat] 錯誤數據: { type: "error", error: "Session 不存在" }
```

### 步驟 3: 檢查 Session 狀態

使用後端診斷工具確認 Session：

```bash
python diagnose_session.py
```

輸入從前端 localStorage 取得的 Session ID，確認：
1. ✅ 認證 Session 存在且有效
2. ✅ 續約 Session 存在且在正確步驟（Step 5+）

### 步驟 4: 檢查後端日誌

查看後端日誌，找出具體錯誤：

```bash
# 實時查看日誌
tail -f backend/logs/app.log | grep -i "session"
```

或在 PowerShell 中：
```powershell
Get-Content backend\logs\app.log -Wait -Tail 50 | Select-String -Pattern "session"
```

## 🐛 常見問題與解決方案

### 問題 1: localStorage 中沒有 renewal_session_id

**原因**：尚未開始續約流程

**解決方案**：
1. 前往 `http://localhost:3000/renewal`
2. 點擊「開始續約」
3. 完成步驟 1-4（輸入客戶、選擇門號等）
4. 到達 Step 5 後才能使用 AI Chat

### 問題 2: renewal_session_id 格式錯誤

**症狀**：localStorage 中有 `renewal_session_id`，但格式是 `renewal_session:renewal_STAFF001_xxx`

**原因**：手動設置了錯誤格式的 Session ID

**解決方案**：
```javascript
// 在瀏覽器 Console 中執行
localStorage.removeItem('renewal_session_id')
// 然後重新開始續約流程
```

### 問題 3: Session 已過期

**症狀**：Redis 中查詢不到 Session

**原因**：Session 預設 8 小時過期

**解決方案**：
1. 清除舊 Session：
   ```javascript
   localStorage.removeItem('renewal_session_id')
   ```
2. 重新開始續約流程

### 問題 4: 尚未到達 Step 5

**症狀**：Session 存在但仍報錯 "目前步驟不允許使用 AI"

**原因**：AI Chat 需要至少到達 Step 5（select_device_type）

**解決方案**：
完成前面的步驟：
1. Step 1: 輸入客戶身分證
2. Step 2: 列出門號
3. Step 3: 選擇門號
4. Step 4: 檢查資格
5. Step 5: 選擇裝置類型 ← **到達這裡後才能使用 AI**

### 問題 5: 前後端 Session ID 不一致

**症狀**：前端使用的 Session ID 與後端 Redis 中的不匹配

**解決方案**：

**檢查前端 Session**（瀏覽器 Console）：
```javascript
console.log('Auth:', localStorage.getItem('session_id'))
console.log('Renewal:', localStorage.getItem('renewal_session_id'))
```

**檢查後端 Session**（Python 診斷）：
```bash
python diagnose_session.py
```

**如果不匹配**：
1. 清除前端 Session：
   ```javascript
   localStorage.clear()
   ```
2. 重新登入
3. 重新開始續約流程

### 問題 6: CORS 錯誤

**症狀**：Console 顯示 CORS 相關錯誤

**原因**：後端未正確配置 CORS

**解決方案**：
確認後端 `main.py` 中有 CORS 設定：
```python
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="http://localhost:3000")
```

## 🔧 調試技巧

### 1. 使用瀏覽器網絡工具

1. F12 → Network 頁籤
2. 篩選 "EventStream" 或 "chat/stream"
3. 查看請求參數和回應

### 2. 直接測試 API

使用 curl 測試（替換為實際的 Session ID）：

```bash
curl -N "http://localhost:8000/api/renewal-workflow/chat/stream?session_id=session_S001_xxx&renewal_session_id=renewal_STAFF001_xxx&message=測試"
```

### 3. 檢查 Redis 內容

```bash
redis-cli

# 查看所有 renewal session
KEYS renewal_*

# 查看特定 session
GET renewal_session:renewal_STAFF001_xxx

# 查看 TTL（剩餘時間）
TTL renewal_session:renewal_STAFF001_xxx
```

### 4. 查看完整的錯誤堆疊

在 `useAIChat.ts` 中，錯誤會記錄到 Console。檢查：
```javascript
[AI Chat] 發送請求: { ... }
[AI Chat] SSE 錯誤事件: { ... }
[AI Chat] 錯誤數據: { ... }
```

## 📝 完整測試流程

### 前置條件檢查

```bash
# 1. Redis 運行中
redis-cli ping
# 應返回: PONG

# 2. 後端運行中
curl http://localhost:8000/health
# 應返回: {"status": "ok"}

# 3. MCP Servers 運行中
curl http://localhost:8001/health  # CRM Server
curl http://localhost:8002/health  # POS Server
curl http://localhost:8003/health  # Promotion Server

# 4. 前端運行中
curl http://localhost:3000
# 應返回 HTML
```

### 完整操作流程

1. **登入**
   ```
   前往: http://localhost:3000/login
   帳號: S001
   密碼: Pass123
   ```

2. **開始續約**
   ```
   前往: http://localhost:3000/renewal
   點擊「開始續約」
   ```

3. **輸入客戶資料**
   ```
   身分證: A123456789
   ```

4. **選擇門號**
   ```
   選擇: 0912345678
   ```

5. **檢查資格**（自動）

6. **選擇裝置類型**
   ```
   前往: http://localhost:3000/renewal/select-device-type
   ```

7. **使用 AI Chat**
   ```
   側邊欄中輸入問題
   例如：「目前有什麼促銷活動？」
   ```

### 預期結果

- ✅ AI 收到訊息並開始回答
- ✅ 可能會看到 Function Calling 標籤（調用 MCP Tools）
- ✅ 最終收到完整回答

## 🎯 快速修復指令

### 重置所有 Session（前端）

在瀏覽器 Console 執行：
```javascript
localStorage.clear()
sessionStorage.clear()
location.href = '/login'
```

### 重置所有 Session（後端）

```bash
redis-cli FLUSHDB
```
⚠️ 注意：這會清除所有 Redis 資料！

### 查看當前有效的 Session

```bash
# 查看所有 session
redis-cli KEYS "session:*"

# 查看所有 renewal session
redis-cli KEYS "renewal_session:*"
```

## 📚 相關文件

- [Session 不存在完整排查指南](./session-not-found-troubleshooting.md)
- [AI ChatBox 整合指南](./ai-chatbox-integration-guide.md)
- [Sprint 7 完成報告](./sprint7-completion-report.md)

---

**最後更新**: 2025-11-03  
**維護者**: GitHub Copilot
