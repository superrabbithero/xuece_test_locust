"""登录压测任务

在任务中调用用户的登录逻辑，用于把登录接口本身作为压测对象。
"""
from locust import task

from ..base import BaseTaskSet


class LoginOnlyBehavior(BaseTaskSet):
    """仅登录任务

    每次任务执行都会调用一次登录接口。
    """

    @task
    def login_task(self):
        """执行登录请求"""
        # 直接调用用户对象上的登录方法
        # 注意：_login 已经包含完整的错误处理和日志
        self.user._login()



