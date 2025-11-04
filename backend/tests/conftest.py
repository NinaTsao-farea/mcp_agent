"""
Pytest 設定檔
"""
import pytest
import sys
import os
from pathlib import Path

# 將 backend 目錄加入 Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 設定測試環境變數（必須在 import 之前）
os.environ['USE_REAL_ORACLE_DB'] = 'false'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'


@pytest.fixture(scope='session')
async def app():
    """建立測試應用"""
    from quart import Quart
    from app.routes import auth
    from app.services.database import DatabaseManager
    from app.services.redis_manager import RedisManager
    
    # 建立簡單的測試應用
    app = Quart(__name__)
    app.config['TESTING'] = True
    app.config['SESSION_EXPIRE_HOURS'] = 8
    
    # 初始化服務
    db_manager = DatabaseManager()
    redis_manager = RedisManager()
    
    await db_manager.initialize()
    await redis_manager.initialize()
    
    app.db_manager = db_manager
    app.redis_manager = redis_manager
    
    # 註冊路由
    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    
    yield app
    
    # 清理
    try:
        # 清理 Redis 中的測試資料
        async for key in redis_manager.redis.scan_iter("session:*"):
            await redis_manager.redis.delete(key)
        async for key in redis_manager.redis.scan_iter("staff_sessions:*"):
            await redis_manager.redis.delete(key)
    except:
        pass


@pytest.fixture
async def test_client(app):
    """測試客戶端"""
    return app.test_client()


@pytest.fixture
async def db_manager(app):
    """資料庫管理器"""
    return app.db_manager


@pytest.fixture
async def redis_manager(app):
    """Redis 管理器"""
    return app.redis_manager