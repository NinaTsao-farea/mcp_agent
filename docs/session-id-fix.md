# Session ID 传递问题修复

## 问题描述

在 `eligibility.vue` 页面点击"下一步：选择续约方式"按钮时，出现错误：
```
缺少 Session ID
```

## 根本原因

**问题 1**：`eligibility.vue` 使用 `route.query.session_id` 获取 session ID
```typescript
// ❌ 错误的方式
const renewalSessionId = computed(() => {
  return route.query.session_id as string || null
})
```

**问题 2**：`select-phone.vue` 导航到 `eligibility.vue` 时没有传递 query 参数
```typescript
// ❌ 缺少 session_id
navigateTo('/renewal/eligibility')
```

## 解决方案

### 核心思想

续约流程的 **session ID 应该从 Composable 获取**，而不是依赖 URL query 参数。

`useRenewalWorkflow` composable 已经管理了 `sessionId` 状态：
```typescript
const sessionId = useState<string | null>('renewal.sessionId', () => null)
```

### 修改内容

#### 1. eligibility.vue

**修改前**：
```typescript
const {
  selectedPhone,
  eligibilityCheck,
  clearSelection
} = useRenewalWorkflow()

const renewalSessionId = computed(() => {
  return route.query.session_id as string || null
})
```

**修改后**：
```typescript
const {
  sessionId: renewalSessionId,  // ✅ 直接从 composable 获取
  selectedPhone,
  eligibilityCheck,
  clearSelection
} = useRenewalWorkflow()
```

#### 2. select-device-type.vue

**修改前**：
```typescript
const { sessionId: authSessionId } = useAuth()

const renewalSessionId = computed(() => {
  return route.query.session_id as string || null
})
```

**修改后**：
```typescript
const { sessionId: authSessionId } = useAuth()
const { sessionId: renewalSessionId } = useRenewalWorkflow()  // ✅
```

#### 3. confirm.vue

**修改前**：
```typescript
const { sessionId: authSessionId } = useAuth()

const renewalSessionId = computed(() => {
  return route.query.session_id as string || null
})
```

**修改后**：
```typescript
const { sessionId: authSessionId } = useAuth()
const { sessionId: renewalSessionId } = useRenewalWorkflow()  // ✅
```

## 为什么这样修改？

### 问题分析

1. **URL query 参数不可靠**：
   - 页面刷新会丢失
   - 导航时容易忘记传递
   - 容易被用户修改

2. **Composable 状态更可靠**：
   - 使用 `useState` 在整个应用中共享
   - 页面切换时自动保持
   - 统一的状态管理

### Session ID 的生命周期

```typescript
// 1. 开始续约流程
const startWorkflow = async () => {
  const response = await $fetch('/api/renewal-workflow/start', ...)
  sessionId.value = response.session_id  // ✅ 存储到 composable
  
  // 同时存储到 localStorage（用于页面刷新恢复）
  if (process.client) {
    localStorage.setItem('renewal_session_id', response.session_id)
  }
}

// 2. 在任何页面使用
const { sessionId: renewalSessionId } = useRenewalWorkflow()
// renewalSessionId.value 总是可用的

// 3. 清理流程
const clearWorkflow = async () => {
  sessionId.value = null  // ✅ 清除状态
  if (process.client) {
    localStorage.removeItem('renewal_session_id')
  }
}
```

## URL Query 参数的作用

虽然我们不再依赖 URL query 参数获取 session ID，但**仍然传递它**作为额外的标识：

```typescript
// ✅ 仍然在导航时传递（便于调试和直接访问）
navigateTo({
  path: '/renewal/select-device-type',
  query: { session_id: renewalSessionId.value }
})
```

**好处**：
- 便于调试（URL 中可以看到 session ID）
- 支持直接访问 URL（虽然 composable 状态可能不存在）
- 向后兼容

## 测试验证

### 测试场景

1. **正常流程**：
   ```
   登入 → 查询客户 → 选择门号 → 资格检查 → 选择装置类型
   ```
   - ✅ session ID 在整个流程中可用

2. **页面刷新**：
   - ✅ 从 localStorage 恢复 session ID

3. **直接访问中间页面**：
   - ✅ 检测到 session ID 不存在，重定向到起始页

## 最佳实践

### 1. 优先使用 Composable 状态

```typescript
// ✅ 推荐
const { sessionId } = useRenewalWorkflow()

// ❌ 不推荐
const sessionId = computed(() => route.query.session_id as string || null)
```

### 2. URL Query 作为辅助

```typescript
// ✅ 传递 query 参数（便于调试）
navigateTo({
  path: '/next-page',
  query: { session_id: sessionId.value }
})

// ❌ 但不依赖它来获取状态
```

### 3. 页面保护

```typescript
// ✅ 检查 composable 状态
onMounted(() => {
  if (!sessionId.value) {
    navigateTo('/renewal/query-customer')
  }
})
```

## 相关文件

修改的文件：
- ✅ `frontend/pages/renewal/eligibility.vue`
- ✅ `frontend/pages/renewal/select-device-type.vue`
- ✅ `frontend/pages/renewal/confirm.vue`

相关文件：
- `frontend/composables/useRenewalWorkflow.ts` - Session 状态管理
- `frontend/pages/renewal/select-phone.vue` - 导航到 eligibility

## 总结

**核心改变**：
- ❌ 不再依赖 `route.query.session_id`
- ✅ 使用 `useRenewalWorkflow().sessionId`

**好处**：
- ✅ Session ID 始终可用
- ✅ 导航时无需手动传递
- ✅ 状态管理更统一
- ✅ 减少错误可能性

**影响范围**：
- 只影响续约流程的 3 个页面
- 向后兼容（仍然传递 query 参数）
- 不影响其他功能
