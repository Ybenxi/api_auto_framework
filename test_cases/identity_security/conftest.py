"""
Identity Security 模块级配置

⚠️ Token 说明：
  Identity Security 接口使用专用 token（通过 sign-in 接口获取），
  不使用全局 OAuth2 token。测试会自动通过 identity_session fixture
  建立使用专用 token 的 session。

  专用 token sign-in 参数（已内置，测试时自动使用）：
    username: byan@fintechautomation.com
    encoded_password: RSA 加密固定值
    Client-Id: M6ztSk1TkUynnH+XVB9XgvyzuXhFH/AIogoKK8hLqkU=
"""
import pytest
import requests
from api.identity_security_api import IdentitySecurityAPI
from utils.logger import logger

# 模块级 marker
pytestmark = pytest.mark.identity_security

# 固定的 sign-in 凭证（Identity Security 专用）
_IS_USERNAME = "byan@fintechautomation.com"
_IS_ENCODED_PASSWORD = (
    "IjU4vtK/LWkr0YHwAFdg3d0ptYVyneOogfJJI7K0HY+zs9f2izM+bxOvMf4fVClrquKfHwxrGRqi"
    "lETN0uzuU4taY26yb5xiQImUfwnQ3fKCOl+KRJgP1U3JfZPIrTDUNoM0fpUXgTQ5lOGZd7cU+EzPy"
    "+o+8o10niUTfT8HcVT0HwYRlx0x/QublMhMPVL6D3OfmufXOnjyzxgsRWyBlwNnYRJ01oF3cKnfwu"
    "nc907aaLE2n1AWKDinhVceRgjOgAD4keiP5Jr4iraE6yzGzhM2FOFBXmgTvF8rzzB/Mbo9h1hDi4ea"
    "8/DBf5BGnyTs4803EzVCKIv266CpCImXAA=="
)


@pytest.fixture(scope="module")
def identity_session():
    """
    Identity Security 专用 session fixture（模块级）。
    用 sign-in 接口获取专用 access_token，建立独立 session。
    返回已设置 Bearer token 的 requests.Session。
    """
    from config.config import config
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    url = f"{config.base_url}/api/v1/cores/{config.core}/user/auth/sign-in"
    logger.info("Identity Security: 获取专用 access_token...")
    r = session.post(
        url,
        json={"username": _IS_USERNAME, "encoded_password": _IS_ENCODED_PASSWORD},
        headers={
            "Client-Id": IdentitySecurityAPI.CLIENT_ID,
            "Jmeter-Test": "Jmeter-Test",
            "Content-Type": "application/json"
        }
    )
    if r.status_code != 200 or r.json().get("code") != 200:
        pytest.skip(f"Identity Security sign-in 失败，跳过全部用例: {r.text[:200]}")

    token = r.json().get("data", {}).get("access_token")
    if not token:
        pytest.skip("sign-in 成功但未返回 access_token")

    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    logger.info("Identity Security: 专用 token 获取成功")
    yield session
    session.close()


@pytest.fixture(scope="module")
def identity_api(identity_session):
    """Identity Security 模块专用 API 实例（使用专用 token）"""
    return IdentitySecurityAPI(session=identity_session)
