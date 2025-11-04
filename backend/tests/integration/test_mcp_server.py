"""
測試 1: CRM MCP Server 獨立運行測試
執行此測試以驗證 CRM Server 的所有 Tools 是否正常工作
"""
import asyncio
import sys
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_all_tools():
    """測試所有 CRM Server Tools"""
    print("\n" + "="*60)
    print("CRM MCP Server 獨立測試")
    print("="*60)
    
    from mcp_servers.crm_server import CRMServer
    
    server = CRMServer()
    print(f"\n✓ CRM Server 初始化成功\n")
    
    # 測試 1: get_customer
    print("[測試 1/5] get_customer")
    print("-" * 60)
    result = await server.get_customer("A123456789")
    
    if result.get("success"):
        customer = result["data"]
        print(f"✓ 查詢客戶成功")
        print(f"  客戶姓名: {customer['name']}")
        print(f"  客戶 ID: {customer['customer_id']}")
        print(f"  電話: {customer['phone']}")
        print(f"  Email: {customer['email']}")
    else:
        print(f"✗ 失敗: {result.get('error')}")
        return False
    
    customer_id = customer['customer_id']
    
    # 測試 2: list_customer_phones
    print(f"\n[測試 2/5] list_customer_phones")
    print("-" * 60)
    result = await server.list_customer_phones(customer_id)
    
    if result.get("success"):
        phones = result["data"]
        print(f"✓ 查詢門號成功: 找到 {len(phones)} 個門號")
        for i, phone in enumerate(phones, 1):
            print(f"  {i}. {phone['phone_number']} - {phone['plan_name']}")
    else:
        print(f"✗ 失敗: {result.get('error')}")
        return False
    
    # 選擇第一個門號進行後續測試
    if not phones:
        print("✗ 沒有門號可供測試")
        return False
    
    test_phone = phones[0]['phone_number']
    
    # 測試 3: get_phone_details
    print(f"\n[測試 3/5] get_phone_details")
    print("-" * 60)
    result = await server.get_phone_details(test_phone)
    
    if result.get("success"):
        details = result["data"]
        contract = details['contract_info']
        usage = details['usage_info']
        billing = details['billing_info']
        
        print(f"✓ 查詢門號詳情成功")
        print(f"\n  合約資訊:")
        print(f"    方案: {contract['plan_name']}")
        print(f"    月租: ${contract['monthly_fee']}")
        print(f"    到期日: {contract['contract_end_date']}")
        
        print(f"\n  使用量:")
        print(f"    數據: {usage['data_used_gb']}/{usage['data_limit_gb']} GB")
        print(f"    語音: {usage['voice_used_minutes']}/{usage['voice_limit_minutes']} 分鐘")
        
        print(f"\n  帳單:")
        print(f"    本月帳單: ${billing['current_month_fee']}")
        print(f"    欠費: ${billing['outstanding_balance']}")
    else:
        print(f"✗ 失敗: {result.get('error')}")
        return False
    
    # 測試 4: check_renewal_eligibility
    print(f"\n[測試 4/5] check_renewal_eligibility")
    print("-" * 60)
    result = await server.check_renewal_eligibility(test_phone, "single")
    
    if result.get("success"):
        eligibility = result["data"]
        print(f"✓ 檢查續約資格成功")
        print(f"  資格: {'符合' if eligibility['is_eligible'] else '不符合'}")
        print(f"  合約到期日: {eligibility['contract_end_date']}")
        print(f"  剩餘天數: {eligibility['days_until_expiry']} 天")
        
        if not eligibility['is_eligible']:
            print(f"\n  不符合原因:")
            for reason in eligibility.get('reasons', []):
                print(f"    - {reason}")
        else:
            print(f"\n  檢查項目:")
            for detail in eligibility.get('details', []):
                status_icon = "✓" if detail['status'] == 'pass' else "✗"
                print(f"    {status_icon} {detail['item']}: {detail['message']}")
    else:
        print(f"✗ 失敗: {result.get('error')}")
        return False
    
    # 測試 5: check_promotion_eligibility
    print(f"\n[測試 5/5] check_promotion_eligibility")
    print("-" * 60)
    result = await server.check_promotion_eligibility(test_phone, "PROMO001")
    
    if result.get("success"):
        promo = result["data"]
        print(f"✓ 檢查促銷資格成功")
        print(f"  促銷活動: {promo['promotion_name']}")
        print(f"  資格: {'符合' if promo['is_eligible'] else '不符合'}")
        print(f"  說明: {promo['description']}")
        
        if not promo['is_eligible']:
            print(f"\n  不符合原因:")
            for reason in promo.get('reasons', []):
                print(f"    - {reason}")
        
        print(f"\n  檢查項目:")
        for detail in promo.get('details', []):
            status_icon = "✓" if detail['status'] == 'pass' else "✗"
            print(f"    {status_icon} {detail['item']}: {detail['message']}")
    else:
        print(f"✗ 失敗: {result.get('error')}")
        return False
    
    return True


