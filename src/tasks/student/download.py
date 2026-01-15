"""学生查看下载资料任务"""
from locust import task
from ..base import BaseTaskSet


class DownloadBehavior(BaseTaskSet):
    """学生下载资料行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        self.homeworkId = self.user.homeworkId
        self.holidaytaskId = self.user.holidayTaskId
    
    @task
    def get_file_info(self):
        """获取文件信息"""
        self.client.get(
            f"/api/homework/student/holidaytask/homework/resource/get?homeworkId={self.homeworkId}&holidaytaskid={self.holidaytaskId}",
            name="/api/homework/student/holidaytask/homework/resource/get",
            headers=self.user.headers
        )

