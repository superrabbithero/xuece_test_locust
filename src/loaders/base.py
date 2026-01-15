"""账号加载器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseAccountLoader(ABC):
    """账号加载器抽象基类"""
    
    @abstractmethod
    def get_account(self) -> Optional[Dict[str, str]]:
        """
        获取一个账号
        
        Returns:
            Optional[Dict[str, str]]: 账号信息字典，如果无可用账号则返回None
        """
        pass
    
    @abstractmethod
    def has_accounts(self) -> bool:
        """
        检查是否还有可用账号
        
        Returns:
            bool: 如果还有可用账号返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def get_total_count(self) -> int:
        """
        获取账号总数
        
        Returns:
            int: 账号总数
        """
        pass

