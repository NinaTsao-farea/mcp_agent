# Step 5 功能完成度分析報告

## 📋 Step 5 定義

**功能名稱**：選擇裝置類型（Select Device Type）

**功能描述**：
- 讓門市人員選擇客戶的續約方式
- 決定是否搭配裝置購買
- 根據選擇分流後續流程

**選項**：
1. 不選擇裝置（單純續約）→ 跳到 Step 8（方案選擇）
2. 智慧型手機（Smartphone）→ 繼續 Step 6（作業系統選擇）
3. 平板（Tablet）→ 繼續 Step 6
4. 穿戴裝置（Wearable）→ 繼續 Step 6

---

## ✅ 後端實現狀態

### 1. 狀態機定義 ✅ 已完成

**文件**：`backend/app/services/workflow_session.py`

```python
class WorkflowStep(str, Enum):
    SELECT_DEVICE_TYPE = "select_device_type"
    # ... 其他步驟

# 狀態轉換規則
ALLOWED_TRANSITIONS = {
    WorkflowStep.CHECK_ELIGIBILITY: [WorkflowStep.SELECT_DEVICE_TYPE],
    WorkflowStep.SELECT_DEVICE_TYPE: [
        WorkflowStep.SELECT_DEVICE_OS,  # 選擇裝置時
        WorkflowStep.LIST_PLANS          # 不選擇裝置時
    ],
}
```

**狀態**：✅ 正確實現

### 2. API 端點 ❌ 未實現

**預期路由**：`POST /api/renewal-workflow/step/select-device-type`

**實際狀態**：
- ❌ 路由不存在於 `backend/app/routes/renewal_workflow.py`
- ❌ 沒有對應的處理函數

**影響**：前端無法調用 API

### 3. 測試代碼 ✅ 部分完成

**文件**：`backend/test_renewal_flow_complete.py`

```python
# Step 5: 選擇裝置類型
device_type = "smartphone"
session['device_type'] = device_type
session['current_step'] = WorkflowStep.SELECT_DEVICE.value
```

**狀態**：✅ 測試中手動模擬了此步驟

---

## ❌ 前端實現狀態

### 1. UI 頁面 ❌ 未實現

**預期文件**：`frontend/pages/renewal/select-device-type.vue`

**實際狀態**：
- ❌ 文件不存在
- ❌ `select-plan.vue` 只是佔位頁面，顯示 "此功能將在 Sprint 3 實作"

**影響**：
- 無法從 UI 進行裝置類型選擇
- Step 4 到 Step 8 之間斷層

### 2. Composable 方法 ❌ 未實現

**預期方法**：`useRenewalWorkflow.ts` 應包含：

```typescript
const selectDeviceType = async (deviceType: string) => {
  // 調用 POST /step/select-device-type
}
```

**實際狀態**：
- ❌ 方法不存在
- ❌ 前端無法與後端 API 互動

---

## 📊 完成度總結

| 層級 | 組件 | 狀態 | 完成度 |
|------|------|------|--------|
| **後端** | 狀態機定義 | ✅ 完成 | 100% |
| **後端** | API 端點 | ❌ 缺失 | 0% |
| **後端** | 業務邏輯 | ❌ 缺失 | 0% |
| **後端** | 測試代碼 | ⚠️ 手動模擬 | 50% |
| **前端** | UI 頁面 | ❌ 缺失 | 0% |
| **前端** | Composable | ❌ 缺失 | 0% |
| **前端** | 路由配置 | ❌ 缺失 | 0% |
| **整體** | **Step 5** | ❌ **未完成** | **15%** |

---

## 🔧 待實現內容

### 後端任務

#### 1. 實現 API 端點

**文件**：`backend/app/routes/renewal_workflow.py`

