# 測試文件與 Service 文件差異分析

## 1. 測試文件差異 (test_pos_mcp_integration.py vs test_promotion_mcp_integration.py)

### 結構相似性
兩個測試文件結構**高度一致**，都包含：
- MCP Server 連接測試
- 主要功能整合測試
- Mock vs MCP 對比測試

### 主要差異

#### A. 測試的服務類型
- **POS**: 設備管理服務（查詢庫存、推薦、預約、價格）
- **Promotion**: 促銷方案服務（搜尋、方案詳情、比較、費用計算）

#### B. 測試步驟數量
- **POS**: 6 個步驟
  1. 取得 POS Service
  2. 查詢門市設備庫存 (`query_device_stock`)
  3. 取得設備詳細資訊 (`get_device_info`)
  4. 取得推薦設備 (`get_recommended_devices`)
  5. 預約設備 (`reserve_device`)
  6. 取得設備價格資訊 (`get_device_pricing`)

- **Promotion**: 6 個步驟
  1. 取得 Promotion Service
  2. 搜尋促銷方案 (`search_promotions`)
  3. 取得方案詳細資訊 (`get_plan_details`)
  4. 比較方案 (`compare_plans`)
  5. 計算升級費用 (`calculate_upgrade_cost`)
  6. 搜尋攜碼專案（再次調用 `search_promotions`）

#### C. 方法參數差異

**POS Methods**:
```python
# 設備相關，需要門市 ID、OS、預算等
query_device_stock(store_id, os_filter)
get_recommended_devices(store_id, os_preference, budget, is_flagship)
reserve_device(store_id, device_id, customer_id, phone_number)
get_device_pricing(device_id, plan_type)
```

**Promotion Methods**:
```python
# 方案相關，需要查詢字串、方案 ID、費用計算等
search_promotions(query, contract_type, limit)
get_plan_details(plan_id)
compare_plans(plan_ids)
calculate_upgrade_cost(current_plan_fee, new_plan_id, device_price, contract_type)
```

#### D. 返回值結構差異

**POS** - 返回設備物件列表或字典:
```python
devices = [
    {
        "device_id": "DEV001",
        "brand": "Apple",
        "model": "iPhone 15 Pro",
        "price": 36900,
        "available": 5
    }
]
```

**Promotion** - 返回方案和促銷資訊:
```python
result = {
    "promotions": [...],
    "total": 3,
    "query": "5G"
}
```

#### E. Mock vs MCP 對比實作

**POS**: 
- 使用 `reload(pos_factory)` 重新載入 factory
- 比較設備數量和欄位結構
- 檢查欄位差異（screen_size, camera, chip）

**Promotion**:
- 直接重新獲取 service
- 使用 try-catch 捕捉 MCP Server 未啟動的情況
- 比較搜尋結果數量和方案名稱

---

## 2. Service 文件差異 (pos_service.py vs promotion_service.py)

### 結構相似性
兩個 Service 都是 **Mock Service**，提供與 MCP Server 相同的介面。

### 主要差異

#### A. 初始化方式

**POS Service**:
```python
def __init__(self):
    logger.info("初始化 Mock POS Service")
    self._init_mock_data()

def _init_mock_data(self):
    # 直接在類別內定義 Mock 資料
    self.mock_devices = {...}
    self.mock_stock = {...}
    self.mock_reservations = {}
```

**Promotion Service**:
```python
def __init__(self):
    # 從 PromotionServer 複製 Mock 資料
    base_server = BasePromotionServer()
    self.promotions = base_server.promotions
    self.plans = base_server.plans
    
    logger.info(
        "Mock Promotion Service 已初始化",
        promotions_count=len(self.promotions),
        plans_count=len(self.plans)
    )
```

**差異原因**: 
- POS Service 自己定義資料結構
- Promotion Service **重用** `promotion_server.py` 的資料，避免重複定義

#### B. 資料複雜度

**POS Service** - 8個設備，3個門市:
- 設備詳細規格（螢幕、相機、晶片、電池）
- 門市庫存管理（quantity, reserved）
- 預約記錄

**Promotion Service** - 6個促銷，7個方案:
- 促銷活動（keywords, benefits, eligibility）
- 方案詳情（月租、數據、語音、合約期）
- 關鍵字搜尋系統

#### C. 方法數量

**POS Service**: 5個方法
1. `query_device_stock()` - 查詢庫存
2. `get_device_info()` - 設備詳情
3. `get_recommended_devices()` - 推薦演算法
4. `reserve_device()` - 預約管理
5. `get_device_pricing()` - 價格計算

