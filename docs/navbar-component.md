# 共用導航栏組件實作說明

## 修改內容

### 1. 創建共用組件：AppNavbar.vue

**位置：** `frontend/components/AppNavbar.vue`

**功能：**
- 顯示系統標題或自定義左側內容（通過插槽）
- 顯示當前登入用戶名稱
- 提供登出功能
- 自動處理登出時的數據清理（認證會話 + 工作流會話）

**特性：**
- ✅ 支持插槽（slot）自定義左側內容
- ✅ 支持 `showWelcome` prop 控制是否顯示"歡迎"文字
- ✅ 統一的登出邏輯，確保數據清理完整

**使用方式：**

```vue
<!-- 方式 1: 預設使用（首頁） -->
<AppNavbar />

<!-- 方式 2: 簡單返回（自動返回首頁） -->
<AppNavbar 
  :show-back="true" 
  title="設定頁面"
/>

<!-- 方式 3: 指定返回路徑 -->
<AppNavbar 
  :show-back="true" 
  title="客戶詳情"
  back-to="/customers"
/>

<!-- 方式 4: 自定義返回邏輯（如續約頁面） -->
<AppNavbar 
  :show-welcome="false" 
  :show-back="true" 
  title="續約流程"
  @back="goBack"
/>
```

### 2. 修改首頁：index.vue

**變更：**
- ❌ 移除原有的導航列 HTML 代碼
- ✅ 使用 `<AppNavbar />` 組件
- ❌ 移除 `logout` 函數（已在 AppNavbar 中）
- ❌ 移除 `useAuth()` 的 `user` 和 `logout` 解構
- ❌ 移除 `useRenewalWorkflow()` 的 `clearWorkflow` 解構

**簡化代碼：**
- 從 ~210 行減少到 ~180 行
- 登出邏輯集中管理，避免重複代碼

### 3. 修改續約頁面：renewal/index.vue

**變更：**
- ❌ 移除原有的導航列 HTML 代碼
- ✅ 使用 `<AppNavbar :show-welcome="false">` 組件
- ✅ 通過 `#left` 插槽提供返回按鈕和標題
- ❌ 移除 `useAuth()` 的 `user` 解構（由 AppNavbar 管理）

**優勢：**
- 統一的導航列樣式
- 統一的登出邏輯
- 減少代碼重複

## 組件結構

```
AppNavbar.vue
├── 左側區域（可自定義）
│   ├── [插槽] 自定義內容（返回按鈕、標題等）
│   └── [預設] 系統標題
├── 右側區域
│   ├── 用戶名稱顯示
│   └── 登出按鈕
└── 登出處理邏輯
    ├── clearWorkflow() - 清除工作流狀態
    ├── authLogout() - 執行登出
    └── navigateTo('/login') - 跳轉登入頁
```

## Props 和 Events

### Props
- `showWelcome` (Boolean, default: true)
  - `true`: 顯示「歡迎，用戶名」
  - `false`: 只顯示「用戶名」

- `showBack` (Boolean, default: false)
  - `true`: 顯示返回按鈕
  - `false`: 不顯示返回按鈕

- `title` (String, default: '')
  - 自定義標題文字
  - 如果為空，顯示「電信門市銷售助理系統」

- `backTo` (String, default: '/')
  - 返回按鈕的預設導航目標
  - 只在沒有監聽 `@back` 事件時使用

### Events
- `@back`: 返回按鈕點擊事件（可選）
  - 如果監聽此事件：由頁面完全控制返回行為
  - 如果不監聽：自動導航到 `backTo` 路徑

## 優勢

### 1. 代碼重用
- ✅ 導航列代碼只維護一份
- ✅ 登出邏輯統一管理
- ✅ 樣式一致性保證

### 2. 易於維護
- ✅ 修改導航列樣式只需改一個文件
- ✅ 登出邏輯變更不需要修改多個頁面
- ✅ 新增頁面時直接使用組件

