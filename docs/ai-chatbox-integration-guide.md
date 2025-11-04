# AI 聊天框整合指南

## 概述

Sprint 7 實作了 AI 智能助理功能，允許客戶在續約流程的 Step 5 及之後與 AI 助理對話，查詢方案資訊、比較方案、詢問設備詳情等。

## 架構說明

### 後端 (Backend)

- **AIConversationManager** (`backend/app/services/ai_conversation_manager.py`)
  - 管理 AI 對話流程
  - 整合 13 個 MCP Tools 作為 Function Calling
  - 實現 SSE 串流回應
  - Token 使用追蹤與成本計算

- **SSE API Endpoint** (`/api/renewal-workflow/chat/stream`)
  - 接收用戶訊息
  - 驗證 Session 和流程步驟（需 >= Step 5）
  - 串流 AI 回應

### 前端 (Frontend)

#### 元件結構

```
frontend/
├── components/
│   ├── AIChatBox.vue          # 主聊天框容器
│   └── ChatMessage.vue         # 單一訊息顯示元件
└── composables/
    └── useAIChat.ts            # SSE 串流處理 Composable
```

#### 元件說明

**1. AIChatBox.vue**
- 完整的聊天介面
- 包含標題欄、訊息列表、Token 統計、輸入框
- 自動滾動到最新訊息
- 範例問題快速點擊
- 支援清除對話

**2. ChatMessage.vue**
- 顯示單一聊天訊息
- 使用 markdown-it 渲染 Markdown 格式
- 支援 Function Calling 狀態顯示
- 區分用戶和助理訊息樣式

**3. useAIChat.ts**
- 管理 EventSource 連接
- 處理 SSE 事件流（message, function_call, function_result, done, error）
- 維護訊息列表和狀態
- Token 使用統計

## 整合步驟

### 1. 在頁面中引入聊天框

以 `select-device-type.vue` (Step 5) 為例：

```vue
<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-6">
      <!-- 主要內容區域 -->
      <div class="flex-1 max-w-5xl">
        <!-- 原有頁面內容 -->
      </div>
      
      <!-- AI 聊天框側邊欄 -->
      <div class="w-96 flex-shrink-0">
        <div class="sticky top-8">
          <AIChatBox 
            v-if="renewalSessionId"
            :session-id="renewalSessionId"
            :disabled="workflowLoading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const {
  sessionId: renewalSessionId,
  loading: workflowLoading
} = useRenewalWorkflow()
</script>
```

### 2. Props 說明

**AIChatBox Props:**
- `sessionId` (required): 續約流程的 Session ID
- `disabled` (optional): 是否禁用輸入（例如頁面載入中時）

### 3. 支援的頁面

AI 聊天框應在 **Step 5 及之後** 的頁面顯示：

- ✅ `/renewal/select-device-type` (Step 5)
- ✅ `/renewal/select-device-os` (Step 6)
- ✅ `/renewal/select-device` (Step 7)
- ✅ `/renewal/list-plans` (Step 8)
- ✅ `/renewal/select-plan` (Step 9)
- ✅ `/renewal/compare-plans` (Step 9+)
- ✅ `/renewal/confirm` (Step 10)

❌ 不應在 Step 1-4 顯示（尚未完成客戶識別和門號選擇）

### 4. 樣式考量

#### 側邊欄佈局（推薦）

```vue
<div class="flex gap-6">
  <div class="flex-1 max-w-5xl">
    <!-- 主內容 -->
  </div>
  <div class="w-96 flex-shrink-0">
    <div class="sticky top-8">
      <AIChatBox :session-id="renewalSessionId" />
    </div>
  </div>
</div>
```

優點：
- 不影響主內容佈局
- 聊天框固定顯示
- 適合桌面瀏覽

#### 底部浮動佈局（備選）

```vue
<div class="relative">
  <!-- 主內容 -->
  
  <div class="fixed bottom-4 right-4 w-96 z-50">
    <AIChatBox :session-id="renewalSessionId" />
  </div>
</div>
```

優點：
- 不佔用主要空間
- 適合行動裝置
- 可摺疊/展開

### 5. 響應式設計

如需支援行動裝置，建議使用條件顯示：

```vue
<template>
  <div>
    <!-- 桌面版：側邊欄 -->
    <div class="hidden lg:block w-96">
      <AIChatBox :session-id="renewalSessionId" />
    </div>
    
    <!-- 行動版：浮動按鈕 + Modal -->
    <div class="lg:hidden">
      <UButton
        icon="i-heroicons-chat-bubble-left-right"
        size="xl"
        class="fixed bottom-4 right-4"
        @click="showChatModal = true"
      />
      
      <UModal v-model="showChatModal">
        <AIChatBox :session-id="renewalSessionId" />
      </UModal>
    </div>
  </div>
</template>
```

## AI 助理功能

### 可用的 MCP Tools

AI 助理可以調用以下 13 個工具：

