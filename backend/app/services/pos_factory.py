"""
POS Service Factory

根據環境變數決定使用 Mock POS Service 或 POS MCP Client
"""
import os
import structlog
from typing import Union

from .pos_service import MockPOSService

logger = structlog.get_logger()


async def get_pos_service():
    """
    取得 POS 服務實例
    
    根據環境變數決定返回：
    - Mock POS Service (預設)
    - POS MCP Client (HTTP Transport)
    - POS MCP Client (stdio Transport)
    
    環境變數:
        USE_MCP_POS: 是否使用 MCP (預設: false)
        USE_HTTP_TRANSPORT: 是否使用 HTTP Transport (預設: true)
    """
    # 在運行時讀取環境變數，而不是在模組載入時
    use_mcp = os.getenv('USE_MCP_POS', 'false').lower() == 'true'
    use_http_transport = os.getenv('USE_HTTP_TRANSPORT', 'true').lower() == 'true'
    
    if use_mcp:
        if use_http_transport:
            logger.info("使用 POS MCP Service (HTTP)")
            from .mcp_client_pos_http import mcp_client_pos_http
            await mcp_client_pos_http.initialize()
            return mcp_client_pos_http
        else:
            logger.info("使用 POS MCP Service (stdio)")
            # TODO: 實作 POS MCP Client stdio
            # from .mcp_client_pos import mcp_client_pos
            # await mcp_client_pos.initialize()
            # return mcp_client_pos
            logger.warning("POS MCP Client (stdio) 尚未實作，使用 Mock Service")
            return MockPOSService()
    else:
        logger.debug("使用 Mock POS Service")
        return MockPOSService()
