# Step 10 確認頁面 400 錯誤修復報告

## 問題描述

在前端整合測試中，從 Step 8 (list-plans) 或 Step 9 (compare-plans) 選擇方案後進入 Step 10 (confirm) 時，出現 400 錯誤：

```
載入申辦摘要失敗: FetchError: [POST] 'http://localhost:8000/api/renewal-workflow/step/confirm': 400
當前步驟為 LIST_PLANS，無法進行確認
```

## 根本原因

前端在選擇方案後直接跳轉到確認頁面，**沒有先呼叫 select-plan API** 更新 session 狀態。

### 後端邏輯要求

```python
# backend/app/routes/renewal_workflow.py - /step/confirm API
if current_step != WorkflowStep.CONFIRM.value:
    return jsonify({
        "success": False,
        "error": f"當前步驟為 {current_step}，無法進行確認"
    }), 400
```

- 確認頁面 API 要求 `current_step == CONFIRM`
- 只有呼叫 select-plan API 後，session 狀態才會從 `LIST_PLANS` 更新為 `CONFIRM`

### 前端問題代碼

**1. list-plans.vue (Step 8)**

```typescript
// 修復前 - 直接跳轉，沒有 API 呼叫
const handleNext = async () => {
  if (!selectedPlan.value) return
  // TODO: 呼叫 select-plan API 並前進到下一步
  navigateTo('/renewal/confirm')
}
```

**2. compare-plans.vue (Step 9)**

```typescript
// 修復前 - 直接跳轉，沒有 API 呼叫
const selectPlan = async (planId: string) => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    // TODO: Call select-plan API
    // For now, just navigate to confirm page
    await router.push({
      path: '/renewal/confirm',
      query: { planId }
    })
  } catch (err: any) {
    console.error('選擇方案錯誤:', err)
    errorMessage.value = err.message || '選擇方案失敗'
    isLoading.value = false
  }
}
```

## 修復方案

### 1. 新增 selectPlan 方法到 composable

**檔案**: `frontend/composables/useRenewalWorkflow.ts`

```typescript
/**
 * Step 8.5: 選擇方案
 */
const selectPlan = async (planId: string) => {
  loading.value = true
  error.value = null
  
  try {
    if (!sessionId.value) {
      throw new Error('請先開始流程')
    }
    
    const authSession = getAuthSessionId()
    if (!authSession) {
      throw new Error('請先登入')
    }
    
    if (!planId) {
      throw new Error('請選擇方案')
    }
    
    const response = await $fetch('/api/renewal-workflow/step/select-plan', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        'X-Session-ID': authSession
      },
      body: {
        session_id: sessionId.value,
        plan_id: planId
      }
    }) as any
    
    if (response.success) {
      currentStep.value = response.next_step
      return response
    } else {
      throw new Error(response.error || '選擇方案失敗')
    }
  } catch (err: any) {
    error.value = err.message || '選擇方案失敗'
    throw err
  } finally {
    loading.value = false
  }
}

// 在 return 中匯出
return {
  // ... 其他方法
  selectPlan,
  // ... 其他方法
}
```

### 2. 修復 list-plans.vue (Step 8)

**檔案**: `frontend/pages/renewal/list-plans.vue`

```typescript
const handleNext = async () => {
  if (!selectedPlan.value) return
  
  try {
    loading.value = true
    error.value = null
    
    // 呼叫 select-plan API 更新 session 狀態到 CONFIRM
    const { selectPlan } = useRenewalWorkflow()
    await selectPlan(selectedPlan.value.plan_id)
    
    // API 成功後才跳轉到確認頁面
    navigateTo('/renewal/confirm')
  } catch (err: any) {
    error.value = err.message || '選擇方案失敗，請稍後再試'
    console.error('Select plan error:', err)
  } finally {
    loading.value = false
  }
}
```

### 3. 修復 compare-plans.vue (Step 9)

**檔案**: `frontend/pages/renewal/compare-plans.vue`

```typescript
const selectPlan = async (planId: string) => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    // 呼叫 select-plan API 更新 session 狀態到 CONFIRM
    const { selectPlan: selectPlanAPI } = useRenewalWorkflow()
    await selectPlanAPI(planId)
    
    // API 成功後才跳轉到確認頁面
    await router.push('/renewal/confirm')
  } catch (err: any) {
    console.error('選擇方案錯誤:', err)
    errorMessage.value = err.message || '選擇方案失敗'
    isLoading.value = false
  }
}
```

## 修復後的完整流程

### Step 8 路徑：方案列表 → 確認頁面

```
1. 用戶在 list-plans.vue 點擊「下一步」
2. 前端呼叫 selectPlan(plan_id) → POST /step/select-plan
3. 後端更新 session:
   - 儲存 selected_plan 資訊
   - 計算費用 (cost_details)
   - current_step = "CONFIRM"
4. API 回傳成功
5. 前端跳轉到 /renewal/confirm
6. confirm 頁面載入，呼叫 POST /step/confirm
7. 後端驗證 current_step == "CONFIRM" ✅
8. 回傳完整申辦摘要
```

