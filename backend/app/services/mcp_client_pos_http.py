"""
POS MCP Client Service - HTTP Transport

透過 HTTP 與 POS MCP Server 通訊
"""
import os
import httpx
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class MCPClientServicePOSHTTP:
    """POS MCP Client - HTTP Transport"""
    
    def __init__(self):
        self.base_url = os.getenv("POS_MCP_SERVER_URL", "http://localhost:8002")
        self.client: Optional[httpx.AsyncClient] = None
        self.initialized = False
        logger.info("MCP Client Service (POS HTTP) 已建立", base_url=self.base_url)
    
    async def initialize(self):
        """初始化 MCP Client"""
        if self.initialized:
            return
        
        logger.info("初始化 MCP Client Service (POS HTTP)")
        
        # 建立 HTTP 客戶端
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 測試連接
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health = response.json()
                logger.info("POS MCP Server 連接成功", health=health)
            else:
                logger.warning(
                    "POS MCP Server 健康檢查返回非 200",
                    status=response.status_code
                )
        except Exception as e:
            logger.error("無法連接 POS MCP Server", error=str(e), base_url=self.base_url)
            raise RuntimeError(f"POS MCP Server 連接失敗: {e}")
        
        self.initialized = True
        logger.info("MCP Client Service (POS HTTP) 初始化完成")
    
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
                    "error": {
                        "code": "MCP_CALL_ERROR",
                        "message": f"HTTP {response.status_code}: {response.text}"
                    }
                }
        except Exception as e:
            logger.error("MCP Tool 調用異常", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": {
                    "code": "MCP_CALL_EXCEPTION",
                    "message": str(e)
                }
            }
    
    async def query_device_stock(
        self,
        store_id: str,
        os_filter: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        查詢門市設備庫存
        
        Args:
            store_id: 門市編號
            os_filter: OS 過濾 (iOS/Android)
            min_price: 最低價格
            max_price: 最高價格
            
        Returns:
            設備列表
        """
        logger.info(
            "HTTP: 查詢門市設備庫存",
            store_id=store_id,
            os_filter=os_filter,
            min_price=min_price,
            max_price=max_price
        )
        
        result = await self._call_tool(
            "query_device_stock",
            {
                "store_id": store_id,
                "os_filter": os_filter,
                "min_price": min_price,
                "max_price": max_price
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            # 返回設備列表（與 Mock Service 格式一致）
            return data.get("devices", [])
        else:
            logger.warning("查詢設備庫存失敗", error=result.get("error"))
            return []
    
    async def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        取得設備詳細資訊
        
        Args:
            device_id: 設備編號
            
        Returns:
            設備資訊
        """
        logger.info("HTTP: 取得設備詳細資訊", device_id=device_id)
        
        result = await self._call_tool(
            "get_device_info",
            {"device_id": device_id}
        )
        
        if result.get("success"):
            return result.get("data")
        else:
            logger.warning("取得設備資訊失敗", error=result.get("error"))
            return None
    
    async def get_recommended_devices(
        self,
        store_id: str,
        os_preference: str,
        budget: float,
        is_flagship: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        取得推薦設備
        
        Args:
            store_id: 門市編號
            os_preference: OS 偏好 (iOS/Android)
            budget: 預算
            is_flagship: 是否為旗艦機 (可選)
            
        Returns:
            推薦結果字典，包含 recommendations 列表和 reason
        """
        logger.info(
            "HTTP: 取得推薦設備",
            store_id=store_id,
            os_preference=os_preference,
            budget=budget,
            is_flagship=is_flagship
        )
        
        params = {
            "store_id": store_id,
            "os_preference": os_preference,
            "budget": budget
        }
        if is_flagship is not None:
            params["is_flagship"] = is_flagship
        
        result = await self._call_tool(
            "get_recommended_devices",
            params
        )
        
        if result.get("success"):
            return result.get("data", {})
        else:
            logger.warning("取得推薦設備失敗", error=result.get("error"))
            return {
                "recommendations": [],
                "reason": result.get("error", {}).get("message", "推薦失敗")
            }
    
    async def reserve_device(
        self,
        store_id: str,
        device_id: str,
        customer_id: str,
        phone_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        預約設備
        
        Args:
            store_id: 門市編號
            device_id: 設備編號
            customer_id: 客戶編號
            phone_number: 門號
            
        Returns:
            預約結果
        """
        logger.info(
            "HTTP: 預約設備",
            store_id=store_id,
            device_id=device_id,
            customer_id=customer_id,
            phone_number=phone_number
        )
        
        result = await self._call_tool(
            "reserve_device",
            {
                "store_id": store_id,
                "device_id": device_id,
                "customer_id": customer_id,
                "phone_number": phone_number
            }
        )
        
        if result.get("success"):
            return result.get("data")
        else:
            logger.warning("預約設備失敗", error=result.get("error"))
            return None
    
    async def get_device_pricing(
        self,
        device_id: str,
        plan_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        取得設備價格資訊
        
        Args:
            device_id: 設備編號
            plan_type: 方案類型 (攜碼/續約/新申辦等)
            
        Returns:
            價格資訊
        """
        logger.info(
            "HTTP: 取得設備價格資訊",
            device_id=device_id,
            plan_type=plan_type
        )
        
        params = {"device_id": device_id}
        if plan_type:
            params["plan_type"] = plan_type
        
        result = await self._call_tool(
            "get_device_pricing",
            params
        )
        
        if result.get("success"):
            return result.get("data")
        else:
            logger.warning("取得設備價格失敗", error=result.get("error"))
            return None
    
    async def close(self):
        """關閉 HTTP 客戶端"""
        if self.client:
            await self.client.aclose()
            logger.info("POS MCP Client HTTP 已關閉")


# 全域實例 (HTTP 模式)
mcp_client_pos_http = MCPClientServicePOSHTTP()
