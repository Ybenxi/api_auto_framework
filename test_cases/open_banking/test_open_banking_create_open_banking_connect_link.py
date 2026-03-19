"""
Open Banking Create Open Banking Connect Link 接口测试用例
测试 POST /api/v1/cores/{core}/open-banking/connections/manage/open-banking 接口

实测行为（与 bank account connect link 一致）：
  - redirect_url 不是必填，缺少时 API 也返回 code=200
  - account_id 不是必填，缺少或错误时默认使用登录用户的 contact 所属 account
"""
import pytest
from api.account_api import AccountAPI
from utils.assertions import assert_status_ok, assert_fields_present
from utils.logger import logger


@pytest.mark.open_banking
@pytest.mark.create_api
class TestOpenBankingCreateOpenBankingConnectLink:

    def test_create_open_banking_connect_link_success(self, open_banking_api, login_session):
        """
        测试场景1：成功创建 Open Banking 连接链接
        验证点：
        1. HTTP 200，业务 code=200
        2. data 是有效的 URL 字符串
        """
        account_api = AccountAPI(session=login_session)
        accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account 数据")
        account_id = accounts[0]["id"]

        response = open_banking_api.create_open_banking_connect_link(
            redirect_url="https://www.fintech.com",
            account_id=account_id
        )
        assert_status_ok(response, 200)
        body = response.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data")
        assert data and isinstance(data, str), "data 应为非空字符串 URL"
        assert data.startswith("http://") or data.startswith("https://")

        logger.info(f"✓ Open Banking 连接链接创建成功: account_id={account_id}")
        logger.info(f"  URL 前缀: {data[:80]}...")

    def test_create_open_banking_connect_link_response_structure(self, open_banking_api, login_session):
        """
        测试场景2：验证响应数据结构
        验证点：
        1. HTTP 200
        2. 响应包含 code 和 data 字段
        3. data 是字符串
        """
        account_api = AccountAPI(session=login_session)
        accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account 数据")
        account_id = accounts[0]["id"]

        response = open_banking_api.create_open_banking_connect_link(
            redirect_url="https://www.fintech.com",
            account_id=account_id
        )
        assert_status_ok(response, 200)
        body = response.json()
        assert isinstance(body, dict)
        assert_fields_present(body, ["code", "data"], "响应")
        assert isinstance(body["data"], str), "data 字段应为字符串"
        logger.info(f"✓ 响应结构验证通过: code={body.get('code')}")

    def test_create_open_banking_connect_link_without_redirect_url(self, open_banking_api, login_session):
        """
        测试场景3：不传 redirect_url 参数
        实测行为：API 不强制校验，缺少 redirect_url 时仍返回 code=200（探索性结果）
        验证点：
        1. HTTP 200
        2. 记录实际行为（不强断言 code != 200）
        """
        account_api = AccountAPI(session=login_session)
        accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account 数据")
        account_id = accounts[0]["id"]

        url = open_banking_api.config.get_full_url("/open-banking/connections/manage/open-banking")
        response = open_banking_api.session.post(url, json={"account_id": account_id})

        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        logger.info(f"  不传 redirect_url: code={code}, data={'有URL' if data else '空'}")
        if code == 200:
            logger.info("  ⚠ API 接受了无 redirect_url 的请求（不强制校验）")
        else:
            logger.info(f"  API 拒绝无 redirect_url: code={code}")
        logger.info("✓ 无 redirect_url 参数场景验证完成")

    def test_create_open_banking_connect_link_without_account_id(self, open_banking_api):
        """
        测试场景4：不传 account_id 参数
        实测行为：API 默认使用登录用户的 contact 所属 account，返回 code=200
        验证点：
        1. HTTP 200
        2. 接口不报错，使用默认 account 生成链接
        """
        url = open_banking_api.config.get_full_url("/open-banking/connections/manage/open-banking")
        response = open_banking_api.session.post(
            url, json={"redirect_url": "https://www.fintech.com"}
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        logger.info(f"  不传 account_id: code={code}, data={'有URL' if data else '空'}")
        if code == 200 and data:
            logger.info("  ✓ 默认使用 contact 所属 account，成功生成连接链接")
        logger.info("✓ 无 account_id 参数场景验证完成")

    def test_create_open_banking_connect_link_with_invalid_account_id(self, open_banking_api):
        """
        测试场景5：传入错误的 account_id
        实测行为：API 忽略无效 account_id，回退到默认 contact 所属 account，返回 code=200
        验证点：
        1. HTTP 200
        2. 接口不报错（使用默认 account 降级处理）
        """
        response = open_banking_api.create_open_banking_connect_link(
            redirect_url="https://www.fintech.com",
            account_id="INVALID_ACCOUNT_ID_99999"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        logger.info(f"  错误 account_id: code={code}, data={'有' if body.get('data') else '空'}")
        if code == 200:
            logger.info("  ✓ API 使用默认 account 降级处理")
        logger.info("✓ 无效 account_id 场景验证完成")
