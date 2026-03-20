"""
Client List / Investment Positions API 封装
提供证券价格快照、历史图表、账户持仓交易等功能

接口全部为 GET 查询类，与股票交易相关：
  1. GET /investment/security/snapshot-price         证券价格快照
  2. GET /investment/security/historical-chart        证券历史图表
  3. GET /investment/positions/accounts/:id/settled-transactions/summary   已结算交易汇总
  4. GET /investment/positions/accounts/:id/pending-transactions/summary   待结算交易汇总
  5. GET /investment/positions/accounts/:id/pending-transactions/details   待结算交易明细
  6. GET /investment/positions/accounts/:id/settled-transactions           已结算交易列表
  7. GET /investment/positions/accounts/:id/pending-transactions           待结算交易列表
  8. GET /investment/positions/accounts/:id/settled-transactions/export    导出已结算交易
  9. GET /investment/positions/accounts/:id/pending-transactions/export    导出待结算交易
"""
import requests
from typing import Optional
from config.config import config
from utils.logger import logger


class ClientListAPI:
    def __init__(self, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()

    # ── 证券行情接口 ──────────────────────────────────────────────────

    def get_security_snapshot_price(
        self,
        symbol: str,
        issue_type: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取证券价格快照（每15分钟刷新）
        GET /investment/security/snapshot-price

        Args:
            symbol: 证券代码，必填，如 AAPL
            issue_type: 证券类型，默认 Common Stock
        Returns:
            {"code":200, "data":{symbol, price, change_dollar, change_percent, ...}}
        """
        url = self.config.get_full_url("/investment/security/snapshot-price")
        params = {"symbol": symbol}
        if issue_type:
            params["issue_type"] = issue_type
        params.update(kwargs)
        logger.debug(f"请求证券快照: symbol={symbol}, issue_type={issue_type}")
        return self.session.get(url, params=params)

    def get_security_historical_chart(
        self,
        symbol: str,
        issue_type: Optional[str] = None,
        interval: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取证券历史价格图表
        GET /investment/security/historical-chart

        Args:
            symbol: 证券代码，必填
            issue_type: 证券类型，默认 Common Stock
            interval: 时间跨度，默认 1D，枚举：1D/5D/1M/3M/1Y/ALL
        Returns:
            {"code":200, "data":{"points":[{price, timestamp}], "timestamp"}}
        """
        url = self.config.get_full_url("/investment/security/historical-chart")
        params = {"symbol": symbol}
        if issue_type:
            params["issue_type"] = issue_type
        if interval:
            params["interval"] = interval
        params.update(kwargs)
        logger.debug(f"请求历史图表: symbol={symbol}, interval={interval}")
        return self.session.get(url, params=params)

    # ── 账户持仓接口 ──────────────────────────────────────────────────

    def get_settled_transactions_summary(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取已结算交易汇总
        GET /investment/positions/accounts/:account_id/settled-transactions/summary
        Returns:
            {"code":200, "data":{"total_holding":{units,current_value,cost_basis,...},"timestamp"}}
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/settled-transactions/summary"
        )
        params = {}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        params.update(kwargs)
        return self.session.get(url, params=params)

    def get_pending_transactions_summary(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取待结算交易汇总
        GET /investment/positions/accounts/:account_id/pending-transactions/summary
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/pending-transactions/summary"
        )
        params = {}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        params.update(kwargs)
        return self.session.get(url, params=params)

    def get_pending_transactions_details(
        self,
        account_id: str,
        symbol: str,
        issue_type: str,
        financial_account_id: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 0,
        size: int = 200,
        **kwargs
    ) -> requests.Response:
        """
        获取待结算交易明细（分页）
        GET /investment/positions/accounts/:account_id/pending-transactions/details
        symbol 和 issue_type 必填
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/pending-transactions/details"
        )
        params = {"symbol": symbol, "issue_type": issue_type, "page": page, "size": size}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if sort:
            params["sort"] = sort
        params.update(kwargs)
        return self.session.get(url, params=params)

    def get_settled_transactions(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 0,
        size: int = 200,
        **kwargs
    ) -> requests.Response:
        """
        获取已结算交易列表（分页）
        GET /investment/positions/accounts/:account_id/settled-transactions
        Returns:
            {"code":200,"data":{"holdings":{"content":[...],"total_elements":N,...},"timestamp"}}
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/settled-transactions"
        )
        params = {"page": page, "size": size}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        if sort:
            params["sort"] = sort
        params.update(kwargs)
        return self.session.get(url, params=params)

    def get_pending_transactions(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 0,
        size: int = 200,
        **kwargs
    ) -> requests.Response:
        """
        获取待结算交易列表（分页）
        GET /investment/positions/accounts/:account_id/pending-transactions
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/pending-transactions"
        )
        params = {"page": page, "size": size}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        if sort:
            params["sort"] = sort
        params.update(kwargs)
        return self.session.get(url, params=params)

    def export_settled_transactions(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        sort: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        导出已结算交易为 XLS
        GET /investment/positions/accounts/:account_id/settled-transactions/export
        Returns: {"code":200,"data":"https://xxx.xls"}
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/settled-transactions/export"
        )
        params = {}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        if sort:
            params["sort"] = sort
        params.update(kwargs)
        return self.session.get(url, params=params)

    def export_pending_transactions(
        self,
        account_id: str,
        financial_account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        sort: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        导出待结算交易为 XLS
        GET /investment/positions/accounts/:account_id/pending-transactions/export
        Returns: {"code":200,"data":"https://xxx.xls"}
        """
        url = self.config.get_full_url(
            f"/investment/positions/accounts/{account_id}/pending-transactions/export"
        )
        params = {}
        if financial_account_id:
            params["financial_account_id"] = financial_account_id
        if symbol:
            params["symbol"] = symbol
        if name:
            params["name"] = name
        if sort:
            params["sort"] = sort
        params.update(kwargs)
        return self.session.get(url, params=params)
