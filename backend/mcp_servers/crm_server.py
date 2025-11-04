"""
CRM MCP Server

提供客戶關係管理相關的 MCP Tools：
1. get_customer - 查詢客戶基本資料
2. list_customer_phones - 列出客戶門號
3. get_phone_details - 查詢門號詳情
4. check_renewal_eligibility - 檢查續約資格
5. check_promotion_eligibility - 檢查促銷資格

Sprint 3 實作
"""
import os
import sys
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
import json

# 添加 mcp_servers 目錄到路徑（為了 import common）
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from common.base_server import BaseMCPServer, MCPToolError

logger = structlog.get_logger()


class CRMServer(BaseMCPServer):
    """
    CRM MCP Server
    
    管理所有客戶相關資料查詢
    
    Note: 目前使用 Mock 資料，未來可整合真實 CRM API
    """
    
    def __init__(self):
        super().__init__("CRM MCP Server")
        
        # 連接 CRM API 的設定
        self.crm_api_url = os.getenv("MCP_CRM_API_URL", "")
        self.crm_api_key = os.getenv("MCP_CRM_API_KEY", "")
        self.use_mock_data = not self.crm_api_url  # 如果沒有設定 API URL，使用 Mock 資料
        
        if self.use_mock_data:
            logger.info("CRM Server 使用 Mock 資料模式")
        else:
            logger.info("CRM Server 初始化完成", api_url=self.crm_api_url[:50])
        
        # 初始化 Mock 資料
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化 Mock 資料（與 MockCRMService 保持一致）"""
        self.mock_customers = {
            "A123456789": {
                "customer_id": "C123456",
                "id_number": "A123456789",
                "name": "張三",
                "phone": "0912345678",
                "email": "zhang@example.com",
                "address": "台北市信義區信義路五段7號",
                "is_company_customer": True,
                "credit_score": 85,
                "blacklist": False,
                "registration_date": "2020-01-01"
            },
            "B987654321": {
                "customer_id": "C987654",
                "id_number": "B987654321",
                "name": "李四",
                "phone": "0923456789",
                "email": "li@example.com",
                "address": "新北市板橋區中山路一段161號",
                "is_company_customer": True,
                "credit_score": 75,
                "blacklist": False,
                "registration_date": "2019-06-15"
            },
            "C111222333": {
                "customer_id": "C111222",
                "id_number": "C111222333",
                "name": "王五",
                "phone": "0934567890",
                "email": "wang@example.com",
                "address": "台中市西屯區台灣大道三段99號",
                "is_company_customer": False,  # 非本公司客戶
                "credit_score": 0,
                "blacklist": False,
                "registration_date": "2018-03-20"
            }
        }
        
        self.mock_phones = {
            "C123456": [
                {
                    "phone_number": "0912345678",
                    "plan_name": "4G 精選方案",
                    "contract_status": "active",
                    "contract_end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "monthly_fee": 999,
                    "is_eligible_for_renewal": True
                },
                {
                    "phone_number": "0987654321",
                    "plan_name": "5G 輕速方案",
                    "contract_status": "active",
                    "contract_end_date": (datetime.now() + timedelta(days=330)).strftime("%Y-%m-%d"),
                    "monthly_fee": 599,
                    "is_eligible_for_renewal": False
                }
            ],
            "C987654": [
                {
                    "phone_number": "0923456789",
                    "plan_name": "5G 飆速方案",
                    "contract_status": "active",
                    "contract_end_date": (datetime.now() + timedelta(days=50)).strftime("%Y-%m-%d"),
                    "monthly_fee": 1399,
                    "is_eligible_for_renewal": True
                }
            ]
        }
        
        logger.debug("Mock 資料初始化完成")
    
    # ========================================
    # MCP Tools 實作 (Sprint 3)
    # ========================================
    
    async def get_customer(self, id_number: str) -> Dict[str, Any]:
        """
        Tool: get_customer
        查詢客戶基本資料
        
        Args:
            id_number: 客戶身分證號
            
        Returns:
            客戶資料
        """
        try:
            logger.info("Tool: get_customer", id_number=id_number[:3] + "***")
            
            # 1. 驗證參數
            if not id_number or len(id_number) != 10:
                return self.error_response(
                    "INVALID_INPUT",
                    "身分證號格式錯誤（應為10位）"
                )
            
            # 2. 查詢客戶資料（使用 Mock 資料或呼叫 API）
            if self.use_mock_data:
                customer = self.mock_customers.get(id_number)
            else:
                # TODO: 呼叫真實 CRM API
                # customer = await self._call_crm_api("/customers", {"id_number": id_number})
                customer = None
            
            # 3. 處理回應
            if not customer:
                return self.error_response(
                    "NOT_FOUND",
                    "查無此客戶"
                )
            
            # 4. 返回標準化格式
            logger.info("查詢到客戶", customer_id=customer["customer_id"])
            return self.success_response(customer)
            
        except Exception as e:
            return await self.handle_error(e, "查詢客戶資料")
    
    async def list_customer_phones(self, customer_id: str) -> Dict[str, Any]:
        """
        Tool: list_customer_phones
        列出客戶所有門號
        
        Args:
            customer_id: 客戶編號
            
        Returns:
            門號列表
        """
        try:
            logger.info("Tool: list_customer_phones", customer_id=customer_id)
            
            # 驗證參數
            if not customer_id:
                return self.error_response(
                    "INVALID_INPUT",
                    "客戶編號不能為空"
                )
            
            # 查詢門號列表
            if self.use_mock_data:
                phones = self.mock_phones.get(customer_id, [])
            else:
                # TODO: 呼叫真實 CRM API
                phones = []
            
            logger.info("查詢到門號", customer_id=customer_id, count=len(phones))
            return self.success_response(phones)
            
        except Exception as e:
            return await self.handle_error(e, "列出客戶門號")
    
    async def get_phone_details(self, phone_number: str) -> Dict[str, Any]:
        """
        Tool: get_phone_details
        查詢門號的詳細資訊
        
        Args:
            phone_number: 門號
            
        Returns:
            門號詳情（包含合約、使用量、帳單資訊）
        """
        try:
            logger.info("Tool: get_phone_details", phone_number=phone_number)
            
            # 驗證參數
            if not phone_number or len(phone_number) != 10:
                return self.error_response(
                    "INVALID_INPUT",
                    "門號格式錯誤（應為10位）"
                )
            
            # 查詢門號詳情（合約、使用量、帳單）
            if self.use_mock_data:
                details = self._get_mock_phone_details(phone_number)
            else:
                # TODO: 呼叫真實 CRM API
                details = None
            
            if not details:
                return self.error_response(
                    "NOT_FOUND",
                    "查無此門號"
                )
            
            logger.info("查詢到門號詳情", phone_number=phone_number)
            return self.success_response(details)
            
        except Exception as e:
            return await self.handle_error(e, "查詢門號詳情")
    
    def _get_mock_phone_details(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """取得 Mock 門號詳情"""
        # 合約資訊
        contract_data = {
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
        
        contract = contract_data.get(phone_number)
        if not contract:
            return None
        
        # 使用量資訊
        data_limit = 50000 if phone_number == "0912345678" else (20000 if phone_number == "0987654321" else 999999)
        voice_limit = 600 if phone_number == "0912345678" else (300 if phone_number == "0987654321" else 999)
        
        usage_info = {
            "phone_number": phone_number,
            "data_used_gb": round(random.uniform(15.0, 45.0), 2),
            "data_limit_gb": data_limit / 1000,
            "voice_used_minutes": random.randint(200, 500),
            "voice_limit_minutes": voice_limit,
            "average_daily_data_mb": random.randint(1000, 1500)
        }
        
        # 帳單資訊
        base_fee = contract["monthly_fee"]
        billing_info = {
            "phone_number": phone_number,
            "current_month_fee": base_fee,
            "outstanding_balance": 0,
            "last_payment_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "payment_history_good": True
        }
        
        return {
            "phone_number": phone_number,
            "contract_info": contract,
            "usage_info": usage_info,
            "billing_info": billing_info
        }
    
    async def check_renewal_eligibility(
        self,
        phone_number: str,
        renewal_type: str
    ) -> Dict[str, Any]:
        """
        Tool: check_renewal_eligibility
        檢查門號續約資格
        
        Args:
            phone_number: 門號
            renewal_type: 續約類型 (single/with_device)
            
        Returns:
            資格檢查結果
        """
        try:
            logger.info(
                "Tool: check_renewal_eligibility",
                phone_number=phone_number,
                renewal_type=renewal_type
            )
            
            # 驗證參數
            error = self.validate_required_params(
                {"phone_number": phone_number, "renewal_type": renewal_type},
                ["phone_number", "renewal_type"]
            )
            if error:
                return error
            
            if renewal_type not in ["single", "with_device"]:
                return self.error_response(
                    "INVALID_INPUT",
                    "續約類型必須為 single 或 with_device"
                )
            
            # 取得門號詳情
            details_result = await self.get_phone_details(phone_number)
            if not details_result.get("success"):
                return details_result
            
            details = details_result["data"]
            contract = details["contract_info"]
            billing = details["billing_info"]
            
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
            if billing["outstanding_balance"] == 0:
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
            
            # 3. 檢查信用狀況（簡化處理）
            checks.append({
                "item": "信用狀況",
                "status": "pass",
                "message": "信用良好，無黑名單記錄"
            })
            not_blacklisted = True
            
            # 綜合判斷
            is_eligible = within_renewal_period and no_outstanding and not_blacklisted
            
            result = {
                "is_eligible": is_eligible,
                "reasons": [] if is_eligible else [check["message"] for check in checks if check["status"] == "fail"],
                "contract_end_date": contract["contract_end_date"],
                "days_until_expiry": days_to_expiry,
                "credit_score": "A",
                "has_outstanding_debt": not no_outstanding,
                "details": checks
            }
            
            logger.info("資格檢查完成", phone_number=phone_number, is_eligible=is_eligible)
            return self.success_response(result)
            
        except Exception as e:
            return await self.handle_error(e, "檢查續約資格")
    
    async def check_promotion_eligibility(
        self,
        phone_number: str,
        promotion_id: str
    ) -> Dict[str, Any]:
        """
        Tool: check_promotion_eligibility
        檢查門號是否符合特定促銷資格
        
        Args:
            phone_number: 門號
            promotion_id: 促銷編號
            
        Returns:
            資格檢查結果
        """
        try:
            logger.info(
                "Tool: check_promotion_eligibility",
                phone_number=phone_number,
                promotion_id=promotion_id
            )
            
            # 驗證參數
            error = self.validate_required_params(
                {"phone_number": phone_number, "promotion_id": promotion_id},
                ["phone_number", "promotion_id"]
            )
            if error:
                return error
            
            # 取得門號詳情
            details_result = await self.get_phone_details(phone_number)
            if not details_result.get("success"):
                return details_result
            
            details = details_result["data"]
            contract = details["contract_info"]
            usage = details["usage_info"]
            
            # Mock 促銷活動資格規則
            # 實際應連接 Promotion MCP Server (Sprint 5)
            promotions_rules = {
                "PROMO001": {
                    "name": "5G 升級優惠",
                    "min_contract_months": 12,
                    "min_data_usage_gb": 20,
                    "description": "合約滿 12 個月且月均用量 20GB 以上"
                },
                "PROMO002": {
                    "name": "老客戶續約折扣",
                    "min_contract_months": 24,
                    "max_outstanding": 0,
                    "description": "合約滿 24 個月且無欠費"
                },
                "PROMO003": {
                    "name": "攜碼專案",
                    "is_mnp_only": True,
                    "description": "限攜碼客戶"
                }
            }
            
            if promotion_id not in promotions_rules:
                return self.error_response(
                    "PROMOTION_NOT_FOUND",
                    f"找不到促銷活動: {promotion_id}"
                )
            
            promo = promotions_rules[promotion_id]
            checks = []
            
            # 計算合約月數
            contract_start = datetime.strptime(contract["contract_start_date"], "%Y-%m-%d")
            contract_months = (datetime.now() - contract_start).days // 30
            
            # 檢查條件
            contract_ok = True
            if "min_contract_months" in promo:
                if contract_months >= promo["min_contract_months"]:
                    checks.append({
                        "item": "合約期限",
                        "status": "pass",
                        "message": f"合約已滿 {contract_months} 個月，符合 {promo['min_contract_months']} 個月條件"
                    })
                else:
                    checks.append({
                        "item": "合約期限",
                        "status": "fail",
                        "message": f"合約僅 {contract_months} 個月，需滿 {promo['min_contract_months']} 個月"
                    })
                    contract_ok = False
            
            usage_ok = True
            if "min_data_usage_gb" in promo:
                avg_usage = usage["data_used_gb"]  # 簡化為當期用量
                if avg_usage >= promo["min_data_usage_gb"]:
                    checks.append({
                        "item": "數據用量",
                        "status": "pass",
                        "message": f"當期用量 {avg_usage} GB，符合 {promo['min_data_usage_gb']} GB 條件"
                    })
                else:
                    checks.append({
                        "item": "數據用量",
                        "status": "fail",
                        "message": f"當期用量 {avg_usage} GB，需達 {promo['min_data_usage_gb']} GB"
                    })
                    usage_ok = False
            
            mnp_ok = True
            if "is_mnp_only" in promo and promo["is_mnp_only"]:
                # 簡化處理，實際需檢查客戶是否為攜碼客戶
                checks.append({
                    "item": "攜碼限定",
                    "status": "fail",
                    "message": "此促銷僅限攜碼客戶"
                })
                mnp_ok = False
            
            is_eligible = contract_ok and usage_ok and mnp_ok
            
            result = {
                "is_eligible": is_eligible,
                "promotion_id": promotion_id,
                "promotion_name": promo["name"],
                "description": promo["description"],
                "reasons": [] if is_eligible else [check["message"] for check in checks if check["status"] == "fail"],
                "details": checks
            }
            
            logger.info("促銷資格檢查完成", promotion_id=promotion_id, is_eligible=is_eligible)
            return self.success_response(result)
            
        except Exception as e:
            return await self.handle_error(e, "檢查促銷資格")


async def main():
    """
    MCP Server 主程式
    
    使用 MCP SDK 啟動 CRM MCP Server
    """
    logger.info("啟動 CRM MCP Server")
    
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        logger.error("找不到 mcp 套件，請執行: pip install mcp")
        raise
    
    # 初始化 CRM 實例
    crm = CRMServer()
    
    # 建立自訂 Server 類別
    class CRMServerMCP(Server):
        def __init__(self):
            super().__init__("crm-mcp-server")
        
        async def list_tools(self) -> list[Tool]:
            """列出所有可用的 Tools"""
            return [
                Tool(
                    name="get_customer",
                    description="查詢客戶基本資料",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id_number": {
                                "type": "string",
                                "description": "身分證字號 (10碼)"
                            }
                        },
                        "required": ["id_number"]
                    }
                ),
                Tool(
                    name="list_customer_phones",
                    description="列出客戶所有門號",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "客戶 ID"
                            }
                        },
                        "required": ["customer_id"]
                    }
                ),
                Tool(
                    name="get_phone_details",
                    description="取得門號詳細資訊",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            }
                        },
                        "required": ["phone_number"]
                    }
                ),
                Tool(
                    name="check_renewal_eligibility",
                    description="檢查門號續約資格",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            },
                            "renewal_type": {
                                "type": "string",
                                "description": "續約類型 (single/with_device)",
                                "enum": ["single", "with_device"]
                            }
                        },
                        "required": ["phone_number", "renewal_type"]
                    }
                ),
                Tool(
                    name="check_promotion_eligibility",
                    description="檢查門號促銷資格",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            },
                            "promotion_id": {
                                "type": "string",
                                "description": "促銷編號"
                            }
                        },
                        "required": ["phone_number", "promotion_id"]
                    }
                )
            ]
        
        async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
            """執行 Tool 調用"""
            logger.info(f"MCP 調用工具: {name}", arguments=arguments)
            
            try:
                if name == "get_customer":
                    result = await crm.get_customer(arguments["id_number"])
                elif name == "list_customer_phones":
                    result = await crm.list_customer_phones(arguments["customer_id"])
                elif name == "get_phone_details":
                    result = await crm.get_phone_details(arguments["phone_number"])
                elif name == "check_renewal_eligibility":
                    result = await crm.check_renewal_eligibility(
                        arguments["phone_number"],
                        arguments["renewal_type"]
                    )
                elif name == "check_promotion_eligibility":
                    result = await crm.check_promotion_eligibility(
                        arguments["phone_number"],
                        arguments["promotion_id"]
                    )
                else:
                    raise ValueError(f"未知的工具: {name}")
                
                # 返回 JSON 結果
                return [TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False)
                )]
                
            except Exception as e:
                logger.error(f"工具執行錯誤: {name}", error=str(e))
                error_result = {
                    "success": False,
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": str(e)
                    }
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False)
                )]
    
    # 建立 Server 實例
    server = CRMServerMCP()
    
    logger.info("CRM MCP Server 已註冊 5 個 Tools")
    
    # 啟動 stdio 通訊
    async with stdio_server() as (read_stream, write_stream):
        logger.info("CRM MCP Server 啟動成功，等待連接...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
