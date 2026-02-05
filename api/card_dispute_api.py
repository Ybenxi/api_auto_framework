"""
Card Dispute 和 Risk Control 相关 API 封装
提供争议管理、风险控制、消费限制和MCC码查询功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. disputed_reason类型定义错误（int → string）
2. disputed_amount类型不一致（string定义，number实际）
3. fileId vs file_id命名不一致
4. 时间字段命名不统一（startTime vs start_time）
5. 接口描述错误（说card holders应为spending limits/MCC codes）
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import DisputeStatus
from utils.logger import logger


class CardDisputeAPI:
    """
    Card Dispute 和 Risk Control API 封装类
    包含争议管理和风险控制功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 CardDisputeAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== Dispute 接口 ====================
    
    def list_disputes(
        self,
        card_id: Optional[str] = None,
        original_transaction_id: Optional[str] = None,
        disputed_amount: Optional[str] = None,
        disputed_reason: Optional[str] = None,
        comments: Optional[str] = None,
        card_holder_name: Optional[str] = None,
        status: Optional[Union[str, DisputeStatus]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取争议列表
        
        Args:
            card_id: 卡片ID
            original_transaction_id: 原始交易ID
            disputed_amount: 争议金额
            disputed_reason: 争议原因
            comments: 备注
            card_holder_name: 持卡人姓名
            status: 争议状态（New/Submitted/Result）
            start_time: 开始时间
            end_time: 结束时间
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. disputed_reason实际是string枚举，不是int
            2. 枚举值未定义（示例中有"noAuthorization"）
            3. JSON格式错误（trailing comma）
        """
        url = self.config.get_full_url("/card-issuance/disputes")
        params = {"page": page, "size": size}
        
        if card_id is not None:
            params["card_id"] = card_id
        if original_transaction_id is not None:
            params["original_transaction_id"] = original_transaction_id
        if disputed_amount is not None:
            params["disputed_amount"] = disputed_amount
        if disputed_reason is not None:
            params["disputed_reason"] = disputed_reason
        if comments is not None:
            params["comments"] = comments
        if card_holder_name is not None:
            params["card_holder_name"] = card_holder_name
        if status is not None:
            params["status"] = str(status) if isinstance(status, DisputeStatus) else status
        if start_time is not None:
            params["startTime"] = start_time  # 注意：使用驼峰命名
        if end_time is not None:
            params["endTime"] = end_time  # 注意：使用驼峰命名
        
        params.update(kwargs)
        logger.debug(f"请求争议列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def create_dispute(
        self,
        file_path: str,
        original_transaction_id: str,
        disputed_amount: str,
        disputed_reason: Optional[str] = None,
        comments: Optional[str] = None
    ) -> requests.Response:
        """
        创建争议
        
        Args:
            file_path: 争议文件路径
            original_transaction_id: 原始交易ID（必需）
            disputed_amount: 争议金额（必需）
            disputed_reason: 争议原因（可选）
            comments: 备注（可选）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：使用multipart/form-data上传文件
            ⚠️ 文档问题：file vs fileId参数命名不一致
        """
        url = self.config.get_full_url("/card-issuance/disputes")
        
        try:
            files = {'file': open(file_path, 'rb')}
            data = {
                'original_transaction_id': original_transaction_id,
                'disputed_amount': disputed_amount
            }
            
            if disputed_reason is not None:
                data['disputed_reason'] = disputed_reason
            if comments is not None:
                data['comments'] = comments
            
            logger.debug(f"创建争议: transaction={original_transaction_id}, amount={disputed_amount}")
            
            response = self.session.post(url, files=files, data=data)
            logger.debug(f"响应状态: {response.status_code}")
            
            return response
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except Exception as e:
            logger.error(f"创建争议失败: {e}", exc_info=True)
            raise

    def get_dispute_detail(self, dispute_id: str) -> requests.Response:
        """
        获取争议详情
        
        Args:
            dispute_id: 争议ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：fileId vs file_id命名不一致
        """
        url = self.config.get_full_url(f"/card-issuance/disputes/{dispute_id}")
        logger.debug(f"请求争议详情: {dispute_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== Risk Control 接口 ====================
    
    def list_spending_limits(
        self,
        card_id: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取消费限制列表
        
        Args:
            card_id: 卡片ID
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：接口描述错误
            文档说"a maximum of ten card holders"应为"ten spending limits"
        """
        url = self.config.get_full_url("/card-issuance/risk-control/spending-limit")
        params = {"page": page, "size": size}
        
        if card_id is not None:
            params["card_id"] = card_id
        
        params.update(kwargs)
        logger.debug(f"请求消费限制列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_card_spending_limit(self, card_id: str) -> requests.Response:
        """
        获取指定卡片的消费限制
        
        Args:
            card_id: 卡片ID
            
        Returns:
            requests.Response: 响应对象，包含：
                - card_id: 卡片ID
                - spending_limit: 消费限制数组
                - associated_nested_program: 关联嵌套项目数组
        """
        url = self.config.get_full_url(f"/card-issuance/risk-control/spending-limit/{card_id}")
        logger.debug(f"请求卡片消费限制: {card_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_mcc_codes(
        self,
        code: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取MCC码列表
        
        Args:
            code: MCC码（4位数字）
            category: MCC类别
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：接口描述错误
            文档说"a maximum of ten card holders"应为"ten MCC codes"
        """
        url = self.config.get_full_url("/card-issuance/risk-control/mcc-code")
        params = {"page": page, "size": size}
        
        if code is not None:
            params["code"] = code
        if category is not None:
            params["category"] = category
        
        params.update(kwargs)
        logger.debug(f"请求MCC码列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应
        
        Args:
            response: requests.Response 对象
            
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
