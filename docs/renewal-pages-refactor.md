# 續約流程頁面重構說明

## 重構目標

將原本的單一大頁面（573行）拆分為：
- 1個主布局頁面
- 4個子功能頁面

這樣的結構更清晰、更易維護、更符合職責單一原則。

## 新的頁面結構

```
frontend/pages/
├── renewal.vue                    # 主布局頁面（導航列 + 進度條 + 子頁面容器）
└── renewal/
    ├── index.vue                  # 重定向頁面
    ├── query-customer.vue         # Step 1: 查詢客戶
    ├── select-phone.vue           # Step 2: 選擇門號
    ├── eligibility.vue            # Step 3: 資格檢查
    └── select-plan.vue            # Step 4: 選擇方案（Sprint 3）
```

## 路由結構

```
/renewal                           → 重定向到 /renewal/query-customer
/renewal/query-customer            → 查詢客戶頁面
/renewal/select-phone              → 選擇門號頁面
/renewal/eligibility               → 資格檢查結果頁面
/renewal/select-plan               → 選擇方案頁面（待實作）
```

## 頁面詳細說明

### 1. renewal.vue（主布局頁面）

**職責：**
- 提供統一的導航列
- 顯示進度條指示器
- 渲染子頁面內容（`<NuxtPage />`）
- 管理返回邏輯
- 初始化工作流會話

**包含元素：**
- AppNavbar 組件
- 4步驟進度條
- 子頁面容器

**代碼行數：** ~120 行

**關鍵功能：**
```vue
<template>
  <div>
    <AppNavbar @back="goBack" />
    <ProgressBar :currentStep="currentStepIndex" />
    <NuxtPage /> <!-- 子頁面渲染位置 -->
  </div>
</template>
```

### 2. renewal/query-customer.vue（查詢客戶）

**職責：**
- 輸入身分證號
- 呼叫查詢 API
- 導航到選擇門號頁面

**包含元素：**
- 身分證號輸入框
- 查詢按鈕
- 測試資料快速填入
- 測試帳號提示

**代碼行數：** ~90 行

**API 調用：**
- `startWorkflow()` - 如果沒有 session
- `queryCustomer()` - 查詢客戶資料
- `listPhones()` - 取得門號列表

**導航流程：**
```
查詢成功 → navigateTo('/renewal/select-phone')
```

### 3. renewal/select-phone.vue（選擇門號）

**職責：**
- 顯示客戶資訊
- 列出所有門號
- 選擇門號並檢查資格
- 導航到資格檢查頁面

**包含元素：**
- 客戶資訊卡片
- 門號卡片列表（可展開詳細資訊）
- 合約/使用量/帳單資訊

**代碼行數：** ~180 行

**API 調用：**
- `selectPhone(phoneNumber)` - 選擇門號並檢查資格

**導航流程：**
```
未查詢客戶 → navigateTo('/renewal/query-customer')
選擇門號後 → navigateTo('/renewal/eligibility')
```

### 4. renewal/eligibility.vue（資格檢查）

**職責：**
- 顯示資格檢查結果
- 列出所有檢查項目
- 提供繼續或返回選項

**包含元素：**
- 符合/不符合資格的視覺提示
- 檢查項目詳細列表
- 操作按鈕

**代碼行數：** ~150 行

**導航流程：**
```
未選擇門號 → navigateTo('/renewal/select-phone')
選擇其他門號 → navigateTo('/renewal/select-phone')
繼續流程 → navigateTo('/renewal/select-plan')
```

### 5. renewal/select-plan.vue（選擇方案）

**職責：**
- Sprint 3 佔位頁面
- 顯示待實作功能預覽

**代碼行數：** ~50 行

## 數據流和狀態管理

### Composable 狀態共享

所有子頁面共享 `useRenewalWorkflow()` composable 的狀態：

```typescript
const {
  sessionId,        // 工作流會話 ID
  customer,         // 客戶資料
  phones,           // 門號列表
  selectedPhone,    // 選中的門號
  eligibilityCheck, // 資格檢查結果
  loading,          // 載入狀態
  error,            // 錯誤訊息
  
  // 方法
  startWorkflow,
  queryCustomer,
  listPhones,
  selectPhone,
  clearSelection,
  clearWorkflow
} = useRenewalWorkflow()
```

### 頁面間導航保護

每個子頁面在 `onMounted` 時檢查必要狀態：

```typescript
// select-phone.vue
onMounted(() => {
  if (!customer.value) {
    navigateTo('/renewal/query-customer')
  }
})

// eligibility.vue
onMounted(() => {
  if (!selectedPhone.value) {
    navigateTo('/renewal/select-phone')
  }
})
```

## 進度條邏輯

主頁面根據當前路由自動計算步驟索引：

```typescript
const currentStepIndex = computed(() => {
  const path = route.path
  if (path.includes('/select-phone')) return 1
  if (path.includes('/eligibility')) return 2
  if (path.includes('/select-plan')) return 3
  return 0 // query-customer
})
```

## 返回邏輯

主頁面的 `goBack` 函數根據當前步驟決定行為：

