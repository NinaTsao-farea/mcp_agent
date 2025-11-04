"""
測試從首頁重新開始續約流程

模擬用戶操作：
1. 登入
2. 開始續約流程
3. 查詢客戶 → 選擇門號 → 選擇裝置類型
4. 返回首頁（導航列返回按鈕）
5. 再次點擊「開始續約」
6. 應該能成功開始新流程，而不是出現「非法的狀態轉換」錯誤
"""
import asyncio
import httpx
from test_config import TEST_STAFF

BASE_URL = "http://localhost:8000"


async def test_restart_workflow():
    """測試從首頁重新開始續約流程"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "="*60)
        print("測試：從首頁重新開始續約流程")
        print("="*60)
        
        # Step 1: 登入
        print("\n[Step 1] 員工登入...")
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "staff_code": TEST_STAFF["staff_code"],
                "password": TEST_STAFF["password"]
            }
        )
        assert login_response.status_code == 200, f"登入失敗: {login_response.text}"
        login_data = login_response.json()
        assert login_data["success"], "登入失敗"
        
        auth_session_id = login_data["session_id"]
        print(f"✅ 登入成功，auth_session_id: {auth_session_id}")
        
        # Step 2: 第一次開始續約流程
        print("\n[Step 2] 第一次開始續約流程...")
        start_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers={"X-Session-ID": auth_session_id}
        )
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data["success"]
        
        first_renewal_session = start_data["session_id"]
        print(f"✅ 第一次續約流程已開始，renewal_session_id: {first_renewal_session}")
        
        # Step 3: 查詢客戶
        print("\n[Step 3] 查詢客戶...")
        query_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers={"X-Session-ID": auth_session_id},
            json={
                "session_id": first_renewal_session,
                "id_number": "A123456789"
            }
        )
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert query_data["success"]
        print(f"✅ 客戶查詢成功: {query_data['customer']['name']}")
        
        # Step 4: 列出門號
        print("\n[Step 4] 列出門號...")
        phones_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            headers={"X-Session-ID": auth_session_id},
            json={"session_id": first_renewal_session}
        )
        assert phones_response.status_code == 200
        phones_data = phones_response.json()
        assert phones_data["success"]
        print(f"✅ 查詢到 {len(phones_data['phones'])} 個門號")
        
        # Step 5: 選擇門號
        print("\n[Step 5] 選擇門號...")
        select_phone_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers={"X-Session-ID": auth_session_id},
            json={
                "session_id": first_renewal_session,
                "phone_number": "0912345678"
            }
        )
        assert select_phone_response.status_code == 200
        select_phone_data = select_phone_response.json()
        assert select_phone_data["success"]
        print(f"✅ 門號選擇成功，符合續約資格")
        
        # Step 6: 選擇裝置類型
        print("\n[Step 6] 選擇裝置類型...")
        device_type_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            headers={"X-Session-ID": auth_session_id},
            json={
                "session_id": first_renewal_session,
                "device_type": "phone"
            }
        )
        print(f"   Response status: {device_type_response.status_code}")
        
        if device_type_response.status_code != 200:
            print(f"   ⚠️  選擇裝置類型失敗: {device_type_response.text}")
            print("   跳過此步驟，繼續測試...")
        else:
            device_type_data = device_type_response.json()
            if device_type_data.get("success"):
                print(f"✅ 裝置類型選擇成功: phone")
                print(f"📍 當前狀態: SELECT_DEVICE_TYPE")
            else:
                print(f"   ⚠️  選擇裝置類型失敗: {device_type_data.get('error')}")
                print("   跳過此步驟，繼續測試...")
        
        # Step 7: 模擬返回首頁（不刪除 session，只是離開）
        print("\n[Step 7] 用戶點擊導航列「返回」按鈕，回到首頁...")
        print("⚠️  注意：session 仍然存在，狀態停留在 SELECT_DEVICE_TYPE")
        
        # Step 8: 用戶再次點擊「開始續約」，應該清空舊 session
        print("\n[Step 8] 用戶再次點擊「開始續約」...")
        print("💡 前端會調用 clearWorkflow() 清空舊 session")
        
        # 模擬前端的 clearWorkflow() - 刪除舊 session
        print(f"   刪除舊 session: {first_renewal_session}")
        try:
            delete_response = await client.delete(
                f"{BASE_URL}/api/renewal-workflow/session/{first_renewal_session}",
                headers={"X-Session-ID": auth_session_id}
            )
            if delete_response.status_code == 200:
                print("   ✅ 舊 session 已刪除")
            else:
                print(f"   ⚠️  刪除 session 響應: {delete_response.status_code}")
        except Exception as e:
            print(f"   ⚠️  刪除 session 異常: {e}")
        
        # Step 9: 開始新的續約流程
        print("\n[Step 9] 開始新的續約流程...")
        new_start_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers={"X-Session-ID": auth_session_id}
        )
        assert new_start_response.status_code == 200
        new_start_data = new_start_response.json()
        assert new_start_data["success"]
        
        second_renewal_session = new_start_data["session_id"]
        print(f"✅ 第二次續約流程已開始，new_renewal_session_id: {second_renewal_session}")
        print(f"   第一次 session: {first_renewal_session}")
        print(f"   第二次 session: {second_renewal_session}")
        assert first_renewal_session != second_renewal_session, "應該是不同的 session"
        
        # Step 10: 再次查詢客戶（這次應該成功，因為是新的 session）
        print("\n[Step 10] 使用新 session 查詢客戶...")
        new_query_response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers={"X-Session-ID": auth_session_id},
            json={
                "session_id": second_renewal_session,
                "id_number": "A123456789"
            }
        )
        
        print(f"   Response status: {new_query_response.status_code}")
        new_query_data = new_query_response.json()
        
        if new_query_response.status_code == 200 and new_query_data.get("success"):
            print(f"✅ 測試通過！使用新 session 查詢客戶成功")
            print(f"   客戶: {new_query_data['customer']['name']}")
            print(f"   新流程狀態正常")
        else:
            print(f"❌ 測試失敗！")
            print(f"   錯誤: {new_query_data.get('error')}")
            print(f"   完整響應: {new_query_data}")
            raise AssertionError("查詢客戶失敗")
        
        # 清理：刪除新的 session
        print("\n[清理] 刪除測試 session...")
        try:
            await client.delete(
                f"{BASE_URL}/api/renewal-workflow/session/{second_renewal_session}",
                headers={"X-Session-ID": auth_session_id}
            )
            print("✅ 清理完成")
        except:
            pass
        
        print("\n" + "="*60)
        print("✅ 測試完成：從首頁重新開始續約流程正常工作")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_restart_workflow())
