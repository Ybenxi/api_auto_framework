"""
Account Summary 相关 API 封装
提供账户摘要信息的查询功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
- balance字段类型不一致（string vs number）
- 字段命名不一致（total_balance vs balance）
- Flat模式缺少响应示例
- Response Properties完全缺失
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import ClassificationMode
from utils.logger import logger


class AccountSummaryAPI:
    """
    Account Summary API 封装类
    提供账户摘要信息的查询功能，支持分类和扁平两种模式
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 AccountSummaryAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    def get_account_summary(
        self,
        classification_mode: Union[str, ClassificationMode],
        **kwargs
    ) -> requests.Response:
        """
        获取账户摘要
        返回可见账户的摘要信息，包括Financial Accounts、Sub Accounts和Cards
        
        Args:
            classification_mode: 分类模式
                - Categorized: 按Asset/Liability分组，再按record_type分组
                - Flat: 无分组（⚠️响应结构待验证）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 数据主体
                    - total_balance: 总余额
                    - asset_financial_accounts: 资产类金融账户（Categorized模式）
                        - total_balance: 资产总余额
                        - record_type: 按类型分组的记录数组
                    - liability_financial_accounts: 负债类金融账户（Categorized模式）
                        - total_balance: 负债总余额
                        - record_type: 按类型分组的记录数组
                    - debit_cards: 借记卡数组
                    
        Note:
            ⚠️ 文档问题：
            1. balance字段可能是string也可能是number
            2. Flat模式响应结构未知（缺少示例）
            3. 字段命名不一致（total_balance vs balance）
        """
        url = self.config.get_full_url("/account/summary")
        params = {}
        
        if isinstance(classification_mode, ClassificationMode):
            params["classification_mode"] = classification_mode.value
        else:
            params["classification_mode"] = classification_mode
        
        params.update(kwargs)
        logger.debug(f"请求账户摘要: classification_mode={params['classification_mode']}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_categorized_response(self, response: requests.Response) -> dict:
        """
        解析Categorized模式响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 解析后的数据，包含：
                - error: 是否有错误
                - total_balance: 总余额（转换为float）
                - asset_balance: 资产总余额
                - liability_balance: 负债总余额
                - financial_accounts_count: 金融账户数量
                - sub_accounts_count: 子账户数量
                - debit_cards_count: 借记卡数量
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            
            # 检查业务code
            if data.get("code") != 200:
                return {
                    "error": True,
                    "code": data.get("code"),
                    "message": data.get("error_message", "Unknown error")
                }
            
            response_data = data.get("data", {})
            
            # 统计数量
            fa_count = 0
            sub_count = 0
            
            # 资产账户
            asset_fas = response_data.get("asset_financial_accounts", {})
            for record_type in asset_fas.get("record_type", []):
                fas = record_type.get("financial_accounts", [])
                fa_count += len(fas)
                for fa in fas:
                    sub_count += len(fa.get("sub_accounts", []))
            
            # 负债账户
            liability_fas = response_data.get("liability_financial_accounts", {})
            for record_type in liability_fas.get("record_type", []):
                fas = record_type.get("financial_accounts", [])
                fa_count += len(fas)
                for fa in fas:
                    sub_count += len(fa.get("sub_accounts", []))
            
            return {
                "error": False,
                "total_balance": self._to_float(response_data.get("total_balance")),
                "asset_balance": self._to_float(asset_fas.get("total_balance")),
                "liability_balance": self._to_float(liability_fas.get("total_balance")),
                "financial_accounts_count": fa_count,
                "sub_accounts_count": sub_count,
                "debit_cards_count": len(response_data.get("debit_cards", []))
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def parse_flat_response(self, response: requests.Response) -> dict:
        """
        解析Flat模式响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 解析后的数据
            
        Note:
            ⚠️ Flat模式响应结构未知，需要根据实际响应调整
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            
            # 检查业务code
            if data.get("code") != 200:
                return {
                    "error": True,
                    "code": data.get("code"),
                    "message": data.get("error_message", "Unknown error")
                }
            
            # Flat模式的具体结构待验证
            return {
                "error": False,
                "data": data.get("data", {}),
                "structure": "flat"
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def _to_float(self, value) -> float:
        """
        将balance字段统一转换为float
        兼容string和number两种格式
        
        Args:
            value: 原始值（可能是string或number或None）
            
        Returns:
            float: 转换后的浮点数，失败返回0.0
        """
        if value is None:
            return 0.0
        
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"无法转换为float: {value}, 错误: {e}")
            return 0.0

    def calculate_total_balance(self, parsed_data: dict) -> float:
        """
        计算并验证总余额
        
        Args:
            parsed_data: parse_categorized_response返回的数据
            
        Returns:
            float: 计算的总余额
        """
        if parsed_data.get("error"):
            return 0.0
        
        # 总余额 = 资产 - 负债
        asset = parsed_data.get("asset_balance", 0.0)
        liability = parsed_data.get("liability_balance", 0.0)
        
        return asset - liability
