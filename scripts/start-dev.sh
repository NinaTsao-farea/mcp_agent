#!/bin/bash
# 電信門市銷售助理系統 - 開發環境快速啟動腳本

echo "🚀 啟動電信門市銷售助理系統開發環境"
echo "=========================================="

# 檢查是否在專案根目錄
if [ ! -f "README.md" ]; then
    echo "❌ 請在專案根目錄執行此腳本"
    exit 1
fi

# 1. 啟動後端
echo "📡 啟動後端服務..."
cd backend

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 建立 Python 虛擬環境..."
    python -m venv venv
fi

# 啟動虛擬環境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 安裝依賴
echo "📦 安裝 Python 依賴..."
pip install -r requirements.txt

# 檢查環境變數
if [ ! -f ".env" ]; then
    echo "⚙️ 建立環境變數檔案..."
    cp .env.example .env
    echo "⚠️ 請編輯 backend/.env 檔案，填入正確的資料庫和服務設定"
fi

# 在背景啟動後端
echo "🎯 啟動 Quart 後端服務 (port 8000)..."
python app.py &
BACKEND_PID=$!

cd ..

# 2. 啟動前端
echo "🎨 啟動前端服務..."
cd frontend

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安裝 Node.js 依賴..."
    pnpm install
fi

# 檢查環境變數
if [ ! -f ".env" ]; then
    echo "⚙️ 建立前端環境變數檔案..."
    cp .env.example .env
fi

# 啟動前端
echo "🎯 啟動 Nuxt 前端服務 (port 3000)..."
pnpm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ 系統啟動完成！"
echo "=========================================="
echo "🌐 前端: http://localhost:3000"
echo "📡 後端: http://localhost:8000"
echo "🔍 API 健康檢查: http://localhost:8000/health"
echo ""
echo "測試帳號："
echo "員工編號: S001"
echo "密碼: password"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待中斷信號
wait $BACKEND_PID $FRONTEND_PID