"""
認證系統測試
測試登入、登出、Session 管理等功能
"""
import pytest
import asyncio
from quart import Quart
from datetime import datetime, timedelta
import bcrypt

# 測試用的模擬資料
TEST_STAFF = {
    "staff_code": "S001",
    "password": "password",
    "staff_id": "STAFF001",
    "name": "測試人員",
    "role": "Sales",
    "store_id": "STORE_A"
}


class TestAuthAPI:
    """認證 API 測試"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, test_client):
        """測試成功登入"""
        response = await test_client.post(
            '/api/auth/login',
            json={
                'staff_code': TEST_STAFF['staff_code'],
                'password': TEST_STAFF['password']
            }
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        
        assert data['success'] is True
        assert 'session_id' in data
        assert 'staff' in data
        assert data['staff']['staff_code'] == TEST_STAFF['staff_code']
        print(f"✅ 登入成功測試通過")
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, test_client):
        """測試錯誤密碼"""
        response = await test_client.post(
            '/api/auth/login',
            json={
                'staff_code': TEST_STAFF['staff_code'],
                'password': 'wrong_password'
            }
        )
        
        assert response.status_code == 401
        data = await response.get_json()
        
        assert data['success'] is False
        assert '密碼錯誤' in data['error']
        print(f"✅ 錯誤密碼測試通過")
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, test_client):
        """測試不存在的員工"""
        response = await test_client.post(
            '/api/auth/login',
            json={
                'staff_code': 'NONEXISTENT',
                'password': 'password'
            }
        )
        
        assert response.status_code == 401
        data = await response.get_json()
        
        assert data['success'] is False
        print(f"✅ 不存在員工測試通過")
    
    @pytest.mark.asyncio
    async def test_logout(self, test_client, auth_session):
        """測試登出"""
        session_id = auth_session['session_id']
        
        response = await test_client.post(
            '/api/auth/logout',
            headers={'X-Session-ID': session_id}
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        
        assert data['success'] is True
        print(f"✅ 登出測試通過")
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, test_client, auth_session):
        """測試取得當前使用者"""
        session_id = auth_session['session_id']
        
        response = await test_client.get(
            '/api/auth/me',
            headers={'X-Session-ID': session_id}
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        
        assert data['success'] is True
        assert 'staff' in data
        assert data['staff']['staff_code'] == TEST_STAFF['staff_code']
        print(f"✅ 取得當前使用者測試通過")
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_session(self, test_client):
        """測試未登入時取得當前使用者"""
        response = await test_client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = await response.get_json()
        
        assert data['success'] is False
        print(f"✅ 未登入測試通過")


class TestSessionManagement:
    """Session 管理測試"""
    
    @pytest.mark.asyncio
    async def test_session_stored_in_redis(self, redis_manager, auth_session):
        """測試 Session 儲存在 Redis"""
        session_id = auth_session['session_id']
        
        session_data = await redis_manager.get_json(f"session:{session_id}")
        
        assert session_data is not None
        assert session_data['staff_code'] == TEST_STAFF['staff_code']
        print(f"✅ Session 儲存測試通過")
    
    @pytest.mark.asyncio
    async def test_session_expiry(self, redis_manager, test_client):
        """測試 Session 過期"""
        # 創建一個已過期的 Session
        expired_session_id = "session_expired_test"
        expired_session_data = {
            "session_id": expired_session_id,
            "staff_id": TEST_STAFF['staff_id'],
            "staff_code": TEST_STAFF['staff_code'],
            "name": TEST_STAFF['name'],
            "role": TEST_STAFF['role'],
            "store_id": TEST_STAFF['store_id'],
            "login_time": (datetime.now() - timedelta(hours=9)).isoformat(),
            "expire_time": (datetime.now() - timedelta(hours=1)).isoformat()
        }
        
        await redis_manager.set_json(
            f"session:{expired_session_id}", 
            expired_session_data, 
            ex=3600
        )
        
        # 嘗試使用過期的 Session
        response = await test_client.get(
            '/api/auth/me',
            headers={'X-Session-ID': expired_session_id}
        )
        
        assert response.status_code == 401
        print(f"✅ Session 過期測試通過")
    
    @pytest.mark.asyncio
    async def test_session_cleanup_on_logout(self, redis_manager, test_client, auth_session):
        """測試登出後 Session 清除"""
        session_id = auth_session['session_id']
        staff_id = auth_session['staff_id']
        
        # 登出
        await test_client.post(
            '/api/auth/logout',
            headers={'X-Session-ID': session_id}
        )
        
        # 檢查 Redis 中的 Session 是否被清除
        session_data = await redis_manager.get_json(f"session:{session_id}")
        staff_sessions = await redis_manager.get(f"staff_sessions:{staff_id}")
        
        assert session_data is None
        assert staff_sessions is None
        print(f"✅ Session 清除測試通過")


class TestAuthMiddleware:
    """認證中介軟體測試"""
    
    @pytest.mark.asyncio
    async def test_protected_route_without_auth(self, test_client):
        """測試未認證訪問受保護路由"""
        # 這裡應該有一個需要認證的路由
        # 暫時使用 /api/auth/me 作為範例
        response = await test_client.get('/api/auth/me')
        
        assert response.status_code == 401
        print(f"✅ 受保護路由測試通過")
    
    @pytest.mark.asyncio
    async def test_protected_route_with_auth(self, test_client, auth_session):
        """測試已認證訪問受保護路由"""
        session_id = auth_session['session_id']
        
        response = await test_client.get(
            '/api/auth/me',
            headers={'X-Session-ID': session_id}
        )
        
        assert response.status_code == 200
        print(f"✅ 已認證訪問測試通過")


class TestPasswordSecurity:
    """密碼安全測試"""
    
    def test_password_hashing(self):
        """測試密碼雜湊"""
        password = "test_password"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        assert bcrypt.checkpw(password.encode('utf-8'), hashed)
        assert not bcrypt.checkpw("wrong_password".encode('utf-8'), hashed)
        print(f"✅ 密碼雜湊測試通過")
    
    @pytest.mark.asyncio
    async def test_change_password(self, test_client, auth_session):
        """測試變更密碼"""
        session_id = auth_session['session_id']
        
        response = await test_client.post(
            '/api/auth/change-password',
            headers={'X-Session-ID': session_id},
            json={
                'old_password': TEST_STAFF['password'],
                'new_password': 'new_password123'
            }
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        
        assert data['success'] is True
        print(f"✅ 變更密碼測試通過")


# Pytest Fixtures
@pytest.fixture
async def test_client(app):
    """測試客戶端"""
    return app.test_client()


@pytest.fixture
async def redis_manager(app):
    """Redis 管理器"""
    return app.redis_manager


@pytest.fixture
async def auth_session(test_client):
    """認證 Session fixture"""
    response = await test_client.post(
        '/api/auth/login',
        json={
            'staff_code': TEST_STAFF['staff_code'],
            'password': TEST_STAFF['password']
        }
    )
    
    data = await response.get_json()
    return {
        'session_id': data['session_id'],
        'staff_id': data['staff']['staff_id'],
        'staff_code': data['staff']['staff_code']
    }


if __name__ == "__main__":
    print("=" * 60)
    print("認證系統測試")
    print("=" * 60)
    print("\n請使用 pytest 執行測試：")
    print("  pytest backend/tests/test_auth.py -v")
    print("=" * 60)