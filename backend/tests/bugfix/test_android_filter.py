"""
快速測試 Android 過濾是否正常工作
"""
import asyncio
import os

os.environ['USE_MCP_POS'] = 'true'
os.environ['USE_HTTP_TRANSPORT'] = 'true'

from app.services.pos_factory import get_pos_service


async def test_android_filter():
    """測試 Android 設備過濾"""
    
    print("\n測試 Android 設備過濾...")
    
    # 取得 POS Service
    pos_service = await get_pos_service()
    print(f"POS Service 類型: {type(pos_service).__name__}")
    
    # 測試小寫 "android"
    print("\n[測試 1] 查詢 android (小寫)...")
    devices = await pos_service.query_device_stock(
        store_id="STORE001",
        os_filter="android"
    )
    print(f"找到 {len(devices)} 個 Android 設備")
    for d in devices[:3]:
        print(f"  - {d['brand']} {d['model']} (OS: {d['os']})")
    
    # 測試大寫 "Android"
    print("\n[測試 2] 查詢 Android (大寫)...")
    devices = await pos_service.query_device_stock(
        store_id="STORE001",
        os_filter="Android"
    )
    print(f"找到 {len(devices)} 個 Android 設備")
    for d in devices[:3]:
        print(f"  - {d['brand']} {d['model']} (OS: {d['os']})")
    
    # 測試 iOS
    print("\n[測試 3] 查詢 iOS...")
    devices = await pos_service.query_device_stock(
        store_id="STORE001",
        os_filter="iOS"
    )
    print(f"找到 {len(devices)} 個 iOS 設備")
    for d in devices[:3]:
        print(f"  - {d['brand']} {d['model']} (OS: {d['os']})")
    
    print("\n✅ 測試完成")


if __name__ == "__main__":
    asyncio.run(test_android_filter())
