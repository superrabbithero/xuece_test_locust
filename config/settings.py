"""配置管理模块"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    # 使用 override=True 确保 .env 文件中的值会覆盖环境变量
    load_dotenv(env_path, override=True)


class Settings:
    """应用配置类"""
    
    # 环境配置
    ENV: str = os.getenv("ENV", "test")
    
    # API配置
    API_HOST: str = os.getenv(
        "API_HOST", 
        "https://xuece-xqdsj-stagingtest1.unisolution.cn"
    )
    
    # 账号配置
    ACCOUNT_FILE: str = os.getenv(
        "ACCOUNT_FILE", 
        "data/accounts_3000.csv"
    )
    ACCOUNT_LOADER_TYPE: str = os.getenv("ACCOUNT_LOADER_TYPE", "csv")  # csv, redis
    
    # Locust配置
    LOCUST_START: int = int(os.getenv("LOCUST_START", "9"))
    LOCUST_END: int = int(os.getenv("LOCUST_END", "1009"))
    
    # 任务选择配置
    # 格式: "all" | "student" | "teacher" | "task1,task2" | None(使用默认)
    # 可用任务: holiday_task, watch_video, outdoor_training, ask_question,
    #          download, homework_free, schedule_task, marking_list
    # 特殊值: all(所有任务), student(所有学生任务), teacher(所有教师任务)
    _selected_tasks = os.getenv("SELECTED_TASKS", "student:user_homepage")
    SELECTED_TASKS: Optional[str] = _selected_tasks if _selected_tasks and _selected_tasks.strip() else None
    
    # Redis配置（如果使用Redis加载器）
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_POOL_KEY: str = os.getenv("REDIS_POOL_KEY", "locust:account_pool")
    
    # 登录配置
    DEFAULT_PASSWORD: str = os.getenv(
        "DEFAULT_PASSWORD", 
        # "c34dd995a8132605764a9347dae6e8ca"
        "3a352bebcc6ac5cc2c6611d751727729"
    )
    CLIENT_TYPE: str = os.getenv("CLIENT_TYPE", "BROWSER")
    CLIENT_VERSION: str = os.getenv("CLIENT_VERSION", "1.30.6")
    SYSTEM_VERSION: str = os.getenv("SYSTEM_VERSION", "chrome137.0.0.0")
    
    # 用户等待时间配置
    WAIT_TIME_MIN: float = float(os.getenv("WAIT_TIME_MIN", "0"))
    WAIT_TIME_MAX: float = float(os.getenv("WAIT_TIME_MAX", "1"))
    
    # 登录模式配置
    # on_start: 在用户 on_start 阶段统一登录（当前默认行为）
    # task:     不在 on_start 登录，由任务中显式调用登录（用于把登录接口当作压测的一部分）
    LOGIN_MODE: str = os.getenv("LOGIN_MODE", "on_start").lower()
    
    # 连接预热配置
    # 在 on_start 阶段先建立连接，避免业务任务首次请求的连接建立开销
    # true: 启用连接预热（推荐，可以确保业务请求的响应时间更准确）
    # false: 禁用连接预热（业务请求首次请求会包含连接建立时间）
    WARMUP_CONNECTION: bool = os.getenv("WARMUP_CONNECTION", "true").lower() == "true"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/locust.log")
    
    # 调试配置
    DEBUG_REQUESTS: bool = os.getenv("DEBUG_REQUESTS", "false").lower() == "true"
    DEBUG_RESPONSES: bool = os.getenv("DEBUG_RESPONSES", "false").lower() == "true"
    
    @classmethod
    def get_account_file_path(cls) -> Path:
        """获取账号文件的完整路径"""
        base_dir = Path(__file__).parent.parent
        return base_dir / cls.ACCOUNT_FILE
    
    @classmethod
    def get_log_file_path(cls) -> Optional[Path]:
        """获取日志文件的完整路径"""
        if not cls.LOG_FILE:
            return None
        base_dir = Path(__file__).parent.parent
        log_path = base_dir / cls.LOG_FILE
        # 确保日志目录存在
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

