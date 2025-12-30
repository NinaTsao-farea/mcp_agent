<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-6">
      <!-- 主要內容區域 -->
      <div class="flex-1 max-w-7xl">
      <!-- Breadcrumb -->
      <nav class="mb-6">
        <ol class="flex items-center space-x-2 text-sm text-gray-500">
          <li>
            <NuxtLink to="/renewal/start" class="hover:text-primary-600 transition-colors">
              續約流程
            </NuxtLink>
          </li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li>
            <NuxtLink to="/renewal/select-phone" class="hover:text-primary-600 transition-colors">
              資格檢查
            </NuxtLink>
          </li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li>
            <NuxtLink to="/renewal/select-device-type" class="hover:text-primary-600 transition-colors">
              選擇續約方式
            </NuxtLink>
          </li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li>
            <NuxtLink to="/renewal/select-device-os" class="hover:text-primary-600 transition-colors">
              選擇作業系統
            </NuxtLink>
          </li>
          <li><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></li>
          <li class="text-primary-600 font-medium">選擇裝置</li>
        </ol>
      </nav>

      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">選擇裝置</h1>
        <p class="text-gray-600">為客戶挑選合適的裝置</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <i class="i-heroicons-arrow-path-solid w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
        <p class="text-gray-600">載入裝置列表中...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <i class="i-heroicons-x-circle-solid w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-red-900 mb-2">載入失敗</h3>
        <p class="text-red-700 mb-4">{{ error }}</p>
        <UButton color="red" variant="outline" @click="loadDevices">重試</UButton>
      </div>

      <!-- Device List -->
      <div v-else>
        <!-- Filter Bar -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center gap-4">
          <div class="flex items-center gap-2">
            <i class="i-heroicons-funnel-solid w-5 h-5 text-gray-500" />
            <span class="text-sm font-medium text-gray-700">篩選：</span>
          </div>
          <USelect
            v-model="selectedBrand"
            :options="brandOptions"
            placeholder="所有品牌"
            class="w-48"
          />
          <USelect
            v-model="selectedPriceRange"
            :options="priceRangeOptions"
            placeholder="所有價格"
            class="w-48"
          />
          <div class="ml-auto text-sm text-gray-600">
            共 <span class="font-semibold text-primary-600">{{ filteredDevices.length }}</span> 款裝置
          </div>
        </div>

        <!-- Device Cards Grid -->
        <div v-if="filteredDevices.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="device in filteredDevices"
            :key="device.device_id"
            class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden cursor-pointer border-2"
            :class="{
              'border-primary-500 ring-2 ring-primary-200': selectedDevice?.device_id === device.device_id,
              'border-gray-200 hover:border-gray-300': selectedDevice?.device_id !== device.device_id
            }"
            @click="selectDeviceCard(device)"
          >
            <!-- Device Image -->
            <div class="relative bg-gradient-to-br from-gray-50 to-gray-100 p-6 flex items-center justify-center h-64">
              <img
                :src="device.image_url || '/images/device-placeholder.png'"
                :alt="device.model"
                class="max-h-full max-w-full object-contain"
              />
              <!-- Recommended Badge -->
              <div
                v-if="device.is_recommended"
                class="absolute top-4 right-4 bg-primary-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1"
              >
                <i class="i-heroicons-star-solid w-4 h-4" />
                推薦
              </div>
              <!-- Stock Badge -->
              <div
                class="absolute bottom-4 left-4 px-3 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-green-100 text-green-700': device.stock_status === 'in_stock',
                  'bg-yellow-100 text-yellow-700': device.stock_status === 'low_stock',
                  'bg-red-100 text-red-700': device.stock_status === 'out_of_stock'
                }"
              >
                {{ stockStatusText(device.stock_status) }}
              </div>
            </div>

            <!-- Device Info -->
            <div class="p-6">
              <!-- Brand & Model -->
              <div class="mb-3">
                <p class="text-sm text-gray-500 mb-1">{{ device.brand }}</p>
                <h3 class="text-lg font-bold text-gray-900">{{ device.model }}</h3>
              </div>

              <!-- Specs -->
              <div class="space-y-2 mb-4">
                <div class="flex items-center gap-2 text-sm text-gray-600">
                  <i class="i-heroicons-cpu-chip-solid w-4 h-4" />
                  <span>{{ device.processor || 'N/A' }}</span>
                </div>
                <div class="flex items-center gap-2 text-sm text-gray-600">
                  <i class="i-heroicons-circle-stack-solid w-4 h-4" />
                  <span>{{ device.storage || 'N/A' }}</span>
                </div>
                <div class="flex items-center gap-2 text-sm text-gray-600">
                  <i class="i-heroicons-device-phone-mobile-solid w-4 h-4" />
                  <span>{{ device.screen_size || 'N/A' }}</span>
                </div>
              </div>

              <!-- Colors -->
              <div v-if="device.colors && device.colors.length > 0" class="mb-4">
                <p class="text-xs text-gray-500 mb-2">可選顏色：</p>
                <div class="flex gap-2">
                  <div
                    v-for="color in device.colors"
                    :key="color"
                    class="w-6 h-6 rounded-full border-2 border-gray-300"
                    :style="{ backgroundColor: getColorCode(color) }"
                    :title="color"
                  />
                </div>
              </div>

              <!-- Price -->
              <div class="flex items-end justify-between pt-4 border-t border-gray-200">
                <div>
                  <p class="text-xs text-gray-500">專案價</p>
                  <p class="text-2xl font-bold text-primary-600">
                    NT$ {{ device.contract_price?.toLocaleString() || '0' }}
                  </p>
                  <p v-if="device.original_price" class="text-xs text-gray-400 line-through">
                    NT$ {{ device.original_price.toLocaleString() }}
                  </p>
                </div>
                <!-- Selection Indicator -->
                <div v-if="selectedDevice?.device_id === device.device_id" class="flex items-center">
                  <i class="i-heroicons-check-circle-solid w-8 h-8 text-primary-500" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="bg-white rounded-lg shadow-sm p-12 text-center">
          <i class="i-heroicons-device-phone-mobile-solid w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">暫無符合條件的裝置</h3>
          <p class="text-gray-600">請嘗試調整篩選條件</p>
        </div>
      </div>

      <!-- Color Selection Modal (if device selected) -->
      <UModal v-model="showColorModal">
        <div class="p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-4">選擇顏色</h3>
          <p class="text-gray-600 mb-6">
            您選擇了 <span class="font-semibold">{{ selectedDevice?.brand }} {{ selectedDevice?.model }}</span>
          </p>
          
          <div class="space-y-3 mb-6">
            <div
              v-for="color in selectedDevice?.colors || []"
              :key="color"
              class="flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all"
              :class="{
                'border-primary-500 bg-primary-50': selectedColor === color,
                'border-gray-200 hover:border-gray-300': selectedColor !== color
              }"
              @click="selectedColor = color"
            >
              <div
                class="w-8 h-8 rounded-full border-2 border-gray-300"
                :style="{ backgroundColor: getColorCode(color) }"
              />
              <span class="font-medium text-gray-900">{{ color }}</span>
              <i
                v-if="selectedColor === color"
                class="i-heroicons-check-circle-solid w-5 h-5 text-primary-500 ml-auto"
              />
            </div>
          </div>

          <div class="flex justify-between gap-3">
            <UButton color="gray" variant="outline" block @click="showColorModal = false" class="flex-1">
              取消
            </UButton>
            <UButton
              color="primary"
              block
              :disabled="!selectedColor || workflowLoading"
              :loading="workflowLoading"
              @click="confirmSelection"
              class="flex-1"
            >
              確認選擇
            </UButton>
          </div>
        </div>
      </UModal>

      <!-- Action Buttons -->
      <div v-if="!loading && !error" class="mt-8 flex justify-between">
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
          color="primary"
          size="lg"
          :disabled="!selectedDevice || workflowLoading"
          :loading="workflowLoading"
          @click="handleNext"
        >
          <span>下一步</span>
          <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 ml-2" />
        </UButton>
      </div>
      </div>
      
      <!-- AI 聊天框側邊欄 -->
      <div class="w-96 flex-shrink-0">
        <div class="sticky top-8">
          <AIChatBox 
            v-if="sessionId"
            :session-id="sessionId"
            :page-context="pageContext"
            :disabled="workflowLoading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const router = useRouter()

