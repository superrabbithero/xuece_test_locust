from locust import FastHttpUser, task, between, TaskSet, constant, SequentialTaskSet
import csv
import os
from queue import Queue
import redis
import json
import time
from redis.exceptions import WatchError


# 本地分配账号
class AccountLoader:
    def __init__(self):
        start = int(os.getenv("LOCUST_START", "0"))
        end = int(os.getenv("LOCUST_END", "0"))
        self.accounts = Queue()
        file_path = os.path.join(os.path.dirname(__file__), "data/accounts_3000.csv")
        
        self.total_workers = 3

        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            all_rows = list(reader)  # 读取所有行
            # 计算每个worker分配的起始和结束位置
            total_accounts = len(all_rows)
            
            end = min(total_accounts, end)

            print(start,end)

            for row in all_rows[start:end]:
                # print(row)
                self.accounts.put(row)
    
    def get_account(self):
        return self.accounts.get()

account_loader = AccountLoader()

# Redis 账号池管理类
# class RedisAccountLoader:
#     def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):

#         self.redis = redis.StrictRedis(
#             host=redis_host,
#             port=redis_port,
#             db=redis_db,
#             decode_responses=True
#         )

#         self.pool_key = "locust:account_pool"

#         self.init_accounts()
        
#     def init_accounts(self):
#         """初始化时将账号导入Redis（每次调用前先清空现有数据）"""
#         # 先删除现有的账号池数据
#         self.redis.delete(self.pool_key)

#         """初始化时将账号导入Redis（只需运行一次）"""
#         file_path = os.path.join(os.path.dirname(__file__), "data/accounts_3000.csv")
#         with open(file_path, newline='') as csvfile:
#             reader = csv.DictReader(csvfile)

#             for row in reader:
#                 self.redis.rpush(self.pool_key, json.dumps(row))
    
#     # def get_account(self):
#     #     """原子化获取账号（LPOP操作是原子的）"""
#     #     account_data = self.redis.lpop(self.pool_key)
#     #     if not account_data:
#     #         raise Exception("No accounts available in Redis pool!")
#     #     return json.loads(account_data)

#     def get_account(self):
#         """使用 Redis 事务确保原子性获取账号"""
#         with self.redis.pipeline() as pipe:
#             while True:
#                 try:
#                     # 开启监视
#                     pipe.watch(self.pool_key)
#                     # 检查列表是否为空
#                     if not pipe.llen(self.pool_key):
#                         raise Exception("No accounts available in Redis pool!")
#                     # 开始事务
#                     pipe.multi()
#                     pipe.lpop(self.pool_key)
#                     result = pipe.execute()[0]
#                     return json.loads(result)
#                 except WatchError:
#                     # 如果其他客户端修改了数据，重试
#                     continue
#                 finally:
#                     pipe.reset()

# # 初始化Redis账号池
# redis_loader = RedisAccountLoader(redis_host='192.168.0.119')

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
                response.failure(f"HTTP错误: {response.status_code}",self.user.account["username"])

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
        self.holidayTaskId = self.user.holidayTaskId 

    @task
    def open_holiday_task_list(self):

        self.client.get("/api/usercenter/common/loginuserinfo/myinfo", 
            name="/api/usercenter/common/loginuserinfo/myinfo",headers=self.user.headers)

        self.client.get("/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE", 
            name="/api/basicdata/common/dictionary/listbytypes",
            headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/terminfo", 
            name="/api/usercenter/common/loginuserinfo/terminfo",
            headers=self.user.headers)

        with self.client.get("/api/usercenter/common/loginuserinfo/terminfo/base", 
            name="/api/usercenter/common/loginuserinfo/terminfo/base",
            headers=self.user.headers, catch_response=True) as response:
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

        self.client.get("/api/usercenter/common/school/course/list", 
            name="/api/usercenter/common/school/course/list",
            headers=self.user.headers, params=params)
    
        self.client.get("/api/usercenter/common/loginuserinfo/gatekeeper/list", 
            name="/api/usercenter/common/loginuserinfo/gatekeeper/list",
            headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/modulepermission", 
            name="/api/usercenter/common/loginuserinfo/modulepermission",
            headers=self.user.headers)

        self.client.get("/api/usercenter/common/loginuserinfo/myschool", 
            name="/api/usercenter/common/loginuserinfo/myschool",
            headers=self.user.headers)

        params={
            "finished": False,
            "holidayTaskId": self.holidayTaskId,
            "courseCode":"",
            "startDatetime":"",
            "endDatetime":"",
            "nameLike":"",
            "type": 1,
            "pageNum":1,
            "pageSize":10
        }
        
        self.client.get("/api/homework/student/holidaytask/homework/list", 
            name="/api/homework/student/holidaytask/homework/list"
            ,headers=self.user.headers,params=params)
        
        self.client.get(f"/api/homework/student/holidaytask/listshelvedcourse?holidayTaskId={self.holidayTaskId}",
        name="/api/homework/student/holidaytask/listshelvedcourse",
         headers=self.user.headers) 

