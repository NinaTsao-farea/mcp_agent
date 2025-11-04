# -*- coding: utf-8 -*-
"""
Test Step 6: Select Device OS

Test flow:
1. Login
2. Start renewal workflow
3. Step 1: Query customer
4. Step 2-3: List phones
5. Step 4: Select phone and check eligibility
6. Step 5: Select device type (smartphone)
7. Step 6: Select device OS (iOS/Android)
"""
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"


async def test_step6_select_ios():
    """Test Step 6 complete flow - select iOS"""
    print("=" * 80)
    print("Step 6 Test - Select iOS")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("\n[1] Login...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "staff_code": "S001",
                "password": "password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        session_id = data.get("session_id")
        print(f"OK Login successful, Session ID: {session_id}")
        
        headers = {"X-Session-ID": session_id}
        
        # 2. Start renewal workflow
        print("\n[2] Start renewal workflow...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        renewal_session_id = data.get("session_id")
        print(f"OK Renewal workflow started, Renewal Session ID: {renewal_session_id}")
        
        # 3. Step 1: Query customer
        print("\n[3] Step 1: Query customer...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            json={
                "session_id": renewal_session_id,
                "id_number": "A123456789"
            },
            headers=headers
        )
        if response.status_code != 200:
            print(f"ERROR Status: {response.status_code}")
            print(f"ERROR Response: {response.text}")
        assert response.status_code == 200
        data = response.json()
        if not data.get("success"):
            print(f"ERROR API failed: {data.get('error')}")
        assert data.get("success") is True
        print(f"OK Customer found: {data.get('customer', {}).get('name')}")
        
        # 4. Step 2-3: List phones
        print("\n[4] Step 2-3: List phones...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        phones = data.get("phones", [])
        print(f"OK Found {len(phones)} phones")
        
        # 5. Step 4: Select phone
        print("\n[5] Step 4: Select phone...")
        test_phone = phones[0]["phone_number"]
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            json={
                "session_id": renewal_session_id,
                "phone_number": test_phone
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"OK Phone {test_phone} selected")
        print(f"OK Eligibility: {data.get('eligibility', {}).get('status')}")
        
        # 6. Step 5: Select device type
        print("\n[6] Step 5: Select device type...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            json={
                "session_id": renewal_session_id,
                "device_type": "smartphone"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("next_step") == "select_device_os"
        print(f"OK Device type selected: smartphone")
        print(f"OK Next step: {data.get('next_step')}")
        
        # 7. Step 6: Select OS (iOS)
        print("\n[7] Step 6: Select OS (iOS)...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": renewal_session_id,
                "os_type": "ios"
            },
            headers=headers
        )
        if response.status_code != 200:
            print(f"ERROR Status: {response.status_code}")
            print(f"ERROR Response: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("os_type") == "ios"
        assert data.get("next_step") == "select_device"
        print(f"OK OS selected: {data.get('os_type')}")
        print(f"OK Next step: {data.get('next_step')}")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 6 (iOS) all tests passed!")
        print("=" * 80)


async def test_step6_select_android():
    """Test Step 6 complete flow - select Android"""
    print("\n" + "=" * 80)
    print("Step 6 Test - Select Android")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Quick setup
        print("\n[Setup] Running prerequisite steps...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"staff_code": "S001", "password": "password"}
        )
        session_id = response.json().get("session_id")
        headers = {"X-Session-ID": session_id}
        
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        renewal_session_id = response.json().get("session_id")
        
        # 3-5: Quick prerequisite steps
        print("\n[3-5] Running prerequisite steps...")
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            json={"session_id": renewal_session_id, "id_number": "A123456789"},
            headers=headers
        )
        phones_resp = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        test_phone = phones_resp.json()["phones"][0]["phone_number"]
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            json={"session_id": renewal_session_id, "phone_number": test_phone},
            headers=headers
        )
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            json={"session_id": renewal_session_id, "device_type": "smartphone"},
            headers=headers
        )
        print("OK Prerequisite steps completed")
        
        # 6. Step 6: Select OS (Android)
        print("\n[6] Step 6: Select OS (Android)...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": renewal_session_id,
                "os_type": "android"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("os_type") == "android"
        assert data.get("next_step") == "select_device"
        print(f"OK OS selected: {data.get('os_type')}")
        print(f"OK Next step: {data.get('next_step')}")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 6 (Android) all tests passed!")
        print("=" * 80)


async def test_step6_case_insensitive():
    """Test Step 6 - case insensitive"""
    print("\n" + "=" * 80)
    print("Step 6 Test - Case Insensitive")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Quick setup
        print("\n[Setup] Running prerequisite steps...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"staff_code": "S001", "password": "password"}
        )
        session_id = response.json().get("session_id")
        headers = {"X-Session-ID": session_id}
        
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        renewal_session_id = response.json().get("session_id")
        
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            json={"session_id": renewal_session_id, "id_number": "A123456789"},
            headers=headers
        )
        phones_resp = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        test_phone = phones_resp.json()["phones"][0]["phone_number"]
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            json={"session_id": renewal_session_id, "phone_number": test_phone},
            headers=headers
        )
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            json={"session_id": renewal_session_id, "device_type": "smartphone"},
            headers=headers
        )
        
        # Test uppercase iOS
        print("\n[Test] Testing uppercase 'iOS'...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": renewal_session_id,
                "os_type": "iOS"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("os_type") == "ios"  # Should convert to lowercase
        print(f"OK 'iOS' correctly converted to 'ios'")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 6 case test passed!")
        print("=" * 80)


async def test_step6_error_handling():
    """Test Step 6 - error handling"""
    print("\n" + "=" * 80)
    print("Step 6 Test - Error Handling")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Quick setup
        print("\n[Setup] Running prerequisite steps...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"staff_code": "S001", "password": "password"}
        )
        session_id = response.json().get("session_id")
        headers = {"X-Session-ID": session_id}
        
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        renewal_session_id = response.json().get("session_id")
        
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            json={"session_id": renewal_session_id, "id_number": "A123456789"},
            headers=headers
        )
        phones_resp = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        test_phone = phones_resp.json()["phones"][0]["phone_number"]
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            json={"session_id": renewal_session_id, "phone_number": test_phone},
            headers=headers
        )
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-type",
            json={"session_id": renewal_session_id, "device_type": "smartphone"},
            headers=headers
        )
        
        # Test 1: Missing session_id
        print("\n[Test 1] Testing missing session_id...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={"os_type": "ios"},
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("success") is False
        print("OK Missing session_id correctly returns 400")
        
        # Test 2: Missing os_type
        print("\n[Test 2] Testing missing os_type...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("success") is False
        print("OK Missing os_type correctly returns 400")
        
        # Test 3: Invalid os_type
        print("\n[Test 3] Testing invalid os_type...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": renewal_session_id,
                "os_type": "windows"
            },
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("success") is False
        print("OK Invalid os_type correctly returns 400")
        
        # Test 4: Invalid session_id
        print("\n[Test 4] Testing invalid session_id...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={
                "session_id": "invalid_session_12345",
                "os_type": "ios"
            },
            headers=headers
        )
        assert response.status_code == 404
        data = response.json()
        assert data.get("success") is False
        print("OK Invalid session_id correctly returns 404")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 6 error handling all tests passed!")
        print("=" * 80)


async def main():
    """Run all tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 20 + "Step 6 - Select Device OS Test Suite" + " " * 22 + "|")
    print("+" + "=" * 78 + "+")
    
    try:
        # Test 1: Select iOS
        await test_step6_select_ios()
        
        # Test 2: Select Android
        await test_step6_select_android()
        
        # Test 3: Case insensitive
        await test_step6_case_insensitive()
        
        # Test 4: Error handling
        await test_step6_error_handling()
        
        print("\n")
        print("+" + "=" * 78 + "+")
        print("|" + " " * 27 + "ALL TESTS PASSED!" + " " * 35 + "|")
        print("+" + "=" * 78 + "+")
        print("\n")
        
    except AssertionError as e:
        print(f"\nFAILED - Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR - Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
