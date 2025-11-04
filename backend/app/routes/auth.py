"""
認證路由 - 處理登入/登出
"""
from turtle import st
from quart import Blueprint, request, jsonify, current_app
import bcrypt
import secrets
import structlog
from datetime import datetime, timedelta

from app.services.database import DatabaseManager
from app.services.redis_manager import RedisManager
from app.utils.exceptions import AuthenticationError, ValidationError

logger = structlog.get_logger()
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
async def login():
    """員工登入"""
    try:
        data = await request.get_json()
        
        # 驗證輸入
        staff_code = data.get('staff_code', '').strip()
        password = data.get('password', '').strip()
        
        if not staff_code or not password:
            raise ValidationError("請輸入員工編號和密碼")
        
        logger.info("員工登入嘗試", staff_code=staff_code)
        
        # 查詢員工資料
        db_manager: DatabaseManager = current_app.db_manager
        
        staff_query = """
        SELECT staff_id, staff_code, name, role, store_id, password_hash, is_active
        FROM staff 
        WHERE staff_code = :staff_code AND is_active = 1
        """
        
        staff_records = await db_manager.execute_query(
            staff_query, 
            {"staff_code": staff_code}
        )
        
        if not staff_records:
            raise AuthenticationError("員工編號或密碼錯誤")
        
        staff = staff_records[0]
        print(f'員工資料: {staff}')
        
        # 驗證密碼 (使用 bcrypt)
        password_bytes = password.encode('utf-8')
        password_hash_str = staff['PASSWORD_HASH']
        # password_hash_str = "$2b$12$84YkEe0ZZucUbksZuKSLOOr9icTU6ZEZbJlBVD0mB0DUI.YbPn6Li"
        password_hash_bytes = password_hash_str.encode('utf-8')
        
        print(f'輸入密碼: {password}')
        print(f'資料庫密碼雜湊: {password_hash_str[:50]}...')
        
        if not bcrypt.checkpw(password_bytes, password_hash_bytes):
            raise AuthenticationError("員工編號或密碼錯誤")
        
        # 生成 Session ID
        session_id = f"session_{staff['STAFF_CODE']}_{secrets.token_hex(16)}"
        
        # 建立 Session 資料
        session_data = {
            "session_id": session_id,
            "staff_id": staff['STAFF_ID'],
            "staff_code": staff['STAFF_CODE'],
            "name": staff['NAME'],
            "role": staff['ROLE'],
            "store_id": staff['STORE_ID'],
            "login_time": datetime.now().isoformat(),
            "expire_time": (datetime.now() + timedelta(hours=current_app.config['SESSION_EXPIRE_HOURS'])).isoformat()
        }
        
        # 儲存到 Redis
        redis_manager: RedisManager = current_app.redis_manager
        expire_seconds = current_app.config['SESSION_EXPIRE_HOURS'] * 3600
        
        await redis_manager.set_json(f"session:{session_id}", session_data, ex=expire_seconds)
        await redis_manager.set(f"staff_sessions:{staff['STAFF_ID']}", session_id, ex=expire_seconds)
        
        # 記錄登入日誌
        # INSERT INTO SYS_LOG (staff_id, login_time, ip_address, user_agent)
        login_log_query = """
        INSERT INTO SYS_LOG (account, store_code, employee_code, employee_ip, login_session, login_start_daytime)
        VALUES ('NSP', :store_id, :staff_id, :ip_address, '', :login_time)
        """
        
        await db_manager.execute_non_query(login_log_query, {
            "store_id": staff['STORE_ID'],
            "staff_id": staff['STAFF_ID'],
            "ip_address": request.headers.get('X-Forwarded-For', request.remote_addr),
            "login_time": datetime.now(),
            #"user_agent": request.headers.get('User-Agent', '')
        })
        
        logger.info("員工登入成功", staff_code=staff_code, session_id=session_id)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "staff": {
                "staff_id": staff['STAFF_ID'],
                "staff_code": staff['STAFF_CODE'],
                "name": staff['NAME'],
                "role": staff['ROLE'],
                "store_id": staff['STORE_ID']
            },
            "expires_at": session_data['expire_time']
        })
        
    except (AuthenticationError, ValidationError) as e:
        return jsonify({"success": False, "error": str(e)}), e.status_code
    except Exception as e:
        logger.error("登入過程發生錯誤", error=str(e))
        return jsonify({"success": False, "error": "系統錯誤"}), 500

