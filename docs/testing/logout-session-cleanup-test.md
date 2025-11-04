# 登出清除會話測試指南

## 修改說明

### 問題
登出後沒有清除續約工作流的會話記錄，導致下次登入時可能看到上一個用戶的查詢記錄。

### 解決方案
在登出時同時清除認證會話和續約工作流會話的所有數據。

## 代碼修改

### 1. useAuth.ts - 登出時清除 localStorage

**修改位置：** `frontend/composables/useAuth.ts` 的 `logout` 函數

**修改內容：**
```typescript
// 清除本地資料
user.value = null
sessionId.value = null

if (process.client) {
  localStorage.removeItem('session_id')
  localStorage.removeItem('user')
  // 清除續約工作流相關資料
  localStorage.removeItem('renewal_session_id')
}
```

**關鍵變更：**
- ✅ 在登出時也清除 `renewal_session_id`
- ✅ 在異常處理分支中也添加相同的清理邏輯
- ✅ 確保無論登出 API 是否成功，都清除本地數據

### 2. index.vue - 登出時清除工作流狀態

**修改位置：** `frontend/pages/index.vue` 的 `logout` 函數

**修改前：**
```typescript
const logout = async () => {
  try {
    await authLogout()
    await navigateTo('/login')
  } catch (error) {
    console.error('登出錯誤:', error)
  }
}
```

**修改後：**
```typescript
const { clearWorkflow } = useRenewalWorkflow()

const logout = async () => {
  try {
    // 清除續約工作流狀態
    await clearWorkflow()
    // 執行登出
    await authLogout()
    await navigateTo('/login')
  } catch (error) {
    console.error('登出錯誤:', error)
  }
}
```

**關鍵變更：**
- ✅ 引入 `useRenewalWorkflow` composable
- ✅ 在登出前先調用 `clearWorkflow()` 清除工作流狀態
- ✅ 確保服務器端的會話也被刪除

## 清理項目清單

### 認證數據清理
- ✅ `user` 狀態：設置為 `null`
- ✅ `sessionId` 狀態：設置為 `null`
- ✅ `localStorage.session_id`：移除
- ✅ `localStorage.user`：移除

### 續約工作流數據清理
- ✅ `sessionId` 狀態：設置為 `null`
- ✅ `currentStep` 狀態：重置為 `'init'`
- ✅ `customer` 狀態：設置為 `null`
- ✅ `phones` 狀態：清空陣列
- ✅ `selectedPhone` 狀態：設置為 `null`
- ✅ `eligibilityCheck` 狀態：設置為 `null`
- ✅ `error` 狀態：設置為 `null`
- ✅ `localStorage.renewal_session_id`：移除

### 服務器端會話清理
- ✅ 調用 `/api/auth/logout` 清除認證會話
- ✅ 調用 `/api/renewal-workflow/session/{id}` DELETE 清除工作流會話

## 測試案例

### 測試案例 1：完整的登出流程

**測試步驟：**
1. 使用 `S001`/`password` 登入系統
2. 點擊「開始續約」
3. 查詢客戶：`A123456789`（張三）
4. 查看門號列表
5. 選擇一個門號並查看資格檢查結果
6. 返回首頁
7. 點擊右上角的「登出」按鈕
8. 登出後再次登入

**預期結果：**
- ✅ 登出時顯示載入狀態
- ✅ 成功跳轉到登入頁面
- ✅ localStorage 中的 `session_id` 被清除
- ✅ localStorage 中的 `user` 被清除
- ✅ localStorage 中的 `renewal_session_id` 被清除
- ✅ 再次登入後，續約頁面是全新的狀態
- ✅ 不會看到之前查詢的客戶資料

**驗證方法：**

1. **檢查 localStorage（Chrome DevTools > Application > Local Storage）：**
   - 登出前應該有：`session_id`、`user`、`renewal_session_id`
   - 登出後應該全部清空

2. **檢查 Network 面板：**
   - 應該看到兩個 API 調用：
     ```
     DELETE /api/renewal-workflow/session/{session_id}
     POST /api/auth/logout
     ```

3. **檢查控制台：**
   - 不應該有錯誤訊息
   - 可能看到：`刪除 Session 失敗:` 如果工作流會話已過期（這是正常的）

### 測試案例 2：在續約頁面中途登出

**測試步驟：**
1. 登入並開始續約流程
2. 查詢客戶：`A123456789`
3. 選擇門號：`0911-111-222`
4. 在資格檢查結果頁面停留
5. 打開瀏覽器的新標籤頁，訪問首頁
6. 在首頁點擊「登出」
7. 再次登入並訪問續約頁面

**預期結果：**
- ✅ 登出成功
- ✅ 所有會話數據被清除
- ✅ 再次登入後訪問續約頁面，從 Step 1 開始
- ✅ 不會看到之前的客戶資料

### 測試案例 3：登出 API 失敗的情況

**測試步驟：**
1. 登入系統
2. 開始續約流程並查詢客戶
3. 關閉後端服務（模擬 API 失敗）
4. 點擊登出

**預期結果：**
- ✅ 即使 API 調用失敗，仍然清除本地數據
- ✅ 跳轉到登入頁面
- ✅ localStorage 中的所有數據被清除
- ✅ 控制台顯示錯誤訊息：`登出錯誤:`

