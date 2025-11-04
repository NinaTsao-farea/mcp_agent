<template>
  <div class="ai-chat-box">
    <!-- 標題欄 -->
    <div class="chat-header">
      <div class="header-title">
        <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5" />
        <h3>AI 智能助理</h3>
      </div>
      
      <div class="header-actions">
        <UBadge v-if="isStreaming" color="green" variant="subtle">
          <UIcon name="i-heroicons-arrow-path" class="w-3 h-3 animate-spin" />
          回答中
        </UBadge>
        
        <UButton
          v-if="messages.length > 0"
          icon="i-heroicons-trash"
          size="xs"
          color="gray"
          variant="ghost"
          @click="handleClear"
        >
          清除
        </UButton>
      </div>
    </div>
    
    <!-- 訊息列表 -->
    <div ref="messagesContainer" class="messages-container">
      <!-- 空狀態 -->
      <div v-if="messages.length === 0" class="empty-state">
        <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-16 h-16 text-gray-300" />
        <p class="text-gray-500">您可以向 AI 助理詢問方案比較、門號詳情等問題</p>
        <div class="example-questions">
          <p class="text-sm text-gray-400 mb-2">範例問題：</p>
          <UButton
            v-for="example in exampleQuestions"
            :key="example"
            size="xs"
            color="gray"
            variant="soft"
            @click="handleExampleClick(example)"
          >
            {{ example }}
          </UButton>
        </div>
      </div>
      
      <!-- 訊息列表 -->
      <ChatMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :show-details="false"
      />
      
      <!-- 錯誤提示 -->
      <UAlert
        v-if="error"
        icon="i-heroicons-exclamation-triangle"
        color="red"
        variant="soft"
        title="發生錯誤"
        :description="error"
        :close-button="{ icon: 'i-heroicons-x-mark', color: 'red', variant: 'link' }"
        @close="error = null"
      />
    </div>
    
    <!-- Token 使用資訊 -->
    <div v-if="tokenUsage" class="token-usage">
      <UIcon name="i-heroicons-chart-bar" class="w-4 h-4" />
      <span class="text-xs text-gray-500">
        Token 使用: {{ tokenUsage.total }} 
        (輸入: {{ tokenUsage.prompt }}, 輸出: {{ tokenUsage.completion }})
      </span>
    </div>
    
    <!-- 輸入框 -->
    <div class="chat-input">
      <UTextarea
        v-model="inputMessage"
        :rows="2"
        placeholder="輸入您的問題..."
        :disabled="isStreaming"
        @keydown.enter.exact.prevent="handleSend"
      />
      
      <UButton
        icon="i-heroicons-paper-airplane"
        :loading="isStreaming"
        :disabled="!inputMessage.trim() || isStreaming"
        @click="handleSend"
      >
        發送
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useAIChat } from '~/composables/useAIChat'
import ChatMessage from './ChatMessage.vue'

interface Props {
  sessionId: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// AI Chat Composable
const {
  messages,
  isConnected,
  isStreaming,
  error,
  tokenUsage,
  sendMessage,
  clearMessages,
  cleanup
} = useAIChat()

// 輸入訊息
const inputMessage = ref('')

// 訊息容器 ref
const messagesContainer = ref<HTMLElement | null>(null)

// 範例問題
const exampleQuestions = [
  '方案 A 和方案 B 有什麼差異？',
  '這個門號的合約何時到期？',
  '有哪些適合學生的方案？',
  '目前有什麼促銷活動？'
]

/**
 * 發送訊息
 */
async function handleSend() {
  if (!inputMessage.value.trim() || isStreaming.value || props.disabled) {
    return
  }
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  await sendMessage(props.sessionId, message)
  
  // 滾動到底部
  scrollToBottom()
}

/**
 * 點擊範例問題
 */
function handleExampleClick(question: string) {
  inputMessage.value = question
  handleSend()
}

/**
 * 清除對話
 */
function handleClear() {
  if (confirm('確定要清除所有對話嗎？')) {
    clearMessages()
    inputMessage.value = ''
  }
}

/**
 * 滾動到底部
 */
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 監聽訊息變化，自動滾動
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 組件掛載時滾動到底部
onMounted(() => {
  scrollToBottom()
})

// 組件卸載時清理
onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.ai-chat-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 600px;
  background: white;
  border: 1px solid rgb(229 231 235); /* gray-200 */
  border-radius: 0.75rem;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgb(229 231 235); /* gray-200 */
  background: rgb(249 250 251); /* gray-50 */
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-title h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: rgb(31 41 55); /* gray-800 */
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: rgb(249 250 251); /* gray-50 */
}

/* 自定義滾動條 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgb(209 213 219); /* gray-300 */
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgb(156 163 175); /* gray-400 */
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 2rem;
}

.empty-state p {
  margin-top: 1rem;
  margin-bottom: 1.5rem;
}

.example-questions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.token-usage {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgb(249 250 251); /* gray-50 */
  border-top: 1px solid rgb(229 231 235); /* gray-200 */
}

.chat-input {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid rgb(229 231 235); /* gray-200 */
  background: white;
}

.chat-input :deep(textarea) {
  resize: none;
}

/* Dark mode support (optional) */
@media (prefers-color-scheme: dark) {
  .ai-chat-box {
    background: rgb(17 24 39); /* gray-900 */
    border-color: rgb(55 65 81); /* gray-700 */
  }
  
  .chat-header {
    background: rgb(31 41 55); /* gray-800 */
    border-bottom-color: rgb(55 65 81); /* gray-700 */
  }
  
  .header-title h3 {
    color: rgb(243 244 246); /* gray-100 */
  }
  
  .messages-container {
    background: rgb(31 41 55); /* gray-800 */
  }
  
  .token-usage {
    background: rgb(31 41 55); /* gray-800 */
    border-top-color: rgb(55 65 81); /* gray-700 */
  }
  
  .chat-input {
    background: rgb(17 24 39); /* gray-900 */
    border-top-color: rgb(55 65 81); /* gray-700 */
  }
}
</style>
