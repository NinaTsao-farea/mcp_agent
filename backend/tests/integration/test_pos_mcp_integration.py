"""
測試 POS MCP Server 整合

測試前請確保：
1. 設置環境變數: USE_MCP_POS=true
2. 啟動 POS MCP Server: uvicorn pos_server_http:app --host 0.0.0.0 --port 8002
3. 啟動後端: python run_app.py
"""
import asyncio
import httpx
import os

# 設置環境變數（測試用）
os.environ['USE_MCP_POS'] = 'true'
os.environ['USE_HTTP_TRANSPORT'] = 'true'

from app.services.pos_factory import get_pos_service

async def test_pos_mcp_integration():
    """測試 POS MCP 整合"""
    
    print("\n" + "="*60)
    print("測試 POS MCP Server 整合")
    print("="*60)
    
    # 取得 POS Service（應該是 MCP Client）
    print("\n[Step 1] 取得 POS Service...")
    pos_service = await get_pos_service()
    print(f"✅ POS Service 類型: {type(pos_service).__name__}")
    
    # 測試 1: 查詢門市設備庫存
    print("\n[Step 2] 查詢門市設備庫存...")
    devices = await pos_service.query_device_stock(
        store_id="STORE001",
        os_filter="iOS"
    )
    print(f"✅ 查詢到 {len(devices)} 個 iOS 設備")
    if devices:
        print(f"   第一個設備: {devices[0]['brand']} {devices[0]['model']} - ${devices[0]['price']}")
    
    # 測試 2: 取得設備詳細資訊
    print("\n[Step 3] 取得設備詳細資訊...")
    if devices:
        device_id = devices[0]['device_id']
        device_info = await pos_service.get_device_info(device_id)
        if device_info:
            print(f"✅ 設備資訊: {device_info['brand']} {device_info['model']}")
            print(f"   儲存空間: {device_info['storage']}")
            print(f"   顏色: {device_info['color']}")
            print(f"   螢幕: {device_info.get('screen_size')}")
        else:
            print("❌ 取得設備資訊失敗")
    
    # 測試 3: 取得推薦設備
    print("\n[Step 4] 取得推薦設備...")
    result = await pos_service.get_recommended_devices(
        store_id="STORE001",
        os_preference="iOS",
        budget=40000,
        is_flagship=True
    )
    recommendations = result.get("recommendations", [])
    reason = result.get("reason", "")
    print(f"✅ 推薦 {len(recommendations)} 個設備")
    if reason:
        print(f"   推薦原因: {reason}")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. {rec['brand']} {rec['model']} ({rec['storage']}) - ${rec['price']}")
        print(f"      推薦分數: {rec.get('recommendation_score', 'N/A')}")
    
    # 測試 4: 預約設備
    print("\n[Step 5] 預約設備...")
    if devices:
        device_id = devices[0]['device_id']
        reserve_result = await pos_service.reserve_device(
            store_id="STORE001",
            device_id=device_id,
            customer_id="C123456",
            phone_number="0912345678"
        )
        if reserve_result:
            print(f"✅ 預約成功")
            print(f"   預約編號: {reserve_result.get('reservation_id')}")
            print(f"   剩餘庫存: {reserve_result.get('remaining_stock')}")
        else:
            print(f"❌ 預約失敗")
    
    # 測試 5: 取得設備價格資訊
    print("\n[Step 6] 取得設備價格資訊...")
    if devices:
        device_id = devices[0]['device_id']
        pricing = await pos_service.get_device_pricing(
            device_id=device_id,
            plan_type="續約"
        )
        if pricing:
            print(f"✅ 價格資訊:")
            print(f"   設備型號: {pricing.get('brand')} {pricing.get('model')}")
            print(f"   市場價: ${pricing.get('market_price')}")
            print(f"   基礎價: ${pricing.get('base_price')}")
            plans = pricing.get('pricing_plans', [])
            if plans:
                print(f"   續約價格: ${plans[0].get('final_price')} (折扣 {plans[0].get('discount_rate')}%)")
        else:
            print("❌ 取得價格資訊失敗")
    
    print("\n" + "="*60)
    print("✅ POS MCP Server 整合測試完成")
    print("="*60)


async def test_mock_vs_mcp_comparison():
    """比較 Mock Service 和 MCP Client 的結果一致性"""
    
    print("\n" + "="*60)
    print("Mock Service vs MCP Client 對比測試")
    print("="*60)
    
    # 測試 Mock Service
    print("\n[測試 Mock Service]")
    os.environ['USE_MCP_POS'] = 'false'
    from app.services.pos_service import MockPOSService
    mock_service = MockPOSService()
    
    mock_devices = await mock_service.query_device_stock(
        store_id="STORE001",
        os_filter="iOS"
    )
    print(f"Mock Service: 查詢到 {len(mock_devices)} 個 iOS 設備")
    
    # 測試 MCP Client
    print("\n[測試 MCP Client]")
    os.environ['USE_MCP_POS'] = 'true'
    from importlib import reload
    from app.services import pos_factory
    reload(pos_factory)
    
    mcp_service = await pos_factory.get_pos_service()
    mcp_devices = await mcp_service.query_device_stock(
        store_id="STORE001",
        os_filter="iOS"
    )
    print(f"MCP Client: 查詢到 {len(mcp_devices)} 個 iOS 設備")
    
    # 比較結果
    print("\n[比較結果]")
    if len(mock_devices) == len(mcp_devices):
        print(f"✅ 設備數量一致: {len(mock_devices)} 個")
    else:
        print(f"⚠️  設備數量不一致: Mock={len(mock_devices)}, MCP={len(mcp_devices)}")
    
    # 比較第一個設備的結構
    if mock_devices and mcp_devices:
        mock_keys = set(mock_devices[0].keys())
        mcp_keys = set(mcp_devices[0].keys())
        
        if mock_keys == mcp_keys:
            print(f"✅ 設備欄位結構一致")
        else:
            print(f"⚠️  設備欄位結構不一致:")
            if mock_keys - mcp_keys:
                print(f"   Mock 多出的欄位: {mock_keys - mcp_keys}")
            if mcp_keys - mock_keys:
                print(f"   MCP 多出的欄位: {mcp_keys - mock_keys}")
    
    print("\n" + "="*60)
    print("✅ 對比測試完成")
    print("="*60)


async def test_mcp_server_connection():
    """測試 MCP Server 連接"""
    
    print("\n" + "="*60)
    print("測試 POS MCP Server 連接")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 健康檢查
            print("\n[檢查] POS MCP Server 健康狀態...")
            response = await client.get("http://localhost:8002/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ POS MCP Server 運行正常")
                print(f"   狀態: {health.get('status')}")
                print(f"   模式: {health.get('mode')}")
                print(f"   設備數: {health.get('devices_count')}")
                print(f"   門市數: {health.get('stores_count')}")
                return True
            else:
                print(f"❌ POS MCP Server 返回錯誤: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無法連接 POS MCP Server: {e}")
            print("\n請確保已啟動 POS MCP Server:")
            print("   cd backend/mcp_servers")
            print("   python -m uvicorn pos_server_http:app --host 0.0.0.0 --port 8002")
            return False


if __name__ == "__main__":
    async def main():
        # 先檢查 MCP Server 是否運行
        is_running = await test_mcp_server_connection()
        
        if is_running:
            # 執行整合測試
            await test_pos_mcp_integration()
            
            # 執行對比測試
            await test_mock_vs_mcp_comparison()
        else:
            print("\n⚠️  跳過整合測試（MCP Server 未運行）")
    
    asyncio.run(main())
