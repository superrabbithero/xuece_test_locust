# Locust 用户加载逻辑分析

## 问题描述
- 设置：100个用户，每秒载入20个用户（spawn_rate=20）
- 现象：要等到所有100个用户加载完成后才会开始调用登录接口
- 结果：登录接口响应时间很长

## 代码加载逻辑梳理

### 1. Locust 用户创建流程

```
Locust 启动
  ↓
按 spawn_rate (20个/秒) 创建用户实例
  ↓
创建 EcommerceUser 实例 (__init__)
  ↓
调用 on_start() 方法
  ↓
执行登录 (_login)
  ↓
开始执行任务 (tasks)
```

### 2. 当前代码执行流程

#### 2.1 用户实例创建 (`__init__`)
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # 初始化用户属性（很快，无阻塞）
    self.account = None
    self.user_id = None
    # ...
```

**特点**：这一步很快，无阻塞操作

#### 2.2 用户启动 (`on_start`)
```python
def on_start(self):
    # 1. 获取配置（很快）
    settings = get_settings()
    
    # 2. 打印配置（仅第一次，有锁保护）
    if not hasattr(EcommerceUser, '_config_printed'):
        print(...)  # 可能有轻微延迟
    
    # 3. 获取账号加载器（单例模式，第一次会初始化CSV加载器）
    account_loader = self._get_account_loader()  # ⚠️ 潜在阻塞点1
    
    # 4. 获取账号（从Queue中取，很快）
    self.account = account_loader.get_account()
    
    # 5. 选择任务（很快）
    selected_tasks = select_tasks(...)
    
    # 6. 执行登录（同步HTTP请求，阻塞）
    self._login()  # ⚠️ 主要阻塞点
```

#### 2.3 账号加载器初始化 (`_get_account_loader`)
```python
@classmethod
def _get_account_loader(cls) -> BaseAccountLoader:
    if cls._account_loader is None:
        # 第一次调用时创建CSVAccountLoader
        cls._account_loader = CSVAccountLoader()  # ⚠️ 潜在阻塞点2
    return cls._account_loader
```

#### 2.4 CSV账号加载器初始化 (`CSVAccountLoader.__init__`)
```python
def __init__(self):
    # 读取整个CSV文件到内存
    with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        all_rows = list(reader)  # ⚠️ 如果文件很大，会有延迟
    
    # 将账号放入Queue
    for row in all_rows[start:end]:
        self.accounts.put(row)
```

**特点**：
- 只执行一次（单例模式）
- 如果CSV文件很大（如30008个账号），读取和初始化会有延迟
- 多个用户同时调用时，第一个用户会触发初始化，其他用户会等待

#### 2.5 登录操作 (`_login`)
```python
def _login(self):
    # 同步HTTP请求，会阻塞直到响应返回
    with self.client.get(
        "/api/usercenter/nnauth/user/login",
        name="用户登录",
        params=params,
        catch_response=True
    ) as response:
        # 处理响应...
```

**特点**：
- 同步阻塞操作
- 每个用户都要等待登录完成
- 如果登录接口慢，会严重影响启动速度

## 问题根本原因分析

### 原因1：Locust 的默认行为（最可能）

**Locust 2.x 的默认行为**：
- Locust 会先创建所有用户实例（按 spawn_rate 速率）
- **然后等待所有用户的 `on_start()` 完成**
- 最后才开始执行任务

这意味着：
1. 虽然用户是按 20个/秒 创建的，但 `on_start()` 可能不会立即执行
2. 所有用户创建完成后，才开始并发执行 `on_start()`
3. 如果登录接口慢，所有用户都会等待

### 原因2：账号加载器初始化竞争

**单例模式的竞争条件**：
```python
if cls._account_loader is None:  # 多个用户可能同时检查
    cls._account_loader = CSVAccountLoader()  # 只有第一个会执行
```

**问题**：
- 虽然只有第一个用户会触发 CSV 加载器初始化
- 但如果多个用户同时调用 `_get_account_loader()`，可能会有竞争
- 在 gevent 协程环境下，如果 CSV 文件很大，初始化会阻塞其他协程

### 原因3：登录接口同步阻塞

**每个用户都要等待登录完成**：
- 100个用户，每个都要执行 `_login()`
- 如果登录接口响应慢（如 500ms），100个用户就是 50秒
- 如果登录接口响应很慢（如 2秒），100个用户就是 200秒

### 原因4：Queue.get() 的潜在阻塞

虽然代码中使用了 `Queue.get()`，但因为有 `empty()` 检查，理论上不会阻塞。但如果 Queue 为空，`get_account()` 会返回 `None`。

## 验证方法

### 1. 添加日志验证执行顺序

在关键位置添加时间戳日志：
```python
import time

def on_start(self):
    logger.info(f"[{time.time()}] 用户 {id(self)} on_start 开始")
    # ...
    logger.info(f"[{time.time()}] 用户 {id(self)} 开始登录")
    self._login()
    logger.info(f"[{time.time()}] 用户 {id(self)} 登录完成")
```

### 2. 检查 Locust 日志

查看 Locust 的启动日志，确认：
- 用户创建的时间点
- `on_start()` 执行的时间点
- 登录请求的时间点

## 解决方案建议

### 方案1：延迟登录（推荐）

将登录从 `on_start()` 移到第一个需要认证的任务中：
- 用户创建后立即开始执行任务
- 在第一个需要 `headers` 的任务中检查是否已登录
- 如果未登录，先执行登录，再执行任务

**优点**：
- 用户创建后立即开始压测
- 登录请求分散到任务执行过程中
- 不会阻塞用户启动

**缺点**：
- 第一个任务可能需要等待登录完成
- 需要修改任务代码，检查登录状态

### 方案2：异步登录（如果支持）

使用异步HTTP客户端（如 `aiohttp`）进行登录：
- 但 Locust 的 `FastHttpUser` 使用的是同步客户端
- 需要切换到 `HttpUser` 或自定义异步客户端

### 方案3：预热登录

在压测开始前，预先登录一批用户：
- 使用单独的脚本预先登录
- 将登录信息缓存（如 Redis）
- 用户启动时从缓存获取登录信息

### 方案4：优化账号加载器

- 使用线程锁保护单例初始化
- 预先初始化账号加载器（在模块加载时）
- 使用更快的账号存储方式（如 Redis）

## 总结

**核心问题**：
1. Locust 默认等待所有用户的 `on_start()` 完成
2. 登录在 `on_start()` 中同步执行，阻塞用户启动
3. 100个用户都要等待登录完成，导致启动慢

**最直接的解决方案**：
- 将登录从 `on_start()` 移到任务中（延迟登录）
- 这样用户创建后可以立即开始执行任务，登录在需要时进行


