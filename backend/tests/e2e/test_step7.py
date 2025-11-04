# -*- coding: utf-8 -*-
"""
Test Step 7: Select Device

Test flow:
1. Login
2. Start renewal workflow
3. Step 1-6: Complete prerequisite steps
4. Step 7: Select device
"""
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"


async def test_step7_select_device():
    """Test Step 7 complete flow - select device"""
    print("=" * 80)
    print("Step 7 Test - Select Device")
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
        
        # 2-6: Quick prerequisite steps
        print("\n[2-6] Running prerequisite steps...")
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
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={"session_id": renewal_session_id, "os_type": "ios"},
            headers=headers
        )
        print("OK Prerequisite steps completed")
        
        # 7. Step 7: Select device
        print("\n[7] Step 7: Select device...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            json={
                "session_id": renewal_session_id,
                "device_id": "DEV001",
                "color": "黑色"
            },
            headers=headers
        )
        if response.status_code != 200:
            print(f"ERROR Status: {response.status_code}")
            print(f"ERROR Response: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("device_id") == "DEV001"
        assert data.get("color") == "黑色"
        assert data.get("next_step") == "list_plans"
        print(f"OK Device selected: {data.get('device_id')}")
        print(f"OK Color: {data.get('color')}")
        print(f"OK Next step: {data.get('next_step')}")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 7 all tests passed!")
        print("=" * 80)


async def test_step7_without_color():
    """Test Step 7 - select device without color"""
    print("\n" + "=" * 80)
    print("Step 7 Test - Select Device Without Color")
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
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={"session_id": renewal_session_id, "os_type": "android"},
            headers=headers
        )
        
        # Test without color (should default to "預設")
        print("\n[Test] Select device without color...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            json={
                "session_id": renewal_session_id,
                "device_id": "DEV002"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("device_id") == "DEV002"
        assert data.get("color") == "預設"
        print(f"OK Device selected without color defaults to '預設'")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 7 without color test passed!")
        print("=" * 80)


async def test_step7_error_handling():
    """Test Step 7 - error handling"""
    print("\n" + "=" * 80)
    print("Step 7 Test - Error Handling")
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
        await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device-os",
            json={"session_id": renewal_session_id, "os_type": "ios"},
            headers=headers
        )
        
        # Test 1: Missing session_id
        print("\n[Test 1] Testing missing session_id...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            json={"device_id": "DEV001"},
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("success") is False
        print("OK Missing session_id correctly returns 400")
        
        # Test 2: Missing device_id
        print("\n[Test 2] Testing missing device_id...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            json={"session_id": renewal_session_id},
            headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("success") is False
        print("OK Missing device_id correctly returns 400")
        
        # Test 3: Invalid session_id
        print("\n[Test 3] Testing invalid session_id...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-device",
            json={
                "session_id": "invalid_session_12345",
                "device_id": "DEV001"
            },
            headers=headers
        )
        assert response.status_code == 404
        data = response.json()
        assert data.get("success") is False
        print("OK Invalid session_id correctly returns 404")
        
        print("\n" + "=" * 80)
        print("SUCCESS - Step 7 error handling all tests passed!")
        print("=" * 80)


async def main():
    """Run all tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 24 + "Step 7 - Select Device Test Suite" + " " * 20 + "|")
    print("+" + "=" * 78 + "+")
    
    try:
        # Test 1: Select device with color
        await test_step7_select_device()
        
        # Test 2: Select device without color
        await test_step7_without_color()
        
        # Test 3: Error handling
        await test_step7_error_handling()
        
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
