<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        方案比較
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        比較所選方案的特性與優惠
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
      <span class="ml-3 text-lg">載入中...</span>
    </div>

    <!-- Error State -->
    <UAlert
      v-else-if="errorMessage"
      color="red"
      variant="soft"
      :title="errorMessage"
      class="mb-6"
    />

    <!-- Comparison Result -->
    <div v-else-if="comparisonData">
      <!-- AI Recommendation -->
      <UCard v-if="comparisonData.recommendation" class="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-sparkles" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100">AI 智能推薦</h3>
          </div>
        </template>
        <p class="text-base text-blue-800 dark:text-blue-200">
          {{ comparisonData.recommendation }}
        </p>
      </UCard>

      <!-- Comparison Table -->
      <UCard class="mb-6">
        <template #header>
          <h3 class="text-lg font-semibold">方案特性比較</h3>
        </template>
        
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-gray-800">
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 border-b">
                  特性
                </th>
                <th
                  v-for="plan in comparisonData.plans"
                  :key="plan.plan_id"
                  class="px-4 py-3 text-center text-sm font-semibold text-gray-700 dark:text-gray-300 border-b"
                >
                  {{ plan.name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <!-- Monthly Fee Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  月租費
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`fee-${plan.plan_id}`"
                  class="px-4 py-3 text-center"
                >
                  <span 
                    class="text-lg font-bold"
                    :class="plan.monthly_fee === minMonthlyFee ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-100'"
                  >
                    ${{ plan.monthly_fee }}
                  </span>
                  <UBadge
                    v-if="plan.monthly_fee === minMonthlyFee"
                    color="green"
                    variant="soft"
                    size="xs"
                    class="ml-2"
                  >
                    最低價
                  </UBadge>
                </td>
              </tr>

              <!-- Data Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  上網流量
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`data-${plan.plan_id}`"
                  class="px-4 py-3 text-center"
                >
                  <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {{ plan.data }}
                  </span>
                  <UBadge
                    v-if="plan.data.includes('無限')"
                    color="blue"
                    variant="soft"
                    size="xs"
                    class="ml-2"
                  >
                    吃到飽
                  </UBadge>
                </td>
              </tr>

              <!-- Voice Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  語音通話
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`voice-${plan.plan_id}`"
                  class="px-4 py-3 text-center text-sm text-gray-700 dark:text-gray-300"
                >
                  {{ plan.voice }}
                </td>
              </tr>

              <!-- SMS Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  簡訊
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`sms-${plan.plan_id}`"
                  class="px-4 py-3 text-center text-sm text-gray-700 dark:text-gray-300"
                >
                  {{ plan.sms }}
                </td>
              </tr>

              <!-- Contract Months Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  合約期限
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`contract-${plan.plan_id}`"
                  class="px-4 py-3 text-center text-sm text-gray-700 dark:text-gray-300"
                >
                  {{ plan.contract_months }} 個月
                </td>
              </tr>

              <!-- Features Row -->
              <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  方案特色
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`features-${plan.plan_id}`"
                  class="px-4 py-3 text-center align-top"
                >
                  <div class="flex flex-wrap gap-1 justify-center">
                    <UBadge
                      v-for="(feature, idx) in plan.features"
                      :key="idx"
                      color="gray"
                      variant="soft"
                      size="xs"
                    >
                      {{ feature }}
                    </UBadge>
                  </div>
                </td>
              </tr>

              <!-- Gifts Row -->
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  贈品
                </td>
                <td
                  v-for="plan in comparisonData.plans"
                  :key="`gifts-${plan.plan_id}`"
                  class="px-4 py-3 text-center align-top"
                >
                  <div class="flex flex-wrap gap-1 justify-center">
                    <UBadge
                      v-for="(gift, idx) in plan.gifts"
                      :key="idx"
                      color="green"
                      variant="soft"
                      size="xs"
                    >
                      {{ gift }}
                    </UBadge>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Action Buttons -->
      <div class="flex justify-between gap-4">
        <UButton
          color="gray"
          variant="soft"
          size="lg"
          @click="goBack"
          :disabled="isLoading"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 mr-2" />
          返回方案列表
        </UButton>

        <div class="flex gap-3">
          <UButton
            v-for="plan in comparisonData.plans"
            :key="`select-${plan.plan_id}`"
            color="primary"
            size="lg"
            @click="selectPlan(plan.plan_id)"
            :disabled="isLoading"
          >
            選擇 {{ plan.name }}
          </UButton>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <UCard v-else class="text-center py-12">
      <UIcon name="i-heroicons-inbox" class="w-16 h-16 mx-auto text-gray-400 mb-4" />
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        沒有可比較的方案
      </p>
      <UButton
        color="primary"
        @click="goBack"
      >
        返回方案列表
      </UButton>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth']
})

const route = useRoute()
const router = useRouter()
const workflow = useRenewalWorkflow()

// State
const isLoading = ref(false)
const errorMessage = ref('')
const comparisonData = ref<any>(null)

// Computed
const minMonthlyFee = computed(() => {
  if (!comparisonData.value?.plans) return 0
  return Math.min(...comparisonData.value.plans.map((p: any) => p.monthly_fee))
})

// Methods
const loadComparison = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    // Get plan IDs from query params
    const planIdsParam = route.query.planIds as string
    if (!planIdsParam) {
      errorMessage.value = '未提供方案 ID'
      return
    }

    const planIds = planIdsParam.split(',')
    
    // Call API
    const response = await workflow.comparePlans(planIds)
    
    if (response.success && response.comparison) {
      comparisonData.value = response.comparison
    } else {
      errorMessage.value = response.error || '比較方案失敗'
    }
  } catch (err: any) {
    console.error('比較方案錯誤:', err)
    errorMessage.value = err.message || '載入失敗，請稍後再試'
  } finally {
    isLoading.value = false
  }
}

const selectPlan = async (planId: string) => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    // 呼叫 select-plan API 更新 session 狀態到 CONFIRM
    const { selectPlan: selectPlanAPI } = useRenewalWorkflow()
    await selectPlanAPI(planId)
    
    // API 成功後才跳轉到確認頁面，帶上來源參數
    await router.push({
      path: '/renewal/confirm',
      query: { from: 'compare-plans' }
    })
  } catch (err: any) {
    console.error('選擇方案錯誤:', err)
    errorMessage.value = err.message || '選擇方案失敗'
    isLoading.value = false
  }
}

const goBack = () => {
  router.push('/renewal/list-plans')
}

// Lifecycle
onMounted(() => {
  loadComparison()
})
</script>

<style scoped>
/* Custom styles if needed */
table {
  border-spacing: 0;
}

tbody tr:last-child td {
  border-bottom: none;
}
</style>
