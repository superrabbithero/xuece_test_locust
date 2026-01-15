"""学生登录首页任务"""
from locust import task
from ..base import BaseTaskSet
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserHomepageBehavior(BaseTaskSet):
    """学生登录首页行为 - 获取用户信息和首页数据"""
    
    @task
    def get_user_info(self):
        """获取用户信息和首页数据"""
        # 自动登录检查：如果未登录，自动执行登录
        if not self.ensure_logged_in():
            logger.warning("登录失败，跳过首页数据请求")
            return
        
        # 确保 headers 存在
        if not self.user.headers:
            logger.error("用户 headers 为空，无法发送请求")
            return
        
        # 获取用户信息
        self.client.get(
            "/api/usercenter/common/loginuserinfo/myinfo",
            name="/api/usercenter/common/loginuserinfo/myinfo",
            headers=self.user.headers
        )
        
        # 获取字典数据
        self.client.get(
            "/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE",
            name="/api/basicdata/common/dictionary/listbytypes",
            headers=self.user.headers
        )
        
        # 获取学期信息
        self.client.get(
            "/api/usercenter/common/loginuserinfo/terminfo",
            name="/api/usercenter/common/loginuserinfo/terminfo",
            headers=self.user.headers
        )
        
        # 获取学期基础信息并解析
        with self.client.get(
            "/api/usercenter/common/loginuserinfo/terminfo/base",
            name="/api/usercenter/common/loginuserinfo/terminfo/base",
            headers=self.user.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    datas = response_data.get("data", [])
                    
                    for data in datas:
                        if data.get("status") == "NOW":
                            self.user.year = data.get("year")
                            semesters = data.get("semesters", [])
                            if semesters and len(semesters) > 0:
                                if semesters[0].get("status") == "NOW":
                                    self.user.semester = semesters[0].get("semester")
                                elif len(semesters) > 1:
                                    self.user.semester = semesters[1].get("semester")
                    response.success()
                except Exception as e:
                    response.failure(f"处理响应时出错: {str(e)}")
            else:
                response.failure(f"HTTP错误: {response.status_code}")
        
        # 获取课程列表
        params = {
            "schoolId": f"{self.user.school_id}",
            "year": f"{self.user.year}",
            "semester": self.user.semester
        }
        
        self.client.get(
            "/api/usercenter/common/school/course/list",
            name="/api/usercenter/common/school/course/list",
            headers=self.user.headers,
            params=params
        )
        
        # 获取门禁列表
        self.client.get(
            "/api/usercenter/common/loginuserinfo/gatekeeper/list",
            name="/api/usercenter/common/loginuserinfo/gatekeeper/list",
            headers=self.user.headers
        )
        
        # 获取模块权限
        self.client.get(
            "/api/usercenter/common/loginuserinfo/modulepermission",
            name="/api/usercenter/common/loginuserinfo/modulepermission",
            headers=self.user.headers
        )
        
        # 获取我的学校信息
        self.client.get(
            "/api/usercenter/common/loginuserinfo/myschool",
            name="/api/usercenter/common/loginuserinfo/myschool",
            headers=self.user.headers
        )
        
        # 获取考试列表
        self.client.get(
            "/api/examcenter/student/exam/querylist_v2?pageNum=1&pageSize=5",
            name="/api/examcenter/student/exam/querylist_v2",
            headers=self.user.headers
        )
        
        # 获取假期作业列表
        self.client.get(
            "/api/homework/student/holidaytask/listshelvedtask",
            name="/api/homework/student/holidaytask/listshelvedtask",
            headers=self.user.headers
        )
        
        # 检查是否为审核员
        self.client.get(
            "/api/holidayvideo/common/holidayvideo/isAuditor",
            name="/api/holidayvideo/common/holidayvideo/isAuditor",
            headers=self.user.headers
        )

