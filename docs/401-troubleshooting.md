# 401 错误诊断指南

## 当前状态
- ✅ 后端健康检查通过
- ✅ 登录API成功（Session ID: session_S001_xxx）
- ❌ 续约流程API返回401未登录

## 问题分析

### 可能原因 1: Session ID 未正确传递
前端发送的 X-Session-ID header 可能未被后端接收

### 可能原因 2: request.user 字段名不匹配
- 中间件设置: `request.user['staff_id']` (小写)
- 路由读取: `request.user.get('STAFF_ID')` (大写) ✅ 已修复

### 可能原因 3: 认证中间件未执行
before_request 可能没有正确执行

## 诊断步骤

### 步骤 1: 检查后端是否收到请求

运行后端时应该看到类似输出：
```
認證檢查 path=/api/renewal-workflow/start has_header=True session_id=session_S001_xxx...
```

如果没有看到，说明请求根本没到达后端。

### 步骤 2: 检查 Session 是否在 Redis 中

```powershell
# 连接 Redis
redis-cli

# 查看所有 session
KEYS session:*

# 查看特定 session
GET session:session_S001_xxx
```

### 步骤 3: 使用 curl 测试

```powershell
# 1. 登录获取 session
curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"staff_code":"S001","password":"password"}'

# 记下返回的 session_id

# 2. 使用 session_id 调用续约API
curl -X POST http://localhost:8000/api/renewal-workflow/start `
  -H "Content-Type: application/json" `
  -H "X-Session-ID: session_S001_xxx"
```

### 步骤 4: 检查前端配置

```javascript
// 在浏览器 Console 中
console.log('API Base URL:', useRuntimeConfig().public.apiBaseUrl)
console.log('Session ID:', localStorage.getItem('session_id'))
```

## 修复建议

### 方案 A: 使用正确的测试账号（推荐）

前端和后端测试都应使用：
```
staff_code: S001
password: password
```

### 方案 B: 添加新的测试账号

在数据库中添加：
```sql
INSERT INTO STAFF VALUES (
  'STAFF_TEST', 
  'staff001', 
  '测试用户', 
  'Sales', 
  'STORE_A', 
  '$2b$12$hash...', -- password123 的 hash
  'test@example.com', 
  '0900-000-000'
);
```

### 方案 C: 修改前端登录页面

更新 `frontend/pages/login.vue` 中的默认值：
```typescript
const credentials = ref({
  staff_code: 'S001',  // 改为 S001
  password: 'password'  // 改为 password
})
```

## 关键修改

### 1. backend/app/routes/renewal_workflow.py (已修改)
```python
# 修改前
staff_id = request.user.get('STAFF_ID')  # 大写

# 修改后
staff_id = request.user.get('staff_id')   # 小写
```

### 2. backend/app/middleware/auth.py (已添加日志)
```python
logger.debug("認證檢查", 
            path=request.path,
            has_header=bool(request.headers.get('X-Session-ID')),
            session_id=session_id[:20] + '...')
```

### 3. frontend/composables/useRenewalWorkflow.ts (已修改)
```typescript
const getAuthSessionId = () => {
  if (authSessionId.value) return authSessionId.value
  if (process.client) return localStorage.getItem('session_id')
  return null
}
```

## 下一步

1. 重启后端服务器
2. 清除浏览器缓存和 localStorage
3. 使用正确的测试账号登录：S001 / password
4. 查看后端日志确认收到请求
5. 再次测试续约流程

## 测试命令

```powershell
# 后端测试
python test_backend_api.py

# 前端测试
# 1. 访问 http://localhost:3000/login
# 2. 输入: S001 / password
# 3. 点击"开始续约"
```
