"""Redis账号加载器"""
import json
from typing import Dict, Optional
import redis
from redis.exceptions import WatchError

from config import get_settings
from .base import BaseAccountLoader


class RedisAccountLoader(BaseAccountLoader):
    """
    Redis账号加载器
    
    从Redis列表中原子化获取账号，支持分布式压测。
    """
    
    def __init__(self):
        """初始化Redis账号加载器"""
        settings = get_settings()
        
        self.redis = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        self.pool_key = settings.REDIS_POOL_KEY
        self.total_count = 0
        
        # 测试连接
        try:
            self.redis.ping()
            self.total_count = self.redis.llen(self.pool_key)
            print(f"Redis账号加载器初始化完成: 连接成功，账号池中有 {self.total_count} 个账号")
        except redis.ConnectionError as e:
            raise ConnectionError(f"无法连接到Redis服务器: {e}")
    
    def get_account(self) -> Optional[Dict[str, str]]:
        """
        使用Redis事务确保原子性获取账号
        
        Returns:
            Optional[Dict[str, str]]: 账号信息字典，如果无可用账号则返回None
        """
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    # 开启监视
                    pipe.watch(self.pool_key)
                    
                    # 检查列表是否为空
                    if not pipe.llen(self.pool_key):
                        return None
                    
                    # 开始事务
                    pipe.multi()
                    pipe.lpop(self.pool_key)
                    result = pipe.execute()[0]
                    
                    if result:
                        return json.loads(result)
                    return None
                    
                except WatchError:
                    # 如果其他客户端修改了数据，重试
                    continue
                finally:
                    pipe.reset()
    
    def has_accounts(self) -> bool:
        """
        检查是否还有可用账号
        
        Returns:
            bool: 如果还有可用账号返回True，否则返回False
        """
        return self.redis.llen(self.pool_key) > 0
    
    def get_total_count(self) -> int:
        """
        获取账号总数（当前池中剩余数量）
        
        Returns:
            int: 当前账号池中的账号数量
        """
        return self.redis.llen(self.pool_key)
    
    def init_accounts(self, file_path: Optional[str] = None):
        """
        初始化时将账号导入Redis（每次调用前先清空现有数据）
        
        Args:
            file_path: CSV文件路径，如果为None则使用配置中的路径
        """
        import csv
        from pathlib import Path
        
        settings = get_settings()
        
        if file_path is None:
            file_path = settings.get_account_file_path()
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"账号文件不存在: {file_path}")
        
        # 先删除现有的账号池数据
        self.redis.delete(self.pool_key)
        
        # 读取CSV文件并导入Redis
        count = 0
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.redis.rpush(self.pool_key, json.dumps(row))
                count += 1
        
        self.total_count = count
        print(f"Redis账号池初始化完成: 导入了 {count} 个账号")

