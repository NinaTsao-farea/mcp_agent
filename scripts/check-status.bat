@echo off
echo ===================================
echo 電信門市銷售助理系統 - 狀態檢查
echo ===================================
echo.

echo [1] 檢查前端服務 (localhost:3000)
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 前端服務: 運行中
) else (
    echo ❌ 前端服務: 未運行
)

echo.
echo [2] 檢查後端服務 (localhost:8000)
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 後端服務: 運行中
) else (
    echo ❌ 後端服務: 未運行
)

echo.
echo [3] 檢查服務端口
netstat -an | findstr ":3000"
netstat -an | findstr ":8000"

echo.
echo ===================================
echo 檢查完成
echo ===================================
echo.
echo 前端地址: http://localhost:3000
echo 後端地址: http://localhost:8000
echo.
pause