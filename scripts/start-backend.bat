@echo off
REM 啟動後端服務腳本

echo 🚀 啟動電信門市銷售助理系統後端
echo ================================

cd /d D:\ai_project\test_mcp_agent2\backend

REM 檢查虛擬環境
if not exist "venv" (
    echo ❌ 虛擬環境不存在，請先執行 .\scripts\setup-dev.bat
    pause
    exit /b 1
)

REM 啟動虛擬環境
call venv\Scripts\activate.bat

REM 啟動應用程式
echo 🎯 啟動 Quart 後端服務...
echo 📍 API 端點: http://localhost:8000
echo 🔍 健康檢查: http://localhost:8000/health
echo 🔑 測試帳號: S001 / password
echo.
echo 📍 API 端點: http://localhost:8000
echo 🔍 健康檢查: http://localhost:8000/health
echo 📖 API 文件: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服務
echo.

python app.py