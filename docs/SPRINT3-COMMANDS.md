# Sprint 3 - 快速指令參考

## ✅ 推薦使用的測試指令

```bash
# 進入 backend 目錄
cd d:\ai_project\test_mcp_agent2\backend

# 執行 Mock 模式完整測試（推薦）
python test_mock_mode.py

# 執行 MCP Server 獨立測試
python test_mcp_server.py
```

## ❌ 不要執行的指令（Windows 會失敗）

```bash
# ❌ 不要執行 - Windows stdio 不相容
python test_mcp_client.py

# ❌ 不要手動啟動 Server 然後測試 Client
python mcp_servers/crm_server.py  # Server 會啟動但 Client 連不上
```

## 📋 環境配置

確保 `.env` 檔案配置正確：
```env
USE_MCP_CRM=false          # 使用 Mock 模式
MCP_CRM_API_URL=           # 留空
MCP_CRM_API_KEY=           # 留空
```

## 🎯 測試結果預期

### test_mock_mode.py
```
✅✅✅ 所有測試通過！Mock CRM Service 工作正常 ✅✅✅

Mock 模式功能驗證完成：
  ✓ 所有 6 個 CRM 方法正常
  ✓ 完整工作流程通過
  ✓ 多客戶案例處理正確
  ✓ 可以開始 Sprint 4-9 開發
```

### test_mcp_server.py
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
```

## 🚀 繼續開發

Sprint 3 已完成，可以開始 Sprint 4：
```bash
# 查看 Sprint 4 規格
cat spec.md | grep "Sprint 4"

# 開始實作 POS MCP Server
# 參考 backend/mcp_servers/crm_server.py
```

## 📚 相關文件

- `docs/sprint3-final-status.md` - 最終狀態總結
- `docs/sprint3-completion-report.md` - 完成報告
- `docs/mcp-stdio-windows-issue.md` - Windows stdio 問題詳解
- `docs/testing/sprint3-testing-guide.md` - 測試指南
