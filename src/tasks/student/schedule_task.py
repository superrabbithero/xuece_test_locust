"""学生查看和提交打卡任务"""
import json
from locust import task
from ..base import BaseTaskSet


class DoScheduleTask(BaseTaskSet):
    """学生打卡任务行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        self.homeworkId = self.user.homeworkId
    
    @task
    def get_question_list(self):
        """获取题目列表"""
        self.client.get(
            f"/api/homework/student/holidaytask/homework/schedule/get?homeworkId={self.homeworkId}",
            name="/api/homework/student/holidaytask/homework/schedule/get",
            headers=self.user.headers
        )
    
    @task(0)
    def get_detail(self):
        """获取个性化打卡任务详情（权重为0，默认不执行）"""
        self.client.get(
            f"/api/homework/student/holidaytask/special/question/detail/list?homeworkId={self.homeworkId}",
            name="/api/homework/student/holidaytask/special/question/detail/list",
            headers=self.user.headers
        )
    
    @task
    def do_save(self):
        """保存打卡任务"""
        payload = {
            "homeworkId": self.homeworkId,
            "stuAnswer": "测试打卡任务提交啦啦啦，压力测试，压力测试，压力测试修改了",
            "stuAnswerImgUrl": [
                "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/7ccf81e729524169ac2ceb4426aa5f2e1.jpeg",
                "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/b74a285a49134e7386b2599298bd935f1.jpeg",
                "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/8b199f2df9f94f42a141fd0aa4358b221.jpeg"
            ],
            "stuAnswerVoiceUrl": [
                "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/62e972445c8f414b9550816d3ab8547a1.mp3"
            ]
        }
        
        self.client.post(
            "/api/homework/student/holidaytask/homework/schedule/save",
            data=json.dumps(payload),
            headers=self.user.headers
        )

