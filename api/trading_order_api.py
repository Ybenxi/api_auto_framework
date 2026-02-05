"""
Trading Order 相关 API 封装
提供交易订单的创建、查询、更新、提交、取消等功能
遵循 API Object 模式，提供灵活的参数化接口
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import IssueType, OrderAction, QuantityType, OrderType, OrderStatus
from utils.logger import logger


class TradingOrderAPI:
    """
    Trading Order 管理 API 封装类
    包含订单生命周期的完整管理
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 TradingOrderAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 辅助查询接口 ====================
    
    def list_investment_financial_accounts(
        self,
        name: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取投资类型的 Financial Accounts 列表
        
        Args:
            name: Financial Account 名称，用于筛选
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/trading-orders/financial-accounts")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        
        params.update(kwargs)
        logger.debug(f"请求投资账户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_securities(
        self,
        issue_type: Optional[Union[str, List[str], IssueType]] = None,
        symbol: Optional[Union[str, List[str]]] = None,
        cusip: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取可交易证券列表
        
        Args:
            issue_type: 证券类型，可以是单个值或数组
            symbol: 证券代码，可以是单个值或数组
            cusip: CUSIP编号
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/trading-orders/securities")
        params = {"page": page, "size": size}
        
        # 处理issue_type（可能是数组）
        if issue_type is not None:
            if isinstance(issue_type, list):
                # 数组参数：使用重复的key
                params["issue_type"] = issue_type
            elif isinstance(issue_type, IssueType):
                params["issue_type"] = issue_type.value
            else:
                params["issue_type"] = issue_type
        
        # 处理symbol（可能是数组）
        if symbol is not None:
            if isinstance(symbol, list):
                params["symbol"] = symbol
            else:
                params["symbol"] = symbol
        
        if cusip is not None:
            params["cusip"] = cusip
        
        params.update(kwargs)
        logger.debug(f"请求证券列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 订单查询接口 ====================
    
    def list_orders(
        self,
        status: Optional[Union[str, OrderStatus]] = None,
        issue_type: Optional[Union[str, IssueType]] = None,
        order_action: Optional[Union[str, OrderAction]] = None,
        financial_account_id: Optional[str] = None,
        sub_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        cusip: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取交易订单列表
        
        Args:
            status: 订单状态
            issue_type: 证券类型
            order_action: 订单动作（Buy/Sell/Sell_All）
            financial_account_id: Financial Account ID
            sub_account_id: Sub Account ID
            symbol: 证券代码
            cusip: CUSIP编号
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/trading-orders")
        params = {"page": page, "size": size}
        
        if status is not None:
            params["status"] = str(status) if isinstance(status, OrderStatus) else status
        if issue_type is not None:
            params["issue_type"] = str(issue_type) if isinstance(issue_type, IssueType) else issue_type
        if order_action is not None:
            params["order_action"] = str(order_action) if isinstance(order_action, OrderAction) else order_action
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if sub_account_id is not None:
            params["sub_account_id"] = sub_account_id
        if symbol is not None:
            params["symbol"] = symbol
        if cusip is not None:
            params["cusip"] = cusip
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        
        params.update(kwargs)
        logger.debug(f"请求订单列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_order_detail(self, order_id: str) -> requests.Response:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/trading-orders/{order_id}")
        logger.debug(f"请求订单详情: {order_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 订单创建接口 ====================
    
    def create_draft_order(self, order_data: dict) -> requests.Response:
        """
        创建草稿订单（需要后续Submit）
        
        Args:
            order_data: 订单数据字典，包含：
                - financial_account_id 或 sub_account_id: 至少提供一个
                - order_action: (required) Buy/Sell/Sell_All
                - security_id: (required) 证券ID
                - quantity_type: (required) Shares/Dollars
                - quantity: (required) 数量（⚠️文档说int，实际可能需要float）
                - order_type: (required) Market_Order/Limit_Order/Stop_Order/Stop_Limit
                - limit_price: 条件必需（order_type=Limit_Order或Stop_Limit时）
                - stop_price: 条件必需（order_type=Stop_Order或Stop_Limit时）
                - timing: 可选，默认 Good_for_Day
                
        Returns:
            requests.Response: 响应对象，订单状态为 New
            
        Note:
            - 创建后需要调用 submit_order() 提交到市场
            - Draft订单可以通过 update_order() 修改
        """
        url = self.config.get_full_url("/trading-orders/draft")
        logger.debug(f"创建草稿订单: {order_data.get('order_action')} {order_data.get('security_id')}")
        
        response = self.session.post(url, json=order_data)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def initiate_order(self, order_data: dict) -> requests.Response:
        """
        直接发起交易订单（立即提交到市场）
        
        Args:
            order_data: 订单数据字典（参数与 create_draft_order 相同）
                
        Returns:
            requests.Response: 响应对象，订单状态为 In_Progress
            
        Note:
            ⚠️ 文档问题：Draft vs Initiate 的差异未明确说明
            根据响应推测：
            - Draft: status=New，需要手动Submit
            - Initiate: status=In_Progress，直接提交到市场
        """
        url = self.config.get_full_url("/trading-orders")
        logger.debug(f"直接发起订单: {order_data.get('order_action')} {order_data.get('security_id')}")
        
        response = self.session.post(url, json=order_data)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 订单操作接口 ====================
    
    def submit_order(self, order_id: str) -> requests.Response:
        """
        提交草稿订单到市场
        
        Args:
            order_id: 订单ID（必须是 Draft 状态的订单）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            - 只能提交status=New的订单
            - 提交后订单状态变为 Pending/In_Progress
        """
        url = self.config.get_full_url(f"/trading-orders/{order_id}/submit")
        logger.debug(f"提交订单: {order_id}")
        
        response = self.session.post(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def update_order(self, order_id: str, update_data: dict) -> requests.Response:
        """
        更新订单信息
        
        Args:
            order_id: 订单ID
            update_data: 要更新的数据（参数与创建订单相同）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要限制：Only draft orders can be updated
            - 只能更新 status=New 的订单
            - 已提交的订单无法更新
        """
        url = self.config.get_full_url(f"/trading-orders/{order_id}")
        logger.debug(f"更新订单: {order_id}")
        
        response = self.session.patch(url, json=update_data)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def cancel_order(self, order_id: str) -> requests.Response:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            - 文档说明：可以取消 pending 或 overnight 订单
            - 推测：New, Pending, Overnight 状态可取消
            - 已成交（Filled, Posted）不可取消
        """
        url = self.config.get_full_url(f"/trading-orders/{order_id}/cancel")
        logger.debug(f"取消订单: {order_id}")
        
        response = self.session.post(url)
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
            # Trading Order使用code包装层
            if "code" in data and data["code"] != 200:
                return {
                    "error": True,
                    "code": data["code"],
                    "message": data.get("error_message", "Unknown error")
                }
            
            # 提取实际数据
            content_data = data.get("data", data)
            
            return {
                "error": False,
                "content": content_data.get("content", []),
                "pageable": content_data.get("pageable", {}),
                "total_elements": content_data.get("total_elements", 0),
                "total_pages": content_data.get("total_pages", 0),
                "size": content_data.get("size", 0),
                "number": content_data.get("number", 0),
                "first": content_data.get("first", False),
                "last": content_data.get("last", False),
                "empty": content_data.get("empty", True)
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def parse_detail_response(self, response: requests.Response) -> dict:
        """
        解析详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和订单详情数据
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
            
            return {
                "error": False,
                "data": data.get("data", data)
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