const { sessionId, queryDevices, selectDevice, loading: workflowLoading, error: workflowError } = useRenewalWorkflow()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const devices = ref<any[]>([])
const selectedDevice = ref<any | null>(null)
const selectedColor = ref<string | null>(null)
const showColorModal = ref(false)

// Filters
const selectedBrand = ref<string>('all')
const selectedPriceRange = ref<string>('all')

// Options
const brandOptions = computed(() => {
  const brands = ['all', ...new Set(devices.value.map(d => d.brand))]
  return brands.map(b => ({ value: b, label: b === 'all' ? '所有品牌' : b }))
})

const priceRangeOptions = [
  { value: 'all', label: '所有價格' },
  { value: 'low', label: 'NT$ 20,000 以下' },
  { value: 'mid', label: 'NT$ 20,000 - 35,000' },
  { value: 'high', label: 'NT$ 35,000 以上' }
]

// Computed
const filteredDevices = computed(() => {
  let filtered = devices.value

  // Filter by brand
  if (selectedBrand.value !== 'all') {
    filtered = filtered.filter(d => d.brand === selectedBrand.value)
  }

  // Filter by price range
  if (selectedPriceRange.value !== 'all') {
    filtered = filtered.filter(d => {
      const price = d.contract_price
      if (selectedPriceRange.value === 'low') return price < 20000
      if (selectedPriceRange.value === 'mid') return price >= 20000 && price <= 35000
      if (selectedPriceRange.value === 'high') return price > 35000
      return true
    })
  }

  return filtered
})

