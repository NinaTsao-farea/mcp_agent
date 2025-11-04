"""
測試「單純續約」流程
驗證：
1. 選擇 device_type = "none" 可以正確跳到 list-plans
2. 後端正確設置 device 為空設備
3. 可以正常列出方案
"""
import asyncio
import httpx
import json
from test_config import BASE_URL, TEST_STAFF, TEST_CUSTOMER, API_TIMEOUT


def print_step(title: str):
    """打印步驟標題"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def print_result(data: dict):
    """打印結果"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


async def test_none_device_type():
    """測試單純續約流程"""
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        
        print_step("Step 0: 登入")
        login_resp = await client.post(
            f"{BASE_URL}/auth/login",
            json=TEST_STAFF
        )
        assert login_resp.status_code == 200
        session_id_auth = login_resp.json()['session_id']
        headers = {"X-Session-ID": session_id_auth}
        print("✅ 登入成功")
        
        print_step("Step 1-3: 完成到選擇門號")
        start_resp = await client.post(f"{BASE_URL}/renewal-workflow/start", headers=headers)
        session_id = start_resp.json()['session_id']
        
        await client.post(
            f"{BASE_URL}/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": session_id, "id_number": TEST_CUSTOMER["id_number"]}
        )
        
        await client.post(
            f"{BASE_URL}/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": session_id}
        )
        
        select_phone_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-phone",
            headers=headers,
            json={"session_id": session_id, "phone_number": TEST_CUSTOMER["phone"]}
        )
        assert select_phone_resp.status_code == 200
        print("✅ 已完成到 Step 3")
        
        print_step("Step 5: 選擇設備類型 = none (單純續約)")
        device_type_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device-type",
            headers=headers,
            json={"session_id": session_id, "device_type": "none"}
        )
        
        print(f"Status Code: {device_type_resp.status_code}")
        response_data = device_type_resp.json()
        print_result(response_data)
        
        if device_type_resp.status_code != 200:
            print("❌ 選擇設備類型失敗")
            return
        
        # 驗證返回的 next_step
        if response_data.get('next_step') != 'list_plans':
            print(f"❌ next_step 錯誤，應該是 'list_plans'，實際是 '{response_data.get('next_step')}'")
            return
        
        print("✅ next_step 正確指向 list_plans")
        
        # 驗證當前狀態
        print_step("驗證：檢查 Session 狀態")
        session_resp = await client.get(
            f"{BASE_URL}/renewal-workflow/session/{session_id}",
            headers=headers
        )
        print(f"Session API Status: {session_resp.status_code}")
        full_response = session_resp.json()
        print(f"完整響應: {json.dumps(full_response, indent=2, ensure_ascii=False)}")
        
        session_data = full_response.get('session', {})
        current_step = session_data.get('current_step')
        customer_selection = session_data.get('customer_selection', {})
        device = customer_selection.get('device')
        
        print(f"當前步驟: {current_step}")
        print(f"設備資料: {json.dumps(device, indent=2, ensure_ascii=False)}")
        
        if current_step != 'list_plans':
            print(f"❌ 當前步驟錯誤，應該是 'list_plans'，實際是 '{current_step}'")
            return
        
        if not device or device.get('device_id') != 'none':
            print(f"❌ 設備資料錯誤，device_id 應該是 'none'，實際是 '{device.get('device_id') if device else None}'")
            return
        
        print("✅ Session 狀態正確")
        
        print_step("Step 8: 列出方案")
        list_plans_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/list-plans",
            headers=headers,
            json={"session_id": session_id}
        )
        
        if list_plans_resp.status_code != 200:
            print(f"❌ 列出方案失敗: {list_plans_resp.status_code}")
            print_result(list_plans_resp.json())
            return
        
        plans_data = list_plans_resp.json()
        plans = plans_data.get('plans', [])
        
        print(f"✅ 成功列出 {len(plans)} 個方案")
        if plans:
            print(f"第一個方案: {plans[0].get('name')} - ${plans[0].get('monthly_fee')}")
        
        print("\n" + "=" * 60)
        print("✅ 單純續約流程測試通過！")
        print("=" * 60)
        print("\n驗證結果：")
        print("✅ 1. 選擇 device_type='none' 成功")
        print("✅ 2. next_step 正確返回 'list_plans'")
        print("✅ 3. Session 狀態正確轉換到 LIST_PLANS")
        print("✅ 4. device 正確設置為空設備")
        print("✅ 5. 可以正常列出方案")


if __name__ == "__main__":
    asyncio.run(test_none_device_type())
