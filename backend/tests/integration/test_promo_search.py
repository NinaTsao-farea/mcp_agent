"""
臨時測試：檢查促銷搜尋邏輯
"""
import sys
import asyncio
sys.path.insert(0, 'app')
from services.promotion_service import MockPromotionService

async def test_search():
    service = MockPromotionService()
    result = await service.search_promotions(
        query='續約搭配裝置 android',
        contract_type='續約',
        limit=10
    )
    print(f'\n找到促銷: {result["total"]} 個')
    for promo in result['promotions']:
        print(f'  - {promo["title"]} (分數: {promo["relevance_score"]})')
    
    return result

print("=== 測試實際搜尋API ===")
result = asyncio.run(test_search())

print("\n=== 詳細檢查 ===")
sys.path.insert(0, 'D:/ai_project/test_mcp_agent2/backend/mcp_servers')
from promotion_server import PromotionServer

server = PromotionServer()
print(f'促銷總數: {len(server.promotions)}')
print(f'方案總數: {len(server.plans)}')

# 測試搜尋
query = '續約搭配裝置 android'
query_lower = query.lower()
print(f'\n搜尋查詢: {query}')
print(f'查詢小寫: {query_lower}')

print("\n=== 檢查所有促銷 ===")
for promo in server.promotions:
    print(f'\n促銷: {promo["promotion_id"]} - {promo["title"]}')
    print(f'  關鍵字: {promo["keywords"]}')
    print(f'  合約類型: {promo["eligibility"].get("contract_type", [])}')
    
    matched = []
    for keyword in promo['keywords']:
        if keyword in query_lower or keyword.lower() in query_lower:
            matched.append(keyword)
    print(f'  匹配關鍵字: {matched}')
    
    # 檢查合約類型
    contract_type = "續約"
    if contract_type in promo["eligibility"].get("contract_type", []):
        print(f'  ✅ 合約類型匹配: {contract_type}')
    else:
        print(f'  ❌ 合約類型不匹配: {contract_type} not in {promo["eligibility"].get("contract_type", [])}')
