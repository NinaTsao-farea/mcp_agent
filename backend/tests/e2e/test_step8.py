"""
Step 8 測試 - 列出方案

測試 POST /api/renewal-workflow/step/list-plans
"""
import sys
import asyncio
import httpx
from pathlib import Path

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

async def test_step8():
    """測試完整 Step 8 流程"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "=" * 60)
        print("Step 8 測試：列出方案")
        print("=" * 60)
        
        # Step 0: 登入
        print("\n[Step 0] 登入...")
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "staff_code": "S001",
                "password": "password"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登入失敗: {login_response.status_code}")
            print(login_response.text)
            return
        
        login_data = login_response.json()
        session_id = login_data["session_id"]
        print(f"✅ 登入成功")
        print(f"   Session ID: {session_id}")
        
        # 設置認證 header
        headers = {"X-Session-ID": session_id}
        
        # Step 1: 開始續約流程
        print("\n[Step 1] 開始續約流程...")
        start_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        
        if start_response.status_code != 200:
            print(f"❌ 開始流程失敗: {start_response.status_code}")
            return
        
        start_data = start_response.json()
        renewal_session_id = start_data["session_id"]
        print(f"✅ 流程已開始")
        print(f"   Renewal Session ID: {renewal_session_id}")
        
        # Step 2: 查詢客戶
        print("\n[Step 2] 查詢客戶...")
        customer_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "id_number": "A123456789"
            }
        )
        
        if customer_response.status_code != 200:
            print(f"❌ 查詢客戶失敗: {customer_response.status_code}")
            return
        
        customer_data = customer_response.json()
        print(f"✅ 客戶查詢成功")
        print(f"   客戶: {customer_data['customer']['name']}")
        
        # Step 3: 列出門號
        print("\n[Step 3] 列出門號...")
        phones_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": renewal_session_id}
        )
        
        if phones_response.status_code != 200:
            print(f"❌ 列出門號失敗: {phones_response.status_code}")
            return
        
        phones_data = phones_response.json()
        phone_number = phones_data["phones"][0]["phone_number"]
        print(f"✅ 門號列表取得成功")
        print(f"   門號數量: {len(phones_data['phones'])}")
        print(f"   選擇門號: {phone_number}")
        
        # Step 4: 選擇門號並檢查資格
        print("\n[Step 4] 選擇門號並檢查資格...")
        select_phone_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "phone_number": phone_number
            }
        )
        
        if select_phone_response.status_code != 200:
            print(f"❌ 選擇門號失敗: {select_phone_response.status_code}")
            return
        
        select_phone_data = select_phone_response.json()
        print(f"✅ 門號選擇成功")
        print(f"   資格檢查: {'通過' if select_phone_data.get('eligibility', {}).get('eligible') else '不通過'}")
        
        # Step 5: 選擇裝置類型
        print("\n[Step 5] 選擇裝置類型...")
        device_type_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "device_type": "smartphone"
            }
        )
        
        if device_type_response.status_code != 200:
            print(f"❌ 選擇裝置類型失敗: {device_type_response.status_code}")
            return
        
        print(f"✅ 裝置類型選擇成功: smartphone")
        
        # Step 6: 選擇作業系統
        print("\n[Step 6] 選擇作業系統...")
        os_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "os_type": "android"
            }
        )
        
        if os_response.status_code != 200:
            print(f"❌ 選擇作業系統失敗: {os_response.status_code}")
            return
        
        print(f"✅ 作業系統選擇成功: Android")
        
        # Step 7: 查詢設備
        print("\n[Step 7] 查詢設備...")
        devices_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-devices",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "store_id": "STORE001"
            }
        )
        
        if devices_response.status_code != 200:
            print(f"❌ 查詢設備失敗: {devices_response.status_code}")
            return
        
        devices_data = devices_response.json()
        device_id = devices_data["devices"][0]["device_id"]
        print(f"✅ 設備查詢成功")
        print(f"   設備數量: {devices_data['device_count']}")
        print(f"   選擇設備: {device_id}")
        
        # Step 7-1: 選擇設備
        print("\n[Step 7-1] 選擇設備...")
        select_device_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "device_id": device_id,
                "color": "黑色"
            }
        )
        
        if select_device_response.status_code != 200:
            print(f"❌ 選擇設備失敗: {select_device_response.status_code}")
            return
        
        print(f"✅ 設備選擇成功")
        
        # Step 8: 列出方案 ⭐ 重點測試
        print("\n[Step 8] ⭐ 列出方案...")
        plans_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-plans",
            headers=headers,
            json={"session_id": renewal_session_id}
        )
        
        print(f"   Status Code: {plans_response.status_code}")
        
        if plans_response.status_code != 200:
            print(f"❌ 列出方案失敗: {plans_response.status_code}")
            print(f"   Response: {plans_response.text}")
            return
        
        plans_data = plans_response.json()
        
        if not plans_data.get("success"):
            print(f"❌ API 返回失敗")
            print(f"   Error: {plans_data.get('error')}")
            return
        
        print(f"✅ 方案列出成功")
        print(f"   方案總數: {plans_data['total']}")
        print(f"   搜尋查詢: {plans_data.get('search_query', 'N/A')}")
        
        # 顯示方案詳情
        print(f"\n   方案列表:")
        for i, plan in enumerate(plans_data["plans"], 1):
            print(f"\n   [{i}] {plan['name']}")
            print(f"       方案 ID: {plan['plan_id']}")
            print(f"       月租費: NT$ {plan['monthly_fee']}")
            print(f"       數據: {plan['data']}")
            print(f"       語音: {plan['voice']}")
            print(f"       簡訊: {plan.get('sms', '不限')}")
            print(f"       合約月數: {plan['contract_months']}")
            print(f"       推薦: {'✅' if plan.get('is_recommended') else '⬜'}")
            if plan.get('gifts'):
                print(f"       贈品: {', '.join(plan['gifts'])}")
            if plan.get('promotion_title'):
                print(f"       促銷: {plan['promotion_title']}")
        
        print(f"\n{'=' * 60}")
        print(f"✅ Step 8 測試完成")
        print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(test_step8())
