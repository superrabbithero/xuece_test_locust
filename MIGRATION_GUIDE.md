# 迁移指南

从单文件 `locustfile.py` 迁移到新项目结构的指南。

## 📋 主要变化

### 1. 目录结构变化

**旧结构：**
```
xuece_test_locust/
├── locustfile.py (699行)
├── requirements.txt
└── data/
```

**新结构：**
```
xuece_test_locust/
├── src/
│   ├── locustfile.py (精简版)
│   ├── loaders/
│   ├── tasks/
│   ├── users/
│   └── utils/
├── config/
├── requirements.txt
└── data/
```

### 2. 运行方式变化

**旧方式：**
```bash
locust -f locustfile.py --host=http://example.com
```

**新方式：**
```bash
# 1. 先配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 2. 运行（host从.env读取）
locust -f src/locustfile.py

# 或覆盖host
locust -f src/locustfile.py --host=http://example.com
```

### 3. 配置方式变化

**旧方式：** 硬编码在代码中
```python
host = "http://xuece-xqdsj-stress.unisolution.cn"
encryptpwd = 'c34dd995a8132605764a9347dae6e8ca'
```

**新方式：** 通过环境变量配置
```env
API_HOST=http://xuece-xqdsj-stress.unisolution.cn
DEFAULT_PASSWORD=c34dd995a8132605764a9347dae6e8ca
```

## 🔄 迁移步骤

### 步骤1：备份旧文件

```bash
# 备份旧的locustfile.py
cp locustfile.py locustfile.py.backup
```

### 步骤2：创建环境配置

```bash
# 复制环境变量示例
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
API_HOST=http://xuece-xqdsj-stress.unisolution.cn
ACCOUNT_FILE=data/accounts_3000.csv
ACCOUNT_LOADER_TYPE=csv
LOCUST_START=0
LOCUST_END=100
DEFAULT_PASSWORD=c34dd995a8132605764a9347dae6e8ca
```

### 步骤3：安装新依赖

```bash
pip install -r requirements.txt
```

### 步骤4：测试运行

```bash
# 测试运行
locust -f src/locustfile.py --headless -u 1 -r 1 -t 10s
```

如果运行成功，说明迁移完成！

## ⚠️ 注意事项

### 1. 账号文件路径

确保 `data/accounts_3000.csv` 文件存在，或在 `.env` 中配置正确的路径。

### 2. Redis配置（如果使用）

如果之前使用Redis，需要：
1. 在 `.env` 中配置Redis连接信息
2. 设置 `ACCOUNT_LOADER_TYPE=redis`
3. 初始化Redis账号池（见README.md）

### 3. 环境变量优先级

命令行参数 > 环境变量 > 默认值

例如：
```bash
# 命令行参数会覆盖.env中的API_HOST
locust -f src/locustfile.py --host=http://other-host.com
```

## 🔍 功能对比

| 功能 | 旧版本 | 新版本 | 说明 |
|------|--------|--------|------|
| 配置管理 | 硬编码 | 环境变量 | ✅ 更灵活 |
| 账号加载 | CSV | CSV/Redis | ✅ 支持分布式 |
| 日志系统 | print | logging | ✅ 更专业 |
| 代码结构 | 单文件 | 模块化 | ✅ 易维护 |
| 类型提示 | 无 | 有 | ✅ 更清晰 |

## 🐛 常见问题

### Q: 运行时报错 "No module named 'config'"

A: 确保在项目根目录运行，不要进入 `src/` 目录。

### Q: 账号加载失败

A: 检查：
1. `.env` 中的 `ACCOUNT_FILE` 路径是否正确
2. CSV文件是否存在
3. `LOCUST_START` 和 `LOCUST_END` 范围是否有效

### Q: 如何切换回旧版本？

A: 使用备份文件：
```bash
cp locustfile.py.backup locustfile.py
locust -f locustfile.py
```

## 📞 需要帮助？

如果遇到问题，请检查：
1. `logs/locust.log` 日志文件
2. README.md 中的常见问题部分
3. 确保所有依赖已安装

