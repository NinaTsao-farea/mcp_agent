<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900">
          電信門市銷售助理系統
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          請輸入您的員工編號和密碼登入
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="handleLogin" class="space-y-6">
          
          <!-- 員工編號 -->
          <div>
            <label for="staff_code" class="label">
              員工編號
            </label>
            <div class="mt-1">
              <UInput
                id="staff_code"
                v-model="form.staffCode"
                type="text"
                placeholder="請輸入員工編號"
                required
                :disabled="loading"
              />
            </div>
          </div>

          <!-- 密碼 -->
          <div>
            <label for="password" class="label">
              密碼
            </label>
            <div class="mt-1">
              <UInput
                id="password"
                v-model="form.password"
                type="password"
                placeholder="請輸入密碼"
                required
                :disabled="loading"
              />
            </div>
          </div>

          <!-- 錯誤訊息 -->
          <div v-if="error" class="text-sm text-red-600">
            {{ error }}
          </div>

          <!-- 登入按鈕 -->
          <div>
            <UButton
              type="submit"
              block
              :loading="loading"
              :disabled="loading"
            >
              {{ loading ? '登入中...' : '登入' }}
            </UButton>
          </div>
        </form>
        
        <div class="mt-6">
          <div class="text-center text-sm text-gray-500">
            <p>測試帳號：S001 / password</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 頁面設定
definePageMeta({
  middleware: 'guest', // 只有未登入使用者能訪問
  layout: false // 不使用預設佈局
})

// 組合式函數
const { login } = useAuth()

// 響應式資料
const form = reactive({
  staffCode: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

// 方法
const handleLogin = async () => {
  if (loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    // 驗證輸入
    if (!form.staffCode.trim()) {
      throw new Error('請輸入員工編號')
    }
    
    if (!form.password.trim()) {
      throw new Error('請輸入密碼')
    }
    
    // 執行登入
    await login({
      staff_code: form.staffCode.trim(),
      password: form.password.trim()
    })
    
    // 登入成功，重導向到首頁
    await navigateTo('/')
    
  } catch (err) {
    error.value = err.message || '登入失敗，請檢查員工編號和密碼'
    console.error('登入錯誤:', err)
  } finally {
    loading.value = false
  }
}

// 自動對焦到員工編號欄位
onMounted(() => {
  nextTick(() => {
    const staffCodeInput = document.getElementById('staff_code')
    if (staffCodeInput) {
      staffCodeInput.focus()
    }
  })
})
</script>