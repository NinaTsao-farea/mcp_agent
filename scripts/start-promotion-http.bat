@echo off
REM 啟動 Promotion MCP Server (HTTP Transport)
REM Port: 8003

echo ========================================
echo Promotion MCP Server - HTTP Transport
echo ========================================
echo.
echo 啟動中...
echo Port: 8003
echo.

cd /d "%~dp0.."
python backend\mcp_servers\promotion_server_http.py

pause
