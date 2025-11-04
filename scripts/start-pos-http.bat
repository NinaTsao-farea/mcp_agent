@echo off
REM 啟動 POS MCP Server (HTTP Transport)

echo ======================================
echo 啟動 POS MCP Server (HTTP)
echo ======================================
echo.

cd /d "%~dp0\..\backend"

echo 正在啟動服務器...
echo URL: http://localhost:8002
echo API Docs: http://localhost:8002/docs
echo.

uvicorn mcp_servers.pos_server_http:app --host 0.0.0.0 --port 8002 --reload
