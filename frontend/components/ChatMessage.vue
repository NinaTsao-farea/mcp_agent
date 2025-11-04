<template>
  <div class="chat-message" :class="[message.role]">
    <div class="message-avatar">
      <UIcon 
        :name="message.role === 'user' ? 'i-heroicons-user-circle' : 'i-heroicons-cpu-chip'" 
        class="w-8 h-8"
      />
    </div>
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">
          {{ message.role === 'user' ? '您' : 'AI 助理' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
      
      <div class="message-body">
        <!-- Loading 動畫 -->
        <div v-if="message.isLoading" class="loading-indicator">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          <span>思考中...</span>
        </div>
        
        <!-- 訊息內容 -->
        <div v-else class="message-text" v-html="renderedContent"></div>
        
        <!-- Function Calls 顯示 -->
        <div v-if="message.functionCalls && message.functionCalls.length > 0" class="function-calls">
          <div class="function-calls-header">
            <UIcon name="i-heroicons-command-line" class="w-4 h-4" />
            <span>工具調用</span>
          </div>
          
          <div 
            v-for="(fc, index) in message.functionCalls" 
            :key="index"
            class="function-call-item"
            :class="fc.status"
          >
            <div class="function-name">
              <UIcon 
                :name="getStatusIcon(fc.status)" 
                class="w-4 h-4"
              />
              <span>{{ getFunctionDisplayName(fc.name) }}</span>
            </div>
            
            <!-- 可選：顯示參數 -->
            <div v-if="showDetails" class="function-args">
              <pre>{{ JSON.stringify(fc.arguments, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import type { ChatMessage, FunctionCall } from '~/composables/useAIChat'

interface Props {
  message: ChatMessage
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})

// 初始化 Markdown 渲染器
let md: MarkdownIt | null = null

onMounted(() => {
  // 在客戶端初始化（避免 SSR 問題）
  md = new MarkdownIt({
    html: false, // 不允許 HTML 標籤（安全性）
    linkify: true, // 自動轉換 URL 為連結
    typographer: true, // 優化排版
    breaks: true // 換行轉換為 <br>
  })
})

/**
 * 格式化時間
 */
function formatTime(date: Date): string {
  return new Intl.DateTimeFormat('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

/**
 * 渲染訊息內容（使用 markdown-it）
 */
const renderedContent = computed(() => {
  if (!md) {
    // SSR 或初始化前使用簡單渲染
    return props.message.content.replace(/\n/g, '<br>')
  }
  
  try {
    return md.render(props.message.content)
  } catch (error) {
    console.error('Markdown rendering error:', error)
    return props.message.content.replace(/\n/g, '<br>')
  }
})

/**
 * 取得 Function 狀態圖示
 */
function getStatusIcon(status: FunctionCall['status']): string {
  switch (status) {
    case 'calling':
      return 'i-heroicons-arrow-path'
    case 'completed':
      return 'i-heroicons-check-circle'
    case 'error':
      return 'i-heroicons-x-circle'
    default:
      return 'i-heroicons-question-mark-circle'
  }
}

/**
 * 取得 Function 顯示名稱（中文化）
 */
function getFunctionDisplayName(name: string): string {
  const nameMap: Record<string, string> = {
    'get_customer': '查詢客戶資料',
    'list_customer_phones': '列出客戶門號',
    'get_phone_details': '查詢門號詳情',
    'check_renewal_eligibility': '檢查續約資格',
    'check_promotion_eligibility': '檢查促銷資格',
    'query_device_stock': '查詢設備庫存',
    'get_device_info': '查詢設備詳情',
    'get_recommended_devices': '取得推薦設備',
    'get_device_pricing': '查詢設備價格',
    'search_promotions': '搜尋促銷方案',
    'get_plan_details': '查詢方案詳情',
    'compare_plans': '比較方案',
    'calculate_upgrade_cost': '計算升級費用'
  }
  
  return nameMap[name] || name
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.chat-message.user .message-avatar {
  color: rgb(59 130 246); /* blue-500 */
}

.chat-message.assistant .message-avatar {
  color: rgb(34 197 94); /* green-500 */
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.chat-message.user .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: rgb(107 114 128); /* gray-500 */
}

.chat-message.user .message-header {
  justify-content: flex-end;
}

.message-role {
  font-weight: 600;
}

.message-time {
  font-size: 0.75rem;
}

.message-body {
  background: rgb(249 250 251); /* gray-50 */
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
}

.chat-message.user .message-body {
  background: rgb(59 130 246); /* blue-500 */
  color: white;
}

.chat-message.assistant .message-body {
  background: white;
  border: 1px solid rgb(229 231 235); /* gray-200 */
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgb(107 114 128); /* gray-500 */
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(code) {
  background: rgb(243 244 246); /* gray-100 */
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 0.875rem;
  color: rgb(220 38 38); /* red-600 */
}

.message-text :deep(pre) {
  background: rgb(31 41 55); /* gray-800 */
  color: rgb(243 244 246); /* gray-100 */
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.5rem 0;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

.message-text :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message-text :deep(li) {
  margin: 0.25rem 0;
}

.message-text :deep(blockquote) {
  border-left: 4px solid rgb(209 213 219); /* gray-300 */
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: rgb(107 114 128); /* gray-500 */
  font-style: italic;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5rem 0;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid rgb(229 231 235); /* gray-200 */
  padding: 0.5rem;
  text-align: left;
}

.message-text :deep(th) {
  background: rgb(243 244 246); /* gray-100 */
  font-weight: 600;
}

.message-text :deep(a) {
  color: rgb(59 130 246); /* blue-500 */
  text-decoration: underline;
}

.message-text :deep(a:hover) {
  color: rgb(37 99 235); /* blue-600 */
}

.function-calls {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgb(229 231 235); /* gray-200 */
}

.function-calls-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgb(107 114 128); /* gray-500 */
}

.function-call-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  background: rgb(243 244 246); /* gray-100 */
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.function-call-item.calling {
  color: rgb(59 130 246); /* blue-500 */
}

.function-call-item.completed {
  color: rgb(34 197 94); /* green-500 */
}

.function-call-item.error {
  color: rgb(239 68 68); /* red-500 */
}

.function-name {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-weight: 500;
}

.function-args {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: rgb(107 114 128); /* gray-500 */
}

.function-args pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Dark mode support (optional) */
@media (prefers-color-scheme: dark) {
  .message-body {
    background: rgb(31 41 55); /* gray-800 */
  }
  
  .chat-message.assistant .message-body {
    background: rgb(55 65 81); /* gray-700 */
    border-color: rgb(75 85 99); /* gray-600 */
  }
  
  .function-calls {
    border-top-color: rgb(75 85 99); /* gray-600 */
  }
  
  .function-call-item {
    background: rgb(31 41 55); /* gray-800 */
  }
}
</style>
