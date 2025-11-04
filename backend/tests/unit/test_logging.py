"""
測試日誌配置

驗證：
1. 日誌可以輸出到控制台
2. 日誌可以記錄到檔案
3. JSON 格式正確
"""
import sys
import os
import json
from pathlib import Path

# 添加 backend 到路徑
sys.path.insert(0, str(Path(__file__).parent))

# 設定環境變數（測試用）
os.environ["LOG_TO_FILE"] = "true"
os.environ["LOG_LEVEL"] = "INFO"

# 導入並初始化日誌
from app.main import setup_logging, logger

print("=" * 80)
print("測試日誌配置")
print("=" * 80)

# 測試各種日誌等級
print("\n[1] 測試日誌等級...")
logger.debug("這是 DEBUG 日誌", test="debug")
logger.info("這是 INFO 日誌", test="info", number=123)
logger.warning("這是 WARNING 日誌", test="warning")
logger.error("這是 ERROR 日誌", test="error", error_code=500)
print("✓ 已記錄各等級日誌")

# 測試帶上下文的日誌
print("\n[2] 測試上下文日誌...")
log_with_context = logger.bind(session_id="sess_test_123", user_id="U001")
log_with_context.info("開始處理請求")
log_with_context.info("處理完成", duration=1.5, status="success")
print("✓ 已記錄上下文日誌")

# 測試異常日誌
print("\n[3] 測試異常日誌...")
try:
    raise ValueError("測試異常")
except Exception as e:
    logger.error(
        "捕獲異常",
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True
    )
print("✓ 已記錄異常日誌")

# 檢查日誌檔案
print("\n[4] 檢查日誌檔案...")
log_file = Path("logs/app.log")
if log_file.exists():
    print(f"✓ 日誌檔案已創建: {log_file}")
    print(f"  大小: {log_file.stat().st_size} bytes")
    
    # 讀取最後幾行
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"  行數: {len(lines)}")
    
    # 驗證 JSON 格式
    print("\n[5] 驗證 JSON 格式...")
    valid_json = 0
    for line in lines[-3:]:  # 檢查最後 3 行
        try:
            log_entry = json.loads(line)
            valid_json += 1
            print(f"✓ JSON 有效: {log_entry.get('event', '')[:50]}...")
        except json.JSONDecodeError:
            print(f"✗ JSON 無效: {line[:50]}...")
    
    print(f"\n  有效 JSON 行數: {valid_json}/{len(lines[-3:])}")
else:
    print("✗ 日誌檔案未創建")

print("\n" + "=" * 80)
print("✅ 測試完成！")
print("=" * 80)
print("\n📝 日誌檔案位置: logs/app.log")
print("💡 提示: 使用以下命令查看日誌：")
print("   - PowerShell: Get-Content logs\\app.log -Wait -Tail 50")
print("   - Bash: tail -f logs/app.log")
print("   - Python: python -c \"import json; [print(json.dumps(json.loads(l), indent=2, ensure_ascii=False)) for l in open('logs/app.log')]\"")