```python
@bp.route('/step/select-device-type', methods=['POST'])
async def select_device_type():
    """
    Step 5: 選擇裝置類型
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "device_type": "smartphone" | "tablet" | "wearable" | "none"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        device_type = data.get('device_type')
        
        # 驗證參數
        valid_types = ["smartphone", "tablet", "wearable", "none"]
        if device_type not in valid_types:
            return jsonify({
                "success": False,
                "error": "無效的裝置類型"
            }), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({
                "success": False,
                "error": "Session 不存在或已過期"
            }), 404
        
        # 檢查前置步驟
        if session_data.get('current_step') != WorkflowStep.SELECT_DEVICE_TYPE.value:
            return jsonify({
                "success": False,
                "error": "請先完成資格檢查"
            }), 400
        
        # 更新 Session
        await workflow_manager.update_customer_selection(
            session_id,
            {"device_type": device_type}
        )
        
        # 決定下一步
        if device_type == "none":
            # 跳過裝置選擇，直接到方案選擇
            next_step = WorkflowStep.LIST_PLANS
        else:
            # 繼續裝置選擇流程
            next_step = WorkflowStep.SELECT_DEVICE_OS
        
        await workflow_manager.transition_to_step(session_id, next_step)
        
        logger.info(
            "裝置類型已選擇",
            session_id=session_id,
            device_type=device_type,
            next_step=next_step.value
        )
        
        return jsonify({
            "success": True,
            "message": "裝置類型已選擇",
            "device_type": device_type,
            "next_step": next_step.value
        })
        
    except Exception as e:
        logger.error("選擇裝置類型錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500
```

### 前端任務

#### 1. 創建 UI 頁面

**文件**：`frontend/pages/renewal/select-device-type.vue`

```vue
<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">選擇續約方式</h1>
        <p class="mt-2 text-gray-600">請選擇是否搭配裝置購買</p>
      </div>

      <!-- 選項卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 單純續約 -->
        <div 
          class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition"
          :class="{ 'ring-2 ring-blue-500': selectedType === 'none' }"
          @click="selectType('none')"
        >
          <UIcon name="i-heroicons-phone-arrow-up-right" class="w-12 h-12 text-blue-600 mb-4" />
          <h3 class="text-xl font-semibold mb-2">單純續約</h3>
          <p class="text-gray-600">不搭配裝置購買，直接選擇資費方案</p>
        </div>

        <!-- 智慧型手機 -->
        <div 
          class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition"
          :class="{ 'ring-2 ring-blue-500': selectedType === 'smartphone' }"
          @click="selectType('smartphone')"
        >
          <UIcon name="i-heroicons-device-phone-mobile" class="w-12 h-12 text-blue-600 mb-4" />
          <h3 class="text-xl font-semibold mb-2">智慧型手機</h3>
          <p class="text-gray-600">搭配 iPhone、Android 手機購買</p>
        </div>

        <!-- 平板 -->
        <div 
          class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition"
          :class="{ 'ring-2 ring-blue-500': selectedType === 'tablet' }"
          @click="selectType('tablet')"
        >
          <UIcon name="i-heroicons-device-tablet" class="w-12 h-12 text-blue-600 mb-4" />
          <h3 class="text-xl font-semibold mb-2">平板電腦</h3>
          <p class="text-gray-600">搭配 iPad、Android 平板購買</p>
        </div>

        <!-- 穿戴裝置 -->
        <div 
          class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition"
          :class="{ 'ring-2 ring-blue-500': selectedType === 'wearable' }"
          @click="selectType('wearable')"
        >
          <UIcon name="i-heroicons-clock" class="w-12 h-12 text-blue-600 mb-4" />
          <h3 class="text-xl font-semibold mb-2">穿戴裝置</h3>
          <p class="text-gray-600">搭配智慧手錶、手環購買</p>
        </div>
      </div>

      <!-- 操作按鈕 -->
      <div class="mt-8 flex justify-between">
        <UButton
          variant="outline"
          size="lg"
          @click="goBack"
        >
          返回
        </UButton>
        <UButton
          size="lg"
          :disabled="!selectedType || loading"
          :loading="loading"
          @click="handleSubmit"
        >
          下一步
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const { selectDeviceType } = useRenewalWorkflow()

const selectedType = ref<string | null>(null)
const loading = ref(false)

const renewalSessionId = computed(() => {
  return route.query.session_id as string || null
})

const selectType = (type: string) => {
  selectedType.value = type
}

const handleSubmit = async () => {
  if (!selectedType.value || !renewalSessionId.value) return
  
  loading.value = true
  try {
    const result = await selectDeviceType(renewalSessionId.value, selectedType.value)
    
    if (result.success) {
      // 根據選擇導向不同頁面
      if (selectedType.value === 'none') {
        // 跳到方案選擇
        router.push({
          path: '/renewal/select-plan',
          query: { session_id: renewalSessionId.value }
        })
      } else {
        // 繼續裝置選擇
        router.push({
          path: '/renewal/select-device-os',
          query: { 
            session_id: renewalSessionId.value,
            device_type: selectedType.value
          }
        })
      }
    }
  } catch (error) {
    console.error('選擇裝置類型失敗:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>
```

