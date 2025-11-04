# Structlog 日誌配置 - 快速指南

## 📍 當前配置

### Structlog 記錄到哪裡？

**預設配置**（`LOG_TO_FILE=true`）：
1. ✅ **檔案**：`backend/logs/app.log` （JSON 格式）
2. ✅ **控制台**：stdout （JSON 格式）

**開發模式**（`LOG_TO_FILE=false`）：
- ✅ **控制台**：stdout （彩色格式）

## ⚙️ 如何修改配置

### 方法 1：修改 .env 檔案（推薦）

```bash
# backend/.env

# 日誌等級：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 是否記錄到檔案
LOG_TO_FILE=true
```

### 方法 2：修改代碼

編輯 `backend/app/main.py` 中的 `setup_logging()` 函數：

```python
def setup_logging():
    """設定結構化日誌"""
    
    # 1. 修改日誌目錄
    log_dir = Path("logs")  # 改成你要的路徑
    
    # 2. 修改輪替策略
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "app.log",
        when="midnight",     # 改成 "H" (每小時), "D" (每天), "W0" (每週一)
        interval=1,          # 輪替間隔
        backupCount=30,      # 保留份數（改成你要的天數）
        encoding="utf-8"
    )
    
    # 3. 修改日誌格式
    # JSON 格式（生產環境）
    processors.append(structlog.processors.JSONRenderer())
    
    # 或彩色格式（開發環境）
    processors.append(structlog.dev.ConsoleRenderer())
```

## 📊 常用配置組合

### 開發環境

```bash
# .env
LOG_TO_FILE=false
LOG_LEVEL=DEBUG
```

**輸出**：控制台彩色格式，包含 DEBUG 信息

### 生產環境

```bash
# .env
LOG_TO_FILE=true
LOG_LEVEL=INFO
```

**輸出**：檔案 JSON 格式 + 控制台 JSON 格式

### 故障排查

```bash
# .env
LOG_TO_FILE=true
LOG_LEVEL=DEBUG
```

**輸出**：詳細的 DEBUG 日誌記錄到檔案

## 📁 日誌檔案位置

```
backend/
├── logs/
│   ├── app.log              ← 當前日誌
│   ├── app.log.2025-10-29   ← 昨天的日誌
│   ├── app.log.2025-10-28   ← 前天的日誌
│   └── ...                   (自動保留 30 天)
```

## 🔍 查看日誌

### Windows PowerShell

```powershell
# 實時查看日誌（類似 tail -f）
Get-Content logs\app.log -Wait -Tail 50

# 查看所有日誌
Get-Content logs\app.log

# 搜尋關鍵字
Select-String -Path logs\app.log -Pattern "錯誤"
```

### 格式化查看 JSON

```powershell
# 美化 JSON 輸出
python -c "import json; [print(json.dumps(json.loads(l), indent=2, ensure_ascii=False)) for l in open('logs/app.log', encoding='utf-8') if l.strip()]"
```

## 🧪 測試日誌配置

```bash
cd backend
python test_logging.py
```

**驗證項目**：
- ✅ 日誌可以輸出到控制台
- ✅ 日誌可以記錄到檔案
- ✅ JSON 格式正確
- ✅ 各等級日誌都能記錄

## 📖 完整文檔

詳細配置說明請參考：
- [`docs/logging-configuration.md`](./logging-configuration.md) - 完整日誌配置文檔

## 💡 常見問題

### Q: 如何只輸出到檔案，不輸出到控制台？

修改 `app/main.py`：

```python
# 移除控制台輸出
logging.basicConfig(
    handlers=[],  # 空的 handlers，不輸出到控制台
    level=getattr(logging, log_level),
)

# 只添加檔案 handler
if log_to_file:
    file_handler = logging.handlers.TimedRotatingFileHandler(...)
    logging.root.addHandler(file_handler)
```

### Q: 如何同時輸出到多個檔案？

```python
# 錯誤日誌單獨記錄
error_handler = logging.handlers.TimedRotatingFileHandler(
    filename=log_dir / "error.log",
    when="midnight",
    backupCount=90,  # 錯誤日誌保留更久
    encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
logging.root.addHandler(error_handler)

# 一般日誌
info_handler = logging.handlers.TimedRotatingFileHandler(
    filename=log_dir / "app.log",
    when="midnight",
    backupCount=30,
    encoding="utf-8"
)
info_handler.setLevel(logging.INFO)
logging.root.addHandler(info_handler)
```

### Q: 如何改變日誌格式？

在 `setup_logging()` 中修改 `processors`：

```python
# JSON 格式
processors.append(structlog.processors.JSONRenderer())

# KeyValue 格式
processors.append(structlog.processors.KeyValueRenderer())

# Logfmt 格式
processors.append(structlog.processors.LogfmtRenderer())

# 自訂格式
processors.append(structlog.dev.ConsoleRenderer(
    colors=True,           # 啟用彩色
    pad_event=30,          # 事件欄位寬度
    exception_formatter=... # 自訂異常格式
))
```

## 🎯 總結

當前配置已經滿足大多數需求：

✅ **靈活**：透過環境變數控制  
✅ **完整**：檔案 + 控制台雙重輸出  
✅ **結構化**：JSON 格式易於解析  
✅ **自動化**：每日輪替，自動清理  
✅ **可擴展**：易於整合 ELK、CloudWatch 等工具  

需要修改時，優先使用環境變數，避免改動代碼！
