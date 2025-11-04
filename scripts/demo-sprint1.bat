@echo off
REM Sprint 1 演示 - 認證系統測試
echo ====================================
echo Sprint 1 認證系統演示
echo ====================================
echo.

REM 檢查 Redis 是否執行
echo [1/4] 檢查 Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Redis 未執行！請先啟動 Redis
    echo    docker run -d -p 6379:6379 redis:7.2-alpine
    pause
    exit /b 1
)
echo ✅ Redis 正常執行

REM 啟動後端
echo.
echo [2/4] 啟動後端服務...
cd /d "%~dp0..\backend"
start "後端服務" cmd /k "set USE_REAL_ORACLE_DB=false && set REDIS_URL=redis://localhost:6379 && D:\Python\Python312\python.exe run_app.py"
timeout /t 3 >nul

REM 啟動前端
echo.
echo [3/4] 啟動前端服務...
cd /d "%~dp0..\frontend"
start "前端服務" cmd /k "pnpm dev"
timeout /t 5 >nul

REM 開啟瀏覽器
echo.
echo [4/4] 開啟瀏覽器...
start http://localhost:3000

echo.
echo ====================================
echo ✅ 系統啟動完成！
echo ====================================
echo.
echo 訪問資訊:
echo   前端: http://localhost:3000
echo   後端: http://localhost:8000
echo.
echo 測試帳號:
echo   員工編號: S001
echo   密碼: password
echo.
echo 功能測試:
echo   1. 登入系統
echo   2. 檢視首頁
echo   3. 登出測試
echo   4. Session 恢復測試 (刷新頁面)
echo.
echo 按任意鍵關閉此視窗...
pause >nul
