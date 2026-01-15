"""教师查看练习监控任务"""
from locust import task
from ..base import BaseTaskSet


class TchMarkingList(BaseTaskSet):
    """教师批改列表行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        self.homeworkId = self.user.homeworkId
    
    @task
    def get_marking_list(self):
        """获取批改列表"""
        params = {
            'holidaytaskId': self.user.holidayTaskId,
            'holidayTaskType': '1',
            'pageNum': '1',
            'pageSize': '5'
        }
        
        self.client.get(
            "/api/homework/teacher/homework/marking/list",
            params=params,
            headers=self.user.headers
        )
    
    @task
    def get_check_list(self):
        """获取检查列表"""
        params = {
            'holidayTaskId': self.user.holidayTaskId,
            'homeworkId': self.user.homeworkId
        }
        
        self.client.get(
            "/api/homework/teacher/homework/monitoring/checkRequireSyncStudents",
            params=params,
            headers=self.user.headers
        )
        
        self.client.get(
            f"/api/homework/teacher/homework/monitoring/info?homeworkId={self.user.homeworkId}",
            headers=self.user.headers
        )
        
        self.client.get(
            f"/api/homework/teacher/homework/monitoring/status/overview?homeworkId={self.user.homeworkId}",
            headers=self.user.headers
        )
        
        self.client.get(
            f"/api/homework/teacher/homework/detail?id={self.user.homeworkId}",
            headers=self.user.headers
        )
        
        self.client.get(
            f"/api/homework/teacher/homework/monitoring/class_info?homeworkId={self.user.homeworkId}",
            headers=self.user.headers
        )
        
        self.client.get(
            f"/api/holidayvideo/teacher/holidayvideo/monitor/video?videoType=VOD&homeworkId={self.user.homeworkId}",
            headers=self.user.headers
        )