async def test_error_handling():
    """測試錯誤處理"""
    print("\n" + "="*60)
    print("錯誤處理測試")
    print("="*60)
    
    from mcp_servers.crm_server import CRMServer
    server = CRMServer()
    
    # 測試無效的身分證號碼
    print("\n[測試] 無效的身分證號碼")
    print("-" * 60)
    result = await server.get_customer("123")  # 太短
    if not result.get("success"):
        error_msg = result.get('error', {}).get('message', '未知錯誤')
        print(f"✓ 正確返回錯誤: {error_msg}")
    else:
        print(f"✗ 應該返回錯誤但卻成功了")
        return False
    
    # 測試不存在的客戶
    print("\n[測試] 不存在的客戶")
    print("-" * 60)
    result = await server.get_customer("Z999999999")
    if not result.get("success"):
        error_msg = result.get('error', {}).get('message', '未知錯誤')
        print(f"✓ 正確返回錯誤: {error_msg}")
    else:
        print(f"✗ 應該返回錯誤但卻成功了")
        return False
    
    # 測試不存在的門號
    print("\n[測試] 不存在的門號")
    print("-" * 60)
    result = await server.get_phone_details("0900000000")
    if not result.get("success"):
        error_msg = result.get('error', {}).get('message', '未知錯誤')
        print(f"✓ 正確返回錯誤: {error_msg}")
    else:
        print(f"✗ 應該返回錯誤但卻成功了")
        return False
    
    # 測試無效的促銷活動 ID
    print("\n[測試] 無效的促銷活動 ID")
    print("-" * 60)
    result = await server.check_promotion_eligibility("0912345678", "INVALID_PROMO")
    if not result.get("success"):
        error_msg = result.get('error', {}).get('message', '未知錯誤')
        print(f"✓ 正確返回錯誤: {error_msg}")
    else:
        print(f"✗ 應該返回錯誤但卻成功了")
        return False
    
    return True


async def main():
    """主程式"""
    print("\n" + "="*60)
    print("CRM MCP Server 完整測試套件")
    print("="*60)
    
    # 執行功能測試
    success = await test_all_tools()
    
    if not success:
        print("\n" + "="*60)
        print("✗ 功能測試失敗")
        print("="*60)
        return
    
    # 執行錯誤處理測試
    success = await test_error_handling()
    
    if not success:
        print("\n" + "="*60)
        print("✗ 錯誤處理測試失敗")
        print("="*60)
        return
    
    # 全部測試通過
    print("\n" + "="*60)
    print("✅ 所有測試通過！CRM MCP Server 工作正常")
    print("="*60)
    print("\n下一步：")
    print("  1. 啟動 CRM MCP Server: python mcp_servers/crm_server.py")
    print("  2. 在另一個終端執行: python test_mcp_client.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
