<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="customer">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        客戶門號列表
      </h2>
      <p class="text-sm text-gray-600 mb-6">
        請選擇要續約的門號
      </p>
      
      <!-- 客戶資訊卡片 -->
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 class="text-sm font-semibold text-gray-700 mb-2">客戶資訊</h3>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-600">姓名：</span>
            <span class="font-medium">{{ customer.name }}</span>
          </div>
          <div>
            <span class="text-gray-600">聯絡電話：</span>
            <span class="font-medium">{{ customer.phone }}</span>
          </div>
          <div v-if="customer.email" class="col-span-2">
            <span class="text-gray-600">Email：</span>
            <span class="font-medium">{{ customer.email }}</span>
          </div>
        </div>
      </div>
      
      <!-- 門號卡片列表 -->
      <div v-if="phones.length > 0" class="space-y-4">
        <div
          v-for="phone in phones"
          :key="phone.phone_number"
          @click="handleSelectPhone(phone.phone_number)"
          class="border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
          :class="selectedPhone?.phone_number === phone.phone_number 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-200 hover:border-gray-300'"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <h4 class="text-lg font-semibold text-gray-900">
                {{ phone.phone_number }}
              </h4>
              <div class="flex items-center gap-2 mt-1">
                <UBadge 
                  :color="phone.is_primary ? 'primary' : 'gray'"
                  variant="soft"
                >
                  {{ phone.is_primary ? '主要門號' : '副門號' }}
                </UBadge>
                <UBadge color="green" variant="soft">
                  {{ phone.status }}
                </UBadge>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-primary-600">
                ${{ phone.monthly_fee }}
              </div>
              <div class="text-xs text-gray-500">每月</div>
            </div>
          </div>
          
          <!-- 方案資訊 -->
          <div class="grid grid-cols-3 gap-4 mb-3 text-sm">
            <div>
              <div class="text-gray-600">目前方案</div>
              <div class="font-medium">{{ phone.plan_name }}</div>
            </div>
            <div>
              <div class="text-gray-600">數據流量</div>
              <div class="font-medium">{{ phone.data_limit }}</div>
            </div>
            <div>
              <div class="text-gray-600">合約到期</div>
              <div class="font-medium">
                {{ formatDate(phone.contract_end_date) }}
              </div>
            </div>
          </div>
          
          <!-- 詳細資訊摺疊 -->
          <UAccordion 
            :items="[{ label: '查看詳細資訊', slot: 'details-' + phone.phone_number }]"
            @click.stop
          >
            <template #[`details-${phone.phone_number}`]>
              <div class="p-4 space-y-4">
                <!-- 合約資訊 -->
                <div v-if="phone.contract">
                  <h5 class="font-semibold text-gray-700 mb-2">合約資訊</h5>
                  <div class="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span class="text-gray-600">合約期間：</span>
                      <span>{{ phone.contract.contract_months }} 個月</span>
                    </div>
                    <div>
                      <span class="text-gray-600">已使用：</span>
                      <span>{{ phone.contract.months_used }} 個月</span>
                    </div>
                    <div>
                      <span class="text-gray-600">語音分鐘：</span>
                      <span>{{ phone.contract.voice_minutes }} 分鐘</span>
                    </div>
                    <div>
                      <span class="text-gray-600">搭配手機：</span>
                      <span>{{ phone.contract.device || '無' }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 使用量資訊 -->
                <div v-if="phone.usage">
                  <h5 class="font-semibold text-gray-700 mb-2">本月使用量</h5>
                  <div class="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span class="text-gray-600">數據用量：</span>
                      <span>{{ phone.usage.data_used_gb?.toFixed(2) }} / {{ phone.usage.data_limit_gb }} GB</span>
                    </div>
                    <div>
                      <span class="text-gray-600">語音用量：</span>
                      <span>{{ phone.usage.voice_used_minutes }} / {{ phone.usage.voice_limit_minutes }} 分鐘</span>
                    </div>
                  </div>
                </div>
                
                <!-- 帳單資訊 -->
                <div v-if="phone.billing">
                  <h5 class="font-semibold text-gray-700 mb-2">帳單資訊</h5>
                  <div class="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span class="text-gray-600">本月帳單：</span>
                      <span class="font-medium">${{ phone.billing.current_month_fee }}</span>
                    </div>
                    <div>
                      <span class="text-gray-600">繳費狀態：</span>
                      <UBadge :color="phone.billing.outstanding_balance === 0 ? 'green' : 'orange'">
                        {{ phone.billing.outstanding_balance === 0 ? '已繳清' : `未繳 $${phone.billing.outstanding_balance}` }}
                      </UBadge>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </UAccordion>
        </div>
      </div>
      
      <div v-else class="text-center py-12 text-gray-500">
        <p>查無門號資料</p>
      </div>
      
      <!-- 返回按鈕 -->
      <div class="mt-6 flex justify-center">
        <UButton
          variant="outline"
          size="lg"
          @click="handleBackToQuery"
        >
          返回重新查詢
        </UButton>
      </div>
    </div>
    
    <div v-else class="text-center py-12 text-gray-500">
      <p>請先查詢客戶資料</p>
      <UButton 
        class="mt-4"
        @click="navigateTo('/renewal/query-customer')"
      >
        返回查詢客戶
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
// Composables
const router = useRouter()
const {
  customer,
  phones,
  selectedPhone,
  loading,
  selectPhone,
  clearWorkflow
} = useRenewalWorkflow()

// 如果沒有客戶資料，返回查詢頁面
onMounted(() => {
  if (!customer.value) {
    navigateTo('/renewal/query-customer')
  }
})

// 方法
const goBack = () => {
  router.back()
}

const handleBackToQuery = () => {
  clearWorkflow()
  navigateTo('/renewal/query-customer')
}

const handleSelectPhone = async (phoneNumber: string) => {
  try {
    const result = await selectPhone(phoneNumber)
    
    if (!result || !result.success) {
      console.log('門號不符合續約資格，顯示檢查結果')
    } else {
      console.log('門號符合續約資格，可繼續流程')
    }
    
    // 無論結果如何，都導航到資格檢查頁面
    navigateTo('/renewal/eligibility')
  } catch (err: any) {
    console.error('選擇門號失敗:', err)
  }
}

// 工具函數
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  })
}

const formatDataUsage = (mb: number) => {
  if (mb >= 1000) {
    return `${(mb / 1000).toFixed(1)} GB`
  }
  return `${mb} MB`
}
</script>
