"""基础任务类"""
from locust import TaskSet
from typing import Optional, Any


class BaseTaskSet(TaskSet):
    """基础任务集合类，提供通用功能"""
    
    @property
    def user(self):
        """获取用户对象"""
        return self.parent
    
    def safe_get(self, key: str, default: Any = None) -> Any:
        """
        安全获取用户属性
        
        Args:
            key: 属性名
            default: 默认值
        
        Returns:
            Any: 属性值
        """
        return getattr(self.user, key, default)
    
    def ensure_logged_in(self) -> bool:
        """
        确保用户已登录（自动登录检查）
        
        这是一个便捷方法，让任务可以轻松检查并确保用户已登录。
        如果 LOGIN_MODE=task，任务在执行前可以调用此方法确保已登录。
        
        Returns:
            bool: 登录是否成功（True=已登录/登录成功，False=登录失败）
        """
        if hasattr(self.user, 'ensure_logged_in'):
            return self.user.ensure_logged_in()
        else:
            # 如果用户对象没有 ensure_logged_in 方法，返回 False
            return False

