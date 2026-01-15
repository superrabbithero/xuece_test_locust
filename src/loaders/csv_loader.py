"""CSV文件账号加载器"""
import csv
from queue import Queue
from typing import Dict, Optional
from pathlib import Path

from config import get_settings
from .base import BaseAccountLoader


class CSVAccountLoader(BaseAccountLoader):
    """
    CSV文件账号加载器
    
    从CSV文件中读取账号信息，支持分片加载。
    """
    
    def __init__(self):
        """初始化CSV账号加载器"""
        settings = get_settings()
        self.accounts = Queue()
        self.total_count = 0
        
        file_path = settings.get_account_file_path()
        start = settings.LOCUST_START
        end = settings.LOCUST_END
        
        if not file_path.exists():
            raise FileNotFoundError(f"账号文件不存在: {file_path}")
        
        # 读取CSV文件
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            all_rows = list(reader)
            
            self.total_count = len(all_rows)
            
            # 计算实际结束位置
            if end == 0:
                end = self.total_count
            else:
                end = min(self.total_count, end)
            
            # 加载指定范围的账号
            for row in all_rows[start:end]:
                self.accounts.put(row)
        
        print(f"CSV账号加载器初始化完成: 加载了 {self.accounts.qsize()} 个账号 (范围: {start}-{end})")
    
    def get_account(self) -> Optional[Dict[str, str]]:
        """
        获取一个账号
        
        Returns:
            Optional[Dict[str, str]]: 账号信息字典，如果无可用账号则返回None
        """
        if self.accounts.empty():
            return None
        return self.accounts.get()
    
    def has_accounts(self) -> bool:
        """
        检查是否还有可用账号
        
        Returns:
            bool: 如果还有可用账号返回True，否则返回False
        """
        return not self.accounts.empty()
    
    def get_total_count(self) -> int:
        """
        获取账号总数
        
        Returns:
            int: 账号总数
        """
        return self.total_count

