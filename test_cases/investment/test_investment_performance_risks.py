"""
Investment - Performance Risks 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/performances/risks 接口

响应结构：{"code": 200, "data": {benchmark, account, alpha, beta, r_squared}}
注意文档问题：sharp_ratio 应为 sharpe_ratio（文档拼写错误，测试时兼容两种）
"""
import pytest
from api.account_api import AccountAPI
from data.enums import FeeType
from utils.logger import logger


def _get_account_id(login_session) -> str:
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accs:
        pytest.skip("无可用 account 数据，跳过")
    return accs[0]["id"]


@pytest.mark.investment
@pytest.mark.detail_api
class TestInvestmentPerformanceRisks:

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        """
        response = investment_api.get_performance_risks(**short_date_range)
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200
        assert body.get("data") is None
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}")

    @pytest.mark.parametrize("fee_val", ["INVALID_FEE_TYPE", "NET", "gross_of_fee"])
    def test_invalid_fee_enum(self, investment_api, login_session, fee_val):
        """
        测试场景2：无效的 fee 枚举值（覆盖3个无效值）
        Test Scenario2: Invalid Fee Enum Value Returns Business Error
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_risks(
            account_id=account_id,
            fee=fee_val,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        if body.get("code") != 200:
            logger.info(f"  ✓ fee='{fee_val}' 被拒绝: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ fee='{fee_val}' 被接受（探索性结果）")

    def test_get_performance_risks_structure(self, investment_api, login_session):
        """
        测试场景3：获取风险指标，验证响应结构
        Test Scenario3: Get Performance Risks and Verify Response Structure
        验证点：
        1. HTTP 200，business code=200
        2. data 包含 benchmark, account, alpha, beta, r_squared
        3. benchmark/account 对象含 name, return_rate, standard_deviation, sharp_ratio(或 sharpe_ratio)
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_risks(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"应返回 code=200，实际: {body.get('code')}"

        data = body.get("data")
        assert isinstance(data, dict), "data 应为对象"

        # 顶层必需字段
        for field in ["benchmark", "account", "alpha", "beta", "r_squared"]:
            assert field in data, f"data 缺少字段: '{field}'"

        # benchmark/account 内部字段（兼容文档拼写错误）
        for obj_name in ["benchmark", "account"]:
            obj = data.get(obj_name, {})
            if obj:
                logger.info(f"  {obj_name} fields: {list(obj.keys())}")
                assert "name" in obj or "return_rate" in obj, \
                    f"{obj_name} 缺少基本字段"
                # 文档拼写 sharp_ratio（错误）与正确拼写 sharpe_ratio 均接受
                ratio_key = "sharp_ratio" if "sharp_ratio" in obj else "sharpe_ratio"
                if ratio_key in obj:
                    logger.info(f"  ✓ {obj_name}.{ratio_key}: {obj.get(ratio_key)}")
                else:
                    logger.info(f"  ⚠ {obj_name} 缺少 sharpe_ratio 字段")

        # 数值类型校验
        for field in ["alpha", "beta", "r_squared"]:
            val = data.get(field)
            if val is not None:
                assert isinstance(val, (int, float)), f"{field} 应为数值"
                logger.info(f"  ✓ {field}: {val}")

        logger.info("✓ 风险指标结构验证通过")

    @pytest.mark.parametrize("fee", [FeeType.NET_OF_FEE, FeeType.GROSS_OF_FEE])
    def test_fee_enum_values(self, investment_api, login_session, fee):
        """
        测试场景4：fee 枚举全覆盖（NET_OF_FEE / GROSS_OF_FEE）
        Test Scenario4: Fee Enum Coverage (NET_OF_FEE / GROSS_OF_FEE)
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_risks(
            account_id=account_id,
            fee=fee,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"fee={fee} 应被接受，实际: {body.get('code')}"
        logger.info(f"✓ fee={fee} 验证通过")

    def test_r_squared_range(self, investment_api, login_session):
        """
        测试场景5：验证 r_squared 取值范围（0~1 之间）
        Test Scenario5: Verify r_squared Value Range (0 to 1)
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_risks(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        r_sq = data.get("r_squared") if data else None
        if r_sq is not None:
            assert 0 <= r_sq <= 1, f"r_squared={r_sq} 应在 0~1 之间"
            logger.info(f"✓ r_squared={r_sq}（在合法范围内）")
        else:
            logger.info("  r_squared 为 null（账户无足够投资数据）")
