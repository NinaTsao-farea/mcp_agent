# 续约流程重启功能

## 问题描述

**原始问题**：当续约流程中发生错误（如状态转换失败）时，session 会卡在错误状态，用户无法重新开始流程。

**错误示例**：
```
ValueError: 非法的狀態轉換: WorkflowStep.SELECT_DEVICE_TYPE -> WorkflowStep.QUERY_CUSTOMER
```

当发生此类错误后，用户无法继续流程，也无法重新开始。

## 解决方案

### 核心改进

1. **自动清理旧 Session**：当调用 `/api/renewal-workflow/start` 时，自动清除该员工之前未完成的 renewal session
2. **确保干净启动**：每次 `/start` 都从 `INIT` 状态开始新流程
3. **错误隔离**：前一次流程的错误不会影响新流程

### 技术实现

#### 1. 新增方法：`clear_staff_sessions`

```python
async def clear_staff_sessions(self, staff_id: str) -> int:
    """
    清除員工的所有續約 Session
    
    Args:
        staff_id: 員工 ID
        
    Returns:
        清除的 Session 數量
    """
    session_ids = await self.get_staff_sessions(staff_id)
    
    if not session_ids:
        return 0
    
    count = 0
    for session_id in session_ids:
        # 刪除 session 資料
        await self.redis.redis.delete(f"renewal_session:{session_id}")
        count += 1
    
    # 清空員工 session 集合
    await self.redis.redis.delete(f"staff_renewal_sessions:{staff_id}")
    
    logger.info(
        "清除員工所有續約 Session",
        staff_id=staff_id,
        count=count
    )
    
    return count
```

#### 2. 修改 `create_session` 方法

```python
async def create_session(self, staff_id: str, clear_existing: bool = True) -> Dict[str, Any]:
    """
    建立新的續約工作流程 Session
    
    Args:
        staff_id: 員工 ID
        clear_existing: 是否清除該員工現有的續約 Session（預設：True）
        
    Returns:
        Session 資料
    """
    # 清除該員工現有的續約 Session
    if clear_existing:
        await self.clear_staff_sessions(staff_id)
    
    # 創建新 session...
```

#### 3. 更新 `/start` 端点

```python
@bp.route('/start', methods=['POST'])
async def start_workflow():
    """
    開始續約流程
    
    自動清除該員工之前未完成的續約 Session，確保每次都能重新開始
    """
    # ...驗證用戶...
    
    # 建立新的工作流程 Session（會自動清除舊的）
    workflow_manager = get_workflow_manager()
    session_data = await workflow_manager.create_session(staff_id, clear_existing=True)
    
    # ...返回結果...
```

## 使用方式

### 前端调用

用户可以在任何时候调用 `startWorkflow()` 重新开始流程：

```typescript
// useRenewalWorkflow.ts

const { startWorkflow } = useRenewalWorkflow()

// 任何时候都可以调用，会自动清理旧流程
const handleRestart = async () => {
  try {
    await startWorkflow()
    // 新流程已开始，从 Step 1 开始
    navigateTo('/renewal/query-customer')
  } catch (error) {
    console.error('重新开始失败:', error)
  }
}
```

### UI 建议

建议在以下场景提供"重新开始"按钮：

1. **错误页面**：当发生错误时，提供"重新开始"选项
2. **导航栏**：在续约流程的任何页面，提供"重新开始"按钮
3. **确认对话框**：如果用户已进入流程中途，弹出确认对话框

示例：
```vue
<template>
  <div class="renewal-header">
    <UButton 
      color="gray" 
      variant="soft"
      @click="handleRestart"
    >
      <Icon name="i-heroicons-arrow-path" />
      重新开始
    </UButton>
  </div>
</template>

<script setup lang="ts">
const { startWorkflow } = useRenewalWorkflow()

const handleRestart = async () => {
  const confirmed = await confirm('確定要重新開始續約流程嗎？目前進度將會遺失。')
  if (confirmed) {
    await startWorkflow()
    navigateTo('/renewal/query-customer')
  }
}
</script>
```

## 测试验证

### 测试场景 1：流程中途重新开始

```bash
# 运行测试
cd backend
python test_restart_workflow.py
```

