"""
Investment 相关 API 封装
提供投资报表、绩效分析、资产配置等功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
- JSON格式错误（trailing comma等5处）
- sharp_ratio拼写错误（应为sharpe_ratio）
- 响应字段未完全定义（benchmark/account对象内部结构）
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import FeeType, IntervalType
from utils.logger import logger


class InvestmentAPI:
    """
    Investment 报表 API 封装类
    包含活动摘要、趋势、绩效、资产配置等报表功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 InvestmentAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 活动报表接口 ====================
    
    def get_activity_summaries(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取活动摘要
        返回指定日期范围内的投资活动汇总数据
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - beginning_market_value: 期初市值
                - net_additions: 净增加额
                - contributions: 贡献额
                - withdrawals: 提取额
                - fees: 费用
                - gain_loss: 损益
                - market_appreciation_or_depreciation: 市场增值/贬值
                - income: 收益
                - ending_market_value: 期末市值
                
        Note:
            ⚠️ 文档问题：响应示例有trailing comma
        """
        url = self.config.get_full_url("/reports/investments/activity-summaries")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        
        params.update(kwargs)
        logger.debug(f"请求活动摘要: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_activity_trends(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取投资趋势
        返回指定日期范围内的市值变化趋势数组
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象（数组），每个元素包含：
                - date: 交易日期
                - market_value: 当日市值
                - net_addition: 当日净增加额
                - bmv_and_net_addition: 期初市值+净增加额
                
        Note:
            ⚠️ 文档问题：响应数组有trailing comma
        """
        url = self.config.get_full_url("/reports/investments/activity-trends")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        
        params.update(kwargs)
        logger.debug(f"请求活动趋势: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 绩效报表接口 ====================
    
    def get_performance_returns(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        fee: Optional[Union[str, FeeType]] = None,
        interval: Optional[Union[str, IntervalType]] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取绩效回报率
        返回指定日期范围内的回报率趋势
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            fee: 费用计算方式，默认 NET_OF_FEE
            interval: 数据间隔，默认 DAILY
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象（数组），每个元素包含：
                - date: 日期
                - return_rate: 回报率
        """
        url = self.config.get_full_url("/reports/investments/performances/returns")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if fee is not None:
            params["fee"] = str(fee) if isinstance(fee, FeeType) else fee
        if interval is not None:
            params["interval"] = str(interval) if isinstance(interval, IntervalType) else interval
        
        params.update(kwargs)
        logger.debug(f"请求绩效回报: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_performance_risks(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        fee: Optional[Union[str, FeeType]] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取绩效风险指标
        返回Alpha、Beta、R-Squared等风险统计指标
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            fee: 费用计算方式，默认 NET_OF_FEE
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - benchmark: 基准指标（默认S&P 500）
                - account: 账户指标
                - alpha: Alpha值（超额收益）
                - beta: Beta值（系统风险）
                - r_squared: R-Squared值（相关性）
                
        Note:
            ⚠️ 文档问题：
            1. sharp_ratio拼写错误（应为sharpe_ratio）
            2. benchmark/account对象内部字段未定义
        """
        url = self.config.get_full_url("/reports/investments/performances/risks")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if fee is not None:
            params["fee"] = str(fee) if isinstance(fee, FeeType) else fee
        
        params.update(kwargs)
        logger.debug(f"请求绩效风险: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 资产配置接口 ====================
    
    def get_asset_allocations(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取资产配置
        返回指定日期范围内的资产配置详情（嵌套结构）
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象（数组），每个元素包含：
                - date: 交易日期
                - allocations: 配置数组（嵌套结构，可能有3-4层）
                    - class: 资产类别（如Equities）
                    - segment: 细分类别（如US Equity-Other）
                    - name: 具体名称（如ALPHABET INC A）
                    - symbol: 代码（如GOOGL）
                    - units: 单位数
                    - market_value: 市值
                    - percent_of_level: 在当前层级的占比
                    - percent_of_total: 在总资产的占比
                    - children: 子级配置（递归结构）
                    
        Note:
            ⚠️ 文档问题：嵌套结构说明不完整
        """
        url = self.config.get_full_url("/reports/investments/asset-allocations")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        
        params.update(kwargs)
        logger.debug(f"请求资产配置: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_asset_allocations_comparison(
        self,
        begin_date: str,
        end_date: str,
        account_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取资产配置对比（实际 vs 目标）
        返回基于已应用策略的实际配置与目标配置的对比
        
        Args:
            begin_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account_id: Account ID（与financial_account_id二选一）
            financial_account_id: Financial Account ID（与account_id二选一）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - strategy_name: 应用的策略名称
                - allocations: 整体配置差异数组
                    - name: 资产名称
                    - actual_start_percent: 实际期初占比
                    - actual_end_percent: 实际期末占比
                    - actual_diff: 实际差异
                    - target_start_percent: 目标期初占比
                    - target_end_percent: 目标期末占比
                    - target_diff: 目标差异
                - dailyItems: 每日明细数组
                    - date: 日期
                    - allocations: 当日配置数组
                        - name: 资产名称
                        - market_value: 市值
                        - actual_percent: 实际占比
                        - target_percent: 目标占比
                        - percent_diff: 差异
                        
        Note:
            ⚠️ 文档问题：
            1. JSON格式错误（分号替代逗号）
            2. 字段命名不一致（actual_percent vs percent）
        """
        url = self.config.get_full_url("/reports/investments/asset-allocations/comparison")
        params = {"begin_date": begin_date, "end_date": end_date}
        
        if account_id is not None:
            params["account_id"] = account_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        
        params.update(kwargs)
        logger.debug(f"请求资产配置对比: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def validate_date_range(self, begin_date: str, end_date: str) -> bool:
        """
        验证日期范围有效性
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期
            
        Returns:
            bool: 日期范围是否有效
        """
        try:
            from datetime import datetime
            begin = datetime.strptime(begin_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return begin <= end
        except Exception as e:
            logger.error(f"日期验证失败: {e}")
            return False
