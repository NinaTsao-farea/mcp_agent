"""
Promotion MCP Server

提供促銷方案管理相關的 MCP Tools：
1. search_promotions - 搜尋促銷方案 (RAG)
2. get_plan_details - 取得方案詳情
3. compare_plans - 比較方案
4. calculate_upgrade_cost - 計算升級費用

Sprint 5 實作
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import structlog

# 添加 common 到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from common.base_server import BaseMCPServer

logger = structlog.get_logger()


class PromotionServer(BaseMCPServer):
    """Promotion MCP Server - 促銷方案管理
    
    提供促銷方案查詢、比較、推薦等功能
    支援 RAG 智能搜尋（目前使用 Mock 資料）
    """
    
    def __init__(self):
        """初始化 Promotion Server"""
        super().__init__(server_name="promotion-server")
        
        # Mock 促銷方案資料
        self.promotions = self._init_mock_promotions()
        
        # Mock 費率方案資料
        self.plans = self._init_mock_plans()
        
        logger.info(
            "Promotion MCP Server 已初始化",
            promotions_count=len(self.promotions),
            plans_count=len(self.plans)
        )
    
    def _init_mock_promotions(self) -> List[Dict[str, Any]]:
        """初始化 Mock 促銷方案資料"""
        return [
            {
                "promotion_id": "PROMO001",
                "title": "5G 雙飽專案",
                "description": "網內免費+上網吃到飽，最適合重度使用者",
                "type": "plan",
                "keywords": ["5G", "吃到飱", "網內免費", "無限上網", "高用量"],
                "benefits": [
                    "網內通話免費",
                    "5G 上網吃到飽",
                    "熱點分享 50GB",
                    "免費來電答鈴"
                ],
                "eligibility": {
                    "contract_type": ["攜碼", "續約", "新申辦"],
                    "min_contract_months": 30
                },
                "plans": ["PLAN001", "PLAN002"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-12-31",
                "priority": 10
            },
            {
                "promotion_id": "PROMO002",
                "title": "學生方案 專屬優惠",
                "description": "年輕就是要划算！學生專屬超值方案",
                "type": "plan",
                "keywords": ["學生", "青年", "優惠", "便宜", "小資"],
                "benefits": [
                    "月租 $399 起",
                    "20GB 上網",
                    "網內免費",
                    "贈送 LINE MUSIC 3個月"
                ],
                "eligibility": {
                    "contract_type": ["攜碼", "續約", "新申辦"],
                    "age_max": 25,
                    "min_contract_months": 24
                },
                "plans": ["PLAN003"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-06-30",
                "priority": 8
            },
            {
                "promotion_id": "PROMO003",
                "title": "攜碼加碼優惠",
                "description": "攜碼來就送！超高額回饋等你拿",
                "type": "discount",
                "keywords": ["攜碼", "回饋", "優惠", "折扣", "加碼"],
                "benefits": [
                    "攜碼享 85 折",
                    "加碼贈送 $3,000 購物金",
                    "免收攜碼手續費",
                    "保證原號移轉"
                ],
                "eligibility": {
                    "contract_type": ["攜碼"],
                    "min_contract_months": 30
                },
                "plans": ["PLAN001", "PLAN002", "PLAN004"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-12-31",
                "priority": 9
            },
            {
                "promotion_id": "PROMO004",
                "title": "老客戶續約好禮",
                "description": "感謝您的支持！續約享專屬優惠",
                "type": "discount",
                "keywords": ["續約", "老客戶", "回饋", "優惠", "忠誠"],
                "benefits": [
                    "續約 9 折優惠",
                    "贈送 2,000 點回饋金",
                    "免收續約手續費",
                    "優先選購新機"
                ],
                "eligibility": {
                    "contract_type": ["續約"],
                    "min_contract_months": 24
                },
                "plans": ["PLAN001", "PLAN002", "PLAN003", "PLAN004", "PLAN005"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-12-31",
                "priority": 7
            },
            {
                "promotion_id": "PROMO005",
                "title": "家庭共享方案",
                "description": "全家一起省！多門號超值優惠",
                "type": "plan",
                "keywords": ["家庭", "共享", "多門號", "優惠", "省錢"],
                "benefits": [
                    "主門號 $999/月",
                    "副門號 $499/月起",
                    "共享 100GB 上網",
                    "網內互打免費"
                ],
                "eligibility": {
                    "contract_type": ["攜碼", "續約", "新申辦"],
                    "min_lines": 2,
                    "min_contract_months": 24
                },
                "plans": ["PLAN006"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-12-31",
                "priority": 6
            },
            {
                "promotion_id": "PROMO006",
                "title": "商務專案 企業優惠",
                "description": "企業行動方案，通話+上網一次滿足",
                "type": "plan",
                "keywords": ["商務", "企業", "公司", "辦公", "通話"],
                "benefits": [
                    "市話+網內免費",
                    "40GB 上網",
                    "國際漫遊優惠",
                    "專屬客服"
                ],
                "eligibility": {
                    "contract_type": ["新申辦", "續約"],
                    "is_business": True,
                    "min_contract_months": 24
                },
                "plans": ["PLAN007"],
                "valid_from": "2025-01-01",
                "valid_until": "2025-12-31",
                "priority": 5
            }
        ]
    
    def _init_mock_plans(self) -> List[Dict[str, Any]]:
        """初始化 Mock 費率方案資料"""
        return [
            {
                "plan_id": "PLAN001",
                "name": "5G 極速飆網 1399",
                "monthly_fee": 1399,
                "contract_months": 30,
                "data": "無限上網",
                "voice": "網內免費",
                "sms": 100,
                "features": [
                    "5G 上網吃到飽（降速至 5Mbps）",
                    "網內通話免費",
                    "網外/市話 300分鐘",
                    "熱點分享 50GB"
                ],
                "suitable_for": ["重度使用者", "影音愛好者", "行動辦公"],
                "upgrade_benefits": "享手機折扣 $12,000"
            },
            {
                "plan_id": "PLAN002",
                "name": "5G 暢遊方案 999",
                "monthly_fee": 999,
                "contract_months": 30,
                "data": "50GB",
                "voice": "網內免費",
                "sms": 50,
                "features": [
                    "5G 上網 50GB",
                    "網內通話免費",
                    "網外/市話 200分鐘",
                    "熱點分享 20GB"
                ],
                "suitable_for": ["中度使用者", "平衡型用戶"],
                "upgrade_benefits": "享手機折扣 $8,000"
            },
            {
                "plan_id": "PLAN003",
                "name": "學生輕量包 399",
                "monthly_fee": 399,
                "contract_months": 24,
                "data": "20GB",
                "voice": "網內免費",
                "sms": 30,
                "features": [
                    "4G/5G 上網 20GB",
                    "網內通話免費",
                    "網外/市話 100分鐘",
                    "贈 LINE MUSIC 3個月"
                ],
                "suitable_for": ["學生", "輕度使用者", "小資族"],
                "upgrade_benefits": "享手機折扣 $3,000"
            },
            {
                "plan_id": "PLAN004",
                "name": "經濟實惠 599",
                "monthly_fee": 599,
                "contract_months": 24,
                "data": "30GB",
                "voice": "網內免費",
                "sms": 50,
                "features": [
                    "4G/5G 上網 30GB",
                    "網內通話免費",
                    "網外/市話 150分鐘",
                    "熱點分享 10GB"
                ],
                "suitable_for": ["一般使用者", "經濟實惠"],
                "upgrade_benefits": "享手機折扣 $5,000"
            },
            {
                "plan_id": "PLAN005",
                "name": "通話大戶 799",
                "monthly_fee": 799,
                "contract_months": 24,
                "data": "40GB",
                "voice": "網內+市話免費",
                "sms": 100,
                "features": [
                    "4G/5G 上網 40GB",
                    "網內+市話通話免費",
                    "網外 200分鐘",
                    "來電答鈴免費"
                ],
                "suitable_for": ["通話需求高", "業務人員"],
                "upgrade_benefits": "享手機折扣 $6,000"
            },
            {
                "plan_id": "PLAN006",
                "name": "家庭共享 1699",
                "monthly_fee": 1699,
                "contract_months": 24,
                "data": "100GB共享",
                "voice": "網內互打免費",
                "sms": 200,
                "features": [
                    "100GB 共享上網",
                    "最多 4 門號共享",
                    "網內互打免費",
                    "副門號 $499/月起"
                ],
                "suitable_for": ["家庭用戶", "多門號需求"],
                "upgrade_benefits": "每門號享手機折扣 $4,000"
            },
            {
                "plan_id": "PLAN007",
                "name": "商務精選 1199",
                "monthly_fee": 1199,
                "contract_months": 24,
                "data": "40GB",
                "voice": "市話+網內免費",
                "sms": 150,
                "features": [
                    "4G/5G 上網 40GB",
                    "市話+網內通話免費",
                    "網外 300分鐘",
                    "國際漫遊優惠",
                    "專屬客服專線"
                ],
                "suitable_for": ["商務人士", "企業用戶"],
                "upgrade_benefits": "享手機折扣 $7,000"
            }
        ]
    
    async def search_promotions(
        self,
        query: str,
        contract_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """搜尋促銷方案 (RAG)
        
        使用語意搜尋找出最相關的促銷方案
        目前使用 Mock 關鍵字比對，未來可整合 Azure AI Search
        
        Args:
            query: 搜尋查詢（自然語言）
            contract_type: 合約類型篩選（攜碼/續約/新申辦）
            limit: 回傳筆數限制
        
        Returns:
            {
                "promotions": [...],
                "total": int,
                "query": str
            }
        """
        logger.info(
            "搜尋促銷方案",
            query=query,
            contract_type=contract_type,
            limit=limit
        )
        
        try:
            # 簡易關鍵字比對（未來替換為 RAG）
            query_lower = query.lower()
            matched_promotions = []
            
            for promo in self.promotions:
                score = 0
                
                # 檢查關鍵字
                for keyword in promo["keywords"]:
                    if keyword in query_lower or keyword.lower() in query_lower:
                        score += 10
                
                # 檢查標題
                if any(word in promo["title"] for word in query.split()):
                    score += 5
                
                # 檢查描述
                if any(word in promo["description"] for word in query.split()):
                    score += 3
                
                # 合約類型篩選
                if contract_type:
                    if contract_type in promo["eligibility"].get("contract_type", []):
                        score += 20
                    else:
                        continue  # 不符合合約類型，跳過
                
                if score > 0:
                    promo_copy = promo.copy()
                    promo_copy["relevance_score"] = score
                    matched_promotions.append(promo_copy)
            
            # 依相關性排序
            matched_promotions.sort(
                key=lambda x: (x["relevance_score"], x["priority"]),
                reverse=True
            )
            
            # 限制回傳筆數
            result_promotions = matched_promotions[:limit]
            
            logger.info(
                "促銷方案搜尋完成",
                total_matched=len(matched_promotions),
                returned=len(result_promotions)
            )
            
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
        logger.info("取得方案詳情", plan_id=plan_id)
        
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
            
            logger.info(
                "方案詳情查詢成功",
                plan_id=plan_id,
                promotions_count=len(applicable_promotions)
            )
            
            return result
            
        except Exception as e:
            logger.error("取得方案詳情失敗", plan_id=plan_id, error=str(e))
            return None
    
    async def compare_plans(
        self,
        plan_ids: List[str]
    ) -> Dict[str, Any]:
        """比較方案
        
        比較多個方案的內容與差異
        
        Args:
            plan_ids: 方案 ID 列表（最多 4 個）
        
        Returns:
            {
                "plans": [...],
                "comparison": {...},
                "recommendation": str
            }
        """
        logger.info("比較方案", plan_ids=plan_ids, count=len(plan_ids))
        
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
                else:
                    logger.warning("方案不存在", plan_id=plan_id)
            
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
            
            logger.info("方案比較完成", plans_count=len(plans))
            
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
        
        計算從現有方案升級到新方案的費用
        
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
            "計算升級費用",
            current_plan_fee=current_plan_fee,
            new_plan_id=new_plan_id,
            device_price=device_price,
            contract_type=contract_type
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
            
            # 計算手機折扣（從 upgrade_benefits 提取）
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
                portability_discount = int(device_price * 0.15)  # 85折 = 15% 折扣
                final_device_price = max(0, final_device_price - portability_discount)
                total_cost = total_contract_cost + final_device_price
            
            result = {
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
            
            logger.info(
                "升級費用計算完成",
                monthly_diff=monthly_diff,
                total_cost=total_cost
            )
            
            return result
            
        except Exception as e:
            logger.error("計算升級費用失敗", error=str(e))
            return {"error": str(e)}
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """取得所有 Tools 的 Schema"""
        return [
            {
                "name": "search_promotions",
                "description": "搜尋促銷方案，使用自然語言查詢找出最相關的促銷活動",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜尋查詢（自然語言），例如：吃到飽方案、學生優惠、攜碼優惠"
                        },
                        "contract_type": {
                            "type": "string",
                            "description": "合約類型篩選",
                            "enum": ["攜碼", "續約", "新申辦"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "回傳筆數限制",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_plan_details",
                "description": "取得方案詳細資訊，包含費率、數據、通話、適用促銷等",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "方案 ID，例如：PLAN001"
                        }
                    },
                    "required": ["plan_id"]
                }
            },
            {
                "name": "compare_plans",
                "description": "比較多個方案的內容與差異，最多可比較 4 個方案",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plan_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "方案 ID 列表，例如：['PLAN001', 'PLAN002']",
                            "maxItems": 4
                        }
                    },
                    "required": ["plan_ids"]
                }
            },
            {
                "name": "calculate_upgrade_cost",
                "description": "計算從現有方案升級到新方案的費用，包含手機折扣",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "current_plan_fee": {
                            "type": "integer",
                            "description": "目前方案月租費"
                        },
                        "new_plan_id": {
                            "type": "string",
                            "description": "新方案 ID"
                        },
                        "device_price": {
                            "type": "integer",
                            "description": "手機價格",
                            "default": 0
                        },
                        "contract_type": {
                            "type": "string",
                            "description": "合約類型",
                            "enum": ["攜碼", "續約", "新申辦"],
                            "default": "續約"
                        }
                    },
                    "required": ["current_plan_fee", "new_plan_id"]
                }
            }
        ]


async def main():
    """Promotion MCP Server 主程式"""
    logger.info("啟動 Promotion MCP Server")
    
    # 建立 server
    server = PromotionServer()
    
    # 執行 stdio MCP Server
    await server.run_stdio()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
