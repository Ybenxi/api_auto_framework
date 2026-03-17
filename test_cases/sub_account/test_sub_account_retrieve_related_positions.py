"""
Sub Account Related Positions 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/holdings 接口
对应文档标题: Retrieve Related Positions
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.positions_api
class TestSubAccountRetrieveRelatedPositions:
    """
    Sub Account 相关持仓查询接口测试用例集
    """

    def _get_sa_id(self, sa_api):
        resp = sa_api.list_sub_accounts(page=0, size=1)
        assert resp.status_code == 200
        parsed = sa_api.parse_list_response(resp)
        subs = parsed.get("content", [])
        return subs[0].get("id") if subs else None

    def test_retrieve_related_positions_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 相关的持仓（Holdings）
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用持仓接口返回 200
        3. 必需字段存在
        4. 隔离性验证：返回的持仓属于该 Sub Account
        """
        sa_api = SubAccountAPI(session=login_session)

        list_response = sa_api.list_sub_accounts(page=0, size=2)
        assert list_response.status_code == 200

        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行测试")

        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")

        positions_response = sa_api.get_related_positions(sub_account_id, page=0, size=10)
        assert positions_response.status_code == 200, \
            f"接口返回状态码错误: {positions_response.status_code}"

        parsed_positions = sa_api.parse_list_response(positions_response)
        assert not parsed_positions.get("error"), f"响应解析失败: {parsed_positions.get('message')}"

        positions = parsed_positions.get("content", [])
        logger.info(f"  总持仓数: {parsed_positions['total_elements']}, 返回 {len(positions)} 条")

        if positions:
            pos = positions[0]
            required_fields = ["id", "symbol"]
            for field in required_fields:
                assert field in pos, f"持仓记录缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {pos.get(field)}")

            # sub_account_id 一致性验证
            if "sub_account_id" in pos:
                for p in positions:
                    assert p.get("sub_account_id") == sub_account_id, \
                        f"持仓 sub_account_id={p.get('sub_account_id')} 与请求 {sub_account_id} 不一致"
                logger.info(f"  ✓ 所有持仓 sub_account_id 一致")
            elif len(sub_accounts) >= 2:
                sa2_id = sub_accounts[1].get("id")
                pos2_resp = sa_api.get_related_positions(sa2_id, page=0, size=10)
                parsed2 = sa_api.parse_list_response(pos2_resp)
                sa1_ids = {p["id"] for p in positions if "id" in p}
                sa2_ids = {p["id"] for p in parsed2.get("content", []) if "id" in p}
                overlap = sa1_ids & sa2_ids
                assert not overlap, f"两个 Sub Account 持仓有重叠: {overlap}"
                logger.info(f"  ✓ 隔离性验证通过：SA1={len(sa1_ids)}条, SA2={len(sa2_ids)}条, 无重叠")

        logger.info("✓ 获取持仓成功")

    def test_retrieve_related_positions_with_symbol_filter(self, login_session):
        """
        测试场景2：使用 symbol 筛选持仓
        先 list 获取真实 symbol，再用它筛选，验证返回数据匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条持仓 symbol 与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        # 获取真实 symbol
        base_resp = sa_api.get_related_positions(sa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = sa_api.parse_list_response(base_resp)
        base_pos = base_parsed.get("content", [])

        if not base_pos:
            pytest.skip(f"Sub Account {sa_id} 无持仓数据，跳过 symbol 筛选测试")

        real_symbol = base_pos[0].get("symbol", "")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"  使用真实 symbol: {real_symbol}")

        positions_response = sa_api.get_related_positions(sa_id, symbol=real_symbol, page=0, size=10)
        assert positions_response.status_code == 200

        parsed_positions = sa_api.parse_list_response(positions_response)
        positions = parsed_positions.get("content", [])

        if positions:
            for pos in positions:
                assert pos.get("symbol") == real_symbol, \
                    f"返回的持仓 symbol='{pos.get('symbol')}' 与筛选值 '{real_symbol}' 不一致"
            logger.info(f"✓ symbol 筛选验证通过，返回 {len(positions)} 条")
        else:
            logger.info(f"  ⚠️ symbol='{real_symbol}' 筛选结果为空")

        logger.info("✓ Symbol 筛选测试完成")

    def test_retrieve_related_positions_with_cusip_filter(self, login_session):
        """
        测试场景3：使用 cusip 筛选持仓
        先 list 获取真实 cusip，再用它筛选，验证返回数据匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条持仓 cusip 与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        # 获取真实 cusip
        base_resp = sa_api.get_related_positions(sa_id, page=0, size=1)
        assert base_resp.status_code == 200
        base_parsed = sa_api.parse_list_response(base_resp)
        base_pos = base_parsed.get("content", [])

        if not base_pos:
            pytest.skip(f"Sub Account {sa_id} 无持仓数据，跳过 cusip 筛选测试")

        real_cusip = base_pos[0].get("cusip", "")
        if not real_cusip:
            pytest.skip("cusip 字段为空，跳过")

        logger.info(f"  使用真实 cusip: {real_cusip}")

        positions_response = sa_api.get_related_positions(sa_id, cusip=real_cusip, page=0, size=10)
        assert positions_response.status_code == 200

        parsed_positions = sa_api.parse_list_response(positions_response)
        positions = parsed_positions.get("content", [])

        if positions:
            for pos in positions:
                assert pos.get("cusip") == real_cusip, \
                    f"返回的持仓 cusip='{pos.get('cusip')}' 与筛选值 '{real_cusip}' 不一致"
            logger.info(f"✓ cusip 筛选验证通过，返回 {len(positions)} 条")
        else:
            logger.info(f"  ⚠️ cusip='{real_cusip}' 筛选结果为空")

        logger.info("✓ CUSIP 筛选测试完成")

    def test_retrieve_related_positions_pagination(self, login_session):
        """
        测试场景4：验证持仓列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        positions_response = sa_api.get_related_positions(sa_id, page=0, size=5)
        assert positions_response.status_code == 200

        parsed_positions = sa_api.parse_list_response(positions_response)

        assert parsed_positions["size"] == 5, f"size 不正确: {parsed_positions['size']}"
        assert parsed_positions["number"] == 0, f"number 不正确: {parsed_positions['number']}"
        assert len(parsed_positions.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总持仓数: {parsed_positions['total_elements']}")
        logger.info(f"  每页大小: {parsed_positions['size']}, 当前页: {parsed_positions['number']}")

    def test_retrieve_related_positions_response_fields(self, login_session):
        """
        测试场景5：验证持仓响应字段完整性
        验证点：
        1. 接口返回 200
        2. 持仓对象必须包含必需字段（assert 断言）
        """
        sa_api = SubAccountAPI(session=login_session)
        sa_id = self._get_sa_id(sa_api)
        if not sa_id:
            pytest.skip("没有可用的 Sub Account")

        positions_response = sa_api.get_related_positions(sa_id, page=0, size=1)
        assert positions_response.status_code == 200

        parsed_positions = sa_api.parse_list_response(positions_response)
        positions = parsed_positions.get("content", [])

        if not positions:
            pytest.skip("无持仓数据，跳过字段验证")

        pos = positions[0]
        required_fields = ["id", "symbol"]

        logger.info("验证持仓必需字段")
        for field in required_fields:
            assert field in pos, f"持仓记录缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {pos.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    def test_retrieve_related_positions_with_invisible_sub_account_id(self, login_session):
        """
        测试场景6：使用不在当前用户 visible 范围内的 sub_account_id 查询持仓
        验证点：
        1. 使用他人账户关联的 sub_account_id（不属于当前用户）
        2. 服务器返回 200 OK（统一错误处理设计）
        3. 返回空列表 或 code != 200（服务端按 visible 范围过滤）
        """
        sa_api = SubAccountAPI(session=login_session)

        invisible_sa_id = "241010195849720143"  # yhan account（不属于当前用户）
        logger.info(f"使用不在 visible 范围内的 Sub Account ID: {invisible_sa_id}")

        positions_response = sa_api.get_related_positions(invisible_sa_id, page=0, size=10)

        assert positions_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {positions_response.status_code}"

        response_body = positions_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  返回业务错误码: code={response_body.get('code')}, msg={response_body.get('error_message')}")
        else:
            parsed_pos = sa_api.parse_list_response(positions_response)
            assert len(parsed_pos.get("content", [])) == 0, \
                f"越权 Sub Account ID 应返回空持仓列表，实际有 {len(parsed_pos.get('content', []))} 条"
            logger.info("  越权 Sub Account ID 返回空持仓列表")

        logger.info("✓ 越权 Sub Account ID 持仓查询验证通过")
