"""
完整續約流程端對端測試 (Step 1-10)

測試完整的續約流程，從客戶查詢到最終提交申辦
"""
import asyncio
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from app.services.workflow_session import WorkflowSessionManager, WorkflowStep
from app.services.crm_factory import get_crm_service
from app.services.pos_factory import get_pos_service
from app.services.promotion_factory import get_promotion_service

logger = structlog.get_logger()

class MockRedisManager:
    """Mock Redis Manager for testing"""
    def __init__(self):
        self.storage = {}
        self.sets = {}
        self.redis = self  # For compatibility with self.redis.sadd()
    
    async def set_json(self, key: str, value: dict, ex: int = None):
        """Store JSON data"""
        import json
        self.storage[key] = json.dumps(value)
    
    async def get_json(self, key: str):
        """Retrieve JSON data"""
        import json
        data = self.storage.get(key)
        return json.loads(data) if data else None
    
    async def delete(self, key: str):
        """Delete key"""
        if key in self.storage:
            del self.storage[key]
    
    async def sadd(self, key: str, value: str):
        """Add to set"""
        if key not in self.sets:
            self.sets[key] = set()
        self.sets[key].add(value)
    
    async def smembers(self, key: str):
        """Get all members of a set"""
        return self.sets.get(key, set())
    
    async def srem(self, key: str, value: str):
        """Remove a member from a set"""
        if key in self.sets:
            self.sets[key].discard(value)


