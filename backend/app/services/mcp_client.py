"""
MCP Client Service - 統一管理 MCP Server 連線
"""
from typing import Optional, Dict, List, Any
import structlog
import os
import json
from pathlib import Path

logger = structlog.get_logger()


class MCPClientService:
    """
    MCP Client 服務
    
    統一管理所有 MCP Server (CRM, POS, Promotion) 的連線
    提供與 MockCRMService 相同的介面以便無縫切換
    """
    
    def __init__(self):
        self._crm_session: Optional[Any] = None
        self._crm_read_stream: Optional[Any] = None
        self._crm_write_stream: Optional[Any] = None
        self._crm_exit_stack: Optional[Any] = None
        
        self._pos_session: Optional[Any] = None
        self._promotion_session: Optional[Any] = None
        self._initialized = False
        
        logger.info("MCP Client Service 已建立")
        
    async def initialize(self):
        """初始化所有 MCP Server 連線"""
        if self._initialized:
            logger.warning("MCP Client 已初始化")
            return
            
        logger.info("初始化 MCP Client Service")
        
        # Sprint 3: 連接 CRM MCP Server
        await self._connect_crm()
        
        # Sprint 4: 連接 POS MCP Server
        # await self._connect_pos()
        
        # Sprint 5: 連接 Promotion MCP Server
        # await self._connect_promotion()
        
        self._initialized = True
        logger.info("MCP Client Service 初始化完成")
    
    async def _connect_crm(self):
        """連接 CRM MCP Server"""
        logger.info("連接 CRM MCP Server")
        
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except ImportError:
            logger.error("找不到 mcp 套件，請執行: pip install mcp")
            raise
        
        # 取得 CRM Server 路徑
        backend_dir = Path(__file__).parent.parent.parent
        crm_server_path = backend_dir / "mcp_servers" / "crm_server.py"
        
        if not crm_server_path.exists():
            logger.error(f"找不到 CRM Server: {crm_server_path}")
            raise FileNotFoundError(f"CRM Server 不存在: {crm_server_path}")
        
        # 設定 Server 參數
        command = os.getenv("MCP_CRM_COMMAND", "python")
        args = [str(crm_server_path)]
        
        # 可選環境變數
        env = {}
        if os.getenv("MCP_CRM_API_URL"):
            env["CRM_API_URL"] = os.getenv("MCP_CRM_API_URL")
        if os.getenv("MCP_CRM_API_KEY"):
            env["CRM_API_KEY"] = os.getenv("MCP_CRM_API_KEY")
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env if env else None
        )
        
        logger.info(f"啟動 CRM MCP Server: {command} {' '.join(args)}")
        
        # 建立 stdio 連線（使用 context manager）
        self._crm_exit_stack = stdio_client(server_params)
        read, write = await self._crm_exit_stack.__aenter__()
        
        self._crm_read_stream = read
        self._crm_write_stream = write
        
        # 建立 ClientSession
        self._crm_session = ClientSession(read, write)
        
        # 初始化 session
        await self._crm_session.__aenter__()
        
        logger.info("CRM MCP Server 連接成功")
    
    async def _connect_pos(self):
        """連接 POS MCP Server (Sprint 4)"""
        logger.info("連接 POS MCP Server (待實作)")
        pass
    
    async def _connect_promotion(self):
        """連接 Promotion MCP Server (Sprint 5)"""
        logger.info("連接 Promotion MCP Server (待實作)")
        pass
    
    async def close(self):
        """關閉所有連線"""
        logger.info("關閉 MCP Client Service")
        
        if self._crm_session:
            try:
                # 關閉 ClientSession
                await self._crm_session.__aexit__(None, None, None)
                logger.info("CRM Session 已關閉")
            except Exception as e:
                logger.error("關閉 CRM Session 失敗", error=str(e))
        
        if self._crm_exit_stack:
            try:
                # 關閉 stdio_client
                await self._crm_exit_stack.__aexit__(None, None, None)
                logger.info("CRM stdio 已關閉")
            except Exception as e:
                logger.error("關閉 CRM stdio 失敗", error=str(e))
        
        if self._pos_session:
            # Sprint 4
            pass
        
        if self._promotion_session:
            # Sprint 5
            pass
        
        self._initialized = False
        logger.info("MCP Client Service 已關閉")
    
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
        logger.info("MCP: 查詢客戶", id_number=id_number[:3] + "***")
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "get_customer",
                {"id_number": id_number}
            )
            
            # 解析 MCP 回應
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    return response_data.get("data")
                else:
                    logger.warning("查詢客戶失敗", error=response_data.get("error"))
                    return None
            
            return None
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="get_customer", error=str(e))
            raise
    
    async def get_customer_phones(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        取得客戶的所有門號
        
        Args:
            customer_id: 客戶 ID
            
        Returns:
            門號列表
        """
        logger.info("MCP: 查詢客戶門號", customer_id=customer_id)
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "list_customer_phones",
                {"customer_id": customer_id}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    return response_data.get("data", [])
                else:
                    logger.warning("查詢門號失敗", error=response_data.get("error"))
                    return []
            
            return []
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="list_customer_phones", error=str(e))
            raise
    
    async def get_phone_contract(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的合約資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            合約資訊
        """
        logger.info("MCP: 查詢門號合約", phone_number=phone_number)
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "get_phone_details",
                {"phone_number": phone_number}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    data = response_data.get("data", {})
                    return data.get("contract_info")
                else:
                    logger.warning("查詢合約失敗", error=response_data.get("error"))
                    return None
            
            return None
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="get_phone_details", error=str(e))
            raise
    
    async def get_phone_usage(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的使用量資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            使用量資訊
        """
        logger.info("MCP: 查詢門號使用量", phone_number=phone_number)
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "get_phone_details",
                {"phone_number": phone_number}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    data = response_data.get("data", {})
                    return data.get("usage_info")
                else:
                    logger.warning("查詢使用量失敗", error=response_data.get("error"))
                    return None
            
            return None
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="get_phone_details", error=str(e))
            raise
    
    async def get_phone_billing(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的帳單資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            帳單資訊
        """
        logger.info("MCP: 查詢門號帳單", phone_number=phone_number)
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "get_phone_details",
                {"phone_number": phone_number}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    data = response_data.get("data", {})
                    return data.get("billing_info")
                else:
                    logger.warning("查詢帳單失敗", error=response_data.get("error"))
                    return None
            
            return None
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="get_phone_details", error=str(e))
            raise
    
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
        logger.info("MCP: 檢查續約資格", phone_number=phone_number, customer_id=customer_id)
        
        if not self._crm_session:
            logger.error("CRM Session 未初始化")
            raise RuntimeError("MCP Client 未初始化，請先呼叫 initialize()")
        
        try:
            result = await self._crm_session.call_tool(
                "check_renewal_eligibility",
                {
                    "phone_number": phone_number,
                    "renewal_type": renewal_type
                }
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                if response_data.get("success"):
                    eligibility_data = response_data.get("data", {})
                    
                    # 轉換為與 MockCRMService 相同的格式
                    return {
                        "eligible": eligibility_data.get("is_eligible", False),
                        "reasons": eligibility_data.get("reasons", []),
                        "contract_end_date": eligibility_data.get("contract_end_date"),
                        "days_until_expiry": eligibility_data.get("days_until_expiry"),
                        "credit_score": eligibility_data.get("credit_score", "A"),
                        "has_outstanding_debt": eligibility_data.get("has_outstanding_debt", False)
                    }
                else:
                    logger.warning("檢查資格失敗", error=response_data.get("error"))
                    return {
                        "eligible": False,
                        "reasons": [response_data.get("error", {}).get("message", "未知錯誤")]
                    }
            
            return {"eligible": False, "reasons": ["無法取得回應"]}
            
        except Exception as e:
            logger.error("MCP 調用失敗", tool="check_renewal_eligibility", error=str(e))
            raise


# 全域實例 (應用程式啟動時初始化)
mcp_client = MCPClientService()