// 生成頁面上下文給 AI
const pageContext = computed(() => {
  if (filteredDevices.value.length === 0) {
    return '目前頁面：選擇裝置\n\n暫無可用的裝置資料。'
  }
  
  const deviceList = filteredDevices.value.map((device, index) => {
    return `${index + 1}. ${device.brand} ${device.model}
   - 作業系統: ${device.os}
   - 處理器: ${device.processor}
   - 儲存空間: ${device.storage}
   - 螢幕尺寸: ${device.screen_size}
   - 專案價: NT$ ${device.contract_price?.toLocaleString()}
   - 原價: NT$ ${device.original_price?.toLocaleString()}
   - 庫存狀態: ${stockStatusText(device.stock_status)}
   - 可用庫存: ${device.available} 台`
  }).join('\n\n')
  
  return `目前頁面：選擇裝置
當前篩選條件：品牌=${selectedBrand.value === 'all' ? '全部' : selectedBrand.value}, 價格範圍=${selectedPriceRange.value === 'all' ? '全部' : selectedPriceRange.value}

以下是目前顯示的 ${filteredDevices.value.length} 款裝置清單：

${deviceList}

---
請根據以上裝置清單回答用戶的問題。`
})

// Methods
const loadDevices = async () => {
  loading.value = true
  error.value = null
  
  if (!sessionId.value) {
    error.value = '找不到 session，請重新開始流程'
    loading.value = false
    return
  }
  
  try {
    console.log('Loading devices with session_id:', sessionId.value)
    
    // 使用 composable 方法呼叫 API
    const response = await queryDevices('STORE001')
    
    console.log('API Response:', response)
    
    if (response.success && response.devices) {
      // 將後端資料結構映射到前端需要的格式
      devices.value = response.devices.map((device: any) => ({
        device_id: device.device_id,
        brand: device.brand,
        model: device.model,
        os: device.os,
        processor: device.chip || 'N/A',
        storage: device.storage,
        screen_size: device.screen_size,
        colors: [device.color], // 後端每個設備是單一顏色，前端包裝成陣列
        contract_price: device.price,
        original_price: device.market_price,
        stock_status: device.available > 5 ? 'in_stock' : device.available > 0 ? 'low_stock' : 'out_of_stock',
        is_recommended: device.available > 10, // 庫存充足的設為推薦
        image_url: `/images/${device.brand.toLowerCase()}-${device.model.toLowerCase().replace(/\s+/g, '-')}.jpg`,
        available: device.available,
        total_quantity: device.total_quantity
      }))
      console.log(devices.value)
    } else {
      error.value = response.error || '載入裝置列表失敗'
    }
  } catch (err: any) {
    error.value = err.message || workflowError.value || '載入裝置列表失敗，請稍後再試'
    console.error('Load devices error:', err)
  } finally {
    loading.value = false
  }
}

const stockStatusText = (status: string) => {
  const map: Record<string, string> = {
    in_stock: '有貨',
    low_stock: '庫存不足',
    out_of_stock: '缺貨'
  }
  return map[status] || '未知'
}

const getColorCode = (colorName: string) => {
  const colorMap: Record<string, string> = {
    '黑色': '#000000',
    '白色': '#FFFFFF',
    '灰色': '#808080',
    '藍色': '#0066CC',
    '粉色': '#FF69B4',
    '黃色': '#FFD700',
    '綠色': '#00AA00',
    '紫色': '#9966CC',
    '鈦金色': '#C0C0C0',
    '紅色': '#CC0000'
  }
  return colorMap[colorName] || '#CCCCCC'
}

const selectDeviceCard = (device: any) => {
  if (device.stock_status === 'out_of_stock') {
    return // Cannot select out of stock device
  }
  
  selectedDevice.value = device
  
  // 自動設定顏色（後端每個設備只有單一顏色）
  if (device.colors && device.colors.length > 0) {
    selectedColor.value = device.colors[0]
  }
}

const handleNext = async () => {
  if (!selectedDevice.value) return
  await confirmSelection()
}

const confirmSelection = async () => {
  if (!selectedDevice.value) return
  
  try {
    // 使用設備的顏色，如果沒有則使用預設
    const color = selectedColor.value || (selectedDevice.value.colors && selectedDevice.value.colors[0]) || '預設'
    await selectDevice(selectedDevice.value.device_id, color)
    
    // Navigate to next step
    navigateTo('/renewal/list-plans')
  } catch (err) {
    console.error('Select device error:', err)
  }
}

// 返回上一步
const goBack = () => {
  // Step 7 select-device 的上一步固定是 Step 6 select-device-os
  navigateTo('/renewal/select-device-os')
}

// Lifecycle
onMounted(() => {
  if (!sessionId.value) {
    navigateTo('/renewal/start')
    return
  }
  
  loadDevices()
})
</script>
