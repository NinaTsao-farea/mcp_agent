<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Breadcrumb -->
      <nav class="mb-6">
        <ol class="flex items-center space-x-2 text-sm text-gray-500">
          <li>續約流程</li>
          <li><i class="i-heroicons-chevron-right-solid w-4 h-4" /></li>
          <li>選擇裝置類型</li>
          <li><i class="i-heroicons-chevron-right-solid w-4 h-4" /></li>
          <li>選擇作業系統</li>
          <li><i class="i-heroicons-chevron-right-solid w-4 h-4" /></li>
          <li>選擇裝置</li>
          <li><i class="i-heroicons-chevron-right-solid w-4 h-4" /></li>
          <li class="text-primary-600 font-medium">選擇方案</li>
        </ol>
      </nav>

      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">選擇方案</h1>
        <p class="text-gray-600">為客戶挑選最適合的資費方案</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <i class="i-heroicons-arrow-path-solid w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
        <p class="text-gray-600">載入方案列表中...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <i class="i-heroicons-x-circle-solid w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-red-900 mb-2">載入失敗</h3>
        <p class="text-red-700 mb-4">{{ error }}</p>
        <UButton color="red" variant="outline" @click="loadPlans">重試</UButton>
      </div>

      <!-- Plan List -->
      <div v-else>
        <!-- Filter Bar -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center gap-4">
          <div class="flex items-center gap-2">
            <i class="i-heroicons-funnel-solid w-5 h-5 text-gray-500" />
            <span class="text-sm font-medium text-gray-700">篩選：</span>
          </div>
          <USelect
            v-model="selectedPriceRange"
            :options="priceRangeOptions"
            placeholder="所有價格"
            class="w-48"
          />
          <USelect
            v-model="selectedDataRange"
            :options="dataRangeOptions"
            placeholder="所有流量"
            class="w-48"
          />
          <div class="ml-auto text-sm text-gray-600">
            共 <span class="font-semibold text-primary-600">{{ filteredPlans.length }}</span> 個方案
          </div>
        </div>

        <!-- Plan Cards Grid -->
        <div v-if="filteredPlans.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="plan in filteredPlans"
            :key="plan.plan_id"
            class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden cursor-pointer border-2"
            :class="{
              'border-primary-500 ring-2 ring-primary-200': selectedPlan?.plan_id === plan.plan_id,
              'border-gray-200 hover:border-gray-300': selectedPlan?.plan_id !== plan.plan_id
            }"
            @click="selectPlanCard(plan)"
          >
            <!-- Recommended Badge -->
            <div
              v-if="plan.is_recommended"
              class="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-2 text-center"
            >
              <div class="flex items-center justify-center gap-2">
                <i class="i-heroicons-star-solid w-5 h-5" />
                <span class="font-semibold">推薦方案</span>
              </div>
            </div>

            <!-- Plan Content -->
            <div class="p-6">
              <!-- Checkbox for Comparison -->
              <div class="flex items-center gap-3 mb-4">
                <UCheckbox
                  :model-value="selectedPlansForCompare.includes(plan.plan_id)"
                  @update:model-value="togglePlanForCompare(plan.plan_id)"
                  @click.stop
                  label="加入比較"
                />
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-900 mb-1">{{ plan.name }}</h3>
                  <p v-if="plan.promotion_title" class="text-sm text-primary-600">
                    {{ plan.promotion_title }}
                  </p>
                </div>
              </div>

              <!-- Price -->
              <div class="mb-6 pb-6 border-b border-gray-200">
                <div class="flex items-baseline gap-2">
                  <span class="text-4xl font-bold text-primary-600">{{ plan.monthly_fee }}</span>
                  <span class="text-gray-600">元/月</span>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  合約期數：{{ plan.contract_months }} 個月
                </p>
              </div>

              <!-- Features -->
              <div class="space-y-3 mb-6">
                <div class="flex items-start gap-3">
                  <i class="i-heroicons-signal-solid w-5 h-5 text-primary-500 mt-0.5" />
                  <div>
                    <p class="text-sm font-medium text-gray-700">數據流量</p>
                    <p class="text-sm text-gray-600">{{ plan.data }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <i class="i-heroicons-phone-solid w-5 h-5 text-primary-500 mt-0.5" />
                  <div>
                    <p class="text-sm font-medium text-gray-700">語音通話</p>
                    <p class="text-sm text-gray-600">{{ plan.voice }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <i class="i-heroicons-chat-bubble-left-right-solid w-5 h-5 text-primary-500 mt-0.5" />
                  <div>
                    <p class="text-sm font-medium text-gray-700">簡訊</p>
                    <p class="text-sm text-gray-600">{{ plan.sms || '不限' }}</p>
                  </div>
                </div>
              </div>

              <!-- Gifts -->
              <div v-if="plan.gifts && plan.gifts.length > 0" class="mb-4">
                <p class="text-sm font-medium text-gray-700 mb-2">贈品</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="gift in plan.gifts"
                    :key="gift"
                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    <i class="i-heroicons-gift-solid w-3 h-3 mr-1" />
                    {{ gift }}
                  </span>
                </div>
              </div>

              <!-- Selection Indicator -->
              <div v-if="selectedPlan?.plan_id === plan.plan_id" class="flex justify-center pt-4 border-t border-gray-200">
                <div class="flex items-center gap-2 text-primary-600 font-medium">
                  <i class="i-heroicons-check-circle-solid w-6 h-6" />
                  <span>已選擇</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="bg-white rounded-lg shadow-sm p-12 text-center">
          <i class="i-heroicons-document-text-solid w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">暫無符合條件的方案</h3>
          <p class="text-gray-600">請嘗試調整篩選條件</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div v-if="!loading && !error" class="mt-8 flex justify-between items-center">
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

        <div class="flex items-center gap-4">
          <!-- Compare Button -->
          <UButton
            v-if="selectedPlansForCompare.length > 0"
            color="blue"
            variant="outline"
            size="lg"
            :disabled="selectedPlansForCompare.length < 2 || workflowLoading"
            @click="comparePlans"
          >
            <UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5 mr-2" />
            比較方案 ({{ selectedPlansForCompare.length }})
          </UButton>

          <!-- Next Button -->
          <UButton
            color="primary"
            size="lg"
            :disabled="!selectedPlan || workflowLoading"
            :loading="workflowLoading"
            @click="handleNext"
          >
            <span>下一步</span>
            <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 ml-2" />
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const router = useRouter()

const { sessionId, listPlans, loading: workflowLoading, error: workflowError } = useRenewalWorkflow()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const plans = ref<any[]>([])
const selectedPlan = ref<any | null>(null)
const selectedPlansForCompare = ref<string[]>([])
const sessionData = ref<any>(null)

// Filters
const selectedPriceRange = ref<string>('all')
const selectedDataRange = ref<string>('all')

// Options
const priceRangeOptions = [
  { value: 'all', label: '所有價格' },
  { value: 'low', label: 'NT$ 500 以下' },
  { value: 'mid', label: 'NT$ 500 - 1000' },
  { value: 'high', label: 'NT$ 1000 以上' }
]

const dataRangeOptions = [
  { value: 'all', label: '所有流量' },
  { value: 'limited', label: '限量（< 100GB）' },
  { value: 'large', label: '大流量（≥ 100GB）' },
  { value: 'unlimited', label: '無限制' }
]

// Computed
const filteredPlans = computed(() => {
  let filtered = plans.value

  // Filter by price range
  if (selectedPriceRange.value !== 'all') {
    filtered = filtered.filter(p => {
      const price = p.monthly_fee
      if (selectedPriceRange.value === 'low') return price < 500
      if (selectedPriceRange.value === 'mid') return price >= 500 && price <= 1000
      if (selectedPriceRange.value === 'high') return price > 1000
      return true
    })
  }

  // Filter by data range
  if (selectedDataRange.value !== 'all') {
    filtered = filtered.filter(p => {
      const data = p.data.toLowerCase()
      if (selectedDataRange.value === 'unlimited') return data.includes('無限') || data.includes('吃到飽')
      if (selectedDataRange.value === 'large') {
        const match = data.match(/(\d+)\s*gb/i)
        return match && parseInt(match[1]) >= 100
      }
      if (selectedDataRange.value === 'limited') {
        const match = data.match(/(\d+)\s*gb/i)
        return match && parseInt(match[1]) < 100
      }
      return true
    })
  }

  return filtered
})

// Methods
const loadPlans = async () => {
  loading.value = true
  error.value = null
  
  if (!sessionId.value) {
    error.value = '找不到 session，請重新開始流程'
    loading.value = false
    return
  }
  
  try {
    console.log('Loading plans with session_id:', sessionId.value)
    
    // 使用 composable 方法呼叫 API
    const response = await listPlans()
    
    console.log('API Response:', response)
    
    if (response.success && response.plans) {
      plans.value = response.plans
    } else {
      error.value = response.error || '載入方案列表失敗'
    }
  } catch (err: any) {
    error.value = err.message || workflowError.value || '載入方案列表失敗，請稍後再試'
    console.error('Load plans error:', err)
  } finally {
    loading.value = false
  }
}

const selectPlanCard = (plan: any) => {
  selectedPlan.value = plan
}

const togglePlanForCompare = (planId: string) => {
  const index = selectedPlansForCompare.value.indexOf(planId)
  if (index > -1) {
    selectedPlansForCompare.value.splice(index, 1)
  } else {
    if (selectedPlansForCompare.value.length >= 4) {
      error.value = '最多只能選擇 4 個方案進行比較'
      return
    }
    selectedPlansForCompare.value.push(planId)
  }
}

const comparePlans = () => {
  if (selectedPlansForCompare.value.length < 2) {
    error.value = '請至少選擇 2 個方案進行比較'
    return
  }
  
  navigateTo({
    path: '/renewal/compare-plans',
    query: {
      planIds: selectedPlansForCompare.value.join(',')
    }
  })
}

const handleNext = async () => {
  if (!selectedPlan.value) return
  
  try {
    loading.value = true
    error.value = null
    
    // 呼叫 select-plan API 更新 session 狀態到 CONFIRM
    const { selectPlan } = useRenewalWorkflow()
    await selectPlan(selectedPlan.value.plan_id)
    
    // API 成功後才跳轉到確認頁面，帶上來源參數
    navigateTo({
      path: '/renewal/confirm',
      query: { from: 'list-plans' }
    })
  } catch (err: any) {
    error.value = err.message || '選擇方案失敗，請稍後再試'
    console.error('Select plan error:', err)
  } finally {
    loading.value = false
  }
}

// 返回上一步
const goBack = () => {
  // 根據 device_type 決定返回路徑
  const deviceType = sessionData.value?.customer_selection?.device_type
  
  if (deviceType === 'none') {
    // 單純續約，返回 select-device-type
    navigateTo('/renewal/select-device-type')
  } else {
    // 有購買設備，返回 select-device
    navigateTo('/renewal/select-device')
  }
}

// Lifecycle
onMounted(async () => {
  if (!sessionId.value) {
    navigateTo('/renewal/start')
    return
  }
  
  // 載入 session 資料以判斷 device_type
  try {
    const { getSession } = useRenewalWorkflow()
    const session = await getSession()
    if (session) {
      sessionData.value = session
    }
  } catch (err) {
    console.error('Failed to load session:', err)
  }
  
  loadPlans()
})
</script>
