import requests
from config.config import config

class AccountAPI:
    """
    账户相关 API 封装
    """
    def __init__(self, session=None):
        self.base_url = config.base_url
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    def list_accounts(self, name="", account_number="", email=""):
        """
        获取账户列表
        :param name: 筛选名称
        :param account_number: 筛选账号
        :param email: 筛选邮箱
        """
        url = f"{self.base_url}/api/v1/cores/actc/accounts"
        
        params = {
            "name": name,
            "account_number": account_number,
            "email": email
        }
        
        # 使用 session 发送 GET 请求
        response = self.session.get(url, params=params)
        
        return response

# 导出类
