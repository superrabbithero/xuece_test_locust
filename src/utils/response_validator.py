"""响应验证工具"""
from typing import Dict, Any, Optional, Tuple

# Locust 响应对象类型（使用 Any 以兼容不同版本的 Locust）
# 实际响应对象具有 status_code, json(), success(), failure() 等方法
ResponseContextManager = Any


class ResponseValidator:
    """响应验证工具类"""
    
    @staticmethod
    def validate_json_response(
        response: ResponseContextManager,
        expected_status: int = 200,
        required_keys: Optional[list] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        验证JSON响应
        
        Args:
            response: Locust响应对象
            expected_status: 期望的HTTP状态码
            required_keys: 响应数据中必须包含的键列表
        
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        if response.status_code != expected_status:
            return False, f"HTTP状态码错误: 期望 {expected_status}, 实际 {response.status_code}"
        
        try:
            response_data = response.json()
        except Exception as e:
            return False, f"JSON解析失败: {str(e)}"
        
        if required_keys:
            for key in required_keys:
                if key not in response_data:
                    return False, f"响应中缺少必需的键: {key}"
        
        return True, None
    
    @staticmethod
    def extract_nested_value(
        data: Dict[str, Any],
        path: str,
        default: Any = None
    ) -> Any:
        """
        从嵌套字典中提取值
        
        Args:
            data: 数据字典
            path: 路径，使用点号分隔，如 "data.user.id"
            default: 默认值
        
        Returns:
            Any: 提取的值，如果路径不存在则返回默认值
        """
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @staticmethod
    def validate_and_extract(
        response: ResponseContextManager,
        data_path: str,
        expected_status: int = 200
    ) -> Tuple[bool, Optional[Any], Optional[str]]:
        """
        验证响应并提取数据
        
        Args:
            response: Locust响应对象
            data_path: 数据路径，如 "data.user.id"
            expected_status: 期望的HTTP状态码
        
        Returns:
            Tuple[bool, Optional[Any], Optional[str]]: (是否成功, 提取的数据, 错误信息)
        """
        success, error = ResponseValidator.validate_json_response(
            response, expected_status
        )
        
        if not success:
            return False, None, error
        
        try:
            response_data = response.json()
            value = ResponseValidator.extract_nested_value(
                response_data, data_path
            )
            return True, value, None
        except Exception as e:
            return False, None, f"数据提取失败: {str(e)}"

