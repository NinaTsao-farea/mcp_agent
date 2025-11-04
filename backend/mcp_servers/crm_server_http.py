"""
CRM MCP Server - HTTP Transport 版本

使用 FastAPI 提供 HTTP 端點，解決 Windows stdio 相容性問題

執行方式:
    uvicorn crm_server_http:app --host 0.0.0.0 --port 8001 --reload

測試方式:
    curl -X POST http://localhost:8001/mcp/tools
    curl -X POST http://localhost:8001/mcp/call -d '{"tool":"get_customer","arguments":{"id_number":"A123456789"}}'
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog

# 添加 mcp_servers 目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from crm_server import CRMServer

logger = structlog.get_logger()

# 建立 FastAPI 應用
app = FastAPI(
    title="CRM MCP Server (HTTP)",
    description="CRM MCP Server with HTTP Transport",
    version="1.0.0"
)

# 初始化 CRM Server
crm = CRMServer()

# 請求/回應模型
class ToolCallRequest(BaseModel):
    """Tool 調用請求"""
    tool: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    """Tool 調用回應"""
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class ToolInfo(BaseModel):
    """Tool 資訊"""
    name: str
    description: str
    parameters: Dict[str, Any]


@app.get("/")
async def root():
    """根路徑 - API 資訊"""
    return {
        "service": "CRM MCP Server (HTTP)",
        "version": "1.0.0",
        "status": "running",
        "transport": "HTTP",
        "endpoints": {
            "tools": "/mcp/tools",
            "call": "/mcp/call",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "CRM MCP Server",
        "mode": "Mock" if crm.use_mock_data else "API"
    }


@app.get("/mcp/tools", response_model=List[ToolInfo])
async def list_tools():
    """列出所有可用的 Tools"""
    tools = [
        {
            "name": "get_customer",
            "description": "查詢客戶基本資料",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_number": {
                        "type": "string",
                        "description": "客戶身分證號（10位）"
                    }
                },
                "required": ["id_number"]
            }
        },
        {
            "name": "list_customer_phones",
            "description": "列出客戶所有門號",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "客戶編號"
                    }
                },
                "required": ["customer_id"]
            }
        },
        {
            "name": "get_phone_details",
            "description": "查詢門號詳細資訊",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "門號（10位）"
                    }
                },
                "required": ["phone_number"]
            }
        },
        {
            "name": "check_renewal_eligibility",
            "description": "檢查門號續約資格",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "門號"
                    },
                    "renewal_type": {
                        "type": "string",
                        "description": "續約類型 (single/with_device)",
                        "enum": ["single", "with_device"]
                    }
                },
                "required": ["phone_number", "renewal_type"]
            }
        },
        {
            "name": "check_promotion_eligibility",
            "description": "檢查促銷資格",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "門號"
                    },
                    "promotion_id": {
                        "type": "string",
                        "description": "促銷編號"
                    }
                },
                "required": ["phone_number", "promotion_id"]
            }
        }
    ]
    
    logger.info("列出 Tools", count=len(tools))
    return tools


@app.post("/mcp/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """
    調用指定的 Tool
    
    Args:
        request: Tool 調用請求（包含 tool 名稱和 arguments）
        
    Returns:
        Tool 執行結果
    """
    logger.info("收到 Tool 調用請求", tool=request.tool, arguments=request.arguments)
    
    try:
        # 路由到對應的 CRM 方法
        if request.tool == "get_customer":
            result = await crm.get_customer(**request.arguments)
        elif request.tool == "list_customer_phones":
            result = await crm.list_customer_phones(**request.arguments)
        elif request.tool == "get_phone_details":
            result = await crm.get_phone_details(**request.arguments)
        elif request.tool == "check_renewal_eligibility":
            result = await crm.check_renewal_eligibility(**request.arguments)
        elif request.tool == "check_promotion_eligibility":
            result = await crm.check_promotion_eligibility(**request.arguments)
        else:
            logger.error("未知的 Tool", tool=request.tool)
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "TOOL_NOT_FOUND",
                        "message": f"Tool '{request.tool}' 不存在"
                    }
                }
            )
        
        # CRM 方法已經返回標準格式 {success: bool, data/error: ...}
        logger.info("Tool 調用完成", tool=request.tool, success=result.get("success"))
        return result
        
    except Exception as e:
        logger.error("Tool 調用失敗", tool=request.tool, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        )


# 啟動訊息
@app.on_event("startup")
async def startup_event():
    logger.info("="*60)
    logger.info("CRM MCP Server (HTTP) 啟動成功")
    logger.info("="*60)
    logger.info("Transport: HTTP")
    logger.info("Mode: Mock" if crm.use_mock_data else "API")
    logger.info("Endpoints:")
    logger.info("  - Health: http://localhost:8001/health")
    logger.info("  - List Tools: http://localhost:8001/mcp/tools")
    logger.info("  - Call Tool: http://localhost:8001/mcp/call")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("CRM MCP Server (HTTP) 關閉")


if __name__ == "__main__":
    import uvicorn
    
    # 從環境變數取得設定
    host = os.getenv("CRM_MCP_HOST", "0.0.0.0")
    port = int(os.getenv("CRM_MCP_PORT", "8001"))
    
    logger.info(
        "啟動 CRM MCP HTTP Server",
        host=host,
        port=port
    )
    
    # 開發模式啟動
    uvicorn.run(
        "crm_server_http:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
