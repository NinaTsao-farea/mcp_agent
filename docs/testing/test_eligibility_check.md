# 資格檢查錯誤處理測試指南

## 修改說明

### 問題
當選擇的門號不符合續約資格時，系統會拋出異常並顯示錯誤提示，用戶體驗不佳。

### 解決方案
修改 `selectPhone` 函數，改為返回響應對象，讓前端根據 `success` 字段判斷並優雅地顯示資格檢查結果。

## 代碼修改

### 1. Composable 修改 (useRenewalWorkflow.ts)

**修改前：**
```typescript
if (response.success && response.eligible) {
  // 符合資格
  selectedPhone.value = phones.value.find(p => p.phone_number === phoneNumber) || null
  eligibilityCheck.value = response.eligibility
  currentStep.value = 'select_device_type'
  return response
} else {
  eligibilityCheck.value = response.eligibility
  throw new Error(response.message || '此門號不符合續約資格')
}
```

**修改後：**
```typescript
// 從 phones 中找到選中的門號
selectedPhone.value = phones.value.find(p => p.phone_number === phoneNumber) || null

if (response.success) {
  // 資格檢查通過
  eligibilityCheck.value = response.eligibility
  currentStep.value = 'select_device_type'
  error.value = null
  return response
} else {
  // 資格檢查不通過，設置資格檢查結果但不拋出異常
  eligibilityCheck.value = response.eligibility
  // 不符合資格時也算是成功獲取了資格檢查結果，只是結果是不通過
  // 不設置 error，讓 UI 根據 eligibilityCheck 顯示詳細信息
  return response
}
```

**關鍵變更：**
- ✅ 無論資格檢查結果如何，都設置 `selectedPhone`
- ✅ 不符合資格時不拋出異常，而是返回響應對象
- ✅ 設置 `eligibilityCheck` 讓 UI 顯示詳細信息
- ✅ 網絡錯誤時返回 `{ success: false, error: "錯誤訊息" }`

### 2. 頁面處理修改 (renewal/index.vue)

**修改前：**
```typescript
const handleSelectPhone = async (phoneNumber: string) => {
  try {
    await selectPhone(phoneNumber)
  } catch (err: any) {
    console.error('選擇門號失敗:', err)
  }
}
```

**修改後：**
```typescript
const handleSelectPhone = async (phoneNumber: string) => {
  try {
    const result = await selectPhone(phoneNumber)
    
    if (!result || !result.success) {
      // 資格檢查不通過時，eligibilityCheck 已經被設置
      // UI 會自動顯示不符合資格的詳細信息
      console.log('門號不符合續約資格，顯示檢查結果')
    } else {
      // 資格檢查通過，繼續流程
      console.log('門號符合續約資格，可繼續流程')
    }
  } catch (err: any) {
    console.error('選擇門號失敗:', err)
  }
}
```

**關鍵變更：**
- ✅ 檢查返回結果的 `success` 字段
- ✅ 不再依賴 try-catch 處理業務邏輯失敗
- ✅ UI 會根據 `eligibilityCheck` 自動渲染結果

## 測試案例

### 測試環境準備

1. **啟動後端服務：**
```powershell
cd backend
python run_app.py
```

2. **啟動前端服務：**
```powershell
cd frontend
pnpm run dev
```

3. **登入系統：**
- 帳號：`S001`
- 密碼：`password`

### 測試案例 1：門號不符合資格（合約未到期）

**測試步驟：**
1. 點擊「開始續約」按鈕
2. 輸入身分證號：`A123456789`（張三）
3. 點擊「查詢客戶」
4. 選擇門號：`0911-222-333`（合約到期日 2026-05-20，未到期）

**預期結果：**
- ✅ 頁面切換到 Step 3：資格檢查結果
- ✅ 顯示紅色 X 圖示和「不符合續約資格」標題
- ✅ 顯示檢查項目：
  - ❌ 合約期限檢查：距離合約到期日還有 209 天，需在到期前 90 天內
  - ✅ 帳單狀態檢查：無未繳費用
  - ✅ 身份驗證檢查：已完成身份驗證
- ✅ 顯示「選擇其他門號」按鈕
- ✅ 控制台顯示：`門號不符合續約資格，顯示檢查結果`
- ✅ 不會顯示錯誤彈窗或異常提示

**Network 面板檢查：**
- ✅ `/api/renewal-workflow/step/select-phone` 返回 200
- ✅ Response body：
```json
{
  "success": false,
  "eligible": false,
  "message": "此門號不符合續約資格",
  "eligibility": {
    "eligible": false,
    "reason": "合約未到期",
    "details": [
      {
        "item": "合約期限檢查",
        "status": "fail",
        "message": "距離合約到期日還有 209 天，需在到期前 90 天內"
      },
      {
        "item": "帳單狀態檢查",
        "status": "pass",
        "message": "無未繳費用"
      },
      {
        "item": "身份驗證檢查",
        "status": "pass",
        "message": "已完成身份驗證"
      }
    ]
  }
}
```

