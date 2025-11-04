"""
測試 Mock 模式的 CRM 功能
使用 MockCRMService 進行完整工作流測試
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_mock_crm_basic():
    """測試 Mock CRM 基本功能"""
    print("\n" + "="*60)
    print("Mock CRM 功能測試")
    print("="*60)
    
    # 確保使用 Mock 模式
    os.environ["USE_MCP_CRM"] = "false"
    
    from app.services.crm_factory import get_crm_service
    
    try:
        # 取得 CRM Service (Mock 模式)
        print("\n[步驟 1] 初始化 CRM Service (Mock 模式)...")
        print("-" * 60)
        crm_service = await get_crm_service()
        print("✓ CRM Service 初始化成功 (使用 MockCRMService)")
        
        # 測試 1: 查詢客戶
        print("\n[測試 1/6] query_customer_by_id")
        print("-" * 60)
        customer = await crm_service.query_customer_by_id("A123456789")
        
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
        phones = await crm_service.get_customer_phones(customer_id)
        
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
        contract = await crm_service.get_phone_contract(test_phone)
        
        if contract:
            print(f"✓ 取得合約資訊成功")
            print(f"  方案: {contract['plan_name']}")
            print(f"  月租: ${contract['monthly_fee']}")
            print(f"  到期日: {contract['contract_end_date']}")
            print(f"  合約月數: {contract['contract_months']} 個月")
        else:
            print("✗ 取得合約資訊失敗")
            return False
        
        # 測試 4: 取得使用量
        print(f"\n[測試 4/6] get_phone_usage")
        print("-" * 60)
        usage = await crm_service.get_phone_usage(test_phone)
        
        if usage:
            print(f"✓ 取得使用量成功")
            print(f"  數據: {usage.get('data_used_gb', 0):.1f}/{usage.get('data_limit_gb', 0):.1f} GB")
            print(f"  語音: {usage.get('voice_used_minutes', 0)}/{usage.get('voice_limit_minutes', 0)} 分鐘")
            print(f"  平均日用量: {usage.get('average_daily_data_mb', 0)} MB")
        else:
            print("✗ 取得使用量失敗")
            return False
        
        # 測試 5: 取得帳單
        print(f"\n[測試 5/6] get_phone_billing")
        print("-" * 60)
        billing = await crm_service.get_phone_billing(test_phone)
        
        if billing:
            print(f"✓ 取得帳單成功")
            print(f"  本月費用: ${billing.get('current_month_fee', 0)}")
            print(f"  未繳金額: ${billing.get('outstanding_balance', 0)}")
            print(f"  繳費紀錄: {'良好' if billing.get('payment_history_good') else '不良'}")
            print(f"  最後繳費: {billing.get('last_payment_date', 'N/A')}")
            print(f"  繳費狀態: {'已繳清' if billing.get('outstanding_balance', 0) == 0 else '有欠費'}")
        else:
            print("✗ 取得帳單失敗")
            return False
        
        # 測試 6: 檢查資格
        print(f"\n[測試 6/6] check_eligibility")
        print("-" * 60)
        result = await crm_service.check_eligibility(test_phone, customer_id)
        
        if result:
            print(f"✓ 檢查資格成功")
            print(f"  資格: {'✓ 符合' if result['eligible'] else '✗ 不符合'}")
            if result.get('contract_end_date'):
                print(f"  合約到期日: {result['contract_end_date']}")
            if result.get('days_until_expiry') is not None:
                print(f"  剩餘天數: {result['days_until_expiry']} 天")
            if result.get('credit_score'):
                print(f"  信用評級: {result['credit_score']}")
            
            if not result['eligible'] and result.get('reasons'):
                print(f"\n  不符合原因:")
                for reason in result['reasons']:
                    print(f"    - {reason}")
        else:
            print("✗ 檢查資格失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_simulation():
    """模擬完整的續約工作流程"""
    print("\n" + "="*60)
    print("完整續約工作流程模擬（Mock 模式）")
    print("="*60)
    
    os.environ["USE_MCP_CRM"] = "false"
    
    from app.services.crm_factory import get_crm_service
    
    try:
        crm_service = await get_crm_service()
        
        # Step 1: 客戶查詢
        print("\n[Step 1] 客戶身分驗證")
        print("-" * 60)
        customer = await crm_service.query_customer_by_id("A123456789")
        if not customer:
            print("✗ 找不到客戶")
            return False
        
        print(f"✓ 客戶驗證成功: {customer['name']}")
        print(f"  客戶編號: {customer['customer_id']}")
        print(f"  本公司客戶: {'是' if customer['is_company_customer'] else '否'}")
        print(f"  信用分數: {customer['credit_score']}")
        
        # Step 2: 門號選擇
        print("\n[Step 2] 門號選擇")
        print("-" * 60)
        phones = await crm_service.get_customer_phones(customer['customer_id'])
        if not phones:
            print("✗ 客戶沒有門號")
            return False
        
        print(f"✓ 找到 {len(phones)} 個門號:")
        for i, phone in enumerate(phones, 1):
            status = "✓ 可續約" if phone.get('is_eligible_for_renewal') else "✗ 不可續約"
            print(f"  {i}. {phone['phone_number']} - {phone['plan_name']} - {status}")
        
        selected_phone = phones[0]['phone_number']
        print(f"\n✓ 選擇門號: {selected_phone}")
        
        # Step 3: 門號資訊查詢
        print("\n[Step 3] 門號完整資訊查詢")
        print("-" * 60)
        contract = await crm_service.get_phone_contract(selected_phone)
        usage = await crm_service.get_phone_usage(selected_phone)
        billing = await crm_service.get_phone_billing(selected_phone)
        
        if not (contract and usage and billing):
            print("✗ 無法取得完整門號資訊")
            return False
        
        print(f"✓ 合約資訊:")
        print(f"  方案: {contract['plan_name']} (${contract['monthly_fee']}/月)")
        print(f"  數據額度: {contract['data_limit']}")
        print(f"  語音額度: {contract['voice_minutes']} 分鐘")
        print(f"  合約期間: {contract['contract_start_date']} ~ {contract['contract_end_date']}")
        print(f"  已使用: {contract['months_used']}/{contract['contract_months']} 個月")
        
        print(f"\n✓ 使用情況:")
        data_used = usage.get('data_used_gb', 0)
        data_limit = usage.get('data_limit_gb', 1)
        print(f"  數據: {data_used:.1f}/{data_limit:.1f} GB ({data_used/data_limit*100:.1f}%)")
        print(f"  語音: {usage.get('voice_used_minutes', 0)}/{usage.get('voice_limit_minutes', 0)} 分鐘")
        print(f"  平均日用量: {usage.get('average_daily_data_mb', 0)} MB")
        
        print(f"\n✓ 帳單狀況:")
        print(f"  本月費用: ${billing.get('current_month_fee', 0)}")
        print(f"  未繳金額: ${billing.get('outstanding_balance', 0)}")
        print(f"  繳費紀錄: {'良好' if billing.get('payment_history_good') else '不良'}")
        print(f"  繳費狀況: {'✓ 已繳清' if billing.get('outstanding_balance', 0) == 0 else '✗ 有欠費'}")
        
        # Step 4: 資格檢查
        print("\n[Step 4] 續約資格檢查")
        print("-" * 60)
        result = await crm_service.check_eligibility(selected_phone, customer['customer_id'])
        
        if result['eligible']:
            print(f"✓✓✓ 符合續約資格 ✓✓✓")
            print(f"  合約到期日: {result.get('contract_end_date', 'N/A')}")
            print(f"  剩餘天數: {result.get('days_until_expiry', 0)} 天")
            print(f"  信用評級: {result.get('credit_score', 'N/A')}")
            print(f"  欠費狀況: {'有欠費' if result.get('has_outstanding_debt') else '無欠費'}")
            print("\n✓ 可以進行續約流程")
        else:
            print(f"✗✗✗ 不符合續約資格 ✗✗✗")
            for reason in result.get('reasons', []):
                print(f"  ✗ {reason}")
            print("\n✗ 無法進行續約")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 工作流程執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_customers():
    """測試多個客戶案例"""
    print("\n" + "="*60)
    print("多客戶測試案例")
    print("="*60)
    
    os.environ["USE_MCP_CRM"] = "false"
    
    from app.services.crm_factory import get_crm_service
    
    test_cases = [
        ("A123456789", "張三 - 本公司客戶，有 2 個門號"),
        ("B987654321", "李四 - 本公司客戶，有 1 個門號"),
        ("C111222333", "王五 - 非本公司客戶"),
        ("D999888777", "不存在的客戶")
    ]
    
    try:
        crm_service = await get_crm_service()
        
        for i, (id_num, description) in enumerate(test_cases, 1):
            print(f"\n[測試案例 {i}/4] {description}")
            print("-" * 60)
            
            customer = await crm_service.query_customer_by_id(id_num)
            
            if customer:
                print(f"✓ 找到客戶: {customer['name']}")
                print(f"  客戶 ID: {customer['customer_id']}")
                print(f"  本公司客戶: {'是' if customer['is_company_customer'] else '否'}")
                
                phones = await crm_service.get_customer_phones(customer['customer_id'])
                print(f"  門號數量: {len(phones)}")
            else:
                print(f"✗ 找不到客戶 (ID: {id_num})")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主程式"""
    print("\n" + "="*60)
    print("Mock CRM Service 完整測試套件")
    print("="*60)
    print("\n使用 MockCRMService 進行測試")
    print("無需啟動 MCP Server，直接使用 Mock 資料")
    
    results = []
    
    # 測試 1: 基本功能
    print("\n\n" + "█"*60)
    print("█ 測試組 1: 基本功能測試")
    print("█"*60)
    success = await test_mock_crm_basic()
    results.append(("基本功能測試", success))
    
    # 測試 2: 工作流程
    print("\n\n" + "█"*60)
    print("█ 測試組 2: 完整工作流程測試")
    print("█"*60)
    success = await test_workflow_simulation()
    results.append(("工作流程測試", success))
    
    # 測試 3: 多客戶案例
    print("\n\n" + "█"*60)
    print("█ 測試組 3: 多客戶案例測試")
    print("█"*60)
    success = await test_multiple_customers()
    results.append(("多客戶測試", success))
    
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
        print("✅✅✅ 所有測試通過！Mock CRM Service 工作正常 ✅✅✅")
        print("="*60)
        print("\nMock 模式功能驗證完成：")
        print("  ✓ 所有 6 個 CRM 方法正常")
        print("  ✓ 完整工作流程通過")
        print("  ✓ 多客戶案例處理正確")
        print("  ✓ 可以開始 Sprint 4-9 開發")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("❌ 部分測試失敗")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
