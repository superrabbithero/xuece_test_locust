# 调试指南

## 启用调试模式

在 `.env` 文件中设置以下配置项来启用调试打印：

```env
# 调试配置
DEBUG_REQUESTS=true   # 打印请求信息
DEBUG_RESPONSES=true  # 打印响应信息
```

## 使用方式

### 1. 全局调试（所有请求）

在 `.env` 中设置：
```env
DEBUG_REQUESTS=true
DEBUG_RESPONSES=true
```

这样所有请求和响应都会被打印出来。

### 2. 在代码中使用调试函数

如果你想在特定位置打印请求和响应，可以在代码中直接调用：

```python
from src.utils.helpers import print_request, print_response

# 打印请求
print_request(
    method="GET",
    url="http://example.com/api/test",
    params={"key": "value"},
    headers={"Authorization": "Bearer token"}
)

# 发送请求
response = self.client.get("/api/test", params={"key": "value"})

# 打印响应
print_response(response, url="http://example.com/api/test")
```

### 3. 在任务中使用

在任何任务类中，你都可以使用调试函数：

```python
from src.tasks.base import BaseTaskSet
from src.utils.helpers import print_request, print_response

class MyTask(BaseTaskSet):
    @task
    def my_api_call(self):
        # 打印请求
        print_request(
            method="POST",
            url=f"{self.user.host}/api/endpoint",
            headers=self.user.headers,
            json_data={"data": "value"}
        )
        
        # 发送请求
        response = self.client.post(
            "/api/endpoint",
            json={"data": "value"},
            headers=self.user.headers
        )
        
        # 打印响应
        print_response(response, url=f"{self.user.host}/api/endpoint")
```

## 调试输出示例

### 请求输出
```
================================================================================
[请求] GET http://example.com/api/usercenter/nnauth/user/login
--------------------------------------------------------------------------------
[参数] {
  "username": "test@example.com",
  "encryptpwd": "***",
  "clienttype": "BROWSER"
}
[请求头] {
  "Content-Type": "application/json"
}
================================================================================
```

### 响应输出
```
================================================================================
[响应] http://example.com/api/usercenter/nnauth/user/login
--------------------------------------------------------------------------------
[状态码] 200
[响应头] {'Content-Type': 'application/json', 'Content-Length': '1234'}
[响应内容]
{"code": 200, "data": {"user": {...}, "authtoken": "..."}}
[JSON响应] {
  "code": 200,
  "data": {
    "user": {
      "id": 123,
      "username": "test@example.com"
    },
    "authtoken": "abc123..."
  }
}
================================================================================
```

## 注意事项

1. **性能影响**：启用调试会显著影响性能，仅用于调试，不要在生产压测中启用
2. **敏感信息**：请求头中的 `Authtoken` 会自动部分隐藏（只显示前后各10个字符）
3. **响应长度**：默认最多打印2000个字符，超长响应会被截断
4. **日志文件**：调试信息会同时输出到控制台和日志文件（如果配置了日志文件）

## 常见问题排查

### 问题1：响应为 None
如果看到 `[状态] 响应为 None（连接失败）`，可能原因：
- 网络连接问题
- 服务器不可达
- DNS解析失败
- 防火墙阻止

### 问题2：解析响应失败
如果看到 `解析登录响应失败: 'NoneType' object has no attribute 'get'`：
- 检查响应内容，可能响应格式不符合预期
- 查看打印的完整响应数据
- 确认API返回的数据结构

### 问题3：HTTP 0 状态码
HTTP 0 表示连接失败：
- 检查 `API_HOST` 配置是否正确
- 测试服务器是否可访问
- 检查网络连接

## 快速调试单个接口

如果你想快速测试单个接口，可以：

1. 创建一个简单的测试脚本：
```python
from src.utils.helpers import print_request, print_response
from locust import HttpUser, task

class TestUser(HttpUser):
    host = "http://your-api-host.com"
    
    @task
    def test_api(self):
        print_request(
            method="GET",
            url=f"{self.host}/api/test",
            params={"key": "value"}
        )
        
        response = self.client.get("/api/test", params={"key": "value"})
        
        print_response(response, url=f"{self.host}/api/test")
```

2. 运行测试：
```bash
locust -f test_script.py --headless -u 1 -r 1 -t 10s
```

这样只会运行一次，方便查看请求和响应。

