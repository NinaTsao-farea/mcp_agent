"""
POS MCP Server - HTTP Transport 版本

使用 FastAPI 提供 HTTP 端點，解決 Windows stdio 相容性問題

執行方式:
    uvicorn pos_server_http:app --host 0.0.0.0 --port 8002 --reload

測試方式:
    curl http://localhost:8002/health
    curl -X POST http://localhost:8002/mcp/tools
    curl -X POST http://localhost:8002/mcp/call -H "Content-Type: application/json" -d "{\"tool\":\"query_device_stock\",\"arguments\":{\"store_id\":\"STORE001\"}}"
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

from pos_server import POSServer

logger = structlog.get_logger()

# 建立 FastAPI 應用
app = FastAPI(
    title="POS MCP Server (HTTP)",
    description="POS MCP Server with HTTP Transport for Device Management",
    version="1.0.0"
)

# 初始化 POS Server
pos = POSServer()

# 請求/回應模型
class ToolCallRequest(BaseModel):
    """Tool 調用請求"""
    tool: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    """Tool 調用回應"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class ToolInfo(BaseModel):
    """Tool 資訊"""
    name: str
    description: str
    parameters: Dict[str, Any]


@app.get("/")
async def root():
    """根路徑 - API 資訊"""
    return {
        "service": "POS MCP Server (HTTP)",
        "version": "1.0.0",
        "status": "running",
        "transport": "HTTP",
        "tools_count": 5,
        "endpoints": {
            "tools": "/mcp/tools",
            "call": "/mcp/call",
            "health": "/health"
        },
        "tools": [
            "query_device_stock",
            "get_device_info",
            "get_recommended_devices",
            "reserve_device",
            "get_device_pricing"
        ]
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "POS MCP Server",
        "mode": "Mock" if pos.use_mock_data else "API",
        "devices_count": len(pos.mock_devices),
        "stores_count": len(pos.mock_stock)
    }


@app.get("/mcp/tools")
async def list_tools():
    """列出所有可用的 Tools"""
    tools = [
        {
            "name": "query_device_stock",
            "description": "查詢門市設備庫存狀況",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼 (例如: STORE001)",
                        "required": True
                    },
                    "os_filter": {
                        "type": "string",
                        "description": "作業系統過濾 (iOS 或 Android)",
                        "enum": ["iOS", "Android"],
                        "required": False
                    },
                    "min_price": {
                        "type": "number",
                        "description": "最低價格過濾",
                        "required": False
                    },
                    "max_price": {
                        "type": "number",
                        "description": "最高價格過濾",
                        "required": False
                    }
                }
            }
        },
        {
            "name": "get_device_info",
            "description": "取得設備詳細資訊",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼 (例如: DEV001)",
                        "required": True
                    }
                }
            }
        },
        {
            "name": "get_recommended_devices",
            "description": "根據客戶偏好取得推薦設備",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼",
                        "required": True
                    },
                    "os_preference": {
                        "type": "string",
                        "description": "作業系統偏好 (iOS 或 Android)",
                        "enum": ["iOS", "Android"],
                        "required": True
                    },
                    "budget": {
                        "type": "number",
                        "description": "預算上限",
                        "required": True
                    },
                    "is_flagship": {
                        "type": "boolean",
                        "description": "是否只要旗艦機",
                        "required": False
                    }
                }
            }
        },
        {
            "name": "reserve_device",
            "description": "預約設備（確保庫存保留）",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼",
                        "required": True
                    },
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼",
                        "required": True
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "客戶編號",
                        "required": True
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "門號",
                        "required": True
                    }
                }
            }
        },
        {
            "name": "get_device_pricing",
            "description": "取得設備價格資訊（含促銷價格）",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼",
                        "required": True
                    },
                    "plan_type": {
                        "type": "string",
                        "description": "方案類型 (攜碼/續約/新申辦)",
                        "required": False
                    }
                }
            }
        }
    ]
    
    return {
        "tools": tools,
        "count": len(tools)
    }


@app.post("/mcp/call")
async def call_tool(request: ToolCallRequest):
    """
    調用 POS Tool
    
    Body:
    {
        "tool": "query_device_stock",
        "arguments": {
            "store_id": "STORE001",
            "os_filter": "iOS"
        }
    }
    """
    try:
        tool_name = request.tool
        args = request.arguments
        
        logger.info("HTTP Tool Call", tool=tool_name, args=args)
        
        # 路由到對應的 Tool 方法
        if tool_name == "query_device_stock":
            result = await pos.query_device_stock(
                store_id=args.get("store_id"),
                os_filter=args.get("os_filter"),
                min_price=args.get("min_price"),
                max_price=args.get("max_price")
            )
        
        elif tool_name == "get_device_info":
            result = await pos.get_device_info(
                device_id=args.get("device_id")
            )
        
        elif tool_name == "get_recommended_devices":
            result = await pos.get_recommended_devices(
                store_id=args.get("store_id"),
                os_preference=args.get("os_preference"),
                budget=args.get("budget"),
                is_flagship=args.get("is_flagship")
            )
        
        elif tool_name == "reserve_device":
            result = await pos.reserve_device(
                store_id=args.get("store_id"),
                device_id=args.get("device_id"),
                customer_id=args.get("customer_id"),
                phone_number=args.get("phone_number")
            )
        
        elif tool_name == "get_device_pricing":
            result = await pos.get_device_pricing(
                device_id=args.get("device_id"),
                plan_type=args.get("plan_type")
            )
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # 返回結果
        if result.get("success"):
            return JSONResponse(content={
                "success": True,
                "data": result.get("data")
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result.get("error")
                }
            )
    
    except Exception as e:
        logger.error("Tool call failed", tool=tool_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("POS MCP Server (HTTP) 啟動")
    logger.info("可用 Tools", tools=5)
    logger.info("Mock 設備數量", devices=len(pos.mock_devices))
    logger.info("門市數量", stores=len(pos.mock_stock))
    print("\n" + "="*60)
    print("🚀 POS MCP Server (HTTP Transport) 已啟動")
    print("="*60)
    print(f"📍 URL: http://localhost:8002")
    print(f"📚 API Docs: http://localhost:8002/docs")
    print(f"🔧 Tools: 5 個")
    print(f"📦 設備: {len(pos.mock_devices)} 個")
    print(f"🏪 門市: {len(pos.mock_stock)} 間")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("POS MCP Server (HTTP) 關閉")
    print("\n👋 POS MCP Server (HTTP) 已關閉\n")


if __name__ == "__main__":
    import uvicorn
    
    # 從環境變數取得設定
    host = os.getenv("POS_MCP_HOST", "0.0.0.0")
    port = int(os.getenv("POS_MCP_PORT", "8002"))
    
    logger.info(
        "啟動 POS MCP HTTP Server",
        host=host,
        port=port
    )
    
    # 啟動 FastAPI
    uvicorn.run(
        "pos_server_http:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
