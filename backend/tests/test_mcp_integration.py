"""
Sprint 3 整合測試
測試 Mock 模式和 MCP 模式的切換及功能
"""
import pytest
import asyncio
import os
from pathlib import Path

# 設定環境變數
os.environ["USE_MCP_CRM"] = "false"  # 先測試 Mock 模式

from app.services.crm_factory import get_crm_service
from app.services.mcp_client import mcp_client


class TestMockMode:
    """測試 Mock 模式 (USE_MCP_CRM=false)"""
    
    @pytest.mark.asyncio
    async def test_mock_mode_enabled(self):
        """測試 Mock 模式啟用"""
        service = get_crm_service()
        assert service is not None
        assert service.__class__.__name__ == "MockCRMService"
        print("✓ Mock 模式啟用成功")
    
    @pytest.mark.asyncio
    async def test_query_customer(self):
        """測試查詢客戶"""
        service = get_crm_service()
        
        # 測試存在的客戶
        customer = await service.query_customer_by_id("A123456789")
        assert customer is not None
        assert customer["id_number"] == "A123456789"
        assert customer["name"] == "王小明"
        print(f"✓ 查詢客戶成功: {customer['name']}")
        
        # 測試不存在的客戶
        customer = await service.query_customer_by_id("X999999999")
        assert customer is None
        print("✓ 查詢不存在的客戶返回 None")
    
    @pytest.mark.asyncio
    async def test_get_customer_phones(self):
        """測試取得客戶門號"""
        service = get_crm_service()
        
        phones = await service.get_customer_phones("CUST001")
        assert len(phones) > 0
        assert phones[0]["phone_number"] == "0912345678"
        print(f"✓ 取得門號列表成功: {len(phones)} 個門號")
    
    @pytest.mark.asyncio
    async def test_get_phone_contract(self):
        """測試取得合約資訊"""
        service = get_crm_service()
        
        contract = await service.get_phone_contract("0912345678")
        assert contract is not None
        assert contract["phone_number"] == "0912345678"
        assert "plan_name" in contract
        assert "monthly_fee" in contract
        print(f"✓ 取得合約資訊成功: {contract['plan_name']}")
    
    @pytest.mark.asyncio
    async def test_get_phone_usage(self):
        """測試取得使用量"""
        service = get_crm_service()
        
        usage = await service.get_phone_usage("0912345678")
        assert usage is not None
        assert "data_used_gb" in usage
        assert "voice_used_minutes" in usage
        print(f"✓ 取得使用量成功: {usage['data_used_gb']} GB")
    
    @pytest.mark.asyncio
    async def test_get_phone_billing(self):
        """測試取得帳單資訊"""
        service = get_crm_service()
        
        billing = await service.get_phone_billing("0912345678")
        assert billing is not None
        assert "current_month_fee" in billing
        assert "outstanding_balance" in billing
        print(f"✓ 取得帳單資訊成功: 本月帳單 ${billing['current_month_fee']}")
    
    @pytest.mark.asyncio
    async def test_check_eligibility(self):
        """測試檢查續約資格"""
        service = get_crm_service()
        
        # 測試符合資格的門號 (合約快到期)
        result = await service.check_eligibility("0912345678", "CUST001")
        assert "eligible" in result
        print(f"✓ 檢查資格成功: {'符合' if result['eligible'] else '不符合'} 續約資格")


class TestMCPMode:
    """測試 MCP 模式 (USE_MCP_CRM=true)"""
    
    @pytest.fixture(autouse=True)
    async def setup_mcp(self):
        """設定 MCP 模式"""
        # 暫時改變環境變數
        original_value = os.environ.get("USE_MCP_CRM")
        os.environ["USE_MCP_CRM"] = "true"
        
        # 重新載入 factory (因為它會快取)
        import importlib
        from app.services import crm_factory
        importlib.reload(crm_factory)
        
        # 初始化 MCP Client
        await mcp_client.initialize()
        
        yield
        
        # 恢復環境變數
        if original_value:
            os.environ["USE_MCP_CRM"] = original_value
        else:
            os.environ.pop("USE_MCP_CRM", None)
        
        # 關閉 MCP Client
        await mcp_client.close()
        
        # 重新載入 factory
        importlib.reload(crm_factory)
    
    @pytest.mark.asyncio
    async def test_mcp_mode_enabled(self):
        """測試 MCP 模式啟用"""
        from app.services import crm_factory
        service = crm_factory.get_crm_service()
        assert service is not None
        assert service.__class__.__name__ == "MCPClientService"
        print("✓ MCP 模式啟用成功")
    
    @pytest.mark.asyncio
    async def test_mcp_query_customer(self):
        """測試 MCP 查詢客戶"""
        customer = await mcp_client.query_customer_by_id("A123456789")
        assert customer is not None
        assert customer["id_number"] == "A123456789"
        assert customer["name"] == "王小明"
        print(f"✓ MCP 查詢客戶成功: {customer['name']}")
    
    @pytest.mark.asyncio
    async def test_mcp_get_customer_phones(self):
        """測試 MCP 取得門號"""
        phones = await mcp_client.get_customer_phones("CUST001")
        assert len(phones) > 0
        assert phones[0]["phone_number"] == "0912345678"
        print(f"✓ MCP 取得門號成功: {len(phones)} 個門號")
    
    @pytest.mark.asyncio
    async def test_mcp_get_phone_details(self):
        """測試 MCP 取得門號詳情"""
        contract = await mcp_client.get_phone_contract("0912345678")
        usage = await mcp_client.get_phone_usage("0912345678")
        billing = await mcp_client.get_phone_billing("0912345678")
        
        assert contract is not None
        assert usage is not None
        assert billing is not None
        
        print(f"✓ MCP 取得門號詳情成功")
        print(f"  - 合約: {contract['plan_name']}")
        print(f"  - 使用: {usage['data_used_gb']} GB")
        print(f"  - 帳單: ${billing['current_month_fee']}")
    
    @pytest.mark.asyncio
    async def test_mcp_check_eligibility(self):
        """測試 MCP 檢查資格"""
        result = await mcp_client.check_eligibility("0912345678", "CUST001")
        assert "eligible" in result
        print(f"✓ MCP 檢查資格成功: {'符合' if result['eligible'] else '不符合'} 續約資格")
        
        if not result["eligible"]:
            print(f"  不符合原因: {', '.join(result.get('reasons', []))}")


