"""
Promotion Service Factory

根據環境變數決定使用 Mock Service 或 MCP Client
"""
import os
import structlog
from typing import Union

from .promotion_service import MockPromotionService

logger = structlog.get_logger()


async def get_promotion_service() -> Union[MockPromotionService]:
    """取得 Promotion Service
    
    根據環境變數決定使用哪種 Service：
    - USE_MCP_PROMOTION=false (預設): 使用 MockPromotionService
    - USE_MCP_PROMOTION=true: 使用 MCP Client
    
    Returns:
        PromotionService 實例
    """
    # 在運行時讀取環境變數
    use_mcp = os.getenv('USE_MCP_PROMOTION', 'false').lower() == 'true'
    
    if not use_mcp:
        # 使用 Mock Service (預設)
        logger.info("使用 Mock Promotion Service")
        return MockPromotionService()
    
    # MCP Client 模式
    use_http = os.getenv('USE_HTTP_TRANSPORT', 'true').lower() == 'true'
    
    if use_http:
        # HTTP Transport
        logger.info("使用 Promotion MCP Service (HTTP)")
        from .mcp_client_promotion_http import mcp_client_promotion_http
        await mcp_client_promotion_http.initialize()
        return mcp_client_promotion_http
    else:
        # stdio Transport (尚未實作)
        logger.warning("Promotion MCP Client (stdio) 尚未實作，使用 Mock Service")
        return MockPromotionService()
