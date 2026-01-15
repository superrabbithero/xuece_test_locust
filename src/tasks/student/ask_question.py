"""学生提问任务"""
import json
from locust import task
from ..base import BaseTaskSet
from src.utils.helpers import get_current_timestamp


class StuAskQuestion(BaseTaskSet):
    """学生提问行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        self.homeworkId = self.user.homeworkId
        # 题目+视频31692  纯视频31687
        
        # 不配置questionId则是纯视频模式提问 1q161c5j5q
        self.questionId = None
        
        # PHYSICAL,CHINESE
        self.courseCode = "PHYSICAL"  # PHYSICAL
        self.topicId = None
    
    @task(1)
    def get_topic_base_info(self):
        """获取话题基础信息"""
        params = {
            "homeworkId": self.homeworkId,
            "questionId": self.questionId
        }
        
        with self.client.post(
            "/api/qacenter/student/homework/question/topicBasicInfo",
            name="/api/qacenter/student/homework/question/topicBasicInfo",
            params=params,
            headers=self.user.headers
        ) as rst:
            if rst.status_code == 200:
                response_data = rst.json()
                
                if response_data["data"]["topicId"]:
                    self.topicId = response_data["data"]["topicId"]
                    payload = {
                        "pageSize": 30,
                        "pageNum": 1,
                        "topicId": self.topicId,
                        "topicReply": True
                    }
                    
                    self.client.post(
                        "/api/qacenter/student/homework/question/replyList",
                        data=json.dumps(payload),
                        headers=self.user.headers,
                        catch_response=True
                    )
                else:
                    payload = {
                        "resourceId": self.questionId,
                        "paperId": self.homeworkId,
                        "type": "HOMEWORK_HOLIDAY",
                        "courseCode": self.courseCode,
                        "content": {
                            "content": "这是测试数据，压测数据，balabala",
                            "fileInfo": [
                                {
                                    "url": "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/qna/3i0wezy/6ca9eb7dfd734b52816f6756fab49ffb1.jpeg",
                                    "name": "雪山2.jpg",
                                    "type": "IMAGE",
                                    "uploadTime": get_current_timestamp()
                                }
                            ]
                        },
                        "topicIdList": None
                    }
                    
                    self.client.post(
                        '/api/qacenter/student/homework/question/homeworkQuiz',
                        data=json.dumps(payload),
                        headers=self.user.headers
                    )
    
    @task(3)
    def send_quiz(self):
        """发送提问"""
        if not self.topicId:
            return
        
        payload = {
            "resourceId": self.questionId,
            "paperId": self.homeworkId,
            "type": "HOMEWORK_HOLIDAY",
            "courseCode": self.courseCode,
            "content": {
                "content": "这是测试数据，压测数据，balabala",
                "fileInfo": [
                    {
                        "url": "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/qna/3i0wezy/6ca9eb7dfd734b52816f6756fab49ffb1.jpeg",
                        "name": "雪山2.jpg",
                        "type": "IMAGE",
                        "uploadTime": get_current_timestamp()
                    }
                ]
            },
            "topicIdList": [self.topicId]
        }
        
        self.client.post(
            '/api/qacenter/student/homework/question/homeworkQuiz',
            data=json.dumps(payload),
            headers=self.user.headers
        )
        
        payload2 = {
            "pageSize": 30,
            "pageNum": 1,
            "topicId": self.topicId,
            "topicReply": True
        }
        
        self.client.post(
            "/api/qacenter/student/homework/question/replyList",
            data=json.dumps(payload2),
            headers=self.user.headers
        )

