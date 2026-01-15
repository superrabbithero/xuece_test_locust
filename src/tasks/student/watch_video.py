"""学生查看题目加视频的打卡任务"""
import json
from locust import task
from ..base import BaseTaskSet


class WatchVideoBehavior(BaseTaskSet):
    """学生查看视频打卡行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        # 配置需要压测的目标假期作业id
        self.homeworkId = self.user.homeworkId
        self.holidayVideoId = None
        self.videoId = None
    
    @task(1)
    def open_watch_video_page(self):
        """打开观看视频页面"""
        self.client.get(
            f"/api/holidayvideo/student/holidayvideo/notice/list/byhomework?homeworkId={self.homeworkId}&videoType=VOD",
            headers=self.user.headers
        )
        
        with self.client.get(
            f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}",
            name="/api/holidayvideo/student/holidayvideo/info?homeworkId",
            headers=self.user.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.holidayVideoId = response_data["data"]["holidayvideoId"]
                    # 题目+视频
                    # self.videoId = response_data["data"]["homeworkVideos"][0]["videoId"]
                    # 纯视频
                    self.videoId = response_data["data"]["videos"][0]["videoId"]
                    response.success()
                except Exception as e:
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                response.failure(f"Status code: {response.status_code}")
        
        if self.holidayVideoId:
            self.client.get(
                f"/api/holidayvideo/student/holidayvideo/feedbackScore?holidayvideoId={self.holidayVideoId}",
                name="/api/holidayvideo/student/holidayvideo/feedbackScore",
                headers=self.user.headers
            )
    
    @task(1)
    def do_feedback(self):
        """提交视频反馈"""
        if self.holidayVideoId is None or self.videoId is None:
            return
        
        payload = {
            "courseCode": "PHYSICAL",
            "feedback": "",
            "gradeCode": self.user.gradeCode,
            "holidayvideoId": self.holidayVideoId,
            "homeworkId": self.homeworkId,
            "videoId": self.videoId,
            "score": 3
        }
        
        self.client.put(
            "/api/holidayvideo/student/holidayvideo/feedback",
            name="/api/holidayvideo/student/holidayvideo/feedback",
            data=json.dumps(payload),
            headers=self.user.headers
        )

