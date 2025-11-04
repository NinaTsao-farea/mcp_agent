/**
 * 訪客中介軟體 - 確保只有未登入使用者能訪問
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const { checkAuth } = useAuth()
  
  try {
    const isAuthenticated = await checkAuth()
    
    if (isAuthenticated) {
      // 已登入，重導向到首頁
      return navigateTo('/')
    }
  } catch (error) {
    // 發生錯誤時允許訪問登入頁面
    console.error('認證檢查錯誤:', error)
  }
})