"""
簡單的後端測試 - 使用內建模組
"""
import urllib.request
import urllib.parse
import json

def test_health():
    """測試健康檢查"""
    try:
        with urllib.request.urlopen('http://localhost:8000/health') as response:
            data = response.read().decode('utf-8')
            print(f"健康檢查 - 狀態碼: {response.status}")
            print(f"回應: {data}")
            return response.status == 200
    except Exception as e:
        print(f"健康檢查失敗: {e}")
        return False

def test_login():
    """測試登入"""
    try:
        data = {
            "staff_code": "S001",
            "password": "password"
        }
        
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:8000/api/auth/login',
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            print(f"登入測試 - 狀態碼: {response.status}")
            print(f"回應: {response_data}")
            return response.status == 200
            
    except urllib.error.HTTPError as e:
        response_data = e.read().decode('utf-8')
        print(f"登入測試 - 狀態碼: {e.code}")
        print(f"錯誤回應: {response_data}")
        return False
    except Exception as e:
        print(f"登入測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("後端測試")
    print("=" * 50)
    
    print("\n[1] 測試健康檢查...")
    health_ok = test_health()
    
    print("\n[2] 測試登入...")
    login_ok = test_login()
    
    print("\n" + "=" * 50)
    print(f"健康檢查: {'✅' if health_ok else '❌'}")
    print(f"登入測試: {'✅' if login_ok else '❌'}")