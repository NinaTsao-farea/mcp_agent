"""
認證中介軟體 - 驗證 Session 並設置使用者資訊
"""
from quart import request, current_app, g
from functools import wraps
import structlog
from datetime import datetime

from app.utils.exceptions import AuthenticationError
from app.services.redis_manager import RedisManager

logger = structlog.get_logger()

async def authenticate_session():
    """驗證 Session 並設置使用者資訊到 request.user"""
    try:
        # 取得 Session ID
        session_id = (
            request.headers.get('X-Session-ID') or 
            request.cookies.get('session_id') or
            request.args.get('session_id')
        )
        
        logger.debug("認證檢查", 
                    path=request.path,
                    has_header=bool(request.headers.get('X-Session-ID')),
                    session_id=session_id[:20] + '...' if session_id and len(session_id) > 20 else session_id)
        
        if not session_id:
            logger.debug("無 Session ID")
            request.user = None
            return
        
        # 從 Redis 取得 Session 資料
        redis_manager: RedisManager = current_app.redis_manager
        session_data = await redis_manager.get_json(f"session:{session_id}")
        
        if not session_data:
            request.user = None
            return
        
        # 檢查 Session 是否過期
        expire_time = datetime.fromisoformat(session_data['expire_time'])
        if datetime.now() > expire_time:
            # Session 過期，清除
            await redis_manager.delete(f"session:{session_id}")
            await redis_manager.delete(f"staff_sessions:{session_data['staff_id']}")
            request.user = None
            return
        
        # 設置使用者資訊
        request.user = {
            "session_id": session_data["session_id"],
            "staff_id": session_data["staff_id"],
            "staff_code": session_data["staff_code"],
            "name": session_data["name"],
            "role": session_data["role"],
            "store_id": session_data["store_id"],
            "login_time": session_data["login_time"]
        }
        
        logger.debug("Session 驗證成功", staff_code=session_data["staff_code"])
        
    except Exception as e:
        logger.error("Session 驗證錯誤", error=str(e))
        request.user = None

def require_auth(f):
    """裝飾器：要求認證"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            raise AuthenticationError("請先登入")
        return await f(*args, **kwargs)
    return decorated_function

def require_role(required_roles):
    """裝飾器：要求特定角色"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                raise AuthenticationError("請先登入")
            
            user_role = request.user.get('role')
            if user_role not in required_roles:
                raise AuthenticationError("權限不足")
            
            return await f(*args, **kwargs)
        return decorated_function
    return decorator

def require_store_access(f):
    """裝飾器：要求門市存取權限（只能存取自己門市的資料）"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            raise AuthenticationError("請先登入")
        
        # 管理員可以存取所有門市
        if request.user.get('role') == 'Manager':
            return await f(*args, **kwargs)
        
        # 其他角色只能存取自己的門市
        # 這個邏輯可以在具體的路由中進一步檢查
        return await f(*args, **kwargs)
    return decorated_function