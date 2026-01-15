# 学测压测自动化脚本

专业的Locust压测脚本项目，支持多环境配置、模块化任务管理和分布式压测。

## 📋 项目特性

- ✅ **模块化设计**：代码按功能拆分，易于维护和扩展
- ✅ **配置管理**：支持多环境配置，通过环境变量灵活切换
- ✅ **多种账号加载方式**：支持CSV文件和Redis分布式加载
- ✅ **任务模块化**：学生和教师任务独立管理
- ✅ **日志系统**：完善的日志记录和错误追踪
- ✅ **类型提示**：完整的类型注解，提高代码可读性

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，配置你的环境参数：

```env
# API配置
API_HOST=http://xuece-xqdsj-stress.unisolution.cn

# 账号配置
ACCOUNT_FILE=data/accounts_3000.csv
ACCOUNT_LOADER_TYPE=csv  # 或 redis

# Locust配置
LOCUST_START=0
LOCUST_END=100
```

### 3. 运行压测

```bash
# 使用默认配置
locust -f src/locustfile.py

# 指定主机（会覆盖.env中的配置）
locust -f src/locustfile.py --host=http://example.com

# 无Web界面运行（命令行模式）
locust -f src/locustfile.py --headless -u 100 -r 10 -t 60s
```

### 4. 访问Web界面

打开浏览器访问：`http://localhost:8089`

## 📁 项目结构

```
xuece_test_locust/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖管理
├── .env.example              # 环境变量示例
│
├── config/                   # 配置管理
│   ├── __init__.py
│   └── settings.py           # 配置加载
│
├── src/                      # 源代码目录
│   ├── locustfile.py         # Locust入口文件
│   │
│   ├── loaders/              # 账号加载器
│   │   ├── base.py           # 基础加载器接口
│   │   ├── csv_loader.py     # CSV文件加载器
│   │   └── redis_loader.py   # Redis加载器
│   │
│   ├── tasks/                # 任务集合
│   │   ├── base.py           # 基础任务类
│   │   ├── student/          # 学生相关任务
│   │   └── teacher/          # 教师相关任务
│   │
│   ├── users/                # 用户类
│   │   └── ecommerce_user.py
│   │
│   └── utils/                # 工具类
│       ├── logger.py         # 日志工具
│       ├── response_validator.py  # 响应验证
│       └── helpers.py         # 辅助函数
│
├── data/                     # 测试数据
│   └── accounts_3000.csv
│
├── reports/                  # 测试报告
└── logs/                     # 日志文件
```

## ⚙️ 配置说明

### 环境变量配置

主要配置项说明：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `API_HOST` | API服务器地址 | `http://xuece-xqdsj-stress.unisolution.cn` |
| `ACCOUNT_FILE` | 账号CSV文件路径 | `data/accounts_3000.csv` |
| `ACCOUNT_LOADER_TYPE` | 账号加载器类型（csv/redis） | `csv` |
| `LOCUST_START` | 账号起始索引 | `0` |
| `LOCUST_END` | 账号结束索引（0表示全部） | `0` |
| `WAIT_TIME_MIN` | 最小等待时间（秒） | `0` |
| `WAIT_TIME_MAX` | 最大等待时间（秒） | `1` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### Redis配置（如果使用Redis加载器）

```env
REDIS_HOST=192.168.0.119
REDIS_PORT=6379
REDIS_DB=0
REDIS_POOL_KEY=locust:account_pool
```

## 📝 任务说明

### 学生任务

- **HolidayTaskListBehavior**: 查看假期作业列表
- **WatchVideoBehavior**: 观看视频打卡
- **DoOutdoorTraining**: 户外训练
- **StuAskQuestion**: 学生提问
- **DownloadBehavior**: 下载资料
- **DoHomeworkFree**: 自由出题练习
- **DoScheduleTask**: 打卡任务

### 教师任务

- **TchMarkingList**: 查看练习监控和批改列表

## 🔧 账号管理

### CSV文件加载

默认使用CSV文件加载账号，CSV文件格式：

```csv
username,password,account_type,holidayTaskId,homeworkId
user1,password1,stu,123,456
user2,password2,tch,123,456
```

### Redis分布式加载

1. 初始化Redis账号池：

```python
from src.loaders import RedisAccountLoader

loader = RedisAccountLoader()
loader.init_accounts("data/accounts_3000.csv")
```

2. 配置环境变量：

```env
ACCOUNT_LOADER_TYPE=redis
REDIS_HOST=192.168.0.119
REDIS_PORT=6379
```

## 📊 报告查看

压测报告会保存在 `reports/` 目录下，可以通过以下方式查看：

1. **Web界面**：访问 `http://localhost:8089` 查看实时统计
2. **HTML报告**：使用 `--html` 参数生成HTML报告
3. **CSV报告**：使用 `--csv` 参数生成CSV报告

```bash
# 生成HTML报告
locust -f src/locustfile.py --headless -u 100 -r 10 -t 60s --html reports/report.html

# 生成CSV报告
locust -f src/locustfile.py --headless -u 100 -r 10 -t 60s --csv reports/stats
```

## 🐛 常见问题

### 1. 无法获取账号

- 检查 `ACCOUNT_FILE` 路径是否正确
- 检查CSV文件格式是否正确
- 检查 `LOCUST_START` 和 `LOCUST_END` 范围是否有效

### 2. Redis连接失败

- 检查Redis服务是否运行
- 检查 `REDIS_HOST` 和 `REDIS_PORT` 配置
- 检查网络连接

### 3. 登录失败

- 检查账号密码是否正确
- 检查 `DEFAULT_PASSWORD` 配置
- 查看日志文件了解详细错误信息

## 🔄 从旧版本迁移

如果你之前使用的是单文件 `locustfile.py`，迁移步骤：

1. 备份旧的 `locustfile.py`
2. 使用新的项目结构
3. 创建 `.env` 文件并配置环境变量
4. 运行 `locust -f src/locustfile.py`

## 📚 开发指南

### 添加新任务

1. 在 `src/tasks/student/` 或 `src/tasks/teacher/` 中创建新文件
2. 继承 `BaseTaskSet` 类
3. 在 `src/users/ecommerce_user.py` 中添加到任务列表

### 添加新的账号加载器

1. 在 `src/loaders/` 中创建新文件
2. 继承 `BaseAccountLoader` 类
3. 实现 `get_account()`, `has_accounts()`, `get_total_count()` 方法
4. 在 `src/users/ecommerce_user.py` 中添加加载逻辑

## 📄 许可证

本项目仅供内部使用。

## 👥 贡献

欢迎提交Issue和Pull Request！

