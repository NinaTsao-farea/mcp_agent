"""
Step 4 測試 - 續約資格檢查

測試 POST /api/renewal-workflow/step/select-phone
包含：符合資格和不符合資格的測試案例
"""
import sys
import asyncio
import httpx
from pathlib import Path

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

async def test_eligibility_check():
    """測試續約資格檢查"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "=" * 80)
        print("Step 4 測試：續約資格檢查")
        print("=" * 80)
        
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
            return
        
        login_data = login_response.json()
        session_id = login_data["session_id"]
        print(f"✅ 登入成功")
        
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
        print(f"✅ 客戶查詢成功: {customer_data['customer']['name']}")
        
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
        available_phones = phones_data.get('phones', [])
        print(f"✅ 列出門號成功: {len(available_phones)} 個門號")
        
        print(f"\n   可用門號列表:")
        for idx, phone in enumerate(available_phones, 1):
            print(f"   {idx}. {phone['phone_number']}")
            print(f"      方案: {phone.get('plan_name', 'N/A')}")
            print(f"      月租費: ${phone.get('monthly_fee', 0)}")
            print(f"      狀態: {phone.get('status', 'N/A')}")
        
        # ========================================
        # 測試案例 1: 不符合資格的門號
        # ========================================
        print("\n" + "=" * 80)
        print("測試案例 1: 不符合續約資格的門號")
        print("=" * 80)
        
        print("\n[Step 4.1] 選擇門號: 0987654321 (預期不符合資格)")
        
        select_phone_response_1 = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers=headers,
            json={
                "session_id": renewal_session_id,
                "phone_number": "0987654321"
            }
        )
        
        select_phone_data_1 = select_phone_response_1.json()
        
        print(f"\n📋 API 回應:")
        print(f"   Success: {select_phone_data_1.get('success')}")
        print(f"   Message: {select_phone_data_1.get('message')}")
        
        if 'eligibility' in select_phone_data_1:
            eligibility = select_phone_data_1['eligibility']
            print(f"\n🔍 資格檢查結果:")
            print(f"   符合資格: {'✓ 是' if eligibility.get('eligible') else '✗ 否'}")
            print(f"   原因: {eligibility.get('reason', 'N/A')}")
            
            if eligibility.get('details'):
                print(f"\n   檢查項目明細:")
                for check in eligibility.get('details', []):
                    status = check.get('status')
                    status_icon = "✓" if status == 'pass' else "✗"
                    status_text = "通過" if status == 'pass' else "未通過"
                    print(f"   {status_icon} {check.get('item')}: {status_text}")
                    print(f"      {check.get('message')}")
        
        # 驗證預期結果
        if not select_phone_data_1.get('success'):
            print(f"\n✅ 測試通過: API 正確回傳不符合資格 (success=False)")
            print(f"   前端應顯示錯誤訊息，不允許繼續下一步")
        else:
            print(f"\n⚠️  測試警告: 預期不符合資格但 API 回傳 success=True")
        
        # ========================================
        # 測試案例 2: 符合資格的門號
        # ========================================
        print("\n" + "=" * 80)
        print("測試案例 2: 符合續約資格的門號")
        print("=" * 80)
        
        print("\n[Step 4.2] 選擇門號: 0912345678 (預期符合資格)")
        
        # 需要重新開始流程（因為 Step 4.1 可能已進入 CHECK_ELIGIBILITY 狀態）
        start_response_2 = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        renewal_session_id_2 = start_response_2.json()["session_id"]
        
        # 重複 Step 1-3
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": renewal_session_id_2, "id_number": "A123456789"}
        )
        
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": renewal_session_id_2}
        )
        
        # 選擇符合資格的門號
        select_phone_response_2 = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers=headers,
            json={
                "session_id": renewal_session_id_2,
                "phone_number": "0912345678"
            }
        )
        
        select_phone_data_2 = select_phone_response_2.json()
        
        print(f"\n📋 API 回應:")
        print(f"   Success: {select_phone_data_2.get('success')}")
        print(f"   Message: {select_phone_data_2.get('message')}")
        
        if 'eligibility' in select_phone_data_2:
            eligibility = select_phone_data_2['eligibility']
            print(f"\n🔍 資格檢查結果:")
            print(f"   符合資格: {'✓ 是' if eligibility.get('eligible') else '✗ 否'}")
            print(f"   原因: {eligibility.get('reason', 'N/A')}")
            
            if eligibility.get('details'):
                print(f"\n   檢查項目明細:")
                for check in eligibility.get('details', []):
                    status = check.get('status')
                    status_icon = "✓" if status == 'pass' else "✗"
                    status_text = "通過" if status == 'pass' else "未通過"
                    print(f"   {status_icon} {check.get('item')}: {status_text}")
                    print(f"      {check.get('message')}")
        
        # 驗證預期結果
        if select_phone_data_2.get('success'):
            print(f"\n✅ 測試通過: API 正確回傳符合資格 (success=True)")
            print(f"   前端應允許繼續下一步 (選擇裝置類型)")
        else:
            print(f"\n⚠️  測試警告: 預期符合資格但 API 回傳 success=False")
        
        # ========================================
        # 測試總結
        # ========================================
        print("\n" + "=" * 80)
        print("測試總結")
        print("=" * 80)
        
        test_1_pass = not select_phone_data_1.get('success')
        test_2_pass = select_phone_data_2.get('success')
        
        print(f"\n測試案例 1 (不符合資格): {'✅ 通過' if test_1_pass else '❌ 失敗'}")
        print(f"測試案例 2 (符合資格):   {'✅ 通過' if test_2_pass else '❌ 失敗'}")
        
        if test_1_pass and test_2_pass:
            print(f"\n🎉 所有測試通過！")
        else:
            print(f"\n⚠️  部分測試失敗，請檢查 API 邏輯")
        
        print("\n" + "=" * 80)
        print("前端實作建議")
        print("=" * 80)
        print("""
1. 檢查 API 回應的 success 欄位
2. 如果 success=false，顯示 eligibility.reason 給使用者
3. 顯示詳細的檢查項目 (eligibility.details)
4. 不允許進入下一步，提供「返回」或「重新選擇」按鈕
5. 如果 success=true，才允許前進到 Step 5 (選擇裝置類型)
        """)


if __name__ == "__main__":
    asyncio.run(test_eligibility_check())
