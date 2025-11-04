<!-- 
  這是一個示例文件，展示如何在 list-plans.vue 中添加「重選門號」按鈕
  實際修改時，請將此代碼段整合到 list-plans.vue 中
-->

<!-- ========================================
     OPTION 1: 簡單版本 - 只添加按鈕
     ======================================== -->

<template>
  <!-- Action Buttons -->
  <div v-if="!loading && !error" class="mt-8 flex justify-between items-center">
    <!-- 左側按鈕組 -->
    <div class="flex gap-3">
      <!-- 原有的返回按鈕 -->
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

      <!-- 【新增】重選門號按鈕 -->
      <UButton
        color="gray"
        variant="ghost"
        size="lg"
        :disabled="workflowLoading"
        @click="goBackToSelectPhone"
        class="text-blue-600 hover:text-blue-700"
      >
        <UIcon name="i-heroicons-phone" class="w-5 h-5 mr-2" />
        重選門號
      </UButton>
    </div>

    <!-- 右側按鈕組（原有的比較和下一步按鈕） -->
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
</template>

<script setup lang="ts">
// 在現有的 script 中添加以下代碼

const router = useRouter()

// 原有的返回功能
const goBack = () => {
  router.back()
}

// 【新增】直接返回到選擇門號頁面
const goBackToSelectPhone = () => {
  // 直接導航到 select-phone 頁面
  // 後端會自動處理：
  // 1. 接受從 list_plans 狀態訪問 select-phone API
  // 2. 清空所有 Step 4-10 的數據
  // 3. 重置狀態到 select_phone
  router.push('/renewal/select-phone')
}
</script>


<!-- ========================================
     OPTION 2: 完整版本 - 帶確認對話框
     ======================================== -->

<template>
  <!-- Action Buttons -->
  <div v-if="!loading && !error" class="mt-8 flex justify-between items-center">
    <div class="flex gap-3">
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
        color="gray"
        variant="ghost"
        size="lg"
        :disabled="workflowLoading"
        @click="showResetConfirm = true"
        class="text-blue-600 hover:text-blue-700"
      >
        <UIcon name="i-heroicons-phone" class="w-5 h-5 mr-2" />
        重選門號
      </UButton>
    </div>

    <div class="flex items-center gap-4">
      <!-- ... 原有的比較和下一步按鈕 ... -->
    </div>
  </div>

  <!-- 【新增】確認對話框 -->
  <UModal v-model="showResetConfirm">
    <div class="p-6">
      <div class="flex items-center gap-3 mb-4">
        <UIcon 
          name="i-heroicons-exclamation-triangle" 
          class="w-8 h-8 text-yellow-500" 
        />
        <h3 class="text-xl font-semibold">確認重選門號？</h3>
      </div>
      
      <p class="text-gray-600 mb-4">
        返回重選門號將會清空以下已選擇的內容：
      </p>
      
      <ul class="list-disc list-inside text-gray-600 mb-6 space-y-1 ml-4">
        <li>資格檢查結果</li>
        <li>設備類型和作業系統</li>
        <li>已選擇的設備 <span v-if="selectedDevice" class="text-sm text-gray-500">({{ selectedDevice.name }})</span></li>
        <li>已選擇的方案</li>
      </ul>
      
      <div class="flex justify-end gap-3">
        <UButton
          color="gray"
          variant="outline"
          @click="showResetConfirm = false"
        >
          取消
        </UButton>
        <UButton
          color="primary"
          @click="confirmReset"
        >
          確認重選
        </UButton>
      </div>
    </div>
  </UModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const router = useRouter()
const showResetConfirm = ref(false)

// 原有代碼...

// 【新增】顯示確認對話框
const goBackToSelectPhone = () => {
  showResetConfirm.value = true
}

// 【新增】確認重置並返回
const confirmReset = () => {
  showResetConfirm.value = false
  router.push('/renewal/select-phone')
}
</script>


<!-- ========================================
     OPTION 3: 極簡版本 - 只添加一行代碼
     ======================================== -->

<!-- 
如果不想改動太多，只需要在現有的返回按鈕旁邊添加：
-->

<UButton @click="router.push('/renewal/select-phone')" color="gray" variant="ghost">
  <UIcon name="i-heroicons-phone" class="w-5 h-5 mr-2" />
  重選門號
</UButton>

<!-- 
視覺效果：
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  [← 返回]  [📱 重選門號]                    [下一步 →]    │
│                                                            │
└────────────────────────────────────────────────────────────┘
-->
