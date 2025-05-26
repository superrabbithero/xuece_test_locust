from locust import HttpUser, task, between, SequentialTaskSet
import csv
import os
from queue import Queue

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

class UserLoginBehavior(SequentialTaskSet):
    wait_time = between(1,3)

    def on_start(self):
        self.account = account_loader.get_account()
        print(f"用户使用账号 {self.account['username']} 登录")
        self.auth_token = None
        self.school_id = None
        self.headers = None
        self.login()

    def login(self):
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
                        "xc-app-user-schoolid":f"{self.school_id}"
                    }

                    response.success()
                except (KeyError, json.JSONDecodeError) as e:
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task
    def get_user_info(self):
        if not self.auth_token:
            self.interrupt()
            return

        self.client.get("/api/usercenter/common/loginuserinfo/myinfo", headers=self.headers)

    @task
    def get_list_by_type(self):
        if not self.auth_token:
            self.interrupt()
            return

        self.client.get("/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE", headers=self.headers)

    @task
    def get_term_info(self):
        if not self.auth_token:
            self.interrupt()
            return

        self.client.get("/api/usercenter/common/loginuserinfo/terminfo", headers=self.headers)

    @task
    def get_term_info_base(self):
        if not self.auth_token:
            self.interrupt()
            return

        with self.client.get("/api/usercenter/common/loginuserinfo/terminfo/base", headers=self.headers, catch_response=True) as response:
            # print(f"@@@@@@@@@@@@@@响应内容: {response.text}")
            if response.status_code == 200:
                
                try:
                    response_data = response.json()
                    datas = response_data.get("data",[])
                    # print(f"#####################{datas}")
                    for data in datas:
                        # print(f"###############{data['status']}")
                        if(data["status"] == "NOW"):
                            self.year = data["year"]
                            semesters = data["semesters"]
                            if semesters[0]["status"] == "NOW":
                                self.semester = semesters[0]["semester"]
                            else:
                                self.semester = semesters[1]["semester"]
                    response.success()
                except Exception as e:
                    response.failure(f"处理响应时出错: {str(e)}")
            else:
                response.failure(f"HTTP错误: {response.status_code}")

    @task
    def get_course_list(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        params={
            "schoolId": f"{self.school_id}",
            "year": f"{self.year}",
            "semester": self.semester
        }

        self.client.get("/api/usercenter/common/school/course/list", headers=self.headers, params=params)
    
    @task
    def get_gatekeeper_list(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/usercenter/common/loginuserinfo/gatekeeper/list", headers=self.headers)

    @task
    def get_modulepermission(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/usercenter/common/loginuserinfo/modulepermission", headers=self.headers)

    @task
    def get_my_school(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/usercenter/common/loginuserinfo/myschool", headers=self.headers)

    
    @task
    def get_exam_list(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/examcenter/student/exam/querylist_v2?pageNum=1&pageSize=5", headers=self.headers)
    
    @task
    def get_listshelvedtask(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/homework/student/holidaytask/listshelvedtask", headers=self.headers)

        

    @task
    def get_isAuditor(self):
        if not self.auth_token:
            self.interrupt()
            return
        
        self.client.get("/api/holidayvideo/common/holidayvideo/isAuditor", headers=self.headers)
    
    @task
    def stop(self):
     self.interrupt()  # 退出SequentialTaskSet

class EcommerceUser(HttpUser):
    tasks = [UserLoginBehavior] # 将SequentialTaskSet分配给用户
    host = "https://xuece-xqdsj-stagingtest1.unisolution.cn"