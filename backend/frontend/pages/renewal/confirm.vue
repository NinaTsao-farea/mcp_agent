<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">確認申辦</h1>
        <p class="mt-2 text-gray-600">請仔細核對以下資訊，確認無誤後即可提交申辦</p>
      </div>

      <!-- 載入中 -->
      <div v-if="loading" class="bg-white shadow rounded-lg p-12 text-center">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p class="text-gray-600">載入申辦資料中...</p>
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

      <!-- 申辦摘要 -->
      <div v-if="!loading && summary" class="space-y-6">
        <!-- 客戶資料 -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <UIcon name="i-heroicons-user" class="w-5 h-5 mr-2" />
              客戶資料
            </h2>
          </div>
          <div class="px-6 py-4">
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">姓名</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.customer?.name || '-' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">身分證字號</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.customer?.id_number || '-' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">聯絡電話</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.customer?.phone || '-' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Email</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.customer?.email || '-' }}</dd>
              </div>
              <div class="sm:col-span-2">
                <dt class="text-sm font-medium text-gray-500">地址</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.customer?.address || '-' }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 門號資料 -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <UIcon name="i-heroicons-device-phone-mobile" class="w-5 h-5 mr-2" />
              門號資料
            </h2>
          </div>
          <div class="px-6 py-4">
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">門號</dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold">
                  {{ summary.phone?.phone_number || '-' }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">門號狀態</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  <UBadge :color="summary.phone?.status === 'active' ? 'green' : 'gray'" variant="soft">
                    {{ summary.phone?.status === 'active' ? '使用中' : summary.phone?.status }}
                  </UBadge>
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 目前合約 -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <UIcon name="i-heroicons-document-text" class="w-5 h-5 mr-2" />
              目前合約
            </h2>
          </div>
          <div class="px-6 py-4">
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">方案名稱</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.contract?.plan_name || '-' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">月租費</dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold">
                  ${{ summary.contract?.monthly_fee?.toLocaleString() || 0 }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">合約起日</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.contract?.contract_start || '-' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">合約到期</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.contract?.contract_end || '-' }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 選擇的手機 -->
        <div v-if="summary.selected_device" class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <UIcon name="i-heroicons-device-phone-mobile" class="w-5 h-5 mr-2" />
              選擇的手機
            </h2>
          </div>
          <div class="px-6 py-4">
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">品牌型號</dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold">
                  {{ summary.selected_device.brand }} {{ summary.selected_device.model }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">顏色</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.selected_device.color }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">容量</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.selected_device.storage }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">價格</dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold text-blue-600">
                  ${{ summary.selected_device.price?.toLocaleString() || 0 }}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 選擇的方案 -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 bg-blue-50 border-b border-blue-200">
            <h2 class="text-lg font-semibold text-blue-900 flex items-center">
              <UIcon name="i-heroicons-sparkles" class="w-5 h-5 mr-2" />
              新選擇的方案
            </h2>
          </div>
          <div class="px-6 py-4">
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">方案名稱</dt>
                <dd class="mt-1 text-sm text-gray-900 font-semibold">
                  {{ summary.selected_plan?.plan_name || '-' }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">月租費</dt>
                <dd class="mt-1 text-lg font-bold text-blue-600">
                  ${{ summary.selected_plan?.monthly_fee?.toLocaleString() || 0 }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">合約期</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ summary.selected_plan?.contract_months || 0 }} 個月
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">網路流量</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.selected_plan?.data || '-' }}</dd>
              </div>
              <div class="sm:col-span-2">
                <dt class="text-sm font-medium text-gray-500">通話</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ summary.selected_plan?.voice || '-' }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 費用總結 -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 shadow rounded-lg overflow-hidden border-2 border-blue-200">
          <div class="px-6 py-4 bg-blue-600">
            <h2 class="text-lg font-semibold text-white flex items-center">
              <UIcon name="i-heroicons-currency-dollar" class="w-5 h-5 mr-2" />
              費用總結
            </h2>
          </div>
          <div class="px-6 py-6">
            <dl class="space-y-3">
              <div class="flex justify-between items-center text-sm">
                <dt class="text-gray-600">手機款</dt>
                <dd class="font-semibold text-gray-900">
                  ${{ summary.cost_summary?.device_payment?.toLocaleString() || 0 }}
                </dd>
              </div>
              <div class="flex justify-between items-center text-sm">
                <dt class="text-gray-600">違約金</dt>
                <dd class="font-semibold text-gray-900">
                  ${{ summary.cost_summary?.contract_breach_fee?.toLocaleString() || 0 }}
                </dd>
              </div>
              <div class="flex justify-between items-center text-sm">
                <dt class="text-gray-600">開通費</dt>
                <dd class="font-semibold text-gray-900">
                  ${{ summary.cost_summary?.activation_fee?.toLocaleString() || 0 }}
                </dd>
              </div>
              <div class="border-t-2 border-blue-300 pt-3 flex justify-between items-center">
                <dt class="text-lg font-bold text-gray-900">應付總額</dt>
                <dd class="text-2xl font-bold text-blue-600">
                  ${{ summary.total_amount?.toLocaleString() || 0 }}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 操作按鈕 -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex flex-col sm:flex-row gap-4 justify-between">
            <UButton
              color="gray"
              variant="outline"
              size="lg"
              :disabled="submitting"
              @click="goBack"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 mr-2" />
              返回修改
            </UButton>
            <UButton
              color="primary"
              size="lg"
              :loading="submitting"
              @click="handleSubmit"
            >
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5 mr-2" />
              確認提交申辦
            </UButton>
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
const config = useRuntimeConfig()
const { sessionId: authSessionId } = useAuth()
const { sessionId: renewalSessionId } = useRenewalWorkflow()

// 狀態
const loading = ref(true)
const error = ref<string | null>(null)
const submitting = ref(false)
const summary = ref<any>(null)

// 取得認證 Session ID
const getAuthSessionId = () => {
  if (authSessionId.value) {
    return authSessionId.value
  }
  if (process.client) {
    return localStorage.getItem('session_id')
  }
  return null
}

// 載入申辦摘要
const loadSummary = async () => {
  loading.value = true
  error.value = null

  try {
    if (!renewalSessionId.value) {
      throw new Error('缺少 Session ID')
    }

    const authSession = getAuthSessionId()
    if (!authSession) {
      throw new Error('請先登入')
    }

    const response = await $fetch('/api/renewal-workflow/step/confirm', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        'X-Session-ID': authSession
      },
      body: {
        session_id: renewalSessionId.value
      }
    }) as any

    if (response.success) {
      summary.value = response.summary
    } else {
      throw new Error(response.error || '載入申辦資料失敗')
    }
  } catch (err: any) {
    console.error('載入申辦摘要失敗:', err)
    error.value = err.message || '載入申辦資料失敗'
  } finally {
    loading.value = false
  }
}