@bp.route('/logout', methods=['POST'])
async def logout():
    """員工登出"""
    try:
        # 取得 Session ID
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        
        if not session_id:
            return jsonify({"success": True, "message": "已登出"})
        
        # 從 Redis 刪除 Session
        redis_manager: RedisManager = current_app.redis_manager
        
        # 取得 Session 資料以獲取 staff_id
        session_data = await redis_manager.get_json(f"session:{session_id}")
        
        if session_data:
            # 刪除相關的 Redis 資料
            await redis_manager.delete(f"session:{session_id}")
            await redis_manager.delete(f"staff_sessions:{session_data['staff_id']}")
            
            logger.info("員工登出成功", staff_code=session_data.get('staff_code'), session_id=session_id)
        
        return jsonify({"success": True, "message": "登出成功"})
        
    except Exception as e:
        logger.error("登出過程發生錯誤", error=str(e))
        return jsonify({"success": False, "error": "系統錯誤"}), 500

@bp.route('/me', methods=['GET'])
async def get_current_user():
    """取得當前使用者資訊"""
    try:
        # 取得 Session ID
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        
        if not session_id:
            raise AuthenticationError("請先登入")
        
        # 從 Redis 取得 Session 資料
        redis_manager: RedisManager = current_app.redis_manager
        session_data = await redis_manager.get_json(f"session:{session_id}")
        
        if not session_data:
            raise AuthenticationError("Session 已過期，請重新登入")
        
        # 檢查 Session 是否過期
        from datetime import datetime
        expire_time = datetime.fromisoformat(session_data['expire_time'])
        if datetime.now() > expire_time:
            # Session 已過期，清除 Redis 資料
            await redis_manager.delete(f"session:{session_id}")
            await redis_manager.delete(f"staff_sessions:{session_data['staff_id']}")
            raise AuthenticationError("Session 已過期，請重新登入")
        
        # 返回員工資訊
        staff_info = {
            "staff_id": session_data['staff_id'],
            "staff_code": session_data['staff_code'],
            "name": session_data['name'],
            "role": session_data['role'],
            "store_id": session_data['store_id']
        }
        
        return jsonify({
            "success": True,
            "staff": staff_info
        })
            
    except AuthenticationError as e:
        return jsonify({"success": False, "error": str(e)}), 401
    except Exception as e:
        logger.error("取得使用者資訊錯誤", error=str(e))
        return jsonify({"success": False, "error": "系統錯誤"}), 500

@bp.route('/change-password', methods=['POST'])
async def change_password():
    """變更密碼"""
    try:
        if not hasattr(request, 'user') or not request.user:
            raise AuthenticationError("請先登入")
        
        data = await request.get_json()
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not old_password or not new_password:
            raise ValidationError("請輸入舊密碼和新密碼")
        
        if len(new_password) < 6:
            raise ValidationError("新密碼長度至少6個字元")
        
        # 驗證舊密碼
        db_manager: DatabaseManager = current_app.db_manager
        
        staff_query = """
        SELECT password_hash FROM staff 
        WHERE staff_id = :staff_id
        """
        
        staff_records = await db_manager.execute_query(
            staff_query, 
            {"staff_id": request.user['staff_id']}
        )
        
        if not staff_records:
            raise AuthenticationError("找不到使用者")
        
        if not bcrypt.checkpw(old_password.encode('utf-8'), staff_records[0]['password_hash'].encode('utf-8')):
            raise AuthenticationError("舊密碼錯誤")
        
        # 產生新密碼雜湊
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 更新密碼
        update_query = """
        UPDATE staff 
        SET password_hash = :password_hash, updated_at = :updated_at
        WHERE staff_id = :staff_id
        """
        
        await db_manager.execute_non_query(update_query, {
            "password_hash": new_password_hash,
            "updated_at": datetime.now(),
            "staff_id": request.user['staff_id']
        })
        
        logger.info("密碼變更成功", staff_id=request.user['staff_id'])
        
        return jsonify({"success": True, "message": "密碼變更成功"})
        
    except (AuthenticationError, ValidationError) as e:
        return jsonify({"success": False, "error": str(e)}), e.status_code
    except Exception as e:
        logger.error("變更密碼錯誤", error=str(e))
        return jsonify({"success": False, "error": "系統錯誤"}), 500