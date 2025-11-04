"""
Step 9 測試 - 比較方案

測試 POST /api/renewal-workflow/step/compare-plans
"""
import sys
import asyncio
import httpx
from pathlib import Path

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

async def test_step9():
    """測試完整 Step 9 流程"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "=" * 60)
        print("Step 9 測試：比較方案")
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
            json={
                "session_id": renewal_session_id
            }
        )
        
        if phones_response.status_code != 200:
            print(f"❌ 列出門號失敗: {phones_response.status_code}")
            return
        
        phones_data = phones_response.json()
        print(f"✅ 列出門號成功")
        print(f"   門號數: {len(phones_data['phones'])}")
        
        # 列出所有門號供參考
        available_phones = phones_data.get('phones', [])
        if available_phones:
            print(f"\n   可用門號:")
            for phone in available_phones:
                print(f"   - {phone['phone_number']} ({phone.get('plan_name', 'N/A')})")
        
        # Step 4: 選擇門號並檢查資格
        # 使用第一個門號 (0912345678) 符合續約資格 (29天後到期)
        print("\n[Step 4] 選擇門號並檢查資格...")
        test_phone_number = "0912345678"  # 使用符合資格的門號
        
        select_phone_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "phone_number": test_phone_number
            }
        )
        
        select_phone_data = select_phone_response.json()
        
        # 檢查 API 回應
        if not select_phone_data.get('success'):
            print(f"❌ 門號選擇失敗: {select_phone_data.get('message', 'Unknown error')}")
            if 'eligibility' in select_phone_data:
                eligibility = select_phone_data['eligibility']
                print(f"\n   資格檢查結果:")
                print(f"   - 符合資格: {'是' if eligibility.get('eligible') else '否'}")
                if not eligibility.get('eligible'):
                    print(f"   - 原因: {eligibility.get('reason', 'N/A')}")
                    if eligibility.get('details'):
                        print(f"   - 檢查項目:")
                        for check in eligibility.get('details', []):
                            status_icon = "✓" if check.get('status') == 'pass' else "✗"
                            print(f"     {status_icon} {check.get('item')}: {check.get('message')}")
            print("\n⚠️  此門號不符合續約資格，無法繼續測試。請使用符合資格的門號。")
            return
        
        print(f"✅ 門號選擇成功: {test_phone_number}")
        if 'eligibility' in select_phone_data:
            eligibility = select_phone_data['eligibility']
            print(f"   資格檢查: {'✓ 通過' if eligibility.get('eligible') else '✗ 不通過'}")
        
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
        
        print(f"✅ 選擇裝置類型成功: smartphone")
        
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
        
        print(f"✅ 選擇作業系統成功: Android")
        
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
        print(f"✅ 設備查詢成功")
        print(f"   設備數量: {len(devices_data.get('devices', []))}")
        print(f"   選擇設備: DEV004")
        
        # Step 7-1: 選擇設備
        print("\n[Step 7-1] 選擇設備...")
        select_device_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "device_id": "DEV004",
                "color": "黑色"
            }
        )
        
        if select_device_response.status_code != 200:
            print(f"❌ 選擇設備失敗: {select_device_response.status_code}")
            return
        
        print(f"✅ 設備選擇成功")
        
        # Step 8: ⭐ 列出方案
        print("\n[Step 8] ⭐ 列出方案...")
        plans_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-plans",
            headers=headers,
            json={
                "session_id": renewal_session_id
            }
        )
        
        if plans_response.status_code != 200:
            print(f"❌ 列出方案失敗: {plans_response.status_code}")
            print(f"   Response: {plans_response.text}")
            return
        
        plans_data = plans_response.json()
        print(f"✅ 列出方案成功")
        print(f"   方案數: {plans_data.get('total', 0)}")
        
        if plans_data.get('total', 0) == 0:
            print("⚠️  沒有可用方案，無法繼續測試 Step 9")
            return
        
        # 取得前 3 個方案的 ID 進行比較
        available_plans = plans_data.get('plans', [])
        plan_ids = [plan['plan_id'] for plan in available_plans[:3]]
        
        print(f"\n   選擇方案進行比較: {plan_ids}")
        
        # Step 9: 比較方案
        print("\n[Step 9] 比較方案...")
        compare_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/compare-plans",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "plan_ids": plan_ids
            }
        )
        
        if compare_response.status_code != 200:
            print(f"❌ 比較方案失敗: {compare_response.status_code}")
            print(f"   Response: {compare_response.text}")
            return
        
        compare_data = compare_response.json()
        
        if not compare_data.get('success'):
            print(f"❌ 比較方案失敗: {compare_data.get('error')}")
            return
        
        print(f"✅ 比較方案成功")
        comparison = compare_data.get('comparison', {})
        compared_plans = comparison.get('plans', [])
        
        print(f"\n📊 比較結果:")
        print(f"   比較方案數: {len(compared_plans)}")
        
        # 顯示方案基本資訊
        for plan in compared_plans:
            print(f"\n   📱 {plan['name']}")
            print(f"      方案 ID: {plan['plan_id']}")
            print(f"      月租費: ${plan['monthly_fee']}")
            print(f"      上網: {plan['data']}")
            print(f"      語音: {plan['voice']}")
            print(f"      合約: {plan['contract_months']} 個月")
        
        # 顯示 AI 推薦
        recommendation = comparison.get('recommendation', '')
        if recommendation:
            print(f"\n🤖 AI 推薦:")
            print(f"   {recommendation}")
        
        # 驗證比較數據
        comparison_info = comparison.get('comparison', {})
        if comparison_info:
            print(f"\n📈 比較數據:")
            
            # 月租費比較
            monthly_fee_info = comparison_info.get('monthly_fee', {})
            if monthly_fee_info:
                print(f"   月租費範圍: ${monthly_fee_info.get('min')} - ${monthly_fee_info.get('max')}")
            
            # 數據流量比較
            data_info = comparison_info.get('data', {})
            if data_info:
                data_values = data_info.get('values', {})
                print(f"   數據方案: {', '.join([f'{k}: {v}' for k, v in data_values.items()])}")
        
        print("\n" + "=" * 60)
        print("✅ Step 9 測試完成")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_step9())
