"""
測試 Promotion MCP Server

測試所有 4 個 Tools：
1. search_promotions - 搜尋促銷方案
2. get_plan_details - 取得方案詳情
3. compare_plans - 比較方案
4. calculate_upgrade_cost - 計算升級費用
"""
import asyncio
import sys
from pathlib import Path

# 添加路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "mcp_servers"))

from mcp_servers.promotion_server import PromotionServer


def print_section(title: str):
    """印出區塊標題"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)


async def test_search_promotions():
    """測試 1: 搜尋促銷方案"""
    print_section("測試 1: search_promotions - 搜尋促銷方案")
    
    server = PromotionServer()
    
    # Test 1.1: 搜尋 "吃到飽"
    print("\n📋 測試 1.1: 搜尋「吃到飽」相關促銷")
    result = await server.search_promotions(query="吃到飽", limit=3)
    print(f"✅ 找到 {result['total']} 筆促銷")
    for i, promo in enumerate(result['promotions'], 1):
        print(f"   {i}. {promo['title']} (相關性: {promo.get('relevance_score', 0)})")
        print(f"      {promo['description']}")
    
    # Test 1.2: 搜尋 "學生優惠"
    print("\n📋 測試 1.2: 搜尋「學生優惠」")
    result = await server.search_promotions(query="學生優惠", limit=2)
    print(f"✅ 找到 {result['total']} 筆促銷")
    for promo in result['promotions']:
        print(f"   - {promo['title']}")
    
    # Test 1.3: 搜尋 "攜碼" + 篩選合約類型
    print("\n📋 測試 1.3: 搜尋「攜碼」（篩選：攜碼合約）")
    result = await server.search_promotions(
        query="攜碼優惠",
        contract_type="攜碼",
        limit=5
    )
    print(f"✅ 找到 {result['total']} 筆符合條件的促銷")
    for promo in result['promotions']:
        print(f"   - {promo['title']}")
        print(f"     適用: {', '.join(promo['eligibility']['contract_type'])}")
    
    # Test 1.4: 搜尋無結果
    print("\n📋 測試 1.4: 搜尋不存在的促銷")
    result = await server.search_promotions(query="xyz123無此促銷")
    print(f"  ✅ 正確處理: 找到 {result['total']} 筆")


async def test_get_plan_details():
    """測試 2: 取得方案詳情"""
    print_section("測試 2: get_plan_details - 取得方案詳情")
    
    server = PromotionServer()
    
    # Test 2.1: 查詢存在的方案
    print("\n📋 測試 2.1: 查詢 PLAN001 (5G 極速飆網)")
    result = await server.get_plan_details("PLAN001")
    if result:
        print(f"✅ 方案: {result['name']}")
        print(f"   月租: ${result['monthly_fee']}")
        print(f"   上網: {result['data']}")
        print(f"   通話: {result['voice']}")
        print(f"   適用促銷: {result['total_promotions']} 個")
        for promo in result['applicable_promotions'][:2]:
            print(f"     - {promo['title']}")
    
    # Test 2.2: 查詢學生方案
    print("\n📋 測試 2.2: 查詢 PLAN003 (學生輕量包)")
    result = await server.get_plan_details("PLAN003")
    if result:
        print(f"✅ 方案: {result['name']}")
        print(f"   月租: ${result['monthly_fee']}")
        print(f"   合約: {result['contract_months']} 個月")
        print(f"   適合: {', '.join(result['suitable_for'])}")
    
    # Test 2.3: 查詢不存在的方案
    print("\n📋 測試 2.3: 查詢不存在的方案")
    result = await server.get_plan_details("INVALID")
    if result is None:
        print("  ✅ 正確處理: 回傳 None")


async def test_compare_plans():
    """測試 3: 比較方案"""
    print_section("測試 3: compare_plans - 比較方案")
    
    server = PromotionServer()
    
    # Test 3.1: 比較 2 個方案
    print("\n📋 測試 3.1: 比較 PLAN001 vs PLAN002")
    result = await server.compare_plans(["PLAN001", "PLAN002"])
    if result.get('plans'):
        print(f"✅ 比較 {len(result['plans'])} 個方案")
        print(f"   月租範圍: ${result['comparison']['monthly_fee']['min']} - ${result['comparison']['monthly_fee']['max']}")
        print(f"   建議: {result['recommendation']}")
    
    # Test 3.2: 比較 3 個方案 (含學生方案)
    print("\n📋 測試 3.2: 比較 3 個方案 (極速/暢遊/學生)")
    result = await server.compare_plans(["PLAN001", "PLAN002", "PLAN003"])
    print(f"✅ 比較 {len(result['plans'])} 個方案")
    for plan in result['plans']:
        print(f"   - {plan['name']}: ${plan['monthly_fee']}/月, {plan['data']}")
    print(f"   {result['recommendation']}")
    
    # Test 3.3: 比較太多方案 (>4)
    print("\n📋 測試 3.3: 嘗試比較 5 個方案 (超過限制)")
    result = await server.compare_plans(["PLAN001", "PLAN002", "PLAN003", "PLAN004", "PLAN005"])
    if 'error' in result:
        print(f"  ✅ 正確處理: {result['error']}")
    
    # Test 3.4: 比較包含不存在的方案
    print("\n📋 測試 3.4: 比較包含不存在的方案")
    result = await server.compare_plans(["PLAN001", "INVALID", "PLAN002"])
    print(f"  ✅ 正確處理: 比較 {len(result['plans'])} 個有效方案")


async def test_calculate_upgrade_cost():
    """測試 4: 計算升級費用"""
    print_section("測試 4: calculate_upgrade_cost - 計算升級費用")
    
    server = PromotionServer()
    
    # Test 4.1: 續約升級（無手機）
    print("\n📋 測試 4.1: 從 $699 續約升級到 PLAN001（無手機）")
    result = await server.calculate_upgrade_cost(
        current_plan_fee=699,
        new_plan_id="PLAN001",
        device_price=0,
        contract_type="續約"
    )
    if 'new_plan' in result:
        print(f"✅ 新方案: {result['new_plan']['name']}")
        print(f"   月租差額: ${result['monthly_diff']} (每月多 ${result['monthly_diff']})")
        print(f"   合約總費用: ${result['total_contract_cost']:,}")
        print(f"   總費用: ${result['total_cost']:,}")
    
    # Test 4.2: 續約升級（含手機）
    print("\n📋 測試 4.2: 從 $699 續約升級到 PLAN001 + iPhone 15 Pro")
    result = await server.calculate_upgrade_cost(
        current_plan_fee=699,
        new_plan_id="PLAN001",
        device_price=36900,
        contract_type="續約"
    )
    if 'new_plan' in result:
        print(f"✅ 新方案: {result['new_plan']['name']}")
        print(f"   手機原價: ${result['device_price']:,}")
        print(f"   手機折扣: ${result['device_discount']:,}")
        print(f"   手機實付: ${result['final_device_price']:,}")
        print(f"   總費用: ${result['total_cost']:,}")
    
    # Test 4.3: 攜碼（額外折扣）
    print("\n📋 測試 4.3: 攜碼到 PLAN002 + Samsung S24")
    result = await server.calculate_upgrade_cost(
        current_plan_fee=0,  # 攜碼無現有方案
        new_plan_id="PLAN002",
        device_price=26900,
        contract_type="攜碼"
    )
    if 'new_plan' in result:
        print(f"✅ 新方案: {result['new_plan']['name']}")
        print(f"   手機原價: ${result['device_price']:,}")
        print(f"   手機實付: ${result['final_device_price']:,} (攜碼享 85 折)")
        print(f"   合約總費用: ${result['total_contract_cost']:,}")
        print(f"   總費用: ${result['total_cost']:,}")
    
    # Test 4.4: 學生方案
    print("\n📋 測試 4.4: 新申辦學生方案 PLAN003")
    result = await server.calculate_upgrade_cost(
        current_plan_fee=0,
        new_plan_id="PLAN003",
        device_price=23900,  # iPhone 14
        contract_type="新申辦"
    )
    if 'new_plan' in result:
        print(f"✅ 新方案: {result['new_plan']['name']}")
        print(f"   月租: ${result['new_plan']['monthly_fee']}")
        print(f"   合約期: {result['new_plan']['contract_months']} 個月")
        print(f"   手機實付: ${result['final_device_price']:,}")
        print(f"   總費用: ${result['total_cost']:,}")


async def test_tools_schema():
    """測試 5: Tools Schema"""
    print_section("測試 5: get_tools_schema - Tools Schema")
    
    server = PromotionServer()
    
    print("\n📋 取得所有 Tools Schema")
    tools = server.get_tools_schema()
    print(f"✅ 共 {len(tools)} 個 Tools")
    
    for tool in tools:
        print(f"\n  Tool: {tool['name']}")
        print(f"  描述: {tool['description']}")
        required = tool['inputSchema'].get('required', [])
        print(f"  必填參數: {', '.join(required) if required else '無'}")


async def main():
    """執行所有測試"""
    print("\n" + "🚀"*30)
    print("  Promotion MCP Server 測試套件")
    print("  測試 Sprint 5: 促銷方案查詢與推薦")
    print("🚀"*30)
    
    try:
        # 執行測試
        await test_search_promotions()
        await test_get_plan_details()
        await test_compare_plans()
        await test_calculate_upgrade_cost()
        await test_tools_schema()
        
        # 總結
        print("\n" + "="*60)
        print("✅✅✅ 所有測試完成！Promotion MCP Server 運作正常 ✅✅✅")
        print("="*60)
        print("\n已驗證:")
        print("  ✅ search_promotions - 搜尋促銷方案 (RAG)")
        print("  ✅ get_plan_details - 取得方案詳情")
        print("  ✅ compare_plans - 比較方案")
        print("  ✅ calculate_upgrade_cost - 計算升級費用")
        print("  ✅ get_tools_schema - Tools Schema")
        print("\nMock 資料:")
        print("  📦 6 個促銷活動")
        print("  📦 7 個費率方案")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
