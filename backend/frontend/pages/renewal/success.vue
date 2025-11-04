<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-indigo-50 py-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow-2xl rounded-2xl overflow-hidden">
        <!-- 成功圖示區 -->
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 px-8 py-12 text-center">
          <div class="inline-flex items-center justify-center w-24 h-24 bg-white rounded-full mb-6 shadow-lg">
            <UIcon name="i-heroicons-check-circle" class="w-16 h-16 text-green-500" />
          </div>
          <h1 class="text-3xl font-bold text-white mb-2">申辦成功！</h1>
          <p class="text-green-50 text-lg">您的續約申請已成功提交</p>
        </div>

        <!-- 訂單資訊 -->
        <div class="px-8 py-10">
          <div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 mb-8">
            <div class="text-center">
              <p class="text-sm text-gray-600 mb-2">訂單編號</p>
              <p class="text-3xl font-bold text-blue-600 tracking-wider mb-4">
                {{ orderNumber || '-' }}
              </p>
              <div class="flex items-center justify-center text-sm text-gray-500">
                <UIcon name="i-heroicons-clock" class="w-4 h-4 mr-2" />
                <span>{{ currentDateTime }}</span>
              </div>
            </div>
          </div>

          <!-- 費用總額 -->
          <div v-if="totalAmount !== null" class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 mb-8">
            <div class="flex justify-between items-center">
              <span class="text-lg text-gray-700">應付總額</span>
              <span class="text-3xl font-bold text-gray-900">
                ${{ totalAmount.toLocaleString() }}
              </span>
            </div>
          </div>

          <!-- 後續步驟 -->
          <div class="border-t border-gray-200 pt-8 mb-8">
            <h2 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <UIcon name="i-heroicons-clipboard-document-list" class="w-6 h-6 mr-2 text-blue-600" />
              後續步驟
            </h2>
            <div class="space-y-4">
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full">
                    <span class="text-sm font-semibold text-blue-600">1</span>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-900">簡訊通知</p>
                  <p class="text-sm text-gray-600">我們將發送簡訊到您的門號，請留意收件</p>
                </div>
              </div>

              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full">
                    <span class="text-sm font-semibold text-blue-600">2</span>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-900">文件準備</p>
                  <p class="text-sm text-gray-600">請攜帶身分證正本及訂單編號</p>
                </div>
              </div>

              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full">
                    <span class="text-sm font-semibold text-blue-600">3</span>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-900">門市辦理</p>
                  <p class="text-sm text-gray-600">請於 7 日內至全台任一門市完成簽約手續</p>
                </div>
              </div>

              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full">
                    <span class="text-sm font-semibold text-blue-600">4</span>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-900">合約生效</p>
                  <p class="text-sm text-gray-600">簽約完成後，新方案將立即生效</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 注意事項 -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
            <div class="flex items-start">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
              <div>
                <p class="text-sm font-medium text-yellow-900 mb-1">重要提醒</p>
                <ul class="text-sm text-yellow-800 space-y-1 list-disc list-inside">
                  <li>訂單保留期限為 7 天，逾期將自動取消</li>
                  <li>若選購手機，需於門市確認實機後才能取貨</li>
                  <li>如有任何問題，請撥打客服專線 0800-000-000</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="flex flex-col sm:flex-row gap-4">
            <UButton
              color="white"
              size="lg"
              block
              @click="viewOrder"
            >
              <UIcon name="i-heroicons-document-text" class="w-5 h-5 mr-2" />
              查看訂單詳情
            </UButton>
            <UButton
              color="primary"
              size="lg"
              block
              @click="startNewApplication"
            >
              <UIcon name="i-heroicons-plus-circle" class="w-5 h-5 mr-2" />
              開始新的申辦
            </UButton>
          </div>

          <!-- 返回首頁 -->
          <div class="mt-6 text-center">
            <UButton
              color="gray"
              variant="link"
              @click="goHome"
            >
              <UIcon name="i-heroicons-home" class="w-4 h-4 mr-1" />
              返回首頁
            </UButton>
          </div>
        </div>
      </div>

      <!-- 客服聯絡卡片 -->
      <div class="mt-8 bg-white shadow rounded-lg p-6">
        <div class="text-center">
          <UIcon name="i-heroicons-phone" class="w-8 h-8 text-blue-600 mx-auto mb-3" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">需要協助嗎？</h3>
          <p class="text-gray-600 mb-4">我們的客服團隊隨時為您服務</p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a href="tel:0800000000" class="flex items-center text-blue-600 hover:text-blue-700 font-medium">
              <UIcon name="i-heroicons-phone" class="w-5 h-5 mr-2" />
              0800-000-000
            </a>
            <span class="hidden sm:inline text-gray-300">|</span>
            <a href="mailto:service@telecom.com" class="flex items-center text-blue-600 hover:text-blue-700 font-medium">
              <UIcon name="i-heroicons-envelope" class="w-5 h-5 mr-2" />
              service@telecom.com
            </a>
          </div>
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

// 從查詢參數取得訂單資訊
const orderNumber = computed(() => route.query.order_number as string || null)
const totalAmount = computed(() => {
  const amount = route.query.total_amount as string
  return amount ? parseFloat(amount) : null
})

// 取得當前時間
const currentDateTime = computed(() => {
  const now = new Date()
  return now.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
})

// 查看訂單詳情
const viewOrder = () => {
  // TODO: 實作訂單詳情頁面
  alert(`訂單編號: ${orderNumber.value}\n\n此功能將在後續版本實作`)
}

// 開始新的申辦
const startNewApplication = () => {
  router.push('/renewal/query-customer')
}

// 返回首頁
const goHome = () => {
  router.push('/')
}

// 頁面載入時檢查是否有訂單編號
onMounted(() => {
  if (!orderNumber.value) {
    // 如果沒有訂單編號，可能是直接訪問此頁面，導向查詢客戶頁面
    router.push('/renewal/query-customer')
  }
})
</script>
