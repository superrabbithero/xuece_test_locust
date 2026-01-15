# 压测脚本专业化重构方案

## 📋 当前问题分析

### 1. 代码结构问题
- ❌ 所有代码（699行）集中在一个 `locustfile.py` 文件中
- ❌ 缺乏模块化，业务逻辑、配置、工具类混在一起
- ❌ 硬编码值过多（host、密码、ID等）
- ❌ 注释掉的代码未清理（Redis账号加载器）

### 2. 扩展性问题
- ❌ 配置管理缺失，无法灵活切换环境
- ❌ 账号加载方式单一，Redis方案被注释
- ❌ 缺少日志系统
- ❌ 缺少测试报告和结果分析
- ❌ 错误处理不完善

### 3. 专业性问题
- ❌ 缺少项目文档和README
- ❌ 依赖管理不完整（requirements.txt只有locust）
- ❌ 缺少代码规范和类型提示
- ❌ 没有环境配置示例

---

## 🎯 重构目标

1. **模块化设计**：按功能拆分代码，提高可维护性
2. **配置管理**：支持多环境配置，易于切换
3. **扩展性**：支持多种账号加载方式，易于添加新功能
4. **专业性**：完善文档、依赖管理、代码规范

---

## 📁 推荐的项目结构

```
xuece_test_locust/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖管理
├── .gitignore               # Git忽略文件
├── .env.example             # 环境变量示例
├── pyproject.toml           # 项目配置（可选，用于代码规范）
│
├── config/                  # 配置管理
│   ├── __init__.py
│   ├── settings.py          # 配置加载
│   └── environments/        # 环境配置
│       ├── dev.yaml
│       ├── test.yaml
│       └── prod.yaml
│
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── locustfile.py        # Locust入口文件（精简版）
│   │
│   ├── loaders/             # 账号加载器
│   │   ├── __init__.py
│   │   ├── base.py          # 基础加载器接口
│   │   ├── csv_loader.py    # CSV文件加载器
│   │   └── redis_loader.py  # Redis加载器
│   │
│   ├── tasks/               # 任务集合
│   │   ├── __init__.py
│   │   ├── base.py          # 基础任务类
│   │   ├── student/         # 学生相关任务
│   │   │   ├── __init__.py
│   │   │   ├── holiday_task.py
│   │   │   ├── watch_video.py
│   │   │   ├── outdoor_training.py
│   │   │   ├── ask_question.py
│   │   │   ├── download.py
│   │   │   ├── homework_free.py
│   │   │   └── schedule_task.py
│   │   └── teacher/         # 教师相关任务
│   │       ├── __init__.py
│   │       └── marking_list.py
│   │
│   ├── users/               # 用户类
│   │   ├── __init__.py
│   │   └── ecommerce_user.py
│   │
│   ├── utils/               # 工具类
│   │   ├── __init__.py
│   │   ├── logger.py        # 日志工具
│   │   ├── response_validator.py  # 响应验证
│   │   └── helpers.py       # 辅助函数
│   │
│   └── api/                 # API客户端封装（可选）
│       ├── __init__.py
│       └── client.py
│
├── data/                    # 测试数据
│   ├── accounts_3000.csv
│   └── accounts.csv
│
├── reports/                 # 测试报告（gitignore）
│   └── .gitkeep
│
├── logs/                    # 日志文件（gitignore）
│   └── .gitkeep
│
└── tests/                   # 单元测试（可选）
    ├── __init__.py
    └── test_loaders.py
```

---

## 🔧 核心改进点

### 1. 配置管理

**创建 `config/settings.py`**：
- 使用 `python-dotenv` 加载环境变量
- 支持 YAML/JSON 配置文件
- 支持多环境（dev/test/prod）
- 集中管理所有配置项

**配置项包括**：
- API 主机地址
- Redis 连接信息
- 账号文件路径
- 登录参数
- 任务权重配置
- 等待时间配置

### 2. 账号加载器抽象

**创建 `src/loaders/base.py`**：
```python
from abc import ABC, abstractmethod

class BaseAccountLoader(ABC):
    @abstractmethod
    def get_account(self):
        """获取一个账号"""
        pass
    
    @abstractmethod
    def has_accounts(self) -> bool:
        """检查是否还有可用账号"""
        pass
```

**实现多种加载器**：
- `CSVAccountLoader`: CSV文件加载
- `RedisAccountLoader`: Redis分布式加载
- `DatabaseAccountLoader`: 数据库加载（未来扩展）

### 3. 任务模块化

**每个业务场景独立文件**：
- 学生任务：`src/tasks/student/`
- 教师任务：`src/tasks/teacher/`
- 基础任务类：提供通用功能（响应验证、错误处理等）

