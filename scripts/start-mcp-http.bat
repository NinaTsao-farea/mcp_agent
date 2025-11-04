@echo off
REM 啟動 CRM MCP Server (HTTP Transport)
echo ============================================================
echo  CRM MCP Server (HTTP Transport)
echo ============================================================
echo.
echo 正在啟動 HTTP Server...
echo Port: 8001
echo Mode: Mock Data
echo.

cd /d %~dp0..\backend

REM 檢查是否已安裝依賴
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [錯誤] 缺少 FastAPI，正在安裝...
    pip install fastapi uvicorn[standard]
)

REM 啟動 Server
echo [啟動] uvicorn mcp_servers.crm_server_http:app --port 8001 --reload
echo.
echo ============================================================
echo Server 端點:
echo   - Health Check: http://localhost:8001/health
echo   - List Tools:   http://localhost:8001/mcp/tools  
echo   - Call Tool:    http://localhost:8001/mcp/call
echo ============================================================
echo.
echo 按 Ctrl+C 停止 Server
echo.

uvicorn mcp_servers.crm_server_http:app --port 8001 --reload

pause
