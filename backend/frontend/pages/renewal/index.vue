<template>
  <div>
    <!-- 這個頁面會自動重定向到第一步 -->
  </div>
</template>

<script setup lang="ts">
// 頁面設定
definePageMeta({
  middleware: 'auth'
})

// 清空舊的 session，開始新的流程
const { clearWorkflow } = useRenewalWorkflow()

onMounted(() => {
  // 清空舊流程
  clearWorkflow()
  
  // 重定向到查詢客戶頁面
  navigateTo('/renewal/query-customer', { replace: true })
})
</script>