**驗證方法：**
```javascript
// 在瀏覽器控制台執行
console.log('session_id:', localStorage.getItem('session_id'))
console.log('user:', localStorage.getItem('user'))
console.log('renewal_session_id:', localStorage.getItem('renewal_session_id'))
// 應該全部返回 null
```

### 測試案例 4：多用戶切換測試

**測試步驟：**
1. 使用用戶 A（S001）登入
2. 查詢客戶：`A123456789`（張三）
3. 記下查詢結果
4. 登出
5. 使用用戶 B（假設有其他測試帳號）登入
6. 訪問續約頁面

**預期結果：**
- ✅ 用戶 B 看不到用戶 A 的查詢記錄
- ✅ 續約頁面從 Step 1 開始
- ✅ 沒有任何客戶資料殘留

## 數據流程圖

```
登入
  ↓
[使用系統 + 續約流程]
  ↓
  ├─ localStorage.session_id
  ├─ localStorage.user
  ├─ localStorage.renewal_session_id
  ├─ 後端 Redis: auth_session
  └─ 後端 Redis: workflow_session
  ↓
點擊登出
  ↓
clearWorkflow()
  ├─ DELETE /api/renewal-workflow/session/{id}
  │   └─ 刪除 Redis workflow_session
  ├─ 清除所有工作流狀態變量
  └─ 移除 localStorage.renewal_session_id
  ↓
authLogout()
  ├─ POST /api/auth/logout
  │   └─ 刪除 Redis auth_session
  ├─ 清除認證狀態變量
  └─ 移除 localStorage.session_id 和 user
  ↓
navigateTo('/login')
  ↓
[全新的登入狀態，無任何殘留數據]
```

## 調試技巧

### 1. 檢查 localStorage
```javascript
// 在瀏覽器控制台執行
console.table({
  session_id: localStorage.getItem('session_id'),
  user: localStorage.getItem('user'),
  renewal_session_id: localStorage.getItem('renewal_session_id')
})
```

### 2. 檢查 Vue 狀態（使用 Vue DevTools）
- 查看 `useAuth` composable 的狀態
- 查看 `useRenewalWorkflow` composable 的狀態
- 登出後所有狀態應該重置

### 3. 監控 Network 請求
```javascript
// 在登出函數中添加臨時日誌
const logout = async () => {
  try {
    console.log('開始清除工作流...')
    await clearWorkflow()
    console.log('工作流已清除')
    
    console.log('開始登出...')
    await authLogout()
    console.log('登出完成')
    
    await navigateTo('/login')
  } catch (error) {
    console.error('登出錯誤:', error)
  }
}
```

### 4. 檢查後端日誌
```bash
# 查看後端日誌，確認會話被刪除
[INFO] DELETE /api/renewal-workflow/session/{session_id}
[INFO] Workflow session deleted: {session_id}
[INFO] POST /api/auth/logout
[INFO] Auth session deleted: {session_id}
```

## 安全性考量

### 1. 敏感資料清理
- ✅ 客戶身分證號不會殘留在瀏覽器
- ✅ 客戶個人資料（姓名、電話）被完全清除
- ✅ 門號和合約資訊不會跨用戶洩露

### 2. 會話管理
- ✅ 前端和後端會話同步清除
- ✅ 即使前端清理失敗，後端會話也會被刪除
- ✅ Redis 會話有 TTL，過期自動清除

### 3. 防止資料洩露
- ✅ 登出後立即跳轉到登入頁面
- ✅ 使用 `auth` middleware 保護頁面
- ✅ 未登入用戶無法訪問續約頁面

## 常見問題

### Q1: 登出後為什麼有時還能看到之前的數據？
**A:** 可能是瀏覽器緩存。請：
- 硬性重新整理：Ctrl + Shift + R
- 清除瀏覽器緩存
- 檢查 localStorage 是否真的被清除

### Q2: 登出時出現 404 錯誤怎麼辦？
**A:** 這可能是工作流會話已經過期（TTL 1小時）。這是正常的，`clearWorkflow` 會捕獲錯誤並繼續執行。

### Q3: 在續約頁面點擊返回會清除數據嗎？
**A:** 不會。返回首頁不會清除數據，只有登出才會清除。這是設計行為，允許用戶暫時離開然後返回繼續。

### Q4: 如果用戶直接關閉瀏覽器怎麼辦？
**A:** 
- 前端 localStorage 會保留
- 後端 Redis 會話會在 TTL 過期後自動清除（認證會話 8 小時，工作流會話 1 小時）
- 下次訪問時，`checkAuth` 會驗證會話有效性

## 總結

此次修改確保了：
1. ✅ **完整的數據清理**：登出時清除所有相關數據
2. ✅ **多層保護**：前端狀態、localStorage、後端會話都被清除
3. ✅ **錯誤處理**：即使 API 失敗也確保本地數據清除
4. ✅ **安全性**：防止客戶資料跨用戶洩露
5. ✅ **用戶體驗**：登出後是全新狀態，避免混淆

這樣的實現符合安全最佳實踐，確保用戶隱私和數據安全。
