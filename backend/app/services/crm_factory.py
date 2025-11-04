import os
import structlog
from typing import Union

from .crm_service import MockCRMService

logger = structlog.get_logger()

async def get_crm_service() -> Union[MockCRMService]: 
    """取得 CRM 服務實例"""
    # 每次呼叫時才讀取環境變數，避免在模組載入時就固定值
    use_mcp = os.getenv('USE_MCP_CRM', 'false').lower() == 'true'
    use_http_transport = os.getenv('USE_HTTP_TRANSPORT', 'true').lower() == 'true'
    
    if use_mcp:
        if use_http_transport:
            logger.info("使用 MCP CRM Service (HTTP)")
            from .mcp_client_http import mcp_client_http
            await mcp_client_http.initialize()
            return mcp_client_http
        else:
            logger.info("使用 MCP CRM Service (stdio)")
            from .mcp_client import mcp_client
            await mcp_client.initialize()
            return mcp_client
    else:
        # 使用 Mock Service (預設)
        logger.debug("使用 Mock CRM Service")
        return MockCRMService()
    