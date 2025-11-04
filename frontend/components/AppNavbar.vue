<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <!-- 如果有返回按鈕 -->
          <button
            v-if="showBack"
            @click="handleBack"
            class="mr-4 text-gray-600 hover:text-gray-900"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          
          <!-- 標題 -->
          <h1 class="text-xl font-semibold text-gray-900">
            {{ title || '電信門市銷售助理系統' }}
          </h1>
        </div>
        
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-600">
            {{ showWelcome ? '歡迎，' : '' }}{{ user?.name || '使用者' }}
          </span>
          <UButton 
            variant="ghost" 
            size="sm"
            @click="handleLogout"
          >
            登出
          </UButton>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
// 定義 props
const props = defineProps({
  showWelcome: {
    type: Boolean,
    default: true
  },
  showBack: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  backTo: {
    type: String,
    default: '/'
  }
})

// 定義 emits
const emit = defineEmits(['back'])

// 檢查是否有監聽器
const attrs = useAttrs()

const { user, logout: authLogout } = useAuth()
const { clearWorkflow } = useRenewalWorkflow()

const handleBack = () => {
  // 如果頁面有監聽 @back 事件，觸發它
  if (attrs.onBack) {
    emit('back')
  } else {
    // 否則使用預設行為：導航到 backTo
    navigateTo(props.backTo)
  }
}

const handleLogout = async () => {
  try {
    // 清除續約工作流狀態
    await clearWorkflow()
    // 執行登出
    await authLogout()
    await navigateTo('/login')
  } catch (error) {
    console.error('登出錯誤:', error)
  }
}
</script>
