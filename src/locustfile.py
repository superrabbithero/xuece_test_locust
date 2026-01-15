"""
Locust压测入口文件

使用方式:
    locust -f src/locustfile.py

或者指定主机:
    locust -f src/locustfile.py --host=http://example.com
"""
from src.users import EcommerceUser

# Locust会自动识别这个文件中的User类
# 所有配置都在config/settings.py中管理

