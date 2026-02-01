import allure
import pytest
from api.account_api import AccountAPI

@allure.feature("账户管理")
@allure.story("获取账户列表")
class TestAccountList:
    """
    账户列表接口测试用例集
    """

    @allure.title("成功获取账户列表")
    @allure.description("使用有效的 Token 调用账户列表接口，预期返回 200 状态码")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_get_account_list_success(self, login_session):
        # 1. 初始化 API 对象并传入已登录的 session
        account_api = AccountAPI(session=login_session)
        
        # 2. 调用接口
        with allure.step("调用获取账户列表接口"):
            response = account_api.list_accounts()
        
        # 3. 断言
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        with allure.step("验证响应业务代码"):
            res_json = response.json()
            assert res_json.get("code") == 200, f"业务代码错误: {res_json.get('code')}"
            
        with allure.step("验证返回数据结构"):
            assert "data" in res_json, "响应中缺少 data 字段"
            assert "content" in res_json["data"], "data 中缺少 content 列表"
            
            # 打印获取到的账户数量（仅作演示）
            accounts = res_json["data"]["content"]
            print(f"成功获取到 {len(accounts)} 个账户")

    @allure.title("带参数筛选账户列表")
    @pytest.mark.parametrize("name", ["Jerry", "test"])
    def test_get_account_list_with_filter(self, login_session, name):
        account_api = AccountAPI(session=login_session)
        
        with allure.step(f"调用接口并筛选名称: {name}"):
            response = account_api.list_accounts(name=name)
        
        assert response.status_code == 200
        assert response.json().get("code") == 200
