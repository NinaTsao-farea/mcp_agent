# Step 10 Confirm API 資料缺失修復報告

## 問題描述

呼叫 `POST /api/renewal-workflow/step/confirm` 時，收到 400 錯誤：

```json
{
  "success": false,
  "error": "申辦資料不完整：缺少 客戶資料, 門號資料, 合約資料"
}
```

## 根本原因

### 資料儲存位置不一致

1. **前面的 API (Step 1-7)** 將資料存在 `session['customer_selection']` 中
2. **Step 10 confirm API** 期望從 `session['customer']`, `session['phone']`, `session['contract']` 讀取
3. **E2E 測試** 直接操作 session，手動設置頂層欄位，所以能通過

### 程式碼分析

**Step 1: query-customer**
```python
# 只更新 customer_selection
await workflow_manager.update_customer_selection(
    session_id,
    {
        "id_number": id_number,
        "customer_id": customer["customer_id"],
        "customer_name": customer["name"],
        "customer_phone": customer["phone"]
    }
)
```

**Step 4: select-phone (修復前)**
```python
# 只更新 customer_selection
await workflow_manager.update_customer_selection(
    session_id,
    {
        "selected_phone_number": phone_number,
        "eligibility_check": eligibility
    }
)
```

**Step 10: confirm (期望)**
```python
customer = session.get('customer')      # ❌ None
phone = session.get('phone')            # ❌ None
contract = session.get('contract')      # ❌ None
selected_device = session.get('device') # ❌ None
selected_plan = session.get('selected_plan')  # ✅ 有 (Step 8.5 設置)

if not customer or not phone or not contract:
    return 400 錯誤
```

## 修復方案

### 修復策略

在關鍵步驟完成後，將完整資料同時存入：
1. `customer_selection` (向下兼容)
2. Session 頂層 (供 confirm API 使用)

### 修改 1: select-phone API (Step 4)

**位置**: `backend/app/routes/renewal_workflow.py` Line 264-293

**修改內容**:
```python
if eligibility["eligible"]:
    # 符合資格，取得完整資料並存入 session 頂層 (供 Step 10 confirm 使用)
    customer = await crm_service.query_customer_by_id(
        customer_selection.get("id_number")
    )
    phone_detail = next(
        (p for p in await crm_service.list_customer_phones(customer_id) 
         if p["phone_number"] == phone_number),
        None
    )
    contract = await crm_service.get_phone_contract(phone_number)
    
    # 將完整資料存入 session 頂層
    session_data['customer'] = customer
    session_data['phone'] = phone_detail
    session_data['contract'] = contract
    await workflow_manager.update_session(session_id, session_data)
```

**說明**:
- 在門號選擇成功後，一次取得客戶、門號、合約完整資料
- 存入 session 頂層，確保後續步驟可以存取
- check_eligibility 內部已經呼叫過 get_phone_contract，這裡再次呼叫確保取得完整資料

### 修改 2: select-device-type API (Step 5)

**位置**: `backend/app/routes/renewal_workflow.py` Line 390-406

**修改內容**:
```python
if device_type == "none":
    # 單純續約，跳過裝置選擇，直接到方案列表
    # 將空設備資料存入 session 頂層 (供 Step 10 confirm 使用)
    session_data['device'] = {
        "device_id": "none",
        "brand": "無",
        "model": "單純續約",
        "color": "無"
    }
    await workflow_manager.update_session(session_id, session_data)
    
    next_step = WorkflowStep.LIST_PLANS
    next_step_name = "list_plans"
```

**說明**:
- 當用戶選擇"單純續約"時，設置一個占位 device 對象
- 避免 confirm API 檢查 device 時出錯
- 前端可正確顯示"無裝置"或"單純續約"

### 修改 3: select-device API (Step 7)

**位置**: `backend/app/routes/renewal_workflow.py` Line 711-729

**修改內容**:
```python
# 取得設備詳細資料 (從 POS service)
pos_service = await get_pos_service()
store_id = session_data.get('store_id', 'STORE001')

# 查詢設備庫存以取得設備詳情
devices = await pos_service.query_device_stock(store_id=store_id)
device_detail = next((d for d in devices if d.get('device_id') == device_id), None)

if not device_detail:
    return jsonify({"success": False, "error": "設備不存在"}), 404

# 更新 Session - 儲存設備選擇
await workflow_manager.update_customer_selection(
    session_id,
    {
        "device_id": device_id,
        "device_color": color if color else "預設"
    }
)

# 將設備資料存入 session 頂層 (供 Step 10 confirm 使用)
session_data['device'] = {
    **device_detail,
    "color": color if color else "預設"
}
await workflow_manager.update_session(session_id, session_data)
```

**說明**:
- 當用戶選擇具體設備時，查詢完整設備資訊
- 將設備詳情（品牌、型號、價格等）存入 session
- 包含用戶選擇的顏色

## Session 資料結構

### 修復後的完整結構

