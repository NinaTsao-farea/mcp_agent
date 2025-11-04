<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold text-gray-900 mb-2">
      查詢客戶資料
    </h2>
    <p class="text-sm text-gray-600 mb-6">
      請輸入客戶身分證號以開始續約流程
    </p>
    
    <div class="max-w-md">
      <UFormGroup label="身分證號" :error="error">
        <UInput
          v-model="idNumber"
          placeholder="例：A123456789"
          size="lg"
          :disabled="loading"
          @keyup.enter="handleQueryCustomer"
        />
      </UFormGroup>
      
      <div class="mt-6 flex gap-4">
        <UButton
          @click="handleQueryCustomer"
          :loading="loading"
          :disabled="!idNumber || loading"
          size="lg"
        >
          查詢客戶
        </UButton>
        
        <!-- 測試資料提示 -->
        <UButton
          variant="ghost"
          @click="fillTestData"
          size="lg"
        >
          使用測試資料
        </UButton>
      </div>
      
      <!-- 測試帳號提示 -->
      <div class="mt-4 p-4 bg-blue-50 rounded-lg">
        <p class="text-xs text-blue-900 font-semibold mb-2">測試身分證號</p>
        <ul class="text-xs text-blue-800 space-y-1">
          <li>• A123456789 - 張三 (2個門號，1個即將到期)</li>
          <li>• B987654321 - 李四 (1個門號，即將到期)</li>
          <li>• C111222333 - 王五 (非本公司客戶)</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Composables
const {
  sessionId,
  loading,
  error,
  startWorkflow,
  queryCustomer,
  listPhones
} = useRenewalWorkflow()

// 狀態
const idNumber = ref('')

// 方法
const fillTestData = () => {
  idNumber.value = 'A123456789'
}

const handleQueryCustomer = async () => {
  if (!idNumber.value) return
  
  try {
    // 如果還沒有 session，先開始流程
    if (!sessionId.value) {
      console.log('開始新的續約流程...')
      await startWorkflow()
      console.log('續約流程已開始，session_id:', sessionId.value)
    }
    
    // 查詢客戶
    console.log('查詢客戶:', idNumber.value)
    const customerResult = await queryCustomer(idNumber.value)
    
    // 檢查是否成功
    if (!customerResult || !customerResult.success) {
      console.error('查詢客戶失敗，不繼續取得門號')
      return
    }
    
    // 自動取得門號列表
    console.log('取得門號列表...')
    await listPhones()
    
    // 導航到選擇門號頁面
    navigateTo('/renewal/select-phone')
  } catch (err: any) {
    console.error('查詢客戶失敗:', err)
  }
}
</script>
