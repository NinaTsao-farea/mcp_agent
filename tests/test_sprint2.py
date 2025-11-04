"""
Sprint 2 快速測試腳本
測試續約流程 Step 1-4 的 API
"""
import asyncio
import json
from typing import Dict, Any


# 模擬測試資料
TEST_CASES = {
    "成功案例 - 符合續約資格": {
        "id_number": "A123456789",
        "expected_customer": "張三",
        "expected_phones_count": 2,
        "select_phone": "0912-345-678",
        "expected_eligible": True
    },
    "失敗案例 - 未到期門號": {
        "id_number": "A123456789",
        "expected_customer": "張三",
        "expected_phones_count": 2,
        "select_phone": "0987-654-321",
        "expected_eligible": False
    },
    "失敗案例 - 有欠費": {
        "id_number": "B987654321",
        "expected_customer": "李四",
        "expected_phones_count": 1,
        "select_phone": "0988-123-456",
        "expected_eligible": False
    },
    "失敗案例 - 非本公司客戶": {
        "id_number": "C111222333",
        "expected_error": "非本公司客戶"
    }
}


def print_header(title: str):
    """列印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step: str):
    """列印步驟"""
    print(f"\n📋 {step}")
    print("-" * 80)


def print_result(success: bool, message: str):
    """列印結果"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def print_json(data: Dict[Any, Any], indent: int = 2):
    """漂亮列印 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=indent))


async def test_workflow_api():
    """測試工作流程 API（僅展示測試流程）"""
    
    print_header("Sprint 2 續約流程測試")
    
    print("📝 測試說明：")
    print("本腳本展示如何測試續約流程的 API")
    print("實際測試需要後端服務運行在 http://localhost:5000")
    print("\n請確保：")
    print("1. 後端服務已啟動（python backend/run_app.py）")
    print("2. Redis 服務已運行")
    print("3. 已使用測試帳號登入（staff001 / password123）")
    
    print_header("測試案例")
    
    for case_name, case_data in TEST_CASES.items():
        print_step(case_name)
        print(f"身分證號：{case_data['id_number']}")
        
        if 'expected_error' in case_data:
            print(f"預期結果：應該返回錯誤 - {case_data['expected_error']}")
        else:
            print(f"預期客戶：{case_data['expected_customer']}")
            print(f"預期門號數量：{case_data['expected_phones_count']}")
            print(f"選擇門號：{case_data['select_phone']}")
            print(f"預期資格檢查：{'通過' if case_data['expected_eligible'] else '不通過'}")
        
        print()
    
    print_header("測試流程")
    
    print("📌 Step 1: 開始工作流程")
    print("POST /api/renewal-workflow/start")
    print("預期：取得 session_id")
    print()
    
    print("📌 Step 2: 查詢客戶")
    print("POST /api/renewal-workflow/step/query-customer")
    print("Body: { session_id, id_number }")
    print("預期：取得客戶資料")
    print()
    
    print("📌 Step 3: 列出門號")
    print("POST /api/renewal-workflow/step/list-phones")
    print("Body: { session_id }")
    print("預期：取得門號列表（含合約、使用量、帳單資訊）")
    print()
    
    print("📌 Step 4: 選擇門號")
    print("POST /api/renewal-workflow/step/select-phone")
    print("Body: { session_id, phone_number }")
    print("預期：取得資格檢查結果")
    print()
    
    print_header("使用 curl 測試範例")
    
    print("1️⃣ 開始工作流程（需要先登入取得 Session Cookie）")
    print("""
curl -X POST http://localhost:5000/api/renewal-workflow/start \\
  -H "Content-Type: application/json" \\
  -b "session_id=YOUR_AUTH_SESSION_ID"
""")
    
    print("\n2️⃣ 查詢客戶")
    print("""
curl -X POST http://localhost:5000/api/renewal-workflow/step/query-customer \\
  -H "Content-Type: application/json" \\
  -b "session_id=YOUR_AUTH_SESSION_ID" \\
  -d '{
    "session_id": "RENEWAL_SESSION_ID",
    "id_number": "A123456789"
  }'
""")
    
    print("\n3️⃣ 列出門號")
    print("""
curl -X POST http://localhost:5000/api/renewal-workflow/step/list-phones \\
  -H "Content-Type: application/json" \\
  -b "session_id=YOUR_AUTH_SESSION_ID" \\
  -d '{
    "session_id": "RENEWAL_SESSION_ID"
  }'
""")
    
    print("\n4️⃣ 選擇門號並檢查資格")
    print("""
curl -X POST http://localhost:5000/api/renewal-workflow/step/select-phone \\
  -H "Content-Type: application/json" \\
  -b "session_id=YOUR_AUTH_SESSION_ID" \\
  -d '{
    "session_id": "RENEWAL_SESSION_ID",
    "phone_number": "0912-345-678"
  }'
""")
    
    print_header("前端測試步驟")
    
    print("1. 啟動前端服務：cd frontend && pnpm run dev")
    print("2. 開啟瀏覽器：http://localhost:3000")
    print("3. 登入系統：staff001 / password123")
    print("4. 點擊「開始續約」")
    print("5. 輸入測試身分證號：A123456789")
    print("6. 查看門號列表")
    print("7. 選擇門號：0912-345-678")
    print("8. 查看資格檢查結果")
    print("\n更多測試場景請參考：docs/sprint2-testing-guide.md")
    
    print_header("檢查清單")
    
    checklist = [
        "[ ] 後端服務正常運行（http://localhost:5000/health 回傳 healthy）",
        "[ ] Redis 服務正常運行",
        "[ ] 前端服務正常運行（http://localhost:3000）",
        "[ ] 可以成功登入",
        "[ ] 可以開始續約流程",
        "[ ] 可以查詢客戶（A123456789）",
        "[ ] 可以顯示門號列表（2個門號）",
        "[ ] 可以選擇門號（0912-345-678）",
        "[ ] 可以顯示資格檢查結果（通過）",
        "[ ] 可以選擇未到期門號並看到不通過結果",
        "[ ] 錯誤訊息正確顯示（非本公司客戶、查無客戶等）",
        "[ ] Session 持久化正常（重新整理頁面後狀態保留）",
        "[ ] 進度指示器正確顯示當前步驟",
        "[ ] 門號卡片樣式正確（主要/副門號標籤）",
        "[ ] 詳細資訊可以展開/收合",
        "[ ] Loading 狀態正確顯示",
    ]
    
    for item in checklist:
        print(item)
    
    print_header("完成")
    print("Sprint 2 實作完成！")
    print("✅ WorkflowSessionManager - 工作流程 Session 管理")
    print("✅ CRMService - Mock CRM 資料服務")
    print("✅ renewal_workflow.py - 6個 API 端點")
    print("✅ useRenewalWorkflow.ts - 前端狀態管理")
    print("✅ renewal/index.vue - 完整 UI 頁面（Step 1-4）")
    print("\n下一步：Sprint 3 - 手機選擇與方案比較（Step 5-10）")


if __name__ == "__main__":
    asyncio.run(test_workflow_api())