#### 2. 更新 Composable

**文件**：`frontend/composables/useRenewalWorkflow.ts`

```typescript
const selectDeviceType = async (sessionId: string, deviceType: string) => {
  loading.value = true
  error.value = null
  
  try {
    const authSession = getAuthSessionId()
    if (!authSession) {
      throw new Error('請先登入')
    }
    
    const response = await $fetch('/api/renewal-workflow/step/select-device-type', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        'X-Session-ID': authSession
      },
      body: {
        session_id: sessionId,
        device_type: deviceType
      }
    }) as any
    
    if (response.success) {
      return response
    } else {
      throw new Error(response.error || '選擇裝置類型失敗')
    }
  } catch (err: any) {
    error.value = err.message || '選擇裝置類型失敗'
    throw err
  } finally {
    loading.value = false
  }
}

// 在 return 中導出
return {
  // ... 其他方法
  selectDeviceType,
}
```

---

## 🎯 實現優先級

### P0（必須）
1. ✅ 更新 spec.md 補充 Step 5 詳細描述
2. ⬜ 實現後端 API 端點 `/step/select-device-type`
3. ⬜ 創建前端頁面 `select-device-type.vue`
4. ⬜ 更新 Composable 新增 `selectDeviceType()` 方法

### P1（重要）
5. ⬜ 新增單元測試（後端）
6. ⬜ 新增 E2E 測試（前端）
7. ⬜ 更新導航流程（從 eligibility → select-device-type）

### P2（可選）
8. ⬜ 優化 UI 設計（圖標、動畫）
9. ⬜ 新增裝置類型說明（tooltip）
10. ⬜ 統計追蹤（記錄選擇分布）

---

## 📝 開發建議

### Sprint 規劃
- **當前狀態**：Step 5 屬於 Sprint 3 範圍（Step 5-7）
- **建議**：在完成 Step 10（Sprint 6）後，回頭補完 Step 5-9
- **原因**：
  - Step 1-4 ✅ 已完成
  - Step 10 ✅ 已完成
  - Step 5-9 ❌ 完全缺失，需整體實現

### 測試流程
完成 Step 5 後，應能實現以下測試路徑：

```
登入 → Step 1 → Step 2-3 → Step 4 → 
  → Step 5（選擇）→ 
    ├─ 單純續約 → Step 8（待實現）
    └─ 搭配裝置 → Step 6（待實現）
```

---

## 🔗 相關文件

- 📄 [spec.md](../spec.md) - 系統規格文件（已更新 Step 5 描述）
- 📄 [Sprint 3 計畫](../docs/sprint3-preparation.md) - Sprint 3 開發計畫
- 📄 [workflow_session.py](../backend/app/services/workflow_session.py) - 狀態機定義
- 📄 [renewal_workflow.py](../backend/app/routes/renewal_workflow.py) - API 路由（待新增）

---

**報告生成時間**：2025-10-29
**報告作者**：AI Assistant
**文件版本**：v1.0
