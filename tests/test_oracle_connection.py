"""
測試新的 Oracle 連線方式
"""
import asyncio
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.database import DatabaseManager

async def test_oracle_connection():
    """測試 Oracle 連線"""
    print("=" * 60)
    print("測試新的 Oracle 連線方式")
    print("=" * 60)
    
    # 創建資料庫管理器
    db_manager = DatabaseManager()
    
    print("\n[1] 測試模擬模式（預設）...")
    await db_manager.initialize()
    
    # 測試查詢
    try:
        result = await db_manager.execute_query(
            "SELECT staff_id, staff_code, name FROM staff WHERE staff_code = :staff_code",
            {"staff_code": "S001"}
        )
        print(f"✅ 模擬查詢成功：{result}")
    except Exception as e:
        print(f"❌ 模擬查詢失敗：{e}")
    
    print("\n[2] 測試真實 Oracle 連線...")
    # 設置環境變數以使用真實資料庫
    os.environ['USE_REAL_ORACLE_DB'] = 'true'
    
    # 重新創建管理器
    db_manager_real = DatabaseManager()
    await db_manager_real.initialize(
        host="localhost",
        port=1521,
        service_name="XEPDB1",
        user="system",
        password="password"
    )
    
    if db_manager_real.dsn:
        print("✅ 真實 Oracle DSN 已建立")
        try:
            result = await db_manager_real.execute_query("SELECT 1 FROM DUAL")
            print(f"✅ 真實 Oracle 查詢成功：{result}")
        except Exception as e:
            print(f"❌ 真實 Oracle 查詢失敗：{e}")
    else:
        print("⚠️ 真實 Oracle 連線失敗，使用模擬模式")
    
    # 清理
    await db_manager.close()
    await db_manager_real.close()
    
    print("\n" + "=" * 60)
    print("連線測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_oracle_connection())