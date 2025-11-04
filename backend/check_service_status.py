"""
檢查當前後端服務的狀態和配置
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def main():
    print("=" * 60)
    print("後端服務診斷")
    print("=" * 60)
    
    # 1. 檢查環境變數
    print("\n1️⃣ 環境變數檢查:")
    use_mcp_crm = os.getenv('USE_MCP_CRM', 'false')
    use_http_transport = os.getenv('USE_HTTP_TRANSPORT', 'true')
    print(f"   USE_MCP_CRM = {use_mcp_crm}")
    print(f"   USE_HTTP_TRANSPORT = {use_http_transport}")
    
    # 2. 檢查後端是否運行
    print("\n2️⃣ 後端服務檢查 (port 8000):")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/api/health")
            print(f"   ✅ 後端運行中 (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ 後端未運行: {e}")
    
    # 3. 檢查 MCP CRM Server 是否運行
    print("\n3️⃣ MCP CRM Server 檢查 (port 8001):")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8001/health")
            print(f"   ✅ MCP CRM Server 運行中 (Status: {response.status_code})")
            data = response.json()
            print(f"   Server: {data.get('server', 'unknown')}")
    except Exception as e:
        print(f"   ❌ MCP CRM Server 未運行: {e}")
    
    # 4. 測試實際使用的服務
    print("\n4️⃣ 測試 CRM 服務:")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 先登入
            login_data = {"staff_code": "S001", "password": "password"}
            login_response = await client.post(
                "http://localhost:8000/api/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["token"]
                
                # 開始續約
                start_response = await client.post(
                    "http://localhost:8000/api/renewal/start",
                    headers={"Authorization": f"Bearer {token}"}
                )
                session_id = start_response.json()["session_id"]
                
                # 查詢客戶
                customer_response = await client.post(
                    "http://localhost:8000/api/renewal/query-customer",
                    json={"id_number": "A123456789"},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if customer_response.status_code == 200:
                    customer_data = customer_response.json()
                    customer_name = customer_data['customer']['name']
                    data_source = customer_data['customer'].get('_data_source', 'Unknown')
                    print(f"   ✅ CRM 查詢成功: {customer_name}")
                    print(f"   📊 實際資料來源: {data_source}")
                    
                    # 判斷使用的服務
                    if use_mcp_crm.lower() == 'true':
                        print(f"   📌 配置顯示: 應該使用 MCP CRM Service")
                        if data_source == 'Mock_Service':
                            print(f"   ⚠️  警告: 配置要求使用 MCP，但實際使用了 Mock！")
                            print(f"   💡 可能原因: 後端在修改 .env 前啟動，未重新載入配置")
                    else:
                        print(f"   📌 配置顯示: 應該使用 Mock CRM Service")
                        if data_source == 'MCP_CRM_Server':
                            print(f"   ⚠️  警告: 配置要求使用 Mock，但實際使用了 MCP！")
                else:
                    print(f"   ❌ CRM 查詢失敗: {customer_response.status_code}")
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("診斷完成")
    print("=" * 60)
    
    # 5. 結論
    print("\n📊 結論:")
    if use_mcp_crm.lower() == 'true':
        print("   ⚠️  USE_MCP_CRM=true")
        print("   ➡️  系統應該嘗試連接 MCP CRM Server (port 8001)")
        print("   ➡️  如果 MCP Server 未運行，初始化時應該會失敗")
        print()
        print("   🤔 可能的情況:")
        print("   1. 後端是在 .env 改變前啟動的（使用舊配置）")
        print("   2. MCP Server 其實有在背景運行")
        print("   3. 有快取機制保留了舊的服務實例")
    else:
        print("   ✅ USE_MCP_CRM=false")
        print("   ➡️  系統使用 Mock CRM Service")

if __name__ == "__main__":
    asyncio.run(main())
