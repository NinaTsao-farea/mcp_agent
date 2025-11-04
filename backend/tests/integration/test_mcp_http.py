"""
測試 MCP HTTP Transport

前提條件: CRM MCP Server (HTTP) 必須先啟動

執行方式:
  終端 1: uvicorn mcp_servers.crm_server_http:app --port 8001
  終端 2: python test_mcp_http.py
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_mcp_http_basic():
    """測試 MCP HTTP 基本功能"""
    print("\n" + "="*60)
    print("MCP HTTP Transport 測試")
    print("="*60)
    
    from app.services.mcp_client_http import MCPClientServiceHTTP
    
    try:
        # 初始化 HTTP Client
        print("\n[步驟 1] 初始化 MCP HTTP Client...")
        print("-" * 60)
        
        client = MCPClientServiceHTTP("http://localhost:8001")
        await client.initialize()
        
        print("✓ MCP HTTP Client 初始化成功")
        print("✓ 已連接到 CRM MCP Server (HTTP)")
        
        # 測試 1: 查詢客戶
        print("\n[測試 1/6] query_customer_by_id")
        print("-" * 60)
        customer = await client.query_customer_by_id("A123456789")
        
        if customer:
            print(f"✓ 查詢客戶成功")
            print(f"  客戶姓名: {customer['name']}")
            print(f"  客戶 ID: {customer['customer_id']}")
            print(f"  電話: {customer['phone']}")
            print(f"  Email: {customer['email']}")
        else:
            print("✗ 查詢客戶失敗")
            return False
        
        customer_id = customer['customer_id']
        
        # 測試 2: 取得客戶門號
        print("\n[測試 2/6] get_customer_phones")
        print("-" * 60)
        phones = await client.get_customer_phones(customer_id)
        
        if phones and len(phones) > 0:
            print(f"✓ 取得門號成功: {len(phones)} 個門號")
            for i, phone in enumerate(phones, 1):
                print(f"  {i}. {phone['phone_number']} - {phone['plan_name']}")
        else:
            print("✗ 取得門號失敗或無門號")
            return False
        
        test_phone = phones[0]['phone_number']
        
        # 測試 3: 取得合約資訊
        print(f"\n[測試 3/6] get_phone_contract")
        print("-" * 60)
        contract = await client.get_phone_contract(test_phone)
        
        if contract:
            print(f"✓ 取得合約資訊成功")
            print(f"  方案: {contract['plan_name']}")
            print(f"  月租: ${contract['monthly_fee']}")
            print(f"  到期日: {contract['contract_end_date']}")
        else:
            print("✗ 取得合約資訊失敗")
            return False
        
        # 測試 4: 取得使用量
        print(f"\n[測試 4/6] get_phone_usage")
        print("-" * 60)
        usage = await client.get_phone_usage(test_phone)
        
        if usage:
            print(f"✓ 取得使用量成功")
            print(f"  數據: {usage['data_used_gb']:.1f}/{usage['data_limit_gb']:.1f} GB")
            print(f"  語音: {usage['voice_used_minutes']}/{usage['voice_limit_minutes']} 分鐘")
        else:
            print("✗ 取得使用量失敗")
            return False
        
        # 測試 5: 取得帳單
        print(f"\n[測試 5/6] get_phone_billing")
        print("-" * 60)
        billing = await client.get_phone_billing(test_phone)
        
        if billing:
            print(f"✓ 取得帳單成功")
            print(f"  本月帳單: ${billing['current_month_fee']}")
            print(f"  欠費: ${billing['outstanding_balance']}")
        else:
            print("✗ 取得帳單失敗")
            return False
        
        # 測試 6: 檢查資格
        print(f"\n[測試 6/6] check_eligibility")
        print("-" * 60)
        result = await client.check_eligibility(test_phone, customer_id)
        
        if result:
            print(f"✓ 檢查資格成功")
            print(f"  資格: {'✓ 符合' if result['eligible'] else '✗ 不符合'}")
            if result.get('contract_end_date'):
                print(f"  合約到期日: {result['contract_end_date']}")
            if result.get('days_until_expiry') is not None:
                print(f"  剩餘天數: {result['days_until_expiry']} 天")
            
            if not result['eligible'] and result.get('reasons'):
                print(f"\n  不符合原因:")
                for reason in result['reasons']:
                    print(f"    - {reason}")
        else:
            print("✗ 檢查資格失敗")
            return False
        
        # 關閉連線
        print("\n[步驟 2] 關閉 MCP HTTP Client...")
        print("-" * 60)
        await client.close()
        print("✓ MCP HTTP Client 已關閉")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_server_endpoints():
    """測試 HTTP Server 端點"""
    print("\n" + "="*60)
    print("HTTP Server 端點測試")
    print("="*60)
    
    import httpx
    
    try:
        async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
            # 測試健康檢查
            print("\n[測試 1/3] Health Check")
            print("-" * 60)
            response = await client.get("/health")
            health = response.json()
            print(f"✓ Server 狀態: {health['status']}")
            print(f"  模式: {health['mode']}")
            
            # 測試列出 Tools
            print("\n[測試 2/3] List Tools")
            print("-" * 60)
            response = await client.get("/mcp/tools")
            tools = response.json()
            print(f"✓ 找到 {len(tools)} 個 Tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            # 測試直接調用 Tool
            print("\n[測試 3/3] Direct Tool Call")
            print("-" * 60)
            response = await client.post(
                "/mcp/call",
                json={
                    "tool": "get_customer",
                    "arguments": {"id_number": "A123456789"}
                }
            )
            result = response.json()
            
            if result.get("success"):
                customer = result.get("data")
                print(f"✓ Tool 調用成功")
                print(f"  客戶: {customer['name']}")
            else:
                print(f"✗ Tool 調用失敗: {result.get('error')}")
                return False
            
            return True
            
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主程式"""
    print("\n" + "="*60)
    print("MCP HTTP Transport 完整測試套件")
    print("="*60)
    print("\n⚠️  注意: 此測試需要 CRM MCP Server (HTTP) 正在運行")
    print("   請確保已在另一個終端執行:")
    print("   uvicorn mcp_servers.crm_server_http:app --port 8001")
    print("\n按 Enter 繼續...")
    input()
    
    results = []
    
    # 測試 1: Server 端點
    print("\n\n" + "█"*60)
    print("█ 測試組 1: HTTP Server 端點")
    print("█"*60)
    success = await test_http_server_endpoints()
    results.append(("Server 端點測試", success))
    
    # 測試 2: Client 基本功能
    print("\n\n" + "█"*60)
    print("█ 測試組 2: HTTP Client 基本功能")
    print("█"*60)
    success = await test_mcp_http_basic()
    results.append(("Client 基本功能", success))
    
    # 總結
    print("\n\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("✅✅✅ 所有測試通過！MCP HTTP Transport 工作正常 ✅✅✅")
        print("="*60)
        print("\nHTTP 模式優勢：")
        print("  ✓ 跨平台相容 (Windows/Linux/macOS)")
        print("  ✓ 易於除錯和監控")
        print("  ✓ 支援負載平衡")
        print("  ✓ 標準 HTTP/REST API")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("❌ 部分測試失敗")
        print("="*60)
        print("\n可能的原因:")
        print("  1. Server 沒有啟動")
        print("  2. Port 8001 被佔用")
        print("  3. 網路連線問題")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
