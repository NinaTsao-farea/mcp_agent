<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="eligibilityCheck">
      <div v-if="eligibilityCheck.eligible">
        <!-- 符合資格 -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            符合續約資格
          </h2>
          <p class="text-gray-600">
            門號 {{ selectedPhone?.phone_number }} 已通過資格檢查
          </p>
        </div>
        
        <!-- 檢查項目 -->
        <div class="space-y-3 mb-8">
          <div
            v-for="(detail, index) in eligibilityCheck.details"
            :key="index"
            class="flex items-start p-4 bg-gray-50 rounded-lg"
          >
            <div 
              class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mr-3"
              :class="detail.status === 'pass' ? 'bg-green-100' : 'bg-red-100'"
            >
              <svg 
                v-if="detail.status === 'pass'"
                class="w-4 h-4 text-green-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg 
                v-else
                class="w-4 h-4 text-red-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="font-semibold text-gray-900">{{ detail.item }}</div>
              <div class="text-sm text-gray-600 mt-1">{{ detail.message }}</div>
            </div>
          </div>
        </div>
        
        <!-- 繼續按鈕 -->
        <div class="flex justify-center gap-4">
          <UButton
            variant="outline"
            size="lg"
            @click="handleBackToPhoneList"
          >
            選擇其他門號
          </UButton>
          <UButton
            size="lg"
            @click="handleContinueToNext"
          >
            下一步：選擇續約方式
          </UButton>
        </div>
      </div>
      
      <div v-else>
        <!-- 不符合資格 -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            不符合續約資格
          </h2>
          <p class="text-gray-600">
            門號 {{ selectedPhone?.phone_number }} 暫時無法續約
          </p>
        </div>
        
        <!-- 檢查項目 -->
        <div class="space-y-3 mb-8">
          <div
            v-for="(detail, index) in eligibilityCheck.details"
            :key="index"
            class="flex items-start p-4 rounded-lg"
            :class="detail.status === 'pass' ? 'bg-green-50' : 'bg-red-50'"
          >
            <div 
              class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mr-3"
              :class="detail.status === 'pass' ? 'bg-green-100' : 'bg-red-100'"
            >
              <svg 
                v-if="detail.status === 'pass'"
                class="w-4 h-4 text-green-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg 
                v-else
                class="w-4 h-4 text-red-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="font-semibold" :class="detail.status === 'pass' ? 'text-green-900' : 'text-red-900'">
                {{ detail.item }}
              </div>
              <div class="text-sm mt-1" :class="detail.status === 'pass' ? 'text-green-700' : 'text-red-700'">
                {{ detail.message }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 返回按鈕 -->
        <div class="flex justify-center">
          <UButton
            variant="outline"
            size="lg"
            @click="handleBackToPhoneList"
          >
            選擇其他門號
          </UButton>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-12 text-gray-500">
      <p>請先選擇門號</p>
      <UButton 
        class="mt-4"
        @click="goBack"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 mr-2" />
        返回
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
// Composables
const router = useRouter()
const route = useRoute()
const {
  sessionId: renewalSessionId,
  selectedPhone,
  eligibilityCheck,
  clearSelection
} = useRenewalWorkflow()

// 如果沒有選擇門號，返回選擇頁面
onMounted(() => {
  if (!selectedPhone.value) {
    navigateTo('/renewal/select-phone')
  }
})

// 方法
const goBack = () => {
  router.back()
}

const handleBackToPhoneList = () => {
  clearSelection()
  navigateTo('/renewal/select-phone')
}

const handleContinueToNext = () => {
  // 導向到 Step 5: 選擇裝置類型
  if (renewalSessionId.value) {
    navigateTo('/renewal/select-device-type')
  } else {
    console.error('缺少 Session ID')
    navigateTo('/renewal/query-customer')
  }
}
</script>
