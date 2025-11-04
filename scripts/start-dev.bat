@echo off
REM 電信門市銷售助理系統 - Windows 開發環境快速啟動腳本

echo 🚀 啟動電信門市銷售助理系統開發環境
echo ==========================================

REM 檢查是否在專案根目錄
if not exist "README.md" (
    echo ❌ 請在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 1. 啟動後端
echo 📡 啟動後端服務...
cd backend

REM 檢查虛擬環境
if not exist "venv" (
    echo 📦 建立 Python 虛擬環境...
    python -m venv venv
)

REM 啟動虛擬環境
call venv\Scripts\activate.bat

REM 安裝依賴
echo 📦 安裝 Python 依賴...
pip install -r requirements.txt

REM 檢查環境變數
if not exist ".env" (
    echo ⚙️ 建立環境變數檔案...
    copy .env.example .env
    echo ⚠️ 請編輯 backend\.env 檔案，填入正確的資料庫和服務設定
)

REM 在新視窗啟動後端
echo 🎯 啟動 Quart 後端服務 (port 8000)...
start "Backend Server" cmd /k "cd /d D:\ai_project\test_mcp_agent2\backend && venv\Scripts\activate.bat && python app.py"

cd ..

REM 2. 啟動前端
echo 🎨 啟動前端服務...
cd frontend

REM 檢查 node_modules
if not exist "node_modules" (
    echo 📦 安裝 Node.js 依賴...
    pnpm install
)

REM 檢查環境變數
if not exist ".env" (
    echo ⚙️ 建立前端環境變數檔案...
    copy .env.example .env
)

REM 啟動前端
echo 🎯 啟動 Nuxt 前端服務 (port 3000)...
start "Frontend Server" cmd /k "cd /d D:\ai_project\test_mcp_agent2\frontend && pnpm run dev"

cd ..

echo.
echo ✅ 系統啟動完成！
echo ==========================================
echo 🌐 前端: http://localhost:3000
echo 📡 後端: http://localhost:8000
echo 🔍 API 健康檢查: http://localhost:8000/health
echo.
echo 測試帳號：
echo 員工編號: S001
echo 密碼: password
echo.
echo 關閉對應的命令視窗來停止服務
pause