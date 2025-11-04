@echo off
REM 測試 CRM MCP Server (HTTP Transport)
echo ============================================================
echo  測試 MCP HTTP Transport
echo ============================================================
echo.
echo 確保 Server 已啟動: scripts\start-mcp-http.bat
echo.
pause

cd /d %~dp0..\backend

echo.
echo [測試 1/3] Health Check...
curl -s http://localhost:8001/health
echo.
echo.

echo [測試 2/3] List Tools...
curl -s http://localhost:8001/mcp/tools | python -m json.tool
echo.
echo.

echo [測試 3/3] Call Tool (get_customer)...
curl -s -X POST http://localhost:8001/mcp/call ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\":\"get_customer\",\"arguments\":{\"id_number\":\"A123456789\"}}" | python -m json.tool
echo.
echo.

echo ============================================================
echo 執行完整測試套件...
echo ============================================================
python test_mcp_http.py

pause
