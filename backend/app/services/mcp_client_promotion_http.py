"""
Promotion MCP Client Service - HTTP Transport

透過 HTTP 與 Promotion MCP Server 通訊
"""
import os
import httpx
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class MCPClientServicePromotionHTTP:
    """Promotion MCP Client - HTTP Transport"""
    
    def __init__(self):
        self.base_url = os.getenv("PROMOTION_MCP_SERVER_URL", "http://localhost:8003")
        self.client: Optional[httpx.AsyncClient] = None
        self.initialized = False
        logger.info("MCP Client Service (Promotion HTTP) 已建立", base_url=self.base_url)
    
    async def initialize(self):
        """初始化 MCP Client"""
        if self.initialized:
            return
        
        logger.info("初始化 MCP Client Service (Promotion HTTP)")
        
        # 建立 HTTP 客戶端
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 測試連接
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health = response.json()
                logger.info("Promotion MCP Server 連接成功", health=health)
            else:
                logger.warning(
                    "Promotion MCP Server 健康檢查返回非 200",
                    status=response.status_code
                )
        except Exception as e:
            logger.error("無法連接 Promotion MCP Server", error=str(e), base_url=self.base_url)
            raise RuntimeError(f"Promotion MCP Server 連接失敗: {e}")
        
        self.initialized = True
        logger.info("MCP Client Service (Promotion HTTP) 初始化完成")
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """調用 MCP Tool
        
        Args:
            tool_name: Tool 名稱
            arguments: Tool 參數
            
        Returns:
            Tool 執行結果
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/mcp/call",
                json={
                    "tool": tool_name,
                    "arguments": arguments
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    "MCP Tool 調用失敗",
                    tool=tool_name,
                    status=response.status_code,
                    response=response.text
                )
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error("MCP Tool 調用異常", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_promotions(
        self,
        query: str,
        contract_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        搜尋促銷方案
        
        Args:
            query: 搜尋查詢
            contract_type: 合約類型篩選 (new/renewal/all)
            limit: 回傳筆數限制
            
        Returns:
            {
                "promotions": [...],
                "total": int,
                "query": str
            }
        """
        logger.info(
            "HTTP: 搜尋促銷方案",
            query=query,
            contract_type=contract_type,
            limit=limit
        )
        
        result = await self._call_tool(
            "search_promotions",
            {
                "query": query,
                "contract_type": contract_type,
                "limit": limit
            }
        )
        
        if result.get("success"):
            # MCP Server 返回 {"success": True, "result": {...}}
            # 直接返回 result 內容（與 Mock Service 格式一致）
            return result.get("result", {})
        else:
            logger.warning("搜尋促銷方案失敗", error=result.get("error"))
            return {
                "promotions": [],
                "total": 0,
                "query": query
            }
    
    async def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        取得方案詳細資訊
        
        Args:
            plan_id: 方案編號
            
        Returns:
            方案詳細資訊
        """
        logger.info("HTTP: 取得方案詳細資訊", plan_id=plan_id)
        
        result = await self._call_tool(
            "get_plan_details",
            {"plan_id": plan_id}
        )
        
        if result.get("success"):
            return result.get("result")
        else:
            logger.warning("取得方案詳細資訊失敗", error=result.get("error"))
            return None
    
    async def compare_plans(
        self,
        plan_ids: List[str]
    ) -> Dict[str, Any]:
        """
        比較多個方案
        
        Args:
            plan_ids: 要比較的方案編號列表
            
        Returns:
            {
                "plans": [...],
                "comparison": {...},
                "recommendation": str
            }
        """
        logger.info(
            "HTTP: 比較方案",
            plan_ids=plan_ids
        )
        
        result = await self._call_tool(
            "compare_plans",
            {"plan_ids": plan_ids}
        )
        
        if result.get("success"):
            return result.get("result", {})
        else:
            logger.warning("比較方案失敗", error=result.get("error"))
            return {
                "plans": [],
                "comparison": {},
                "recommendation": "比較失敗"
            }
    
    async def calculate_upgrade_cost(
        self,
        current_plan_fee: int,
        new_plan_id: str,
        device_price: int = 0,
        contract_type: str = "續約"
    ) -> Dict[str, Any]:
        """
        計算升級費用
        
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
            "HTTP: 計算升級費用",
            current_plan_fee=current_plan_fee,
            new_plan_id=new_plan_id,
            device_price=device_price,
            contract_type=contract_type
        )
        
        result = await self._call_tool(
            "calculate_upgrade_cost",
            {
                "current_plan_fee": current_plan_fee,
                "new_plan_id": new_plan_id,
                "device_price": device_price,
                "contract_type": contract_type
            }
        )
        
        if result.get("success"):
            return result.get("result", {})
        else:
            logger.warning("計算升級費用失敗", error=result.get("error"))
            return {
                "new_plan": None,
                "monthly_diff": 0,
                "total_contract_cost": 0,
                "device_discount": 0,
                "final_device_price": 0,
                "total_cost": 0
            }
    
    async def close(self):
        """關閉 HTTP 客戶端"""
        if self.client:
            await self.client.aclose()
            logger.info("Promotion MCP Client HTTP 已關閉")


# 全域實例 (HTTP 模式)
mcp_client_promotion_http = MCPClientServicePromotionHTTP()
