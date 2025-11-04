<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 麵包屑導航 -->
      <nav class="mb-6 text-sm">
        <ol class="flex items-center space-x-2 text-gray-500">
          <li>續約流程</li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li>選擇續約方式</li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li class="text-blue-600 font-medium">選擇作業系統</li>
        </ol>
      </nav>

      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">選擇作業系統</h1>
        <p class="mt-2 text-gray-600">請選擇您喜歡的手機作業系統</p>
      </div>

      <!-- 錯誤訊息 -->
      <UAlert
        v-if="error"
        icon="i-heroicons-exclamation-triangle"
        color="red"
        variant="soft"
        title="錯誤"
        :description="error"
        class="mb-6"
        :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'gray', variant: 'link', padded: false }"
        @close="error = null"
      />

      <!-- 選項卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <!-- iOS -->
        <div 
          class="bg-white p-8 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedOS === 'ios' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectOS('ios')"
        >
          <div class="flex flex-col items-center text-center">
            <div class="flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-4">
              <UIcon name="i-heroicons-device-phone-mobile" class="w-12 h-12 text-gray-700" />
            </div>
            <div class="flex items-center justify-between w-full mb-2">
              <h3 class="text-2xl font-semibold text-gray-900 flex-1">iOS</h3>
              <UIcon 
                v-if="selectedOS === 'ios'" 
                name="i-heroicons-check-circle-solid" 
                class="w-8 h-8 text-blue-600" 
              />
            </div>
            <p class="text-gray-600 mb-4">iPhone 系列手機</p>
            <div class="w-full space-y-2 text-left">
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>流暢的使用體驗</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>完整的生態系統</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>高品質應用程式</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Android -->
        <div 
          class="bg-white p-8 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedOS === 'android' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectOS('android')"
        >
          <div class="flex flex-col items-center text-center">
            <div class="flex items-center justify-center w-20 h-20 rounded-full bg-green-100 mb-4">
              <UIcon name="i-heroicons-device-phone-mobile" class="w-12 h-12 text-green-600" />
            </div>
            <div class="flex items-center justify-between w-full mb-2">
              <h3 class="text-2xl font-semibold text-gray-900 flex-1">Android</h3>
              <UIcon 
                v-if="selectedOS === 'android'" 
                name="i-heroicons-check-circle-solid" 
                class="w-8 h-8 text-blue-600" 
              />
            </div>
            <p class="text-gray-600 mb-4">Samsung, Google Pixel 等</p>
            <div class="w-full space-y-2 text-left">
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>多樣化選擇</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>客製化彈性高</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2 text-green-600" />
                <span>價格選擇豐富</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 提示訊息 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-start">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
          <div class="text-sm text-blue-800">
            <p class="font-medium mb-1">選擇建議</p>
            <ul class="space-y-1 text-blue-700">
              <li>• 若您目前使用 iPhone，建議繼續選擇 iOS</li>
              <li>• 若您追求更多客製化功能，可選擇 Android</li>
              <li>• 兩種系統都有豐富的機型與價格選擇</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 操作按鈕 -->
      <div class="flex justify-between items-center">
        <UButton
          color="gray"
          variant="outline"
          size="lg"
          :disabled="workflowLoading"
          @click="goBack"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 mr-2" />
          返回
        </UButton>
        
        <UButton
          color="primary"
          size="lg"
          :disabled="!selectedOS || workflowLoading"
          :loading="workflowLoading"
          @click="handleSubmit"
        >
          <span>下一步：選擇手機</span>
          <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 ml-2" />
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const router = useRouter()
const {
  sessionId: renewalSessionId,
  selectDeviceOS,
  loading: workflowLoading,
  error: workflowError
} = useRenewalWorkflow()

// 狀態
const selectedOS = ref<string | null>(null)
const error = ref<string | null>(null)

// 選擇作業系統
const selectOS = (os: string) => {
  selectedOS.value = os
  error.value = null
}

// 提交選擇
const handleSubmit = async () => {
  if (!selectedOS.value) {
    error.value = '請選擇作業系統'
    return
  }
  
  if (!renewalSessionId.value) {
    error.value = '缺少 Session ID，請重新開始流程'
    return
  }
  
  try {
    const response = await selectDeviceOS(selectedOS.value)
    
    if (response.success) {
      // 導向到 Step 7: 選擇手機
      await router.push('/renewal/select-device')
    }
  } catch (err: any) {
    console.error('選擇作業系統失敗:', err)
    error.value = workflowError.value || err.message || '選擇作業系統失敗'
  }
}

// 返回上一步
const goBack = () => {
  // Step 6 select-device-os 的上一步固定是 Step 5 select-device-type
  navigateTo('/renewal/select-device-type')
}

// 頁面載入時檢查參數
onMounted(() => {
  if (!renewalSessionId.value) {
    error.value = '缺少 Session ID，請重新開始流程'
  }
})
</script>
