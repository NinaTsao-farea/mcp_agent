@echo off
REM 前端啟動腳本

echo 🎨 啟動前端開發伺服器
echo =======================

cd /d D:\ai_project\test_mcp_agent2\frontend

REM 檢查 node_modules
if not exist "node_modules" (
    echo 📦 安裝 Node.js 依賴...
    pnpm install
)

REM 檢查環境變數檔案
if not exist ".env" (
    echo ⚙️ 建立前端環境變數檔案...
    copy .env.example .env
)

echo 🚀 啟動 Nuxt 開發伺服器...
echo 📍 前端地址: http://localhost:3000
echo.

pnpm run dev