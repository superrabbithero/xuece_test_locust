#!/usr/bin/env python
"""
项目设置验证脚本

运行此脚本来验证项目是否正确配置：
    python verify_setup.py
"""
import sys
from pathlib import Path


def check_imports():
    """检查必要的模块是否可以导入"""
    print("[*] 检查模块导入...")
    try:
        from config import get_settings
        from src.loaders import CSVAccountLoader, RedisAccountLoader
        from src.users import EcommerceUser
        from src.tasks.student import HolidayTaskListBehavior
        from src.tasks.teacher import TchMarkingList
        print("[OK] 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"[ERROR] 模块导入失败: {e}")
        return False


def check_config():
    """检查配置加载"""
    print("\n[*] 检查配置加载...")
    try:
        from config import get_settings
        settings = get_settings()
        print(f"[OK] 配置加载成功")
        print(f"   - API_HOST: {settings.API_HOST}")
        print(f"   - ACCOUNT_FILE: {settings.ACCOUNT_FILE}")
        print(f"   - ACCOUNT_LOADER_TYPE: {settings.ACCOUNT_LOADER_TYPE}")
        return True
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return False


def check_data_files():
    """检查数据文件"""
    print("\n[*] 检查数据文件...")
    from config import get_settings
    settings = get_settings()
    account_file = settings.get_account_file_path()
    
    if account_file.exists():
        print(f"[OK] 账号文件存在: {account_file}")
        return True
    else:
        print(f"[WARN] 账号文件不存在: {account_file}")
        print(f"   请检查 .env 中的 ACCOUNT_FILE 配置")
        return False


def check_env_file():
    """检查环境变量文件"""
    print("\n[*] 检查环境变量文件...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("[OK] .env 文件存在")
        return True
    elif env_example.exists():
        print("[WARN] .env 文件不存在，但 .env.example 存在")
        print("   请运行: cp .env.example .env")
        return False
    else:
        print("[WARN] 环境变量文件不存在")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n[*] 检查依赖包...")
    required_packages = [
        'locust',
        'dotenv',
        'redis'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package} 已安装")
        except ImportError:
            print(f"[ERROR] {package} 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n[WARN] 缺少依赖包: {', '.join(missing)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("项目设置验证")
    print("=" * 50)
    
    results = []
    
    # 检查依赖
    results.append(("依赖包", check_dependencies()))
    
    # 检查环境文件
    results.append(("环境文件", check_env_file()))
    
    # 检查模块导入
    results.append(("模块导入", check_imports()))
    
    # 检查配置
    results.append(("配置加载", check_config()))
    
    # 检查数据文件
    results.append(("数据文件", check_data_files()))
    
    # 总结
    print("\n" + "=" * 50)
    print("验证结果总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有检查通过！项目配置正确，可以开始使用！")
        print("\n运行压测:")
        print("  locust -f src/locustfile.py")
        return 0
    else:
        print("\n[WARN] 部分检查未通过，请根据上述提示修复问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())

