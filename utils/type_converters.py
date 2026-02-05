"""
类型转换工具模块
提供统一的类型转换函数，处理API响应中的类型不一致问题
"""
from typing import Any, Optional
from utils.logger import logger


def to_bool(value: Any) -> bool:
    """
    转换为布尔值
    兼容boolean和string类型
    
    Args:
        value: 原始值（可能是bool, string, int等）
        
    Returns:
        bool: 转换后的布尔值
        
    Examples:
        >>> to_bool(True)
        True
        >>> to_bool("true")
        True
        >>> to_bool("false")
        False
        >>> to_bool("1")
        True
    """
    if value is None:
        return False
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes']
    
    if isinstance(value, int):
        return value != 0
    
    return bool(value)


def to_float(value: Any) -> float:
    """
    转换为浮点数
    兼容string和number类型
    
    Args:
        value: 原始值（可能是string, int, float等）
        
    Returns:
        float: 转换后的浮点数，失败返回0.0
        
    Examples:
        >>> to_float("123.45")
        123.45
        >>> to_float(100)
        100.0
        >>> to_float(None)
        0.0
    """
    if value is None:
        return 0.0
    
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"无法转换为float: {value}, 错误: {e}")
        return 0.0


def to_int(value: Any) -> int:
    """
    转换为整数
    兼容string和number类型
    
    Args:
        value: 原始值（可能是string, int, float等）
        
    Returns:
        int: 转换后的整数，失败返回0
    """
    if value is None:
        return 0
    
    try:
        return int(float(value))  # 先转float再转int，支持"123.45"这种
    except (ValueError, TypeError) as e:
        logger.warning(f"无法转换为int: {value}, 错误: {e}")
        return 0


def safe_get_field(data: dict, *field_names) -> Any:
    """
    安全获取字段值，支持多个可能的字段名
    用于处理字段命名不一致的问题
    
    Args:
        data: 数据字典
        *field_names: 可能的字段名列表
        
    Returns:
        Any: 第一个找到的字段值，都不存在返回None
        
    Examples:
        >>> data = {"total_balance": "100"}
        >>> safe_get_field(data, "balance", "total_balance")
        "100"
        
        >>> data = {"file_id": "123"}
        >>> safe_get_field(data, "fileId", "file_id")
        "123"
    """
    for field in field_names:
        if field in data:
            return data[field]
    return None
