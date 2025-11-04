/**
 * 認證相關的組合式函數
 */

// 類型定義
interface User {
  staff_id: string
  staff_code: string
  name: string
  role: string
  store_id: string
}

interface LoginCredentials {
  staff_code: string
  password: string
}

interface ChangePasswordData {
  old_password: string
  new_password: string
}

export const useAuth = () => {
  const user = useState<User | null>('auth.user', () => null)
  const sessionId = useState<string | null>('auth.sessionId', () => null)
  
  const config = useRuntimeConfig()
  
  /**
   * 登入
   */
  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await $fetch('/api/auth/login', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        body: credentials
      }) as any
      
      if (response.success) {
        // 儲存使用者資訊和 Session ID
        user.value = response.staff
        sessionId.value = response.session_id
        
        // 儲存到 localStorage
        if (process.client) {
          localStorage.setItem('session_id', response.session_id)
          localStorage.setItem('user', JSON.stringify(response.staff))
        }
        
        return response
      } else {
        throw new Error(response.error || '登入失敗')
      }
    } catch (error) {
      throw error
    }
  }
  
  /**
   * 登出
   */
  const logout = async () => {
    try {
      if (sessionId.value) {
        await $fetch('/api/auth/logout', {
          method: 'POST',
          baseURL: config.public.apiBaseUrl,
          headers: {
            'X-Session-ID': sessionId.value
          }
        })
      }
      
      // 清除本地資料
      user.value = null
      sessionId.value = null
      
      if (process.client) {
        localStorage.removeItem('session_id')
        localStorage.removeItem('user')
        // 清除續約工作流相關資料
        localStorage.removeItem('renewal_session_id')
      }
      
    } catch (error) {
      console.error('登出錯誤:', error)
      // 即使請求失敗也要清除本地資料
      user.value = null
      sessionId.value = null
      
      if (process.client) {
        localStorage.removeItem('session_id')
        localStorage.removeItem('user')
        // 清除續約工作流相關資料
        localStorage.removeItem('renewal_session_id')
      }
    }
  }
  
  /**
   * 初始化認證狀態
   */
  const initAuth = async () => {
    if (process.client) {
      const storedSessionId = localStorage.getItem('session_id')
      const storedUser = localStorage.getItem('user')
      
      if (storedSessionId && storedUser) {
        sessionId.value = storedSessionId
        user.value = JSON.parse(storedUser)
        
        // 驗證 Session 是否還有效
        try {
          const response = await $fetch('/api/auth/me', {
            method: 'GET',
            baseURL: config.public.apiBaseUrl,
            headers: {
              'X-Session-ID': storedSessionId
            }
          }) as any
          
          if (response.success) {
            user.value = response.user
          } else {
            // Session 無效，清除本地資料
            await logout()
          }
        } catch (error) {
          // Session 驗證失敗，清除本地資料
          await logout()
        }
      }
    }
  }
  
  /**
   * 取得當前使用者資訊
   */
  const getCurrentUser = async () => {
    if (!sessionId.value) {
      throw new Error('未登入')
    }
    
    try {
      const response = await $fetch('/api/auth/me', {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': sessionId.value
        }
      }) as any
      
      if (response.success) {
        user.value = response.user
        return response.user
      } else {
        throw new Error(response.error || '取得使用者資訊失敗')
      }
    } catch (error) {
      throw error
    }
  }
  
  /**
   * 變更密碼
   */
  const changePassword = async (passwords: ChangePasswordData) => {
    try {
      if (!sessionId.value) {
        throw new Error('未登入')
      }
      
      const response = await $fetch('/api/auth/change-password', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': sessionId.value
        },
        body: passwords
      }) as any
      
      if (response.success) {
        return response
      } else {
        throw new Error(response.error || '變更密碼失敗')
      }
    } catch (error) {
      throw error
    }
  }
  
  /**
   * 檢查認證狀態
   */
  const checkAuth = async (): Promise<boolean> => {
    try {
      // 如果已經有使用者資訊和 Session ID，先檢查本地狀態
      if (user.value && sessionId.value) {
        return true
      }
      
      // 嘗試從 localStorage 恢復 Session
      if (process.client) {
        const storedSessionId = localStorage.getItem('session_id')
        const storedUser = localStorage.getItem('user')
        
        if (storedSessionId && storedUser) {
          // 向後端驗證 Session 是否仍然有效
          const response = await $fetch('/api/auth/me', {
            method: 'GET',
            baseURL: config.public.apiBaseUrl,
            headers: {
              'X-Session-ID': storedSessionId
            }
          }) as any
          
          if (response.success && response.staff) {
            // Session 有效，恢復使用者狀態
            user.value = response.staff
            sessionId.value = storedSessionId
            return true
          } else {
            // Session 無效，清除本地儲存
            localStorage.removeItem('session_id')
            localStorage.removeItem('user')
            user.value = null
            sessionId.value = null
            return false
          }
        }
      }
      
      return false
    } catch (error) {
      console.error('認證檢查失敗:', error)
      
      // 清除可能無效的本地狀態
      if (process.client) {
        localStorage.removeItem('session_id')
        localStorage.removeItem('user')
      }
      user.value = null
      sessionId.value = null
      
      return false
    }
  }
  
  /**
   * 檢查是否為管理員
   */
  const isManager = computed(() => {
    return user.value?.role === 'Manager' || user.value?.role === 'Admin'
  })
  
  /**
   * 檢查是否為系統管理員
   */
  const isAdmin = computed(() => {
    return user.value?.role === 'Admin'
  })
  
  return {
    user: readonly(user),
    sessionId: readonly(sessionId),
    isLoggedIn: computed(() => !!user.value && !!sessionId.value),
    isManager,
    isAdmin,
    login,
    logout,
    initAuth,
    getCurrentUser,
    changePassword,
    checkAuth
  }
}