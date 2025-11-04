# 非本公司客户错误处理测试

## 修改内容

### 1. `frontend/composables/useRenewalWorkflow.ts` - queryCustomer 函数
**修改前**：失败时抛出异常
```typescript
if (response.success) {
  // ...
} else {
  throw new Error(response.error || response.message)
}
```

**修改后**：失败时返回响应对象，不抛出异常
```typescript
if (response.success) {
  customer.value = response.customer
  currentStep.value = 'list_phones'
  error.value = null
  return response
} else {
  // 设置错误信息但不抛异常
  const errorMessage = response.message || response.error || '查詢客戶失敗'
  error.value = errorMessage
  return response
}
```

### 2. `frontend/pages/renewal/index.vue` - handleQueryCustomer 函数
**修改前**：不检查返回结果，直接继续获取门号
```typescript
await queryCustomer(idNumber.value)
await listPhones()  // 总是执行
```

**修改后**：检查返回结果，失败时不继续
```typescript
const customerResult = await queryCustomer(idNumber.value)

// 检查是否成功
if (!customerResult || !customerResult.success) {
  console.error('查詢客戶失敗，不繼續取得門號')
  return  // 提前返回，不执行 listPhones()
}

await listPhones()  // 只有成功时才执行
```

## 测试步骤

### 测试案例 1: 非本公司客户
1. 登录系统（S001 / password）
2. 点击"开始续约"
3. 输入身分证号：`C111222333`
4. 点击"查询客户"

**预期结果**：
- ❌ 不应该继续调用门号列表 API
- ✅ 显示错误信息："很抱歉，目前暫不提供新申辦服務，感謝您的詢問"
- ✅ 停留在查询客户页面
- ✅ 输入框下方显示红色错误信息

### 测试案例 2: 不存在的客户
1. 输入身分证号：`X000000000`
2. 点击"查询客户"

**预期结果**：
- ❌ 不应该继续调用门号列表 API
- ✅ 显示错误信息："查無此客戶"
- ✅ 停留在查询客户页面

### 测试案例 3: 正常客户（对照组）
1. 输入身分证号：`A123456789`
2. 点击"查询客户"

**预期结果**：
- ✅ 成功查询客户
- ✅ 自动调用门号列表 API
- ✅ 显示客户信息和门号列表
- ✅ 进入 Step 2（选择门号）

## 后端响应格式

### 成功响应
```json
{
  "success": true,
  "message": "客戶查詢成功",
  "customer": {
    "customer_id": "C123456",
    "name": "張三",
    "phone": "0912-345-678",
    "email": "zhang@example.com",
    "is_company_customer": true
  }
}
```

### 非本公司客户响应
```json
{
  "success": false,
  "error": "非本公司客戶",
  "message": "很抱歉，目前暫不提供新申辦服務，感謝您的詢問",
  "customer": {
    "name": "王五",
    "is_company_customer": false
  }
}
```

### 不存在的客户响应
```json
{
  "success": false,
  "error": "查無此客戶",
  "message": "很抱歉，查無此身分證號的客戶資料"
}
```

## UI 显示

### 错误信息显示位置
错误信息通过 `UFormGroup` 的 `:error` 属性绑定到 `error` 状态：

```vue
<UFormGroup label="身分證號" :error="error">
  <UInput v-model="idNumber" ... />
</UFormGroup>
```

当 `error` 有值时，会在输入框下方显示红色错误信息。

## 调试方法

### 浏览器 Console
```javascript
// 查看查询结果
// 应该能看到：
console.log('查詢客戶:', idNumber.value)
console.log('查詢結果:', customerResult)

// 如果失败，应该看到：
console.error('查詢客戶失敗，不繼續取得門號')

// 不应该看到：
console.log('取得門號列表...')  // 失败时不应该出现
```

### Network 面板
- 成功时：应该看到 2 个请求
  1. POST `/api/renewal-workflow/step/query-customer` (200)
  2. POST `/api/renewal-workflow/step/list-phones` (200)

- 失败时：应该只看到 1 个请求
  1. POST `/api/renewal-workflow/step/query-customer` (400)
  2. ❌ 不应该有 list-phones 请求

## 完成标准

- ✅ 非本公司客户返回错误时不继续获取门号
- ✅ 错误信息正确显示在输入框下方
- ✅ 正常客户依然可以正常查询和显示门号列表
- ✅ Console 日志清晰显示流程
- ✅ Network 面板显示正确的 API 调用顺序