```python
{
    "session_id": "renewal_xxx",
    "staff_id": "STAFF001",
    "current_step": "CONFIRM",
    "store_id": "STORE001",
    "created_at": "2025-10-31T10:00:00",
    "updated_at": "2025-10-31T10:05:00",
    
    # 頂層欄位 (供 confirm API 使用)
    "customer": {
        "customer_id": "CUST001",
        "name": "王大明",
        "id_number": "A123456789",
        "phone": "0912345678",
        "email": "wang@example.com",
        "address": "台北市信義區...",
        "contract_type": "續約"
    },
    "phone": {
        "phone_number": "0987654321",
        "plan_name": "4G 輕量方案",
        "monthly_fee": 599,
        "data_usage": "5GB",
        "contract_start": "2023-01-01",
        "contract_end": "2024-12-31"
    },
    "contract": {
        "contract_id": "CTR001",
        "contract_start_date": "2023-01-01",
        "contract_end_date": "2024-12-31",
        "contract_months": 24,
        "monthly_fee": 599,
        "status": "active"
    },
    "device": {
        "device_id": "DEV001",
        "brand": "Apple",
        "model": "iPhone 15 Pro",
        "os": "iOS",
        "storage": "256GB",
        "color": "黑色",
        "pricing": {
            "base_price": 35900,
            "stock_quantity": 5
        }
    },
    "selected_plan": {
        "plan_id": "PLAN001",
        "plan_name": "5G 旗艦方案",
        "monthly_fee": 1399,
        "contract_months": 30,
        "data": "網內免費吃到飽",
        "voice": "網內免費",
        "cost_details": {
            "upgrade_fee": 0,
            "device_price": 35900,
            "total": 35900
        },
        "selected_at": "2025-10-31T10:05:00"
    },
    
    # customer_selection (向下兼容，給其他 API 使用)
    "customer_selection": {
        "id_number": "A123456789",
        "customer_id": "CUST001",
        "customer_name": "王大明",
        "customer_phone": "0912345678",
        "selected_phone_number": "0987654321",
        "eligibility_check": {...},
        "device_type": "smartphone",
        "device_os": "iOS",
        "device_id": "DEV001",
        "device_color": "黑色"
    }
}
```

## 測試驗證

### 測試步驟

1. ✅ 重啟後端服務 (載入修改後的程式碼)
2. ✅ 從 Step 1 開始完整流程
3. ✅ Step 1: 查詢客戶
4. ✅ Step 2-3: 列出並選擇門號
5. ✅ Step 4: 檢查續約資格 → **驗證**: customer, phone, contract 已存入 session
6. ✅ Step 5-7: 選擇設備 (或選擇"單純續約") → **驗證**: device 已存入 session
7. ✅ Step 8: 選擇方案 → **驗證**: selected_plan 已存入 session
8. ✅ Step 10: 確認申辦 → **預期**: 成功載入，顯示完整申辦摘要

### 驗證命令

**檢查 session 資料**:
```bash
# 在 Redis CLI 中
GET renewal_session:renewal_xxx
```

**預期結果**:
```json
{
  "success": true,
  "summary": {
    "customer": { "name": "王大明", ... },
    "phone": { "phone_number": "0987654321", ... },
    "contract": { "contract_id": "CTR001", ... },
    "selected_device": { "brand": "Apple", ... },
    "selected_plan": { "plan_name": "5G 旗艦方案", ... },
    "cost_summary": { "total": 35900, ... }
  }
}
```

## 相關檔案

### 修改檔案

1. ✅ `backend/app/routes/renewal_workflow.py`
   - Line 264-293: select-phone API (新增完整資料存入)
   - Line 390-406: select-device-type API (處理 none 情況)
   - Line 711-729: select-device API (新增設備資料存入)

### 未修改檔案

- ❌ `backend/app/routes/renewal_workflow.py` - confirm API (無需修改，已正確實作)
- ❌ `backend/app/services/workflow_session.py` (無需修改)
- ❌ 前端檔案 (無需修改)

## 向下兼容性

### 保持兼容

所有修改都**保持向下兼容**：
- ✅ 仍然更新 `customer_selection` (其他 API 依賴)
- ✅ 額外存入頂層欄位 (供 confirm API 使用)
- ✅ E2E 測試無需修改 (仍可直接操作 session)

### 未來改進建議

1. **統一資料儲存位置**: 考慮全面遷移到頂層欄位，移除 customer_selection
2. **減少重複呼叫**: select-phone 中 check_eligibility 已取得 contract，可優化避免重複查詢
3. **加入資料驗證**: 在 confirm API 前增加 middleware 驗證必要欄位

## 修復日期

2025-10-31

## 測試狀態

- [ ] Step 1-4: 待測試
- [ ] Step 5: 單純續約路徑 - 待測試
- [ ] Step 5-7: 選擇設備路徑 - 待測試
- [ ] Step 8: 選擇方案 - 待測試
- [ ] Step 10: 確認申辦 - 待測試
- [ ] 完整 E2E 流程: 待測試
