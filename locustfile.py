from locust import HttpUser, task, between, TaskSet, constant, SequentialTaskSet
import csv
import os
from queue import Queue
import json


class AccountLoader:
    def __init__(self):
        self.accounts = Queue()
        file_path = os.path.join(os.path.dirname(__file__), "data/accounts.csv")
        
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.accounts.put(row)
    
    def get_account(self):
        return self.accounts.get()

account_loader = AccountLoader()

#用户登录首页
class UserLoginBehavior(TaskSet):

    @task
    def get_user_info(self):

        self.client.get("/api/usercenter/common/loginuserinfo/myinfo", headers=self.user.headers)

        self.client.get("/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/terminfo", headers=self.user.headers)

        with self.client.get("/api/usercenter/common/loginuserinfo/terminfo/base", headers=self.user.headers, catch_response=True) as response:
            # print(f"@@@@@@@@@@@@@@响应内容: {response.text}")
            if response.status_code == 200:
                
                try:
                    response_data = response.json()
                    datas = response_data.get("data",[])
                    # print(f"#####################{datas}")
                    for data in datas:
                        # print(f"###############{data['status']}")
                        if(data["status"] == "NOW"):
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

        params={
            "schoolId": f"{self.user.school_id}",
            "year": f"{self.user.year}",
            "semester": self.user.semester
        }

        self.client.get("/api/usercenter/common/school/course/list", headers=self.user.headers, params=params)
    
        self.client.get("/api/usercenter/common/loginuserinfo/gatekeeper/list", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/modulepermission", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/myschool", headers=self.user.headers)

        self.client.get("/api/examcenter/student/exam/querylist_v2?pageNum=1&pageSize=5", headers=self.user.headers)
    
        self.client.get("/api/homework/student/holidaytask/listshelvedtask", headers=self.user.headers)

        self.client.get("/api/holidayvideo/common/holidayvideo/isAuditor", headers=self.user.headers)
    
#学生查看假期作业列表
class HolidayTaskListBehavior(TaskSet):

    def on_start(self):

        #配置需要压测的目标假期作业id
        self.holidayTaskId = 758 

    @task
    def open_holiday_task_list(self):

        self.client.get("/api/usercenter/common/loginuserinfo/myinfo", headers=self.user.headers)

        self.client.get("/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/terminfo", headers=self.user.headers)

        with self.client.get("/api/usercenter/common/loginuserinfo/terminfo/base", headers=self.user.headers, catch_response=True) as response:
            if response.status_code == 200:
                
                try:
                    response_data = response.json()
                    datas = response_data.get("data",[])
                    for data in datas:
                        if(data["status"] == "NOW"):
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

        params={
            "schoolId": f"{self.user.school_id}",
            "year": f"{self.user.year}",
            "semester": self.user.semester
        }

        self.client.get("/api/usercenter/common/school/course/list", headers=self.user.headers, params=params)
    
        self.client.get("/api/usercenter/common/loginuserinfo/gatekeeper/list", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/modulepermission", headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/myschool", headers=self.user.headers)

        params={
            "finished": false,
            "holidayTaskId": self.holidayTaskId,
            "type": 1,
            "pageNum":1,
            "pageSize":10
        }
        
        self.client.get("/api/examcenter/student/exam/querylist_v2?pageNum=1&pageSize=5", headers=self.user.headers,params=params)
    
        self.client.get(f"/api/homework/student/holidaytask/listshelvedcourse?holidayTaskId={self.holidayTaskId}", headers=self.user.headers)

