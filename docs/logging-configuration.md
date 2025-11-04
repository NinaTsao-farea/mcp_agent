# 日誌配置說明

## 當前配置

### Structlog 輸出位置

**默認配置**（`LOG_TO_FILE=true`）：
- ✅ **檔案輸出**：`logs/app.log`
- ✅ **控制台輸出**：同時輸出到 stdout

**開發模式**（`LOG_TO_FILE=false`）：
- ✅ **控制台輸出**：彩色格式，便於閱讀

### 日誌輪替策略

使用 Python 標準庫的 `TimedRotatingFileHandler`：

```python
logging.handlers.TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",      # 每天午夜輪替
    interval=1,           # 每 1 天
    backupCount=30,       # 保留 30 天
    encoding="utf-8"
)
```

**輪替規則**：
- 每天午夜自動創建新的日誌檔案
- 舊檔案重命名為：`app.log.2025-10-29`
- 自動刪除 30 天前的日誌

## 環境變數配置

在 `.env` 文件中設定：

```bash
# 日誌等級：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 是否記錄到檔案
LOG_TO_FILE=true
```

### LOG_LEVEL 說明

| 等級 | 說明 | 適用場景 |
|------|------|---------|
| **DEBUG** | 詳細的調試信息 | 開發階段排查問題 |
| **INFO** | 一般信息（默認） | 生產環境正常運行 |
| **WARNING** | 警告信息 | 需要注意但不影響運行 |
| **ERROR** | 錯誤信息 | 發生錯誤但系統可繼續 |
| **CRITICAL** | 嚴重錯誤 | 系統無法繼續運行 |

### LOG_TO_FILE 說明

| 值 | 輸出方式 | 格式 | 適用場景 |
|----|---------|------|---------|
| **true** | 控制台 + 檔案 | JSON（檔案）<br>彩色（控制台） | 生產環境<br>需要記錄追蹤 |
| **false** | 僅控制台 | 彩色輸出 | 開發環境<br>即時調試 |

## 日誌格式

### 檔案格式（JSON）

```json
{
  "event": "開始續約流程",
  "level": "info",
  "logger": "app.routes.renewal_workflow",
  "staff_id": "STAFF001",
  "session_id": "renewal_STAFF001_abc123",
  "timestamp": "2025-10-29T14:30:15.123456"
}
```

**優點**：
- 結構化，易於解析
- 可導入日誌分析工具（ELK, Splunk）
- 支持複雜查詢

### 控制台格式（彩色）

```
2025-10-29T14:30:15.123456 [info     ] 開始續約流程           staff_id=STAFF001 session_id=renewal_STAFF001_abc123
```

**優點**：
- 人類可讀
- 彩色高亮關鍵信息
- 適合開發調試

## 使用範例

### 基本日誌

```python
import structlog

logger = structlog.get_logger()

# INFO 等級
logger.info("用戶登入成功", user_id="U001", ip="192.168.1.1")

# WARNING 等級
logger.warning("API 響應緩慢", endpoint="/api/data", response_time=5.2)

# ERROR 等級
logger.error("資料庫連線失敗", error=str(e), retry_count=3)
```

### 帶上下文的日誌

```python
# 綁定上下文
log = logger.bind(session_id="sess_123", user_id="U001")

# 所有後續日誌都會包含這些上下文
log.info("開始處理請求")
log.info("處理完成", duration=1.5)
```

### 異常處理日誌

```python
try:
    # 業務邏輯
    result = await process_data()
except Exception as e:
    logger.error(
        "處理數據失敗",
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True  # 包含完整堆棧追蹤
    )
    raise
```

## 日誌檔案結構

```
backend/
├── logs/
│   ├── app.log                 # 當前日誌
│   ├── app.log.2025-10-29     # 昨天的日誌
│   ├── app.log.2025-10-28     # 前天的日誌
│   └── ...                     # 保留 30 天
├── app/
│   └── main.py                 # 日誌配置在這裡
└── .env                        # 環境變數
```

## 生產環境建議

### 1. 啟用檔案日誌

```bash
# .env
LOG_TO_FILE=true
LOG_LEVEL=INFO
```

### 2. 日誌輪替配置

如果需要更靈活的輪替策略，可以修改 `app/main.py`：

```python
# 按大小輪替（每 100MB）
file_handler = logging.handlers.RotatingFileHandler(
    filename=log_dir / "app.log",
    maxBytes=100 * 1024 * 1024,  # 100MB
    backupCount=10,
    encoding="utf-8"
)

# 或按時間輪替（每小時）
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=log_dir / "app.log",
    when="H",         # H=小時, D=天, W0=週一
    interval=1,
    backupCount=168,  # 保留 7 天（168 小時）
    encoding="utf-8"
)
```

### 3. 集成日誌分析工具

#### 選項 A：Filebeat + ELK Stack

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /path/to/logs/app.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
```

#### 選項 B：CloudWatch Logs（AWS）

```python
import watchtower

