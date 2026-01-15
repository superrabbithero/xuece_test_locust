"""学生查看和提交自由出题练习任务"""
import json
from locust import task
from ..base import BaseTaskSet


class DoHomeworkFree(BaseTaskSet):
    """学生自由出题练习行为"""
    
    def on_start(self):
        """任务开始时的初始化"""
        self.holidaytaskId = self.user.holidaytaskId
    
    @task
    def get_question_list(self):
        """获取题目列表"""
        self.client.get(
            f"/api/homework/student/homework/get?homeworkId={self.holidaytaskId}",
            headers=self.user.headers
        )
    
    @task(0)
    def do_save(self):
        """保存答案（权重为0，默认不执行）"""
        payload = {
            "homeworkId": self.user.homeworkId,
            "questionInfos": [
                {
                    "questionSeq": "1",
                    "questionType": "MCHOICE",
                    "stuAnswer": "",
                    "isNoAsked": True
                },
                {
                    "questionSeq": "2",
                    "questionType": "MCHOICE",
                    "stuAnswer": "",
                    "isNoAsked": True
                },
                {
                    "questionSeq": "3",
                    "questionType": "MCHOICE",
                    "stuAnswer": "",
                    "isNoAsked": True
                },
                {
                    "questionSeq": "6",
                    "questionType": "SHORTANSWER",
                    "stuAnswerImgUrl": "",
                    "isNoAsked": True
                },
                {
                    "questionSeq": "7",
                    "questionType": "SHORTANSWER",
                    "stuAnswerImgUrl": "",
                    "isNoAsked": True
                }
            ],
            "autoSubmit": True
        }
        
        self.client.post(
            "/api/homework/student/homework/save",
            data=json.dumps(payload),
            headers=self.user.headers
        )
        
        self.client.get(
            "/api/homework/student/holidaytask/homework/list?finished=false&holidayTaskId=758&courseCode=&startDatetime=&endDatetime=&type=1&nameLike=&pageNum=1&pageSize=22",
            headers=self.user.headers
        )