### 4. 日志系统

**创建 `src/utils/logger.py`**：
- 使用 `logging` 模块
- 支持文件和控制台输出
- 不同级别日志（DEBUG/INFO/WARNING/ERROR）
- 日志轮转和归档

### 5. 响应验证工具

**创建 `src/utils/response_validator.py`**：
- 统一响应验证逻辑
- 提取公共的响应处理代码
- 减少重复代码

### 6. 环境管理

**创建 `.env.example`**：
```env
# 环境配置
ENV=test

# API配置
API_HOST=http://xuece-xqdsj-stress.unisolution.cn

# 账号配置
ACCOUNT_FILE=data/accounts_3000.csv
ACCOUNT_LOADER_TYPE=csv  # csv, redis

# Redis配置（如果使用Redis加载器）
REDIS_HOST=192.168.0.119
REDIS_PORT=6379
REDIS_DB=0

# Locust配置
LOCUST_START=0
LOCUST_END=100

# 登录配置
DEFAULT_PASSWORD=c34dd995a8132605764a9347dae6e8ca
CLIENT_VERSION=1.30.6
```

---

## 📦 依赖管理改进

**更新 `requirements.txt`**：
```txt
# 核心依赖
locust==2.37.5

# 配置管理
python-dotenv==1.0.0
pyyaml==6.0.1

# Redis支持
redis==5.0.1

# 日志增强
colorlog==6.8.0

# 代码质量（开发依赖）
pytest==7.4.3
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

---

## 🚀 使用方式改进

### 重构前
```bash
locust -f locustfile.py --host=http://xuece-xqdsj-stress.unisolution.cn
```

### 重构后
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 2. 运行压测
locust -f src/locustfile.py

# 3. 或使用配置文件
locust -f src/locustfile.py --config config/environments/test.yaml
```

---

## 📝 文档完善

### README.md 应包含：
1. 项目简介
2. 快速开始
3. 配置说明
4. 任务说明
5. 账号管理
6. 报告查看
7. 常见问题

---

## ✅ 实施步骤建议

### 阶段一：基础重构（1-2天）
1. ✅ 创建新的目录结构
2. ✅ 拆分配置管理模块
3. ✅ 拆分账号加载器
4. ✅ 创建基础工具类

### 阶段二：任务模块化（2-3天）
1. ✅ 拆分学生任务到独立文件
2. ✅ 拆分教师任务到独立文件
3. ✅ 提取公共逻辑到基类

### 阶段三：增强功能（1-2天）
1. ✅ 添加日志系统
2. ✅ 完善错误处理
3. ✅ 添加响应验证工具
4. ✅ 完善Redis加载器

### 阶段四：文档和优化（1天）
1. ✅ 编写README文档
2. ✅ 添加代码注释和类型提示
3. ✅ 代码规范检查
4. ✅ 测试验证

---

## 🎨 代码质量提升

### 1. 类型提示
```python
from typing import Dict, Optional, List

def get_account(self) -> Optional[Dict[str, str]]:
    """获取账号"""
    pass
```

### 2. 文档字符串
```python
class CSVAccountLoader(BaseAccountLoader):
    """
    CSV文件账号加载器
    
    从CSV文件中读取账号信息，支持分片加载。
    """
    pass
```

### 3. 错误处理
```python
try:
    account = loader.get_account()
except AccountExhaustedException as e:
    logger.error(f"账号池已耗尽: {e}")
    raise
```

---

## 🔄 向后兼容

重构过程中保持：
- 原有的功能不变
- 支持原有的运行方式（逐步迁移）
- 数据格式兼容

---

## 📊 预期收益

1. **可维护性** ⬆️ 80%：代码模块化，易于定位和修改
2. **扩展性** ⬆️ 90%：新功能添加更容易
3. **可读性** ⬆️ 70%：结构清晰，职责明确
4. **专业性** ⬆️ 85%：符合项目规范，便于团队协作

---

## 💡 额外建议

1. **CI/CD集成**：添加GitHub Actions或GitLab CI，自动化测试
2. **监控集成**：集成Prometheus/Grafana监控压测指标
3. **数据生成器**：创建测试数据生成工具
4. **报告分析**：添加报告自动分析和告警
5. **分布式支持**：完善多机器分布式压测支持

---

## 下一步行动

您希望我：
1. **直接开始重构**：按照上述方案逐步实施
2. **先创建基础结构**：搭建目录和配置文件框架
3. **分模块重构**：先重构某个具体模块作为示例

请告诉我您的偏好，我将开始实施！