#学生查看题目加视频的打卡任务
class WatchVideoBehavior(TaskSet):
    
    
    def on_start(self):
        #配置需要压测的目标假期作业id
        self.homeworkId = 30799 
        self.holidayVideoId = None

    @task
    def open_watch_video_page(self):

        self.client.get(f"/api/holidayvideo/student/holidayvideo/notice/list/byhomework?homeworkId={self.homeworkId}&videoType=VOD", headers=self.user.headers)
           
        with self.client.get(
            f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}",
            headers=self.user.headers,
            catch_response=True) as response:
            # print(f"响应状态码: {response.status_code}")
            # print(f"响应内容: {response.text}")
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.holidayVideoId = response_data["data"]["holidayvideoId"]
                    response.success()
                except (KeyError, json.JSONDecodeError) as e:
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                response.failure(f"Status code: {response.status_code}")

        self.client.get(f"/api/holidayvideo/student/holidayvideo/feedbackScore?holidayvideoId={self.holidayVideoId}", headers=self.user.headers)    

    @task
    def do_feedback(self):

        payload = {
            "courseCode": "PHYSICAL",
            "feedback": "",
            "gradeCode": "S02",
            "holidayvideoId": 2650,
            "homeworkId": 31537,
            "videoId": "20306ccc422971f08f0f5107e0c90102",
            "score": 3
        }

        self.client.put("/api/holidayvideo/student/holidayvideo/feedback", data=json.dumps(payload), headers=self.user.headers)

#学生查看拓展并完成训练（需要完善一下按查询到的未作答的题目进行提交）
class DoOutdoorTraining(TaskSet):
    def on_start(self):
        self.homeworkId = 31537
    
    @task
    def get_question_list(self):

        self.client.get(f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}", headers=self.user.headers)

        payload = {
            "homeworkId": 31537,
            "questionSeq": 1,
            "stuId": 207910
        }

        self.client.post("/api/homework/student/homework/extraInfo",
            data=json.dumps(payload),
            headers=self.user.headers)

    @task
    def do_save():

        payload = {
            "homeworkId": 31537,
            "extraInfos": [
                {
                "questionSeq": 1,
                "questionExtraInfos": [
                    {
                    "questionId": "1q02cftohg",
                    "stuAnswer": [
                        "C"
                    ],
                    "stuAnswerImgUrl": []
                    }
                ]
                }
            ]
        }

        self.client.post("/api/homework/student/homework/saveExtraInfo",
            data=json.dumps(payload),
            headers=self.user.headers)

#学生提问
class StuAskQuestion(TaskSet):

    def on_start(self):
        self.homeworkId = 31547
        self.questionId = '1q02cftog2'
        self.topicId = None

    @task
    def get_topic_base_info(self):
        with self.client.post(
            f"/api/qacenter/student/homework/question/topicBasicInfo?homeworkId={self.homeworkId}&questionId={self.questionId}",
            headers=self.user.headers
        ) as rst:
            response_data = rst.json()
            print(response_data)
            if response_data["data"]["topicId"]:
                self.topicId = response_data["data"]["topicId"]
                payload = {
                    "pageSize": 30,
                    "pageNum": 1,
                    "topicId": self.topicId,
                    "topicReply": True
                }
                self.client.post("/api/qacenter/student/homework/question/replyList", 
                    data=json.dumps(payload),
                    headers=self.user.headers
                )
    
    @task
    def send_quiz(self):
        if self.topicId:
            payload = {
                "resourceId": self.questionId,
                "paperId": self.homeworkId,
                "type": "HOMEWORK_HOLIDAY",
                "courseCode": "PHYSICAL",
                "content": {
                    "content": "img test",
                    "fileInfo": [
                        {
                            "url": "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/qna/3i0wezy/6ca9eb7dfd734b52816f6756fab49ffb1.jpeg",
                            "name": "雪山2.jpg",
                            "type": "IMAGE",
                            "uploadTime": 1749143533871
                        }
                    ]
                },
                "topicIdList": [self.topicId]
            }

            content = payload["content"]["content"]

            self.client.get(f"/api/holidayvideo/student/holidayvideo/sensitiveword/check?content={content}",headers=self.user.headers)

            self.client.post('/api/qacenter/student/homework/question/homeworkQuiz',
                data=json.dumps(payload),
                headers=self.user.headers    
            )

            payload2 = {
                    "pageSize": 30,
                    "pageNum": 1,
                    "topicId": self.topicId,
                    "topicReply": True
                }
            self.client.post("/api/qacenter/student/homework/question/replyList",
                data=json.dumps(payload),
                headers=self.user.headers
            )

