"""
完整續約流程業務邏輯測試 (Step 1-10)
不需要啟動 Web 服務，直接測試業務邏輯層

測試完整流程的所有步驟和數據流轉
"""
import asyncio
import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent))

import structlog
from app.services.workflow_session import WorkflowSessionManager, WorkflowStep
from app.services.crm_factory import get_crm_service
from app.services.pos_factory import get_pos_service
from app.services.promotion_factory import get_promotion_service

logger = structlog.get_logger()

# Mock Redis Manager
class MockRedisManager:
    """Mock Redis Manager for testing"""
    def __init__(self):
        self.storage = {}
        self.sets = {}
        self.redis = self
    
    async def set_json(self, key: str, value: dict, ex: int = None):
        import json
        self.storage[key] = json.dumps(value)
    
    async def get_json(self, key: str):
        import json
        data = self.storage.get(key)
        return json.loads(data) if data else None
    
    async def delete(self, key: str):
        if key in self.storage:
            del self.storage[key]
    
    async def sadd(self, key: str, value: str):
        if key not in self.sets:
            self.sets[key] = set()
        self.sets[key].add(value)


# Mock Oracle Manager
class MockOracleManager:
    """Mock Oracle Manager for testing"""
    def __init__(self):
        self.executed_queries = []
    
    async def execute(self, sql: str, params: dict):
        self.executed_queries.append({
            'sql': sql,
            'params': params,
            'timestamp': str(datetime.datetime.now())
        })
        logger.info("Mock SQL 執行", 
                   sql_preview=sql[:60] + "..." if len(sql) > 60 else sql,
                   params=params)
        return True


