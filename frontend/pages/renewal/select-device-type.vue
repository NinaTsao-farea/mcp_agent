<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-6">
      <!-- 主要內容區域 -->
      <div class="flex-1 max-w-5xl">
      <!-- 麵包屑導航 -->
      <nav class="mb-6 text-sm">
        <ol class="flex items-center space-x-2 text-gray-500">
          <li>續約流程</li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li>資格檢查</li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li class="text-blue-600 font-medium">選擇續約方式</li>
        </ol>
      </nav>

      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">選擇續約方式</h1>
        <p class="mt-2 text-gray-600">請選擇是否搭配裝置購買</p>
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
        <!-- 單純續約 -->
        <div 
          class="bg-white p-6 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedType === 'none' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectType('none')"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-blue-100">
                <UIcon name="i-heroicons-phone-arrow-up-right" class="w-7 h-7 text-blue-600" />
              </div>
            </div>
            <div class="ml-4 flex-1">
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">單純續約</h3>
                <UIcon 
                  v-if="selectedType === 'none'" 
                  name="i-heroicons-check-circle-solid" 
                  class="w-6 h-6 text-blue-600" 
                />
              </div>
              <p class="mt-2 text-gray-600">不搭配裝置購買，直接選擇資費方案</p>
              <div class="mt-3 flex items-center text-sm text-blue-600">
                <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 mr-1" />
                <span>直接前往方案選擇</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 智慧型手機 -->
        <div 
          class="bg-white p-6 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedType === 'smartphone' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectType('smartphone')"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-green-100">
                <UIcon name="i-heroicons-device-phone-mobile" class="w-7 h-7 text-green-600" />
              </div>
            </div>
            <div class="ml-4 flex-1">
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">智慧型手機</h3>
                <UIcon 
                  v-if="selectedType === 'smartphone'" 
                  name="i-heroicons-check-circle-solid" 
                  class="w-6 h-6 text-blue-600" 
                />
              </div>
              <p class="mt-2 text-gray-600">搭配 iPhone、Android 手機購買</p>
              <div class="mt-3">
                <UBadge color="green" variant="soft" size="xs">最熱門</UBadge>
              </div>
            </div>
          </div>
        </div>

        <!-- 平板電腦 -->
        <div 
          class="bg-white p-6 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedType === 'tablet' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectType('tablet')"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-purple-100">
                <UIcon name="i-heroicons-device-tablet" class="w-7 h-7 text-purple-600" />
              </div>
            </div>
            <div class="ml-4 flex-1">
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">平板電腦</h3>
                <UIcon 
                  v-if="selectedType === 'tablet'" 
                  name="i-heroicons-check-circle-solid" 
                  class="w-6 h-6 text-blue-600" 
                />
              </div>
              <p class="mt-2 text-gray-600">搭配 iPad、Android 平板購買</p>
              <div class="mt-3 text-sm text-gray-500">
                適合商務、學習使用
              </div>
            </div>
          </div>
        </div>

        <!-- 穿戴裝置 -->
        <div 
          class="bg-white p-6 rounded-xl shadow-md cursor-pointer hover:shadow-xl transition-all duration-200 border-2"
          :class="selectedType === 'wearable' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent hover:border-gray-300'"
          @click="selectType('wearable')"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-orange-100">
                <UIcon name="i-heroicons-clock" class="w-7 h-7 text-orange-600" />
              </div>
            </div>
            <div class="ml-4 flex-1">
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">穿戴裝置</h3>
                <UIcon 
                  v-if="selectedType === 'wearable'" 
                  name="i-heroicons-check-circle-solid"
                  class="w-6 h-6 text-blue-600" 
                />
              </div>
              <p class="mt-2 text-gray-600">搭配智慧手錶、手環購買</p>
              <div class="mt-3 text-sm text-gray-500">
                適合運動、健康追蹤
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
            <p class="font-medium mb-1">溫馨提醒</p>
            <ul class="space-y-1 text-blue-700">
              <li>• 單純續約：維持原有資費方案或更換新方案</li>
              <li>• 搭配裝置：可享專屬優惠價格及分期方案</li>
              <li>• 選擇後可隨時返回修改</li>
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
          :disabled="!selectedType || workflowLoading"
          :loading="workflowLoading"
          @click="handleSubmit"
        >
          <span>下一步</span>
          <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 ml-2" />
        </UButton>
      </div>
      </div>
      
      <!-- AI 聊天框側邊欄 -->
      <div class="w-96 flex-shrink-0">
        <div class="sticky top-8">
          <AIChatBox 
            v-if="renewalSessionId"
            :session-id="renewalSessionId"
            :disabled="workflowLoading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const {
  sessionId: renewalSessionId,
  selectDeviceType,
  loading: workflowLoading,
  error: workflowError
} = useRenewalWorkflow()

// 狀態
const selectedType = ref<string | null>(null)
const error = ref<string | null>(null)

// 選擇裝置類型
const selectType = (type: string) => {
  selectedType.value = type
  error.value = null
}

// 提交選擇
const handleSubmit = async () => {
  if (!selectedType.value) {
    error.value = '請選擇續約方式'
    return
  }
  
  if (!renewalSessionId.value) {
    error.value = '缺少 Session ID，請重新開始流程'
    return
  }
  
  try {
    const response = await selectDeviceType(selectedType.value)
    
    if (response.success) {
      // 根據選擇導向不同頁面
      if (selectedType.value === 'none') {
        // 單純續約，跳到方案列表
        await router.push('/renewal/list-plans')
      } else {
        // 搭配裝置，前往作業系統選擇
        await router.push('/renewal/select-device-os')
      }
    }
  } catch (err: any) {
    console.error('選擇裝置類型失敗:', err)
    error.value = workflowError.value || err.message || '選擇裝置類型失敗'
  }
}

// 返回上一步
const goBack = () => {
  // Step 5 select-device-type 的上一步固定是 Step 3 select-phone
  navigateTo('/renewal/select-phone')
}

// 頁面載入時檢查參數
onMounted(() => {
  if (!renewalSessionId.value) {
    error.value = '缺少 Session ID，請重新開始流程'
  }
})
</script>
