"""
AI Conversation Manager - Sprint 7

管理 AI 對話流程，包含：
- 對話歷史管理
- Function Calling 協調
- Token 使用追蹤
- SSE 串流輸出
"""
from typing import AsyncGenerator, Dict, List, Any, Optional
import json
import os
import structlog
from datetime import datetime
from openai import AsyncAzureOpenAI

from .mcp_client_http import MCPClientServiceHTTP
from .mcp_client_pos_http import MCPClientServicePOSHTTP
from .mcp_client_promotion_http import MCPClientServicePromotionHTTP
from .redis_manager import RedisManager

logger = structlog.get_logger()


# Azure OpenAI GPT-4o 定價 (每 1K tokens)
PRICING = {
    "gpt-4o": {
        "prompt": 0.005,      # $0.005 per 1K tokens
        "completion": 0.015    # $0.015 per 1K tokens
    }
}


class AIConversationManager:
    """
    AI 對話管理器
    
    負責：
    1. 管理對話歷史
    2. 協調 Function Calling
    3. 串流輸出 AI 回答
    4. 追蹤 Token 使用
    """
    
    def __init__(self):
        """初始化 AI 對話管理器"""
        # Azure OpenAI Client
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # MCP Clients
        self.crm_client = MCPClientServiceHTTP()
        self.pos_client = MCPClientServicePOSHTTP()
        self.promotion_client = MCPClientServicePromotionHTTP()
        
        # Redis Manager
        self.redis_manager = RedisManager()
        
        # 配置
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.max_iterations = int(os.getenv("AI_MAX_FUNCTION_ITERATIONS", "5"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))
        
        logger.info("AI Conversation Manager 初始化", model=self.model)
    
    async def initialize(self):
        """初始化所有 MCP Clients"""
        logger.info("初始化 MCP Clients")
        await self.crm_client.initialize()
        await self.pos_client.initialize()
        await self.promotion_client.initialize()
        await self.redis_manager.initialize()
        logger.info("所有 MCP Clients 初始化完成")
    
    async def close(self):
        """關閉所有連線"""
        logger.info("關閉 AI Conversation Manager")
        await self.crm_client.close()
        await self.pos_client.close()
        await self.promotion_client.close()
        await self.redis_manager.close()
    
    def _get_system_prompt(self, session_data: Dict[str, Any]) -> str:
        """
        根據 Session 資料生成系統提示詞
        
        Args:
            session_data: 續約 Session 資料
            
        Returns:
            系統提示詞
        """
        customer = session_data.get("customer", {})
        phone = session_data.get("phone", {})
        contract = session_data.get("contract", {})
        selected_device = session_data.get("selected_device", {})
        selected_plan = session_data.get("selected_plan", {})
        
        prompt = f"""你是一個專業的電信門市銷售助理 AI。你的任務是協助門市人員回答客戶的問題，提供方案建議。

當前續約流程上下文：
"""
        
        if customer:
            prompt += f"""
客戶資訊：
- 姓名：{customer.get('name', '未知')}
- 身分證：{customer.get('id_number', '未知')}
- 聯絡電話：{customer.get('phone', '未知')}
"""
        
        if phone:
            prompt += f"""
門號資訊：
- 門號：{phone.get('phone_number', '未知')}
- 狀態：{phone.get('status', '未知')}
"""
        
        if contract:
            prompt += f"""
合約資訊：
- 目前方案：{contract.get('plan_name', '未知')}
- 月租費：{contract.get('monthly_fee', '未知')} 元
- 合約到期日：{contract.get('contract_end', '未知')}
"""
        
        if selected_device:
            prompt += f"""
已選擇的手機：
- 品牌：{selected_device.get('brand', '未知')}
- 型號：{selected_device.get('model', '未知')}
- 顏色：{selected_device.get('color', '未知')}
- 價格：{selected_device.get('price', '未知')} 元
"""
        
        if selected_plan:
            prompt += f"""
已選擇的方案：
- 方案名稱：{selected_plan.get('plan_name', '未知')}
- 月租費：{selected_plan.get('monthly_fee', '未知')} 元
- 合約期：{selected_plan.get('contract_months', '未知')} 個月
"""
        
        prompt += """
你可以使用以下工具來回答問題：
- compare_plans: 比較方案差異
- get_phone_details: 查詢門號詳情
- search_promotions: 搜尋促銷方案
- calculate_upgrade_cost: 計算升級費用
- 以及其他客戶、庫存、促銷相關的工具

請用專業、友善的語氣回答，提供清晰、有用的資訊。如果需要使用工具，請直接調用。
"""
        
        return prompt
    
    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        取得所有可用的 Function 定義
        
        Returns:
            Function 定義列表
        """
        return [
            # CRM Tools
            {
                "type": "function",
                "function": {
                    "name": "get_customer",
                    "description": "根據身分證號查詢客戶基本資料，包含姓名、聯絡方式、地址等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id_number": {
                                "type": "string",
                                "description": "客戶身分證號"
                            }
                        },
                        "required": ["id_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_customer_phones",
                    "description": "查詢客戶所有門號列表，包含合約狀況、月租費等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "客戶編號"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_phone_details",
                    "description": "查詢門號的詳細資訊，包含合約、使用量、帳單等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            }
                        },
                        "required": ["phone_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_renewal_eligibility",
                    "description": "檢查門號是否符合續約資格，包含合約到期日、欠費狀況等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            },
                            "renewal_type": {
                                "type": "string",
                                "enum": ["single", "with_device"],
                                "description": "續約類型：single(單純續約) 或 with_device(搭配手機)"
                            }
                        },
                        "required": ["phone_number", "renewal_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_promotion_eligibility",
                    "description": "檢查門號是否符合特定促銷資格，包含在網時間、月消費等條件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "門號"
                            },
                            "promotion_id": {
                                "type": "string",
                                "description": "促銷編號"
                            }
                        },
                        "required": ["phone_number", "promotion_id"]
                    }
                }
            },
            
            # POS Tools
            {
                "type": "function",
                "function": {
                    "name": "query_device_stock",
                    "description": "查詢門市設備庫存，可依品牌、型號篩選",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "store_id": {
                                "type": "string",
                                "description": "門市編號"
                            },
                            "device_model": {
                                "type": "string",
                                "description": "設備型號（可選）"
                            },
                            "brand": {
                                "type": "string",
                                "description": "品牌（可選）"
                            }
                        },
                        "required": ["store_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_info",
                    "description": "查詢設備詳細資訊，包含規格、價格、顏色等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "設備編號"
                            }
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommended_devices",
                    "description": "根據客戶需求推薦適合的設備",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "os_type": {
                                "type": "string",
                                "enum": ["android", "ios"],
                                "description": "作業系統類型"
                            },
                            "price_range": {
                                "type": "object",
                                "properties": {
                                    "min": {"type": "number"},
                                    "max": {"type": "number"}
                                },
                                "description": "價格範圍（可選）"
                            }
                        },
                        "required": ["os_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_pricing",
                    "description": "查詢設備在不同合約期數下的價格",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "設備編號"
                            },
                            "contract_period": {
                                "type": "number",
                                "enum": [24, 30, 36],
                                "description": "合約期數（月）"
                            }
                        },
                        "required": ["device_id", "contract_period"]
                    }
                }
            },
            
            # Promotion Tools
            {
                "type": "function",
                "function": {
                    "name": "search_promotions",
                    "description": "使用 RAG 搜尋相關促銷方案，基於客戶需求和使用習慣",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜尋查詢，例如：5G吃到飽、學生方案等"
                            },
                            "top_k": {
                                "type": "number",
                                "description": "返回結果數量，預設 5"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_plan_details",
                    "description": "取得方案完整資訊，包含費用、流量、通話、合約期等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan_id": {
                                "type": "string",
                                "description": "方案編號"
                            }
                        },
                        "required": ["plan_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_plans",
                    "description": "比較多個方案的差異，生成比較表格和推薦建議",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "要比較的方案 ID 列表"
                            }
                        },
                        "required": ["plan_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_upgrade_cost",
                    "description": "計算從目前方案升級到新方案的費用，包含違約金、差額等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "current_plan_id": {
                                "type": "string",
                                "description": "目前方案編號"
                            },
                            "new_plan_id": {
                                "type": "string",
                                "description": "新方案編號"
                            },
                            "remaining_contract_months": {
                                "type": "number",
                                "description": "剩餘合約月數"
                            }
                        },
                        "required": ["current_plan_id", "new_plan_id", "remaining_contract_months"]
                    }
                }
            }
        ]
    
    async def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        調用 MCP Function
        
        Args:
            function_name: Function 名稱
            arguments: Function 參數
            
        Returns:
            Function 執行結果
        """
        logger.info("調用 Function", function=function_name, arguments=arguments)
        
        try:
            # CRM Tools
            if function_name == "get_customer":
                # Function: get_customer -> Client method: query_customer_by_id
                result = await self.crm_client.query_customer_by_id(arguments.get("id_number"))
                return result if result else {"error": "客戶不存在"}
                
            elif function_name == "list_customer_phones":
                # Function: list_customer_phones -> Client method: get_customer_phones
                result = await self.crm_client.get_customer_phones(arguments.get("customer_id"))
                return {"phones": result} if result else {"phones": []}
                
            elif function_name == "get_phone_details":
                # Function: get_phone_details -> Client method: get_phone_contract
                result = await self.crm_client.get_phone_contract(arguments.get("phone_number"))
                return result if result else {"error": "門號不存在"}
                
            elif function_name == "check_renewal_eligibility":
                # 透過 _call_tool 直接調用 MCP Server
                result = await self.crm_client._call_tool("check_renewal_eligibility", arguments)
                if result.get("success"):
                    return result.get("data", {})
                else:
                    return {"error": result.get("error", {}).get("message", "檢查失敗")}
                    
            elif function_name == "check_promotion_eligibility":
                # 透過 _call_tool 直接調用 MCP Server
                result = await self.crm_client._call_tool("check_promotion_eligibility", arguments)
                if result.get("success"):
                    return result.get("data", {})
                else:
                    return {"error": result.get("error", {}).get("message", "檢查失敗")}
            
            # POS Tools
            elif function_name == "query_device_stock":
                # 參數映射：AI 可能傳 device_model/brand，但實際方法只支援 store_id, os_filter, min_price, max_price
                # 簡化：只傳 store_id，忽略其他參數（實際應該做更智能的映射）
                store_id = arguments.get("store_id", "STORE001")  # 預設門市
                # 如果 store_id 只是數字，補上 STORE 前綴
                if store_id and store_id.isdigit():
                    store_id = f"STORE{store_id.zfill(3)}"  # 例如: "1" -> "STORE001"
                result = await self.pos_client.query_device_stock(store_id=store_id)
                return result if result else {"error": "查詢失敗"}
                
            elif function_name == "get_device_info":
                result = await self.pos_client.get_device_info(arguments.get("device_id"))
                return result if result else {"error": "設備不存在"}
                
            elif function_name == "get_recommended_devices":
                result = await self.pos_client.get_recommended_devices(**arguments)
                return {"devices": result} if result else {"devices": []}
                
            elif function_name == "get_device_pricing":
                result = await self.pos_client.get_device_pricing(**arguments)
                return result if result else {"error": "查詢失敗"}
            
            # Promotion Tools
            elif function_name == "search_promotions":
                # 參數映射：top_k -> limit
                query = arguments.get("query", "")
                contract_type = arguments.get("contract_type")
                limit = arguments.get("top_k", arguments.get("limit", 5))  # top_k 或 limit
                result = await self.promotion_client.search_promotions(
                    query=query,
                    contract_type=contract_type,
                    limit=limit
                )
                return result if result else {"promotions": []}
                
            elif function_name == "get_plan_details":
                result = await self.promotion_client.get_plan_details(arguments.get("plan_id"))
                return result if result else {"error": "方案不存在"}
                
            elif function_name == "compare_plans":
                result = await self.promotion_client.compare_plans(**arguments)
                return result if result else {"error": "比較失敗"}
                
            elif function_name == "calculate_upgrade_cost":
                result = await self.promotion_client.calculate_upgrade_cost(**arguments)
                return result if result else {"error": "計算失敗"}
            
            else:
                error_msg = f"未知的 Function: {function_name}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Function 調用失敗: {str(e)}"
            logger.error(error_msg, function=function_name, error=str(e))
            return {"error": error_msg}
    
    async def chat_stream(
        self,
        session_id: str,
        user_message: str,
        staff_id: str
    ) -> AsyncGenerator[str, None]:
        """
        AI 對話串流
        
        Args:
            session_id: 續約 Session ID
            user_message: 使用者訊息
            staff_id: 門市人員 ID
            
        Yields:
            SSE 格式的事件字串
        """
        logger.info("開始 AI 對話", session_id=session_id, staff_id=staff_id)
        
        # 取得 Session 資料
        # 注意：session_id 是 renewal_session_id，需要用 renewal_session: 前綴
        session_key = f"renewal_session:{session_id}"
        session_data = await self.redis_manager.get_json(session_key)
        
        if not session_data:
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': 'Session 不存在'})}\n\n"
            return
        
        # 建立對話歷史
        messages = [
            {"role": "system", "content": self._get_system_prompt(session_data)},
            {"role": "user", "content": user_message}
        ]
        
        # Function Calling 迭代
        total_prompt_tokens = 0
        total_completion_tokens = 0
        iteration = 0
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                logger.debug(f"Function Calling 迭代 {iteration}")
                
                # 調用 OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self._get_function_definitions(),
                    tool_choice="auto",
                    max_tokens=self.max_tokens,
                    stream=True
                )
                
                # 收集串流回應
                collected_messages = []
                tool_calls = []
                current_tool_call = None
                
                async for chunk in response:
                    if not chunk.choices:
                        continue
                    
                    delta = chunk.choices[0].delta
                    
                    # 處理文字內容
                    if delta.content:
                        collected_messages.append(delta.content)
                        # 串流輸出
                        yield f"event: message\ndata: {json.dumps({'type': 'message', 'content': delta.content})}\n\n"
                    
                    # 處理 Tool Calls
                    if delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if tool_call.index is not None:
                                # 新的 tool call
                                if current_tool_call and current_tool_call["index"] != tool_call.index:
                                    tool_calls.append(current_tool_call)
                                
                                if tool_call.index >= len(tool_calls):
                                    current_tool_call = {
                                        "index": tool_call.index,
                                        "id": tool_call.id or "",
                                        "type": "function",
                                        "function": {
                                            "name": tool_call.function.name or "",
                                            "arguments": tool_call.function.arguments or ""
                                        }
                                    }
                                else:
                                    current_tool_call = tool_calls[tool_call.index]
                            
                            # 累積參數
                            if tool_call.function and tool_call.function.arguments:
                                current_tool_call["function"]["arguments"] += tool_call.function.arguments
                            if tool_call.function and tool_call.function.name:
                                current_tool_call["function"]["name"] = tool_call.function.name
                            if tool_call.id:
                                current_tool_call["id"] = tool_call.id
                
                # 加入最後一個 tool call
                if current_tool_call:
                    tool_calls.append(current_tool_call)
                
                # 如果沒有 tool calls，結束迭代
                if not tool_calls:
                    # 取得 Token 使用量（估計）
                    total_prompt_tokens += len(user_message) // 4
                    total_completion_tokens += len("".join(collected_messages)) // 4
                    break
                
                # 執行 Tool Calls
                assistant_message = {
                    "role": "assistant",
                    "content": "".join(collected_messages) if collected_messages else None,
                    "tool_calls": []
                }
                
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    arguments_str = tool_call["function"]["arguments"]
                    
                    try:
                        arguments = json.loads(arguments_str)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # 通知前端 Function Calling
                    yield f"event: function_call\ndata: {json.dumps({'type': 'function_call', 'name': function_name, 'arguments': arguments})}\n\n"
                    
                    # 調用 Function
                    result = await self._call_function(function_name, arguments)
                    
                    # 通知前端 Function 結果
                    yield f"event: function_result\ndata: {json.dumps({'type': 'function_result', 'name': function_name, 'result': result})}\n\n"
                    
                    # 加入到對話歷史
                    assistant_message["tool_calls"].append({
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": arguments_str
                        }
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                messages.append(assistant_message)
                
                # 更新 Token 計數（估計）
                total_prompt_tokens += len(arguments_str) // 4
                total_completion_tokens += len(json.dumps(result)) // 4
            
            # 完成
            total_tokens = total_prompt_tokens + total_completion_tokens
            yield f"event: done\ndata: {json.dumps({'type': 'done', 'tokens': {'prompt': total_prompt_tokens, 'completion': total_completion_tokens, 'total': total_tokens}})}\n\n"
            
            # 記錄 AI 使用
            await self._log_ai_usage(
                staff_id=staff_id,
                session_id=session_id,
                usage_type="chat",
                prompt_text=user_message,
                response_text="".join(collected_messages),
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens
            )
            
        except Exception as e:
            error_msg = f"AI 對話錯誤: {str(e)}"
            logger.error(error_msg, error=str(e))
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
    
    async def _log_ai_usage(
        self,
        staff_id: str,
        session_id: str,
        usage_type: str,
        prompt_text: str,
        response_text: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ):
        """
        記錄 AI 使用到資料庫
        
        Args:
            staff_id: 門市人員 ID
            session_id: Session ID
            usage_type: 使用類型（chat/comparison/recommendation）
            prompt_text: 提示詞文字
            response_text: 回應文字
            prompt_tokens: Prompt Token 數
            completion_tokens: Completion Token 數
            total_tokens: 總 Token 數
        """
        # 計算成本
        cost = (
            prompt_tokens / 1000 * PRICING["gpt-4o"]["prompt"] +
            completion_tokens / 1000 * PRICING["gpt-4o"]["completion"]
        )
        
        logger.info(
            "記錄 AI 使用",
            staff_id=staff_id,
            session_id=session_id,
            usage_type=usage_type,
            total_tokens=total_tokens,
            cost=cost
        )
        
        try:
            # 取得 DatabaseManager
            from .database import DatabaseManager
            db = DatabaseManager()
            await db.initialize()
            
            # 寫入資料庫
            sql = """
                INSERT INTO ai_usage_logs (
                    staff_id, session_id, usage_type,
                    prompt_text, response_text,
                    prompt_tokens, completion_tokens, total_tokens,
                    cost_amount, created_at
                )
                VALUES (
                    :staff_id, :session_id, :usage_type,
                    :prompt_text, :response_text,
                    :prompt_tokens, :completion_tokens, :total_tokens,
                    :cost_amount, SYSDATE
                )
            """
            
            await db.execute(
                sql,
                {
                    'staff_id': staff_id,
                    'session_id': session_id,
                    'usage_type': usage_type,
                    'prompt_text': prompt_text[:4000] if prompt_text else None,  # CLOB 限制
                    'response_text': response_text[:4000] if response_text else None,  # CLOB 限制
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'cost_amount': cost
                }
            )
            
            await db.close()
            
            logger.info("AI 使用記錄已寫入資料庫", usage_id="auto-generated")
            
        except Exception as e:
            logger.error("寫入 AI 使用記錄失敗", error=str(e), exc_info=True)
