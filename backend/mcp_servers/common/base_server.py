"""
MCP Server 基礎類別

提供共用的功能：
- 錯誤處理
- 日誌記錄
- 回傳格式標準化
"""
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()


class BaseMCPServer:
    """
    MCP Server 基礎類別
    
    所有 MCP Server 應繼承此類別以獲得標準化的功能
    """
    
    def __init__(self, server_name: str):
        """
        初始化
        
        Args:
            server_name: Server 名稱 (用於日誌記錄)
        """
        self.server_name = server_name
        logger.info(f"初始化 {server_name}")
    
    def success_response(self, data: Any) -> Dict[str, Any]:
        """
        成功回應格式
        
        Args:
            data: 回傳的資料
            
        Returns:
            標準化的成功回應
        """
        return {
            "success": True,
            "data": data
        }
    
    def error_response(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        錯誤回應格式
        
        Args:
            error_code: 錯誤代碼
            message: 錯誤訊息
            details: 額外的錯誤細節
            
        Returns:
            標準化的錯誤回應
        """
        response = {
            "success": False,
            "error_code": error_code,
            "message": message
        }
        if details:
            response["details"] = details
        return response
    
    async def handle_error(
        self,
        error: Exception,
        context: str
    ) -> Dict[str, Any]:
        """
        統一錯誤處理
        
        Args:
            error: 例外物件
            context: 錯誤發生的上下文
            
        Returns:
            標準化的錯誤回應
        """
        logger.error(
            f"{self.server_name} 錯誤",
            context=context,
            error=str(error),
            error_type=type(error).__name__,
            exc_info=True
        )
        
        return self.error_response(
            error_code="INTERNAL_ERROR",
            message=f"{context}時發生錯誤",
            details={"error_type": type(error).__name__}
        )
    
    def validate_required_params(
        self,
        params: Dict[str, Any],
        required: list[str]
    ) -> Optional[Dict[str, Any]]:
        """
        驗證必要參數
        
        Args:
            params: 參數字典
            required: 必要參數列表
            
        Returns:
            如果驗證失敗返回錯誤回應，成功返回 None
        """
        missing = [key for key in required if key not in params or params[key] is None]
        
        if missing:
            return self.error_response(
                error_code="INVALID_PARAMS",
                message=f"缺少必要參數: {', '.join(missing)}",
                details={"missing_params": missing}
            )
        
        return None


class MCPToolError(Exception):
    """MCP Tool 執行錯誤"""
    
    def __init__(self, error_code: str, message: str, details: Optional[Dict] = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)