class TestWorkflowIntegration:
    """測試完整工作流 (Steps 1-4)"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """測試 Mock 模式完整流程"""
        print("\n=== 測試 Mock 模式完整工作流 ===")
        
        service = get_crm_service()
        
        # Step 1: 查詢客戶
        print("\n[Step 1] 查詢客戶...")
        customer = await service.query_customer_by_id("A123456789")
        assert customer is not None
        customer_id = customer["customer_id"]
        print(f"✓ 客戶: {customer['name']} (ID: {customer_id})")
        
        # Step 2: 取得門號列表
        print("\n[Step 2] 取得門號列表...")
        phones = await service.get_customer_phones(customer_id)
        assert len(phones) > 0
        selected_phone = phones[0]["phone_number"]
        print(f"✓ 找到 {len(phones)} 個門號")
        print(f"✓ 選擇門號: {selected_phone}")
        
        # Step 3: 取得門號詳情
        print("\n[Step 3] 取得門號詳情...")
        contract = await service.get_phone_contract(selected_phone)
        usage = await service.get_phone_usage(selected_phone)
        billing = await service.get_phone_billing(selected_phone)
        
        assert contract is not None
        assert usage is not None
        assert billing is not None
        
        print(f"✓ 合約: {contract['plan_name']} (${contract['monthly_fee']}/月)")
        print(f"✓ 使用: {usage['data_used_gb']}/{usage['data_limit_gb']} GB")
        print(f"✓ 帳單: ${billing['current_month_fee']} (欠費: ${billing['outstanding_balance']})")
        
        # Step 4: 檢查資格
        print("\n[Step 4] 檢查續約資格...")
        result = await service.check_eligibility(selected_phone, customer_id)
        
        if result["eligible"]:
            print(f"✓ 符合續約資格")
            print(f"  - 合約到期日: {result['contract_end_date']}")
            print(f"  - 剩餘天數: {result['days_until_expiry']} 天")
        else:
            print(f"✗ 不符合續約資格")
            for reason in result.get("reasons", []):
                print(f"  - {reason}")
        
        print("\n✓ Mock 模式完整工作流測試完成")
    
    @pytest.mark.asyncio
    async def test_full_workflow_mcp(self):
        """測試 MCP 模式完整流程"""
        print("\n=== 測試 MCP 模式完整工作流 ===")
        
        # 切換到 MCP 模式
        os.environ["USE_MCP_CRM"] = "true"
        
        # 初始化 MCP Client
        await mcp_client.initialize()
        
        try:
            # Step 1: 查詢客戶
            print("\n[Step 1] 查詢客戶...")
            customer = await mcp_client.query_customer_by_id("A123456789")
            assert customer is not None
            customer_id = customer["customer_id"]
            print(f"✓ 客戶: {customer['name']} (ID: {customer_id})")
            
            # Step 2: 取得門號列表
            print("\n[Step 2] 取得門號列表...")
            phones = await mcp_client.get_customer_phones(customer_id)
            assert len(phones) > 0
            selected_phone = phones[0]["phone_number"]
            print(f"✓ 找到 {len(phones)} 個門號")
            print(f"✓ 選擇門號: {selected_phone}")
            
            # Step 3: 取得門號詳情
            print("\n[Step 3] 取得門號詳情...")
            contract = await mcp_client.get_phone_contract(selected_phone)
            usage = await mcp_client.get_phone_usage(selected_phone)
            billing = await mcp_client.get_phone_billing(selected_phone)
            
            assert contract is not None
            assert usage is not None
            assert billing is not None
            
            print(f"✓ 合約: {contract['plan_name']} (${contract['monthly_fee']}/月)")
            print(f"✓ 使用: {usage['data_used_gb']}/{usage['data_limit_gb']} GB")
            print(f"✓ 帳單: ${billing['current_month_fee']} (欠費: ${billing['outstanding_balance']})")
            
            # Step 4: 檢查資格
            print("\n[Step 4] 檢查續約資格...")
            result = await mcp_client.check_eligibility(selected_phone, customer_id)
            
            if result["eligible"]:
                print(f"✓ 符合續約資格")
                print(f"  - 合約到期日: {result['contract_end_date']}")
                print(f"  - 剩餘天數: {result['days_until_expiry']} 天")
            else:
                print(f"✗ 不符合續約資格")
                for reason in result.get("reasons", []):
                    print(f"  - {reason}")
            
            print("\n✓ MCP 模式完整工作流測試完成")
            
        finally:
            # 關閉 MCP Client
            await mcp_client.close()
            os.environ["USE_MCP_CRM"] = "false"


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v", "-s"])
