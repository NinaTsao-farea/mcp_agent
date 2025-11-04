"""
CRM 服務工廠
根據環境配置返回適當的 CRM 服務實例
"""
import os
from typing import Union
import structlog

from .crm_service import MockCRMService

logger = structlog.get_logger()

# 從環境變數讀取配置
USE_MCP = os.getenv('USE_MCP_CRM', 'false').lower() == 'true'


def get_crm_service() -> Union[MockCRMService, 'MCPClientService']:
    """
    取得 CRM 服務實例
    
    開發階段: 返回 MockCRMService
    Sprint 3 後: 可切換為 MCPClientService
    
    環境變數:
        USE_MCP_CRM: 'true' 使用 MCP, 'false' 使用 Mock (預設)
    
    Returns:
        CRM 服務實例 (Mock 或 MCP)
    """
    if USE_MCP:
        logger.info("使用 MCP CRM Service")
        # Sprint 3 實作後引入
        from .mcp_client import mcp_client
        return mcp_client
    else:
        logger.debug("使用 Mock CRM Service")
        return MockCRMService()
