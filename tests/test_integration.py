"""
電信門市銷售助理系統 - 整合測試
測試前端與後端的基本通信
"""
import asyncio
import aiohttp
import json

async def test_backend_health():
    """測試後端健康檢查"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 後端健康檢查: 通過")
                    print(f"   狀態: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ 後端健康檢查: 失敗 (狀態碼: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ 後端健康檢查: 連線失敗 - {e}")
        return False

async def test_auth_endpoints():
    """測試認證端點"""
    try:
        async with aiohttp.ClientSession() as session:
            # 測試登入端點
            async with session.post('http://localhost:8000/api/auth/login', 
                                   json={'staff_code': 'test', 'password': 'test'}) as response:
                print(f"✅ 認證端點: 可訪問 (狀態碼: {response.status})")
                return True
    except Exception as e:
        print(f"❌ 認證端點: 連線失敗 - {e}")
        return False

async def test_frontend():
    """測試前端首頁"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000') as response:
                if response.status == 200:
                    print("✅ 前端首頁: 可訪問")
                    return True
                else:
                    print(f"❌ 前端首頁: 無法訪問 (狀態碼: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ 前端首頁: 連線失敗 - {e}")
        return False

async def main():
    """主測試函數"""
    print("=" * 50)
    print("電信門市銷售助理系統 - 整合測試")
    print("=" * 50)
    print()
    
    # 測試後端
    print("[1] 測試後端服務...")
    backend_health = await test_backend_health()
    backend_auth = await test_auth_endpoints()
    
    print()
    print("[2] 測試前端服務...")
    frontend_ok = await test_frontend()
    
    print()
    print("=" * 50)
    print("測試結果摘要:")
    print("=" * 50)
    print(f"後端健康檢查: {'✅ 通過' if backend_health else '❌ 失敗'}")
    print(f"後端認證端點: {'✅ 通過' if backend_auth else '❌ 失敗'}")
    print(f"前端首頁: {'✅ 通過' if frontend_ok else '❌ 失敗'}")
    
    if backend_health and backend_auth and frontend_ok:
        print("\n🎉 所有測試通過！系統準備就緒。")
        print("\n開發資訊:")
        print("- 前端: http://localhost:3000")
        print("- 後端: http://localhost:8000")
        print("- 後端API文檔: http://localhost:8000/docs (如果有的話)")
    else:
        print("\n⚠️ 部分測試失敗，請檢查服務狀態。")

if __name__ == "__main__":
    asyncio.run(main())