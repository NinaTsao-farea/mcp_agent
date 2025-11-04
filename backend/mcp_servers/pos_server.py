"""
POS MCP Server

提供門市設備管理相關的 MCP Tools：
1. query_device_stock - 查詢設備庫存
2. get_device_info - 取得設備詳細資訊
3. get_recommended_devices - 取得推薦設備
4. reserve_device - 預約設備
5. get_device_pricing - 取得設備價格資訊

Sprint 4 實作
"""
import os
import sys
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
import json

# 添加 mcp_servers 目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from common.base_server import BaseMCPServer, MCPToolError

logger = structlog.get_logger()


class POSServer(BaseMCPServer):
    """
    POS MCP Server
    
    管理所有門市設備相關操作
    
    Note: 目前使用 Mock 資料，未來可整合真實 POS 系統 API
    """
    
    def __init__(self):
        super().__init__("POS MCP Server")
        
        # 連接 POS API 的設定
        self.pos_api_url = os.getenv("MCP_POS_API_URL", "")
        self.pos_api_key = os.getenv("MCP_POS_API_KEY", "")
        self.use_mock_data = not self.pos_api_url
        
        if self.use_mock_data:
            logger.info("POS Server 使用 Mock 資料模式")
        else:
            logger.info("POS Server 初始化完成", api_url=self.pos_api_url[:50])
        
        # 初始化 Mock 資料
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化 Mock 設備資料"""
        
        # Mock 設備主檔
        self.mock_devices = {
            "DEV001": {
                "device_id": "DEV001",
                "brand": "Apple",
                "model": "iPhone 15 Pro",
                "storage": "256GB",
                "color": "自然鈦金屬",
                "os": "iOS",
                "screen_size": "6.1",
                "camera": "48MP 主鏡頭 + 12MP 超廣角 + 12MP 望遠",
                "battery": "3274 mAh",
                "chip": "A17 Pro",
                "price": 36900,
                "market_price": 39900,
                "release_date": "2023-09-22",
                "is_5g": True,
                "is_flagship": True,
                "popularity_score": 95
            },
            "DEV002": {
                "device_id": "DEV002",
                "brand": "Apple",
                "model": "iPhone 15",
                "storage": "128GB",
                "color": "粉紅色",
                "os": "iOS",
                "screen_size": "6.1",
                "camera": "48MP 主鏡頭 + 12MP 超廣角",
                "battery": "3349 mAh",
                "chip": "A16 Bionic",
                "price": 29900,
                "market_price": 32900,
                "release_date": "2023-09-22",
                "is_5g": True,
                "is_flagship": False,
                "popularity_score": 90
            },
            "DEV003": {
                "device_id": "DEV003",
                "brand": "Samsung",
                "model": "Galaxy S24 Ultra",
                "storage": "512GB",
                "color": "鈦灰色",
                "os": "Android",
                "screen_size": "6.8",
                "camera": "200MP 主鏡頭 + 12MP 超廣角 + 50MP 望遠 + 10MP 望遠",
                "battery": "5000 mAh",
                "chip": "Snapdragon 8 Gen 3",
                "price": 42900,
                "market_price": 46900,
                "release_date": "2024-01-17",
                "is_5g": True,
                "is_flagship": True,
                "popularity_score": 92
            },
            "DEV004": {
                "device_id": "DEV004",
                "brand": "Samsung",
                "model": "Galaxy S24",
                "storage": "256GB",
                "color": "星燦紫",
                "os": "Android",
                "screen_size": "6.2",
                "camera": "50MP 主鏡頭 + 12MP 超廣角 + 10MP 望遠",
                "battery": "4000 mAh",
                "chip": "Exynos 2400",
                "price": 26900,
                "market_price": 29900,
                "release_date": "2024-01-17",
                "is_5g": True,
                "is_flagship": False,
                "popularity_score": 85
            },
            "DEV005": {
                "device_id": "DEV005",
                "brand": "Google",
                "model": "Pixel 8 Pro",
                "storage": "256GB",
                "color": "天青色",
                "os": "Android",
                "screen_size": "6.7",
                "camera": "50MP 主鏡頭 + 48MP 超廣角 + 48MP 望遠",
                "battery": "5050 mAh",
                "chip": "Google Tensor G3",
                "price": 32900,
                "market_price": 35900,
                "release_date": "2023-10-04",
                "is_5g": True,
                "is_flagship": True,
                "popularity_score": 88
            },
            "DEV006": {
                "device_id": "DEV006",
                "brand": "Xiaomi",
                "model": "小米 14 Pro",
                "storage": "512GB",
                "color": "鈦金屬",
                "os": "Android",
                "screen_size": "6.73",
                "camera": "50MP 主鏡頭 + 50MP 超廣角 + 50MP 望遠",
                "battery": "4880 mAh",
                "chip": "Snapdragon 8 Gen 3",
                "price": 28900,
                "market_price": 31900,
                "release_date": "2023-10-26",
                "is_5g": True,
                "is_flagship": True,
                "popularity_score": 83
            },
            "DEV007": {
                "device_id": "DEV007",
                "brand": "OPPO",
                "model": "Find X7 Ultra",
                "storage": "256GB",
                "color": "海洋藍",
                "os": "Android",
                "screen_size": "6.82",
                "camera": "50MP 主鏡頭 + 50MP 超廣角 + 50MP 望遠 + 50MP 潛望式望遠",
                "battery": "5000 mAh",
                "chip": "Snapdragon 8 Gen 3",
                "price": 35900,
                "market_price": 39900,
                "release_date": "2024-01-08",
                "is_5g": True,
                "is_flagship": True,
                "popularity_score": 80
            },
            "DEV008": {
                "device_id": "DEV008",
                "brand": "Apple",
                "model": "iPhone 14",
                "storage": "128GB",
                "color": "午夜色",
                "os": "iOS",
                "screen_size": "6.1",
                "camera": "12MP 主鏡頭 + 12MP 超廣角",
                "battery": "3279 mAh",
                "chip": "A15 Bionic",
                "price": 23900,
                "market_price": 27900,
                "release_date": "2022-09-16",
                "is_5g": True,
                "is_flagship": False,
                "popularity_score": 78
            }
        }
        
        # Mock 門市庫存
        self.mock_stock = {
            "STORE001": {  # 信義門市
                "DEV001": {"quantity": 5, "reserved": 1},
                "DEV002": {"quantity": 8, "reserved": 2},
                "DEV003": {"quantity": 3, "reserved": 0},
                "DEV004": {"quantity": 6, "reserved": 1},
                "DEV005": {"quantity": 2, "reserved": 0},
                "DEV006": {"quantity": 4, "reserved": 0},
                "DEV007": {"quantity": 1, "reserved": 0},
                "DEV008": {"quantity": 10, "reserved": 3}
            },
            "STORE002": {  # 板橋門市
                "DEV001": {"quantity": 3, "reserved": 0},
                "DEV002": {"quantity": 12, "reserved": 4},
                "DEV003": {"quantity": 2, "reserved": 1},
                "DEV004": {"quantity": 8, "reserved": 2},
                "DEV005": {"quantity": 0, "reserved": 0},
                "DEV006": {"quantity": 5, "reserved": 1},
                "DEV007": {"quantity": 2, "reserved": 0},
                "DEV008": {"quantity": 15, "reserved": 5}
            },
            "STORE003": {  # 台中門市
                "DEV001": {"quantity": 4, "reserved": 1},
                "DEV002": {"quantity": 10, "reserved": 3},
                "DEV003": {"quantity": 1, "reserved": 0},
                "DEV004": {"quantity": 7, "reserved": 1},
                "DEV005": {"quantity": 3, "reserved": 1},
                "DEV006": {"quantity": 6, "reserved": 2},
                "DEV007": {"quantity": 0, "reserved": 0},
                "DEV008": {"quantity": 12, "reserved": 4}
            }
        }
        
        # Mock 預約記錄
        self.mock_reservations = {}
    
    def register_tools(self):
        """註冊所有 POS Tools"""
        
        # Tool 1: query_device_stock
        self.server.add_tool(
            name="query_device_stock",
            description="查詢門市設備庫存狀況",
            input_schema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼 (例如: STORE001)"
                    },
                    "os_filter": {
                        "type": "string",
                        "description": "作業系統過濾 (iOS 或 Android)，選填",
                        "enum": ["iOS", "Android"]
                    },
                    "min_price": {
                        "type": "number",
                        "description": "最低價格過濾，選填"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "最高價格過濾，選填"
                    }
                },
                "required": ["store_id"]
            },
            handler=self.query_device_stock
        )
        
        # Tool 2: get_device_info
        self.server.add_tool(
            name="get_device_info",
            description="取得設備詳細資訊",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼 (例如: DEV001)"
                    }
                },
                "required": ["device_id"]
            },
            handler=self.get_device_info
        )
        
        # Tool 3: get_recommended_devices
        self.server.add_tool(
            name="get_recommended_devices",
            description="根據客戶偏好取得推薦設備",
            input_schema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼"
                    },
                    "os_preference": {
                        "type": "string",
                        "description": "作業系統偏好 (iOS 或 Android)",
                        "enum": ["iOS", "Android"]
                    },
                    "budget": {
                        "type": "number",
                        "description": "預算上限"
                    },
                    "is_flagship": {
                        "type": "boolean",
                        "description": "是否只要旗艦機，選填"
                    }
                },
                "required": ["store_id", "os_preference", "budget"]
            },
            handler=self.get_recommended_devices
        )
        
        # Tool 4: reserve_device
        self.server.add_tool(
            name="reserve_device",
            description="預約設備（確保庫存保留）",
            input_schema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "門市代碼"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "客戶編號"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "門號"
                    }
                },
                "required": ["store_id", "device_id", "customer_id", "phone_number"]
            },
            handler=self.reserve_device
        )
        
        # Tool 5: get_device_pricing
        self.server.add_tool(
            name="get_device_pricing",
            description="取得設備價格資訊（含促銷價格）",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "設備代碼"
                    },
                    "plan_type": {
                        "type": "string",
                        "description": "方案類型 (例如: 攜碼/續約/新申辦)，選填"
                    }
                },
                "required": ["device_id"]
            },
            handler=self.get_device_pricing
        )
        
        logger.info("已註冊 5 個 POS Tools")
    
    # ==================== Tool 實作 ====================
    
    async def query_device_stock(self, store_id: str, os_filter: Optional[str] = None,
                                  min_price: Optional[float] = None, 
                                  max_price: Optional[float] = None) -> Dict[str, Any]:
        """Tool 1: 查詢門市設備庫存"""
        try:
            logger.info("Tool: query_device_stock", store_id=store_id, os_filter=os_filter)
            
            if store_id not in self.mock_stock:
                return {"success": False, "error": f"門市 {store_id} 不存在"}
            
            store_stock = self.mock_stock[store_id]
            devices = []
            
            for device_id, stock_info in store_stock.items():
                device = self.mock_devices.get(device_id)
                if not device:
                    continue
                
                # 過濾條件（不區分大小寫）
                if os_filter and device["os"].lower() != os_filter.lower():
                    continue
                if min_price and device["price"] < min_price:
                    continue
                if max_price and device["price"] > max_price:
                    continue
                
                available = stock_info["quantity"] - stock_info["reserved"]
                devices.append({
                    "device_id": device_id,
                    "brand": device["brand"],
                    "model": device["model"],
                    "storage": device["storage"],
                    "color": device["color"],
                    "os": device["os"],
                    "price": device["price"],
                    "market_price": device["market_price"],
                    "total_quantity": stock_info["quantity"],
                    "reserved": stock_info["reserved"],
                    "available": available,
                    "in_stock": available > 0,
                    "screen_size": device["screen_size"],
                    "camera": device["camera"],
                    "chip": device["chip"]
                })
            
            devices.sort(key=lambda x: x["available"], reverse=True)
            
            return {
                "success": True,
                "data": {
                    "store_id": store_id,
                    "filter": {"os": os_filter, "min_price": min_price, "max_price": max_price},
                    "device_count": len(devices),
                    "devices": devices
                }
            }
            
        except Exception as e:
            logger.error("查詢庫存失敗", error=str(e))
            return {"success": False, "error": f"查詢庫存失敗: {str(e)}"}
    
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Tool 2: 取得設備詳細資訊"""
        try:
            logger.info("Tool: get_device_info", device_id=device_id)
            
            if device_id not in self.mock_devices:
                return {"success": False, "error": f"設備 {device_id} 不存在"}
            
            device = self.mock_devices[device_id].copy()
            
            # 計算總庫存
            total_stock = 0
            available_stock = 0
            store_stock_list = []
            
            for store_id, store_stock in self.mock_stock.items():
                if device_id in store_stock:
                    stock_info = store_stock[device_id]
                    available = stock_info["quantity"] - stock_info["reserved"]
                    total_stock += stock_info["quantity"]
                    available_stock += available
                    store_stock_list.append({
                        "store_id": store_id,
                        "quantity": stock_info["quantity"],
                        "reserved": stock_info["reserved"],
                        "available": available
                    })
            
            device["stock_summary"] = {
                "total_stock": total_stock,
                "available_stock": available_stock,
                "stores": store_stock_list
            }
            
            return {"success": True, "data": device}
            
        except Exception as e:
            logger.error("取得設備資訊失敗", error=str(e))
            return {"success": False, "error": f"取得設備資訊失敗: {str(e)}"}
    
    async def get_recommended_devices(self, store_id: str, os_preference: str, 
                                      budget: float, is_flagship: Optional[bool] = None) -> Dict[str, Any]:
        """Tool 3: 取得推薦設備"""
        try:
            logger.info("Tool: get_recommended_devices", store_id=store_id, os=os_preference, budget=budget)
            
            if store_id not in self.mock_stock:
                return {"success": False, "error": f"門市 {store_id} 不存在"}
            
            store_stock = self.mock_stock[store_id]
            candidates = []
            
            for device_id, stock_info in store_stock.items():
                device = self.mock_devices.get(device_id)
                if not device:
                    continue
                
                if device["os"] != os_preference or device["price"] > budget:
                    continue
                if is_flagship is not None and device["is_flagship"] != is_flagship:
                    continue
                
                available = stock_info["quantity"] - stock_info["reserved"]
                if available <= 0:
                    continue
                
                # 計算推薦分數
                score = device["popularity_score"]
                price_ratio = device["price"] / budget
                if price_ratio >= 0.8:
                    score += 5
                elif price_ratio >= 0.6:
                    score += 3
                
                if device["is_flagship"]:
                    score += 3
                
                release_date = datetime.strptime(device["release_date"], "%Y-%m-%d")
                months_old = (datetime.now() - release_date).days / 30
                if months_old < 6:
                    score += 5
                elif months_old < 12:
                    score += 2
                
                if available >= 5:
                    score += 2
                
                candidates.append({
                    "device_id": device_id,
                    "brand": device["brand"],
                    "model": device["model"],
                    "storage": device["storage"],
                    "color": device["color"],
                    "price": device["price"],
                    "market_price": device["market_price"],
                    "discount": device["market_price"] - device["price"],
                    "is_flagship": device["is_flagship"],
                    "popularity_score": device["popularity_score"],
                    "available": available,
                    "recommendation_score": score,
                    "screen_size": device["screen_size"],
                    "camera": device["camera"],
                    "chip": device["chip"]
                })
            
            candidates.sort(key=lambda x: x["recommendation_score"], reverse=True)
            recommendations = candidates[:5]
            
            if not recommendations:
                return {"success": False, "error": f"目前沒有符合條件的設備"}
            
            top = recommendations[0]
            reason = f"根據您的預算 ${budget:,.0f} 和 {os_preference} 偏好，"
            reason += f"推薦 {top['brand']} {top['model']}。"
            if top["is_flagship"]:
                reason += " 這是旗艦機型，性能卓越。"
            if top["discount"] > 0:
                reason += f" 目前特價中，省下 ${top['discount']:,.0f}。"
            
            return {
                "success": True,
                "data": {
                    "store_id": store_id,
                    "criteria": {"os_preference": os_preference, "budget": budget, "is_flagship": is_flagship},
                    "recommendation_count": len(recommendations),
                    "recommendations": recommendations,
                    "reason": reason
                }
            }
            
        except Exception as e:
            logger.error("產生推薦失敗", error=str(e))
            return {"success": False, "error": f"產生推薦失敗: {str(e)}"}
    
    async def reserve_device(self, store_id: str, device_id: str, 
                            customer_id: str, phone_number: str) -> Dict[str, Any]:
        """Tool 4: 預約設備"""
        try:
            logger.info("Tool: reserve_device", store_id=store_id, device_id=device_id)
            
            if store_id not in self.mock_stock:
                return {"success": False, "error": f"門市 {store_id} 不存在"}
            if device_id not in self.mock_devices:
                return {"success": False, "error": f"設備 {device_id} 不存在"}
            if device_id not in self.mock_stock[store_id]:
                return {"success": False, "error": f"門市 {store_id} 沒有設備 {device_id}"}
            
            stock_info = self.mock_stock[store_id][device_id]
            available = stock_info["quantity"] - stock_info["reserved"]
            
            if available <= 0:
                return {"success": False, "error": "該設備目前無庫存"}
            
            reservation_id = f"RSV{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
            expires_at = datetime.now() + timedelta(hours=24)
            
            self.mock_reservations[reservation_id] = {
                "reservation_id": reservation_id,
                "store_id": store_id,
                "device_id": device_id,
                "customer_id": customer_id,
                "phone_number": phone_number,
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "status": "active"
            }
            
            self.mock_stock[store_id][device_id]["reserved"] += 1
            device = self.mock_devices[device_id]
            
            return {
                "success": True,
                "data": {
                    "reservation_id": reservation_id,
                    "store_id": store_id,
                    "device": {
                        "device_id": device_id,
                        "brand": device["brand"],
                        "model": device["model"],
                        "storage": device["storage"],
                        "color": device["color"],
                        "price": device["price"]
                    },
                    "customer_id": customer_id,
                    "phone_number": phone_number,
                    "created_at": self.mock_reservations[reservation_id]["created_at"],
                    "expires_at": expires_at.isoformat(),
                    "remaining_stock": available - 1
                }
            }
            
        except Exception as e:
            logger.error("預約失敗", error=str(e))
            return {"success": False, "error": f"預約失敗: {str(e)}"}
    
    async def get_device_pricing(self, device_id: str, 
                                 plan_type: Optional[str] = None) -> Dict[str, Any]:
        """Tool 5: 取得設備價格資訊"""
        try:
            logger.info("Tool: get_device_pricing", device_id=device_id, plan_type=plan_type)
            
            if device_id not in self.mock_devices:
                return {"success": False, "error": f"設備 {device_id} 不存在"}
            
            device = self.mock_devices[device_id]
            base_price = device["price"]
            market_price = device["market_price"]
            
            pricing_plans = []
            
            if not plan_type or plan_type == "攜碼":
                mnp_discount = base_price * 0.15
                pricing_plans.append({
                    "plan_type": "攜碼",
                    "original_price": base_price,
                    "discount": mnp_discount,
                    "final_price": base_price - mnp_discount,
                    "discount_rate": 15,
                    "description": "攜碼享85折優惠"
                })
            
            if not plan_type or plan_type == "續約":
                renewal_discount = base_price * 0.10
                pricing_plans.append({
                    "plan_type": "續約",
                    "original_price": base_price,
                    "discount": renewal_discount,
                    "final_price": base_price - renewal_discount,
                    "discount_rate": 10,
                    "description": "續約享9折優惠"
                })
            
            if not plan_type or plan_type == "新申辦":
                new_discount = base_price * 0.05
                pricing_plans.append({
                    "plan_type": "新申辦",
                    "original_price": base_price,
                    "discount": new_discount,
                    "final_price": base_price - new_discount,
                    "discount_rate": 5,
                    "description": "新申辦享95折優惠"
                })
            
            pricing_plans.append({
                "plan_type": "現金價",
                "original_price": base_price,
                "discount": 0,
                "final_price": base_price,
                "discount_rate": 0,
                "description": "直接購買無合約"
            })
            
            installment_options = []
            for months in [12, 24, 30]:
                installment_options.append({
                    "months": months,
                    "monthly_payment": round(base_price / months, 0),
                    "total": base_price,
                    "interest_rate": 0
                })
            
            return {
                "success": True,
                "data": {
                    "device_id": device_id,
                    "brand": device["brand"],
                    "model": device["model"],
                    "storage": device["storage"],
                    "base_price": base_price,
                    "market_price": market_price,
                    "market_discount": market_price - base_price,
                    "pricing_plans": pricing_plans,
                    "installment_options": installment_options
                }
            }
            
        except Exception as e:
            logger.error("取得價格資訊失敗", error=str(e))
            return {"success": False, "error": f"取得價格資訊失敗: {str(e)}"}


# ==================== 主程式 ====================

async def main():
    """主程式：啟動 POS MCP Server"""
    server = POSServer()
    server.register_tools()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
