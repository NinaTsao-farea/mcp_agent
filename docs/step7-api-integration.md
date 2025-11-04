# Step 7 整合真實 API - 變更摘要

## 📋 變更概述

將 Step 7 (選擇裝置) 的前端頁面從使用假資料改為調用後端真實 API `query-devices`。

## 🔧 後端變更

### 1. 修正 `renewal_workflow.py` - query-devices API

**檔案**: `backend/app/routes/renewal_workflow.py`

**問題**: API 從錯誤的 session 位置讀取 OS 類型
- 原本: 從 `session_data['device']['os_preference']` 讀取
- 實際: Step 6 儲存在 `session_data['customer_selection']['device_os']`

**修正** (Line ~513-527):
```python
# 檢查是否已選擇作業系統 (從 customer_selection 取得)
customer_selection = session_data.get('customer_selection', {})
os_preference = customer_selection.get('device_os')

if not os_preference:
    return jsonify({
        "success": False,
        "error": "請先選擇作業系統"
    }), 400
```

### 2. 修正 `renewal_workflow.py` - get-recommendations API

**檔案**: `backend/app/routes/renewal_workflow.py`

**修正** (Line ~583-597):
```python
# 檢查是否已選擇作業系統 (從 customer_selection 取得)
customer_selection = session_data.get('customer_selection', {})
os_preference = customer_selection.get('device_os')

if not os_preference:
    return jsonify({
        "success": False,
        "error": "請先選擇作業系統"
    }), 400
```

## 🎨 前端變更

### 1. 移除假資料

**檔案**: `frontend/pages/renewal/select-device.vue`

**移除** (Line 245-336):
- 刪除整個 `mockDevices` 陣列 (90+ 行假資料)
- 包含 5 個假設備 (iPhone 15 Pro, iPhone 15, Galaxy S24 Ultra, Galaxy S24, Pixel 8 Pro)

### 2. 更新 `loadDevices` 方法

**檔案**: `frontend/pages/renewal/select-device.vue`

**修改** (Line ~300-340):

**修改前**:
```typescript
const loadDevices = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Mock delay
    await new Promise(resolve => setTimeout(resolve, 500))
    devices.value = mockDevices
  } catch (err) {
    error.value = '載入裝置列表失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}
```

**修改後**:
```typescript
const loadDevices = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await $fetch('/api/renewal-workflow/step/query-devices', {
      method: 'POST',
      body: {
        session_id: sessionId.value,
        store_id: 'STORE001'
      }
    })
    
    if (response.success && response.devices) {
      // 將後端資料結構映射到前端需要的格式
      devices.value = response.devices.map((device: any) => ({
        device_id: device.device_id,
        brand: device.brand,
        model: device.model,
        os: device.os,
        processor: device.chip || 'N/A',
        storage: device.storage,
        screen_size: device.screen_size,
        colors: [device.color], // 後端每個設備是單一顏色，包裝成陣列
        contract_price: device.price,
        original_price: device.market_price,
        stock_status: device.available > 5 ? 'in_stock' : 
                      device.available > 0 ? 'low_stock' : 'out_of_stock',
        is_recommended: device.available > 10, // 庫存充足的設為推薦
        image_url: `/images/${device.brand.toLowerCase()}-${device.model.toLowerCase().replace(/\s+/g, '-')}.jpg`,
        available: device.available,
        total_quantity: device.total_quantity
      }))
    } else {
      error.value = response.error || '載入裝置列表失敗'
    }
  } catch (err: any) {
    error.value = err.data?.error || '載入裝置列表失敗，請稍後再試'
    console.error('Load devices error:', err)
  } finally {
    loading.value = false
  }
}
```

### 3. 簡化顏色選擇邏輯

**檔案**: `frontend/pages/renewal/select-device.vue`

**修改** (Line ~368-395):

**原因**: 後端每個設備只有單一顏色（`device.color` 是字串），不需要顏色選擇彈窗。

**修改前**:
```typescript
const selectDeviceCard = (device: any) => {
  if (device.stock_status === 'out_of_stock') {
    return
  }
  
  selectedDevice.value = device
  
  // If device has colors, show color selection modal
  if (device.colors && device.colors.length > 0) {
    selectedColor.value = device.colors[0]
    showColorModal.value = true  // ← 顯示彈窗
  }
}

const handleNext = async () => {
  if (!selectedDevice.value) return
  
  // If has colors but not opened modal yet
  if (selectedDevice.value.colors && selectedDevice.value.colors.length > 0 && !selectedColor.value) {
    showColorModal.value = true
    return
  }
  
  await confirmSelection()
}
```

**修改後**:
```typescript
const selectDeviceCard = (device: any) => {
  if (device.stock_status === 'out_of_stock') {
    return
  }
  
  selectedDevice.value = device
  
  // 自動設定顏色（後端每個設備只有單一顏色）
  if (device.colors && device.colors.length > 0) {
    selectedColor.value = device.colors[0]
  }
}

const handleNext = async () => {
  if (!selectedDevice.value) return
  await confirmSelection()  // ← 直接確認，不顯示彈窗
}

const confirmSelection = async () => {
  if (!selectedDevice.value) return
  
  try {
    // 使用設備的顏色，如果沒有則使用預設
    const color = selectedColor.value || 
                  (selectedDevice.value.colors && selectedDevice.value.colors[0]) || 
                  '預設'
    await selectDevice(selectedDevice.value.device_id, color)
    
    // Navigate to next step
    navigateTo('/renewal/list-plans')
  } catch (err) {
    console.error('Select device error:', err)
  }
}
```

## 📊 資料結構映射

### 後端 API 回應結構

