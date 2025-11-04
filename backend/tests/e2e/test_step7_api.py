"""
測試 Step 7 - 使用真實 API query-devices
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_step7_with_query_devices():
    """測試完整流程：從登入到使用 query-devices API"""
    print("\n" + "="*60)
    print("測試 Step 7 - Query Devices API")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 登入
        print("\n[Step 1] 登入...")
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"staff_code": "S001", "password": "password"}
        )
        assert login_response.status_code == 200
        data = login_response.json()
        assert data.get("success") is True
        session_id = data.get("session_id")
        print(f"✓ 登入成功, Session ID: {session_id}")
        
        headers = {"X-Session-ID": session_id}
        
        # 2. 開始續約流程
        print("\n[Step 2] 開始續約流程...")
        start_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        if start_response.status_code != 200:
            print(f"✗ 錯誤: {start_response.status_code}")
            print(f"回應: {start_response.text}")
        assert start_response.status_code == 200
        data = start_response.json()
        assert data.get("success") is True
        renewal_session_id = data.get("session_id")
        print(f"✓ Renewal Session ID: {renewal_session_id}")
        
        # 3. 查詢客戶
        print("\n[Step 3] 查詢客戶...")
        customer_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            json={
                "session_id": renewal_session_id,
                "id_number": "A123456789"
            },
            headers=headers
        )
        assert customer_response.status_code == 200
        print(f"✓ 客戶: {customer_response.json()['customer']['name']}")
        
        # 4. 列出門號
        print("\n[Step 4] 列出門號...")
        phones_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        assert phones_response.status_code == 200
        phones = phones_response.json()["phones"]
        print(f"✓ 找到 {len(phones)} 個門號")
        
        # 5. 選擇門號
        print("\n[Step 5] 選擇門號...")
        select_phone_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            json={
                "session_id": renewal_session_id,
                "phone_number": phones[0]["phone_number"]
            },
            headers=headers
        )
        assert select_phone_response.status_code == 200
        print(f"✓ 門號: {phones[0]['phone_number']}")
        
        # 6. 選擇裝置類型
        print("\n[Step 6a] 選擇裝置類型 (smartphone)...")
        device_type_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            json={
                "session_id": renewal_session_id,
                "device_type": "smartphone"
            },
            headers=headers
        )
        assert device_type_response.status_code == 200
        print(f"✓ 裝置類型: smartphone")
        print(f"✓ 下一步: {device_type_response.json()['next_step']}")
        
        # 7. 選擇作業系統
        print("\n[Step 6b] 選擇作業系統 (ios)...")
        os_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": renewal_session_id,
                "os_type": "ios"
            },
            headers=headers
        )
        assert os_response.status_code == 200
        print(f"✓ 作業系統: ios")
        print(f"✓ 下一步: {os_response.json()['next_step']}")
        
        # Debug: 檢查 session 狀態
        print("\n[Debug] 檢查 session 中的 device_os...")
        debug_session_response = await client.get(
            f"{BASE_URL}/api/renewal-workflow/session/{renewal_session_id}",
            headers=headers
        )
        if debug_session_response.status_code == 200:
            debug_data = debug_session_response.json()['session']
            customer_selection = debug_data.get('customer_selection', {})
            device_os_value = customer_selection.get('device_os')
            print(f"  customer_selection.device_os = '{device_os_value}'")
            print(f"  device_os type: {type(device_os_value)}")
            print(f"  device_os repr: {repr(device_os_value)}")
            print(f"  device_os bool: {bool(device_os_value)}")
            if device_os_value:
                print(f"  device_os length: {len(device_os_value)}")
                print(f"  device_os bytes: {device_os_value.encode('utf-8') if isinstance(device_os_value, str) else 'N/A'}")
        
        # 8. 查詢設備 (使用 query-devices API)
        print("\n[Step 7] 查詢設備...")
        query_devices_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-devices",
            json={
                "session_id": renewal_session_id,
                "store_id": "STORE001"
            },
            headers=headers
        )
        
        print(f"狀態碼: {query_devices_response.status_code}")
        result = query_devices_response.json()
        
        if query_devices_response.status_code == 200:
            print(f"✓ 查詢成功")
            print(f"✓ 門市: {result['store_id']}")
            print(f"✓ 作業系統: {result['os_preference']}")
            print(f"✓ 找到 {result['device_count']} 個設備")
            
            # 顯示設備列表
            print("\n設備列表:")
            for i, device in enumerate(result['devices'], 1):
                print(f"\n  [{i}] {device['brand']} {device['model']}")
                print(f"      ID: {device['device_id']}")
                print(f"      顏色: {device['color']}")
                print(f"      儲存: {device['storage']}")
                print(f"      價格: NT$ {device['price']:,}")
                print(f"      庫存: {device['available']}/{device['total_quantity']}")
                print(f"      狀態: {'有貨' if device['in_stock'] else '缺貨'}")
            
            # 9. 選擇第一個設備
            if result['devices']:
                print("\n[Step 8] 選擇設備...")
                first_device = result['devices'][0]
                select_device_response = await client.post(
                    f"{BASE_URL}/api/renewal-workflow/step/select-device",
                    json={
                        "session_id": renewal_session_id,
                        "device_id": first_device['device_id'],
                        "color": first_device['color']
                    },
                    headers=headers
                )
                
                if select_device_response.status_code == 200:
                    print(f"✓ 設備選擇成功")
                    select_result = select_device_response.json()
                    print(f"✓ 設備 ID: {select_result['device_id']}")
                    print(f"✓ 顏色: {select_result['color']}")
                    print(f"✓ 下一步: {select_result['next_step']}")
                else:
                    print(f"✗ 設備選擇失敗: {select_device_response.json()}")
            
            print("\n" + "="*60)
            print("測試完成 - 成功 ✓")
            print("="*60)
        else:
            print(f"✗ 查詢失敗")
            print(f"錯誤: {result.get('error', 'Unknown error')}")
            print("\n檢查 session 狀態...")
            
            # 檢查 session
            session_response = await client.get(
                f"{BASE_URL}/api/renewal-workflow/session/{renewal_session_id}",
                headers=headers
            )
            if session_response.status_code == 200:
                session_data = session_response.json()['session']
                print(f"\nSession 資料:")
                print(f"  當前步驟: {session_data.get('current_step')}")
                print(f"  客戶選擇: {session_data.get('customer_selection')}")

if __name__ == "__main__":
    asyncio.run(test_step7_with_query_devices())
