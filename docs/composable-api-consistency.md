# Composable API 一致性修复

## 问题描述

在 `useRenewalWorkflow` Composable 中发现 API 设计不一致的问题：

### 原有设计（不一致）

```typescript
// Step 4: 选择门号
const selectPhone = async (phoneNumber: string) => {
  // ✅ 使用内部的 sessionId.value
  body: {
    session_id: sessionId.value,
    phone_number: phoneNumber
  }
}

// Step 5: 选择装置类型
const selectDeviceType = async (renewalSessionId: string, deviceType: string) => {
  // ❌ 从外部传入 renewalSessionId 参数
  body: {
    session_id: renewalSessionId,
    device_type: deviceType
  }
}
```

## 问题分析

### 为什么不一致？

1. **历史原因**：Step 5 是在修复 session ID 传递问题时添加的
2. **设计错误**：错误地设计成需要从外部传入 session ID
3. **违反原则**：Composable 已经管理了 sessionId 状态，不应该重复传参

### 影响范围

- **前端页面调用复杂**：需要手动传递 `renewalSessionId`
- **代码冗余**：sessionId 在 Composable 内部已存在
- **维护困难**：不同步骤使用不同的调用方式

## 解决方案

### 1. 修改 Composable API

统一使用内部的 `sessionId.value`：

```typescript
// 修改前
const selectDeviceType = async (renewalSessionId: string, deviceType: string) => {
  // ...
  body: {
    session_id: renewalSessionId,
    device_type: deviceType
  }
}

// 修改后
const selectDeviceType = async (deviceType: string) => {
  // 添加检查
  if (!sessionId.value) {
    throw new Error('請先開始流程')
  }
  
  // ...
  body: {
    session_id: sessionId.value,  // 使用内部状态
    device_type: deviceType
  }
}
```

### 2. 修改前端页面调用

简化 `select-device-type.vue` 的实现：

```typescript
// 修改前：直接调用 API，手动管理 loading/error
const handleSubmit = async () => {
  loading.value = true
  error.value = null
  
  try {
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
        session_id: renewalSessionId.value,  // 需要手动传递
        device_type: selectedType.value
      }
    })
    // ...
  } finally {
    loading.value = false
  }
}

// 修改后：使用 Composable 方法
const {
  sessionId: renewalSessionId,
  selectDeviceType,
  loading: workflowLoading,
  error: workflowError
} = useRenewalWorkflow()

const handleSubmit = async () => {
  if (!selectedType.value) {
    error.value = '請選擇續約方式'
    return
  }
  
  try {
    // 只需传递 deviceType，sessionId 由 Composable 管理
    const response = await selectDeviceType(selectedType.value)
    
    if (response.success) {
      await router.push('/renewal/select-plan')
    }
  } catch (err: any) {
    error.value = workflowError.value || err.message
  }
}
```

## 修改文件清单

### 1. `frontend/composables/useRenewalWorkflow.ts`

- 修改 `selectDeviceType` 函数签名
- 移除 `renewalSessionId` 参数
- 添加 `sessionId` 检查
- 使用内部的 `sessionId.value`

### 2. `frontend/pages/renewal/select-device-type.vue`

- 从 Composable 解构 `selectDeviceType`, `loading`, `error`
- 移除本地的 `loading`, `getAuthSessionId()`
- 移除直接的 API 调用
- 使用 Composable 的 `selectDeviceType()` 方法
- 使用 Composable 的 `workflowLoading` 状态

## 设计原则总结

### ✅ 正确的 Composable 设计

1. **状态集中管理**
   ```typescript
   const sessionId = useState<string | null>('renewal.sessionId', () => null)
   ```

2. **方法内部访问状态**
   ```typescript
   const someAction = async (param: string) => {
     // ✅ 使用内部状态
     if (!sessionId.value) {
       throw new Error('請先開始流程')
     }
     
     await $fetch('/api/...', {
       body: {
         session_id: sessionId.value,  // 使用内部状态
         param: param
       }
     })
   }
   ```

3. **暴露只读状态**
   ```typescript
   return {
     sessionId: readonly(sessionId),  // 只读，不可外部修改
     someAction
   }
   ```

### ❌ 错误的设计模式

1. **重复传递内部状态**
   ```typescript
   // ❌ 错误：sessionId 是内部状态，不应该作为参数
   const someAction = async (sessionId: string, param: string) => {
     await $fetch('/api/...', {
       body: { session_id: sessionId, param }
     })
   }
   ```

2. **页面直接调用 API**
   ```typescript
   // ❌ 错误：绕过 Composable，无法统一管理状态
   const response = await $fetch('/api/...', {
     body: { session_id: renewalSessionId.value }
   })
   ```

## 统一调用模式

### 所有步骤方法签名

```typescript
// Step 1: 开始流程
startWorkflow(): Promise<any>

// Step 2: 查询客户
queryCustomer(idNumber: string): Promise<any>

// Step 3: 列出门号
listPhones(): Promise<any>

// Step 4: 选择门号
selectPhone(phoneNumber: string): Promise<any>

// Step 5: 选择装置类型 ✅ 已修复
selectDeviceType(deviceType: string): Promise<any>

// Step 10: 确认申办
confirmApplication(): Promise<any>

// Step 10: 提交申办
submitApplication(): Promise<any>
```

### 共同特征

1. ✅ **不传递 session_id** - 由 Composable 内部管理
2. ✅ **只传递业务参数** - 如 idNumber, phoneNumber, deviceType
3. ✅ **统一错误处理** - 使用 Composable 的 error 状态
4. ✅ **统一 loading 状态** - 使用 Composable 的 loading 状态

## 测试建议

### 1. 单元测试

验证 `selectDeviceType` 方法：

```typescript
it('should use internal sessionId', async () => {
  const { sessionId, selectDeviceType } = useRenewalWorkflow()
  
  // 设置 sessionId
  sessionId.value = 'test-session-123'
  
  // 调用时不需要传递 sessionId
  await selectDeviceType('smartphone')
  
  // 验证 API 调用使用了内部的 sessionId
  expect(mockFetch).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({
      body: {
        session_id: 'test-session-123',
        device_type: 'smartphone'
      }
    })
  )
})
```

### 2. 集成测试

测试完整流程：

```typescript
it('should complete Step 5 without passing sessionId', async () => {
  // 1. 开始流程
  await startWorkflow()
  
  // 2. 查询客户
  await queryCustomer('A123456789')
  
  // 3. 列出门号
  await listPhones()
  
  // 4. 选择门号
  await selectPhone('0912345678')
  
  // 5. 选择装置类型（不需要传递 sessionId）
  const response = await selectDeviceType('smartphone')
  
  expect(response.success).toBe(true)
  expect(response.next_step).toBe('select_device_os')
})
```

## 总结

### 修复内容

- ✅ 统一了 Composable API 设计
- ✅ 移除了冗余的参数传递
- ✅ 简化了前端页面调用
- ✅ 提高了代码可维护性

### 影响范围

- `frontend/composables/useRenewalWorkflow.ts` - 核心修改
- `frontend/pages/renewal/select-device-type.vue` - 调用方式修改

### 后续步骤

当实现 Step 6-9 时，请遵循相同的设计原则：

1. 方法只接收业务参数
2. 内部使用 `sessionId.value`
3. 统一使用 Composable 的 loading/error 状态
4. 页面通过 Composable 调用，不直接调用 API

---

**日期**: 2025-10-29  
**修改人**: GitHub Copilot  
**版本**: 1.0
