<template>
  <div class="app-container">
    <!-- 導航列 -->
    <AppNavbar />
    
    <!-- 主要內容 -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <!-- 開始續約流程 -->
          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              續約流程
            </h2>
            <p class="text-sm text-gray-600 mb-4">
              開始新的客戶續約服務流程
            </p>
            <UButton 
              color="primary" 
              block
              @click="startRenewal"
            >
              開始續約
            </UButton>
          </div>
          
          <!-- 個人統計 -->
          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              今日統計
            </h2>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">服務客戶數</span>
                <span class="text-sm font-medium">{{ stats.todayCustomers }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">成功續約</span>
                <span class="text-sm font-medium">{{ stats.todaySales }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">轉換率</span>
                <span class="text-sm font-medium">{{ stats.conversionRate }}%</span>
              </div>
            </div>
          </div>
          
          <!-- AI 助理 -->
          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              AI 助理
            </h2>
            <p class="text-sm text-gray-600 mb-4">
              快速查詢方案資訊和客戶問題
            </p>
            <UButton 
              color="gray" 
              block
              @click="openAIChat"
            >
              開啟對話
            </UButton>
          </div>
          
        </div>
        
        <!-- 最近的續約記錄 -->
        <div class="mt-8">
          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              最近的續約記錄
            </h2>
            <div class="overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      時間
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      客戶
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      門號
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      狀態
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-if="recentRecords.length === 0">
                    <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                      暫無記錄
                    </td>
                  </tr>
                  <tr v-for="record in recentRecords" :key="record.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatTime(record.createdAt) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ record.customerName }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ record.phoneNumber }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <UBadge 
                        :color="getStatusColor(record.status)"
                        variant="soft"
                      >
                        {{ getStatusText(record.status) }}
                      </UBadge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
// 頁面設定
definePageMeta({
  middleware: 'auth' // 需要登入才能訪問
})

// 組合式函數
const { stats, recentRecords, fetchDashboardData } = useStatistics()

// 載入資料
onMounted(async () => {
  await fetchDashboardData()
})

// 方法
const startRenewal = () => {
  navigateTo('/renewal')
}

const openAIChat = () => {
  // TODO: 開啟 AI 對話介面
  console.log('開啟 AI 對話')
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-TW')
}

const getStatusColor = (status) => {
  switch (status) {
    case 'completed': return 'green'
    case 'in_progress': return 'blue'
    case 'cancelled': return 'red'
    default: return 'gray'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'in_progress': return '進行中'
    case 'cancelled': return '已取消'
    default: return '未知'
  }
}
</script>