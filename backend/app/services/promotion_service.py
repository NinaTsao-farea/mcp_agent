"""
Mock Promotion Service

提供促銷方案查詢、比較服務（Mock 模式）
不需啟動 MCP Server 即可使用，適合開發測試

與 PromotionServer 具有相同介面
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import structlog

logger = structlog.get_logger()

# 匯入 PromotionServer 的 Mock 資料初始化方法
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))
from promotion_server import PromotionServer as BasePromotionServer

class MockPromotionService:
    """Mock Promotion Service
    
    與 Promotion MCP Server 相同介面，但不需要啟動 MCP Server
    適合開發測試使用
    """
    
    def __init__(self):
        """初始化 Mock Promotion Service"""
        # 建立 base server 以取得 Mock 資料
        base_server = BasePromotionServer()
        
        # 複製 Mock 資料
        self.promotions = base_server.promotions
        self.plans = base_server.plans
        
        logger.info(
            "Mock Promotion Service 已初始化",
            promotions_count=len(self.promotions),
            plans_count=len(self.plans)
        )
    
    async def search_promotions(
        self,
        query: str,
        contract_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """搜尋促銷方案
        
        Args:
            query: 搜尋查詢
            contract_type: 合約類型篩選
            limit: 回傳筆數限制
        
        Returns:
            {
                "promotions": [...],
                "total": int,
                "query": str
            }
        """
        logger.info(
            "Mock: 搜尋促銷方案",
            query=query,
            contract_type=contract_type
        )
        
        try:
            # 簡易關鍵字比對
            query_lower = query.lower()
            matched_promotions = []
            
            logger.debug(
                "開始搜尋",
                query=query,
                query_lower=query_lower,
                contract_type=contract_type,
                total_promotions=len(self.promotions)
            )
            
            for promo in self.promotions:
                score = 0
                matched_keywords = []
                
                # 檢查關鍵字
                for keyword in promo["keywords"]:
                    if keyword in query_lower or keyword.lower() in query_lower:
                        score += 10
                        matched_keywords.append(keyword)
                
                # 檢查標題
                if any(word in promo["title"] for word in query.split()):
                    score += 5
                
                # 檢查描述
                if any(word in promo["description"] for word in query.split()):
                    score += 3
                
                # 合約類型篩選
                if contract_type:
                    promo_contract_types = promo["eligibility"].get("contract_type", [])
                    if contract_type in promo_contract_types:
                        score += 20
                    else:
                        logger.debug(
                            "合約類型不符",
                            promotion_id=promo["promotion_id"],
                            required=contract_type,
                            available=promo_contract_types,
                            initial_score=score
                        )
                        continue
                
                if score > 0:
                    promo_copy = promo.copy()
                    promo_copy["relevance_score"] = score
                    matched_promotions.append(promo_copy)
                    
                    logger.debug(
                        "促銷匹配",
                        promotion_id=promo["promotion_id"],
                        promotion_title=promo["title"],
                        score=score,
                        matched_keywords=matched_keywords
                    )
            
            # 依相關性排序
            matched_promotions.sort(
                key=lambda x: (x["relevance_score"], x["priority"]),
                reverse=True
            )
            
            # 限制回傳筆數
            result_promotions = matched_promotions[:limit]
            
            return {
                "promotions": result_promotions,
                "total": len(matched_promotions),
                "query": query
            }
            
        except Exception as e:
            logger.error("搜尋促銷方案失敗", error=str(e))
            return {
                "promotions": [],
                "total": 0,
                "query": query,
                "error": str(e)
            }
    
    async def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """取得方案詳情
        
        Args:
            plan_id: 方案 ID
        
        Returns:
            方案詳細資訊，若不存在則回傳 None
        """
        logger.info("Mock: 取得方案詳情", plan_id=plan_id)
        
        try:
            # 查詢方案
            plan = next((p for p in self.plans if p["plan_id"] == plan_id), None)
            
            if not plan:
                logger.warning("方案不存在", plan_id=plan_id)
                return None
            
            # 查詢適用的促銷活動
            applicable_promotions = []
            for promo in self.promotions:
                if plan_id in promo.get("plans", []):
                    applicable_promotions.append({
                        "promotion_id": promo["promotion_id"],
                        "title": promo["title"],
                        "benefits": promo["benefits"]
                    })
            
            # 組合完整資訊
            result = plan.copy()
            result["applicable_promotions"] = applicable_promotions
            result["total_promotions"] = len(applicable_promotions)
            
            return result
            
        except Exception as e:
            logger.error("取得方案詳情失敗", plan_id=plan_id, error=str(e))
            return None
    
    async def compare_plans(
        self,
        plan_ids: List[str]
    ) -> Dict[str, Any]:
        """比較方案
        
        Args:
            plan_ids: 方案 ID 列表（最多 4 個）
        
        Returns:
            {
                "plans": [...],
                "comparison": {...},
                "recommendation": str
            }
        """
        logger.info("Mock: 比較方案", plan_ids=plan_ids)
        
        try:
            if len(plan_ids) > 4:
                return {
                    "error": "最多只能比較 4 個方案",
                    "plans": [],
                    "comparison": {}
                }
            
            # 取得方案詳情
            plans = []
            for plan_id in plan_ids:
                plan = await self.get_plan_details(plan_id)
                if plan:
                    plans.append(plan)
            
            if not plans:
                return {
                    "error": "沒有找到有效的方案",
                    "plans": [],
                    "comparison": {}
                }
            
            # 建立比較表
            comparison = {
                "monthly_fee": {
                    "min": min(p["monthly_fee"] for p in plans),
                    "max": max(p["monthly_fee"] for p in plans),
                    "values": {p["plan_id"]: p["monthly_fee"] for p in plans}
                },
                "data": {
                    "values": {p["plan_id"]: p["data"] for p in plans}
                },
                "voice": {
                    "values": {p["plan_id"]: p["voice"] for p in plans}
                },
                "contract_months": {
                    "values": {p["plan_id"]: p["contract_months"] for p in plans}
                }
            }
            
            # 生成建議
            recommendation = self._generate_recommendation(plans)
            
            return {
                "plans": plans,
                "comparison": comparison,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error("比較方案失敗", error=str(e))
            return {
                "error": str(e),
                "plans": [],
                "comparison": {}
            }
    
    def _generate_recommendation(self, plans: List[Dict[str, Any]]) -> str:
        """生成方案推薦建議"""
        if not plans:
            return "無法提供建議"
        
        if len(plans) == 1:
            return f"目前只有一個方案 {plans[0]['name']}"
        
        # 找出最便宜的
        cheapest = min(plans, key=lambda x: x["monthly_fee"])
        # 找出數據最多的
        unlimited_data = [p for p in plans if "無限" in p["data"]]
        
        recommendations = []
        recommendations.append(
            f"🏷️ 最經濟實惠：{cheapest['name']} (月租 ${cheapest['monthly_fee']})"
        )
        
        if unlimited_data:
            recommendations.append(
                f"🚀 重度使用者：{unlimited_data[0]['name']} (上網吃到飽)"
            )
        
        return " | ".join(recommendations)
    
    async def calculate_upgrade_cost(
        self,
        current_plan_fee: int,
        new_plan_id: str,
        device_price: int = 0,
        contract_type: str = "續約"
    ) -> Dict[str, Any]:
        """計算升級費用
        
        Args:
            current_plan_fee: 目前方案月租費
            new_plan_id: 新方案 ID
            device_price: 手機價格
            contract_type: 合約類型
        
        Returns:
            {
                "new_plan": {...},
                "monthly_diff": int,
                "total_contract_cost": int,
                "device_discount": int,
                "final_device_price": int,
                "total_cost": int
            }
        """
        logger.info(
            "Mock: 計算升級費用",
            new_plan_id=new_plan_id,
            device_price=device_price
        )
        
        try:
            # 取得新方案
            new_plan = await self.get_plan_details(new_plan_id)
            if not new_plan:
                return {"error": "方案不存在"}
            
            # 計算月租差額
            monthly_diff = new_plan["monthly_fee"] - current_plan_fee
            
            # 計算合約期總費用
            total_contract_cost = new_plan["monthly_fee"] * new_plan["contract_months"]
            
            # 計算手機折扣
            device_discount = 0
            if "upgrade_benefits" in new_plan:
                benefit_text = new_plan["upgrade_benefits"]
                if "$" in benefit_text:
                    import re
                    match = re.search(r'\$([0-9,]+)', benefit_text)
                    if match:
                        device_discount = int(match.group(1).replace(',', ''))
            
            # 計算手機實付金額
            final_device_price = max(0, device_price - device_discount)
            
            # 總費用
            total_cost = total_contract_cost + final_device_price
            
            # 攜碼額外折扣
            if contract_type == "攜碼":
                portability_discount = int(device_price * 0.15)
                final_device_price = max(0, final_device_price - portability_discount)
                total_cost = total_contract_cost + final_device_price
            
            return {
                "new_plan": new_plan,
                "current_plan_fee": current_plan_fee,
                "monthly_diff": monthly_diff,
                "total_contract_cost": total_contract_cost,
                "device_price": device_price,
                "device_discount": device_discount,
                "final_device_price": final_device_price,
                "total_cost": total_cost,
                "contract_type": contract_type
            }
            
        except Exception as e:
            logger.error("計算升級費用失敗", error=str(e))
            return {"error": str(e)}
