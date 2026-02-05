"""
Sub Program 相关 API 封装
提供子项目和嵌套项目的查询功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. Sub Program List响应无code包装层（格式不一致）
2. spending_limit_location字段未定义
3. Nested Program status枚举值未定义
4. spending_limit_amount字段作用不明
5. page_content vs 标准分页字段命名不一致
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import CardNetwork, SubProgramStatus, ClassificationType, NestedProgramLogStatus
from utils.logger import logger


class SubProgramAPI:
    """
    Sub Program API 封装类
    包含子项目和嵌套项目的查询功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 SubProgramAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== Sub Program 查询接口 ====================
    
    def list_sub_programs(
        self,
        name: Optional[str] = None,
        business_name: Optional[str] = None,
        network: Optional[Union[str, CardNetwork]] = None,
        is_virtual: Optional[bool] = None,
        classification_type: Optional[Union[str, ClassificationType]] = None,
        status: Optional[Union[str, SubProgramStatus]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取子项目列表
        
        Args:
            name: 子项目名称
            business_name: 商户名称
            network: 卡片网络
            is_virtual: 是否虚拟卡
            classification_type: 分类类型（Business/Consumer）
            status: 子项目状态
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应直接返回数组，无code包装层
            2. 与同模块的Detail接口格式不一致
            3. spending_limit_location字段未在Properties定义
        """
        url = self.config.get_full_url("/card-issuance/sub-programs")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        if business_name is not None:
            params["business_name"] = business_name
        if network is not None:
            params["network"] = str(network) if isinstance(network, CardNetwork) else network
        if is_virtual is not None:
            params["is_virtual"] = is_virtual
        if classification_type is not None:
            params["classification_type"] = str(classification_type) if isinstance(classification_type, ClassificationType) else classification_type
        if status is not None:
            params["status"] = str(status) if isinstance(status, SubProgramStatus) else status
        
        params.update(kwargs)
        logger.debug(f"请求子项目列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_sub_program_detail(self, sub_program_id: str) -> requests.Response:
        """
        获取子项目详情
        
        Args:
            sub_program_id: 子项目ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            响应格式：{"code": 200, "data": {...}}
            与List接口格式不一致（List直接返回数组）
        """
        url = self.config.get_full_url(f"/card-issuance/sub-programs/{sub_program_id}")
        logger.debug(f"请求子项目详情: {sub_program_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== Nested Program 查询接口 ====================
    
    def list_nested_programs(
        self,
        sub_program_id: str,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取子项目下的嵌套项目列表
        
        Args:
            sub_program_id: 子项目ID
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            spending_limit_amount字段作用不明（与spending_limit数组关系？）
        """
        url = self.config.get_full_url(f"/card-issuance/sub-programs/{sub_program_id}/nested-programs")
        params = {"page": page, "size": size}
        
        params.update(kwargs)
        logger.debug(f"请求嵌套项目列表: sub_program={sub_program_id}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_nested_program_detail(self, nested_program_id: str) -> requests.Response:
        """
        获取嵌套项目详情
        
        Args:
            nested_program_id: 嵌套项目ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/card-issuance/nested-programs/{nested_program_id}")
        logger.debug(f"请求嵌套项目详情: {nested_program_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_nested_program_using_log(
        self,
        card_number: str,
        nested_program_id: str,
        status: Optional[Union[str, NestedProgramLogStatus]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取嵌套项目使用日志
        返回特定卡片在嵌套项目中的交易记录
        
        Args:
            card_number: 卡号或card ID（必需）
            nested_program_id: 嵌套项目ID（必需）
            status: 日志状态（Completed/Cancel/Pending）
            start_time: 开始时间（UTC，格式 yyyy-MM-dd HH:mm:ss）
            end_time: 结束时间（UTC，格式 yyyy-MM-dd HH:mm:ss）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应结构特殊：有page_content包装层
            2. total_used_amount字段未在Properties定义
            3. direction字段枚举值未定义
            4. HTTP方法未在标题标注
        """
        url = self.config.get_full_url("/card-issuance/nested-programs/using-log")
        params = {
            "card_number": card_number,
            "nested_program_id": nested_program_id,
            "page": page,
            "size": size
        }
        
        if status is not None:
            params["status"] = str(status) if isinstance(status, NestedProgramLogStatus) else status
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        
        params.update(kwargs)
        logger.debug(f"请求嵌套项目使用日志: card={card_number}, nested_program={nested_program_id}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response, is_array: bool = False) -> dict:
        """
        解析列表响应
        兼容直接数组和标准分页两种格式
        
        Args:
            response: requests.Response 对象
            is_array: 是否是直接数组响应（Sub Program List特殊情况）
            
        Returns:
            dict: 包含 error, content, pageable 等字段
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            
            # 格式1：直接数组（Sub Program List）
            if is_array and isinstance(data, list):
                return {
                    "error": False,
                    "content": data,
                    "is_array_response": True
                }
            
            # 格式2：标准格式（有code包装层）
            if isinstance(data, dict):
                # 检查code字段
                if "code" in data and data["code"] != 200:
                    return {
                        "error": True,
                        "code": data["code"],
                        "message": data.get("error_message", "Unknown error")
                    }
                
                content_data = data.get("data", data)
                
                return {
                    "error": False,
                    "content": content_data.get("content", []),
                    "pageable": content_data.get("pageable", {}),
                    "total_elements": content_data.get("total_elements", 0),
                    "total_pages": content_data.get("total_pages", 0)
                }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
