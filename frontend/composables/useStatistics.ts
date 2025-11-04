/**
 * 統計相關的組合式函數
 */
export const useStatistics = () => {
  const { sessionId } = useAuth()
  const config = useRuntimeConfig()
  
  // 響應式資料
  const stats = reactive({
    todayCustomers: 0,
    todaySales: 0,
    conversionRate: 0,
    thisWeek: {
      customers: 0,
      sales: 0,
      aiUsage: 0
    }
  })
  
  const recentRecords = ref([])
  const loading = ref(false)
  
  /**
   * 取得當日統計
   */
  const fetchDailyStats = async () => {
    try {
      const response = await $fetch('/api/statistics/daily-stats', {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': sessionId.value || ''
        }
      }) as any
      
      if (response.success) {
        Object.assign(stats, response.data)
      }
      
      return response.data
    } catch (error) {
      console.error('取得統計資料錯誤:', error)
      throw error
    }
  }
  
  /**
   * 取得個人儀表板資料
   */
  const fetchDashboardData = async () => {
    loading.value = true
    
    try {
      const response = await $fetch('/api/statistics/my-dashboard', {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': sessionId.value || ''
        }
      }) as any
      
      if (response.success) {
        // 更新統計資料
        Object.assign(stats, response.data)
        
        // 更新最近記錄
        recentRecords.value = response.data.recentRecords || []
      }
      
      return response.data
    } catch (error) {
      console.error('取得儀表板資料錯誤:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 取得門市排行榜
   */
  const fetchStoreRankings = async () => {
    try {
      const response = await $fetch('/api/statistics/store-rankings', {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': sessionId.value || ''
        }
      }) as any
      
      if (response.success) {
        return response.data
      } else {
        throw new Error(response.error || '取得排行榜失敗')
      }
    } catch (error) {
      console.error('取得排行榜錯誤:', error)
      throw error
    }
  }
  
  return {
    stats: readonly(stats),
    recentRecords: readonly(recentRecords),
    loading: readonly(loading),
    fetchDailyStats,
    fetchDashboardData,
    fetchStoreRankings
  }
}