### Step 9 路徑：比較方案 → 確認頁面

```
1. 用戶在 compare-plans.vue 點擊某方案的「選擇此方案」
2. 前端呼叫 selectPlanAPI(plan_id) → POST /step/select-plan
3. 後端更新 session (同上)
4. API 回傳成功
5. 前端跳轉到 /renewal/confirm
6. confirm 頁面正常載入 ✅
```

## 後端 select-plan API 功能

**路徑**: `backend/app/routes/renewal_workflow.py`

```python
@bp.route('/step/select-plan', methods=['POST'])
async def select_plan():
    # 1. 驗證 session 和 plan 存在
    # 2. 取得方案詳情
    # 3. 計算升級費用
    cost_result = await promotion_service.calculate_upgrade_cost(
        current_plan_fee=contract.get('monthly_fee', 0),
        new_plan_id=plan_id,
        device_price=device_price,
        contract_type=customer.get('contract_type', '續約')
    )
    
    # 4. 更新 session
    session['selected_plan'] = {
        "plan_id": plan_id,
        "plan_name": plan['name'],
        "monthly_fee": plan['monthly_fee'],
        "contract_months": plan['contract_months'],
        "data": plan['data'],
        "voice": plan['voice'],
        "cost_details": cost_result,
        "selected_at": str(datetime.now())
    }
    
    # 5. 前進到 CONFIRM 步驟 (關鍵!)
    session['current_step'] = WorkflowStep.CONFIRM.value
    await workflow_manager.update_session(session_id, session)
    
    return jsonify({
        "success": True,
        "message": "方案已選擇",
        "next_step": "CONFIRM",
        "selected_plan": session['selected_plan']
    })
```

## 測試驗證

### 測試案例 1: 從方案列表選擇

1. ✅ 啟動後端 (port 8000) 和前端 (port 3000)
2. ✅ 從 Step 1 開始完整流程
3. ✅ 到達 Step 8 方案列表頁
4. ✅ 點擊任一方案卡片選取
5. ✅ 點擊「下一步」按鈕
6. ✅ **預期**: 成功跳轉到 Step 10，顯示完整申辦摘要
7. ✅ **驗證**: 沒有 400 錯誤

### 測試案例 2: 從比較方案選擇

1. ✅ 在 Step 8 勾選 2-4 個方案的「加入比較」
2. ✅ 點擊「比較方案」按鈕進入 Step 9
3. ✅ 在比較表格中點擊任一方案的「選擇此方案」
4. ✅ **預期**: 成功跳轉到 Step 10，顯示完整申辦摘要
5. ✅ **驗證**: 沒有 400 錯誤

### 預期錯誤處理

#### 網路錯誤
```typescript
// 前端顯示錯誤訊息
error.value = "選擇方案失敗，請稍後再試"
// 不跳轉，留在當前頁面
```

#### 方案不存在
```json
{
  "success": false,
  "error": "方案不存在"
}
```

#### Session 不存在
```json
{
  "success": false,
  "error": "Session 不存在"
}
```

## 影響範圍

### 修改檔案

1. ✅ `frontend/composables/useRenewalWorkflow.ts`
   - 新增 `selectPlan()` 方法
   - 在 return 中匯出 `selectPlan`

2. ✅ `frontend/pages/renewal/list-plans.vue`
   - 修復 `handleNext()` 方法
   - 新增 API 呼叫和錯誤處理

3. ✅ `frontend/pages/renewal/compare-plans.vue`
   - 修復 `selectPlan()` 方法
   - 新增 API 呼叫和錯誤處理

### 未修改檔案

- ❌ 後端 API（已正確實作，無需修改）
- ❌ confirm.vue（無需修改，只是呼叫端）
- ❌ 其他前端頁面（不涉及方案選擇）

## 總結

### 問題本質

前端實作不完整，有 TODO 註解但沒有實際呼叫 API，導致後端 session 狀態機流程中斷。

### 解決方案

補齊缺少的 API 呼叫，確保 session 狀態正確轉換：`LIST_PLANS → CONFIRM`

### 關鍵學習

1. **狀態機要完整**: 後端用 WorkflowStep enum 控制流程，前端必須配合呼叫對應 API
2. **不要跳過步驟**: 每個步驟的狀態轉換都有對應的 API，不能直接跳轉頁面
3. **TODO 要完成**: TODO 註解應該在開發完成前清除，避免留下未實作的功能
4. **錯誤處理**: API 呼叫失敗時要顯示錯誤，不能靜默跳轉

### 後續行動

- [x] 修復 Step 8 → Step 10 流程
- [x] 修復 Step 9 → Step 10 流程
- [ ] 執行完整前端整合測試
- [ ] 更新測試文檔記錄測試結果
- [ ] 確認所有 TODO 註解都已清除

## 修復日期

2025-10-31

## 測試狀態

- [ ] Step 8 → Step 10: 待測試
- [ ] Step 9 → Step 10: 待測試
- [ ] 完整 E2E 流程: 待測試
