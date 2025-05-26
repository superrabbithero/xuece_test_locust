from locust import HttpUser, task, between
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

class LoginUser(HttpUser):
    wait_time = between(1, 3)  # 用户等待时间1-5秒
    host = "https://xuece-xqdsj-stagingtest1.unisolution.cn"
    
    def on_start(self):
        # 每个用户获取唯一账号
        self.account = account_loader.get_account()
        print(f"用户使用账号 {self.account['username']} 登录")

    @task
    def login(self):
        params = {
            "username":self.account['username'],
            "encryptpwd":'c34dd995a8132605764a9347dae6e8ca',
            "clienttype":"BROWSER",
            "clientversion":"1.30.6",
            "systemversion":"chrome136.0.0.0"
        }
        # self.client.get("/login", params=params)
        with self.client.get("/api/usercenter/nnauth/user/login", params=params, catch_response=True) as response:
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")