"""学生注册服务任务"""
from locust import task
from ..base import BaseTaskSet
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RegistrationServiceBehavior(BaseTaskSet):
    """学生注册服务行为"""
    
    @task
    def get_registration_service(self):
        """获取学生注册服务信息"""

        # print(self.user.account,"::get_registration_service")
        # logger.info(f'{self.user.account,}::get_registration_service')
        
        # 自动登录检查：如果未登录，自动执行登录
        if not self.ensure_logged_in():
            logger.warning("登录失败，跳过注册服务请求")
            return
        
        # 确保 headers 存在
        if not self.user.headers:
            logger.error("用户 headers 为空，无法发送请求")
            return
        
        response = self.client.get(
            "/api/usercenter/student/registrationservice",
            name="/api/usercenter/student/registrationservice",
            headers=self.user.headers
        )
        
        # 简单打印返回体
        # if hasattr(response, 'text'):
        #     print(f"[注册服务接口响应] {response.text}")

