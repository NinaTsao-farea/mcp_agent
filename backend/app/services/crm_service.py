"""
Mock CRM 服務 - 用於開發與測試階段
提供模擬的客戶、門號、合約、使用量等資料
Note: Sprint 3 後將被 MCPClientServiceHTTP (HTTP Transport) 取代
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import random

logger = structlog.get_logger()

# 匯入 CRMServer 的 Mock 資料初始化方法
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))
from crm_server import CRMServer as BaseCRMServer

class MockCRMService:
    """
    CRM Mock 服務
    
    用於開發與測試階段的模擬資料服務
    Sprint 3 後將被 MCPClientServiceHTTP (HTTP Transport) 取代
    """
    
    def __init__(self, use_real_api: bool = False):
        """
        初始化
        
        Args:
            use_real_api: 是否使用真實 API (保留參數以維持介面相容性)
        """
        self.use_real_api = use_real_api
        
        if use_real_api:
            logger.warning("真實 CRM API 尚未實作，使用 Mock 資料")
        
        # 從 CRMServer 複製 Mock 資料
        base_server = BaseCRMServer()
        self.mock_customers = base_server.mock_customers
        self.mock_phones = base_server.mock_phones
        
        logger.info(
            "Mock CRM Service 初始化",
            mode="Mock",
            customers_count=len(self.mock_customers),
            phones_count=len(self.mock_phones)
        )
    
    async def query_customer_by_id(self, id_number: str) -> Optional[Dict[str, Any]]:
        """
        透過身分證號查詢客戶
        
        Args:
            id_number: 身分證號
            
        Returns:
            客戶資料，若不存在則返回 None
        """
        logger.info("查詢客戶", id_number=id_number[:3] + "***")
        
        # 使用從 CRMServer 複製的 Mock 資料
        customer = self.mock_customers.get(id_number)
        
        if customer:
            # 加入資料來源標記
            customer = customer.copy()
            customer["_data_source"] = "Mock_Service"
            logger.info("查詢到客戶", customer_id=customer["customer_id"])
        else:
            logger.info("客戶不存在")
        
        return customer
    
    async def get_customer_phones(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        取得客戶的所有門號
        
        Args:
            customer_id: 客戶 ID
            
        Returns:
            門號列表
        """
        logger.info("查詢客戶門號", customer_id=customer_id)
        
        # 使用從 CRMServer 複製的 Mock 資料
        phones = self.mock_phones.get(customer_id, [])
        
        # 複製並加入資料來源標記
        phones_with_source = []
        for phone in phones:
            phone_copy = phone.copy()
            phone_copy["_data_source"] = "Mock_Service"
            # 補充 CRMServer 資料中沒有的欄位，保持向下相容
            if "data_limit" not in phone_copy:
                if phone_copy.get("monthly_fee") == 999:
                    phone_copy["data_limit"] = "50GB"
                elif phone_copy.get("monthly_fee") == 599:
                    phone_copy["data_limit"] = "20GB"
                else:
                    phone_copy["data_limit"] = "無限制"
            if "is_primary" not in phone_copy:
                phone_copy["is_primary"] = (phones.index(phone) == 0)
            if "status" not in phone_copy:
                phone_copy["status"] = phone_copy.get("contract_status", "active")
            phones_with_source.append(phone_copy)
        
        logger.info("查詢到門號", customer_id=customer_id, count=len(phones_with_source))
        
        return phones_with_source
    
    async def get_phone_contract(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的合約資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            合約資訊
        """
        logger.info("查詢門號合約", phone_number=phone_number)
        
        # Mock 資料 (與 CRMServer._get_mock_phone_details 中的 contract_data 保持一致)
        mock_contracts = {
            "0912345678": {
                "phone_number": "0912345678",
                "plan_id": "PLAN_4G_999",
                "plan_name": "4G 精選方案",
                "monthly_fee": 999,
                "data_limit": "50GB",
                "voice_minutes": 600,
                "contract_start_date": (datetime.now() - timedelta(days=700)).strftime("%Y-%m-%d"),
                "contract_end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "contract_months": 24,
                "months_used": 23,
                "early_termination_fee": 1000,
                "device": "iPhone 14",
                "device_subsidy": 10000,
                "status": "active"
            },
            "0987654321": {
                "phone_number": "0987654321",
                "plan_id": "PLAN_5G_599",
                "plan_name": "5G 輕速方案",
                "monthly_fee": 599,
                "data_limit": "20GB",
                "voice_minutes": 300,
                "contract_start_date": (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
                "contract_end_date": (datetime.now() + timedelta(days=330)).strftime("%Y-%m-%d"),
                "contract_months": 24,
                "months_used": 13,
                "early_termination_fee": 5000,
                "device": "單門號",
                "device_subsidy": 0,
                "status": "active"
            },
            "0923456789": {
                "phone_number": "0923456789",
                "plan_id": "PLAN_5G_1399",
                "plan_name": "5G 飆速方案",
                "monthly_fee": 1399,
                "data_limit": "無限制",
                "voice_minutes": 999,
                "contract_start_date": (datetime.now() - timedelta(days=680)).strftime("%Y-%m-%d"),
                "contract_end_date": (datetime.now() + timedelta(days=50)).strftime("%Y-%m-%d"),
                "contract_months": 24,
                "months_used": 22,
                "early_termination_fee": 2000,
                "device": "Samsung Galaxy S23",
                "device_subsidy": 15000,
                "status": "active"
            }
        }
        
        contract = mock_contracts.get(phone_number)
        
        if contract:
            logger.info("查詢到合約", phone_number=phone_number)
        else:
            logger.warning("合約不存在", phone_number=phone_number)
        
        return contract
    
    async def get_phone_usage(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的使用量資訊 (與 MCP Server 格式一致)
        
        Args:
            phone_number: 門號
            
        Returns:
            使用量資訊
        """
        logger.info("查詢門號使用量", phone_number=phone_number)
        
        # Mock 資料 (與 CRMServer._get_mock_phone_details 中的 usage_info 邏輯保持一致)
        # 確定資料限制（GB）
        if phone_number == "0912345678":
            data_limit_gb = 50.0
            voice_limit_minutes = 600
        elif phone_number == "0987654321":
            data_limit_gb = 20.0
            voice_limit_minutes = 300
        else:
            data_limit_gb = 100.0
            voice_limit_minutes = 999
        
        # Mock 資料 - 使用 MCP Server 格式
        usage = {
            "phone_number": phone_number,
            "data_used_gb": round(random.uniform(15.0, data_limit_gb * 0.9), 2),  # GB
            "data_limit_gb": data_limit_gb,  # GB
            "voice_used_minutes": random.randint(200, 500),  # 分鐘
            "voice_limit_minutes": voice_limit_minutes,  # 分鐘
            "average_daily_data_mb": random.randint(1000, 1500)  # MB/天
        }
        
        logger.info("查詢到使用量", phone_number=phone_number)
        
        return usage
    
    async def get_phone_billing(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        取得門號的帳單資訊 (與 MCP Server 格式一致)
        
        Args:
            phone_number: 門號
            
        Returns:
            帳單資訊
        """
        logger.info("查詢門號帳單", phone_number=phone_number)
        
        # Mock 資料 (與 CRMServer._get_mock_phone_details 中的 billing_info 邏輯保持一致)
        base_fee = 999 if phone_number == "0912345678" else (599 if phone_number == "0987654321" else 1399)
        
        billing = {
            "phone_number": phone_number,
            "current_month_fee": base_fee,  # 本月費用
            "outstanding_balance": 0,  # 未繳金額（0 表示已繳清）
            "payment_history_good": True,  # 繳費紀錄良好
            "last_payment_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")  # 最後繳費日期
        }
        
        # 隨機決定是否有未繳款項
        if random.random() > 0.8:  # 20% 機率有未繳
            billing["outstanding_balance"] = random.randint(500, base_fee)
            billing["payment_history_good"] = False
        
        logger.info("查詢到帳單", phone_number=phone_number)
        
        return billing
    
    async def check_eligibility(
        self,
        phone_number: str,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        檢查續約資格
        
        Args:
            phone_number: 門號
            customer_id: 客戶 ID
            
        Returns:
            資格檢查結果
        """
        logger.info("檢查續約資格", phone_number=phone_number, customer_id=customer_id)
        
        # 取得合約資訊
        contract = await self.get_phone_contract(phone_number)
        
        if not contract:
            return {
                "eligible": False,
                "reason": "找不到合約資訊",
                "details": []
            }
        
        # 計算到期天數
        contract_end = datetime.strptime(contract["contract_end_date"], "%Y-%m-%d")
        days_to_expiry = (contract_end - datetime.now()).days
        
        # 檢查項目
        checks = []
        
        # 1. 檢查合約到期時間 (60天內)
        if days_to_expiry <= 60 and days_to_expiry >= 0:
            checks.append({
                "item": "合約到期",
                "status": "pass",
                "message": f"合約將於 {days_to_expiry} 天後到期，符合續約條件"
            })
            within_renewal_period = True
        elif days_to_expiry < 0:
            checks.append({
                "item": "合約到期",
                "status": "pass",
                "message": "合約已到期，可立即續約"
            })
            within_renewal_period = True
        else:
            checks.append({
                "item": "合約到期",
                "status": "fail",
                "message": f"合約還有 {days_to_expiry} 天才到期，需在 60 天內才可續約"
            })
            within_renewal_period = False
        
        # 2. 檢查欠費狀況
        billing = await self.get_phone_billing(phone_number)
        if billing and billing["outstanding_balance"] == 0:
            checks.append({
                "item": "帳單繳費",
                "status": "pass",
                "message": "無欠費記錄"
            })
            no_outstanding = True
        else:
            checks.append({
                "item": "帳單繳費",
                "status": "fail",
                "message": f"有欠費 ${billing['outstanding_balance']}，請先繳清"
            })
            no_outstanding = False
        
        # 3. 檢查黑名單 (從客戶資料取得)
        # 這裡簡化處理，實際應該呼叫 query_customer_by_id
        checks.append({
            "item": "信用狀況",
            "status": "pass",
            "message": "信用良好，無黑名單記錄"
        })
        not_blacklisted = True
        
        # 綜合判斷
        eligible = within_renewal_period and no_outstanding and not_blacklisted
        
        result = {
            "eligible": eligible,
            "reason": "符合續約資格" if eligible else "不符合續約資格",
            "details": checks,
            "contract_end_date": contract["contract_end_date"],
            "days_to_expiry": days_to_expiry
        }
        
        logger.info(
            "資格檢查完成",
            phone_number=phone_number,
            eligible=eligible
        )
        
        return result
