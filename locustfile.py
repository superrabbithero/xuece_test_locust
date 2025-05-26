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
                school_id = response_data["data"]["user"]["schoolId"]
                auth_token = response_data["data"]["authtoken"]

                self.auth_token = auth_token
                self.school_id = school_id

                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task