# 添加 CloudWatch handler
cw_handler = watchtower.CloudWatchLogHandler(
    log_group="renewal-workflow",
    stream_name="app-logs"
)
logging.root.addHandler(cw_handler)
```

#### 選項 C：Azure Monitor

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

# 添加 Azure Monitor handler
azure_handler = AzureLogHandler(
    connection_string="InstrumentationKey=xxx"
)
logging.root.addHandler(azure_handler)
```

## 開發環境建議

### 1. 僅控制台輸出

```bash
# .env
LOG_TO_FILE=false
LOG_LEVEL=DEBUG
```

### 2. 彩色輸出

默認已啟用，使用 `structlog.dev.ConsoleRenderer()`

### 3. 即時查看日誌

```bash
# Windows PowerShell
Get-Content logs\app.log -Wait -Tail 50

# 或使用 Python
python -m http.server --directory logs 8080
# 訪問 http://localhost:8080/app.log
```

## 日誌查詢示例

### 使用 jq 查詢 JSON 日誌

```bash
# 安裝 jq: https://stedolan.github.io/jq/

# 查詢所有錯誤
cat logs/app.log | jq 'select(.level=="error")'

# 查詢特定用戶的日誌
cat logs/app.log | jq 'select(.staff_id=="STAFF001")'

# 統計各等級日誌數量
cat logs/app.log | jq -r '.level' | sort | uniq -c

# 查詢最近 10 條錯誤
cat logs/app.log | jq 'select(.level=="error")' | tail -n 10
```

### 使用 Python 查詢

```python
import json

def search_logs(keyword, level=None):
    """搜索日誌"""
    with open("logs/app.log", "r", encoding="utf-8") as f:
        for line in f:
            try:
                log = json.loads(line)
                if level and log.get("level") != level:
                    continue
                if keyword in json.dumps(log):
                    print(json.dumps(log, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                continue

# 搜索所有包含 "錯誤" 的日誌
search_logs("錯誤")

# 搜索所有 ERROR 等級的日誌
search_logs("資料庫", level="error")
```

## 效能考慮

### 日誌效能影響

| 配置 | I/O 負擔 | 磁碟使用 | 效能影響 |
|------|---------|---------|---------|
| 僅控制台 | 低 | 無 | < 1% |
| 控制台 + 檔案 | 中等 | ~100MB/天 | < 2% |
| 多個 handlers | 高 | 依配置 | 2-5% |

### 優化建議

1. **使用適當的日誌等級**
   ```python
   # 生產環境：INFO
   # 開發環境：DEBUG
   LOG_LEVEL=INFO
   ```

2. **避免過度日誌**
   ```python
   # ❌ 不好：在循環中記錄
   for item in items:
       logger.debug("處理項目", item=item)
   
   # ✅ 好：記錄摘要
   logger.info("批次處理完成", count=len(items), duration=elapsed)
   ```

3. **使用異步日誌**（如需要高效能）
   ```python
   from logging.handlers import QueueHandler
   import queue
   
   log_queue = queue.Queue()
   queue_handler = QueueHandler(log_queue)
   logging.root.addHandler(queue_handler)
   ```

## 故障排查

### 問題 1：日誌檔案未創建

**原因**：`logs/` 目錄不存在或無寫入權限

**解決**：
```bash
# 創建目錄
mkdir logs

# 檢查權限（Linux/Mac）
chmod 755 logs
```

### 問題 2：日誌檔案不輪替

**原因**：應用程式未在午夜運行

**解決**：日誌會在下次應用程式運行且到達輪替時間時輪替

### 問題 3：日誌檔案過大

**原因**：日誌等級設為 DEBUG 且流量大

**解決**：
```bash
# 改為 INFO 等級
LOG_LEVEL=INFO

# 或減少保留天數
backupCount=7  # 僅保留 7 天
```

### 問題 4：無法查看彩色輸出

**原因**：Windows PowerShell 預設不支持 ANSI 色彩

**解決**：
```powershell
# Windows 10/11 啟用虛擬終端
$PSStyle.OutputRendering = 'ANSI'

# 或使用 Windows Terminal
# https://aka.ms/terminal
```

## 總結

當前配置：
- ✅ **預設記錄到檔案**：`logs/app.log`（JSON 格式）
- ✅ **預設輸出到控制台**：彩色格式（開發友好）
- ✅ **自動輪替**：每日午夜，保留 30 天
- ✅ **可配置**：透過環境變數 `LOG_LEVEL` 和 `LOG_TO_FILE`
- ✅ **結構化**：JSON 格式易於查詢和分析

建議：
- **開發環境**：`LOG_TO_FILE=false`, `LOG_LEVEL=DEBUG`
- **生產環境**：`LOG_TO_FILE=true`, `LOG_LEVEL=INFO`
