# 登录模式使用指南

## 概述

本项目支持两种登录模式，可以根据压测需求灵活选择：

1. **`on_start` 模式**（默认）：所有用户在启动时统一登录，然后执行业务任务
2. **`task` 模式**：不在启动时登录，登录行为作为压测任务的一部分执行

## 配置方式

在 `.env` 文件中设置 `LOGIN_MODE`：

```env
# 模式一：启动时统一登录（默认）
LOGIN_MODE=on_start

# 模式二：登录作为压测任务
LOGIN_MODE=task
```

## 模式一：on_start 模式（默认）

### 特点
- ✅ 所有用户在 `on_start()` 阶段统一登录
- ✅ 登录完成后才开始执行业务任务
- ✅ 业务任务执行时用户已经登录，无需检查登录状态
- ⚠️ 所有用户启动时会同时发起登录请求，可能对登录接口造成瞬时压力

### 适用场景
- 主要压测业务接口，登录接口压力不是重点
- 需要确保所有业务请求都在已登录状态下执行
- 传统的压测场景

### 配置示例

```env
LOGIN_MODE=on_start
SELECTED_TASKS=student:user_homepage
```

### 执行流程

```
用户创建 → on_start() → 登录 → 开始执行任务 → 任务循环
```

## 模式二：task 模式（登录作为压测任务）

### 特点
- ✅ 用户创建时**不登录**
- ✅ 登录行为由任务控制，可以作为压测对象
- ✅ 登录请求的并发度由 Locust 的用户数和 spawn_rate 控制
- ✅ 支持"自动登录检查"功能，业务任务可以自动确保已登录

### 适用场景
- **专门压测登录接口**：使用 `login_only` 任务
- **登录+业务混合压测**：登录和业务接口一起压测
- **避免启动时的登录请求洪峰**：登录请求分散到任务执行过程中

### 配置示例

#### 示例 1：专门压测登录接口

```env
LOGIN_MODE=task
SELECTED_TASKS=student:login_only
```

效果：
- 每个用户只执行 `LoginOnlyBehavior` 任务
- 每次任务执行都会调用一次登录接口
- 登录接口的并发度 = Locust 配置的用户数

#### 示例 2：业务任务自动登录检查

```env
LOGIN_MODE=task
SELECTED_TASKS=student:registration_service
```

效果：
- 用户启动时不登录
- `RegistrationServiceBehavior` 任务执行前会自动检查登录状态
- 如果未登录，自动执行一次登录
- 如果已登录，直接执行业务请求（不重复登录）

#### 示例 3：登录 + 业务混合压测

```env
LOGIN_MODE=task
SELECTED_TASKS=student:login_only,student:user_homepage
```

效果：
- 用户启动时不登录
- 任务随机执行 `login_only` 或 `user_homepage`
- `user_homepage` 任务会自动检查登录状态，未登录时自动登录

### 执行流程

```
用户创建 → on_start()（不登录） → 开始执行任务
                                    ↓
任务执行 → 检查登录状态 → 未登录则自动登录 → 执行业务请求
```

## 自动登录检查功能

### 功能说明

在 `LOGIN_MODE=task` 模式下，业务任务可以使用 `ensure_logged_in()` 方法自动检查并确保用户已登录。

### 工作原理

1. **检查登录状态**：检查 `_is_logged_in` 标记和 `auth_token`、`headers` 是否存在
2. **已登录**：直接返回 `True`，不重复登录
3. **未登录**：自动调用 `_login()` 进行登录，登录成功后返回 `True`

### 使用方法

在任务方法中调用 `self.ensure_logged_in()`：

```python
from locust import task
from ..base import BaseTaskSet
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MyBusinessTask(BaseTaskSet):
    @task
    def my_business_request(self):
        # 自动登录检查：如果未登录，自动执行登录
        if not self.ensure_logged_in():
            logger.warning("登录失败，跳过业务请求")
            return
        
        # 确保 headers 存在
        if not self.user.headers:
            logger.error("用户 headers 为空，无法发送请求")
            return
        
        # 执行业务请求
        self.client.get(
            "/api/business/endpoint",
            name="/api/business/endpoint",
            headers=self.user.headers
        )
```

### 已更新的任务

以下任务已经更新，支持自动登录检查：

- ✅ `RegistrationServiceBehavior` (`src/tasks/student/registration_service.py`)
- ✅ `UserHomepageBehavior` (`src/tasks/student/user_homepage.py`)

### 注意事项

1. **登录状态标记**：登录成功后会自动设置 `_is_logged_in = True`，避免重复登录
2. **登录失败处理**：如果自动登录失败，`ensure_logged_in()` 返回 `False`，任务应该跳过业务请求
3. **headers 检查**：即使登录成功，也应该检查 `self.user.headers` 是否存在，确保可以发送请求
4. **性能考虑**：已登录的用户不会重复登录，不会造成额外的性能开销

## 任务类型说明

### login_only 任务

专门用于压测登录接口的任务：

```python
class LoginOnlyBehavior(BaseTaskSet):
    @task
    def login_task(self):
        """执行登录请求"""
        self.user._login()
```

- 每次任务执行都会调用一次登录接口
- 适合专门压测登录接口的场景

### 业务任务（带自动登录检查）

业务任务在执行前会自动检查登录状态：

```python
class BusinessTask(BaseTaskSet):
    @task
    def business_request(self):
        # 自动登录检查
        if not self.ensure_logged_in():
            return
        # 执行业务请求
        ...
```

- 第一次执行时会自动登录
- 后续执行时如果已登录，不会重复登录
- 适合登录+业务混合压测的场景

## 对比总结

| 特性 | on_start 模式 | task 模式 |
|------|--------------|-----------|
| 登录时机 | 用户启动时统一登录 | 任务执行时登录 |
| 登录接口压力 | 启动时集中压力 | 分散到任务执行过程中 |
| 业务任务登录检查 | 不需要（已登录） | 需要（自动检查） |
| 适用场景 | 传统压测、业务接口压测 | 登录接口压测、混合压测 |
| 配置复杂度 | 简单 | 需要理解任务选择 |

## 推荐配置

### 场景 1：压测业务接口（推荐 on_start）

```env
LOGIN_MODE=on_start
SELECTED_TASKS=student:user_homepage
```

### 场景 2：压测登录接口（推荐 task + login_only）

```env
LOGIN_MODE=task
SELECTED_TASKS=student:login_only
```

### 场景 3：混合压测（推荐 task + 多个任务）

```env
LOGIN_MODE=task
SELECTED_TASKS=student:login_only,student:user_homepage,student:registration_service
```

## 常见问题

### Q: task 模式下，业务任务第一次执行时会自动登录吗？

A: 是的。如果任务中调用了 `ensure_logged_in()`，第一次执行时会自动登录。后续执行时如果已登录，不会重复登录。

### Q: 可以同时压测登录接口和业务接口吗？

A: 可以。配置 `SELECTED_TASKS=student:login_only,student:user_homepage`，任务会随机执行。业务任务会自动检查登录状态。

### Q: 登录失败怎么办？

A: `ensure_logged_in()` 返回 `False` 时，任务应该跳过业务请求。已更新的任务都包含了这个检查。

### Q: 如何知道当前使用的是哪种模式？

A: 启动时会打印配置信息，包括 `LOGIN_MODE` 的值。也可以在 `.env` 文件中查看。