#学生查看下载资料
class DownloadBehavior(TaskSet):
    def on_start(self):
        self.homeworkId = 30499
        self.holidaytaskId = 758

    @task
    def get_file_info(self):
        self.client.get(f"/api/homework/student/holidaytask/homework/resource/get?homeworkId={self.homeworkId}&holidaytaskid={self.holidaytaskId}")

#学生查看和提交自由出题练习
class DoHomeworkFree(TaskSet):
    def on_start(self):
        self.homeworkId = 758
    @task
    def get_question_list(self):
        self.client.get(f"/api/homework/student/homework/get?homeworkId={self.homeworkId}")

    @task(0)
    def do_save(self):
        payload = {
          "homeworkId": 31111,
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

        self.client.post("/api/homework/student/homework/save", data=json.dumps(payload), headers=self.user.headers)

        self.client.get(
            "/api/homework/student/holidaytask/homework/list?finished=false&holidayTaskId=758&courseCode=&startDatetime=&endDatetime=&type=1&nameLike=&pageNum=1&pageSize=22",
            headers=self.user.headers)

#学生查看和提交打卡任务
class DoScheduleTask(TaskSet):
    def on_start(self):
        self.homeworkId = 30779

    @task
    def get_question_list(self):
        self.client.get(f"/api/homework/student/holidaytask/homework/schedule/get?homeworkId={self.homeworkId}")

    @task
    def get_detail(self):
        self.client.get(f"/api/homework/student/holidaytask/special/question/detail/list?homeworkId={self.homeworkId}")

    @task(0)
    def do_save(self):
        payload = {
          "homeworkId": 30779,
          "stuAnswer": "测试数据测试数据",
          "stuAnswerImgUrl": [
            "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/7ccf81e729524169ac2ceb4426aa5f2e1.jpeg",
            "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/b74a285a49134e7386b2599298bd935f1.jpeg",
            "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/8b199f2df9f94f42a141fd0aa4358b221.jpeg"
          ],
          "stuAnswerVoiceUrl": [
            "https://test-xueceresource.oss-cn-shanghai.aliyuncs.com/homework/student/3i0wezx/62e972445c8f414b9550816d3ab8547a1.mp3"
          ]
        }

        self.client.post("/api/homework/student/holidaytask/homework/schedule/save", data=json.dumps(payload), headers=self.user.headers)


class EcommerceUser(HttpUser):
    # wait_time = constant(30)
    wait_time = between(1,5)
    tasks = [StuAskQuestion] # 将SequentialTaskSet分配给用户
    host = "https://xuece-xqdsj-stagingtest1.unisolution.cn"
    

    def on_start(self):
        # 只在第一次运行时获取账号，后续不再更换
        if not hasattr(self,'account'):
            print(hasattr(self,'account'))
            self.account = account_loader.get_account()
            self.user_id = id(self)
            print(f"用户{self.user_id}固定使用账号 {self.account['username']} 登录")
            self.auth_token = None
            self.school_id = None
            self.headers = None
            self._login()

    def _login(self):
        params = {
            "username":self.account['username'],
            "encryptpwd":'c34dd995a8132605764a9347dae6e8ca', #测试数据统一密码
            "clienttype":"BROWSER",
            "clientversion":"1.30.6",
            "systemversion":"chrome136.0.0.0"
        }
        # self.client.get("/login", params=params)
        with self.client.get("/api/usercenter/nnauth/user/login", params=params, catch_response=True) as response:
            # print(f"响应状态码: {response.status_code}")
            # print(f"响应内容: {response.text}")
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    school_id = response_data["data"]["user"]["schoolId"]
                    auth_token = response_data["data"]["authtoken"]

                    self.auth_token = auth_token
                    self.school_id = school_id

                    self.headers = {
                        "Authtoken":self.auth_token,
                        "xc-app-user-schoolid":f"{self.school_id}",
                        "Content-Type": "application/json"
                    }

                    response.success()
                except (KeyError, json.JSONDecodeError) as e:
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                response.failure(f"Status code: {response.status_code}")


