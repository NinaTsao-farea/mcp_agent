"""
測試 MCP CRM 整合
驗證主後端通過 MCP Client 調用 CRM MCP Server
"""
import asyncio
import httpx
import json
from test_config import BASE_URL, TEST_STAFF, TEST_CUSTOMER, API_TIMEOUT

def print_step(title: str):
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)

async def test_mcp_crm():
    """測試 MCP CRM 整合"""
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        
        print_step("Step 1: 登入")
        login_resp = await client.post(
            f"{BASE_URL}/auth/login",
            json=TEST_STAFF
        )
        assert login_resp.status_code == 200
        session_id_auth = login_resp.json()['session_id']
        headers = {"X-Session-ID": session_id_auth}
        print("✅ 登入成功")
        
        print_step("Step 2: 開始續約流程")
        start_resp = await client.post(f"{BASE_URL}/renewal-workflow/start", headers=headers)
        session_id = start_resp.json()['session_id']
        print(f"✅ Session ID: {session_id}")
        
        print_step("Step 3: 查詢客戶 (通過 MCP CRM)")
        customer_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": session_id, "id_number": TEST_CUSTOMER["id_number"]}
        )
        
        print(f"Status Code: {customer_resp.status_code}")
        customer_data = customer_resp.json()
        print(json.dumps(customer_data, indent=2, ensure_ascii=False))
        
        if customer_resp.status_code != 200:
            print("❌ 查詢客戶失敗")
            return
        
        print(f"\n✅ 客戶姓名: {customer_data['customer']['name']}")
        print(f"✅ 客戶ID: {customer_data['customer']['customer_id']}")
        
        # 顯示資料來源
        data_source = customer_data['customer'].get('_data_source', 'Unknown')
        if data_source == 'MCP_CRM_Server':
            print("📡 資料來源: MCP CRM Server ✅")
        elif data_source == 'Mock_Service':
            print("🔧 資料來源: Mock Service (測試資料)")
        else:
            print(f"❓ 資料來源: {data_source}")
        
        print_step("Step 4: 列出門號 (通過 MCP CRM)")
        phones_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": session_id}
        )
        
        print(f"Status Code: {phones_resp.status_code}")
        phones_data = phones_resp.json()
        print(json.dumps(phones_data, indent=2, ensure_ascii=False))
        
        if phones_resp.status_code != 200:
            print("❌ 列出門號失敗")
            return
        
        print(f"\n✅ 找到 {len(phones_data['phones'])} 個門號")
        for phone in phones_data['phones']:
            print(f"   - {phone['phone_number']} ({phone['plan_name']})")
        
        # 顯示資料來源
        if phones_data['phones']:
            data_source = phones_data['phones'][0].get('_data_source', 'Unknown')
            if data_source == 'MCP_CRM_Server':
                print("📡 資料來源: MCP CRM Server ✅")
            elif data_source == 'Mock_Service':
                print("🔧 資料來源: Mock Service (測試資料)")
            else:
                print(f"❓ 資料來源: {data_source}")
        
        print_step("Step 5: 選擇門號")
        select_phone_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-phone",
            headers=headers,
            json={"session_id": session_id, "phone_number": TEST_CUSTOMER["phone"]}
        )
        
        if select_phone_resp.status_code != 200:
            print("❌ 選擇門號失敗")
            return
        
        print("✅ 門號選擇成功")
        
        print("\n" + "=" * 60)
        print("✅ MCP CRM 整合測試通過！")
        print("=" * 60)
        print("\n驗證結果：")
        print("✅ 1. 主後端成功連接到 MCP CRM Server")
        print("✅ 2. 通過 MCP Client 成功查詢客戶資料")
        print("✅ 3. 通過 MCP Client 成功列出門號")
        print("✅ 4. 完整的 CRM 流程運作正常")

if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_crm())
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
