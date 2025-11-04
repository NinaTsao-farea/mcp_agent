@echo off
REM 執行認證系統測試
echo ====================================
echo 執行認證系統測試
echo ====================================

cd /d "%~dp0..\backend"

REM 確保測試環境變數
set USE_REAL_ORACLE_DB=false
set REDIS_URL=redis://localhost:6379/1

REM 執行測試
D:\Python\Python312\python.exe -m pytest tests/test_auth.py -v --tb=short

echo.
echo ====================================
echo 測試完成
echo ====================================
pause