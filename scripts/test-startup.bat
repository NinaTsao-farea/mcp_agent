@echo off
REM 系統啟動測試腳本

echo 🧪 電信門市銷售助理系統啟動測試
echo ===================================

echo.
echo 📋 測試項目：
echo   1. 前端 Nuxt 開發伺服器
echo   2. 後端 Quart API 伺服器
echo   3. 系統整合測試
echo.

pause

echo.
echo 🎨 測試前端啟動...
echo -----------------
cd /d D:\ai_project\test_mcp_agent2\frontend

REM 檢查前端依賴
if not exist "node_modules" (
    echo 📦 安裝前端依賴...
    pnpm install
)

REM 測試前端啟動（背景）
echo 🚀 啟動前端測試...
start /min "Frontend Test" cmd /c "pnpm run dev"

REM 等待前端啟動
timeout /t 5 /nobreak > nul

echo.
echo 📡 測試後端啟動...
echo -----------------
cd /d D:\ai_project\test_mcp_agent2\backend

REM 檢查後端依賴
if not exist "venv" (
    echo ❌ 後端虛擬環境不存在
    echo 請先執行: .\scripts\setup-dev.bat
    pause
    exit /b 1
)

REM 測試後端啟動（背景）
echo 🚀 啟動後端測試...
start /min "Backend Test" cmd /c "venv\Scripts\activate.bat && python app.py"

REM 等待後端啟動
timeout /t 3 /nobreak > nul

echo.
echo ✅ 啟動測試完成！
echo ==================
echo.
echo 📍 前端地址: http://localhost:3000
echo 📍 後端地址: http://localhost:8000
echo 🔍 健康檢查: http://localhost:8000/health
echo.
echo 🔑 測試帳號：
echo    員工編號: S001
echo    密碼: password
echo.
echo 請在瀏覽器中測試上述地址
echo 按任意鍵關閉測試服務...

pause

echo.
echo 🛑 關閉測試服務...
taskkill /f /im "node.exe" 2>nul
taskkill /f /im "python.exe" 2>nul

echo ✅ 測試完成