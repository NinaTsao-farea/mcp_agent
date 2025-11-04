@echo off
REM 測試 Promotion MCP Server HTTP 端點

echo ========================================
echo 測試 Promotion MCP Server HTTP
echo ========================================
echo.

cd /d "%~dp0.."

echo [1/6] 測試根端點...
curl http://localhost:8003/
echo.
echo.

echo [2/6] 測試健康檢查...
curl http://localhost:8003/health
echo.
echo.

echo [3/6] 測試取得 Tools Schema...
curl http://localhost:8003/mcp/tools
echo.
echo.

echo [4/6] 測試搜尋促銷 (吃到飽)...
curl -X POST http://localhost:8003/mcp/call ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\": \"search_promotions\", \"arguments\": {\"query\": \"吃到飽\", \"limit\": 3}}"
echo.
echo.

echo [5/6] 測試取得方案詳情...
curl -X POST http://localhost:8003/mcp/call ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\": \"get_plan_details\", \"arguments\": {\"plan_id\": \"PLAN001\"}}"
echo.
echo.

echo [6/6] 測試比較方案...
curl -X POST http://localhost:8003/mcp/call ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\": \"compare_plans\", \"arguments\": {\"plan_ids\": [\"PLAN001\", \"PLAN002\", \"PLAN003\"]}}"
echo.
echo.

echo ========================================
echo 測試完成
echo ========================================

pause
