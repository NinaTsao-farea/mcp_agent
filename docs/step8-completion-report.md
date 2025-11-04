# Step 8 開發完成報告

## 完成時間
2025-10-30

## 功能概述
Step 8: 列出可選方案

使用 RAG 檢索相關促銷方案，並過濾出符合客戶資格的方案

## 實作內容

### 1. 後端 API (`backend/app/routes/renewal_workflow.py`)

新增 `POST /api/renewal-workflow/step/list-plans`

**請求參數：**
```json
{
  "session_id": "string"
}
```

**回應格式：**
```json
{
  "success": true,
  "plans": [
    {
      "plan_id": "PLAN001",
      "name": "5G 吃到飽方案",
      "monthly_fee": 1399,
      "data": "無限制",
      "voice": "網內免費",
      "sms": "不限",
      "contract_months": 30,
      "gifts": ["藍牙耳機"],
      "promotion_id": "PROMO001",
      "promotion_title": "5G 升級優惠",
      "relevance_score": 95,
      "is_recommended": true
    }
  ],
  "total": 3,
  "search_query": "續約搭配裝置 android Samsung Galaxy S24"
}
```

**功能特色：**
- ✅ 從 Session 讀取客戶選擇資料（門號、裝置類型、作業系統、選擇的設備）
- ✅ 智能建構搜尋查詢
  - 單純續約：「單純續約 不搭配裝置」
  - 續約搭機：「續約搭配裝置 [os] [brand] [model]」
- ✅ 使用 Promotion Service 進行 RAG 檢索
- ✅ 取得每個促銷關聯的方案詳情
- ✅ 組合完整方案資訊（包含促銷資訊）
- ✅ 依相關性和推薦度排序
- ✅ 更新 Session 狀態到 SELECT_PLAN

### 2. Composable (`frontend/composables/useRenewalWorkflow.ts`)

新增 `listPlans()` 方法

**特點：**
- ✅ 統一的 API 呼叫模式
- ✅ 自動處理認證（X-Session-ID header）
- ✅ 統一的錯誤處理和 loading 狀態
- ✅ 與其他 workflow 方法一致的介面

### 3. 前端頁面 (`frontend/pages/renewal/list-plans.vue`)

**UI 組件：**
- ✅ Breadcrumb 導航
- ✅ 頁面標題與說明
- ✅ Loading 狀態動畫
- ✅ 錯誤狀態顯示與重試按鈕
- ✅ 篩選工具列
  - 價格區間篩選（< 500, 500-1000, > 1000）
  - 流量區間篩選（限量、大流量、無限制）
  - 方案數量顯示
- ✅ 方案卡片網格（響應式 1/2/3 欄）
- ✅ 推薦方案標示（漸層背景）
- ✅ 方案詳細資訊
  - 月租費（大字體顯示）
  - 合約期數
  - 數據流量（帶圖示）
  - 語音通話（帶圖示）
  - 簡訊（帶圖示）
  - 贈品（標籤形式）
  - 促銷活動標題
- ✅ 選擇狀態指示（邊框高亮 + 勾選圖示）
- ✅ 空狀態顯示
- ✅ 返回/下一步按鈕

**互動功能：**
- ✅ 點擊卡片選擇方案
- ✅ 篩選器即時過濾
- ✅ 選擇狀態視覺反饋
- ✅ 未選擇時禁用下一步按鈕

### 4. 測試檔案 (`backend/test_step8.py`)

完整的端對端測試流程：

1. ✅ 登入
2. ✅ 開始續約流程
3. ✅ 查詢客戶
4. ✅ 列出門號
5. ✅ 選擇門號並檢查資格
6. ✅ 選擇裝置類型（smartphone）
7. ✅ 選擇作業系統（android）
8. ✅ 查詢設備
9. ✅ 選擇設備
10. ⭐ **列出方案（Step 8 重點測試）**
    - 驗證 API 狀態碼
    - 驗證回應格式
    - 顯示方案總數
    - 顯示搜尋查詢
    - 列出所有方案詳情

## 測試方法

### 後端測試

```bash
cd backend
python test_step8.py
```

**預期結果：**
- 所有步驟綠色勾選通過
- Step 8 顯示符合條件的方案列表
- 每個方案包含完整資訊

### 前端測試

1. 啟動後端：
```bash
cd backend
python run_app.py
```

2. 啟動前端：
```bash
cd frontend
pnpm run dev
```

3. 瀏覽器測試流程：
   - 登入系統
   - 完成 Step 1-7
   - 在 Step 7 選擇設備後點擊「下一步」
   - 應自動跳轉到 `/renewal/list-plans`
   - 驗證方案卡片正確顯示
   - 測試篩選功能
   - 選擇方案並點擊下一步

## 與 spec.md 的對應

根據 `spec.md` 第 3.2.1 節「10 步驟流程定義」：

```plaintext
│ Step 8: 顯示可選方案（卡片）                              │
│ └─ RAG 檢索 + 逐一檢查資格 → 只顯示符合條件的方案       │
```

**實作狀態：**
- ✅ RAG 檢索：使用 Promotion Service 的 search_promotions
- ✅ 卡片顯示：使用 Vue 3 + Nuxt UI 實作響應式卡片網格
- ⚠️ 資格檢查：已預留 TODO，目前顯示所有檢索到的方案

## 待優化項目

1. **資格檢查邏輯**
   - 在網時間檢查
   - 月消費門檻檢查
   - 方案類型限制
   - 特殊身份驗證（學生、軍公教）

2. **方案排序優化**
   - 加入更多排序因素（性價比、客戶偏好等）
   - 個人化推薦權重

3. **前端優化**
   - 添加方案比較功能（Step 9）
   - 方案詳情展開/收合
   - 更豐富的動畫效果

4. **效能優化**
   - 方案資料快取
   - 分頁載入（如方案數量過多）

## 下一步

繼續開發 **Step 9: 方案比較**
- 允許選擇 2-3 個方案進行比較
- 顯示比較表格
- AI 生成推薦理由

## 相關檔案

- `backend/app/routes/renewal_workflow.py` - Line ~1097 (+170 lines)
- `frontend/composables/useRenewalWorkflow.ts` - (+40 lines)
- `frontend/pages/renewal/list-plans.vue` - (全新檔案, 400+ lines)
- `backend/test_step8.py` - (全新檔案, 200+ lines)
