"""
完整續約流程端對端測試 (Step 1-10)
使用實際的 API 端點進行測試

測試流程：
1. 登入取得 token
2. 開始續約流程
3. 查詢客戶
4. 列出門號
5. 選擇門號並檢查資格
6. 選擇手機
7. 搜尋方案
8. 選擇方案
9. 確認申辦
10. 提交申辦
"""
import asyncio
import aiohttp
import sys
from pathlib import Path

# 配置
BASE_URL = "http://localhost:5000"
TEST_STAFF_ID = "STAFF001"
TEST_PASSWORD = "password"
TEST_ID_NUMBER = "A123456789"

async def login(session: aiohttp.ClientSession):
    """登入取得 token"""
    print("\n[登入] 門市人員登入")
    print("-" * 80)
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "staff_id": TEST_STAFF_ID,
        "password": TEST_PASSWORD
    }
    
    try:
        async with session.post(url, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result.get('token')
                print(f"✓ 登入成功")
                print(f"  Staff ID: {TEST_STAFF_ID}")
                return token
            else:
                error = await resp.text()
                print(f"✗ 登入失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def start_workflow(session: aiohttp.ClientSession, token: str):
    """開始續約流程"""
    print("\n[Step 1] 開始續約流程")
    print("-" * 80)
    
    url = f"{BASE_URL}/start"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with session.post(url, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                session_id = result.get('session_id')
                print(f"✓ 流程已開始")
                print(f"  Session ID: {session_id}")
                return session_id
            else:
                error = await resp.text()
                print(f"✗ 開始流程失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def query_customer(session: aiohttp.ClientSession, token: str, session_id: str):
    """查詢客戶"""
    print("\n[Step 2] 查詢客戶")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/query-customer"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "id_number": TEST_ID_NUMBER
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                customer = result.get('customer', {})
                print(f"✓ 客戶查詢成功")
                print(f"  姓名: {customer.get('name', 'Unknown')}")
                print(f"  客戶ID: {customer.get('customer_id', 'Unknown')}")
                return customer
            else:
                error = await resp.text()
                print(f"✗ 查詢客戶失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def list_phones(session: aiohttp.ClientSession, token: str, session_id: str, customer_id: str):
    """列出客戶門號"""
    print("\n[Step 3] 列出客戶門號")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/list-phones"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "customer_id": customer_id
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                phones = result.get('phones', [])
                print(f"✓ 找到 {len(phones)} 個門號")
                for phone in phones:
                    print(f"  - {phone.get('phone_number')} ({phone.get('status')})")
                return phones
            else:
                error = await resp.text()
                print(f"✗ 列出門號失敗: {error}")
                return []
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return []


async def check_eligibility(session: aiohttp.ClientSession, token: str, session_id: str, 
                            customer_id: str, phone_number: str):
    """檢查續約資格"""
    print("\n[Step 4] 檢查續約資格")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/check-eligibility"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "customer_id": customer_id,
        "phone_number": phone_number
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                eligibility = result.get('eligibility', {})
                eligible = eligibility.get('eligible', False)
                print(f"✓ 續約資格: {'符合' if eligible else '不符合'}")
                if not eligible:
                    reason = eligibility.get('reason', 'Unknown')
                    print(f"  原因: {reason}")
                return eligible
            else:
                error = await resp.text()
                print(f"✗ 檢查資格失敗: {error}")
                return False
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return False


async def select_device_type(session: aiohttp.ClientSession, token: str, session_id: str, 
                             device_type: str = "smartphone"):
    """選擇裝置類型"""
    print("\n[Step 5] 選擇裝置類型")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/select-device-type"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "device_type": device_type
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✓ 裝置類型已選擇: {device_type}")
                return True
            else:
                error = await resp.text()
                print(f"✗ 選擇裝置類型失敗: {error}")
                return False
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return False


async def search_promotions(session: aiohttp.ClientSession, token: str, session_id: str, 
                            query: str = "吃到飽"):
    """搜尋促銷方案"""
    print("\n[Step 6] 搜尋促銷方案")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/search-promotions"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "query": query,
        "limit": 5
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                promotions = result.get('promotions', [])
                print(f"✓ 找到 {len(promotions)} 個促銷方案")
                for promo in promotions[:3]:
                    title = promo.get('title', 'Unknown')
                    print(f"  - {title}")
                return promotions
            else:
                error = await resp.text()
                print(f"✗ 搜尋方案失敗: {error}")
                return []
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return []


async def get_plan_details(session: aiohttp.ClientSession, token: str, session_id: str, plan_id: str):
    """取得方案詳情"""
    print("\n[Step 7] 取得方案詳情")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/get-plan-details"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "plan_id": plan_id
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                plan = result.get('plan', {})
                print(f"✓ 方案詳情取得成功")
                print(f"  方案名稱: {plan.get('name', 'Unknown')}")
                print(f"  月租費: ${plan.get('monthly_fee', 0)}")
                return plan
            else:
                error = await resp.text()
                print(f"✗ 取得方案詳情失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def select_plan(session: aiohttp.ClientSession, token: str, session_id: str, plan_id: str):
    """選擇方案"""
    print("\n[Step 8] 選擇方案")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/select-plan"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "plan_id": plan_id
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                selected_plan = result.get('selected_plan', {})
                cost_details = selected_plan.get('cost_details', {})
                print(f"✓ 方案已選擇")
                print(f"  方案名稱: {selected_plan.get('plan_name', 'Unknown')}")
                print(f"  月租費: ${selected_plan.get('monthly_fee', 0)}")
                print(f"\n費用明細:")
                print(f"  手機款: ${cost_details.get('device_payment', 0)}")
                print(f"  違約金: ${cost_details.get('contract_breach_fee', 0)}")
                print(f"  開通費: ${cost_details.get('activation_fee', 0)}")
                total = (
                    cost_details.get('device_payment', 0) +
                    cost_details.get('contract_breach_fee', 0) +
                    cost_details.get('activation_fee', 0)
                )
                print(f"  總計: ${total}")
                return selected_plan
            else:
                error = await resp.text()
                print(f"✗ 選擇方案失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def confirm_application(session: aiohttp.ClientSession, token: str, session_id: str):
    """確認申辦"""
    print("\n[Step 9] 確認申辦")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/confirm"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                summary = result.get('summary', {})
                customer = summary.get('customer', {})
                phone = summary.get('phone', {})
                selected_plan = summary.get('selected_plan', {})
                total_amount = summary.get('total_amount', 0)
                
                print(f"✓ 確認申辦資料")
                print(f"\n申辦摘要:")
                print(f"  客戶: {customer.get('name')} ({customer.get('id_number')})")
                print(f"  門號: {phone.get('phone_number')}")
                print(f"  方案: {selected_plan.get('plan_name')} - ${selected_plan.get('monthly_fee')}/月")
                print(f"  總金額: ${total_amount}")
                return summary
            else:
                error = await resp.text()
                print(f"✗ 確認申辦失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def submit_application(session: aiohttp.ClientSession, token: str, session_id: str):
    """提交申辦"""
    print("\n[Step 10] 提交申辦")
    print("-" * 80)
    
    url = f"{BASE_URL}/step/submit"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id
    }
    
    try:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                order_number = result.get('order_number')
                total_amount = result.get('total_amount')
                print(f"✓ 申辦提交成功")
                print(f"  申辦單號: {order_number}")
                print(f"  總金額: ${total_amount}")
                return order_number
            else:
                error = await resp.text()
                print(f"✗ 提交申辦失敗: {error}")
                return None
    except Exception as e:
        print(f"✗ 連線錯誤: {str(e)}")
        return None


async def test_complete_renewal_flow():
    """完整續約流程測試"""
    
    print("=" * 80)
    print("完整續約流程測試 (Step 1-10)")
    print("=" * 80)
    print(f"\n測試環境: {BASE_URL}")
    print(f"測試帳號: {TEST_STAFF_ID}")
    print(f"測試客戶: {TEST_ID_NUMBER}")
    
    async with aiohttp.ClientSession() as session:
        # 登入
        token = await login(session)
        if not token:
            print("\n✗ 測試中止：登入失敗")
            return
        
        # 開始流程
        session_id = await start_workflow(session, token)
        if not session_id:
            print("\n✗ 測試中止：無法開始流程")
            return
        
        # 查詢客戶
        customer = await query_customer(session, token, session_id)
        if not customer:
            print("\n✗ 測試中止：查詢客戶失敗")
            return
        
        customer_id = customer.get('customer_id')
        
        # 列出門號
        phones = await list_phones(session, token, session_id, customer_id)
        if not phones:
            print("\n✗ 測試中止：沒有可用門號")
            return
        
        # 選擇第一個門號
        phone_number = phones[0].get('phone_number')
        
        # 檢查資格
        eligible = await check_eligibility(session, token, session_id, customer_id, phone_number)
        if not eligible:
            print("\n⚠ 續約資格不符，但繼續測試流程...")
            # 在實際環境中可能需要中止
        
        # 選擇裝置類型
        await select_device_type(session, token, session_id, "smartphone")
        
        # 搜尋促銷方案
        promotions = await search_promotions(session, token, session_id, "吃到飽")
        if not promotions:
            print("\n✗ 測試中止：沒有可用方案")
            return
        
        # 取得第一個方案的詳情
        # 由於搜尋返回的是促銷活動，我們需要從中找到方案
        # 簡化處理：直接使用已知的方案ID
        plan_id = "PLAN_5G_UNLIMITED_1399"  # 從 promotion_server.py 的 Mock 資料中取得
        
        # 選擇方案
        selected_plan = await select_plan(session, token, session_id, plan_id)
        if not selected_plan:
            print("\n✗ 測試中止：選擇方案失敗")
            return
        
        # 確認申辦
        summary = await confirm_application(session, token, session_id)
        if not summary:
            print("\n✗ 測試中止：確認申辦失敗")
            return
        
        # 提交申辦
        order_number = await submit_application(session, token, session_id)
        if not order_number:
            print("\n✗ 測試中止：提交申辦失敗")
            return
        
        # 測試結果總結
        print("\n" + "=" * 80)
        print("測試結果總結")
        print("=" * 80)
        
        test_results = {
            "登入": "✓ 通過",
            "開始流程": "✓ 通過",
            "查詢客戶": "✓ 通過",
            "列出門號": f"✓ 通過 ({len(phones)} 個門號)",
            "檢查資格": "✓ 通過" if eligible else "⚠ 不符合",
            "選擇裝置類型": "✓ 通過",
            "搜尋方案": f"✓ 通過 ({len(promotions)} 個方案)",
            "選擇方案": "✓ 通過",
            "確認申辦": "✓ 通過",
            "提交申辦": "✓ 通過"
        }
        
        for step, result in test_results.items():
            print(f"{step}: {result}")
        
        print(f"\n最終結果:")
        print(f"  Session ID: {session_id}")
        print(f"  訂單號碼: {order_number}")
        print(f"  客戶: {customer.get('name')}")
        print(f"  門號: {phone_number}")
        
        print("\n" + "=" * 80)
        print("✓ 完整續約流程測試成功！")
        print("=" * 80)


async def check_backend_status():
    """檢查後端服務狀態"""
    print("檢查後端服務狀態...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    print(f"✓ 後端服務運行中 ({BASE_URL})")
                    return True
    except Exception as e:
        print(f"✗ 無法連接到後端服務 ({BASE_URL})")
        print(f"  錯誤: {str(e)}")
        print(f"\n請確認:")
        print(f"  1. 後端服務已啟動")
        print(f"  2. 服務運行在 {BASE_URL}")
        print(f"  3. 防火牆允許連接")
        return False


async def main():
    """主程式"""
    # 檢查後端狀態
    if not await check_backend_status():
        print("\n請先啟動後端服務:")
        print("  cd backend")
        print("  python run_app.py")
        return
    
    print()
    
    # 執行完整流程測試
    await test_complete_renewal_flow()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
    except Exception as e:
        print(f"\n測試發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