// 提交申辦
const handleSubmit = async () => {
  if (!confirm('確認要提交申辦嗎？提交後將無法修改。')) {
    return
  }

  submitting.value = true
  error.value = null

  try {
    if (!renewalSessionId.value) {
      throw new Error('缺少 Session ID')
    }

    const authSession = getAuthSessionId()
    if (!authSession) {
      throw new Error('請先登入')
    }

    const response = await $fetch('/api/renewal-workflow/step/submit', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        'X-Session-ID': authSession
      },
      body: {
        session_id: renewalSessionId.value
      }
    }) as any

    if (response.success) {
      // 導向成功頁面
      await router.push({
        path: '/renewal/success',
        query: {
          order_number: response.order_number,
          total_amount: response.total_amount
        }
      })
    } else {
      throw new Error(response.error || '提交申辦失敗')
    }
  } catch (err: any) {
    console.error('提交申辦失敗:', err)
    error.value = err.message || '提交申辦失敗'
  } finally {
    submitting.value = false
  }
}

// 返回上一步 - 智能判斷返回到哪裡
const goBack = () => {
  const from = route.query.from as string
  
  // 根據來源參數決定返回位置
  if (from === 'compare-plans') {
    // 從比較方案頁面來的，返回方案列表頁（比較頁面依賴方案列表）
    // 用戶可以在方案列表重新選擇或進入比較
    router.push('/renewal/list-plans')
  } else if (from === 'list-plans') {
    // 從方案列表頁面來的，返回方案列表頁
    router.push('/renewal/list-plans')
  } else {
    // 沒有來源參數，預設返回方案列表頁
    // 這是最安全的選擇，讓用戶可以重新選擇方案
    router.push('/renewal/list-plans')
  }
}

// 頁面載入時取得申辦摘要
onMounted(() => {
  loadSummary()
})
</script>
