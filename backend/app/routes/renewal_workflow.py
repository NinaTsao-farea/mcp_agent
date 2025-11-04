"""
續約工作流程路由
"""
from quart import Blueprint, request, jsonify, current_app
import structlog
import json
from datetime import datetime

from ..services.workflow_session import WorkflowSessionManager, WorkflowStep
from ..services.crm_factory import get_crm_service
from ..services.pos_factory import get_pos_service
from ..services.promotion_factory import get_promotion_service
from ..utils.exceptions import APIException

logger = structlog.get_logger()
bp = Blueprint('renewal_workflow', __name__)


def get_workflow_manager() -> WorkflowSessionManager:
    """取得工作流程管理器"""
    return WorkflowSessionManager(current_app.redis_manager)


@bp.route('/start', methods=['POST'])
async def start_workflow():
    """
    開始續約流程
    
    自動清除該員工之前未完成的續約 Session，確保每次都能重新開始
    """
    try:        
        # 取得當前登入使用者
        if not hasattr(request, 'user') or not request.user:
            logger.warning("未登入或 Session 無效")
            return jsonify({"success": False, "error": "未登入"}), 401
        
        staff_id = request.user.get('staff_id')
        
        if not staff_id:
            logger.warning("無法取得 staff_id")
            return jsonify({"success": False, "error": "未登入"}), 401
        
        # 建立新的工作流程 Session（會自動清除舊的）
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.create_session(staff_id, clear_existing=True)
        
        logger.info(
            "開始續約流程",
            staff_id=staff_id,
            session_id=session_data["session_id"],
            current_step=session_data["current_step"]
        )
        
        return jsonify({
            "success": True,
            "message": "續約流程已開始",
            "session_id": session_data["session_id"],
            "current_step": session_data["current_step"]
        })
        
    except Exception as e:
        logger.error("開始續約流程錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/query-customer', methods=['POST'])
async def query_customer():
    """
    Step 1: 查詢客戶
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "id_number": "A123456789"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        id_number = data.get('id_number')
        
        if not session_id or not id_number:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 查詢客戶
        crm_service = await get_crm_service()
        customer = await crm_service.query_customer_by_id(id_number)
        
        if not customer:
            return jsonify({
                "success": False,
                "error": "查無此客戶",
                "message": "很抱歉，查無此身分證號的客戶資料"
            }), 404
        
        # 檢查是否為本公司客戶
        if not customer.get('is_company_customer'):
            return jsonify({
                "success": False,
                "error": "非本公司客戶",
                "message": "很抱歉，目前暫不提供新申辦服務，感謝您的詢問",
                "customer": {
                    "name": customer.get('name'),
                    "is_company_customer": False
                }
            }), 400
        
        # 更新 Session
        await workflow_manager.update_customer_selection(
            session_id,
            {
                "id_number": id_number,
                "customer_id": customer["customer_id"],
                "customer_name": customer["name"],
                "customer_phone": customer["phone"]
            }
        )
        
        # 轉換到 QUERY_CUSTOMER 狀態
        await workflow_manager.transition_to_step(session_id, WorkflowStep.QUERY_CUSTOMER)
        
        # 然後轉換到下一步驟
        await workflow_manager.transition_to_step(session_id, WorkflowStep.LIST_PHONES)
        
        logger.info(
            "客戶查詢成功",
            session_id=session_id,
            customer_id=customer["customer_id"]
        )
        
        return jsonify({
            "success": True,
            "message": "客戶查詢成功",
            "customer": {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "phone": customer["phone"],
                "email": customer.get("email"),
                "is_company_customer": True,
                "_data_source": customer.get("_data_source", "Unknown")  # 保留資料來源標記
            }
        })
        
    except Exception as e:
        logger.error("查詢客戶錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/list-phones', methods=['POST'])
async def list_phones():
    """
    Step 2-3: 列出客戶的所有門號
    
    Request Body:
        {
            "session_id": "renewal_xxx"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        customer_selection = session_data.get("customer_selection", {})
        customer_id = customer_selection.get("customer_id")
        
        if not customer_id:
            return jsonify({"success": False, "error": "請先查詢客戶"}), 400
        
        # 取得客戶門號列表
        crm_service = await get_crm_service()
        phones = await crm_service.get_customer_phones(customer_id)
        
        if not phones:
            return jsonify({
                "success": False,
                "error": "此客戶無門號",
                "message": "查無此客戶的門號資料"
            }), 404
        
        # 為每個門號補充詳細資訊
        phones_with_details = []
        for phone in phones:
            phone_number = phone["phone_number"]
            
            # 取得合約、使用量、帳單資訊
            contract = await crm_service.get_phone_contract(phone_number)
            usage = await crm_service.get_phone_usage(phone_number)
            billing = await crm_service.get_phone_billing(phone_number)
            
            phones_with_details.append({
                **phone,
                "contract": contract,
                "usage": usage,
                "billing": billing
            })
        
        # 轉換到 SELECT_PHONE 狀態
        await workflow_manager.transition_to_step(session_id, WorkflowStep.SELECT_PHONE)
        
        logger.info(
            "門號列表取得成功",
            session_id=session_id,
            customer_id=customer_id,
            phone_count=len(phones_with_details)
        )
        
        return jsonify({
            "success": True,
            "message": "門號列表取得成功",
            "phones": phones_with_details
        })
        
    except Exception as e:
        logger.error("列出門號錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/select-phone', methods=['POST'])
async def select_phone():
    """
    Step 3: 選擇門號並檢查續約資格
    
    允許從 Step 4-10 返回重選門號，返回時會清空所有後續選擇數據
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "phone_number": "0912345678"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        phone_number = data.get('phone_number')
        
        if not session_id or not phone_number:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查當前步驟：允許從 Step 3-10 的任何步驟訪問
        current_step = session_data.get("current_step")
        allowed_steps = [
            WorkflowStep.SELECT_PHONE.value,
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        
        if current_step not in allowed_steps:
            return jsonify({
                "success": False,
                "error": f"無法從 {current_step} 返回選擇門號，請先列出門號"
            }), 400
        
        customer_selection = session_data.get("customer_selection", {})
        customer_id = customer_selection.get("customer_id")
        
        if not customer_id:
            return jsonify({"success": False, "error": "請先查詢客戶"}), 400
        
        # 如果是從後續步驟返回，清空所有 Step 4-10 的選擇數據並重置狀態
        if current_step != WorkflowStep.SELECT_PHONE.value:
            logger.info(
                "用戶從後續步驟返回重選門號，清空所有後續數據",
                session_id=session_id,
                from_step=current_step,
                phone_number=phone_number
            )
            
            # 清空所有後續選擇數據
            fields_to_clear = [
                "selected_phone_number",
                "eligibility_check",
                "device_type",
                "device_os",
                "selected_device",
                "selected_plan",
                "device_data",
                "customer_data",
                "phone_data",
                "contract_data"
            ]
            
            updates = {field: None for field in fields_to_clear}
            await workflow_manager.update_customer_selection(session_id, updates)
            
            # 手動重置狀態到 SELECT_PHONE（繞過狀態轉換檢查）
            session_data['current_step'] = WorkflowStep.SELECT_PHONE.value
            session_data['updated_at'] = datetime.now().isoformat()
            await workflow_manager.redis.set_json(
                f"renewal_session:{session_id}",
                session_data,
                ex=3600
            )
            logger.info(
                "已重置工作流程狀態",
                session_id=session_id,
                new_step=WorkflowStep.SELECT_PHONE.value
            )
        
        # 檢查續約資格
        crm_service = await get_crm_service()
        eligibility = await crm_service.check_eligibility(phone_number, customer_id)
        
        # 更新 Session
        await workflow_manager.update_customer_selection(
            session_id,
            {
                "selected_phone_number": phone_number,
                "eligibility_check": eligibility
            }
        )
        
        # 先轉換到 CHECK_ELIGIBILITY 狀態
        await workflow_manager.transition_to_step(session_id, WorkflowStep.CHECK_ELIGIBILITY)
        
        if eligibility["eligible"]:
            # 轉換到下一步驟
            await workflow_manager.transition_to_step(
                session_id,
                WorkflowStep.SELECT_DEVICE_TYPE
            )
            
            logger.info(
                "門號選擇成功，符合續約資格",
                session_id=session_id,
                phone_number=phone_number
            )
            
            return jsonify({
                "success": True,
                "message": "此門號符合續約資格",
                "eligible": True,
                "eligibility": eligibility
            })
        else:
            # 不符合資格
            logger.warning(
                "門號不符合續約資格",
                session_id=session_id,
                phone_number=phone_number,
                reason=eligibility.get("reason", "未知原因")
            )
            
            return jsonify({
                "success": False,
                "message": "此門號不符合續約資格",
                "eligible": False,
                "eligibility": eligibility
            })
        
    except Exception as e:
        logger.error("選擇門號錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/select-device-type', methods=['POST'])
async def select_device_type():
    """
    Step 5: 選擇裝置類型
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "device_type": "none" | "smartphone" | "tablet" | "wearable"
        }
    
    Response:
        {
            "success": true,
            "message": "裝置類型已選擇",
            "device_type": "smartphone",
            "next_step": "select_device_os" | "list_plans"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        device_type = data.get('device_type')
        
        # 驗證參數
        if not session_id or not device_type:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證裝置類型
        valid_types = ["none", "smartphone", "tablet", "wearable"]
        if device_type not in valid_types:
            return jsonify({
                "success": False,
                "error": f"無效的裝置類型，必須是 {', '.join(valid_types)} 之一"
            }), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查當前步驟 - 允許從 Step 4 之後的所有步驟訪問
        current_step = session_data.get('current_step')
        allowed_steps = [
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step not in allowed_steps:
            return jsonify({
                "success": False,
                "error": f"當前步驟錯誤，無法從 {current_step} 返回選擇裝置類型"
            }), 400
        
        # 決定下一步
        if device_type == "none":
            next_step = WorkflowStep.LIST_PLANS
            next_step_name = "list_plans"
        else:
            next_step = WorkflowStep.SELECT_DEVICE_OS
            next_step_name = "select_device_os"
        
        # 判斷是否需要重置狀態
        # 只有從 SELECT_DEVICE_OS 或更後面的步驟返回時才需要重置
        # 從 CHECK_ELIGIBILITY 首次進入不需要重置
        needs_reset = False
        later_steps = [
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step in later_steps:
            # 從後續步驟返回，需要重置
            needs_reset = True
        
        if needs_reset:
            logger.info(
                "用戶從後續步驟返回重選裝置類型",
                session_id=session_id,
                from_step=current_step,
                device_type=device_type
            )
            
            # 手動重置狀態到 SELECT_DEVICE_TYPE（繞過狀態轉換檢查）
            session_data['current_step'] = WorkflowStep.SELECT_DEVICE_TYPE.value
            session_data['updated_at'] = datetime.now().isoformat()
            await workflow_manager.redis.set_json(
                f"renewal_session:{session_id}",
                session_data,
                ex=3600
            )
            logger.info(
                "已重置工作流程狀態",
                session_id=session_id,
                new_step=WorkflowStep.SELECT_DEVICE_TYPE.value
            )
        
        # 更新 Session - 儲存裝置類型選擇
        await workflow_manager.update_customer_selection(
            session_id,
            {"device_type": device_type}
        )
        
        # 處理 device_type == "none" 的特殊情況
        if device_type == "none":
            # 單純續約，跳過裝置選擇，直接到方案列表
            # 儲存空設備資料
            await workflow_manager.update_customer_selection(
                session_id,
                {
                    "device": {
                        "device_id": "none",
                        "brand": "無",
                        "model": "單純續約",
                        "color": "無"
                    }
                }
            )
        
        # 轉換狀態
        try:
            await workflow_manager.transition_to_step(session_id, next_step)
            logger.info(
                "狀態轉換成功",
                session_id=session_id,
                device_type=device_type,
                next_step=next_step_name
            )
        except ValueError as e:
            logger.error(
                "狀態轉換失敗",
                session_id=session_id,
                device_type=device_type,
                next_step=next_step_name,
                error=str(e)
            )
            return jsonify({"success": False, "error": f"狀態轉換失敗: {str(e)}"}), 400
        
        logger.info(
            "裝置類型已選擇",
            session_id=session_id,
            device_type=device_type,
            next_step=next_step_name
        )
        
        return jsonify({
            "success": True,
            "message": "裝置類型已選擇",
            "device_type": device_type,
            "next_step": next_step_name
        })
        
    except Exception as e:
        logger.error("選擇裝置類型錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/select-device-os', methods=['POST'])
async def select_device_os():
    """
    Step 6: 選擇裝置作業系統
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "os_type": "ios" | "android"
        }
    
    Response:
        {
            "success": true,
            "message": "作業系統已選擇",
            "os_type": "ios",
            "next_step": "select_device"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        os_type = data.get('os_type')
        
        # 驗證參數
        if not session_id or not os_type:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證作業系統類型
        valid_os = ["ios", "android"]
        os_type_lower = os_type.lower()
        if os_type_lower not in valid_os:
            return jsonify({
                "success": False,
                "error": f"無效的作業系統，必須是 {', '.join(valid_os)} 之一"
            }), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查當前步驟 - 允許從 Step 4 之後的所有步驟訪問
        current_step = session_data.get('current_step')
        allowed_steps = [
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step not in allowed_steps:
            return jsonify({
                "success": False,
                "error": f"當前步驟錯誤，無法從 {current_step} 返回選擇作業系統"
            }), 400
        
        # 如果是從後續步驟返回，先重置狀態到 SELECT_DEVICE_OS
        if current_step != WorkflowStep.SELECT_DEVICE_OS.value:
            logger.info(
                "用戶從後續步驟返回重選作業系統",
                session_id=session_id,
                from_step=current_step,
                os_type=os_type_lower
            )
            
            # 手動重置狀態到 SELECT_DEVICE_OS（繞過狀態轉換檢查）
            session_data['current_step'] = WorkflowStep.SELECT_DEVICE_OS.value
            session_data['updated_at'] = datetime.now().isoformat()
            await workflow_manager.redis.set_json(
                f"renewal_session:{session_id}",
                session_data,
                ex=3600
            )
            logger.info(
                "已重置工作流程狀態",
                session_id=session_id,
                new_step=WorkflowStep.SELECT_DEVICE_OS.value
            )
        
        # 更新 Session - 儲存作業系統選擇
        await workflow_manager.update_customer_selection(
            session_id,
            {"device_os": os_type_lower}
        )
        
        # 轉換狀態到 SELECT_DEVICE
        await workflow_manager.transition_to_step(session_id, WorkflowStep.SELECT_DEVICE)
        
        logger.info(
            "作業系統已選擇",
            session_id=session_id,
            os_type=os_type_lower
        )
        
        return jsonify({
            "success": True,
            "message": "作業系統已選擇",
            "os_type": os_type_lower,
            "next_step": "select_device"
        })
        
    except Exception as e:
        logger.error("選擇作業系統錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/query-devices', methods=['POST'])
async def query_devices():
    """
    Step 7: 查詢可用設備
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "store_id": "STORE001",
            "min_price": 20000,  # 選填
            "max_price": 40000   # 選填
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        store_id = data.get('store_id', 'STORE001')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查是否已選擇作業系統 (從 customer_selection 取得)
        customer_selection = session_data.get('customer_selection', {})
        os_preference = customer_selection.get('device_os')
        
        # Debug log
        logger.info(
            "query_devices: 檢查 OS",
            session_id=session_id,
            has_customer_selection=bool(customer_selection),
            os_preference=os_preference,
            customer_selection_keys=list(customer_selection.keys()) if customer_selection else []
        )
        
        if not os_preference:
            logger.warning(
                "query_devices: 未找到 device_os",
                session_id=session_id,
                customer_selection=customer_selection
            )
            return jsonify({
                "success": False,
                "error": "請先選擇作業系統"
            }), 400
        
        # 查詢設備庫存
        pos_service = await get_pos_service()
        devices = await pos_service.query_device_stock(
            store_id=store_id,
            os_filter=os_preference,
            min_price=min_price,
            max_price=max_price
        )
        
        logger.info(
            "查詢設備",
            session_id=session_id,
            store_id=store_id,
            os=os_preference,
            device_count=len(devices)
        )
        
        return jsonify({
            "success": True,
            "store_id": store_id,
            "os_preference": os_preference,
            "device_count": len(devices),
            "devices": devices
        })
        
    except Exception as e:
        logger.error("查詢設備錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/get-recommendations', methods=['POST'])
async def get_recommendations():
    """
    Step 7-1: 取得智能推薦設備
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "store_id": "STORE001",
            "budget": 35000,
            "is_flagship": true  # 選填
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        store_id = data.get('store_id', 'STORE001')
        budget = data.get('budget')
        is_flagship = data.get('is_flagship')
        
        if not session_id or not budget:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查是否已選擇作業系統 (從 customer_selection 取得)
        customer_selection = session_data.get('customer_selection', {})
        os_preference = customer_selection.get('device_os')
        
        if not os_preference:
            return jsonify({
                "success": False,
                "error": "請先選擇作業系統"
            }), 400
        
        # 取得推薦設備
        pos_service = await get_pos_service()
        result = await pos_service.get_recommended_devices(
            store_id=store_id,
            os_preference=os_preference,
            budget=budget,
            is_flagship=is_flagship
        )
        
        recommendations = result.get('recommendations', [])
        reason = result.get('reason', '')
        
        logger.info(
            "取得推薦設備",
            session_id=session_id,
            store_id=store_id,
            budget=budget,
            recommendation_count=len(recommendations)
        )
        
        return jsonify({
            "success": True,
            "store_id": store_id,
            "os_preference": os_preference,
            "budget": budget,
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
            "reason": reason
        })
        
    except Exception as e:
        logger.error("取得推薦設備錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/select-device', methods=['POST'])
async def select_device():
    """
    Step 7: 選擇設備
    
    Request Body:
        {
            "session_id": "renewal_xxx",
            "device_id": "DEV001",
            "color": "黑色"  # 選填
        }
    
    Response:
        {
            "success": true,
            "message": "設備已選擇",
            "device_id": "DEV001",
            "color": "黑色",
            "next_step": "list_plans"
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        device_id = data.get('device_id')
        color = data.get('color')
        
        # 驗證參數
        if not session_id or not device_id:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        # 檢查當前步驟 - 允許從 Step 4 之後的所有步驟訪問
        current_step = session_data.get('current_step')
        allowed_steps = [
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step not in allowed_steps:
            return jsonify({
                "success": False,
                "error": f"當前步驟錯誤，無法從 {current_step} 返回選擇設備"
            }), 400
        
        # 如果是從後續步驟返回，先重置狀態到 SELECT_DEVICE
        if current_step != WorkflowStep.SELECT_DEVICE.value:
            logger.info(
                "用戶從後續步驟返回重選設備",
                session_id=session_id,
                from_step=current_step,
                device_id=device_id
            )
            
            # 手動重置狀態到 SELECT_DEVICE（繞過狀態轉換檢查）
            session_data['current_step'] = WorkflowStep.SELECT_DEVICE.value
            session_data['updated_at'] = datetime.now().isoformat()
            await workflow_manager.redis.set_json(
                f"renewal_session:{session_id}",
                session_data,
                ex=3600
            )
            logger.info(
                "已重置工作流程狀態",
                session_id=session_id,
                new_step=WorkflowStep.SELECT_DEVICE.value
            )
        
        # 取得設備詳細資料 (從 POS service)
        pos_service = await get_pos_service()
        store_id = session_data.get('store_id', 'STORE001')
        
        # 查詢設備庫存以取得設備詳情
        devices = await pos_service.query_device_stock(store_id=store_id)
        device_detail = next((d for d in devices if d.get('device_id') == device_id), None)
        
        if not device_detail:
            return jsonify({"success": False, "error": "設備不存在"}), 404
        
        # 更新 Session - 儲存設備選擇
        await workflow_manager.update_customer_selection(
            session_id,
            {
                "device_id": device_id,
                "device_color": color if color else "預設"
            }
        )
        
        # 重新獲取 session_data（可能已被更新）
        session_data = await workflow_manager.get_session(session_id)
        
        # 將設備資料存入 session 頂層 (供 Step 10 confirm 使用)
        session_data['device'] = {
            **device_detail,
            "color": color if color else "預設"
        }
        await workflow_manager.update_session(session_id, session_data)
        
        # 轉換狀態到 LIST_PLANS
        await workflow_manager.transition_to_step(session_id, WorkflowStep.LIST_PLANS)
        
        logger.info(
            "設備已選擇",
            session_id=session_id,
            device_id=device_id,
            color=color
        )
        
        return jsonify({
            "success": True,
            "message": "設備已選擇",
            "device_id": device_id,
            "color": color if color else "預設",
            "next_step": "list_plans"
        })
        
    except Exception as e:
        logger.error("選擇設備錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/session/<session_id>', methods=['GET'])
async def get_session(session_id: str):
    """
    取得工作流程 Session 資料
    """
    try:
        workflow_manager = get_workflow_manager()
        session_data = await workflow_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({"success": False, "error": "Session 不存在或已過期"}), 404
        
        return jsonify({
            "success": True,
            "session": session_data
        })
        
    except Exception as e:
        logger.error("取得 Session 錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/session/<session_id>', methods=['DELETE'])
async def delete_session(session_id: str):
    """
    刪除工作流程 Session
    """
    try:
        workflow_manager = get_workflow_manager()
        success = await workflow_manager.delete_session(session_id)
        
        if not success:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        logger.info("刪除續約流程 Session", session_id=session_id)
        
        return jsonify({
            "success": True,
            "message": "Session 已刪除"
        })
        
    except Exception as e:
        logger.error("刪除 Session 錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


# ============================================================
# Step 8-9: 方案選擇與比較
# ============================================================

@bp.route('/step/search-promotions', methods=['POST'])
async def search_promotions():
    """Step 8: 搜尋促銷方案 (RAG)
    
    Request Body:
    {
        "session_id": "string",
        "query": "string",  # 搜尋查詢，例如：吃到飽方案、學生優惠
        "limit": 5  # 可選，預設 5
    }
    
    Response:
    {
        "success": true,
        "promotions": [...],
        "total": int,
        "query": "string"
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        query = data.get('query')
        limit = data.get('limit', 5)
        
        if not session_id or not query:
            return jsonify({
                "success": False,
                "error": "缺少必要參數 session_id 或 query"
            }), 400
        
        # 驗證 session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        logger.info(
            "搜尋促銷方案",
            session_id=session_id,
            query=query
        )
        
        # 呼叫 Promotion Service
        promotion_service = await get_promotion_service()
        
        # 根據 session 中的合約類型篩選
        contract_type = session.get('customer', {}).get('contract_type')
        
        result = await promotion_service.search_promotions(
            query=query,
            contract_type=contract_type,
            limit=limit
        )
        
        # 更新 session (記錄搜尋歷史)
        if 'search_history' not in session:
            session['search_history'] = []
        session['search_history'].append({
            "query": query,
            "timestamp": str(__import__('datetime').datetime.now()),
            "results_count": result.get('total', 0)
        })
        await workflow_manager.update_session(session_id, session)
        
        logger.info(
            "促銷方案搜尋完成",
            session_id=session_id,
            total=result.get('total', 0)
        )
        
        return jsonify({
            "success": True,
            "promotions": result.get('promotions', []),
            "total": result.get('total', 0),
            "query": query
        })
        
    except Exception as e:
        logger.error("搜尋促銷方案錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/step/get-plan-details', methods=['POST'])
async def get_plan_details():
    """Step 8: 取得方案詳情
    
    Request Body:
    {
        "session_id": "string",
        "plan_id": "string"
    }
    
    Response:
    {
        "success": true,
        "plan": {...},
        "applicable_promotions": [...]
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        plan_id = data.get('plan_id')
        
        if not session_id or not plan_id:
            return jsonify({
                "success": False,
                "error": "缺少必要參數"
            }), 400
        
        # 驗證 session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        logger.info(
            "取得方案詳情",
            session_id=session_id,
            plan_id=plan_id
        )
        
        # 呼叫 Promotion Service
        promotion_service = await get_promotion_service()
        plan = await promotion_service.get_plan_details(plan_id)
        
        if not plan:
            return jsonify({
                "success": False,
                "error": "方案不存在"
            }), 404
        
        logger.info(
            "方案詳情取得成功",
            session_id=session_id,
            plan_id=plan_id
        )
        
        return jsonify({
            "success": True,
            "plan": plan
        })
        
    except Exception as e:
        logger.error("取得方案詳情錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/step/calculate-upgrade-cost', methods=['POST'])
async def calculate_upgrade_cost():
    """Step 8-9: 計算升級費用
    
    Request Body:
    {
        "session_id": "string",
        "plan_id": "string",
        "include_device": true/false  # 是否包含手機費用
    }
    
    Response:
    {
        "success": true,
        "cost_details": {...}
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        plan_id = data.get('plan_id')
        include_device = data.get('include_device', True)
        
        if not session_id or not plan_id:
            return jsonify({
                "success": False,
                "error": "缺少必要參數"
            }), 400
        
        # 驗證 session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        logger.info(
            "計算升級費用",
            session_id=session_id,
            plan_id=plan_id
        )
        
        # 從 session 取得資料
        contract = session.get('contract', {})
        device = session.get('device', {})
        customer = session.get('customer', {})
        
        current_plan_fee = contract.get('monthly_fee', 0)
        device_price = 0
        if include_device and device.get('pricing'):
            device_price = device['pricing'].get('base_price', 0)
        
        contract_type = customer.get('contract_type', '續約')
        
        # 呼叫 Promotion Service
        promotion_service = await get_promotion_service()
        result = await promotion_service.calculate_upgrade_cost(
            current_plan_fee=current_plan_fee,
            new_plan_id=plan_id,
            device_price=device_price,
            contract_type=contract_type
        )
        
        if 'error' in result:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 400
        
        logger.info(
            "升級費用計算完成",
            session_id=session_id,
            total_cost=result.get('total_cost', 0)
        )
        
        return jsonify({
            "success": True,
            "cost_details": result
        })
        
    except Exception as e:
        logger.error("計算升級費用錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/step/list-plans', methods=['POST'])
async def list_plans():
    """Step 8: 列出可選方案
    
    使用 RAG 檢索相關促銷方案，並過濾出符合客戶資格的方案
    
    Request Body:
    {
        "session_id": "string"
    }
    
    Response:
    {
        "success": true,
        "plans": [
            {
                "plan_id": "PLAN001",
                "name": "5G 吃到飽方案",
                "monthly_fee": 1399,
                "data": "無限制",
                "voice": "網內免費",
                "contract_months": 30,
                "gifts": ["藍牙耳機"],
                "is_recommended": true
            }
        ],
        "total": 3
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        # 取得客戶選擇資料
        customer_selection = session.get('customer_selection', {})
        phone_number = customer_selection.get('selected_phone_number')
        device_type = customer_selection.get('device_type', 'smartphone')
        device_os = customer_selection.get('device_os')
        selected_device = customer_selection.get('selected_device')
        
        if not phone_number:
            return jsonify({
                "success": False,
                "error": "請先選擇門號"
            }), 400
        
        logger.info(
            "Step 8: 開始列出方案",
            session_id=session_id,
            phone_number=phone_number,
            device_type=device_type,
            has_device=bool(selected_device)
        )
        
        # 建構搜尋查詢
        query_parts = []
        
        # 根據裝置類型建構查詢
        # 注意：contract_type 必須與促銷資料中的 eligibility.contract_type 一致
        if device_type == 'none':
            query_parts.append("單純續約 不搭配裝置")
            contract_type = "續約"
        else:
            query_parts.append("續約搭配裝置")
            contract_type = "續約"  # 修正：使用「續約」而非「續約搭機」
            
            if device_os:
                query_parts.append(device_os)
            
            if selected_device:
                device_brand = selected_device.get('brand', '')
                device_model = selected_device.get('model', '')
                if device_brand and device_model:
                    query_parts.append(f"{device_brand} {device_model}")
        
        search_query = " ".join(query_parts)
        
        logger.info(
            "建構搜尋查詢",
            session_id=session_id,
            query=search_query,
            contract_type=contract_type
        )
        
        # 使用 Promotion Service 搜尋方案
        promotion_service = await get_promotion_service()
        search_result = await promotion_service.search_promotions(
            query=search_query,
            contract_type=contract_type,
            limit=10
        )
        
        promotions = search_result.get('promotions', [])
        
        logger.info(
            "RAG 檢索完成",
            session_id=session_id,
            promotions_found=len(promotions)
        )
        
        # 取得符合資格的方案詳情
        qualified_plans = []
        
        logger.info(
            "開始處理促銷方案",
            session_id=session_id,
            promotions_count=len(promotions)
        )
        
        for promo in promotions:
            # 取得促銷關聯的方案
            plan_ids = promo.get('plans', [])
            
            logger.debug(
                "處理促銷",
                promotion_id=promo.get("promotion_id"),
                promotion_title=promo.get("title"),
                plan_ids=plan_ids
            )
            
            for plan_id in plan_ids:
                plan = await promotion_service.get_plan_details(plan_id)
                
                if not plan:
                    logger.warning(
                        "方案不存在",
                        plan_id=plan_id,
                        promotion_id=promo.get("promotion_id")
                    )
                    continue
                
                logger.debug(
                    "方案詳情取得",
                    plan_id=plan_id,
                    plan_name=plan.get("name")
                )
                
                # TODO: 可在此處加入資格檢查邏輯
                # 例如：檢查在網時間、月消費門檻等
                
                # 組合方案資訊
                plan_info = {
                    "plan_id": plan["plan_id"],
                    "name": plan["name"],
                    "monthly_fee": plan["monthly_fee"],
                    "data": plan.get("data", "未提供"),
                    "voice": plan.get("voice", "未提供"),
                    "sms": plan.get("sms", "不限"),
                    "contract_months": plan["contract_months"],
                    "gifts": plan.get("gifts", []),
                    "promotion_id": promo["promotion_id"],
                    "promotion_title": promo["title"],
                    "relevance_score": promo.get("relevance_score", 0),
                    "is_recommended": promo.get("priority", 0) >= 8
                }
                
                # 避免重複
                if not any(p["plan_id"] == plan_id for p in qualified_plans):
                    qualified_plans.append(plan_info)
        
        # 依相關性和推薦度排序
        qualified_plans.sort(
            key=lambda x: (x["is_recommended"], x["relevance_score"]),
            reverse=True
        )
        
        # 更新 Session 狀態
        session['current_step'] = WorkflowStep.LIST_PLANS.value
        await workflow_manager.update_session(session_id, session)
        
        logger.info(
            "Step 8: 列出方案完成",
            session_id=session_id,
            qualified_plans_count=len(qualified_plans)
        )
        
        return jsonify({
            "success": True,
            "plans": qualified_plans,
            "total": len(qualified_plans),
            "search_query": search_query
        })
        
    except Exception as e:
        logger.error("列出方案錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/compare-plans', methods=['POST'])
async def compare_plans():
    """Step 9: 比較方案
    
    Request body:
    {
        "session_id": "uuid",
        "plan_ids": ["PLAN001", "PLAN002", "PLAN003"]
    }
    
    Response:
    {
        "success": true,
        "comparison": {
            "plans": [...],
            "comparison": {...},
            "recommendation": "..."
        }
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        plan_ids = data.get('plan_ids', [])
        
        logger.info(
            "Step 9: 比較方案",
            session_id=session_id,
            plan_ids=plan_ids
        )
        
        # 初始化服務
        workflow_manager = get_workflow_manager()
        promotion_service = await get_promotion_service()
        
        # 驗證 Session
        session = await workflow_manager.get_session(session_id)
        if not session:
            logger.warning("Session 不存在", session_id=session_id)
            return jsonify({"success": False, "error": "Session 不存在"}), 401
        
        # 驗證當前步驟 - 允許從 Step 4 之後的所有步驟訪問
        current_step = session.get('current_step')
        allowed_steps = [
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step not in allowed_steps:
            logger.warning(
                "當前步驟不正確",
                session_id=session_id,
                current_step=current_step
            )
            return jsonify({
                "success": False,
                "error": f"無法從 {current_step} 訪問比較方案"
            }), 400
        
        # 驗證 plan_ids
        if not plan_ids or not isinstance(plan_ids, list):
            return jsonify({
                "success": False,
                "error": "請提供要比較的方案 ID 列表"
            }), 400
        
        if len(plan_ids) < 2:
            return jsonify({
                "success": False,
                "error": "至少需要選擇 2 個方案進行比較"
            }), 400
        
        if len(plan_ids) > 4:
            return jsonify({
                "success": False,
                "error": "最多只能比較 4 個方案"
            }), 400
        
        # 調用促銷服務進行方案比較
        comparison_result = await promotion_service.compare_plans(plan_ids)
        
        if "error" in comparison_result:
            logger.warning(
                "比較方案失敗",
                session_id=session_id,
                error=comparison_result["error"]
            )
            return jsonify({
                "success": False,
                "error": comparison_result["error"]
            }), 400
        
        # 儲存比較結果到 session
        session['comparison_result'] = comparison_result
        session['compared_plan_ids'] = plan_ids
        session['current_step'] = WorkflowStep.COMPARE_PLANS.value
        await workflow_manager.update_session(session_id, session)
        
        logger.info(
            "Step 9: 比較方案完成",
            session_id=session_id,
            compared_plans_count=len(comparison_result.get('plans', []))
        )
        
        return jsonify({
            "success": True,
            "comparison": comparison_result
        })
        
    except Exception as e:
        logger.error("比較方案錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "系統錯誤"}), 500


@bp.route('/step/select-plan', methods=['POST'])
async def select_plan():
    """Step 8-9: 選擇方案
    
    Request Body:
    {
        "session_id": "string",
        "plan_id": "string"
    }
    
    Response:
    {
        "success": true,
        "message": "方案已選擇",
        "next_step": "CONFIRM"
    }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        plan_id = data.get('plan_id')
        
        if not session_id or not plan_id:
            return jsonify({
                "success": False,
                "error": "缺少必要參數"
            }), 400
        
        # 驗證 session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        logger.info(
            "選擇方案",
            session_id=session_id,
            plan_id=plan_id
        )
        
        # 取得方案詳情
        promotion_service = await get_promotion_service()
        plan = await promotion_service.get_plan_details(plan_id)
        
        if not plan:
            return jsonify({
                "success": False,
                "error": "方案不存在"
            }), 404
        
        # 計算費用
        contract = session.get('contract', {})
        device = session.get('device', {})
        customer = session.get('customer', {})
        
        device_price = 0
        if device.get('pricing'):
            device_price = device['pricing'].get('base_price', 0)
        
        cost_result = await promotion_service.calculate_upgrade_cost(
            current_plan_fee=contract.get('monthly_fee', 0),
            new_plan_id=plan_id,
            device_price=device_price,
            contract_type=customer.get('contract_type', '續約')
        )
        
        # 更新 session
        session['selected_plan'] = {
            "plan_id": plan_id,
            "plan_name": plan['name'],
            "monthly_fee": plan['monthly_fee'],
            "contract_months": plan['contract_months'],
            "data": plan['data'],
            "voice": plan['voice'],
            "cost_details": cost_result,
            "selected_at": str(__import__('datetime').datetime.now())
        }
        
        # 前進到 CONFIRM 步驟
        session['current_step'] = WorkflowStep.CONFIRM.value
        await workflow_manager.update_session(session_id, session)
        
        logger.info(
            "方案選擇完成",
            session_id=session_id,
            plan_id=plan_id,
            next_step="CONFIRM"
        )
        
        return jsonify({
            "success": True,
            "message": "方案已選擇",
            "next_step": "CONFIRM",
            "selected_plan": session['selected_plan']
        })
        
    except Exception as e:
        logger.error("選擇方案錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/step/confirm', methods=['POST'])
async def confirm_application():
    """
    Step 10: 確認申辦
    
    顯示完整申辦摘要，讓門市人員最後確認
    
    Request Body:
        {
            "session_id": "renewal_xxx"
        }
    
    Response:
        {
            "success": true,
            "summary": {
                "customer": {...},      # 客戶資料
                "phone": {...},         # 門號資料
                "contract": {...},      # 合約資料
                "selected_device": {...}, # 選擇的手機
                "selected_plan": {...}, # 選擇的方案
                "cost_summary": {...}   # 費用總結
            }
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        # 檢查當前步驟 - 允許從 Step 4 之後的所有步驟訪問
        current_step = session.get('current_step')
        allowed_steps = [
            WorkflowStep.CHECK_ELIGIBILITY.value,
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        if current_step not in allowed_steps:
            return jsonify({
                "success": False,
                "error": f"無法從 {current_step} 訪問確認頁面"
            }), 400
        
        # 取得或驗證必要資料
        customer_selection = session.get('customer_selection', {})
        selected_plan = session.get('selected_plan')
        selected_device = session.get('device')
        
        # 如果頂層沒有資料，從 customer_selection 和 services 取得
        customer = session.get('customer')
        phone = session.get('phone')
        contract = session.get('contract')
        
        # 動態取得缺失的資料
        crm_service = await get_crm_service()
        
        if not customer and customer_selection.get('id_number'):
            customer = await crm_service.query_customer_by_id(
                customer_selection.get('id_number')
            )
        
        if not phone and customer_selection.get('selected_phone_number'):
            phone_number = customer_selection.get('selected_phone_number')
            customer_id = customer_selection.get('customer_id')
            phones_list = await crm_service.get_customer_phones(customer_id)
            phone = next(
                (p for p in phones_list if p["phone_number"] == phone_number),
                None
            )
        
        if not contract and customer_selection.get('selected_phone_number'):
            contract = await crm_service.get_phone_contract(
                customer_selection.get('selected_phone_number')
            )
        
        # 驗證必要資料完整性
        missing_fields = []
        if not customer:
            missing_fields.append('客戶資料')
        if not phone:
            missing_fields.append('門號資料')
        if not contract:
            missing_fields.append('合約資料')
        if not selected_plan:
            missing_fields.append('方案選擇')
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"申辦資料不完整：缺少 {', '.join(missing_fields)}"
            }), 400
        
        # 組裝完整申辦摘要
        summary = {
            "customer": {
                "name": customer.get('name'),
                "id_number": customer.get('id_number'),
                "phone": customer.get('phone'),
                "email": customer.get('email'),
                "address": customer.get('address'),
                "contract_type": customer.get('contract_type', '續約')
            },
            "phone": {
                "phone_number": phone.get('phone_number'),
                "status": phone.get('status')
            },
            "contract": {
                "plan_name": contract.get('plan_name'),
                "monthly_fee": contract.get('monthly_fee'),
                "contract_start": contract.get('contract_start_date'),
                "contract_end": contract.get('contract_end_date'),
                "remaining_months": contract.get('remaining_contract_months', 0)
            },
            "selected_device": {
                "brand": selected_device.get('brand', '無'),
                "model": selected_device.get('model', '無'),
                "color": selected_device.get('color', '無'),
                "storage": selected_device.get('storage', '無'),
                "price": selected_device.get('pricing', {}).get('base_price', 0) if selected_device else 0
            } if selected_device else None,
            "selected_plan": {
                "plan_name": selected_plan.get('plan_name'),
                "monthly_fee": selected_plan.get('monthly_fee'),
                "contract_months": selected_plan.get('contract_months'),
                "data": selected_plan.get('data'),
                "voice": selected_plan.get('voice')
            },
            "cost_summary": selected_plan.get('cost_details', {})
        }
        
        # 計算總費用
        cost_details = selected_plan.get('cost_details', {})
        total_amount = (
            cost_details.get('device_payment', 0) +
            cost_details.get('contract_breach_fee', 0) +
            cost_details.get('activation_fee', 0)
        )
        
        summary['total_amount'] = total_amount
        
        logger.info(
            "顯示確認申辦摘要",
            session_id=session_id,
            customer_name=customer.get('name'),
            total_amount=total_amount
        )
        
        return jsonify({
            "success": True,
            "message": "請確認申辦資料",
            "summary": summary
        })
        
    except Exception as e:
        logger.error("確認申辦錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/step/submit', methods=['POST'])
async def submit_application():
    """
    Step 10: 提交申辦
    
    將申辦資料寫入資料庫，更新 RenewalSessions 狀態，記錄 CustomerServiceLogs
    
    Request Body:
        {
            "session_id": "renewal_xxx"
        }
    
    Response:
        {
            "success": true,
            "message": "申辦成功",
            "session_id": "renewal_xxx",
            "order_number": "ORD20240129001" // 申辦單號
        }
    """
    try:
        data = await request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        # 檢查當前步驟
        current_step = session.get('current_step')
        if current_step != WorkflowStep.CONFIRM.value:
            return jsonify({
                "success": False,
                "error": f"當前步驟為 {current_step}，必須先確認申辦"
            }), 400
        
        # 再次驗證必要資料
        customer = session.get('customer')
        phone = session.get('phone')
        selected_plan = session.get('selected_plan')
        staff_id = session.get('staff_id')
        
        if not all([customer, phone, selected_plan, staff_id]):
            return jsonify({
                "success": False,
                "error": "申辦資料不完整"
            }), 400
        
        # 計算總金額
        cost_details = selected_plan.get('cost_details', {})
        total_amount = (
            cost_details.get('device_payment', 0) +
            cost_details.get('contract_breach_fee', 0) +
            cost_details.get('activation_fee', 0)
        )
        
        # 生成申辦單號（格式：ORD + 日期 + 流水號）
        import datetime
        today = datetime.datetime.now().strftime('%Y%m%d')
        order_number = f"ORD{today}{session_id[-6:]}"
        
        # 取得資料庫連線
        oracle_manager = current_app.oracle_manager
        
        try:
            # 開始資料庫交易
            # 1. 更新 RenewalSessions
            update_session_sql = """
                UPDATE renewal_sessions
                SET status = 'COMPLETED',
                    is_sale_confirmed = 1,
                    total_amount = :total_amount,
                    completed_at = SYSDATE,
                    updated_at = SYSDATE
                WHERE session_id = :session_id
            """
            
            await oracle_manager.execute(
                update_session_sql,
                {
                    'session_id': session_id,
                    'total_amount': total_amount
                }
            )
            
            # 2. 記錄 CustomerServiceLogs
            service_log_sql = """
                INSERT INTO customer_service_logs (
                    staff_id, customer_id, service_type, service_result, notes, created_at
                )
                VALUES (
                    :staff_id, :customer_id, 'renewal', 'completed', :notes, SYSDATE
                )
            """
            
            notes = f"續約申辦完成 - 方案: {selected_plan.get('plan_name')}, 總金額: {total_amount}"
            
            await oracle_manager.execute(
                service_log_sql,
                {
                    'staff_id': staff_id,
                    'customer_id': customer.get('customer_id'),
                    'notes': notes
                }
            )
            
            logger.info(
                "申辦提交成功",
                session_id=session_id,
                order_number=order_number,
                customer_id=customer.get('customer_id'),
                total_amount=total_amount
            )
            
        except Exception as db_error:
            logger.error(
                "資料庫更新失敗",
                session_id=session_id,
                error=str(db_error),
                exc_info=True
            )
            return jsonify({
                "success": False,
                "error": "資料庫更新失敗，請稍後再試"
            }), 500
        
        # 更新 Redis Session 狀態
        session['current_step'] = WorkflowStep.COMPLETED.value
        session['order_number'] = order_number
        session['completed_at'] = str(datetime.datetime.now())
        await workflow_manager.update_session(session_id, session)
        
        return jsonify({
            "success": True,
            "message": "申辦成功",
            "session_id": session_id,
            "order_number": order_number,
            "total_amount": total_amount
        })
        
    except Exception as e:
        logger.error("提交申辦錯誤", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/chat/stream', methods=['GET'])
async def chat_stream():
    """
    AI 自由對話 (SSE 串流)
    
    Sprint 7 新增功能：門市人員可以在 Step 5 之後隨時向 AI 詢問問題
    
    Query Parameters:
        session_id: 續約流程 Session ID
        message: 用戶訊息
    
    Response: Server-Sent Events (SSE)
        event: message
        data: {"type": "message", "content": "..."}
        
        event: function_call
        data: {"type": "function_call", "name": "compare_plans", "arguments": {...}}
        
        event: function_result
        data: {"type": "function_result", "name": "compare_plans", "result": {...}}
        
        event: done
        data: {"type": "done", "tokens": {"prompt": 150, "completion": 200, "total": 350}}
        
        event: error
        data: {"type": "error", "error": "..."}
    """
    try:
        # 取得當前登入使用者
        if not hasattr(request, 'user') or not request.user:
            logger.warning("未登入或 Session 無效")
            return jsonify({"success": False, "error": "未登入"}), 401
        
        staff_id = request.user.get('staff_id')
        
        if not staff_id:
            logger.warning("無法取得 staff_id")
            return jsonify({"success": False, "error": "未登入"}), 401
        
        # 從 query parameters 取得請求資料（EventSource 使用 GET）
        # 注意：session_id 是認證用的，renewal_session_id 才是續約流程的
        renewal_session_id = request.args.get('renewal_session_id')
        message = request.args.get('message')
        
        if not renewal_session_id:
            logger.warning("缺少 renewal_session_id")
            return jsonify({"success": False, "error": "缺少 renewal_session_id"}), 400
        
        if not message:
            logger.warning("缺少 message")
            return jsonify({"success": False, "error": "缺少 message"}), 400
        
        # 驗證 Session
        workflow_manager = get_workflow_manager()
        session = await workflow_manager.get_session(renewal_session_id)
        
        if not session:
            logger.warning("Session 不存在", renewal_session_id=renewal_session_id)
            return jsonify({"success": False, "error": "Session 不存在"}), 404
        
        # 檢查是否為該員工的 Session
        if session.get('staff_id') != staff_id:
            logger.warning("Session 不屬於該員工", renewal_session_id=renewal_session_id, staff_id=staff_id)
            return jsonify({"success": False, "error": "Session 不屬於該員工"}), 403
        
        # 檢查是否已到達可以使用 AI 的步驟（Step 5 之後）
        current_step = session.get('current_step')
        allowed_steps = [
            WorkflowStep.SELECT_DEVICE_TYPE.value,
            WorkflowStep.SELECT_DEVICE_OS.value,
            WorkflowStep.SELECT_DEVICE.value,
            WorkflowStep.LIST_PLANS.value,
            WorkflowStep.COMPARE_PLANS.value,
            WorkflowStep.CONFIRM.value
        ]
        
        if current_step not in allowed_steps:
            logger.warning(
                "目前步驟不允許使用 AI 對話",
                renewal_session_id=renewal_session_id,
                current_step=current_step
            )
            return jsonify({
                "success": False,
                "error": f"請先完成前面的步驟，才能使用 AI 對話功能"
            }), 400
        
        logger.info(
            "開始 AI 對話",
            renewal_session_id=renewal_session_id,
            staff_id=staff_id,
            message=message[:50]  # 只記錄前 50 字
        )
        
        # 建立 AI 對話管理器
        from ..services.ai_conversation_manager import AIConversationManager
        ai_manager = AIConversationManager()
        await ai_manager.initialize()
        
        # 使用生成器函數返回 SSE 串流
        async def generate_sse():
            """生成 SSE 事件串流"""
            try:
                async for event in ai_manager.chat_stream(
                    session_id=renewal_session_id,
                    user_message=message,
                    staff_id=staff_id
                ):
                    yield event
            except Exception as e:
                logger.error("SSE 串流錯誤", error=str(e), exc_info=True)
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            finally:
                await ai_manager.close()
        
        # 返回 SSE 回應
        return generate_sse(), {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
        
    except Exception as e:
        logger.error("AI 對話失敗", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500