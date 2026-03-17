"""
Financial Account Related Positions 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/holdings 接口
对应文档标题: Retrieve Related Positions
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


def _get_fa_id_with_positions(fa_api: FinancialAccountAPI, page_size: int = 20):
    """
    遍历 FA 列表，找到第一个有持仓（Positions/Holdings）数据的 FA ID。
    返回 (fa_id, first_position) 或 (None, None)。
    """
    list_resp = fa_api.list_financial_accounts(page=0, size=page_size)
    if list_resp.status_code != 200:
        return None, None

    accounts = fa_api.parse_list_response(list_resp).get("content", [])
    for acc in accounts:
        fa_id = acc.get("id")
        if not fa_id:
            continue
        resp = fa_api.get_related_positions(fa_id, page=0, size=1)
        if resp.status_code != 200:
            continue
        positions = fa_api.parse_list_response(resp).get("content", [])
        if positions:
            logger.info(f"  找到有持仓数据的 FA: {fa_id}")
            return fa_id, positions[0]

    return None, None


@pytest.mark.financial_account
@pytest.mark.positions_api
class TestFinancialAccountRetrieveRelatedPositions:
    """
    Financial Account 相关持仓查询接口测试用例集
    """

    def test_retrieve_related_positions_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的持仓（Holdings）
        验证点：
        1. 遍历 FA 列表，找到有持仓数据的 FA
        2. 接口返回 200，total_elements > 0
        3. 必需字段存在
        4. 隔离性验证：返回的持仓属于该 FA
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_pos = _get_fa_id_with_positions(fa_api)
        if not fa_id:
            pytest.skip("未找到有持仓数据的 Financial Account")

        logger.info(f"使用有数据的 Financial Account ID: {fa_id}")

        positions_response = fa_api.get_related_positions(fa_id, page=0, size=10)
        assert positions_response.status_code == 200

        parsed_positions = fa_api.parse_list_response(positions_response)
        assert not parsed_positions.get("error")

        positions = parsed_positions.get("content", [])
        assert len(positions) > 0, f"FA {fa_id} 应有持仓数据，但返回空列表"
        logger.info(f"  总持仓数: {parsed_positions['total_elements']}, 返回 {len(positions)} 条")

        # 必需字段验证
        pos = positions[0]
        required_fields = ["id", "symbol"]
        for field in required_fields:
            assert field in pos, f"持仓记录缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {pos.get(field)}")

        # financial_account_id 一致性（如字段存在）
        if "financial_account_id" in pos:
            for p in positions:
                assert p.get("financial_account_id") == fa_id, \
                    f"持仓 financial_account_id={p.get('financial_account_id')} 与请求 {fa_id} 不一致"
            logger.info("  ✓ 所有持仓 financial_account_id 一致")

        logger.info("✓ 获取持仓成功")

    def test_retrieve_related_positions_with_symbol_filter(self, login_session):
        """
        测试场景2：使用 symbol 精确筛选持仓
        从有数据的 FA 中取真实 symbol，验证筛选结果的 symbol 与筛选值一致
        验证点：
        1. 接口返回 200
        2. 返回的每条持仓 symbol 与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_pos = _get_fa_id_with_positions(fa_api)
        if not fa_id or not first_pos:
            pytest.skip("未找到有持仓数据的 Financial Account")

        real_symbol = first_pos.get("symbol", "")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"使用真实 symbol: {real_symbol}（FA: {fa_id}）")

        positions_response = fa_api.get_related_positions(fa_id, symbol=real_symbol, page=0, size=10)
        assert positions_response.status_code == 200

        positions = fa_api.parse_list_response(positions_response).get("content", [])
        assert len(positions) > 0, f"symbol='{real_symbol}' 筛选结果为空"

        for pos in positions:
            assert pos.get("symbol") == real_symbol, \
                f"返回的持仓 symbol='{pos.get('symbol')}' 与筛选值 '{real_symbol}' 不一致"

        logger.info(f"✓ symbol 筛选验证通过，返回 {len(positions)} 条")

    def test_retrieve_related_positions_with_cusip_filter(self, login_session):
        """
        测试场景3：使用 cusip 精确筛选持仓
        从有数据的 FA 中取真实 cusip，验证筛选结果的 cusip 与筛选值一致
        验证点：
        1. 接口返回 200
        2. 返回的每条持仓 cusip 与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_pos = _get_fa_id_with_positions(fa_api)
        if not fa_id or not first_pos:
            pytest.skip("未找到有持仓数据的 Financial Account")

        real_cusip = first_pos.get("cusip", "")
        if not real_cusip:
            pytest.skip("cusip 字段为空，跳过 cusip 筛选测试")

        logger.info(f"使用真实 cusip: {real_cusip}（FA: {fa_id}）")

        positions_response = fa_api.get_related_positions(fa_id, cusip=real_cusip, page=0, size=10)
        assert positions_response.status_code == 200

        positions = fa_api.parse_list_response(positions_response).get("content", [])
        assert len(positions) > 0, f"cusip='{real_cusip}' 筛选结果为空"

        for pos in positions:
            assert pos.get("cusip") == real_cusip, \
                f"返回的持仓 cusip='{pos.get('cusip')}' 与筛选值 '{real_cusip}' 不一致"

        logger.info(f"✓ cusip 筛选验证通过，返回 {len(positions)} 条")

    def test_retrieve_related_positions_pagination(self, login_session):
        """
        测试场景4：验证持仓列表分页功能
        验证点：
        1. 使用有数据的 FA，确保分页元数据有意义
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size，total_elements > 0
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_positions(fa_api)
        if not fa_id:
            pytest.skip("未找到有持仓数据的 Financial Account")

        positions_response = fa_api.get_related_positions(fa_id, page=0, size=5)
        assert positions_response.status_code == 200

        parsed_positions = fa_api.parse_list_response(positions_response)

        assert parsed_positions["size"] == 5, f"size 不正确: {parsed_positions['size']}"
        assert parsed_positions["number"] == 0, f"number 不正确: {parsed_positions['number']}"
        assert len(parsed_positions.get("content", [])) <= 5, "返回数量超过 size=5"
        assert parsed_positions["total_elements"] > 0, \
            f"有数据的 FA 分页 total_elements 应 > 0，实际: {parsed_positions['total_elements']}"

        logger.info(f"✓ 分页测试通过: total={parsed_positions['total_elements']}, "
                    f"size={parsed_positions['size']}, page={parsed_positions['number']}")

    def test_retrieve_related_positions_response_fields(self, login_session):
        """
        测试场景5：验证持仓响应字段完整性
        验证点：
        1. 使用有数据的 FA
        2. 持仓对象必须包含必需字段（assert 断言）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_pos = _get_fa_id_with_positions(fa_api)
        if not fa_id or not first_pos:
            pytest.skip("未找到有持仓数据的 Financial Account")

        required_fields = ["id", "symbol"]

        logger.info("验证持仓必需字段")
        for field in required_fields:
            assert field in first_pos, f"持仓记录缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {first_pos.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    def test_retrieve_related_positions_with_invalid_fa_id(self, login_session):
        """
        测试场景6：使用无效 FA ID 查询持仓
        验证点：
        1. 使用格式无效 ID："invalid_fa_id_99999"
        2. 服务器返回 200
        3. 返回空列表 或 code != 200
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("使用无效 FA ID 查询持仓")
        positions_response = fa_api.get_related_positions("invalid_fa_id_99999", page=0, size=10)
        assert positions_response.status_code == 200

        response_body = positions_response.json()
        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  返回业务错误 code={response_body.get('code')}")
        else:
            parsed_positions = fa_api.parse_list_response(positions_response)
            assert len(parsed_positions.get("content", [])) == 0, \
                f"无效 FA ID 应返回空列表，实际返回 {len(parsed_positions.get('content', []))} 条"
            logger.info("  无效 FA ID 返回空持仓列表")

        logger.info("✓ 无效 FA ID 持仓查询验证通过")

    def test_retrieve_related_positions_with_invisible_fa_id(self, login_session):
        """
        测试场景7：使用越权 FA ID 查询持仓 → 返回空或拒绝
        验证点：
        1. 使用越权 FA ID：241010195850134683（ACTC Yhan FA）
        2. 服务器返回 200
        3. 返回空列表 或 code=506
        """
        fa_api = FinancialAccountAPI(session=login_session)

        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA
        logger.info(f"使用越权 FA ID 查询持仓: {invisible_fa_id}")

        positions_response = fa_api.get_related_positions(invisible_fa_id, page=0, size=10)
        assert positions_response.status_code == 200

        response_body = positions_response.json()
        if isinstance(response_body, dict) and response_body.get("code") == 506:
            logger.info("  返回 code=506 visibility permission deny")
        else:
            parsed_positions = fa_api.parse_list_response(positions_response)
            assert len(parsed_positions.get("content", [])) == 0, \
                f"越权 FA ID 应返回空持仓列表，实际返回 {len(parsed_positions.get('content', []))} 条"
            logger.info("  越权 FA ID 返回空持仓列表")

        logger.info("✓ 越权 FA ID 持仓查询验证通过")