```typescript
const goBack = () => {
  if (currentStepIndex.value === 0) {
    // 第一步，返回首頁
    navigateTo('/')
  } else {
    // 其他步驟，返回上一步
    const prevStep = steps[currentStepIndex.value - 1]
    navigateTo(prevStep.path)
  }
}
```

## 優勢對比

### 重構前（單一頁面）
- ❌ 573 行代碼，難以維護
- ❌ 所有邏輯混在一起
- ❌ 難以單獨測試某個步驟
- ❌ 條件判斷複雜（v-if 嵌套）
- ❌ 難以並行開發

### 重構後（多頁面）
- ✅ 每個頁面 50-180 行，清晰易讀
- ✅ 職責分離，符合單一職責原則
- ✅ 可以單獨測試每個步驟
- ✅ 路由驅動，狀態管理簡單
- ✅ 團隊可以並行開發不同步驟
- ✅ 易於擴展新步驟（Sprint 3）

## 代碼行數對比

| 文件 | 行數 | 說明 |
|------|------|------|
| **重構前** | | |
| renewal/index.vue | 573 | 包含所有步驟 |
| **總計** | **573** | |
| | | |
| **重構後** | | |
| renewal.vue | 120 | 主布局 |
| query-customer.vue | 90 | Step 1 |
| select-phone.vue | 180 | Step 2 |
| eligibility.vue | 150 | Step 3 |
| select-plan.vue | 50 | Step 4（佔位） |
| index.vue | 15 | 重定向 |
| **總計** | **605** | 含註釋和空行 |

雖然總行數略增（+32行），但可維護性大幅提升。

## 測試指南

### 測試流程 1：完整流程

1. 訪問 http://localhost:3000/renewal
2. 應該自動重定向到 `/renewal/query-customer`
3. 輸入測試身分證號：`A123456789`
4. 點擊「查詢客戶」
5. 應該導航到 `/renewal/select-phone`
6. 選擇門號：`0911-111-222`
7. 應該導航到 `/renewal/eligibility`
8. 查看資格檢查結果
9. 點擊「繼續選擇方案」
10. 應該導航到 `/renewal/select-plan`

### 測試流程 2：返回導航

1. 在 `/renewal/eligibility` 頁面
2. 點擊導航列的返回按鈕
3. 應該返回到 `/renewal/select-phone`
4. 再次點擊返回按鈕
5. 應該返回到 `/renewal/query-customer`
6. 再次點擊返回按鈕
7. 應該返回到首頁 `/`

### 測試流程 3：直接訪問檢查

1. 直接訪問 http://localhost:3000/renewal/eligibility
2. 因為沒有選擇門號，應該重定向到 `/renewal/select-phone`
3. 因為沒有查詢客戶，應該重定向到 `/renewal/query-customer`

### 測試流程 4：進度條顯示

1. 在每個步驟頁面檢查進度條
2. 當前步驟應該高亮顯示
3. 已完成步驟應該顯示為完成狀態
4. 未完成步驟應該顯示為灰色

## 未來擴展

### Sprint 3 步驟

當實作 Sprint 3 時，只需要：

1. 更新 `select-plan.vue` 的內容
2. 創建新的子頁面（如需要）：
   - `renewal/select-device-type.vue`
   - `renewal/select-device.vue`
   - `renewal/select-device-specs.vue`
   - `renewal/compare-plans.vue`
   - `renewal/confirm.vue`

3. 更新主頁面的步驟定義

### 添加新步驟示例

```vue
// renewal.vue
const steps = [
  { label: '查詢客戶', path: '/renewal/query-customer' },
  { label: '選擇門號', path: '/renewal/select-phone' },
  { label: '資格檢查', path: '/renewal/eligibility' },
  { label: '選擇類型', path: '/renewal/select-type' }, // 新增
  { label: '選擇裝置', path: '/renewal/select-device' }, // 新增
  { label: '選擇方案', path: '/renewal/select-plan' },
  { label: '確認訂單', path: '/renewal/confirm' } // 新增
]
```

## 遷移注意事項

### 1. 路由變更

**舊路由：**
```
/renewal/index  → 單一頁面
```

**新路由：**
```
/renewal  → 主布局（重定向）
/renewal/query-customer  → 查詢客戶
/renewal/select-phone    → 選擇門號
/renewal/eligibility     → 資格檢查
/renewal/select-plan     → 選擇方案
```

### 2. 書籤和外部連結

如果有外部系統連結到 `/renewal`，需要更新為具體的子頁面路徑。

### 3. 備份文件

舊的 `renewal/index.vue` 已備份為 `renewal/index.vue.old`，可以隨時恢復或參考。

## 總結

這次重構將單一大頁面拆分為多個小頁面，帶來的好處：

1. ✅ **可維護性** - 每個文件職責單一，易於理解和修改
2. ✅ **可測試性** - 可以單獨測試每個步驟
3. ✅ **可擴展性** - 添加新步驟只需新增文件
4. ✅ **團隊協作** - 多人可以同時開發不同步驟
5. ✅ **用戶體驗** - 每個步驟有獨立 URL，可以書籤、分享、刷新
6. ✅ **代碼組織** - 符合 Nuxt 3 的最佳實踐

這是一次成功的重構，為後續的 Sprint 3 開發奠定了良好的基礎。
