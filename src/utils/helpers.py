"""辅助函数模块"""
import time
import json
from typing import Dict, Any, Optional
from config import get_settings


def get_current_timestamp() -> int:
    """
    获取当前时间戳（毫秒）
    
    Returns:
        int: 当前时间戳（毫秒）
    """
    return int(time.time() * 1000)


def build_headers(auth_token: str, school_id: int) -> Dict[str, str]:
    """
    构建请求头
    
    Args:
        auth_token: 认证令牌
        school_id: 学校ID
    
    Returns:
        Dict[str, str]: 请求头字典
    """
    return {
        "Authtoken": auth_token,
        "xc-app-user-schoolid": f"{school_id}",
        "Content-Type": "application/json"
    }


def print_request(
    method: str,
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    json_data: Optional[Dict] = None
):
    """
    打印请求信息（用于调试）
    
    Args:
        method: HTTP方法 (GET, POST, PUT, DELETE等)
        url: 请求URL
        params: URL参数
        headers: 请求头
        data: 请求体（原始数据）
        json_data: JSON请求体
    """
    settings = get_settings()
    if not settings.DEBUG_REQUESTS:
        return
    
    print("\n" + "=" * 80)
    print(f"[请求] {method} {url}")
    print("-" * 80)
    
    if params:
        print(f"[参数] {json.dumps(params, ensure_ascii=False, indent=2)}")
    
    if headers:
        # 隐藏敏感信息
        safe_headers = headers.copy()
        if "Authtoken" in safe_headers:
            token = safe_headers["Authtoken"]
            if token and len(token) > 20:
                safe_headers["Authtoken"] = token[:10] + "..." + token[-10:]
        print(f"[请求头] {json.dumps(safe_headers, ensure_ascii=False, indent=2)}")
    
    if json_data:
        print(f"[JSON请求体] {json.dumps(json_data, ensure_ascii=False, indent=2)}")
    elif data:
        if isinstance(data, str):
            try:
                # 尝试解析为JSON
                parsed = json.loads(data)
                print(f"[JSON请求体] {json.dumps(parsed, ensure_ascii=False, indent=2)}")
            except:
                print(f"[请求体] {data[:500]}")  # 限制长度
        else:
            print(f"[请求体] {str(data)[:500]}")
    
    print("=" * 80 + "\n")


def print_response(
    response: Any,
    url: str = "",
    max_length: int = 2000
):
    """
    打印响应信息（用于调试）
    
    Args:
        response: Locust响应对象
        url: 请求URL（可选，用于标识）
        max_length: 响应内容最大打印长度
    """
    settings = get_settings()
    if not settings.DEBUG_RESPONSES:
        return
    
    print("\n" + "=" * 80)
    if url:
        print(f"[响应] {url}")
    else:
        print("[响应]")
    print("-" * 80)
    
    if response is None:
        print("[状态] 响应为 None（连接失败）")
        print("=" * 80 + "\n")
        return
    
    # 打印状态码
    status_code = getattr(response, 'status_code', 'Unknown')
    print(f"[状态码] {status_code}")
    
    # 打印响应头
    if hasattr(response, 'headers'):
        print(f"[响应头] {dict(response.headers)}")
    
    # 打印响应内容
    try:
        if hasattr(response, 'text'):
            response_text = response.text
            if len(response_text) > max_length:
                print(f"[响应内容] (前{max_length}字符)")
                print(response_text[:max_length])
                print(f"... (共{len(response_text)}字符，已截断)")
            else:
                print(f"[响应内容]")
                print(response_text)
        
        # 尝试解析JSON
        if hasattr(response, 'json'):
            try:
                response_json = response.json()
                print(f"[JSON响应] {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except:
                pass  # 如果不是JSON，忽略
    except Exception as e:
        print(f"[错误] 无法读取响应内容: {str(e)}")
    
    print("=" * 80 + "\n")

