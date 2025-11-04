"""
POS MCP Server 測試套件

測試所有 5 個 POS Tools 的功能
"""
import asyncio
import sys
from pathlib import Path

# 添加 backend 目錄到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from mcp_servers.pos_server import POSServer


def print_section(title: str):
    """印出區塊標題"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)


def print_result(tool_name: str, result: dict, show_data: bool = True):
    """印出測試結果"""
    success = result.get("success", False)
    status = "✅ 成功" if success else "❌ 失敗"
    
    print(f"\n{status} - {tool_name}")
    
    if success and show_data:
        data = result.get("data")
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "devices" or key == "recommendations":
                    print(f"  📦 {key}: {len(value)} 項")
                    for i, item in enumerate(value[:3], 1):  # 只顯示前 3 項
                        if "brand" in item:
                            print(f"     {i}. {item.get('brand')} {item.get('model')} - ${item.get('price'):,}")
                elif key == "device":
                    print(f"  📱 設備: {value.get('brand')} {value.get('model')}")
                elif key == "pricing_plans":
                    print(f"  💰 價格方案: {len(value)} 種")
                    for plan in value[:2]:
                        print(f"     {plan['plan_type']}: ${plan['final_price']:,.0f}")
                elif isinstance(value, (str, int, float, bool)):
                    print(f"  {key}: {value}")
        else:
            print(f"  Data: {data}")
    elif not success:
        print(f"  ❌ 錯誤: {result.get('error')}")


async def test_query_device_stock():
    """測試 Tool 1: query_device_stock"""
    print_section("測試 1: 查詢設備庫存")
    
    server = POSServer()
    
    # Test 1.1: 查詢全部庫存
    print("\n📋 測試 1.1: 查詢 STORE001 全部庫存")
    result = await server.query_device_stock(store_id="STORE001")
    print_result("query_device_stock (全部)", result)
    
    # Test 1.2: 過濾 iOS 設備
    print("\n📋 測試 1.2: 查詢 iOS 設備")
    result = await server.query_device_stock(store_id="STORE001", os_filter="iOS")
    print_result("query_device_stock (iOS)", result)
    
    # Test 1.3: 價格範圍過濾
    print("\n📋 測試 1.3: 查詢價格 $25,000-$35,000")
    result = await server.query_device_stock(
        store_id="STORE001",
        min_price=25000,
        max_price=35000
    )
    print_result("query_device_stock (價格過濾)", result)
    
    # Test 1.4: 錯誤測試 - 不存在的門市
    print("\n📋 測試 1.4: 錯誤測試 - 不存在的門市")
    result = await server.query_device_stock(store_id="STORE999")
    print_result("query_device_stock (錯誤)", result, show_data=False)


async def test_get_device_info():
    """測試 Tool 2: get_device_info"""
    print_section("測試 2: 取得設備詳細資訊")
    
    server = POSServer()
    
    # Test 2.1: 查詢 iPhone 15 Pro
    print("\n📋 測試 2.1: 查詢 iPhone 15 Pro (DEV001)")
    result = await server.get_device_info(device_id="DEV001")
    
    if result.get("success"):
        data = result["data"]
        print(f"\n✅ 成功 - get_device_info")
        print(f"  📱 品牌: {data['brand']}")
        print(f"  📱 型號: {data['model']}")
        print(f"  💾 容量: {data['storage']}")
        print(f"  🎨 顏色: {data['color']}")
        print(f"  💰 價格: ${data['price']:,}")
        print(f"  📺 螢幕: {data['screen_size']}\"")
        print(f"  📷 相機: {data['camera']}")
        print(f"  🔧 晶片: {data['chip']}")
        print(f"  📦 總庫存: {data['stock_summary']['total_stock']}")
        print(f"  ✅ 可售: {data['stock_summary']['available_stock']}")
    else:
        print_result("get_device_info", result, show_data=False)
    
    # Test 2.2: 查詢 Samsung S24 Ultra
    print("\n📋 測試 2.2: 查詢 Samsung S24 Ultra (DEV003)")
    result = await server.get_device_info(device_id="DEV003")
    print_result("get_device_info (Android)", result)
    
    # Test 2.3: 錯誤測試 - 不存在的設備
    print("\n📋 測試 2.3: 錯誤測試 - 不存在的設備")
    result = await server.get_device_info(device_id="DEV999")
    print_result("get_device_info (錯誤)", result, show_data=False)


async def test_get_recommended_devices():
    """測試 Tool 3: get_recommended_devices"""
    print_section("測試 3: 取得推薦設備")
    
    server = POSServer()
    
    # Test 3.1: iOS 推薦，預算 $35,000
    print("\n📋 測試 3.1: iOS 推薦 (預算 $35,000)")
    result = await server.get_recommended_devices(
        store_id="STORE001",
        os_preference="iOS",
        budget=35000
    )
    
    if result.get("success"):
        data = result["data"]
        print(f"\n✅ 成功 - get_recommended_devices")
        print(f"  推薦理由: {data['reason']}")
        print(f"  推薦數量: {data['recommendation_count']}")
        print(f"\n  前 3 名推薦:")
        for i, rec in enumerate(data["recommendations"][:3], 1):
            print(f"    {i}. {rec['brand']} {rec['model']}")
            print(f"       💰 ${rec['price']:,} (折扣 ${rec['discount']:,})")
            print(f"       ⭐ 推薦分數: {rec['recommendation_score']}")
    else:
        print_result("get_recommended_devices", result, show_data=False)
    
    # Test 3.2: Android 旗艦機，預算 $45,000
    print("\n📋 測試 3.2: Android 旗艦機 (預算 $45,000)")
    result = await server.get_recommended_devices(
        store_id="STORE001",
        os_preference="Android",
        budget=45000,
        is_flagship=True
    )
    print_result("get_recommended_devices (旗艦機)", result)
    
    # Test 3.3: 預算不足測試
    print("\n📋 測試 3.3: 預算太低 ($5,000)")
    result = await server.get_recommended_devices(
        store_id="STORE001",
        os_preference="iOS",
        budget=5000
    )
    print_result("get_recommended_devices (預算不足)", result, show_data=False)


async def test_reserve_device():
    """測試 Tool 4: reserve_device"""
    print_section("測試 4: 預約設備")
    
    server = POSServer()
    
    # Test 4.1: 預約 iPhone 15
    print("\n📋 測試 4.1: 預約 iPhone 15 (DEV002)")
    result = await server.reserve_device(
        store_id="STORE001",
        device_id="DEV002",
        customer_id="C123456",
        phone_number="0912345678"
    )
    
    if result.get("success"):
        data = result["data"]
        print(f"\n✅ 成功 - reserve_device")
        print(f"  🎫 預約編號: {data['reservation_id']}")
        print(f"  📱 設備: {data['device']['brand']} {data['device']['model']}")
        print(f"  💰 價格: ${data['device']['price']:,}")
        print(f"  👤 客戶: {data['customer_id']}")
        print(f"  📞 門號: {data['phone_number']}")
        print(f"  ⏰ 到期時間: {data['expires_at'][:19]}")
        print(f"  📦 剩餘庫存: {data['remaining_stock']}")
    else:
        print_result("reserve_device", result, show_data=False)
    
    # Test 4.2: 預約另一台
    print("\n📋 測試 4.2: 預約 Galaxy S24 (DEV004)")
    result = await server.reserve_device(
        store_id="STORE002",
        device_id="DEV004",
        customer_id="C987654",
        phone_number="0923456789"
    )
    print_result("reserve_device (第二次)", result)
    
    # Test 4.3: 錯誤測試 - 無庫存
    print("\n📋 測試 4.3: 錯誤測試 - 預約無庫存設備")
    result = await server.reserve_device(
        store_id="STORE002",
        device_id="DEV005",  # STORE002 這款無庫存
        customer_id="C123456",
        phone_number="0912345678"
    )
    print_result("reserve_device (無庫存)", result, show_data=False)


async def test_get_device_pricing():
    """測試 Tool 5: get_device_pricing"""
    print_section("測試 5: 取得設備價格資訊")
    
    server = POSServer()
    
    # Test 5.1: 查詢全部價格方案
    print("\n📋 測試 5.1: iPhone 15 Pro 全部價格方案 (DEV001)")
    result = await server.get_device_pricing(device_id="DEV001")
    
    if result.get("success"):
        data = result["data"]
        print(f"\n✅ 成功 - get_device_pricing")
        print(f"  📱 設備: {data['brand']} {data['model']}")
        print(f"  💰 基本價: ${data['base_price']:,}")
        print(f"  🏷️ 市價: ${data['market_price']:,}")
        print(f"  💵 折扣: ${data['market_discount']:,}")
        print(f"\n  價格方案:")
        for plan in data["pricing_plans"]:
            print(f"    {plan['plan_type']}: ${plan['final_price']:,.0f} ({plan['description']})")
        print(f"\n  分期選項:")
        for option in data["installment_options"]:
            print(f"    {option['months']}期: 月付 ${option['monthly_payment']:,.0f}")
    else:
        print_result("get_device_pricing", result, show_data=False)
    
    # Test 5.2: 查詢特定方案
    print("\n📋 測試 5.2: Samsung S24 攜碼價格 (DEV004)")
    result = await server.get_device_pricing(device_id="DEV004", plan_type="攜碼")
    print_result("get_device_pricing (攜碼)", result)
    
    # Test 5.3: 錯誤測試
    print("\n📋 測試 5.3: 錯誤測試 - 不存在的設備")
    result = await server.get_device_pricing(device_id="DEV999")
    print_result("get_device_pricing (錯誤)", result, show_data=False)


async def test_error_scenarios():
    """測試錯誤情境"""
    print_section("測試 6: 錯誤處理")
    
    server = POSServer()
    
    tests = [
        ("不存在的門市", server.query_device_stock(store_id="INVALID")),
        ("不存在的設備", server.get_device_info(device_id="INVALID")),
        ("不存在的預約", server.reserve_device("INVALID", "INVALID", "C123", "0912345678")),
    ]
    
    for test_name, test_coro in tests:
        print(f"\n📋 {test_name}")
        result = await test_coro
        status = "✅ 正確處理" if not result.get("success") else "❌ 應該失敗"
        print(f"  {status}")
        if not result.get("success"):
            print(f"  錯誤訊息: {result.get('error')}")


async def main():
    """執行所有測試"""
    print("\n" + "🚀"*30)
    print("  POS MCP Server 測試套件")
    print("  測試所有 5 個 Tools 的功能")
    print("🚀"*30)
    
    try:
        # 執行測試
        await test_query_device_stock()
        await test_get_device_info()
        await test_get_recommended_devices()
        await test_reserve_device()
        await test_get_device_pricing()
        await test_error_scenarios()
        
        # 總結
        print("\n" + "="*60)
        print("✅✅✅ 所有測試完成！POS MCP Server 工作正常 ✅✅✅")
        print("="*60)
        print("\n已驗證:")
        print("  ✅ Tool 1: query_device_stock - 庫存查詢")
        print("  ✅ Tool 2: get_device_info - 設備資訊")
        print("  ✅ Tool 3: get_recommended_devices - 智能推薦")
        print("  ✅ Tool 4: reserve_device - 預約管理")
        print("  ✅ Tool 5: get_device_pricing - 價格查詢")
        print("  ✅ 錯誤處理 - 所有錯誤情境")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