#学生查看题目加视频的打卡任务
class WatchVideoBehavior(TaskSet):
    
    
    def on_start(self):
        #配置需要压测的目标假期作业id
        self.homeworkId = self.user.homeworkId 
        self.holidayVideoId = None
        self.videoId = None

    @task(1)
    def open_watch_video_page(self):

        self.client.get(f"/api/holidayvideo/student/holidayvideo/notice/list/byhomework?homeworkId={self.homeworkId}&videoType=VOD", headers=self.user.headers)
           
        with self.client.get(
            f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}",
            name="/api/holidayvideo/student/holidayvideo/info?homeworkId",
            headers=self.user.headers,
            catch_response=True) as response:
            # print(f"响应状态码: {response.status_code}")
            # print(f"响应内容: {response.text}")


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
                    print(f"解析响应失败: {str(e)}")
            else:
                response.failure(f"Status code: {response.status_code}")
                print(response.status_code,response.json())

        self.client.get(f"/api/holidayvideo/student/holidayvideo/feedbackScore?holidayvideoId={self.holidayVideoId}", 
            name="/api/holidayvideo/student/holidayvideo/feedbackScore",
            headers=self.user.headers)  


    @task(1)
    def do_feedback(self):

        if self.holidayVideoId == None or self.videoId == None:
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

        self.client.put("/api/holidayvideo/student/holidayvideo/feedback", 
            name="/api/holidayvideo/student/holidayvideo/feedback",
            data=json.dumps(payload), headers=self.user.headers)