### 測試案例 2：門號符合續約資格

**測試步驟：**
1. 點擊「選擇其他門號」返回門號列表
2. 選擇門號：`0911-111-222`（合約到期日 2024-12-31，即將到期）

**預期結果：**
- ✅ 頁面切換到 Step 3：資格檢查結果
- ✅ 顯示綠色勾選圖示和「符合續約資格」標題
- ✅ 顯示檢查項目：
  - ✅ 合約期限檢查：距離合約到期日 69 天，符合續約條件
  - ✅ 帳單狀態檢查：無未繳費用
  - ✅ 身份驗證檢查：已完成身份驗證
- ✅ 顯示「選擇其他門號」和「繼續選擇方案」按鈕
- ✅ 控制台顯示：`門號符合續約資格，可繼續流程`

**Network 面板檢查：**
- ✅ `/api/renewal-workflow/step/select-phone` 返回 200
- ✅ Response body：
```json
{
  "success": true,
  "eligible": true,
  "message": "門號符合續約資格",
  "eligibility": {
    "eligible": true,
    "reason": "符合所有續約條件",
    "details": [
      {
        "item": "合約期限檢查",
        "status": "pass",
        "message": "距離合約到期日 69 天，符合續約條件"
      },
      {
        "item": "帳單狀態檢查",
        "status": "pass",
        "message": "無未繳費用"
      },
      {
        "item": "身份驗證檢查",
        "status": "pass",
        "message": "已完成身份驗證"
      }
    ],
    "contract_end_date": "2024-12-31",
    "days_to_expiry": 69
  }
}
```

### 測試案例 3：門號有未繳費用

**測試步驟：**
1. 返回 Step 1，輸入身分證號：`B987654321`（李四）
2. 點擊「查詢客戶」
3. 選擇門號：`0922-333-444`（有未繳費用）

**預期結果：**
- ✅ 顯示「不符合續約資格」
- ✅ 檢查項目顯示：
  - ❌ 帳單狀態檢查：有未繳費用 2,500 元
  - （其他項目可能也不通過）
- ✅ 不會拋出異常或顯示錯誤彈窗

## 用戶體驗改善

### 修改前的問題
1. ❌ 拋出異常，顯示錯誤彈窗
2. ❌ 用戶看不到詳細的檢查結果
3. ❌ 無法知道哪個檢查項目不通過
4. ❌ 用戶體驗差，感覺像是系統錯誤

### 修改後的優勢
1. ✅ 優雅地顯示資格檢查結果
2. ✅ 詳細列出每個檢查項目的狀態
3. ✅ 清楚說明不符合資格的原因
4. ✅ 提供「選擇其他門號」選項
5. ✅ 用戶體驗良好，符合業務邏輯

## API 響應格式

### 符合資格時
```json
{
  "success": true,
  "eligible": true,
  "message": "門號符合續約資格",
  "eligibility": {
    "eligible": true,
    "reason": "符合所有續約條件",
    "details": [...],
    "contract_end_date": "2024-12-31",
    "days_to_expiry": 69
  }
}
```

### 不符合資格時
```json
{
  "success": false,
  "eligible": false,
  "message": "此門號不符合續約資格",
  "eligibility": {
    "eligible": false,
    "reason": "合約未到期",
    "details": [...],
    "contract_end_date": "2026-05-20",
    "days_to_expiry": 209
  }
}
```

### 網絡錯誤時
```json
{
  "success": false,
  "error": "網絡錯誤或其他異常訊息"
}
```

## 調試方法

### 1. 控制台日誌
打開 Chrome DevTools 的 Console 面板，查看：
- `門號不符合續約資格，顯示檢查結果` - 資格不通過
- `門號符合續約資格，可繼續流程` - 資格通過

### 2. Network 面板
檢查 `/api/renewal-workflow/step/select-phone` 請求：
- Status Code 應為 200（即使資格不通過）
- Response body 包含 `success`、`eligible`、`eligibility` 字段

### 3. Vue DevTools
查看 composable 狀態：
- `eligibilityCheck`: 應包含檢查結果
- `selectedPhone`: 應被設置為選中的門號
- `error`: 應為 null（不符合資格不是錯誤）

## 總結

此次修改將**業務邏輯失敗**（門號不符合資格）與**系統錯誤**（API 調用失敗、網絡錯誤）區分開來：

- **業務邏輯失敗**：返回 `{ success: false, eligible: false }`，優雅顯示檢查結果
- **系統錯誤**：返回 `{ success: false, error: "錯誤訊息" }`，顯示錯誤提示

這樣的處理方式更符合實際業務場景，提供更好的用戶體驗。