### 3. 靈活性
- ✅ 支持自定義左側內容（插槽）
- ✅ 支持控制用戶名顯示方式（props）
- ✅ 可擴展其他功能（如通知、菜單等）

## 使用範例

### 範例 1：首頁（無返回按鈕）
```vue
<template>
  <div>
    <AppNavbar />
    <!-- 頁面內容 -->
  </div>
</template>
```

### 範例 2：簡單頁面（自動返回首頁）
```vue
<template>
  <div>
    <AppNavbar 
      :show-back="true" 
      title="關於我們"
    />
    <!-- 不需要定義 goBack 函數 -->
    <!-- 點擊返回會自動導航到 '/' -->
  </div>
</template>
```

### 範例 3：列表詳情頁（指定返回路徑）
```vue
<template>
  <div>
    <AppNavbar 
      :show-back="true" 
      title="客戶詳情"
      back-to="/customers"
    />
    <!-- 點擊返回會導航到 '/customers' -->
  </div>
</template>
```

### 範例 4：複雜流程頁面（自定義返回邏輯）
```vue
<template>
  <div>
    <AppNavbar 
      :show-back="true" 
      title="續約流程"
      @back="handleBack"
    />
    <!-- 頁面內容 -->
  </div>
</template>

<script setup>
const handleBack = () => {
  // 根據當前步驟決定返回行為
  if (currentStep.value === 0) {
    navigateTo('/')
  } else {
    goToPreviousStep()
  }
}
</script>
```

## 測試檢查

### 首頁測試
1. 訪問 http://localhost:3000
2. 確認導航列顯示：
   - 左側：「電信門市銷售助理系統」
   - 右側：「歡迎，用戶名」+ 登出按鈕
   - 沒有返回按鈕
3. 點擊登出按鈕
4. 確認跳轉到登入頁面
5. 確認 localStorage 數據被清除

### 續約頁面測試
1. 訪問 http://localhost:3000/renewal
2. 確認導航列顯示：
   - 左側：返回按鈕 + 「續約流程」
   - 右側：「用戶名」（無"歡迎"）+ 登出按鈕
3. 在 Step 1 點擊返回按鈕
4. 確認返回首頁
5. 開始續約流程，進入 Step 2
6. 點擊返回按鈕
7. 確認返回到門號列表（Step 2）而不是首頁
8. 點擊登出按鈕
9. 確認跳轉到登入頁面

### 登出功能測試
1. 登入系統
2. 開始續約流程並查詢客戶
3. 在任意頁面點擊登出
4. 檢查 Network 面板：
   - ✅ DELETE /api/renewal-workflow/session/{id}
   - ✅ POST /api/auth/logout
5. 檢查 localStorage：
   - ✅ session_id 被清除
   - ✅ user 被清除
   - ✅ renewal_session_id 被清除

## 未來擴展建議

### 1. 添加麵包屑導航
```vue
<AppNavbar>
  <template #breadcrumb>
    <span>首頁 > 續約流程 > 查詢客戶</span>
  </template>
</AppNavbar>
```

### 2. 添加通知圖標
```vue
<AppNavbar show-notifications />
```

### 3. 添加用戶菜單
```vue
<AppNavbar>
  <template #user-menu>
    <UDropdown>
      <UButton>{{ user.name }}</UButton>
      <template #content>
        <UDropdownItem>個人設定</UDropdownItem>
        <UDropdownItem>變更密碼</UDropdownItem>
        <UDropdownItem @click="logout">登出</UDropdownItem>
      </template>
    </UDropdown>
  </template>
</AppNavbar>
```

## 總結

此次重構將導航列提取為共用組件，具有以下優點：
1. ✅ **減少重複代碼**：從多個頁面中移除重複的導航列代碼
2. ✅ **統一用戶體驗**：所有頁面的導航列外觀和行為一致
3. ✅ **易於維護**：修改導航列只需改一處
4. ✅ **靈活可擴展**：支持插槽和 props 自定義
5. ✅ **統一登出邏輯**：確保數據清理的完整性和一致性

這是一個符合 Vue 3 最佳實踐的組件化設計。
