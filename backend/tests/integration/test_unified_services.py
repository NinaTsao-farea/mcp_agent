"""
測試統一後的三個 Mock Service
驗證所有服務都能正確從對應的 MCP Server 重用 Mock 資料
"""
import asyncio
import sys
from pathlib import Path

# 確保能夠 import app 目錄下的模組
sys.path.insert(0, str(Path(__file__).parent))

from app.services.crm_service import MockCRMService
from app.services.pos_service import MockPOSService
from app.services.promotion_service import MockPromotionService


async def test_crm_service():
    """測試 CRM Service"""
    print("\n" + "="*60)
    print("測試 CRM Service (從 BaseCRMServer 重用資料)")
    print("="*60)
    
    service = MockCRMService()
    
    # 測試 1: 查詢客戶
    print("\n[測試 1] 查詢客戶 A123456789")
    customer = await service.query_customer_by_id("A123456789")
    if customer:
        print(f"✅ 找到客戶: {customer['name']} (ID: {customer['customer_id']})")
        print(f"   資料來源: {customer.get('_data_source', 'N/A')}")
    else:
        print("❌ 未找到客戶")
        return False
    
    # 測試 2: 查詢客戶門號
    print("\n[測試 2] 查詢客戶 C123456 的門號")
    phones = await service.get_customer_phones("C123456")
    if phones:
        print(f"✅ 找到 {len(phones)} 個門號:")
        for phone in phones:
            print(f"   - {phone['phone_number']}: {phone['plan_name']} (月租 ${phone['monthly_fee']})")
    else:
        print("❌ 未找到門號")
        return False
    
    # 測試 3: 查詢門號合約
    print("\n[測試 3] 查詢門號 0912345678 的合約")
    contract = await service.get_phone_contract("0912345678")
    if contract:
        print(f"✅ 找到合約: {contract['plan_name']}")
        print(f"   合約狀態: {contract['status']}")
        print(f"   到期日期: {contract['contract_end_date']}")
    else:
        print("❌ 未找到合約")
        return False
    
    print("\n✅ CRM Service 測試通過!")
    return True


async def test_pos_service():
    """測試 POS Service"""
    print("\n" + "="*60)
    print("測試 POS Service (從 BasePOSServer 重用資料)")
    print("="*60)
    
    service = MockPOSService()
    
    # 測試 1: 查詢門市庫存 (所有設備)
    print("\n[測試 1] 查詢 STORE001 的所有設備庫存")
    devices = await service.query_device_stock("STORE001")
    if devices:
        print(f"✅ 找到 {len(devices)} 個設備:")
        for dev in devices[:3]:  # 只顯示前 3 個
            print(f"   - {dev['brand']} {dev['model']}: 可用 {dev['available']} 台")
    else:
        print("❌ 未找到設備")
        return False
    
    # 測試 2: 過濾 iOS 設備
    print("\n[測試 2] 查詢 STORE001 的 iOS 設備")
    ios_devices = await service.query_device_stock("STORE001", os_filter="iOS")
    if ios_devices:
        print(f"✅ 找到 {len(ios_devices)} 個 iOS 設備:")
        for dev in ios_devices:
            print(f"   - {dev['brand']} {dev['model']}: {dev['os']}")
    else:
        print("❌ 未找到 iOS 設備")
        return False
    
    # 測試 3: 過濾 Android 設備 (測試 case-insensitive)
    print("\n[測試 3] 查詢 STORE001 的 Android 設備 (小寫)")
    android_devices = await service.query_device_stock("STORE001", os_filter="android")
    if android_devices:
        print(f"✅ 找到 {len(android_devices)} 個 Android 設備:")
        for dev in android_devices[:3]:
            print(f"   - {dev['brand']} {dev['model']}: {dev['os']}")
    else:
        print("❌ 未找到 Android 設備")
        return False
    
    # 測試 4: 取得設備詳情
    print("\n[測試 4] 取得設備 DEV001 的詳情")
    device_info = await service.get_device_info("DEV001")
    if device_info:
        print(f"✅ 找到設備: {device_info['brand']} {device_info['model']}")
        print(f"   總庫存: {device_info['stock_summary']['total_stock']} 台")
        print(f"   可用庫存: {device_info['stock_summary']['available_stock']} 台")
    else:
        print("❌ 未找到設備")
        return False
    
    print("\n✅ POS Service 測試通過!")
    return True


async def test_promotion_service():
    """測試 Promotion Service"""
    print("\n" + "="*60)
    print("測試 Promotion Service (從 BasePromotionServer 重用資料)")
    print("="*60)
    
    service = MockPromotionService()
    
    # 測試 1: 搜尋促銷方案 (續約)
    print("\n[測試 1] 搜尋續約促銷方案")
    result = await service.search_promotions("續約", contract_type="續約", limit=3)
    if result and result.get("promotions"):
        print(f"✅ 找到 {len(result['promotions'])} 個促銷方案:")
        for promo in result["promotions"]:
            print(f"   - {promo['title']} (相關性分數: {promo.get('relevance_score', 0)})")
    else:
        print("❌ 未找到促銷方案")
        return False
    
    # 測試 2: 取得方案詳情
    print("\n[測試 2] 取得方案 PLAN001 的詳情")
    plan = await service.get_plan_details("PLAN001")
    if plan:
        print(f"✅ 找到方案: {plan['name']}")
        print(f"   月租費: ${plan['monthly_fee']}")
        print(f"   上網: {plan['data']}")
        print(f"   適用促銷: {plan.get('total_promotions', 0)} 個")
    else:
        print("❌ 未找到方案")
        return False
    
    # 測試 3: 比較方案
    print("\n[測試 3] 比較兩個方案")
    comparison = await service.compare_plans(["PLAN001", "PLAN002"])
    if comparison and comparison.get("plans"):
        print(f"✅ 比較結果:")
        print(f"   方案數量: {len(comparison['plans'])}")
        print(f"   月租費範圍: ${comparison['comparison']['monthly_fee']['min']} ~ ${comparison['comparison']['monthly_fee']['max']}")
        print(f"   推薦: {comparison.get('recommendation', 'N/A')}")
    else:
        print("❌ 比較失敗")
        return False
    
    print("\n✅ Promotion Service 測試通過!")
    return True


async def main():
    """執行所有測試"""
    print("\n" + "="*60)
    print("統一 Mock Service 資料來源測試")
    print("方案 A: 三個 Service 都從對應的 MCP Server 重用 Mock 資料")
    print("="*60)
    
    results = []
    
    # 測試 CRM Service
    try:
        result = await test_crm_service()
        results.append(("CRM Service", result))
    except Exception as e:
        print(f"\n❌ CRM Service 測試失敗: {e}")
        results.append(("CRM Service", False))
    
    # 測試 POS Service
    try:
        result = await test_pos_service()
        results.append(("POS Service", result))
    except Exception as e:
        print(f"\n❌ POS Service 測試失敗: {e}")
        results.append(("POS Service", False))
    
    # 測試 Promotion Service
    try:
        result = await test_promotion_service()
        results.append(("Promotion Service", result))
    except Exception as e:
        print(f"\n❌ Promotion Service 測試失敗: {e}")
        results.append(("Promotion Service", False))
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    for service_name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{service_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 所有測試通過！三個 Service 已成功統一資料來源！")
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤訊息")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
