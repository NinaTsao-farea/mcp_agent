"""
測試 Sprint 7 SSE 端點的 GET 請求支援

執行測試：
python -m pytest backend/test_sse_endpoint.py -v
"""
import pytest

def test_chat_stream_endpoint_method():
    """測試 chat/stream 端點支援 GET 方法"""
    # 檢查路由定義
    from app.routes.renewal_workflow import bp
    
    # 查找 chat/stream 路由規則
    chat_stream_rule = None
    for rule in bp.url_map.iter_rules():
        if 'chat/stream' in rule.rule:
            chat_stream_rule = rule
            break
    
    assert chat_stream_rule is not None, "找不到 chat/stream 路由"
    assert 'GET' in chat_stream_rule.methods, "chat/stream 應該支援 GET 方法"
    print(f"✅ chat/stream 支援的方法: {chat_stream_rule.methods}")

if __name__ == '__main__':
    test_chat_stream_endpoint_method()
    print("✅ 測試通過！")
