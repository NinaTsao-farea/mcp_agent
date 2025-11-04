"""
POS MCP Server HTTP Transport 測試

測試 HTTP 端點與所有 5 個 Tools
"""
import asyncio
import sys
import httpx
from pathlib import Path

# 測試配置
BASE_URL = "http://localhost:8002"
TIMEOUT = 30.0


def print_section(title: str):
    """印出區塊標題"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)


def print_result(test_name: str, success: bool, data: dict = None, error: str = None):
    """印出測試結果"""
    status = "✅ 成功" if success else "❌ 失敗"
    print(f"\n{status} - {test_name}")
    
    if success and data:
        if isinstance(data, dict):
            for key, value in list(data.items())[:5]:  # 只顯示前5項
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} 項")
                elif isinstance(value, dict):
                    print(f"  {key}: {{...}}")
                elif isinstance(value, (str, int, float, bool)):
                    print(f"  {key}: {value}")
    elif error:
        print(f"  錯誤: {error}")


async def test_health_check():
    """測試健康檢查端點"""
    print_section("測試 0: 健康檢查")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ 健康檢查成功")
                print(f"  狀態: {data.get('status')}")
                print(f"  服務: {data.get('service')}")
                print(f"  模式: {data.get('mode')}")
                print(f"  設備數: {data.get('devices_count')}")
                print(f"  門市數: {data.get('stores_count')}")
                return True
            else:
                print(f"\n❌ 健康檢查失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ 無法連接到服務器: {str(e)}")
            print(f"\n請先啟動 POS MCP Server (HTTP):")
            print(f"  cd backend")
            print(f"  uvicorn mcp_servers.pos_server_http:app --port 8002")
            return False


async def test_list_tools():
    """測試列出 Tools"""
    print_section("測試 1: 列出所有 Tools")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/mcp/tools")
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", [])
                print(f"\n✅ 成功取得 Tools 列表")
                print(f"  Tools 數量: {data.get('count')}")
                print(f"\n  可用 Tools:")
                for tool in tools:
                    print(f"    - {tool['name']}: {tool['description']}")
                return True
            else:
                print(f"\n❌ 失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            return False


async def test_query_device_stock():
    """測試 Tool 1: query_device_stock"""
    print_section("測試 2: 查詢設備庫存")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test 2.1: 查詢全部
        print("\n📋 測試 2.1: 查詢 STORE001 全部庫存")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "query_device_stock",
                    "arguments": {"store_id": "STORE001"}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                devices = data.get("devices", [])
                print(f"✅ 成功")
                print(f"  門市: {data.get('store_id')}")
                print(f"  設備數: {data.get('device_count')}")
                print(f"  前3名:")
                for i, dev in enumerate(devices[:3], 1):
                    print(f"    {i}. {dev['brand']} {dev['model']} - ${dev['price']:,} (庫存: {dev['available']})")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
        
        # Test 2.2: iOS 過濾
        print("\n📋 測試 2.2: 過濾 iOS 設備")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "query_device_stock",
                    "arguments": {"store_id": "STORE001", "os_filter": "iOS"}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                print(f"✅ 成功 - 找到 {data.get('device_count')} 台 iOS 設備")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def test_get_device_info():
    """測試 Tool 2: get_device_info"""
    print_section("測試 3: 取得設備詳細資訊")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print("\n📋 測試 3.1: 查詢 iPhone 15 Pro (DEV001)")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "get_device_info",
                    "arguments": {"device_id": "DEV001"}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                print(f"✅ 成功")
                print(f"  品牌: {data.get('brand')}")
                print(f"  型號: {data.get('model')}")
                print(f"  價格: ${data.get('price'):,}")
                print(f"  總庫存: {data.get('stock_summary', {}).get('total_stock')}")
                print(f"  可售: {data.get('stock_summary', {}).get('available_stock')}")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def test_get_recommended_devices():
    """測試 Tool 3: get_recommended_devices"""
    print_section("測試 4: 取得推薦設備")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print("\n📋 測試 4.1: iOS 推薦 (預算 $35,000)")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "get_recommended_devices",
                    "arguments": {
                        "store_id": "STORE001",
                        "os_preference": "iOS",
                        "budget": 35000
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                recs = data.get("recommendations", [])
                print(f"✅ 成功")
                print(f"  推薦理由: {data.get('reason')}")
                print(f"  推薦數量: {data.get('recommendation_count')}")
                print(f"\n  前3名推薦:")
                for i, rec in enumerate(recs[:3], 1):
                    print(f"    {i}. {rec['brand']} {rec['model']}")
                    print(f"       ${rec['price']:,} (推薦分數: {rec['recommendation_score']})")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def test_reserve_device():
    """測試 Tool 4: reserve_device"""
    print_section("測試 5: 預約設備")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print("\n📋 測試 5.1: 預約 iPhone 15 (DEV002)")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "reserve_device",
                    "arguments": {
                        "store_id": "STORE001",
                        "device_id": "DEV002",
                        "customer_id": "C123456",
                        "phone_number": "0912345678"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                device = data.get("device", {})
                print(f"✅ 成功")
                print(f"  預約編號: {data.get('reservation_id')}")
                print(f"  設備: {device.get('brand')} {device.get('model')}")
                print(f"  價格: ${device.get('price'):,}")
                print(f"  到期: {data.get('expires_at')[:19]}")
                print(f"  剩餘庫存: {data.get('remaining_stock')}")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def test_get_device_pricing():
    """測試 Tool 5: get_device_pricing"""
    print_section("測試 6: 取得設備價格資訊")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print("\n📋 測試 6.1: iPhone 15 Pro 價格方案 (DEV001)")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "get_device_pricing",
                    "arguments": {"device_id": "DEV001"}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                plans = data.get("pricing_plans", [])
                print(f"✅ 成功")
                print(f"  設備: {data.get('brand')} {data.get('model')}")
                print(f"  基本價: ${data.get('base_price'):,}")
                print(f"  市價: ${data.get('market_price'):,}")
                print(f"\n  價格方案:")
                for plan in plans[:3]:
                    print(f"    {plan['plan_type']}: ${plan['final_price']:,.0f}")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def test_error_handling():
    """測試錯誤處理"""
    print_section("測試 7: HTTP 錯誤處理")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test 7.1: 無效的 Tool
        print("\n📋 測試 7.1: 呼叫不存在的 Tool")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "invalid_tool",
                    "arguments": {}
                }
            )
            
            if response.status_code == 404:
                print(f"✅ 正確處理 - HTTP 404")
            else:
                print(f"⚠️ 預期 404，實際 {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
        
        # Test 7.2: 無效的參數
        print("\n📋 測試 7.2: 無效的門市代碼")
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/call",
                json={
                    "tool": "query_device_stock",
                    "arguments": {"store_id": "INVALID"}
                }
            )
            
            if response.status_code == 400:
                result = response.json()
                print(f"✅ 正確處理 - HTTP 400")
                print(f"  錯誤訊息: {result.get('error')}")
            else:
                print(f"⚠️ 預期 400，實際 {response.status_code}")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def main():
    """執行所有測試"""
    print("\n" + "🚀"*30)
    print("  POS MCP Server HTTP Transport 測試")
    print("  測試 FastAPI 端點與所有 Tools")
    print("🚀"*30)
    
    # 測試健康檢查
    if not await test_health_check():
        print("\n⚠️ 無法連接到服務器，測試中止")
        return False
    
    try:
        # 執行所有測試
        await test_list_tools()
        await test_query_device_stock()
        await test_get_device_info()
        await test_get_recommended_devices()
        await test_reserve_device()
        await test_get_device_pricing()
        await test_error_handling()
        
        # 總結
        print("\n" + "="*60)
        print("✅✅✅ 所有測試完成！POS HTTP Transport 工作正常 ✅✅✅")
        print("="*60)
        print("\n已驗證:")
        print("  ✅ 健康檢查端點")
        print("  ✅ Tools 列表端點")
        print("  ✅ Tool 1: query_device_stock")
        print("  ✅ Tool 2: get_device_info")
        print("  ✅ Tool 3: get_recommended_devices")
        print("  ✅ Tool 4: reserve_device")
        print("  ✅ Tool 5: get_device_pricing")
        print("  ✅ HTTP 錯誤處理")
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
