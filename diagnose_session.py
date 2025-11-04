"""
Sprint 7 AI Chat 問題診斷腳本

用於診斷 "Session 不存在" 錯誤
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from app.services.redis_manager import RedisManager

async def diagnose():
    """診斷 Session 問題"""
    print("=" * 80)
    print(" Sprint 7 AI Chat - Session 診斷工具")
    print("=" * 80)
    
    # 初始化 Redis
    redis_manager = RedisManager()
    await redis_manager.initialize("redis://localhost:6379")
    
    print("\n1. 檢查認證 Session")
    print("-" * 80)
    auth_session_id = input("請輸入認證 Session ID (session_S001_...): ").strip()
    
    if auth_session_id:
        session_key = f"session:{auth_session_id}"
        auth_data = await redis_manager.get_json(session_key)
        
        if auth_data:
            print(f"✓ 認證 Session 存在")
            print(f"  - Staff ID: {auth_data.get('staff_id')}")
            print(f"  - Staff Code: {auth_data.get('staff_code')}")
            print(f"  - Name: {auth_data.get('name')}")
            print(f"  - Expire Time: {auth_data.get('expire_time')}")
        else:
            print(f"✗ 認證 Session 不存在或已過期")
            print(f"  請先登入系統")
            await redis_manager.close()
            return
    else:
        print("跳過認證 Session 檢查")
    
    print("\n2. 檢查續約流程 Session")
    print("-" * 80)
    renewal_session_id = input("請輸入續約 Session ID (renewal_STAFF001_...): ").strip()
    renewal_session_key = f"renewal_session_id:{renewal_session_id}"
    if renewal_session_id:
        # 檢查續約 Session
        renewal_data = await redis_manager.get_json(renewal_session_key)
        
        if renewal_data:
            print(f"✓ 續約 Session 存在")
            print(f"  - Session ID: {renewal_data.get('renewal_session_id')}")
            print(f"  - Staff ID: {renewal_data.get('staff_id')}")
            print(f"  - Current Step: {renewal_data.get('current_step')}")
            print(f"  - Customer: {renewal_data.get('customer', {}).get('name', 'N/A')}")
            print(f"  - Phone: {renewal_data.get('phone', {}).get('phone_number', 'N/A')}")
            
            # 檢查是否可以使用 AI
            current_step = renewal_data.get('current_step')
            allowed_steps = [
                'select_device_type',
                'select_device_os', 
                'select_device',
                'list_plans',
                'compare_plans',
                'confirm'
            ]
            
            if current_step in allowed_steps:
                print(f"\n  ✓ 當前步驟 '{current_step}' 允許使用 AI 對話")
            else:
                print(f"\n  ✗ 當前步驟 '{current_step}' 不允許使用 AI 對話")
                print(f"  允許的步驟: {', '.join(allowed_steps)}")
                print(f"  請先完成前面的步驟（至少到 Step 5: 選擇裝置類型）")
            
            # 檢查 staff_id 是否匹配
            if auth_data and renewal_data.get('staff_id') != auth_data.get('staff_id'):
                print(f"\n  ⚠ 警告: Session 的 staff_id 不匹配")
                print(f"    認證 Session: {auth_data.get('staff_id')}")
                print(f"    續約 Session: {renewal_data.get('staff_id')}")
        else:
            print(f"✗ 續約 Session 不存在")
            print(f"\n可能的原因:")
            print(f"  1. Session 已過期（預設 8 小時）")
            print(f"  2. Session ID 不正確")
            print(f"  3. 尚未開始續約流程")
            print(f"\n解決方案:")
            print(f"  - 呼叫 POST /api/renewal-workflow/start 開始新的續約流程")
            print(f"  - 檢查 Redis 中的 Key（使用 redis-cli KEYS 'renewal_*'）")
    else:
        print("跳過續約 Session 檢查")
    
    print("\n3. 列出所有續約 Session")
    print("-" * 80)
    
    # 使用 Redis SCAN 列出所有 renewal_ 開頭的 key
    import redis.asyncio as redis
    redis_client = redis.from_url("redis://localhost:6379")
    
    cursor = 0
    renewal_sessions = []
    
    while True:
        cursor, keys = await redis_client.scan(cursor, match='renewal_*', count=100)
        renewal_sessions.extend([k.decode() for k in keys])
        if cursor == 0:
            break
    
    await redis_client.close()
    
    if renewal_sessions:
        print(f"找到 {len(renewal_sessions)} 個續約 Session:")
        for i, session_id in enumerate(renewal_sessions[:10], 1):  # 只顯示前 10 個
            session_data = await redis_manager.get_json(session_id)
            if session_data:
                staff_id = session_data.get('staff_id', 'N/A')
                step = session_data.get('current_step', 'N/A')
                print(f"  {i}. {session_id}")
                print(f"     Staff: {staff_id}, Step: {step}")
        
        if len(renewal_sessions) > 10:
            print(f"  ... 還有 {len(renewal_sessions) - 10} 個 Session")
    else:
        print("✗ 沒有找到任何續約 Session")
        print("\n請先開始續約流程:")
        print("  POST /api/renewal-workflow/start")
        print("  Body: {}")
    
    # 關閉 Redis 連線
    await redis_manager.close()
    
    print("\n" + "=" * 80)
    print(" 診斷完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(diagnose())
