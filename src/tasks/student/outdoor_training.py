"""学生查看拓展并完成训练任务"""
import json
from locust import task
from ..base import BaseTaskSet


class DoOutdoorTraining(BaseTaskSet):
    """学生户外训练任务（需要完善一下按查询到的未作答的题目进行提交）"""
    
    def on_start(self):
        """任务开始时的初始化"""
        # self.homeworkId = self.user.homeworkId
        self.homeworkId = 70073  # TODO: 应该从配置或用户属性获取
        self.questionId = None
    
    @task(1)
    def get_question_list(self):
        """获取题目列表"""
        self.client.get(
            f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}",
            headers=self.user.headers
        )
        
        payload = {
            "homeworkId": self.homeworkId,
            "questionSeq": 1,
            "stuId": self.user.user_id
        }
        
        with self.client.post(
            "/api/homework/student/homework/extraInfo",
            data=json.dumps(payload),
            headers=self.user.headers
        ) as rsp:
            rsp_data = rsp.json().get("data", None)
            
            try:
                if rsp_data and len(rsp_data) > 0:
                    self.questionId = rsp_data[0].get("questionId", None)
            except Exception as e:
                print(f"解析失败: {str(e)}")
    
    @task(1)
    def do_save(self):
        """保存答案"""
        if self.questionId is None:
            return
        
        payload = {
            "homeworkId": self.homeworkId,
            "extraInfos": [
                {
                    "questionSeq": 1,
                    "questionExtraInfos": [
                        {
                            "questionId": self.questionId,
                            "stuAnswer": ["B"],
                            "stuAnswerImgUrl": []
                        }
                    ]
                }
            ]
        }
        
        self.client.post(
            "/api/homework/student/homework/saveExtraInfo",
            data=json.dumps(payload),
            headers=self.user.headers
        )

