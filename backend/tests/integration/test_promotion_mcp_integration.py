"""
測試 Promotion MCP Server 整合

測試前請確保：
1. 設置環境變數: USE_MCP_PROMOTION=true
2. 啟動 Promotion MCP Server: python promotion_server_http.py (port 8003)
3. 啟動後端: python run_app.py
"""
import asyncio
import httpx
import os

# 設置環境變數（測試用）
os.environ['USE_MCP_PROMOTION'] = 'true'
os.environ['USE_HTTP_TRANSPORT'] = 'true'

from app.services.promotion_factory import get_promotion_service

async def test_promotion_mcp_integration():
    """測試 Promotion MCP 整合"""
    
    print("\n" + "="*60)
    print("測試 Promotion MCP Server 整合")
    print("="*60)
    
    # 取得 Promotion Service（應該是 MCP Client）
    print("\n[Step 1] 取得 Promotion Service...")
    promotion_service = await get_promotion_service()
    print(f"✅ Promotion Service 類型: {type(promotion_service).__name__}")
    
    # 測試 1: 搜尋促銷方案
    print("\n[Step 2] 搜尋促銷方案（關鍵字：5G）...")
    search_result = await promotion_service.search_promotions(
        query="5G",
        contract_type="renewal",
        limit=3
    )
    print(f"✅ 找到 {search_result.get('total', 0)} 個促銷方案")
    for i, promo in enumerate(search_result.get("promotions", []), 1):
        print(f"   {i}. {promo['title']}")
        print(f"      {promo['description'][:60]}...")
        print(f"      折扣: {promo.get('discount_value')} 元")
    
    # 測試 2: 取得方案詳細資訊
    print("\n[Step 3] 取得方案詳細資訊...")
    plan_details = await promotion_service.get_plan_details("PLAN_5G_1399")
    if plan_details:
        print(f"✅ 方案資訊:")
        print(f"   名稱: {plan_details['name']}")
        print(f"   月租: ${plan_details['monthly_fee']}")
        print(f"   數據: {plan_details['data_quota']}")
        print(f"   通話: {plan_details['voice_minutes']} 分鐘")
        print(f"   合約期: {plan_details['contract_months']} 個月")
    else:
        print("❌ 取得方案資訊失敗")
    
    # 測試 3: 比較多個方案
    print("\n[Step 4] 比較方案...")
    comparison = await promotion_service.compare_plans(
        plan_ids=["PLAN_5G_1399", "PLAN_5G_999", "PLAN_4G_799"]
    )
    
    if comparison.get("plans"):
        print(f"✅ 比較 {len(comparison['plans'])} 個方案:")
        for plan in comparison["plans"]:
            print(f"   • {plan['name']} - ${plan['monthly_fee']}/月")
            print(f"     數據: {plan['data_quota']}, 通話: {plan['voice_minutes']} 分鐘")
        
        if comparison.get("recommendation"):
            print(f"\n   💡 推薦: {comparison['recommendation']}")
    else:
        print("❌ 比較方案失敗")
    
    # 測試 4: 計算升級費用
    print("\n[Step 5] 計算升級費用...")
    upgrade_cost = await promotion_service.calculate_upgrade_cost(
        current_plan_fee=599,  # 使用月費而不是 plan_id
        new_plan_id="PLAN_5G_1399",
        device_price=25000,
        contract_type="續約"
    )
    
    if upgrade_cost.get("new_plan"):
        print(f"✅ 升級費用試算:")
        print(f"   新方案: {upgrade_cost['new_plan']['name']} (${upgrade_cost['new_plan']['monthly_fee']}/月)")
        print(f"   月費差異: ${upgrade_cost.get('monthly_diff', 0)}")
        print(f"   合約總費用: ${upgrade_cost.get('total_contract_cost', 0)}")
        print(f"   設備補貼: ${upgrade_cost.get('device_discount', 0)}")
        print(f"   設備實付: ${upgrade_cost.get('final_device_price', 0)}")
        print(f"   總費用: ${upgrade_cost.get('total_cost', 0)}")
    else:
        print("❌ 計算升級費用失敗")
    
    # 測試 5: 搜尋其他類型促銷
    print("\n[Step 6] 搜尋攜碼專案...")
    mnp_result = await promotion_service.search_promotions(
        query="攜碼",
        limit=2
    )
    print(f"✅ 找到 {mnp_result.get('total', 0)} 個攜碼專案")
    for i, promo in enumerate(mnp_result.get("promotions", []), 1):
        print(f"   {i}. {promo['title']}")
        print(f"      適用: {promo.get('contract_type', 'all')}")
    
    print("\n" + "="*60)
    print("✅ Promotion MCP Server 整合測試完成")
    print("="*60)


