#!/usr/bin/env python3
"""
啟動腳本 - 啟動電信門市銷售助理系統後端
"""
import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 設置環境變數
os.environ.setdefault('QUART_ENV', 'development')
os.environ.setdefault('QUART_DEBUG', 'true')

if __name__ == '__main__':
    from app.main import create_app
    
    print("正在啟動電信門市銷售助理系統後端...")
    print("服務地址: http://localhost:8000")
    print("環境: development")
    print("按 Ctrl+C 停止服務器")
    
    # 創建應用實例
    app = create_app()
    
    # 使用 Hypercorn 啟動應用
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    
    config = Config()
    config.bind = ["localhost:8000"]
    config.debug = True
    config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
    config.access_logger = None  # 使用預設日誌
    
    try:
        asyncio.run(serve(app, config))
    except KeyboardInterrupt:
        print("\n服務器已停止")
    except Exception as e:
        print(f"啟動失敗: {e}")
        sys.exit(1)