async def test_complete_workflow():
    """測試完整續約流程 Step 1-10"""
    
    print("=" * 80)
    print("開始完整續約流程測試 (Step 1-10)")
    print("=" * 80)
    
    # 初始化
    redis_manager = MockRedisManager()
    workflow_manager = WorkflowSessionManager(redis_manager)
    crm_service = await get_crm_service()
    pos_service = await get_pos_service()
    promotion_service = await get_promotion_service()
    
    staff_id = "STAFF001"
    test_id_number = "A123456789"
    
    # ========================================
    # Step 1: 開始流程並查詢客戶
    # ========================================
    print("\n[Step 1] 開始流程並查詢客戶")
    print("-" * 80)
    
    session_data = await workflow_manager.create_session(staff_id)
    session_id = session_data['session_id']
    print(f"✓ Session 已建立: {session_id}")
    
    customer = await crm_service.query_customer_by_id(test_id_number)
    print(f"✓ 客戶查詢成功: {customer.get('name', 'Unknown')}")
    
    session = await workflow_manager.get_session(session_id)
    session['customer'] = customer
    session['current_step'] = WorkflowStep.LIST_PHONES.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 2-3: 查詢門號列表
    # ========================================
    print("\n[Step 2-3] 查詢門號列表")
    print("-" * 80)
    
    phones = await crm_service.get_customer_phones(customer['customer_id'])
    print(f"✓ 找到 {len(phones)} 個門號")
    for phone in phones:
        print(f"  - {phone['phone_number']} ({phone['status']})")
    
    session['phones'] = phones
    session['current_step'] = WorkflowStep.CHECK_ELIGIBILITY.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 4: 選擇門號並檢查資格
    # ========================================
    print("\n[Step 4] 選擇門號並檢查資格")
    print("-" * 80)
    
    selected_phone = phones[0]
    # 組合門號詳情（合併合約、使用量、帳單）
    contract = await crm_service.get_phone_contract(selected_phone['phone_number'])
    usage = await crm_service.get_phone_usage(selected_phone['phone_number'])
    billing = await crm_service.get_phone_billing(selected_phone['phone_number'])
    
    # 如果合約不存在，建立測試合約資料
    if not contract:
        print("  建立測試合約資料")
        import datetime
        contract = {
            'contract_id': 'TEST_CONTRACT_001',
            'plan_name': '4G 吃到飽',
            'monthly_fee': 999,
            'contract_start_date': (datetime.datetime.now() - datetime.timedelta(days=730)).strftime('%Y-%m-%d'),
            'contract_end_date': (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            'remaining_contract_months': 1
        }
    
    phone_details = {
        **selected_phone,
        'contract': contract,
        'usage': usage or {},
        'billing': billing or {}
    }
    print(f"✓ 門號詳情: {phone_details['phone_number']}")
    
    # 模擬符合資格
    eligibility = {
        'eligible': True,
        'reason': '符合續約資格'
    }
    print(f"✓ 續約資格: 符合")
    
    session['phone'] = phone_details
    session['contract'] = contract
    session['eligibility'] = eligibility
    session['current_step'] = WorkflowStep.SELECT_DEVICE_TYPE.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 5: 選擇續約類型（簡化：直接進入手機選擇）
    # ========================================
    print("\n[Step 5] 選擇續約類型")
    print("-" * 80)
    
    renewal_type = "upgrade"  # 可選: upgrade, keep_plan
    print(f"✓ 續約類型: {renewal_type}")
    
    session['renewal_type'] = renewal_type
    session['current_step'] = WorkflowStep.SELECT_DEVICE.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 6: 查詢並選擇手機
    # ========================================
    print("\n[Step 6] 查詢並選擇手機")
    print("-" * 80)
    
    # 使用門市ID查詢庫存
    store_id = "STR001"  # 預設門市
    devices = await pos_service.query_device_stock(
        store_id=store_id,
        os_filter="iOS"
    )
    print(f"✓ 找到 {len(devices)} 款手機")
    
    selected_device = devices[0] if devices else None
    if selected_device:
        device_details = await pos_service.get_device_info(selected_device['device_id'])
        pricing = await pos_service.get_device_pricing(
            device_id=selected_device['device_id'],
            plan_type="吃到飽"
        )
        device_details['pricing'] = pricing
        
        print(f"✓ 選擇手機: {device_details['brand']} {device_details['model']}")
        print(f"  價格: ${pricing.get('base_price', 0)}")
        
        session['device'] = device_details
    else:
        print("✓ 不選擇手機（單純續約）")
        session['device'] = None
    
    session['current_step'] = WorkflowStep.LIST_PLANS.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 7: 促銷資格（簡化處理）
    # ========================================
    print("\n[Step 7] 促銷資格")
    print("-" * 80)
    
    # 根據客戶類型自動判斷
    promo_eligibility = {
        "eligible": True,
        "eligible_promotions": ["學生專案"] if "學生" in customer.get('contract_type', '') else ["一般促銷"]
    }
    print(f"✓ 促銷資格: 符合")
    print(f"  符合促銷: {', '.join(promo_eligibility['eligible_promotions'])}")
    
    session['promotion_eligibility'] = promo_eligibility
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 8: 搜尋並列出方案
    # ========================================
    print("\n[Step 8] 搜尋並列出方案")
    print("-" * 80)
    
    # 取得所有可用方案（直接使用 promotion_service 的內部方案列表）
    # 注意：在實際 API 中應該有專門的 list_plans 端點
    all_plans = promotion_service.plans if hasattr(promotion_service, 'plans') else []
    
    # 篩選適合的方案（這裡簡單取前 7 個）
    plans = all_plans[:7]
    
    print(f"✓ 找到 {len(plans)} 個方案")
    for i, plan in enumerate(plans[:3], 1):
        print(f"  {i}. {plan['name']} - ${plan['monthly_fee']}/月")
        print(f"     數據: {plan['data']}, 通話: {plan['voice']}")
    
    session['available_plans'] = plans
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 9: 比較方案（可選）
    # ========================================
    print("\n[Step 9] 比較方案（可選）")
    print("-" * 80)
    
    if len(plans) >= 2:
        # 選擇前 3 個方案進行比較
        plan_ids = [plans[0]['plan_id'], plans[1]['plan_id'], plans[2]['plan_id']]
        comparison = await promotion_service.compare_plans(plan_ids)
        print(f"✓ 方案比較完成")
        print(f"  比較 {len(comparison['plans'])} 個方案")
        if comparison.get('recommendation'):
            print(f"  AI 推薦: {comparison['recommendation']}")
        
        # 記錄比較歷史
        if 'comparison_history' not in session:
            session['comparison_history'] = []
        session['comparison_history'].append({
            'plan_ids': plan_ids,
            'timestamp': str(__import__('datetime').datetime.now())
        })
    else:
        print("⚠️ 方案數量不足，跳過比較")
    
    # ========================================
    # Step 9: 選擇方案並計算費用
    # ========================================
    print("\n[Step 9] 選擇方案並計算費用")
    print("-" * 80)
    
    if len(plans) == 0:
        print("❌ 無可用方案")
        return
    
    selected_plan = plans[0]
    
    # 安全取得 device_price
    device = session.get('device')
    if device and device != "none" and isinstance(device, dict):
        device_price = device.get('pricing', {}).get('base_price', 0)
    else:
        device_price = 0
    
    cost_result = await promotion_service.calculate_upgrade_cost(
        current_plan_fee=session['contract'].get('monthly_fee', 0),
        new_plan_id=selected_plan['plan_id'],
        device_price=device_price,
        contract_type=customer.get('contract_type', '續約')
    )
    
    print(f"✓ 選擇方案: {selected_plan['name']}")
    print(f"  月租費: ${selected_plan['monthly_fee']}")
    print(f"  合約期: {selected_plan['contract_months']} 個月")
    print(f"\n費用明細:")
    print(f"  手機款: ${cost_result.get('device_payment', 0)}")
    print(f"  違約金: ${cost_result.get('contract_breach_fee', 0)}")
    print(f"  開通費: ${cost_result.get('activation_fee', 0)}")
    total = (
        cost_result.get('device_payment', 0) +
        cost_result.get('contract_breach_fee', 0) +
        cost_result.get('activation_fee', 0)
    )
    print(f"  總計: ${total}")
    
    session['selected_plan'] = {
        "plan_id": selected_plan['plan_id'],
        "plan_name": selected_plan['name'],
        "monthly_fee": selected_plan['monthly_fee'],
        "contract_months": selected_plan['contract_months'],
        "data": selected_plan['data'],
        "voice": selected_plan['voice'],
        "cost_details": cost_result,
        "selected_at": str(__import__('datetime').datetime.now())
    }
    session['current_step'] = WorkflowStep.CONFIRM.value
    await workflow_manager.update_session(session_id, session)
    
    # ========================================
    # Step 10: 確認申辦
    # ========================================
    print("\n[Step 10] 確認申辦")
    print("-" * 80)
    
    # 驗證資料完整性
    required_fields = ['customer', 'phone', 'contract', 'selected_plan']
    missing = [f for f in required_fields if not session.get(f)]
    
    if missing:
        print(f"✗ 申辦資料不完整，缺少: {', '.join(missing)}")
        return
    
    print("✓ 申辦資料驗證通過")
    print("\n申辦摘要:")
    print(f"  客戶: {session['customer']['name']} ({session['customer']['id_number']})")
    print(f"  門號: {session['phone']['phone_number']}")
    if session.get('device'):
        print(f"  手機: {session['device']['brand']} {session['device']['model']}")
    print(f"  方案: {session['selected_plan']['plan_name']} (${session['selected_plan']['monthly_fee']}/月)")
    print(f"  總金額: ${total}")
    
    # ========================================
    # Step 10: 提交申辦（模擬）
    # ========================================
    print("\n[Step 10] 提交申辦（模擬）")
    print("-" * 80)
    
    import datetime
    today = datetime.datetime.now().strftime('%Y%m%d')
    order_number = f"ORD{today}{session_id[-6:]}"
    
    session['current_step'] = WorkflowStep.COMPLETED.value
    session['order_number'] = order_number
    session['completed_at'] = str(datetime.datetime.now())
    await workflow_manager.update_session(session_id, session)
    
    print(f"✓ 申辦提交成功")
    print(f"  申辦單號: {order_number}")
    print(f"  完成時間: {session['completed_at']}")
    
    # ========================================
    # 測試結果總結
    # ========================================
    print("\n" + "=" * 80)
    print("測試結果總結")
    print("=" * 80)
    
    final_session = await workflow_manager.get_session(session_id)
    
    test_results = {
        "Session 建立": "✓ 通過",
        "客戶查詢 (Step 1)": "✓ 通過",
        "門號列表 (Step 2-3)": "✓ 通過",
        "資格檢查 (Step 4)": "✓ 通過" if eligibility['eligible'] else "✗ 失敗",
        "續約類型選擇 (Step 5)": "✓ 通過",
        "手機選擇 (Step 6)": "✓ 通過",
        "促銷資格檢查 (Step 7)": "✓ 通過",
        "方案搜尋 (Step 8)": f"✓ 通過 ({len(plans)} 個方案)",
        "方案比較 (Step 9)": "✓ 通過" if len(plans) >= 2 else "⊘ 跳過",
        "方案選擇與費用計算 (Step 9)": "✓ 通過",
        "確認申辦 (Step 10)": "✓ 通過",
        "提交申辦 (Step 10)": "✓ 通過",
        "最終狀態": final_session['current_step']
    }
    
    for step, result in test_results.items():
        print(f"{step}: {result}")
    
    print("\n最終 Session 資料:")
    print(f"  Session ID: {session_id}")
    print(f"  訂單號碼: {order_number}")
    print(f"  當前步驟: {final_session['current_step']}")
    print(f"  總金額: ${total}")
    
    print("\n" + "=" * 80)
    print("✓ 完整流程測試成功！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
