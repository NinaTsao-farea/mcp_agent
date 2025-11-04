"""
測試前端使用的 API 是否正常工作
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_login():
    """測試登入"""
    print("\n=== 測試登入 ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "staff_code": "S001",
                "password": "password"
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200 and data.get("success"):
            session_id = data.get("session_id")
            print(f"✅ 登入成功，Session ID: {session_id}")
            return session_id
        else:
            print(f"❌ 登入失敗")
            return None

async def test_start_workflow(session_id):
    """測試開始續約流程"""
    print("\n=== 測試開始續約流程 ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers={"X-Session-ID": session_id}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200 and data.get("success"):
            renewal_session_id = data.get("session_id")
            print(f"✅ 開始流程成功，Renewal Session ID: {renewal_session_id}")
            return renewal_session_id
        else:
            print(f"❌ 開始流程失敗")
            return None

async def test_query_customer(session_id, renewal_session_id):
    """測試查詢客戶"""
    print("\n=== 測試查詢客戶 ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers={"X-Session-ID": session_id},
            json={
                "session_id": renewal_session_id,
                "id_number": "A123456789"
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200 and data.get("success"):
            customer = data.get("customer")
            print(f"✅ 查詢客戶成功")
            print(f"   客戶姓名: {customer.get('name')}")
            print(f"   客戶ID: {customer.get('customer_id')}")
            return True
        else:
            print(f"❌ 查詢客戶失敗")
            return False

async def test_list_phones(session_id, renewal_session_id):
    """測試列出門號"""
    print("\n=== 測試列出門號 ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            headers={"X-Session-ID": session_id},
            json={"session_id": renewal_session_id}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200 and data.get("success"):
            phones = data.get("phones", [])
            print(f"✅ 列出門號成功，共 {len(phones)} 個門號")
            for phone in phones:
                print(f"   - {phone.get('phone_number')} ({phone.get('status')})")
            return True
        else:
            print(f"❌ 列出門號失敗")
            return False

async def test_select_phone(session_id, renewal_session_id):
    """測試選擇門號並檢查資格"""
    print("\n=== 測試選擇門號並檢查資格 ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers={"X-Session-ID": session_id},
            json={
                "session_id": renewal_session_id,
                "phone_number": "0912345678"
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200 and data.get("success"):
            eligibility = data.get("eligibility")
            print(f"✅ 選擇門號成功")
            print(f"   續約資格: {'符合' if eligibility.get('eligible') else '不符合'}")
            print(f"   原因: {eligibility.get('reason')}")
            return True
        else:
            print(f"❌ 選擇門號失敗")
            return False

async def main():
    """主測試流程"""
    print("=" * 60)
    print("前端 API 測試")
    print("=" * 60)
    
    # 1. 登入
    session_id = await test_login()
    if not session_id:
        print("\n❌ 測試終止：登入失敗")
        return
    
    # 2. 開始續約流程
    renewal_session_id = await test_start_workflow(session_id)
    if not renewal_session_id:
        print("\n❌ 測試終止：開始流程失敗")
        return
    
    # 3. 查詢客戶
    if not await test_query_customer(session_id, renewal_session_id):
        print("\n❌ 測試終止：查詢客戶失敗")
        return
    
    # 4. 列出門號
    if not await test_list_phones(session_id, renewal_session_id):
        print("\n❌ 測試終止：列出門號失敗")
        return
    
    # 5. 選擇門號並檢查資格
    if not await test_select_phone(session_id, renewal_session_id):
        print("\n❌ 測試終止：選擇門號失敗")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有測試通過！前端可以正常使用這些 API")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
