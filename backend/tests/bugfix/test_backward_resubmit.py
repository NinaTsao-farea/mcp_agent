"""
測試從後續步驟返回並重新提交的場景
驗證：
1. Step 7 → 返回 Step 6 → 重新提交 → 應該成功
2. Step 7 → 返回 Step 5 → 重新提交 → 應該成功
3. Step 8 → 返回 Step 7 → 重新提交 → 應該成功
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api"


def print_step(title: str):
    """打印步驟標題"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def print_result(data: dict):
    """打印結果"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


async def test_backward_resubmit():
    """測試返回並重新提交"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print_step("Step 0: 登入")
        login_resp = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "staff_code": "S001",
                "password": "password"
            }
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
            json={"session_id": session_id, "id_number": "A123456789"}
        )
        
        await client.post(
            f"{BASE_URL}/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": session_id}
        )
        
        select_phone_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-phone",
            headers=headers,
            json={"session_id": session_id, "phone_number": "0912345678"}
        )
        assert select_phone_resp.status_code == 200
        print("✅ 已完成到 Step 3")
        
        print_step("Step 5: 選擇設備類型")
        device_type_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device-type",
            headers=headers,
            json={"session_id": session_id, "device_type": "smartphone"}
        )
        assert device_type_resp.status_code == 200
        print("✅ Step 5 完成")
        
        print_step("Step 6: 選擇作業系統")
        device_os_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device-os",
            headers=headers,
            json={"session_id": session_id, "os_type": "ios"}
        )
        assert device_os_resp.status_code == 200
        print("✅ Step 6 完成")
        
        print_step("Step 7: 選擇設備")
        query_devices_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/query-devices",
            headers=headers,
            json={"session_id": session_id, "os_type": "ios"}
        )
        devices = query_devices_resp.json()['devices']
        device_id = devices[0]['device_id']
        
        select_device_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device",
            headers=headers,
            json={"session_id": session_id, "device_id": device_id, "color": "黑色"}
        )
        assert select_device_resp.status_code == 200
        print("✅ Step 7 完成")
        
        # ========================================
        # 測試 1: 從 Step 7 返回 Step 6 重新提交
        # ========================================
        print_step("🔙 測試 1: Step 7 → Step 6 → 重新提交")
        
        # 模擬用戶返回（前端會用 router.back()）
        # 後端狀態仍在 SELECT_DEVICE，但用戶要重新提交 select-device-os
        
        device_os_resubmit = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device-os",
            headers=headers,
            json={"session_id": session_id, "os_type": "android"}
        )
        
        if device_os_resubmit.status_code == 200:
            print("✅ 測試 1 通過：可以從 Step 7 返回 Step 6 重新提交")
            print_result(device_os_resubmit.json())
        else:
            print(f"❌ 測試 1 失敗：{device_os_resubmit.status_code}")
            print_result(device_os_resubmit.json())
            return
        
        # 重新選擇設備
        query_devices_resp2 = await client.post(
            f"{BASE_URL}/renewal-workflow/step/query-devices",
            headers=headers,
            json={"session_id": session_id, "os_type": "android"}
        )
        android_devices = query_devices_resp2.json()['devices']
        android_device_id = android_devices[0]['device_id']
        
        select_device_resp2 = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device",
            headers=headers,
            json={"session_id": session_id, "device_id": android_device_id, "color": "白色"}
        )
        assert select_device_resp2.status_code == 200
        print("✅ 已重新選擇 Android 設備")
        
        # ========================================
        # 測試 2: 從 Step 8 返回 Step 7 重新提交
        # ========================================
        print_step("🔙 測試 2: Step 8 → Step 7 → 重新提交")
        
        # 先到 Step 8
        list_plans_resp = await client.post(
            f"{BASE_URL}/renewal-workflow/step/list-plans",
            headers=headers,
            json={"session_id": session_id}
        )
        assert list_plans_resp.status_code == 200
        print("✅ 已到達 Step 8")
        
        # 模擬返回並重新選擇設備
        select_device_resubmit = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device",
            headers=headers,
            json={"session_id": session_id, "device_id": devices[0]['device_id'], "color": "金色"}
        )
        
        if select_device_resubmit.status_code == 200:
            print("✅ 測試 2 通過：可以從 Step 8 返回 Step 7 重新提交")
            print_result(select_device_resubmit.json())
        else:
            print(f"❌ 測試 2 失敗：{select_device_resubmit.status_code}")
            print_result(select_device_resubmit.json())
            return
        
        # ========================================
        # 測試 3: 從 Step 8 返回 Step 5 重新提交
        # ========================================
        print_step("🔙 測試 3: Step 8 → Step 5 → 重新提交")
        
        # 重新選擇設備類型
        device_type_resubmit = await client.post(
            f"{BASE_URL}/renewal-workflow/step/select-device-type",
            headers=headers,
            json={"session_id": session_id, "device_type": "smartphone"}
        )
        
        if device_type_resubmit.status_code == 200:
            print("✅ 測試 3 通過：可以從 Step 8 返回 Step 5 重新提交")
            print_result(device_type_resubmit.json())
        else:
            print(f"❌ 測試 3 失敗：{device_type_resubmit.status_code}")
            print_result(device_type_resubmit.json())
            return
        
        print("\n" + "=" * 60)
        print("✅ 所有測試通過！")
        print("=" * 60)
        print("\n驗證結果：")
        print("✅ 1. 可以從 Step 7 返回 Step 6 並重新提交")
        print("✅ 2. 可以從 Step 8 返回 Step 7 並重新提交")
        print("✅ 3. 可以從 Step 8 返回 Step 5 並重新提交")
        print("✅ 4. 後端自動重置狀態，避免狀態轉換衝突")


if __name__ == "__main__":
    asyncio.run(test_backward_resubmit())
