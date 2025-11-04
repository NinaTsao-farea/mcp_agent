"""
Sprint 3 手動測試腳本
快速測試 Mock 和 MCP 模式
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_mock_mode():
    """測試 Mock 模式"""
    print("\n" + "="*60)
    print("測試 Mock 模式 (USE_MCP_CRM=false)")
    print("="*60)
    
    os.environ["USE_MCP_CRM"] = "false"
    
    from app.services.crm_factory import get_crm_service
    
    service = get_crm_service()
    print(f"\n✓ 服務類型: {service.__class__.__name__}")
    
    # 測試查詢客戶
    print("\n[1] 測試查詢客戶...")
    customer = await service.query_customer_by_id("A123456789")
    if customer:
        print(f"✓ 客戶: {customer['name']}")
        print(f"  ID: {customer['customer_id']}")
        print(f"  電話: {customer['phone']}")
        print(f"  Email: {customer['email']}")
    else:
        print("✗ 查詢失敗")
        return
    
    # 測試取得門號
    print("\n[2] 測試取得門號列表...")
    phones = await service.get_customer_phones(customer["customer_id"])
    print(f"✓ 找到 {len(phones)} 個門號:")
    for phone in phones:
        print(f"  - {phone['phone_number']} ({phone['plan_name']})")
    
    if not phones:
        print("✗ 無門號")
        return
    
    # 測試門號詳情
    phone_number = phones[0]["phone_number"]
    print(f"\n[3] 測試取得門號詳情: {phone_number}...")
    
    contract = await service.get_phone_contract(phone_number)
    print(f"✓ 合約資訊:")
    print(f"  方案: {contract['plan_name']}")
    print(f"  月租: ${contract['monthly_fee']}")
    print(f"  到期日: {contract['contract_end_date']}")
    
    usage = await service.get_phone_usage(phone_number)
    print(f"✓ 使用量:")
    # MockCRMService 使用不同的結構
    current = usage.get('current_month', {})
    data_used_mb = current.get('data_used', 0)
    data_limit_mb = current.get('data_limit', 0)
    print(f"  數據: {data_used_mb/1024:.1f}/{data_limit_mb/1024:.1f} GB")
    print(f"  語音: {current.get('voice_used', 0)}/{current.get('voice_limit', 0)} 分鐘")
    
    billing = await service.get_phone_billing(phone_number)
    print(f"✓ 帳單:")
    # MockCRMService 使用不同的結構
    current_bill = billing.get('current_bill', {})
    print(f"  本月帳單: ${current_bill.get('total', 0)}")
    print(f"  欠費: ${billing.get('total_outstanding', 0)}")
    
    # 測試資格檢查
    print(f"\n[4] 測試檢查續約資格...")
    result = await service.check_eligibility(phone_number, customer["customer_id"])
    
    if result["eligible"]:
        print(f"✓ 符合續約資格")
        print(f"  合約到期日: {result.get('contract_end_date', 'N/A')}")
        # MockCRMService 使用 days_to_expiry
        days = result.get('days_to_expiry') or result.get('days_until_expiry', 0)
        print(f"  剩餘天數: {days} 天")
    else:
        print(f"✗ 不符合續約資格")
        # MockCRMService 使用 reason 而非 reasons 陣列
        if 'reason' in result:
            print(f"  - {result['reason']}")
        elif 'reasons' in result:
            for reason in result.get("reasons", []):
                print(f"  - {reason}")
    
    print("\n✓ Mock 模式測試完成")


async def test_mcp_mode():
    """測試 MCP 模式"""
    print("\n" + "="*60)
    print("測試 MCP 模式 (USE_MCP_CRM=true)")
    print("="*60)
    
    os.environ["USE_MCP_CRM"] = "true"
    
    from app.services.mcp_client import mcp_client
    
    # 初始化
    print("\n正在初始化 MCP Client...")
    try:
        await mcp_client.initialize()
        print("✓ MCP Client 初始化成功")
    except Exception as e:
        print(f"✗ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        # 測試查詢客戶
        print("\n[1] 測試查詢客戶...")
        customer = await mcp_client.query_customer_by_id("A123456789")
        if customer:
            print(f"✓ 客戶: {customer['name']}")
            print(f"  ID: {customer['customer_id']}")
            print(f"  電話: {customer['phone']}")
            print(f"  Email: {customer['email']}")
        else:
            print("✗ 查詢失敗")
            return
        
        # 測試取得門號
        print("\n[2] 測試取得門號列表...")
        phones = await mcp_client.get_customer_phones(customer["customer_id"])
        print(f"✓ 找到 {len(phones)} 個門號:")
        for phone in phones:
            print(f"  - {phone['phone_number']} ({phone['plan_name']})")
        
        if not phones:
            print("✗ 無門號")
            return
        
        # 測試門號詳情
        phone_number = phones[0]["phone_number"]
        print(f"\n[3] 測試取得門號詳情: {phone_number}...")
        
        contract = await mcp_client.get_phone_contract(phone_number)
        print(f"✓ 合約資訊:")
        print(f"  方案: {contract['plan_name']}")
        print(f"  月租: ${contract['monthly_fee']}")
        print(f"  到期日: {contract['contract_end_date']}")
        
        usage = await mcp_client.get_phone_usage(phone_number)
        print(f"✓ 使用量:")
        # MCP Server 回傳的結構
        print(f"  數據: {usage.get('data_used_gb', 0)}/{usage.get('data_limit_gb', 0)} GB")
        print(f"  語音: {usage.get('voice_used_minutes', 0)}/{usage.get('voice_limit_minutes', 0)} 分鐘")
        
        billing = await mcp_client.get_phone_billing(phone_number)
        print(f"✓ 帳單:")
        # MCP Server 回傳的結構
        print(f"  本月帳單: ${billing.get('current_month_fee', 0)}")
        print(f"  欠費: ${billing.get('outstanding_balance', 0)}")
        
        # 測試資格檢查
        print(f"\n[4] 測試檢查續約資格...")
        result = await mcp_client.check_eligibility(phone_number, customer["customer_id"])
        
        if result["eligible"]:
            print(f"✓ 符合續約資格")
            print(f"  合約到期日: {result.get('contract_end_date', 'N/A')}")
            # MCP Client 統一使用 days_until_expiry
            days = result.get('days_until_expiry', 0)
            print(f"  剩餘天數: {days} 天")
        else:
            print(f"✗ 不符合續約資格")
            for reason in result.get("reasons", []):
                print(f"  - {reason}")
        
        print("\n✓ MCP 模式測試完成")
        
    except Exception as e:
        print(f"\n✗ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 關閉連線
        print("\n正在關閉 MCP Client...")
        await mcp_client.close()
        print("✓ MCP Client 已關閉")


async def main():
    """主程式"""
    print("\n" + "="*60)
    print("Sprint 3 整合測試")
    print("="*60)
    
    # 測試 Mock 模式
    await test_mock_mode()
    
    # 測試 MCP 模式
    await test_mcp_mode()
    
    print("\n" + "="*60)
    print("所有測試完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
