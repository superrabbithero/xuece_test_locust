from locust import HttpUser, task, constant

class EcommerceUser(HttpUser):
    wait_time = constant(300)
    # wait_time = between(1,5)
    # tasks = [WatchVideoBehavior] # 将Task分配给用户
    # host = "https://xuece-xqdsj-stagingtest1.unisolution.cn"
    # host = "https://xuece-xqdsj-stress.unisolution.cn"
    # host = "https://api.superrabbithero.xyz"
    host = "https://xqdsj.xuece.cn"
    

    @task
    def login(self):

        with self.client.get("api/usercenter/nnauth/user/login?username=math_huang&encryptpwd=c34dd995a8132605764a9347dae6e8ca&clienttype=BROWSER&clientversion=1.30.6&systemversion=chrome137.0.0.0", catch_response=True) as response:
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response}")
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Status code: {response.status_code}")

        # with self.client.get("/api/packages/search?appname=0&page=1&per_page=10", catch_response=True) as response:
        #     print(f"响应状态码: {response.status_code}")
        #     print(f"响应内容: {response}")
        #     if response.status_code == 200:
        #         pass
        #     else:
        #         response.failure(f"Status code: {response.status_code}")