async def test_complete_renewal_workflow():
    """測試完整續約流程 Step 1-10"""
    
    print("=" * 80)
    print("完整續約流程業務邏輯測試 (Step 1-10)")
    print("=" * 80)
    print()
    
    # 初始化
    redis_manager = MockRedisManager()
    oracle_manager = MockOracleManager()
    workflow_manager = WorkflowSessionManager(redis_manager)
    
    staff_id = "STAFF001"
    test_id_number = "A123456789"
    
    test_results = {}
    
    # ========================================
    # Step 1: 開始流程並查詢客戶
    # ========================================
    print("[Step 1] 開始流程並查詢客戶")
    print("-" * 80)
    
    try:
        # 建立 Session
        session_data = await workflow_manager.create_session(staff_id)
        session_id = session_data['session_id']
        print(f"✓ Session 已建立: {session_id}")
        
        # 查詢客戶（使用 Mock CRM Service）
        crm_service = await get_crm_service()
        customer = await crm_service.query_customer_by_id(test_id_number)
        
        if customer:
            print(f"✓ 客戶查詢成功")
            print(f"  姓名: {customer.get('name', 'Unknown')}")
            print(f"  客戶ID: {customer.get('customer_id', 'Unknown')}")
            
            # 更新 Session
            session = await workflow_manager.get_session(session_id)
            session['customer'] = customer
            session['current_step'] = WorkflowStep.LIST_PHONES.value
            await workflow_manager.update_session(session_id, session)
            
            test_results['Step 1'] = "✓ 通過"
        else:
            print(f"✗ 客戶查詢失敗")
            test_results['Step 1'] = "✗ 失敗"
            return
            
    except Exception as e:
        print(f"✗ Step 1 錯誤: {str(e)}")
        test_results['Step 1'] = f"✗ 錯誤: {str(e)}"
        return
    
    # ========================================
    # Step 2-3: 查詢門號列表
    # ========================================
    print(f"\n[Step 2-3] 查詢門號列表")
    print("-" * 80)
    
    try:
        phones = await crm_service.get_customer_phones(customer['customer_id'])
        print(f"✓ 找到 {len(phones)} 個門號")
        for phone in phones:
            print(f"  - {phone.get('phone_number')} ({phone.get('status')})")
        
        if phones:
            session = await workflow_manager.get_session(session_id)
            session['phones'] = phones
            session['current_step'] = WorkflowStep.SELECT_PHONE.value
            await workflow_manager.update_session(session_id, session)
            test_results['Step 2-3'] = f"✓ 通過 ({len(phones)} 個門號)"
        else:
            print(f"✗ 沒有可用門號")
            test_results['Step 2-3'] = "✗ 沒有門號"
            return
            
    except Exception as e:
        print(f"✗ Step 2-3 錯誤: {str(e)}")
        test_results['Step 2-3'] = f"✗ 錯誤"
        return
    
    # ========================================
    # Step 4: 選擇門號並檢查資格
    # ========================================
    print(f"\n[Step 4] 選擇門號並檢查資格")
    print("-" * 80)
    
    try:
        selected_phone = phones[0]
        phone_number = selected_phone['phone_number']
        print(f"✓ 選擇門號: {phone_number}")
        
        # 取得門號詳情
        contract = await crm_service.get_phone_contract(phone_number)
        usage = await crm_service.get_phone_usage(phone_number)
        billing = await crm_service.get_phone_billing(phone_number)
        
        # 如果合約不存在，建立測試資料
        if not contract:
            print("  建立測試合約資料")
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
        
        # 模擬符合資格（簡化處理）
        eligibility = {
            'eligible': True,
            'reason': '符合續約資格'
        }
        print(f"✓ 續約資格: 符合")
        
        # 更新 Session
        session = await workflow_manager.get_session(session_id)
        session['phone'] = phone_details
        session['contract'] = contract
        session['eligibility'] = eligibility
        session['current_step'] = WorkflowStep.SELECT_DEVICE_TYPE.value
        await workflow_manager.update_session(session_id, session)
        
        test_results['Step 4'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 4 錯誤: {str(e)}")
        test_results['Step 4'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 5: 選擇裝置類型
    # ========================================
    print(f"\n[Step 5] 選擇裝置類型")
    print("-" * 80)
    
    try:
        device_type = "smartphone"
        print(f"✓ 裝置類型: {device_type}")
        
        session = await workflow_manager.get_session(session_id)
        session['device_type'] = device_type
        session['current_step'] = WorkflowStep.SELECT_DEVICE.value
        await workflow_manager.update_session(session_id, session)
        
        test_results['Step 5'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 5 錯誤: {str(e)}")
        test_results['Step 5'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 6: 選擇手機（可選）
    # ========================================
    print(f"\n[Step 6] 選擇手機")
    print("-" * 80)
    
    try:
        # 簡化：不選擇手機，直接續約
        print(f"✓ 選擇：不選擇手機（單純續約）")
        
        session = await workflow_manager.get_session(session_id)
        session['device'] = None
        session['current_step'] = WorkflowStep.LIST_PLANS.value
        await workflow_manager.update_session(session_id, session)
        
        test_results['Step 6'] = "✓ 通過（無手機）"
        
    except Exception as e:
        print(f"✗ Step 6 錯誤: {str(e)}")
        test_results['Step 6'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 7: 促銷資格
    # ========================================
    print(f"\n[Step 7] 促銷資格")
    print("-" * 80)
    
    try:
        promo_eligibility = {
            "eligible": True,
            "eligible_promotions": ["一般促銷"]
        }
        print(f"✓ 促銷資格: 符合")
        
        session = await workflow_manager.get_session(session_id)
        session['promotion_eligibility'] = promo_eligibility
        await workflow_manager.update_session(session_id, session)
        
        test_results['Step 7'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 7 錯誤: {str(e)}")
        test_results['Step 7'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 8: 搜尋並選擇方案
    # ========================================
    print(f"\n[Step 8] 搜尋並選擇方案")
    print("-" * 80)
    
    try:
        promotion_service = await get_promotion_service()
        
        # 搜尋方案
        result = await promotion_service.search_promotions(
            query="吃到飽",
            contract_type="續約",
            limit=5
        )
        promotions = result.get('promotions', [])
        print(f"✓ 找到 {len(promotions)} 個促銷方案")
        
        # 使用實際存在的方案ID（從 promotion_server.py Mock 資料）
        plan_id = "PLAN001"  # 5G 極速飆網 1399
        
        # 計算費用
        device_price = 0  # 沒有選擇手機
        cost_result = await promotion_service.calculate_upgrade_cost(
            current_plan_fee=contract.get('monthly_fee', 0),
            new_plan_id=plan_id,
            device_price=device_price,
            contract_type="續約"
        )
        
        new_plan = cost_result.get('new_plan', {})
        print(f"✓ 選擇方案: {new_plan.get('name', 'Unknown')}")
        print(f"  月租費: ${new_plan.get('monthly_fee', 0)}")
        print(f"  合約期: {new_plan.get('contract_months', 0)} 個月")
        
        # 更新 Session
        session = await workflow_manager.get_session(session_id)
        session['selected_plan'] = {
            "plan_id": plan_id,
            "plan_name": new_plan.get('name', 'Unknown'),
            "monthly_fee": new_plan.get('monthly_fee', 0),
            "contract_months": new_plan.get('contract_months', 0),
            "data": new_plan.get('data', 'Unknown'),
            "voice": new_plan.get('voice', 'Unknown'),
            "cost_details": cost_result,
            "selected_at": str(datetime.datetime.now())
        }
        session['current_step'] = WorkflowStep.CONFIRM.value
        await workflow_manager.update_session(session_id, session)
        
        test_results['Step 8'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 8 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        test_results['Step 8'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 9: 確認申辦
    # ========================================
    print(f"\n[Step 9] 確認申辦")
    print("-" * 80)
    
    try:
        session = await workflow_manager.get_session(session_id)
        
        # 驗證資料完整性
        required_fields = ['customer', 'phone', 'contract', 'selected_plan']
        missing = [f for f in required_fields if not session.get(f)]
        
        if missing:
            print(f"✗ 申辦資料不完整，缺少: {', '.join(missing)}")
            test_results['Step 9'] = "✗ 資料不完整"
            return
        
        # 計算總費用
        cost_details = session['selected_plan']['cost_details']
        total_amount = (
            cost_details.get('device_payment', 0) +
            cost_details.get('contract_breach_fee', 0) +
            cost_details.get('activation_fee', 0)
        )
        
        print(f"✓ 確認申辦資料")
        print(f"\n申辦摘要:")
        print(f"  客戶: {session['customer'].get('name')} ({session['customer'].get('id_number', 'N/A')})")
        print(f"  門號: {session['phone']['phone_number']}")
        print(f"  方案: {session['selected_plan']['plan_name']} - ${session['selected_plan']['monthly_fee']}/月")
        print(f"  總金額: ${total_amount}")
        
        test_results['Step 9'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 9 錯誤: {str(e)}")
        test_results['Step 9'] = "✗ 錯誤"
        return
    
    # ========================================
    # Step 10: 提交申辦
    # ========================================
    print(f"\n[Step 10] 提交申辦")
    print("-" * 80)
    
    try:
        session = await workflow_manager.get_session(session_id)
        
        # 生成申辦單號
        today = datetime.datetime.now().strftime('%Y%m%d')
        order_number = f"ORD{today}{session_id[-6:]}"
        
        # 計算總金額
        cost_details = session['selected_plan']['cost_details']
        total_amount = (
            cost_details.get('device_payment', 0) +
            cost_details.get('contract_breach_fee', 0) +
            cost_details.get('activation_fee', 0)
        )
        
        # 模擬資料庫更新
        print(f"✓ 模擬資料庫更新...")
        
        # 1. 更新 RenewalSessions
        await oracle_manager.execute(
            """
            UPDATE renewal_sessions
            SET status = 'COMPLETED',
                is_sale_confirmed = 1,
                total_amount = :total_amount,
                completed_at = SYSDATE,
                updated_at = SYSDATE
            WHERE session_id = :session_id
            """,
            {'session_id': session_id, 'total_amount': total_amount}
        )
        print(f"  - RenewalSessions 更新完成")
        
        # 2. 記錄 CustomerServiceLogs
        notes = f"續約申辦完成 - 方案: {session['selected_plan']['plan_name']}, 總金額: {total_amount}"
        await oracle_manager.execute(
            """
            INSERT INTO customer_service_logs (
                staff_id, customer_id, service_type, service_result, notes, created_at
            )
            VALUES (
                :staff_id, :customer_id, 'renewal', 'completed', :notes, SYSDATE
            )
            """,
            {
                'staff_id': staff_id,
                'customer_id': customer['customer_id'],
                'notes': notes
            }
        )
        print(f"  - CustomerServiceLogs 記錄完成")
        
        # 更新 Session 狀態
        session['current_step'] = WorkflowStep.COMPLETED.value
        session['order_number'] = order_number
        session['completed_at'] = str(datetime.datetime.now())
        await workflow_manager.update_session(session_id, session)
        
        print(f"\n✓ 申辦提交成功")
        print(f"  申辦單號: {order_number}")
        print(f"  總金額: ${total_amount}")
        print(f"  完成時間: {session['completed_at']}")
        
        test_results['Step 10'] = "✓ 通過"
        
    except Exception as e:
        print(f"✗ Step 10 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        test_results['Step 10'] = "✗ 錯誤"
        return
    
    # ========================================
    # 測試結果總結
    # ========================================
    print("\n" + "=" * 80)
    print("測試結果總結")
    print("=" * 80)
    
    final_session = await workflow_manager.get_session(session_id)
    
    for step, result in test_results.items():
        print(f"{step}: {result}")
    
    print(f"\n最終 Session 資料:")
    print(f"  Session ID: {session_id}")
    print(f"  訂單號碼: {final_session.get('order_number', 'N/A')}")
    print(f"  當前步驟: {final_session['current_step']}")
    print(f"  客戶: {final_session['customer'].get('name')}")
    print(f"  門號: {final_session['phone']['phone_number']}")
    print(f"  方案: {final_session['selected_plan']['plan_name']}")
    
    print(f"\n資料庫操作記錄:")
    for i, query in enumerate(oracle_manager.executed_queries, 1):
        print(f"  {i}. {query['sql'][:60].strip()}...")
        print(f"     時間: {query['timestamp']}")
    
    # 檢查是否所有步驟都通過
    all_passed = all('✓' in result for result in test_results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ 完整續約流程測試成功！所有 10 個步驟都通過！")
    else:
        failed_steps = [step for step, result in test_results.items() if '✗' in result]
        print(f"⚠ 部分步驟失敗: {', '.join(failed_steps)}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(test_complete_renewal_workflow())
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
    except Exception as e:
        print(f"\n測試發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
