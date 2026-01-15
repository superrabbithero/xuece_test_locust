"""登录性能测试脚本

用于诊断登录请求的性能问题，对比不同场景下的响应时间。
"""
import time
import requests
from locust import FastHttpUser, task, events
from src.users.ecommerce_user import EcommerceUser
from config import get_settings


def test_requests_library():
    """测试使用 requests 库直接请求的性能"""
    settings = get_settings()
    params = {
        "username": "test_user",
        "encryptpwd": settings.DEFAULT_PASSWORD,
        "clienttype": settings.CLIENT_TYPE,
        "clientversion": settings.CLIENT_VERSION,
        "systemversion": settings.SYSTEM_VERSION
    }
    
    url = f"{settings.API_HOST}/api/usercenter/nnauth/user/login"
    
    print("\n" + "=" * 80)
    print("测试 1: 使用 requests 库直接请求")
    print("=" * 80)
    
    # 第一次请求（可能包含连接建立）
    start = time.time()
    response = requests.get(url, params=params, timeout=10)
    first_time = (time.time() - start) * 1000
    print(f"第一次请求耗时: {first_time:.2f}ms (状态码: {response.status_code})")
    
    # 后续请求（连接复用）
    times = []
    for i in range(5):
        start = time.time()
        response = requests.get(url, params=params, timeout=10)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"第 {i+2} 次请求耗时: {elapsed:.2f}ms (状态码: {response.status_code})")
    
    avg_time = sum(times) / len(times)
    print(f"\n后续请求平均耗时: {avg_time:.2f}ms")
    print(f"首次请求额外开销: {first_time - avg_time:.2f}ms")


def test_locust_user():
    """测试使用 Locust FastHttpUser 的性能"""
    settings = get_settings()
    
    print("\n" + "=" * 80)
    print("测试 2: 使用 Locust FastHttpUser")
    print("=" * 80)
    
    # 创建用户实例
    user = EcommerceUser(environment=None)
    user.host = settings.API_HOST
    
    # 设置测试账号
    user.account = {
        'username': 'test_user',
        'account_type': 'stu'
    }
    
    # 第一次请求
    start = time.time()
    user._login()
    first_time = (time.time() - start) * 1000
    print(f"第一次请求耗时: {first_time:.2f}ms")
    
    # 重置登录状态，测试后续请求
    user._is_logged_in = False
    user.auth_token = None
    user.headers = None
    
    times = []
    for i in range(5):
        start = time.time()
        user._login()
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"第 {i+2} 次请求耗时: {elapsed:.2f}ms")
        
        # 重置登录状态
        user._is_logged_in = False
        user.auth_token = None
        user.headers = None
    
    avg_time = sum(times) / len(times)
    print(f"\n后续请求平均耗时: {avg_time:.2f}ms")
    print(f"首次请求额外开销: {first_time - avg_time:.2f}ms")


def test_with_timing():
    """测试带详细计时的登录性能"""
    settings = get_settings()
    
    print("\n" + "=" * 80)
    print("测试 3: 详细计时分析")
    print("=" * 80)
    
    user = EcommerceUser(environment=None)
    user.host = settings.API_HOST
    user.account = {
        'username': 'test_user',
        'account_type': 'stu'
    }
    
    # 测试一次登录，记录各步骤耗时
    timings = {}
    
    # 准备参数
    start = time.time()
    params = {
        "username": user.account['username'],
        "encryptpwd": settings.DEFAULT_PASSWORD,
        "clienttype": settings.CLIENT_TYPE,
        "clientversion": settings.CLIENT_VERSION,
        "systemversion": settings.SYSTEM_VERSION
    }
    timings['准备参数'] = (time.time() - start) * 1000
    
    # HTTP 请求
    start = time.time()
    with user.client.get(
        "/api/usercenter/nnauth/user/login",
        name="用户登录",
        params=params,
        catch_response=True
    ) as response:
        timings['HTTP请求'] = (time.time() - start) * 1000
        
        # 解析响应
        start = time.time()
        if response and response.status_code == 200:
            response_data = response.json()
            timings['解析JSON'] = (time.time() - start) * 1000
            
            # 提取数据
            start = time.time()
            data = response_data.get("data")
            user_data = data.get("user") if data else None
            if user_data:
                user.school_id = user_data.get("schoolId")
                user.user_id = user_data.get("id")
                user.gradeCode = user_data.get("gradeCode")
                if user.user_id:
                    user.auth_token = data.get("authtoken")
                    from src.utils.helpers import build_headers
                    user.headers = build_headers(user.auth_token, user.school_id)
            timings['提取数据'] = (time.time() - start) * 1000
            response.success()
    
    print("\n各步骤耗时:")
    for step, elapsed in timings.items():
        print(f"  {step}: {elapsed:.2f}ms")
    
    total = sum(timings.values())
    print(f"\n总耗时: {total:.2f}ms")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("登录性能诊断工具")
    print("=" * 80)
    print("\n注意：请确保 .env 文件中的 API_HOST 配置正确")
    print("注意：请确保测试账号有效")
    
    try:
        # 测试 1: requests 库
        test_requests_library()
        
        # 测试 2: Locust FastHttpUser
        test_locust_user()
        
        # 测试 3: 详细计时
        test_with_timing()
        
        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)
        print("\n分析建议:")
        print("1. 如果第一次请求明显慢，说明是连接建立的开销（DNS、TCP、TLS）")
        print("2. 如果后续请求也慢，说明是 Locust 框架或代码逻辑的开销")
        print("3. 对比 requests 和 Locust 的耗时，找出差异来源")
        
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
        import traceback
        traceback.print_exc()

