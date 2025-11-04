/**
 * 續約工作流程 Composable
 */

// 類型定義
export interface Customer {
  customer_id: string
  name: string
  phone: string
  email?: string
  is_company_customer: boolean
}

export interface PhoneContract {
  phone_number: string
  plan_name: string
  monthly_fee: number
  data_limit: string
  contract_start_date: string
  contract_end_date: string
  is_primary: boolean
  status: string
  contract?: any
  usage?: any
  billing?: any
}

export interface EligibilityCheck {
  eligible: boolean
  reason: string
  details: Array<{
    item: string
    status: 'pass' | 'fail'
    message: string
  }>
  contract_end_date?: string
  days_to_expiry?: number
}

export interface WorkflowSession {
  session_id: string
  staff_id: string
  current_step: string
  customer_selection: {
    id_number?: string
    customer_id?: string
    customer_name?: string
    customer_phone?: string
    selected_phone_number?: string
    eligibility_check?: EligibilityCheck
  }
  created_at: string
  updated_at: string
}

export const useRenewalWorkflow = () => {
  // 狀態
  const sessionId = useState<string | null>('renewal.sessionId', () => null)
  const currentStep = useState<string>('renewal.currentStep', () => 'init')
  const customer = useState<Customer | null>('renewal.customer', () => null)
  const phones = useState<PhoneContract[]>('renewal.phones', () => [])
  const selectedPhone = useState<PhoneContract | null>('renewal.selectedPhone', () => null)
  const eligibilityCheck = useState<EligibilityCheck | null>('renewal.eligibilityCheck', () => null)
  
  const loading = useState<boolean>('renewal.loading', () => false)
  const error = useState<string | null>('renewal.error', () => null)
  
  const config = useRuntimeConfig()
  const { sessionId: authSessionId } = useAuth()
  
  /**
   * 獲取認證 Session ID
   */
  const getAuthSessionId = () => {
    // 優先從 composable 獲取
    if (authSessionId.value) {
      return authSessionId.value
    }
    
    // 從 localStorage 獲取
    if (process.client) {
      return localStorage.getItem('session_id')
    }
    
    return null
  }
  
  /**
   * 開始續約流程
   */
  const startWorkflow = async () => {
    loading.value = true
    error.value = null
    
    try {
      const authSession = getAuthSessionId()
      
      if (!authSession) {
        throw new Error('請先登入')
      }
      console.log("authSession",authSession)
      console.log("config.public.apiBaseUrl",config.public.apiBaseUrl)
      console.log('Session ID:', localStorage.getItem('session_id'))
      console.log('User:', localStorage.getItem('user'))
      
      const response = await $fetch('/api/renewal-workflow/start', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        }
      }) as any
      
      if (response.success) {
        sessionId.value = response.session_id
        currentStep.value = response.current_step
        
        // 儲存到 localStorage
        if (process.client) {
          localStorage.setItem('renewal_session_id', response.session_id)
        }
        
        return response
      } else {
        throw new Error(response.error || '開始流程失敗')
      }
    } catch (err: any) {
      error.value = err.message || '開始流程失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 1: 查詢客戶
   */
  const queryCustomer = async (idNumber: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        error.value = '請先開始流程'
        return { success: false, error: '請先開始流程' }
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        error.value = '請先登入'
        return { success: false, error: '請先登入' }
      }
      
      const response = await $fetch('/api/renewal-workflow/step/query-customer', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          id_number: idNumber
        }
      }) as any
      
      if (response.success) {
        customer.value = response.customer
        currentStep.value = 'list_phones'
        error.value = null
        return response
      } else {
        // API 返回錯誤，設置錯誤訊息但不拋出異常
        const errorMessage = response.message || response.error || '查詢客戶失敗'
        error.value = errorMessage
        return response
      }
    } catch (err: any) {
      // 網絡錯誤或其他異常
      const errorMessage = err.data?.message || err.data?.error || err.message || '查詢客戶失敗'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 2-3: 列出門號
   */
  const listPhones = async () => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/list-phones', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value
        }
      }) as any
      
      if (response.success) {
        phones.value = response.phones
        currentStep.value = 'select_phone'
        return response
      } else {
        throw new Error(response.error || '取得門號列表失敗')
      }
    } catch (err: any) {
      error.value = err.message || '取得門號列表失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 4: 選擇門號並檢查資格
   */
  const selectPhone = async (phoneNumber: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/select-phone', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          phone_number: phoneNumber
        }
      }) as any
      
      // 從 phones 中找到選中的門號
      selectedPhone.value = phones.value.find(p => p.phone_number === phoneNumber) || null
      
      if (response.success) {
        // 資格檢查通過
        eligibilityCheck.value = response.eligibility
        currentStep.value = 'select_device_type'
        error.value = null
        return response
      } else {
        // 資格檢查不通過，設置資格檢查結果但不拋出異常
        eligibilityCheck.value = response.eligibility
        // 不符合資格時也算是成功獲取了資格檢查結果，只是結果是不通過
        // 不設置 error，讓 UI 根據 eligibilityCheck 顯示詳細信息
        return response
      }
    } catch (err: any) {
      // 網絡錯誤或其他異常
      const errorMessage = err.data?.message || err.data?.error || err.message || '檢查資格失敗'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 取得 Session 資料
   */
  const getSession = async () => {
    if (!sessionId.value) return null
    
    try {
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch(`/api/renewal-workflow/session/${sessionId.value}`, {
        method: 'GET',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        }
      }) as any
      
      if (response.success) {
        return response.session as WorkflowSession
      }
      return null
    } catch (err) {
      console.error('取得 Session 失敗:', err)
      return null
    }
  }
  
  /**
   * 清除選擇狀態（返回門號列表）
   */
  const clearSelection = () => {
    selectedPhone.value = null
    eligibilityCheck.value = null
    error.value = null
  }
  
  /**
   * 清除流程狀態
   */
  const clearWorkflow = async () => {
    if (sessionId.value) {
      try {
        const authSession = getAuthSessionId()
        
        if (authSession) {
          await $fetch(`/api/renewal-workflow/session/${sessionId.value}`, {
            method: 'DELETE',
            baseURL: config.public.apiBaseUrl,
            headers: {
              'X-Session-ID': authSession
            }
          })
        }
      } catch (err) {
        console.error('刪除 Session 失敗:', err)
      }
    }
    
    // 清除狀態
    sessionId.value = null
    currentStep.value = 'init'
    customer.value = null
    phones.value = []
    selectedPhone.value = null
    eligibilityCheck.value = null
    error.value = null
    
    // 清除 localStorage
    if (process.client) {
      localStorage.removeItem('renewal_session_id')
    }
  }
  
  /**
   * 從 localStorage 恢復 Session
   */
  const restoreSession = async () => {
    if (process.client) {
      const storedSessionId = localStorage.getItem('renewal_session_id')
      
      if (storedSessionId) {
        sessionId.value = storedSessionId
        
        // 嘗試取得 Session 資料
        const session = await getSession()
        
        if (session) {
          currentStep.value = session.current_step
          
          // 恢復客戶資料
          if (session.customer_selection.customer_id) {
            customer.value = {
              customer_id: session.customer_selection.customer_id,
              name: session.customer_selection.customer_name || '',
              phone: session.customer_selection.customer_phone || '',
              is_company_customer: true
            }
          }
          
          return true
        } else {
          // Session 無效，清除
          await clearWorkflow()
          return false
        }
      }
    }
    
    return false
  }
  
  /**
   * Step 5: 選擇裝置類型
   */
  const selectDeviceType = async (deviceType: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/select-device-type', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          device_type: deviceType
        }
      }) as any
      
      if (response.success) {
        currentStep.value = response.next_step
        return response
      } else {
        throw new Error(response.error || '選擇裝置類型失敗')
      }
    } catch (err: any) {
      error.value = err.message || '選擇裝置類型失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 6: 選擇裝置作業系統
   */
  const selectDeviceOS = async (osType: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/select-device-os', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          os_type: osType.toLowerCase()
        }
      }) as any
      
      if (response.success) {
        currentStep.value = response.next_step
        return response
      } else {
        throw new Error(response.error || '選擇作業系統失敗')
      }
    } catch (err: any) {
      error.value = err.message || '選擇作業系統失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 7: 查詢可用設備
   */
  const queryDevices = async (storeId: string = 'STORE001') => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/query-devices', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          store_id: storeId
        }
      }) as any
      
      if (response.success) {
        return response
      } else {
        throw new Error(response.error || '查詢設備失敗')
      }
    } catch (err: any) {
      error.value = err.message || '查詢設備失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 8: 列出可選方案
   */
  const listPlans = async () => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/list-plans', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value
        }
      }) as any
      
      if (response.success) {
        return response
      } else {
        throw new Error(response.error || '取得方案列表失敗')
      }
    } catch (err: any) {
      error.value = err.message || '取得方案列表失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 8.5: 選擇方案
   */
  const selectPlan = async (planId: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      if (!planId) {
        throw new Error('請選擇方案')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/select-plan', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          plan_id: planId
        }
      }) as any
      
      if (response.success) {
        currentStep.value = response.next_step
        return response
      } else {
        throw new Error(response.error || '選擇方案失敗')
      }
    } catch (err: any) {
      error.value = err.message || '選擇方案失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Step 9: 比較方案
   */
  const comparePlans = async (planIds: string[]) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      if (!planIds || planIds.length < 2) {
        throw new Error('請至少選擇 2 個方案進行比較')
      }
      
      if (planIds.length > 4) {
        throw new Error('最多只能比較 4 個方案')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/compare-plans', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          plan_ids: planIds
        }
      }) as any
      
      if (response.success) {
        return response
      } else {
        throw new Error(response.error || '比較方案失敗')
      }
    } catch (err: any) {
      error.value = err.message || '比較方案失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 7: 選擇設備
   */
  const selectDevice = async (deviceId: string, color?: string) => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/select-device', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value,
          device_id: deviceId,
          color: color || '預設'
        }
      }) as any
      
      if (response.success) {
        currentStep.value = response.next_step
        return response
      } else {
        throw new Error(response.error || '選擇設備失敗')
      }
    } catch (err: any) {
      error.value = err.message || '選擇設備失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 10: 確認申辦 - 取得完整申辦摘要
   */
  const confirmApplication = async () => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/confirm', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value
        }
      }) as any
      
      if (response.success) {
        currentStep.value = 'confirm'
        return response
      } else {
        throw new Error(response.error || '取得申辦摘要失敗')
      }
    } catch (err: any) {
      error.value = err.message || '取得申辦摘要失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Step 10: 提交申辦
   */
  const submitApplication = async () => {
    loading.value = true
    error.value = null
    
    try {
      if (!sessionId.value) {
        throw new Error('請先開始流程')
      }
      
      const authSession = getAuthSessionId()
      if (!authSession) {
        throw new Error('請先登入')
      }
      
      const response = await $fetch('/api/renewal-workflow/step/submit', {
        method: 'POST',
        baseURL: config.public.apiBaseUrl,
        headers: {
          'X-Session-ID': authSession
        },
        body: {
          session_id: sessionId.value
        }
      }) as any
      
      if (response.success) {
        currentStep.value = 'completed'
        
        // 清除 localStorage 中的續約 session（但保留登入 session）
        if (process.client) {
          localStorage.removeItem('renewal_session_id')
        }
        
        return response
      } else {
        throw new Error(response.error || '提交申辦失敗')
      }
    } catch (err: any) {
      error.value = err.message || '提交申辦失敗'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 狀態
    sessionId: readonly(sessionId),
    currentStep: readonly(currentStep),
    customer: readonly(customer),
    phones: readonly(phones),
    selectedPhone: readonly(selectedPhone),
    eligibilityCheck: readonly(eligibilityCheck),
    loading: readonly(loading),
    error: readonly(error),
    
    // 方法
    startWorkflow,
    queryCustomer,
    listPhones,
    selectPhone,
    selectDeviceType,
    selectDeviceOS,
    queryDevices,
    selectDevice,
    listPlans,
    selectPlan,
    comparePlans,
    confirmApplication,
    submitApplication,
    getSession,
    clearSelection,
    clearWorkflow,
    restoreSession
  }
}
