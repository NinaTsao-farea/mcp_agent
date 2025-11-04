"""
简单的 MCP Server 测试
"""
import asyncio
import sys
from pathlib import Path

# 添加 backend 到路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_crm_server_standalone():
    """测试 CRM Server 独立运行"""
    print("\n=== 测试 CRM Server 独立运行 ===\n")
    
    from mcp_servers.crm_server import CRMServer
    
    server = CRMServer()
    
    # 测试 get_customer
    print("[1] 测试 get_customer...")
    result = await server.get_customer("A123456789")
    print(f"结果: {result}\n")
    
    if result.get("success"):
        customer = result["data"]
        print(f"✓ 客户: {customer['name']}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    
    # 测试 list_customer_phones
    print("\n[2] 测试 list_customer_phones...")
    result = await server.list_customer_phones("CUST001")
    print(f"结果: {result}\n")
    
    if result.get("success"):
        phones = result["data"]
        print(f"✓ 找到 {len(phones)} 个门号")
        for phone in phones:
            print(f"  - {phone['phone_number']}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    
    # 测试 get_phone_details
    print("\n[3] 测试 get_phone_details...")
    result = await server.get_phone_details("0912345678")
    print(f"结果 keys: {result.keys() if isinstance(result, dict) else 'not dict'}\n")
    
    if result.get("success"):
        details = result["data"]
        print(f"✓ 合约: {details['contract_info']['plan_name']}")
        print(f"✓ 使用: {details['usage_info']['data_used_gb']} GB")
        print(f"✓ 账单: ${details['billing_info']['current_month_fee']}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    
    # 测试 check_renewal_eligibility
    print("\n[4] 测试 check_renewal_eligibility...")
    result = await server.check_renewal_eligibility("0912345678", "single")
    print(f"结果 keys: {result.keys() if isinstance(result, dict) else 'not dict'}\n")
    
    if result.get("success"):
        eligibility = result["data"]
        print(f"✓ 资格: {'符合' if eligibility['is_eligible'] else '不符合'}")
        if not eligibility['is_eligible']:
            for reason in eligibility.get('reasons', []):
                print(f"  - {reason}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    
    print("\n✓ CRM Server 独立测试完成")


async def test_mcp_client_connection():
    """测试 MCP Client 连接"""
    print("\n=== 测试 MCP Client 连接 ===\n")
    
    import os
    os.environ["USE_MCP_CRM"] = "true"
    
    from app.services.mcp_client import mcp_client
    
    try:
        print("初始化 MCP Client...")
        await mcp_client.initialize()
        print("✓ 初始化成功\n")
        
        # 测试调用
        print("[1] 测试查询客户...")
        customer = await mcp_client.query_customer_by_id("A123456789")
        if customer:
            print(f"✓ 客户: {customer['name']}")
        else:
            print("✗ 查询失败")
        
        print("\n✓ MCP Client 测试完成")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n关闭 MCP Client...")
        await mcp_client.close()
        print("✓ 已关闭")


async def main():
    """主程序"""
    # 先测试 Server 独立运行
    await test_crm_server_standalone()
    
    # 再测试通过 MCP Client 连接
    await test_mcp_client_connection()


if __name__ == "__main__":
    asyncio.run(main())
