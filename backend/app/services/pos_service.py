"""
Mock POS Service

提供 Mock 模式的 POS 功能，用於開發和測試
與 POS MCP Server 保持相同的介面，共享相同的 Mock 資料
"""
import sys
from pathlib import Path
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random

logger = structlog.get_logger()

# 匯入 POSServer 的 Mock 資料初始化方法
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))
from pos_server import POSServer as BasePOSServer

class MockPOSService:
    """
    Mock POS Service
    
    提供與 POS MCP Server 相同的介面，但使用 Mock 資料
    與 POS MCP Server 共享相同的 Mock 資料，避免重複定義
    適合用於開發、測試和無 MCP Server 的環境
    """
    
    def __init__(self):
        # 從 POSServer 複製 Mock 資料
        base_server = BasePOSServer()
        self.mock_devices = base_server.mock_devices
        self.mock_stock = base_server.mock_stock
        self.mock_reservations = {}
        
        logger.info(
            "Mock POS Service 初始化",
            devices_count=len(self.mock_devices),
            stores_count=len(self.mock_stock)
        )
    
    async def query_device_stock(self, store_id: str, os_filter: Optional[str] = None,
                                  min_price: Optional[float] = None, 
                                  max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """查詢門市設備庫存"""
        logger.info(
            "Mock: query_device_stock",
            store_id=store_id,
            os_filter=os_filter,
            min_price=min_price,
            max_price=max_price
        )
        
        if store_id not in self.mock_stock:
            logger.warning("門市不存在", store_id=store_id)
            return []
        
        store_stock = self.mock_stock[store_id]
        devices = []
        total_checked = 0
        filtered_by_os = 0
        
        for device_id, stock_info in store_stock.items():
            total_checked += 1
            device = self.mock_devices.get(device_id)
            if not device:
                continue
            
            # 過濾條件
            if os_filter and device["os"].lower() != os_filter.lower():
                filtered_by_os += 1
                logger.debug(
                    "OS 過濾",
                    device_id=device_id,
                    device_os=device["os"],
                    filter_os=os_filter
                )
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
        
        logger.info(
            "Mock: query_device_stock 結果",
            total_checked=total_checked,
            filtered_by_os=filtered_by_os,
            result_count=len(devices)
        )
        
        return devices
    
    async def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """取得設備詳細資訊"""
        logger.debug("Mock: get_device_info", device_id=device_id)
        
        if device_id not in self.mock_devices:
            logger.warning("設備不存在", device_id=device_id)
            return None
        
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
        
        return device
    
    async def get_recommended_devices(self, store_id: str, os_preference: str, 
                                      budget: float, is_flagship: Optional[bool] = None) -> Dict[str, Any]:
        """取得推薦設備"""
        logger.debug("Mock: get_recommended_devices", store_id=store_id, os=os_preference, budget=budget)
        
        if store_id not in self.mock_stock:
            return {
                "recommendations": [],
                "reason": f"門市 {store_id} 不存在"
            }
        
        store_stock = self.mock_stock[store_id]
        candidates = []
        
        for device_id, stock_info in store_stock.items():
            device = self.mock_devices.get(device_id)
            if not device:
                continue
            
            if device["os"].lower() != os_preference.lower() or device["price"] > budget:
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
                "chip": device["chip"],
                "battery": device["battery"]
            })
        
        candidates.sort(key=lambda x: x["recommendation_score"], reverse=True)
        recommendations = candidates[:5]
        
        if not recommendations:
            return {
                "recommendations": [],
                "reason": f"目前沒有符合條件的設備 (預算: {budget}, 系統: {os_preference})"
            }
        
        top = recommendations[0]
        reason = f"根據您的預算 ${budget:,.0f} 和 {os_preference} 偏好，"
        reason += f"推薦 {top['brand']} {top['model']}。"
        if top["is_flagship"]:
            reason += " 這是旗艦機型，性能卓越。"
        if top["discount"] > 0:
            reason += f" 目前特價中，省下 ${top['discount']:,.0f}。"
        
        return {
            "recommendations": recommendations,
            "reason": reason
        }
    
    async def reserve_device(self, store_id: str, device_id: str, 
                            customer_id: str, phone_number: str) -> Optional[Dict[str, Any]]:
        """預約設備"""
        logger.debug("Mock: reserve_device", store_id=store_id, device_id=device_id)
        
        if store_id not in self.mock_stock:
            logger.warning("門市不存在", store_id=store_id)
            return None
        if device_id not in self.mock_devices:
            logger.warning("設備不存在", device_id=device_id)
            return None
        if device_id not in self.mock_stock[store_id]:
            logger.warning("門市沒有此設備", store_id=store_id, device_id=device_id)
            return None
        
        stock_info = self.mock_stock[store_id][device_id]
        available = stock_info["quantity"] - stock_info["reserved"]
        
        if available <= 0:
            logger.warning("庫存不足", store_id=store_id, device_id=device_id)
            return None
        
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
        
        logger.info("預約成功", reservation_id=reservation_id)
        
        return {
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
    
    async def get_device_pricing(self, device_id: str, 
                                 plan_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """取得設備價格資訊"""
        logger.debug("Mock: get_device_pricing", device_id=device_id, plan_type=plan_type)
        
        if device_id not in self.mock_devices:
            logger.warning("設備不存在", device_id=device_id)
            return None
        
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
