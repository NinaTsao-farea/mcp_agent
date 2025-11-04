@echo off
REM 測試 POS MCP Server (HTTP Transport)

echo ======================================
echo 測試 POS MCP Server (HTTP)
echo ======================================
echo.

cd /d "%~dp0\..\backend"

echo 執行 HTTP Transport 測試...
echo.

python test_pos_http.py

echo.
echo 測試完成！
pause
