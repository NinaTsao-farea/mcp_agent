<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航列 -->
    <AppNavbar 
      :show-welcome="false" 
      :show-back="true" 
      title="續約流程"
      @back="goBack"
    />
    
    <!-- 主要內容 -->
    <main class="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- 進度條 -->
      <div class="mb-8 px-4">
        <div class="flex items-center justify-between">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <!-- 步驟圓圈 -->
            <div class="flex flex-col items-center">
              <div 
                class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-colors"
                :class="getStepClass(index)"
              >
                {{ index + 1 }}
              </div>
              <span 
                class="mt-2 text-xs text-center"
                :class="currentStepIndex >= index ? 'text-gray-900' : 'text-gray-400'"
              >
                {{ step.label }}
              </span>
            </div>
            
            <!-- 連接線 -->
            <div 
              v-if="index < steps.length - 1"
              class="flex-1 h-1 mx-2 transition-colors"
              :class="currentStepIndex > index ? 'bg-primary-600' : 'bg-gray-200'"
            />
          </div>
        </div>
      </div>
      
      <!-- 子頁面內容 -->
      <div class="px-4 py-6 sm:px-0">
        <NuxtPage />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// 頁面設定
definePageMeta({
  middleware: 'auth'
})

// Composables
const {
  sessionId,
  customer,
  selectedPhone,
  eligibilityCheck,
  startWorkflow,
  clearWorkflow,
  restoreSession
} = useRenewalWorkflow()

const route = useRoute()

// 步驟定義 - 精簡為關鍵流程
const steps = [
  { label: '客戶資料', paths: ['/renewal/start', '/renewal/query-customer', '/renewal/select-phone'] },
  { label: '資格檢查', paths: ['/renewal/eligibility'] },
  { label: '選擇設備', paths: ['/renewal/select-device-type', '/renewal/select-device-os', '/renewal/select-device', '/renewal/query-devices'] },
  { label: '選擇方案', paths: ['/renewal/list-plans', '/renewal/compare-plans'] },
  { label: '確認申辦', paths: ['/renewal/confirm', '/renewal/success'] }
]

// 當前步驟索引
const currentStepIndex = computed(() => {
  const path = route.path
  
  // 找出當前路徑屬於哪個步驟
  for (let i = 0; i < steps.length; i++) {
    if (steps[i].paths.some(p => path.includes(p.split('/').pop() || ''))) {
      return i
    }
  }
  
  return 0 // 預設第一步
})

// 步驟樣式
const getStepClass = (index: number) => {
  if (index < currentStepIndex.value) {
    return 'bg-primary-600 text-white'
  } else if (index === currentStepIndex.value) {
    return 'bg-primary-600 text-white ring-4 ring-primary-100'
  } else {
    return 'bg-gray-200 text-gray-600'
  }
}

// 方法
const router = useRouter()

const goBack = () => {
  // 使用瀏覽器返回，讓各頁面的 goBack 邏輯自行處理
  router.back()
}

// 生命週期
onMounted(async () => {
  // 嘗試恢復 Session
  const restored = await restoreSession()
  
  if (!restored) {
    // 如果沒有 Session，開始新流程
    try {
      await startWorkflow()
    } catch (err) {
      console.error('開始流程失敗:', err)
    }
  }
  
  // 根據狀態導航到正確的步驟
  if (route.path === '/renewal' || route.path === '/renewal/') {
    // 預設導航到開始頁面
    navigateTo('/renewal/start')
  }
})

onBeforeUnmount(() => {
  // 離開頁面時不清除 Session，保留狀態
})
</script>

<style scoped>
/* 自定義樣式 */
</style>
