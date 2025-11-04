/**
 * 認證中介軟體 - 確保使用者已登入
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const { checkAuth } = useAuth()
  
  try {
    const isAuthenticated = await checkAuth()
    
    if (!isAuthenticated) {
      // 未登入，重導向到登入頁面
      return navigateTo('/login')
    }
  } catch (error) {
    console.error('認證檢查錯誤:', error)
    return navigateTo('/login')
  }
})