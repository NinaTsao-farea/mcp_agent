"""
MCP Client Service - HTTP Transport 版本

使用 HTTP 連接 MCP Server，解決 Windows stdio 相容性問題
"""
from typing import Optional, Dict, List, Any
import structlog
import os
import httpx
from pathlib import Path

logger = structlog.get_logger()


class MCPClientServiceHTTP:
    """
    MCP Client 服務 (HTTP Transport)
    
    使用 HTTP 連接 MCP Server，提供與 MockCRMService 相同的介面
    """
    
    def __init__(self, base_url: str = None):
        """
        初始化 HTTP Client
        
        Args:
            base_url: MCP Server 的 HTTP URL，預設從環境變數讀取
        """
        self.base_url = base_url or os.getenv("MCP_CRM_HTTP_URL", "http://localhost:8001")
        self.client: Optional[httpx.AsyncClient] = None
        self.initialized = False
        
        logger.info("MCP Client Service (HTTP) 已建立", base_url=self.base_url)
        
    async def initialize(self):
        """初始化 HTTP Client"""
        if self.initialized:
            logger.warning("MCP Client 已初始化")
            return
            
        logger.info("初始化 MCP Client Service (HTTP)")
        
        # 建立 HTTP Client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MCP-Client-HTTP/1.0"
            }
        )
        
        # 健康檢查
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            health = response.json()
            logger.info("MCP Server 連接成功", health=health)
        except Exception as e:
            logger.error("無法連接 MCP Server", error=str(e), url=self.base_url)
            raise RuntimeError(f"無法連接 MCP Server: {e}")
        
        self.initialized = True
        logger.info("MCP Client Service (HTTP) 初始化完成")
    
    async def close(self):
        """關閉 HTTP Client"""
        logger.info("關閉 MCP Client Service (HTTP)")
        
        if self.client:
            await self.client.aclose()
            logger.info("HTTP Client 已關閉")
        
        self.initialized = False
    
    async def _call_tool(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        調用 MCP Tool
        
        Args:
            tool: Tool 名稱
            arguments: Tool 參數
            
        Returns:
            Tool 執行結果
        """
        if not self.client:
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            response = await self.client.post(
                "/mcp/call",
                json={
                    "tool": tool,
                    "arguments": arguments
                }
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug("Tool 調用成功", tool=tool, success=result.get("success"))
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP 錯誤", tool=tool, status=e.response.status_code)
            # 嘗試解析錯誤訊息
            try:
                error_detail = e.response.json()
                return error_detail
            except:
                return {
                    "success": False,
                    "error": {
                        "code": "HTTP_ERROR",
                        "message": f"HTTP {e.response.status_code}: {str(e)}"
                    }
                }
        except Exception as e:
            logger.error("Tool 調用失敗", tool=tool, error=str(e))
            return {
                "success": False,
                "error": {
                    "code": "CALL_ERROR",
                    "message": str(e)
                }
            }
    
    # ========================================
    # CRM Tools (與 MockCRMService 保持相同介面)
    # ========================================
    
    async def query_customer_by_id(self, id_number: str) -> Optional[Dict[str, Any]]:
        """
        透過身分證號查詢客戶
        
        Args:
            id_number: 身分證號
            
        Returns:
            客戶資料，若不存在則返回 None
        """
        logger.info("HTTP: 查詢客戶", id_number=id_number[:3] + "***")
        
        result = await self._call_tool("get_customer", {"id_number": id_number})
        
        if result.get("success"):
            customer_data = result.get("data")
            # 加入資料來源標記
            if customer_data:
                customer_data["_data_source"] = "MCP_CRM_Server"
            return customer_data
        else:
            logger.warning("查詢客戶失敗", error=result.get("error"))
            return None
    
    async def get_customer_phones(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        取得客戶的所有門號
        
        Args:
            customer_id: 客戶 ID
            
        Returns:
            門號列表
        """
        logger.info("HTTP: 查詢客戶門號", customer_id=customer_id)
        
        result = await self._call_tool("list_customer_phones", {"customer_id": customer_id})
        
        if result.get("success"):
            phones = result.get("data", [])
            # 加入資料來源標記
            for phone in phones:
                phone["_data_source"] = "MCP_CRM_Server"
            return phones
        else:
            logger.warning("查詢門號失敗", error=result.get("error"))
            return []
    
    async def get_phone_contract(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的合約資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            合約資訊
        """
        logger.info("HTTP: 查詢門號合約", phone_number=phone_number)
        
        result = await self._call_tool("get_phone_details", {"phone_number": phone_number})
        
        if result.get("success"):
            data = result.get("data", {})
            return data.get("contract_info")
        else:
            logger.warning("查詢合約失敗", error=result.get("error"))
            return None
    
    async def get_phone_usage(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的使用量資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            使用量資訊
        """
        logger.info("HTTP: 查詢門號使用量", phone_number=phone_number)
        
        result = await self._call_tool("get_phone_details", {"phone_number": phone_number})
        
        if result.get("success"):
            data = result.get("data", {})
            return data.get("usage_info")
        else:
            logger.warning("查詢使用量失敗", error=result.get("error"))
            return None
    
    async def get_phone_billing(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的帳單資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            帳單資訊
        """
        logger.info("HTTP: 查詢門號帳單", phone_number=phone_number)
        
        result = await self._call_tool("get_phone_details", {"phone_number": phone_number})
        
        if result.get("success"):
            data = result.get("data", {})
            return data.get("billing_info")
        else:
            logger.warning("查詢帳單失敗", error=result.get("error"))
            return None
    
    async def check_eligibility(
        self,
        phone_number: str,
        customer_id: str,
        renewal_type: str = "single"
    ) -> Dict[str, Any]:
        """
        檢查續約資格
        
        Args:
            phone_number: 門號
            customer_id: 客戶 ID
            renewal_type: 續約類型 (single/with_device)
            
        Returns:
            資格檢查結果
        """
        logger.info("HTTP: 檢查續約資格", phone_number=phone_number, customer_id=customer_id)
        
        result = await self._call_tool(
            "check_renewal_eligibility",
            {
                "phone_number": phone_number,
                "renewal_type": renewal_type
            }
        )
        
        if result.get("success"):
            eligibility_data = result.get("data", {})
            
            # 轉換為與 MockCRMService 相同的格式
            is_eligible = eligibility_data.get("is_eligible", False)
            
            # MCP Server 的 details 已經是正確的格式
            details = eligibility_data.get("details", [])
            
            # 如果沒有 details，但有 reasons (字符串列表)，轉換為 details 格式
            if not details and eligibility_data.get("reasons"):
                reasons_list = eligibility_data.get("reasons", [])
                details = [{
                    "item": "資格檢查",
                    "status": "fail",
                    "message": reason
                } for reason in reasons_list if isinstance(reason, str)]
            
            return {
                "eligible": is_eligible,
                "reason": "符合續約資格" if is_eligible else "不符合續約資格",
                "details": details,
                "contract_end_date": eligibility_data.get("contract_end_date"),
                "days_to_expiry": eligibility_data.get("days_until_expiry", 0)
            }
        else:
            logger.warning("檢查資格失敗", error=result.get("error"))
            return {
                "eligible": False,
                "reason": result.get("error", {}).get("message", "未知錯誤"),
                "details": []
            }


# 全域實例 (HTTP 模式)
mcp_client_http = MCPClientServiceHTTP()
