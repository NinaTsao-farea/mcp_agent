"""
測試當 MCP CRM Server 未啟動時的行為
"""
import asyncio
import sys
import os

# 添加 backend 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_without_mcp_server():
    """測試沒有 MCP Server 時的行為"""
    
    print("=" * 60)
    print("測試：MCP Server 未啟動時的行為")
    print("=" * 60)
    
    # 檢查環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    use_mcp = os.getenv('USE_MCP_CRM', 'false')
    print(f"\n環境變數 USE_MCP_CRM: {use_mcp}")
    
    if use_mcp.lower() != 'true':
        print("✅ USE_MCP_CRM=false，會使用 Mock Service")
        return
    
    print("⚠️  USE_MCP_CRM=true，應該會嘗試連接 MCP Server")
    
    # 嘗試初始化 CRM Service
    print("\n嘗試初始化 CRM Service...")
    
    try:
        from app.services.crm_factory import get_crm_service
        crm_service = await get_crm_service()
        print(f"✅ CRM Service 初始化成功: {type(crm_service).__name__}")
        
        # 測試查詢客戶
        print("\n測試查詢客戶...")
        customer = await crm_service.query_customer_by_id("A123456789")
        if customer:
            print(f"✅ 查詢成功: {customer.get('name')}")
            print(f"   使用的服務類型: {type(crm_service).__name__}")
        
    except RuntimeError as e:
        print(f"❌ 連接失敗（預期行為）: {e}")
        print("\n說明：當 USE_MCP_CRM=true 但 MCP Server 未啟動時")
        print("      應該會拋出 RuntimeError")
    except Exception as e:
        print(f"❌ 未預期的錯誤: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_without_mcp_server())
