@echo off
REM 快速設定開發環境腳本

echo 🚀 設定電信門市銷售助理系統開發環境
echo =======================================

cd backend

REM 檢查虛擬環境
if not exist "venv" (
    echo 📦 建立 Python 虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 建立虛擬環境失敗
        pause
        exit /b 1
    )
)

REM 啟動虛擬環境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 啟動虛擬環境失敗
    pause
    exit /b 1
)

REM 安裝核心依賴
echo 📦 安裝核心依賴...
pip install -r requirements-dev.txt
if errorlevel 1 (
    echo ❌ 安裝依賴失敗
    pause
    exit /b 1
)

REM 檢查環境變數檔案
if not exist ".env" (
    echo ⚙️ 建立環境變數檔案...
    copy .env.example .env
    echo ⚠️ 請編輯 backend\.env 檔案設定資料庫連線資訊
)

echo ✅ 開發環境設定完成！
echo 📝 接下來您可以執行：
echo    .\scripts\start-backend.bat  - 啟動後端服務
echo    .\scripts\start-dev.bat      - 啟動完整開發環境

pause