```json
{
  "success": true,
  "store_id": "STORE001",
  "os_preference": "ios",
  "device_count": 3,
  "devices": [
    {
      "device_id": "IPHONE15PRO-256-BLACK",
      "brand": "Apple",
      "model": "iPhone 15 Pro",
      "storage": "256GB",
      "color": "黑色",
      "os": "ios",
      "price": 35900,
      "market_price": 39900,
      "total_quantity": 50,
      "reserved": 5,
      "available": 45,
      "in_stock": true,
      "screen_size": "6.1\"",
      "camera": "48MP",
      "chip": "A17 Pro"
    }
  ]
}
```

### 前端資料結構

```typescript
{
  device_id: "IPHONE15PRO-256-BLACK",
  brand: "Apple",
  model: "iPhone 15 Pro",
  os: "ios",
  processor: "A17 Pro",          // ← 從 chip 映射
  storage: "256GB",
  screen_size: "6.1\"",
  colors: ["黑色"],              // ← 從 color 包裝成陣列
  contract_price: 35900,         // ← 從 price 映射
  original_price: 39900,         // ← 從 market_price 映射
  stock_status: "in_stock",      // ← 根據 available 計算
  is_recommended: true,          // ← available > 10
  image_url: "/images/apple-iphone-15-pro.jpg",
  available: 45,
  total_quantity: 50
}
```

### 庫存狀態計算邏輯

```typescript
stock_status: device.available > 5 ? 'in_stock' :      // 有貨
              device.available > 0 ? 'low_stock' :      // 庫存不足
              'out_of_stock'                             // 缺貨
```

## 🧪 測試

### 測試檔案

**新增**: `backend/test_step7_api.py`
- 完整端到端測試
- 從登入到選擇設備
- 驗證 API 整合

### 測試步驟

1. 登入 (staff001)
2. 開始續約流程
3. 查詢客戶 (A123456789)
4. 列出門號
5. 選擇門號
6. 選擇裝置類型 (smartphone)
7. 選擇作業系統 (ios)
8. **查詢設備 (query-devices API)** ← 重點測試
9. 選擇設備

### 執行測試

```bash
cd backend
python test_step7_api.py
```

### 預期輸出

```
============================================================
測試 Step 7 - Query Devices API
============================================================

[Step 1] 登入...
✓ 登入成功

[Step 2] 開始續約流程...
✓ Session ID: renewal_xxx

[Step 3] 查詢客戶...
✓ 客戶: 王小明

[Step 4] 列出門號...
✓ 找到 2 個門號

[Step 5] 選擇門號...
✓ 門號: 0912345678

[Step 6a] 選擇裝置類型 (smartphone)...
✓ 裝置類型: smartphone
✓ 下一步: select_device_os

[Step 6b] 選擇作業系統 (ios)...
✓ 作業系統: ios
✓ 下一步: select_device

[Step 7] 查詢設備...
✓ 查詢成功
✓ 門市: STORE001
✓ 作業系統: ios
✓ 找到 3 個設備

設備列表:

  [1] Apple iPhone 15 Pro
      ID: IPHONE15PRO-256-BLACK
      顏色: 黑色
      儲存: 256GB
      價格: NT$ 35,900
      庫存: 45/50
      狀態: 有貨

  [2] Apple iPhone 15
      ID: IPHONE15-128-BLACK
      顏色: 黑色
      儲存: 128GB
      價格: NT$ 28,900
      庫存: 30/40
      狀態: 有貨

[Step 8] 選擇設備...
✓ 設備選擇成功
✓ 設備 ID: IPHONE15PRO-256-BLACK
✓ 顏色: 黑色
✓ 下一步: list_plans

============================================================
測試完成 - 成功 ✓
============================================================
```

## ✅ 驗證清單

- [x] 後端 API 從正確的 session 位置讀取 OS 類型
- [x] 前端移除假資料
- [x] 前端調用真實 API
- [x] 資料結構正確映射
- [x] 庫存狀態正確計算
- [x] 顏色邏輯簡化（自動選擇）
- [x] 錯誤處理完整
- [x] 建立端到端測試

## 🎯 後續工作

1. **圖片處理**: 根據實際設備動態生成或映射正確的產品圖片
2. **推薦邏輯**: 考慮使用 `get-recommendations` API 提供智能推薦
3. **價格篩選**: 前端可以使用 `min_price` 和 `max_price` 參數
4. **庫存即時更新**: 考慮加入定時刷新或 WebSocket 即時更新
5. **多顏色支援**: 如果未來需要支援同型號多顏色，需要調整 POS service 的資料結構

## 📝 注意事項

1. **顏色選擇彈窗保留**: UI 中的顏色選擇彈窗代碼保留但不顯示，未來如需支援多顏色可快速啟用
2. **庫存閾值**: 目前 `available > 5` 為有貨，`> 10` 為推薦，可根據業務需求調整
3. **門市 ID**: 目前硬編碼 `STORE001`，未來可從使用者 profile 或 session 取得
4. **圖片路徑**: 使用命名規則生成，需確保圖片檔案存在或提供預設圖片

## 🔄 資料流程

```
前端 (select-device.vue)
    ↓ onMounted()
    ↓ loadDevices()
    ↓ $fetch('/api/renewal-workflow/step/query-devices')
    ↓
後端 (renewal_workflow.py)
    ↓ query_devices()
    ↓ 從 session 讀取 customer_selection.device_os
    ↓ 調用 POS Service
    ↓
POS Service (pos_service.py)
    ↓ query_device_stock()
    ↓ 根據 os_filter 篩選
    ↓ 返回設備列表
    ↓
後端 API 回應
    ↓
前端接收並映射資料
    ↓ devices.value = response.devices.map(...)
    ↓
UI 顯示設備卡片
```
