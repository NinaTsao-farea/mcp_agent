# 從首頁重新開始續約流程 - 問題修正

## 問題描述

用戶在續約流程中途（例如在 `select-device` 頁面）點擊導航列的「返回」按鈕回到首頁，然後再次點擊「開始續約」，會遇到以下錯誤：

```
POST /api/renewal-workflow/step/query-customer 500
error: "非法的狀態轉換: WorkflowStep.SELECT_DEVICE_TYPE -> WorkflowStep.QUERY_CUSTOMER"
```

## 根本原因

1. 舊的 renewal session 仍然存在，狀態停留在 `SELECT_DEVICE_TYPE`
2. 前端沒有清空舊 session，而是繼續使用它
3. 當嘗試查詢客戶時，後端拒絕從 `SELECT_DEVICE_TYPE` 轉換到 `QUERY_CUSTOMER`（違反工作流程規則）

## 解決方案

修改 `frontend/pages/renewal/index.vue`，在重定向到 `query-customer` 頁面之前，先清空舊的 session：

```vue
<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

// 清空舊的 session，開始新的流程
const { clearWorkflow } = useRenewalWorkflow()

onMounted(() => {
  // 清空舊流程
  clearWorkflow()
  
  // 重定向到查詢客戶頁面
  navigateTo('/renewal/query-customer', { replace: true })
})
</script>
```

## 工作流程

### 修正前

```
首頁 -> 點擊「開始續約」
  -> /renewal (自動重定向)
  -> /renewal/query-customer
  -> 檢查 sessionId (存在舊的)
  -> ❌ 直接使用舊 session 查詢客戶
  -> ❌ 狀態轉換失敗 (SELECT_DEVICE_TYPE -> QUERY_CUSTOMER)
```

### 修正後

```
首頁 -> 點擊「開始續約」
  -> /renewal (自動重定向)
  -> onMounted 執行
  -> ✅ clearWorkflow() 刪除舊 session
  -> /renewal/query-customer
  -> 檢查 sessionId (null)
  -> ✅ startWorkflow() 創建新 session
  -> ✅ 查詢客戶成功 (INIT -> QUERY_CUSTOMER)
```

## `clearWorkflow()` 功能

位於 `frontend/composables/useRenewalWorkflow.ts`，功能包括：

1. 調用後端 API 刪除 server 端的 session
2. 清空前端狀態（sessionId, customer, phones, etc.）
3. 清除 localStorage 中的 `renewal_session_id`

## 測試驗證

執行 `backend/test_restart_workflow_from_homepage.py` 驗證：

```bash
cd backend
python test_restart_workflow_from_homepage.py
```

**測試步驟**：
1. 登入
2. 開始第一次續約流程
3. 完成查詢客戶、選擇門號、選擇裝置類型
4. 模擬返回首頁（session 仍存在）
5. 刪除舊 session
6. 開始第二次續約流程（新 session）
7. ✅ 驗證可以成功查詢客戶，沒有狀態轉換錯誤

## 相關文件

- `frontend/pages/renewal/index.vue` - 續約流程入口頁面
- `frontend/pages/renewal/query-customer.vue` - 查詢客戶頁面
- `frontend/composables/useRenewalWorkflow.ts` - 續約流程狀態管理
- `backend/test_restart_workflow_from_homepage.py` - 自動化測試