**CRM 相關 (5 個)**
1. `get_customer` - 查詢客戶資料
2. `list_customer_phones` - 列出客戶門號
3. `get_phone_details` - 查詢門號詳情
4. `check_renewal_eligibility` - 檢查續約資格
5. `check_promotion_eligibility` - 檢查促銷資格

**POS 相關 (4 個)**
6. `query_device_stock` - 查詢設備庫存
7. `get_device_info` - 查詢設備詳情
8. `get_recommended_devices` - 取得推薦設備
9. `get_device_pricing` - 查詢設備價格

**Promotion 相關 (4 個)**
10. `search_promotions` - 搜尋促銷方案
11. `get_plan_details` - 查詢方案詳情
12. `compare_plans` - 比較方案
13. `calculate_upgrade_cost` - 計算升級費用

### 範例問題

系統內建以下範例問題（可在 `AIChatBox.vue` 中自訂）：

- 方案 A 和方案 B 有什麼差異？
- 這個門號的合約何時到期？
- 有哪些適合學生的方案？
- 目前有什麼促銷活動？

### 對話上下文

AI 助理會自動獲得以下上下文資訊：

- 客戶姓名、ID
- 選擇的門號
- 當前流程步驟
- 已選擇的裝置類型/作業系統（如有）

範例 System Prompt：
```
你是一位專業的電信客服助理。
客戶：張三 (ID: A123456789)
選擇的門號：0912345678
當前步驟：選擇裝置類型
```

## SSE 事件格式

### 事件類型

```typescript
// 1. 訊息內容
event: message
data: {"content": "根據您的查詢..."}

// 2. Function 調用開始
event: function_call
data: {"name": "compare_plans", "arguments": {...}}

// 3. Function 調用結果
event: function_result
data: {"name": "compare_plans", "result": {...}}

// 4. 對話完成
event: done
data: {"token_usage": {...}}

// 5. 錯誤
event: error
data: {"error": "錯誤訊息"}
```

### Token 使用統計

```typescript
{
  "prompt_tokens": 150,
  "completion_tokens": 80,
  "total_tokens": 230,
  "estimated_cost": 0.00196
}
```

## 測試指南

### 1. 手動測試

1. 啟動後端和前端服務
2. 登入系統
3. 開始續約流程，進行到 Step 5
4. 確認 AI 聊天框顯示
5. 輸入測試問題

### 2. 測試案例

**基本對話測試**
```
Q: 你好，請問你能幫我什麼？
Expected: AI 介紹自己的功能
```

**Function Calling 測試**
```
Q: 比較 999 元和 1399 元方案
Expected: 調用 compare_plans，顯示比較結果
```

**錯誤處理測試**
```
- 斷開網路連接
Expected: 顯示錯誤訊息，提示重試
```

**Token 統計測試**
```
- 完成一次對話
Expected: 底部顯示 Token 使用統計
```

### 3. 後端測試

```bash
cd backend
python -m pytest test_sprint7_core.py -v
```

預期結果：6/6 測試通過

## 常見問題

### Q1: 聊天框無法連接？

**檢查清單：**
- ✅ Session ID 是否有效
- ✅ 是否在 Step 5+ 頁面
- ✅ 後端服務是否運行
- ✅ CORS 設定是否正確

### Q2: Function Calling 沒有觸發？

**可能原因：**
- AI 判斷不需要調用工具
- 問題描述不夠明確
- System Prompt 未正確設置

**解決方法：**
- 提供更具體的問題
- 檢查後端日誌

### Q3: 訊息顯示亂碼？

**可能原因：**
- Markdown 渲染問題
- 字元編碼問題

**解決方法：**
- 確保 markdown-it 正確安裝
- 檢查 API 回應編碼

### Q4: Token 統計不準確？

**說明：**
Token 估算使用字元數 / 4 的近似演算法，與實際可能有 ±10% 誤差。

## 效能考量

### 1. SSE 連接管理

- 組件卸載時自動關閉連接
- 避免重複連接
- 錯誤時自動重試

### 2. 訊息緩存

- 使用 `useState` 保持訊息列表
- 避免不必要的重新渲染

### 3. 滾動效能

- 使用 `nextTick` 批次滾動
- 虛擬滾動（未來優化）

## 未來改進

### P2 優化項目

1. **訊息歷史持久化**
   - 儲存對話到 localStorage
   - 頁面重新載入後恢復

2. **語音輸入**
   - 整合 Web Speech API
   - 語音轉文字

3. **多語言支援**
   - 英文介面
   - i18n 整合

4. **更豐富的互動**
   - 快速回覆按鈕
   - 方案卡片預覽
   - 圖片/圖表支援

5. **效能優化**
   - 訊息虛擬滾動
   - 懶加載歷史訊息
   - WebSocket 替代 SSE

## 相關文件

- [Sprint 7 開發計畫](./sprint7-plan.md)
- [Sprint 7 完成報告](./sprint7-completion-report.md)
- [MCP 整合報告](./promotion-mcp-integration-report.md)
- [Logging 設定指南](./logging-configuration.md)

## 聯絡與支援

如有問題或建議，請聯繫開發團隊或提交 Issue。
