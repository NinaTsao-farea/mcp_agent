@echo off
REM ================================================================================
REM 前端整合測試 - 快速啟動腳本
REM ================================================================================

echo.
echo ================================================================================
echo 前端整合測試 - 快速啟動
echo ================================================================================
echo.

REM 檢查目錄
if not exist "backend\app.py" (
    echo [錯誤] 找不到 backend\app.py
    echo 請確認在專案根目錄執行此腳本
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [錯誤] 找不到 frontend\package.json
    echo 請確認在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 啟動後端
echo [1/2] 啟動後端服務...
echo.
start "Backend Server" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul

REM 啟動前端
echo [2/2] 啟動前端服務...
echo.
start "Frontend Server" cmd /k "cd frontend && pnpm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo 服務啟動完成！
echo ================================================================================
echo.
echo 後端: http://localhost:5000
echo 前端: http://localhost:3000
echo.
echo 請等待 3-5 秒讓服務完全啟動，然後訪問:
echo   http://localhost:3000/renewal/start
echo.
echo 按任意鍵開啟瀏覽器...
pause >nul

REM 開啟瀏覽器
start http://localhost:3000/renewal/start

echo.
echo 測試完成後，請手動關閉兩個服務視窗
echo.
pause
