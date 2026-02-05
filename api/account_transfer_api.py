"""
Account Transfer 相关 API 封装
提供UniFi平台内管理账户之间的资金转移功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. HTTP方法标注错误（示例中GET/POST混淆）
2. 响应格式不一致（部分无code包装层）
3. amount字段类型不一致（string vs number）
4. 多个响应字段未在Properties定义（fee, completed_date, direction等）
5. 接口描述错误（说ACH应为Account Transfer）
6. 与Internal Pay模块高度相似但差异未说明
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import PaymentTransactionStatus, PaymentTransactionType, AccountSubType
from utils.logger import logger
from utils.type_converters import to_float


class AccountTransferAPI:
    """
    Account Transfer API 封装类
    提供UniFi平台内管理账户之间的资金转移功能
    
    核心特性：
    - 实时结算
    - 跨Profile灵活性（可跨不同profile转账）
    - 成本效率（内部处理，无外部清算）
    - 可审计性强
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 AccountTransferAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 查询接口 ====================
    
    def list_transactions(
        self,
        transaction_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[Union[str, PaymentTransactionStatus]] = None,
        payer_financial_account_id: Optional[str] = None,
        payee_financial_account_id: Optional[str] = None,
        transaction_type: Optional[Union[str, PaymentTransactionType]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取Account Transfer交易列表
        
        Args:
            transaction_id: 交易ID
            start_date: 开始日期（UTC，格式 YYYY-MM-DD）
            end_date: 结束日期（UTC，格式 YYYY-MM-DD）
            status: 交易状态
            payer_financial_account_id: 付款方Financial Account ID
            payee_financial_account_id: 收款方Financial Account ID
            transaction_type: 交易类型（Credit或Debit）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层（直接返回分页结构）
            2. 响应中包含direction字段，但Properties中未定义
            3. transaction_type参数描述错误（说Internal Pay应为Account Transfer）
        """
        url = self.config.get_full_url("/money-movements/account-transfer/transactions")
        params = {"page": page, "size": size}
        
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if status is not None:
            params["status"] = str(status) if isinstance(status, PaymentTransactionStatus) else status
        if payer_financial_account_id is not None:
            params["payer_financial_account_id"] = payer_financial_account_id
        if payee_financial_account_id is not None:
            params["payee_financial_account_id"] = payee_financial_account_id
        if transaction_type is not None:
            params["transaction_type"] = str(transaction_type) if isinstance(transaction_type, PaymentTransactionType) else transaction_type
        
        params.update(kwargs)
        logger.debug(f"请求Account Transfer交易列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_financial_accounts(
        self,
        account_number: Optional[str] = None,
        name: Optional[str] = None,
        sub_type: Optional[Union[str, AccountSubType]] = None,
        account_ids: Optional[Union[List[str], str]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取可用于Account Transfer的Financial Accounts列表
        
        Args:
            account_number: Financial Account账号
            name: Financial Account名称（模糊搜索）
            sub_type: 账户子类型（Checking/Savings）
            account_ids: 账户ID数组或逗号分隔字符串
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 接口描述错误（说ACH应为Account Transfer）
            3. HTTP方法示例错误（GET写成POST）
        """
        url = self.config.get_full_url("/money-movements/account-transfer/financial-accounts")
        params = {"page": page, "size": size}
        
        if account_number is not None:
            params["account_number"] = account_number
        if name is not None:
            params["name"] = name
        if sub_type is not None:
            params["sub_type"] = str(sub_type) if isinstance(sub_type, AccountSubType) else sub_type
        if account_ids is not None:
            if isinstance(account_ids, list):
                params["account_ids"] = ",".join(account_ids)
            else:
                params["account_ids"] = account_ids
        
        params.update(kwargs)
        logger.debug(f"请求Account Transfer可用账户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 交易操作接口 ====================
    
    def initiate_transfer(
        self,
        payer_financial_account_id: str,
        payee_financial_account_id: str,
        amount: str,
        payer_sub_account_id: Optional[str] = None,
        payee_sub_account_id: Optional[str] = None,
        memo: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起Account Transfer转账
        
        Args:
            payer_financial_account_id: 付款方Financial Account ID（必需）
            payee_financial_account_id: 收款方Financial Account ID（必需）
            amount: 转账金额（必需，string格式）
            payer_sub_account_id: 付款方Sub Account ID（条件必需）
            payee_sub_account_id: 收款方Sub Account ID（条件必需）
            memo: 备注（可选）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：这是真实的转账操作，会扣款
            测试建议：skip或使用测试账户
            
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 条件必需字段逻辑不清
            3. 英文语法错误（transfer of funds）
        """
        url = self.config.get_full_url("/money-movements/account-transfer")
        
        payload = {
            "payer_financial_account_id": payer_financial_account_id,
            "payee_financial_account_id": payee_financial_account_id,
            "amount": amount
        }
        
        if payer_sub_account_id is not None:
            payload["payer_sub_account_id"] = payer_sub_account_id
        if payee_sub_account_id is not None:
            payload["payee_sub_account_id"] = payee_sub_account_id
        if memo is not None:
            payload["memo"] = memo
        
        payload.update(kwargs)
        logger.warning(f"⚠️ 发起Account Transfer: {amount} from {payer_financial_account_id} to {payee_financial_account_id}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def quote_transaction_fee(
        self,
        financial_account_id: str,
        amount: str,
        **kwargs
    ) -> requests.Response:
        """
        计算Account Transfer交易费用
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 交易金额（必需）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 费用信息
                    - financial_account_id: 账户ID
                    - fee: 费用金额
                    - amount: 交易金额
                    - same_day: 是否当天到账（⚠️未定义）
                    
        Note:
            ⚠️ 文档问题：
            1. same_day字段未说明
            2. HTTP方法示例错误（POST写成GET）
        """
        url = self.config.get_full_url("/money-movements/account-transfer/fee")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount
        }
        
        payload.update(kwargs)
        logger.debug(f"计算Account Transfer费用: amount={amount}, account={financial_account_id}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应
        兼容无code包装层的格式
        
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
            
            # Account Transfer的List接口无code包装层
            if isinstance(data, dict) and "content" in data:
                return {
                    "error": False,
                    "content": data.get("content", []),
                    "pageable": data.get("pageable", {}),
                    "total_elements": data.get("total_elements", 0),
                    "total_pages": data.get("total_pages", 0),
                    "no_code_wrapper": True
                }
            elif isinstance(data, dict) and "code" in data:
                if data["code"] != 200:
                    return {
                        "error": True,
                        "code": data["code"],
                        "message": data.get("error_message", "Unknown error")
                    }
                
                content_data = data.get("data", {})
                return {
                    "error": False,
                    "content": content_data.get("content", []),
                    "pageable": content_data.get("pageable", {}),
                    "total_elements": content_data.get("total_elements", 0),
                    "total_pages": content_data.get("total_pages", 0)
                }
            else:
                return {
                    "error": True,
                    "message": "Unknown response format",
                    "raw_response": response.text
                }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def parse_transfer_response(self, response: requests.Response) -> dict:
        """
        解析转账响应
        兼容无code包装层的格式
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和交易数据
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            
            # Transfer响应无code包装层
            if isinstance(data, dict) and "id" in data:
                return {
                    "error": False,
                    "data": data,
                    "no_code_wrapper": True
                }
            elif isinstance(data, dict) and "code" in data:
                if data["code"] != 200:
                    return {
                        "error": True,
                        "code": data["code"],
                        "message": data.get("error_message", "Unknown error")
                    }
                return {
                    "error": False,
                    "data": data.get("data", {})
                }
            else:
                return {
                    "error": True,
                    "message": "Unknown response format",
                    "raw_response": response.text
                }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
