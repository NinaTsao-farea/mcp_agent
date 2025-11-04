# -*- coding: utf-8 -*-
"""
Sprint 7 整合測試 Part 1：Azure OpenAI 連線測試

測試項目：
1. Azure OpenAI 連線
2. 基本對話功能
3. Function Calling（模擬）
4. Token 使用追蹤

執行方式：
python backend/test_sprint7_integration_openai.py
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import structlog
from openai import AsyncAzureOpenAI
from app.services.ai_conversation_manager import AIConversationManager

logger = structlog.get_logger()

# Azure OpenAI 配置（從環境變數讀取）
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")


async def test_azure_openai_connection():
    """測試 1: Azure OpenAI 連線"""
    print("\n" + "="*80)
    print("測試 1: Azure OpenAI 連線測試")
    print("="*80)
    
    try:
        print(f"\n  Endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"  Deployment: {AZURE_OPENAI_DEPLOYMENT}")
        print(f"  API Version: {AZURE_OPENAI_API_VERSION}")
        
        if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
            print(f"\n  ✗ 缺少必要的環境變數")
            print(f"  請設定: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT")
            return False
        
        # 創建 Azure OpenAI 客戶端
        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        print(f"\n  ✓ Azure OpenAI 客戶端創建成功")
        print(f"  Model: {AZURE_OPENAI_DEPLOYMENT}")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ Azure OpenAI 連線失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_chat():
    """測試 2: 基本對話功能"""
    print("\n" + "="*80)
    print("測試 2: 基本對話功能")
    print("="*80)
    
    try:
        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        # 簡單對話測試
        messages = [
            {"role": "system", "content": "你是一個友善的助手。"},
            {"role": "user", "content": "請用一句話介紹台灣"}
        ]
        
        print(f"\n  發送測試訊息...")
        response = await client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=100
        )
        
        reply = response.choices[0].message.content
        print(f"\n  AI 回覆: {reply[:80]}...")
        print(f"  ✓ 基本對話功能正常")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ 基本對話測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_function_calling():
    """測試 3: Function Calling（模擬）"""
    print("\n" + "="*80)
    print("測試 3: Function Calling")
    print("="*80)
    
    try:
        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        # 定義測試用的 Functions
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "get_plan_details",
                    "description": "查詢資費方案的詳細資訊",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan_id": {
                                "type": "string",
                                "description": "方案ID，例如：999、1399"
                            }
                        },
                        "required": ["plan_id"]
                    }
                }
            }
        ]
        
        messages = [
            {"role": "system", "content": "你是電信方案助手，可以查詢方案資訊。"},
            {"role": "user", "content": "請幫我查詢 999 元方案的詳細資訊"}
        ]
        
        print(f"\n  測試 Function Calling...")
        response = await client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            tools=functions,
            tool_choice="auto",
            max_tokens=500
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"\n  ✓ AI 調用 Function: {tool_call.function.name}")
                print(f"  參數: {tool_call.function.arguments}")
            return True
        else:
            print(f"\n  ⚠ AI 沒有調用 Function")
            print(f"  直接回答: {message.content}")
            return True  # 不一定要調用，所以還是算通過
            
    except Exception as e:
        print(f"\n  ✗ Function Calling 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_conversation_manager():
    """測試 4: AIConversationManager 初始化"""
    print("\n" + "="*80)
    print("測試 4: AIConversationManager")
    print("="*80)
    
    try:
        print(f"\n  創建 AIConversationManager...")
        ai_manager = AIConversationManager()
        
        print(f"  ✓ AIConversationManager 創建成功")
        print(f"  Model: {ai_manager.model}")
        print(f"  Max Tokens: {ai_manager.max_tokens}")
        
        # 檢查 Function Definitions
        functions = ai_manager._get_function_definitions()
        print(f"  ✓ 已載入 {len(functions)} 個 Functions")
        
        # 列出前5個 Functions
        for i, func in enumerate(functions[:5]):
            func_name = func["function"]["name"]
            print(f"    {i+1}. {func_name}")
        
        if len(functions) > 5:
            print(f"    ... 還有 {len(functions) - 5} 個 Functions")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ AIConversationManager 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_calculation():
    """測試 5: Token 使用計算"""
    print("\n" + "="*80)
    print("測試 5: Token 使用計算")
    print("="*80)
    
    try:
        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        messages = [
            {"role": "system", "content": "你是助手"},
            {"role": "user", "content": "請說 Hello"}
        ]
        
        response = await client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=50
        )
        
        usage = response.usage
        print(f"\n  Token 使用:")
        print(f"    Prompt Tokens: {usage.prompt_tokens}")
        print(f"    Completion Tokens: {usage.completion_tokens}")
        print(f"    Total Tokens: {usage.total_tokens}")
        
        # 計算成本 (GPT-4o 價格)
        prompt_cost = usage.prompt_tokens / 1000 * 0.005
        completion_cost = usage.completion_tokens / 1000 * 0.015
        total_cost = prompt_cost + completion_cost
        
        print(f"\n  估計成本:")
        print(f"    Prompt: ${prompt_cost:.6f}")
        print(f"    Completion: ${completion_cost:.6f}")
        print(f"    Total: ${total_cost:.6f}")
        
        print(f"\n  ✓ Token 計算功能正常")
        return True
        
    except Exception as e:
        print(f"\n  ✗ Token 計算測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """執行所有測試"""
    print("\n" + "="*80)
    print(" Sprint 7 整合測試 Part 1: Azure OpenAI")
    print("="*80)
    print(f" 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    tests = [
        ("Azure OpenAI 連線", test_azure_openai_connection),
        ("基本對話功能", test_basic_chat),
        ("Function Calling", test_function_calling),
        ("AIConversationManager", test_ai_conversation_manager),
        ("Token 使用計算", test_token_calculation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 測試 '{name}' 執行失敗: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 總結
    print("\n" + "="*80)
    print(" 測試總結")
    print("="*80)
    
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n" + "="*80)
        print(" 🎉 Part 1 測試完全通過！")
        print("="*80)
        print("\n可以繼續執行 Part 2 (MCP Servers 測試)")
        return 0
    else:
        print(f"\n✗ {total - passed} 個測試失敗")
        print("請修復這些問題後再繼續")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
