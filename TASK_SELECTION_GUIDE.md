# 任务选择指南

## 概述

你可以通过配置选择要执行的任务，而不是运行所有任务。这对于：
- 测试特定功能
- 减少压测范围
- 调试特定接口
- 提高压测效率

## 配置方式

在 `.env` 文件中添加 `SELECTED_TASKS` 配置项：

```env
# 任务选择配置
SELECTED_TASKS=holiday_task,watch_video
```

### 精确控制账号类型

如果学生和教师都有同名任务，你可以使用 `账号类型:任务名称` 的格式来精确指定：

```env
# 只执行学生的 user_homepage 任务（即使教师也有同名任务）
SELECTED_TASKS=student:user_homepage

# 同时指定学生和教师的不同任务
SELECTED_TASKS=student:user_homepage,teacher:marking_list
```

## 可用任务列表

### 学生任务

| 任务名称 | 说明 |
|---------|------|
| `user_homepage` | 学生登录首页（获取用户信息和首页数据） |
| `holiday_task` | 查看假期作业列表 |
| `watch_video` | 观看视频打卡 |
| `outdoor_training` | 户外训练 |
| `ask_question` | 学生提问 |
| `download` | 下载资料 |
| `homework_free` | 自由出题练习 |
| `schedule_task` | 打卡任务 |
| `registration_service` | 学生注册服务 |

### 教师任务

| 任务名称 | 说明 |
|---------|------|
| `marking_list` | 查看练习监控和批改列表 |

## 使用示例

### 1. 执行所有任务（默认）

```env
# 不设置 SELECTED_TASKS，或设置为空
SELECTED_TASKS=
```

或者：

```env
SELECTED_TASKS=all
```

### 2. 执行所有学生任务

```env
SELECTED_TASKS=student
```

### 3. 执行所有教师任务

```env
SELECTED_TASKS=teacher
```

### 4. 执行指定任务（单个）

```env
# 只执行观看视频任务
SELECTED_TASKS=watch_video
```

### 5. 执行指定任务（多个）

```env
# 执行多个任务，用逗号分隔
SELECTED_TASKS=holiday_task,watch_video,ask_question
```

### 6. 精确指定账号类型的任务

```env
# 只执行学生的 user_homepage（即使教师也有同名任务）
SELECTED_TASKS=student:user_homepage

# 混合使用：指定账号类型和普通任务名称
SELECTED_TASKS=student:user_homepage,holiday_task,watch_video
```

### 7. 测试特定功能

```env
# 只测试登录和查看作业列表
SELECTED_TASKS=holiday_task
```

## 配置示例

### 示例1：只测试视频相关功能

```env
SELECTED_TASKS=watch_video
```

### 示例2：测试学生提问和下载功能

```env
SELECTED_TASKS=ask_question,download
```

### 示例3：测试所有学生任务（除了自由出题）

```env
SELECTED_TASKS=holiday_task,watch_video,outdoor_training,ask_question,download,schedule_task
```

## 注意事项

1. **账号类型匹配**：
   - 学生账号只能执行学生任务
   - 教师账号只能执行教师任务
   - 如果配置了不匹配的任务，会被自动过滤

2. **任务名称大小写**：
   - 任务名称不区分大小写
   - 建议使用小写

3. **无效任务名称**：
   - 如果配置了无效的任务名称，会被忽略
   - 会在日志中显示警告信息

4. **空配置**：
   - 如果配置为空或无效，会使用默认任务（所有任务）

## 查看可用任务

你可以运行以下Python代码查看所有可用任务：

```python
from src.utils.task_selector import get_available_tasks

tasks = get_available_tasks()
print("任务映射:", tasks['task_map'].keys())
print("任务组:", tasks['task_groups'].keys())
```

## 在代码中使用

如果你想在代码中动态选择任务：

```python
from src.utils.task_selector import select_tasks

# 选择特定任务
tasks = select_tasks(
    account_type='stu',
    task_config='holiday_task,watch_video'
)

# 使用选中的任务
self.tasks = tasks
```

## 常见场景

### 场景1：快速测试登录功能

```env
SELECTED_TASKS=user_homepage
```

只执行登录首页任务，快速验证登录是否正常并获取用户信息。

**如果学生和教师都有 user_homepage 任务，只想测试学生的：**

```env
SELECTED_TASKS=student:user_homepage
```

这样即使教师账号也有 user_homepage 任务，也只会执行学生版本。

### 场景2：测试视频功能

```env
SELECTED_TASKS=watch_video
```

只测试视频观看和反馈功能。

### 场景3：测试提问功能

```env
SELECTED_TASKS=ask_question
```

只测试学生提问功能。

### 场景4：排除某些任务

如果你想排除某些任务，可以列出所有其他任务：

```env
# 排除 homework_free 和 schedule_task
SELECTED_TASKS=holiday_task,watch_video,outdoor_training,ask_question,download
```

## 调试建议

1. **先测试单个任务**：确认任务名称正确
2. **逐步增加任务**：从单个任务开始，逐步添加
3. **查看日志**：检查日志中的任务选择信息
4. **验证账号类型**：确保任务与账号类型匹配

## 完整配置示例

```env
# .env 文件示例

# API配置
API_HOST=http://xuece-xqdsj-stress.unisolution.cn

# 任务选择配置
# 只执行观看视频和提问任务
SELECTED_TASKS=watch_video,ask_question

# 其他配置...
```