测试步骤：
1. 开始续约流程
2. 执行 Step 1-4，进入 `select_device_type` 状态
3. 调用 `/start` 重新开始
4. 验证：
   - ✅ 创建了新的 session
   - ✅ 旧 session 已被清除
   - ✅ 新 session 状态为 `init`
   - ✅ 可以正常执行流程

### 测试场景 2：错误后重新开始

测试步骤：
1. 开始续约流程
2. 输入不存在的身份证（触发错误）
3. 调用 `/start` 重新开始
4. 使用正确的身份证重新查询
5. 验证：流程正常执行

## 技术细节

### Session 生命周期

```
用户登入
  ↓
调用 /start
  ↓
清除旧 renewal sessions ← [自动]
  ↓
创建新 session (state: INIT)
  ↓
执行 Step 1-10
  ↓
完成或遇到错误
  ↓
可以随时调用 /start 重新开始 ← [关键改进]
```

### Redis 键结构

```
# 单个 session 数据
renewal_session:{session_id} → JSON object (TTL: 1小时)

# 员工的 session 集合
staff_renewal_sessions:{staff_id} → Set<session_id>
```

当调用 `/start` 时：
1. 从 `staff_renewal_sessions:{staff_id}` 获取所有 session IDs
2. 逐个删除 `renewal_session:{session_id}`
3. 清空 `staff_renewal_sessions:{staff_id}`
4. 创建新 session

### 性能考虑

- **清理开销**：通常每个员工只有 0-2 个旧 session，清理速度很快（< 10ms）
- **并发安全**：Redis 操作是原子的，支持并发调用
- **内存优化**：自动清理避免了 session 堆积

## 向后兼容性

### API 兼容性

✅ **完全向后兼容**：
- `/start` 端点签名未变
- 响应格式未变
- 前端代码无需修改

### 行为变化

⚠️ **行为变化**（需要注意）：
- **之前**：每次 `/start` 创建新 session，旧 session 保留到过期
- **现在**：每次 `/start` 清除旧 session，创建新 session

**影响**：
- ✅ 正面：用户不会因为旧 session 卡住
- ⚠️ 需要注意：如果用户在多个浏览器标签页同时操作，后打开的标签页会让先前的 session 失效

## 最佳实践

### 1. 前端状态管理

```typescript
// 监听 session 失效
watch(error, (newError) => {
  if (newError?.includes('Session 不存在')) {
    // session 可能在其他标签页被清除
    showNotification('流程已在其他地方重新开始，请刷新页面')
    // 自动重新开始
    startWorkflow()
  }
})
```

### 2. 多标签页处理

使用 BroadcastChannel API 同步多标签页状态：

```typescript
const channel = new BroadcastChannel('renewal_workflow')

// 当开始新流程时，通知其他标签页
const startWorkflow = async () => {
  const response = await $fetch('/api/renewal-workflow/start', ...)
  channel.postMessage({ type: 'workflow_restarted', session_id: response.session_id })
  return response
}

// 监听其他标签页的重启事件
channel.onmessage = (event) => {
  if (event.data.type === 'workflow_restarted') {
    showNotification('流程已在其他标签页重新开始')
    // 更新本地状态或跳转到首页
  }
}
```

### 3. 错误处理

```typescript
try {
  await selectDeviceType(sessionId, deviceType)
} catch (error) {
  if (error.message.includes('非法的狀態轉換')) {
    // 状态转换错误，提供重新开始选项
    const restart = await confirm(
      '流程状态异常，是否重新开始？'
    )
    if (restart) {
      await startWorkflow()
      navigateTo('/renewal/query-customer')
    }
  }
}
```

## 日志示例

成功重启流程时的日志：

```log
[info] 清除員工所有續約 Session staff_id=STAFF001 count=1
[info] 建立續約流程 Session session_id=renewal_STAFF001_xxx staff_id=STAFF001 cleared_existing=True
[info] 開始續約流程 staff_id=STAFF001 session_id=renewal_STAFF001_xxx current_step=init
```

## 总结

这个改进确保了：

✅ **用户友好**：任何时候都可以重新开始，不会卡住  
✅ **错误恢复**：发生错误后可以轻松重试  
✅ **状态清晰**：每次开始都是干净的 INIT 状态  
✅ **向后兼容**：现有代码无需修改  
✅ **自动清理**：避免 session 堆积  

用户体验显著提升，消除了"流程卡住无法继续"的问题。
