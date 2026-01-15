"""学生查看假期作业列表任务"""
from locust import task
from ..base import BaseTaskSet


class HolidayTaskListBehavior(BaseTaskSet):
    """学生查看假期作业列表行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        # 配置需要压测的目标假期作业id
        self.holidayTaskId = self.user.holidayTaskId
    
    @task
    def open_holiday_task_list(self):
        """打开假期作业列表"""
        self.client.get(
            "/api/usercenter/common/loginuserinfo/myinfo",
            name="/api/usercenter/common/loginuserinfo/myinfo",
            headers=self.user.headers
        )
        
        self.client.get(
            "/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE",
            name="/api/basicdata/common/dictionary/listbytypes",
            headers=self.user.headers
        )
        
        self.client.get(
            "/api/usercenter/common/loginuserinfo/terminfo",
            name="/api/usercenter/common/loginuserinfo/terminfo",
            headers=self.user.headers
        )
        
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
                        if data["status"] == "NOW":
                            self.user.year = data["year"]
                            semesters = data["semesters"]
                            if semesters[0]["status"] == "NOW":
                                self.user.semester = semesters[0]["semester"]
                            else:
                                self.user.semester = semesters[1]["semester"]
                    response.success()
                except Exception as e:
                    response.failure(f"处理响应时出错: {str(e)}")
            else:
                response.failure(f"HTTP错误: {response.status_code}")
        
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
        
        self.client.get(
            "/api/usercenter/common/loginuserinfo/gatekeeper/list",
            name="/api/usercenter/common/loginuserinfo/gatekeeper/list",
            headers=self.user.headers
        )
        
        self.client.get(
            "/api/usercenter/common/loginuserinfo/modulepermission",
            name="/api/usercenter/common/loginuserinfo/modulepermission",
            headers=self.user.headers
        )
        
        self.client.get(
            "/api/usercenter/common/loginuserinfo/myschool",
            name="/api/usercenter/common/loginuserinfo/myschool",
            headers=self.user.headers
        )
        
        params = {
            "finished": False,
            "holidayTaskId": self.holidayTaskId,
            "courseCode": "",
            "startDatetime": "",
            "endDatetime": "",
            "nameLike": "",
            "type": 1,
            "pageNum": 1,
            "pageSize": 10
        }
        
        self.client.get(
            "/api/homework/student/holidaytask/homework/list",
            name="/api/homework/student/holidaytask/homework/list",
            headers=self.user.headers,
            params=params
        )
        
        self.client.get(
            f"/api/homework/student/holidaytask/listshelvedcourse?holidayTaskId={self.holidayTaskId}",
            name="/api/homework/student/holidaytask/listshelvedcourse",
            headers=self.user.headers
        )