**Promotion Service**: 4個方法
1. `search_promotions()` - 搜尋演算法
2. `get_plan_details()` - 方案詳情
3. `compare_plans()` - 方案比較
4. `calculate_upgrade_cost()` - 費用計算

#### D. 核心演算法差異

**POS Service - 推薦演算法** (get_recommended_devices):
```python
# 複雜評分系統
score = device["popularity_score"]
price_ratio = device["price"] / budget
if price_ratio >= 0.8: score += 5
if device["is_flagship"]: score += 3
if months_old < 6: score += 5
if available >= 5: score += 2
```

**Promotion Service - 搜尋演算法** (search_promotions):
```python
# 關鍵字匹配系統
for keyword in promo["keywords"]:
    if keyword in query_lower:
        score += 10
if any(word in promo["title"] for word in query.split()):
    score += 5
if contract_type in promo_contract_types:
    score += 20
```

#### E. 返回格式統一性

**POS Service**:
- 大部分方法直接返回物件或 None
- `get_recommended_devices()` 返回 Dict (包含 recommendations 和 reason)

**Promotion Service**:
- 所有方法都返回 Dict
- 包含完整的錯誤處理（"error" 欄位）
- 更豐富的後設資料（total, query, relevance_score）

#### F. 過濾與篩選

**POS Service**:
```python
# OS 過濾（不區分大小寫）
if os_filter and device["os"].lower() != os_filter.lower():
    continue

# 價格過濾
if min_price and device["price"] < min_price:
    continue
```

**Promotion Service**:
```python
# 合約類型篩選
if contract_type:
    if contract_type in promo_contract_types:
        score += 20
    else:
        continue  # 不符合直接跳過
```

#### G. 日誌詳細程度

**POS Service**:
- 簡潔的 info 日誌
- Debug 日誌用於 OS 過濾

**Promotion Service**:
- 非常詳細的 debug 日誌
- 記錄搜尋過程（matched_keywords, relevance_score）
- 記錄合約類型不符的原因

---

## 3. 共同模式

### 兩組文件都遵循的設計模式

1. **介面一致性**: Mock Service 與 MCP Client 完全相同的介面
2. **工廠模式**: 通過 `get_xxx_service()` 動態選擇 Mock 或 MCP
3. **環境變數控制**: `USE_MCP_POS` / `USE_MCP_PROMOTION`
4. **異步支援**: 所有方法都是 `async`
5. **詳細日誌**: 使用 structlog 記錄操作
6. **錯誤處理**: Try-catch 包裝關鍵操作

### 測試結構一致性

1. **三層測試**:
   - Server 連接測試
   - 功能整合測試
   - Mock vs MCP 對比測試

2. **健康檢查**:
   - 先檢查 MCP Server 是否運行
   - 顯示 Server 狀態（設備數/促銷數）

3. **友善輸出**:
   - 使用 emoji 和格式化輸出
   - 清楚的測試步驟編號
   - 詳細的結果顯示

---

## 4. 改進建議

### 對 POS 測試的建議
✅ 已完成:
- 方法簽章統一（budget, plan_type）
- 欄位結構統一（screen_size, camera, chip）
- OS 大小寫不敏感

### 對 Promotion 測試的建議
✅ 已完成:
- 方法簽章統一（compare_plans, calculate_upgrade_cost）
- Mock vs MCP 對比測試

### 待優化項目
1. **統一錯誤處理格式**: 
   - POS 返回 None
   - Promotion 返回 {"error": "..."}
   - 建議統一為後者

2. **增加性能測試**:
   - 測量查詢響應時間
   - 比較 Mock vs MCP 性能差異

3. **增加邊界測試**:
   - 無效的 store_id / plan_id
   - 空的查詢字串
   - 超大的 limit 值

---

## 總結

| 比較項目 | POS | Promotion |
|---------|-----|-----------|
| **服務類型** | 設備管理 | 促銷方案 |
| **方法數量** | 5 個 | 4 個 |
| **核心功能** | 庫存、推薦、預約 | 搜尋、比較、計算 |
| **資料來源** | 自定義 Mock 資料 | 重用 Server Mock 資料 |
| **演算法複雜度** | 推薦評分系統 | 關鍵字匹配系統 |
| **錯誤處理** | 返回 None | 返回 Dict with error |
| **日誌詳細度** | 中等 | 詳細 |
| **測試覆蓋率** | 6 個測試步驟 | 6 個測試步驟 |
| **對比測試** | 欄位結構比較 | 結果數量比較 |

兩組文件在架構上**高度一致**，都正確實作了 Mock/MCP 雙模式支援，並通過完整的測試驗證了功能正確性。
