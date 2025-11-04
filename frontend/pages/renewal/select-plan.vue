<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        選擇方案
      </h2>
      <p class="text-gray-600 mb-6">
        此功能將在 Sprint 3 實作
      </p>
      
      <div class="max-w-md mx-auto text-left mb-8 p-4 bg-gray-50 rounded-lg">
        <h3 class="font-semibold text-gray-900 mb-2">Sprint 3 功能預覽</h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li>• Step 5: 選擇續約類型（單純續約/搭配手機）</li>
          <li>• Step 6-7: 選擇裝置（品牌/型號/顏色/容量）</li>
          <li>• Step 8-9: 選擇資費方案並比較</li>
          <li>• Step 10: 確認訂單並送出</li>
        </ul>
      </div>
      
      <div class="flex justify-center gap-4">
        <UButton
          variant="outline"
          size="lg"
          @click="navigateTo('/renewal/eligibility')"
        >
          返回資格檢查
        </UButton>
        <UButton
          size="lg"
          @click="navigateTo('/')"
        >
          返回首頁
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 這個頁面是 Sprint 3 的佔位頁面
</script>