#学生查看拓展并完成训练（需要完善一下按查询到的未作答的题目进行提交）
class DoOutdoorTraining(TaskSet):
    def on_start(self):
        # self.homeworkId = self.user.homeworkId
        self.homeworkId = 70073
        self.questionId = None
    
    @task(1)
    def get_question_list(self):

        self.client.get(f"/api/holidayvideo/student/holidayvideo/info?homeworkId={self.homeworkId}", headers=self.user.headers)

        payload = {
            "homeworkId": self.homeworkId,
            "questionSeq": 1,
            "stuId": self.user.user_id
        }

        with self.client.post("/api/homework/student/homework/extraInfo",
            data=json.dumps(payload),
            headers=self.user.headers)as rsp:
            rsp_data = rsp.json().get("data",None)

            try:
                self.questionId = rsp_data[0].get("questionId",None)
            except Exception as e:
                print("解析失败")

    @task(1)
    def do_save(self):
        if self.questionId == None:
            return
        payload = {
            "homeworkId": self.homeworkId,
            "extraInfos": [
                {
                "questionSeq": 1,
                "questionExtraInfos": [
                    {
                    "questionId": self.questionId,
                    "stuAnswer": [
                        "B"
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
        self.homeworkId = self.user.homeworkId  
        #题目+视频31692  纯视频31687

        #不配置questionId则是纯视频模式提问 1q161c5j5q
        self.questionId = None 
        
        #PHYSICAL,CHINESE
        self.courseCode = "PHYSICAL" #PHYSICAL
        self.topicId = None

    @task(1)
    def get_topic_base_info(self):
        params = {
            "homeworkId": self.homeworkId ,
            "questionId": self.questionId
        }

        # print(params)

        with self.client.post(
            "/api/qacenter/student/homework/question/topicBasicInfo",
            name="/api/qacenter/student/homework/question/topicBasicInfo",
            params=params,
            headers=self.user.headers
        ) as rst:
            # print(self.user.account['username'])
            # if self.user.account['username'] == "locustTestStu3000":
            #     print(rst.status_code)
            # print(rst.status_code)
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

                    self.client.post("/api/qacenter/student/homework/question/replyList", 
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
                                    "uploadTime": int(time.time() * 1000)
                                }
                            ]
                        },
                        "topicIdList": None
                    }

                    self.client.post('/api/qacenter/student/homework/question/homeworkQuiz',
                        data=json.dumps(payload),
                        headers=self.user.headers   
                    )


    
    @task(3)
    def send_quiz(self):
        if self.topicId:
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
                            "uploadTime": int(time.time() * 1000)
                        }
                    ]
                },
                "topicIdList": [self.topicId]
            }

            content = payload["content"]["content"]

            # params

            # with self.client.get(f"/api/holidayvideo/student/holidayvideo/sensitiveword/check?content={content}",headers=self.user.headers)as rsp:                    
            #     print(rsp)

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
                data=json.dumps(payload2),
                headers=self.user.headers
            )


#学生查看下载资料
class DownloadBehavior(TaskSet):
    def on_start(self):
        self.homeworkId = self.user.homeworkId
        self.holidaytaskId = self.user.holidayTaskId

    @task
    def get_file_info(self):
        self.client.get(f"/api/homework/student/holidaytask/homework/resource/get?homeworkId={self.homeworkId}&holidaytaskid={self.holidaytaskId}",
            name="/api/homework/student/holidaytask/homework/resource/get",
            headers=self.user.headers)

#学生查看和提交自由出题练习
class DoHomeworkFree(TaskSet):
    def on_start(self):
        self.holidaytaskId = self.user.holidaytaskId
    @task
    def get_question_list(self):
        self.client.get(f"/api/homework/student/homework/get?homeworkId={self.holidaytaskId}")

    @task(0)
    def do_save(self):
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

        self.client.post("/api/homework/student/homework/save", data=json.dumps(payload), headers=self.user.headers)

        self.client.get(
            "/api/homework/student/holidaytask/homework/list?finished=false&holidayTaskId=758&courseCode=&startDatetime=&endDatetime=&type=1&nameLike=&pageNum=1&pageSize=22",
            headers=self.user.headers)

#学生查看和提交打卡任务
class DoScheduleTask(TaskSet):
    def on_start(self):
        self.homeworkId = self.user.homeworkId

    @task
    def get_question_list(self):
        self.client.get(f"/api/homework/student/holidaytask/homework/schedule/get?homeworkId={self.homeworkId}",
            name="/api/homework/student/holidaytask/homework/schedule/get",
            headers=self.user.headers)

    #个性化打卡任务
    @task(0)
    def get_detail(self):
        self.client.get(f"/api/homework/student/holidaytask/special/question/detail/list?homeworkId={self.homeworkId}",
            name="/api/homework/student/holidaytask/special/question/detail/list",
            headers=self.user.headers)

    @task
    def do_save(self):
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

        self.client.post("/api/homework/student/holidaytask/homework/schedule/save", data=json.dumps(payload), headers=self.user.headers)
    


