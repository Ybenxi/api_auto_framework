"""
Card Report 相关 API 封装
提供卡片支出报告、消费对比、Top消费查询功能

接口说明：
  card_number 参数可以传卡片的 id 或 tokenized card number
  时间格式：yyyy-MM-dd HH:mm:ss（UTC）
"""
import requests
from typing import Optional, Union
from config.config import config
from utils.logger import logger


class CardReportAPI:
    def __init__(self, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()

    def get_expenditure_category(
        self,
        card_number: str,
        start_time: str,
        end_time: str,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片支出分类报告
        GET /card/report/expenditure-category

        Args:
            card_number: 卡片 ID 或 tokenized 卡号（必填）
            start_time: 开始时间，格式 yyyy-MM-dd HH:mm:ss（UTC，必填）
            end_time: 结束时间，格式 yyyy-MM-dd HH:mm:ss（UTC，必填）
        Returns:
            {"code": 200, "data": [{merchant_category, total_settled_amount, total_amount, count}]}
        """
        url = self.config.get_full_url("/card/report/expenditure-category")
        params = {"card_number": card_number, "start_time": start_time, "end_time": end_time}
        params.update(kwargs)
        logger.debug(f"请求支出分类报告: card={card_number}")
        return self.session.get(url, params=params)

    def get_expenditure_comparison(
        self,
        card_number: str,
        time_period: str,
        start_time: str,
        end_time: str,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片支出对比报告
        GET /card/report/expenditure-comparison

        Args:
            card_number: 卡片 ID 或 tokenized 卡号（必填）
            time_period: 时间维度，Yearly 或 Monthly（必填）
            start_time: 开始时间（UTC，必填）
            end_time: 结束时间（UTC，必填）
        Returns:
            {"code": 200, "data": [{month, year, amount}]}
        """
        url = self.config.get_full_url("/card/report/expenditure-comparison")
        params = {
            "card_number": card_number,
            "time_period": time_period,
            "start_time": start_time,
            "end_time": end_time
        }
        params.update(kwargs)
        logger.debug(f"请求支出对比报告: card={card_number}, period={time_period}")
        return self.session.get(url, params=params)

    def get_top_expenditure(
        self,
        card_number: str,
        top_number: int,
        start_time: str,
        end_time: str,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片 Top 消费报告
        GET /card/report/top-expenditure

        Args:
            card_number: 卡片 ID 或 tokenized 卡号（必填）
            top_number: 返回条数上限（必填，正整数）
            start_time: 开始时间（UTC，必填）
            end_time: 结束时间（UTC，必填）
        Returns:
            {"code": 200, "data": {total_settled_amount, percentage, top_transactions: [...]}}
        """
        url = self.config.get_full_url("/card/report/top-expenditure")
        params = {
            "card_number": card_number,
            "top_number": top_number,
            "start_time": start_time,
            "end_time": end_time
        }
        params.update(kwargs)
        logger.debug(f"请求 Top 消费报告: card={card_number}, top={top_number}")
        return self.session.get(url, params=params)
