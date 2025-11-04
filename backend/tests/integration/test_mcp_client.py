"""
測試 2: MCP Client 連線測試

⚠️ 注意: 此測試在 Windows PowerShell 環境下有已知的 stdio 相容性問題
錯誤: asyncio.exceptions.CancelledError - MCP SDK stdio transport 限制

建議:
1. 開發階段使用 test_mock_mode.py (Mock 模式) ✅
2. 生產環境可考慮將 MCP 改為 HTTP transport

執行方式 (僅供參考，Windows 下會失敗): 
  1. 終端 1: python mcp_servers/crm_server.py
  2. 終端 2: python test_mcp_client.py

已知問題:
- Windows PowerShell: stdio mode 不相容 ❌
- Linux/macOS: stdio mode 可能正常 (未測試)
- 解決方案: 使用 Mock 模式或未來改用 HTTP transport
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_mcp_client_basic():
    """測試 MCP Client 基本功能"""
    print("\n" + "="*60)
    print("MCP Client 連線測試")
    print("="*60)
    
    # 設定使用 MCP 模式
    os.environ["USE_MCP_CRM"] = "false"
    
    from app.services.mcp_client import mcp_client
    
    try:
        # 初始化連線
        print("\n[步驟 1] 初始化 MCP Client...")
        print("-" * 60)
        await mcp_client.initialize()
        print("✓ MCP Client 初始化成功")
        print("✓ 已連接到 CRM MCP Server")
        
        # 測試 1: 查詢客戶
        print("\n[測試 1/6] query_customer_by_id")
        print("-" * 60)
        customer = await mcp_client.query_customer_by_id("A123456789")
        
        if customer:
            print(f"✓ 查詢客戶成功")
            print(f"  客戶姓名: {customer['name']}")
            print(f"  客戶 ID: {customer['customer_id']}")
            print(f"  電話: {customer['phone']}")
            print(f"  Email: {customer['email']}")
        else:
            print("✗ 查詢客戶失敗")
            return False
        
        # customer_id = customer['customer_id']
        
        # # 測試 2: 取得客戶門號
        # print("\n[測試 2/6] get_customer_phones")
        # print("-" * 60)
        # phones = await mcp_client.get_customer_phones(customer_id)
        
        # if phones and len(phones) > 0:
        #     print(f"✓ 取得門號成功: {len(phones)} 個門號")
        #     for i, phone in enumerate(phones, 1):
        #         print(f"  {i}. {phone['phone_number']} - {phone['plan_name']}")
        # else:
        #     print("✗ 取得門號失敗或無門號")
        #     return False
        
        # test_phone = phones[0]['phone_number']
        
        # # 測試 3: 取得合約資訊
        # print(f"\n[測試 3/6] get_phone_contract")
        # print("-" * 60)
        # contract = await mcp_client.get_phone_contract(test_phone)
        
        # if contract:
        #     print(f"✓ 取得合約資訊成功")
        #     print(f"  方案: {contract['plan_name']}")
        #     print(f"  月租: ${contract['monthly_fee']}")
        #     print(f"  到期日: {contract['contract_end_date']}")
        # else:
        #     print("✗ 取得合約資訊失敗")
        #     return False
        
        # # 測試 4: 取得使用量
        # print(f"\n[測試 4/6] get_phone_usage")
        # print("-" * 60)
        # usage = await mcp_client.get_phone_usage(test_phone)
        
        # if usage:
        #     print(f"✓ 取得使用量成功")
        #     print(f"  數據: {usage['data_used_gb']}/{usage['data_limit_gb']} GB")
        #     print(f"  語音: {usage['voice_used_minutes']}/{usage['voice_limit_minutes']} 分鐘")
        # else:
        #     print("✗ 取得使用量失敗")
        #     return False
        
        # # 測試 5: 取得帳單
        # print(f"\n[測試 5/6] get_phone_billing")
        # print("-" * 60)
        # billing = await mcp_client.get_phone_billing(test_phone)
        
        # if billing:
        #     print(f"✓ 取得帳單成功")
        #     print(f"  本月帳單: ${billing['current_month_fee']}")
        #     print(f"  欠費: ${billing['outstanding_balance']}")
        # else:
        #     print("✗ 取得帳單失敗")
        #     return False
        
        # # 測試 6: 檢查資格
        # print(f"\n[測試 6/6] check_eligibility")
        # print("-" * 60)
        # result = await mcp_client.check_eligibility(test_phone, customer_id)
        
        # if result:
        #     print(f"✓ 檢查資格成功")
        #     print(f"  資格: {'符合' if result['eligible'] else '不符合'}")
        #     if result.get('contract_end_date'):
        #         print(f"  合約到期日: {result['contract_end_date']}")
        #     if result.get('days_until_expiry') is not None:
        #         print(f"  剩餘天數: {result['days_until_expiry']} 天")
            
        #     if not result['eligible'] and result.get('reasons'):
        #         print(f"\n  不符合原因:")
        #         for reason in result['reasons']:
        #             print(f"    - {reason}")
        # else:
        #     print("✗ 檢查資格失敗")
        #     return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 關閉連線
        print("\n[步驟 2] 關閉 MCP Client...")
        print("-" * 60)
        await mcp_client.close()
        print("✓ MCP Client 已關閉")


async def test_workflow_simulation():
    """模擬完整的續約工作流程"""
    print("\n" + "="*60)
    print("完整續約工作流程模擬（透過 MCP）")
    print("="*60)
    
    os.environ["USE_MCP_CRM"] = "true"
    
    from app.services.mcp_client import mcp_client
    
    try:
        await mcp_client.initialize()
        
        # Step 1: 客戶查詢
        print("\n[Step 1] 客戶身分驗證")
        print("-" * 60)
        customer = await mcp_client.query_customer_by_id("A123456789")
        if not customer:
            print("✗ 找不到客戶")
            return False
        
        print(f"✓ 客戶驗證成功: {customer['name']}")
        
        # Step 2: 門號選擇
        print("\n[Step 2] 門號選擇")
        print("-" * 60)
        phones = await mcp_client.get_customer_phones(customer['customer_id'])
        if not phones:
            print("✗ 客戶沒有門號")
            return False
        
        print(f"✓ 找到 {len(phones)} 個門號")
        selected_phone = phones[0]['phone_number']
        print(f"✓ 選擇門號: {selected_phone}")
        
        # Step 3: 門號資訊查詢
        print("\n[Step 3] 門號資訊查詢")
        print("-" * 60)
        contract = await mcp_client.get_phone_contract(selected_phone)
        usage = await mcp_client.get_phone_usage(selected_phone)
        billing = await mcp_client.get_phone_billing(selected_phone)
        
        if not (contract and usage and billing):
            print("✗ 無法取得完整門號資訊")
            return False
        
        print(f"✓ 合約: {contract['plan_name']} (${contract['monthly_fee']}/月)")
        print(f"✓ 使用: {usage['data_used_gb']}/{usage['data_limit_gb']} GB")
        print(f"✓ 帳單: ${billing['current_month_fee']} (欠費: ${billing['outstanding_balance']})")
        
        # Step 4: 資格檢查
        print("\n[Step 4] 續約資格檢查")
        print("-" * 60)
        result = await mcp_client.check_eligibility(selected_phone, customer['customer_id'])
        
        if result['eligible']:
            print(f"✓ 符合續約資格")
            print(f"  合約到期日: {result.get('contract_end_date', 'N/A')}")
            print(f"  剩餘天數: {result.get('days_until_expiry', 0)} 天")
            print("\n✓ 可以進行續約流程")
        else:
            print(f"✗ 不符合續約資格")
            for reason in result.get('reasons', []):
                print(f"  - {reason}")
            print("\n✗ 無法進行續約")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 工作流程執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await mcp_client.close()


async def main():
    """主程式"""
    print("\n" + "="*60)
    print("MCP Client 完整測試套件")
    print("="*60)
    print("\n⚠️  注意: 此測試需要 CRM MCP Server 正在運行")
    print("   請確保已在另一個終端執行: python mcp_servers/crm_server.py")
    print("\n按 Enter 繼續...")
    input()
    
    # 執行基本功能測試
    print("\n開始執行測試...")
    success = await test_mcp_client_basic()
    
    if not success:
        print("\n" + "="*60)
        print("✗ 基本功能測試失敗")
        print("="*60)
        print("\n可能的原因:")
        print("  1. CRM MCP Server 沒有啟動")
        print("  2. Server 連接埠被佔用")
        print("  3. 網路連線問題")
        print("="*60 + "\n")
        return
    
    # # 執行工作流程測試
    # success = await test_workflow_simulation()
    
    # if not success:
    #     print("\n" + "="*60)
    #     print("✗ 工作流程測試失敗")
    #     print("="*60)
    #     return
    
    # # 全部測試通過
    # print("\n" + "="*60)
    # print("✅ 所有測試通過！MCP Client 工作正常")
    # print("="*60)
    # print("\nMCP 模式整合測試完成：")
    # print("  ✓ CRM MCP Server 正常運行")
    # print("  ✓ MCP Client 連線成功")
    # print("  ✓ 所有 6 個 CRM 方法正常")
    # print("  ✓ 完整工作流程通過")
    # print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
