# Sprint 3 測試快速參考

## 🎯 推薦測試方式

### ✅ 使用 Mock 模式測試（推薦）

```bash
# 進入 backend 目錄
cd backend

# 執行 Mock 模式完整測試
python test_mock_mode.py
```

**預期結果**：
```
✅✅✅ 所有測試通過！Mock CRM Service 工作正常 ✅✅✅

Mock 模式功能驗證完成：
  ✓ 所有 6 個 CRM 方法正常
  ✓ 完整工作流程通過
  ✓ 多客戶案例處理正確
  ✓ 可以開始 Sprint 4-9 開發
```

### ✅ 測試 MCP Server（獨立測試）

```bash
# 測試 CRM Server 的 5 個 Tools
python test_mcp_server.py
```

**預期結果**：
```
測試結果總結
============================================================
✓ ALL TESTS PASSED (所有測試通過)

Tool 測試結果:
  ✓ get_customer: 查詢到客戶 張三
  ✓ list_customer_phones: 找到 2 個門號
  ✓ get_phone_details: 完整門號資訊
  ✓ check_renewal_eligibility: 符合續約資格
  ✓ check_promotion_eligibility: 符合 5G 升級優惠

錯誤處理測試結果:
  ✓ 身分證格式錯誤: 正確返回錯誤
  ✓ 客戶不存在: 正確返回錯誤
  ✓ 門號不存在: 正確返回錯誤
  ✓ 促銷不存在: 正確返回錯誤
```

## ⚠️ 已知問題

### ❌ MCP Client 連線測試（Windows 不支援）

```bash
# ⚠️ 不要執行這個測試（會失敗）
python test_mcp_client.py
```

**錯誤**：
```
asyncio.exceptions.CancelledError: Cancelled by cancel scope [ID]
```

**原因**：
- Windows PowerShell 環境下 MCP SDK stdio 模式不相容
- 這是 MCP SDK 的已知限制，不是程式碼錯誤

**解決方案**：
- 使用 `test_mock_mode.py` 代替
- 參見 `docs/mcp-stdio-windows-issue.md` 詳細說明

## 📋 測試檔案說明

| 檔案 | 用途 | 狀態 | 執行時間 |
|------|------|------|---------|
| `test_mock_mode.py` | Mock 模式完整測試 | ✅ 推薦使用 | ~2 秒 |
| `test_mcp_server.py` | Server 獨立測試 | ✅ 推薦使用 | ~1 秒 |
| `test_mcp_client.py` | Client 連線測試 | ❌ Windows 不支援 | N/A |
| `test_sprint3.py` | 整合測試（Mock） | ✅ 可用 | ~3 秒 |

## 🚀 開發工作流

### 1. 日常開發測試

```bash
# 快速測試 CRM 功能
python test_mock_mode.py
```

### 2. Server 功能驗證

```bash
# 驗證 MCP Server 實作
python test_mcp_server.py
```

### 3. 整合測試

```bash
# 完整 Sprint 3 測試（Mock 模式）
python test_sprint3.py
```

## 📊 測試覆蓋率

### Mock CRM Service
- ✅ `query_customer_by_id()` - 3 個測試案例
- ✅ `get_customer_phones()` - 3 個測試案例
- ✅ `get_phone_contract()` - 3 個測試案例
- ✅ `get_phone_usage()` - 3 個測試案例
- ✅ `get_phone_billing()` - 3 個測試案例
- ✅ `check_eligibility()` - 2 個測試案例

### CRM MCP Server
- ✅ `get_customer` - 正常 + 錯誤處理
- ✅ `list_customer_phones` - 正常 + 錯誤處理
- ✅ `get_phone_details` - 正常 + 錯誤處理
- ✅ `check_renewal_eligibility` - 正常案例
- ✅ `check_promotion_eligibility` - 正常案例

### 工作流程
- ✅ 完整續約流程（4 步驟）
- ✅ 多客戶案例（4 種情況）

## 🔧 環境配置

### .env 設定（開發階段）

```env
# 使用 Mock 模式
USE_MCP_CRM=false

# CRM Server 配置（留空使用 Mock 資料）
MCP_CRM_API_URL=
MCP_CRM_API_KEY=
```

## 📚 相關文件

- `docs/sprint3-completion-report.md` - 完成報告
- `docs/mcp-stdio-windows-issue.md` - Windows stdio 問題分析
- `spec.md` - 專案規格
- `README.md` - 專案說明

## 💡 常見問題

### Q1: 為什麼不使用 MCP 模式？
**A**: Windows 環境下 MCP SDK stdio 模式有相容性問題。Mock 模式完全滿足開發需求。

### Q2: Mock 模式和 MCP 模式有什麼區別？
**A**: 
- Mock 模式：直接呼叫本地函數，速度快，適合開發
- MCP 模式：透過進程間通訊，適合生產環境的分散式部署

### Q3: 未來會解決 MCP 問題嗎？
**A**: 會，但優先級為 P2。生產環境建議改用 HTTP Transport，跨平台相容性更好。

### Q4: 可以開始 Sprint 4 了嗎？
**A**: 可以！Mock 模式完全支援後續開發，不受 MCP stdio 問題影響。

---

**更新日期**: 2025-10-29  
**狀態**: Sprint 3 完成 (95%) - Mock 模式完全可用
