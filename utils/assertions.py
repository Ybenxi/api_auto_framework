"""
通用断言工具模块
提供 HTTP 响应、列表结构、字段完整性等常用断言函数
"""
import requests
from typing import List, Optional, Union, Dict, Any
from utils.logger import logger


def assert_status_ok(response: requests.Response, expected_status: int = 200):
    """
    断言 HTTP 响应状态码为成功状态
    
    Args:
        response: requests.Response 对象
        expected_status: 期望的状态码，默认为 200
        
    Raises:
        AssertionError: 如果状态码不匹配
    """
    if response.status_code != expected_status:
        error_msg = f"接口返回状态码错误: 期望 {expected_status}，实际 {response.status_code}"
        logger.error(error_msg)
        raise AssertionError(error_msg)
    logger.debug(f"状态码断言通过: {expected_status}")


def assert_response_parsed(parsed: dict):
    """
    断言响应解析成功（无 error 字段或 error 为 False）
    
    Args:
        parsed: 解析后的响应字典，应包含 error 字段
        
    Raises:
        AssertionError: 如果响应解析失败
    """
    if parsed.get("error"):
        error_msg = f"响应解析失败: {parsed.get('message', '未知错误')}"
        logger.error(error_msg)
        raise AssertionError(error_msg)
    logger.debug("响应解析断言通过")


def assert_list_structure(
    parsed: dict,
    required_fields: Optional[List[str]] = None,
    has_pagination: bool = True
):
    """
    断言列表响应结构完整
    
    Args:
        parsed: 解析后的响应字典
        required_fields: 响应根级别必需字段列表，如 ["content", "total_elements"]
        has_pagination: 是否验证分页相关字段
        
    Raises:
        AssertionError: 如果结构不完整
    """
    if required_fields is None:
        required_fields = ["content"]
    
    for field in required_fields:
        if field not in parsed:
            error_msg = f"响应中缺少必需字段: {field}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    if not isinstance(parsed["content"], list):
        error_msg = "content 字段不是列表类型"
        logger.error(error_msg)
        raise AssertionError(error_msg)
    
    if has_pagination:
        pagination_fields = ["total_elements", "size", "number"]
        for field in pagination_fields:
            if field not in parsed:
                error_msg = f"响应中缺少分页字段: {field}"
                logger.error(error_msg)
                raise AssertionError(error_msg)
    
    logger.debug("列表结构断言通过")


def assert_enum_filter(
    result_list: List[Dict[str, Any]],
    field_name: str,
    expected_value: Union[str, Any],
    allow_none: bool = False
):
    """
    断言列表中的每个元素都符合枚举筛选条件
    
    Args:
        result_list: 结果列表
        field_name: 要验证的字段名
        expected_value: 期望的字段值（可以是枚举对象，会自动提取 .value）
        allow_none: 是否允许字段值为 None（跳过验证）
        
    Raises:
        AssertionError: 如果存在不符合条件的元素
    """
    # 如果 expected_value 是枚举对象，提取其值
    if hasattr(expected_value, 'value'):
        expected_str = expected_value.value
    else:
        expected_str = str(expected_value)
    
    for item in result_list:
        actual_value = item.get(field_name)
        
        if actual_value is None:
            if not allow_none:
                error_msg = f"列表项缺少字段 '{field_name}'，期望值: {expected_str}"
                logger.error(error_msg)
                raise AssertionError(error_msg)
            continue
        
        actual_str = str(actual_value)
        if actual_str != expected_str:
            error_msg = f"字段 '{field_name}' 值不匹配: 期望 '{expected_str}'，实际 '{actual_str}'"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    logger.debug(f"枚举筛选断言通过: {field_name}={expected_str}")


def assert_string_contains_filter(
    result_list: List[Dict[str, Any]],
    field_name: str,
    search_keyword: str,
    case_sensitive: bool = False
):
    """
    断言列表中的每个元素的指定字段都包含搜索关键词（用于名称筛选等场景）
    
    Args:
        result_list: 结果列表
        field_name: 要验证的字段名
        search_keyword: 搜索关键词
        case_sensitive: 是否区分大小写
        
    Raises:
        AssertionError: 如果存在不包含关键词的元素
    """
    if not case_sensitive:
        search_keyword = search_keyword.lower()
    
    for item in result_list:
        field_value = item.get(field_name, "")
        if not case_sensitive:
            field_value = str(field_value).lower()
        else:
            field_value = str(field_value)
        
        if search_keyword not in field_value:
            error_msg = f"字段 '{field_name}' 的值 '{item.get(field_name)}' 不包含搜索关键词 '{search_keyword}'"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    logger.debug(f"字符串包含筛选断言通过: {field_name} contains '{search_keyword}'")


def assert_pagination(
    parsed: dict,
    expected_size: Optional[int] = None,
    expected_page: Optional[int] = None
):
    """
    断言分页信息正确
    
    Args:
        parsed: 解析后的响应字典
        expected_size: 期望的每页大小
        expected_page: 期望的页码（从 0 开始）
        
    Raises:
        AssertionError: 如果分页信息不正确
    """
    content = parsed.get("content", [])
    
    if expected_size is not None:
        if len(content) > expected_size:
            error_msg = f"返回的数据量 {len(content)} 超过了指定的每页大小 {expected_size}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        if parsed.get("size") != expected_size:
            error_msg = f"分页信息中的 size 不正确: 期望 {expected_size}，实际 {parsed.get('size')}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    if expected_page is not None:
        if parsed.get("number") != expected_page:
            error_msg = f"分页信息中的页码不正确: 期望 {expected_page}，实际 {parsed.get('number')}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    logger.debug(f"分页断言通过: size={expected_size}, page={expected_page}")


def assert_empty_result(parsed: dict):
    """
    断言返回空结果
    
    Args:
        parsed: 解析后的响应字典
        
    Raises:
        AssertionError: 如果结果不为空
    """
    if len(parsed.get("content", [])) != 0:
        error_msg = "期望返回空列表，但实际有数据"
        logger.error(error_msg)
        raise AssertionError(error_msg)
    if parsed.get("empty", False) != True:
        error_msg = "empty 字段应该为 True"
        logger.error(error_msg)
        raise AssertionError(error_msg)
    logger.debug("空结果断言通过")


def assert_fields_present(
    obj: Dict[str, Any],
    required_fields: List[str],
    obj_name: str = "对象"
):
    """
    断言对象包含所有必需字段
    
    Args:
        obj: 要验证的对象字典
        required_fields: 必需字段列表
        obj_name: 对象名称（用于错误提示）
        
    Raises:
        AssertionError: 如果缺少必需字段
    """
    for field in required_fields:
        if field not in obj:
            error_msg = f"{obj_name}缺少必需字段: {field}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    logger.debug(f"{obj_name}字段完整性断言通过")
