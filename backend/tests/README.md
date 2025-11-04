# Backend 測試目錄結構

本目錄包含所有後端測試文件，已按測試類型分類整理。

## 📁 目錄結構

```
tests/
├── integration/          # 整合測試 (15 個測試)
│   ├── test_mcp_client.py
│   ├── test_mcp_connection.py
│   ├── test_mcp_crm_integration.py
│   ├── test_mcp_http.py
│   ├── test_mcp_server.py
│   ├── test_mcp_simple.py
│   ├── test_pos_http.py
│   ├── test_pos_integration.py
│   ├── test_pos_mcp_integration.py
│   ├── test_pos_server.py
│   ├── test_promotion_integration.py
│   ├── test_promotion_mcp_integration.py
│   ├── test_promotion_server.py
│   ├── test_promo_search.py
│   └── test_unified_services.py
│
├── e2e/                  # 端到端測試 (12 個測試)
│   ├── test_complete_workflow.py
│   ├── test_renewal_flow_complete.py
│   ├── test_renewal_flow_e2e.py
│   ├── test_restart_workflow.py
│   ├── test_restart_workflow_from_homepage.py
│   ├── test_step4_eligibility.py
│   ├── test_step5.py
│   ├── test_step6.py
│   ├── test_step7.py
│   ├── test_step7_api.py
│   ├── test_step8.py
│   └── test_step9.py
│
├── unit/                 # 單元測試 (3 個測試)
│   ├── test_config.py
│   ├── test_logging.py
│   └── test_mock_mode.py
│
├── api/                  # API 測試 (2 個測試)
│   ├── test_frontend_apis.py
│   └── test_sprint6_apis.py
│
├── bugfix/              # Bug 修復驗證測試 (4 個測試)
│   ├── test_android_filter.py
│   ├── test_backward_navigation.py
│   ├── test_backward_resubmit.py
│   └── test_none_device_type.py
│
├── conftest.py          # pytest 配置
├── test_auth.py         # 認證測試
└── test_mcp_integration.py  # MCP 整合測試
```

## 🧪 測試類型說明

### Integration Tests (整合測試)
測試多個組件之間的交互，確保不同服務能正確協作。

**主要測試**:
- `test_unified_services.py` - 驗證三個 Service 統一從 MCP Server 重用資料
- `test_mcp_*_integration.py` - 測試 MCP Client 與各 Server 的整合
- `test_pos_integration.py` - POS 服務整合測試
- `test_promotion_integration.py` - Promotion 服務整合測試

**執行方式**:
```bash
# 執行所有整合測試
pytest tests/integration/

# 執行特定測試
python tests/integration/test_unified_services.py
```

### E2E Tests (端到端測試)
測試完整的業務流程，模擬真實用戶操作。

**主要測試**:
- `test_complete_workflow.py` - 完整續約流程
- `test_renewal_flow_*.py` - 續約流程各階段測試
- `test_step*.py` - 各步驟詳細測試

**執行方式**:
```bash
# 執行所有端到端測試
pytest tests/e2e/

# 執行特定流程測試
python tests/e2e/test_complete_workflow.py
```

### Unit Tests (單元測試)
測試單一組件或功能的正確性。

**主要測試**:
- `test_config.py` - 配置管理
- `test_logging.py` - 日誌功能
- `test_mock_mode.py` - Mock 模式切換

**執行方式**:
```bash
# 執行所有單元測試
pytest tests/unit/
```

### API Tests (API 測試)
測試 REST API 端點的正確性。

**主要測試**:
- `test_frontend_apis.py` - 前端 API 介面
- `test_sprint6_apis.py` - Sprint 6 功能 API

**執行方式**:
```bash
# 執行所有 API 測試
pytest tests/api/
```

### Bug Fix Tests (Bug 修復驗證測試)
驗證已修復的 Bug 不再復現。

**主要測試**:
- `test_android_filter.py` - Android 設備過濾 Bug 修復驗證
- `test_backward_navigation.py` - 返回導航問題修復驗證
- `test_none_device_type.py` - 設備類型處理修復驗證

**執行方式**:
```bash
# 執行所有 Bug 修復測試
pytest tests/bugfix/
```

## 🚀 執行所有測試

```bash
# 執行所有測試
pytest tests/

# 執行測試並顯示詳細輸出
pytest tests/ -v

# 執行測試並顯示覆蓋率
pytest tests/ --cov=app
```

## 📝 測試命名規範

- `test_*.py` - 所有測試文件必須以 `test_` 開頭
- 測試函數必須以 `test_` 或 `async def test_` 開頭
- 測試類必須以 `Test` 開頭

## 🔧 添加新測試

根據測試類型將文件放入對應目錄：

1. **整合測試** → `tests/integration/`
2. **端到端測試** → `tests/e2e/`
3. **單元測試** → `tests/unit/`
4. **API 測試** → `tests/api/`
5. **Bug 修復測試** → `tests/bugfix/`

## 📊 測試統計

- **總測試數**: 36 個測試文件
- **整合測試**: 15 個
- **端到端測試**: 12 個
- **單元測試**: 3 個
- **API 測試**: 2 個
- **Bug 修復測試**: 4 個

## 🎯 測試優先級

1. **高優先級**: Bug 修復測試、單元測試
2. **中優先級**: 整合測試、API 測試
3. **低優先級**: 端到端測試（執行時間較長）

## 🔍 CI/CD 建議

```yaml
# 建議的測試執行順序
1. pytest tests/unit/           # 快速單元測試
2. pytest tests/bugfix/         # 驗證 Bug 修復
3. pytest tests/api/            # API 測試
4. pytest tests/integration/    # 整合測試
5. pytest tests/e2e/            # 端到端測試（可選）
```

---

**最後更新**: 2025-10-31  
**整理狀態**: ✅ 完成