#教师查看练习监控
class tchMarkingList(TaskSet):
    def on_start(self):
        self.homeworkId = self.user.homeworkId

    @task
    def get_Marking_list(self):
        params = {
            'holidaytaskId' : self.user.holidayTaskId,
            'holidayTaskType' : '1',
            'pageNum': '1',
            'pageSize':'5'

        }

        self.client.get(f"/api/homework/teacher/homework/marking/list", params=params,headers=self.user.headers)


    @task
    def get_checkList(self):
        params = {
            'holidayTaskId' : self.user.holidayTaskId,
            'homeworkId': self.user.homeworkId

        }
        self.client.get(f"/api/homework/teacher/homework/monitoring/checkRequireSyncStudents",params=params,headers=self.user.headers)

        self.client.get(f"/api/homework/teacher/homework/monitoring/info?homeworkId={self.user.homeworkId}",headers=self.user.headers)

        self.client.get(f"/api/homework/teacher/homework/monitoring/status/overview?homeworkId={self.user.homeworkId}",headers=self.user.headers)

        self.client.get(f"/api/homework/teacher/homework/detail?id={self.user.homeworkId}",headers=self.user.headers)

        self.client.get(f"/api/homework/teacher/homework/monitoring/class_info?homeworkId={self.user.homeworkId}",headers=self.user.headers)

        self.client.get(f"/api/holidayvideo/teacher/holidayvideo/monitor/video?videoType=VOD&homeworkId={self.user.homeworkId}",headers=self.user.headers)


#用户类
class EcommerceUser(FastHttpUser):
    # wait_time = constant(5)
    wait_time = between(0,1)
    tasks = [] # 将Task分配给用户
    # host = "https://xuece-xqdsj-stagingtest1.unisolution.cn"
    host = "http://xuece-xqdsj-stress.unisolution.cn"
    # host = "https://47.117.16.192"
    # host = "http://8.159.129.28"
    

    def on_start(self):
        # 只在第一次运行时获取账号，后续不再更换
        if not hasattr(self,'account'):
            # print(hasattr(self,'account'))
            # 使用本地数据
            self.account = account_loader.get_account()
            # 开启redis使用分布式
                
            # self.account = redis_loader.get_account()
            if self.account['account_type'] == 'stu':
                self.tasks = [HolidayTaskListBehavior,WatchVideoBehavior,DoOutdoorTraining,StuAskQuestion,DownloadBehavior,DoScheduleTask]
                # self.wait_time = lambda: between(0,0.01)(self)
            else:
                self.tasks = [tchMarkingList]
                # self.wait_time = lambda: between(1,5)(self)
            self.id = id(self)
            self.user_id = None
            print(f"用户{self.id}固定使用账号 {self.account['username']} 登录")
            self.auth_token = None
            self.school_id = None
            self.headers = None
            self.gradeCode = None
            # print(self.account)
            self.holidayTaskId = self.account['holidayTaskId']
            self.homeworkId = self.account['homeworkId']
            self._login()

    def _login(self):

        params = {
            "username":self.account['username'],
            "encryptpwd":'c34dd995a8132605764a9347dae6e8ca', #测试数据统一密码
            "clienttype":"BROWSER",
            "clientversion":"1.30.6",
            "systemversion":"chrome137.0.0.0"
        }

        with self.client.get("/api/usercenter/nnauth/user/login",name="用户登录", params=params) as response:
            # print(f"响应状态码: {response.status_code}")
            # print(f"响应内容: {response}")
            
            if response.status_code == 200:
                response_data = response.json()
                # print(response_data)
                school_id = response_data["data"]["user"]["schoolId"]
                self.user_id = response_data["data"]["user"]["id"]
                if self.user_id:
                    auth_token = response_data["data"]["authtoken"]
                    self.gradeCode = response_data["data"]["user"].get("gradeCode",None)

                    self.auth_token = auth_token
                    self.school_id = school_id

                    self.headers = {
                        "Authtoken":self.auth_token,
                        "xc-app-user-schoolid":f"{self.school_id}",
                        "Content-Type": "application/json"
                    }
                else:
                    print("存在登录失败",self.account['username'])



