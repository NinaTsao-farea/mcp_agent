# 认证 Session 测试指南

## 问题描述
前端点击"开始续约"按钮时出现 401 错误，原因是没有正确传递认证 session ID。

## 解决方案
在 `useRenewalWorkflow.ts` 中添加 `getAuthSessionId()` 辅助函数，优先从 composable 获取，如果为空则从 localStorage 获取。

## 测试步骤

### 1. 确保已登录
```
1. 访问 http://localhost:3000/login
2. 输入：staff001 / password123
3. 点击登录
4. 确认跳转到首页
```

### 2. 验证 Session 存储
打开浏览器开发者工具 (F12)：
```javascript
// 在 Console 中执行
localStorage.getItem('session_id')
// 应该返回类似: "session_staff001_abc123..."
```

### 3. 测试续约流程
```
1. 在首页点击"开始续约"
2. 检查 Network 面板
3. 查看 /api/renewal-workflow/start 请求
4. 确认 Request Headers 中有: X-Session-ID: session_staff001_...
5. 应该返回 200 状态码和 session_id
```

### 4. 如果仍然出现 401

#### 检查点 1: Session 是否存在
```javascript
// 在浏览器 Console 中
localStorage.getItem('session_id')
```

#### 检查点 2: 后端 Redis 中是否有 Session
```bash
# 连接到 Redis
redis-cli

# 查看所有 session keys
KEYS session:*

# 查看具体 session 数据
GET session:session_staff001_xxx
```

#### 检查点 3: 重新登录
```
1. 点击登出
2. 重新登录
3. 再次尝试续约流程
```

## 修改的文件

1. **frontend/composables/useRenewalWorkflow.ts**
   - 添加 `getAuthSessionId()` 函数
   - 更新所有 API 调用使用该函数获取 session ID

## 预期结果

✅ 登录后 localStorage 中应该有 session_id
✅ 点击"开始续约"应该成功返回 renewal session
✅ Network 面板中所有请求应该带有 X-Session-ID header
✅ 状态码应该是 200，不是 401

## 调试命令

### 前端
```javascript
// 检查认证状态
const { user, sessionId, isLoggedIn } = useAuth()
console.log('User:', user.value)
console.log('Session ID:', sessionId.value)
console.log('Is Logged In:', isLoggedIn.value)
```

### 后端
```python
# 查看日志
# 应该看到类似输出：
# Session 驗證成功 staff_code=staff001
```

## 常见问题

### Q: 为什么使用 localStorage 而不是 Cookie？
A: 当前实现中，后端返回 session_id 但没有设置 cookie。前端将其存储在 localStorage 中，然后通过 X-Session-ID header 发送。

### Q: 生产环境建议？
A: 建议改用 HTTP-only Cookie 存储 session，更安全且自动发送。

### Q: Session 过期时间？
A: 默认 8 小时（SESSION_EXPIRE_HOURS=8）
