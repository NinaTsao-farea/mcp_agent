/**
 * AI Chat Composable - Sprint 7
 * 
 * 處理 AI 對話的 SSE 串流接收
 * TypeScript: 使用 MessageEvent 類型處理 EventSource 事件
 */
import { ref, type Ref } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isLoading?: boolean
  functionCalls?: FunctionCall[]
}

export interface FunctionCall {
  name: string
  arguments: Record<string, any>
  result?: any
  status: 'calling' | 'completed' | 'error'
}

export interface TokenUsage {
  prompt: number
  completion: number
  total: number
}

export function useAIChat() {
  const messages: Ref<ChatMessage[]> = ref([])
  const isConnected = ref(false)
  const isStreaming = ref(false)
  const error = ref<string | null>(null)
  const tokenUsage: Ref<TokenUsage | null> = ref(null)
  
  let eventSource: EventSource | null = null
  let currentMessageId: string | null = null
  
  /**
   * 發送訊息並接收 AI 回答（SSE 串流）
   */
  async function sendMessage(sessionId: string, message: string) {
    if (!message.trim()) {
      return
    }
    
    // 重置狀態
    error.value = null
    tokenUsage.value = null
    
    // 添加使用者訊息
    const userMessageId = `user-${Date.now()}`
    messages.value.push({
      id: userMessageId,
      role: 'user',
      content: message,
      timestamp: new Date()
    })
    
    // 添加 AI 訊息（載入中）
    currentMessageId = `assistant-${Date.now()}`
    messages.value.push({
      id: currentMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
      functionCalls: []
    })
    
    try {
      // 使用 EventSource 建立 SSE 連線（只支援 GET 請求）
      const config = useRuntimeConfig()
      const baseURL = config.public.apiBaseUrl || 'http://localhost:8000'
      
      // 取得認證 Session ID
      const authSessionId = typeof window !== 'undefined' 
        ? localStorage.getItem('session_id') 
        : null
      
      if (!authSessionId) {
        throw new Error('請先登入')
      }
      
      const url = new URL('/api/renewal-workflow/chat/stream', baseURL)
      url.searchParams.set('session_id', authSessionId)  // 認證 Session ID
      url.searchParams.set('renewal_session_id', sessionId)  // 續約流程 Session ID
      url.searchParams.set('message', message)
      
      // 調試日誌
      console.log('[AI Chat] 發送請求:', {
        authSessionId,
        renewalSessionId: sessionId,
        message,
        url: url.toString()
      })
      
      eventSource = new EventSource(url.toString())
      isConnected.value = true
      isStreaming.value = true
      
      // 處理訊息事件
      eventSource.addEventListener('message', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          handleSSEEvent(data)
        } catch (e) {
          console.error('解析 SSE 訊息失敗:', e)
        }
      })
      
      // 處理 function_call 事件
      eventSource.addEventListener('function_call', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          handleFunctionCall(data)
        } catch (e) {
          console.error('解析 function_call 失敗:', e)
        }
      })
      
      // 處理 function_result 事件
      eventSource.addEventListener('function_result', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          handleFunctionResult(data)
        } catch (e) {
          console.error('解析 function_result 失敗:', e)
        }
      })
      
      // 處理 done 事件
      eventSource.addEventListener('done', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          handleDone(data)
        } catch (e) {
          console.error('解析 done 事件失敗:', e)
        }
      })
      
      // 處理錯誤事件
      eventSource.addEventListener('error', (event: MessageEvent) => {
        try {
          console.error('[AI Chat] SSE 錯誤事件:', event)
          const data = JSON.parse(event.data)
          console.error('[AI Chat] 錯誤數據:', data)
          handleError(data)
        } catch (e) {
          console.error('[AI Chat] SSE 連線錯誤:', e, 'Event:', event)
          error.value = '連線錯誤，請檢查 Session 是否有效'
          closeConnection()
        }
      })
      
    } catch (e: any) {
      console.error('發送訊息失敗:', e)
      error.value = e.message || '發送訊息失敗'
      
      // 移除載入中的訊息
      if (currentMessageId) {
        const index = messages.value.findIndex(m => m.id === currentMessageId)
        if (index !== -1) {
          messages.value.splice(index, 1)
        }
      }
    }
  }
  
  /**
   * 處理 SSE 訊息事件
   */
  function handleSSEEvent(data: any) {
    if (data.type === 'message' && currentMessageId) {
      const currentMessage = messages.value.find(m => m.id === currentMessageId)
      if (currentMessage) {
        currentMessage.content += data.content
        currentMessage.isLoading = false
      }
    }
  }
  
  /**
   * 處理 Function Calling 事件
   */
  function handleFunctionCall(data: any) {
    if (data.type === 'function_call' && currentMessageId) {
      const currentMessage = messages.value.find(m => m.id === currentMessageId)
      if (currentMessage) {
        if (!currentMessage.functionCalls) {
          currentMessage.functionCalls = []
        }
        
        currentMessage.functionCalls.push({
          name: data.name,
          arguments: data.arguments,
          status: 'calling'
        })
      }
    }
  }
  
  /**
   * 處理 Function Result 事件
   */
  function handleFunctionResult(data: any) {
    if (data.type === 'function_result' && currentMessageId) {
      const currentMessage = messages.value.find(m => m.id === currentMessageId)
      if (currentMessage && currentMessage.functionCalls) {
        const functionCall = currentMessage.functionCalls.find(
          fc => fc.name === data.name && fc.status === 'calling'
        )
        if (functionCall) {
          functionCall.result = data.result
          functionCall.status = 'completed'
        }
      }
    }
  }
  
  /**
   * 處理完成事件
   */
  function handleDone(data: any) {
    if (data.type === 'done') {
      tokenUsage.value = data.tokens
      
      if (currentMessageId) {
        const currentMessage = messages.value.find(m => m.id === currentMessageId)
        if (currentMessage) {
          currentMessage.isLoading = false
        }
      }
      
      closeConnection()
    }
  }
  
  /**
   * 處理錯誤事件
   */
  function handleError(data: any) {
    if (data.type === 'error') {
      error.value = data.error
      
      if (currentMessageId) {
        const currentMessage = messages.value.find(m => m.id === currentMessageId)
        if (currentMessage) {
          currentMessage.isLoading = false
          currentMessage.content = `錯誤: ${data.error}`
        }
      }
      
      closeConnection()
    }
  }
  
  /**
   * 關閉 SSE 連線
   */
  function closeConnection() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    isConnected.value = false
    isStreaming.value = false
  }
  
  /**
   * 清除對話歷史
   */
  function clearMessages() {
    messages.value = []
    error.value = null
    tokenUsage.value = null
  }
  
  /**
   * 組件卸載時清理
   */
  function cleanup() {
    closeConnection()
  }
  
  return {
    messages,
    isConnected,
    isStreaming,
    error,
    tokenUsage,
    sendMessage,
    clearMessages,
    cleanup
  }
}
