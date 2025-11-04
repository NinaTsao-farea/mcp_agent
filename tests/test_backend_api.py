"""
簡單的後端 API 測試
"""
import requests
import json

def test_login():
    """測試登入 API"""
    url = "http://localhost:8000/api/auth/login"
    data = {
        "staff_code": "S001",
        "password": "password"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"登入測試 - 狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"Session ID: {session_id}")
            return session_id
        return None
    except Exception as e:
        print(f"登入測試失敗: {e}")
        return None


def test_start_workflow(session_id):
    """測試開始續約流程 API"""
    if not session_id:
        print("沒有 Session ID，跳過續約流程測試")
        return False
    
    url = "http://localhost:8000/api/renewal-workflow/start"
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": session_id
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=5)
        print(f"續約流程測試 - 狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"續約流程測試失敗: {e}")
        return False

def test_health():
    """測試健康檢查"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"健康檢查 - 狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康檢查失敗: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("後端 API 測試")
    print("=" * 50)
    
    print("\n[1] 測試健康檢查...")
    health_ok = test_health()
    
    print("\n[2] 測試登入 API...")
    session_id = test_login()
    login_ok = session_id is not None
    
    print("\n[3] 測試續約流程 API...")
    workflow_ok = test_start_workflow(session_id)
    
    print("\n" + "=" * 50)
    print("測試結果:")
    print(f"健康檢查: {'✅ 成功' if health_ok else '❌ 失敗'}")
    print(f"登入 API: {'✅ 成功' if login_ok else '❌ 失敗'}")
    print(f"續約流程 API: {'✅ 成功' if workflow_ok else '❌ 失敗'}")
    
    if health_ok and login_ok and workflow_ok:
        print("\n🎉 所有測試通過！後端 API 正常運作。")
    else:
        print("\n⚠️ 部分測試失敗，請檢查後端服務。")