"""
Promotion MCP Server - HTTP Transport

透過 FastAPI 提供 HTTP 端點存取 Promotion MCP Server
用於整合測試與開發模式

啟動方式:
    python promotion_server_http.py
    或使用腳本: .\scripts\start-promotion-http.bat

API 端點:
    GET  /              - 服務資訊
    GET  /health        - 健康檢查
    GET  /mcp/tools     - 取得所有 Tools Schema
    POST /mcp/call      - 呼叫指定 Tool
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 添加路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from promotion_server import PromotionServer

# 設定 structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# FastAPI App
app = FastAPI(
    title="Promotion MCP Server",
    description="促銷方案管理 MCP Server (HTTP Transport)",
    version="1.0.0"
)

# Promotion Server 實例
promotion_server: PromotionServer = None


class MCPCallRequest(BaseModel):
    """MCP Tool 呼叫請求"""
    tool: str
    arguments: Dict[str, Any]


class MCPCallResponse(BaseModel):
    """MCP Tool 呼叫回應"""
    success: bool
    result: Any = None
    error: str = None


@app.on_event("startup")
async def startup_event():
    """啟動事件"""
    global promotion_server
    
    logger.info("啟動 Promotion MCP Server (HTTP Transport)")
    
    # 建立 Promotion Server
    promotion_server = PromotionServer()
    
    logger.info(
        "Promotion MCP Server HTTP Transport 已啟動",
        promotions_count=len(promotion_server.promotions),
        plans_count=len(promotion_server.plans)
    )


@app.get("/")
async def root():
    """服務資訊"""
    return {
        "service": "Promotion MCP Server",
        "version": "1.0.0",
        "transport": "HTTP",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "tools": "/mcp/tools",
            "call": "/mcp/call"
        },
        "tools": [
            "search_promotions",
            "get_plan_details",
            "compare_plans",
            "calculate_upgrade_cost"
        ]
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "service": "promotion-mcp-server",
        "promotions_count": len(promotion_server.promotions) if promotion_server else 0,
        "plans_count": len(promotion_server.plans) if promotion_server else 0
    }


@app.get("/mcp/tools")
async def get_tools():
    """取得所有 Tools Schema"""
    if not promotion_server:
        raise HTTPException(status_code=500, detail="Promotion Server 未初始化")
    
    try:
        tools = promotion_server.get_tools_schema()
        
        return {
            "tools": tools,
            "count": len(tools)
        }
        
    except Exception as e:
        logger.error("取得 Tools Schema 失敗", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/call")
async def call_tool(request: MCPCallRequest) -> MCPCallResponse:
    """呼叫 MCP Tool"""
    if not promotion_server:
        raise HTTPException(status_code=500, detail="Promotion Server 未初始化")
    
    logger.info(
        "呼叫 MCP Tool",
        tool=request.tool,
        arguments=request.arguments
    )
    
    try:
        # 根據 Tool 名稱呼叫對應方法
        if request.tool == "search_promotions":
            result = await promotion_server.search_promotions(**request.arguments)
            
        elif request.tool == "get_plan_details":
            result = await promotion_server.get_plan_details(**request.arguments)
            
        elif request.tool == "compare_plans":
            result = await promotion_server.compare_plans(**request.arguments)
            
        elif request.tool == "calculate_upgrade_cost":
            result = await promotion_server.calculate_upgrade_cost(**request.arguments)
            
        else:
            logger.warning("未知的 Tool", tool=request.tool)
            return MCPCallResponse(
                success=False,
                error=f"未知的 Tool: {request.tool}"
            )
        
        logger.info("Tool 呼叫成功", tool=request.tool)
        
        return MCPCallResponse(
            success=True,
            result=result
        )
        
    except Exception as e:
        logger.error(
            "Tool 呼叫失敗",
            tool=request.tool,
            error=str(e)
        )
        
        return MCPCallResponse(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    
    # 從環境變數取得設定
    host = os.getenv("PROMOTION_MCP_HOST", "0.0.0.0")
    port = int(os.getenv("PROMOTION_MCP_PORT", "8003"))
    
    logger.info(
        "啟動 Promotion MCP HTTP Server",
        host=host,
        port=port
    )
    
    # 啟動 FastAPI
    uvicorn.run(
        "promotion_server_http:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