async def test_mcp_server_connection():
    """測試 MCP Server 連接"""
    
    print("\n" + "="*60)
    print("測試 Promotion MCP Server 連接")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 健康檢查
            print("\n[檢查] Promotion MCP Server 健康狀態...")
            response = await client.get("http://localhost:8003/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Promotion MCP Server 運行正常")
                print(f"   狀態: {health.get('status')}")
                print(f"   促銷數: {health.get('promotions_count')}")
                print(f"   方案數: {health.get('plans_count')}")
                return True
            else:
                print(f"❌ Promotion MCP Server 返回錯誤: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無法連接 Promotion MCP Server: {e}")
            print("\n請確保已啟動 Promotion MCP Server:")
            print("   cd backend/mcp_servers")
            print("   python promotion_server_http.py")
            print("   或使用: python -m uvicorn promotion_server_http:app --host 0.0.0.0 --port 8003")
            return False


async def test_compare_mock_vs_mcp():
    """比較 Mock Service 和 MCP Service 的結果"""
    
    print("\n" + "="*60)
    print("比較 Mock Service vs MCP Service")
    print("="*60)
    
    # 測試 Mock Service
    print("\n[Mock Service]")
    os.environ['USE_MCP_PROMOTION'] = 'false'
    mock_service = await get_promotion_service()
    print(f"Service 類型: {type(mock_service).__name__}")
    
    mock_result = await mock_service.search_promotions(query="5G", limit=3)
    print(f"搜尋結果: {mock_result.get('total')} 個促銷方案")
    
    mock_plan = await mock_service.get_plan_details("PLAN_5G_1399")
    print(f"方案查詢: {mock_plan['name'] if mock_plan else 'None'}")
    
    # 測試 MCP Service
    print("\n[MCP Service]")
    os.environ['USE_MCP_PROMOTION'] = 'true'
    
    try:
        mcp_service = await get_promotion_service()
        print(f"Service 類型: {type(mcp_service).__name__}")
        
        mcp_result = await mcp_service.search_promotions(query="5G", limit=3)
        print(f"搜尋結果: {mcp_result.get('total')} 個促銷方案")
        
        mcp_plan = await mcp_service.get_plan_details("PLAN_5G_1399")
        print(f"方案查詢: {mcp_plan['name'] if mcp_plan else 'None'}")
        
        # 比較結果
        print("\n[比較]")
        if mock_result.get('total') == mcp_result.get('total'):
            print("✅ 搜尋結果數量一致")
        else:
            print(f"⚠️  搜尋結果數量不同: Mock={mock_result.get('total')}, MCP={mcp_result.get('total')}")
        
        if mock_plan and mcp_plan:
            if mock_plan['name'] == mcp_plan['name']:
                print("✅ 方案資訊一致")
            else:
                print("⚠️  方案資訊不同")
        
    except Exception as e:
        print(f"⚠️  MCP Service 測試失敗: {e}")
        print("   可能 MCP Server 未啟動")


if __name__ == "__main__":
    async def main():
        # 先檢查 MCP Server 是否運行
        is_running = await test_mcp_server_connection()
        
        if is_running:
            # 執行整合測試
            await test_promotion_mcp_integration()
            
            # 比較 Mock vs MCP
            await test_compare_mock_vs_mcp()
        else:
            print("\n⚠️  跳過整合測試（MCP Server 未運行）")
    
    asyncio.run(main())
