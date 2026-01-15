"""电商用户类（压测用户）"""
import json
from typing import Dict, Optional
from locust import FastHttpUser, between

from config import get_settings
from src.loaders import CSVAccountLoader, RedisAccountLoader, BaseAccountLoader
from src.utils.helpers import build_headers, print_request, print_response
from src.utils.logger import get_logger
from src.utils.task_selector import select_tasks

logger = get_logger(__name__)


class EcommerceUser(FastHttpUser):
    """压测用户类"""
    
    # 等待时间配置（从配置中读取）
    # 在类定义时从配置读取（此时 .env 应该已经加载）
    _settings_for_wait_time = get_settings()
    wait_time = between(_settings_for_wait_time.WAIT_TIME_MIN, _settings_for_wait_time.WAIT_TIME_MAX)
    
    # 任务列表（根据账号类型动态设置）
    tasks = []
    
    # API主机地址（从配置中读取）
    # 在类定义时从配置读取（此时 .env 应该已经加载）
    _settings_for_host = get_settings()
    host = _settings_for_host.API_HOST
    
    # 账号加载器（类属性，所有实例共享）
    _account_loader: Optional[BaseAccountLoader] = None
    
    def __init__(self, *args, **kwargs):
        """初始化用户"""
        super().__init__(*args, **kwargs)
        self.account: Optional[Dict[str, str]] = None
        self.user_id: Optional[int] = None
        self.auth_token: Optional[str] = None
        self.school_id: Optional[int] = None
        self.headers: Optional[Dict[str, str]] = None
        self.gradeCode: Optional[str] = None
        self.year: Optional[str] = None
        self.semester: Optional[str] = None
        self.holidayTaskId: Optional[str] = None
        self.homeworkId: Optional[str] = None
        self.holidaytaskId: Optional[str] = None  # 注意：原代码中有这个拼写
        self._is_logged_in: bool = False  # 登录状态标记
    
    @classmethod
    def _get_account_loader(cls) -> BaseAccountLoader:
        """获取账号加载器（单例模式）"""
        if cls._account_loader is None:
            settings = get_settings()
            loader_type = settings.ACCOUNT_LOADER_TYPE.lower()
            
            if loader_type == "redis":
                cls._account_loader = RedisAccountLoader()
            else:
                cls._account_loader = CSVAccountLoader()
            
            logger.info(f"使用账号加载器: {loader_type}")
        
        return cls._account_loader
    
    def on_start(self):
        """用户启动时的初始化"""
        # 在运行时获取配置（确保 .env 文件已加载）
        settings = get_settings()
        
        # 打印配置信息（仅第一次，避免重复打印）——精简版，减少控制台噪音
        if not hasattr(EcommerceUser, '_config_printed'):
            print(f"[配置] ENV={settings.ENV}, API_HOST={settings.API_HOST}, "
                  f"WAIT_TIME={settings.WAIT_TIME_MIN}-{settings.WAIT_TIME_MAX}s, "
                  f"ACCOUNT_LOADER_TYPE={settings.ACCOUNT_LOADER_TYPE}, "
                  f"SELECTED_TASKS={settings.SELECTED_TASKS or '(默认)'}")
            logger.info("配置信息已加载")
            EcommerceUser._config_printed = True
        
        # 验证并更新主机地址（从配置中读取，确保使用最新配置）
        # original_host = self.host
        # self.host = settings.API_HOST
        
        # 如果配置被覆盖，记录警告（仅在第一次打印）——改为只打日志，不再大段 print
        # if not hasattr(EcommerceUser, '_host_verified'):
        #     if original_host != settings.API_HOST:
        #         logger.warning(f"主机地址已从 {original_host} 更新为 {settings.API_HOST}")
        #     else:
        #         logger.info(f"主机地址验证通过: {self.host}")
        #     EcommerceUser._host_verified = True
        
        # 只在第一次运行时获取账号，后续不再更换
        if self.account is None:
            # 获取账号
            account_loader = self._get_account_loader()
            self.account = account_loader.get_account()
            
            if not self.account:
                logger.error("无法获取账号，用户初始化失败")
                return
            
            # 根据账号类型和配置选择任务
            account_type = self.account.get('account_type', 'stu')
            selected_tasks = select_tasks(
                account_type=account_type,
                task_config=None  # 使用配置中的 SELECTED_TASKS
            )
            self.tasks = selected_tasks
            
            # 任务选择信息只写日志，避免控制台刷屏
            task_names = [task.__name__ for task in selected_tasks]
            logger.info(
                "账号类型: %s, 选中任务数量: %d, 任务列表: %s, 配置的 SELECTED_TASKS: %s",
                account_type,
                len(selected_tasks),
                ", ".join(task_names),
                settings.SELECTED_TASKS or "(使用默认任务)",
            )
            
            # 初始化用户属性
            self.holidayTaskId = self.account.get('holidayTaskId')
            self.homeworkId = self.account.get('homeworkId')
            self.holidaytaskId = self.account.get('holidayTaskId')  # 兼容原代码拼写
            
            # 连接预热：在业务请求前建立连接，避免首次请求的连接建立开销
            # 这样可以确保业务任务的响应时间更准确（不包含连接建立时间）
            if getattr(settings, "WARMUP_CONNECTION", True):
                self._warmup_connection()
            
            logger.info(f"用户 {id(self)} 使用账号 {self.account.get('username')} 登录")
            
            # 根据登录模式决定是否在 on_start 阶段执行登录
            # LOGIN_MODE = on_start:  在这里统一登录（默认）
            # LOGIN_MODE = task:      不在这里登录，由任务中显式调用（例如 LoginOnlyBehavior）
            login_mode = getattr(settings, "LOGIN_MODE", "on_start")
            if login_mode == "on_start":
                self._login()
            else:
                logger.info("LOGIN_MODE=task，登录将在任务中执行，不在 on_start 中调用")
    
    def _warmup_connection(self):
        """
        预热连接：建立 TCP 连接和 TLS 握手（如果是 HTTPS）
        
        这样可以避免业务任务首次请求时的连接建立开销，
        确保业务请求的响应时间更准确（不包含连接建立时间）。
        
        使用 Locust 的 self.client 建立连接，连接会被复用给后续请求。
        """
        try:
            # 使用 Locust 的 client 发送一个轻量级请求来建立连接
            # 这样可以复用连接池，后续业务请求可以直接使用已建立的连接
            # 使用 HEAD 请求，只获取响应头，不传输响应体，更轻量
            try:
                self.client.head(
                    "/",
                    name="[连接预热]",
                    timeout=5,
                    allow_redirects=True
                )
                logger.debug(f"用户 {id(self)} 连接预热完成（HEAD /）")
            except Exception:
                # 如果 HEAD 请求失败（例如服务器不支持或路径不存在），尝试使用 GET 请求
                self.client.get(
                    "/",
                    name="[连接预热]",
                    timeout=5,
                    allow_redirects=True
                )
                logger.debug(f"用户 {id(self)} 连接预热完成（GET /）")
        except Exception as e:
            # 连接预热失败不影响后续流程，只记录调试信息
            # 业务请求仍然可以正常工作，只是首次请求会包含连接建立时间
            logger.debug(f"用户 {id(self)} 连接预热失败: {str(e)}，业务请求可能包含连接建立时间")
    
    def _login(self):
        """用户登录"""
        if not self.account:
            logger.error("账号信息为空，无法登录")
            return
        
        settings = get_settings()
        params = {
            "username": self.account['username'],
            "encryptpwd": settings.DEFAULT_PASSWORD,
            "clienttype": settings.CLIENT_TYPE,
            "clientversion": settings.CLIENT_VERSION,
            "systemversion": settings.SYSTEM_VERSION
        }
        
        # 打印请求信息（如果启用调试）- 优化：条件调用，避免不必要的函数调用开销
        full_url = f"{self.host}/api/usercenter/nnauth/user/login"
        if settings.DEBUG_REQUESTS:
            print_request(
                method="GET",
                url=full_url,
                params=params,
                headers=None  # 登录时还没有headers
            )
        
        try:
            with self.client.get(
                "/api/usercenter/nnauth/user/login",
                name="用户登录",
                params=params,
                catch_response=True
            ) as response:
                # 打印响应信息（如果启用调试）- 优化：条件调用，避免不必要的函数调用开销
                if settings.DEBUG_RESPONSES:
                    print_response(response, url=full_url)
                
                # 检查响应是否为 None（连接失败的情况）
                if response is None:
                    logger.error(
                        f"用户 {self.account.get('username')} 登录失败: "
                        "连接失败，响应为 None（可能是网络问题或服务器不可达）"
                    )
                    return
                
                # HTTP 0 通常表示连接失败
                if response.status_code == 0:
                    logger.error(
                        f"用户 {self.account.get('username')} 登录失败: "
                        "HTTP 0 - 连接失败（可能是网络问题、超时或服务器不可达）"
                    )
                    response.failure("连接失败")
                    return
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        
                        # 打印完整的响应数据（用于调试）
                        if settings.DEBUG_RESPONSES:
                            print(f"[调试] 完整响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                        
                        data = response_data.get("data") if response_data else None
                        if data is None:
                            logger.error(
                                f"用户 {self.account.get('username')} 登录失败: "
                                f"响应中缺少data字段。完整响应: {json.dumps(response_data, ensure_ascii=False)}"
                            )
                            response.failure("响应中缺少data字段")
                            return
                        
                        user = data.get("user") if isinstance(data, dict) else None
                        if user is None:
                            logger.error(
                                f"用户 {self.account.get('username')} 登录失败: "
                                f"响应中缺少user字段。data内容: {json.dumps(data, ensure_ascii=False)}"
                            )
                            response.failure("响应中缺少user字段")
                            return
                        
                        self.school_id = user.get("schoolId")
                        self.user_id = user.get("id")
                        self.gradeCode = user.get("gradeCode")
                        
                        if self.user_id:
                            self.auth_token = data.get("authtoken")
                            self.headers = build_headers(self.auth_token, self.school_id)
                            self._is_logged_in = True  # 标记为已登录
                            logger.debug(f"用户 {self.account.get('username')} 登录成功")
                            response.success()
                        else:
                            logger.warning(f"用户 {self.account.get('username')} 登录失败：user_id为空")
                            response.failure("user_id为空")
                    except Exception as e:
                        logger.error(f"解析登录响应失败: {str(e)}")
                        # 打印原始响应文本以便调试
                        if hasattr(response, 'text'):
                            logger.error(f"原始响应内容: {response.text[:500]}")
                        response.failure(f"解析响应失败: {str(e)}")
                else:
                    error_msg = f"HTTP {response.status_code}"
                    logger.error(
                        f"用户 {self.account.get('username')} 登录失败: {error_msg}"
                    )
                    response.failure(error_msg)
        except Exception as e:
            # 捕获所有其他异常（包括上下文管理器异常）
            logger.error(
                f"用户 {self.account.get('username')} 登录时发生异常: {str(e)}"
            )
    
    def ensure_logged_in(self) -> bool:
        """
        确保用户已登录（自动登录检查）
        
        如果用户未登录，自动调用 _login() 进行登录。
        如果已登录，直接返回 True，不重复登录。
        
        Returns:
            bool: 登录是否成功（True=已登录/登录成功，False=登录失败）
        """
        # 如果已经登录，直接返回
        if self._is_logged_in and self.auth_token and self.headers:
            return True
        
        # 如果未登录，尝试登录
        logger.debug(f"用户 {self.account.get('username') if self.account else 'unknown'} 未登录，自动执行登录")
        self._login()
        
        # 检查登录是否成功
        if self._is_logged_in and self.auth_token and self.headers:
            return True
        else:
            logger.warning(f"用户 {self.account.get('username') if self.account else 'unknown'} 自动登录失败")
            return False

